# בריף ל־GPT: תמונות לסרט «בין כוח לברכה»

אתה **מפיק התמונות** של סרט אנימציה קצר בעברית. אתה **לא** מנפיש ולא מרכיב: אתה יוצר תמונות (רקעים, וגם "חלקי נייר" בודדים) שיונפשו אחר כך בקוד. עובדים **בשלבים, ועוצרים לאישור בסוף כל שלב**. דבר איתי בעברית פשוטה ובקצרה.
**כל מה שאתה צריך נמצא בהודעה הזאת. אין קבצים מצורפים.** את רשימת 75 הרגעים של הסרט אשלח בהודעה נפרדת לפני שלב 3.

## 1. הסרט
- **שם:** «בין כוח לברכה». על פרשת תולדות (בראשית כה–כז): יצחק ורבקה, עשו ויעקב, לבן.
- **פורמט:** אנכי **9:16** (סטטוס בווטסאפ). אורך כ־4:20, פתיח של 3 שניות. קהל: הציבור הישראלי, בראשו דתי־לאומי.
- **הרעיון:** הנהגה היא **כתר וגם אגרוף**. הצד הבריא: כתר והדר (כבוד, שירות, אחריות גם למי שלא בחר, הקשבה). הצד המכוער והלא בריא: שררה אלימה (להשתיק, למחוק, לשלוט בשכר של אחר). הסרט עוקב אחרי היד: מתי היא פתוחה ומתי נסגרת לאגרוף.
- **אח מול אויב:** ויכוח לגיטימי יכול להתקיים גם בלי הסכמה (יצחק ורבקה, ובסוף "אח שחולק"). מה שהופך אח לאויב הוא **האלימות** ואי־היכולת לקבל את האחר (עשו ב"וְאַהַרְגָה").
- **שלוש הצצות חוזרות (לשמור עליהן בעקביות):**
  1. **צל הכתר על השולחן** הוא צל של **אגרוף** בתחילת הסרט, ובסוף אותו צל הוא **כף יד פתוחה**.
  2. **טבעת זהב דקה סביב שולחן עגול** (מלמעלה) = גבולות הוויכוח הלגיטימי. מי שמכניס אלימות **פורץ את הטבעת** והיא נסדקת, והכיסא שלו נשאר **מחוץ** לטבעת.
  3. **שני כיסאות שונים:** כיסא מחוץ לטבעת (מי שיצא מהגבולות) וכיסא **אחר** של אח שחולק (ירוק) שנכנס לאור בסוף. כיסא על גבעה = הנהגה, ונמחק בדיו.

## 2. סגנון (בכל תמונה, בלי יוצא מן הכלל)
קולאז' נייר בסגנון ריזוגרף. **לא** צילומי, **לא** תלת־ממד. בכל פרומפט, באנגלית, הדבק בתחילתו את בלוק הסגנון הזה (`STYLE`) ואחריו `Scene: ...`:

```
Contemporary paper-cut collage in a riso-print style: layered cut and torn paper shapes with slightly rough edges, flat spot colors (warm gold, riso blue, vivid orange, pink, cream, ink black), halftone dot shading, slight print misregistration, visible paper grain, soft shadows between paper layers. VERTICAL 9:16 portrait, flat graphic illustration (not photographic, not 3D). No text, no letters, no numbers anywhere. NO FACES: people appear only seen from above or from behind as simple colored shapes (round head and shoulders), never eyes, nose, mouth or face profile. Keep the main subject inside the central 70% of the frame height, leaving the top 10% and bottom 15% calm.
```

**דמויות וצבעים (בלי פנים; זיהוי לפי חתימה וצבע):**
| | חתימה | צבע |
|---|---|---|
| יצחק | גלימת צמר, מטה | שמנת |
| רבקה | צעיף ארוך | ורוד |
| עשו | גלימת ציד עם שולי פרווה, כתפיים רחבות (**בלי נשק, בלי קשת**) | כתום |
| יעקב | דמות צרה | כחול |
| אח שחולק (בפרק האחרון) | | ירוק |
| לבן | **רק** יד כבדה עם טבעת + ספר חשבונות | ירוק־אפור קר |
| **כתר** (הצד הבריא) | | זהב |
| **אגרוף** (שררה אלימה) | | שחור דיו + אדום |

## 3. כללים קשיחים
1. **בלי פנים בשום תמונה.** אנשים רק מלמעלה, מהגב, כצל/צללית, או כידיים. אסורים: עיניים, אף, פה, פרופיל פנים (גם לא "נקודות" שנראות כעיניים).
2. **בלי טקסט:** בלי אותיות, ספרות או חתימות. כל הטקסט (כולל הכותרת) מתווסף בקוד.
3. **בלי אלימות מוצגת ובלי נשק:** בלי דם, חרבות, קשתות, גופות, לוחמים. האגרוף והצל מספיקים.
4. **בלי** דגלים, לוגואים, ארגונים, אנשים אמיתיים.
5. **שוטים רגישים** (מאופקים בכוונה): יד על ידית דלת מבפנים בחדר חשוך, וקנה כתיבה שלא חותם על שורה ריקה. בלי אנשים ובלי פנים.
6. **9:16 אנכי.** הנושא בתוך 70% האמצעיים של הגובה, חלק עליון (10%) ותחתון (15%) שקטים. אם הכלי שלך תומך רק ב־2:3, צור ב־2:3 עם הנושא ב־80% האמצעיים של הרוחב, כדי שאפשר יהיה לחתוך ל־9:16.
7. **אובייקט למעבר:** בתמונות שמסומנות כך, האובייקט צריך להיות ברור, גדול ומבודד.

## 4. איך התמונות יונפשו (תכנן בהתאם)
הרקעים יקבלו רעד נייר בפריימים מדורגים, גרגר, רסטר זז, מעברי נייר נקרע ודיו, וקווי קול וטיפוגרפיה בקוד.
- **רקעים (Plates):** סצנה שלמה אחת, שכבות ברורות, מקומות שקטים.
- **חלקים להנפשה (Sprites):** כתר, אגרוף, כף יד פתוחה, כף יד של יצחק עם מטה, צעיף, שולחן עגול מלמעלה, כיסא, מטבעות, כיכר לחם, ספר חשבונות. צור אותם **על רקע ירוק אחיד וחלק** (לניתוק), עם רווח מסביב לכל חלק, בלי צל על הרקע.
- **פתיח (3 שניות):** אגרוף שחור שנפתח והופך לכתר זהב, והכותרת «בין כוח לברכה» (נכתבת בקוד). מכאן הצורך בחלקי כתר/אגרוף/יד נקיים.

## 5. תהליך (עוצרים בכל שלב לאישור)
**שלב 0:** קרא את הבריף. החזר **5 שורות** שמסכמות מה הבנת, ושאל מה לא ברור. אל תיצור תמונות עדיין.
**שלב 1:** צור **תמונה אחת**: T1 (למטה). הצג, ובדוק ברשימת הבדיקה (סעיף 6). חכה לאישורי.
**שלב 2:** אחרי אישור, צור את T2–T6 (3 במקביל לכל היותר). הצג גיליון אחד עם כולן. חכה.
**שלב 3:** אשלח לך את 75 הרגעים. הצע **תוכנית תמונות**: קבץ רגעים שאפשר לשרת בתמונה אחת או באותו חלק. טבלה: מזהה (`P01`...), אילו רגעים משרתת, תיאור שורה אחת, האם צריכה חלקים נפרדים, ופרומפט באנגלית. **אל תיצור את הכמות לפני אישור.** ציין אומדן כמה תמונות בסך הכול.
**שלב 4:** אחרי אישור, צור בקבוצות של 3–4, שמור כל תמונה מיד, והצג כל קבוצה.
**שלב 5:** מסירה: תיקייה `art/`, גיליון מגע של כולן, ורשימת **"מה חלש"** כנה (בלי לתקן יותר מפעם אחת לכל תמונה).

## 6. בדיקה לכל תמונה (✅ / ❌ / ⚠️)
פנים (אין) · טקסט/ספרות (אין) · נשק (אין) · ידיים (חמש אצבעות) · סגנון וצבעי דמויות עקביים · כתר = זהב ואגרוף = שחור־אדום · הטבעת והכיסאות כמתואר · אזורים שקטים · אובייקט למעבר ברור · 9:16.

## 7. שמות קבצים
`T1_..T6_` (בדיקה), `P01_name.png` (רקעים), `S01_name.png` (חלקים). באנגלית וללא רווחים.

## 8. תקציב
כל יצירת תמונה בתשלום עולה כסף וקיימת תקרה חודשית. **אל תחרוג משלב**, אל תריץ אצוות בלי אישור, ועדכן אותי אחרי כל שלב כמה תמונות נוצרו.

## 9. אם יש לך גישה לקוד/מאגר (Codex)
אפשר להשתמש ב־`.claude/skills/keyframe-images/scripts/gemini_image.py` (נדרש `GEMINI_API_KEY` בסביבה; אסור להדפיס מפתחות) עם `--ref`. אם אין לך מפתח או גישה: צור במה שיש לך בשיחה, ואל תבקש ממני להדביק מפתח.

## 10. ערכת בדיקה: 6 תמונות (T1–T6)
לכל תמונה: `STYLE` (מהסעיף 2) + `Scene:` שלמטה.

**T1 `T1_table_crown.png`** שולחן עגול מלמעלה, כתר זהב במרכז
Scene: Top-down view of a round table inside a thin gold ring drawn around it (the ring marks the limits of legitimate debate). A cream figure (Isaac, wool mantle, staff) on one side lifts a gold paper crown toward an orange figure's chair; a pink veiled figure (Rebecca) on the opposite side pulls the crown with a thin thread toward a blue figure's chair. The crown sits in the middle of the tug of war. Both stay seated at the table inside the ring: an argument without agreement, but within bounds. Two more empty chairs. All figures are simple shapes seen from above, no faces.

**T2 `T2_crown_shadow_fist.png`** (הרעיון המרכזי) צל הכתר הוא אגרוף
Scene: Top-down round table with a gold paper crown in the middle. The crown casts a long black ink shadow across the table that is clearly the silhouette of a clenched fist. Ink-black and red halftone in the shadow, warm gold on the crown side.

**T3 `T3_split_crown_fist.png`** מסך מפוצל
Scene: Split composition stacked vertically. Top half: a gold paper crown with radiating halftone light rays on warm cream. Bottom half: a black ink fist with red halftone dots and jagged torn edges on grey. A long road of paper strips runs between the two halves.

**T4 `T4_tent_shadows.png`** פתיחה: שני צללים על יריעה
Scene: A large tent cloth lit warmly from inside; two huge paper-cut shadows on it, an old seated man with a staff and a standing woman in a veil, facing each other in argument (hands raised). Only shadows, no figures visible. Dusk sky around, cut-paper stars.

**T5 `T5_sprites_sheet.png`** גיליון חלקים להנפשה (על רקע ירוק אחיד לניתוק)
Scene: A sheet of separate cut-paper objects on a flat solid bright green background, each with generous space around it: a gold crown, a black ink fist, an open blue hand, a cream hand holding a staff, a pink veil, a round table seen from above, an empty wooden chair, a stack of coins, a loaf of bread. No faces, no text.

**T6 `T6_fist_breaks_ring.png`** האגרוף פורץ את הטבעת (אח מול אויב)
Scene: Top-down round table inside a thin gold ring, with an orange figure (Esau) seated at it. A huge black ink fist pushes up through the ring from the orange figure's side and the gold ring cracks and breaks apart at that point; the orange chair is tipping outside the ring into darkness. Other seated figures (cream, pink, blue) stay inside the intact part of the ring. No faces, no blood, no weapons.


**התחל עכשיו בשלב 0.**
