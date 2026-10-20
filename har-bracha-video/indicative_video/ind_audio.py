import json,subprocess,sys,numpy as np
sys.path.insert(0,"../edit")
from mixlib import *
T=30.2; N=int(T*SR)+SR
# narration schedule (global seconds)
START={"a1":0.4,"a2":3.3,"a3":11.0,"a4":14.7,"a5":18.1,"a1r":21.5}
TEMPO={"a2":1.1}
pick=json.load(open("takes/res.json"))
EQ="equalizer=f=1100:t=q:w=1.2:g=3,equalizer=f=3200:t=q:w=1:g=5,equalizer=f=6500:t=q:w=1:g=2.5"
voice=np.zeros(N); info={}
for k,st in START.items():
    base=k[:-1] if k.endswith("r") else k
    take=pick[base]["pick"]["take"]; src=f"takes/{base}_{take}_t.wav"; nat=len(readwav(src))/SR
    tempo=TEMPO.get(k,1.0)
    af=f"highpass=f=90,rubberband=pitch=1.1:tempo={tempo}:formant=shifted,{EQ},acompressor=threshold=-22dB:ratio=3:attack=4:release=60,loudnorm=I=-15:TP=-1.5:LRA=6"
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",src,"-af",af,"-ar",str(SR),"-ac","1",f"final/{k}.wav"],check=True)
    w=readwav(f"final/{k}.wav"); place(voice,w,st,1.0); info[k]=dict(start=st,dur=round(len(w)/SR,2),tempo=tempo,nat=round(nat,2)); print(k,info[k])
json.dump(info,open("vinfo.json","w"))
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
low=np.where(np.arange(N)/SR>24.1,0.5,1.0); music=music*fade*low
# ---- sfx
sfx=np.zeros(N)
def whoosh(st,d=0.55,g=0.5):
    t=tt(d); w=bp(noise(d),500,5000)*np.sin(np.pi*t/d)**2; place(sfx,w,st,g)
for b_ in [2.85,10.65,14.35,17.75,21.15]: whoosh(b_)
def pop(st,f0=520,g=0.5):
    t=tt(0.14); f=f0+520*(t/0.14); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30),st,g)
def ting(st,f=1760,g=0.4):
    t=tt(0.9); place(sfx,(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*5),st,g)
def thud(st,g=0.6):
    t=tt(0.25); place(sfx,np.sin(2*np.pi*(90*np.exp(-t*10)+40)*t)*np.exp(-t*14)+0.3*lp(noise(0.25),500)*np.exp(-t*20),st,g)
# explain scene: truck rumble 3.3..5.3, lift clunk, tick, X pops
tr=np.arange(int(2.2*SR))/SR; rum=lp(noise(2.2),180)*(0.6+0.4*np.sin(2*np.pi*11*tr))*np.sin(np.pi*np.clip(tr/2.2,0,1))**0.5; place(sfx,rum,3.2,0.9)
thud(3.0+1.0,0.7); whoosh(3.0+1.0,0.5,0.3); ting(3.0+1.95)
for i in range(3): pop(3.0+3.1+i*0.25,380,0.5); thud(3.0+3.1+i*0.25,0.35)
# flows
for st in [10.8,14.5,17.9]: pop(st+0.2); thud(st+2.4); ting(st+2.65)
for st in [0.4+0.95, 21.3+0.55]: thud(st,0.7); whoosh(st-0.25,0.3,0.3)
# logo video audio
ea=subprocess.run(["ffmpeg","-loglevel","quiet","-ss","3.0","-t","5.8","-i","../edit/end.mp4","-af","rubberband=tempo=1.7","-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
ea=np.frombuffer(ea,dtype=np.float32).astype(np.float64); end_a=np.zeros(N); place(end_a,ea,24.1,1.0)
# final card chime
ting(27.5,1319,0.45); ting(27.95,1760,0.35); ting(28.4,2093,0.3)
mix=voice*1.0+music*0.30*(1-0.55*va)+sfx*0.55+end_a*0.45
save(mix[:int(T*SR)],"mix_i.wav"); print("mix ok")
