# -*- coding: utf-8 -*-
"""מייצר מסלול קול לדקה הראשונה: הקריינות המקורית (מוסטת 3 שניות לפתיח) + אפקטי נייר עדינים (מסונתזים, חינם). בלי מוזיקה."""
import numpy as np, wave, subprocess, sys
SR=44100; DUR=64.4
rng=np.random.default_rng(7)
def lp(x,a): 
    y=np.zeros_like(x); s=0.0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
def env(n,att,dec): 
    t=np.arange(n)/SR; e=np.minimum(t/att,1)*np.exp(-t/dec); return e/e.max()
def tear(d=.55):
    n=int(SR*d); x=rng.standard_normal(n); x=x-lp(x,.06)           # הדגשת גבהים
    cr=(rng.random(n)<.0025)*rng.standard_normal(n)*3              # קליקים של סיבי נייר
    return (x*.5+cr)*env(n,.02,.18)*np.hanning(n)**.3
def whoosh(d=.4):
    n=int(SR*d); x=rng.standard_normal(n); x=lp(x,.12); t=np.arange(n)/n
    return x*np.sin(np.pi*t)**2*1.6
def thump(d=.25):
    n=int(SR*d); t=np.arange(n)/SR; return np.sin(2*np.pi*(90-60*t/d*.5)*t)*np.exp(-t/.07)*1.1
def glitch(d=.2):
    n=int(SR*d); x=rng.standard_normal(n)*(rng.random(n)<.18); return lp(x,.5)*3*np.exp(-np.arange(n)/SR/.1)
out=np.zeros(int(SR*DUR))
def put(x,t,g):
    i=int(t*SR); out[i:i+len(x)]+=x[:max(0,len(out)-i)]*g if i<len(out) else 0
for t in (2.8,24.6,34.7): put(tear(),t,.30)
for t in (7.1,13.6,37.8,58.2): put(whoosh(),t,.22)
put(thump(),24.85,.45); put(glitch(),30.0,.22)
out=np.clip(out,-1,1); pcm=(out*32767).astype('<i2')
w=wave.open('/tmp/sfx.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
NARR=sys.argv[1]
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',NARR,'-i','/tmp/sfx.wav','-filter_complex',
 f'[0:a]atrim=0:61.5,asetpts=PTS-STARTPTS,adelay=3000|3000,aresample={SR},loudnorm=I=-16:TP=-1.5:LRA=11[n];[1:a]volume=0.55[s];[n][s]amix=inputs=2:duration=longest:normalize=0,atrim=0:{DUR}[o]',
 '-map','[o]','-ac','2','-c:a','pcm_s16le','/tmp/audio_min1.wav'],check=True)
print('audio ok')
