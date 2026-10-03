# Real-life sound for the phone part → assets/foley.wav (48 kHz stereo, final-video seconds).
# Reads the edit times (T) from ui/index.html: finger taps, soft swipes, dictation on/off ticks, the age counter ticking,
# a pop when a follow-up is saved, rising chimes on the salary steps, over a quiet early-morning kitchen room tone.
import re, subprocess, numpy as np
SR = 48000; DUR = 51.8
rng = np.random.default_rng(5)
html = open("ui/index.html", encoding="utf-8").read()
blk = html[html.index("const T = window.T"):html.index("};", html.index("const T = window.T"))]
T = {k: float(v) for k, v in re.findall(r"(\w+): ([\d.]+)", blk)}
out = np.zeros((int(SR * DUR), 2), np.float32)

def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); sig = sig[: max(0, len(out) - i)]
    if sig.ndim == 1: sig = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1)
    out[i:i + len(sig)] += sig * gain

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)

def tap(bright=0.3):
    n = int(0.03 * SR); t = np.arange(n) / SR
    s = 0.35 * np.convolve(rng.normal(0, 1, n) * np.exp(-t * 260), np.ones(4) / 4, "same") \
        + 0.5 * np.sin(2 * np.pi * (1800 + 600 * bright) * t) * np.exp(-t * 420) + 0.6 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 90)
    return s / np.abs(s).max()

def tick():
    n = int(0.012 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 600)

def swish(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    s = np.convolve(rng.normal(0, 1, n), np.ones(40) / 40, "same") * np.sin(np.pi * t / d) ** 2
    return s / np.abs(s).max()

def buzz(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    env = np.clip(t / 0.02, 0, 1) * np.clip((d - t) / 0.04, 0, 1)
    s = np.sin(2 * np.pi * 150 * t) * 0.6 + np.sin(2 * np.pi * 300 * t) * 0.2
    return s * env

ping, pop, chime = load("assets/sfx/notification.mp3"), load("assets/sfx/pop.mp3"), load("assets/sfx/chime.mp3")
K = [float(x) for x in re.search(r"K: \[([^\]]+)\]", blk).group(1).split(",")]
AGES = [(2, 6), (2, 7), (2, 6), (2, 15)]
for at in [T["toDay"] - 0.15, T["tapBlk"], T["tapMine"]] + [k + T["tapR"] for k in K]: add(tap(), at, 0.13)
for k in K[1:]: add(swish(), k - 0.5, 0.05)
add(swish(), T["backDay"], 0.04)
for k, (a0, a1) in zip(K, AGES):
    add(tick(), k + 0.2, 0.05); add(tick(), k + T["okAt"], 0.05)          # dictation on / off
    a, b = k + T["roll0"], k + T["roll1"]
    for j in range(1, a1 - a0 + 1):                                         # one soft tick per year of age (ease-out like the UI)
        p = 1 - np.sqrt(1 - j / (a1 - a0)); add(tick(), a + p * (b - a), 0.06)
    add(pop, k + T["savedAt"], 0.18)
S = T["mine"] + 0.6 + 3 * T["mineStep"]
for j in range(3): add(chime[: int(0.6 * SR)], S + 0.15 + j * 0.3, 0.06 + 0.02 * j)   # the salary steps climb

# room tone: soft brown noise + a far bird
w = np.cumsum(rng.normal(0, 1, len(out))); w -= np.convolve(w, np.ones(4800) / 4800, "same"); w /= np.abs(w).max()
out += np.stack([w, np.roll(w, 900)], 1) * 0.012
for at in (1.2, 6.8, 19.5, 29.0, 44.0):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    chirp = np.sin(2 * np.pi * (3600 + 1400 * np.sin(2 * np.pi * 18 * tt)) * tt) * np.hanning(n)
    for k in range(3): add(chirp, at + k * 0.16, 0.012, pan=-0.6)
fade = np.clip((DUR - np.arange(len(out)) / SR) / 1.0, 0, 1)[:, None]   # the room fades under the signature card
out = np.clip(out * fade, -1, 1).astype(np.float32)   # float32! (float64 bytes read as f32le = loud static)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "assets/foley.wav"], input=out.tobytes(), check=True)
print("foley ok", DUR, "s")
