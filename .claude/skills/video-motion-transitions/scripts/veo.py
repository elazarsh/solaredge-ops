#!/usr/bin/env python3
"""הנפשת תמונה לווידאו (image-to-video) עם Veo, עם תור סבלני ל-429 וגיבוי בין דגמים.

משימה בודדת: python3 veo.py --image img/k1.png --prompt "Slow push-in..." --out veo/k1.mp4 [--last-image img/k2.png]
אצווה:        python3 veo.py --plan shots.json --outdir veo --workers 2
  shots.json: {"k1": {"image": "img/k1.png", "prompt": "...", "last_image": "img/k2.png"(אופציונלי)}, ...}
פרומפט תנועה: מקבל אוטומטית סיומת (--suffix) שמקבעת "מצלמה נייחת" ו"כל אות עברית נשארת בדיוק כמו בתמונה".
429 (מכסה/הוצאה): ממתין 75-105 ש' ומנסה שוב, מתחלף בין --models. --max-attempts 0 = בלי הגבלה.
קבצים קיימים מדולגים. מי שנכשל נרשם ב-<outdir>/pending.json -> להשתמש בגיבוי camera_clip.py ולשדרג כשהמכסה חוזרת.
דגמים: veo-3.1-lite-generate-preview (זול), veo-3.1-fast-generate-preview, veo-3.1-generate-preview (יקר). 8 ש', 1080p.
דורש GEMINI_API_KEY וגם Pillow. קריאות בתשלום: הרץ קודם על תמונה אחת.
"""
import argparse, base64, concurrent.futures as cf, io, json, os, random, sys, time, urllib.error, urllib.request

KEY = os.environ.get("GEMINI_API_KEY")
B = "https://generativelanguage.googleapis.com/v1beta/"
SUFFIX = (" The camera stays still. The composition and every Hebrew letter or word in the drawing stay exactly as in the "
          "image and never change or morph; nothing new is added. Silent.")


def call(url, data=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                               headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    return json.load(urllib.request.urlopen(r, timeout=300))


def enc(path):
    from PIL import Image
    im = Image.open(path).convert("RGB"); im.thumbnail((1920, 1080))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=92)
    return {"bytesBase64Encoded": base64.b64encode(buf.getvalue()).decode(), "mimeType": "image/jpeg"}


def run(k, item, out, models, res, suffix, max_attempts):
    if os.path.exists(out):
        return "exists"
    inst = {"prompt": item["prompt"] + suffix, "image": enc(item["image"])}
    if item.get("last_image"):
        inst["lastFrame"] = enc(item["last_image"])
    body = {"instances": [inst], "parameters": {"aspectRatio": "16:9", "durationSeconds": 8, "resolution": res}}
    attempt = -1
    while True:
        attempt += 1
        if max_attempts and attempt >= max_attempts:
            return "gave-up"
        m = models[attempt % len(models)]
        try:
            op = call(B + f"models/{m}:predictLongRunning", body)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:150].replace("\n", " ")
            print(k, m, "HTTP", e.code, msg[:80], flush=True)
            time.sleep(75 + random.random() * 30 if e.code == 429 else 20)
            continue
        except Exception as e:
            print(k, "EXC", str(e)[:80], flush=True); time.sleep(20); continue
        try:
            while not op.get("done"):
                time.sleep(10); op = call(B + op["name"])
        except Exception as e:
            print(k, "poll EXC", str(e)[:80], flush=True); time.sleep(20); continue
        g = op.get("response", {}).get("generateVideoResponse", {})
        if "error" in op or "generatedSamples" not in g:
            print(k, m, "ERR", json.dumps(op)[:200], flush=True); time.sleep(10); continue
        uri = g["generatedSamples"][0]["video"]["uri"]
        data = urllib.request.urlopen(urllib.request.Request(uri, headers={"x-goog-api-key": KEY}), timeout=300).read()
        open(out, "wb").write(data)
        return "ok " + m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image"); ap.add_argument("--last-image"); ap.add_argument("--prompt"); ap.add_argument("--out")
    ap.add_argument("--plan"); ap.add_argument("--outdir", default="veo"); ap.add_argument("--only", nargs="*")
    ap.add_argument("--models", default="veo-3.1-lite-generate-preview,veo-3.1-fast-generate-preview")
    ap.add_argument("--resolution", default="1080p"); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--suffix", default=SUFFIX); ap.add_argument("--max-attempts", type=int, default=0)
    a = ap.parse_args()
    if not KEY:
        sys.exit("GEMINI_API_KEY לא מוגדר (ראה ai-api-setup)")
    models = a.models.split(",")
    if a.plan:
        plan = json.load(open(a.plan, encoding="utf-8")); os.makedirs(a.outdir, exist_ok=True)
        ks = [k for k in plan if not a.only or k in a.only]
        with cf.ThreadPoolExecutor(a.workers) as ex:
            res = list(ex.map(lambda k: run(k, plan[k], os.path.join(a.outdir, k + ".mp4"), models, a.resolution, a.suffix, a.max_attempts), ks))
        for k, r in zip(ks, res):
            print("RESULT", k, r)
        pend = [k for k, r in zip(ks, res) if r == "gave-up"]
        json.dump(pend, open(os.path.join(a.outdir, "pending.json"), "w"))
    else:
        if not (a.image and a.prompt and a.out):
            sys.exit("צריך --image --prompt --out (או --plan)")
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        print(run("shot", {"image": a.image, "prompt": a.prompt, "last_image": a.last_image}, a.out, models, a.resolution, a.suffix, a.max_attempts))


if __name__ == "__main__":
    main()
