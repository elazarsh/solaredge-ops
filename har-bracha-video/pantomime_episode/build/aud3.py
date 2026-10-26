import sys,subprocess,json,numpy as np
sys.path.insert(0,"../edit")
from mixlib import *
from scipy import signal
TL=json.load(open("tl.json")); B0=4.0
S=lambda n,o=0.0:TL[n]["start"]+B0+o
S0=B0+TL["_total"]-0.25+1.65-0.25+0.0   # slogan start (global)
S0=B0+TL["_total"]+1.65-0.25
T=S0+2.6+4.06+0.5; N=int(T*SR)+SR
rng2=np.random.default_rng(7)
def nz(d): return rng2.normal(size=int(d*SR))
def env_adsr(n,a=0.01,r=0.1):
    e=np.ones(n); na=int(a*SR); nr=int(r*SR)
    if na>0: e[:na]=np.linspace(0,1,na)
    if nr>0 and nr<n: e[-nr:]*=np.linspace(1,0,nr)
    return e
# ---------------- instruments ----------------
def pizz(f,d=0.22):
    t=tt(d); y=(signal.sawtooth(2*np.pi*f*t,0.5)+0.4*np.sin(2*np.pi*2*f*t))*np.exp(-t*16); return lp(y,3000,2)
def bass(f,d=0.34):
    t=tt(d); y=(np.sin(2*np.pi*f*t)+0.45*np.sin(2*np.pi*2*f*t)*np.exp(-t*8))*np.exp(-t*6.5)*(1-np.exp(-t*220)); return y
def clar(f,d=0.3,vib=1.0):
    t=tt(d); v=1+0.004*vib*np.sin(2*np.pi*5.6*t)*np.clip(t/0.15,0,1); ph=2*np.pi*f*np.cumsum(v)/SR
    y=np.sin(ph)+0.42*np.sin(3*ph)+0.2*np.sin(5*ph)+0.08*np.sin(7*ph); y+=0.05*lp(nz(d),3000)
    return lp(y,4200,2)*env_adsr(len(t),0.03,0.07)
def trumpet(f,d=0.4):
    t=tt(d); ph=2*np.pi*f*t; y=signal.sawtooth(ph)*0.6+0.3*np.sin(2*ph); wah=0.5+0.5*np.sin(2*np.pi*2.2*t); y=bp(y,500,2600)*(0.6+0.7*wah); return y*env_adsr(len(t),0.05,0.1)
def xylo(f,d=0.3):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*3.9*t)*np.exp(-t*30))*np.exp(-t*14)
def glock(f,d=0.6):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*f*2.76*t)+0.15*np.sin(2*np.pi*f*5.4*t))*np.exp(-t*6)
def wblock(f=900,d=0.08):
    t=tt(d); return np.sin(2*np.pi*f*t)*np.exp(-t*70)
def brush(d=0.18):
    t=tt(d); return lp(hp(nz(d),1500),7000)*np.exp(-t*18)
def ride(d=0.5):
    t=tt(d); y=hp(nz(d),6000)*np.exp(-t*9)+0.25*np.sin(2*np.pi*5400*t)*np.exp(-t*9); return y
def kickd(d=0.2):
    t=tt(d); return np.sin(2*np.pi*(90*np.exp(-t*20)+50)*t)*np.exp(-t*16)
def ukulele(fs,d=0.35):
    y=0
    for i,f in enumerate(fs): y=y+pizz(f,d)*(1-0.05*i)
    return y/len(fs)
# --------------- music cues ----------------
music=np.zeros(N)
def swing(i,beat): return (i//2)*beat+(0 if i%2==0 else beat*0.66)
def cue(style,t0,t1,vol=1.0):
    seg=np.zeros(N)
    P={"jaunty":dict(bpm=126,ch=[(60,[60,64,67,69]),(57,[57,61,64,67]),(62,[62,65,69,72]),(55,[55,59,62,65])],bass=[36,45,38,43],mel=[[76,79,76,72,76,79,81,79],[77,76,73,76,81,76,73,69],[74,77,81,77,74,77,81,84],[83,81,79,77,74,71,67,71]]),
       "sneak":dict(bpm=100,ch=[(57,[57,60,64]),(52,[52,56,59]),(57,[57,60,64]),(52,[52,56,59])],bass=[33,34,35,36],mel=[[72,0,71,0,69,0,0,0],[0,0,76,0,75,0,0,0],[72,0,71,0,69,0,68,0],[0,0,0,0,0,0,0,0]]),
       "panic":dict(bpm=156,ch=[(50,[50,53,57]),(55,[55,58,62]),(50,[50,53,57]),(57,[57,61,64])],bass=[38,43,38,45],mel=[[74,77,81,77,74,77,81,86],[76,79,83,79,76,79,83,88],[74,77,81,77,74,77,81,86],[73,76,81,76,73,76,81,85]]),
       "friendly":dict(bpm=112,ch=[(65,[65,69,72]),(72,[60,64,67]),(70,[62,65,70]),(67,[59,62,67])],bass=[41,48,46,43],mel=[[77,0,81,0,84,81,77,0],[76,0,79,0,84,79,76,0],[77,81,86,84,82,0,79,0],[79,0,77,0,72,0,0,0]]),
       "cool":dict(bpm=108,ch=[(60,[60,63,67,70]),(65,[65,68,72,75]),(60,[60,63,67,70]),(67,[59,62,67,70])],bass=[36,41,36,43],mel=[[75,0,0,74,72,0,70,0],[72,0,0,75,77,0,0,0],[75,0,74,0,72,0,67,0],[70,0,0,67,0,0,0,0]]),
       "resolve":dict(bpm=132,ch=[(60,[60,64,67,69]),(65,[65,69,72]),(67,[67,71,74]),(60,[60,64,67,72])],bass=[36,41,43,36],mel=[[76,79,84,79,76,79,84,88],[77,81,84,81,77,81,84,89],[79,83,86,83,79,83,86,91],[84,0,84,0,88,0,0,0]])}[style]
    beat=60/P["bpm"]; t=t0; bar=0; sw=style in("jaunty","cool","resolve","friendly")
    while t<t1-0.05:
        ch=P["ch"][bar%4]; b=P["bass"][bar%4]; mel=P["mel"][bar%4]
        for k in range(4):   # walking bass on quarters
            n_=[b,b+4 if style!="sneak" else b+1,b+7 if style!="sneak" else b+2,b+9][k] if style in("jaunty","resolve","friendly","cool") else b+[0,0,7,0][k]+(12 if style=="panic" and k%2 else 0)
            place(seg,bass(midi(n_),0.33),t+k*beat,0.55)
            if style in("jaunty","resolve","cool","friendly") and k in(1,3): place(seg,ukulele([midi(x) for x in ch[1]],0.26) if style!="cool" else ukulele([midi(x-12) for x in ch[1][:3]],0.3),t+k*beat+(beat*0.66 if sw else beat/2)*0,0.25)
        if style in("jaunty","resolve","friendly"): 
            for k in (0,2): place(seg,kickd(),t+k*beat,0.3)
            for k in (1,3): place(seg,brush(),t+k*beat,0.28)
        if style=="cool":
            for k in range(8): place(seg,ride(0.3),t+swing(k,beat/1)*0.5*2/2*(1 if True else 1),0.12) if k%2==0 or k==3 or k==7 else None
            for k in (1,3): place(seg,brush(0.14),t+k*beat,0.2)
        if style=="sneak":
            for k in range(4): place(seg,wblock(700+100*(k%2)),t+k*beat+beat*0.5,0.35)
            place(seg,glock(midi(ch[1][2]+24),0.5),t+3*beat,0.12 if bar%2 else 0.0)
        if style=="panic":
            for k in range(8): place(seg,brush(0.1),t+k*beat/2,0.3)
            place(seg,kickd(),t,0.4); place(seg,kickd(),t+2*beat,0.4)
        for i,n_ in enumerate(mel):
            if n_<=0: continue
            tm=t+(swing(i,beat/2*2)/1 if False else (i//2)*beat+(0 if i%2==0 else beat*(0.66 if sw else 0.5)))
            if style in("jaunty","resolve","friendly"): place(seg,clar(midi(n_),0.26 if style!="friendly" else 0.3),tm,0.34)
            elif style=="panic": place(seg,xylo(midi(n_),0.25),tm,0.3)
            elif style=="cool": place(seg,trumpet(midi(n_-12),0.42),tm,0.32)
            elif style=="sneak": place(seg,clar(midi(n_-12),0.2,0.2),tm,0.25)
        t+=4*beat; bar+=1
    ts_=np.arange(N)/SR; m=np.clip((ts_-t0)/0.12,0,1)*np.clip((t1-ts_)/0.15,0,1)
    music[:]+=seg*m*vol
# ------------- SFX -------------
sfx=np.zeros(N); fx_truck=np.zeros(N)
def pl(buf,x,st,g): place(buf,x,st,g)
def whoosh(st,d=0.5,g=0.4): t=tt(d); pl(sfx,bp(nz(d),500,5000)*np.sin(np.pi*t/d)**2,st,g)
def pop(st,f0=520,g=0.5): t=tt(0.14); pl(sfx,np.sin(2*np.pi*np.cumsum(f0+520*(t/0.14))/SR)*np.exp(-t*30),st,g)
def ting(st,f=1760,g=0.4): t=tt(0.9); pl(sfx,(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*5),st,g)
def thud(st,g=0.6): t=tt(0.25); pl(sfx,np.sin(2*np.pi*(90*np.exp(-t*10)+40)*t)*np.exp(-t*14)+0.3*lp(nz(0.25),500)*np.exp(-t*20),st,g)
def plop(st,g=0.6): t=tt(0.2); f=300+500*np.exp(-t*25); pl(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*22)+0.25*lp(nz(0.2),900)*np.exp(-t*25),st,g)
def boing(st,g=0.5,up=True):
    t=tt(0.45); f=(250+700*(t/0.45)**0.7) if up else (900-650*(t/0.45)); pl(sfx,np.sin(2*np.pi*np.cumsum(f)/SR+1.5*np.sin(2*np.pi*14*t))*np.exp(-t*5)*(np.sin(np.pi*np.clip(t/0.45,0,1))**0.3),st,g)
def step(st,g=0.3): t=tt(0.09); pl(sfx,lp(nz(0.09),1500)*np.exp(-t*50)+0.4*np.sin(2*np.pi*140*t)*np.exp(-t*40),st,g)
def hiss(st,d=0.6,g=0.35): t=tt(d); pl(sfx,hp(nz(d),3500)*np.sin(np.pi*t/d)**0.8,st,g)
def whistle(st,d=0.8,g=0.3): t=tt(d); f=900+1500*(t/d)**1.5; pl(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*np.clip(t/d,0,1))**0.5,st,g)
def scrape(st,d=1.1,g=0.35): t=tt(d); pl(sfx,bp(nz(d),300,2200)*(0.6+0.4*np.sin(2*np.pi*7*t))*np.sin(np.pi*t/d)**0.6,st,g)
def crinkle(st,d=0.35,g=0.25): t=tt(d); pl(sfx,hp(nz(d),2500)*(rng2.random(len(t))>0.7)*np.exp(-t*7),st,g)
def ticks(a,b,g=0.35):
    t=a; dt=0.28
    while t<b:
        t_=tt(0.05); pl(sfx,np.sin(2*np.pi*(1900 if int((t-a)/dt)%2 else 1400)*t_)*np.exp(-t_*90),t,g); t+=dt; dt=max(0.07,dt*0.95)
def meow(st,g=0.35):
    d=0.55; t=tt(d); f=420+260*np.sin(np.pi*np.clip(t/d,0,1))**1.5; src=signal.sawtooth(2*np.pi*np.cumsum(f*(1+0.01*np.sin(2*np.pi*20*t)))/SR)
    y=bp(src,650,1200)*0.8+bp(src,1800,2600)*0.4; pl(sfx,y*np.sin(np.pi*np.clip(t/d,0,1))**0.7,st,g)
def tune(st,notes,g=0.3):
    for i,n in enumerate(notes): pl(sfx,xylo(midi(n),0.4),st+i*0.13,g)
# truck family (go to fx_truck so music ducks)
def truck_pass(st,dur,g=1.0,f0=46):
    t=np.arange(int(dur*SR))/SR; u=t/dur; env=np.sin(np.pi*np.clip(u,0,1))**0.7
    f=f0*(1.0+0.25*(1-u)); ph=2*np.pi*np.cumsum(f)/SR
    eng=(signal.sawtooth(ph)*0.5+np.sin(ph)+0.4*np.sin(2*ph))*(0.7+0.3*np.sin(2*np.pi*f*0.5*t)) 
    chug=lp(nz(dur),220)*(0.5+0.5*np.sin(2*np.pi*17*t))
    road=bp(nz(dur),250,1400)*0.25*(0.7+0.3*np.sin(2*np.pi*9*t))
    y=lp(eng,420,2)*0.8+chug*1.0+road; pl(fx_truck,y*env,st,g*0.9)
def diesel(st,dur,g=0.6):
    t=np.arange(int(dur*SR))/SR; y=lp(nz(dur),160)*(0.45+0.55*np.sin(2*np.pi*14*t)**2)+0.5*lp(signal.sawtooth(2*np.pi*38*t),260)
    pl(fx_truck,y*env_adsr(len(t),0.15,0.3),st,g)
def air_brake(st,g=0.55):
    d=0.9; t=tt(d); y=hp(nz(d),2200)*np.exp(-t*4.5); y[:int(0.04*SR)]*=np.linspace(0,1,int(0.04*SR)); pl(fx_truck,y,st,g); pl(fx_truck,hp(nz(0.05),4000)*np.exp(-tt(0.05)*60),st+0.95,0.25)
def reverse_beep(st,dur,g=0.28):
    t=st
    while t<st+dur:
        tb=tt(0.2); pl(fx_truck,np.sign(np.sin(2*np.pi*1050*tb))*0.3*np.sin(2*np.pi*1050*tb)**0+np.sin(2*np.pi*1050*tb)*0.6,t,g); t+=0.5
def hydraulic(st,dur=1.0,g=0.5):
    t=np.arange(int(dur*SR))/SR; f=380+260*np.sin(np.pi*t/dur)+120*(t/dur); y=lp(signal.sawtooth(2*np.pi*np.cumsum(f)/SR),1500)*0.5+bp(nz(dur),800,3000)*0.35
    pl(fx_truck,y*env_adsr(len(t),0.08,0.15)*(0.7+0.3*np.sin(2*np.pi*11*t)),st,g)
def clank(st,g=0.5):
    d=0.5; t=tt(d); y=sum(a*np.sin(2*np.pi*f*t+p) for a,f,p in [(1,310,0),(.8,830,1),(.6,1370,2),(.5,2310,3),(.3,3300,1)])*np.exp(-t*14)+0.5*hp(nz(d),1500)*np.exp(-t*35)
    pl(fx_truck,y,st,g)
def dump(st,g=0.55):
    d=0.9; t=tt(d); y=bp(nz(d),150,2500)*(np.exp(-t*3.5)*(0.6+0.4*(rng2.random(len(t))>0.5)))+0.8*lp(nz(d),200)*np.exp(-t*5); pl(fx_truck,y,st,g)
def compactor(st,dur=1.0,g=0.4):
    t=np.arange(int(dur*SR))/SR; y=bp(nz(dur),100,900)*(0.5+0.5*np.sin(2*np.pi*6*t)**2)+0.5*lp(nz(dur),120); pl(fx_truck,y*env_adsr(len(t),0.1,0.2),st,g)
# ---------------- MUSIC PLAN (global times) ----------------
def G(n,o=0.0): return S(n,o)
# intro jingle 0-4
cue("jaunty",0.0,B0-0.05,0.9)
# body
cue("jaunty",G("c1"),G("Hbag"),1.0)
cue("sneak",G("Hbag"),G("c3t"),0.9)
cue("panic",G("c3t"),G("wait2"),0.8)
cue("sneak",G("wait2"),G("steam"),0.9)
cue("panic",G("steam"),G("c4a"),0.8)
cue("friendly",G("c4a"),G("Ldrop"),0.9)
cue("cool",G("Ldrop"),G("G"),1.0)
cue("sneak",G("G"),G("K"),0.0)
cue("jaunty",G("K")+0.9,G("c6")+0.0,0.8)
cue("resolve",G("c6"),S0-0.1,1.0)
# --------------- SFX PLAN ---------------
# intro: title pops
for i in range(10): pop(0.5+i*0.06+0.1,420+30*i,0.3)
whoosh(0.3,0.5,0.35); ting(1.3,1568,0.35); ting(1.4,2093,0.3); ting(1.5,2637,0.25)
for i in range(4): step(B0-0.0+0)
# c1
for i in range(4): step(G("c1")+0.05+i*0.27)
whoosh(G("c1")+1.2,0.45,0.25); plop(G("c1")+1.85,0.7); crinkle(G("c1")+1.85,0.3,0.25); thud(G("c1")+2.6,0.2)
# truck 1
truck_pass(G("c2a")+0.05,1.5,0.9); air_brake(G("c2a")+1.1); diesel(G("c2a")+1.3,2.1,0.5)
hydraulic(G("c2a")+1.5,0.9,0.5); clank(G("c2a")+2.0,0.5); hydraulic(G("c2a")+2.2,0.9,0.5); compactor(G("c2a")+2.9,0.6,0.4); dump(G("c2a")+2.8,0.5); clank(G("c2a")+3.35,0.55); thud(G("c2a")+3.4,0.6)
truck_pass(G("c2a")+3.3,1.4,0.9,f0=55)
# bag still here: fly
t=tt(1.0); buzz=np.sin(2*np.pi*(240+40*np.sin(2*np.pi*9*t))*t)*(0.5+0.5*np.sin(2*np.pi*3*t))*np.sin(np.pi*t)**0.5; pl(sfx,buzz,G("Hbag"),0.18)
boing(G("c2b")+0.1,0.55); whoosh(G("c2b"),0.3,0.25)
scrape(G("c3a")+0.45,1.2,0.4); crinkle(G("c3a")+0.45,1.0,0.2)
ticks(G("wait1"),G("wait1")+1.8,0.4); whoosh(G("wait1")-0.1,0.5,0.25); whoosh(G("wait1")+1.4,0.5,0.25)
# truck 2
truck_pass(G("c3t")-0.2,1.9,1.0); whistle(G("c3t")+1.0,0.8,0.28); hiss(G("c3t")+1.05,0.6,0.25)
ticks(G("wait2"),G("wait2")+2.0,0.4); boing(G("wait2")+0.1,0.35); whistle(G("wait2")+1.0,0.9,0.3); hiss(G("wait2")+1.1,0.7,0.22); whoosh(G("wait2")-0.1,0.4,0.25)
thud(G("c3c")+0.3,0.4); truck_pass(G("c3c")+0.95,1.6,1.0)
whistle(G("steam")+0.05,0.9,0.35); hiss(G("steam")+0.15,0.8,0.3); ting(G("steam")+0.75,1568,0.35); ting(G("steam")+0.85,2093,0.25)
# driver
whoosh(G("c4a"),0.4,0.25); thud(G("c4a")+0.5,0.35); boing(G("c4a")+1.2,0.3); diesel(G("c4a"),3.0,0.35)
boing(G("c4b")+0.1,0.35,up=False); ting(G("c4b")+0.75,1760,0.35)
# cat drop + punch
meow(G("Ldrop")+0.1,0.3); plop(G("Ldrop")+0.4,0.6); crinkle(G("Ldrop")+0.4,0.3,0.2); thud(G("Ldrop")+0.5,0.35)
ting(G("Ldrop")+0.45,1568,0.35); pop(G("Ldrop")+0.45,700,0.3); boing(G("Ldrop")+1.0,0.25,up=False); pop(G("Ldrop")+1.0,300,0.3)
thud(G("c5")+0.5,0.45); truck_pass(G("c5")+0.05,1.6,1.0); air_brake(G("c5")+1.1,0.5); hydraulic(G("c5")+1.4,1.1,0.5); clank(G("c5")+1.7,0.5); hydraulic(G("c5")+2.0,0.8,0.5); compactor(G("c5")+2.2,0.8,0.4); dump(G("c5")+2.3,0.5); pop(G("c5")+2.3,300,0.3)
boing(G("G")+0.1,0.55); dump(G("G")+0.05,0.4); clank(G("G")+0.35,0.4); pop(G("G")+0.4,300,0.3)
# aha
whistle(G("K")+0.0,0.5,0.2); ting(G("K")+0.05,2349,0.4); tune(G("K")+0.1,[79,83,86,91],0.35); pop(G("K")+0.9,300,0.3); thud(G("K")+0.9,0.2); pop(G("K")+1.5,700,0.3); ting(G("K")+1.5,1568,0.35)
# resolution
for i in range(4): step(G("c6")+0.05+i*0.25)
hiss(G("c6")+1.0,0.3,0.12); plop(G("c6")+1.3,0.6); tune(G("c6")+1.45,[72,76,79,84],0.3)
# slogan
whoosh(S0-0.15,0.4,0.3); pop(S0+0.05,520,0.45); pop(S0+0.5,380,0.4); thud(S0+0.5,0.35); ting(S0+0.6,1760,0.3)
# voice + logo
v=readwav("../ind/final/a1r.wav"); voice=np.zeros(N); place(voice,v,S0+0.2,1.0)
ea=subprocess.run(["ffmpeg","-loglevel","quiet","-ss","3.0","-t","6.9","-i","../edit/end.mp4","-af","rubberband=tempo=1.7","-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
ea=np.frombuffer(ea,dtype=np.float32).astype(np.float64); L=len(ea)/SR
ea=ea*np.clip(np.arange(len(ea))/SR/0.3,0,1)*np.clip((L-np.arange(len(ea))/SR)/0.7,0,1)
end_a=np.zeros(N); place(end_a,ea,S0+2.6,1.0)
# duck music under truck + voice + fade out before logo jingle
tr_env=lp(np.abs(fx_truck),6,1); tr_env=np.clip(tr_env/(np.percentile(tr_env,98)+1e-9),0,1)
va=lp(np.abs(voice),8,1); va=np.clip(va/(np.percentile(va,95)+1e-9),0,1)
ts=np.arange(N)/SR
music=music*np.clip(ts/0.3,0,1)*np.clip((S0+2.2-ts)/1.2,0,1)
mix=voice*1.0+music*0.30*(1-0.55*tr_env)*(1-0.5*va)+sfx*0.65+fx_truck*0.8+end_a*0.85
peak=np.abs(mix).max(); print("peak",peak)
if peak>0.97: mix=mix*0.95/peak
save(mix[:int((S0+2.6+4.06)*SR)],"pan_mix3.wav"); print("ok S0",S0)
