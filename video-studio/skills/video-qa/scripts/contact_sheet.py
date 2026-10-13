#!/usr/bin/env python3
"""Contact sheets with a timecode on every frame, the way an editor reviews a cut.

    python3 contact_sheet.py final.mp4 --fps 6 --out-dir qa/            # whole video
    python3 contact_sheet.py final.mp4 --start 12 --end 15 --fps 12     # zoom into one effect
    python3 contact_sheet.py final.mp4 --moments 3.4,9.1,14.0           # full-size frames

Needs ffmpeg/ffprobe on PATH and Pillow. Prints the files it wrote, one per line.
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Optional, Sequence

from PIL import Image, ImageDraw, ImageFont


def _run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {res.stderr.strip()[-600:]}")
    return res.stdout


def probe_duration(path: str) -> float:
    out = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path])
    return float(out.strip())


def timecode(t: float) -> str:
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


def _label(img: Image.Image, text: str) -> Image.Image:
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    f = _font(max(12, img.width // 14))
    box = draw.textbbox((0, 0), text, font=f)
    w, h = box[2] - box[0] + 10, box[3] - box[1] + 8
    draw.rectangle((0, 0, w, h), fill=(0, 0, 0))
    draw.text((5, 2), text, font=f, fill=(255, 255, 0))
    return img


def extract_frames(video: str, start: float, dur: float, fps: float, thumb_w: int, tmp: str) -> list[str]:
    _run([
        "ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", video,
        "-vf", f"fps={fps},scale={thumb_w}:-2", os.path.join(tmp, "f_%05d.png"),
    ])
    return sorted(os.path.join(tmp, n) for n in os.listdir(tmp) if n.startswith("f_"))


def build_sheets(video: str, out_dir: str, fps: float, cols: int, thumb_w: int,
                 start: float, end: Optional[float], per_sheet: int) -> list[str]:
    total = probe_duration(video)
    end = min(end if end is not None else total, total)
    if end <= start:
        raise ValueError("--end must be after --start")
    os.makedirs(out_dir, exist_ok=True)
    written: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_frames(video, start, end - start, fps, thumb_w, tmp)
        if not frames:
            raise RuntimeError("no frames extracted")
        thumbs = []
        for i, p in enumerate(frames):
            with Image.open(p) as im:
                thumbs.append(_label(im, timecode(start + i / fps)))
        tw, th = thumbs[0].size
        for n in range(math.ceil(len(thumbs) / per_sheet)):
            chunk = thumbs[n * per_sheet:(n + 1) * per_sheet]
            rows = math.ceil(len(chunk) / cols)
            sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
            for i, t in enumerate(chunk):
                sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
            path = os.path.join(out_dir, f"sheet_{n + 1:02d}.png")
            sheet.save(path)
            written.append(path)
    return written


def grab_moments(video: str, out_dir: str, moments: Sequence[float]) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for t in moments:
        path = os.path.join(out_dir, f"moment_{t:07.2f}.png")
        _run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", path])
        written.append(path)
    return written


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out-dir", default="qa")
    ap.add_argument("--fps", type=float, default=6.0, help="frames per second to sample (default 6)")
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--thumb-width", type=int, default=320)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--per-sheet", type=int, default=36)
    ap.add_argument("--moments", default="", help="comma-separated seconds to save as full-size frames")
    args = ap.parse_args(argv)
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"error: {tool} not found on PATH", file=sys.stderr)
            return 2
    files = build_sheets(args.video, args.out_dir, args.fps, args.cols, args.thumb_width,
                         args.start, args.end, args.per_sheet)
    if args.moments:
        files += grab_moments(args.video, args.out_dir, [float(x) for x in args.moments.split(",") if x.strip()])
    print("\n".join(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
