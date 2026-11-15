#!/usr/bin/env python3
"""מזריק משכי סצנות ו-cues לתבנית: מחליף __DUR__ ו-__CUES__ ושומר page.html (cues לפי סדר מפתחות הסצנות).
  python3 build.py index.html --cues cues.json --durations durations.json --out page.html
"""
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("template")
ap.add_argument("--cues", default="cues.json"); ap.add_argument("--durations", default="durations.json"); ap.add_argument("--out", default="page.html")
a = ap.parse_args()
c = json.load(open(a.cues, encoding="utf-8"))["cues"]; D = json.load(open(a.durations))
cues = [c[k] for k in sorted(c)]
t = open(a.template, encoding="utf-8").read().replace("__DUR__", json.dumps(D)).replace("__CUES__", json.dumps(cues, ensure_ascii=False))
open(a.out, "w", encoding="utf-8").write(t); print("built", a.out, len(t), "scenes", len(D))
