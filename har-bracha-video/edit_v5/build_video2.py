import json,subprocess,sys
cfg=json.load(open("timing.json"))
SRC="../user_video/user.mp4"; segs=cfg["segs"]; XF=cfg["xf"]
fc=[]; names=[]
for i,(n,a,b,sp,fz) in enumerate(segs):
    f=f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps=30"
    if i==len(segs)-1: fz=cfg["freeze"]
    if fz: f+=f",tpad=stop_mode=clone:stop_duration={fz}"
    fc.append(f+f"[s{i}]"); names.append(f"[s{i}]")
fc.append("".join(names)+f"concat=n={len(segs)}:v=1:a=0,fps=30,settb=1/30[v1]")
cs=cfg["cat_speed"]
fc.append(f"[1:v]setpts=(PTS-STARTPTS)/{cs},fps=30,scale=1620:1080,tpad=stop_mode=clone:stop_duration={cfg['cat_freeze']},settb=1/30[c]")
es,ee=cfg["e_src"]
fc.append(f"[2:v]trim={es}:{ee},setpts=(PTS-STARTPTS)/{cfg['e_speed']},fps=30,scale=-2:1080,crop=1620:1080,settb=1/30[e]")
M_END=sum((b-a)/sp+fz for _,a,b,sp,fz in segs)+cfg["freeze"]
fc.append(f"[v1][c]xfade=transition=fade:duration={XF}:offset={M_END-XF:.3f}[vc]")
fc.append(f"[vc][e]xfade=transition=fade:duration={XF}:offset={cfg['e0']:.3f}[vx]")
inputs=["-i",SRC,"-i","cat.mp4","-i","end.mp4"]; last="vx"; n=3
SL0=cfg["slogan"][0]
def add(png,start,end,x,y,w=None,fin=0.12,fout=0.12):
    global last,n
    inputs.extend(["-loop","1","-framerate","30","-t","40","-i",png])
    sc=f",scale={w}:-1" if w else ""
    fc.append(f"[{n}:v]format=rgba{sc},fade=t=in:st={start:.3f}:d={fin}:alpha=1,fade=t=out:st={max(start+0.1,end-fout):.3f}:d={fout}:alpha=1[o{n}]")
    fc.append(f"[{last}][o{n}]overlay=x={x}:y={y}:eof_action=pass[l{n}]"); last=f"l{n}"; n+=1
mode=sys.argv[1]; out=sys.argv[2]
if mode=="subs":
    for cid,s,e in cfg["caps"]: add(f"ov/cap_{cid}.png",s,e,0,870)
if mode in("subs","clean"):
    s,e=cfg["sign"]; add("ov/sign.png",s,e,160,50)
    for idx,s in cfg["cards"]: add(f"ov/card{idx+1}.png",s,cfg["card_end"],660+idx*320,25,w=300)
inputs.extend(["-framerate","30","-i","slogan_frames/f%03d.png"])
fc.append(f"[{n}:v]format=rgba,setpts=PTS+{SL0}/TB[slg]")
fc.append(f"[{last}][slg]overlay=x=0:y=0:eof_action=pass[ls]"); last="ls"; n+=1
fc.append(f"[{last}]format=yuv420p[vout]")
subprocess.run(["ffmpeg","-loglevel","error","-y",*inputs,"-filter_complex",";".join(fc),"-map","[vout]","-an","-c:v","libx264","-preset","medium","-crf","19","-r","30",out],check=True)
print(out)
