# solaredge-ops — מפת ידע לסשנים (קרא קודם)

הריפו הזה מחזיק **שני עולמות**. לפני שמתחילים, מזהים לאיזה מהם הבקשה שייכת.

| עולם | איפה | מתי |
|---|---|---|
| ניטור SolarEdge | `solaredge_ops/`, `tests/`, `README.md`, `config.example.yaml` | קוד, התראות, דוחות, דשבורד |
| סטודיו וידאו (פרסומות בעברית) | `video-studio/`, `.claude/skills/`, `.claude/hooks/` | כל בקשה לסרטון, פרסומת, מודעה, קמפיין, ריל, קריינות, כתוביות |

## כללי עבודה קבועים
- **מדברים עם המשתמש רק בעברית.**
- **בקשת סרטון או פרסומת ← קודם כל טוענים את הסקילים ואת `video-studio/PLAYBOOK.md`.** אין צורך שהמשתמש יזכיר אותם. אם לא ברור שם הסקיל, מחפשים ב-`.claude/skills/*/SKILL.md`.
- תסריט בטבלה ← אישור ← הפקה רק אחרי שהמשתמש כותב "תפיק".
- כל מספר, שם או טענה מגיעים מהמשתמש (`facts.md`). לא ממציאים עובדות.
- לא מפרסמים ולא מבצעים push לענף שאינו ענף העבודה של הסשן בלי אישור מפורש.

## איפה הידע (מקור אמת אחד לכל נושא)
| נושא | מקום |
|---|---|
| העדפות המשתמש, לקחים, מלכודות טכניות, שיטת הוולוג | `video-studio/PLAYBOOK.md` |
| סקירת כלים והתקנות | `video-studio/GUIDE.md`, `video-studio/setup.sh` |
| תהליך פרסומת מקצה לקצה (בריף ← QA) | `.claude/skills/ad-creative/` (+ `references/`, `templates/`) |
| עברית: RTL, פונטים, ניקוד לקריינות, לשון פנייה | `.claude/skills/hebrew-video/` |
| קריינות (Gemini TTS), מוזיקה (Lyria), תמונות, סאונד | `.claude/skills/media-use/` |
| תנועה איכותית וסנכרון לקצב | `.claude/skills/motion-craft/` |
| בניית הסרטון ורינדור | `.claude/skills/hyperframes*`, `video-studio/remotion/` |
| דירוג תסריטים עם TypeSafe (Jev) | `.claude/skills/script-judge/` |
| כלי שורת פקודה (QA, beat-grid, loudnorm, new-ad) | `video-studio/tools/` |
| דוגמאות עבודה (תסריטים, בריפים, עובדות) | `video-studio/ads/<קמפיין>/` (טקסט בלבד; מדיה כבדה לא נשמרת בגיט) |
| Hooks אוטומטיים | `.claude/settings.json` ← `.claude/hooks/` (הקמת סביבה, ניתוב בקשות פרסומת, QA אחרי רינדור) |

## ניתוב מהיר לפי בקשה
- פרסומת / מודעה / קמפיין / ריל שיווקי ← `ad-creative` + `hebrew-video` (+ `script-judge` לדירוג)
- קריינות או מוזיקה ← `media-use`
- סרטון מ-URL של מוצר ← `product-launch-video`; הסבר מנושא ← `faceless-explainer`; מ-PR ← `pr-to-video`
- כתוביות על סרטון קיים ← `embedded-captions`; גרפיקות על סרטון ראיון ← `talking-head-recut`
- לא ברור ← `hyperframes` (נקודת הכניסה)

## מפתחות וסביבה
- `GEMINI_API_KEY`: קריינות ותמונות. `TYPESAFE_API_KEY`: דירוג תסריטים. שניהם בהגדרות הסביבה, לעולם לא בקבצים.
- אחרי סשן חדש על ענף חדש ה-hook מריץ `video-studio/setup.sh`; אם נכשל, היומן ב-`/tmp/video-studio-setup.log`.

## שמירת הידע
- כשלומדים משהו חדש על ההעדפות של המשתמש או על מלכודת טכנית ← מוסיפים ל-`video-studio/PLAYBOOK.md` (לא רק בשיחה).
- סקיל חדש ← `.claude/skills/<שם>/SKILL.md` עם תיאור שמפרט **מתי** להפעיל אותו, ושורה בטבלה למעלה.
- השינויים האלה צריכים להיות ב-`main` כדי שכל סשן יראה אותם. סשן שרץ על ענף ישן לא יראה סקילים חדשים.
