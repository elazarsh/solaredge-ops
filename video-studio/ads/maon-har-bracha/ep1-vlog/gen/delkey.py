# When is the RIGHT thumb's tip on the ⌫ key? Tip = extreme point of the right-thumb blob toward up-left.
# usage: delkey.py clip [keyx keyy]   (UI pixels of the key centre; default ⌫ = 990,1810)
import sys, json, cv2, numpy as np
c = sys.argv[1]; KX, KY = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (990, 1810)
cap = cv2.VideoCapture(f"clips/{c}.mp4"); fps = cap.get(5); Q = json.load(open(f"clips/{c}.json"))["quads"]
UW, UH = 1080, 2590
for i in range(len(Q)):
    ok, f = cap.read()
    if not ok: break
    q = np.float32(Q[i]); Hi = cv2.getPerspectiveTransform(q, np.float32([[0, 0], [UW, 0], [UW, UH], [0, UH]]))
    w = cv2.warpPerspective(f, Hi, (UW, UH))                     # screen in UI space
    hsv = cv2.cvtColor(w, cv2.COLOR_BGR2HSV); g = cv2.inRange(hsv, (40, 60, 60), (85, 255, 255)) > 0
    occ = (~g).astype(np.uint8); occ[:, :12] = 0; occ[:, -12:] = 0; occ[:60] = 0; occ[-12:] = 0
    occ = cv2.morphologyEx(occ, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(occ)
    best = None
    for k in range(1, n):
        if st[k, 4] < 3000 or cen[k][0] < UW * 0.45: continue      # right thumb only
        ys, xs = np.where(lab == k); s = -0.55 * xs - 0.85 * ys
        j = s.argmax(); best = (xs[j], ys[j])
    if best is None: continue
    d = np.hypot(best[0] - KX, best[1] - KY)
    print(f"{i / fps:5.2f} tip ({best[0]:4d},{best[1]:4d}) d={d:5.0f} " + ("<<< ON ⌫" if d < 90 else ""))
