# Real-life sound for the vlog part → assets/foley.wav (48 kHz stereo, final-video seconds).
# Keyboard clicks land exactly on the UI's keystrokes (same typing script as ui/index.html), phone buzz on the wood,
# taps, the WhatsApp send pop and an incoming-message ping, over a quiet kitchen room tone.
import json, re, subprocess, numpy as np
SR = 48000; DUR = 34.3
rng = np.random.default_rng(3)
html = open("ui/index.html", encoding="utf-8").read()
T = {k: float(v) for k, v in re.findall(r"(\w+): ([\d.]+)", html[html.index("const T = window.T"):html.index("};", html.index("const T = window.T"))])}
out = np.zeros((int(SR * DUR), 2), np.float32)

def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); sig = sig[: max(0, len(out) - i)]
    if sig.ndim == 1: sig = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1)
    out[i:i + len(sig)] += sig * gain

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)

def click(bright=1.0):
    n = int(0.03 * SR); t = np.arange(n) / SR
    noise = rng.normal(0, 1, n) * np.exp(-t * 260)
    tick = np.sin(2 * np.pi * (1800 + 600 * bright) * t) * np.exp(-t * 420)
    thump = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 90) * 0.6
    s = 0.35 * np.convolve(noise, np.ones(4) / 4, "same") + 0.5 * tick + thump
    return s / np.abs(s).max()

def buzz(d=0.42):
    n = int(d * SR); t = np.arange(n) / SR
    env = np.clip(t / 0.02, 0, 1) * np.clip((d - t) / 0.04, 0, 1)
    s = np.sign(np.sin(2 * np.pi * 172 * t)) * 0.5 + np.sin(2 * np.pi * 344 * t) * 0.3   # motor + rattle on wood
    s = np.convolve(s, np.ones(24) / 24, "same")
    return s * env

# typing script (mirrors ui/index.html)
ev = []; t = T["type0"]
def typ(s, cps):
    global t
    for ch in s: ev.append((t, ch)); t += 1 / cps
def dele(n, cps):
    global t
    for _ in range(n): ev.append((t, "⌫")); t += 1 / cps
typ("רחלי, את טועה", 13 / (T["del0"] - T["type0"] - 0.25)); t = max(t, T["del0"]); dele(7, 1 / T["delStep"]); t += 0.35
typ("נראה לי שאת טועה 🙂", 14); t += 0.25; typ("\n", 10)
typ("אני כמעט בטוחה ששלחו על זה הודעה בקבוצת העדכונים", 22)
for at, ch in ev:
    add(click(rng.uniform(0.6, 1.4) if ch not in " ⌫\n" else 0.2), at + rng.uniform(-0.004, 0.004), 0.16 if ch != " " else 0.2, pan=rng.uniform(-0.15, 0.15))

# phone on the table
for at in (0.15, T["n2"], T["n3"]): add(buzz(), at - 0.05, 0.22)
for at in (T["open"], T["sel"], T["back"], T["tapB"], T["fwd"], T["pick"], T["fsend"]): add(click(0.3), at, 0.12)
pop, ping = load("../ep1-forwarded/assets/sfx/pop.mp3"), load("../ep1-forwarded/assets/sfx/notification.mp3")
add(pop, T["send"], 0.35); add(pop, T["fwIn"], 0.3); add(ping, T["oops"], 0.3)

# room tone: soft brown noise + a far bird, never silent
w = np.cumsum(rng.normal(0, 1, len(out))); w -= np.convolve(w, np.ones(4800) / 4800, "same"); w /= np.abs(w).max()
out += np.stack([w, np.roll(w, 900)], 1) * 0.012
for at in (5.2, 13.8, 22.5):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    chirp = np.sin(2 * np.pi * (3600 + 1400 * np.sin(2 * np.pi * 18 * tt)) * tt) * np.hanning(n)
    for k in range(3): add(chirp, at + k * 0.16, 0.012, pan=-0.6)
out = np.clip(out, -1, 1)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "assets/foley.wav"], input=out.tobytes(), check=True)
print("foley:", len(ev), "keystrokes, typing", round(ev[0][0], 2), "→", round(ev[-1][0], 2), "s")
