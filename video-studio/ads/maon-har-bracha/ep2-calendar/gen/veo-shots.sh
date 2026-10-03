#!/usr/bin/env bash
# Veo shots for ep2 (Esti's phone). The phone screen must stay flat chroma green so the calendar UI can be keyed in.
# Retries with a different sound line (Veo sometimes rejects on its audio filter) and falls back to the fast model.
cd "$(dirname "$0")/.."
KEEP="The phone screen stays one uniform flat bright chroma-key green the entire time: no content, no icons, no text, no reflections ever appear on it. Realistic handheld phone video with very subtle natural movement, no zoom, no cuts, no camera moves. Adult woman's hands only, no face. Soft early-morning sunrise light."
H="She holds the phone steadily in her left hand, upright and facing the camera, almost perfectly still."
SOUNDS=("Sound: quiet kitchen room tone and a distant bird." "Sound: a wall clock ticking softly." "Sound: calm morning, a spoon clinks on a glass once.")
shot() { # name frame prompt
  for m in veo-3.1-generate-preview veo-3.1-fast-generate-preview; do
    for s in "${SOUNDS[@]}"; do
      [ -f "clips/$1.mp4" ] && return 0
      python3 gen/veo.py "clips/$1.mp4" "frames/$2.jpg" "$KEEP $3 $s" $m && return 0
      sleep 20
    done
  done
}
shot table table "The smartphone lies flat on the stone counter. It vibrates briefly twice, buzzing on the stone. Then a woman's hand enters from the bottom right, her index finger taps the middle of the screen once, and the hand leaves the frame." > gen/v-table.log 2>&1 &
sleep 30
shot read hand "$H She calmly reads for the whole clip. No finger touches the screen; her other hand stays out of the frame. Only tiny natural breathing movement." > gen/v-read.log 2>&1 &
sleep 30
shot tap hand "$H For two seconds she reads. Then her right index finger comes in from the bottom right, taps once in the middle of the screen, and leaves the frame. She reads calmly. Around the sixth second the finger comes back, taps once on the lower middle of the screen, and leaves again." > gen/v-tap.log 2>&1 &
sleep 30
shot swipe hand "$H For two seconds she reads. Then her right index finger comes in from the right and swipes once horizontally from right to left across the middle of the screen, and leaves the frame. She reads calmly for two seconds, then swipes once more the same way, and the finger leaves the frame." > gen/v-swipe.log 2>&1 &
wait
ls -la clips
