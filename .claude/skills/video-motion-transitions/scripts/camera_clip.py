#!/usr/bin/env python3
"""גיבוי כשאין Veo: קליפ תנועת מצלמה (זום/פאן) מתמונה אחת עם ffmpeg.

python3 camera_clip.py img/k1.png out.mp4 [--kind 0|1|2|3] [--seconds 8] [--ease-start] [--ease-end]
kind: 0=זום פנימה איטי, 1=פאן ימינה, 2=זום החוצה, 3=פאן שמאלה. ease = האטה לאפס בקצה כדי להתחבר לפריים נקי.
חשוב (באג שהיה): zoompan בלי הגבלה יצר סרטון של 32 דקות. כאן הקלט הוא תמונה אחת + trim=end_frame + -frames:v.
"""
import argparse, subprocess, sys

def cam(kind, s0, n, ease_s, ease_e, fps=24):
    s = f"({s0}+on/{fps})"
    es = f"min(1,on/{fps*1.2})" if ease_s else "1"
    ee = f"min(1,({n}-on)/{fps*1.2})" if ease_e else "1"
    w = f"(({es})*({ee}))"; w = f"({w}*{w}*(3-2*{w}))"
    if kind == 0: zr, px, py = f"(1.03+0.012*{s})", "0.5", "0.5"
    elif kind == 1: zr, px, py = "1.14", f"(0.1+0.08*({s}+1))", "0.4"
    elif kind == 2: zr, px, py = f"(1.15-0.012*{s})", "0.5", "0.5"
    else: zr, px, py = "1.14", f"(0.9-0.08*({s}+1))", "0.6"
    z = f"1+({zr}-1)*{w}"
    return z, f"(iw-iw/zoom)*(0.5+({px}-0.5)*{w})", f"(ih-ih/zoom)*(0.5+({py}-0.5)*{w})"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image"); ap.add_argument("out"); ap.add_argument("--kind", type=int, default=0)
    ap.add_argument("--seconds", type=float, default=8); ap.add_argument("--start", type=float, default=0, help="נקודת התחלה בציר התנועה (לחיבור רציף)")
    ap.add_argument("--ease-start", action="store_true"); ap.add_argument("--ease-end", action="store_true")
    a = ap.parse_args(); n = int(a.seconds * 24)
    z, x, y = cam(a.kind % 4, a.start, n, a.ease_start, a.ease_end)
    vf = (f"scale=2400:1350,zoompan=z='{z}':x='{x}':y='{y}':d={n}:s=1920x1080:fps=24,"
          f"trim=end_frame={n},setpts=PTS-STARTPTS,format=yuv420p")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.image, "-vf", vf, "-frames:v", str(n),
                        "-c:v", "libx264", "-crf", "17", "-preset", "fast", a.out], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-600:])
    print("saved", a.out, f"{a.seconds}s")

main()
