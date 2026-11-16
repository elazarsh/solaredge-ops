#!/usr/bin/env python3
"""Shrink images before a model reads them. One small contact sheet instead of many full-size images.

Usage: python3 img_prep.py <files-or-dirs...> --out DIR [--max 1024] [--sheet] [--cols 4] [--seen seen.json]
Writes DIR/<name>.jpg (long side <= --max, JPEG q70) and, with --sheet, DIR/sheet.jpg (labelled grid).
--seen keeps a list of file hashes already shown; a repeat is reported so it is not read again.
Pillow only; no network; originals untouched.
"""
import argparse, hashlib, json, os, sys
from PIL import Image, ImageDraw

EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

def collect(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += [os.path.join(p, f) for f in sorted(os.listdir(p)) if os.path.splitext(f)[1].lower() in EXT]
        elif os.path.splitext(p)[1].lower() in EXT:
            out.append(p)
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("paths", nargs="+"); ap.add_argument("--out", required=True)
    ap.add_argument("--max", type=int, default=1024); ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--cols", type=int, default=4); ap.add_argument("--seen")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    seen = set(json.load(open(a.seen))) if a.seen and os.path.exists(a.seen) else set()
    thumbs, rows = [], []
    for p in collect(a.paths):
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
        im = Image.open(p).convert("RGB"); w, hh = im.size
        s = min(1.0, a.max / max(w, hh)); sm = im.resize((max(1, int(w * s)), max(1, int(hh * s))))
        dst = os.path.join(a.out, os.path.splitext(os.path.basename(p))[0] + ".jpg"); sm.save(dst, "JPEG", quality=70)
        rows.append((os.path.basename(p), os.path.getsize(p), os.path.getsize(dst), (w, hh), sm.size, h in seen))
        seen.add(h); thumbs.append((os.path.basename(p), sm))
    if a.sheet and thumbs:
        cell = 320; cols = min(a.cols, len(thumbs)); nrows = -(-len(thumbs) // cols)
        sheet = Image.new("RGB", (cols * cell, nrows * (cell + 18)), "white"); d = ImageDraw.Draw(sheet)
        for i, (name, t) in enumerate(thumbs):
            t = t.copy(); t.thumbnail((cell, cell)); x, y = (i % cols) * cell, (i // cols) * (cell + 18)
            sheet.paste(t, (x, y + 18)); d.text((x + 3, y + 3), name[:40], fill="black")
        sheet.save(os.path.join(a.out, "sheet.jpg"), "JPEG", quality=70)
    if a.seen: json.dump(sorted(seen), open(a.seen, "w"))
    tot0 = sum(r[1] for r in rows); tot1 = sum(r[2] for r in rows)
    for n, b0, b1, d0, d1, rep in rows:
        print(f"{n}: {d0[0]}x{d0[1]} {b0/1024:.0f}KB -> {d1[0]}x{d1[1]} {b1/1024:.0f}KB" + ("  [ALREADY SEEN, skip re-reading]" if rep else ""))
    print(f"total {tot0/1024:.0f}KB -> {tot1/1024:.0f}KB" + (" | sheet: " + os.path.join(a.out, "sheet.jpg") if a.sheet and thumbs else ""))

if __name__ == "__main__":
    sys.exit(main())
