---
name: html-to-video
description: >
  סרטון שנבנה כדף HTML/GSAP דטרמיניסטי והופך לווידאו: טיפוגרפיה בתנועה, אינפוגרפיקה, נייר גזור, סרטון הסבר, צילום מסך מונפש.
  סנכרון לקריינות דרך cues מתמלול, צילום פריימים ב־Chromium ו־ffmpeg, בדיקת חפיפות. להפעיל ב"סרטון הסבר",
  "טיפוגרפיה בתנועה", "בלי תמונות", "תבנה את הסרטון כ־HTML", "טקסט על טקסט". HTML/GSAP to video, explainer, kinetic typography.
---

# html-to-video

מתאים כשלא צריך תמונות מצוירות: הטקסט כתוב (לא מצויר), תיקון = שינוי קוד, חד בכל רזולוציה, **אין שגיאות כתיב בעברית**.
קבצים: `assets/template.html` (תבנית עובדת), `scripts/` (`setup.sh`, `cues.py`, `build.py`, `render.sh`, `render_frames.js`, `snap.js`, `overlap_check.js`, `lib.js`), `references/explainer-guide.md`.

## זרימה
```bash
S=.claude/skills/html-to-video
bash $S/scripts/setup.sh .                       # playwright-core (בלי הורדת דפדפן), gsap.min.js, פונט Heebo מקומי (לא CDN)
cp $S/assets/template.html index.html            # עורכים סצנות (S01, S02…) ו־CAT לפי הסרטון
python3 .claude/skills/hebrew-narration/scripts/tts.py narr.json --outdir vo      # קול לכל סצנה (מפתחות s01…)
python3 .claude/skills/hebrew-narration/scripts/asr.py transcribe vo/*.wav --out words.json
python3 $S/scripts/cues.py spec.json words.json --wavdir vo      # -> cues.json, durations.json
python3 $S/scripts/build.py index.html                            # -> page.html (מזריק __DUR__ ו־__CUES__)
node $S/scripts/snap.js . 3 8 15 --out tmp/q                      # פריימים לבדיקה בעין
node $S/scripts/overlap_check.js .                                # בדיקת חפיפות אוטומטית
bash $S/scripts/render.sh . --audio out/mix.wav --out out/film.mp4   # 4 workers, ~22 פריימים/ש' במצטבר
```
`MAXF=240 bash render.sh …` = רנדר של 10 שניות לבדיקה. הקול והמיקס: `video-audio-mix` (שים `voice_t = OFF[i]+LEAD`).

## חוזה הדף (חובה לדטרמיניזם)
- ציר זמן GSAP `paused:true`; `window.seek(t){tl.time(t);…}`, `window.preload()`, `window.TOTAL`, `window.OFF`. **בלי `Math.random`/`Date`/זמן אמת**: אותו t = אותו פריים. צילום: 1920×1080, 24fps, JPEG 90.
- GSAP ופונטים **מקומיים** (לא CDN בזמן צילום). **כל מחלקת CSS שהדף משתמש בה חייבת להיות מוגדרת** (`.tag{position:absolute;white-space:nowrap}`); מחלקה חסרה גרמה לפס ירוק מתוח.
- `fromTo` לכל כניסה; אם יש עוד tween על אותו אלמנט שישב אחרי כניסה: `immediateRender:false` לשני. אלמנט עם אנימציית "חיים" (נשימה) עטוף בקבוצה חיצונית נפרדת מקבוצת תנועת ה־cue כדי שלא יתנגשו. ב־SVG: `svgOrigin`.
- **מבנה בטוח מחפיפות:** כל שלב (phase) במכל משלו; המכל הקודם נעלם (opacity 0) **לפני** שהבא נכנס, מרווח ~0.3 ש'. מעבר בין שלבים = מעלימים את הקודם. כותרת שלא נעלמת עולה על רשימה = הבאג הנפוץ.

## סנכרון לקריינות (cues)
- לכל סצנה קול משלה; הקול מתחיל `LEAD=0.6` ש' אחרי תחילת הסצנה. כל אלמנט מופעל ב־`Q(i,'שם')`.
- `spec.json`: `{"s01":[["title","שני",1,0.4],["chat","הרגיל",1,2.5]]}` = [שם cue, **מילת מפתח כפי שהיא מתומללת**, מופע n, זמן גיבוי]. ה־ASR כותב אנגלית בלטינית ("Skill"), מספרים כספרות ("24"), בלי ניקוד. `cues.py` מדפיס `missing` כשלא נמצאה מילה → לתקן מילת מפתח.
- קצב ההקראה קובע את הסצנות: **לפחות 80% מהידע מגיע מההאזנה**, הטקסט על המסך רק משלים (אין שתיקות מיותרות).

## בדיקות לפני מסירה (פרטים ב־`video-qa-delivery`)
1. `overlap_check.js`: OVERLAP / SPILL / OFFSCREEN. יש תוצאות שווא (טקסט באותו אלמנט, חיתוך מכוון, מספרים עולים) → **תמיד גם בעין** (`snap.js` + `contact_sheet.py`).
2. ודא שאין שגיאות `PAGEERR`/`CONSOLE` ב־`snap.js`.
3. הצג 6–10 פריימים מייצגים (כל סצנה, ובכל מעבר בין שלבים).

## Chromium
הסביבה מגדירה `PLAYWRIGHT_BROWSERS_PATH` (בדרך כלל `/opt/pw-browsers`); **אין להריץ `playwright install`**. `lib.js` מוצא את הדפדפן ואת `playwright-core` דינמית (או `CHROMIUM_PATH`).
