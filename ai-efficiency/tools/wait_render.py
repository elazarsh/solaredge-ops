#!/usr/bin/env python3
"""Wait for a long job with ONE command instead of repeated `sleep N; tail log` calls. Prints only the verdict.

Usage: python3 wait_render.py --file out.mp4 [--log render.log --pattern 'done|error'] [--timeout 540] [--interval 5]
Done when: the file exists and its size stops changing for 2 checks, or (with --log/--pattern) the regex matches the log.
Exit 0 done, 2 timeout, 3 log matched an error word (error|traceback|failed). Keep --timeout under the 600 s tool limit.
"""
import argparse, os, re, sys, time

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--file"); ap.add_argument("--log"); ap.add_argument("--pattern")
    ap.add_argument("--timeout", type=int, default=540); ap.add_argument("--interval", type=int, default=5)
    a = ap.parse_args(); t0 = time.time(); last = -1; stable = 0
    while time.time() - t0 < a.timeout:
        if a.log and os.path.exists(a.log):
            txt = open(a.log, errors="replace").read()[-20000:]
            if re.search(r"(?i)\b(traceback|error|failed)\b", txt): print("ERROR in log:", txt.strip().splitlines()[-1][:200]); return 3
            if a.pattern and re.search(a.pattern, txt): print("DONE (log matched):", txt.strip().splitlines()[-1][:200]); return 0
        if a.file and os.path.exists(a.file):
            sz = os.path.getsize(a.file); stable = stable + 1 if sz == last and sz > 0 else 0; last = sz
            if stable >= 2 and not a.pattern: print(f"DONE: {a.file} {sz/1e6:.1f} MB after {time.time()-t0:.0f}s"); return 0
        time.sleep(a.interval)
    print(f"TIMEOUT after {a.timeout}s"); return 2

if __name__ == "__main__":
    sys.exit(main())
