#!/bin/bash
# פיצול סרטון לחלקים מתחת ל-30MiB (גבול העלאה), בגבולות סצנות, עם קידוד מחדש. אם חלק גדול מדי: מעלה crf ומקודד שוב.
# שימוש: bash split.sh film.mp4 outdir "0 63.1 176.8 281.4 9999" [prefix=part] [width=1280] [limitMB=29]
#   הגבולות = שניות תחילת כל חלק + סיום אחרון (9999 = עד הסוף). בחר גבולות בתחילת סצנה (cue של מעבר).
# דוגמה שעבדה: סרטון 6 דק' 1080p -> 3 חלקים של ~13.8/16.5/10MB ב-crf 25-28, 1280x720.
set -e
SRC="$1"; OUT="$2"; read -ra B <<< "$3"; PRE=${4:-part}; WID=${5:-1280}; LIM=${6:-29}
[ -f "$SRC" ] && [ ${#B[@]} -ge 2 ] || { echo "usage: split.sh film.mp4 outdir \"0 60 9999\" [prefix] [width] [limitMB]"; exit 1; }
mkdir -p "$OUT"; H=$(( WID * 9 / 16 / 2 * 2 ))
for ((i=0; i<${#B[@]}-1; i++)); do
  f="$OUT/${PRE}_$((i+1)).mp4"; crf=25
  while :; do
    ffmpeg -v error -y -ss ${B[$i]} -to ${B[$((i+1))]} -i "$SRC" -vf scale=$WID:$H -c:v libx264 -preset medium -crf $crf -maxrate 1800k -bufsize 3600k -c:a aac -b:a 96k -movflags +faststart "$f"
    mb=$(( $(stat -c %s "$f") / 1048576 ))
    [ $mb -lt $LIM ] && break
    crf=$((crf+3)); echo "$f ${mb}MB > ${LIM}MB, מקודד שוב ב-crf $crf"; [ $crf -gt 40 ] && { echo "לא מצליח להקטין"; exit 1; }
  done
done
ls -la "$OUT"/${PRE}_*.mp4
