# Real-life sound for the phone part → assets/foley.wav (48 kHz stereo, final-video seconds).
# Reads the edit times (T) from ui/index.html: notification pings, finger taps, soft swipes, the year counter ticking,
# WhatsApp send/receive, over a quiet early-morning kitchen room tone.
import re, subprocess, numpy as np
SR = 48000; DUR = 57.6
rng = np.random.default_rng(5)
html = open("ui/index.html", encoding="utf-8").read()
blk = html[html.index("const T = window.T"):html.index("};", html.index("const T = window.T"))]
T = {k: float(v) for k, v in re.findall(r"(\w+): ([\d.]+)", blk)}
E = [float(x) for x in re.search(r"E: \[([^\]]+)\]", blk).group(1).split(",")]
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

ping, pop = load("assets/sfx/notification.mp3"), load("assets/sfx/pop.mp3")
for at in (T["nb1"], T["nb2"]): add(buzz(), at - 0.05, 0.12); add(ping, at, 0.28)
for at in [T["tapBlk"]] + [e + T["linkAt"] for e in E] + [T["tapPin"], T["tapShare"], T["pick"], T["send"]]: add(tap(), at, 0.13)
for e in E[1:]: add(swish(), e - 0.5, 0.05)
add(swish(), T["backDay"], 0.04)
YEARS = [2030, 2032, 2031, 2039]
for e, y in zip(E, YEARS):                       # one soft tick per year the counter rolls through (ease-out, like the UI)
    a, b = e + T["futAt"] + 0.35, e + T["futAt"] + 1.25
    for k in range(1, y - 2026 + 1):
        p = 1 - np.sqrt(1 - k / (y - 2026)); add(tick(), a + p * (b - a), 0.06)
add(pop, T["esti"], 0.3); add(ping, T["rachel"], 0.22); add(pop, T["fw"], 0.25)

# room tone: soft brown noise + a far bird
w = np.cumsum(rng.normal(0, 1, len(out))); w -= np.convolve(w, np.ones(4800) / 4800, "same"); w /= np.abs(w).max()
out += np.stack([w, np.roll(w, 900)], 1) * 0.012
for at in (1.2, 6.8, 19.5, 29.0, 44.0):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    chirp = np.sin(2 * np.pi * (3600 + 1400 * np.sin(2 * np.pi * 18 * tt)) * tt) * np.hanning(n)
    for k in range(3): add(chirp, at + k * 0.16, 0.012, pan=-0.6)
fade = np.clip((DUR - np.arange(len(out)) / SR) / 1.0, 0, 1)[:, None]   # the room fades under the signature card
out = np.clip(out * fade, -1, 1)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "assets/foley.wav"], input=out.tobytes(), check=True)
print("foley ok", DUR, "s")
