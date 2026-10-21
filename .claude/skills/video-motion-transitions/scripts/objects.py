#!/usr/bin/env python3
"""זיהוי אובייקטים בתמונה (Gemini, תיבות תוחמות) ובניית מסכות למעברי אובייקט (fill/matte/portal/shatter/match).

  python3 objects.py prepare items.json [--obj-dir objcache]
     items.json: [["img/k7.png","the laughing man pointing his finger","mask"], ...]   (תמונה, תווית באנגלית, צורה)
     צורה: mask (grabCut בתוך התיבה, ברירת מחדל) | ellipse | rect (לפתחים כמו דלת/חלון/ילון)
  python3 objects.py boxes img/k7.png "the ark" "the tower"      # הדפסת תיבות בלבד (0-1000: ymin,xmin,ymax,xmax)
הפלט נשמר ב-<obj-dir>/<hash>.npz ונקרא ע"י trans.py לפי (תמונה, תווית, צורה). תוויות: תיאור ויזואלי ספציפי.
תמיד לבדוק ויזואלית את המסכה (matte/shatter על מסכה שגויה נראה רע). דורש GEMINI_API_KEY, numpy, opencv, Pillow.
"""
import base64, concurrent.futures as cf, hashlib, io, json, os, sys, time, urllib.request
import numpy as np, cv2
from PIL import Image

OBJ_DIR = "objcache"


def boxes(img_path, labels):
    key = os.environ.get("GEMINI_API_KEY") or sys.exit("GEMINI_API_KEY לא מוגדר")
    im = Image.open(img_path).convert("RGB"); im.thumbnail((1024, 1024)); buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
    prompt = ("Detect these objects in the drawing and return JSON: a list of {\"label\":..., \"box_2d\":[ymin,xmin,ymax,xmax]} "
              "normalized 0-1000, one entry per label, in the same order. Labels: " + "; ".join(labels))
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}, {"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    for _ in range(4):
        try:
            req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
                                         data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
            d = json.load(urllib.request.urlopen(req, timeout=90))
            return json.loads(d["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:
            print("retry", str(e)[:60], flush=True); time.sleep(8)


def key(img, label):
    return hashlib.md5((img + "|" + label).encode()).hexdigest()[:12]


def mask_from_box(img, box, shape="mask"):
    src = cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB); H, W = src.shape[:2]
    y0, x0, y1, x1 = [v / 1000 for v in box]; X0, Y0, X1, Y1 = int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)
    m = np.zeros((H, W), np.float32)
    if shape == "ellipse":
        cv2.ellipse(m, ((X0 + X1) // 2, (Y0 + Y1) // 2), ((X1 - X0) // 2, (Y1 - Y0) // 2), 0, 0, 360, 1.0, -1, cv2.LINE_AA); return m
    if shape == "rect":
        r = int(min(X1 - X0, Y1 - Y0) * 0.06); cv2.rectangle(m, (X0 + r, Y0), (X1 - r, Y1), 1.0, -1); cv2.rectangle(m, (X0, Y0 + r), (X1, Y1 - r), 1.0, -1)
        for cx, cy in ((X0 + r, Y0 + r), (X1 - r, Y0 + r), (X0 + r, Y1 - r), (X1 - r, Y1 - r)):
            cv2.circle(m, (cx, cy), r, 1.0, -1)
        return cv2.GaussianBlur(m, (0, 0), 3)
    s = 0.5; ss = cv2.resize(src, (int(W * s), int(H * s)), interpolation=cv2.INTER_AREA); h, w = ss.shape[:2]
    mg = int(0.025 * w); rx0 = max(1, int(x0 * w) - mg); ry0 = max(1, int(y0 * h) - mg); rx1 = min(w - 2, int(x1 * w) + mg); ry1 = min(h - 2, int(y1 * h) + mg)
    gm = np.zeros((h, w), np.uint8); bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(ss, gm, (rx0, ry0, rx1 - rx0, ry1 - ry0), bg, fg, 5, cv2.GC_INIT_WITH_RECT); f = ((gm == 1) | (gm == 3)).astype(np.uint8)
    except Exception:
        f = np.zeros((h, w), np.uint8)
    f[:ry0] = 0; f[ry1:] = 0; f[:, :rx0] = 0; f[:, rx1:] = 0
    f = cv2.morphologyEx(f, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); n, lab, st, _ = cv2.connectedComponentsWithStats(f)
    if n > 1:
        keep = np.zeros_like(f)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] > 0.01 * f.size * 0.02 + 200:
                keep[lab == i] = 1
        f = keep
    area = f.sum(); box_area = max(1, (rx1 - rx0) * (ry1 - ry0))
    if area < 0.06 * box_area or area > 0.985 * box_area:  # grabCut נכשל -> אליפסה בתוך התיבה
        f = np.zeros((h, w), np.uint8); cv2.ellipse(f, ((rx0 + rx1) // 2, (ry0 + ry1) // 2), ((rx1 - rx0) // 2, (ry1 - ry0) // 2), 0, 0, 360, 1, -1)
    m = cv2.resize(f.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(m, (0, 0), 2.5)


def get(img, label, shape="mask"):
    """נקרא ע"י trans.py: (mask, box) מהמטמון או None."""
    p = f"{OBJ_DIR}/{key(img, label + shape)}.npz"
    if os.path.exists(p):
        d = np.load(p); return d["mask"], tuple(d["box"])
    print(f"WARNING: אין מסכה ב-{OBJ_DIR} עבור {img!r}/{label!r}/{shape} (הרץ objects.py prepare)", file=sys.stderr)
    return None


def prepare(items):
    os.makedirs(OBJ_DIR, exist_ok=True); byimg = {}
    for img, label, shape in items:
        byimg.setdefault(img, []).append((label, shape))

    def work(img):
        res = boxes(img, [l for l, _ in byimg[img]]) or []
        for (label, shape), r in zip(byimg[img], res):
            box = r["box_2d"]; m = mask_from_box(img, box, shape)
            np.savez_compressed(f"{OBJ_DIR}/{key(img, label + shape)}.npz", mask=m.astype(np.float16), box=np.array(box, np.float32))
        return img, len(res)
    with cf.ThreadPoolExecutor(3) as ex:
        for r in ex.map(work, list(byimg)):
            print("objs", r, flush=True)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "prepare":
        if "--obj-dir" in sys.argv:
            OBJ_DIR = sys.argv[sys.argv.index("--obj-dir") + 1]
        prepare(json.load(open(sys.argv[2], encoding="utf-8")))
    elif len(sys.argv) >= 4 and sys.argv[1] == "boxes":
        print(boxes(sys.argv[2], sys.argv[3:]))
    else:
        print(__doc__)
