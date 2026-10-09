#!/usr/bin/env python3
"""UserPromptSubmit hook: match the prompt against router-rules.json and print a short hint
naming the personal-knowledge-base skills that apply. Stdout is added to Claude's context.
Never blocks. Edit router-rules.json to tune keywords."""
import json, os, re, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

prompt = (data.get("prompt") or "").lower()
if len(prompt) < 4:
    sys.exit(0)

here = os.path.dirname(os.path.abspath(__file__))
candidates = [os.path.join(here, "router-rules.json"),
              os.path.expanduser("~/.claude/hooks/router-rules.json")]
rules = None
for p in candidates:
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                rules = json.load(f)
            break
        except Exception:
            pass
if not rules:
    sys.exit(0)

hits = []
for rule in rules.get("rules", []):
    kws = [k.lower() for k in rule.get("keywords", [])]
    matched = [k for k in kws if k in prompt]
    if matched:
        hits.append((len(matched), rule))

if not hits:
    sys.exit(0)

hits.sort(key=lambda t: -t[0])
seen, skills = set(), []
for _, rule in hits[:4]:
    for s in rule.get("skills", []):
        if s not in seen:
            seen.add(s)
            skills.append(s)
skills = skills[:6]
always = rules.get("always", [])
msg = "KB router: this request likely matches skill(s): " + ", ".join(skills) + \
      ". Load them with the Skill tool before starting if they fit."
if always:
    msg += " Cross-cutting: " + ", ".join(always) + "."
print(msg)
sys.exit(0)
