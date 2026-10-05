# -*- coding: utf-8 -*-
"""פסקול זמני אנרגטי (placeholder) מסונתז: 120 BPM, פופ-דאנס אופטימי בסול מז'ור, סיידצ'יין, דרופים. להחלפה במוזיקה מורשית."""
import numpy as np, wave, subprocess, os, sys
from scipy.signal import fftconvolve, lfilter
from scenes import S as SCENES, BEAT, start
SR=44100
import engine
TOTAL=engine.TOTAL; N=int(SR*TOTAL)
SCR=engine.SCR
rng=np.random.RandomState(11)
BUS={k:[np.zeros(N,np.float32),np.zeros(N,np.float32)] for k in ('m','d')}
REV=np.zeros(N,np.float32); kick_times=[]
def add(sig,t,gain=1.0,pan=0.0,rev=0.0,bus='d'):
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=N: return
    sig=sig[:N-i]; n=len(sig); L,R=BUS[bus]
    L[i:i+n]+=sig*gain*(1-max(0,pan)); R[i:i+n]+=sig*gain*(1+min(0,pan))
    if rev: REV[i:i+n]+=sig*rev
def tt(d): return np.arange(int(d*SR))/SR
def note(m): return 440*2**((m-69)/12)
def saw(f,t,det=0.0): return 2*((f*(1+det)*t)%1.0)-1
def lp(x,a): return lfilter([1-a],[1,-a],x)
def piano(m,d=1.0,vel=0.4):
    f=note(m); t=tt(d); s=np.zeros_like(t)
    for h,a in ((1,1),(2,0.45),(3,0.25),(4,0.14),(5,0.08)): s+=a*np.sin(2*np.pi*f*h*t)*np.exp(-t*(2.4+h*1.2))
    return (s*vel*np.minimum(1,t/0.004)).astype(np.float32)
def pluck_saw(m,d=0.35,vel=0.35,bright=0.9):
    f=note(m); t=tt(d); x=(saw(f,t,0.004)+saw(f,t,-0.004))*0.5; x=x*np.exp(-t*7)
    y=lp(x,bright*0.55)*0.6+x*0.4
    return (y*vel*np.minimum(1,t/0.003)).astype(np.float32)
def stab(ms,d=0.4,vel=0.22):
    t=tt(d); s=np.zeros_like(t)
    for m in ms:
        f=note(m)
        for det in (-0.012,0,0.012): s+=saw(f,t,det)
    s=s/(len(ms)*3)*np.exp(-t*5.5)*np.minimum(1,t/0.004)
    return (lp(s,0.45)*vel*3).astype(np.float32)
def pad(ms,d,vel=0.12,a=0.5,rel=0.5):
    t=tt(d); s=np.zeros_like(t)
    for m in ms:
        f=note(m)
        for det in (-0.006,0,0.006): s+=saw(f,t,det)
    e=np.minimum(1,t/a)*np.clip((d-t)/rel,0,1)
    return (lp(s/(len(ms)*3),0.9)*e*vel*4).astype(np.float32)
def bass(m,d=0.3,vel=0.55):
    f=note(m); t=tt(d); s=(np.sin(2*np.pi*f*t)+0.5*saw(f,t)*0.4+0.3*np.sin(4*np.pi*f*t))*np.minimum(1,t/0.004)*np.clip((d-t)/0.03,0,1)*np.exp(-t*2.2)
    return (lp(s,0.8)*vel).astype(np.float32)
def kick(vel=0.95):
    t=tt(0.34); f=48+150*np.exp(-t*32); ph=2*np.pi*np.cumsum(f)/SR
    return ((np.sin(ph)*np.exp(-t*10)+0.25*np.sin(ph*0.5)*np.exp(-t*6))*vel*1.1).astype(np.float32)
def clap(vel=0.55):
    out=np.zeros(int(0.3*SR),np.float32)
    for off,g in ((0,0.6),(0.011,0.8),(0.024,1.0)):
        n=int(0.16*SR); x=rng.randn(n); x=x-lp(x,0.55); x=x*np.exp(-np.arange(n)/SR*24)*g; i=int(off*SR); out[i:i+n]+=x[:len(out)-i]*0.5
    return out*vel*1.4
def snare(vel=0.5):
    t=tt(0.25); n=rng.randn(len(t)); x=(n-lp(n,0.5))*np.exp(-t*20)+np.sin(2*np.pi*190*t)*np.exp(-t*28)*0.6
    return (x*vel).astype(np.float32)
def hat(vel=0.18,d=0.05,op=False):
    d=0.22 if op else d; n=int(d*SR); x=np.diff(rng.randn(n),prepend=0); return (x*np.exp(-np.arange(n)/SR*(18 if op else 90))*vel).astype(np.float32)
def shaker(vel=0.1):
    n=int(0.06*SR); x=np.diff(rng.randn(n),prepend=0); return (x*np.exp(-np.arange(n)/SR*60)*vel).astype(np.float32)
def tom(f0,vel=0.5):
    t=tt(0.3); f=f0*(1+0.6*np.exp(-t*20)); ph=2*np.pi*np.cumsum(f)/SR; return (np.sin(ph)*np.exp(-t*9)*vel).astype(np.float32)
def noise_sweep(d,up=True,vel=0.4):
    t=tt(d); k=(t/d) if up else (1-t/d); n=rng.randn(len(t))
    x=lp(n,0.97)*8*(1-k)**2+lp(n,0.6)*1.5*(k*(1-k)*4)+np.diff(n,prepend=0)*0.5*k**2
    e=np.sin(np.pi*np.clip(k,0,1)**(0.7 if up else 1.4)); return (x*e*vel).astype(np.float32)
def riser(d,vel=0.35):
    t=tt(d); k=t/d; n=np.diff(rng.randn(len(t)),prepend=0)
    return (n*k**2*vel*0.7+np.sin(2*np.pi*(250+2200*k**2)*t)*k**3*vel*0.4).astype(np.float32)
def crash(d=1.8,vel=0.3):
    n=int(d*SR); x=np.diff(rng.randn(n),prepend=0); return (x*np.exp(-np.arange(n)/SR*2.4)*vel).astype(np.float32)
def boom(vel=0.8):
    t=tt(1.2); f=60*np.exp(-t*2.5)+28; ph=2*np.pi*np.cumsum(f)/SR; return (np.sin(ph)*np.exp(-t*3.0)*vel).astype(np.float32)
def pop(f=1800,d=0.12,vel=0.25):
    t=tt(d); return (np.sin(2*np.pi*(f+900*t/d)*t)*np.exp(-t*34)*vel).astype(np.float32)
def zap(vel=0.25):
    t=tt(0.18); return (np.sign(np.sin(2*np.pi*(900-3000*t)*t))*np.exp(-t*20)*vel*0.4+rng.randn(len(t))*np.exp(-t*40)*vel*0.3).astype(np.float32)
CH={'G':[55,59,62,67],'D':[50,54,57,62],'Em':[52,55,59,64],'C':[48,52,55,60]}
ROOT={'G':43,'D':38,'Em':40,'C':36}
PROG=['G','D','Em','C']
def ch_at(b): return PROG[int(b//4)%4]
# מבנה
T_DROP=start('M08'); T_GROW=start('M27'); T_BUILD=start('M34'); T_CLOSE=start('C01'); T_LOGO=start('L01'); T_SPLIT=T_LOGO+3.5; T_END=T_LOGO+7.0
HOOK=[[71,74,76,74,71,74,76,79],[76,74,71,69,67,69,71,74]]
BEATS=int(TOTAL/BEAT)
def section(t):
    if t<T_DROP: return 'intro'
    if t<T_GROW: return 'drop'
    if t<T_BUILD: return 'grow'
    if t<T_CLOSE: return 'build'
    if t<T_LOGO: return 'close'
    if t<T_END: return 'logo'
    return 'end'
for b in range(BEATS):
    t=b*BEAT; sec=section(t); ch=ch_at(b); cm=CH[ch]; root=ROOT[ch]; bi=b%4
    ph8=b*2
    # ארפג'ו פסנתר/פלאק
    if sec in('intro','grow','close'):
        for h in range(2):
            m=cm[((b*2+h)%4)]+12
            v={'intro':0.30,'grow':0.34,'close':0.26}[sec]
            if sec=='intro' and t<2: v*=t/2
            add(piano(m,1.0,v),t+h*BEAT/2,1.0,pan=0.3*(1 if h else -1),rev=0.35,bus='m')
    if sec=='intro' and t>=4:
        add(pluck_saw(cm[b%4]+24,0.25,0.22),t+BEAT/2,1.0,pan=-0.3,bus='m')
    # פדים
    if bi==0 and sec!='end':
        v={'intro':0.10,'drop':0.14,'grow':0.17,'build':0.18,'close':0.13,'logo':0.15}[sec]
        add(pad([m+(12 if sec in('grow','close') else 0) for m in cm],4*BEAT+0.4,v),t,1.0,rev=0.4,bus='m')
    # תופים
    if sec=='intro':
        if t>=4 and bi in(1,3): add(clap(0.45),t)
        if t>=2: add(shaker(0.09),t); add(shaker(0.07),t+BEAT/2)
        if t>=8: add(kick(0.7),t) if bi in(0,2) else None; kick_times.append(t) if (t>=8 and bi in(0,2)) else None
        if t>=12 and t<T_DROP-0.5: add(kick(0.8),t) if bi in(1,3) else None; kick_times.append(t) if (bi in(1,3)) else None
        if t>=8: add(hat(0.12),t+BEAT/2)
    if sec in('drop','logo'):
        add(kick(1.0),t); kick_times.append(t)
        if bi in(1,3): add(clap(0.9),t); add(snare(0.4),t)
        add(hat(0.17),t+BEAT/2); add(hat(0.07),t+BEAT/4); add(hat(0.07),t+3*BEAT/4)
        if bi in(0,2): add(hat(0.10,op=True),t+BEAT/2) if False else None
        add(hat(0.2,op=True),t+BEAT/2) if bi==3 else None
        # בס מתגלגל: 8ביות
        seq=[0,0,12,0,0,0,12,7]
        for h in range(2): add(bass(root+seq[(b*2+h)%8],BEAT*0.45,1.0 if h==0 else 0.85),t+h*BEAT/2,bus='m')
        # סטאבים אקורד על אוף-ביט
        if bi in(0,1,2,3): add(stab(cm,0.28,0.38 if sec=='drop' else 0.42),t+BEAT/2,1.0,pan=0.2*(1 if bi%2 else -1),bus='m')
        # מנגינה (hook)
        bar=(b//4)%2
        for h in range(4):
            idx=(bi*2+ (h//2))%8
        for h in range(8):
            pass
    if sec=='grow':
        add(kick(0.62),t); kick_times.append(t)
        if bi in(1,3): add(clap(0.32),t)
        add(hat(0.09),t+BEAT/2)
        add(bass(root,BEAT*1.8,0.4),t,bus='m') if bi in(0,2) else None
    if sec=='build':
        add(kick(0.85),t); kick_times.append(t)
        add(clap(0.4+0.25*(t-T_BUILD)/(T_CLOSE-T_BUILD)),t) if bi in(1,3) else None
    if sec=='close':
        pass
# hook לדרופ וללוגו
def hook(t0,t1,vel=0.30):
    t=t0; bar=0
    while t<t1-1e-6:
        for h in range(8):
            tn=t+h*BEAT/2
            if tn>=t1: break
            m=HOOK[bar%2][h]; add(pluck_saw(m,0.4,vel),tn,1.0,pan=0.25*(1 if h%2 else -1),rev=0.25,bus='m'); add(pluck_saw(m+12,0.3,vel*0.4),tn+0.18,1.0,pan=-0.2,bus='m')
        t+=4*BEAT; bar+=1
hook(T_DROP+4.0, T_GROW,0.5)  # מבר 3 של הדרופ
hook(T_LOGO,T_END,0.55)
# מעברי מקטעים
def snare_roll(t0,t1,v0=0.15,v1=0.55):
    n=int((t1-t0)/(BEAT/4)); 
    for k in range(n):
        x=k/max(1,n-1); add(snare(v0+(v1-v0)*x),t0+k*(BEAT/4)*(1 if k<n*0.5 else 1))
snare_roll(T_DROP-4.0,T_DROP-0.5,0.12,0.6)
add(riser(3.5,0.35),T_DROP-4.0); add(noise_sweep(1.0,True,0.5),T_DROP-1.5)
for k in range(4): add(tom(150-k*20,0.45),T_DROP-1.5+k*0.25*BEAT*2)
add(boom(0.9),T_DROP); add(crash(2.4,0.42),T_DROP); add(kick(1.0),T_DROP)
add(crash(2.0,0.3),T_GROW); add(noise_sweep(0.9,False,0.35),T_GROW-0.9)
snare_roll(T_BUILD,T_CLOSE,0.12,0.5); add(riser(T_CLOSE-T_BUILD,0.35),T_BUILD)
add(crash(2.0,0.3),T_CLOSE)
add(riser(3.0,0.3),T_LOGO-3.0)
add(boom(1.0),T_LOGO); add(crash(2.6,0.5),T_LOGO); add(noise_sweep(1.2,True,0.45),T_LOGO-1.2)
add(boom(0.8),T_SPLIT); add(crash(2.0,0.35),T_SPLIT); add(zap(0.4),T_SPLIT)
# אקורד סיום
for m in (43,55,59,62,67,71,74): add(piano(m,3.5,0.30),T_END,rev=0.7,bus='m')
add(pad([55,59,62,67,71],3.6,0.25,0.15,1.8),T_END,rev=0.6,bus='m'); add(crash(3.0,0.5),T_END); add(boom(0.9),T_END)
# SFX מעברים וטקסט
t=0
for s in SCENES:
    sid=s[0]; cfg=engine.CFG[sid]; ttype,td=cfg['tr']
    if t>0:
        if ttype in('whip','whipL'): add(noise_sweep(0.45,True,0.45),t-0.15,pan=0.3 if ttype=='whip' else -0.3)
        elif ttype=='zoom': add(noise_sweep(0.7,True,0.45),t-0.25); add(tom(110,0.5),t)
        elif ttype=='flash': add(zap(0.35),t-0.05)
        elif ttype=='glitch': add(zap(0.5),t)
        elif ttype in('diag','diagO','push','blinds'): add(noise_sweep(0.4,True,0.35),t-0.12)
        elif ttype=='circle': add(pop(900,0.2,0.3),t+0.05); add(noise_sweep(0.5,True,0.3),t-0.15)
    if cfg['style'] in('card','circle','card_video') and t>0: add(pop(1200,0.15,0.22),t+0.1)
    t+=s[2]
for T in engine.TEXTS:
    if T['kind'] in('pill','big','counter'):
        add(pop(1500,0.12,0.30),T['t0']+0.05); add(pop(2200,0.1,0.18),T['t0']+0.25)
    if T['kind']=='counter':
        for k in range(8): add(pop(900+k*120,0.05,0.08),T['t0']+k*0.1)
    if T['kind']=='end': add(pop(1100,0.2,0.2),T['t0']+0.2)
# לוגו SFX
for k,tl in enumerate([0.0,0.2,0.4,0.9,1.2,1.5,1.9]): add(pop(700+k*150,0.12,0.28),T_LOGO+tl)
for k in range(8): add(pop(1400+k*200,0.15,0.18),T_LOGO+4.8+k*0.15)
# פסנתר חי מהסרטון
vid=f"{SCR}/src/מוזיקה/WhatsApp_Video_2026-07-30_at_19.03.17.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-i",vid,"-t","3.0","-ac","1","-ar",str(SR),f"{SCR}/clip_piano.wav"])
with wave.open(f"{SCR}/clip_piano.wav") as w: xclip=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
# סיידצ'יין
duck=np.ones(N,np.float32)
for kt in kick_times:
    i=int(kt*SR); n=int(0.3*SR); seg=1-0.68*np.exp(-np.arange(min(n,N-i))/SR/0.085); 
    if i<N: duck[i:i+len(seg)]=np.minimum(duck[i:i+len(seg)],seg)
Lm,Rm=BUS['m']; Ld,Rd=BUS['d']
ir=lp((rng.randn(int(1.6*SR))*np.exp(-np.arange(int(1.6*SR))/SR*2.8)).astype(np.float32),0.6)*0.5
rv=fftconvolve(REV,ir)[:N].astype(np.float32)
L=Lm*duck+Ld+rv*0.45; R=Rm*duck+Rd+np.roll(rv,int(0.013*SR))*0.45
# הפסקות מכוונות בין משפטי הסיום
def gain_env(ranges):
    g=np.ones(N,np.float32)
    for a,b,v in ranges:
        i,j=int(a*SR),int(b*SR); fade=int(0.08*SR); g[i:j]=np.minimum(g[i:j],v); 
        g[max(0,i-fade):i]=np.minimum(g[max(0,i-fade):i],np.linspace(1,v,len(g[max(0,i-fade):i]))); g[j:j+fade]=np.minimum(g[j:j+fade],np.linspace(v,1,len(g[j:j+fade])))
    return g
ends=[(T['t0']+2.65,T['t1']+0.35,0.25) for T in engine.TEXTS if T['kind']=='end']
g=gain_env(ends+[(start('M28'),start('M28')+3.0,0.5)])
# הרמה בסוף כל משפט (הפסקה אמיתית): נשארת שקט קצר
L*=g; R*=g
i0=int(start('M28')*SR); xs=xclip*1.8; n=min(len(xs),N-i0); L[i0:i0+n]+=xs[:n]; R[i0:i0+n]+=xs[:n]
fi=int(0.4*SR); L[:fi]*=np.linspace(0,1,fi); R[:fi]*=np.linspace(0,1,fi)
fo=int(1.6*SR); L[-fo:]*=np.linspace(1,0,fo); R[-fo:]*=np.linspace(1,0,fo)
m=np.stack([L,R],1); peak=float(np.percentile(np.abs(m),99.6)); m=np.tanh(m/peak*0.95)*0.92
pcm=(m*32767).astype(np.int16)
with wave.open(f"{SCR}/soundtrack.wav","wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio ok",peak,TOTAL)
