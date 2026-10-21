import json,re,wave
src=open('v2/cues.py',encoding='utf-8').read()
pre=src[:src.index('def strip')]
ns={};exec(pre,{'json':json,'re':re,'open':open},ns)  # loads v2 words only for syntax; SPEC defined
old=ns['SPEC']
SPEC={}
for k,v in old.items():
    n=int(k[1:])
    SPEC[f's{n if n<3 else n+1:02d}']=v
SPEC['s03']=[('title','שני',1,0.4),('chat','הרגיל',1,2.5),('ask','שואלים',1,4.1),('ans','ומקבלים',1,4.5),('cannot','אפשר',1,7.1),('menu','בתפריט',1,9.2),('area','לאזור',1,10.1),('works','עובד',1,14.3),('p1','פותח',1,15.1),('p2','מריץ',1,16.2),('p3','זוכר',1,17.4),('p4','ומפעיל',1,18.7),('why','ולמה',1,20.2),('long','ארוכה',1,22.9),('files','בקבצים',1,24.8),('rule','אצבע',1,27.6),('chatuse','לשיחה',1,28.5),('ask2','לשאלות',1,29.3),('write','ולכתיבת',1,29.8),('regular','רגיל',3,31.4),('build','לבנייה',1,32.2),('files2','עם',1,33.6),('code','וקוד',1,34.2)]
def fix(k,n,kw=None,nth=None):
    L=SPEC[k]
    for j,(a,b,c,d) in enumerate(L):
        if a==n:L[j]=(a,kw if kw is not None else b,nth if nth is not None else c,d)
fix('s02','apprentice','שוליה');fix('s04','skill','Skill');fix('s05','studio','Studio');fix('s05','m1','קול',1);fix('s07','upgrade','שידרגנו');fix('s13','frames','ופרימים')
SPEC['s15']=[('open','פותחים',1,1.0),('cc','ועוברים',1,3.0),('attach','מצרפים',1,6.0),('write','וכותבים',1,8.0),('when','באורך',1,11.5),('ask','שאל',1,15.4),('table','בטבלה',1,17.6),('wait','ואל',1,18.5),('stamp','תפיק',1,20.0),('secret','הסוד',1,21.2)]
# fixes for renamed/changed scenes
SPEC['s11']=[(n,kw,nth,fb) if n!='n24' else (n,'24',1,fb) for n,kw,nth,fb in SPEC['s11']]
W=json.load(open('v3/words.json'))
def strip(s):return re.sub(r'[^א-ת0-9A-Za-z]','',s)
out={};miss=[]
for k in sorted(SPEC):
    ws=W[k];out[k]={}
    for name,kw,nth,fb in SPEC[k]:
        c=0;t=None
        for x in ws:
            if strip(kw) and strip(kw) in strip(x['w']):
                c+=1
                if c==nth:t=x['s'];break
        if t is None:t=fb;miss.append((k,name,kw))
        out[k][name]=round(t,2)
print('missing:',miss)
dur={}
for k in sorted(SPEC):
    with wave.open(f'v3/vo/{k}.wav') as w:dur[k]=round(w.getnframes()/w.getframerate(),2)
json.dump(dict(cues=out,dur=dur),open('v3/cues.json','w'),ensure_ascii=False)
D=[round(dur[k]+1.1+0.6*0,2) for k in sorted(SPEC)];D[-1]=round(dur['s16']+3.0,2)
json.dump(D,open('v3/durations.json','w'));print(D,sum(D))
