import numpy as np, json, wave, subprocess
from scipy import signal
SR=44100; T=35.0; N=int(SR*T)
rng=np.random.default_rng(7)
def tt(d): return np.arange(int(SR*d))/SR
def place(buf,x,start,gain=1.0):
    i=int(start*SR); j=min(N,i+len(x))
    if i<N: buf[i:j]+=x[:j-i]*gain
def adsr(n,a=0.005,d=0.1,s=0.5,r=0.2):
    e=np.ones(n); na=int(a*SR); nd=int(d*SR); nr=int(r*SR)
    e[:na]=np.linspace(0,1,na,endpoint=False)
    e[na:na+nd]=np.linspace(1,s,nd) if na+nd<=n else e[na:na+nd]
    e[na+nd:n-nr]=s
    e[n-nr:]=np.linspace(s,0,nr)
    return e
def lp(x,f,o=2): b,a=signal.butter(o,f/(SR/2),"low"); return signal.lfilter(b,a,x)
def hp(x,f,o=2): b,a=signal.butter(o,f/(SR/2),"high"); return signal.lfilter(b,a,x)
def bp(x,f1,f2,o=2): b,a=signal.butter(o,[f1/(SR/2),f2/(SR/2)],"band"); return signal.lfilter(b,a,x)
def midi(m): return 440*2**((m-69)/12)
# ---- voices
voice=np.zeros(N)
for L in json.load(open("lines_env.json")):
    w=np.frombuffer(subprocess.run(["ffmpeg","-loglevel","quiet","-i",f"audio/final/{L['id']}.wav","-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout,dtype=np.float32)
    place(voice,w,L["start"],1.0)
# voice activity for ducking
va=lp(np.abs(voice),8,1); va=np.clip(va/ (np.percentile(va,95)+1e-9),0,1)
# ---- music: lounge 0..12.93
def rhodes(f,d,vel=0.5):
    t=tt(d); y=np.sin(2*np.pi*f*t+0.8*np.exp(-t*6)*np.sin(2*np.pi*f*t))*np.exp(-t*3.2)
    y+=0.25*np.sin(2*np.pi*f*2*t)*np.exp(-t*5)
    return y*vel
music=np.zeros(N)
bpm=96; beat=60/bpm
chords=[[50,53,57,60,64],[43,53,59,64],[48,52,55,59,62],[45,52,55,61,64]]  # Dm9 G13 Cmaj9 A7
basses=[38,43,36,33]
t0=0.0; bar=0
while t0<12.93:
    ch=chords[bar%4]
    for k,beat_pos in enumerate([0,1.5,2,3.5]):   # comping with swing-ish
        st=t0+beat_pos*beat+(0.04 if beat_pos%1 else 0)
        for n in ch: place(music,rhodes(midi(n+12),0.9,0.07),st+rng.uniform(0,0.012))
    for k,(bp_,off) in enumerate([(0,0),(1,7),(2,0),(3,5)]):
        st=t0+bp_*beat
        f=midi(basses[bar%4]+off)
        d=0.55; x=np.sin(2*np.pi*f*tt(d))*np.exp(-tt(d)*4.5)
        place(music,x,st,0.55)
    for h in range(8):
        st=t0+h*beat/2+(0.035 if h%2 else 0)
        n=hp(rng.normal(size=int(0.05*SR)),6000)*np.exp(-tt(0.05)*60)
        place(music,n,st,0.16 if h%2==0 else 0.09)
    t0+=4*beat; bar+=1
music[int(12.93*SR):]=0
mus_gain=0.30*(1-0.62*va)
# ---- guitar: 17.4..33.4
def pluck(f,d):
    n=int(SR/f); buf=rng.uniform(-1,1,n); out=np.zeros(int(SR*d))
    for i in range(len(out)):
        out[i]=buf[i%n]; buf[i%n]=0.5*(buf[i%n]+buf[(i+1)%n])*0.996
    return out
guitar=np.zeros(N)
prog=[[45,52,57,60,64],[41,48,53,57,60]]
t0=17.4; i=0; step=60/78/2
while t0<33.0:
    ch=prog[(i//8)%2]
    n=ch[[0,2,3,4,3,2,1,2][i%8]]
    place(guitar,pluck(midi(n),0.8)*0.5,t0)
    t0+=step; i+=1
g_env=np.clip((np.arange(N)/SR-17.4)/0.8,0,1)*np.clip((33.4-np.arange(N)/SR)/0.8,0,1)
guitar=guitar*g_env
guit_gain=0.22*(1-0.55*va)
# ---- sfx
sfx=np.zeros(N)
def noise(d): return rng.normal(size=int(d*SR))
# door creak + footsteps
t=tt(0.9); creak=(signal.sawtooth(2*np.pi*np.cumsum(110+60*np.sin(2*np.pi*3*t))/SR)*0.3); creak=bp(creak,200,1800)*np.hanning(len(t))
place(sfx,creak,0.0,0.5)
for s in [0.5,0.95,1.4,1.85,2.3,2.75,3.2]:
    place(sfx,lp(noise(0.05),900)*np.exp(-tt(0.05)*70),s,1.2)
# record scratch
t=tt(0.45); f=900*np.exp(-t*4.2); sc=signal.sawtooth(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.5)
sc=bp(sc+0.6*noise(0.45),400,5000)*np.hstack([np.ones(len(t)-2000),np.linspace(1,0,2000)])
place(sfx,sc,12.93,0.55)
# whoosh
t=tt(0.7); w=noise(0.7); w=bp(w,400,4000)*np.sin(np.pi*t/0.7)**2
place(sfx,w,17.3,0.5)
# meow
t=tt(0.8); f0=np.interp(t,[0,0.15,0.5,0.8],[520,780,560,430])
saw=signal.sawtooth(2*np.pi*np.cumsum(f0)/SR); m=bp(saw,700,1200)+0.8*bp(saw,1800,2800)
m*=adsr(len(t),0.06,0.12,0.7,0.3)
place(sfx,m,16.2,0.55)
# pop sounds
for s in [19.74,21.30,22.92]:
    t=tt(0.12); f=520+500*(t/0.12); p=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*34)
    place(sfx,p,s,0.5)
# chirps in street ambience
for s in [14.2,18.8,25.6,31.2]:
    t=tt(0.09); f=3000+1400*np.sin(np.pi*t/0.09)
    place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.hanning(len(t)),s,0.05)
    place(sfx,np.sin(2*np.pi*np.cumsum(f*1.07)/SR)*np.hanning(len(t)),s+0.12,0.04)
# street ambience
amb=np.zeros(N); a=lp(rng.normal(size=N),420,2)*0.35
for s,d in [(14.3,2.6),(21.0,3.0),(30.5,3.0)]:
    t=tt(d); c=bp(noise(d),150,1200)*np.sin(np.pi*t/d)**2*1.2
    place(a,c,s)
amb=a*np.clip((np.arange(N)/SR-12.93)/0.3,0,1)
amb*=1.0
# end jingle + yawn
for k,(n,s) in enumerate([(72,33.35),(76,33.55),(79,33.75),(84,34.0)]):
    t=tt(0.9); f=midi(n); y=(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*f*4*t)*np.exp(-t*8))*np.exp(-t*4.5)
    place(sfx,y,s,0.28)
t=tt(0.9); f0=np.interp(t,[0,0.3,0.9],[300,380,240]); y=bp(signal.sawtooth(2*np.pi*np.cumsum(f0)/SR)*0.5+noise(0.9)*0.25,500,2200)*adsr(len(t),0.2,0.2,0.6,0.4)
place(sfx,y,33.9,0.18)
# ---- mix
mix=voice*1.0+music*mus_gain+guitar*guit_gain+sfx*0.55+amb*0.10
mix=mix/np.max(np.abs(mix))*0.89
pcm=(mix*32767).astype(np.int16)
with wave.open("audio/mix.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok",len(pcm)/SR,"peak",np.max(np.abs(mix)))
