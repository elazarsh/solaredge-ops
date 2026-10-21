#!/usr/bin/env bash
# Generates the realistic shots. Part 1 and part 2 chains run in parallel.
cd "$(dirname "$0")"
last() { ffmpeg -v error -y -sseof -0.1 -i "$1" -frames:v 1 -q:v 2 "$2"; }
STYLE="Static top-down overhead camera, locked off, no zoom, no camera movement. Realistic phone video, natural slightly slow hand movements, adult woman's hands only, no face. No text, no music, no voices."
part1() {
  python3 veo.py clips/s3_sticky.mp4 frames/f2_after_laptop.jpg "$STYLE One hand takes a small square bright yellow sticky note out of the navy bag and presses it flat onto the middle of the silver laptop lid, smoothing it once, then both hands leave the frame completely and the note stays still on the laptop for the last two seconds. Warm dim evening lamp light. Sound: soft paper rustle." && echo P1 done
}
part2() {
  python3 img.py frames/f4_afternoon.jpg "Realistic smartphone photo shot straight down (top-down, 90 degrees) onto the SAME light oak wooden table with the same framing as the second reference photo, but now in the afternoon: bright, warm natural sunlight from a window at the upper right, cheerful mood. In the upper middle of the frame lies the navy leather tote bag from the first reference photo, relaxed and almost empty, its open top facing the bottom of the frame. A set of house keys with a small red felt heart keychain lies to the left of the bag. The lower 60% of the table is empty. Natural phone-camera look, no text, no people." ../hf/assets/gen/raw/bag_light.jpg frames/f1_evening.jpg || return 1
  python3 veo.py clips/s4_badge.mp4 frames/f4_afternoon.jpg "$STYLE A woman's hands enter from the bottom, pull a white plastic staff ID badge on a colorful lanyard out of the navy bag and lay it flat and straight on the table below the bag, badge face up and fully visible, plain white card with no writing, then the hands leave the frame and the badge stays still. Bright warm afternoon sunlight. Sound: light rustle, soft click of the badge on wood." || return 1
  last clips/s4_badge.mp4 frames/f5_start.jpg
  python3 veo.py clips/s5_drawing_sock.mp4 frames/f5_start.jpg "$STYLE The hands take a folded sheet of paper out of the bag, unfold it and lay it flat on the table: it is a toddler's colorful crayon drawing with a big yellow sun and a smiling stick figure. Then one hand pulls out one tiny mint-green toddler sock with little dinosaurs and drops it next to the drawing. Hands leave the frame. Bright warm afternoon sunlight. Sound: paper unfolding." || return 1
  last clips/s5_drawing_sock.mp4 frames/f6_start.jpg
  python3 veo.py clips/s6_glitter.mp4 frames/f6_start.jpg "$STYLE The hands lift the navy leather bag by its handles, turn it upside down above the table and shake it gently: a big sparkling shower of colorful glitter (gold, pink, silver, turquoise) pours out of the bag and rains down onto the table and the drawing, glitter everywhere, catching the sunlight. Then the hands put the bag down at the top of the frame and leave. Bright warm afternoon sunlight. Sound: soft shaking, glitter sprinkling sparkle." && echo P2 done
}
part1 > p1.log 2>&1 &
part2 > p2.log 2>&1 &
wait
