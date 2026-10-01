#!/usr/bin/env bash
cd "$(dirname "$0")"
last() { ffmpeg -v error -y -sseof -0.1 -i "$1" -frames:v 1 -q:v 2 "$2"; }
STYLE="Static top-down overhead camera, locked off, no zoom, no camera movement. Realistic phone video, natural slightly slow hand movements, adult woman's hands only, no face. No text, no music, no voices."
EVE="Warm dim evening lamp light."
part1() {
  python3 veo.py clips/s2b_chargers.mp4 frames/f2_after_laptop.jpg "$STYLE The hands pull two white chargers with long white cables hopelessly tangled together with black over-ear headphones out of the navy bag and drop the tangle on the table to the right of the silver laptop, try once to untangle it, give up, and leave the frame. $EVE Sound: cables rustling, a soft sigh-like pause." || return 1
  last clips/s2b_chargers.mp4 frames/f2c_start.jpg
  python3 veo.py clips/s2c_coffee.mp4 frames/f2c_start.jpg "$STYLE One hand pulls a takeaway paper coffee cup with a lid out of the side of the navy bag and sets it on the table to the left of the laptop, gives it a tiny shake showing it is still full and cold, and leaves the frame. $EVE Sound: paper cup on wood, liquid slosh." || return 1
  last clips/s2c_coffee.mp4 frames/f3_start.jpg
  python3 veo.py clips/s3b_sticky.mp4 frames/f3_start.jpg "$STYLE One hand takes a small square bright yellow sticky note out of the navy bag and presses it flat onto the middle of the silver laptop lid, smoothing it once, then the hand leaves the frame completely and the note stays still on the laptop for the last three seconds. $EVE Sound: soft paper rustle." && echo P1 done
}
part2() {
  python3 veo.py clips/s5b_star.mp4 frames/f6_start.jpg "$STYLE One hand takes a small shiny gold star sticker out of the navy bag, shows it to the camera for a moment, then peels it and sticks it proudly on the back of the other hand, and both hands stay in frame showing the star sticker on the back of the hand. Bright warm afternoon sunlight. Sound: soft sticker peel." && echo P2 done
}
part1 > p31.log 2>&1 &
part2 > p32.log 2>&1 &
wait
