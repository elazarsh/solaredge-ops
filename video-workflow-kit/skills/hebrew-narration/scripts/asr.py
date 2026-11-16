#!/usr/bin/env python3
"""תמלול עברי עם זמני מילים (Gemini gemini-3.8-flash) ובדיקת הקראה מול הטקסט.

  transcribe: python3 asr.py transcribe vo/*.wav --out words.json
      -> {"<שם קובץ בלי סיומת>": [{"w":מילה,"s":התחלה,"e":סוף}, ...]}  (גם לסנכרון cues)
  check:      python3 asr.py check narr.md|narr.json --words words.json [--keys-from-files]
      משווה מילה-מילה (בלי ניקוד) ומדפיס הבדלים. מפתחות כמו ב-tts.py (p01.. או מפתחות ה-JSON).
דורש GEMINI_API_KEY (ל-transcribe בלבד). לבדיקה בלי רשת: check עם words.json קיים.
זכור: ה-ASR טועה לפעמים (למשל "תשע"->"9"); חשד = להקשיב/לנסח מחדש, לא להסיק אוטומטית.
"""
import argparse, base64, concurrent.futures as cf, difflib, json, os, re, sys, time, urllib.request

PROMPT = ("תמלל את ההקלטה בעברית בדיוק כפי שנאמרה, בלי ניקוד. החזר JSON בלבד: רשימה של אובייקטים "
          "{\"w\":\"מילה\",\"s\":שניות_התחלה,\"e\":שניות_סיום} לכל מילה, בסדר שנאמרו. "
          "אם נאמרה מילה לא ברורה או שגויה, תמלל כפי ששמעת.")


def asr(path, key, model="gemini-3.8-flash"):
    b = base64.b64encode(open(path, "rb").read()).decode()
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": b}}, {"text": PROMPT}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    d = json.load(urllib.request.urlopen(req, timeout=180))
    return json.loads(d["candidates"][0]["content"]["parts"][0]["text"])


def norm(t):
    t = re.sub(r"[֑-ׇ]", "", t)
    t = t.replace("־", " ").replace("—", " ")
    return re.sub(r"[^\wא-ת ]", " ", t).split()


def load_items(path):
    txt = open(path, encoding="utf-8").read()
    if path.endswith(".json"):
        return json.loads(txt)
    return {f"p{i:02d}": p for i, p in enumerate([p.strip() for p in txt.split("\n\n") if p.strip()], 1)}


def cmd_transcribe(a):
    key = os.environ.get("GEMINI_API_KEY") or sys.exit("GEMINI_API_KEY לא מוגדר (ראה ai-api-setup)")

    def one(p):
        for t in range(6):
            try:
                return os.path.splitext(os.path.basename(p))[0], asr(p, key)
            except Exception as e:
                print(p, "retry", str(e)[:60], flush=True)
                time.sleep(8 * (t + 1))
        return os.path.splitext(os.path.basename(p))[0], []

    with cf.ThreadPoolExecutor(4) as ex:
        out = dict(ex.map(one, a.files))
    json.dump(out, open(a.out, "w"), ensure_ascii=False)
    for k, w in out.items():
        print(k, len(w), "words", (f"{w[0]['s']}->{w[-1]['e']}" if w else "EMPTY"))


def cmd_check(a):
    items, words = load_items(a.text), json.load(open(a.words))
    bad = 0
    for k, txt in items.items():
        if k not in words:
            print(k, "אין תמלול"); continue
        ref = norm(txt); hyp = norm(" ".join(x["w"] for x in words[k]))
        sm = difflib.SequenceMatcher(None, ref, hyp)
        diffs = [(" ".join(ref[i1:i2]), " ".join(hyp[j1:j2])) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
        flag = "OK " if not diffs else "CHECK"
        bad += bool(diffs)
        print(f"{flag} {k} ratio={sm.ratio():.3f} words={len(ref)}/{len(hyp)}")
        for exp, got in diffs:
            print(f"    צפוי: {exp!r}  נשמע: {got!r}")
    print(f"\n{bad} פסקאות עם הבדלים מתוך {len(items)}. כל הבדל: להקשיב, לא לסמוך על ה-ASR בלבד.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    t = sp.add_parser("transcribe"); t.add_argument("files", nargs="+"); t.add_argument("--out", default="words.json")
    c = sp.add_parser("check"); c.add_argument("text"); c.add_argument("--words", default="words.json")
    a = ap.parse_args()
    {"transcribe": cmd_transcribe, "check": cmd_check}[a.cmd](a)
