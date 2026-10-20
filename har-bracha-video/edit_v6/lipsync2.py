import json,subprocess,numpy as np,sys
vinfo=json.load(open("vinfo.json")); VID=sys.argv[1] if len(sys.argv)>1 else "v5_clean.mp4"
# id: (x0,y0,x1,y1) mouth search region in output frame
REG={"k1a":(450,100,1150,430),"k1b":(380,120,900,520),"y1":(50,450,760,880),"k2":(760,330,1500,720),"k3":(760,330,1500,720),
     "k4":(150,250,800,640),"y2a":(800,350,1350,680),"y2b":(800,350,1350,680),"l3":(1100,420,1500,700),"c1":(1000,0,1620,520)}
FPS=30
# id: (start_lo,start_hi,end_max)
CON={"k1a":(0.2,1.0,4.85),"k1b":(6.0,6.6,7.4),"y1":(7.2,8.6,9.9),"k2":(9.8,10.4,11.3),"k3":(11.9,12.6,14.5),
     "k4":(26.45,27.4,33.0),"y2a":(32.9,33.6,35.2),"l3":(35.1,36.0,37.15),"y2b":(37.2,37.9,39.3),"c1":(40.4,41.0,45.9)}
def mouth_signal(t0,t1,reg):
    x0,y0,x1,y1=reg; w=(x1-x0)//2*2; h=(y1-y0)//2*2
    cmd=["ffmpeg","-loglevel","error","-ss",f"{t0:.3f}","-t",f"{t1-t0:.3f}","-i",VID,"-vf",f"fps={FPS},crop={w}:{h}:{x0}:{y0}","-f","rawvideo","-pix_fmt","rgb24","-"]
    raw=subprocess.run(cmd,capture_output=True).stdout
    n=len(raw)//(w*h*3); a=np.frombuffer(raw[:n*w*h*3],dtype=np.uint8).reshape(n,h,w,3).astype(int)
    R,G,B=a[...,0],a[...,1],a[...,2]
    dark=((R-G)>=30)&(G<70)&(B<70)&(R<150)
    tongue=(R>185)&(G<115)&(B<115)
    m=(dark|tongue).reshape(n,-1).mean(axis=1)
    return m
def env(path):
    raw=subprocess.run(["ffmpeg","-loglevel","quiet","-i",path,"-ar","16000","-ac","1","-f","f32le","-"],capture_output=True).stdout
    a=np.frombuffer(raw,dtype=np.float32); hop=16000//FPS
    n=len(a)//hop; e=np.sqrt((a[:n*hop].reshape(n,hop)**2).mean(axis=1)); return e/(e.max()+1e-9)
def sm(x,k=3): return np.convolve(x,np.ones(k)/k,mode="same")
res={}
for lid,reg in REG.items():
    st=vinfo[lid]["start"]; dur=vinfo[lid]["dur"]; PAD=1.0
    t0=max(0,st-PAD); t1=st+dur+PAD
    m=sm(mouth_signal(t0,t1,reg)); 
    if len(m)<5 or m.max()<1e-4: print(lid,"no mouth signal"); continue
    m=(m-m.mean())/(m.std()+1e-9)
    e=env(f"final/{lid}.wav"); ts_m=t0+np.arange(len(m))/FPS
    best=(-9,0,1); base=None
    lo,hi,emax=CON[lid]
    for s in np.arange(0.88,1.121,0.02):
        for st2 in np.arange(lo,hi+1e-6,1/30):
            if st2+dur*s>emax+1e-6: continue
            d=st2-st
            tt=st2+np.arange(len(e))/FPS*s
            idx=np.round((tt-t0)*FPS).astype(int); ok=(idx>=0)&(idx<len(m))
            if ok.sum()<len(e)*0.9: continue
            sc=np.corrcoef(sm(e[ok]),m[idx[ok]])[0,1]
            if sc>best[0]: best=(sc,d,s)
    tt=st+np.arange(len(e))/FPS; idx=np.round((tt-t0)*FPS).astype(int); ok=(idx>=0)&(idx<len(m)); base=np.corrcoef(sm(e[ok]),m[idx[ok]])[0,1]
    res[lid]=dict(base=round(float(base),3),best=round(float(best[0]),3),shift=round(float(best[1]),3),stretch=round(float(best[2]),3))
    print(lid,res[lid],flush=True)
json.dump(res,open("lipsync2.json","w"),indent=1)
