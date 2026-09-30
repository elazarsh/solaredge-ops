#!/usr/bin/env bash
# Grid of frames (with timestamps) so Claude can Read one PNG and review the whole ad visually.
# Usage: bash video-studio/tools/contact-sheet.sh <video> [out.png] [cols=4] [rows=3]
set -euo pipefail
f="${1:?usage: contact-sheet.sh <video> [out.png] [cols] [rows]}"; out="${2:-${f%.*}.sheet.png}"
cols="${3:-4}"; rows="${4:-3}"; n=$((cols*rows))
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
fps=$(awk -v d="$dur" -v n="$n" 'BEGIN{printf "%.4f", n/d}')
ffmpeg -hide_banner -loglevel error -y -i "$f" -frames:v 1 -vf \
  "fps=$fps,scale=270:-2,drawtext=text='%{pts\:hms}':x=8:y=8:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6,tile=${cols}x${rows}:padding=6:color=gray" \
  "$out"
echo "$out"
