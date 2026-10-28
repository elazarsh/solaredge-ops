# פתיחת ספר חדש

## 1. מאגרים (המשתמש לוחץ, Claude ממלא)
1. מאגר פרטי חדש מהתבנית: ב־`elazarsh/journey-to-father-comic` לסמן Settings → General → **Template repository**, ואז "Use this template" → שם כמו `<שם-הספר>-comic`, Private.
2. מאגר ציבורי ריק לאתר: https://github.com/new?name=<שם>&visibility=public (בלי README).
3. גישה לאפליקציית Claude לשני המאגרים: https://github.com/apps/claude/installations/select_target
4. אחרי הדחיפה הראשונה לאתר: Settings → Pages → Deploy from a branch → main → / (root).

## 2. מה לנקות מהתבנית
- `art/`, `production/`, `handoffs/`, `print/`, `ref/`: לרוקן (שומרים את `production/scripts/`).
- בצופה: `STR` (טקסטים), `PAGES` (עמוד 1), `STORY`, `GEO`, `TX`, `ADJ`, `FACES`, `PTREE` (הדפסה): לבנות מחדש לספר החדש. המנוע עצמו (צורות, כיתוב, פנים, הדפסה) נשאר.
- `tools/build_site.py`: כתובת האתר, תיאור og, שם הקובץ.
- `tools/print_pdf.js`: טקסט הכריכה האחורית (`BACK`), תמונת הכריכה, QR.

## 3. CLAUDE.md לספר החדש (שלד)
```
# <שם הספר>
סקיל: family-comic-book. שלב נוכחי: <תסריט / דמויות / תמונות / פריסה / פרסום>.
דמויות: <שם, גיל, גובה יחסי, בגדים>. דמות המספר לפי ref/<קובץ>.
אסור לפרסם: ref/, sources/. אתר ציבורי: <כתובת>.
שורות מומצאות שממתינות לאישור: <רשימה>.
```

## 4. כלים נדרשים בסביבה
`python3` (Pillow, opencv-python-headless, pymupdf, qrcode), `node` עם Playwright ו־Chromium (בסביבת הענן מותקן מראש), מודל YuNet לזיהוי פנים (`face_detection_yunet_2023mar.onnx` מ־opencv_zoo).
