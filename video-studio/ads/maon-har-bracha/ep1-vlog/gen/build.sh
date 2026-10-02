#!/usr/bin/env bash
# Full rebuild of the vlog version from the committed Veo clips (clips/*.mp4 + tracked quads clips/*.json).
#  1. ui/        → ui.mp4            phone screen only (1080×2590), timeline in final-video seconds (T in ui/index.html)
#  2. foley.py   → assets/foley.wav  keyboard clicks on the exact keystrokes, buzz, taps, send/receive, room tone
#  3. composite  → assets/footage.mp4  UI keyed + perspective-warped onto the green screens per edl.json
#  4. index.html → out/…-raw.mp4     stickers, VO card, referral page, lockup, audio
#  5. loudnorm + QA
# New shots: gen/veo-shots.sh / gen/veo-retry.sh, then gen/track.py clip.mp4 clip.json [--static]; thumb timing: gen/thumb.py.
set -euo pipefail
cd "$(dirname "$0")/.."
TOOLS=../../../tools
(cd ui && npx --yes hyperframes@0.8.96 render -o ../ui.mp4 -f 30 -q high -w 2 --quiet)
python3 gen/foley.py
python3 gen/composite.py edl.json ui.mp4 assets/footage.mp4
npx --yes hyperframes@0.8.96 render -o out/ep1-vlog-v9-raw.mp4 -f 30 -q high -w 2 --quiet
bash $TOOLS/loudnorm.sh out/ep1-vlog-v9-raw.mp4 out/ep1-vlog-v9-norm.mp4
# delivery size (the raw render is ~180 MB because of the film grain)
ffmpeg -v error -y -i out/ep1-vlog-v9-norm.mp4 -c:v libx264 -crf 21 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a copy out/ep1-vlog-v9.2.mp4
bash $TOOLS/ad-qa.sh out/ep1-vlog-v9.2.mp4
