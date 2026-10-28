# קו הייצור: כלים, מאגרים ותמונות

## 1. מאגרים
- **מאגר פרטי לכל ספר** (`<שם-הספר>-comic`). מבנה:
  ```
  AGENTS.md                 הנחיות לכלי התמונות (Codex/ChatGPT)
  CLAUDE.md                 הנחיות ל־Claude (שלב נוכחי, מה אסור לגעת)
  sources/                  יומנים, מכתבים, תמלולים (פרטי)
  ref/                      תמונות רפרנס של הדמות (פרטי, לא עולה לאתר)
  production/manifest.json  רשימת כל התמונות: גודל, אזור בטוח, אזורים שקטים, פרומפט
  production/pages/pNN.md   חבילה לכל עמוד
  production/character-sheets.md
  art/                      תמונות סופיות (WebP לרשת), art/chars/ לגיליונות דמות
  viewer/index.html         הצופה (Claude בלבד)
  tools/                    build_site.py, print_pdf.js, print_pdf.py
  print/                    קובצי PDF
  handoffs/<כלי>/           תיקייה לכל כלי: טיוטות, מצב, בקשות תיקון
  ```
- **מאגר ציבורי נפרד** (למשל `<שם>-site`) רק עם `index.html` ו־`art/*.webp`, עם GitHub Pages (Deploy from a branch, main, root). כך המשפחה משתפת קישור, והחומרים הפרטיים נשארים פרטיים.
- הרשאות: לאפליקציית Claude ב־GitHub צריכה להיות גישה לשני המאגרים (https://github.com/apps/claude/installations/select_target).

## 2. עבודה במקביל בכמה כלים
- כל כלי מקבל קובץ הנחיות במאגר: `AGENTS.md` (Codex), `CLAUDE.md` (Claude), `portable/gpt-instructions.md` מהסקיל (ChatGPT Project).
- כל כלי כותב רק לתיקייה שלו ב־`handoffs/` ולתיקיות שבאחריותו (Codex: `art/`; Claude: `viewer/`, `tools/`, `print/`).
- קובץ מצב משותף `handoffs/<כלי>/state.json`: מה הושלם, מה ממתין, בקשות תיקון. בקשות תיקון לתמונות נכתבות ב־`handoffs/codex/IMAGE-REQUESTS.md`.
- דחיפה קטנה לכל עמוד (`art: page N`), כדי שהכלי השני יראה התקדמות מיד.

## 3. הנחיות לתמונות (לכלי התמונות)
- **סגנון קבוע** לכל הספר (בלוק סגנון), למשל: "Warm painterly European graphic-novel illustration with Pixar-like emotional expressiveness, fine clean ink outlines, soft cinematic lighting, richly detailed backgrounds, expressive faces."
- **גיליונות דמות קודם**, מאושרים, ומצורפים לכל יצירה שבה הדמות מופיעה. דמות המספר לפי תמונה אמיתית (`ref/`).
- **יחסי גובה וגיל** כתובים במפורש אם הם חלק מהעלילה (למשל האבא נמוך מהאמא).
- **סצנה אחת לכל קובץ.** בלי טקסט, בלי אותיות, בלי בועות, בלי מסגרות, בלי חלוקה לפאנלים, בלי סימן מים. שלטים וספרים עם קשקוש לא קריא.
- **אזור בטוח** לתוכן החשוב (הצופה חותך, מגדיל 4-15% ומזיז בגלילה), **אזורים שקטים** לכיתוב (שמיים, קיר, רצפה), ומרווח סביב ראשים (כדי שלא ייחתכו).
- **פלטה לכל סצנה** (אירופה קר כחול־אפור, אונייה כחולים ומנורות חמות, לילה כחול כהה, ארץ ישראל זהוב).
- **שכבות** (חפצים שחוצים פאנלים, כמו מזוודה או שחפים): רקע ירוק מלא #00FF00, ואז הסרת רקע לסקריפט chromakey.
- סצנות רגישות: צללית בלבד, בלי אלימות.
- מוסרים PNG בגודל המבוקש; Claude ממיר ל־WebP לרשת (בערך 1536 פיקסלים בצד הארוך).

## 4. ערכת ההפקה (manifest.json)
לכל קובץ: `file`, `kind` (panel/layer/circle), `generate_size`, `safe_area_center`, `calm_areas` (איפה הכיתוב), `palette`, `characters`, `prompt` מוכן להדבקה. הצופה מייצא אותה (`window.__manifest()` בתבנית).

## 5. בדיקת תמונות שהגיעו
- גיליון מגע לכל עמוד, השוואה לגיליונות הדמות (פנים, בגדים, גיל, גובה).
- גיליון חיתוכים: התמונה המלאה עם המסגרת של מה שנראה בפאנל (ראו qa-checklist).
- זיהוי פנים (YuNet) לכל תמונה, נשמר בטבלת `FACES` בצופה.
- בקשות תיקון ספציפיות ("לשמור הכל, לשנות רק...").
