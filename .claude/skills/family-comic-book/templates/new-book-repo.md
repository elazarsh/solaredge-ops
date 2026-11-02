# פתיחת ספר חדש

הדרך הקצרה (מומלצת): `python3 engine/new_book.py <תיקיית הספר> --title "..." --title-en "..." --prefix G1 --hero "סבא ..."`.
הקבצים שנוצרים באים מ־`templates/new-book/`. פירוט השלבים: `SKILL.md` סעיף 0.

## מאגרים
1. **פרטי** לכל ספר (או תיקייה `books/<שם>/` במאגר הפרטי של המשפחה, כמו `elazarsh/journey-to-father-comic`). כל החומרים והתמונות האמיתיות רק שם.
2. **ציבורי** רק אם המשתמש ביקש אתר לשיתוף, ורק עם האתר לקריאה (בלי `sources/`, `ref/`).
3. גישה לאפליקציית Claude ב־GitHub: https://github.com/apps/claude/installations/select_target

## כלים בסביבה
`python3` (Pillow, opencv-python-headless), `node` עם Playwright ו־Chromium (בענן מותקן מראש), מודל YuNet (`face_detection_yunet_2023mar.onnx` מ־opencv_zoo, להוריד מ־media.githubusercontent ולא את קובץ ה־LFS).
