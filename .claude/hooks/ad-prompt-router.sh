#!/bin/bash
# When the user asks for an ad / video in Hebrew or English, remind Claude of the ad workflow skills.
set -uo pipefail
prompt=$(python3 -c 'import json,sys;print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null)
if grep -qiE 'פרסומ|מודע|קמפיין|סרטון|קריינ|רילס|טיקטוק|סטורי|\bads?\b|advert|commercial|promo|reels?\b' <<<"$prompt"; then
  echo "Ad/video request detected: follow /ad-creative (brief → diagnosis → strategy → 3 concepts → storyboard → production → QA) and /hebrew-video for any Hebrew text or voiceover. Get approval on concept and script before writing composition code."
fi
exit 0
