#!/usr/bin/env bash
# Opt-in installer for vetted community skills. Prints the commands, asks for confirmation, then runs them.
# Usage: install-community-skills.sh [video|design|quality|all] [--dry-run] [--yes]
# Never run without reading the repos you are installing (skills may contain scripts).
set -euo pipefail
SET="${1:-video}"; DRY=0; YES=0
for a in "$@"; do case "$a" in --dry-run) DRY=1;; --yes) YES=1;; esac; done
declare -a CMDS
video()   { CMDS+=("npx skills add heygen-com/hyperframes" "npx skills add https://github.com/greensock/gsap-skills" "npx skills add https://github.com/pixel-point/animate-text --skill animate-text"); }
three()   { CMDS+=("npx skills add https://github.com/cloudai-x/threejs-skills"); }
design()  { CMDS+=("npx skills add anthropics/skills --skill frontend-design" "npx skills add anthropics/skills --skill canvas-design" "npx skills add vercel-labs/agent-skills --skill web-design-guidelines"); }
quality() { CMDS+=("npx skills add obra/superpowers --skill brainstorming" "npx skills add obra/superpowers --skill systematic-debugging"); }
case "$SET" in video) video;; design) design;; quality) quality;; three) three;; all) video; three; design; quality;; *) echo "unknown set: $SET"; exit 1;; esac
command -v npx >/dev/null || { echo "npx (Node.js) is required"; exit 1; }
echo "Will run:"; printf '  %s\n' "${CMDS[@]}"
[ "$DRY" = 1 ] && { echo "(dry run)"; exit 0; }
if [ "$YES" != 1 ]; then read -r -p "Have you reviewed these repos and want to proceed? [y/N] " ok; [ "$ok" = "y" ] || { echo "aborted"; exit 1; }; fi
for c in "${CMDS[@]}"; do echo ">> $c"; eval "$c" || echo "FAILED: $c"; done
echo "Done. Restart Claude Code to load new skills. Re-read what was installed under ~/.claude/skills or .agents/skills."
