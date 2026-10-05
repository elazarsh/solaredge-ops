# -*- coding: utf-8 -*-
"""פסקול זמני (placeholder) v3 – פופ-דאנס 120 BPM בסול מז'ור. סינתזה band-limited, תופים משופרים, ריוורב, דיליי, סיידצ'יין, הומניזציה.
בחלק הספורט (M08–M12) קצב מוגבר: קאוביל, קונגות, 16ביות, מחיאות סינקופה, פילים ושריקת שופט."""
import numpy as np, wave, subprocess, os, sys, math
from scipy.signal import butter, sosfilt, fftconvolve
from scenes import S as SCENES, BEAT, start
import engine, logo_anim
SR=44100; TOTAL=engine.TOTAL; N=int(SR*TOTAL); SCR=engine.SCR
rng=np.random.RandomState(21)
def bq(x,kind,fc,order=2):
    sos=butter(order,min(fc,SR/2-100)/(SR/2),btype=kind,output='sos'); return sosfilt(sos,x).astype(np.float32)
def band(x,lo,hi): return bq(bq(x,'high',lo),'low',hi)
BUSN=('d','b','m','x')
BUS={k:[np.zeros(N,np.float32),np.zeros(N,np.float32)] for k in BUSN}
SEND={'plate':np.zeros(N,np.float32)}
kick_times=[]
def add(sig,t,gain=1.0,pan=0.0,rev=0.0,bus='d',human=0.0):
    t=t+rng.uniform(-human,human) if human else t
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=N: return
    sig=sig[:N-i]; n=len(sig); L,R=BUS[bus]
    L[i:i+n]+=sig*gain*(1-max(0,pan)); R[i:i+n]+=sig*gain*(1+min(0,pan))
    if rev: SEND['plate'][i:i+n]+=sig*rev
def tt(d): return np.arange(int(d*SR))/SR
def note(m): return 440*2**((m-69)/12)
def bl_saw(f,t,phase=0.0,maxf=9000,K=None):
    K=K or int(max(2,min(maxf/f,48))); w=2*np.pi*f*t+phase; out=np.zeros_like(t)
    for k in range(1,K+1): out+=np.sin(k*w)/k
    return out*0.6
# ---------- כלים
def piano(m,d=1.1,vel=0.4):
    f=note(m); t=tt(d); s=np.zeros_like(t); B=0.0004
    for k in range(1,11):
        fk=k*f*math.sqrt(1+B*k*k)
        if fk>9000: break
        s+=(1/k**1.15)*np.sin(2*np.pi*fk*t+rng.uniform(0,6.28))*np.exp(-t*(1.6+0.55*k)*(1+0.3*(m<55)))
    nz=band(rng.randn(len(t)),1500,5000)*np.exp(-t*90)*0.08
    s=(s+nz)*np.minimum(1,t/0.003)*np.clip((d-t)/0.05,0,1)
    return (s*vel).astype(np.float32)
def pluck(m,d=0.35,vel=0.35,cut=3500):
    f=note(m); t=tt(d); s=(bl_saw(f,t,rng.uniform(0,6),maxf=7000)+bl_saw(f*1.004,t,rng.uniform(0,6),maxf=7000))*0.5
    s=bq(s,'low',cut)*np.exp(-t*8)*np.minimum(1,t/0.003)
    return (s*vel).astype(np.float32)
def supersaw(ms,d,vel,a=0.004,rel=0.04,dec=0.0,K=None,cut=6000,voices=(-11,-5,0,5,11)):
    t=tt(d); s=np.zeros_like(t)
    for m in ms:
        f=note(m)
        for c in voices: s+=bl_saw(f*2**(c/1200),t,rng.uniform(0,6.28),maxf=cut,K=K)
    s=s/(len(ms)*len(voices))*np.minimum(1,t/a)*np.clip((d-t)/rel,0,1)*np.exp(-t*dec)
    return (bq(s,'low',cut)*vel*3.2).astype(np.float32)
def pad(ms,d,vel,bright=1.0,a=0.6,rel=0.6):
    K=3+int(7*bright); cut=900+5500*bright
    return supersaw(ms,d,vel,a=a,rel=rel,K=K,cut=cut,voices=(-8,0,8))
def bass(m,d=0.28,vel=0.7):
    f=note(m); t=tt(d); s=np.sin(2*np.pi*f*t)+0.45*bl_saw(f,t,maxf=1500)*0.8+0.2*np.sin(4*np.pi*f*t)
    s=np.tanh(1.3*s)*np.minimum(1,t/0.004)*np.clip((d-t)/0.03,0,1)*np.exp(-t*2.0)
    return (bq(s,'low',900)*vel).astype(np.float32)
def kick(vel=1.0):
    t=tt(0.36); f=46+130*np.exp(-t*34); ph=2*np.pi*np.cumsum(f)/SR
    body=np.sin(ph)*np.exp(-t*8.5); click=band(rng.randn(len(t)),1500,7000)*np.exp(-t*600)*0.35
    sub=np.sin(2*np.pi*46*t)*np.exp(-t*5)*0.4
    x=np.tanh(1.9*(body+sub))/1.25+click
    return (x*vel).astype(np.float32)
def snare(vel=0.5):
    t=tt(0.28); tone=np.sin(2*np.pi*190*t)*np.exp(-t*34)*0.55+np.sin(2*np.pi*330*t)*np.exp(-t*46)*0.3
    nz=band(rng.randn(len(t)),1400,9500)*np.exp(-t*17)
    return ((tone+nz*0.9)*vel).astype(np.float32)
def clap(vel=0.6):
    out=np.zeros(int(0.35*SR),np.float32)
    for off,g in ((0,0.55),(0.010,0.75),(0.021,0.9),(0.034,1.0)):
        n=int(0.2*SR); x=band(rng.randn(n),900,4200)*np.exp(-np.arange(n)/SR*26)*g; i=int(off*SR); out[i:i+n]+=x[:len(out)-i]*0.5
    return out*vel*1.7
def hat(vel=0.15,op=False):
    d=0.28 if op else 0.06; t=tt(d); nz=bq(rng.randn(len(t)),'high',7000)
    met=sum(np.sign(np.sin(2*np.pi*fr*t)) for fr in (2160,3050,4300,5800,7300))*0.12
    return ((bq(nz+met,'high',6500))*np.exp(-t*(14 if op else 85))*vel).astype(np.float32)
def shaker(vel=0.1):
    t=tt(0.07); return (band(rng.randn(len(t)),4500,11000)*np.exp(-t*55)*vel).astype(np.float32)
def cowbell(vel=0.3):
    t=tt(0.28); x=(np.sign(np.sin(2*np.pi*562*t))+np.sign(np.sin(2*np.pi*845*t)))*0.5; x=band(x,450,3600)*np.exp(-t*14)
    return (x*vel).astype(np.float32)
def conga(f0,vel=0.4):
    t=tt(0.25); f=f0*(1+0.35*np.exp(-t*30)); ph=2*np.pi*np.cumsum(f)/SR; x=np.sin(ph)*np.exp(-t*16)+band(rng.randn(len(t)),600,2500)*np.exp(-t*90)*0.3
    return (x*vel).astype(np.float32)
def tom(f0,vel=0.5):
    t=tt(0.35); f=f0*(1+0.7*np.exp(-t*18)); ph=2*np.pi*np.cumsum(f)/SR; x=np.sin(ph)*np.exp(-t*8)+band(rng.randn(len(t)),300,2000)*np.exp(-t*70)*0.15
    return (x*vel).astype(np.float32)
def whistle(vel=0.35):
    out=np.zeros(int(0.9*SR),np.float32)
    for off,d in ((0.0,0.16),(0.24,0.42)):
        t=tt(d); f=3050+80*np.sin(2*np.pi*38*t); ph=2*np.pi*np.cumsum(f)/SR
        x=np.sin(ph)*(1+0.3*np.sin(2*np.pi*55*t))+0.25*np.sin(2*ph); x=x*np.minimum(1,t/0.01)*np.clip((d-t)/0.04,0,1)+band(rng.randn(len(t)),2500,6000)*0.08
        i=int(off*SR); out[i:i+len(x)]+=(x*vel*0.6).astype(np.float32)[:len(out)-i]
    return out
def crash(d=2.0,vel=0.3):
    t=tt(d); x=bq(rng.randn(len(t)),'high',3500)*np.exp(-t*2.3)*np.minimum(1,t/0.004)
    return (x*vel).astype(np.float32)
def revcrash(d=2.0,vel=0.3):
    return crash(d,vel)[::-1].copy()
def boom(vel=0.9):
    t=tt(1.3); f=26+40*np.exp(-t*3); ph=2*np.pi*np.cumsum(f)/SR; return (np.sin(ph)*np.exp(-t*2.6)*vel).astype(np.float32)
def riser(d,vel=0.3):
    t=tt(d); k=t/d; f=300*(2**(3.3*k)); ph=2*np.pi*np.cumsum(f)/SR
    saw=sum(np.sin((j)*ph)/j for j in range(1,5))*0.4
    nz=bq(rng.randn(len(t)),'high',2500)*k**2
    return ((saw*k**2.2*0.5+nz*0.7)*vel*np.minimum(1,(d-t)/0.02)).astype(np.float32)
def sweep(d,up=True,vel=0.4):
    t=tt(d); k=t/d; nz=bq(rng.randn(len(t)),'high',1800)*(np.sin(np.pi*k)**(1.0 if up else 1.0))*(k if up else 1-k)
    return (nz*vel).astype(np.float32)
def pop(f=1800,d=0.12,vel=0.25):
    t=tt(d); return (np.sin(2*np.pi*(f+900*t/d)*t)*np.exp(-t*34)*vel).astype(np.float32)
def zap(vel=0.25):
    t=tt(0.18); return (np.sign(np.sin(2*np.pi*(900-3000*t)*t))*np.exp(-t*20)*vel*0.3+band(rng.randn(len(t)),1000,8000)*np.exp(-t*40)*vel*0.3).astype(np.float32)
# ---------- הרמוניה
CH={'G':[55,59,62,67],'D':[50,54,57,62],'Em':[52,55,59,64],'C':[48,52,55,60]}
ROOT={'G':43,'D':38,'Em':40,'C':36}; PROG=['G','D','Em','C']
def ch_at(b): return PROG[int(b//4)%4]
HOOK=[[71,74,76,74,71,74,76,79],[76,74,71,69,67,69,71,74],[79,76,74,76,79,81,79,76],[74,71,69,71,74,76,74,71]]
# ---------- מבנה
T={k:start(k) for k in ('M08','M13','M26','M27','M34','C01','C03','L01')}
T_DROP=T['M08']; T_SPORT_END=T['M13']; T_BREAK=T['M26']; T_GROW=T['M27']; T_BUILD=T['M34']; T_CLOSE=T['C01']; T_LOGO=T['L01']; T_SPLIT=T_LOGO+3.5; T_END=T_LOGO+9.0
def section(t):
    if t<T_DROP: return 'intro'
    if t<T_BREAK: return 'drop'
    if t<T_GROW: return 'break'
    if t<T_BUILD: return 'grow'
    if t<T_CLOSE: return 'build'
    if t<T_LOGO: return 'close'
    if t<T_END: return 'logo'
    return 'end'
BEATS=int(TOTAL/BEAT)
def delay_add(sig,t,vel,bus='m',pan=0.3):
    for k,(dt,g) in enumerate(((0.375,0.40),(0.75,0.22),(1.125,0.11))): add(sig,t+dt,vel*g,pan=pan*(1 if k%2==0 else -1),bus=bus)
for b in range(BEATS):
    t=b*BEAT; sec=section(t); ch=ch_at(b); cm=CH[ch]; root=ROOT[ch]; bi=b%4; bar=b//4
    sport=(T_DROP<=t<T_SPORT_END)
    # --- פסנתר / ארפג'ו
    if sec in('intro','grow','close','break'):
        for h in range(2):
            m=cm[((b*2+h)%4)]+12
            v={'intro':0.34,'grow':0.38,'close':0.30,'break':0.30}[sec]
            if sec=='intro': v*=min(1,t/1.5)
            add(piano(m,1.1,v),t+h*BEAT/2,1.0,pan=0.28*(1 if h else -1),rev=0.30,bus='m',human=0.004)
    if sec=='intro' and t>=4: add(pluck(cm[(b)%4]+24,0.3,0.20),t+BEAT/2,1.0,pan=-0.3,bus='m',rev=0.15)
    if sec=='grow' and t>=T_GROW+8:
        for h in range(4): add(pluck(cm[(b*4+h)%4]+24,0.18,0.14,cut=5000),t+h*BEAT/4,1.0,pan=0.3*(1 if h%2 else -1),bus='m')
    # --- פד
    if bi==0 and sec not in('end',):
        v={'intro':0.11,'drop':0.12,'break':0.15,'grow':0.16,'build':0.17,'close':0.13,'logo':0.14}[sec]
        br=min(1,t/14) if sec=='intro' else 1.0
        add(pad([m+(12 if sec in('grow','close','break') else 0) for m in cm],4*BEAT+0.5,v,bright=br),t,1.0,rev=0.35,bus='m')
    # --- תופים וקצב
    if sec=='intro':
        if t>=2: add(shaker(0.08*(0.6+0.4*(b%2))),t+BEAT/2,human=0.004); add(shaker(0.05),t,human=0.004)
        if t>=4 and bi in(1,3): add(clap(0.45),t,rev=0.2)
        if t>=8:
            if bi in(0,2) or t>=12: add(kick(0.8),t); kick_times.append(t)
            add(hat(0.12),t+BEAT/2,human=0.003)
        if t>=8: add(bass(root,BEAT*1.8,0.55),t,bus='b') if bi in(0,2) else None
    if sec in('drop','logo'):
        add(kick(1.0),t); kick_times.append(t)
        if bi in(1,3): add(clap(0.85),t,rev=0.25); add(snare(0.38),t)
        for h,vh in enumerate((0.16,0.05,0.10,0.05)): add(hat(vh*(1.0 if not sport else 1.15)),t+h*BEAT/4,human=0.003,pan=0.2)
        if bi==3: add(hat(0.22,op=True),t+BEAT/2)
        seq=[0,0,12,0,0,12,0,7]
        for h in range(2): add(bass(root+seq[(b*2+h)%8],BEAT*0.45,0.95 if h==0 else 0.8),t+h*BEAT/2,bus='b')
        add(supersaw(cm,0.28,0.30 if sec=='drop' else 0.34,dec=6,cut=7000),t+BEAT/2,1.0,pan=0.22*(1 if bi%2 else -1),bus='m',rev=0.12)
        if sec=='logo' and t>=T_LOGO+1.0: add(pluck(cm[(b)%4]+24,0.25,0.18),t+BEAT*0.75,1.0,pan=0.3,bus='m')
        # תוספות קצב לחלק הספורט
        if sport:
            add(cowbell(0.28),t+BEAT/2) if bi in(1,3) else None
            for off,fq,vv in ((0.75,300,0.28),(1.5,230,0.26),(2.75,300,0.28),(3.5,230,0.26)):
                if abs((bi+0)-int(off))<1e-9 or int(off)==bi: add(conga(fq,vv),t+(off-int(off))*BEAT+0.0)
            add(clap(0.38),t+BEAT/2,rev=0.2) if bi in(0,2) else None
            add(snare(0.14),t+BEAT*0.75) if bi in(1,3) else None
            if bi==3 and bar%2==1:
                for k,(fq,vv) in enumerate(((190,0.5),(160,0.5),(130,0.55),(105,0.6))): add(tom(fq,vv),t+k*BEAT/4)
    if sec=='break':
        add(kick(0.55),t); kick_times.append(t)
        add(bass(root,BEAT*1.8,0.45),t,bus='b') if bi in(0,2) else None
    if sec=='grow':
        add(kick(0.66),t); kick_times.append(t)
        if bi in(1,3): add(clap(0.34),t,rev=0.3)
        add(hat(0.08),t+BEAT/2,human=0.003)
        add(bass(root,BEAT*1.85,0.5),t,bus='b') if bi in(0,2) else None
    if sec=='build':
        f_=(t-T_BUILD)/(T_CLOSE-T_BUILD); add(kick(0.7+0.3*f_),t); kick_times.append(t)
        if bi in(1,3): add(clap(0.4+0.3*f_),t)
        add(bass(root,BEAT*0.9,0.5+0.3*f_),t,bus='b')
# ---------- הוק (מלודיה) + דיליי
def hook(t0,t1,vel,rev=0.25):
    t=t0; k=0
    while t<t1-1e-6:
        for h in range(8):
            tn=t+h*BEAT/2
            if tn>=t1: break
            m=HOOK[k%4][h]; sig=pluck(m,0.42,vel,cut=4800); o=0.35*pluck(m+12,0.3,vel,cut=6500); sig[:len(o)]+=o
            add(sig,tn,1.0,pan=0.22*(1 if h%2 else -1),rev=rev,bus='m')
            if h in (0,3,6): delay_add(sig,tn,0.8)
        t+=4*BEAT; k+=1
hook(T_DROP+4.0,T_BREAK,0.5)
hook(T_LOGO,T_END,0.55)
# ---------- מעברים
def snare_roll(t0,t1,v0,v1):
    n=int(round((t1-t0)/(BEAT/4)))
    for k in range(n): x=k/max(1,n-1); add(snare(v0+(v1-v0)*x),t0+k*(BEAT/4))
snare_roll(T_DROP-3.0,T_DROP-0.5,0.12,0.6)
add(riser(3.5,0.38),T_DROP-3.5); add(revcrash(2.0,0.35),T_DROP-2.0)
for k,fq in enumerate((190,165,140,115)): add(tom(fq,0.5),T_DROP-1.0+k*BEAT/2)
add(boom(0.95),T_DROP); add(crash(2.6,0.45),T_DROP); add(kick(1.0),T_DROP); add(whistle(0.45),T_DROP+0.02)
add(crash(2.2,0.32),T_GROW); add(revcrash(1.2,0.3),T_GROW-1.2)
snare_roll(T_BUILD,T_CLOSE,0.12,0.5); add(riser(T_CLOSE-T_BUILD,0.36),T_BUILD); add(revcrash(1.5,0.3),T_CLOSE-1.5)
add(crash(2.0,0.3),T_CLOSE)
add(riser(2.8,0.32),T_LOGO-2.8); add(revcrash(1.6,0.3),T_LOGO-1.6)
add(boom(1.0),T_LOGO); add(crash(2.8,0.5),T_LOGO)
add(boom(0.8),T_SPLIT); add(crash(2.2,0.38),T_SPLIT); add(zap(0.4),T_SPLIT); add(sweep(0.8,True,0.5),T_SPLIT-0.8)
# סיום
for m in (43,55,59,62,67,71,74): add(piano(m,3.5,0.32),T_END,rev=0.7,bus='m')
add(pad([55,59,62,67,71],3.8,0.26,bright=0.9,a=0.15,rel=2.0),T_END,rev=0.6,bus='m'); add(crash(3.0,0.5),T_END); add(boom(0.9),T_END)
# SFX
t=0
for s in SCENES:
    sid=s[0]; cfg=engine.CFG[sid]; ttype,td=cfg['tr']
    if t>0:
        if ttype in('whip','whipL'): add(sweep(0.45,True,0.5),t-0.15,pan=0.3 if ttype=='whip' else -0.3)
        elif ttype=='zoom': add(sweep(0.7,True,0.5),t-0.25); add(tom(110,0.5),t)
        elif ttype=='flash': add(zap(0.35),t-0.05)
        elif ttype=='glitch': add(zap(0.5),t)
        elif ttype in('diag','diagO','push','blinds'): add(sweep(0.4,True,0.4),t-0.12)
        elif ttype=='circle': add(pop(900,0.2,0.3),t+0.05); add(sweep(0.5,True,0.35),t-0.15)
    if cfg['style'] in('card','circle','card_video') and t>0: add(pop(1200,0.15,0.22),t+0.1)
    t+=s[2]
for Tt in engine.TEXTS:
    if Tt['kind'] in('pill','big','counter'): add(pop(1500,0.12,0.30),Tt['t0']+0.05); add(pop(2200,0.1,0.18),Tt['t0']+0.25)
    if Tt['kind']=='counter':
        for k in range(8): add(pop(900+k*120,0.05,0.08),Tt['t0']+k*0.1)
    if Tt['kind']=='end': add(pop(1100,0.2,0.2),Tt['t0']+0.2)
for k,tl in enumerate([0.0,0.2,0.4,0.9,1.2,1.5,1.9]): add(pop(700+k*150,0.12,0.28),T_LOGO+tl)
# משחק הכדור: פופים בתפיסות + קפיצות
for tc in (5.8,6.8,7.9,9.0): add(pop(700,0.14,0.35),T_LOGO+tc); add(tom(200,0.35),T_LOGO+tc)
for (t0,t1,a,b_,h) in logo_anim.BALL: add(pop(1300,0.1,0.18),T_LOGO+t0)
# פסנתר חי מהסרטון
vid=f"{SCR}/src/מוזיקה/WhatsApp_Video_2026-07-30_at_19.03.17.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-i",vid,"-t","3.0","-ac","1","-ar",str(SR),f"{SCR}/clip_piano.wav"])
with wave.open(f"{SCR}/clip_piano.wav") as w: xclip=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
# ---------- מיקס
duck=np.ones(N,np.float32)
for kt in kick_times:
    i=int(kt*SR); n=min(int(0.32*SR),N-i)
    if n>0: seg=1-0.66*np.exp(-np.arange(n)/SR/0.085); duck[i:i+n]=np.minimum(duck[i:i+n],seg)
# ריוורב פלייט סטריאו
rl=int(2.0*SR); tr=np.arange(rl)/SR
def mkir(): return bq(rng.randn(rl)*np.exp(-tr*2.6),'low',7000)*0.6
irL,irR=mkir(),mkir(); pre=int(0.018*SR); irL=np.concatenate([np.zeros(pre,np.float32),irL]); irR=np.concatenate([np.zeros(pre+int(0.004*SR),np.float32),irR])
irL=irL/np.sqrt((irL**2).sum()); irR=irR/np.sqrt((irR**2).sum())
rvL=fftconvolve(bq(SEND['plate'],'high',250),irL)[:N].astype(np.float32); rvR=fftconvolve(bq(SEND['plate'],'high',250),irR)[:N].astype(np.float32)
d_,b_,m_,x_=[BUS[k] for k in BUSN]
mL=bq(m_[0],'high',110)*duck; mR=bq(m_[1],'high',110)*duck
bL=bq(b_[0],'low',4000)*(0.55+0.45*duck); bR=bq(b_[1],'low',4000)*(0.55+0.45*duck)
L=d_[0]*0.9+bL*0.8+mL*1.1+rvL*0.9; R=d_[1]*0.9+bR*0.8+mR*1.1+rvR*0.9
# הפסקות מכוונות בין משפטי הסיום ושקט קצר לפני הדרופ
def gain_env(ranges):
    g=np.ones(N,np.float32)
    for a,b,v in ranges:
        i,j=int(a*SR),int(b*SR); fade=int(0.06*SR); g[i:j]=np.minimum(g[i:j],v)
        g[max(0,i-fade):i]=np.minimum(g[max(0,i-fade):i],np.linspace(1,v,len(g[max(0,i-fade):i]))); g[j:j+fade]=np.minimum(g[j:j+fade],np.linspace(v,1,len(g[j:j+fade])))
    return g
ends=[(Tt['t0']+2.65,Tt['t1']+0.35,0.25) for Tt in engine.TEXTS if Tt['kind']=='end']
g=gain_env(ends+[(T_DROP-0.5,T_DROP-0.01,0.0),(start('M28'),start('M28')+3.0,0.55)])
L*=g; R*=g
i0=int(start('M28')*SR); xs=xclip*1.8; n=min(len(xs),N-i0); L[i0:i0+n]+=xs[:n]; R[i0:i0+n]+=xs[:n]
fi=int(0.4*SR); L[:fi]*=np.linspace(0,1,fi); R[:fi]*=np.linspace(0,1,fi)
fo=int(1.2*SR); L[-fo:]*=np.linspace(1,0,fo); R[-fo:]*=np.linspace(1,0,fo)
m=np.stack([L,R],1); peak=float(np.percentile(np.abs(m),99.7)); m=np.tanh(m/peak*0.9)*0.9
with wave.open(f"{SCR}/soundtrack.wav","wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m*32767).astype(np.int16).tobytes())
def r(x,a,b): return round(float(np.sqrt((x[int(a*SR):int(b*SR)]**2).mean())),3)
for nm,bb in zip(('d','b','m','x'),(d_,b_,m_,x_)): print(nm,'intro',r(bb[0],4,8),'drop',r(bb[0],24,32),'grow',r(bb[0],44,52),'logo',r(bb[0],72,76))
print('mduck drop',r(mL,24,32),'intro',r(mL,4,8),'plate',r(rvL,24,32),r(rvL,4,8))
print("audio ok",peak,TOTAL)
