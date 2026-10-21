---
name: ai-api-setup
description: >
  מפתחות API, משתני סביבה ורשת בסביבת ענן עבור הפקת סרטונים (Gemini, OpenAI), מכסות ועלויות. להפעיל כש"אין מפתח",
  "403 מהפרוקסי", "429", "איך מוסיפים מפתח", "בדוק שהשירותים עובדים", לפני הפקה ראשונה. API keys, env vars, network policy, quotas.
---

# ai-api-setup

## כלל אחד: מפתח לעולם לא מודבק ולא מודפס בשיחה
מפתח נכנס **בהגדרות הסביבה של הסשן (secrets / משתני סביבה)**, ולא בצ'אט. אחרי הוספה פותחים סשן חדש. אם מפתח דלף: מבטלים ויוצרים חדש. אין להדפיס `env`, ואין לשמור מפתח בקבצי הפרויקט או בפקודות git.

## בדיקה (חינמית, לא מדפיסה מפתחות)
```bash
python3 .claude/skills/ai-api-setup/scripts/check_env.py            # יש/אין, אורך, וגישה לרשת (רשימת מודלים)
python3 .claude/skills/ai-api-setup/scripts/check_env.py --models   # מציג דגמי קול/תמונה/Veo/Lyria/OpenAI בחשבון
```

## משתנים
| משתנה | שירות | שימוש |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio | TTS, ASR, תמונות, Veo, Lyria, זיהוי אובייקטים |
| `OPENAI_API_KEY` | OpenAI | תמונות gpt-image (אופציונלי; גם שרת `mcp-gpt-image`) |
| `OPENAI_IMAGE_MODEL`, `OPENAI_BASE_URL` | OpenAI | דגם ברירת מחדל / כתובת בסיס |
| `CHROMIUM_PATH`, `PLAYWRIGHT_BROWSERS_PATH` | צילום HTML | נתיב דפדפן (ברירת מחדל `/opt/pw-browsers`) |

השגת מפתח Gemini: aistudio.google.com → "Get API key". שירותים יקרים (Veo, Lyria) דורשים חשבון חיוב; מגדירים תקרת הוצאה. שמות כפתורים משתנים: אם משהו לא זהה, לשאול.

## רשת (סשן בענן)
- כל ההפקה מדברת עם `generativelanguage.googleapis.com` (+ הורדת וידאו מ־URI שה־API מחזיר) ועם `api.openai.com`. אם הפרוקסי מחזיר **403/407** או שההעברה נקטעת: הדומיין לא מאושר במדיניות הרשת של הסביבה → יש להוסיף אותו בהגדרות הסביבה (Network access). אפשר לקרוא את `/root/.ccr/README.md` לפרטים. **אין לכבות אימות TLS.**
- `npm i`/`pip install` דורשים גישה לרשום החבילות (npm, PyPI).

## מכסות ועלויות
- 429 ב־Veo (מכסה יומית/הוצאה): תור סבלני + גיבוי מצלמה (`video-motion-transitions`). TTS/ASR: 3 במקביל לכל היותר.
- **הערכת עלות לפני ריצה ארוכה** (מוצגת בתסריט). בדיקות: תמונה אחת, איכות נמוכה, קטע מוזיקה אחד, קליפ Veo אחד בדגם lite.
- עלות משמעותית: Veo (לפי קליפ של 8 ש'), Lyria, תמונות 2K באיכות גבוהה. TTS ו־ASR זולים.
