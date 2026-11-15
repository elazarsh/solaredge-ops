#!/bin/bash
# צילום כל הפריימים של page.html (N workers במקביל) והרכבת mp4 עם קול.
# שימוש: bash render.sh <dir עם page.html> [--audio mix.wav] [--out film.mp4] [--workers 4] [--page page.html] [--fps 24]
# כל worker מצלם כל N-י פריים (קבצים קיימים מדולגים => אפשר להמשיך אחרי הפסקה). MAXF=240 לבדיקה קצרה (10 שניות).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DIR="$1"; shift
AUDIO=""; OUT="film.mp4"; NW=4; PAGE="page.html"; FPS=24
while [ $# -gt 0 ]; do case "$1" in --audio) AUDIO="$2";; --out) OUT="$2";; --workers) NW="$2";; --page) PAGE="$2";; --fps) FPS="$2";; esac; shift 2; done
FR="$DIR/frames"; mkdir -p "$FR"; PIDS=()
for ((w=0; w<NW; w++)); do node "$HERE/render_frames.js" "$DIR" $w $NW $((8800+w)) --page "$PAGE" --out "$FR" --fps $FPS & PIDS+=($!); done
for p in "${PIDS[@]}"; do wait $p; done
N=$(ls "$FR"/*.jpg | wc -l); echo "frames: $N"
if [ -n "$AUDIO" ]; then
  ffmpeg -v error -y -framerate $FPS -i "$FR/%05d.jpg" -i "$AUDIO" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$OUT"
else
  ffmpeg -v error -y -framerate $FPS -i "$FR/%05d.jpg" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p "$OUT"
fi
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
