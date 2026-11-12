# -*- coding: utf-8 -*-
"""כתוביות SRT מדויקות יותר: מחלק מילים לפי זמן דיבור בפועל (בלי השתיקות), ושותק היכן שהקריין שתק.
קלט: word_times.json (מ-align.py). פלט: srt/*.srt"""
import json,re,os
d=json.load(open('voice/word_times.json',encoding='utf-8'))
words=d['words']; T=[list(t) for t in d['times']]; S=d['silences']
n=len(words)
L=[len(re.sub(r'[^א-ת]','',w)) or 1 for w in words]
# קטעים רציפים
segs=[]; a=0
for i in range(1,n+1):
    if i==n or abs(T[i][0]-T[i-1][1])>0.02:
        segs.append((a,i-1)); a=i
newT=[None]*n
fixed=0
for (a,b) in segs:
    t0=T[a][0]; t1=T[b][1]
    inner=[(s,e) for s,e,_ in S if s>=t0-0.01 and e<=t1+0.01 and (e-s)>=0.22]
    if not inner:
        for i in range(a,b+1): newT[i]=tuple(T[i])
        continue
    fixed+=len(inner)
    sil=sum(e-s for s,e in inner)
    speech=(t1-t0)-sil
    tot=sum(L[a:b+1])
    # זמן דיבור מצטבר בגבולות מילים
    cum=[0]
    for i in range(a,b+1): cum.append(cum[-1]+L[i]/tot*speech)
    # מיקום כל שתיקה בציר הדיבור
    pos=[]; acc=0; prev=t0
    for s,e in inner:
        acc+=s-prev; prev=e; pos.append((acc,e-s))
    # הצמדה לגבול מילה הקרוב
    ins={}   # אינדקס גבול (0..m) -> משך שתיקה
    for x,dur in pos:
        k=min(range(len(cum)),key=lambda j:abs(cum[j]-x))
        ins[k]=ins.get(k,0)+dur
    t=t0
    # בנייה: זמן ממשי = t0 + cum + שתיקות שלפני
    for j in range(len(cum)-1):
        pre=sum(v for k,v in ins.items() if k<=j)
        pre2=sum(v for k,v in ins.items() if k<=j+1 and k>j)  # שתיקה בסוף המילה לא נספרת לתוכה
        newT[a+j]=(round(t0+cum[j]+pre,3),round(t0+cum[j+1]+pre,3))
for i in range(n):
    if newT[i] is None: newT[i]=tuple(T[i])
print('segments',len(segs),'pauses redistributed',fixed)
# חלוקה לכתוביות: בפיסוק, בפער>=0.25 ש', או מעל 7 מילים
def brk(i):
    w=words[i]
    if re.search(r'[.?!:,]["״]?$',w): return True
    if i+1<n and newT[i+1][0]-newT[i][1]>=0.25: return True
    return False
phr=[]; cur=[]
for i in range(n):
    cur.append(i)
    if brk(i) or i==n-1:
        phr.append(cur); cur=[]
cues=[]
for ph in phr:
    k=-(-len(ph)//7)   # מספר חלקים שווה בערך, עד 7 מילים לכתובית
    sz=-(-len(ph)//k)
    for j in range(0,len(ph),sz): cues.append(ph[j:j+sz])
def ts(x):
    x=max(0,x); h=int(x//3600); m=int(x%3600//60); s=x%60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s-int(s))*1000)):03d}".replace(',1000',',999')
def build(off,path):
    lines=[]
    for k,c in enumerate(cues):
        st=newT[c[0]][0]+off-0.05
        en=newT[c[-1]][1]+off+0.15
        if k+1<len(cues): en=min(en,newT[cues[k+1][0]][0]+off-0.06)
        en=max(en,st+0.7)
        txt=' '.join(words[i] for i in c)
        if len(c)>=5:   # שבירת שורה באמצע
            h=len(c)//2+len(c)%2
            txt=' '.join(words[i] for i in c[:h])+'\n'+' '.join(words[i] for i in c[h:])
        lines.append(f"{k+1}\n{ts(st)} --> {ts(en)}\n{txt}\n")
    open(path,'w',encoding='utf-8').write('\n'.join(lines))
    return len(lines)
os.makedirs('release',exist_ok=True)
print(build(1.6,'release/bein_koach_livracha_v1.srt'),'cues (video timing, +1.6s intro)')
build(0.0,'release/bein_koach_livracha_narration_only.srt')
json.dump({'times':newT},open('voice/word_times_v2.json','w'))
