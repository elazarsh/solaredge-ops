#!/bin/bash
# ייצוא קובצי שמע נפרדים (קלים להעברה): הקראה בלבד, ומיקס מלא (קריינות+מוזיקה+סאונד), ב-mp3 256k ובנרמול -14 LUFS.
# שימוש: bash export_audio.sh narration_concat.wav|film.mp4 out.mp3
# להקראה בלבד: חבר את קובצי הקול (vo/*.wav) עם concat:  printf "file '%s'\n" vo/p*.wav > l.txt; ffmpeg -f concat -safe 0 -i l.txt narr.wav
set -e
ffmpeg -v error -y -i "$1" -vn -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a libmp3lame -b:a 256k "$2"; ls -la "$2"
