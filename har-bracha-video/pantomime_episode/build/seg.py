import subprocess,json,os
RAW="../raw/"
FPS=25
# (name, src file, start, end, speed)
SEGS=[("s1","1793053230639",0.3,5.9,1.1),
      ("s2","1793053250478",0.0,6.04,1.15),
      ("s3","1793053828239",0.0,4.04,1.0),
      ("s4a","1793053707069",0.5,4.2,1.2),("s4b","1793053707069",5.9,7.04,1.0),
      ("s5","1793054018602",0.4,6.0,1.05),
      ("s6","1793054279301",0.0,6.04,1.1),
      ("s7","1793053341954",2.4,4.04,1.0,0.8)]
os.makedirs("seg",exist_ok=True); info=[]; t=0
for sg in SEGS:
    n,f,a,b,sp=sg[:5]; hold=sg[5] if len(sg)>5 else 0
    d=(b-a)/sp+hold; nf=int(round(d*FPS)); d=nf/FPS
    fc=(f"[0:v]trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{sp},fps={FPS},tpad=stop_mode=clone:stop_duration={hold},split[a][b];"
        "[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=35:3,eq=brightness=-0.05[bg];"
        "[b]scale=1620:1080[fg];[bg][fg]overlay=150:0,format=yuv420p[v]")
    subprocess.run(["ffmpeg","-v","error","-y","-i",RAW+f+".mp4","-filter_complex",fc,"-map","[v]","-frames:v",str(nf),"-c:v","libx264","-crf","14","-preset","fast",f"seg/{n}.mp4"],check=True)
    info.append(dict(name=n,src=f,a=a,b=b,speed=sp,start=round(t,3),dur=d)); t+=d
json.dump(info,open("seg.json","w"),indent=1); print(info, "total",t)
