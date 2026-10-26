import subprocess,json
RAW="../raw/"; IM="/home/user/solaredge-ops/har-bracha-video/pantomime_episode/frames/"; FPS=25
C={"c1":"1793053230639","c2":"1793054188760","c3":"1793053828239","c3b":"1793053707069","c4":"1793054018602","c5":"1793054279301","c6":"1793053341954"}
# ("clip",name,key,a,b,speed) / ("still",name,img,dur,cx,z0,z1)
EDL=[("clip","c1","c1",1.4,5.2,1.0),
 ("clip","c2a","c2",0.0,4.85,1.1),
 ("still","Hbag","H_bag.png",1.0,0.4,1.0,1.07),
 ("clip","c2b","c2",4.85,5.9,1.1),
 ("clip","c3a","c3",0.0,1.75,1.0),
 ("still","wait1","A_end.png",1.8,0.6,1.0,1.1),
 ("clip","c3t","c3",2.4,3.95,1.0),
 ("still","wait2","C_end.png",2.0,0.55,1.0,1.12),
 ("clip","c3c","c3b",1.5,4.0,1.15),
 ("clip","steam","c3b",6.0,6.9,1.0),
 ("clip","c4a","c4",0.75,2.5,1.0),
 ("clip","c4b","c4",3.75,5.0,1.0),
 ("clip","c5","c5",0.0,4.4,1.05),
 ("still","G","G_react.png",1.6,0.62,1.0,1.12),
 ("clip","c6","c6",2.5,4.04,1.0)]
def mk_clip(n,key,a,b,sp):
    nf=int(round((b-a)/sp*FPS))
    fc=(f"[0:v]trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{sp},fps={FPS},split[a][b];"
        "[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=35:3,eq=brightness=-0.05[bg];"
        "[b]scale=1620:1080[fg];[bg][fg]overlay=150:0,format=yuv420p[v]")
    subprocess.run(["ffmpeg","-v","error","-y","-i",RAW+C[key]+".mp4","-filter_complex",fc,"-map","[v]","-frames:v",str(nf),"-c:v","libx264","-crf","14","-preset","fast",f"seg2/{n}.mp4"],check=True); return nf/FPS
def mk_still(n,img,dur,cx,z0,z1):
    nf=int(round(dur*FPS))
    zp=f"zoompan=z='{z0}+({z1}-{z0})*on/{nf}':x='min(max(iw*{cx}-iw/zoom/2,0),iw-iw/zoom)':y='ih/2-ih/zoom/2':d={nf}:s=1620x1080:fps={FPS}"
    fc=(f"[0:v]scale=3240:2160,{zp},split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=35:3,eq=brightness=-0.05[bg];"
        "[b]format=yuv420p[fg];[bg][fg]overlay=150:0,format=yuv420p[v]")
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",IM+img,"-filter_complex",fc,"-map","[v]","-frames:v",str(nf),"-c:v","libx264","-crf","14","-preset","fast",f"seg2/{n}.mp4"],check=True); return nf/FPS
t=0; tl={}
for it in EDL:
    d=mk_clip(it[1],*it[2:]) if it[0]=="clip" else mk_still(it[1],*it[2:])
    tl[it[1]]=dict(start=round(t,3),dur=d); t+=d
tl["_total"]=round(t,3)
json.dump(tl,open("tl.json","w"),indent=1); print(tl)
open("list2.txt","w").write("".join(f"file 'seg2/{it[1]}.mp4'\n" for it in EDL))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-i","list2.txt","-c","copy","base2.mp4"],check=True)
