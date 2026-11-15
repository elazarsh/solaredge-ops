#!/usr/bin/env python3
"""בדיקת איכות טכנית לסרטון סופי: אורך, סנכרון קול/וידאו, גודל, פריימים שחורים, עוצמה, ופלט תקין לפני מסירה.

  python3 check_video.py film.mp4 [--expect-dur 540] [--max-mb 30] [--wpm-text narr.md]
מדפיס שורת OK/WARN/FAIL לכל בדיקה; קוד יציאה 1 אם יש FAIL. לא מחליף צפייה בגיליון מגע ובתמלול (ראה SKILL.md).
"""
import argparse, json, os, re, subprocess, sys

def run(*c): return subprocess.run(c, capture_output=True, text=True)
ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--expect-dur", type=float); ap.add_argument("--max-mb", type=float)
ap.add_argument("--wpm-text"); a = ap.parse_args()
bad = 0
def rep(level, msg):
    global bad; bad += level == "FAIL"; print(f"{level:4} {msg}")
info = json.loads(run("ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,duration:format=duration,size", "-of", "json", a.video).stdout or "{}")
if not info: sys.exit("FAIL לא ניתן לקרוא את הקובץ")
st = {s["codec_type"]: s for s in info["streams"]}; fdur = float(info["format"]["duration"]); mb = int(info["format"]["size"]) / 2**20
rep("OK", f"אורך {fdur:.1f}s, גודל {mb:.1f}MB, וידאו {st['video']['width']}x{st['video']['height']} {st['video']['r_frame_rate']}")
if "audio" not in st: rep("FAIL", "אין ערוץ קול")
else:
    dv, da = float(st["video"].get("duration", fdur)), float(st["audio"].get("duration", fdur))
    rep("OK" if abs(dv - da) < 0.5 else "FAIL", f"סנכרון אורך וידאו {dv:.2f}s / קול {da:.2f}s")
if a.expect_dur: rep("OK" if abs(fdur - a.expect_dur) <= max(2, a.expect_dur * .02) else "WARN", f"אורך צפוי {a.expect_dur}s, בפועל {fdur:.1f}s")
if a.max_mb: rep("OK" if mb <= a.max_mb else "FAIL", f"גודל {mb:.1f}MB (מקסימום {a.max_mb}MB) -> פצל עם split.sh" if mb > a.max_mb else f"גודל מתחת ל-{a.max_mb}MB")
bl = run("ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-vf", "blackdetect=d=0.5:pix_th=0.05", "-an", "-f", "null", "-").stderr
segs = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bl)
rep("OK" if not segs else "WARN", "פריימים שחורים: " + (", ".join(f"{s}-{e}" for s, e in segs) if segs else "אין") + (" (מכוון? dipblack/פתיחה)" if segs else ""))
if "audio" in st:
    ls = run("ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-af", "ebur128", "-vn", "-f", "null", "-").stderr
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", ls[ls.rfind("Summary"):] if "Summary" in ls else ls)
    if m: rep("OK" if -17 <= float(m.group(1)) <= -12 else "WARN", f"עוצמה משולבת {m.group(1)} LUFS (יעד ~ -14)")
    vd = run("ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-af", "volumedetect", "-vn", "-f", "null", "-").stderr
    mv = re.search(r"max_volume: (-?[\d.]+) dB", vd)
    if mv and float(mv.group(1)) > -0.1: rep("WARN", "קליפינג בקול (max_volume 0dB)")
if a.wpm_text:
    words = len(re.sub(r"[֑-ׇ]", "", open(a.wpm_text, encoding="utf-8").read()).split())
    rep("OK", f"{words} מילים ב-{fdur:.0f}s = {words / fdur * 60:.0f} מילים/דקה כולל שתיקות (הקראה עצמה ~120-130)")
sys.exit(1 if bad else 0)
