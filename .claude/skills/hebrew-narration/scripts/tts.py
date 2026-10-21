#!/usr/bin/env python3
"""הפקת קריינות עברית עם Gemini TTS (gemini-3.8-flash-tts, קול Sulafat כברירת מחדל).

קלט: קובץ md (פסקאות מופרדות בשורה ריקה -> p01, p02...) או JSON {"מפתח": "טקסט מנוקד"}.
פלט: <outdir>/<key>.wav ו-durs.json (אורך בשניות לכל קובץ). קבצים קיימים מדולגים (חידוש אחרי כשל).
דורש GEMINI_API_KEY במשתנה סביבה. 429 -> המתנה וניסיון חוזר. ברירת מחדל: 3 במקביל.

דוגמאות:
  python3 tts.py narr.md --outdir vo
  python3 tts.py narr.json --outdir vo --only s03 s04 --force     # תיקון פסקה בודדת
  python3 tts.py narr.md --outdir vo --wpm 135 --dry-run          # בלי קריאה לרשת
"""
import argparse, base64, concurrent.futures as cf, json, os, sys, time, urllib.error, urllib.request, wave

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
STYLE = ("Hebrew storyteller narration, warm and engaging, unhurried but flowing, about {wpm} words per minute, "
         "natural breaths at commas and full stops, clear natural Israeli Hebrew pronunciation.{extra}")
END_SOFT = " Slightly softer and slower on the very last words of each paragraph."


def load_items(path):
    txt = open(path, encoding="utf-8").read()
    if path.endswith(".json"):
        return json.loads(txt)
    paras = [p.strip() for p in txt.split("\n\n") if p.strip()]
    return {f"p{i:02d}": p for i, p in enumerate(paras, 1)}


def wav_dur(path):
    with wave.open(path) as w:
        return round(w.getnframes() / w.getframerate(), 2)


def tts(text, style, voice, out, key, retries):
    body = {"model": "gemini-3.8-flash-tts",
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
                       "annotations": [{"type": "speech_metadata", "style": style}]}]}],
            "response_format": {"type": "audio", "mime_type": "audio/wav"},
            "generation_config": {"speech_config": [{"voice": voice}]}, "store": False}
    for t in range(retries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "x-goog-api-key": key})
            d = json.load(urllib.request.urlopen(req, timeout=240))
            a = [p for s in d["steps"] if s["type"] == "model_output" for p in s["content"] if p["type"] == "audio"][0]
            open(out, "wb").write(base64.b64decode(a["data"]))
            return wav_dur(out)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:120].replace("\n", " ")
            wait = (20 if e.code == 429 else 8) * (t + 1)
            print(f"{os.path.basename(out)} HTTP {e.code} {msg} -> retry in {wait}s", flush=True)
            time.sleep(wait)
        except Exception as e:  # רשת / תגובה לא צפויה
            print(f"{os.path.basename(out)} err {str(e)[:80]}", flush=True)
            time.sleep(8 * (t + 1))
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--outdir", default="vo")
    ap.add_argument("--voice", default="Sulafat")
    ap.add_argument("--wpm", type=int, default=135, help="הנחיית קצב בסגנון (בפועל המודל נותן ~10-15%% פחות)")
    ap.add_argument("--style", help="סגנון מלא באנגלית (דורס את ברירת המחדל)")
    ap.add_argument("--soft-end", action="store_true", help="האטה ורכות בסוף כל פסקה")
    ap.add_argument("--only", nargs="*", help="להפיק רק מפתחות אלה")
    ap.add_argument("--force", action="store_true", help="להפיק מחדש גם אם הקובץ קיים")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--retries", type=int, default=10)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    items = load_items(a.input)
    keys = [k for k in items if not a.only or k in a.only]
    style = a.style or STYLE.format(wpm=a.wpm, extra=END_SOFT if a.soft_end else "")
    words = {k: len(__import__("re").sub(r"[֑-ׇ]", "", items[k]).split()) for k in keys}
    if a.dry_run:
        print("style:", style)
        for k in keys:
            print(k, words[k], "words")
        return
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY לא מוגדר (ראה ai-api-setup)")
    os.makedirs(a.outdir, exist_ok=True)

    def one(k):
        out = os.path.join(a.outdir, f"{k}.wav")
        if os.path.exists(out) and not a.force:
            return k, wav_dur(out)
        d = tts(items[k], style, a.voice, out, key, a.retries)
        print(k, "ok" if d else "FAILED", d, flush=True)
        return k, d

    with cf.ThreadPoolExecutor(a.workers) as ex:
        res = dict(ex.map(one, keys))
    dp = os.path.join(a.outdir, "durs.json")
    old = json.load(open(dp)) if os.path.exists(dp) else {}
    old.update({k: v for k, v in res.items() if v})
    json.dump(old, open(dp, "w"))
    tot_w = sum(words[k] for k in keys if res.get(k))
    tot_d = sum(res[k] for k in keys if res.get(k))
    if tot_d:
        print(f"words {tot_w} dur {tot_d:.1f}s -> {tot_w / tot_d * 60:.0f} wpm (בפועל)")
    bad = [k for k in keys if not res.get(k)]
    if bad:
        sys.exit(f"נכשלו: {bad}")


if __name__ == "__main__":
    main()
