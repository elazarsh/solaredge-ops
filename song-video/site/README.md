# עמודי הקריאה של ״והנה איל״

שלושה עיצובים לאותו תוכן: `a-dawn.html` (עלות השחר), `b-manuscript.html` (כתב יד), `c-stage.html` (במה), ו־`index.html` לבחירה.

## מבנה
- `build_data.py` בונה את `data.js`: נוסח השיר וזמני המילים (מ־`../build/timeline.json`), הפרשנות, מראי המקומות (הפסוקים נמשכים מספריא), הדוגמיות (`SAMPLES`) והשראות נוספות (`INSP`). כאן עורכים תוכן.
- `engine.js` משותף: סנכרון אודיו, הדגשת מילים, מצב יוצר, גלילה אחרי השיר.
- `src/*.html` הם התבניות. `assemble.py` מחבר אותן לקבצים שבתיקייה (מטמיע גופן גיבוי).
- `song.mp3` קישור סימבולי ל־`../assets/song.mp3` (לא נשמר ב־git). `art.jpg` היא גרסה קטנה של `../assets/background-art.jpg`.
- `tools/shot.mjs`, `tools/audio_test.mjs`: צילומי מסך ובדיקת אודיו בכרום headless.

## עדכון
```
python3 -I build_data.py && python3 assemble.py
```

## מצב יוצר
כפתור בתחתית כל עיצוב (או `#creator` בכתובת) מציג איפה מוצעות הדוגמיות השקטות של ״עוקד והנעקד והמזבח״ ו״למען אחי ורעי״. זמני ההצעה ב־`SAMPLES` ב־`build_data.py`.
