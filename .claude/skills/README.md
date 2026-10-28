# סקילים להפקת סרטונים עם קלוד (עברית)

שמונה סקילים שהופכים את הידע משני הסרטים הראשונים (סרט פחם "נח – הפוסט־טראומטי הראשון" וסרטון הסבר) לתהליך חוזר. סשן שעובד בפרויקט הזה טוען אותם אוטומטית לפי ה־`description` של כל סקיל; **המשתמש צריך להכיר רק את הראשון**.

| סקיל | מתי מופעל | מה בתוכו |
|---|---|---|
| `video-with-claude` | "תכין לי סרטון על…" | **המנהל**: שאלות פתיחה, תסריט בטבלה, שער "תפיק", שלבים, כללי העדפות, טעויות לא לחזור עליהן. `references/script-table-template.md`, `references/guide.md` |
| `hebrew-narration` | הקראה מנוקדת, תיקון הגייה | `tts.py` (Gemini TTS), `asr.py` (תמלול ובדיקה), דוגמאות מנוקדות |
| `keyframe-images` | תמונות לסרט, טקסט עברי בתמונה | `gemini_image.py` (עם בדיקת קריאה חוזרת), `openai_image.py` (generate/edit, התאמה ל־16:9) |
| `video-motion-transitions` | אנימציה לתמונה, מעברים, הרכבה | `veo.py`, `camera_clip.py` (גיבוי), `trans.py` (25 מעברים), `objects.py`, `assemble.py` |
| `html-to-video` | סרטון הסבר/טיפוגרפיה ב־HTML | תבנית עובדת, `cues.py`, `render.sh`, `overlap_check.js`, `snap.js` |
| `video-audio-mix` | מוזיקה, סאונד, מיקס | `lyria.py`, `mix.py`+`sfx_lib.py`, `master.sh` (−14 LUFS) |
| `video-qa-delivery` | בדיקה ומסירה | `check_video.py`, `contact_sheet.py`, `split.sh` (<30MB), `export_audio.sh` |
| `ai-api-setup` | מפתחות, רשת, מכסות | `check_env.py` (בדיקה בלי להדפיס מפתחות) |

## סדר העבודה
שאלות פתיחה → תסריט בטבלה → **"תפיק"** → סגנון נעול → חומרים (תמונות+תנועה, או דף HTML) → קול (ניקוד, TTS, תמלול) → הרכבה ומיקס → בדיקות → משוב → מסירה (חלקים <30MB + שמע נפרד).
מסלול איור: `keyframe-images` → `video-motion-transitions` → `video-audio-mix`. מסלול הסבר/טיפוגרפיה: `html-to-video` → `video-audio-mix`. בשניהם `hebrew-narration` בהתחלה ו־`video-qa-delivery` בסוף.

## דרישות
- משתני סביבה (בהגדרות הסביבה, **לא בצ'אט**): `GEMINI_API_KEY` (חובה), `OPENAI_API_KEY` (אופציונלי).
- רשת: `generativelanguage.googleapis.com`, `api.openai.com`, ורישומי npm/PyPI להתקנה.
- כלים: `ffmpeg`, `python3` (numpy, scipy, opencv-python-headless, Pillow), `node` (≥18). HTML: `bash .claude/skills/html-to-video/scripts/setup.sh .` מתקין playwright-core, gsap ו־Heebo; Chromium מגיע מ־`/opt/pw-browsers` (אין `playwright install`).
- התקנת פייתון: `pip install numpy scipy opencv-python-headless pillow`.
- בדיקה: `python3 .claude/skills/ai-api-setup/scripts/check_env.py`.

## התקנה בפרויקט אחר או אישית
- פרויקט אחר: להעתיק את כל `.claude/skills/` (הסקילים מפנים זה לזה בנתיב יחסי, לכן להעתיק את כולם ביחד).
- אישית לכל הפרויקטים: `cp -r .claude/skills/* ~/.claude/skills/`. הפניות בתוך הסקילים כתובות כ־`.claude/skills/<שם>/scripts/…`; במצב אישי יש להחליף ל־`~/.claude/skills/<שם>/scripts/…`.
- סקיל שנוצר אחרי תחילת סשן עשוי לא להופיע ברשימה עד סשן חדש; ניתן לקרוא את `SKILL.md` ידנית.

## עלויות
תמונות, Veo, Lyria ו־TTS עולים כסף (Veo הכי יקר). ההפקה מתחילה רק אחרי "תפיק", ומקדימה בדיקת תמונה/קליפ/קטע אחד. מכסת Veo נגמרת: יש גיבוי מצלמה (`camera_clip.py`) ושדרוג מאוחר.

## ספר קומיקס משפחתי
| סקיל | מתי מופעל | מה בתוכו |
|---|---|---|
| `family-comic-book` | "ספר קומיקס משפחתי", "סיפור של סבא/סבתא", "ספר מהיומנים" | שיטת סיפור (מתח, חידה, סוף ומסר), חלוקת עבודה בין ChatGPT/Codex ל־Claude, מאגר גיטהב לכל ספר, ארכיטקטורת הצופה, אתר ו־PDF להדפסה, בדיקות. `references/`, `portable/` (ChatGPT, Codex), `templates/` |

מימוש לדוגמה: `elazarsh/journey-to-father-comic` ("הגיבור שלי · המסע אל אבא"), אתר: https://elazarsh.github.io/hagibor-hanamuch/
