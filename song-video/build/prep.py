#!/usr/bin/env python3
"""Build timeline.json for the lyrics video.

Inputs : ../timings.json (stanza windows), transcript words (faster-whisper output),
         ../assets/stanzas.json (poem text), ../assets/song.mp3 (loudness envelope).
Output : timeline.json (stanzas with per-word timings, background windows, loudness envelope).

Usage: python3 -I prep.py <transcript.json> <out timeline.json>
"""
import json, re, subprocess, sys, array, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FPS = 24
LEAD = 3.5       # title card before the song starts
TAIL = 10.0       # end card after the song
SONG_DUR = 232.32

transcript = json.load(open(sys.argv[1], encoding="utf-8"))
timings = json.load(open(os.path.join(ROOT, "timings.json"), encoding="utf-8"))["stanzas"]
stanzas = json.load(open(os.path.join(ROOT, "assets", "stanzas.json"), encoding="utf-8"))

NIQQUD = re.compile(r"[֑-ׇ]")
def letters(s):
    return re.sub(r"[^א-ת]", "", NIQQUD.sub("", s))

# ---- whisper words -> stanza buckets
ww = []
for seg in transcript:
    for w in seg["words"]:
        ww.append({"t": w["w"], "s": w["s"], "e": w["e"], "n": max(1, len(letters(w["w"])))})

def bucket(w):
    mid = (w["s"] + w["e"]) / 2
    best, bd = None, 1e9
    for t in timings:
        a, b = t["start"], t["end"]
        d = 0 if a <= mid <= b else min(abs(mid - a), abs(mid - b))
        if d < bd:
            best, bd = t["id"], d
    return best if bd < 1.0 else None

buckets = {t["id"]: [] for t in timings}
for w in ww:
    k = bucket(w)
    if k is not None:
        buckets[k].append(w)

def align(poem_words, wwords, a, b):
    """Map poem words to times by cumulative letter count over whisper words."""
    weights = [len(letters(p)) for p in poem_words]
    total = sum(weights) or 1
    if not wwords:
        return None
    wtot = sum(w["n"] for w in wwords)
    # whisper anchors: fraction intervals
    anchors, c = [], 0
    for w in wwords:
        anchors.append((c / wtot, (c + w["n"]) / wtot, w["s"], w["e"]))
        c += w["n"]
    def t_at(f, end):
        for f0, f1, s, e in anchors:
            if (f > f0 - 1e-9 and f <= f1 + 1e-9) if end else (f >= f0 - 1e-9 and f < f1 - 1e-9):
                return s + (f - f0) / max(f1 - f0, 1e-9) * (e - s)
        return anchors[-1][3] if end else anchors[0][2]
    out, c = [], 0
    for p, wgt in zip(poem_words, weights):
        f0, f1 = c / total, (c + wgt) / total
        if wgt == 0:
            out.append(None)
        else:
            out.append((t_at(f0, False), t_at(f1, True)))
        c += wgt
    # fill punctuation-only tokens with neighbours
    for i, o in enumerate(out):
        if o is None:
            prev = next((out[j] for j in range(i - 1, -1, -1) if out[j]), None)
            nxt = next((out[j] for j in range(i + 1, len(out)) if out[j]), None)
            t = prev[1] if prev else nxt[0]
            out[i] = (t, t)
    # monotonic + clamp
    last = a
    res = []
    for s, e in out:
        s = max(s, last - 0.02)
        e = max(e, s + 0.05)
        res.append((round(s, 3), round(e, 3)))
        last = s
    return res

EMPH = {
    0: ["מרחק", "קח נא את בנך"], 1: ["הלב מסתבך"], 3: ["וההר לפניהם"], 5: ["חיי שרה"],
    6: ["הנני"], 7: ["וההר עוד בתוכם"], 9: ["הוכן לו האיל"], 10: ["איל"], 11: ["קול ישועה"],
    13: ["מסירותם", "שבויים שבו"], 15: ["ההבטחה מקבלת גוף"], 16: ["עינים"],
    17: ["ימצאו אותנו שם"], 18: ["איל"], 19: ["אבקשה טוב לך"],
}
ALL_GOLD = {2, 4, 8, 12, 14, 19}

def mark_emph(words, phrases):
    flags = [False] * len(words)
    keys = [letters(w) for w in words]
    for ph in phrases:
        pk = [letters(x) for x in ph.split()]
        for i in range(len(words) - len(pk) + 1):
            if keys[i:i + len(pk)] == pk:
                for j in range(i, i + len(pk)):
                    flags[j] = True
    return flags

out_st = []
for t, s in zip(timings, stanzas):
    sid = t["id"]
    lines = s["lines"]
    flat, line_idx = [], []
    for li, line in enumerate(lines):
        for w in line.split():
            flat.append(w)
            line_idx.append(li)
    wwords = buckets[sid]
    if sid == 19 or not wwords:
        # sung stanza: no reliable word times -> distribute across stanza window per line
        a, b = t["start"], t["end"]
        L = len(lines)
        times = []
        for li, line in enumerate(lines):
            la = a + (b - a) * li / L
            lb = a + (b - a) * (li + 1) / L
            ws = line.split()
            n = len(ws)
            for k in range(n):
                times.append((round(la, 3), round(lb, 3)))   # whole line lights together
        al = times
    else:
        al = align(flat, wwords, t["start"], t["end"])
    emph = mark_emph(flat, EMPH.get(sid, []))
    gold_all = sid in ALL_GOLD
    out_lines = [[] for _ in lines]
    for i, w in enumerate(flat):
        out_lines[line_idx[i]].append({"t": w, "s": al[i][0], "e": al[i][1], "em": emph[i] or gold_all,
                                       "k": letters(w)})
    out_st.append({"id": sid, "kind": t["kind"], "verified": t["verified"], "lines": out_lines,
                   "first": al[0][0], "last": al[-1][1], "whisper_words": len(wwords)})

# ---- loudness envelope per frame (song time)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "assets", "song.mp3"), "-ac", "1",
                      "-ar", "8000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
d = array.array("h"); d.frombytes(raw)
sr = 8000
nfr = int(math.ceil(SONG_DUR * FPS))
env = []
for i in range(nfr):
    seg = d[int(i / FPS * sr): int((i + 1) / FPS * sr)]
    env.append(math.sqrt(sum(x * x for x in seg) / max(1, len(seg))) / 32768)
mx = max(env) or 1
env = [e / mx for e in env]
sm, y = [], 0.0
for e in env:                       # smooth: fast attack, slow release
    y = e if e > y else y + (e - y) * 0.12
    sm.append(round(y, 3))

# ---- background windows (song time). box = x,y,w,h on the 1920x1080 canvas
L = [-120, 60, 1250, 703]
R = [790, 60, 1250, 703]
R2 = [560, 0, 1400, 787]
L2 = [-60, 170, 1250, 703]
FULL = [0, 0, 1920, 1080]
OP = 0.56
windows = [
    {"id": "w0",  "type": "still", "src": "art", "crop": [0, 100, 1100], "box": R,  "t0": -3.5, "t1": 26.9, "zoom": [1.0, 1.10]},
    {"id": "w1",  "type": "clip", "src": "d-mother-door", "crop": [250, 150, 700], "box": L, "t0": 27.0, "t1": 45.2, "clipStart": 27.3},
    {"id": "w3",  "type": "clip", "src": "c1-walk-mountain", "crop": [300, 0, 980], "box": R2, "t0": 50.2, "t1": 56.0, "clipStart": 50.6},
    {"id": "w4",  "type": "clip", "src": "c2-walk-olive", "crop": [300, 120, 800], "box": L2, "t0": 56.0, "t1": 60.6, "clipStart": 56.4},
    {"id": "w5",  "type": "still", "src": "art", "crop": [380, 330, 900], "box": L, "t0": 60.2, "t1": 75.2, "zoom": [1.0, 1.12]},
    {"id": "w6",  "type": "still", "src": "art", "crop": [800, 150, 872], "box": R, "t0": 75.0, "t1": 99.2, "zoom": [1.0, 1.06], "freeze": [94.7, 98.9]},
    {"id": "w7",  "type": "clip", "src": "a-calm", "crop": [0, 130, 760], "box": L, "t0": 98.8, "t1": 109.9, "clipStart": 98.8, "fadeOut": 1.3},
    {"id": "w8a", "type": "clip", "src": "b-turn", "crop": [0, 60, 1000], "box": R, "t0": 109.4, "t1": 116.4, "clipStart": 109.6, "fadeIn": 1.2, "fadeOut": 0.8},
    {"id": "w8b", "type": "clip", "src": "b-calm", "crop": [0, 60, 1000], "box": R, "t0": 115.9, "t1": 121.6, "clipStart": 116.0, "fadeIn": 0.8, "fadeOut": 1.2},
    {"id": "w9",  "type": "still", "src": "art", "crop": [0, 250, 700], "box": L, "t0": 121.0, "t1": 136.0, "zoom": [1.0, 1.15]},
    {"id": "w10", "type": "still", "src": "art", "crop": [900, 0, 772], "box": R, "t0": 129.0, "t1": 137.0, "zoom": [1.0, 1.08]},
    {"id": "w11a", "type": "clip", "src": "a-salute", "crop": [300, 0, 800], "box": R, "t0": 136.4, "t1": 148.2, "clipStart": 136.8, "fadeOut": 0.9},
    {"id": "w11b", "type": "clip", "src": "a-calm", "crop": [0, 100, 900], "box": L, "t0": 147.7, "t1": 160.8, "clipStart": 147.9, "fadeIn": 1.0},
    {"id": "w12", "type": "grow", "src": "art", "box": FULL, "t0": 160.4, "t1": 181.2, "grow": [0.36, 1.0]},
    {"id": "w13", "type": "still", "src": "art", "crop": [0, 0, 1672], "box": FULL, "t0": 180.6, "t1": 196.2, "zoom": [1.10, 1.0], "dy": [30, -30]},
    {"id": "w14a", "type": "clip", "src": "c1-walk-mountain", "crop": [300, 0, 980], "box": R2, "t0": 195.4, "t1": 205.2, "clipStart": 195.8},
    {"id": "w14b", "type": "clip", "src": "c2-walk-olive", "crop": [300, 120, 800], "box": L2, "t0": 202.6, "t1": 212.6, "clipStart": 203.0},
    {"id": "w15", "type": "still", "src": "art", "crop": [0, 100, 1100], "box": R, "t0": 212.6, "t1": 224.2, "zoom": [1.0, 1.10]},
    {"id": "w16", "type": "still", "src": "art", "crop": [0, 0, 1672], "box": FULL, "t0": 223.6, "t1": 233.6, "zoom": [1.0, 1.06], "opacity": 0.46},
]
for w in windows:
    w.setdefault("fadeIn", 1.5); w.setdefault("fadeOut", 1.5); w.setdefault("opacity", OP)

timeline = {"fps": FPS, "lead": LEAD, "songDur": SONG_DUR, "tail": TAIL,
            "total": round(LEAD + SONG_DUR + TAIL, 3), "stanzas": out_st, "windows": windows, "env": sm}
json.dump(timeline, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print("stanzas", len(out_st), "frames total", int(math.ceil(timeline["total"] * FPS)))
for s in out_st:
    print(s["id"], s["whisper_words"], s["first"], s["last"], sum(len(l) for l in s["lines"]))
