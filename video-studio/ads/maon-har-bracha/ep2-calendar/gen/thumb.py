# Thumb activity over a tracked screen: how much of the screen quad is covered (not green) and how fast that changes.
# usage: thumb.py clip   → prints per-0.125 s: covered %, motion
import sys, json, cv2, numpy as np
c = sys.argv[1]; cap = cv2.VideoCapture(f"clips/{c}.mp4"); fps = cap.get(5)
Q = json.load(open(f"clips/{c}.json"))["quads"]; prev = None; rows = []
for i in range(len(Q)):
    ok, f = cap.read()
    if not ok: break
    poly = np.zeros(f.shape[:2], np.uint8); cv2.fillConvexPoly(poly, np.array(Q[i], np.int32), 1)
    poly = cv2.erode(poly, np.ones((15, 15), np.uint8))
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); g = cv2.inRange(hsv, (40, 90, 90), (85, 255, 255)) > 0
    occ = (~g) & (poly > 0)
    # where on the screen is the thumb tip (topmost covered point), as a fraction of screen height
    ys = np.where(occ)[0]
    tip = (ys.min() - min(p[1] for p in Q[i])) / 900 if len(ys) > 200 else None
    mot = 0 if prev is None else (occ ^ prev).sum() / poly.sum()
    rows.append((i / fps, occ.sum() / poly.sum(), mot, tip)); prev = occ
for t, cov, mot, tip in rows[::3]:
    print(f"{t:5.2f}  cover {cov*100:4.1f}%  motion {mot*100:5.2f}  tip {'' if tip is None else round(tip,2)}  " + "#" * int(mot * 400))
