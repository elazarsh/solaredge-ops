import sys,subprocess,numpy as np
sys.path.insert(0,"../edit")
from mixlib import *
from scipy import signal
T=42.5; N=int(T*SR)+SR
S0=35.24
# ---------- music ----------
bpm=112; beat=60/bpm; music=np.zeros(N)
chords=[[60,64,67,71],[55,59,62,67],[57,60,64,69],[53,57,60,65]]; bass=[36,31,33,29]
def marimba(f,d=0.5):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*4*t)*np.exp(-t*18))*np.exp(-t*7)
def pad(f,d):
    t=tt(d); y=(signal.sawtooth(2*np.pi*f*t)+signal.sawtooth(2*np.pi*f*1.004*t))*0.5; y=lp(y,1400,2); return y*adsr(len(t),0.3,0.2,0.7,0.4)
t0=0.0; bar=0
while t0<38.5:
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
def g(t): return t if t<14.36 else (t+2.04 if t<31.8 else t+3.44)
# s1 (0-5.08)
for i in range(6): step(0.5+i*0.27)
whoosh(2.0,0.4,0.25); plop(2.4,0.7); thud(4.05,0.2); hiss(3.3,0.3,0.1)
# s2 truck 1 (5.08-10.32)
truck(5.7,4.2,0.9); hiss(6.9,0.5,0.4); hydraulic(7.2,0.8,0.4); hydraulic(7.9,0.9,0.4); thud(8.7,0.8); boing(10.0,0.55); whoosh(9.8,0.4,0.25)
# s3 (10.32-14.36): drag + waiting
scrape(10.9,1.2,0.4); ticks(11.2,13.4,0.4)
whoosh(11.2,0.5,0.25); whoosh(12.9,0.5,0.25)
truck(13.1,3.0,0.85); whistle(14.2,0.8,0.28); hiss(14.0,0.6,0.25)
# wait2 still (14.36-16.4): time passes, he fumes
ticks(14.45,16.35,0.4); whoosh(14.4,0.5,0.25); boing(14.5,0.35); whistle(15.3,0.9,0.28); hiss(15.4,0.7,0.22)
# s4a (16.4-19.48)
truck(g(16.6),2.3,0.9)
# s4b (19.48-20.6)
whistle(g(17.5),0.95,0.35); hiss(g(17.6),0.8,0.3); ting(g(18.3),1568,0.35); ting(g(18.4),2093,0.25)
# s5
whoosh(g(19.0),0.4,0.25); thud(g(20.2),0.35); boing(g(21.2),0.3); ting(g(22.6),1760,0.35); boing(g(23.0),0.35,up=False)
# s6
plop(g(24.35),0.6); thud(g(25.0),0.45); truck(g(25.4),3.2,0.9); hydraulic(g(26.7),0.9,0.4); thud(g(28.3),0.85); boing(g(28.95),0.5)
# s7 (31.4-33.84) and F still (33.84-35.24)
for i in range(5): step(g(29.7)+i*0.25)
hiss(g(31.0),0.3,0.12); plop(g(31.55),0.6); tune(g(31.7)+0.15,[72,76,79,84],0.28)
# slogan card
S0=g(31.8)
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
save(mix[:int((S0+2.6+4.06)*SR)],"pan_mix.wav"); print("ok")
