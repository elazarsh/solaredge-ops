import sys,subprocess,numpy as np
sys.path.insert(0,"../edit")
from mixlib import *
from scipy import signal
T=40; N=int(T*SR)+SR
S0=32.08
# ---------- music ----------
bpm=112; beat=60/bpm; music=np.zeros(N)
chords=[[60,64,67,71],[55,59,62,67],[57,60,64,69],[53,57,60,65]]; bass=[36,31,33,29]
def marimba(f,d=0.5):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*4*t)*np.exp(-t*18))*np.exp(-t*7)
def pad(f,d):
    t=tt(d); y=(signal.sawtooth(2*np.pi*f*t)+signal.sawtooth(2*np.pi*f*1.004*t))*0.5; y=lp(y,1400,2); return y*adsr(len(t),0.3,0.2,0.7,0.4)
t0=0.0; bar=0
while t0<35:
    ch=chords[bar%4]
    for k in range(8):
        n_=ch[[0,2,1,3,2,3,1,2][k]]+12; place(music,marimba(midi(n_),0.45),t0+k*beat/2,0.30)
    for n_ in ch[:3]: place(music,pad(midi(n_),4*beat),t0,0.05)
    for k in range(4):
        f=midi(bass[bar%4]); d=0.4; place(music,np.sin(2*np.pi*f*tt(d))*np.exp(-tt(d)*5),t0+k*beat,0.5)
        kick=np.sin(2*np.pi*(120*np.exp(-tt(0.15)*18)+45)*tt(0.15))*np.exp(-tt(0.15)*14); place(music,kick,t0+k*beat,0.45)
        place(music,hp(noise(0.05),7000)*np.exp(-tt(0.05)*60),t0+k*beat+beat/2,0.2)
    t0+=4*beat; bar+=1
ts=np.arange(N)/SR
music=music*np.clip(ts/0.6,0,1)*np.clip((S0+2.2-ts)/1.4,0,1)
# ---------- sfx ----------
sfx=np.zeros(N)
def whoosh(st,d=0.55,g=0.5):
    t=tt(d); place(sfx,bp(noise(d),500,5000)*np.sin(np.pi*t/d)**2,st,g)
def pop(st,f0=520,g=0.5):
    t=tt(0.14); f=f0+520*(t/0.14); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30),st,g)
def ting(st,f=1760,g=0.4):
    t=tt(0.9); place(sfx,(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*5),st,g)
def thud(st,g=0.6):
    t=tt(0.25); place(sfx,np.sin(2*np.pi*(90*np.exp(-t*10)+40)*t)*np.exp(-t*14)+0.3*lp(noise(0.25),500)*np.exp(-t*20),st,g)
def plop(st,g=0.6):
    t=tt(0.2); f=300+500*np.exp(-t*25); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*22)+0.25*lp(noise(0.2),900)*np.exp(-t*25),st,g)
def boing(st,g=0.5,up=True):
    t=tt(0.45); f=(250+700*(t/0.45)**0.7) if up else (900-650*(t/0.45)); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR+1.5*np.sin(2*np.pi*14*t))*np.exp(-t*5)*(np.sin(np.pi*np.clip(t/0.45,0,1))**0.3),st,g)
def step(st,g=0.25):
    t=tt(0.07); place(sfx,lp(noise(0.07),1800)*np.exp(-t*60),st,g)
def truck(st,dur,g=0.9,rev=True):
    t=np.arange(int(dur*SR))/SR; env=np.sin(np.pi*np.clip(t/dur,0,1))**0.6
    rum=lp(noise(dur),170)*(0.6+0.4*np.sin(2*np.pi*(11+3*(t/dur))*t))*env
    eng=lp(signal.sawtooth(2*np.pi*(48+14*np.sin(np.pi*t/dur))*t),300)*0.25*env
    place(sfx,rum+eng,st,g)
def hiss(st,d=0.6,g=0.35):
    t=tt(d); place(sfx,hp(noise(d),3500)*np.sin(np.pi*t/d)**0.8,st,g)
def hydraulic(st,d=1.2,g=0.35):
    t=tt(d); f=180+120*np.sin(2*np.pi*3*t/d)+80*(t/d); place(sfx,(lp(signal.sawtooth(2*np.pi*np.cumsum(f)/SR),900))*np.sin(np.pi*t/d)**0.7+0.5*bp(noise(d),600,2500)*np.sin(np.pi*t/d),st,g)
def whistle(st,d=0.8,g=0.3):
    t=tt(d); f=900+1500*(t/d)**1.5; place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*np.clip(t/d,0,1))**0.5,st,g)
def scrape(st,d=1.1,g=0.35):
    t=tt(d); place(sfx,bp(noise(d),300,2200)*(0.6+0.4*np.sin(2*np.pi*7*t))*np.sin(np.pi*t/d)**0.6,st,g)
def ticks(a,b,g=0.35):
    # time-lapse ticking, accelerating
    t=a; dt=0.28
    while t<b:
        t_=tt(0.05); place(sfx,(np.sin(2*np.pi*(1900 if int((t-a)/dt)%2 else 1400)*t_))*np.exp(-t_*90),t,g); t+=dt; dt=max(0.07,dt*0.95)
def tune(st,notes,g=0.3):
    for i,n in enumerate(notes): place(sfx,marimba(midi(n),0.35),st+i*0.13,g)
import json
TL=json.load(open("tl.json")); S=lambda n:TL[n]["start"]
# c1: steps, toss, land, sit
for i in range(4): step(S("c1")+0.05+i*0.27)
whoosh(S("c1")+1.2,0.45,0.25); plop(S("c1")+1.85,0.7); hiss(S("c1")+1.9,0.3,0.1); thud(S("c1")+2.6,0.2)
# truck 1: arrives, brakes, arm lifts only the bin, leaves
truck(S("c2a")+0.1,4.3,0.9); hiss(S("c2a")+1.3,0.5,0.4); hydraulic(S("c2a")+1.5,0.9,0.4); hydraulic(S("c2a")+2.5,0.9,0.4); thud(S("c2a")+3.35,0.8)
# bag still here: fly buzz
t=tt(1.0); buzz=np.sin(2*np.pi*(240+40*np.sin(2*np.pi*9*t))*t)*(0.5+0.5*np.sin(2*np.pi*3*t))*np.sin(np.pi*t)**0.5; place(sfx,buzz,S("Hbag"),0.18); ting(S("Hbag")+0.05,880,0.12)
# shock
boing(S("c2b")+0.1,0.55); whoosh(S("c2b")+0.0,0.3,0.25)
# drag closer
scrape(S("c3a")+0.45,1.2,0.4)
# waiting 1: time-lapse
ticks(S("wait1"),S("wait1")+1.8,0.4); whoosh(S("wait1")-0.1,0.5,0.25); whoosh(S("wait1")+1.4,0.5,0.25)
# truck 2 passes, he fumes
truck(S("c3t")-0.15,2.3,0.85); whistle(S("c3t")+1.0,0.8,0.28); hiss(S("c3t")+1.05,0.6,0.25)
# waiting 2
ticks(S("wait2"),S("wait2")+2.0,0.4); boing(S("wait2")+0.1,0.35); whistle(S("wait2")+1.0,0.9,0.3); hiss(S("wait2")+1.1,0.7,0.22); whoosh(S("wait2")-0.1,0.4,0.25)
# closer, pleading, truck 3
thud(S("c3c")+0.3,0.4); truck(S("c3c")+1.1,1.9,0.9)
whistle(S("steam")+0.05,0.9,0.35); hiss(S("steam")+0.15,0.8,0.3); ting(S("steam")+0.75,1568,0.35); ting(S("steam")+0.85,2093,0.25)
# driver
whoosh(S("c4a")+0.0,0.4,0.25); thud(S("c4a")+0.5,0.35); boing(S("c4a")+1.2,0.3)
boing(S("c4b")+0.1,0.35,up=False); ting(S("c4b")+0.75,1760,0.35)
# cat
plop(S("c5")+0.5,0.6); thud(S("c5")+2.3,0.45); truck(S("c5")+1.0,3.1,0.9); hydraulic(S("c5")+2.6,0.9,0.4); thud(S("c5")+3.6,0.5)
# reaction
boing(S("G")+0.1,0.55); hydraulic(S("G")+0.1,0.8,0.25); thud(S("G")+0.6,0.7)
# resolution
for i in range(4): step(S("c6")+0.05+i*0.25)
hiss(S("c6")+1.0,0.3,0.12); plop(S("c6")+1.3,0.6); tune(S("c6")+1.45,[72,76,79,84],0.28)
# slogan card
whoosh(S0-0.15,0.4,0.3); pop(S0+0.05,520,0.45); pop(S0+0.5,380,0.4); thud(S0+0.5,0.35); ting(S0+0.6,1760,0.3)
# ---------- voice + logo ----------
v=readwav("../ind/final/a1r.wav"); voice=np.zeros(N); place(voice,v,S0+0.2,1.0)
ea=subprocess.run(["ffmpeg","-loglevel","quiet","-ss","3.0","-t","6.9","-i","../edit/end.mp4","-af","rubberband=tempo=1.7","-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
ea=np.frombuffer(ea,dtype=np.float32).astype(np.float64); L=len(ea)/SR
ea=ea*np.clip(np.arange(len(ea))/SR/0.3,0,1)*np.clip((L-np.arange(len(ea))/SR)/0.7,0,1)
end_a=np.zeros(N); place(end_a,ea,S0+2.6,1.0)
va=lp(np.abs(voice),8,1); va=np.clip(va/(np.percentile(va,95)+1e-9),0,1)
mix=voice*1.0+music*0.27*(1-0.5*va)+sfx*0.6+end_a*0.85
peak=np.abs(mix).max(); print("peak",peak)
if peak>0.97: mix=mix*0.95/peak
save(mix[:int((S0+2.6+4.06)*SR)],"pan_mix2.wav"); print("ok")
