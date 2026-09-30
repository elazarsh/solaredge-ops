#!/usr/bin/env python3
"""Beat grid for a song, and peak offsets for sound effects (numpy + ffmpeg only).

Song:  python3 video-studio/tools/beat-grid.py song.mp3 [--bpm 120] [--bars 7] [--beats-per-bar 4] [-o grid.json]
       Prints BPM, the first downbeat and a bar/beat table; writes JSON with every beat time.
       --bpm is a hint (search ±8%); omit it to search 70–180 BPM.
SFX:   python3 video-studio/tools/beat-grid.py --peak pop.mp3 [click.mp3 ...]
       Prints each file's loudest-moment offset. Place an SFX so its PEAK lands on the beat:
       data-start = beat_time - peak.
"""
import argparse, json, subprocess, sys
import numpy as np

SR = 22050
HOP = 512


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def peak_offset(path):
    y = load(path)
    win = int(0.005 * SR)  # 5 ms RMS so a single sample spike doesn't win
    env = np.sqrt(np.convolve(y ** 2, np.ones(win) / win, mode="same"))
    return float(np.argmax(env) / SR)


def onset_envelope(y):
    n_fft = 2048
    frames = 1 + (len(y) - n_fft) // HOP
    idx = np.arange(n_fft)[None, :] + HOP * np.arange(frames)[:, None]
    spec = np.abs(np.fft.rfft(y[idx] * np.hanning(n_fft), axis=1))
    logspec = np.log1p(100 * spec)
    flux = np.maximum(0, np.diff(logspec, axis=0)).sum(axis=1)
    flux = np.concatenate([[0], flux])
    flux -= np.convolve(flux, np.ones(16) / 16, mode="same")  # remove slow trend
    flux = np.maximum(flux, 0)
    low = spec[:, : int(150 * n_fft / SR)].sum(axis=1)  # kick-drum band for downbeats
    return flux / (flux.max() or 1), low / (low.max() or 1)


def tempo(env, lo, hi):
    fps = SR / HOP
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lags = np.arange(len(ac))
    best, best_score = None, -1
    for bpm in np.arange(lo, hi, 0.05):
        lag = 60 * fps / bpm
        # score the lag and its multiples (robust to syncopation)
        score = sum(np.interp(lag * k, lags, ac) / k for k in (1, 2, 4))
        if score > best_score:
            best, best_score = bpm, score
    return float(best)


def phase(env, period_frames):
    best, best_score = 0.0, -1
    for p in np.arange(0, period_frames, 0.25):
        pos = np.arange(p, len(env) - 1, period_frames)
        score = np.interp(pos, np.arange(len(env)), env).sum()
        if score > best_score:
            best, best_score = p, score
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song", nargs="?")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("--beats-per-bar", type=int, default=4)
    ap.add_argument("--peak", nargs="+", metavar="SFX")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    if a.peak:
        for f in a.peak:
            print(f"{peak_offset(f):.3f}s  {f}")
        return
    if not a.song:
        ap.error("song path required (or --peak)")

    y = load(a.song)
    env, low = onset_envelope(y)
    lo, hi = (a.bpm * 0.92, a.bpm * 1.08) if a.bpm else (70, 180)
    bpm = tempo(env, lo, hi)
    if abs(bpm - round(bpm)) < 0.35:  # most produced music sits on an integer BPM
        bpm = float(round(bpm))
    fps = SR / HOP
    period = 60 * fps / bpm
    ph = phase(env, period)
    # + half a window: an STFT frame's energy is centred n_fft/2 samples after its start
    beats = np.arange(ph, len(env) - 1, period) / fps + 1024 / SR

    # downbeat = the beat position within the bar with the most low-end energy
    bpb = a.beats_per_bar
    lowat = np.interp(beats * fps, np.arange(len(low)), low)
    offs = int(np.argmax([lowat[k::bpb].mean() for k in range(bpb)]))
    beats = beats[offs:]
    beat_s = 60 / bpm
    grid = {
        "bpm": round(bpm, 2), "beat_seconds": round(beat_s, 4), "beats_per_bar": bpb,
        "first_downbeat": round(float(beats[0]), 3),
        "beats": [round(float(t), 3) for t in beats],
        "section_seconds": round(a.bars * bpb * beat_s, 3),
    }
    if a.out:
        json.dump(grid, open(a.out, "w"), indent=1)
    print(f"BPM {grid['bpm']}  beat {grid['beat_seconds']}s  first downbeat {grid['first_downbeat']}s")
    print(f"{a.bars} bars = {grid['section_seconds']}s (trim the song to start at the first downbeat)")
    print("bar | " + " | ".join(f"beat {i + 1}" for i in range(bpb)))
    for b in range(min(a.bars, len(beats) // bpb)):
        row = beats[b * bpb:(b + 1) * bpb] - beats[0]
        print(f"{b + 1:>3} | " + " | ".join(f"{t:6.3f}" for t in row))


if __name__ == "__main__":
    sys.exit(main())
