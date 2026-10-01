# Assemble the realistic shots into one 30fps footage track (video + native foley audio).
import subprocess, sys, json
EDL = json.load(open("edl.json"))
segs = []
for i, s in enumerate(EDL):
    src, a, b, speed, hold = s["src"], s["in"], s["out"], s.get("speed", 1.0), s.get("hold", 0)
    out = f"seg/{i:02d}.mp4"
    dur = (b - a) / speed
    vf = f"trim={a}:{b},setpts=(PTS-STARTPTS)/{speed},fps=30,scale=1080:1920"
    af = f"atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={speed},aresample=48000"
    if hold:
        vf += f",tpad=stop_mode=clone:stop_duration={hold}"
        af += f",apad=pad_dur={hold}"
    total = dur + hold
    subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-vf",vf,"-af",af,"-t",f"{total:.3f}",
                    "-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",out],check=True)
    segs.append(out); print(out, round(total,3))
open("seg/list.txt","w").write("".join(f"file '{p.split('/')[1]}'\n" for p in segs))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","seg/list.txt","-c","copy","footage.mp4"],check=True)
print(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","footage.mp4"],capture_output=True,text=True).stdout)
