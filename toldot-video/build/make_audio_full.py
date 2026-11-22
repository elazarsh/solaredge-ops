# -*- coding: utf-8 -*-
"""קול לסרט המלא: הקריינות המקורית (מוסטת OFF שניות) + אפקטי נייר מסונתזים לפי sfx.json. בלי מוזיקה.
usage: python3 make_audio_full.py narr.wav sfx.json out.wav"""
import numpy as np, wave, subprocess, sys, json
SR=44100; OFF=1.6
narr,sfxj,outp=sys.argv[1:4]
info=json.load(open(sfxj)); DUR=info['TEND']; ev=info['SFX']
rng=np.random.default_rng(7)
def lp(x,a):
    y=np.zeros_like(x); s=0.0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
def env(n,att,dec): t=np.arange(n)/SR; e=np.minimum(t/att,1)*np.exp(-t/dec); return e/e.max()
def tear(d=.55):
    n=int(SR*d); x=rng.standard_normal(n); x=x-lp(x,.06); cr=(rng.random(n)<.0025)*rng.standard_normal(n)*3
    return (x*.5+cr)*env(n,.02,.18)*np.hanning(n)**.3
def whoosh(d=.4):
    n=int(SR*d); x=lp(rng.standard_normal(n),.12); t=np.arange(n)/n; return x*np.sin(np.pi*t)**2*1.6
def thump(d=.25):
    n=int(SR*d); t=np.arange(n)/SR; return np.sin(2*np.pi*(90-30*t/d)*t)*np.exp(-t/.07)*1.1
def glitch(d=.2):
    n=int(SR*d); x=rng.standard_normal(n)*(rng.random(n)<.18); return lp(x,.5)*3*np.exp(-np.arange(n)/SR/.1)
out=np.zeros(int(SR*DUR)+SR)
def put(x,t,g):
    i=int(max(0,t)*SR)
    if i<len(out): out[i:i+len(x)]+=x[:len(out)-i]*g
G={'tear':(tear,.30),'whoosh':(whoosh,.22),'soft':(lambda:whoosh(.3),.10),'stamp':(thump,.45),'glitch':(glitch,.22)}
for e in ev:
    if e['k'] in G and e['t']>0: f,g=G[e['k']]; put(f(),e['t'],g)
out=np.clip(out[:int(SR*DUR)],-1,1); pcm=(out*32767).astype('<i2')
w=wave.open('/tmp/sfx_full.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',narr,'-i','/tmp/sfx_full.wav','-filter_complex',
 f'[0:a]asetpts=PTS-STARTPTS,adelay={int(OFF*1000)}|{int(OFF*1000)},aresample={SR},loudnorm=I=-16:TP=-1.5:LRA=11[n];[1:a]volume=0.55[s];[n][s]amix=inputs=2:duration=longest:normalize=0,atrim=0:{DUR}[o]',
 '-map','[o]','-ac','2','-c:a','pcm_s16le',outp],check=True)
print('audio ok',DUR)
