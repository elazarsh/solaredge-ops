#!/usr/bin/env python3
"""Time map for code-driven video editing.

An effect is placed on a word of the ORIGINAL recording ("on the word X"). After silences are cut
and freeze-frames are added, that word lands somewhere else in the FINAL video. This module is the
single source of truth for that conversion, and it also builds the ffmpeg audio graph that cuts the
sound by the very same map, so picture, effects and sound cannot drift apart.

Pure standard library. Importable (``from timemap import TimeMap``) and runnable:

    python3 timemap.py words.json --max-gap 0.45 --pad 0.08
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

EPS = 1e-9


@dataclass(frozen=True)
class Piece:
    kind: str          # "play" or "hold"
    orig_start: float  # for "hold": the frozen original time (orig_start == orig_end)
    orig_end: float
    final_start: float
    final_end: float


def segments_from_words(
    words: Sequence[dict],
    duration: Optional[float] = None,
    max_gap: float = 0.45,
    pad: float = 0.08,
    min_len: float = 0.3,
) -> list[tuple[float, float]]:
    """Turn a word table [{"word", "start", "end"}, ...] into segments worth keeping.

    Words closer than ``max_gap`` seconds stay in one segment. Each segment is padded by ``pad`` on
    both sides so breaths and word edges are not clipped, and segments shorter than ``min_len`` are
    dropped (usually a stray noise). Timestamps must be in seconds of the original recording.
    """
    ordered = sorted((w for w in words if w["end"] > w["start"]), key=lambda w: w["start"])
    if not ordered:
        return []
    groups: list[list[float]] = [[ordered[0]["start"], ordered[0]["end"]]]
    for w in ordered[1:]:
        if w["start"] - groups[-1][1] <= max_gap:
            groups[-1][1] = max(groups[-1][1], w["end"])
        else:
            groups.append([w["start"], w["end"]])
    out: list[tuple[float, float]] = []
    for s, e in groups:
        s, e = max(0.0, s - pad), e + pad
        if duration is not None:
            e = min(e, duration)
        if e - s >= min_len:
            if out and s <= out[-1][1] + EPS:  # padding made neighbours touch: merge
                out[-1] = (out[-1][0], max(out[-1][1], e))
            else:
                out.append((s, e))
    return out


class TimeMap:
    """Maps original time <-> final time for a cut-and-hold edit."""

    def __init__(
        self,
        keep: Iterable[tuple[float, float]],
        holds: Iterable[tuple[float, float]] = (),
    ) -> None:
        segs = sorted((float(s), float(e)) for s, e in keep)
        if not segs:
            raise ValueError("keep must contain at least one segment")
        for (s, e) in segs:
            if e <= s:
                raise ValueError(f"empty or reversed segment: {(s, e)}")
        for (_, e1), (s2, _) in zip(segs, segs[1:]):
            if s2 < e1 - EPS:
                raise ValueError("keep segments overlap; merge them first")
        hold_list = sorted((float(t), float(d)) for t, d in holds)
        for t, d in hold_list:
            if d <= 0:
                raise ValueError(f"hold duration must be positive: {(t, d)}")
            if not any(s - EPS <= t <= e + EPS for s, e in segs):
                raise ValueError(f"hold at {t}s falls inside a cut region")

        pieces: list[Piece] = []
        cursor = 0.0
        for s, e in segs:
            at = s
            for t, d in hold_list:
                if s - EPS <= t <= e + EPS and t > at - EPS:
                    if t - at > EPS:
                        pieces.append(Piece("play", at, t, cursor, cursor + (t - at)))
                        cursor += t - at
                    pieces.append(Piece("hold", t, t, cursor, cursor + d))
                    cursor += d
                    at = t
            if e - at > EPS:
                pieces.append(Piece("play", at, e, cursor, cursor + (e - at)))
                cursor += e - at
        self.pieces = pieces
        self.final_duration = cursor

    def to_final(self, t: float, after_hold: bool = False) -> Optional[float]:
        """Final time at which original time ``t`` appears, or None if ``t`` was cut.

        If a freeze-frame sits at ``t``, returns where the freeze starts (``after_hold=True``: where
        it ends, i.e. when playback resumes).
        """
        result: Optional[float] = None
        for p in self.pieces:
            if p.kind == "hold" and abs(p.orig_start - t) <= 1e-6:
                return p.final_end if after_hold else p.final_start
            if p.kind == "play" and p.orig_start - EPS <= t <= p.orig_end + EPS and result is None:
                result = p.final_start + (t - p.orig_start)
        return result

    def to_orig(self, f: float) -> Optional[tuple[float, bool]]:
        """(original time to sample, is_frozen) for final time ``f``; None past the end."""
        if f < -EPS or f > self.final_duration + EPS:
            return None
        for p in self.pieces:
            if p.final_start - EPS <= f < p.final_end - EPS or (
                f >= self.final_duration - EPS and p is self.pieces[-1]
            ):
                if p.kind == "hold":
                    return p.orig_start, True
                return p.orig_start + (min(f, p.final_end) - p.final_start), False
        return None

    def audio_filtergraph(self, input_label: str = "0:a", out_label: str = "aout") -> str:
        """ffmpeg -filter_complex graph that cuts audio by this map (holds become silence)."""
        parts: list[str] = []
        labels: list[str] = []
        for i, p in enumerate(self.pieces):
            lab = f"a{i}"
            if p.kind == "play":
                parts.append(
                    f"[{input_label}]atrim=start={p.orig_start:.6f}:end={p.orig_end:.6f},"
                    f"asetpts=PTS-STARTPTS[{lab}]"
                )
            else:
                dur = p.final_end - p.final_start
                parts.append(
                    f"anullsrc=r=48000:cl=stereo,atrim=duration={dur:.6f},asetpts=PTS-STARTPTS[{lab}]"
                )
            labels.append(f"[{lab}]")
        parts.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[{out_label}]")
        return ";".join(parts)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Suggest keep-segments from a word table")
    ap.add_argument("words_json", help='JSON list of {"word","start","end"} in seconds')
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--max-gap", type=float, default=0.45)
    ap.add_argument("--pad", type=float, default=0.08)
    ap.add_argument("--min-len", type=float, default=0.3)
    args = ap.parse_args(argv)
    with open(args.words_json, encoding="utf-8") as fh:
        words = json.load(fh)
    keep = segments_from_words(words, args.duration, args.max_gap, args.pad, args.min_len)
    tm = TimeMap(keep)
    print(json.dumps({"keep": keep, "final_duration": round(tm.final_duration, 3)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
