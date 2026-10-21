#!/usr/bin/env python3
"""יצירת מוזיקת רקע עם Lyria (lyria-3-pro-preview) דרך generateContent.

יחיד:  python3 lyria.py --prompt "Sparse, intimate score... instrumental only, about 60 seconds" --out mus/m1.mp3
אצווה: python3 lyria.py --plan music.json --outdir mus [--base "בלוק פתיחה משותף"]
  music.json: {"m2": "Uneasy and wry: low cello pulses...", "m3": "..."}   (פרומפט לכל קטע רגשי)
כללי פרומפט: "Instrumental only, no vocals, no drums" + כלים, סולם, BPM, מצב רוח ומה קורה לאורך הקטע. קטע אחד לכל חלק רגשי בסרט.
קבצים קיימים מדולגים; 429/שגיאה -> ניסיון חוזר עם המתנה. דורש GEMINI_API_KEY. יקר יחסית: קודם קטע אחד.
"""
import argparse, base64, json, os, sys, time, urllib.error, urllib.request

def gen(prompt, out, model, key, tries=8):
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["AUDIO"]}}
    for t in range(tries):
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=300))
            for c in d.get("candidates", []):
                for p in c["content"]["parts"]:
                    if "inlineData" in p:
                        mt = p["inlineData"]["mimeType"]; path = out if out.endswith(".wav") == ("wav" in mt) else os.path.splitext(out)[0] + (".mp3" if "mpeg" in mt else ".wav")
                        open(path, "wb").write(base64.b64decode(p["inlineData"]["data"])); return path
            print("no audio in response", str(d)[:150])
        except urllib.error.HTTPError as e:
            print(os.path.basename(out), e.code, e.read().decode()[:100], flush=True); time.sleep(30 * (t + 1))
        except Exception as e:
            print(os.path.basename(out), "exc", str(e)[:80], flush=True); time.sleep(20)
    return None

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt"); ap.add_argument("--out"); ap.add_argument("--plan"); ap.add_argument("--outdir", default="mus")
    ap.add_argument("--base", default=""); ap.add_argument("--model", default="lyria-3-pro-preview"); a = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY") or sys.exit("GEMINI_API_KEY לא מוגדר (ראה ai-api-setup)")
    if a.plan:
        os.makedirs(a.outdir, exist_ok=True)
        for k, v in json.load(open(a.plan, encoding="utf-8")).items():
            out = os.path.join(a.outdir, k + ".mp3")
            if os.path.exists(out): continue
            print(k, gen(a.base + " " + v, out, a.model, key), flush=True)
    elif a.prompt and a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); print(gen(a.prompt, a.out, a.model, key))
    else:
        sys.exit("צריך --prompt ו---out או --plan")
