#!/usr/bin/env python3
"""Final cut of "Prague's most extreme cable car" (v3).

Everything is driven by the narration: the length of each narrated line decides the length of its scene
(guide, section 12a). Inputs (all in this folder):
  voice/L1..L6.wav + voice/lines.json   narration (Gemini TTS, verified by transcription)
  music/epic.wav, music/nursery.wav     music (Google Lyria 3 Clip)
  clips/clip1|2|5.mp4                   generated scenes (Veo 3.1 Fast)
  photo_petrin.jpg                      the real photo (never regenerated; faces of passers-by are blurred)
Outputs: final.mp4 (Hebrew narration subtitles burned in), final_clean.mp4 (no subtitles), narration.srt

    python3 build_final.py                # audio + video
    python3 build_final.py --audio-only   # just the mix (fast)
"""
from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "skills" / "video-edit-engine" / "scripts"))
from hebrew_text import render_text  # noqa: E402

W, H, FPS, SR = 1080, 1920, 30, 48000
ANTON = str(HERE / "fonts" / "Anton-Regular.ttf")
HEEBO = str(HERE / "fonts" / "Heebo[wght].ttf")

# ------------------------------------------------------------------------------------------------ timeline
LINES = json.loads((HERE / "voice" / "lines.json").read_text(encoding="utf-8"))
TEMPO = {"L1": 1.10, "L2": 1.08, "L3": 1.10, "L4": 1.10, "L5": 1.10, "L6": 1.0}  # gentle speed-up (pitch preserved)
D = {k: LINES[k]["seconds"] / TEMPO[k] for k in TEMPO}
L6_LAST_WORD = 3.66  # seconds into L6 where "בקצת" starts (0.85 s comic pause before it)


class TL:
    """All times in seconds of the final video."""
    t_L1 = 0.20
    S1_end = max(4.10, t_L1 + D["L1"] + 0.20)
    t_L2 = S1_end + 0.20
    cd0 = t_L2 + D["L2"] + 0.05            # 3 .. 2 .. 1
    boom = cd0 + 1.02
    SCR = boom + 0.20                      # record scratch = hard cut to the real photo
    NURS = SCR + 0.55                      # half a second of true silence, then the nursery music
    t_L3 = SCR + 0.75
    cap3 = t_L3 + 1.5
    S3_end = t_L3 + D["L3"] + 0.25
    t_L4 = S3_end + 0.25
    S4_end = t_L4 + D["L4"] + 0.25
    S5_start = S4_end
    t_L5 = S5_start + 0.30
    S5_end = max(S5_start + 4.0, t_L5 + D["L5"] + 0.30)
    S6_start = S5_end
    t_L6 = S6_start + 0.35
    end6 = t_L6 + D["L6"]
    dip = end6 + 0.12
    title = dip + 0.30
    ding = dip + 0.60
    END = ding + 1.50


SUBS = [(TL.t_L1, TL.t_L1 + D["L1"], LINES["L1"]["text"]),
        (TL.t_L2, TL.t_L2 + D["L2"], "נוף פנורמי! גבהים מסחררים! תחזיקו חזקקקק!"),
        (TL.t_L3, TL.t_L3 + D["L3"], LINES["L3"]["text"]),
        (TL.t_L4, TL.t_L4 + D["L4"], LINES["L4"]["text"]),
        (TL.t_L5, TL.t_L5 + D["L5"], LINES["L5"]["text"]),
        (TL.t_L6, TL.t_L6 + L6_LAST_WORD - 0.1, "רכבל פטז'ין. יותר אקסטרים ממעלית..."),
        (TL.t_L6 + L6_LAST_WORD - 0.05, TL.end6 + 0.2, "בקצת.")]


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ audio
def lp(x, fc):
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    X[f > fc] = 0
    return np.fft.irfft(X, x.shape[0], axis=0)


def hp(x, fc):
    return x - lp(x, fc)


def reverb(x, decay=0.5, wet=0.2, seed=3):
    rs = np.random.default_rng(seed)
    n = int(decay * SR * 3)
    ir = rs.standard_normal(n) * np.exp(-np.arange(n) / (decay * SR))
    ir[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    ir = lp(ir[:, None], 6000)[:, 0]
    L = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[: len(x) + n // 2]
    y = y / (np.abs(y).max() + 1e-9) * np.abs(x).max()
    out = np.zeros(len(y))
    out[: len(x)] += x * (1 - wet)
    return out + y * wet


def load(path, tempo=1.0):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if tempo != 1.0:
        cmd += ["-af", f"atempo={tempo}"]
    cmd += ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def tt(d):
    return np.arange(int(d * SR)) / SR


def kick(d=0.5, f0=38, f1=90):
    t = tt(d)
    return np.sin(2 * np.pi * np.cumsum(f0 + f1 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.16)


def build_audio(path: Path):
    rs = np.random.default_rng(11)
    N = int((TL.END + 0.2) * SR)
    music = np.zeros((N, 2))
    voice = np.zeros((N, 2))
    sfx = np.zeros((N, 2))

    def put(buf, sig, t0, g=1.0, pan=0.0):
        i = int(t0 * SR)
        if sig.ndim == 1:
            sig = np.stack([sig * (1 - max(pan, 0)), sig * (1 + min(pan, 0))], axis=1)
        s = sig[: max(0, N - i)]
        buf[i:i + len(s)] += s * g

    # music 1: epic trailer bed, from the first frame up to the record scratch (hard cut)
    ep = load(HERE / "music" / "epic.mp3")
    seg = ep[: int(TL.SCR * SR)].copy()
    seg *= np.minimum(np.arange(len(seg)) / (0.05 * SR), 1)[:, None]
    seg *= np.minimum((len(seg) - np.arange(len(seg))) / (0.02 * SR), 1)[:, None]  # 20 ms fade = the cut
    # build-up shaping: starts ~ -6 dB and swells into the countdown
    shape = 0.55 + 0.45 * np.clip((np.arange(len(seg)) / SR) / (TL.cd0), 0, 1) ** 1.5
    # the loudest part of the epic bed sits under line 2: pull it back so every word of the narration stays clear
    dip = np.ones(len(seg))
    a0, a1 = int((TL.t_L2 - 0.1) * SR), int((TL.t_L2 + D["L2"] + 0.15) * SR)
    dip[a0:a1] = float(__import__("os").environ.get("L2_DIP", "0.18"))
    mus = seg * shape[:, None] * dip[:, None]
    if __import__("os").environ.get("L2_LP", "1") == "1":  # also roll the highs off the score under line 2 so consonants are not masked
        mus[a0:a1] = lp(mus[a0:a1], 2800)
    put(music, mus, 0, 0.62)
    # music 2: kindergarten bed, after the silence, faded out under scene 5 -> 6
    nu = load(HERE / "music" / "nursery.mp3")
    n_len = int((TL.S5_end + 0.5 - TL.NURS) * SR)
    nseg = nu[:n_len].copy()
    nseg *= np.minimum(np.arange(len(nseg)) / (0.04 * SR), 1)[:, None]
    nseg *= np.clip((len(nseg) - np.arange(len(nseg))) / (0.7 * SR), 0, 1)[:, None]
    put(music, nseg, TL.NURS, 0.42)

    # narration: tempo, EQ for body, soft compression, a touch of room
    for key, t0 in (("L1", TL.t_L1), ("L2", TL.t_L2), ("L3", TL.t_L3), ("L4", TL.t_L4), ("L5", TL.t_L5), ("L6", TL.t_L6)):
        v = load(HERE / "voice" / f"{key}.wav", TEMPO[key]).mean(axis=1)
        v = hp(v[:, None], 70)[:, 0]
        v = v + 0.45 * lp(v[:, None], 190)[:, 0]
        v = np.tanh(2.4 * v / (np.abs(v).max() + 1e-9)) / np.tanh(2.4)
        v = v + 0.30 * (lp(v[:, None], 4200)[:, 0] - lp(v[:, None], 1800)[:, 0])  # presence band: consonants cut through the score
        v = reverb(v, 0.35, 0.10)
        v *= 0.9 / (np.abs(v).max() + 1e-9)
        put(voice, v, t0)

    # SFX ------------------------------------------------------------------------------------------------
    def whoosh(d, up=True):
        n = int(d * SR)
        x = rs.standard_normal(n)
        env = np.sin(np.linspace(0, np.pi, n)) ** 2
        sweep = hp(x[:, None], 300)[:, 0] * env
        return lp(sweep[:, None], 2500 if up else 1500)[:, 0] * 0.9

    put(sfx, whoosh(0.4), TL.S1_end - 0.28, 0.7)                                   # zoom transition
    for k in range(3):                                                             # 3 .. 2 .. 1
        put(sfx, kick(0.35, 55, 70) + 0.25 * np.sin(2 * np.pi * 880 * tt(0.35)) * np.exp(-tt(0.35) / 0.05), TL.cd0 + k * 0.34, 0.7)
    rt = tt(1.1)
    put(sfx, hp(rs.standard_normal(len(rt))[:, None], 1800)[:, 0] * (rt / 1.1) ** 2, TL.cd0 - 0.05, 0.4)  # riser
    bt = tt(1.0)
    boom = np.sin(2 * np.pi * np.cumsum(30 + 80 * np.exp(-bt / 0.2)) / SR) * np.exp(-bt / 0.35) + 0.5 * lp(rs.standard_normal(len(bt))[:, None], 300)[:, 0] * np.exp(-bt / 0.15)
    cut = int(0.2 * SR)  # the boom is chopped by the scratch
    boom = boom[:cut + 1] * np.minimum((cut - np.arange(cut + 1)) / (0.02 * SR), 1)
    put(sfx, boom, TL.boom, 1.5)
    st = tt(0.25)
    scr = (np.sign(np.sin(2 * np.pi * np.cumsum(1500 * np.exp(-st / 0.12) + 120) / SR)) * 0.3
           + 0.2 * hp(rs.standard_normal(len(st))[:, None], 800)[:, 0]) * np.exp(-st / 0.1) * np.minimum((0.25 - st) / 0.02, 1)
    put(sfx, scr, TL.SCR, 0.9)                                                    # RECORD SCRATCH
    for k, t0 in enumerate((TL.cap3, TL.cap3 + 0.15)):                            # toy squeaks
        q = tt(0.12)
        put(sfx, np.sin(2 * np.pi * np.cumsum(1200 + 11000 * q) / SR) * np.exp(-q / 0.08), t0, 0.5)
    put(sfx, whoosh(0.5), TL.S3_end - 0.30, 0.8)                                  # whip to the stairs
    put(sfx, kick(0.6) + 0.5 * hp(rs.standard_normal(int(0.6 * SR))[:, None], 1500)[:, 0] * np.exp(-tt(0.6) / 0.1), TL.S3_end + 0.1, 0.9)
    sirt = tt(1.0)
    put(sfx, np.sin(2 * np.pi * np.cumsum(750 + 260 * np.sin(2 * np.pi * 1.6 * sirt)) / SR) * np.minimum(sirt / 0.05, 1) * np.clip(1 - (sirt - 0.85) / 0.15, 0, 1), TL.t_L4 - 0.15, 0.2)
    k = 0
    while TL.t_L4 + 0.6 + k * 0.33 < TL.S4_end - 0.1:                             # over-dramatic footsteps
        put(sfx, lp(rs.standard_normal(int(0.12 * SR))[:, None], 400)[:, 0] * np.exp(-tt(0.12) / 0.03), TL.t_L4 + 0.6 + k * 0.33, 0.8)
        k += 1
    put(sfx, whoosh(0.5, False), TL.S4_end - 0.2, 0.6)                            # page peel (paper-ish)
    ap = np.zeros(int(3.6 * SR))
    for _ in range(300):                                                          # kids applauding
        i = rs.integers(0, len(ap) - 2400)
        ap[i:i + 2400] += lp(hp(rs.standard_normal(2400)[:, None], 1500), 5000)[:, 0] * np.exp(-np.arange(2400) / SR / 0.012)
    put(sfx, ap * np.minimum(tt(3.6) / 0.3, 1) * 0.10, TL.S5_start + 0.5, 1.0)
    for j, fr in enumerate((523.25, 659.25, 783.99, 1046.5)):                     # old-school victory jingle
        jt = tt(0.18)
        put(sfx, np.sign(np.sin(2 * np.pi * fr * jt)) * np.exp(-jt / 0.12), TL.S5_end - 0.85 + j * 0.12, 0.16)
    put(sfx, whoosh(0.4), TL.S5_end - 0.28, 0.45)                                 # match-dissolve swoosh
    put(sfx, reverb(kick(0.9, 32, 60), 0.6, 0.3), TL.t_L6 - 0.10, 0.7)            # solemn low hit under the deadpan line
    dt = tt(1.6)
    ding = reverb((np.sin(2 * np.pi * 1760 * dt) + 0.5 * np.sin(2 * np.pi * 2637 * dt)) * np.exp(-dt / 0.5), 0.5, 0.25)
    put(sfx, ding, TL.ding, 0.5)                                                  # elevator DING

    # ducking: music and sfx step back whenever the narrator speaks
    def movavg(x, n):
        c = np.cumsum(np.insert(x, 0, 0.0))
        out = np.empty_like(x)
        h = n // 2
        idx = np.arange(len(x))
        lo, hi = np.clip(idx - h, 0, len(x)), np.clip(idx + n - h, 0, len(x))
        out[:] = (c[hi] - c[lo]) / np.maximum(hi - lo, 1)
        return out

    env = np.sqrt(movavg(voice.mean(axis=1) ** 2, int(0.05 * SR)))
    env = movavg(env, int(0.18 * SR))
    duck = 1 - 0.74 * np.clip(env / (env.max() * 0.35 + 1e-9), 0, 1)
    mix = voice * 1.0 + music * duck[:, None] + sfx * (1 - 0.35 * np.clip(env / (env.max() * 0.35 + 1e-9), 0, 1))[:, None]
    mix = np.tanh(mix * 0.85) / np.tanh(0.85)
    pcm = (np.clip(mix / (np.abs(mix).max() + 1e-9) * 0.95, -1, 1) * 32767).astype("<i2")
    raw = path.with_suffix(".raw.wav")
    with wave.open(str(raw), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", str(SR), str(path)], check=True)
    raw.unlink()


# ------------------------------------------------------------------------------------------------ video helpers
_cache: dict = {}


def text(txt, font, size, fill=(255, 255, 255, 255), stroke=0, direction="ltr", weight=None, max_width=980, shadow=True):
    key = (txt, font, size, fill, stroke, direction, weight, max_width, shadow)
    if key not in _cache:
        img = render_text(txt, font, size, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255), direction=direction,
                          max_width=max_width, padding=14 + (10 if shadow else 0), weight=weight, align="center")
        if shadow:
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            sh.putalpha(img.getchannel("A").point(lambda v: int(v * 0.65)))
            sh = sh.filter(ImageFilter.GaussianBlur(7))
            base = Image.new("RGBA", img.size, (0, 0, 0, 0))
            base.alpha_composite(sh, (6, 8))
            base.alpha_composite(img)
            img = base
        _cache[key] = img
    return _cache[key]


def paste(frame, img, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def pop(t, t0, dur=0.16):
    p = ease((t - t0) / dur)
    s = 1.0 + 0.30 * (1 - p) + (0.05 * math.sin(p * math.pi) if p < 1 else 0)
    return s, p


def zoom(img, z, cx=0.5, cy=0.5):
    if z == 1.0:
        return img
    bw, bh = W / z, H / z
    x0 = min(max(cx * W - bw / 2, 0), W - bw)
    y0 = min(max(cy * H - bh / 2, 0), H - bh)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh))


def zoom_blur(img, z, cx=0.5, cy=0.5, n=4, spread=0.05):
    acc = None
    for i in range(n):
        f = zoom(img, z * (1 + spread * i / n), cx, cy).convert("RGB")
        a = np.asarray(f, dtype=np.float32)
        acc = a if acc is None else acc + a
    return Image.fromarray((acc / n).astype(np.uint8)).convert("RGBA")


_vig = None


def vignette(strength=0.38):
    global _vig
    if _vig is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
        _vig = np.clip(1 - strength * (r ** 2.2) / 1.6, 0.4, 1)[..., None]
    return _vig


_grain = None


def grade(img: Image.Image, t: float, grain=5.0, warm=1.0) -> Image.Image:
    """Cinematic polish for generated scenes only: S-curve, teal shadows / warm highlights, vignette, light grain."""
    global _grain
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255
    a = a * 0.45 + (a * a * (3 - 2 * a)) * 0.55
    lum = a.mean(axis=2, keepdims=True)
    a[..., 2:3] += 0.035 * (1 - lum)
    a[..., 0:1] += 0.030 * warm * lum
    a *= vignette()
    if _grain is None:
        rs = np.random.default_rng(1)
        _grain = [rs.standard_normal((H, W, 1)).astype(np.float32) for _ in range(6)]
    a += _grain[int(t * FPS) % 6] * grain / 255
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")


class Clip:
    """A generated clip, time-stretched to its slot and streamed frame by frame (nothing held in memory)."""

    def __init__(self, path: Path, crop: str, t0: float, t1: float):
        src = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                   capture_output=True, text=True, check=True).stdout)
        self.t0, self.n = t0, int(round((t1 - t0) * FPS))
        vf = f"{crop},setpts=PTS*{(t1 - t0) / src:.5f},fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE)
        self.i, self.cur = -1, None

    def frame(self, t):
        want = min(max(int(round((t - self.t0) * FPS)), 0), self.n)
        while self.i < want:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) == W * H * 3:
                self.cur = Image.frombytes("RGB", (W, H), buf).convert("RGBA")
            self.i += 1
        return self.cur

    def close(self):
        self.p.terminate()
        self.p.stdout.close()
        self.p.wait()


class PhotoWorld:
    def __init__(self, path: Path):
        ph = Image.open(path).convert("RGB")
        for box in ((762, 588, 824, 654),):  # two passers-by looking back at the camera: blur their faces
            reg = ph.crop(box).filter(ImageFilter.GaussianBlur(10))
            mask = Image.new("L", reg.size, 0)
            ImageDraw.Draw(mask).ellipse((2, 2, reg.width - 2, reg.height - 2), fill=255)
            ph.paste(reg, box[:2], mask.filter(ImageFilter.GaussianBlur(5)))
        self.k = W / ph.width
        self.top = (H - int(ph.height * self.k)) // 2
        bg = ph.resize((int(ph.width * H / ph.height) + 1, H), Image.BICUBIC)
        left = (bg.width - W) // 2
        bg = bg.crop((left, 0, left + W, H)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.eval(bg, lambda v: int(v * 0.5))
        c = bg.copy()
        c.paste(ph.resize((W, int(ph.height * self.k)), Image.LANCZOS), (0, self.top))
        self.c2 = c.resize((W * 2, H * 2), Image.BICUBIC)
        self.car = self.p2c(300, 760)
        self.stairs = self.p2c(720, 860)
        self.ring = self.p2c(752, 790)

    def p2c(self, x, y):
        return x * self.k, self.top + y * self.k

    def view(self, cx, cy, z, shake=0.0, t=0.0):
        bw, bh = W / z, H / z
        cx += shake * math.sin(t * 37) * 3
        cy += shake * math.cos(t * 29) * 3
        x0 = min(max(cx - bw / 2, 0), W - bw)
        y0 = min(max(cy - bh / 2, 0), H - bh)
        ph_h = H - 2 * self.top
        if bh <= ph_h:  # the view fits inside the photo: never show the blurred filler below/above it
            y0 = min(max(y0, self.top), self.top + ph_h - bh)
        img = self.c2.resize((W, H), Image.BICUBIC, box=(x0 * 2, y0 * 2, (x0 + bw) * 2, (y0 + bh) * 2))
        return img.convert("RGBA"), (x0, y0, z)

    def cam(self, t):
        """Camera path for scenes 3-4 and 6: (cx, cy, z, whip-blur)."""
        cx0, cy0 = W / 2, H / 2
        if t < TL.NURS:
            return cx0, cy0, 1.0, 0.0
        if t < TL.S3_end - 0.30:                       # slow, absurd push-in on the little car
            p = ease((t - TL.NURS) / (TL.S3_end - 0.30 - TL.NURS))
            return cx0 + (self.car[0] - cx0) * p, cy0 + (self.car[1] - cy0) * p, 1 + 0.9 * p, 0.0
        if t < TL.S3_end + 0.20:                       # whip: car -> stairs ("zoom into the detail")
            p = ease((t - (TL.S3_end - 0.30)) / 0.5)
            return (self.car[0] + (self.stairs[0] - self.car[0]) * p, self.car[1] + (self.stairs[1] - self.car[1]) * p,
                    1.9 + (1.5 - 1.9) * p, math.sin(p * math.pi))
        if t < TL.S4_end + 0.4:
            p = (t - (TL.S3_end + 0.20)) / (TL.S4_end - TL.S3_end)
            return self.stairs[0], self.stairs[1], 1.5 + 1.0 * ease(p), 0.0
        p = ease((t - TL.S6_start) / (TL.dip - TL.S6_start))
        return self.car[0], self.car[1], 1.45 - 0.25 + 0.5 * p, 0.0


def stars(draw, cx, cy, r, n=5, fill=(255, 205, 40, 255)):
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * r * 2.5
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((x + rr * math.cos(a), cy + rr * math.sin(a)))
        draw.polygon(pts, fill=fill, outline=(0, 0, 0, 255))


def news_graphics(frame, t, cam, world):
    d = ImageDraw.Draw(frame)
    sx, sy = (world.ring[0] - cam[0]) * cam[2], (world.ring[1] - cam[1]) * cam[2]
    r = 215 * cam[2] / 1.5
    p = ease((t - TL.t_L4) / 0.35)
    if p > 0:
        bbox = (sx - r, sy - r * 1.12, sx + r, sy + r * 1.12)
        d.arc(bbox, -90, -90 + 360 * p, fill=(255, 40, 40, 255), width=11)
    if int((t - TL.t_L4) * 4) % 2 == 0 and p > 0.6:
        ax, ay = sx - r - 190, sy - r - 60
        d.polygon([(ax, ay), (ax + 125, ay + 45), (ax + 72, ay + 66), (ax + 118, ay + 150), (ax + 62, ay + 160), (ax + 22, ay + 76), (ax - 22, ay + 108)],
                  fill=(255, 40, 40, 255), outline=(255, 255, 255, 255))
    q = ease((t - (TL.S3_end + 0.05)) / 0.25)
    off = int((1 - q) * -160)
    d.rectangle((0, 300 + off, W, 392 + off), fill=(200, 0, 0, 240))
    paste(frame, text("BREAKING", ANTON, 64, (255, 255, 255, 255), 0, "ltr", None, 500, False), 190, 346 + off)
    paste(frame, text("חדשות דחופות", HEEBO, 56, (255, 255, 255, 255), 0, "rtl", 800, 600, False), 800, 346 + off)
    d.rectangle((0, 392 + off, W, 440 + off), fill=(10, 10, 14, 235))
    d.ellipse((38, 410 + off, 58, 430 + off), fill=(255, 50, 50, 255 if int(t * 2) % 2 == 0 else 90))
    paste(frame, text("LIVE", ANTON, 34, (255, 255, 255, 255), 0, "ltr", None, 200, False), 118, 417 + off)
    ticker = "BREAKING  •  EXTREME  •  " * 6
    ti = text(ticker, ANTON, 34, (255, 255, 255, 255), 0, "ltr", None, 6000, False)
    x0 = int((t * 140) % (ti.width / 3))
    frame.alpha_composite(ti.crop((x0, 0, x0 + W - 190, ti.height)), (190, 396 + off))


def heart_monitor(frame, t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((50, 330, 520, 520), 24, fill=(12, 16, 20, 225), outline=(255, 255, 255, 255), width=5)
    pts = [(78 + i * 8.5, 480 - (62 if (i + int(t * 30)) % 18 == 0 else 7 * math.sin(i))) for i in range(50)]
    d.line(pts, fill=(70, 255, 130, 255), width=5)
    paste(ov, text("72 BPM", ANTON, 66, (70, 255, 130, 255), 0, "ltr", None, 400, False), 285, 388)
    stars(d, 770, 425, 30)
    return Image.alpha_composite(frame, ov)


def peel(a: Image.Image, b: Image.Image, p: float) -> Image.Image:
    """Page peel from the top-right corner: A is the old page, B the new chapter underneath."""
    A = np.asarray(a.convert("RGB"), dtype=np.float32)
    B = np.asarray(b.convert("RGB"), dtype=np.float32)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    s = (x / W + (1 - y / H)) / 2
    th = 1.0 - 1.12 * p
    band = 0.075
    out = np.where((s > th)[..., None], B, A)
    shadow = np.clip(1 - (th - s) / 0.06, 0, 1) * (s <= th)
    out = out * (1 - 0.40 * shadow[..., None])
    curl = (s > th) & (s <= th + band)
    g = np.clip((s - th) / band, 0, 1)[..., None]
    back = (A * 0.30 + 255 * 0.70) * (0.78 + 0.22 * (1 - g))
    out = np.where(curl[..., None], back, out)
    cast = np.clip(1 - (s - th - band) / 0.05, 0, 1) * (s > th + band)
    out = out * (1 - 0.30 * cast[..., None])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------------------------------------------ video
def render(clean_out: Path, subs_out: Path, audio: Path):
    world = PhotoWorld(HERE / "photo_petrin.jpg")
    c1 = Clip(HERE / "clips" / "clip1.mp4", "null", 0.0, TL.S1_end + 0.20)
    c2 = Clip(HERE / "clips" / "clip2.mp4", "crop=594:1056:63:112", TL.S1_end - 0.20, TL.SCR + 0.02)
    c5 = Clip(HERE / "clips" / "clip5.mp4", "null", TL.S5_start - 0.20, TL.S5_end + 0.25)
    enc = lambda out: subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                        "-i", str(audio), "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "3300k", "-bufsize", "6600k",
                                        "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                                        "-shortest", str(out)], stdin=subprocess.PIPE)
    pa, pb = enc(clean_out), enc(subs_out)
    n = int(TL.END * FPS)
    for i in range(n):
        t = i / FPS
        frame = scene(t, world, c1, c2, c5)
        clean = frame.convert("RGB")
        pa.stdin.write(clean.tobytes())
        fs = frame.copy()
        for a, b, txt in SUBS:
            if a <= t < b + 0.05:
                paste(fs, text(txt, HEEBO, 54, (255, 255, 255, 255), 7, "rtl", 800, 940, False), W / 2, 1395)
        pb.stdin.write(fs.convert("RGB").tobytes())
        if i % 90 == 0:
            print(f"  frame {i}/{n}", flush=True)
    for c in (c1, c2, c5):
        c.close()
    for p in (pa, pb):
        p.stdin.close()
        if p.wait() != 0:
            raise RuntimeError("ffmpeg encode failed")


def scene(t, world, c1, c2, c5):
    # ---- scene 1 / 2 (generated, graded) with a zoom-through transition
    if t < TL.SCR:
        zt0 = TL.S1_end - 0.20
        if t < zt0:
            f = grade(c1.frame(t), t)
        elif t < TL.S1_end + 0.15:
            p = ease((t - zt0) / 0.35)
            a = zoom_blur(grade(c1.frame(t), t), 1 + 1.6 * p, 0.5, 0.5)
            b = zoom_blur(grade(c2.frame(t), t), 2.6 - 1.6 * p, 0.5, 0.5)
            f = Image.blend(a, b, ease((p - 0.4) / 0.25))
        else:
            f = grade(c2.frame(t), t, warm=1.4)
        if TL.t_L1 + 1.3 <= t < TL.S1_end - 0.05:
            s, al = pop(t, TL.t_L1 + 1.3)
            paste(f, text("THE ULTIMATE EXTREME EXPERIENCE", ANTON, 128, (255, 236, 80, 255), 8, "ltr", None, 960), W / 2, 760, s, al)
        for k in range(3):
            c0 = TL.cd0 + k * 0.34
            if c0 <= t < c0 + 0.34:
                s, al = pop(t, c0, 0.09)
                paste(f, text(str(3 - k), ANTON, 640, (255, 255, 255, 255), 14, "ltr", None, 800), W / 2, 930, s, al)
        if TL.boom - 0.35 < t:  # camera shake into the boom
            sh = (random.Random(int(t * 60)).uniform(-16, 16), random.Random(int(t * 60) + 1).uniform(-16, 16))
            f = f.transform(f.size, Image.AFFINE, (1, 0, sh[0], 0, 1, sh[1]))
        if t >= TL.boom - 0.04:  # washout: white takes the whole frame
            f = Image.alpha_composite(f, Image.new("RGBA", (W, H), (255, 255, 255, int(255 * ease((t - (TL.boom - 0.04)) / 0.08)))))
        return f
    # ---- photo scenes 3-4, page peel into scene 5, match dissolve back to the photo
    peel_t0, md0, md1 = TL.S4_end - 0.15, TL.S6_start - 0.30, TL.S6_start + 0.25
    if t < peel_t0:
        return photo_frame(t, world)
    if t < peel_t0 + 0.50:
        return peel(photo_frame(t, world), c5_frame(t, c5), ease((t - peel_t0) / 0.50))
    if t < md0:
        return c5_frame(t, c5)
    if t < md1:  # the little yellow wagon becomes the little funicular car
        p = ease((t - md0) / (md1 - md0))
        return Image.blend(zoom(c5_frame(t, c5, overlays=False), 1 + 0.30 * p, 0.55, 0.75), photo_frame(t, world), p)
    if t < TL.dip:
        return photo_frame(t, world)
    f = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < TL.dip + 0.12:  # dip to black
        f = Image.blend(photo_frame(t, world), f, ease((t - TL.dip) / 0.12))
    if t >= TL.title:
        s, al = pop(t, TL.title, 0.20)
        paste(f, text("PETŘÍN EXTREME", ANTON, 158, (255, 255, 255, 255), 0, "ltr", None, 1060), W / 2, 880, s, al)
        if t >= TL.title + 0.40:
            s2, a2 = pop(t, TL.title + 0.40, 0.2)
            paste(f, text("לא לבעלי לב חלש. או לב פועם.", HEEBO, 58, (255, 255, 255, 255), 0, "rtl", 800, 900), W / 2, 1030, 1.0, a2)
    return f


def photo_frame(t, world):
    cx, cy, z, blur = world.cam(t)
    shake = 1.0 if (TL.S3_end < t < TL.S4_end) else 0.0
    if blur > 0.05:  # whip pan: average a few samples in time (motion blur)
        acc = None
        for k in range(5):
            cx_, cy_, z_, _ = world.cam(t - 0.012 * k * (1 + 2 * blur))
            fr, _cam = world.view(cx_, cy_, z_)
            a_ = np.asarray(fr.convert("RGB"), dtype=np.float32)
            acc = a_ if acc is None else acc + a_
        f = Image.fromarray((acc / 5).astype(np.uint8)).convert("RGBA")
        cam = (min(max(cx - W / z / 2, 0), W - W / z), min(max(cy - H / z / 2, 0), H - H / z), z)
    else:
        f, cam = world.view(cx, cy, z, shake, t)
    if TL.SCR <= t < TL.SCR + 0.25:  # the white of the washout melts away on the real photo
        f = Image.alpha_composite(f, Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - TL.SCR) / 0.25)))))
    if TL.cap3 <= t < TL.S3_end + 0.05:
        s, al = pop(t, TL.cap3)
        paste(f, text("PRAGUE EXTREME ROLLER COASTER", ANTON, 118, (255, 236, 80, 255), 8, "ltr", None, 960), W / 2, 560, s, al)
    if TL.S3_end - 0.05 <= t < TL.S4_end + 0.2:
        news_graphics(f, t, cam, world)
        if TL.t_L4 + 1.3 <= t:
            s, al = pop(t, TL.t_L4 + 1.3)
            paste(f, text("EXTREME MODE: STAIRS", ANTON, 118, (255, 236, 80, 255), 8, "ltr", None, 960), W / 2, 690, s, al)
    return f


def c5_frame(t, c5, overlays=True):
    f = grade(c5.frame(t), t, grain=3.0, warm=0.4)
    if not overlays:
        return f
    f = heart_monitor(f, t)
    if t >= TL.t_L5 + 1.4:
        s, al = pop(t, TL.t_L5 + 1.4)
        paste(f, text("SURVIVAL RATE: 100%", ANTON, 112, (255, 236, 80, 255), 8, "ltr", None, 960), W / 2, 640, s, al)
    return f


def write_srt(path: Path):
    def ts(x):
        return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round((x % 1) * 1000)) % 1000:03d}"
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(SUBS, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--out-dir", default=str(HERE))
    a = ap.parse_args()
    out = Path(a.out_dir)
    print({k: round(v, 2) for k, v in vars(TL).items() if not k.startswith("_")})
    mix = out / "final_audio.wav"
    build_audio(mix)
    write_srt(out / "narration.srt")
    if not a.audio_only:
        render(out / "final_clean.mp4", out / "final.mp4", mix)
    print("done")
