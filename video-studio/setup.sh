#!/usr/bin/env bash
# Rebuilds the video toolchain in a fresh cloud container (containers are ephemeral).
# Usage: bash video-studio/setup.sh
set -uo pipefail
cd "$(dirname "$0")"

echo "==> ffmpeg + Hebrew system fonts"
if ! command -v ffmpeg >/dev/null; then
  # Some PPAs are blocked by the egress proxy; their warnings are harmless.
  apt-get update -qq >/dev/null 2>&1 || true
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg fonts-noto-core sox >/dev/null
fi
mkdir -p ~/.fonts && cp remotion/public/fonts/*.ttf ~/.fonts/ && fc-cache -f >/dev/null

echo "==> Python audio analysis (beat grid)"
python3 -c "import numpy" 2>/dev/null || pip install -q numpy 2>/dev/null

echo "==> Remotion project dependencies"
(cd remotion && npm install --no-audit --no-fund --silent)

echo "==> HyperFrames CLI + its headless Chrome"
command -v hyperframes >/dev/null || npm install -g hyperframes@0.8.96 --silent
hyperframes browser ensure >/dev/null

echo "==> Checks"
ffmpeg -version | head -1
hyperframes doctor 2>&1 | grep -E '✓|✗' | grep -E 'FFmpeg|Chrome' || true
echo "Done. Render a smoke test: (cd video-studio/remotion && npx remotion render HebrewSmokeTest out/smoke-test.mp4)"
