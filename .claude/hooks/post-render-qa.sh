#!/bin/bash
# After a render command, run ad-qa.sh on the newest MP4 and hand the report to Claude.
set -uo pipefail
input=$(cat)
cmd=$(python3 -c 'import json,sys;print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' <<<"$input" 2>/dev/null)
grep -qE '(remotion|hyperframes)[^|;&]* render|ffmpeg .*\.mp4|motion-blur\.sh' <<<"$cmd" || exit 0
grep -qE -- '--help|-h( |$)|--version' <<<"$cmd" && exit 0
cd "${CLAUDE_PROJECT_DIR:-.}"
f=$(find video-studio -name '*.mp4' -mmin -3 -not -path '*/node_modules/*' -not -name '*.norm.mp4' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
[ -n "$f" ] || exit 0
report=$(bash video-studio/tools/ad-qa.sh "$f" 1 180 2>&1)
python3 -c 'import json,sys
f,r=sys.argv[1],sys.argv[2]
msg=f"Automatic QA of {f}:\n{r}\nFix FAIL lines before delivering; then review visually with video-studio/tools/contact-sheet.sh and safe-zone-check.sh (see /ad-creative references/review.md)."
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":msg}}))' "$f" "$report"
