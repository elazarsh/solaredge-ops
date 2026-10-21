#!/usr/bin/env python3
"""מיקס אודיו: קריינות + מוזיקה (עם הנמכה מתחת לקול) + אפקטים מסונכרנים -> wav סטריאו 48kHz.

שימוש: python3 mix.py mix.json
mix.json:
{ "out": "out/mix.wav", "duration": 120.0, "sr": 48000,
  "voice": [ {"file": "vo/p01.wav", "t": 0.6}, ... ],                          // t = שנייה שבה הקריינות מתחילה
  "music": [ {"file": "mus/m1.mp3", "t0": 0, "t1": 40, "gain": 0.55}, ... ],     // מתארך בלולאה עם crossfade, fade 2.5 ש'
  "sfx":   [ {"kind": "whoosh", "t": 12.3, "g": 1.0}, {"kind": "burn", "t": 40.0} ],   // ראה sfx_lib.py לשמות
  "duck_music": 0.55, "duck_sfx": 0.35, "reverb_voice": 0.10, "wind": false }
הקול מעובד: מסנן 75Hz, חימום, נרמול RMS, ריוורב קל. מוזיקה מונמכת ב-duck_music בזמן דיבור. בסוף: master.sh (loudnorm -14 LUFS).
תלויות: numpy, scipy, ffmpeg (לקריאת mp3).
"""
import json, subprocess, sys
import numpy as np, scipy.io.wavfile as w, scipy.signal as sg
from sfx_lib import Kit

def rd(path, SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def loopto(x, n, xf):
    out = x.copy()
    while len(out) < n:
        fade = np.linspace(0, 1, xf)[:, None]; out = np.concatenate([out[:-xf], out[-xf:] * (1 - fade) + x[:xf] * fade, x[xf:]])
    return out[:n]

def main(cfg):
    SR = cfg.get("sr", 48000); END = cfg["duration"]; N = int((END + 0.5) * SR); K = Kit(SR); tt = np.arange(N) / SR
    def put(buf, x, t0, g=1.0, pan=0.0):
        i = int(t0 * SR); j = min(len(buf), i + len(x))
        if j <= i or i < 0: return
        x = x[:j - i] * g; buf[i:j, 0] += x * np.sqrt((1 - pan) / 2); buf[i:j, 1] += x * np.sqrt((1 + pan) / 2)
    V = np.zeros((N, 2)); vact = np.zeros(N)
    for v in cfg["voice"]:
        sr, a = w.read(v["file"]); a = a.astype(np.float64) / 32768
        if a.ndim > 1: a = a[:, 0]
        a = sg.resample_poly(a, SR // sr, 1) if SR % sr == 0 else sg.resample(a, int(len(a) * SR / sr))
        a = K.hp(a, 75); a = a + .35 * K.lp(a, 260); a *= .1 / np.sqrt(np.mean(a ** 2)); a = np.tanh(a * 5) / 5; a = K.rev(a, K.IR_S, cfg.get("reverb_voice", .10))
        f = int(.02 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        put(V, a, v["t"]); i = int(v["t"] * SR); vact[i:i + len(a)] = 1
    vact = np.clip(K.lp(vact, 2.5, 1), 0, 1)
    M = np.zeros((N, 2))
    for m in cfg.get("music", []):
        t0, t1 = max(0, m["t0"]), m["t1"]; n = int((t1 - t0) * SR); x = rd(m["file"], SR)
        x *= .10 / np.sqrt(np.mean(x ** 2)) * m.get("gain", .55); x = loopto(x, n, int(4 * SR))
        fi = min(int(2.5 * SR), n // 2); x[:fi] *= np.linspace(0, 1, fi)[:, None]; x[-fi:] *= np.linspace(1, 0, fi)[:, None]
        i = int(t0 * SR); j = min(N, i + len(x)); M[i:j] += x[:j - i]
    M *= (1 - cfg.get("duck_music", .55) * vact)[:, None]
    S = np.zeros((N, 2))
    if cfg.get("wind"):
        wd = K.bp(K.rng.standard_normal(N), 180, 900) * (.5 + .5 * np.sin(2 * np.pi * .07 * tt)) * .02; S[:, 0] += wd; S[:, 1] += np.roll(wd, 700)
    for e in cfg.get("sfx", []):
        for x, t0, g, pan in K.events(e["kind"], e["t"], e.get("g", 1.0)): put(S, x, t0, g, pan)
    S *= (1 - cfg.get("duck_sfx", .35) * vact)[:, None]
    Mx = V + M + S; Mx = np.tanh(Mx * 1.2) / 1.2
    Mx *= np.clip(tt / .5, 0, 1)[:, None] * np.clip((END + .5 - tt) / 2.0, 0, 1)[:, None]
    Mx /= max(np.abs(Mx).max(), 1e-9); Mx *= .9
    import os; os.makedirs(os.path.dirname(cfg["out"]) or ".", exist_ok=True)
    w.write(cfg["out"], SR, (Mx * 32767).astype(np.int16)); print("mix ok", cfg["out"], END, "s")

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(json.load(open(sys.argv[1], encoding="utf-8")))
