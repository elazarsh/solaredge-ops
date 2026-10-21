#!/usr/bin/env python3
"""גיליון מגע: רשת תמונות בתוויות, מקבצי תמונה או מזמנים בתוך וידאו.

  python3 contact_sheet.py out.jpg img/k1.png img/k2.png ...          # מתמונות
  python3 contact_sheet.py out.jpg --video film.mp4 --times 5 30 61.5  # מפריימים בזמנים (שניות)
  python3 contact_sheet.py out.jpg --video film.mp4 --every 10         # פריים כל 10 שניות
  --cols 4 (תמונות) / 2 (וידאו: תאים גדולים לקריאת טקסט)
מצרפים את הגיליון לשיחה/בודקים בעין: חפיפות טקסט, פריימים שחורים, חיתוכים, טקסט שנחתך. רק Pillow + ffmpeg.
"""
import argparse, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("images", nargs="*")
ap.add_argument("--video"); ap.add_argument("--times", nargs="*", type=float); ap.add_argument("--every", type=float)
ap.add_argument("--cols", type=int); a = ap.parse_args()
items = []  # (label, path)
if a.video:
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout)
    if a.times: times = a.times
    elif a.every: times = [x * a.every for x in range(int(d / a.every) + 1) if x * a.every < d]
    else: sys.exit("צריך --times או --every")
    tmp = tempfile.mkdtemp()
    for t in times:
        p = os.path.join(tmp, f"{t:.1f}.jpg")
        if t >= d: print(f"דילוג על t={t}: אחרי סוף הסרטון ({d:.1f}s)"); continue
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", a.video, "-frames:v", "1", "-q:v", "3", p], check=True)
        items.append((f"t={t:.1f}", p))
    cols, w, h = a.cols or 2, 960, 540
else:
    if not a.images: sys.exit("צריך תמונות או --video")
    items = [(os.path.splitext(os.path.basename(p))[0], p) for p in a.images]; cols, w, h = a.cols or 4, 480, 270
rows = (len(items) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), "white"); d = ImageDraw.Draw(sheet)
for i, (lab, p) in enumerate(items):
    im = Image.open(p).convert("RGB").resize((w, h)); sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    d.rectangle([(i % cols) * w, (i // cols) * h, (i % cols) * w + 130, (i // cols) * h + 26], fill=(0, 0, 0)); d.text(((i % cols) * w + 6, (i // cols) * h + 7), lab, fill=(255, 255, 0))
sheet.save(a.out, quality=85); print("saved", a.out, len(items), "cells")
