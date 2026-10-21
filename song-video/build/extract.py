#!/usr/bin/env python3
"""Pre-render background windows: clip crops -> JPEG frame sequences, still crops -> JPEG.
Usage: python3 -I extract.py timeline.json   (writes ./frames/<id>/%04d.jpg and ./stills/<id>.jpg)
"""
import json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
tl = json.load(open(sys.argv[1], encoding="utf-8"))
art = Image.open(os.path.join(ROOT, "assets", "background-art.jpg")).convert("RGB")
os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
os.makedirs(os.path.join(HERE, "stills"), exist_ok=True)

from PIL import ImageFilter
art.resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14)).save(os.path.join(HERE, "stills", "base.jpg"), quality=90)

def even(n): return int(round(n / 2)) * 2

for w in tl["windows"]:
    bx, by, bw, bh = w["box"]
    if w["type"] == "clip":
        cx, cy, cw = w["crop"]
        ch = even(cw * bh / bw)
        out = os.path.join(HERE, "frames", w["id"])
        os.makedirs(out, exist_ok=True)
        src = os.path.join(ROOT, "clips", w["src"] + ".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                        f"crop={cw}:{ch}:{cx}:{cy},scale={bw}:{bh}:flags=lanczos", "-q:v", "3",
                        os.path.join(out, "%04d.jpg")], check=True)
        n = len(os.listdir(out))
        w["nframes"] = n
        print(w["id"], "frames", n, f"crop {cw}x{ch}@{cx},{cy} -> {bw}x{bh}")
    elif w["type"] in ("still", "grow"):
        zmax = max(w.get("zoom", [1, 1])) if w["type"] == "still" else 1.0
        if w["type"] == "still":
            cx, cy, cw = w["crop"]
            ch = round(cw * bh / bw)
            img = art.crop((cx, cy, cx + cw, min(cy + ch, art.height)))
        else:
            img = art
        tw, th = int(bw * zmax), int(bh * zmax)
        img = img.resize((tw, th), Image.LANCZOS)
        img.save(os.path.join(HERE, "stills", w["id"] + ".jpg"), quality=92)
        w["still"] = [tw, th]
        print(w["id"], "still", tw, th)
json.dump(tl, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
