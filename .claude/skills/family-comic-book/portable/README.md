# שימוש בידע הזה בכלים אחרים

הסקיל כתוב כך שאפשר לעבוד גם בלי Claude, ובמקביל בכמה כלים.

| כלי | מה לשים בו | תפקיד מומלץ |
|---|---|---|
| **ChatGPT (Project)** | את `gpt-instructions.md` בהנחיות הפרויקט, ואת קובצי `references/` כקבצים | חילוץ סיפור, טיוטת תסריט, גיליונות דמות ותמונות |
| **Codex** | `AGENTS.md` (מתוך `AGENTS.template.md`) בשורש מאגר הספר | ייצור התמונות לפי `production/manifest.json`, דחיפה לגיטהב עמוד אחר עמוד |
| **Claude Code** | הסקיל הזה (`.claude/skills/family-comic-book`) + `CLAUDE.md` במאגר הספר | תסריט סופי, פריסה, כיתוב, אתר, PDF, בדיקות |
| **Gemini / אחר** | `gpt-instructions.md` כהנחיית מערכת | כמו ChatGPT |

## איך עובדים במקביל
1. פותחים מאגר פרטי לספר (ראו `templates/new-book-repo.md`).
2. כל כלי מקבל את קובץ ההנחיות שלו ועובד רק בתיקיות שלו; מסירות דרך `handoffs/<כלי>/`.
3. כל כלי דוחף שינויים קטנים ומעדכן `handoffs/<כלי>/state.json`.
4. Claude מחבר הכל: בודק תמונות, מבקש תיקונים ב־`handoffs/codex/IMAGE-REQUESTS.md`, ובונה אתר ו־PDF.
