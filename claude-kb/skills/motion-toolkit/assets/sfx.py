#!/usr/bin/env python3
"""Procedural sound design for motion videos (numpy only, no samples, no licensing issues).
Builds an SFX bus from a cue sheet (cues.json written by render.js from HF.cue(...)) plus a beat-locked music bed.

Usage: sfx.py cues.json out.wav [--duration 32] [--bpm 120] [--energy "0:0.3,4:0.8,28:1"] [--key A] [--no-music] [--sfx-gain 1.0] [--music-gain 1.0]
                                [--lufs -15] [--ceiling -2.0]
Cue types: slam, whoosh(dur,dir), riser(dur), tick(pitch), key, pop, glitch(dur), shimmer, hit(power), swell(dur), click
Energy map = piecewise-constant music intensity: <0.35 pad only, >=0.35 kick, >=0.55 bass+arp, >=0.7 hats+clap, >=0.9 extra layers.

CUE TIME SEMANTICS: cue.t is where the sound LANDS / PEAKS, not where it starts.
  riser, swell : placed with lead = dur -> the sound STARTS at t - dur and PEAKS (ends) exactly at t.
                 Cue a riser at the hit time it builds into (e.g. riser t=29, dur=2 with a hit at t=29), not where the build begins.
  whoosh       : starts at t - 0.45*dur, so its loudest point is ~at t (mid-move).
  all others   : the transient starts at t.

MASTER CHAIN (replaces the old tanh(x*1.25) overdrive + peak-normalise, which clipped ~1 % of samples and measured ~-2.5 LUFS / +6.5 dBTP):
  1. SFX bus = soft_limit(reverb(one-shots) * SFX_BUS) * --sfx-gain. soft_limit = look-ahead-free soft-knee limiter (instant attack,
     dB-linear release). The noise sweeps (riser/whoosh) have ~13 dB crest factor; this tames them without ducking the music bed.
  2. Music bus = music * MUSIC_BUS * --music-gain. Sum, low-pass 16-17.5 kHz (lossy codecs cut there anyway; doing it before the
     limiter keeps the encoded true peak honest), end fade, static headroom trim so peaks <= -3 dBFS.
  3. Integrated loudness (ITU-R BS.1770-4 gating: 400 ms blocks, 75 % overlap, -70 LUFS absolute and -10 LU relative gates).
     K-weighting approximation: the magnitude response of the two BS.1770 48 kHz biquads (shelf + RLB high-pass) applied
     zero-phase in the FFT domain; the phase is ignored, which only matters at the 0.1 LU level. Gain -> --lufs.
  4. Final limiter: stereo-linked, look-ahead gain smoothing; detector = 4x FFT-oversampled peaks (true-peak-ish), ceiling --ceiling dBTP.
     The loudness gain is re-trimmed after limiting so the output lands on --lufs. build.sh then runs ffmpeg loudnorm (linear) to -14 LUFS."""
import sys, json, argparse
import numpy as np

SR = 48000
rng = np.random.default_rng(11)

def tax(d): return np.arange(int(SR * d)) / SR

def fft_filter(x, fn):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X * fn(f), len(x))

def lowpass(x, fc): return fft_filter(x, lambda f: 1 / (1 + (f / fc) ** 4))
def highpass(x, fc): return fft_filter(x, lambda f: (f / fc) ** 4 / (1 + (f / fc) ** 4))

def sweep_noise(dur, f0, f1, width=0.55, curve=1.4):
    """Band-limited noise whose center frequency glides f0->f1 (STFT overlap-add)."""
    n = int(SR * dur); x = rng.standard_normal(n); win = 2048; hop = 512
    out = np.zeros(n + win); w = np.hanning(win); fr = np.fft.rfftfreq(win, 1 / SR) + 1e-6
    for s in range(0, n, hop):
        p = (s / max(1, n)) ** curve; fc = f0 * (f1 / f0) ** p
        seg = np.zeros(win); seg[: min(win, n - s)] = x[s : s + win][: min(win, n - s)]
        g = np.exp(-((np.log(fr / fc)) ** 2) / (2 * width ** 2))
        out[s : s + win] += np.fft.irfft(np.fft.rfft(seg * w) * g, win) * w
    return out[:n]

def pan(mono, p0, p1=None):
    """Equal-power pan, p in [-1,1]; p1 animates the pan across the clip."""
    n = len(mono); p = np.linspace(p0, p1 if p1 is not None else p0, n); a = (p + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)], axis=1)

def reverb(st, rt=1.4, wet=0.2):
    """Noise-IR plate. L and R use independent (decorrelated) IRs; the old R = -L IR made the wet signal exactly anti-phase,
    which cancels in mono (phone speakers) and made the 160 kbps AAC encode overshoot the true peak by up to ~5 dB."""
    n = int(SR * rt); dec = np.exp(-np.arange(n) / SR * (6.9 / rt))
    irs = (highpass(rng.standard_normal(n) * dec, 150) * 0.15, highpass(np.random.default_rng(12).standard_normal(n) * dec, 150) * 0.15)
    out = np.zeros_like(st)
    for c in range(2):
        L = len(st) + n; Lp = 1 << (L - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(st[:, c], Lp) * np.fft.rfft(irs[c], Lp), Lp)[: len(st)]
        out[:, c] = y
    return st * (1 - wet) + out * wet * 3.0

# ---------------- one-shots (return mono arrays) ----------------
def impact(power=0.8):
    t = tax(1.8); f = 42 + 150 * np.exp(-t * 22); body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.2)
    crack = highpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 55) * 0.55
    sub = lowpass(np.sin(2 * np.pi * 36 * t) * np.exp(-t * 1.9), 120) * 0.9
    return (body * 0.9 + crack + sub) * power

def whoosh(dur=0.6, d=1):
    a = sweep_noise(dur, 350, 7000, 0.7, 1.6) if d >= 0 else sweep_noise(dur, 7000, 350, 0.7, 1.6)
    t = tax(dur); env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2.2
    return a * env * 2.2

def riser(dur=2.0):
    n = sweep_noise(dur, 250, 9000, 0.9, 2.0); t = tax(dur); p = t / dur
    f = 180 * 2 ** (3.2 * p); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (n * 1.8 + tone) * (p ** 2.2) * (1 + 0.25 * np.sin(2 * np.pi * (6 + 18 * p) * t))

def swell(dur=1.2):
    t = tax(dur); return highpass(rng.standard_normal(len(t)), 1500) * (t / dur) ** 3 * 0.5

def tick(pitch=1.0):
    t = tax(0.05); return np.sin(2 * np.pi * 1700 * pitch * t) * np.exp(-t * 130) * 0.5 + highpass(rng.standard_normal(len(t)), 4000) * np.exp(-t * 300) * 0.25

def key():
    t = tax(0.03); return highpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 220) * 0.35

def click():
    t = tax(0.02); return highpass(rng.standard_normal(len(t)), 1500) * np.exp(-t * 400) * 0.6

def pop(power=0.7):
    t = tax(0.25); f = 380 + 700 * (1 - np.exp(-t * 30)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.5 * power + highpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 100) * 0.2

def shimmer():
    t = tax(1.4); out = np.zeros(len(t))
    for i, f in enumerate([2093, 2637, 3136, 3951, 5274]):
        s = 0.05 * i; out += np.sin(2 * np.pi * f * (1 + 0.002 * i) * t) * np.exp(-np.clip(t - s, 0, None) * 4.5) * (t >= s) * (0.5 / (1 + i * 0.4))
    return out * 0.5

def glitch(dur=0.35):
    t = tax(dur); x = np.sign(np.sin(2 * np.pi * 220 * t * (1 + 4 * rng.random()))) * 0.25
    x += highpass(rng.standard_normal(len(t)), 2000) * 0.35
    gate = (np.floor(t * 38) % 2 == 0) * np.exp(-t * 6); step = 24; crushed = np.round(x * step) / step
    return crushed * gate

def hit(power=1.0):
    t = tax(3.0); chord = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 1.6) for f in (55, 110, 164.8, 220, 329.6)) * 0.18
    imp = impact(power); sh = shimmer()
    return chord + np.pad(imp, (0, len(t) - len(imp)))[: len(t)] + np.pad(sh, (0, len(t) - len(sh)))[: len(t)] * 0.6

ONE = {'slam': lambda c: (impact(c.get('power', 0.8)), 0), 'hit': lambda c: (hit(c.get('power', 1.0)), 0),
       'whoosh': lambda c: (whoosh(c.get('dur', 0.6), c.get('dir', 1)), c.get('dir', 1)), 'riser': lambda c: (riser(c.get('dur', 2.0)), 0),
       'swell': lambda c: (swell(c.get('dur', 1.2)), 0), 'tick': lambda c: (tick(c.get('pitch', 1.0)), 0), 'key': lambda c: (key(), 0),
       'click': lambda c: (click(), 0), 'pop': lambda c: (pop(c.get('power', 0.7)), 0), 'shimmer': lambda c: (shimmer(), 0), 'glitch': lambda c: (glitch(c.get('dur', 0.35)), 0)}

def place(buf, mono, t0, p0=0.0, p1=None, gain=1.0, lead=0.0):
    """Mix mono clip into stereo buf starting at t0 - lead (so the transient lands on t0). Risers/swells: lead=duration so they START at
    t0 - duration and PEAK at t0 (cue.t = peak/landing time, see module docstring)."""
    st = pan(mono * gain, p0, p1); s = int((t0 - lead) * SR)
    if s < 0: st = st[-s:]; s = 0
    e = min(len(buf), s + len(st))
    if e > s: buf[s:e] += st[: e - s]          # cues past the end of the timeline are dropped

# ---------------- music ----------------
NOTE = {'A': 57, 'C': 60, 'D': 62, 'E': 64, 'F': 53, 'G': 55}
def mid(m): return 440 * 2 ** ((m - 69) / 12)

def energy_at(emap, t):
    e = 0.3
    for tt, v in emap:
        if t >= tt: e = v
    return e

def music(dur, bpm, emap, key='A'):
    n = int(SR * dur); beat = 60 / bpm; out = np.zeros((n, 2)); kicks = []
    root = NOTE.get(key, 57); prog = [(0, 'm'), (-4, ''), (3, ''), (-2, '')]   # i - VI - III - VII (minor feel)
    def chord(r, q): return [r, r + (3 if q == 'm' else 4), r + 7]
    # pad (additive, lowpassed) - 1 chord per bar
    for b in range(int(dur / (4 * beat)) + 1):
        t0 = b * 4 * beat; s = int(t0 * SR); L = min(int(4 * beat * SR), n - s)
        if L <= 0: break
        r, q = prog[b % 4]; tt = np.arange(L) / SR; x = np.zeros(L)
        for m in chord(root + r, q):
            for h, a in ((1, 1), (2, 0.5), (3, 0.28), (4, 0.15)):
                x += a * np.sin(2 * np.pi * mid(m) * h * tt * (1 + 0.0015 * (b % 3)) + h) + a * 0.6 * np.sin(2 * np.pi * mid(m) * h * tt * 0.997)
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (4 * beat - tt) / 0.5); pd = lowpass(x, 1800) * env * 0.045
        e = energy_at(emap, t0); out[s : s + L, 0] += pd * (0.8 + 0.2 * min(1, e)); out[s : s + L, 1] += np.roll(pd, 190) * (0.8 + 0.2 * min(1, e))
    # drums / arp / bass on a 16th grid
    step = beat / 4; k = 0; t = 0.0
    while t < dur - 0.05:
        e = energy_at(emap, t); s = int(t * SR); bar = int(t // (4 * beat)); r, q = prog[bar % 4]; ch = chord(root + r, q); pos = k % 16
        if e >= 0.35 and pos % 4 == 0:  # four on the floor
            tt = tax(0.4); f = 48 + 120 * np.exp(-tt * 30); kk = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8) * 0.9
            L = min(len(kk), n - s); out[s : s + L] += kk[:L, None]; kicks.append(t)
        if e >= 0.7 and pos in (4, 12):  # clap
            tt = tax(0.18); cl = highpass(rng.standard_normal(len(tt)), 1200) * np.exp(-tt * 28) * 0.28; L = min(len(cl), n - s); out[s : s + L] += cl[:L, None]
        if e >= 0.7 and pos % 2 == 1:  # off 8th hats
            tt = tax(0.06); hh = highpass(rng.standard_normal(len(tt)), 7000) * np.exp(-tt * 90) * (0.10 if pos % 4 == 3 else 0.07); L = min(len(hh), n - s); out[s : s + L] += hh[:L, None]
        if e >= 0.55 and pos % 4 == 2:  # off-beat bass
            tt = tax(beat * 0.45); bs = lowpass(np.sin(2 * np.pi * mid(ch[0] - 12) * tt) + 0.4 * np.sign(np.sin(2 * np.pi * mid(ch[0] - 12) * tt)), 400) * np.exp(-tt * 3.5) * 0.32
            L = min(len(bs), n - s); out[s : s + L] += bs[:L, None]
        if e >= 0.55:  # arp 16ths
            note = ch[[0, 1, 2, 1, 2, 1, 0, 2][k % 8]] + 12; tt = tax(step * 1.8)
            ar = (np.sin(2 * np.pi * mid(note) * tt) + 0.35 * np.sin(2 * np.pi * mid(note) * 2 * tt)) * np.exp(-tt * 14) * (0.07 + 0.03 * (e >= 0.9))
            L = min(len(ar), n - s); out[s : s + L, 0] += ar[:L] * 0.9; out[s : s + L, 1] += ar[:L] * 1.1
        t += step; k += 1
    # sidechain-style ducking keyed on kicks (pump) applied to everything except the kicks themselves is approximated by gain curve
    duck = np.ones(n)
    for kt in kicks:
        s = int(kt * SR); L = min(int(0.22 * SR), n - s); duck[s : s + L] = np.minimum(duck[s : s + L], 1 - 0.45 * np.exp(-np.arange(L) / SR * 18))
    return out * duck[:, None]

# ---------------- master: bus dynamics, loudness, true-peak limiter ----------------
SFX_BUS, MUSIC_BUS = 0.25, 0.25        # was 0.95 / 0.9 into tanh(x*1.25); the raw SFX bus peaks at ~+27 dBFS (riser + whoosh + slam)
SFX_LIM_THR, SFX_LIM_KNEE, SFX_LIM_REL = -6.0, 6.0, 150.0  # SFX bus soft limiter: threshold dBFS, knee dB, release dB/s
HEADROOM = -3.0                        # dBFS peak ceiling of the summed mix before loudness normalisation
TP_ATTACK, TP_REL = 0.002, 50.0        # final limiter: look-ahead/attack half-window (s), release (dB/s)
MASTER_LP = (16000.0, 17500.0)         # zero-phase cosine low-pass band (Hz) before the limiter: AAC <= 160k cuts ~18 kHz anyway,
                                       # and removing HF from limited noise AFTER limiting would bring the peaks back (+1.8 dB seen)

def db2lin(d): return 10 ** (np.asarray(d) / 20)
def lin2db(x): return 20 * np.log10(np.maximum(x, 1e-12))

def release_curve(gr, rate):
    """Instant attack, linear-in-dB release: out[i] = max(gr[i], out[i-1] - rate) (rate in dB/sample), vectorised via cummax."""
    k = rate * np.arange(len(gr)); return np.maximum.accumulate(gr + k) - k

def sliding_max(x, w):
    """Centered running max over x[i-w .. i+w] (van Herk / Gil-Werman, O(n))."""
    L = 2 * w + 1; n = len(x); m = -(-(n + 2 * w) // L) * L
    xp = np.full(m, -np.inf); xp[w : w + n] = x; b = xp.reshape(-1, L)
    g = np.maximum.accumulate(b, axis=1).ravel(); h = np.maximum.accumulate(b[:, ::-1], axis=1)[:, ::-1].ravel()
    return np.maximum(h[:n], g[L - 1 : L - 1 + n])

def box_mean(x, w):
    """Centered moving average over x[i-w .. i+w] (edges padded with the edge value)."""
    xp = np.concatenate([np.full(w, x[0]), x, np.full(w, x[-1])]); c = np.concatenate([[0.0], np.cumsum(xp)])
    return (c[2 * w + 1 :] - c[: -2 * w - 1]) / (2 * w + 1)

def soft_limit(x, thr=None, knee=None, rel=None):
    """Look-ahead-free soft-knee limiter (stereo-linked, infinite ratio above the knee, instant attack, dB-linear release)."""
    thr = SFX_LIM_THR if thr is None else thr; knee = SFX_LIM_KNEE if knee is None else knee; rel = SFX_LIM_REL if rel is None else rel
    over = lin2db(np.abs(x).max(axis=1)) - thr
    gr = np.where(over > knee / 2, over, np.where(over > -knee / 2, (over + knee / 2) ** 2 / (2 * knee), 0.0))
    return x * db2lin(-release_curve(gr, rel / SR))[:, None]

def oversample4(x):
    """4x band-limited (FFT zero-pad) interpolation along axis 0."""
    n = len(x); X = np.fft.rfft(x, axis=0); Y = np.zeros((2 * n + 1,) + x.shape[1:], complex); Y[: len(X)] = X
    return np.fft.irfft(Y, 4 * n, axis=0) * 4

def true_peak_db(x): return float(lin2db(np.abs(oversample4(x)).max()))

_KW = (([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]),   # BS.1770 stage 1 (shelf)
       ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]))                                          # stage 2 (RLB high-pass)

def k_weight(x):
    """K-weighting approximation: |H_shelf * H_rlb| of the 48 kHz BS.1770 biquads applied zero-phase via FFT (SR is fixed at 48 kHz)."""
    X = np.fft.rfft(x, axis=0); z = np.exp(-2j * np.pi * np.fft.rfftfreq(len(x))); H = np.ones(len(z))   # z = z^-1 at f/SR
    for b, a in _KW: H = H * np.abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z))
    return np.fft.irfft(X * H[:, None], len(x), axis=0)

def loudness(x):
    """Integrated loudness in LUFS (BS.1770-4 gating; L/R weights 1.0). Returns -70 for silence."""
    y = k_weight(x); blk, hop = int(0.4 * SR), int(0.1 * SR)
    if len(y) < blk: return -70.0
    c = np.concatenate([[0.0], np.cumsum((y ** 2).sum(axis=1))]); s = np.arange(0, len(y) - blk + 1, hop)
    z = (c[s + blk] - c[s]) / blk; lk = -0.691 + 10 * np.log10(np.maximum(z, 1e-20))
    if not np.any(lk > -70): return -70.0
    rel = -0.691 + 10 * np.log10(z[lk > -70].mean()) - 10
    return float(-0.691 + 10 * np.log10(z[(lk > -70) & (lk > rel)].mean()))

def tp_limit(x, ceiling=-2.0, attack=None, rel=None):
    """Final limiter. Detector: per-sample max of the 4x oversampled |x| (both channels). Gain reduction gets a dB-linear release,
    then a running max + moving average over +-attack, which ramps the gain down BEFORE each peak (look-ahead, fine offline) and
    keeps gain <= required gain at every sample. Returns (y, gain_curve)."""
    attack = TP_ATTACK if attack is None else attack; rel = TP_REL if rel is None else rel
    n = len(x); env = np.abs(oversample4(x)).reshape(n, 4, -1).max(axis=(1, 2))
    gr = np.maximum(0.0, lin2db(env) - ceiling); w = max(1, int(attack * SR))
    gr = box_mean(sliding_max(release_curve(gr, rel / SR), w), w); g = db2lin(-gr)
    return x * g[:, None], g

def master(sfx, mus, duration, lufs=-15.0, ceiling=-2.0, info=None):
    """Sum + low-pass + end fade + headroom trim (peaks <= HEADROOM dBFS) -> loudness to `lufs` -> limit at `ceiling` dBTP."""
    n = len(sfx); f = np.fft.rfftfreq(n, 1 / SR); lo, hi = MASTER_LP
    H = np.where(f <= lo, 1.0, np.where(f >= hi, 0.0, 0.5 + 0.5 * np.cos(np.pi * (f - lo) / (hi - lo))))
    mix = np.fft.irfft(np.fft.rfft(sfx + mus, axis=0) * H[:, None], n, axis=0)
    fade = np.clip((duration - np.arange(n) / SR) / 0.9, 0, 1); mix = mix * fade[:, None]
    pk = np.abs(mix).max(); trim = min(1.0, float(db2lin(HEADROOM)) / pk) if pk > 0 else 1.0; mix = mix * trim
    l0 = loudness(mix); gain = (lufs - l0) if l0 > -60 else 0.0; y, g = mix, np.ones(n)
    for _ in range(4):                                  # limiting lowers loudness a little: re-trim the gain and limit again
        y, g = tp_limit(mix * db2lin(gain), ceiling); l1 = loudness(y)
        if l0 <= -60 or abs(l1 - lufs) < 0.05: break
        gain += lufs - l1
    tp = true_peak_db(y); max_gr = max(0.0, float(-lin2db(g.min())))
    if tp > ceiling: y = y * db2lin(ceiling - tp); g = g * db2lin(ceiling - tp); l1 += ceiling - tp; tp = ceiling   # overshoot safety
    if info is not None:
        info.update(fade=fade, trim=trim, gain_db=gain, final_gain=g, pre_peak=float(lin2db(pk)), pre_lufs=l0, lufs=l1, tp=tp, max_gr=max_gr)
    return y

def render_buses(cues, duration, bpm, emap, key='A', no_music=False, sfx_gain=1.0, music_gain=1.0):
    """Returns (sfx_bus, music_bus): SFX one-shots + reverb, soft-limited, then * sfx_gain (post-limiter, so it is a true balance knob)."""
    n = int(SR * duration); sfx = np.zeros((n, 2))
    for c in cues:
        ty = c['type']
        if ty not in ONE: continue
        mono, d = ONE[ty](c); t0 = c['t']; lead = 0.0
        if ty in ('riser', 'swell'): lead = c.get('dur', 2.0 if ty == 'riser' else 1.2)   # cue.t = PEAK time
        if ty == 'whoosh': lead = c.get('dur', 0.6) * 0.45          # whoosh peak lands mid-transition
        p0, p1 = (0.0, None)
        if ty == 'whoosh': p0, p1 = (0.8 * d, -0.8 * d) if d in (1, -1) else (0.0, None)   # dir=1: right -> left
        place(sfx, mono, t0, p0, p1, 1.0, lead)
    sfx = soft_limit(reverb(sfx, 1.3, 0.16) * SFX_BUS) * sfx_gain
    mus = music(duration, bpm, emap, key) * MUSIC_BUS * music_gain if not no_music else np.zeros((n, 2))
    return sfx, mus

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cues'); ap.add_argument('out')
    ap.add_argument('--duration', type=float, default=30); ap.add_argument('--bpm', type=float, default=120)
    ap.add_argument('--energy', default='0:0.3,4:0.8'); ap.add_argument('--key', default='A'); ap.add_argument('--no-music', action='store_true')
    ap.add_argument('--sfx-gain', type=float, default=1.0); ap.add_argument('--music-gain', type=float, default=1.0)
    ap.add_argument('--lufs', type=float, default=-15.0, help='integrated loudness target before the final limiter (LUFS)')
    ap.add_argument('--ceiling', type=float, default=-2.0, help='final limiter ceiling, 4x-oversampled peak (dBTP-ish)')
    a = ap.parse_args()
    emap = sorted((float(x.split(':')[0]), float(x.split(':')[1])) for x in a.energy.split(','))
    cues = json.load(open(a.cues))
    sfx, mus = render_buses(cues, a.duration, a.bpm, emap, a.key, a.no_music, a.sfx_gain, a.music_gain)
    info = {}; mix = master(sfx, mus, a.duration, a.lufs, a.ceiling, info)
    pcm = np.clip(np.round(mix * 32767), -32768, 32767).astype('<i2')
    import wave
    with wave.open(a.out, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(f"wrote {a.out}  {a.duration}s  cues={len(cues)}  {info['lufs']:.1f} LUFS  tp {info['tp']:.1f} dBTP  "
          f"(gain {info['gain_db']:+.1f} dB, max limiter GR {info['max_gr']:.1f} dB)")

if __name__ == '__main__': main()
