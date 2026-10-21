# Thumb tips over the screen, in UI pixels (1080×2590): which thumb is where, frame by frame.
# A "tap" = a tip that stops moving down and turns back up. usage: tips.py clip [t0 t1]
import sys, json, cv2, numpy as np
c = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 99
cap = cv2.VideoCapture(f"clips/{c}.mp4"); fps = cap.get(5); Q = json.load(open(f"clips/{c}.json"))["quads"]
UW, UH = 1080, 2590; rows = []
for i in range(len(Q)):
    ok, f = cap.read()
    if not ok: break
    t = i / fps
    if t < t0 or t > t1: continue
    q = np.float32(Q[i]); Hi = cv2.getPerspectiveTransform(q, np.float32([[0, 0], [UW, 0], [UW, UH], [0, UH]]))
    poly = np.zeros(f.shape[:2], np.uint8); cv2.fillConvexPoly(poly, q.astype(np.int32), 1)
    poly = cv2.erode(poly, np.ones((9, 9), np.uint8))
    g = cv2.inRange(cv2.cvtColor(f, cv2.COLOR_BGR2HSV), (40, 90, 90), (85, 255, 255)) > 0
    occ = ((~g) & (poly > 0)).astype(np.uint8)
    occ = cv2.morphologyEx(occ, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(occ)
    tips = []
    for k in range(1, n):
        if st[k, 4] < 400: continue
        ys, xs = np.where(lab == k); j = ys.argmin()
        p = cv2.perspectiveTransform(np.float32([[[xs[j], ys[j]]]]), Hi)[0, 0]
        tips.append((int(p[0]), int(p[1])))
    tips.sort()
    rows.append((t, tips))
for t, tips in rows:
    print(f"{t:5.2f}  " + "  ".join(f"({x:4d},{y:4d})" for x, y in tips))
