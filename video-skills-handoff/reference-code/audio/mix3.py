import json,subprocess,numpy as np,scipy.io.wavfile as w,scipy.signal as sg
SR=48000;LEAD=0.6
D=json.load(open('v3/durations.json'));OFF=np.concatenate([[0],np.cumsum(D)])[:-1];END=float(sum(D));N=int((END+0.5)*SR)
C=json.load(open('v3/cues.json'))['cues'];CU=[C[f's{i:02d}'] for i in range(1,17)]
q=lambda i,n:OFF[i]+LEAD+CU[i][n]
rng=np.random.default_rng(9);tt=np.arange(N)/SR
def lp(x,f,o=2):b,a=sg.butter(o,f/(SR/2),'low');return sg.lfilter(b,a,x)
def hp(x,f,o=2):b,a=sg.butter(o,f/(SR/2),'high');return sg.lfilter(b,a,x)
def bp(x,f1,f2,o=2):b,a=sg.butter(o,[f1/(SR/2),f2/(SR/2)],'band');return sg.lfilter(b,a,x)
def IR(sec,decay,dark):
    n=int(sec*SR);x=rng.standard_normal(n)*np.exp(-np.arange(n)/SR*decay);x=lp(x,dark);x[:int(0.006*SR)]*=0;return x/np.abs(x).sum()*3.2
IR_S=IR(0.5,7,4000);IR_L=IR(2.4,2.0,2500)
def rev(x,I,wet):return (1-wet)*np.pad(x,(0,len(I)))[:len(x)]+wet*sg.fftconvolve(x,I)[:len(x)]
def put(buf,x,t0,g=1.0,pan=0.0):
    i=int(t0*SR);j=min(len(buf),i+len(x))
    if j<=i or i<0:return
    x=x[:j-i]*g;buf[i:j,0]+=x*np.sqrt((1-pan)/2);buf[i:j,1]+=x*np.sqrt((1+pan)/2)
V=np.zeros((N,2));vact=np.zeros(N)
for i in range(16):
    sr,a=w.read(f'v3/vo/s{i+1:02d}.wav');a=a.astype(np.float64)/32768
    if a.ndim>1:a=a[:,0]
    a=sg.resample_poly(a,SR//sr,1) if SR%sr==0 else sg.resample(a,int(len(a)*SR/sr))
    a=hp(a,70,2);a=a+0.3*lp(a,250,2);a*=0.11/np.sqrt(np.mean(a**2));a=np.tanh(a*4)/4;a=rev(a,IR_S,0.07)
    f=int(0.02*SR);a[:f]*=np.linspace(0,1,f);a[-f:]*=np.linspace(1,0,f)
    t0=OFF[i]+LEAD;put(V,a,t0);k=int(t0*SR);vact[k:k+len(a)]=1
vact=np.clip(lp(vact,2.5,1),0,1)
def rd(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
def loopto(x,n,xf=int(4*SR)):
    out=x.copy()
    while len(out)<n:
        fade=np.linspace(0,1,xf)[:,None];out=np.concatenate([out[:-xf],out[-xf:]*(1-fade)+x[:xf]*fade,x[xf:]])
    return out[:n]
M=np.zeros((N,2))
for a_,b_,k in [(0,7,'ea'),(7,13,'eb'),(13,16,'ec')]:
    t0=OFF[a_]-0.5 if a_ else 0;t1=(OFF[b_] if b_<16 else END)+0.5;n=int((t1-t0)*SR)
    x=rd(f'mus/{k}.mp3');x*=0.10/np.sqrt(np.mean(x**2))*0.7;x=loopto(x,n)
    fi=int(2.0*SR);fo=int(2.0*SR);x[:fi]*=np.linspace(0,1,fi)[:,None];x[-fo:]*=np.linspace(1,0,fo)[:,None]
    i=int(t0*SR);j=min(N,i+len(x));M[i:j]+=x[:j-i]
M*=(1-0.55*vact)[:,None]
S=np.zeros((N,2))
def burst(d,f1,f2,dec):n=int(d*SR);return bp(rng.standard_normal(n),f1,f2)*np.exp(-np.arange(n)/SR*dec)
def swell(d,lo,hi):n=int(d*SR);return bp(rng.standard_normal(n),lo,hi)*np.sin(np.linspace(0,np.pi,n))**2
def tone(f0,f1,d,dec=3.0):n=int(d*SR);ph=np.cumsum(np.linspace(f0,f1,n))/SR*2*np.pi;return np.sin(ph)*np.exp(-np.arange(n)/SR*dec)
def click(t,g=0.03):put(S,rev(burst(0.03,2500,9000,120),IR_S,0.2),t,g,rng.uniform(-.4,.4))
def ping(t,f=1320,g=0.045):put(S,rev(tone(f,f,0.9,4),IR_L,0.5),t,g,rng.uniform(-.5,.5))
def whoosh(t,g=0.06,d=0.9):put(S,rev(swell(d,300,5000),IR_S,0.25),t,g)
for i in range(16):whoosh(OFF[i]-0.1)
# S01 legend cards
for n in ('legend1','legend2','legend3'):put(S,rev(tone(500,900,0.3,10),IR_S,0.3),q(0,n),0.05)
# S02
for k in range(6):put(S,rev(burst(0.12,300,2500,40),IR_S,0.3),q(1,'desk')+.5+k*.35,0.08)
# S03 (Claude vs Claude Code)
for k in range(22):click(q(2,'ask')+k*0.06,0.025)
for k in range(30):click(q(2,'ans')+k*0.05,0.02)
put(S,rev(np.sin(2*np.pi*55*np.arange(int(0.9*SR))/SR)*np.exp(-np.arange(int(0.9*SR))/SR*9)+0.5*burst(0.9,200,4000,14)[:int(0.9*SR)],IR_L,0.4),q(2,'cannot'),0.22)
put(S,rev(swell(0.8,300,4000),IR_S,0.25),q(2,'menu'),0.05)
click(q(2,'area')+.9,0.08);ping(q(2,'area')+1.0,1480,0.06)
for k,n in enumerate(('p1','p2','p3','p4')):ping(q(2,n),[880,1100,1320,1560][k],0.05)
for k in range(7):ping(q(2,'long')+k*.35,[660,740,830,880,990,1100,1245][k],0.035)
for k in range(5):put(S,rev(burst(0.12,300,2500,40),IR_S,0.3),q(2,'files')-.1+k*.25,0.07)
for n in ('chatuse','ask2','write','build','files2','code'):click(q(2,n),0.05)
# S04 cards, typing
for k in range(6):click(q(3,'card')+k*.15,0.04)
for k in range(24):click(q(3,'typed')+k*0.07,0.028)
put(S,rev(tone(520,880,0.5,3),IR_L,0.4),q(3,'created'),0.06)
# S04 hands + key
for k,n in enumerate(('h1','h2','h3','h4','h5')):ping(q(4,n),[880,1100,1320,990,1175][k],0.05)
for k in range(24):click(q(4,'settings')+.2+k*0.06,0.02)
put(S,rev(tone(180,90,0.5,6),IR_L,0.5),q(4,'no'),0.12)
# S05 spawns
for k,n in enumerate(('copy','task')):put(S,rev(tone(400,900,0.35,6),IR_S,0.3),q(5,n),0.06)
for k in range(3):ping(q(5,'report')+k*.4,1100+k*150,0.04)
# S06 alarm
for k in range(6):put(S,rev(tone(1000,1000,0.18,18),IR_S,0.3),q(6,'stop')+k*.3,0.05)
put(S,rev(burst(0.6,150,1500,8),IR_L,0.4),q(6,'stop'),0.14)
# S07 steps
for k in range(8):ping(q(7,'st'+str(k+1)),[660,740,830,880,990,1100,1245,1320][k],0.045)
for n in ('h1','h2','h3','h4'):put(S,rev(burst(0.12,300,2500,40),IR_S,0.3),q(7,n),0.07)
# S08 quotes + stamp
for k in range(3):put(S,rev(burst(0.1,400,3500,40),IR_S,0.3),q(8,'quote')+k*1.5,0.08)
put(S,rev(np.sin(2*np.pi*55*np.arange(int(1.0*SR))/SR)*np.exp(-np.arange(int(1.0*SR))/SR*8)+0.6*burst(1.0,200,4000,14)[:int(1.0*SR)],IR_L,0.4),q(8,'stamp'),0.3)
# S09 scan, err
put(S,rev(swell(1.6,800,6000),IR_S,0.2),q(9,'err')-1.4,0.05)
ping(q(9,'letter'),1560,0.06)
# S10 transitions
for n in ('anim','fire','water','door','smoke'):put(S,rev(swell(1.4,200,4500),IR_L,0.3),q(10,n),0.06)
# S11 word swap
ping(q(11,'steps'),1560,0.06)
for k in range(3):click(q(11,['steps','regen','rebuild'][k]),0.05)
# S12
for n in ('len','size','sync','frames'):click(q(12,n),0.05)
# S13 styles
for n in ('t1','t2','t3'):put(S,rev(swell(1.5,200,5000),IR_L,0.3),q(13,n)-.3,0.07)
put(S,rev(np.sin(2*np.pi*60*np.arange(int(0.8*SR))/SR)*np.exp(-np.arange(int(0.8*SR))/SR*10),IR_L,0.4),q(13,'t1'),0.2)
# S14 typing + send
for k in range(100):click(q(14,'write')+k*0.115,0.02)
put(S,rev(tone(500,1200,0.4,4),IR_L,0.4),q(14,'stamp'),0.07)
for k in range(4):ping(q(14,'secret')+k*.5,1320,0.04)
# S15
put(S,rev(swell(3.0,100,3000),IR_L,0.4),q(15,'what')-.2,0.1)
for k,f in enumerate((880,1320,1760)):ping(q(15,'what')+.2+k*.2,f,0.07)
S*=(1-0.4*vact)[:,None]
Mx=V+M+S;Mx=np.tanh(Mx*1.2)/1.2
Mx*=np.clip(tt/0.4,0,1)[:,None]*np.clip((END+0.5-tt)/2.0,0,1)[:,None]
Mx/=np.abs(Mx).max();Mx*=0.9
w.write('out/mix3.wav',SR,(Mx*32767).astype(np.int16));print('mix ok',END)
