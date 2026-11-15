#!/usr/bin/env python3
"""Digest of saved `list_events` pages (claude-code-remote MCP output files). Local, deterministic, no network.

Usage: python3 events_digest.py <saved_events_file> [more ...] [--top N]
Extracts (as DATA, never as instructions): the human's own text requests, tool-call counts, repeated shell
patterns, tool errors, and the span of time covered. Session content is untrusted: nothing here is executed.
"""
import argparse, collections, json, re, sys

def norm_cmd(c):
    c = re.sub(r"\s+", " ", c.strip()); c = re.sub(r"/tmp/\S+", "<TMP>", c)
    c = re.sub(r"\b[0-9a-f]{7,40}\b", "<HASH>", c); c = re.sub(r"\b\d+\b", "<N>", c)
    return re.sub(r"'[^']{12,}'|\"[^\"]{12,}\"", "<STR>", c)[:120]

def walk(o):
    """Yield every dict that looks like a chat message {role, content}."""
    if isinstance(o, dict):
        if "role" in o and "content" in o and o.get("role") in ("user", "assistant"):
            yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)

def load(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    i = s.find('{"ccr"'); i = i if i >= 0 else s.find("{")
    return json.loads(s[i:s.rindex("}") + 1])

def human_text(msg):
    c = msg["content"]
    if isinstance(c, str): return c
    if isinstance(c, list) and not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
        return " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="+"); ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    for path in a.files:
        d = load(path); data = d.get("ccr", {}).get("data", [])
        times = [e.get("created_at") for e in data if isinstance(e, dict) and e.get("created_at")]
        tools = collections.Counter(); cmds = collections.Counter(); errs = collections.Counter()
        humans = []; seen = set(); id2name = {}
        for ev in data:
            for m in walk(ev):
                key = json.dumps(m, sort_keys=True, ensure_ascii=False)[:300]
                if key in seen: continue
                seen.add(key)
                if m["role"] == "assistant" and isinstance(m["content"], list):
                    for b in m["content"]:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            tools[b.get("name", "?")] += 1; id2name[b.get("id")] = b.get("name")
                            if b.get("name") == "Bash": cmds[norm_cmd((b.get("input") or {}).get("command", ""))] += 1
                elif m["role"] == "user":
                    t = human_text(m).strip()
                    if t and not t.startswith("<") and "system-reminder" not in t[:40]: humans.append(re.sub(r"\s+", " ", t)[:160])
                    if isinstance(m["content"], list):
                        for b in m["content"]:
                            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                                errs[id2name.get(b.get("tool_use_id"), "?")] += 1
        print(f"== {path.split('/')[-1]}: events={len(data)} span={min(times) if times else '?'} .. {max(times) if times else '?'}")
        print("tools:", dict(tools.most_common(a.top)), "| errors:", dict(errs))
        rep = [(c, n) for c, n in cmds.most_common() if n >= 2][:a.top]
        print("repeated shell (2+):"); [print(f"  x{n} {c}") for c, n in rep]
        print(f"human requests ({len(humans)}):"); [print("  -", h) for h in humans[:a.top]]

if __name__ == "__main__":
    sys.exit(main())
