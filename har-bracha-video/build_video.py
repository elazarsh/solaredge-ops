# -*- coding: utf-8 -*-
"""רינדור מקבילי: python build_video.py <chunk> <nchunks>  ->  seg_<chunk>.mp4"""
import sys,subprocess,os,time
from engine import *
c,n=int(sys.argv[1]),int(sys.argv[2])
total=int(TOTAL*FPS); per=(total+n-1)//n; a,b=c*per,min(total,(c+1)*per)
out=f"{SCR}/seg_{c}.mp4"
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s","1920x1080","-r","30","-i","-","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-g","30","-bf","2",out],stdin=subprocess.PIPE)
t0=time.time()
for fi in range(a,b):
    p.stdin.write(frame_at(fi).tobytes())
    if (fi-a)%90==0: print(f"chunk{c} {fi-a}/{b-a} {time.time()-t0:.0f}s",flush=True)
p.stdin.close(); p.wait(); print("done",c,time.time()-t0)
