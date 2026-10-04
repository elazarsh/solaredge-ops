# Track the green phone screen in a Veo clip → per-frame quad (TL, TR, BR, BL of the SCREEN, phone-up), smoothed.
# Corners come from a 4-point polygon fit of the green hull (handles perspective); when a hand hides a corner the
# fit fails and we fall back to the min-area rectangle. usage: track.py clip.mp4 out.json [--static]
import sys, json, cv2, numpy as np
cap = cv2.VideoCapture(sys.argv[1]); static = "--static" in sys.argv
quads, good = [], []
def order(pts):
    c = pts.mean(0)
    (_, _), (w, h), a = cv2.minAreaRect(pts.astype(np.float32))
    e = [p - c for p in pts]
    # long axis of the screen, pointing to the image top
    vecs = [pts[(i + 1) % 4] - pts[i] for i in range(4)]
    L = max(vecs, key=np.linalg.norm); u = L / np.linalg.norm(L)
    if u[1] > 0: u = -u
    v = np.array([-u[1], u[0]])
    if v[0] < 0: v = -v
    P = {}
    for p in pts:
        d = p - c; P[(np.dot(d, u) > 0, np.dot(d, v) > 0)] = p
    try: return np.array([P[(True, False)], P[(True, True)], P[(False, True)], P[(False, False)]])
    except KeyError: return None
while True:
    ok, f = cap.read()
    if not ok: break
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (40, 90, 90), (85, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs: quads.append(None); good.append(False); continue
    cnt = max(cs, key=cv2.contourArea); hull = cv2.convexHull(cnt)
    rect = cv2.boxPoints(cv2.minAreaRect(hull)); pts = cnt.reshape(-1, 2).astype(float)
    # fit a line to each side from contour points lying on that side's middle 70% (skips rounded corners,
    # the notch and any thumb crossing), then intersect neighbouring lines → perspective-correct corners
    for tol in (14, 30, 50):
      lines = []
      for i in range(4):
          a, b = rect[i], rect[(i + 1) % 4]; d = b - a; Ln = np.linalg.norm(d); t = d / Ln; nrm = np.array([-t[1], t[0]])
          rel = pts - a; along = rel @ t / Ln; dist = np.abs(rel @ nrm)
          sel = pts[(along > 0.15) & (along < 0.85) & (dist < tol)]
          if len(sel) < 20: lines = None; break
          vx, vy, x0, y0 = cv2.fitLine(sel.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
          lines.append((np.array([x0, y0]), np.array([vx, vy])))
      if lines: break
    q = None
    if lines:
        q = []
        for i in range(4):
            (p1, d1), (p2, d2) = lines[i - 1], lines[i]
            A = np.array([d1, -d2]).T
            if abs(np.linalg.det(A)) < 1e-6: q = None; break
            s_ = np.linalg.solve(A, p2 - p1); q.append(p1 + s_[0] * d1)
        q = np.array(q) if q is not None else None
    ok4 = q is not None and abs(cv2.contourArea(q.astype(np.float32)) / cv2.contourArea(hull) - 1.02) < 0.06
    o = order(q if ok4 else rect)
    if o is None: o = order(rect)
    quads.append(o); good.append(ok4 and o is not None)
first = next(x for x in quads if x is not None)
for i, x in enumerate(quads):   # a frame without a usable quad keeps the previous one
    if x is None: quads[i] = quads[i - 1] if i else first
q = np.array(quads, dtype=float)
if static:   # phone lying still: one quad (median of the clean frames) for the whole clip
    g = q[np.array(good)] if any(good) else q
    sm = np.repeat(np.median(g, 0)[None], len(q), 0)
else:
    k = 5; pad = np.pad(q, ((k // 2, k // 2), (0, 0), (0, 0)), mode="edge")
    sm = np.array([np.median(pad[i:i + k], 0) for i in range(len(q))])
    pad = np.pad(sm, ((1, 1), (0, 0), (0, 0)), mode="edge")
    sm = np.array([pad[i:i + 3].mean(0) for i in range(len(sm))])
json.dump({"fps": cap.get(cv2.CAP_PROP_FPS), "quads": sm.round(2).tolist()}, open(sys.argv[2], "w"))
w = np.linalg.norm(sm[:, 1] - sm[:, 0], axis=1); h = np.linalg.norm(sm[:, 3] - sm[:, 0], axis=1)
print(len(sm), "frames, %d%% 4-corner fits; screen w %.0f–%.0f h %.0f–%.0f, aspect %.3f" % (100 * np.mean(good), w.min(), w.max(), h.min(), h.max(), (h / w).mean()))
