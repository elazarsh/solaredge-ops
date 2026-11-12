# -*- coding: utf-8 -*-
"""בונה timeline.json (רגעים עם זמנים) ו־subs.json (כתוביות) מהקלטה: מריצים מתיקיית toldot-video."""
import csv,json,re
wt=json.load(open('voice/word_times.json',encoding='utf-8'))
T=wt['times']; words=wt['words']
rows=list(csv.DictReader(open('handoff/beats.csv',encoding='utf-8-sig')))
beats=[]; n=0
for r in rows:
    b=int(r['beat'])
    if b==0: continue
    k=len(r['narration_he'].split()); w=[(words[n+i],T[n+i][0],T[n+i][1]) for i in range(k)]; n+=k
    beats.append({'n':b,'s':w[0][1],'e':w[-1][2],'text':r['narration_he'],'words':w})
assert n==len(words),(n,len(words))
# כתוביות: מקטעים של עד 6 מילים, חיתוך מועדף בסימני פיסוק
subs=[]
for b in beats:
    ws=b['words']; i=0
    while i<len(ws):
        rem=len(ws)-i
        if rem<=7: j=len(ws)
        else:
            j=i+6
            for k in range(i+3,min(i+7,len(ws))):
                if re.search(r'[.,:?!״"]$',ws[k-1][0]): j=k
        ch=ws[i:j]; subs.append({'t0':round(ch[0][1]-0.05,3),'t1':round(ch[-1][2]+0.3,3),'text':' '.join(x[0] for x in ch)}); i=j
for a,b in zip(subs,subs[1:]):
    if a['t1']>b['t0']-0.03: a['t1']=round(b['t0']-0.03,3)
out={'beats':[{k:v for k,v in b.items() if k!='words'} for b in beats],'subs':subs,'audio_end':wt['duration']}
json.dump(out,open('build/timeline.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(beats),'beats',len(subs),'subtitle chunks; max chunk words',max(len(s['text'].split()) for s in subs),'; audio end',wt['duration'])
