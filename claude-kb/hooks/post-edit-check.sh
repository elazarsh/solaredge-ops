#!/usr/bin/env bash
# PostToolUse(Write|Edit|MultiEdit): fast syntax check of the file just written.
# Exit 2 feeds the error back to Claude so it fixes it immediately. Silent when fine or unsupported.
set -u
f=$(python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))
except Exception:
    pass' 2>/dev/null)
[ -z "$f" ] && exit 0
[ -f "$f" ] || exit 0
err=""
case "$f" in
  *.py)   err=$(python3 -m py_compile "$f" 2>&1) ;;
  *.sh)   err=$(bash -n "$f" 2>&1) ;;
  *.json) err=$(python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$f" 2>&1) ;;
  *.js|*.mjs|*.cjs) command -v node >/dev/null 2>&1 && err=$(node --check "$f" 2>&1) ;;
  *.yml|*.yaml) python3 -c 'import yaml' 2>/dev/null && err=$(python3 -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1]))' "$f" 2>&1) ;;
esac
if [ -n "$err" ]; then
  echo "Syntax check failed for $f:" >&2
  echo "$err" | head -15 >&2
  exit 2
fi
exit 0
