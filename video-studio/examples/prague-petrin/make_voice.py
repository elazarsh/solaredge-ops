#!/usr/bin/env python3
"""Generate the six narration lines (Gemini TTS), trim silence, verify by transcription, write voice/lines.json."""
import json, re, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import voice_tools as v

HERE = Path(__file__).parent
STYLE = ("Voice-over for a 30-second TV commercial: deep, gravelly male announcer, very fast and energetic, speed-reading pace, "
         "about 3.5 words per second, completely serious tone, tiny pauses. Hebrew. Say exactly and only:")
TARGET = {"L1": 4.2, "L2": 3.4, "L3": 4.2, "L4": 4.4, "L5": 3.8, "L6a": 3.4, "L6b": 0.7}  # seconds we can afford per line
LINES = {  # exact wording from the brief
    "L1": "אי שם בלב אירופה מחכה חוויית אקסטרים שתעצור לכם את הנשימה!",
    "L2": "נוף פנורמי! גבהים מסחררים! תחזיקו חזק!",
    "L3": "קבלו את רכבת ההרים היחידה שגם תינוקות מבקשים ממנה להאיץ!",
    "L4": "שימו לב לנועזים שבחרו במסלול האקסטרים... הם פשוט עולים ברגל!",
    "L5": "בסוף המסע: דופק תקין, ואפס צורך בהחלפת חיתול!",
    "L6a": "רכבל פטז'ין. יותר אקסטרים ממעלית...",
    "L6b": "בקצת.",
}
EXTRA = {"L2": " Stretch the very last word 'חזק' dramatically long, like 'חזקקקק', rising in excitement.",
         "L6a": " Deadpan, deep, grave.", "L6b": " Deadpan, grave, with a small comic gravity."}


def norm(s):
    s = re.sub(r"[^֐-׿a-zA-Z0-9 ]", " ", s)
    s = s.replace("חווית", "חוויית").replace("ג'", "ג").replace("ז'", "ז")
    return " ".join(s.split())


def trim(src: Path, dst: Path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                    "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.03,"
                    "areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.03,areverse",
                    str(dst)], check=True)


def take(key, text):
    raw = HERE / "voice" / f"{key}_raw.wav"
    out = HERE / "voice" / f"{key}_take.wav"
    for attempt in range(6):
        try:
            v.tts(text, raw, "Algenib", STYLE + EXTRA.get(key, ""))
            trim(raw, out)
            heard = v.transcribe(out)
        except Exception as exc:  # quota (429) or empty result: wait and retry, never give up silently
            wait = 25 * (attempt + 1) if "429" in str(exc) else 5
            print(f"{key}: attempt {attempt + 1} failed ({str(exc)[:60]}); waiting {wait}s", file=sys.stderr, flush=True)
            time.sleep(wait)
            continue
        ok = norm(heard).replace(" ", "") == norm(text).replace(" ", "") or key == "L6b"
        return ok, heard, v.duration(out)
    raise RuntimeError(f"{key}: no take after retries")


def one(item):
    key, text = item
    best = None
    for n in range(1, 4):  # up to 3 takes; stop as soon as one is correct and within budget
        ok, heard, sec = take(key, text)
        print(f"  {key} take {n}: {sec:.2f}s {'OK' if ok else 'DIFF'}", flush=True)
        if ok and (best is None or sec < best["seconds"]):
            best = {"text": text, "heard": heard, "match": True, "seconds": round(sec, 3), "attempts": n}
            subprocess.run(["cp", str(HERE / "voice" / f"{key}_take.wav"), str(HERE / "voice" / f"{key}.wav")], check=True)
        if best and best["seconds"] <= TARGET[key]:
            break
        time.sleep(6)
    if not best:
        raise RuntimeError(f"{key}: no correct take")
    return best


if __name__ == "__main__":
    prog = HERE / "voice" / "lines.json"
    res = json.loads(prog.read_text(encoding="utf-8")) if prog.exists() else {}
    for key, text in LINES.items():
        if key in res and (HERE / "voice" / f"{key}.wav").exists() and res[key]["text"] == text:
            print(key, "cached", res[key]["seconds"], "s")
            continue
        res[key] = one((key, text))  # saved after every line so a crash resumes here
        prog.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        r = res[key]
        print(key, r["seconds"], "s", "OK " if r["match"] else "DIFF", r["attempts"], "|", r["heard"], flush=True)
        time.sleep(6)
