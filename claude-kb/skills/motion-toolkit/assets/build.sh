#!/usr/bin/env bash
# One-command build: vendor setup (once) -> deterministic render with motion blur -> procedural audio -> mux to MP4.
# Usage: build.sh <project_dir> [composition=index.html] [out=video.mp4]
# Config via env: FPS=30 DURATION=30 W=1080 H=1920 SUB=4 SHUTTER=0.5 WORKERS=4 BPM=120 ENERGY="0:0.3,4:0.8" KEY=A
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; P="$(cd "$1" && pwd)"; COMP="${2:-index.html}"; OUT="${3:-video.mp4}"
FPS="${FPS:-30}"; DURATION="${DURATION:-30}"; W="${W:-1080}"; H="${H:-1920}"; SUB="${SUB:-4}"; SHUTTER="${SHUTTER:-0.5}"; WORKERS="${WORKERS:-4}"
BPM="${BPM:-120}"; ENERGY="${ENERGY:-0:0.3,4:0.8}"; KEY="${KEY:-A}"
[ -f "$P/vendor/gsap.min.js" ] || "$HERE/setup.sh" "$P"
cp "$HERE/engine.js" "$P/vendor/engine.js"
export PLAYWRIGHT_MODULE="$P/.deps/node_modules/playwright"
FR="$P/.frames"; rm -rf "$FR"; mkdir -p "$FR"
node "$HERE/render.js" "$P/$COMP" "$FR" --fps "$FPS" --duration "$DURATION" --w "$W" --h "$H" --sub "$SUB" --shutter "$SHUTTER" --workers "$WORKERS"
python3 "$HERE/sfx.py" "$FR/cues.json" "$FR/audio.wav" --duration "$DURATION" --bpm "$BPM" --energy "$ENERGY" --key "$KEY"
# average the SUB sub-frames of every frame (temporal supersampling = real motion blur), keep one output frame per group
if [ "$SUB" -gt 1 ]; then
  VF="tmix=frames=${SUB},select='eq(mod(n\,${SUB})\,$((SUB-1)))',setpts=N/${FPS}/TB"; IN_FPS=$((FPS*SUB))
else VF="setpts=N/${FPS}/TB"; IN_FPS=$FPS; fi
ffmpeg -loglevel error -y -framerate "$IN_FPS" -i "$FR/s_%06d.png" -i "$FR/audio.wav" -vf "$VF,format=yuv420p" \
  -r "$FPS" -c:v libx264 -preset slow -crf 16 -tune animation -c:a aac -b:a 256k -shortest -movflags +faststart "$P/$OUT"
echo "built $P/$OUT"
