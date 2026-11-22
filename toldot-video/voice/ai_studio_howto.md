# איך מריצים קול בגוגל AI Studio (בלי מפתח API)

**מפתח לא נחוץ.** דף הניסוי של AI Studio עובד עם כניסה בחשבון גוגל רגיל. מפתח API נדרש רק כשקוד (כמוני) קורא לשירות. התפריטים משתנים לפעמים: אם משהו לא תואם למה שאתה רואה, תכתוב לי מה יש במסך ואכוון אותך.

## צעדים
1. היכנס ל־**aistudio.google.com** עם חשבון גוגל.
2. בתפריט הצד חפש **Generate Media** (או **Speech**) ← **Text to speech / Speech generation**. אם אין, בבורר המודלים בחר מודל ששמו מכיל **TTS** (למשל «Gemini 3.8 Flash TTS»).
3. בחר מצב **Single-speaker** (דובר אחד).
4. בחר **קול** (Voice) מהרשימה.
5. בשדה **Style instructions** (הוראות סגנון) הדבק את הבלוק שלמטה. אם אין שדה כזה, תגיד לי ואתאים.
6. בשדה הטקסט הדבק את הטקסט המנוקד. **המודל הנוכחי קורא את שדה הטקסט מילה במילה.** לכן: **בלי סוגריים מרובעים [ ]** ובלי הוראות במילים. מותר רק תג נקודתי **בסוגריים משולשים באנגלית** כמו `<short pause>` (כבר מופיע בטקסט המוכן). הנימה והקצב נמצאים בשדה הסגנון.
7. לחץ **Run**, האזן, ואז **הורד** (Download או ⋮).

## סבב 1: בחירת קול גברי (3–4 קבצים)
קולות גבריים לבדיקה (לפי תיאורי גוגל): **Charon** (מסביר), **Orus** (יציב), ואם זמינים: **Achird** (ידידותי) ו־**Sadaltager** (בקי). הדבק בכל הרצה את אותו טקסט ואת אותה הוראת סגנון, **ושנה רק את הקול**.

**הוראת סגנון:**
```
Hebrew narration of a Torah-portion reflection, spoken by a thoughtful, warm male teacher to friends who respect him: friendly and conversational yet dignified. Speak SLOWLY and deliberately, about 90 words per minute, clearly slower than normal conversation, giving every sentence room to land. Articulate every vowel-marked word clearly. Take a natural breath between sentences. On the key phrase of a paragraph (the punch), slow down further, lower the pitch slightly, and let the last two or three words land with weight; honor every marked pause as a real, audible pause. Emotion is subtle: gentle warmth on human moments, quieter and more measured when the text turns serious. Never theatrical, never newsreader-stiff, no sing-song, never rushed. Do not read any bracketed words aloud.
```

**טקסט לבדיקה (פסקה 1, כולל תג `<short pause>`):**
```
הַפָּרָשָׁה מַתְחִילָה בְּוִכּוּחַ לֹא פָּשׁוּט בֵּין בְּנֵי זוּג. יִצְחָק רוֹצֶה לְבָרֵךְ אֶת עֵשָׂו וְרִבְקָה עוֹשָׂה הַכֹּל כְּדֵי שֶׁהַבְּרָכָה תַּגִּיעַ לְיַעֲקֹב. הַמַּחֲלֹקֶת מַתְחִילָה בְּחֶדֶר אֶחָד, אֲבָל הַשְּׁאֵלָה גְּדוֹלָה מֵהַבַּיִת שֶׁלָּהֶם. לְאַבְרָהָם הֻבְטַח שֶׁיִּהְיֶה אַב הֲמוֹן גּוֹיִים וְשֶׁבְּזַרְעוֹ יִתְבָּרְכוּ גּוֹיֵי הָאָרֶץ. עַל הַשֻּׁלְחָן נִמְצֵאת הַשְּׁאֵלָה מִי יִשָּׂא אֶת הַהַבְטָחָה הַזֹּאת? <short pause> מִי יָדַע לְהִשְׁתַּמֵּשׁ בְּצוּרָה רְאוּיָה בַּכּוֹחַ הֶעָצוּם הַזֶּה לְאֹרֶךְ הַדֶּרֶךְ?
```

שמור כל תוצאה כ־`voice_Charon.wav` וכו'.

## איך מעבירים לי את הקבצים
העלה ל־Google Drive לתיקייה בשם **toldot-voice** (בדיוק), ותכתוב לי כאן. אני אקרא משם. (אם אפליקציית הצ'אט מאפשרת צירוף קבצים, אפשר גם כך.)

## אחרי שנבחר קול
נריץ את כל התוכנית: `tts_paste_ready.md` (20 קטעים, לכל קטע שדה סגנון ושדה טקסט) ב־AI Studio לפי רשימת הרצה שאכין, או שאריץ אני דרך מפתח אם תעדיף (קודם אומדן עלות ואישורך).

מקורות: [תיעוד Gemini TTS](https://ai.google.dev/gemini-api/docs/speech-generation), [רשימת קולות](https://ai.google.dev/api/voices).
