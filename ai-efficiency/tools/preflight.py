#!/usr/bin/env python3
"""Free pre-flight for a production session: finds blockers before work starts. Never prints secret values.

Usage: python3 preflight.py [--env NAME ...] [--bins ffmpeg ...] [--mods numpy ...] [--net host ...]
Checks: env var NAMES (yes/no, plus near-miss names such as gpt_api_key vs OPENAI_API_KEY), binaries, python modules,
the git remote (ls-remote), and optionally HTTPS reachability of hosts (--net). Exit code 1 if a required item fails.
Env vars load only at session start: after adding one, open a NEW session before re-checking.
"""
import argparse, importlib.util, os, re, shutil, subprocess, sys, urllib.request

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", nargs="*", default=["GEMINI_API_KEY", "OPENAI_API_KEY"])
    ap.add_argument("--bins", nargs="*", default=["ffmpeg", "ffprobe", "node", "python3", "git"])
    ap.add_argument("--mods", nargs="*", default=["numpy", "PIL"])
    ap.add_argument("--net", nargs="*", default=[]); a = ap.parse_args(); fail = 0
    for n in a.env:
        if os.environ.get(n): print(f"OK    env {n} set"); continue
        stem = re.sub(r"[^a-z0-9]", "", n.lower().replace("_api_key", ""))
        near = [k for k in os.environ if k != n and stem and stem in re.sub(r"[^a-z0-9]", "", k.lower())]
        print(f"FAIL  env {n} missing" + (f" (similar names set: {', '.join(near)}; the tool reads exactly {n})" if near else "")); fail += 1
    for b in a.bins:
        ok = shutil.which(b); print(("OK    bin " if ok else "FAIL  bin ") + b); fail += 0 if ok else 1
    for m in a.mods:
        ok = importlib.util.find_spec(m) is not None; print(("OK    py  " if ok else "FAIL  py  ") + m); fail += 0 if ok else 1
    r = subprocess.run(["git", "ls-remote", "--exit-code", "origin", "HEAD"], capture_output=True, text=True, timeout=30) if shutil.which("git") else None
    if r is None: print("WARN  git missing")
    elif r.returncode == 0: print("OK    git remote reachable; branch " + subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip())
    else: print("FAIL  git remote not reachable or not attached to this session"); fail += 1
    for h in a.net:
        try: print(f"OK    net {h} -> HTTP {urllib.request.urlopen(urllib.request.Request('https://' + h, method='HEAD'), timeout=10).status}")
        except Exception as e:
            code = getattr(e, "code", None); print(f"{'OK  ' if code else 'FAIL'}  net {h} -> {code or repr(e)[:60]}"); fail += 0 if code else 1
    print("result:", "BLOCKERS FOUND" if fail else "ready"); return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main())
