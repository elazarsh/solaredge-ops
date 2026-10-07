#!/usr/bin/env bash
# Two-thumb typing on a green-toned keyboard (frames/hands2x-kb.jpg from gen/chroma-keyboard.py), with a press-and-hold on ⌫.
cd "$(dirname "$0")/.."
KEEP="The phone screen and its green on-screen keyboard stay exactly as they are the entire time: all green, nothing on the screen changes, no new content, no reflections. Realistic handheld phone video, very subtle natural movement, no zoom, no cuts. Adult woman's hands only. Warm morning light."
ACT="She holds the phone with both hands and types on the on-screen keyboard with BOTH thumbs, alternating left and right thumb on the keys, for two seconds. Then her right thumb presses and holds the backspace key, the wide key at the far right end of the TOP row of the keyboard, for one second, deleting. Then she continues typing with both thumbs alternating until the end."
SOUNDS=("Sound: soft phone keyboard taps." "Sound: gentle kitchen room tone and soft taps." "Sound: a wall clock ticking softly.")
shot() {
  for s in "${SOUNDS[@]}"; do
    [ -f "$1" ] && return 0
    python3 gen/veo.py "$1" frames/hands2x-kb.jpg "$KEEP $ACT $s" veo-3.1-fast-generate-preview && return 0
    sleep 30
  done
}
shot clips/type3a.mp4 > gen/v-type3a.log 2>&1 &
sleep 45
shot clips/type3b.mp4 > gen/v-type3b.log 2>&1 &
wait
