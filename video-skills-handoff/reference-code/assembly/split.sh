#!/bin/bash
cd "$(dirname "$0")/out"
SRC=${1:-film_v2.mp4}; TAG=${2:-v2}
B=(0 63.1 176.8 281.4 383.8 461.3 9999)
for i in 0 1 2 3 4 5; do
  s=${B[$i]}; e=${B[$((i+1))]}
  ffmpeg -v error -y -ss $s -to $e -i $SRC -vf scale=1280:720 -c:v libx264 -preset medium -crf 28 -maxrate 1800k -bufsize 3600k -c:a aac -b:a 96k -movflags +faststart part_${TAG}_$((i+1)).mp4
done
ls -la part_${TAG}_*.mp4
