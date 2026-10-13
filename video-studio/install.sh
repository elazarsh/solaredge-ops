#!/usr/bin/env bash
# Install the video-studio skills and agents for your user (works in every project).
# Usage:  bash video-studio/install.sh [--force]      Env: CLAUDE_HOME (default: ~/.claude)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="${CLAUDE_HOME:-$HOME/.claude}"
force=0
[[ "${1:-}" == "--force" ]] && force=1

mkdir -p "$dest/skills" "$dest/agents"
copied=0
skipped=0

for src in "$here"/skills/*/; do
  name="$(basename "$src")"
  target="$dest/skills/$name"
  if [[ -e "$target" && $force -eq 0 ]] && ! diff -rq --exclude=__pycache__ "$src" "$target" >/dev/null 2>&1; then
    echo "SKIP  skills/$name (exists and differs; use --force to overwrite)"; skipped=$((skipped+1)); continue
  fi
  rm -rf "$target"; cp -R "$src" "$target"; find "$target" -name __pycache__ -prune -exec rm -rf {} +
  echo "OK    skills/$name"; copied=$((copied+1))
done

for src in "$here"/agents/*.md; do
  name="$(basename "$src")"
  target="$dest/agents/$name"
  if [[ -e "$target" && $force -eq 0 ]] && ! diff -q "$src" "$target" >/dev/null 2>&1; then
    echo "SKIP  agents/$name (exists and differs; use --force to overwrite)"; skipped=$((skipped+1)); continue
  fi
  cp "$src" "$target"; echo "OK    agents/$name"; copied=$((copied+1))
done

echo "Done: $copied installed, $skipped skipped, into $dest"
echo "Start a NEW Claude Code session, then say: \"/video-studio\" or just describe the video you want."
