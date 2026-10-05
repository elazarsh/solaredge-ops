# -*- coding: utf-8 -*-
"""פסקול זמני (placeholder) מסונתז: 100 BPM, מותאם לסטוריבורד. להחלפה במוזיקה מורשית."""
import numpy as np, wave, subprocess, os, sys
from scipy.signal import fftconvolve, lfilter
from scenes import S as SCENES, BEAT
SR=44100; TOTAL=108.0; N=int(SR*TOTAL)
SCR="/tmp/claude-0/-home-user-solaredge-ops/73fe8d55-5833-5852-9694-53b5adaa6cc2/scratchpad"
rng=np.random.RandomState(5)
L=np.zeros(N,np.float32); R=np.zeros(N,np.float32); REV=np.zeros(N,np.float32)
def add(sig,t,gain=1.0,pan=0.0,rev=0.0):
    i=int(t*SR); 
    if i>=N or i<0: 
        if i<0: sig=sig[-i:]; i=0
        else: return
    sig=sig[:N-i]; n=len(sig)
    gl=gain*(1-max(0,pan)); gr=gain*(1+min(0,pan))
    L[i:i+n]+=sig*gl; R[i:i+n]+=sig*gr
    if rev: REV[i:i+n]+=sig*rev
def tt(d): return np.arange(int(d*SR))/SR
def env(d,a=0.005,dec=3.0,rel=0.0):
    t=tt(d); e=np.minimum(1,t/max(a,1e-4))*np.exp(-t*dec); 
    if rel: e*=np.clip((d-t)/rel,0,1)
    return e
def note(f): return 440*2**((f-69)/12)
def piano(m,d=1.2,vel=0.5):
    f=note(m); t=tt(d); s=np.zeros_like(t)
    for h,a in ((1,1),(2,0.45),(3,0.25),(4,0.14),(5,0.08),(6,0.04)):
        s+=a*np.sin(2*np.pi*f*h*t*(1+0.0003*h*h))*np.exp(-t*(2.2+h*1.1))
    return (s*vel*np.minimum(1,t/0.004)).astype(np.float32)
def pluck(m,d=0.5,vel=0.4):
    f=note(m); t=tt(d); s=np.zeros_like(t)
    for h,a in ((1,1),(2,0.6),(3,0.5),(4,0.3),(5,0.2),(6,0.12)):
        s+=a*np.sin(2*np.pi*f*h*t)*np.exp(-t*(5+h*3))
    return (s*vel).astype(np.float32)
def pad(ms,d,vel=0.12,a=0.8,rel=0.8):
    t=tt(d); s=np.zeros_like(t)
    for m in ms:
        f=note(m)
        for det in (-0.07,0,0.07):
            ph=2*np.pi*f*(1+det*0.01)*t
            s+=(np.sin(ph)+0.5*np.sin(2*ph)+0.25*np.sin(3*ph))/3
    e=np.minimum(1,t/a)*np.clip((d-t)/rel,0,1)
    s=s/len(ms)*e*vel
    return lfilter([0.08],[1,-0.92],s).astype(np.float32)*6
def bass(m,d=0.55,vel=0.5):
    f=note(m); t=tt(d); s=(np.sin(2*np.pi*f*t)+0.35*np.sin(4*np.pi*f*t))*np.exp(-t*3.2)*np.minimum(1,t/0.006)
    return (s*vel).astype(np.float32)
def kick(vel=0.9):
    t=tt(0.32); f=45+110*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*np.exp(-t*11)*vel).astype(np.float32)
def clap(vel=0.5):
    out=np.zeros(int(0.25*SR),np.float32)
    for off,g in ((0,0.7),(0.012,0.8),(0.026,1.0)):
        n=int(0.12*SR); x=rng.randn(n); x=x-lfilter([0.5],[1,-0.5],x); x=x*np.exp(-np.arange(n)/SR*28)*g
        i=int(off*SR); out[i:i+n]+=x[:len(out)-i]*0.5
    return out*vel
def hat(vel=0.18,d=0.05):
    n=int(d*SR); x=rng.randn(n); x=np.diff(x,prepend=0); return (x*np.exp(-np.arange(n)/SR*90)*vel).astype(np.float32)
def noise_sweep(d,up=True,vel=0.4):
    t=tt(d); n=rng.randn(len(t)); k=(t/d) if up else (1-t/d)
    # lowpass sweep via varying blend of smoothed noise
    s1=lfilter([0.02],[1,-0.98],n)*8; s2=lfilter([0.3],[1,-0.7],n)*1.5; s3=np.diff(n,prepend=0)*0.5
    x=s1*(1-k)**2+s2*(k*(1-k)*4)+s3*(k**2)
    e=np.sin(np.pi*np.clip(k,0,1)**(0.7 if up else 1.4))
    return (x*e*vel).astype(np.float32)
def riser(d,vel=0.35):
    t=tt(d); k=t/d; n=rng.randn(len(t)); n=np.diff(n,prepend=0)
    return (n*k**2*vel*0.7+np.sin(2*np.pi*(300+1800*k**2)*t)*k**3*vel*0.4).astype(np.float32)
def pop(f=1800,d=0.12,vel=0.25):
    t=tt(d); return (np.sin(2*np.pi*(f+900*t/d)*t)*np.exp(-t*34)*vel).astype(np.float32)
def zap(vel=0.25):
    t=tt(0.18); return (np.sign(np.sin(2*np.pi*(900-3000*t)*t))*np.exp(-t*20)*vel*0.4+rng.randn(len(t))*np.exp(-t*40)*vel*0.3).astype(np.float32)
def crash(d=1.6,vel=0.28):
    n=int(d*SR); x=rng.randn(n); x=np.diff(x,prepend=0); return (x*np.exp(-np.arange(n)/SR*2.8)*vel).astype(np.float32)
def chord_midi(name):
    return {'C':[60,64,67],'G':[55,59,62],'Am':[57,60,64],'F':[53,57,60]}[name]
PROG=['C','G','Am','F']
def chord_at(beat): return PROG[int(beat//4)%4]
BEATS=int(TOTAL/BEAT)  # 180
# ---- שכבות לפי חלקים
for b in range(BEATS):
    t=b*BEAT; ch=chord_at(b); cm=chord_midi(ch); root={'C':36,'G':31,'Am':33,'F':29}[ch]
    # פעימות-על
    sec = 'A' if t<20.4 else 'B' if t<51.6 else 'T' if t<54 else 'C' if t<72 else 'D' if t<82.8 else 'E' if t<94.8 else 'L'
    # פסנתר: ארפג'ו שמיניות
    arp=[cm[0],cm[1],cm[2],cm[1]+12]
    if sec in('A','B','D','E','L') and not (sec=='L' and t>=104.4) or (sec=='C' and True):
        for h in range(2):
            m=arp[(b*2+h)%4]+ (12 if sec in('A','D','E','L') else 0)
            v=0.30 if sec in('A',) else 0.34 if sec in('B','L') else 0.28
            if sec=='E' and t>=90: v=0.22
            if sec=='C' and h==1 and (b%2): continue
            add(piano(m,1.0,v),t+h*BEAT/2,1.0,pan=0.25*(1 if h else -1),rev=0.35)
    # פד
    if b%4==0 and not (sec=='L' and t>=104.4):
        dd=4*BEAT+0.3
        v=0.10 if sec=='A' else 0.16 if sec in('B','C') else 0.13
        add(pad([m+12 if sec in('C','D') else m for m in cm],dd,v),t,1.0,rev=0.5)
    # גיטרה פריטה מקטע A (פעימה 8) עד סוף B
    if 8<=b<34 or 34<=b<86:
        if b%2==0 or sec=='B':
            add(pluck(cm[(b)%3]+12,0.4,0.22 if sec=='A' else 0.28),t+BEAT*0.5,1.0,pan=-0.3,rev=0.2)
    # תופים
    if sec=='A':
        if b>=16 and b%2==1: add(clap(0.25),t)
        if b>=20: add(hat(0.08),t+BEAT/2)
    if sec=='B':
        add(kick(0.95),t) if b%2==0 else add(kick(0.55),t+BEAT*0.5)
        if b%2==1: add(clap(0.55),t)
        add(hat(0.16),t+BEAT/2); add(hat(0.08),t)
        add(bass(root+12*0,BEAT*0.9,0.55),t,1.0)
        if b%4==3: add(bass(root+7,BEAT*0.4,0.4),t+BEAT*0.5)
    if sec=='T':   # האטה
        if b%2==0: add(kick(0.4),t)
    if sec=='C':
        if b%2==0: add(kick(0.45),t)
        add(bass(root,BEAT*1.8,0.4),t) if b%2==0 else None
    if sec=='D' and t>=76:
        add(kick(0.5),t) if b%2==0 else None
        add(clap(0.3),t) if b%2==1 else None
    if sec=='L' and t<104.4:
        add(kick(0.8),t); add(hat(0.14),t+BEAT/2)
        if b%2==1: add(clap(0.45),t)
        add(bass(root,BEAT*0.9,0.5),t)
    if sec=='E':
        add(bass(root,BEAT*3.5,0.35),t) if (b%4==0 and t<90) else None
# ---- אירועים בנקודות מפתח
add(riser(2.4,0.35),15.6); add(riser(3.6,0.0),0)   # ריזר לפני הדרופ
for k in range(8): add(hat(0.15),18.0+k*0.15)
add(crash(2.2,0.4),20.4); add(kick(1.0),20.4); add(bass(36,2.4,0.7),20.4)
add(noise_sweep(1.2,False,0.4),19.2)
# רגשי: קרשנדו 72–82.8
add(riser(10.8,0.20),72.0); add(crash(2.0,0.3),82.8)
# סיום: משפטים והפסקות
add(riser(4.8,0.30),90.0)
add(crash(3.0,0.55),94.8); add(kick(1.0),94.8); add(noise_sweep(1.5,True,0.5),93.6)
# אקורד אחרון
for m in (48,52,55,60,64,67,72): add(piano(m,3.8,0.35),104.4,rev=0.7)
add(pad([48,55,60,64,67],4.2,0.2,0.2,2.0),104.4,rev=0.6)
# SFX לפי מעברים וטקסט
import engine  # CFG, TEXTS
t=0
for s in SCENES:
    sid=s[0]; cfg=engine.CFG[sid]; ttype,td=cfg['tr']
    if t>0:
        if ttype in('whip','whipL'): add(noise_sweep(0.5,True,0.45),t-0.18,pan=0.3 if ttype=='whip' else -0.3)
        elif ttype=='zoom': add(noise_sweep(0.8,True,0.5),t-0.3); add(kick(0.5),t)
        elif ttype in('flash',): add(zap(0.35),t-0.05)
        elif ttype=='glitch': add(zap(0.5),t)
        elif ttype in('diag','diagO','push','blinds'): add(noise_sweep(0.45,True,0.35),t-0.15)
        elif ttype=='circle': add(pop(900,0.2,0.3),t+0.05); add(noise_sweep(0.6,True,0.3),t-0.2)
    if cfg['style'] in('card','circle','card_video') and t>0: add(pop(1200,0.15,0.22),t+0.12)
    t+=s[2]
for T in engine.TEXTS:
    if T['kind'] in('pill','big','counter'):
        add(pop(1500,0.12,0.30),T['t0']+0.05); add(pop(2200,0.1,0.18),T['t0']+0.25)
    if T['kind']=='counter':
        for k in range(8): add(pop(900+k*120,0.05,0.08),T['t0']+k*0.1)
# לוגו: הרכבת חלקים
for k,tl in enumerate([95.4,95.6,95.75,95.95,96.1,96.35,96.6,96.9,97.2,97.5]): add(pop(700+k*140,0.12,0.28),tl)
add(noise_sweep(0.6,True,0.4),98.0)   # פירוק
for k,tl in enumerate([100.7,101.0,101.3,101.6,101.9,102.2,102.6,102.9,103.2]): add(pop(600+k*160,0.14,0.28),tl)
add(noise_sweep(1.0,True,0.4),104.4)
for k in range(6): add(pop(1800+k*300,0.2,0.18),105.4+k*0.15)
# ---- דוכס: פסנתר חי מהסרטון S34 (61.2–64.8) בתוך הערבוב
vid=f"{SCR}/src/מוזיקה/WhatsApp_Video_2026-07-30_at_19.03.17.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-i",vid,"-t","3.6","-ac","1","-ar",str(SR),f"{SCR}/clip_piano.wav"])
import wave as _w
with _w.open(f"{SCR}/clip_piano.wav") as w:
    x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
duck_ranges=[(61.2,64.8,0.45)]
# ---- ריוורב
ir=(rng.randn(int(1.8*SR))*np.exp(-np.arange(int(1.8*SR))/SR*2.6)).astype(np.float32)
ir=lfilter([0.3],[1,-0.7],ir)*0.5
rv=fftconvolve(REV,ir)[:N].astype(np.float32)
L+=rv*0.5; R+=np.roll(rv,int(0.013*SR))*0.5
# ---- הפסקות מכוונות בין משפטי הסיום (שקט)
def gain_env(ranges,N=N):
    g=np.ones(N,np.float32)
    for a,b,v in ranges:
        i,j=int(a*SR),int(b*SR); fade=int(0.12*SR)
        g[i:j]=v
        g[i-fade:i]=np.linspace(1,v,fade) if i-fade>=0 else g[i-fade:i]
        g[j:j+fade]=np.linspace(v,1,fade)
    return g
g=gain_env([(85.3,86.5,0.12),(89.0,90.0,0.12)]+duck_ranges)
L*=g; R*=g
# מיקס הקליפ החי
i0=int(61.2*SR); xs=x[:int(3.6*SR)]*1.6; L[i0:i0+len(xs)]+=xs; R[i0:i0+len(xs)]+=xs
# פייד פתיחה/סגירה
fi=int(1.2*SR); L[:fi]*=np.linspace(0,1,fi); R[:fi]*=np.linspace(0,1,fi)
fo=int(1.8*SR); L[-fo:]*=np.linspace(1,0,fo); R[-fo:]*=np.linspace(1,0,fo)
# נרמול + סאטורציה רכה
m=np.stack([L,R],1); peak=np.abs(m).max(); m=np.tanh(m/peak*1.3)*0.85
pcm=(m*32767).astype(np.int16)
with wave.open(f"{SCR}/soundtrack.wav","wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio ok",peak)
