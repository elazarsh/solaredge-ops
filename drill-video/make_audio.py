#!/usr/bin/env python3
"""Synthesise the whole soundtrack (no external assets, no narration).
Timeline is shared with timeline.js. Output: build/audio.wav (48k stereo)."""
import numpy as np, wave, sys

SR = 48000
D = 59.0
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


# ---------------------------------------------------------------- S1 routine (2-11)
amb = env_fade(lp(pink(10.0), 900) * 0.10, 1.2, 0.8)
place(amb, 2.1, 1.0)
for s in np.arange(2.8, 10.5, 0.9):
    if rng.random() < 0.6:
        k = rng.integers(2, 5)
        for j in range(k):
            f0 = rng.uniform(2800, 3800)
            place(chirp(f0, f0 + rng.uniform(-800, 1200), rng.uniform(0.07, 0.14)), s + j * 0.16, 0.05, rng.uniform(-0.8, 0.8))
place(boom(2.0, 55), 2.1, 0.10)

# ---------------------------------------------------------------- S2 alert, pushes, strike (10.5-31.5)
TI = 26.0
sir = siren(26.0 - 11.2 + 0.4, 640, 260, 8.0)
sir_pre = env_fade(sir, 1.5, 0.05)
place(sir_pre, 11.2, 0.30, -0.3)
place(echo(sir_pre * 0.5, 0.31, 0.4, 3)[: len(sir_pre)], 11.2, 0.20, 0.3)
sir_post = env_fade(lp(siren(8.0, 640, 260, 8.0), 650), 2.5, 2.5)     # muffled after the blast
place(sir_post, TI + 0.2, 0.30, -0.2)
sir2 = env_fade(siren(15.0, 590, 230, 10.0), 2.0, 2.0)
place(lp(sir2, 1800), 12.5, 0.12, 0.6)
# phone-style notification pings
for tp in (13.5, 16.2, 18.9, 21.6):
    place(beep(1046, 0.14), tp, 0.20)
    place(beep(1568, 0.22), tp + 0.14, 0.20)
# distant booms
for tb, g in [(16.8, 0.35), (19.5, 0.40), (22.2, 0.50)]:
    place(boom(3.0, 62), tb, g, rng.uniform(-0.4, 0.4))
# incoming whistle (falling pitch, rising level), 1.7 s
tw = tt(1.7)
f = 3200 - 2300 * (tw / 1.7) ** 1.3
wh = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR)
wh = lp(wh + 0.35 * hp(noise(1.7), 2500), 4500) * (tw / 1.7) ** 2
place(wh / np.max(np.abs(wh)), TI - 1.7, 0.45)
place(boom(2.0, 38) * 0.2, TI - 1.0, 0.5)       # rumble building up
# IMPACT
place(boom(6.0, 36), TI, 1.0)
place(boom(4.0, 70), TI + 0.02, 0.7)
place(static_burst(0.5) * 1.0, TI, 0.5)          # sharp crack
deb = np.zeros(int(3.0 * SR))
for _ in range(500):
    i2 = rng.integers(int(0.15 * SR), len(deb) - 600)
    L = rng.integers(60, 500)
    deb[i2:i2 + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1.0) * np.exp(-i2 / SR / 1.2)
deb = hp(deb, 500)
place(deb / np.max(np.abs(deb)), TI + 0.1, 0.45)                       # debris falling
for tg in (TI + 0.4, TI + 0.9, TI + 1.6):                                # glass
    gl = hp(noise(0.35), 3500) * np.exp(-tt(0.35) * 12)
    place(gl / np.max(np.abs(gl)), tg, 0.25, rng.uniform(-0.6, 0.6))
tn = tt(5.0)                                                              # tinnitus
tin = np.sin(2 * np.pi * 7600 * tn) * np.exp(-tn / 1.8) * np.minimum(1, tn / 0.05)
place(tin, TI + 0.15, 0.10)
# breaking sting
place(boom(3.0, 45), TI + 3.5, 0.5)
for k in range(4):
    place(beep(880 if k % 2 == 0 else 660, 0.22), TI + 3.6 + k * 0.28, 0.22)

# ---------------------------------------------------------------- S4 live (31-52.5)
place(whoosh(1.2), 30.8, 0.3)
n4 = 21.5
wind = lp(pink(n4), 600) * 0.16 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * tt(n4)))
place(env_fade(wind, 1.2, 2.0), 31.0, 1.0)
crack = np.zeros(int(n4 * SR))
for _ in range(450):
    i2 = rng.integers(0, len(crack) - 400)
    L = rng.integers(40, 300)
    crack[i2:i2 + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1.0)
crack = hp(crack, 800)
place(env_fade(crack / np.max(np.abs(crack)), 1.2, 2.0), 31.0, 0.10)
place(lp(env_fade(siren(18.0, 600, 220, 12.0), 3.0, 4.0), 1200), 32.0, 0.05, -0.6)
for ts in (31.3, 34.8, 38.3, 41.8, 45.3, 48.8):
    place(whoosh(0.6), ts - 0.32, 0.30, rng.uniform(-0.5, 0.5))
    place(static_burst(0.18), ts - 0.05, 0.08)
for ts in (36.0, 43.0, 47.5, 51.0):
    place(static_burst(0.12), ts, 0.10)
    place(beep(1700, 0.09), ts + 0.1, 0.08)
    place(static_burst(0.3), ts + 1.2, 0.09)

# ---------------------------------------------------------------- S5 end (52-59)
t = tt(7.0)
pulse = np.sin(2 * np.pi * 48 * t) * np.maximum(0, np.sin(2 * np.pi * 0.9 * t)) ** 6
place(env_fade(pulse, 0.4, 2.0), 52.0, 0.6)
for ts in (52.6, 54.1, 55.5):
    place(boom(2.5, 52), ts, 0.45)
    place(echo(beep(440, 0.4, 1.0), 0.4, 0.35, 3), ts + 0.1, 0.05)

# ---------------------------------------------------------------- master
mix[0] = lp(mix[0], 14000)
mix[1] = lp(mix[1], 14000)
mix = np.tanh(mix * 1.15)          # soft limiter: keeps the quiet scenes audible next to the blast
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
