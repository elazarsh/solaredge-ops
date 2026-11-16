#!/usr/bin/env python3
"""Deterministic digest of Claude Code session transcripts (JSONL).

Usage:
  python3 session_digest.py <transcript.jsonl> [more.jsonl ...] [--out DIR] [--top N]

Reads only local files, makes no network calls and no LLM calls. Output:
  DIR/digest.json   machine-readable metrics
  DIR/digest.md     short report (measured vs unknown is explicit)
A field the transcript does not expose is reported as null, never as 0.
"""
import argparse, collections, json, os, re, sys

def norm_cmd(c: str) -> str:
    """Normalise a shell command so repeated work groups together."""
    c = re.sub(r"\s+", " ", c.strip())
    c = re.sub(r"/tmp/[^\s'\"]+", "<TMP>", c)
    c = re.sub(r"\b[0-9a-f]{7,40}\b", "<HASH>", c)
    c = re.sub(r"\b\d+\b", "<N>", c)
    c = re.sub(r"'[^']{12,}'|\"[^\"]{12,}\"", "<STR>", c)
    return c[:140]

def text_len(content) -> int:
    if isinstance(content, str):
        return len(content)
    n = 0
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict):
                if b.get("type") == "text":
                    n += len(b.get("text", ""))
                elif b.get("type") == "tool_result":
                    n += text_len(b.get("content"))
                elif b.get("type") == "image":
                    n += 1500  # rough, unmeasured placeholder; flagged in report
    return n

def digest(paths):
    tot = collections.Counter(); per_tool_calls = collections.Counter()
    per_tool_result_chars = collections.Counter(); cmds = collections.Counter()
    errors = collections.Counter(); notif = 0; stop_hook = 0
    tool_by_id = {}; msgs = 0; cache_read_max = 0; sessions = set(); big = []; att = collections.Counter(); att_n = collections.Counter()
    for p in paths:
        for line in open(p, encoding="utf-8", errors="replace"):
            try: d = json.loads(line)
            except Exception: continue
            t = d.get("type"); m = d.get("message") if isinstance(d.get("message"), dict) else {}
            if t == "attachment":
                a = d.get("attachment") or {}; k = a.get("type", "?")
                att[k] += len(re.sub(r"[A-Za-z0-9+/=]{200,}", "", json.dumps(a, ensure_ascii=False))); att_n[k] += 1
            if t in ("user", "attachment", "system"):
                body = d.get("message", d)
                if t == "user" and isinstance(m.get("content"), list):
                    imgs = sum(1 for x in m["content"] if isinstance(x, dict) and x.get("type") == "image")
                    size = text_len(m["content"])
                    first = next((x for x in m["content"] if isinstance(x, dict) and x.get("type") == "tool_result"), None)
                    label = ("tool_result:" + str(first.get("tool_use_id", ""))[-8:]) if first else ("text+%d image(s)" % imgs if imgs else "user text")
                else:
                    raw = json.dumps(body, ensure_ascii=False)
                    size = len(re.sub(r"[A-Za-z0-9+/=]{200,}", "", raw))  # drop base64 blobs
                    label = re.sub(r"\s+", " ", re.sub(r'[\\"{}\[\]]', " ", raw))[:70].strip()
                big.append((size, t, label))
            sessions.add(d.get("sessionId") or os.path.basename(p))
            if t == "assistant":
                msgs += 1
                u = m.get("usage") or {}
                tot["input"] += u.get("input_tokens", 0) or 0
                tot["cache_creation"] += u.get("cache_creation_input_tokens", 0) or 0
                c_read = u.get("cache_read_input_tokens", 0) or 0
                tot["cache_read"] += c_read; cache_read_max = max(cache_read_max, c_read)
                tot["output"] += u.get("output_tokens", 0) or 0
                tot["thinking"] += (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
                for b in m.get("content") or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        name = b.get("name", "?"); per_tool_calls[name] += 1
                        tool_by_id[b.get("id")] = name
                        if name == "Bash":
                            cmds[norm_cmd((b.get("input") or {}).get("command", ""))] += 1
            elif t == "user":
                c = m.get("content")
                if isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            nm = tool_by_id.get(b.get("tool_use_id"), "?")
                            per_tool_result_chars[nm] += text_len(b.get("content"))
                            if b.get("is_error"): errors[nm] += 1
                txt = json.dumps(c, ensure_ascii=False) if c is not None else ""
                if "queued-remote-notifications" in txt: notif += 1
                if "Stop hook feedback" in txt: stop_hook += 1
    repeated = [(c, n) for c, n in cmds.most_common() if n >= 3]
    return {
        "sessions": len(sessions), "assistant_turns": msgs,
        "tokens": dict(tot) if msgs else None,
        "peak_context_cache_read": cache_read_max or None,
        "tool_calls": dict(per_tool_calls.most_common()),
        "tool_result_chars": dict(per_tool_result_chars.most_common()),
        "tool_errors": dict(errors),
        "repeated_bash_patterns": [{"pattern": c, "count": n} for c, n in repeated],
        "attachment_chars_by_type": [{"type": k, "chars": n, "count": att_n[k]} for k, n in att.most_common()],
        "largest_context_items_chars": [{"chars": n, "type": ty, "starts_with": lb} for n, ty, lb in sorted(big, reverse=True)[:10]],
        "notification_wakes": notif, "stop_hook_feedbacks": stop_hook,
        "notes": ["tool_result_chars is characters, not tokens (images counted as a fixed 1500 placeholder)",
                  "cache_read is re-reading the same context each turn; it is cheap per token but accumulates"],
    }

def to_md(d, top):
    L = ["# Session digest", ""]
    L.append(f"- sessions: {d['sessions']} | assistant turns: {d['assistant_turns']}")
    t = d["tokens"]
    if t:
        L.append(f"- tokens (measured): input {t.get('input',0):,} | output {t.get('output',0):,} (thinking {t.get('thinking',0):,}) | "
                 f"cache_creation {t.get('cache_creation',0):,} | cache_read {t.get('cache_read',0):,}")
    else:
        L.append("- tokens: unknown (no usage in transcript)")
    L.append(f"- peak context re-read in one turn: {d['peak_context_cache_read']:,}" if d["peak_context_cache_read"] else "- peak context: unknown")
    L.append(f"- PR/notification wake-ups: {d['notification_wakes']} | stop-hook feedbacks: {d['stop_hook_feedbacks']}")
    L += ["", "## Tool calls (count | result chars)"]
    for k, n in list(d["tool_calls"].items())[:top]:
        L.append(f"- {k}: {n} | {d['tool_result_chars'].get(k, 0):,} chars | errors {d['tool_errors'].get(k, 0)}")
    L += ["", "## Harness injections by type (chars; listings and hooks re-sent into context)"]
    for r in d["attachment_chars_by_type"][:top]:
        L.append(f"- {r['type']}: {r['chars']:,} chars in {r['count']} injections")
    L += ["", "## Largest text items that entered context (chars; images count as a fixed placeholder)"]
    for r in d["largest_context_items_chars"][:top]:
        L.append(f"- {r['chars']:,} [{r['type']}] {r['starts_with']}")
    L += ["", "## Repeated shell patterns (3+ times): candidates for a script"]
    for r in d["repeated_bash_patterns"][:top]:
        L.append(f"- x{r['count']}: `{r['pattern']}`")
    if not d["repeated_bash_patterns"]:
        L.append("- none")
    L += ["", "## Notes"] + [f"- {n}" for n in d["notes"]]
    return "\n".join(L) + "\n"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="."); ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()
    d = digest(a.files); os.makedirs(a.out, exist_ok=True)
    json.dump(d, open(os.path.join(a.out, "digest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    md = to_md(d, a.top); open(os.path.join(a.out, "digest.md"), "w", encoding="utf-8").write(md)
    print(md)

if __name__ == "__main__":
    sys.exit(main())
