# Composite the rendered phone UI onto the green screens of the Veo footage → footage.mp4 (1080×1920, 30 fps, no audio).
# usage: composite.py edl.json ui.mp4 out.mp4
# EDL rows (final-video seconds): {"clip": "type", "in": 0.4, "start": 10.2, "end": 18.2, "zoom": 1.4}
#  optional "solid": true keeps only skin (the finger) inside the screen, for shots where Veo drew on the green
#  optional camera keyframes instead of a fixed zoom: "cam": [[t, zoom, u, v], ...] — at time t the point (u, v) of the
#  SCREEN (0..1, from the segment's median quad, so the phone keeps its natural handheld drift) sits at the frame centre;
#  zoom and focus ease between keyframes (smoothstep) → slow, calm push-ins.
#  - the background is cropped+scaled FIRST ("camera closer"), then the UI is warped straight to output pixels,
#    so the text stays crisp even when the footage is upscaled;
#  - the green key is soft and limited to the tracked screen quad, so the thumb stays in front of the screen;
#  - light screen sheen, despill and a shared film grain make the UI sit in the shot.
import sys, json, subprocess, cv2, numpy as np
edl, ui_path, out_path = sys.argv[1:4]
EDL = json.load(open(edl)); FPS = 30; W, H = 1080, 1920
ui = cv2.VideoCapture(ui_path); UW, UH = int(ui.get(3)), int(ui.get(4))
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-g", "30", "-keyint_min", "30", "-movflags", "+faststart", "-pix_fmt", "yuv420p", out_path], stdin=subprocess.PIPE)
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
src_ui = None
def ui_frame(n):
    global src_ui
    ok, f = ui.read()
    if ok: src_ui = f
    return src_ui

n = 0
for seg in EDL:
    cap = cv2.VideoCapture(f"clips/{seg['clip']}.mp4"); cfps = cap.get(cv2.CAP_PROP_FPS)
    track = json.load(open(f"clips/{seg['clip']}.json"))["quads"]
    frames = []; cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(f)
    Q = np.array(track)
    i0, i1 = int(seg["in"] * cfps), min(len(Q) - 1, int((seg["in"] + seg["end"] - seg["start"]) * cfps))
    c = Q[i0:i1 + 1].reshape(-1, 2).mean(0) if "center" not in seg else np.array(seg["center"], float)
    Qm = np.median(Q[i0:i1 + 1], 0).astype(np.float32)
    Hs = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), Qm)
    def camera(t):
        if "cam" not in seg:
            Z = seg.get("zoom", 1.0); return Z, c[0], c[1] + seg.get("dy", 0)
        ks = seg["cam"]
        if t <= ks[0][0]: k0 = k1 = ks[0]; f = 0
        elif t >= ks[-1][0]: k0 = k1 = ks[-1]; f = 0
        else:
            j = max(i for i in range(len(ks)) if ks[i][0] <= t); k0, k1 = ks[j], ks[j + 1]
            f = (t - k0[0]) / (k1[0] - k0[0]); f = f * f * (3 - 2 * f)
        z, u, v = [k0[i] + (k1[i] - k0[i]) * f for i in (1, 2, 3)]
        P = cv2.perspectiveTransform(np.float32([[[u, v]]]), Hs)[0, 0]
        return z, float(P[0]), float(P[1])
    # tilt of the phone in this segment (its long axis vs vertical): with "cam", the virtual camera turns with the phone
    # (90 %), so the screen stands upright and fills the frame at high zoom instead of being cut at the sides
    axis = (Qm[0] + Qm[1]) / 2 - (Qm[3] + Qm[2]) / 2
    tilt = float(np.degrees(np.arctan2(axis[0], -axis[1])))
    rot = -0.9 * tilt if "cam" in seg else 0.0
    while n < round(seg["end"] * FPS):
        t = n / FPS; st = seg["in"] + (t - seg["start"]) * seg.get("speed", 1.0)
        k = min(len(frames) - 1, max(0, int(round(st * cfps))))
        Z, cx, cy = camera(t)
        if rot == 0.0:
            cw, ch = W / Z, H / Z
            cx = float(np.clip(cx, cw / 2, W - cw / 2)); cy = float(np.clip(cy, ch / 2, H - ch / 2))
        M = cv2.getRotationMatrix2D((cx, cy), -rot, Z).astype(np.float32)   # rotate+scale about the focus point…
        M[:, 2] += np.float32([W / 2 - cx, H / 2 - cy])                     # …and bring it to the frame centre
        bg = cv2.warpAffine(frames[k], M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        q = cv2.transform(np.array(Q[k], np.float32)[None], M)[0]
        # soft green key inside the (slightly grown) screen quad
        poly = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(poly, q.astype(np.int32), 255)
        poly = cv2.dilate(poly, np.ones((int(10 * Z), int(10 * Z)), np.uint8))
        b, g, r = [bg[..., i].astype(np.float32) for i in range(3)]
        # key on green DOMINANCE (not brightness), so dark-green drawings on the screen (gen/chroma-keyboard.py) key fully
        gr = (g - np.maximum(r, b)) / np.maximum(g, 1)
        a = np.clip((gr - 0.22) / 0.33, 0, 1) * (poly / 255.0)
        if seg.get("solid"):   # Veo drew things on the screen (e.g. a keyboard): inside the screen keep only skin (the finger)
            skin = np.clip(((r - b) - 18) / 25, 0, 1) * np.clip(((r - g) - 4) / 14, 0, 1)
            skin = cv2.GaussianBlur(cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), (0, 0), 1.2 * Z)
            inner = cv2.erode(poly, np.ones((int(6 * Z), int(6 * Z)), np.uint8)) / 255.0
            a = np.maximum(a, inner * (1 - skin))
        a = cv2.GaussianBlur(a, (0, 0), 0.8 * Z)
        A = a[..., None]
        fg = bg.astype(np.float32) * (1 - A)
        # despill what remains near the screen (thumb edges, bezel)
        near = cv2.dilate(poly, np.ones((int(30 * Z), int(30 * Z)), np.uint8)) > 0
        b2, g2, r2 = fg[..., 0], fg[..., 1], fg[..., 2]
        fg[..., 1] = np.where(near, np.minimum(g2, (r2 + b2) / 2 + 12), g2)   # skin keeps g < (r+b)/2+12; green fringes don't
        # the UI, pre-scaled to about its on-screen size, then perspective-warped to the quad
        u = ui_frame(n)
        sw = np.linalg.norm(q[1] - q[0]); s = max(0.2, min(1.0, sw / UW * 1.15))
        us = cv2.resize(u, (int(UW * s), int(UH * s)), interpolation=cv2.INTER_AREA)
        Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [us.shape[1], 0], [us.shape[1], us.shape[0]], [0, us.shape[0]]]), q)
        uw = cv2.warpPerspective(us, Hm, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)
        # the top band of the screen (where some phones have a notch) is always screen: at high zoom the keyed notch
        # edge looks jagged, so the UI simply covers it (thumbs never reach that band)
        band = np.zeros(us.shape[:2], np.float32); bh, bw = band.shape
        band[: int(0.075 * bh), int(0.12 * bw): int(0.88 * bw)] = 1
        band = cv2.warpPerspective(band, Hm, (W, H), flags=cv2.INTER_LINEAR)
        A = np.maximum(A, band[..., None]); fg = fg * (1 - band[..., None])
        uw = cv2.GaussianBlur(uw, (0, 0), 0.45)                # a touch of camera softness (text stays sharp at any zoom)
        uw = uw * 0.94 + 8                                     # an emissive screen filmed in daylight: a bit less contrast
        # diagonal sheen across the glass
        d = ((xx - q[0][0]) * 0.6 + (yy - q[0][1]) * 0.8) / (np.linalg.norm(q[2] - q[0]) + 1)
        sheen = np.clip(1 - np.abs(d - 0.35) / 0.25, 0, 1)[..., None] * 14
        uw = uw + sheen
        out = np.clip(fg, 0, 255) + uw * A
        out += rng.normal(0, 3.2, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)   # shared grain
        ff.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
        n += 1
    print(seg["clip"], seg["start"], "→", seg["end"], flush=True)
ff.stdin.close(); ff.wait()
print(out_path, n, "frames")
