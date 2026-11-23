#!/usr/bin/env python3
"""Synthesise the whole soundtrack (no external assets, no narration).
Timeline is shared with timeline.js. Output: build/audio.wav (48k stereo)."""
import numpy as np, wave, sys

SR = 48000
D = 90.0
N = int(SR * D)
rng = np.random.default_rng(7)
mix = np.zeros((2, N), dtype=np.float64)


def tt(dur):
    return np.arange(int(SR * dur)) / SR


def lp(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def hp(x, fc):
    return x - lp(x, fc)


def noise(dur):
    return rng.standard_normal(int(SR * dur))


def pink(dur):
    n = noise(dur)
    X = np.fft.rfft(n)
    f = np.fft.rfftfreq(len(n), 1 / SR)
    f[0] = 1
    X /= np.sqrt(f)
    p = np.fft.irfft(X, len(n))
    return p / np.max(np.abs(p))


def env_fade(x, fi=0.0, fo=0.0):
    e = np.ones(len(x))
    a, b = int(fi * SR), int(fo * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if b:
        e[-b:] = np.minimum(e[-b:], np.linspace(1, 0, b))
    return x * e


def place(x, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    seg = x[: N - i] * gain
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    mix[0, i:i + len(seg)] += seg * l
    mix[1, i:i + len(seg)] += seg * r


def echo(x, delay=0.23, fb=0.45, n=6):
    out = x.copy()
    pad = int(delay * SR)
    cur = x
    for k in range(1, n + 1):
        cur = np.concatenate([np.zeros(pad), cur]) * fb
        out = np.concatenate([out, np.zeros(len(cur) - len(out))]) if len(cur) > len(out) else out
        out[: len(cur)] += cur
    return out


def boom(dur=3.0, f=70):
    t = tt(dur)
    n = lp(noise(dur), 220)
    tone = np.sin(2 * np.pi * (f + 40 * np.exp(-t * 6)) * t)
    e = np.exp(-t * 1.6)
    b = (n * 1.5 + tone) * e
    b[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    return b / np.max(np.abs(b))


def siren(dur, base=640, depth=260, period=9.0):
    t = tt(dur)
    w = 2 * np.pi / period
    phase = 2 * np.pi * base * t - (2 * np.pi * depth / w) * np.cos(w * t)
    s = np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    s = lp(s, 2600)
    return s / np.max(np.abs(s))


def chirp(f0=3200, f1=4300, dur=0.12):
    t = tt(dur)
    ph = 2 * np.pi * (f0 * t + (f1 - f0) * t ** 2 / (2 * dur))
    return np.sin(ph) * np.sin(np.pi * t / dur) ** 2


def beep(f, dur=0.18, g=1.0):
    t = tt(dur)
    return env_fade(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t), 0.005, 0.03) * g


def static_burst(dur=0.25):
    x = hp(noise(dur), 1500)
    return env_fade(x / np.max(np.abs(x)), 0.005, dur * 0.7)


def whoosh(dur=1.2):
    n = noise(dur)
    t = tt(dur)
    out = np.zeros_like(n)
    # sweep via cross-fading band-passed layers
    for i, fc in enumerate([300, 800, 2000, 5000]):
        b = lp(n, fc * 1.5) - lp(n, fc / 1.5)
        c = np.exp(-((t - dur * (0.2 + 0.2 * i)) / 0.25) ** 2)
        out += b * c
    return out / np.max(np.abs(out))


# ---------------------------------------------------------------- S1 routine (2-15)
amb = lp(pink(14.0), 900) * 0.10
amb = env_fade(amb, 1.5, 0.8)
place(amb, 2.3, 1.0)
for s in np.arange(3.0, 13.5, 0.9):
    if rng.random() < 0.6:
        k = rng.integers(2, 5)
        for j in range(k):
            f0 = rng.uniform(2800, 3800)
            place(chirp(f0, f0 + rng.uniform(-800, 1200), rng.uniform(0.07, 0.14)), s + j * 0.16, 0.05, rng.uniform(-0.8, 0.8))
place(boom(2.0, 55), 2.3, 0.10)

# ---------------------------------------------------------------- S2 sirens (14.3-34.3)
sir = env_fade(siren(19.5, 640, 260, 8.0), 1.5, 3.0)
sir_r = echo(sir * 0.5, 0.31, 0.4, 3)[: len(sir)]
place(sir, 14.8, 0.30, -0.3)
place(sir_r, 14.8, 0.22, 0.3)
sir2 = env_fade(siren(16.0, 590, 230, 10.0), 2.0, 3.0)
place(lp(sir2, 1800), 16.0, 0.12, 0.6)
for tb, g in [(21.0, 0.55), (25.0, 0.45), (28.5, 0.6), (31.2, 0.35)]:
    place(boom(3.0, 62), tb, g, rng.uniform(-0.4, 0.4))
for s in np.arange(18, 31, 0.9):
    place(boom(0.6, 48), s, 0.10)

# ---------------------------------------------------------------- S3 news (33.8-58.3)
place(whoosh(1.2), 33.5, 0.35)
place(boom(2.5, 48), 33.9, 0.4)
t = tt(24.5)
drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t) + 0.25 * np.sin(2 * np.pi * 110 * t + np.sin(t * 0.5)))
drone *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.125 * t))
drone = env_fade(drone / np.max(np.abs(drone)), 1.5, 1.5)
place(drone, 33.8, 0.20)
tm, step = 36.3, 0.8
while tm < 50.0:
    place(beep(1320, 0.05, 0.5), tm, 0.05)
    tm += step
    step = max(0.3, step * 0.95)
for ts in (36.3, 41.3, 46.3):
    place(whoosh(0.7), ts - 0.2, 0.18)
    place(beep(660, 0.12), ts, 0.12)
    place(beep(990, 0.18), ts + 0.12, 0.12)
place(boom(4.0, 45), 50.5, 0.8)
for k in range(4):
    place(beep(880 if k % 2 == 0 else 660, 0.22), 50.6 + k * 0.28, 0.22)
place(whoosh(1.0), 50.3, 0.3)

# ---------------------------------------------------------------- S4 live (57.8-84.3)
place(whoosh(1.2), 57.5, 0.3)
n4 = 27.0
wind = lp(pink(n4), 600) * 0.16 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * tt(n4)))
place(env_fade(wind, 1.2, 2.0), 57.8, 1.0)
crack = np.zeros(int(n4 * SR))
for _ in range(550):
    i2 = rng.integers(0, len(crack) - 400)
    L = rng.integers(40, 300)
    crack[i2:i2 + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1.0)
crack = hp(crack, 800)
place(env_fade(crack / np.max(np.abs(crack)), 1.2, 2.0), 57.8, 0.10)
place(lp(env_fade(siren(24.0, 600, 220, 12.0), 3.0, 4.0), 1200), 59.0, 0.05, -0.6)
for ts in (64.0, 67.5, 71.0, 74.5, 78.0, 81.0):
    place(whoosh(0.6), ts - 0.32, 0.30, rng.uniform(-0.5, 0.5))
    place(static_burst(0.18), ts - 0.05, 0.08)
for ts in (66.0, 72.5, 77.0, 82.0):
    place(static_burst(0.12), ts, 0.10)
    place(beep(1700, 0.09), ts + 0.1, 0.08)
    place(static_burst(0.3), ts + 1.2, 0.09)
place(whoosh(2.5), 59.0, 0.3)
place(boom(3.0, 58), 61.0, 0.5)

# ---------------------------------------------------------------- S5 end (83.8-90)
t = tt(6.2)
pulse = np.sin(2 * np.pi * 48 * t) * np.maximum(0, np.sin(2 * np.pi * 0.9 * t)) ** 6
pulse = env_fade(pulse, 0.4, 2.0)
place(pulse, 83.8, 0.6)
for ts in (84.4, 85.9, 87.3):
    place(boom(2.5, 52), ts, 0.45)
    place(echo(beep(440, 0.4, 1.0), 0.4, 0.35, 3), ts + 0.1, 0.05)

# ---------------------------------------------------------------- master
mix[0] = lp(mix[0], 14000)
mix[1] = lp(mix[1], 14000)
peak = np.max(np.abs(mix))
mix *= 0.89 / peak
# gentle master fade
mix[:, :int(1.0 * SR)] *= np.linspace(0, 1, int(1.0 * SR))
mix[:, -int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
pcm = (mix.T * 32767).astype(np.int16)
out = sys.argv[1] if len(sys.argv) > 1 else "build/audio.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", out, "peak before norm", round(float(peak), 2))
