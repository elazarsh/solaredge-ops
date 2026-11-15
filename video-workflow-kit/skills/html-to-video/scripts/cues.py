#!/usr/bin/env python3
"""סנכרון ויזואליה לקריינות: מוצא את זמן ההגייה של מילות מפתח (מתוך תמלול ASR עם זמני מילים) ומחשב משכי סצנות.

  python3 cues.py spec.json words.json --wavdir vo --out cues.json --durations durations.json
spec.json:  {"s01": [["title","שני",1,0.4], ["chat","הרגיל",1,2.5]], "s02": [...]}   # [שם cue, מילת מפתח, מופע n, זמן גיבוי]
words.json: הפלט של hebrew-narration/scripts/asr.py transcribe  ({"s01":[{"w","s","e"},...]})
חשוב: מילת המפתח כפי שהיא *מתומללת* (ללא ניקוד; אנגלית בלטינית "Skill"; מספרים כספרות "24"). התאמה = הכלה אחרי ניקוי סימנים.
הפלט cues.json: {"cues": {scene: {name: שניות מתחילת קובץ הקול}}, "dur": {scene: אורך קובץ הקול}}.
durations.json: רשימת משכי סצנות (אורך קול + --pad, ובסצנה האחרונה + --pad-last). ה-HTML מפעיל כל אלמנט ב-Q(i,'name') = תחילת סצנה + LEAD + cue.
cue שלא נמצא מקבל את זמן הגיבוי ומודפס ב-"missing" -> לתקן את מילת המפתח.
"""
import argparse, json, os, re, wave

def strip(s):
    return re.sub(r"[^א-ת0-9A-Za-z]", "", s)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec"); ap.add_argument("words"); ap.add_argument("--wavdir", default="vo")
    ap.add_argument("--out", default="cues.json"); ap.add_argument("--durations", default="durations.json")
    ap.add_argument("--pad", type=float, default=1.1); ap.add_argument("--pad-last", type=float, default=3.0)
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8")); W = json.load(open(a.words, encoding="utf-8"))
    out, miss = {}, []
    for k in sorted(spec):
        ws = W.get(k, []); out[k] = {}
        for name, kw, nth, fb in spec[k]:
            c, t = 0, None
            for x in ws:
                if strip(kw) and strip(kw) in strip(x["w"]):
                    c += 1
                    if c == nth:
                        t = x["s"]; break
            if t is None:
                t = fb; miss.append((k, name, kw))
            out[k][name] = round(t, 2)
    dur = {}
    for k in sorted(spec):
        with wave.open(os.path.join(a.wavdir, k + ".wav")) as w:
            dur[k] = round(w.getnframes() / w.getframerate(), 2)
    keys = sorted(spec)
    D = [round(dur[k] + a.pad, 2) for k in keys]; D[-1] = round(dur[keys[-1]] + a.pad_last, 2)
    json.dump({"cues": out, "dur": dur}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(D, open(a.durations, "w"))
    print("missing:", miss); print("durations:", D, "total", round(sum(D), 1))

if __name__ == "__main__":
    main()
