# -*- coding: utf-8 -*-
import json
d=json.load(open('tts_plan.json',encoding='utf-8'))
out=["# להדבקה בגוגל (Gemini 3.8): קטע אחר קטע\n",
"**לכל קטע שני שדות:** (1) **Style instructions** = נימה, קצב ורגש, (2) **הטקסט** = ההקראה בלבד. בתוך הטקסט רק תגיות נקודתיות בסוגריים משולשים, באנגלית (`<short pause>`). בלי סוגריים מרובעים.",
"**שתיקה ארוכה** (3 שניות בין פסקאות, 1.4 שניות אחרי «וְאַהַרְגָה», 0.5 לפני פסקה 7) לא נשלחת כתגית: נמדדת ומוכנסת בהרכבה. מסומנת בכל קטע.\n","---\n"]
for k in d['order']:
    it=d['items'][k]
    out.append(f"## {k}\n")
    if it.get('pre_pause'): out.append(f"*שתיקה לפני (בהרכבה): {it['pre_pause']} שניות*\n")
    out.append("**Style instructions:**\n```\n"+it['style']+"\n```\n")
    out.append("**טקסט:**\n```\n"+it['text']+"\n```\n")
    if it.get('pause_after'): out.append(f"*שתיקה אחרי (בהרכבה): {it['pause_after']} שניות*\n")
    out.append("---\n")
open('tts_paste_ready.md','w',encoding='utf-8').write("\n".join(out))
base=d['items']['p1a']['style'].split(' Direction for this passage')[0]
open('style_instructions_base.txt','w',encoding='utf-8').write(base+"\n")
print(base)
