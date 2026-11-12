# -*- coding: utf-8 -*-
"""(תחביר Gemini 3.8) מפרק את הטקסט המנוקד עם התגיות לקטעים: לכל קטע טקסט נקי (בלי תגיות) + סגנון נפרד + שתיקה אחריו.
תגיות לא נשלחות כטקסט (כך שלא יוקראו בטעות). שימוש: python3 make_plan.py tts_input.txt tts_plan.json"""
import re, json, sys
BASE=("Hebrew narration of a Torah-portion reflection, delivered by a thoughtful, warm teacher speaking to friends who respect him: "
      "friendly and conversational yet dignified. Unhurried pace of about 110 words per minute, clear articulation of the vowel-marked words, "
      "natural pauses at commas and full stops. Emotion is subtle: gentle warmth on human moments, lower and more measured when the text turns serious. "
      "Never theatrical, never newsreader-stiff, no sing-song. Do not read any bracketed words aloud.")
DIR={ # תגית -> (כיוון באנגלית, שתיקה בשניות לפני, שתיקה אחרי, היקף: para=כל הפסקה, sent=המשפט הבא, none)
 "Quiet tension":("quiet, restrained, a little tense",0,0,"para"),
 "Warm, reflective":("warm and reflective",0,0,"para"),
 "Keep the same warmth":("keep the same warm, reflective tone as the previous paragraph",0,0,"para"),
 "Genuine question":("a sincere, genuinely curious question, with a soft rise at the end",0,0,"sent"),
 "Slow, deliberate":("slow and deliberate, each word weighed, as if quoting scripture",0,0,"sent"),
 "Lower voice":("a lower, more serious voice, quiet but clear",0,0,"sent"),
 "Firm, controlled":("firm and controlled, steady and not angry",0,0,"sent"),
 "Slow down":("slow down a little more than usual",0,0,"para"),
 "Quieter, with care":("quieter and careful, gentle, with great care",0,0,"sent"),
 "Pause, then renewed resolve":("calm renewed resolve",0.8,0,"para"),
 "Quiet conviction":("quiet conviction",0,0,"para"),
 "Stress both words":("give clear weight to the first two quoted words",0,0,"sent"),
 "Cautious hope":("cautiously hopeful",0,0,"para"),
 "Finish gently":("finish gently, a little softer and slower",0,0,"sent"),
}
INLINE={"Brief pause":"<short pause>"}   # Gemini 3.8: אירועים נקודתיים בסוגריים משולשים, באנגלית, בתוך הטקסט
PAUSE={"Hold silence":1.4}               # שתיקה ארוכה: נמדדת בהרכבה (לא תגית)
txt=open(sys.argv[1],encoding='utf-8').read().strip()
paras=[p.strip() for p in re.split(r'\n\s*\n',txt) if p.strip()]
plan={}; prev_para_dir=None; order=[]
for pi,p in enumerate(paras,1):
    toks=re.split(r'(\[[^\]]+\])',p)
    toks=[t for t in toks if t and t.strip()]
    para_dir=None; pre=0.0
    segs=[]; cur=[]; sent_dir=None; sent_open=False; pending_pause=0.0
    def flush(pause_after=0.0):
        global cur
        t=" ".join(x.strip() for x in cur).strip()
        if t: segs.append({"text":t,"sent_dir":cur_dir[0],"pause_after":pause_after})
        cur=[]
    cur_dir=[None]
    for tk in toks:
        m=re.fullmatch(r'\[([^\]]+)\]',tk.strip())
        if m:
            name=m.group(1)
            if name in INLINE:
                cur.append(INLINE[name]); continue
            if name in PAUSE:
                if " ".join(cur).strip(): flush(PAUSE[name])
                elif segs: segs[-1]["pause_after"]+=PAUSE[name]
                cur_dir[0]=None; continue
            d,pb,pa,scope=DIR[name]
            if scope=="para":
                para_dir = prev_para_dir if name=="Keep the same warmth" and prev_para_dir else d
                if pb: pre=pb
            else:
                flush(0.0); cur_dir[0]=d; sent_open=True
            continue
        # טקסט: אם יש כיוון משפט פתוח, חותכים אחרי סוף המשפט הראשון
        text=tk
        if cur_dir[0]:
            mm=re.search(r'[.?!](?=\s|$)',text)
            if mm:
                head,tail=text[:mm.end()],text[mm.end():]
                cur.append(head); flush(0.0); cur_dir[0]=None
                if tail.strip(): cur.append(tail)
                continue
        cur.append(text)
    flush(0.0)
    if para_dir: prev_para_dir=para_dir
    if pre and segs: segs[0]["pre_pause"]=pre
    for si,s in enumerate(segs,1):
        key=f"p{pi}{chr(96+si)}"
        d="; ".join(x for x in [para_dir,s['sent_dir']] if x)
        style=BASE+(" Direction for this passage: "+d+"." if d else "")
        item={"text":s["text"],"style":style,"pause_after":s["pause_after"]}
        if s.get("pre_pause"): item["pre_pause"]=s["pre_pause"]
        plan[key]=item; order.append(key)
json.dump({"order":order,"items":plan},open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
words=0
for k in order:
    it=plan[k]; w=len(re.sub(r'<[^>]+>','',re.sub(r'[\u0591-\u05C7]','',it['text'])).split()); words+=w
    print(k,w,'w','pause',it['pause_after'],'|',it['style'].split('Direction for this passage: ')[-1][:70] if 'Direction' in it['style'] else '(base)','|',re.sub(r'[֑-ׇ]','',it['text'])[:45])
print(len(order),'segments',words,'words')
