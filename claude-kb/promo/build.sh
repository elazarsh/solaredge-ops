#!/usr/bin/env bash
# Builds claude-kb-promo.mp4: frames (Playwright) + synthetic audio (numpy) -> H.264/AAC via ffmpeg.
# Needs: node + playwright (PLAYWRIGHT_MODULE=path to module if not resolvable), chromium, ffmpeg, python3+numpy.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$(mktemp -d)}"
mkdir -p "$WORK/frames"
python3 "$HERE/audio.py" "$WORK/audio.wav"
node "$HERE/render.js" "$HERE/promo.html" "$WORK/frames" 30 30
ffmpeg -loglevel error -y -framerate 30 -i "$WORK/frames/f_%05d.png" -i "$WORK/audio.wav" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$HERE/claude-kb-promo.mp4"
echo "done: $HERE/claude-kb-promo.mp4"
