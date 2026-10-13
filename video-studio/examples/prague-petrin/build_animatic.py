#!/usr/bin/env python3
"""Build the 24-second ANIMATIC of "Prague's most extreme cable car".

An animatic = the whole video at draft quality, to judge timing, structure and jokes before paying for
generated clips and a voice. What is REAL here: the photo scenes (3, 4, 6), the Hebrew captions and
narration subtitles, the timing, and a synthesised sound track (no copyrighted music). What is a
PLACEHOLDER: scenes 1, 2 and 5 (procedural drawings standing in for PixVerse clips) and the narrator
(subtitles only). Placeholders are labelled on screen.

    python3 build_animatic.py --out animatic.mp4         # needs ffmpeg, Pillow(+RAQM), numpy
"""
from __future__ import annotations

import argparse
import math
import os
import random
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "skills" / "video-edit-engine" / "scripts"))
from hebrew_text import render_text  # noqa: E402

W, H, FPS, DUR = 1080, 1920, 30, 24.0
SR = 48000
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # has Hebrew; use Heebo/Rubik for the final

# ---- the user's exact narration (do not edit the wording) ------------------------------------------------
NARRATION = [  # (start, end, text)
    (0.3, 3.9, "אי שם בלב אירופה מחכה חוויית אקסטרים שתעצור לכם את הנשימה!"),
    (4.2, 7.0, "נוף פנורמי! גבהים מסחררים! תחזיקו חזקקקק!"),
    (9.0, 12.9, "קבלו את רכבת ההרים היחידה שגם תינוקות מבקשים ממנה להאיץ!"),
    (13.2, 16.9, "שימו לב לנועזים שבחרו במסלול האקסטרים... הם פשוט עולים ברגל!"),
    (17.3, 20.9, "בסוף המסע: דופק תקין, ואפס צורך בהחלפת חיתול!"),
    (21.4, 23.5, "רכבל פטז'ין. יותר אקסטרים ממעלית... בקצת."),
]
# (start, end, text, kind) on-screen captions
CAPTIONS = [
    (1.6, 4.0, "THE ULTIMATE EXTREME EXPERIENCE", "en"),
    (10.4, 13.0, "PRAGUE EXTREME ROLLER COASTER", "en"),
    (14.2, 17.0, "EXTREME MODE: STAIRS", "en"),
    (19.4, 21.0, "SURVIVAL RATE: 100%", "en"),
    (22.9, 24.0, "PETŘÍN EXTREME", "en"),
]
FINAL_SUB = "לא לבעלי לב חלש. או לב פועם."


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ---- text helpers -----------------------------------------------------------------------------------------
_text_cache: dict = {}


def text_img(text, size, fill=(255, 255, 255, 255), stroke=8, direction="rtl", max_width=980):
    key = (text, size, fill, stroke, direction, max_width)
    if key not in _text_cache:
        _text_cache[key] = render_text(text, BOLD, size, fill=fill, stroke_width=stroke,
                                       direction=direction, max_width=max_width, padding=10)
    return _text_cache[key]


def paste_center(frame: Image.Image, img: Image.Image, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        img = img.copy()
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img.putalpha(a)
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def pop(t, t0, dur=0.18):
    """scale and alpha for a pop-in starting at t0."""
    p = ease((t - t0) / dur)
    return 1.35 - 0.35 * p, p


# ---- photo canvas and camera ------------------------------------------------------------------------------
class PhotoWorld:
    """Photo scaled to full width, centred on a blurred copy of itself, so it 'fills the 9:16 screen'."""

    def __init__(self, path: Path):
        ph = Image.open(path).convert("RGB")
        self.fw = W
        self.fh = int(ph.height * W / ph.width)
        self.top = (H - self.fh) // 2
        bg = ph.resize((int(ph.width * H / ph.height) + 1, H), Image.BICUBIC)
        left = (bg.width - W) // 2
        bg = bg.crop((left, 0, left + W, H)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.eval(bg, lambda v: int(v * 0.55))
        canvas = bg.copy()
        canvas.paste(ph.resize((self.fw, self.fh), Image.LANCZOS), (0, self.top))
        self.canvas2x = canvas.resize((W * 2, H * 2), Image.BICUBIC)
        self.k = W / ph.width

    def p2c(self, x, y):  # photo px -> canvas px
        return x * self.k, self.top + y * self.k

    def view(self, cx, cy, z):
        bw, bh = W / z, H / z
        x0 = min(max(cx - bw / 2, 0), W - bw)
        y0 = min(max(cy - bh / 2, 0), H - bh)
        img = self.canvas2x.resize((W, H), Image.BICUBIC, box=(x0 * 2, y0 * 2, (x0 + bw) * 2, (y0 + bh) * 2))
        return img.convert("RGBA"), (x0, y0, z)

    @staticmethod
    def to_screen(cam, x, y):
        x0, y0, z = cam
        return (x - x0) * z, (y - y0) * z


# ---- placeholder scenes -----------------------------------------------------------------------------------
def label(frame, text):
    paste_center(frame, text_img(text, 34, (255, 255, 255, 230), 4, "ltr", 1000), W / 2, 150)


def scene1(t, rnd):  # 0-4 epic aerial (placeholder)
    f = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(f)
    for y in range(H):  # cold dramatic sky
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(20 + 90 * k), int(40 + 80 * k), int(90 + 80 * k), 255))
    sh = (int(8 * math.sin(t * 40)), int(8 * math.cos(t * 33)))
    for layer, (col, base, amp, speed) in enumerate([((60, 80, 120), 1000, 260, 30), ((35, 50, 85), 1250, 300, 60),
                                                     ((15, 22, 40), 1500, 340, 110)]):
        pts = [(-50, H)]
        for x in range(-50, W + 60, 40):
            pts.append((x + sh[0], base - amp * (0.5 + 0.5 * math.sin((x + t * speed * 3) / (140 + layer * 70)))
                        - 60 * math.sin((x + t * speed) / 61) + sh[1]))
        pts.append((W + 50, H))
        d.polygon(pts, fill=col + (255,))
    cx = int(-100 + (t / 4) * (W + 200))  # gondola on a cable, swinging
    d.line([(0, 380 + sh[1]), (W, 520 + sh[1])], fill=(10, 10, 15, 255), width=6)
    gy = 380 + (cx / W) * 140 + 70
    sw = 14 * math.sin(t * 5)
    d.line([(cx, gy - 70), (cx + sw, gy)], fill=(10, 10, 15, 255), width=5)
    d.rounded_rectangle((cx + sw - 55, gy, cx + sw + 55, gy + 85), 14, fill=(200, 40, 40, 255))
    return f


def scene2(t, rnd):  # 4-8 extreme montage (placeholder)
    f = Image.new("RGBA", (W, H), (30, 5, 5, 255))
    d = ImageDraw.Draw(f)
    r = random.Random(int(t * 30))
    for _ in range(70):  # speed lines
        a = r.uniform(0, 2 * math.pi)
        r0, r1 = r.uniform(120, 500), r.uniform(900, 1500)
        d.line([(W / 2 + r0 * math.cos(a), H / 2 + r0 * math.sin(a)), (W / 2 + r1 * math.cos(a), H / 2 + r1 * math.sin(a))],
               fill=(255, r.randint(120, 220), 40, 255), width=r.randint(3, 10))
    ph = (t - 4) * 3
    d.rounded_rectangle((W / 2 - 360, H / 2 - 120 + 80 * math.sin(ph * 4), W / 2 + 360, H / 2 + 80 + 80 * math.sin(ph * 4)),
                        60, outline=(255, 255, 255, 255), width=10)  # a "coaster car" placeholder
    shake = (int(r.uniform(-14, 14)), int(r.uniform(-14, 14)))
    return f.transform(f.size, Image.AFFINE, (1, 0, shake[0], 0, 1, shake[1]))


def scene5(t, rnd):  # 17-21 toy train + heart monitor (placeholder)
    f = Image.new("RGBA", (W, H), (190, 225, 255, 255))
    d = ImageDraw.Draw(f)
    d.ellipse((780, 330, 1000, 550), fill=(255, 225, 90, 255))
    for i, (x, y) in enumerate([(120, 420), (480, 560), (700, 300)]):
        d.ellipse((x, y, x + 260, y + 90), fill=(255, 255, 255, 255))
    d.rectangle((0, 1050, W, H), fill=(110, 200, 120, 255))
    d.rectangle((0, 1180, W, 1210), fill=(90, 70, 60, 255))
    x = (t - 17) / 4 * (W + 900) - 700
    wob = 6 * math.sin(t * 45)
    for k in range(3):  # little wagons
        bx = x - k * 230
        d.rounded_rectangle((bx, 1020 + wob, bx + 200, 1150 + wob), 20, fill=[(230, 60, 60, 255), (60, 120, 230, 255), (250, 190, 40, 255)][k])
        for wx in (30, 150):
            d.ellipse((bx + wx - 28, 1130 + wob, bx + wx + 28, 1186 + wob), fill=(40, 40, 40, 255))
    d.rectangle((x + 20, 940 + wob, x + 130, 1020 + wob), fill=(230, 60, 60, 255))
    for j in range(4):  # puffs
        d.ellipse((x - 60 - j * 70, 900 - j * 30, x - 20 - j * 70, 940 - j * 30), fill=(245, 245, 245, 200))
    dy = -640  # keep the heart monitor, stars and baby clear of the narration subtitle (y ~1390)
    d.rounded_rectangle((70, 1290 + dy, 520, 1500 + dy), 24, fill=(15, 20, 25, 255), outline=(255, 255, 255, 255), width=5)
    pts = [(95 + i * 8, 1420 + dy - (60 if (i + int(t * 30)) % 18 == 0 else 6 * math.sin(i))) for i in range(50)]
    d.line(pts, fill=(60, 255, 120, 255), width=5)
    paste_center(f, text_img("72 BPM", 70, (60, 255, 120, 255), 0, "ltr", 400), 295, 1335 + dy)
    paste_center(f, text_img("★★★★★", 74, (255, 215, 0, 255), 4, "ltr", 700), 700, 1480 + dy)
    d.ellipse((780, 1200 + dy, 900, 1320 + dy), fill=(255, 220, 190, 255))  # calm baby
    d.ellipse((815, 1245 + dy, 828, 1258 + dy), fill=(40, 40, 40, 255))
    d.ellipse((852, 1245 + dy, 865, 1258 + dy), fill=(40, 40, 40, 255))
    d.arc((820, 1265 + dy, 860, 1300 + dy), 20, 160, fill=(120, 40, 40, 255), width=4)
    return f



class ClipReader:
    """Streams a generated clip as 1080x1920 RGB frames at 30 fps (one ffmpeg process, nothing held in memory)."""

    def __init__(self, path: Path, vf: str):
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf", f"fps={FPS},{vf},scale={W}:{H}:flags=lanczos",
                                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None

    def next(self) -> Image.Image:
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = Image.frombytes("RGB", (W, H), buf).convert("RGBA")
        return self.last  # hold the last frame if the clip is a hair short

    def close(self):
        self.proc.stdout.close()
        self.proc.wait()


# Veo 3.1 Fast output is 720x1280; clip 2 arrives letterboxed (720x1056 picture), so it is cropped to 9:16 first.
CLIP_FILTERS = {"clip1": "null", "clip2": "crop=594:1056:63:112", "clip5": "null"}


def heart_monitor_overlay(f, t):
    """Fake heart monitor + 5 stars drawn over the generated scene-5 clip."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    dy = -640
    d.rounded_rectangle((70, 1290 + dy, 520, 1500 + dy), 24, fill=(15, 20, 25, 225), outline=(255, 255, 255, 255), width=5)
    pts = [(95 + i * 8, 1420 + dy - (60 if (i + int(t * 30)) % 18 == 0 else 6 * math.sin(i))) for i in range(50)]
    d.line(pts, fill=(60, 255, 120, 255), width=5)
    paste_center(ov, text_img("72 BPM", 70, (60, 255, 120, 255), 0, "ltr", 400), 295, 1335 + dy)
    paste_center(ov, text_img("★★★★★", 74, (255, 215, 0, 255), 4, "ltr", 700), 760, 1480 + dy)
    return Image.alpha_composite(f, ov)


# ---- rendering --------------------------------------------------------------------------------------------
def render(out_video: Path, world: PhotoWorld, clips_dir: Path | None = None):
    car_c = world.p2c(300, 760)
    stairs_c = world.p2c(720, 860)
    ring_c = world.p2c(750, 780)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out_video)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    rnd = random.Random(7)
    readers = {}
    if clips_dir:
        for name, vf in CLIP_FILTERS.items():
            if (clips_dir / f"{name}.mp4").exists():
                readers[name] = ClipReader(clips_dir / f"{name}.mp4", vf)
    for i in range(n):
        t = i / FPS
        placeholder = None
        if t < 4:
            frame, placeholder = (readers["clip1"].next(), None) if "clip1" in readers else (scene1(t, rnd), "PLACEHOLDER - clip 1")
        elif t < 8:
            frame, placeholder = (readers["clip2"].next(), None) if "clip2" in readers else (scene2(t, rnd), "PLACEHOLDER - clip 2")
        elif t < 13:  # scene 3: photo, slow absurd zoom on the little car
            z = 1.0 if t < 8.5 else 1.0 + 0.95 * ease((t - 8.5) / 4.5)
            cx = 540 + (car_c[0] - 540) * ease((t - 8.5) / 4.5)
            cy = 960 + (car_c[1] - 960) * ease((t - 8.5) / 4.5)
            frame, cam = world.view(cx, cy, z)
        elif t < 17:  # scene 4: dramatic zoom to the stairs
            p = ease((t - 13) / 0.9)
            z = 1.15 + 1.1 * p + 0.15 * (t - 13) / 4
            frame, cam = world.view(stairs_c[0], stairs_c[1], z)
            d = ImageDraw.Draw(frame)
            sx, sy = world.to_screen(cam, *ring_c)
            r = 230 * cam[2] / 1.6 * (1 + 0.04 * math.sin(t * 14))
            d.ellipse((sx - r, sy - r * 1.1, sx + r, sy + r * 1.1), outline=(255, 30, 30, 255), width=10)
            if int(t * 4) % 2 == 0:  # blinking arrow
                ax, ay = sx - r - 150, sy - r - 40
                d.polygon([(ax, ay), (ax + 120, ay + 40), (ax + 70, ay + 60), (ax + 110, ay + 140), (ax + 60, ay + 150),
                           (ax + 20, ay + 70), (ax - 20, ay + 100)], fill=(255, 30, 30, 255))
            d.rectangle((0, 250, W, 340), fill=(200, 0, 0, 235))
            paste_center(frame, text_img("חדשות דחופות  |  BREAKING", 54, (255, 255, 255, 255), 0, "rtl", 1000), W / 2, 295)
        elif t < 21:
            if "clip5" in readers:
                frame, placeholder = heart_monitor_overlay(readers["clip5"].next(), t), None
            else:
                frame, placeholder = scene5(t, rnd), "PLACEHOLDER - clip 5"
        elif t < 22.6:  # scene 6: back to the photo, one more slow zoom
            frame, cam = world.view(car_c[0], car_c[1], 1.15 + 0.5 * ease((t - 21) / 1.6))
        else:
            frame = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        if placeholder:
            label(frame, placeholder)
        # captions
        for (a, b, txt, kind) in CAPTIONS:
            if a <= t < b:
                s, al = pop(t, a)
                size = 112 if len(txt) < 24 else 104
                paste_center(frame, text_img(txt, size, (255, 230, 40, 255) if t < 22.6 else (255, 255, 255, 255), 10, "ltr", 960),
                             W / 2, 860 if t >= 22.6 else (430 if t >= 19 else 760), s, al)
        if t >= 23.0:
            s, al = pop(t, 23.0)
            paste_center(frame, text_img(FINAL_SUB, 56, (255, 255, 255, 255), 5, "rtl", 900), W / 2, 1075, s, al)
        # countdown 3-2-1 and the BOOM flash (scene 2)
        for k, t0 in enumerate((7.0, 7.34, 7.68)):
            if t0 <= t < t0 + 0.34:
                s, al = pop(t, t0, 0.1)
                paste_center(frame, text_img(str(3 - k), 520, (255, 255, 255, 255), 14, "ltr", 700), W / 2, 960, s, al)
        if 7.85 <= t < 8.0:
            frame = Image.alpha_composite(frame, Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - 7.85) / 0.15)))))
        # narration subtitles (stand-in for the narrator), inside the Reels safe zone
        for (a, b, txt) in NARRATION:
            if a <= t < b:
                paste_center(frame, text_img(txt, 52, (255, 255, 255, 255), 6, "rtl", 940), W / 2, 1390)
        proc.stdin.write(frame.convert("RGB").tobytes())
    for r in readers.values():
        r.close()
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")


# ---- sound (all synthesised here; nothing copyrighted) ------------------------------------------------------
def lp(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[f > fc] = 0
    return np.fft.irfft(X, len(x))


def hp(x, fc):
    return x - lp(x, fc)


def tt(d):
    return np.arange(int(d * SR)) / SR


def kick(d=0.5):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(38 + 90 * np.exp(-t / 0.05)) / SR
    return np.sin(ph) * np.exp(-t / 0.16)


def noise(d, rs):
    return rs.standard_normal(int(d * SR))


def tone(f, d, tau, harm=0.3):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + harm * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.05)) * np.exp(-t / tau)


def build_audio(path: Path):
    rs = np.random.default_rng(5)
    N = int(DUR * SR)
    mix = np.zeros(N)

    def add(sig, t0, g=1.0):
        i = int(t0 * SR)
        if i >= N:
            return
        s = sig[: N - i]
        mix[i:i + len(s)] += s * g

    # scenes 1-2: epic stand-in - drums, low pad, rising riser (real orchestra to be licensed or generated)
    beat = 0.5
    for k in range(int(8 / beat)):
        add(kick(), k * beat, 0.9)
        if k >= 8:
            add(kick(0.3), k * beat + beat / 2, 0.6)
    t = tt(8)
    pad = sum(np.sign(np.sin(2 * np.pi * f * t + p)) for f, p in [(73.4, 0), (110.0, 1), (146.8, 2), (174.6, 3)]) / 4
    add(lp(pad, 700) * (0.25 + 0.2 * np.minimum(t / 8, 1)) * np.minimum(t / 0.5, 1) * (t < 7.85), 0, 0.5)
    rt = tt(2.0)
    add(hp(noise(2.0, rs), 2000) * (rt / 2.0) ** 2, 5.8, 0.5)
    # BOOM, then RECORD SCRATCH + half a second of near silence
    bt = tt(1.6)
    boom = np.sin(2 * np.pi * np.cumsum(28 + 70 * np.exp(-bt / 0.2)) / SR) * np.exp(-bt / 0.5) + 0.4 * lp(noise(1.6, rs), 300) * np.exp(-bt / 0.2)
    cut = int(0.3 * SR)  # the music (and the boom's tail) are CUT at 8.0 s: that is the joke
    boom = boom[:cut] * np.minimum(np.arange(cut)[::-1] / (0.02 * SR), 1)
    add(boom, 7.7, 1.3)
    st = tt(0.25)
    f = 1500 * np.exp(-st / 0.12) + 120
    add((np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + 0.2 * hp(noise(0.25, rs), 800)) * np.exp(-st / 0.1) * np.minimum((0.25 - st) / 0.02, 1), 8.0, 0.8)
    # silly nursery music 8.75-17.2 (after half a second of real silence): marimba + flute + toy squeaks (own tune)
    melody = [0, 4, 7, 4, 0, 4, 7, 4, 2, 5, 9, 5, 2, 5, 9, 5, 4, 7, 11, 7, 4, 7, 11, 7, 0, 4, 7, 12, 7, 4, 2, 0]
    step = 0.25
    for k in range(int((17.2 - 8.75) / step)):
        n = melody[k % len(melody)]
        fr = 261.63 * 2 ** (n / 12)
        add(tone(fr, 0.4, 0.14), 8.75 + k * step, 0.35)
        if k % 4 == 0:
            ft = tt(0.9)
            add(np.sin(2 * np.pi * fr * 2 * ft + 0.02 * np.sin(2 * np.pi * 5.5 * ft)) * np.minimum(ft / 0.04, 1) * np.exp(-ft / 0.5), 8.75 + k * step, 0.12)
    for t0 in (10.45, 10.6):
        q = tt(0.12)
        add(np.sin(2 * np.pi * np.cumsum(1200 + 11000 * q) / SR) * np.exp(-q / 0.08), t0, 0.5)
    # scene 4: stab, siren, over-dramatic footsteps
    add(kick(0.6) + 0.5 * hp(noise(0.6, rs), 1500) * np.exp(-tt(0.6) / 0.1), 13.0, 1.0)
    sirt = tt(1.3)
    add(np.sin(2 * np.pi * np.cumsum(750 + 260 * np.sin(2 * np.pi * 1.6 * sirt)) / SR) * np.minimum(sirt / 0.05, 1) * np.maximum(1 - (sirt - 1.1) / 0.2, 0), 13.3, 0.25)
    for k in range(9):
        add(lp(noise(0.12, rs), 400) * np.exp(-tt(0.12) / 0.03), 14.1 + k * 0.33, 1.1)
    # scene 5: kids applause, victory jingle
    ap = np.zeros(int(3.2 * SR))
    for _ in range(260):
        i = rs.integers(0, len(ap) - 2400)
        ap[i:i + 2400] += lp(hp(noise(0.05, rs), 1500), 5000)[:2400] * np.exp(-np.arange(2400) / SR / 0.012)
    add(ap * np.minimum(tt(3.2) / 0.3, 1) * 0.12, 17.4, 1.0)
    for k, fr in enumerate((523.25, 659.25, 783.99, 1046.5)):
        jt = tt(0.18)
        add(np.sign(np.sin(2 * np.pi * fr * jt)) * np.exp(-jt / 0.12), 20.0 + k * 0.12, 0.18)
    # scene 6: low hit, silence, elevator DING
    add(kick(0.7), 21.4, 0.9)
    dt = tt(1.0)
    add((np.sin(2 * np.pi * 1760 * dt) + 0.5 * np.sin(2 * np.pi * 2637 * dt)) * np.exp(-dt / 0.45), 23.4, 0.45)

    mix = np.tanh(mix * 0.9)
    pcm = (mix / max(1e-9, np.abs(mix).max()) * 0.9 * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", default=str(HERE / "photo_petrin.jpg"))
    ap.add_argument("--out", default=str(HERE / "animatic.mp4"))
    ap.add_argument("--clips-dir", default=str(HERE / "clips"), help="folder with clip1/clip2/clip5.mp4 (Veo); missing clips fall back to placeholders")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        v, a, an = Path(td) / "v.mp4", Path(td) / "a.wav", Path(td) / "an.wav"
        build_audio(a)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), str(an)], check=True)
        render(v, PhotoWorld(Path(args.photo)), Path(args.clips_dir))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-i", str(an), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", args.out], check=True)
    print(args.out)


if __name__ == "__main__":
    main()
