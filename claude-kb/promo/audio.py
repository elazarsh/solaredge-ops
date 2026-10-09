#!/usr/bin/env python3
"""Generates a 30 s synthetic ad soundtrack (pad + arpeggio + kick/hat + riser + hits). No samples, no copyright issues.
Usage: audio.py out.wav"""
import sys
import numpy as np

SR, DUR, BPM = 44100, 30.0, 120
N = int(SR * DUR)
t = np.arange(N) / SR
beat = 60 / BPM
rng = np.random.default_rng(7)

def env_adsr(n, a=0.01, d=0.1, s=0.6, r=0.1):
    e = np.ones(n)
    ai, di, ri = int(a*SR), int(d*SR), int(r*SR)
    e[:ai] = np.linspace(0, 1, ai) if ai else e[:ai]
    e[ai:ai+di] = np.linspace(1, s, di)[:max(0, n-ai)][:len(e[ai:ai+di])]
    e[ai+di:] = s
    if ri and ri < n: e[-ri:] *= np.linspace(1, 0, ri)
    return e

def midi(m): return 440 * 2 ** ((m - 69) / 12)

mix = np.zeros(N)

# Pad: Am - F - C - G, 4 beats (2 s) each
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
for bar in range(int(DUR / (4*beat)) + 1):
    start = int(bar * 4 * beat * SR)
    ch = chords[bar % 4]
    n = min(int(4 * beat * SR), N - start)
    if n <= 0: break
    seg = np.zeros(n); tt = np.arange(n) / SR
    for m in ch:
        f = midi(m)
        seg += np.sin(2*np.pi*f*tt) + 0.5*np.sin(2*np.pi*f*2.003*tt) + 0.3*np.sin(2*np.pi*f*0.998*tt)
    seg *= env_adsr(n, a=0.4, d=0.3, s=0.8, r=0.4) / 6
    mix[start:start+n] += seg * 0.55

# Arpeggio (8ths) from 3.6 s
arp_start = 3.6
step = beat / 2
k = 0
x = arp_start
while x < DUR - 0.5:
    ch = chords[int((x // (4*beat)) % 4)]
    m = ch[[0, 1, 2, 1][k % 4]] + 12
    n = int(step * 1.4 * SR); s = int(x * SR)
    n = min(n, N - s)
    if n <= 0: break
    tt = np.arange(n) / SR; f = midi(m)
    note = (np.sin(2*np.pi*f*tt) + 0.4*np.sign(np.sin(2*np.pi*f*tt))*0.3) * env_adsr(n, 0.005, 0.08, 0.3, 0.05)
    mix[s:s+n] += note * 0.16
    x += step; k += 1

def kick(s):
    n = int(0.35 * SR); n = min(n, N - s)
    if n <= 0: return
    tt = np.arange(n) / SR
    f = 55 + 120 * np.exp(-tt * 28)
    ph = 2*np.pi*np.cumsum(f)/SR
    mix[s:s+n] += np.sin(ph) * np.exp(-tt * 9) * 0.85

def hat(s, g=0.12):
    n = int(0.06 * SR); n = min(n, N - s)
    if n <= 0: return
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0)  # crude highpass
    mix[s:s+n] += noise * np.exp(-np.arange(n)/SR * 60) * g

def bass(s, m, length):
    n = min(int(length * SR), N - s)
    if n <= 0: return
    tt = np.arange(n) / SR
    mix[s:s+n] += np.sin(2*np.pi*midi(m)*tt) * env_adsr(n, 0.01, 0.1, 0.7, 0.05) * 0.38

# Drums + bass: kick from 3.6 s on beats; hats on off-beats from 8.6 s; bass from 8.6 s
b = 3.6
while b < DUR - 0.2:
    kick(int(b * SR))
    b += beat
b = 8.6 + beat / 2
while b < DUR - 0.2:
    hat(int(b * SR)); b += beat
b = 8.6
while b < DUR - 0.3:
    ch = chords[int((b // (4*beat)) % 4)]
    bass(int(b * SR), ch[0] - 12, beat * 0.9); b += beat

# Scene-change whooshes / hits at scene boundaries
for tc in (3.6, 8.6, 14.6, 20.6, 26.2):
    s = int(tc * SR); n = int(0.5 * SR); n = min(n, N - s)
    noise = rng.standard_normal(n)
    sweep = np.cumsum(noise) * 0  # placeholder for clarity
    tt = np.arange(n) / SR
    whoosh = rng.standard_normal(n) * np.exp(-tt * 7) * 0.10
    mix[s:s+n] += whoosh
    kick(s)

# Riser into the CTA (22.2 -> 26.2)
rs, re_ = int(22.2 * SR), int(26.2 * SR)
n = re_ - rs
tt = np.arange(n) / SR
f = 200 + 1800 * (tt / (n / SR)) ** 2
ph = 2*np.pi*np.cumsum(f)/SR
mix[rs:re_] += np.sin(ph) * np.linspace(0, 1, n) ** 2 * 0.12
# Final hit
s = int(26.2 * SR); n = int(1.6 * SR); n = min(n, N - s); tt = np.arange(n) / SR
for m in (45, 57, 64, 69):
    mix[s:s+n] += np.sin(2*np.pi*midi(m)*tt) * np.exp(-tt * 1.6) * 0.12

# Intro/outro fades, soft limiter, normalise
fade_in = np.clip(t / 0.4, 0, 1); fade_out = np.clip((DUR - t) / 1.2, 0, 1)
mix *= fade_in * fade_out
mix = np.tanh(mix * 1.4)
mix /= np.max(np.abs(mix)) / 0.89

# Simple stereo widening
left = mix; right = np.roll(mix, int(0.012 * SR)) * 0.96
st = np.stack([left, right], axis=1)
pcm = (st * 32767).astype('<i2')
import wave
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1], f'{DUR}s')
