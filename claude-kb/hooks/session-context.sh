#!/usr/bin/env bash
# SessionStart: print short context that Claude receives at session start.
# Keeps it brief: date, git state, handoff file presence, knowledge-base pointer.
set -u
echo "## Session context (auto)"
echo "- Date: $(date +%Y-%m-%d) ($(date +%Z))"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  br=$(git branch --show-current 2>/dev/null)
  dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  echo "- Git: branch '${br:-detached}', ${dirty} changed file(s)"
fi
for f in HANDOFF.md .claude/HANDOFF.md; do
  if [ -f "$f" ]; then echo "- $f exists: read it first and verify against the actual files before assuming anything is done."; fi
done
for f in CLAUDE.md AGENTS.md; do
  [ -f "$f" ] && echo "- Project instructions: $f"
done
echo "- Personal knowledge base: skills in ~/.claude/skills (index: kb-router skill). Hebrew user: reply in Hebrew unless asked otherwise; apply verify-and-safety-gates before declaring done."
exit 0
