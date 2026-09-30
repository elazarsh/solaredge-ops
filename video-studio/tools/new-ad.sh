#!/usr/bin/env bash
# Start a new ad folder with the ad-creative templates.
# Usage: bash video-studio/tools/new-ad.sh <slug>
set -euo pipefail
slug="${1:?usage: new-ad.sh <slug>}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
tpl="$root/.claude/skills/ad-creative/templates"
dir="$root/video-studio/ads/$slug"
[ -e "$dir" ] && { echo "exists: $dir" >&2; exit 1; }
mkdir -p "$dir/assets" "$dir/out"
for f in brief concepts storyboard; do
  sed "s/{{SLUG}}/$slug/g" "$tpl/$f.md" > "$dir/$f.md"
done
echo "$dir"
