import json,subprocess,sys,numpy as np
sys.path.insert(0,".")
from mixlib import *
# ---------------- timeline ----------------
SEGS=[("A",0.2,4.9),("B",5.6,14.3),("W",15.0,15.6),("X",16.5,20.5),("M",22.8,32.8)]
FREEZE=0.7; XF=0.25
CAT_SPEED=0.9; CAT_DUR=4.04/CAT_SPEED
E_SRC=(3.2,8.2); E_SPEED=2.3; E_DUR=(E_SRC[1]-E_SRC[0])/E_SPEED
out0={}; t=0.0
for n,a,b in SEGS: out0[n]=t; t+=b-a
M_END=t+FREEZE
CAT0=M_END-XF; E0=CAT0+CAT_DUR-XF; TOTAL=E0+E_DUR
def O(src):  # map source time of user.mp4 -> out time
    for n,a,b in SEGS:
        if a<=src<=b+0.001: return out0[n]+src-a
    if src>SEGS[-1][2]: return out0["M"]+src-SEGS[-1][1]
    raise ValueError(src)
print("segments out0",out0,"M_END",round(M_END,2),"CAT0",round(CAT0,2),"E0",round(E0,2),"TOTAL",round(TOTAL,2))
# ---------------- voices ----------------
pk=json.load(open("takes/res.json")); pc=json.load(open("takes/res_cat.json"))
pick={k:v["pick"]["take"] for k,v in pk.items()}
pick.update({"k3":pc["k3"]["pick"]["take"],"y2":pc["y2"]["pick"]["take"],"l3":pc["l3"]["pick"]["take"],"c1":pc["c1"]["pick"]["take"]})
CH={"k":("pigeon",1.08),"y":("yossi",1.15),"l":("liat",1.26),"c":("cat",1.12)}
# id: (start_out, max_tempo, fixed_tempo)
CATV0=CAT0+1.1
LINES={
 "k1a":(O(0.5),1.3,None),"l1":(O(4.05),1.0,None),"k1b":(O(5.9),1.1,None),"y1":(O(8.2),1.05,None),
 "k2":(O(10.7),1.0,None),"l2":(O(12.0),1.0,None),"k3":(O(12.6),1.25,None),
 "k4":(O(22.95),1.08,None),"y2":(O(29.45),1.2,None),"l3":(O(31.7),1.25,None),"c1":(CATV0,1.45,None)}
EQ="equalizer=f=1100:t=q:w=1.2:g=3,equalizer=f=3200:t=q:w=1:g=5,equalizer=f=6500:t=q:w=1:g=2.5"
voice=np.zeros(int(TOTAL*SR)+SR); vinfo={}
for lid,(st,mt,ft) in LINES.items():
    src=f"takes/{lid}_{pick[lid]}_t.wav"
    nat=len(readwav(src))/SR
    # window = until next line start or generous
    T=1.0
    win={"k1a":3.4,"l1":0.9,"k1b":1.3,"y1":1.8,"k2":1.3,"l2":0.65,"k3":1.9,"k4":6.4,"y2":2.2,"l3":1.9,"c1":CAT_DUR-1.1-0.15}[lid]
    if nat>win: T=min(mt,nat/win)
    name,pitch=CH[lid[0]]
    dst=f"final/{lid}.wav"
    af=f"highpass=f=90,rubberband=pitch={pitch}:tempo={T}:formant=shifted,{EQ},acompressor=threshold=-22dB:ratio=3:attack=4:release=60,loudnorm=I=-15:TP=-1.5:LRA=6"
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",src,"-af",af,"-ar",str(SR),"-ac","1",dst],check=True)
    w=readwav(dst); place(voice,w,st,1.0)
    vinfo[lid]=dict(start=round(st,2),dur=round(len(w)/SR,2),tempo=round(T,2),nat=round(nat,2))
    print(lid,vinfo[lid])
json.dump(vinfo,open("vinfo.json","w"))
# k4 word timings
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",compute_type="int8")
a=readwav(f"takes/k4_{pick['k4']}_t.wav"); a16=subprocess.run(["ffmpeg","-loglevel","quiet","-i",f"takes/k4_{pick['k4']}_t.wav","-ar","16000","-ac","1","-f","f32le","-"],capture_output=True).stdout
arr=np.frombuffer(a16,dtype=np.float32); segs,_=m.transcribe(arr,language="he",word_timestamps=True)
words=[(w.word.strip(),float(w.start),float(w.end)) for s in segs for w in s.words]
print(words)
T4=vinfo["k4"]["tempo"]; s4=vinfo["k4"]["start"]
def wt(i,which): return s4+words[i][which]/T4
json.dump(dict(words=words),open("k4words.json","w"),ensure_ascii=False)
# find word indices
def find(txt):
    for i,(w,_,_) in enumerate(words):
        if txt in w: return i
    return None
ik=find("קרטונ"); ig=find("גזם"); isq=find("קיות")
print("idx",ik,ig,isq)
tk,tg,tsq=wt(ik,1),wt(ig,1),wt(isq,1)
# ---------------- captions / overlays timing ----------------
def end_of(lid): return vinfo[lid]["start"]+vinfo[lid]["dur"]+0.15
caps=[["k1a",vinfo["k1a"]["start"],end_of("k1a")],["l1",vinfo["l1"]["start"],end_of("l1")],["k1b",vinfo["k1b"]["start"],end_of("k1b")],
 ["y1",vinfo["y1"]["start"],end_of("y1")],["k2",vinfo["k2"]["start"],end_of("k2")],["l2",vinfo["l2"]["start"],end_of("l2")],["k3",vinfo["k3"]["start"],end_of("k3")],
 ["k4a",s4,tk-0.05],["k4b",tk-0.05,tg-0.05],["k4c",tg-0.05,tsq-0.05],["k4d",tsq-0.05,end_of("k4")],
 ["y2",vinfo["y2"]["start"],end_of("y2")],["l3",vinfo["l3"]["start"],end_of("l3")],
 ["n1a",CATV0,CATV0+vinfo["c1"]["dur"]*0.55],["n1b",CATV0+vinfo["c1"]["dur"]*0.55,CATV0+vinfo["c1"]["dur"]+0.3]]
sign=[O(20.0)-0.2,O(22.8)+1.2]
cfg=dict(caps=caps,sign=sign,cards=[[0,tk],[1,tg],[2,tsq]],card_end=end_of("k4")+0.3,segs=SEGS,freeze=FREEZE,xf=XF,cat_speed=CAT_SPEED,e_src=E_SRC,e_speed=E_SPEED,total=TOTAL,out0=out0,cat0=CAT0,e0=E0)
cp=cfg["caps"]
for i in range(len(cp)-1):
    if cp[i][2]>cp[i+1][1]-0.02: cp[i][2]=cp[i+1][1]-0.02
json.dump(cfg,open("timing.json","w"),indent=1)
# ---------------- music & sfx ----------------
N=int(TOTAL*SR)+SR
music=np.zeros(N); beat=60/96
chords=[[50,53,57,60,64],[43,53,59,64],[48,52,55,59,62],[45,52,55,61,64]]; basses=[38,43,36,33]
MUS_END=O(14.3)-0.1   # scratch just before the wall
t0=0.0; bar=0
while t0<MUS_END:
    ch=chords[bar%4]
    for bp_ in [0,1.5,2,3.5]:
        st=t0+bp_*beat+(0.04 if bp_%1 else 0)
        for n in ch: place(music,rhodes(midi(n+12),0.9,0.07),st+rng.uniform(0,0.012))
    for bp_,off in [(0,0),(1,7),(2,0),(3,5)]:
        f=midi(basses[bar%4]+off); d=0.55; place(music,np.sin(2*np.pi*f*tt(d))*np.exp(-tt(d)*4.5),t0+bp_*beat,0.55)
    for h in range(8):
        place(music,hp(rng.normal(size=int(0.05*SR)),6000)*np.exp(-tt(0.05)*60),t0+h*beat/2+(0.035 if h%2 else 0),0.16 if h%2==0 else 0.09)
    t0+=4*beat; bar+=1
music[int(MUS_END*SR):]=0
va=lp(np.abs(voice[:N]),8,1); va=np.clip(va/(np.percentile(va,95)+1e-9),0,1)
guitar=np.zeros(N); GS=O(22.8); GE=CAT0+CAT_DUR*0.6
prog=[[45,52,57,60,64],[41,48,53,57,60]]; step=60/78/2; i=0; tg0=GS
while tg0<GE:
    ch=prog[(i//8)%2]; n=ch[[0,2,3,4,3,2,1,2][i%8]]
    place(guitar,pluck(midi(n),0.8)*0.5,tg0); tg0+=step; i+=1
env=np.clip((np.arange(N)/SR-GS)/0.8,0,1)*np.clip((GE+0.6-np.arange(N)/SR)/0.8,0,1); guitar*=env
sfx=np.zeros(N)
t=tt(0.9); creak=signal.sawtooth(2*np.pi*np.cumsum(110+60*np.sin(2*np.pi*3*t))/SR)*0.3; creak=bp(creak,200,1800)*np.hanning(len(t)); place(sfx,creak,0.0,0.45)
for s in [0.45,0.9,1.35,1.8,2.25,2.7]: place(sfx,lp(noise(0.05),900)*np.exp(-tt(0.05)*70),s,1.0)
t=tt(0.45); f=900*np.exp(-t*4.2); sc=signal.sawtooth(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.5)
sc=bp(sc+0.6*noise(0.45),400,5000)*np.hstack([np.ones(len(t)-2000),np.linspace(1,0,2000)]); place(sfx,sc,MUS_END-0.05,0.55)
t=tt(0.8); w=bp(noise(0.8),400,4000)*np.sin(np.pi*t/0.8)**2; place(sfx,w,O(14.3),0.5)
for s in np.arange(O(16.6),O(19.6),0.34): place(sfx,lp(noise(0.03),1500)*np.exp(-tt(0.03)*90),s,0.35)
tm=tt(0.8); f0=np.interp(tm,[0,0.15,0.5,0.8],[520,780,560,430]); saw=signal.sawtooth(2*np.pi*np.cumsum(f0)/SR)
me=bp(saw,700,1200)+0.8*bp(saw,1800,2800); me*=adsr(len(tm),0.06,0.12,0.7,0.3); place(sfx,me,O(20.2),0.5)
for s in [tk,tg,tsq]:
    t=tt(0.12); f=520+500*(t/0.12); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*34),s-0.02,0.5)
# street ambience under exterior
amb=np.zeros(N); a=lp(rng.normal(size=N),420,2)*0.35
amb=a*np.clip((np.arange(N)/SR-O(15.0))/0.4,0,1)*np.clip((CAT0+CAT_DUR-np.arange(N)/SR)/0.5,0,1)
for s in [O(17.6),O(25.0)+0.0,CAT0+0.8]:
    for k in range(2):
        tc=tt(0.09); f=3000+1400*np.sin(np.pi*tc/0.09); place(sfx,np.sin(2*np.pi*np.cumsum(f*(1+0.07*k))/SR)*np.hanning(len(tc)),s+0.12*k,0.04)
# ending clip audio
ea=subprocess.run(["ffmpeg","-loglevel","quiet","-i","end.mp4","-ss",str(E_SRC[0]),"-t",str(E_SRC[1]-E_SRC[0]),"-af",f"rubberband=tempo={E_SPEED}","-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
ea=np.frombuffer(ea,dtype=np.float32).astype(np.float64); end_a=np.zeros(N); place(end_a,ea,E0,1.0)
mix=voice[:N]*1.0+music*0.30*(1-0.6*va)+guitar*0.22*(1-0.55*va)+sfx*0.55+amb*0.10+end_a*0.45
save(mix[:int(TOTAL*SR)],"mix.wav"); print("mix ok",TOTAL)
