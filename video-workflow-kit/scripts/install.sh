#!/usr/bin/env bash
# video-workflow-kit installer. Default = DRY RUN (prints what it would do). Pass --yes to run.
# Read it before running. It does not touch secrets and makes no paid API calls.
set -euo pipefail
YES=0; [ "${1:-}" = "--yes" ] && YES=1
KIT="$(cd "$(dirname "$0")/.." && pwd)"
run() { echo "+ $*"; if [ "$YES" = 1 ]; then "$@"; fi; }

echo "== 1. own skills -> ./.claude/skills (existing folders are NOT overwritten)"
run mkdir -p .claude/skills
for d in "$KIT"/skills/*/; do
  n="$(basename "$d")"
  if [ -e ".claude/skills/$n" ]; then echo "skip (exists): $n"; else run cp -r "$d" ".claude/skills/$n"; fi
done
[ -e .claude/skills/README.md ] || run cp "$KIT/skills/README.md" .claude/skills/README.md

echo "== 2. HyperFrames skills (third-party, from source)"
run npx --yes skills add heygen-com/hyperframes -y

echo "== 3. four selected Google skills (NOT all 178)"
run npx --yes skills add google/skills --skill gemini-api --skill gemini-live-api --skill gemini-interactions-api --skill finding-google-skills -y

echo "== 4. python packages"
run python3 -m pip install numpy scipy opencv-python-headless pillow

echo "== 5. browser for local rendering"
run npx --yes hyperframes browser ensure

echo "== 6. plugins: merge $KIT/settings.snippet.json into .claude/settings.json by hand (not automated on purpose)"
echo "== 7. keys: add GEMINI_API_KEY (and optionally OPENAI_API_KEY) as environment secrets, NOT in chat; then open a new session"
echo "== 8. free checks afterwards:"
echo "   python3 .claude/skills/ai-api-setup/scripts/check_env.py"
echo "   npx hyperframes doctor"
if [ "$YES" != 1 ]; then echo "(dry run: nothing was changed. Re-run with --yes)"; fi
