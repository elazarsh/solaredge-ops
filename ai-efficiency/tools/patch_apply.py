#!/usr/bin/env python3
"""Apply exact text replacements from a JSON list, safely and repeatably. Replaces inline python heredoc edits.

Usage: python3 patch_apply.py patches.json [--apply]
patches.json: [{"file": "path", "old": "text", "new": "text", "count": 1}, ...]
Default is a DRY RUN. Each `old` must occur exactly `count` times; if `old` is absent and `new` is present the
patch is reported as already applied (safe to re-run). With --apply a .bak copy is written next to each file once.
"""
import argparse, json, os, shutil, sys

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("patches"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(); items = json.load(open(a.patches, encoding="utf-8")); bad = 0; texts = {}
    for i, it in enumerate(items, 1):
        f, old, new, cnt = it["file"], it["old"], it["new"], it.get("count", 1)
        if f not in texts: texts[f] = open(f, encoding="utf-8").read()
        t = texts[f]; n = t.count(old)
        if n == cnt: texts[f] = t.replace(old, new); print(f"#{i} OK      {f} ({n}x)")
        elif n == 0 and new in t: print(f"#{i} SKIP    {f} already applied")
        else: print(f"#{i} FAIL    {f} expected {cnt} match(es), found {n}"); bad += 1
    if bad: print(f"{bad} patch(es) failed: nothing written"); return 1
    if a.apply:
        for f, t in texts.items():
            if not os.path.exists(f + ".bak"): shutil.copy2(f, f + ".bak")
            open(f, "w", encoding="utf-8").write(t)
        print("applied")
    else: print("dry run (use --apply)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
