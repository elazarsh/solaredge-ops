import subprocess
IM="/home/user/solaredge-ops/har-bracha-video/pantomime_episode/frames/"
def still(name,img,dur,cx,z0,z1):
    n=int(round(dur*25))
    zp=f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='min(max(iw*{cx}-iw/zoom/2,0),iw-iw/zoom)':y='ih/2-ih/zoom/2':d={n}:s=1620x1080:fps=25"
    fc=(f"[0:v]scale=3240:2160,{zp},split[a][b];"
        "[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=35:3,eq=brightness=-0.05[bg];"
        "[b]format=yuv420p[fg];[bg][fg]overlay=150:0,format=yuv420p[v]")
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",IM+img,"-filter_complex",fc,"-map","[v]","-frames:v",str(n),"-c:v","libx264","-crf","14","-preset","fast",f"seg/{name}.mp4"],check=True)
still("wait2","C_end.png",2.04,0.55,1.0,1.12)
still("sF","F_end.png",1.65,0.22,1.0,1.1)
