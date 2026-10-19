import numpy as np, subprocess, wave, json
from scipy import signal
SR=44100
rng=np.random.default_rng(11)
def tt(d): return np.arange(int(SR*d))/SR
def lp(x,f,o=2): b,a=signal.butter(o,f/(SR/2),"low"); return signal.lfilter(b,a,x)
def hp(x,f,o=2): b,a=signal.butter(o,f/(SR/2),"high"); return signal.lfilter(b,a,x)
def bp(x,f1,f2,o=2): b,a=signal.butter(o,[f1/(SR/2),f2/(SR/2)],"band"); return signal.lfilter(b,a,x)
def midi(m): return 440*2**((m-69)/12)
def noise(d): return rng.normal(size=int(d*SR))
def place(buf,x,start,gain=1.0):
    i=int(start*SR); j=min(len(buf),i+len(x))
    if 0<=i<len(buf): buf[i:j]+=x[:j-i]*gain
def readwav(path):
    raw=subprocess.run(["ffmpeg","-loglevel","quiet","-i",path,"-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.float32).astype(np.float64)
def adsr(n,a=0.005,d=0.1,s=0.5,r=0.2):
    e=np.ones(n); na=int(a*SR); nd=int(d*SR); nr=int(r*SR)
    e[:na]=np.linspace(0,1,na,endpoint=False)
    if na+nd<=n: e[na:na+nd]=np.linspace(1,s,nd)
    e[na+nd:n-nr]=s; e[n-nr:]=np.linspace(s,0,nr); return e
def rhodes(f,d,vel=0.5):
    t=tt(d); y=np.sin(2*np.pi*f*t+0.8*np.exp(-t*6)*np.sin(2*np.pi*f*t))*np.exp(-t*3.2)
    y+=0.25*np.sin(2*np.pi*f*2*t)*np.exp(-t*5); return y*vel
def pluck(f,d):
    n=int(SR/f); buf=rng.uniform(-1,1,n); out=np.zeros(int(SR*d))
    for i in range(len(out)):
        out[i]=buf[i%n]; buf[i%n]=0.5*(buf[i%n]+buf[(i+1)%n])*0.996
    return out
def save(mix,path):
    mix=mix/np.max(np.abs(mix))*0.89
    with wave.open(path,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
