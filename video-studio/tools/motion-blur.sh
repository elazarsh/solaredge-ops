#!/usr/bin/env bash
# Real motion blur: render N subframes per output frame, then average them (ffmpeg tmix).
# Usage (inside a HyperFrames project dir):
#   bash video-studio/tools/motion-blur.sh <out.mp4> [fps=60] [subframes=4] [quality=delivery]
# fps*subframes must be ≤ 240 (HyperFrames limit): 60×4, 30×8, 48×5 …
set -euo pipefail
out="${1:?usage: motion-blur.sh <out.mp4> [fps] [subframes] [quality]}"; fps="${2:-60}"; sub="${3:-4}"; q="${4:-delivery}"
hi=$((fps*sub)); [ "$hi" -le 240 ] || { echo "fps×subframes=$hi > 240" >&2; exit 1; }
tmp="$(mktemp -d)/hi.mp4"
npx --yes hyperframes@0.8.96 render --fps "$hi" --quality "$q" -o "$tmp"
w=$(printf '1%.0s ' $(seq 1 "$sub"))
ffmpeg -hide_banner -loglevel error -y -i "$tmp" \
  -vf "tmix=frames=$sub:weights='$w',select='not(mod(n\,$sub))',setpts=N/($fps*TB)" -r "$fps" \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart "$out"
rm -rf "$(dirname "$tmp")"; echo "$out"
