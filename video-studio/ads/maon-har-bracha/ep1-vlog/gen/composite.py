# Composite the rendered phone UI onto the green screens of the Veo footage → footage.mp4 (1080×1920, 30 fps, no audio).
# usage: composite.py edl.json ui.mp4 out.mp4
# EDL rows (final-video seconds): {"clip": "type", "in": 0.4, "start": 10.2, "end": 18.2, "zoom": 1.4}
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
    Z = seg.get("zoom", 1.0)
    cw, ch = W / Z, H / Z
    ox = float(np.clip(c[0] - cw / 2, 0, W - cw)); oy = float(np.clip(c[1] - ch / 2 + seg.get("dy", 0), 0, H - ch))
    while n < round(seg["end"] * FPS):
        t = n / FPS; st = seg["in"] + (t - seg["start"]) * seg.get("speed", 1.0)
        k = min(len(frames) - 1, max(0, int(round(st * cfps))))
        M = np.float32([[Z, 0, -ox * Z], [0, Z, -oy * Z]])
        bg = cv2.warpAffine(frames[k], M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        q = ((np.array(Q[k], np.float64) - [ox, oy]) * Z).astype(np.float32)
        # soft green key inside the (slightly grown) screen quad
        poly = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(poly, q.astype(np.int32), 255)
        poly = cv2.dilate(poly, np.ones((int(10 * Z), int(10 * Z)), np.uint8))
        b, g, r = [bg[..., i].astype(np.float32) for i in range(3)]
        gr = g - np.maximum(r, b)
        a = np.clip((gr - 20) / 90, 0, 1) * (poly / 255.0)
        a = cv2.GaussianBlur(a, (0, 0), 0.8 * Z)
        # the screen's own green (for un-mixing motion-blurred thumb edges: pixel = fg·(1−a) + green·a)
        core = a > 0.95
        Gc = np.median(bg[core], 0).astype(np.float32) if core.sum() > 500 else np.float32([40, 230, 40])
        A = a[..., None]
        fg = bg.astype(np.float32) - A * Gc
        # despill what remains near the screen (thumb, bezel)
        near = cv2.dilate(poly, np.ones((int(30 * Z), int(30 * Z)), np.uint8)) > 0
        b2, g2, r2 = fg[..., 0], fg[..., 1], fg[..., 2]
        fg[..., 1] = np.where(near, np.minimum(g2, np.maximum(r2, b2) * 1.02 + 2), g2)
        # the UI, pre-scaled to about its on-screen size, then perspective-warped to the quad
        u = ui_frame(n)
        sw = np.linalg.norm(q[1] - q[0]); s = max(0.2, min(1.0, sw / UW * 1.15))
        us = cv2.resize(u, (int(UW * s), int(UH * s)), interpolation=cv2.INTER_AREA)
        Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [us.shape[1], 0], [us.shape[1], us.shape[0]], [0, us.shape[0]]]), q)
        uw = cv2.warpPerspective(us, Hm, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)
        uw = cv2.GaussianBlur(uw, (0, 0), 0.35 * Z)           # camera softness
        uw = uw * 0.94 + 8                                     # an emissive screen filmed in daylight: a bit less contrast
        # diagonal sheen across the glass
        d = ((xx - q[0][0]) * 0.6 + (yy - q[0][1]) * 0.8) / (np.linalg.norm(q[2] - q[0]) + 1)
        sheen = np.clip(1 - np.abs(d - 0.35) / 0.25, 0, 1)[..., None] * 14
        uw = uw + sheen
        out = np.clip(fg, 0, 255) + uw * A
        out += rng.normal(0, 3.2, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)   # shared grain
        ff.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
        n += 1
    print(seg["clip"], seg["start"], "→", seg["end"], "zoom", Z, flush=True)
ff.stdin.close(); ff.wait()
print(out_path, n, "frames")
