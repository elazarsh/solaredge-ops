#!/usr/bin/env bash
# Two-thumb typing with a visible delete moment (v9.1). The delete taps are located with gen/thumb.py and the ⌫ key is placed there.
cd "$(dirname "$0")/.."
KEEP="The phone screen stays one uniform flat bright chroma-key green the entire time, nothing ever appears on it. Realistic handheld phone video, very subtle natural movement, no zoom, no cuts. Adult woman's hands only. Warm morning light."
ACT="She holds the phone with both hands and types a message with BOTH thumbs, alternating left and right thumb quickly on the lower third of the screen for two seconds. Then she pauses, and her right thumb taps the same single spot near the right edge of the screen, at about 60 percent of the screen height, five times in a row, as if pressing delete. Then she types again with both thumbs alternating until the end."
SOUNDS=("Sound: soft phone keyboard taps." "Sound: gentle kitchen room tone and soft taps." "Sound: a wall clock ticking softly.")
shot() {
  for s in "${SOUNDS[@]}"; do
    [ -f "$1" ] && return 0
    python3 gen/veo.py "$1" frames/hands2x.jpg "$KEEP $ACT $s" veo-3.1-fast-generate-preview && return 0
    sleep 30
  done
}
shot clips/type2a.mp4 > gen/v-type2a.log 2>&1 &
sleep 45
shot clips/type2b.mp4 > gen/v-type2b.log 2>&1 &
wait
