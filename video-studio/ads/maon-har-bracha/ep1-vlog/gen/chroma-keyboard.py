# Paint the on-screen keyboard into the green screen of a first frame, in SHADES OF GREEN, so Veo "sees" the keys
# (and presses ⌫ where it really is) while the whole screen stays keyable.
# usage: chroma-keyboard.py frame.jpg ui-snapshot.png out.jpg [kb_top_px=1590]
import sys, cv2, numpy as np, subprocess, json, os
src, snap, out = sys.argv[1:4]; kb_top = int(sys.argv[4]) if len(sys.argv) > 4 else 1590
f = cv2.imread(src); ui = cv2.imread(snap); UH, UW = ui.shape[:2]
# screen quad of the still frame (same method as track.py, via a 1-frame video)
tmp = "/tmp/_ck.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", src, "-t", "0.2", "-r", "5", "-pix_fmt", "yuv420p", tmp], check=True)
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "track.py"), tmp, "/tmp/_ck.json"], check=True)
q = np.float32(json.load(open("/tmp/_ck.json"))["quads"][0])
hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); g = cv2.inRange(hsv, (40, 90, 90), (85, 255, 255)) > 0
green = np.median(f[g], 0)
L = cv2.cvtColor(ui, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
V = 0.47 + 0.53 * L ** 2                                         # dark glyphs → dark green, white keys → full green
tone = (green[None, None, :] * V[..., None]).astype(np.float32)
tone[:kb_top] = green                                            # only the keyboard is drawn
H = cv2.getPerspectiveTransform(np.float32([[0, 0], [UW, 0], [UW, UH], [0, UH]]), q)
w = cv2.warpPerspective(tone, H, (f.shape[1], f.shape[0]), flags=cv2.INTER_AREA)
inside = cv2.warpPerspective(np.ones((UH, UW), np.float32), H, (f.shape[1], f.shape[0])) > 0.5
m = (g & inside)[..., None]
o = np.where(m, w, f).astype(np.uint8)
cv2.imwrite(out, o, [cv2.IMWRITE_JPEG_QUALITY, 95]); print(out, "quad", q.astype(int).tolist())
