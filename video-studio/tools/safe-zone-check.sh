#!/usr/bin/env bash
# Frames with the 9:16 Reels/TikTok UI zones drawn on (red = covered by app UI, green = safe box).
# Usage: bash video-studio/tools/safe-zone-check.sh <video> [out.png] [times="0.5 3 middle end-2"]
set -euo pipefail
f="${1:?usage: safe-zone-check.sh <video> [out.png]}"; out="${2:-${f%.*}.safezone.png}"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
times="${3:-0.5 3 $(awk -v d="$dur" 'BEGIN{printf "%.2f %.2f", d/2, d-2}')}"
tmp=$(mktemp -d); i=0
for t in $times; do
  ffmpeg -hide_banner -loglevel error -y -ss "$t" -i "$f" -frames:v 1 -vf \
"scale=1080:1920,drawbox=x=0:y=0:w=iw:h=ih*0.14:color=red@0.35:t=fill,drawbox=x=0:y=ih*0.65:w=iw:h=ih*0.35:color=red@0.35:t=fill,drawbox=x=iw-140:y=ih*0.35:w=140:h=ih*0.30:color=orange@0.3:t=fill,drawbox=x=iw*0.06:y=ih*0.14:w=iw*0.88:h=ih*0.51:color=lime@0.9:t=4,scale=360:-2,drawtext=text='t=$t':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6" \
    "$tmp/$(printf %02d $i).png"; i=$((i+1))
done
ffmpeg -hide_banner -loglevel error -y -pattern_type glob -i "$tmp/*.png" -vf "tile=${i}x1:padding=6:color=gray" -frames:v 1 "$out"
rm -rf "$tmp"; echo "$out"
