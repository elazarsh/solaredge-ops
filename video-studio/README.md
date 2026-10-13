# video-studio

ערכת יצירת וידאו ל-Claude: סקילים, סוכנים וסקריפטים שנבנו מהעקרונות שבמדריך
[השיטה של המעצבת הראשית של Claude Code](https://brainai.co.il/guides/claude-code-lead-designer-method/)
ובמדריכי הווידאו של Brain (brainai.co.il), בתוספת חיבור ל-API הרשמי של PixVerse.

> זה סיכום עצמאי שלי של השיטות מהאתר, לא מוצר רשמי של Anthropic או של Brain.
> רשימת העקרונות והמקור של כל אחד: [`skills/video-studio/reference/principles.md`](skills/video-studio/reference/principles.md).

**מה אתה צריך לעשות?** פתח את [`START-HERE.he.md`](START-HERE.he.md). זה כל מה שדורש ממך פעולה.

## מה יש בפנים

| רכיב | תפקיד |
|---|---|
| `skills/video-studio` | נקודת הכניסה: בוחר מסלול, מפעיל שערי אישור לפני כסף ורינדור, מסכם בכנות |
| `skills/video-versions` | חמש כיווני וידאו שונים באמת כסטוריבורד (בלי רינדור), Claude בוחר ומנמק, אתה מחליט |
| `skills/video-mini-arena` | זירה בתשובה אחת: 6 גרסאות להוק/כותרת/תסריט, שופט קשוח, מנצח אחד |
| `skills/video-edit-engine` | עריכת סרטון שצילמת כקוד: תמלול ברמת מילה, חיתוך שתיקות, כתוביות עברית, 16 אפקטים על מילים, סאונד |
| `skills/video-hooks-real-action` | הוקים של פעולה אמיתית באוויר + אלמנט שנבנה בקוד (שריפה, קימוט, ניגוב, פיצוץ, לחיצה) |
| `skills/video-prompt-craft` | פרומפטים למודלי וידאו: נוסחה בשבעה חלקים, מסקוט ב-5 סצנות, צילום אחד מהמסלול לרחוב, החלפת דמות |
| `skills/pixverse-generate` | יצירת סרטונים ב-PixVerse (טקסט, תמונה, מעבר, הארכה) עם הערכת עלות ואישור לפני כל הוצאה |
| `skills/video-qa` | בדיקה כמו עורך: גיליונות מגע עם timecode, נחיתת אפקטים, עברית, כתוביות, עוצמת קול |
| `agents/video-director` | מריץ את כל התהליך מקצה לקצה |
| `agents/video-concept-judge` | שופט עיוור וקשוח לרעיונות, הוקים ועריכות |
| `agents/video-qa-reviewer` | בודק עצמאי של פריימים אמיתיים לפני שאתה רואה |
| `agents/video-sound-designer` | גיליון סאונד, מיקס, נרמול ל-14- LUFS |
| `agents/video-prompt-writer` | כותב פרומפטים לקליפים במקביל |
| `skills/*/scripts` | `timemap.py` (מפת זמן), `hebrew_text.py` (עברית נכונה), `contact_sheet.py`, `pixverse.py` |
| `mcp/pixverse.mcp.json.example` | הגדרה לשרת ה-MCP הרשמי של PixVerse (אופציונלי) |
| `examples/prague-petrin` | דוגמה מלאה: אנימטיק של 24 שניות ("רכבל האקסטרים של פראג") עם תמונה אמיתית, סאונד מסונתז, פרומפטים ועלות |

## על PixVerse

תיקון לתשובה הראשונה שלי בשיחה: **כן אפשר** להתחבר ל-PixVerse. יש להם API רשמי (`app-api.pixverse.ai`),
קובץ `llms.txt` ושרת MCP רשמי (`uvx pixverse-mcp`). נדרש חשבון ב-platform.pixverse.ai, מפתח API וקרדיטים
(נקנים בנפרד ממנוי האפליקציה). הסקריפט `pixverse.py` עוטף את ה-API עם הערכת עלות וחסימה מעל 300 קרדיטים כברירת מחדל.

## מה נבדק ומה לא (בכנות)

**נבדק בפועל (25 בדיקות, `python3 -m unittest discover -s video-studio/tests -v`):**
- `timemap.py`: מיפוי זמן אחרי חיתוך והקפאה, דחיית קלטים שגויים, וגרף אודיו שרץ ב-ffmpeg ומחזיר את האורך הצפוי.
- `hebrew_text.py`: רינדור עברית עם RAQM, גלישת שורות, ונפילה רועשת כש-RAQM חסר.
- `contact_sheet.py`: גיליונות עם timecode ופריימים בודדים על סרטון בדיקה אמיתי.
- `pixverse.py`: מול שרת מדומה בלבד (שליחה, polling, הורדה, מזהה ייחודי בכל בקשה, מפתח לא נחשף, חסימת עלות, שגיאות קריאות).
- מבנה הסקילים והסוכנים (front matter, נתיבים שמוזכרים בקבצים קיימים) והתקנת `install.sh`.
- הפקודות של ffmpeg שמופיעות בתיעוד (`ebur128`, `loudnorm`, `filter_complex_script`).

**לא נבדק:**
- `pixverse.py` מול ה-API החי: אין מפתח בסשן הזה. בהרצה הראשונה להתחיל ב-`balance` ובקליפ בדיקה קטן.
- `install.ps1` (אין PowerShell כאן).
- האפקטים עצמם (`effects-catalog.md`), הפרדת אדם, תמלול עברי עם ivrit.ai, HyperFrames ורינדור: אין כאן סרטון, OpenCV או GPU.
  הקטלוג הוא מתכונים שמבוססים על המדריכים, לא קוד שהורץ.
- לא צפיתי בהרצאה המקורית ביוטיוב, וקראתי רק חלק מהמדריכים באתר (רשימה ב-`principles.md`).
- מספרי המחיר של PixVerse נלקחו מהתיעוד ב-13.10.2026. לבדוק בדף התמחור לפני הוצאה גדולה.

## מבנה

```
video-studio/
  START-HERE.he.md          מה לעשות (בשפה פשוטה)
  README.md
  install.sh / install.ps1  התקנה למשתמש (~/.claude)
  .claude-plugin/plugin.json
  mcp/pixverse.mcp.json.example
  agents/                   5 סוכנים
  skills/                   8 סקילים (+ reference/ ו-scripts/)
  tests/test_video_studio.py
```
