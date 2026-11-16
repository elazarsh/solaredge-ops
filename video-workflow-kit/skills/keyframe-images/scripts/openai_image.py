#!/usr/bin/env python3
"""יצירה ועריכה של תמונות עם OpenAI (gpt-image-*) דרך ה-REST API, כולל התאמה ל-16:9.

generate: python3 openai_image.py generate --prompt "..." --out img/k1.png [--model gpt-image-1] [--quality low|medium|high]
edit:     python3 openai_image.py edit --prompt "same character, new pose" --ref img/ref.png [--ref img/ref2.png] --out img/k2.png
  (edit = תמונות ייחוס לעקביות דמות/סגנון; נתמך בנקודת הקצה /v1/images/edits עם image[])
גדלים: gpt-image-1/1.5/2 -> 1024x1024, 1536x1024 (3:2), 1024x1536. דגמי 2.5 (sunburst/flare) מקבלים גם גודל חופשי
  (כפולות של 16, יחס 1:3-3:1), למשל 1536x864 = 16:9 ישירות. לכן: ברירת מחדל --size auto-169:
  2.5 -> 1536x864; אחרת 1536x1024 ואז חיתוך מרכזי ל-16:9 (--fit crop) או הרחבה עם שוליים בצבע פינה (--fit pad).
--aspect-only מדלג על הקריאה: רק ממיר קובץ קיים (--src) ל-16:9 (לבדיקה בלי כסף).
כדי לראות איזה דגם זמין בחשבון: python3 ../../ai-api-setup/scripts/check_env.py --models
מפתח: OPENAI_API_KEY בלבד מהסביבה. אל תריץ הרבה תמונות איכות גבוהה בלי אישור על עלות.
"""
import argparse, base64, io, json, os, sys, uuid, urllib.error, urllib.request

API = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")


def to_169(png, mode):
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB"); w, h = im.size
    if abs(w / h - 16 / 9) < 0.01:
        return im
    if mode == "crop":
        nh = round(w * 9 / 16); top = (h - nh) // 2
        return im.crop((0, top, w, top + nh)) if nh <= h else im
    nw = round(h * 16 / 9); bg = im.getpixel((0, 0))
    out = Image.new("RGB", (max(nw, w), h), bg); out.paste(im, ((out.width - w) // 2, 0)); return out


def multipart(fields, files):
    b = uuid.uuid4().hex; body = b""
    for k, v in fields.items():
        body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for name, fn, data in files:
        body += (f'--{b}\r\nContent-Disposition: form-data; name="{name}"; filename="{fn}"\r\n'
                 f'Content-Type: image/png\r\n\r\n').encode() + data + b"\r\n"
    return body + f"--{b}--\r\n".encode(), f"multipart/form-data; boundary={b}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["generate", "edit"])
    ap.add_argument("--prompt"); ap.add_argument("--out", required=True)
    ap.add_argument("--ref", action="append", default=[]); ap.add_argument("--model", default=os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1"))
    ap.add_argument("--quality", default="medium"); ap.add_argument("--size", default="auto-169")
    ap.add_argument("--fit", choices=["crop", "pad"], default="crop"); ap.add_argument("--aspect-only", metavar="SRC")
    a = ap.parse_args()
    if a.aspect_only:
        to_169(open(a.aspect_only, "rb").read(), a.fit).save(a.out); print("saved", a.out); return
    key = os.environ.get("OPENAI_API_KEY") or sys.exit("OPENAI_API_KEY לא מוגדר (ראה ai-api-setup)")
    if not a.prompt:
        sys.exit("צריך --prompt")
    size = a.size
    if size == "auto-169":
        size = "1536x864" if "2.5" in a.model else "1536x1024"
    try:
        if a.cmd == "generate":
            body = json.dumps({"model": a.model, "prompt": a.prompt, "size": size, "quality": a.quality, "n": 1}).encode()
            req = urllib.request.Request(API + "/images/generations", data=body,
                                         headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        else:
            if not a.ref:
                sys.exit("edit דורש --ref")
            files = [("image[]", os.path.basename(p), open(p, "rb").read()) for p in a.ref]
            body, ct = multipart({"model": a.model, "prompt": a.prompt, "size": size, "quality": a.quality}, files)
            req = urllib.request.Request(API + "/images/edits", data=body, headers={"Authorization": "Bearer " + key, "Content-Type": ct})
        d = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:300]}")
    png = base64.b64decode(d["data"][0]["b64_json"])
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    to_169(png, a.fit).save(a.out); print("saved", a.out, "size", size, "model", a.model)


if __name__ == "__main__":
    main()
