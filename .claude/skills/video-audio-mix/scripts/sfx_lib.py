"""ספריית אפקטי קול סינתטיים (numpy/scipy) למעברים ולאלמנטים על המסך. משמשת את mix.py.
שמות: whoosh swell ping click thump hammer scratch typing alarm stamp
מעברים (מתאימים לשמות ב-video-motion-transitions): whip smash tear burn water ripple ink erase peel wipe iris zoomthrough
 washout goldbloom colordrain colorseep dipblack dissolve defocus fill matte portal shatter match smoke
"""
import numpy as np, scipy.signal as sg

class Kit:
    def __init__(self, sr=48000, seed=5):
        self.SR = sr; self.rng = np.random.default_rng(seed)
        self.IR_S = self._ir(0.7, 6, 3500); self.IR_L = self._ir(3.2, 1.8, 1800)
    def lp(s, x, f, o=2): b, a = sg.butter(o, f / (s.SR / 2), "low"); return sg.lfilter(b, a, x)
    def hp(s, x, f, o=2): b, a = sg.butter(o, f / (s.SR / 2), "high"); return sg.lfilter(b, a, x)
    def bp(s, x, f1, f2, o=2): b, a = sg.butter(o, [f1 / (s.SR / 2), f2 / (s.SR / 2)], "band"); return sg.lfilter(b, a, x)
    def _ir(s, sec, decay, dark):
        n = int(sec * s.SR); x = s.rng.standard_normal(n) * np.exp(-np.arange(n) / s.SR * decay); x = s.lp(x, dark); x[:int(0.006 * s.SR)] *= 0
        return x / np.abs(x).sum() * 3.2
    def rev(s, x, I, wet): return (1 - wet) * np.pad(x, (0, len(I)))[:len(x)] + wet * sg.fftconvolve(x, I)[:len(x)]
    def burst(s, d, f1, f2, dec): n = int(d * s.SR); return s.bp(s.rng.standard_normal(n), f1, f2) * np.exp(-np.arange(n) / s.SR * dec)
    def swell(s, d, lo, hi): n = int(d * s.SR); return s.bp(s.rng.standard_normal(n), lo, hi) * np.sin(np.linspace(0, np.pi, n)) ** 2
    def tone(s, f0, f1, d, dec=3.0): n = int(d * s.SR); ph = np.cumsum(np.linspace(f0, f1, n)) / s.SR * 2 * np.pi; return np.sin(ph) * np.exp(-np.arange(n) / s.SR * dec)
    def sub(s, f, d, dec): n = int(d * s.SR); return np.sin(2 * np.pi * f * np.arange(n) / s.SR) * np.exp(-np.arange(n) / s.SR * dec)

    def events(s, kind, t, g=1.0):
        """מחזיר רשימת (שמע, זמן_התחלה, עוצמה, פאן). t = רגע שיא האפקט (המעבר באמצע הקליפ)."""
        R, I, L = s.rev, s.IR_S, s.IR_L; E = []; rng = s.rng
        add = lambda x, t0, gain, pan=0.0: E.append((x, t0, gain * g, pan))
        if kind == "whoosh": add(R(s.swell(0.9, 300, 5000), I, .25), t - .1, .06)
        elif kind == "swell": add(R(s.swell(1.4, 200, 4500), L, .3), t, .06)
        elif kind == "ping": add(R(s.tone(1320, 1320, .9, 4), L, .5), t, .045, rng.uniform(-.5, .5))
        elif kind == "click": add(R(s.burst(.03, 2500, 9000, 120), I, .2), t, .03, rng.uniform(-.4, .4))
        elif kind == "thump": add(R(s.sub(55, 1.2, 7) + .5 * s.burst(1.2, 150, 900, 14), L, .35), t, .35)
        elif kind == "hammer": add(R(s.burst(.35, 260, 1500, 40) + .7 * s.sub(150, .35, 32), L, .45), t, .05, -.25)
        elif kind == "scratch": add(s.bp(rng.standard_normal(int(2 * s.SR)), 1800, 7500) * (.55 + .45 * np.sin(np.linspace(0, 2 * np.pi * 6, int(2 * s.SR)))) * .02 / .05, t, .05)
        elif kind == "typing":
            for k in range(24): add(R(s.burst(.03, 2500, 9000, 120), I, .2), t + k * .07, .028, rng.uniform(-.4, .4))
        elif kind == "alarm":
            for k in range(6): add(R(s.tone(1000, 1000, .18, 18), I, .3), t + k * .3, .05)
        elif kind == "stamp": add(R(s.sub(55, 1.0, 8) + .6 * s.burst(1.0, 200, 4000, 14), L, .4), t, .3)
        elif kind == "whip": add(R(s.swell(.7, 300, 4000), I, .2), t - .35, .05)
        elif kind == "smash": add(R(s.sub(48, .8, 9) + .6 * s.burst(.8, 200, 3500, 16), L, .3), t - .15, .32)
        elif kind == "tear":
            n = int(1.0 * s.SR); x = s.bp(rng.standard_normal(n), 1200, 7000) * (.5 + .5 * np.sign(np.sin(np.linspace(0, 60, n)))) * np.hanning(n) + .4 * s.bp(rng.standard_normal(n), 150, 600) * np.hanning(n); add(R(x, I, .2), t - .5, .06)
        elif kind == "burn":
            for _ in range(120): add(s.burst(.03, 1200, 8000, 110), t - 1.5 + rng.uniform(0, 3.2), rng.uniform(.01, .035), rng.uniform(-.8, .8))
            add(R(s.swell(3.0, 60, 500), L, .3), t - 1.6, .06)
        elif kind == "water":
            add(R(s.swell(3.2, 150, 2500), L, .3), t - 1.7, .06)
            for _ in range(10): add(R(s.tone(rng.uniform(800, 1500), rng.uniform(300, 600), .15, 25), L, .5), t - 1.2 + rng.uniform(0, 2.6), .012)
        elif kind == "ripple":
            for i, dt in enumerate((0, .55, 1.1)): add(R(s.tone(900 - i * 150, 420 - i * 60, .4, 9), L, .55), t - .6 + dt, .045)
        elif kind == "ink": add(R(s.sub(55, 1.2, 4), L, .4), t - 1.4, .18); add(R(s.swell(2.4, 100, 900), L, .3), t - 1.3, .04)
        elif kind == "erase":
            n = int(2.6 * s.SR); add(s.bp(rng.standard_normal(n), 1800, 6500) * (.55 + .45 * np.sin(np.linspace(0, 2 * np.pi * 9, n))) * np.hanning(n), t - 1.4, .03)
        elif kind == "peel":
            n = int(1.6 * s.SR); add(R(s.bp(rng.standard_normal(n), 2500, 9000) * np.linspace(.2, 1, n) * np.exp(-np.linspace(0, 3, n)), I, .2), t - .6, .05)
        elif kind == "wipe": add(R(s.swell(1.6, 200, 2500), I, .2), t - .8, .04)
        elif kind == "iris": add(R(s.tone(220, 440, 1.6, 1.5), L, .5), t - .9, .03); add(s.swell(1.8, 800, 5000), t - 1.0, .02)
        elif kind == "zoomthrough": add(R(s.swell(1.7, 200, 3500), I, .2), t - 1.0, .055); add(R(s.tone(180, 700, 1.6, 2.2), L, .3), t - 1.0, .025)
        elif kind == "washout": add(R(s.swell(2.2, 400, 3000), L, .4), t - 1.2, .04); add(R(s.tone(880, 880, 1.8, 2.0), L, .6), t - .8, .025)
        elif kind == "goldbloom":
            for f in (1200, 1800, 2400): add(R(s.tone(f, f, 2.0, 2.2) * (.6 + .4 * np.sin(np.linspace(0, 14, int(2.0 * s.SR)))), L, .6), t - 1.0, .012)
        elif kind == "colordrain": add(R(s.tone(660, 330, 2.4, 1.4), L, .6), t - 1.2, .03)
        elif kind == "colorseep": add(R(s.tone(330, 660, 2.4, 1.4), L, .6), t - 1.2, .03)
        elif kind == "dipblack": add(R(s.swell(2.6, 60, 400), L, .4), t - 1.3, .05)
        elif kind in ("dissolve", "defocus"): add(R(s.swell(2.2, 300, 2500), L, .4), t - 1.1, .025)
        elif kind == "fill": add(R(s.swell(3.0, 60, 700), L, .3), t - 1.6, .07); add(R(s.swell(1.6, 300, 3000), I, .2), t - .2, .04)
        elif kind == "matte": add(R(s.swell(2.6, 200, 3500), L, .3), t - 1.4, .05); add(R(s.tone(300, 600, 2.0, 1.2), L, .5), t - 1.2, .02)
        elif kind == "portal": add(R(s.swell(2.8, 150, 3000), L, .35), t - 1.5, .06); add(R(s.tone(160, 520, 2.4, 1.0), L, .4), t - 1.4, .03)
        elif kind == "shatter":
            add(R(s.burst(.5, 300, 6000, 10), I, .3), t - 1.3, .18)
            for _ in range(26): add(R(s.tone(rng.uniform(1500, 4200), rng.uniform(900, 2500), .08, 45), L, .4), t - 1.0 + rng.uniform(0, 2.2), rng.uniform(.01, .03))
        elif kind == "match": add(R(s.tone(520, 520, 2.6, 1.3), L, .6), t - 1.3, .025); add(R(s.tone(780, 780, 2.6, 1.3), L, .6), t - 1.1, .018)
        elif kind == "smoke": add(R(s.bp(rng.standard_normal(int(2.6 * s.SR)), 250, 2200) * np.hanning(int(2.6 * s.SR)), L, .2), t - 1.2, .045)
        else: raise ValueError("unknown sfx kind: " + kind)
        return E
