import json,subprocess,numpy as np,scipy.io.wavfile as w,scipy.signal as sg,os
SR=48000
TL=json.load(open('tmp/timeline.json'));paras=TL['paras'];segs=TL['segs'];END=TL['total']+0.5;N=int(END*SR)
rng=np.random.default_rng(5);tt=np.arange(N)/SR
def lp(x,f,o=2):b,a=sg.butter(o,f/(SR/2),'low');return sg.lfilter(b,a,x)
def hp(x,f,o=2):b,a=sg.butter(o,f/(SR/2),'high');return sg.lfilter(b,a,x)
def bp(x,f1,f2,o=2):b,a=sg.butter(o,[f1/(SR/2),f2/(SR/2)],'band');return sg.lfilter(b,a,x)
def IR(sec,decay,dark):
    n=int(sec*SR);x=rng.standard_normal(n)*np.exp(-np.arange(n)/SR*decay);x=lp(x,dark);x[:int(0.006*SR)]*=0;return x/np.abs(x).sum()*3.2
IR_S=IR(0.7,6,3500);IR_L=IR(3.2,1.8,1800)
def rev(x,I,wet):return (1-wet)*np.pad(x,(0,len(I)))[:len(x)]+wet*sg.fftconvolve(x,I)[:len(x)]
def put(buf,x,t0,g=1.0,pan=0.0):
    i=int(t0*SR);j=min(len(buf),i+len(x))
    if j<=i or i<0:return
    x=x[:j-i]*g;buf[i:j,0]+=x*np.sqrt((1-pan)/2);buf[i:j,1]+=x*np.sqrt((1+pan)/2)
def rd(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
# voice
V=np.zeros((N,2));vact=np.zeros(N)
for q in paras:
    sr,a=w.read(f'vo/p{q["par"]:02d}.wav');a=a.astype(np.float64)/32768
    if a.ndim>1:a=a[:,0]
    a=sg.resample_poly(a,SR//sr,1) if SR%sr==0 else sg.resample(a,int(len(a)*SR/sr))
    a=hp(a,75,2);a=a+0.35*lp(a,260,2);a*=0.1/np.sqrt(np.mean(a**2));a=np.tanh(a*5)/5;a=rev(a,IR_S,0.10)
    f=int(0.02*SR);a[:f]*=np.linspace(0,1,f);a[-f:]*=np.linspace(1,0,f)
    put(V,a,q['vo']);i=int(q['vo']*SR);vact[i:i+len(a)]=1
vact=np.clip(lp(vact,2.5,1),0,1)
# music by section
SEC=[(1,3,'m1'),(4,5,'m2'),(6,6,'m3'),(7,10,'m4'),(11,12,'m5'),(13,16,'m6'),(17,19,'m7'),(20,21,'m8'),(22,22,'m9')]
M=np.zeros((N,2));P={q['par']:q for q in paras}
def loopto(x,n,xf=int(4*SR)):
    out=x.copy()
    while len(out)<n:
        fade=np.linspace(0,1,xf)[:,None];out=np.concatenate([out[:-xf],out[-xf:]*(1-fade)+x[:xf]*fade,x[xf:]])
    return out[:n]
for a,b,k in SEC:
    t0=max(0,P[a]['t0']-1.0);t1=(P[b]['end']+ (6.0 if b==22 else 1.0));n=int((t1-t0)*SR)
    path=f'mus/{k}.mp3'
    if not os.path.exists(path):path='mus/m1.mp3'
    x=rd(path);x*=0.10/np.sqrt(np.mean(x**2))*0.55;x=loopto(x,n)
    fi=int(2.5*SR);fo=int(2.5*SR);x[:fi]*=np.linspace(0,1,fi)[:,None];x[-fo:]*=np.linspace(1,0,fo)[:,None]
    i=int(t0*SR);j=min(N,i+len(x));M[i:j]+=x[:j-i]
M*=(1-0.6*vact)[:,None]
S=np.zeros((N,2))
def env(a,b,fi,fo):return np.clip((tt-a)/fi,0,1)*np.clip((b-tt)/fo,0,1)
def burst(d,f1,f2,dec):n=int(d*SR);return bp(rng.standard_normal(n),f1,f2)*np.exp(-np.arange(n)/SR*dec)
def whoosh(t0,d,g=0.03):
    n=int(d*SR);x=bp(rng.standard_normal(n),250,2200)*np.hanning(n);put(S,rev(x,IR_L,0.2),t0,g)
wind=bp(rng.standard_normal(N),180,900)*(0.5+0.5*np.sin(2*np.pi*0.07*tt))*0.02;S[:,0]+=wind;S[:,1]+=np.roll(wind,700)
def tone(f0,f1,d,dec=3.0):
    n=int(d*SR);ph=np.cumsum(np.linspace(f0,f1,n))/SR*2*np.pi;return np.sin(ph)*np.exp(-np.arange(n)/SR*dec)
def swell(d,lo,hi):
    n=int(d*SR);return bp(rng.standard_normal(n),lo,hi)*np.sin(np.linspace(0,np.pi,n))**2
def sfx(kind,t,g=1.0):
    if kind=='whip':put(S,rev(swell(0.7,300,4000),IR_S,0.2),t-0.35,0.05*g)
    elif kind=='smash':
        n=int(0.8*SR);x=np.sin(2*np.pi*48*np.arange(n)/SR)*np.exp(-np.arange(n)/SR*9)+0.6*burst(0.8,200,3500,16)[:n];put(S,rev(x,IR_L,0.3),t-0.15,0.32*g)
    elif kind=='tear':
        n=int(1.0*SR);x=bp(rng.standard_normal(n),1200,7000)*(0.5+0.5*np.sign(np.sin(np.linspace(0,60,n))))*np.hanning(n)+0.4*bp(rng.standard_normal(n),150,600)*np.hanning(n);put(S,rev(x,IR_S,0.2),t-0.5,0.06*g)
    elif kind=='burn':
        for i in range(120):put(S,burst(0.03,1200,8000,110),t-1.5+rng.uniform(0,3.2),rng.uniform(0.01,0.035),rng.uniform(-0.8,0.8))
        put(S,rev(swell(3.0,60,500),IR_L,0.3),t-1.6,0.06*g)
    elif kind=='water':
        put(S,rev(swell(3.2,150,2500),IR_L,0.3),t-1.7,0.06*g)
        for i in range(10):put(S,rev(tone(rng.uniform(800,1500),rng.uniform(300,600),0.15,25),IR_L,0.5),t-1.2+rng.uniform(0,2.6),0.012)
    elif kind=='ripple':
        for i,dt in enumerate((0,0.55,1.1)):put(S,rev(tone(900-i*150,420-i*60,0.4,9),IR_L,0.55),t-0.6+dt,0.045*g)
    elif kind=='ink':
        put(S,rev(np.sin(2*np.pi*55*np.arange(int(1.2*SR))/SR)*np.exp(-np.arange(int(1.2*SR))/SR*4),IR_L,0.4),t-1.4,0.18*g)
        put(S,rev(swell(2.4,100,900),IR_L,0.3),t-1.3,0.04*g)
    elif kind=='erase':
        n=int(2.6*SR);x=bp(rng.standard_normal(n),1800,6500)*(0.55+0.45*np.sin(np.linspace(0,2*np.pi*9,n)))*np.hanning(n);put(S,x,t-1.4,0.03*g)
    elif kind=='peel':
        n=int(1.6*SR);x=bp(rng.standard_normal(n),2500,9000)*np.linspace(0.2,1,n)*np.exp(-np.linspace(0,3,n));put(S,rev(x,IR_S,0.2),t-0.6,0.05*g)
    elif kind=='wipe':put(S,rev(swell(1.6,200,2500),IR_S,0.2),t-0.8,0.04*g)
    elif kind=='iris':
        put(S,rev(tone(220,440,1.6,1.5),IR_L,0.5),t-0.9,0.03*g);put(S,swell(1.8,800,5000),t-1.0,0.02*g)
    elif kind=='zoomthrough':
        put(S,rev(swell(1.7,200,3500),IR_S,0.2),t-1.0,0.055*g);put(S,rev(tone(180,700,1.6,2.2),IR_L,0.3),t-1.0,0.025*g)
    elif kind=='washout':
        put(S,rev(swell(2.2,400,3000),IR_L,0.4),t-1.2,0.04*g);put(S,rev(tone(880,880,1.8,2.0),IR_L,0.6),t-0.8,0.025*g)
    elif kind=='goldbloom':
        for f in (1200,1800,2400):put(S,rev(tone(f,f,2.0,2.2)*(0.6+0.4*np.sin(np.linspace(0,14,int(2.0*SR)))),IR_L,0.6),t-1.0,0.012)
    elif kind=='colordrain':put(S,rev(tone(660,330,2.4,1.4),IR_L,0.6),t-1.2,0.03*g)
    elif kind=='colorseep':put(S,rev(tone(330,660,2.4,1.4),IR_L,0.6),t-1.2,0.03*g)
    elif kind=='dipblack':put(S,rev(swell(2.6,60,400),IR_L,0.4),t-1.3,0.05*g)
    elif kind in('dissolve','defocus'):put(S,rev(swell(2.2,300,2500),IR_L,0.4),t-1.1,0.025*g)
    elif kind=='fill':
        put(S,rev(swell(3.0,60,700),IR_L,0.3),t-1.6,0.07*g);put(S,rev(swell(1.6,300,3000),IR_S,0.2),t-0.2,0.04*g)
    elif kind=='matte':put(S,rev(swell(2.6,200,3500),IR_L,0.3),t-1.4,0.05*g);put(S,rev(tone(300,600,2.0,1.2),IR_L,0.5),t-1.2,0.02*g)
    elif kind=='portal':put(S,rev(swell(2.8,150,3000),IR_L,0.35),t-1.5,0.06*g);put(S,rev(tone(160,520,2.4,1.0),IR_L,0.4),t-1.4,0.03*g)
    elif kind=='shatter':
        n=int(0.5*SR);put(S,rev(burst(0.5,300,6000,10),IR_S,0.3),t-1.3,0.18*g)
        for i in range(26):put(S,rev(tone(rng.uniform(1500,4200),rng.uniform(900,2500),0.08,45),IR_L,0.4),t-1.0+rng.uniform(0,2.2),rng.uniform(0.01,0.03))
    elif kind=='match':
        put(S,rev(tone(520,520,2.6,1.3),IR_L,0.6),t-1.3,0.025*g);put(S,rev(tone(780,780,2.6,1.3),IR_L,0.6),t-1.1,0.018*g)
    elif kind=='smoke':whoosh(t-1.2,2.6,0.045)
for s in segs:
    k=s.get('trans','smoke')
    if k=='real':whoosh(s['t0']+s['dur']*0.30,min(2.4,s['dur']*0.4),0.028)
    else:sfx(k,s['t0']+4.0/s['speed'])
for s in segs:
    if s.get('trans')=='dipblack':
        tc=s['t0']+4.0/s['speed'];M[int(max(0,tc-0.4)*SR):int((tc+0.5)*SR)]*=0.35
def seg_of(key):return [s for s in segs if s['key']==key][0]
def arrive(k):  # time a keyframe is reached
    for s in segs:
        if s['key'].endswith('_'+k) or (k=='K4' and s['key']=='C') : return s['t0']+s['dur']
    return None
# flood rumble K13->K16
a=seg_of('K13_K14');b=seg_of('K15_K16')
rum=lp(rng.standard_normal(N),95,4)*env(a['t0']+a['dur']*0.5,b['t0']+b['dur'],3.0,3.0)*0.5;S[:,0]+=rum;S[:,1]+=np.roll(rum,100)
# door slam at K39 arrival, tear drip at K29, closing door at K16
def thump(t,g=0.35):
    n=int(1.2*SR);x=np.sin(2*np.pi*55*np.arange(n)/SR)*np.exp(-np.arange(n)/SR*7)+0.5*burst(1.2,150,900,14)[:n];put(S,rev(x,IR_L,0.35),t,g)
for k,g in (('K39',0.4),('K16',0.35),('K24',0.25)):
    t=arrive(k)
    if t:thump(t-0.9,g)
t=arrive('K29')
if t:
    n=int(0.35*SR);x=np.sin(2*np.pi*np.linspace(900,350,n).cumsum()/SR)*np.exp(-np.arange(n)/SR*18);put(S,rev(x,IR_L,0.5),t-1.8,0.08)
# charcoal writing on plank (E4) and hammer (D, K6_K7)
e=seg_of('E4_lite');sc=bp(rng.standard_normal(N),1800,7500)*(0.55+0.45*np.sin(2*np.pi*3.1*tt))*env(e['t0']+e['dur']*0.5,e['t0']+e['dur']*0.98,0.5,0.6)*0.02;S[:,0]+=sc;S[:,1]+=np.roll(sc,60)
d=seg_of('D');tcur=d['t0']+d['dur']*0.55
while tcur<d['t0']+d['dur']:
    x=burst(0.35,260,1500,40)+0.7*np.sin(2*np.pi*150*np.arange(int(0.35*SR))/SR)*np.exp(-np.arange(int(0.35*SR))/SR*32);put(S,rev(x,IR_L,0.45),tcur,0.05,-0.25);tcur+=rng.uniform(0.85,1.05)
S*=(1-0.35*vact)[:,None]
Mx=V+M+S;Mx=np.tanh(Mx*1.2)/1.2
Mx*=np.clip(tt/0.5,0,1)[:,None]*np.clip((END-tt)/2.0,0,1)[:,None]
Mx/=np.abs(Mx).max();Mx*=0.9
w.write('out/mix_full.wav',SR,(Mx*32767).astype(np.int16));print('mix ok',END)
