#!/usr/bin/env bash
# Veo sometimes rejects a clip on its audio filter ("issue with the audio"); retry with a different sound line.
cd "$(dirname "$0")/.."
KEEP="The phone screen stays one uniform flat bright chroma-key green the entire time, nothing ever appears on it. Realistic handheld phone video, very subtle natural movement, no zoom, no cuts. Adult woman's hands only. Warm morning light."
H="She holds the phone steadily in her left hand, facing the camera."
SOUNDS=("Sound: a wall clock ticking softly." "Sound: gentle kitchen room tone and a distant bird." "Sound: quiet morning, a spoon clinks on a mug once.")
shot() { # out prompt
  for s in "${SOUNDS[@]}"; do
    [ -f "$1" ] && return 0
    python3 gen/veo.py "$1" frames/hand2.jpg "$KEEP $H $2 $s" veo-3.1-fast-generate-preview && return 0
    sleep 30
  done
}
shot clips/read.mp4 "She calmly reads; her right thumb rests on the phone's lower frame below the screen and never covers the screen." > gen/v-read.log 2>&1 &
sleep 40
shot clips/tap.mp4 "For three seconds she reads. Then her right thumb reaches up and taps once on the middle of the screen, and goes back to rest near the bottom corner." > gen/v-tap.log 2>&1 &
wait
