import json,subprocess,sys,numpy as np
sys.path.insert(0,"../edit")
from mixlib import *
T=40.8; N=int(T*SR)+SR
# narration schedule (global seconds)
START={"n1":0.5,"n2":4.55,"n3":10.2,"n4":15.2,"n5":20.15,"n6":26.9}
pick=json.load(open("takes/res.json"))
EQ="equalizer=f=1100:t=q:w=1.2:g=3,equalizer=f=3200:t=q:w=1:g=5,equalizer=f=6500:t=q:w=1:g=2.5"
voice=np.zeros(N); info={}
WIN={"n1":3.0,"n2":4.6,"n3":4.6,"n4":4.6,"n5":6.1,"n6":4.9}
for k,st in START.items():
    take=pick[k]["pick"]["take"]; src=f"takes/{k}_{take}_t.wav"; nat=len(readwav(src))/SR
    tempo=max(1.0,min(1.25,nat/WIN[k])) if nat>WIN[k] else 1.0
    af=f"highpass=f=90,rubberband=pitch=1.1:tempo={tempo}:formant=shifted,{EQ},acompressor=threshold=-22dB:ratio=3:attack=4:release=60,loudnorm=I=-15:TP=-1.5:LRA=6"
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",src,"-af",af,"-ar",str(SR),"-ac","1",f"final/{k}.wav"],check=True)
    w=readwav(f"final/{k}.wav"); place(voice,w,st,1.0); info[k]=dict(start=st,dur=round(len(w)/SR,2),tempo=round(tempo,2),nat=round(nat,2)); print(k,info[k])
json.dump(info,open("vinfo_t.json","w"))
# envelope 25fps for mouth flap
hop=SR//25; n=len(voice)//hop; e=np.sqrt((voice[:n*hop].reshape(n,hop)**2).mean(axis=1)); e=e/(np.percentile(e,95)+1e-9)
json.dump({"amp":[round(float(x),3) for x in np.clip(e,0,1.3)]},open("env.json","w"))
va=lp(np.abs(voice),8,1); va=np.clip(va/(np.percentile(va,95)+1e-9),0,1)
# ---- music: bright corporate bed, 112 bpm
bpm=112; beat=60/bpm; music=np.zeros(N)
chords=[[60,64,67,71],[55,59,62,67],[57,60,64,69],[53,57,60,65]]   # Cmaj7 G Am7 Fmaj
bass=[36,31,33,29]
def marimba(f,d=0.5):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*4*t)*np.exp(-t*18))*np.exp(-t*7)
def pad(f,d):
    t=tt(d); y=(signal.sawtooth(2*np.pi*f*t)+signal.sawtooth(2*np.pi*f*1.004*t))*0.5; y=lp(y,1400,2); return y*adsr(len(t),0.3,0.2,0.7,0.4)
t0=0.0; bar=0
while t0<T-0.5:
    ch=chords[bar%4]
    for k in range(8):
        n_=ch[[0,2,1,3,2,3,1,2][k]]+12; place(music,marimba(midi(n_),0.45),t0+k*beat/2,0.30)
    for n_ in ch[:3]: place(music,pad(midi(n_),4*beat),t0,0.05)
    for k in range(4):
        f=midi(bass[bar%4]); d=0.4; place(music,np.sin(2*np.pi*f*tt(d))*np.exp(-tt(d)*5),t0+k*beat,0.5)
        kick=np.sin(2*np.pi*(120*np.exp(-tt(0.15)*18)+45)*tt(0.15))*np.exp(-tt(0.15)*14); place(music,kick,t0+k*beat,0.55)
        place(music,hp(noise(0.05),7000)*np.exp(-tt(0.05)*60),t0+k*beat+beat/2,0.22)
        if k%2==1: place(music,bp(noise(0.12),1500,4500)*np.exp(-tt(0.12)*28),t0+k*beat,0.3)
    t0+=4*beat; bar+=1
fade=np.clip((np.arange(N)/SR-0.0)/0.6,0,1)*np.clip((T-np.arange(N)/SR)/1.5,0,1)
# logo section: calm music lower
low=np.where(np.arange(N)/SR>31.4,0.5,1.0); music=music*fade*low
# ---- sfx
sfx=np.zeros(N)
def whoosh(st,d=0.55,g=0.5):
    t=tt(d); w=bp(noise(d),500,5000)*np.sin(np.pi*t/d)**2; place(sfx,w,st,g)
for b_ in [4.05,9.75,14.75,19.75,26.25]: whoosh(b_)
def pop(st,f0=520,g=0.5):
    t=tt(0.14); f=f0+520*(t/0.14); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30),st,g)
for st in [4.45,10.15,15.15]: pop(st)
def ting(st,f=1760,g=0.4):
    t=tt(0.9); place(sfx,(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*5),st,g)
def thud(st,g=0.6):
    t=tt(0.25); place(sfx,np.sin(2*np.pi*(90*np.exp(-t*10)+40)*t)*np.exp(-t*14)+0.3*lp(noise(0.25),500)*np.exp(-t*20),st,g)
for ls in [4.2+2.95,9.9+2.95,14.9+2.95]: thud(ls); ting(ls+0.25)
# slam hits for slogan
for st in [1.0+0.35,26.4+0.7+0.35]: thud(st,0.7); whoosh(st-0.25,0.3,0.3)
# cat meow at S5 (local 1.7)
tm=tt(0.8); f0=np.interp(tm,[0,0.15,0.5,0.8],[520,780,560,430]); saw=signal.sawtooth(2*np.pi*np.cumsum(f0)/SR)
me=(bp(saw,700,1200)+0.8*bp(saw,1800,2800))*adsr(len(tm),0.06,0.12,0.7,0.3); place(sfx,me,19.9+1.75,0.5)
# steps for kid walking
for s in np.arange(19.9+0.3,19.9+1.6,0.26): place(sfx,lp(noise(0.03),1500)*np.exp(-tt(0.03)*90),s,0.4)
# bag throw whoosh + tick
whoosh(19.9+3.5,0.4,0.35); ting(19.9+4.4,1568,0.45)
# logo video audio
ea=subprocess.run(["ffmpeg","-loglevel","quiet","-ss","2.6","-t","6.2","-i","../edit/end.mp4","-af","rubberband=tempo=1.2","-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
ea=np.frombuffer(ea,dtype=np.float32).astype(np.float64); end_a=np.zeros(N); place(end_a,ea,31.4,1.0)
# final card chime
ting(36.9,1319,0.45); ting(37.4,1760,0.35); ting(37.9,2093,0.3)
mix=voice*1.0+music*0.30*(1-0.55*va)+sfx*0.55+end_a*0.45
save(mix[:int(T*SR)],"mix_t.wav"); print("mix ok")
