#!/bin/sh
# Cut a segment from a source clip and slow it down with motion-interpolated frames.
# usage: slowmo.sh <src.mp4> <start_s> <end_s> <speed e.g. 0.3> <out.mp4>
set -e
src="$1"; ss="$2"; to="$3"; speed="$4"; out="$5"
ffmpeg -v error -y -ss "$ss" -to "$to" -i "$src" -an \
  -vf "setpts=PTS/${speed},minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" \
  -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p "$out"
echo "$out $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")s"
