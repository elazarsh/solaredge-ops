#!/usr/bin/env python3
"""הרכבת סרט מקליפים לפי חלונות פסקאות הקריינות, עם התאמת מהירות, אימות אורך ומטמון בטוח.

שימוש: python3 assemble.py plan.json
plan.json:
{ "out": "out/body.mp4", "timeline": "out/timeline.json", "workdir": "tmp",
  "lead": 0.35, "tail": 1.4, "min_speed": 0.8, "max_speed": 1.3, "hold_last": 7.5,
  "paragraphs": [ {"id": "p01", "dur": 12.3, "clips": [{"file": "veo/a.mp4", "ss": 0, "to": 8}, "veo/b.mp4"]}, ... ] }
לכל פסקה: חלון = lead + אורך הקריינות + tail. מהירות = (סך אורך המקורות)/(חלון), חסומה ל-[min_speed,max_speed]; אם נשאר פער
המרווח נחלק לשני הצדדים (lead גדל). פלט: body.mp4 (24fps, 1920x1080) ו-timeline.json עם voice_t לכל פסקה (להזנת mix.json).
כללים שנלמדו בדם:
 * מפתח המטמון = קובץ מקור + ss/to + מהירות; קליפ ביניים נבדק באורך (ffprobe) ואם קצר מהצפוי ->tmp/stale ונוצר מחדש.
   (קליפ חלקי של 2.7 ש' במקום 5 קיצר סרט שלם.)
 * "החזקה" בסוף: תמונה אחת + -frames:v. אין zoompan בלי הגבלה (יצר סרטון של 32 דקות).
 * קליפ חסר או שבור: הסקריפט נעצר עם שם הקובץ, לא ממשיך בשקט.
"""
import hashlib, json, os, shutil, subprocess, sys

FMT = "scale=1920:1080:flags=lanczos,fps=24,format=yuv420p"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit("ffmpeg failed: " + " ".join(cmd[:6]) + "\n" + r.stderr[-600:])

def main(p):
    wd = p.get("workdir", "tmp"); os.makedirs(wd, exist_ok=True); os.makedirs(os.path.join(wd, "stale"), exist_ok=True)
    lead0, tail = p.get("lead", .35), p.get("tail", 1.4); lo, hi = p.get("min_speed", .8), p.get("max_speed", 1.3)
    t = 0.0; names = []; tl = []
    for par in p["paragraphs"]:
        clips = [c if isinstance(c, dict) else {"file": c} for c in par["clips"]]
        for c in clips:
            if not os.path.exists(c["file"]): sys.exit("חסר קליפ: " + c["file"])
            c.setdefault("ss", 0); c.setdefault("to", min(8.0, dur(c["file"])))
        src = sum(c["to"] - c["ss"] for c in clips); D = par["dur"]
        sp = min(hi, max(lo, src / (D + lead0 + tail))); win = src / sp
        lead = lead0 + max(0, win - D - lead0 - tail) / 2
        start = t
        for c in clips:
            d = (c["to"] - c["ss"]) / sp
            key = hashlib.md5(f'{c["file"]}|{c["ss"]}|{c["to"]}|{sp:.4f}'.encode()).hexdigest()[:10]
            out = os.path.join(wd, f"{os.path.basename(c['file'])[:-4]}_{key}.mp4")
            if os.path.exists(out) and abs(dur(out) - d) > 0.15:
                shutil.move(out, os.path.join(wd, "stale", os.path.basename(out))); print("stale ->", out)
            if not os.path.exists(out):
                sh(["ffmpeg", "-v", "error", "-y", "-ss", str(c["ss"]), "-t", str(c["to"] - c["ss"]), "-i", c["file"],
                    "-vf", f"setpts=(PTS-STARTPTS)/{sp:.4f},{FMT}", "-an", "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-r", "24", out])
            got = dur(out)
            if abs(got - d) > 0.3: sys.exit(f"אורך קליפ שגוי: {out} {got:.2f}s במקום {d:.2f}s")
            names.append(os.path.basename(out)); t += d
        tl.append({"id": par["id"], "t0": round(start, 2), "voice_t": round(start + lead, 2), "dur": par["dur"], "end": round(t, 2), "speed": round(sp, 3)})
    if p.get("hold_last"):
        last = p["paragraphs"][-1]["clips"][-1]; last = last["file"] if isinstance(last, dict) else last
        hold = os.path.join(wd, "hold.mp4"); n = int(p["hold_last"] * 24)
        sh(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", last, "-frames:v", "1", os.path.join(wd, "hold.png")])
        sh(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", os.path.join(wd, "hold.png"), "-vf", "scale=2112:1188,zoompan=z='1+0.0008*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=1920x1080:fps=24,format=yuv420p" % n,
            "-frames:v", str(n), "-c:v", "libx264", "-crf", "17", hold])
        names.append("hold.mp4"); t += p["hold_last"]
    lst = os.path.join(wd, "list.txt"); open(lst, "w").write("".join(f"file '{n}'\n" for n in names))
    os.makedirs(os.path.dirname(p["out"]) or ".", exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", p["out"]])
    json.dump({"total": round(t, 2), "paragraphs": tl}, open(p.get("timeline", "timeline.json"), "w"), indent=1)
    print("body", p["out"], round(dur(p["out"]), 2), "s (planned", round(t, 2), ")")
    if abs(dur(p["out"]) - t) > 0.5: sys.exit("אורך הסרט לא תואם את התוכנית: יש קליפ חלקי/שבור")

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(json.load(open(sys.argv[1], encoding="utf-8")))
