#!/usr/bin/env python3
"""יצירת תמונות מפתח עם Gemini (gemini-3-pro-image), עם נעילת סגנון, תמונות ייחוס ובדיקת טקסט עברי.

פרומפט סופי = בלוק סגנון קבוע (--style קובץ/טקסט) + תיאור הסצנה. 16:9, 2K.
אם יש --must/--forbid: אחרי כל יצירה מודל ראייה קורא את המילים שבתמונה; מנסה שוב עד --tries ושומר את הטובה ביותר.
כל ניסיון נשמר כ-<out>_try<i>.png (לא הולך לאיבוד).

יחיד:  python3 gemini_image.py --style style.txt --prompt "A mother holds a baby..." --out img/k1.png [--ref img/ref.png] [--must נח] [--forbid נוח]
אצווה: python3 gemini_image.py --style style.txt --plan plan.json --outdir img --workers 3 [--only k1 k2]
  plan.json: {"k1": {"prompt": "...", "must": ["נח"], "forbid": ["נוח"], "refs": ["img/ref.png"]}, ...}
קריאת טקסט מתמונה קיימת: python3 gemini_image.py --read img/k1.png
ברירת מחדל: "no text" מתווסף לפרומפט אלא אם יש must (כתובת רצויה). דורש GEMINI_API_KEY.
"""
import argparse, base64, concurrent.futures as cf, json, os, re, sys, time, urllib.request, urllib.error

KEY = os.environ.get("GEMINI_API_KEY")
B = "https://generativelanguage.googleapis.com/v1beta/models/"
NOTEXT = " Absolutely no text, no letters, no words anywhere in the image."


def _post(model, body, timeout):
    req = urllib.request.Request(B + model + ":generateContent", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def _b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()


def call_img(prompt, refs=(), model="gemini-3-pro-image", size="2K"):
    parts = [{"inlineData": {"mimeType": "image/png" if p.endswith(".png") else "image/jpeg", "data": _b64(p)}} for p in refs]
    parts.append({"text": prompt})
    d = _post(model, {"contents": [{"parts": parts}], "generationConfig": {
        "responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9", "imageSize": size}}}, 400)
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("no image in response: " + str(d)[:200])


def read_words(png_bytes):
    q = ("List ALL Hebrew words and any digits that are hand-lettered in this drawing, separated by commas. "
         "Write each word exactly as spelled (letter by letter), no niqqud, no explanation. If there is no text, write NONE.")
    d = _post("gemini-3.8-flash", {"contents": [{"parts": [
        {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(png_bytes).decode()}}, {"text": q}]}],
        "generationConfig": {"temperature": 0}}, 120)
    t = d["candidates"][0]["content"]["parts"][0]["text"]
    return [w.strip() for w in re.split(r"[,\n]", re.sub(r"[^א-ת0-9, \n]", "", t)) if w.strip()]


def make(name, out, prompt, refs=(), must=(), forbid=(), tries=5):
    best, bests = None, -99
    for i in range(tries):
        try:
            png = call_img(prompt, refs)
        except Exception as e:
            print(name, i, "ERR", str(e)[:120], flush=True)
            time.sleep(15 * (i + 1))
            continue
        open(f"{os.path.splitext(out)[0]}_try{i}.png", "wb").write(png)
        if not (must or forbid):
            open(out, "wb").write(png); print(name, "ok", flush=True); return "ok"
        try:
            got = read_words(png)
        except Exception:
            got = []
        j = " ".join(got)
        score = sum(1 for m in must if m in j) - 10 * sum(1 for f in forbid if f in j.split())
        print(name, i, got[:12], "OK" if score == len(must) else f"retry {score}/{len(must)}", flush=True)
        if score > bests:
            best, bests = png, score
        if score == len(must):
            break
    if best is None:
        return "FAIL"
    open(out, "wb").write(best)
    return "ok" if bests == len(must) else f"weak {bests}/{len(must)} (לתקן ידנית או כתובת ב-HTML)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--style", default="", help="טקסט או נתיב לקובץ עם בלוק הסגנון הקבוע")
    ap.add_argument("--prompt"); ap.add_argument("--out"); ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--must", nargs="*", default=[]); ap.add_argument("--forbid", nargs="*", default=[])
    ap.add_argument("--plan"); ap.add_argument("--outdir", default="img"); ap.add_argument("--only", nargs="*")
    ap.add_argument("--tries", type=int, default=5); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--read"); a = ap.parse_args()
    if not KEY:
        sys.exit("GEMINI_API_KEY לא מוגדר (ראה ai-api-setup)")
    if a.read:
        print(read_words(open(a.read, "rb").read())); return
    style = open(a.style, encoding="utf-8").read().strip() if a.style and os.path.exists(a.style) else a.style

    def full(p, must):
        return (style + "\n\nScene: " + p + ("" if must else NOTEXT)).strip()

    if a.plan:
        plan = json.load(open(a.plan, encoding="utf-8")); os.makedirs(a.outdir, exist_ok=True)
        ids = [k for k in plan if not a.only or k in a.only]

        def one(k):
            out = os.path.join(a.outdir, k + ".png")
            if os.path.exists(out):
                return k, "exists"
            it = plan[k]
            return k, make(k, out, full(it["prompt"], it.get("must")), it.get("refs", a.ref), it.get("must", ()), it.get("forbid", ()), a.tries)
        with cf.ThreadPoolExecutor(a.workers) as ex:
            for k, r in ex.map(one, ids):
                print("RESULT", k, r)
    else:
        if not (a.prompt and a.out):
            sys.exit("צריך --prompt ו---out (או --plan)")
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        print(make(os.path.basename(a.out), a.out, full(a.prompt, a.must), a.ref, a.must, a.forbid, a.tries))


if __name__ == "__main__":
    main()
