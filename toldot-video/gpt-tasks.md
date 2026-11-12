# משימות ל־GPT: תמונות מפתח לסרטון «תולדות»

(להדביק ל־ChatGPT/Codex כפרויקט אחד, יחד עם `style.txt`, ולצרף את ציור הייחוס מסרט "נח" אם יש. אם אין, שלב A יוצר אותו.)

## מי אתה ומה המשימה
אתה מפיק התמונות של סרטון איור מונפש בעברית על פרשת תולדות (יצחק, רבקה, עשו, יעקב). אתה יוצר **תמונות מפתח ב־16:9** שנעים אחר כך בסרטון (Veo, או תנועת מצלמה) ולכן כל תמונה חייבת להיות נקייה, אחת, וקריאה.

## כללי ברזל (חלים על כל תמונה)
1. **בלי פנים. בשום תמונה.** אנשים רק מהגב, כצללית או צל, חתוכים בצוואר, או כידיים וזרועות בלבד. אסור: עיניים, אף, פה, פרופיל פנים. (זה הכלל הכי חשוב, והסיבה: דמויות מקראיות.)
2. **בלי טקסט בתמונה.** בלי אותיות, בלי ספרות, בלי חתימות, בלי כתובות על קירות או קלפים. הפסוקים מתווספים אחר כך ב־HTML. איפה שכתוב "אזור שקט" משאירים נייר נקי.
3. **סגנון אחד:** הדבק את תוכן `style.txt` בתחילת כל פרומפט (הוא כבר מוגדר למטה כ־`STYLE`). צרף את ציור הייחוס לכל תמונה.
4. **נושא מרכזי בתוך 80% המרכזיים** של התמונה (יהיה זום איטי). 16:9. מומלץ `1536x864`; אם לא נתמך: `1536x1024` וחיתוך 16:9.
5. **אפס אלימות מוצגת:** בלי נשק מכוון, בלי דם, בלי לוחמים. שוט 17, 19, 25 הם מאופקים בכוונה.
6. **סצנה אחת, רעיון אחד לכל תמונה.** בלי פאנלים ובלי מסגרות.
7. **אובייקט למעבר:** בתמונות שמצוין בהן "אובייקט למעבר" האובייקט חייב להיות ברור, מבודד וגדול מספיק (המעבר גוזר אותו אוטומטית).
8. **שם קובץ קבוע:** `K01.png` וכו' (ראה למטה). אחרי כל תמונה: לשמור מיד.

## איך עובדים (עוצרים לאישור בכל שלב)
- **שלב A:** סגנון (3 דוגמאות) ← עצור, המשתמש בוחר.
- **שלב B:** 8 דפי ייחוס ← עצור, המשתמש מאשר.
- **שלב C:** תמונה אחת קודם (`K02`), להציג ← רק אז אצווה של 3–4 במקביל.
- **שלב D:** בדיקות (בסוף הקובץ) + גיליון מגע + דוח "מה חלש".
אל תתחיל שלב עד שהקודם אושר. אל תמציא שינויים בפרומפטים; אם משהו לא מסתדר, שאל.

---

## הגדרות קבועות (להדביק בכל פרומפט שבו הדמות מופיעה)

**STYLE** = תוכן `style.txt` (פחם וגרפיט על נייר בז', ללא פנים, 16:9).

**דמויות (חתימות חזותיות, לא פנים):**
- **ISAAC:** "Isaac: an old man seen only from behind or by his hands, wrapped in a heavy cream-colored wool mantle, leaning on a plain wooden staff, white hair and beard never shown in detail, eyes never drawn."
- **REBECCA:** "Rebecca: a woman seen only from behind or by her hands, a long soft veil covering her head and shoulders, washed with faded rose-grey, a clay water jug at her side."
- **ESAU:** "Esau: a broad-shouldered man seen only from behind or by his arms, hairy forearms, a hunter's bow and quiver on his back, earthy red-ochre wash."
- **JACOB:** "Jacob: a slimmer younger man seen only from behind or by his hands, plain linen tunic, a shepherd's staff, cool blue-grey wash."
- **LAMP (ההבטחה):** "The promise: a small ancient clay oil lamp with a steady golden flame, the only spot of gold in the drawing."
- **LABAN:** אף פעם לא רואים אותו. רק "a heavy hand wearing a thick ring" וספר חשבונות. גוון ירוק־אפור קר.

**פלטות (אות ← תיאור):**
- **W:** soft warm watercolor washes (ochre, terracotta, sage green, golden morning light) over the charcoal lines.
- **G:** almost monochrome charcoal and cold grey, desaturated, heavy shadows, only a trace of faded ochre.
- **D:** very dark charcoal and cold blue-grey, low light, only the paper tone shows.
- **H:** charcoal drawing with one fragile warm wash of gold and soft rose, a moment of returning color.
- **A:** warm amber and gold washes glowing out of dark charcoal.

**פורמט פרומפט:** `STYLE + Palette: <פלטה> + <דמויות שמופיעות> + Scene: <תיאור>`

---

## שלב A: נעילת סגנון (3 דוגמאות, תמונה אחת לכל סגנון)
המשתמש כבר אוהב את סגנון הפחם של "נח". אם צורף ציור ייחוס: צור רק **דוגמה אחת** של K02 לאישור. אם לא צורף: צור שלוש דוגמאות לאותה סצנה (K02) ובקש בחירה:
- **A1 פחם וגרפיט** (ברירת המחדל, `style.txt`)
- **A2 דיו וצבעי מים** (אותו מבנה, אבל "ink wash and watercolor on cream paper")
- **A3 חיתוך נייר שכבות** ("layered cut paper silhouettes with soft shadows")
בכולם: בלי פנים, בלי טקסט.
**תוצר:** `ref/style_choice.png` (נעילת הסגנון, מצרפים לכל תמונה).

## שלב B: דפי ייחוס (8 קבצים ב־`ref/`)
כל דף: נייר בז', 16:9, כמה זוויות של אותה דמות/חפץ, **אותה חתימה בכל הזוויות**. בלי פנים ובלי טקסט.
| קובץ | תוכן |
|---|---|
| `R1_isaac.png` | ISAAC: עומד מהגב עם מטה, יושב מהגב, תקריב של שתי ידיים מקומטות על מטה |
| `R2_rebecca.png` | REBECCA: עומדת מהגב בפתח אוהל, יד מחזיקה קצה צעיף, כד חרס |
| `R3_esau.png` | ESAU: מהגב עם קשת ואשפה; בגלימת מלכות כבדה עם שוליים זהובים; זרוע שעירה וקמוצה |
| `R4_jacob.png` | JACOB: מהגב ישוב ליד מנורה; עומד עם מטה; יד חלקה (חשופה) ויד בכפפת עור עיזים שעירה |
| `R5_lamp.png` | LAMP: מנורת החרס הזהובה מכמה זוויות, ביד, על שולחן |
| `R6_chair.png` | כיסא עץ פשוט וריק על גבעה בשקיעה; אותו כיסא מקרוב ומרחוק |
| `R7_table.png` | שולחן עגול מקרשים עם 5–6 שרפרפים, בתוך מעגל אור של מנורה, וגם מהצד |
| `R8_tents.png` | האוהל של יצחק (גדול, עשוי יריעות צמר), האוהל של יעקב (קטן, צנוע), בית המדרש (בית אבן עם חלונות קטנים ושתי קומות) |

---

## שלב C: תמונות המפתח

לכל תמונה: **קובץ**, **פלטה**, **ייחוס לצירוף** (`R#` + `style_choice.png`), **פרומפט**, והערות.
(במקום `STYLE` מדביקים את `style.txt`. הפרומפטים באנגלית כי הם מדויקים יותר למודל.)

### פתיחה/סיום
**`K00.png`** · פלטה A · ייחוס: style_choice
Scene: A vast quiet sheet of warm beige paper; very low along the bottom edge a tiny smudged charcoal silhouette of a lone tent with a single glowing golden lamp inside, a few charcoal stars above. The upper two thirds nearly empty paper with soft ghost traces. *(אזור שקט עליון לכותרת. משמש גם לפתיחה וגם לסיום.)*

### פרק א
**`K01.png`** · A · R1, R2, R8
Scene: The glow of a large tent seen from outside at dusk; on the tent cloth two huge shadows cast by a lamp inside: an old seated man leaning on a staff (left) and a standing woman in a long veil (right), facing each other; her shadow-arm raised in argument, his shadow-hand lifted in refusal. Shadow-theatre composition, warm amber light behind the cloth, dark desert around. Only shadows, no people visible.

**`K02.png`** · W · R1, R2, R5 *(זו התמונה הראשונה לבדיקה)*
Scene: Close view of a low table inside a tent. In the center the small glowing golden clay lamp (the blessing). From the left an old man's wrinkled hands in a cream wool sleeve push the lamp toward the right, where a hunter's bow and quiver lean against the table edge; from the right a woman's slender hands in a rose-grey veil sleeve pull it toward the left, where a shepherd's staff and a tent pole rest. The lamp sits in the middle of the tug. Hands only, no faces.

**`K03.png`** · A · R5, R8
Scene: Very wide view from high up: a small tent with a glowing lamp at the bottom of the frame, lost under an enormous night sky full of charcoal stars; faint tiny silhouettes of countless travelers in varied garments along the far horizon; one star clearly brighter than the rest, in the same gold as the lamp. **אובייקט למעבר: הכוכב הבהיר.**

**`K04.png`** · A · R5, R7
Scene: A night desert. In the foreground a plain wooden table with a single golden clay lamp burning on it; two empty stools at the table, a hunter's bow and quiver leaning on one stool and a shepherd's staff on the other; beyond the table a long winding road of footprints running to the far horizon under stars, the lamp's light falling on the first stretch. No people. **אובייקט למעבר: להבת המנורה.**

### פרק ב
**`K05.png`** · W · R1
Scene: Close view of an old man's hands (cream wool sleeves, no face) holding a round loaf of bread above cracked dry furrowed earth in a famine; tiny green-ochre sprouts rising in the cracks; a few seeds falling from one hand. Sparse dry landscape behind. **אובייקט למעבר: כיכר הלחם.**

**`K06.png`** · W (+אוכרה) · R3, R1
Scene: A man seen only from behind, broad shoulders, hairy forearms, a hunter's bow and quiver on his back, wearing a long rich royal robe with heavy gold trim over his hunter's clothes, carrying a tray with a bowl in both hands toward a distant seated old man in a cream mantle (also from behind) at a tent door; wide golden grass field. The tension of a field-man dressed as a king serving his father. **אובייקט למעבר: המגש.**

**`K07.png`** · W→A · R3
Scene: High vantage over a valley at dusk: the same broad-shouldered man in the royal robe with bow, seen from behind, small, on a hill edge in the left third; below him in the valley hundreds of small tents each with a tiny lamp glowing like fireflies: a whole people. Quiet and golden.

### פרק ג
**`K08.png`** · H · R2
Scene: A woman seen only from behind, in a long veil, standing in a tent doorway at dusk with one hand resting on her side; drawn like a Kentridge ghost drawing: inside the outline of her body around the belly, two faint circular charcoal swirls pressing against each other like two small storms (twins), erased-and-redrawn ghost lines. No face.

**`K09.png`** · G · R2, R3
Scene: The veiled woman seen from behind, small, in the right foreground at a tent door, looking across an open sand plain toward a huge elongated shadow of a bow-carrying broad man (the shadow only), the shadow of a hand spreading over a small distant lit tent; late low sun. No face.

**`K10.png`** · H · R4, R2
Scene: Inside a quiet tent, a slim young man seen from behind sitting cross-legged beside a clay lamp and a small cooking pot, soft blue-grey tones; from the right edge of the frame a woman's hand in a veil sleeve comes to rest gently on his shoulder. Intimate, calm, lamp glow.

**`K11.png`** · G · R4, R3
Scene: The slim young man seen from behind at a tent opening, holding in his arms an enormous folded heavy hunter's garment (dark wool with fur trim, much too big for him) and a pair of rough goatskin gloves on top; ahead beyond the opening a second tent glows warm in the distance; his shoulders slightly bowed, hesitant. **אובייקט למעבר: פתח האוהל המואר.**

**`K12.png`** · G→A · R4
Scene: Extreme close view of a hand entering a tent flap: a young smooth wrist at the edge of an oversized dark wool sleeve, the hand and forearm covered with rough goatskin hair, reaching toward the warm lit inside; soft wavy blue-grey charcoal lines float out behind it like a voice (sound waves). No body or face visible.

### פרק ד
**`K13.png`** · A · R1, R3
Scene: An old man's hands in cream wool sleeves raised in blessing over the bowed back of a kneeling figure in a rich robe (from behind, head bowed, no face); glittering charcoal drops of dew falling from the sky; ears of wheat and heavy grape vines growing out of the ground around them, golden abundance.

**`K14.png`** · A · R6 *(אזור שקט עליון לפסוק)*
Scene: A single plain empty wooden chair on top of a lonely hill at golden sunset, a shepherd's staff leaning on it; below the hill a vast calm valley of small tents and sheep; the chair's long soft shadow stretches down the hill. The top third kept as plain paper (quiet area). No people.

**`K15.png`** · A→G
Scene: A huge figure seen only from behind, draped in a very wide open cloak that spreads like a roof over many small silhouettes of people sheltering beneath; most face toward him, a few small silhouettes at the edge are stepping out from under the cloak with their backs to him. Dusk, charcoal sky. No faces.

**`K16.png`** · D (+אור זהוב) 
Scene: A very large dark charcoal hand, drawn mid-way as it opens from a clenched fist, looming above a crowd of many small raised hands and arms reaching up from below (an unseen crowd of voices drawn only as hands); a faint ray of light between the fingers of the big hand. Pure hands, no faces.

### פרק ה
**`K17.png`** · D · R3 *(אזור שקט עליון לפסוק)*
Scene: A broad-shouldered man seen from behind standing at the entrance of a dark tent at night, one large hand clenched into a tight fist at his side, red-ochre wash only on his arm; his huge shadow stretching along the ground toward a distant small blue-grey tent. No weapons, no violence. The top third plain dark paper (quiet area).

**`K18.png`** · G · R6 + **`K18b.png`** (סיום)
Scene (K18): A hand holding a rag (left edge) caught mid-motion erasing the legs of a plain wooden chair drawn in charcoal; the legs half smudged away, ghost traces and smudges where they were, the seat and back still partly visible and starting to tilt. The act of erasing is visible (Kentridge).
Scene (K18b): the same composition, the chair now completely erased, only smudges and faint ghost lines on the paper, hand and rag at the lower right. *(תמונת סיום ל־Veo.)*

**`K19.png`** · D
Scene: Close view of a hand holding a reed pen hovering just above a blank signature line at the bottom of a sheet of parchment; one round drop of black ink hanging from the pen tip about to fall; the hand hesitating, slightly withdrawn. The parchment is completely empty (no writing). **אובייקט למעבר: טיפת הדיו.**

**`K20.png`** · D (+מעגל אור זהוב) · R7
Scene: Wide night view: a long round plank table in a circle of golden lamplight with maps and papers on it, several stools around it with silhouettes seen from behind seated at the table; one stool stands apart, pushed back outside the circle of light into the dark, turned away, empty. **אובייקט למעבר: מעגל האור. (חשוב: אותו שולחן יחזור ב־K38.)**

### פרק ו
**`K21.png`** · G · R2, R4
Scene: Night: a woman's hands (veil sleeve) pressing a travel bundle and a shepherd's staff into the hands of a young man seen from behind, hurried; a torch flickering; behind them a road splitting into darkness. No faces.

**`K22.png`** · G (ירוק־אפור קר) 
Scene: Top-down close view: a heavy hand wearing a thick ring holds a reed pen over an open ledger page filled with crossed-out and rewritten tally marks smudged in several layers; the other hand's fingertips drag small piles of coins across the page; at the page edge tiny silhouettes of sheep drawn as marks. No body, no face. **אובייקט למעבר: דף הספר.**

**`K23.png`** · D (+זהב נר) · R8
Scene: Interior of an ancient stone study-house at night: a long table with open scrolls and a single candle, a young man seen from behind bent over a scroll, shelves of scrolls behind; on the stone wall to the right fourteen scratched vertical tally strokes in groups of five (four strokes crossed by a diagonal) plus four strokes. Quiet and dim. *(ספרו את השריטות: חייבות להיות 14.)*

**`K24.png`** · H · R8 + **`K24b.png`** (סיום)
Scene (K24): Exterior of a two-story stone study-house at dusk; masons' hands and many small figures seen from behind on wooden-pole scaffolding hauling stone blocks up to begin a third floor; a few lit windows. Sense of building upward.
Scene (K24b): the same house now with a finished third floor, scaffold gone, a warm window lit at the top; the whole house taller.

**`K25.png`** · D *(שוט רגיש. מאופק.)*
Scene: The inside of a heavy plain door at dawn seen from inside a small dark concrete room (this one frame may be modern): a hand gripping the inner door handle tightly from inside, only the wrist and hand visible, knuckles tense; a thin line of cold pale morning light under the door; nothing else visible; stillness. Respectful and restrained: no blood, no weapons, no people, no faces.

**`K26.png`** · H · R2, R4
Scene: Dawn at a tent door: the veiled woman seen from behind, one hand holding the veil edge, looking down a long road where a tiny slim silhouette walks away toward a far hill; on the threshold at her feet a small lit clay lamp and an extra empty bowl set out for his return; first rose-gold light on the horizon.

**`K27.png`** · H *(רקע ל־HTML)*
Scene: A large plain wall of stone drawn in charcoal, nearly empty; in the lower left only four short scratched vertical tally strokes, freshly made; a wide empty area to the right and above kept clean (more strokes will be added later by animation); a faint sunrise glow at the top edge. No text.

### פרק ז–ח
**`K28.png`** · A (על כהה) · R1 *(אזור שקט עליון לפסוק)*
Scene: In darkness, an old man's hand (cream wool sleeve) held out open, palm up, in the opening of a tent as if calling someone; a path of golden light flows from the palm toward a faint road; soft concentric charcoal ripples around it (a calling voice). The top third plain dark paper (quiet area). No face. **אובייקט למעבר: היד הפתוחה.**

**`K29.png`** · A · R1, R4
Scene: Extreme close-up: an old man's wrinkled hands in cream wool sleeves holding a younger, bare, smooth hand between both of his; warm gold light glows in the clasp and rises upward as faint stars and specks of dust. No faces. *(מקביל ל־K12: שם כפפה שעירה, כאן יד חשופה.)*

**`K30.png`** · G→H · R4 *(אזור שקט בתחתית ל־«צא ולמד»)*
Scene: A young man seen from behind walking on a road at the border between night and dawn: the left half of the sky and ground deep charcoal night, the right half warm dawn light; a traveler's pack on his back with a loaf and a water-skin on the dark side and the tips of rolled scrolls sticking out on the dawn side; a staff in his hand. The bottom fifth plain paper (quiet area).

**`K31.png`** · G (+אוכרה וירוק־אפור קר)
Scene: Evening at an ancient well in a foreign pastoral town: a huge round stone covering the well, flocks of sheep, tents and houses in a different style (rounded roofs, woven cloths with abstract geometric patterns, no writing); a small slim traveler seen from behind approaching, tiny at the lower left; the world feels unfamiliar and its customs different. **אובייקט למעבר: כף היד (ב־K32).**

**`K32.png`** · G (ירוק־אפור קר)
Scene: Close-up of a young man's open bare palm held out; from the left edge a heavy ring-wearing hand drops fewer coins into it than expected and begins to pull some back; the open palm trembles slightly; behind, a blurred ledger. No faces.

**`K33.png`** · H · R5
Scene: A wooden balance scale in a quiet tent, hands adjusting weights: on one pan a rough stone, on the other pan a shepherd's staff, a loaf and a few coins; the beam tilts; two hands (one young, one from the side) gently adjusting. Warm lamp light.

### פרק ט
**`K34.png`** · A · R1, R2 *(חזרה מתוקנת על K01)*
Scene: Two large shadows on a tent cloth, as in the film's first frame: an old seated man with a staff and a standing veiled woman, but now side by side facing the same direction, both shadows pointing toward a glowing road beyond the cloth; a lit lamp between them. Only shadows.

**`K35.png`** · A · R1, R2, R5
Scene: Close-up: an old man's hands in cream wool sleeves passing the small golden clay lamp (the promise, steady flame) into a younger man's waiting open hands; a woman's veil-sleeved hand supports from below; golden light on the hands. No faces. *(אותה מנורה בדיוק מ־R5.)*

**`K36.png`** · G · R3, R4
Scene: Two men seen only from behind at the top of a hill at dusk: the older brother (broad shoulders, red-ochre wash) on the left points an arm toward a darkening horizon with a faint storm cloud far away; the younger brother (blue-grey wash) on the right stands still, shoulders square, looking toward a different part of the sky where the sun sets; between them a clear gap of paper. No faces.

**`K37.png`** · H · R4
Scene: A young man seen from behind carrying on his back and shoulders a small stone house, its door open and a warm lamp glowing inside; his posture heavy but steady; a long road before him. No face.

**`K38.png`** · H→A · R7 *(חזרה מתוקנת על K20, אותו שולחן!)*
Scene: The same round plank table in the golden lamplight as in the earlier frame: now a young bare hand pulls the empty stool from the dark edge closer to the warm circle of lamplight; around the table all places are taken by silhouettes seen from behind; soft dawn light enters from the tent door. No faces.

---

## שלב D: בדיקות (לפני שמוסרים)
רשימה לכל תמונה, עם סימון ✅ / ❌ / ⚠️:
1. **פנים:** אין עיניים, אף, פה או פרופיל. (גם לא "נקודות" שנראות כעיניים.)
2. **טקסט:** אין אותיות או ספרות, גם לא כתמים שנראים כמו כתב.
3. **ידיים:** חמש אצבעות, מבנה סביר.
4. **סגנון:** אותו פחם על נייר בז', אותה פלטה לאותו פרק, אותן חתימות דמויות (גלימת שמנת ליצחק, צעיף לרבקה, אוכרה לעשו, כחול־אפור ליעקב).
5. **אובייקט למעבר** ברור ומבודד (אלה שסומנו).
6. **אזורי שקט** נקיים איפה שנדרש (K00, K14, K17, K28, K30).
7. **ספירה:** K23 = 14 שריטות. K27 = 4 שריטות.
8. **חזרות עקביות:** מנורה (K02, K04, K35 אותה מנורה), כיסא (K14 ← K18), שולחן (K20 ← K38 אותו שולחן), צללים באוהל (K01 ← K34).
9. **גיליון מגע:** כל התמונות בגיליון אחד. לסמן ⚠️ איפה נראה "לא שייך".

**דוח סיום:** רשימת תמונות שעברו, רשימת ⚠️ עם הסבר, ומה מוצע לתקן (בלי לתקן לבד יותר מפעם אחת לכל תמונה).
