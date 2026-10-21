#!/bin/bash
# Rebuild the video toolchain in a fresh cloud container (ffmpeg, fonts, Remotion, HyperFrames).
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "$CLAUDE_PROJECT_DIR"
bash video-studio/setup.sh >/tmp/video-studio-setup.log 2>&1 \
  && echo "video-studio toolchain ready (ffmpeg, Hebrew fonts, Remotion, HyperFrames)." \
  || echo "video-studio setup failed; see /tmp/video-studio-setup.log"
