#!/usr/bin/env python3
"""Static audit of a skill/plugin repo BEFORE installing it. Read-only; never executes repo code.

Usage: python3 skill_audit.py <path-to-cloned-repo> [--json]
Reports: license, size, number of SKILL.md files, total description length (context cost),
risky patterns (pipe-to-shell, base64 decode, destructive rm, netcat), and binary/large files.
"""
import argparse, json, os, re, sys

RISKY = {
    "pipe_to_shell": re.compile(r"(curl|wget)[^\n|]*\|\s*(ba)?sh"),
    "base64_decode": re.compile(r"base64\s+(-d|--decode)"),
    "rm_rf_root_or_home": re.compile(r"rm\s+-rf\s+(/|~|\$HOME)(\s|$)"),
    "netcat_shell": re.compile(r"\bnc\s+-e\b"),
    "eval_of_download": re.compile(r"eval\s+\"?\$\(\s*(curl|wget)"),
}
TEXT_EXT = {".md", ".sh", ".py", ".js", ".mjs", ".ts", ".json", ".yaml", ".yml", ".toml", ".txt"}

def license_of(root):
    for n in os.listdir(root):
        if n.lower().startswith("licen"):
            head = open(os.path.join(root, n), encoding="utf-8", errors="replace").read(600)
            for k in ("MIT", "Apache", "GPL", "BSD", "Mozilla", "CC BY", "Unlicense"):
                if k.lower() in head.lower():
                    return k
            return "unrecognized (read " + n + ")"
    return "none found"

def desc_len(text):
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m: return 0
    d = re.search(r"description:\s*(.*)", m.group(1), re.S)
    return len(d.group(1)) if d else 0

def audit(root):
    n_files = size = n_skill = desc = 0; hits = []; big = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "node_modules")]
        for f in fn:
            p = os.path.join(dp, f); rel = os.path.relpath(p, root)
            try: sz = os.path.getsize(p)
            except OSError: continue
            n_files += 1; size += sz
            if sz > 5_000_000: big.append((rel, sz))
            if f == "SKILL.md":
                n_skill += 1; desc += desc_len(open(p, encoding="utf-8", errors="replace").read())
            if os.path.splitext(f)[1].lower() in TEXT_EXT and sz < 2_000_000:
                txt = open(p, encoding="utf-8", errors="replace").read()
                for name, rx in RISKY.items():
                    for m in rx.finditer(txt):
                        hits.append({"file": rel, "pattern": name, "line": txt.count("\n", 0, m.start()) + 1})
    return {"license": license_of(root), "files": n_files, "size_mb": round(size / 1e6, 1),
            "skill_md_count": n_skill, "description_chars_total": desc,
            "risky_hits": hits[:50], "large_files": [{"file": f, "mb": round(s / 1e6, 1)} for f, s in big[:10]]}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("repo"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(); r = audit(a.repo)
    if a.json: print(json.dumps(r, ensure_ascii=False, indent=2)); return
    print(f"license: {r['license']} | files: {r['files']} | size: {r['size_mb']} MB | SKILL.md: {r['skill_md_count']}")
    print(f"context cost: ~{r['description_chars_total']:,} description chars loaded every session if installed")
    print(f"risky patterns: {len(r['risky_hits'])}")
    for h in r["risky_hits"][:15]: print(f"  {h['file']}:{h['line']} {h['pattern']}")
    for b in r["large_files"]: print(f"  large: {b['file']} {b['mb']} MB")
    print("verdict: READ the SKILL.md and scripts before installing; this report is not a security guarantee.")

if __name__ == "__main__":
    sys.exit(main())
