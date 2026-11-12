#!/usr/bin/env python3
"""Validate toldot-video/art: manifest vs files, naming, size, aspect, sprite background, beat coverage.
Usage: python3 toldot-video/art/validate_art.py [--strict-coverage]   (needs Pillow: pip install pillow)
Exit code 0 = OK, 1 = errors."""
import json, os, re, sys
ART = os.path.dirname(os.path.abspath(__file__))
NAME = re.compile(r'^(T[1-6]|P\d{2}|S\d{2})_[a-z0-9_]+\.(png|jpg|jpeg|webp)$')
errs, warns = [], []
try:
    from PIL import Image
except ImportError:
    Image = None; warns.append("Pillow missing: skipping image checks (pip install pillow)")
m = json.load(open(os.path.join(ART, 'manifest.json'), encoding='utf-8'))
imgs = m.get('images', [])
covered = set(); seen = set()
for it in imgs:
    f = it.get('file', ''); i = it.get('id', '?')
    p = os.path.join(ART, f)
    if i in seen: errs.append(f"duplicate id {i}")
    seen.add(i)
    if not os.path.isfile(p): errs.append(f"{i}: file missing: {f}"); continue
    if not NAME.match(os.path.basename(f)): errs.append(f"{i}: bad file name {os.path.basename(f)}")
    if it.get('type') not in ('test', 'plate', 'sprite'): errs.append(f"{i}: type must be test|plate|sprite")
    folder = f.split('/')[0]
    if {'test': 'test', 'plate': 'plates', 'sprite': 'sprites'}.get(it.get('type')) != folder:
        errs.append(f"{i}: type {it.get('type')} not in folder {folder}")
    sz = os.path.getsize(p) / 1e6
    if sz > 8: errs.append(f"{i}: file {sz:.1f} MB (>8 MB), compress it")
    qa = it.get('qa', {})
    for k in ('faces', 'text', 'weapons'):
        if qa.get(k) not in ('pass',) and it.get('status') == 'approved': errs.append(f"{i}: approved but qa.{k} != pass")
    if Image:
        im = Image.open(p).convert('RGB'); w, h = im.size
        r = w / h
        if it.get('type') == 'sprite': pass   # sprites may have any aspect
        elif not (abs(r - 9/16) < 0.02 or abs(r - 2/3) < 0.02): errs.append(f"{i}: aspect {w}x{h} is neither 9:16 nor 2:3")
        elif abs(r - 2/3) < 0.02: warns.append(f"{i}: 2:3 image; keep subject in the middle 80% width so it can be cropped to 9:16")
        if max(w, h) > 4096: warns.append(f"{i}: very large {w}x{h}")
        if it.get('type') == 'sprite':
            px = [im.getpixel(c) for c in ((2, 2), (w-3, 2), (2, h-3), (w-3, h-3))]
            if not all(g > r_ + 40 and g > b + 40 for r_, g, b in px): errs.append(f"{i}: sprite corners are not flat green")
    for b in it.get('beats', []): covered.add(int(b))
all_beats = set(range(0, 76))
missing = sorted(all_beats - covered)
if imgs and missing: (errs if '--strict-coverage' in sys.argv else warns).append(f"beats not covered yet: {missing}")
print(f"{len(imgs)} images in manifest · {sum(1 for i in imgs if i.get('type')=='plate')} plates · {sum(1 for i in imgs if i.get('type')=='sprite')} sprites · {sum(1 for i in imgs if i.get('type')=='test')} tests")
for w_ in warns: print("WARN ", w_)
for e in errs: print("ERROR", e)
print("OK" if not errs else f"{len(errs)} error(s)")
sys.exit(1 if errs else 0)
