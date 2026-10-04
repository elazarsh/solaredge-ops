# Real-life sound for the phone part → assets/foley.wav (48 kHz stereo, final-video seconds).
# Reads the edit times (T) and the greeting text from ui/index.html: the phone buzzing on the counter, finger taps, the
# rewind into the past and the whoosh back to today,
# a keyboard click on every keystroke, WhatsApp send/receive, rising chimes on the salary steps, quiet room tone.
import re, subprocess, numpy as np
SR = 48000; DUR = 44.8
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
def click(bright=1.0):
    n = int(0.03 * SR); t = np.arange(n) / SR
    s_ = 0.35 * np.convolve(rng.normal(0, 1, n) * np.exp(-t * 260), np.ones(4) / 4, "same") + 0.5 * np.sin(2 * np.pi * (1800 + 600 * bright) * t) * np.exp(-t * 420) + 0.6 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 90)
    return s_ / np.abs(s_).max()
for at in (0.35, 1.05): add(buzz(), at, 0.22)                           # the reminder buzzes on the counter
for at in (T["tapNotif"], T["tapSave"], T["tapSend"]): add(tap(), at, 0.13)
# flashback: a reversed whoosh + fast reverse ticks into the past, a forward whoosh back to today
wh = load("assets/sfx/whoosh-cinematic.mp3")
add(wh[::-1][-int(1.2 * SR):], 4.85, 0.35)
for j in range(10): add(tick(), 4.95 + j * 0.07, 0.05)
add(wh[: int(1.2 * SR)], 10.3, 0.3)
# keystrokes: same timing as the UI (MSG spread evenly from type0 to send-0.25)
msg = re.search(r'const MSG = "([^"]+)"', html).group(1).replace("\\n", "\n")
chars = list(msg); cps = len(chars) / (T["send"] - 0.25 - T["type0"])
for k, ch in enumerate(chars):
    add(click(rng.uniform(0.6, 1.4) if ch not in " \n" else 0.2), T["type0"] + k / cps + rng.uniform(-0.004, 0.004), 0.14, pan=rng.uniform(-0.15, 0.15))
add(pop, T["send"], 0.3); add(ping, T["mom"], 0.25)
S = T["rows"] + 3 * T["rowStep"]
for j in range(3): add(chime[: int(0.6 * SR)], S + 0.15 + j * 0.3, 0.06 + 0.02 * j)   # the salary steps climb

# room tone: soft brown noise + a far bird
w = np.cumsum(rng.normal(0, 1, len(out))); w -= np.convolve(w, np.ones(4800) / 4800, "same"); w /= np.abs(w).max()
out += np.stack([w, np.roll(w, 900)], 1) * 0.012
for at in (2.2, 8.0, 29.0):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    chirp = np.sin(2 * np.pi * (3600 + 1400 * np.sin(2 * np.pi * 18 * tt)) * tt) * np.hanning(n)
    for k in range(3): add(chirp, at + k * 0.16, 0.012, pan=-0.6)
fade = np.clip((DUR - np.arange(len(out)) / SR) / 1.0, 0, 1)[:, None]   # the room fades under the signature card
out = np.clip(out * fade, -1, 1).astype(np.float32)   # float32! (float64 bytes read as f32le = loud static)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "assets/foley.wav"], input=out.tobytes(), check=True)
print("foley ok", DUR, "s")
