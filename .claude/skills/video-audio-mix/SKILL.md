---
name: video-audio-mix
description: >
  מוזיקת רקע (Lyria), אפקטי קול סינתטיים מסונכרנים למעברים, הנמכת מוזיקה מתחת לקול, נרמול ל־-14 LUFS והדבקה לסרטון.
  להפעיל ב"מוזיקה לסרטון", "סאונד למעברים", "המוזיקה מכסה על הקול", "נרמול עוצמה", "מיקס".
  Music (Lyria), synthetic SFX, ducking, loudnorm -14 LUFS, final mix.
---

# video-audio-mix

סקריפטים ב־`scripts/`: `lyria.py` (מוזיקה), `sfx_lib.py` + `mix.py` (מיקס), `master.sh` (נרמול והדבקה). תלויות: numpy, scipy, ffmpeg; `GEMINI_API_KEY` למוזיקה.

## 1. מוזיקה
קטע לכל קטע רגשי (פתיחה, מתח, שיא, חיבוק, סיום). פרומפט: כלים + סולם + BPM + מצב רוח + מה קורה לאורך הקטע + **"Instrumental only, no vocals, no drums"**, כ־60 שניות (מוארך אחר כך בלולאה).
```bash
python3 scripts/lyria.py --prompt "Sparse, intimate cinematic score… solo oud, soft duduk, D minor, 56 BPM… about 60 seconds" --out mus/m1.mp3
python3 scripts/lyria.py --plan music.json --outdir mus --base "Sparse cinematic score for an animated film. Instrumental only."
```
קודם קטע אחד (עולה כסף). קבצים קיימים מדולגים; 429 → המתנה וחוזר. אם קטע חסר, המיקס יכול להשתמש בקטע אחר (`music[].file`).

## 2. מיקס (`mix.py mix.json`)
- **קול:** מסנן 75Hz, חימום, נרמול RMS, ריוורב קל (0.10). מתחיל ב־`voice_t` של כל פסקה (מתוך `timeline.json` של `assemble.py`, או `OFF[i]+LEAD` ב־HTML).
- **מוזיקה:** מולאפת בלולאה עם crossfade 4 ש', fade 2.5 ש' בקצוות, **מונמכת ~55% בזמן דיבור** (`duck_music`).
- **אפקטים:** `sfx:[{kind,t}]` מ־`sfx_lib.py`: whoosh swell ping click thump hammer scratch typing alarm stamp, ומעברים: whip smash tear burn water ripple ink erase peel wipe iris zoomthrough washout goldbloom colordrain colorseep dipblack dissolve defocus fill matte portal shatter match smoke. **לכל סוג מעבר צליל משלו, עדין.** `t` = רגע שיא המעבר (אמצע הקליפ של 8 ש' ÷ מהירות). אפקטים מונמכים 35% מתחת לקול.
- ב־HTML: פינג/קליק על כל cue (`ping` על הופעת אלמנט, `typing` על הקלדה, `stamp` על "חותמת").
- סיום: `tanh` רך, fade in 0.5 / out 2, נרמול שיא 0.9.

## 3. נרמול והדבקה
```bash
python3 scripts/mix.py mix.json                                    # out/mix.wav
bash scripts/master.sh body.mp4 out/mix.wav out/film_v1.mp4 out/mix.mp3   # loudnorm I=-14 TP=-1.5 LRA=11 + aac 192k + mp3
```
יעד −14 LUFS (סטנדרט סרטונים); הקראה ברורה מעל המוזיקה. בדוק עם `video-qa-delivery/scripts/check_video.py` (מציג LUFS וקליפינג).

## 4. בדיקה כנה
לא ניתן "להקשיב" כאן: דווח שהמיקס נבדק מספרית (LUFS, קליפינג, אורך) ולא בשמיעה, והמשתמש מאזין. אם המוזיקה מכסה על הקול: להגדיל `duck_music` (0.6–0.7) או להנמיך `gain`.
