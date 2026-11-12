# -*- coding: utf-8 -*-
"""התאמה גסה בין הטקסט הנעול להקלטה, בלי תמלול: עצירות הקול (silencedetect) מול סימני פיסוק, תכנון דינמי,
ובין עוגנים: חלוקה לפי מספר אותיות. פלט: זמני מילים משוערים (word_times.json). דיוק משוער ±0.3-0.5 ש'."""
import re,subprocess,json,math,sys
WAV=sys.argv[1]
D=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',WAV],capture_output=True,text=True).stdout)
err=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',WAV,'-af','silencedetect=noise=-40dB:d=0.22','-f','null','-'],capture_output=True,text=True).stderr
S=[(float(a),float(b),float(c)) for a,b,c in re.findall(r'silence_start: ([\d.]+)\s*\n?.*?silence_end: ([\d.]+) \| silence_duration: ([\d.]+)',err.replace('\n',' \n'))]
if not S:
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',err)]
    mm=re.findall(r'silence_end: ([\d.]+) \| silence_duration: ([\d.]+)',err)
    S=[(st[i],float(mm[i][0]),float(mm[i][1])) for i in range(min(len(st),len(mm)))]
# סינון: הקצוות
lead=S[0][1] if S and S[0][0]<0.1 else 0.0
trail_start=S[-1][0] if S and S[-1][1]>=D-0.15 else D
S=[s for s in S if s[0]>=0.1 and s[1]<=D-0.15]
paras=[l for l in open('../narr.md',encoding='utf-8').read().split('\n') if l and not (l.startswith('P') and len(l)<4)]
words=[]; 
for p in paras: words+=p.split()
L=[len(re.sub(r'[^א-ת]','',w)) or 1 for w in words]
def btype(w):
    w2=w.rstrip('״"')
    if re.search(r'[.?!]$',w2) or re.search(r'[.?!]$',w): return 'S'
    if w.endswith(':'): return 'C'
    if w.endswith(','): return 'K'
    return None
B=[(i,btype(w)) for i,w in enumerate(words) if btype(w)]   # אחרי מילה i
# סוף הטקסט הוא S
speech=trail_start-lead-sum(s[2] for s in S)
r0=sum(L)/speech
print('silences',len(S),'boundaries',len(B),'lead',lead,'trail_start',trail_start,'r0 letters/s',round(r0,2))
skipB={'S':2.5,'C':1.0,'K':0.25}
def match(bt,d):
    if bt=='S': return 0 if d>=0.55 else (0.55-d)*4
    if bt=='C': return 0 if 0.3<=d<=1.1 else 0.6
    return 0 if 0.22<=d<=0.8 else (d-0.8)*2 if d>0.8 else 0.4
def skips(d): return 0.9 if d>=0.55 else 0.45
nB=len(B); nS=len(S)
INF=1e9
# עוגן 0 = התחלה (מילה -1 , סוף שתיקה=lead). עוגן סופי: מילה אחרונה, התחלת "שתיקת" הסוף
def letters(i0,i1): return sum(L[i0+1:i1+1])      # אותיות במילים i0+1..i1
# מצבים: (b,s) b בין 0..nB (0=התחלה וירטואלית), s בין 0..nS (0=התחלה וירטואלית)
best={(0,0):(0.0,None)}
def bword(b): return -1 if b==0 else B[b-1][0]
def send(s): return lead if s==0 else S[s-1][1]
def sstart(s): return S[s-1][0]
W=7
for b in range(0,nB+1):
    for s in range(0,nS+1):
        if (b,s) not in best: continue
        c0=best[(b,s)][0]
        for b2 in range(b+1,min(nB,b+W)+1):
            for s2 in range(s+1,min(nS,s+W)+1):
                skB=sum(skipB[B[k-1][1]] for k in range(b+1,b2))
                skS=sum(skips(S[k-1][2]) for k in range(s+1,s2))
                m=match(B[b2-1][1],S[s2-1][2])
                T=sstart(s2)-send(s)
                if T<=0.05: continue
                lt=letters(bword(b),bword(b2))
                r=lt/T
                rc=3*(math.log(r/r0))**2
                c=c0+skB+skS+m+rc
                if (b2,s2) not in best or c<best[(b2,s2)][0]: best[(b2,s2)]=(c,(b,s))
# סיום: מהעוגן (b,s) לסוף: מילים עד האחרונה, זמן עד trail_start
fin=None
for (b,s),(c,_) in best.items():
    lt=letters(bword(b),len(words)-1); T=trail_start-send(s)
    if T<=0.1: continue
    skB=sum(skipB[B[k-1][1]] for k in range(b+1,nB+1)); skS=sum(skips(S[k-1][2]) for k in range(s+1,nS+1))
    cc=c+skB+skS+3*(math.log(max(lt,1)/T/r0))**2
    if fin is None or cc<fin[0]: fin=(cc,(b,s))
print('total cost',round(fin[0],1))
# שחזור
path=[]; cur=fin[1]
while cur is not None:
    path.append(cur); cur=best[cur][1]
path=path[::-1]
anch=[(0,0)]+[p for p in path[1:]]
used_s=set(s for b,s in anch if s>0)
unm=[S[k-1] for k in range(1,nS+1) if k not in used_s]
print('anchors',len(anch)-1,'unmatched silences',len(unm),[(round(u[0],1),round(u[2],2)) for u in unm][:40])
# זמני מילים: בין עוגנים
wt=[None]*len(words)
pts=[]
for (b,s) in anch: pts.append((bword(b), send(s)))
pts.append((len(words)-1,trail_start))
# pts[k] = (אחרי מילה w, זמן שבו הדיבור מתחדש) ; הקטע הבא מתחיל ב-send ומסתיים בהתחלת השתיקה הבאה
segs=[]
for k in range(len(anch)):
    b,s=anch[k]
    w0=bword(b)+1
    if k+1<len(anch):
        b2,s2=anch[k+1]; w1=bword(b2); t0=send(s); t1=sstart(s2)
    else:
        w1=len(words)-1; t0=send(s); t1=trail_start
    tot=sum(L[w0:w1+1]); t=t0
    for w in range(w0,w1+1):
        d=(t1-t0)*L[w]/tot
        wt[w]=(round(t,3),round(t+d,3)); t+=d
json.dump({'words':words,'times':wt,'duration':D,'lead':lead,'trail_start':trail_start,'silences':S},open('word_times.json','w',encoding='utf-8'),ensure_ascii=False)
# בדיקת סבירות: קצב לכל קטע (מילים בדקה)
bad=0
for k in range(len(anch)):
    b,s=anch[k]; w0=bword(b)+1
    w1=bword(anch[k+1][0]) if k+1<len(anch) else len(words)-1
    t0=wt[w0][0]; t1=wt[w1][1]; n=w1-w0+1
    wpm=n/(t1-t0)*60 if t1>t0 else 0
    if wpm<70 or wpm>230: bad+=1; print('suspicious seg',w0,w1,n,'words',round(t1-t0,2),'s',round(wpm),'wpm')
print('suspicious segments:',bad)
