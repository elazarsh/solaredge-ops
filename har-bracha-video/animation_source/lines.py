# Voice lines: id, character, gemini voice, niqqud text, plain text, direction, start (s), window (s)
KAL="Speak in Hebrew. Character: a slick, shady lawyer who is also a pigeon, selling a dubious apartment. Warm, smooth, oily baritone, overconfident, a smile in the voice, quick rolling salesman rhythm, no long pauses between words."
YOS="Speak in Hebrew. Character: a young male mouse, dry, sarcastic and tired, slightly nasal, deadpan, a bit of a whiner; sentences end with a complaining rising tone. Natural everyday Israeli speech, not theatrical."
LIA="Speak in Hebrew. Character: a young female mouse, warm, bright and naive, breathy genuine enthusiasm, sweet and sincere. Natural everyday Israeli speech."
NAR="Speak in Hebrew. Character: a neutral municipal public announcement voice, flat, polite, no smile, no emphasis, slightly bored, brisk, rapid pace, about 3.5 words per second, no long pauses."
LINES=[
 dict(id="k1",ch="kalman",voice="Algieba",
  nik="תִּכָּנְסוּ, שִׂימוּ לֵב לָאוֹר, שִׂימוּ לֵב לַשֶּׁטַח, שִׂימוּ לֵב לַקִּירוֹת, מְמוּחְזָרִים, אֶקוֹלוֹגִיִּים, בְּלִי רְטִיבוּת, חוּץ מִגֶּשֶׁם.",
  plain="תיכנסו. שימו לב לאור, שימו לב לשטח, שימו לב לקירות: ממוחזרים. אקולוגיים. בלי רטיבות. חוץ מגשם.",
  style=KAL+" VERY fast pace, roughly 3.5 words per second, tight rhythm with almost no pauses between phrases. Deliver 'חוץ מגשם' last, with an innocent, casual tone, as if it's a tiny detail.",start=0.3,win=5.6),
 dict(id="l1",ch="liat",voice="Leda",nik="וָואוּ.",plain="וואו.",
  style=LIA+" A short breathy delighted gasp: 'wow'.",start=5.1,win=1.0),
 dict(id="y1",ch="yossi",voice="Zubenelgenubi",nik="וּמָה עִם הָאַרְנוֹנָה?",plain="ומה עם הארנונה?",
  style=YOS+" Suspicious, deadpan, a raised-eyebrow question. Enunciate every syllable clearly, including the final syllable.",start=6.2,win=1.7),
 dict(id="k2",ch="kalman",voice="Algieba",nik="אֵין אַרְנוֹנָה.",plain="אין ארנונה.",
  style=KAL+" Dropped casually and extra friendly, like a minor detail. Enunciate every syllable clearly, including the final syllable 'נה'.",start=8.0,win=1.1),
 dict(id="l2",ch="liat",voice="Leda",nik="אֵין?",plain="אין?",
  style=LIA+" Puzzled but still smiling, sweet.",start=9.2,win=0.8),
 dict(id="k3",ch="kalman",voice="Algieba",nik="הַמּוֹעָצָה לֹא אוֹסֶפֶת כָּאן כְּלוּם.",plain="המועצה לא אוספת כאן כלום.",
  style=KAL+" Cheerful, as if it were a perk of the apartment. Fast but enunciate every syllable clearly, finish the last word 'כְּלוּם' fully.",start=9.9,win=2.0),
 dict(id="k4",ch="kalman",voice="Algieba",
  nik="אָז תּוֹשָׁבִים בִּקְצָרָה, קַרְטוֹנִים לַקַּרְטוֹנִיָּה, גֶּזֶם לְפִנַּת הַגֶּזֶם, שַׂקִּיּוֹת לְתוֹךְ הַפַּח.",
  plain="אז תושבים, בקצרה: קרטונים – לקרטוניה. גזם – לפינת הגזם. שקיות – לתוך הפח.",
  style=KAL+" Now he drops the sales act: tired, honest and sincere, like a weary public service message to the audience, a small sigh before starting, brisk pace, roughly 3 words per second, short pauses only between the three items, slight emphasis on each of the three items.",start=18.3,win=5.5),
 dict(id="y2",ch="yossi",voice="Zubenelgenubi",nik="אוּף, זֶה הַבַּיִת שֶׁלָּנוּ.",plain="אוף... זה הבית שלנו.",
  style=YOS+" An exasperated whiny groan, funny and sulky, not angry at anyone, like a long sigh to the sky; stretch the word 'אוף' only slightly, then say the rest quickly.",start=24.2,win=2.0),
 dict(id="l3",ch="liat",voice="Leda",nik="וַאֲנִי כְּבָר קָנִיתִי וִילוֹנוֹת.",plain="ואני כבר קניתי וילונות...",
  style=LIA+" Soft, small and gently disappointed, a little pout, no crying, a quick sad trail-off at the end.",start=26.2,win=2.0),
 dict(id="k5",ch="kalman",voice="Algieba",nik="יֵשׁ לִי עוֹד פְּגִישָׁה.",plain="יש לי עוד פגישה.",
  style=KAL+" Sheepish, trying to slip away politely, slightly rushed.",start=28.2,win=1.1),
 dict(id="n1",ch="narrator",voice="Schedar",
  nik="וְשִׁלְחוּ יֶלֶד בַּגִּיל הַמַּתְאִים לִזְרוֹק אֶת הַפַּח, מִחוּץ לַפַּח לֹא נֶאֱסָף.",
  plain="ושלחו ילד בגיל המתאים לזרוק את הפח. מחוץ לפח – לא נאסף.",
  style=NAR+" Slow down slightly on the last words 'לֹא נֶאֱסָף'.",start=30.0,win=4.4),
]
