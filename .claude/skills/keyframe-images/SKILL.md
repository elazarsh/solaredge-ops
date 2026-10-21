---
name: keyframe-images
description: >
  יצירת תמונות מפתח לסרט מאויר: נעילת סגנון, עקביות דמויות עם תמונת ייחוס, טקסט עברי בתוך תמונה עם בדיקת קריאה חוזרת,
  ספקי תמונה Gemini ו־OpenAI. להפעיל ב"תמונות לסרט", "איור פחם/נייר גזור", "דמות עקבית", "טקסט בעברית בתמונה יצא שגוי",
  "תיצור תמונה עם gpt-image". Keyframe illustration, style lock, character consistency, Hebrew text in images, Gemini/OpenAI image.
---

# keyframe-images

## 1. נעילת סגנון (לפני כל הפקה)
1. מבקשים 2–3 דוגמאות לאותה סצנה בסגנונות שונים (תמונה אחת לכל סגנון, זול), המשתמש בוחר אחת.
2. כותבים **בלוק סגנון קבוע** (`style.txt`) ומצרפים אותו לכל פרומפט + את הדוגמה שנבחרה כתמונת ייחוס. דוגמה לבלוק (פחם): "Hand-drawn in exactly the style of the attached reference drawing: smudged charcoal and soft graphite on warm beige handmade paper … figures drawn from behind, in shadow or as simple silhouettes with no detailed faces. It is a drawing, not a photograph." ראה `examples/noah_keyframe_plan.py` (בלוק `BASE`, פלטות צבע `PAL`, רשימת תמונות עם מילים נדרשות).
3. פלטת צבע לכל קטע רגשי (חם / אפור קר / כהה / צבע שמתעורר), כדי שהסרט ירגיש כמסע.

## 2. עקביות דמויות
תמונת ייחוס לכל יצירה (`--ref`), תיאור קבוע של הדמות בכל פרומפט (למשל "Noah: old man, long beard, plain robe, as in the reference"), דמויות בצללית או מאחור (אין "פנים" שמשתנות). ב־OpenAI: `edit` עם `--ref`.

## 3. פרומפט תמונה
בלוק סגנון + `Scene: <תיאור>`. מציינים הרכב, מצב רוח, מה בקדמה. **תמיד "no text"** אלא אם צריך כתובת (הסקריפט מוסיף זאת אוטומטית כשאין `must`).

## 4. טקסט עברי בתוך תמונה (הסיכון הגדול)
המודל טועה באותיות ("נוח" במקום "נח", אות מיותרת, כיוון הפוך). לכן:
- מציינים בפרומפט את המילים מדויקות ("hand-lettered Hebrew in thick charcoal brush strokes, spelled exactly as given, right to left: …").
- `--must` (מילים חייבות) ו־`--forbid` (איות שגוי ידוע): הסקריפט קורא את התמונה בחזרה עם מודל ראייה, מנסה שוב עד 5–6 פעמים ושומר את הטובה (`_try0.png…` נשמרים).
- אם `weak`: תיקון ידני / מקום נקי בתמונה וכתובת ב־HTML (הכי בטוח) / יצירה מחדש.
- אחרי שגם זה לא עוזר, סאב־אייג'נט "בודק טקסט": פותח כל תמונה ורושם כל מילה עברית, אות אחר אות.
- כיוון: אם כלי האנימציה כותב משמאל לימין, ליצור בהיפוך מראה (ראה guide סעיף 10).

## 5. ספקים

### Gemini (ברירת מחדל): `scripts/gemini_image.py`
```bash
python3 scripts/gemini_image.py --style style.txt --prompt "A mother holds a baby…" --out img/k1.png --ref img/ref.png
python3 scripts/gemini_image.py --style style.txt --plan plan.json --outdir img --workers 3
python3 scripts/gemini_image.py --read img/k1.png        # אילו מילים כתובות בתמונה
```
דגם `gemini-3-pro-image`, 16:9, 2K. plan.json: `{"k7": {"prompt": "...", "must": ["כמה","קטן"], "forbid": ["נוח"], "refs": ["img/K5.png"]}}`.

### OpenAI: `scripts/openai_image.py` (נבדק בפועל: generate ו־edit עם gpt-image-1-mini)
```bash
python3 scripts/openai_image.py generate --prompt "…" --out img/k1.png --quality medium
python3 scripts/openai_image.py edit --prompt "same character, new pose" --ref img/ref.png --out img/k2.png
```
- דגמים בחשבון (נבדק): `gpt-image-1`, `gpt-image-1-mini`, `gpt-image-1.5`, `gpt-image-2`, `gpt-image-2.5-sunburst`, `gpt-image-2.5-flare`. ברירת מחדל `gpt-image-1` (`OPENAI_IMAGE_MODEL` או `--model`).
- גדלים: 1024x1024 / 1536x1024 / 1024x1536; דגמי 2.5 גם גודל חופשי (כפולות 16), למשל `1536x864` = 16:9. לדגמים אחרים הסקריפט מייצר 3:2 וחותך ל־16:9 (`--fit crop`) או מרחיב (`--fit pad`).
- איכות `low|medium|high` (2.5: גם `xhigh|max`). **איכות נמוכה לבדיקות** ומתעדכנים מול התיעוד: https://developers.openai.com/api/docs/guides/image-generation
- בפרויקט יש גם שרת MCP `mcp-gpt-image` (`.mcp.json`): כלים `generate_image`/`edit_image` ישירות בשיחה. הסקריפט כאן מתאים לאצווה ולשליטה בגודל.
- אין בדיקת טקסט אוטומטית ב־OpenAI: להריץ `gemini_image.py --read` על התוצאה לבדיקת מילים.

## 6. כללים
- הרץ **תמונה אחת קודם**, הצג, ורק אחר כך אצווה (3–4 במקביל, שמירה מיד, ניסיון חוזר אוטומטי).
- כל תמונה נשמרת בשם ברור; גיליון מגע לבדיקת עקביות: `video-qa-delivery/scripts/contact_sheet.py`.
- התמונות הן נקודת הפתיחה ל־`video-motion-transitions` (Veo / מצלמה / מעברים).
