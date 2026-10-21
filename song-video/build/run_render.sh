#!/bin/sh
# Render all frames with 4 parallel Chromium workers into out/frames. usage: run_render.sh [total_frames]
TOTAL=${1:-5948}; W=4; PER=$(( (TOTAL + W - 1) / W ))
mkdir -p out/frames
i=0
while [ $i -lt $W ]; do
  a=$(( i * PER )); b=$(( a + PER )); [ $b -gt $TOTAL ] && b=$TOTAL
  node render.mjs --out out/frames --from $a --to $b > out/worker$i.log 2>&1 &
  i=$(( i + 1 ))
done
wait
echo "ALL DONE $(ls out/frames | wc -l) frames"
