# ״והנה איל״ — סרטון שיר (HTML → וידאו)

## קבצים
- `02-script.md` — התסריט שאושר (גרסה v3). `01-brief.md` — מסמך הבנה. `timings.json` — זמני הבתים.
- `assets/` — חומרי המקור (אודיו, קליפים, פוסטר, תמונת רקע, גופנים, תמלול).
- `clips/` — קטעים חתוכים (A, B, D מואטים; C במהירות מקור). `tools/slowmo.sh` — חיתוך והאטה.
- `build/` — הקומפוזיציה: `prep.py` (זמני מילים וחלונות), `extract.py` (פריימים וחיתוכים), `index.html` (הקומפוזיציה), `render.mjs` ו־`run_render.sh` (רינדור), `sheet.py` (גיליון מגע).
- `delivery/` — גרסה 1: `vayera-video-master.mp4`, `vayera-video-share.mp4`. **גרסה 2 (אפקטים מורחבים, כותרת תלת־ממדית):** `vayera-video-v2-master.mp4` (49MB) ו־`vayera-video-v2-share.mp4` (20MB).
- `assets/title/` — תמונת הכותרת (מקור ונוסח מנוקה משוליים), `build/defringe.py` — הניקוי.

## בנייה מחדש
```
cd build && npm i playwright-core
python3 -I prep.py ../assets/transcript-whisper.json timeline.json
python3 -I extract.py timeline.json
./run_render.sh 5948
ffmpeg -framerate 24 -i out/frames/f%05d.jpg -i ../assets/song.mp3 \
  -filter_complex "[1:a]adelay=5500|5500,apad=whole_dur=247.82[a]" -map 0:v -map "[a]" \
  -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -c:a aac -b:a 192k -t 247.82 out/vayera-video.mp4
```
