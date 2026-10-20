import json,subprocess,numpy as np,sys
vinfo=json.load(open("vinfo.json")); VID=sys.argv[1] if len(sys.argv)>1 else "v5_clean.mp4"
# id: (x0,y0,x1,y1) mouth search region in output frame
REG={"k1a":(450,100,1150,430),"k1b":(380,120,900,520),"y1":(50,450,760,880),"k2":(760,330,1500,720),"k3":(760,330,1500,720),
     "k4":(150,250,800,640),"y2a":(800,350,1350,680),"y2b":(800,350,1350,680),"l3":(1100,420,1500,700),"c1":(1000,0,1620,520)}
FPS=30
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
    for s in np.arange(0.88,1.16,0.02):
        for d in np.arange(-0.9,0.91,1/30):
            # audio frame k at time st+d+k/FPS*s
            tt=st+d+np.arange(len(e))/FPS*s
            idx=np.round((tt-t0)*FPS).astype(int); ok=(idx>=0)&(idx<len(m))
            if ok.sum()<len(e)*0.9: continue
            ee=sm(e[ok]); mm=m[idx[ok]]
            sc=np.corrcoef(ee,mm)[0,1]
            if abs(d)<1e-6 and abs(s-1.0)<1e-6: base=sc
            if sc>best[0]: best=(sc,d,s)
    if base is None:
        tt=st+np.arange(len(e))/FPS; idx=np.round((tt-t0)*FPS).astype(int); ok=(idx>=0)&(idx<len(m)); base=np.corrcoef(sm(e[ok]),m[idx[ok]])[0,1]
    res[lid]=dict(base=round(float(base),3),best=round(float(best[0]),3),shift=round(float(best[1]),3),stretch=round(float(best[2]),3))
    print(lid,res[lid],flush=True)
json.dump(res,open("lipsync.json","w"),indent=1)
