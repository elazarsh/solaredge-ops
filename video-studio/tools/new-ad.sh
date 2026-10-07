#!/usr/bin/env bash
# Start a new ad folder with the ad-creative templates.
# Usage: bash video-studio/tools/new-ad.sh <slug> <age>
#   age: kids | teens | young | adults | parents | mature | seniors
set -euo pipefail
slug="${1:?usage: new-ad.sh <slug> <age>}"
age="${2:?choose age: kids | teens | young | adults | parents | mature | seniors}"
case "$age" in kids|teens|young|adults|parents|mature|seniors) ;; *) echo "unknown age: $age" >&2; exit 1;; esac
root="$(cd "$(dirname "$0")/../.." && pwd)"
tpl="$root/.claude/skills/ad-creative/templates"
dir="$root/video-studio/ads/$slug"
[ -e "$dir" ] && { echo "exists: $dir" >&2; exit 1; }
mkdir -p "$dir/assets" "$dir/out"
for f in brief concepts storyboard; do
  sed -e "s/{{SLUG}}/$slug/g" -e "s/{{AGE}}/$age/g" "$tpl/$f.md" > "$dir/$f.md"
done
echo "$dir"
