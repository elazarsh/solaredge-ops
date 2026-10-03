#!/usr/bin/env bash
# Full rebuild of ep2 "היומן" from the committed Veo clips (clips/*.mp4 + tracked quads clips/*.json).
#  1. ui/        → ui.mp4               phone screen only (1080×2590), timeline in final-video seconds (T in ui/index.html)
#  2. foley.py   → assets/foley.wav     pings, taps, swipes, year ticks, WhatsApp pops, room tone (reads T)
#  3. composite  → assets/footage.mp4   calendar UI keyed + perspective-warped onto the green screens per edl.json
#  4. index.html → out/…-raw.mp4        opening sticker, science card, signature card, referral page, lockup, audio
#  5. loudnorm + delivery encode + QA
# New shots: gen/veo-shots.sh, then gen/track.py clip.mp4 clip.json [--static]; finger timing: gen/thumb.py <clip>.
# Music/VO: gen/audio.py music|vo (the TTS take is trimmed to the line; check with gen/hear.py).
set -euo pipefail
cd "$(dirname "$0")/.."
TOOLS=../../../tools
(cd ui && npx --yes hyperframes@0.8.96 render -o ../ui.mp4 -f 30 -q high -w 2 --quiet)
python3 gen/foley.py
python3 gen/composite.py edl.json ui.mp4 assets/footage.mp4
npx --yes hyperframes@0.8.96 render -o out/ep2-calendar-raw.mp4 -f 30 -q high -w 2 --quiet
bash $TOOLS/loudnorm.sh out/ep2-calendar-raw.mp4 out/ep2-calendar-norm.mp4
ffmpeg -v error -y -i out/ep2-calendar-norm.mp4 -c:v libx264 -crf 21 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a copy out/ep2-calendar-v1.mp4
bash $TOOLS/ad-qa.sh out/ep2-calendar-v1.mp4
