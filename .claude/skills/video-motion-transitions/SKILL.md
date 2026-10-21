---
name: video-motion-transitions
description: >
  הנפשת תמונה לווידאו (Veo), מכסות ו־429 וגיבוי תנועת מצלמה, וספריית 25 מעברים בעלי משמעות (כולל מבוססי אובייקטים),
  והרכבת הסרט לפי אורכי ההקראה. להפעיל ב"אנימציה לתמונה", "מעבר בין תמונות", "שריפה/מים/דלת/התפוררות",
  "Veo נתקע על 429", "הרכב את הקליפים". Image-to-video, Veo quota fallback, meaningful transitions, assembly.
---

# video-motion-transitions

סקריפטים (`scripts/`): `veo.py` (תנועה), `camera_clip.py` (גיבוי), `objects.py` (מסכות), `trans.py` (25 מעברים), `assemble.py` (הרכבה).
תלויות: numpy, opencv-python-headless, Pillow, ffmpeg; `GEMINI_API_KEY`. ספרייה מלאה: `references/transitions-library.md`.

## 1. עיקרון: סרט ולא מצגת
כל תמונה זזה (תנועה פנימית: נשימה, רוח, קו שמרים, יד) וכל מעבר מספר משהו. **תכנן מראש שהמכסה תיגמר** (בהפקה הקודמת 42 מתוך 62 קליפים נשארו סטטיים כי לא תוכנן גיבוי).

## 2. תנועה עם Veo: `veo.py`
```bash
python3 scripts/veo.py --image img/k1.png --prompt "The hand slowly drags the charcoal…" --out veo/k1.mp4     # קודם אחד!
python3 scripts/veo.py --plan shots.json --outdir veo --workers 2        # {"k1":{"image":…,"prompt":…,"last_image":…}}
```
- image-to-video, 8 ש', 1080p. דגמים: `veo-3.1-lite-generate-preview` (זול, ברירת מחדל ראשונה), `…-fast-…`, `veo-3.1-generate-preview` (יקר). `--last-image` = תמונת סיום (Veo בונה את הדרך בין שתי תמונות; כך נבנו מעברי פחם).
- **פרומפט תנועה:** מה זז (ידיים, אש, רוח, נשימה), במה לא לגעת. הסקריפט מוסיף סיומת קבועה: **"The camera stays still. … every Hebrew letter or word in the drawing stay exactly as in the image and never change or morph; nothing new is added. Silent."** אל תוריד אותה (בלי זה האותיות העבריות מתעוותות).
- **429 (מכסה יומית/הוצאה):** לא עוצרים. הסקריפט ממתין 75–105 ש' ומנסה שוב, מתחלף בין דגמים; `--max-attempts N` לוותר ולרשום ב־`pending.json`. בינתיים בונים **גיבוי** (סעיף 3) ומשדרגים כשהמכסה חוזרת.
- הרצה במקביל מוגבלת (2–3), כל קליפ נשמר מיד, קיים = מדולג. קודם הצג קליפ אחד למשתמש.

## 3. גיבוי: תמונה + תנועת מצלמה + מעבר
`camera_clip.py img out.mp4 --kind 0..3 --seconds 8 [--ease-start --ease-end]`: זום פנימה / פאן ימינה / זום החוצה / פאן שמאלה, עם האטה לאפס בקצה לחיבור רציף. **תמונה אחת + `-frames:v`** (zoompan בלי הגבלה יצר סרטון של 32 דקות). ב־`trans.py` הגיבוי הוא ברירת המחדל כשאין `--vid-a/--vid-b`. כשהמכסה חוזרת: מריצים `veo.py` על `pending` ומרנדרים מחדש (מפתח המטמון משתנה).

## 4. מעברים: `trans.py`
```bash
python3 scripts/trans.py img/k1.png img/k2.png burn --out tmp/k1_k2.mp4 --idx 3
python3 scripts/trans.py img/k3.png img/k4.png portal --params '{"objA":"the open lit doorway","shape":"rect"}'   # אחרי objects.py prepare
```
- 25 סוגים (טבלה ב־references). קליפ של 8 ש' (24fps, 1920×1080): מצלמה על A → המעבר באמצע → מצלמה על B. `--ease-a/--ease-b` כשהקליפ מתחבר לקליפ Veo סמוך. `--vid-a/--vid-b` = קליפ Veo כמקור פריימים.
- **מעברי אובייקט:** קודם `python3 scripts/objects.py prepare items.json` (Gemini מאתר תיבות, grabCut בונה מסכה, נשמר ב־`objcache/`). **לבדוק את המסכה בעין.**
- **תוכנית מעברים:** לכל זוג תמונות `{kind,params}` לפי הסיפור (`references/transition-plan-example.json`). מגוון: 14+ סוגים, לא אותו אפקט יותר מ־3 פעמים. רנדור כבד (~12–45 ש' לקליפ): 3 במקביל, מטמון לפי (מקור, מהירות, דגלים).
- באג שנפתר: גיבוי multiply יצר גוון ירוק → לערבב ב־`gbrp` (ב־ffmpeg). מעברי `trans.py` מחושבים ב־numpy/RGB ואינם סובלים מזה.

## 5. הרכבה לפי הקריינות: `assemble.py plan.json`
חלון לכל פסקה = LEAD 0.35 + אורך קול + TAIL 1.4; מהירות הקליפים 0.8–1.3 כדי להתאים; פער נחלק לצדדים. **אימות אורך לפני שימוש + `stale/`** (קליפ חלקי במטמון קיצר פעם סרט שלם). פלט `timeline.json` עם `voice_t` לכל פסקה → `video-audio-mix/mix.json`. "החזקה" בסוף: תמונה אחת עם זום איטי (ללא zoompan בלתי מוגבל).

## 6. סדר עבודה מומלץ
תמונות (`keyframe-images`) → Veo לשוטים הכי חשובים / גיבוי לכולם → תוכנית מעברים → רנדור מעברים → `assemble.py` → קול ומיקס (`video-audio-mix`) → בדיקות (`video-qa-delivery`).
