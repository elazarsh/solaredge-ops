#!/bin/bash
# נרמול עוצמה סופי (-14 LUFS, TP -1.5) והדבקה לווידאו; אופציונלי גם ייצוא mp3 של המיקס.
# שימוש: bash master.sh video.mp4 mix.wav out.mp4 [mix.mp3]
set -e
[ $# -ge 3 ] || { echo "usage: master.sh video.mp4 mix.wav out.mp4 [mix.mp3]"; exit 1; }
ffmpeg -v error -y -i "$1" -i "$2" -af loudnorm=I=-14:TP=-1.5:LRA=11 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$3"
[ -n "$4" ] && ffmpeg -v error -y -i "$2" -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a libmp3lame -b:a 256k "$4"
ls -la "$3" ${4:+"$4"}
