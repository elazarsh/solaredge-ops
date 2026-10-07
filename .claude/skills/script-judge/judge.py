#!/usr/bin/env python3
"""Judge an ad script with TypeSafe (System One / Jev). Stdlib only.

  TYPESAFE_API_KEY=... python3 judge.py script.json [--age mature] [--weights w.json] [--dry-run]

script.json: {"hook": str, "body": str, "lines": [str, ...], "facts": [str, ...]}
Prints a markdown table: raw answers, flags, weighted composite. Keeps raw answers so weights
can change without a new API call (--save raw.json / --load raw.json).
"""
import argparse, json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://api.typesafe.ai/v1/systemone"
AGES = {
    "kids": "children 6-11, short simple sentences, silly humor",
    "teens": "teenagers 13-17, fast, ironic, native to trends",
    "young": "adults 18-29, fast, self-aware humor, informal",
    "adults": "adults 30-45, practical, short on time, wants proof",
    "parents": "parents of young children, tired, values time and trust",
    "mature": "adults 45-60, calm pace, warm humor, clear and concrete",
    "seniors": "adults 60+, slow pace, large text, respectful tone",
}
# Composite: only the "quality" dimensions, normalized 0-1. Change weights freely; no re-inference needed.
DEFAULT_WEIGHTS = {"hook_gap": 3, "twist_strength": 3, "audience_fit": 2, "clarity_after_reveal": 2, "warmth": 1}
LEVELS = {"hook_gap": 3, "twist_strength": 3, "audience_fit": 3, "clarity_after_reveal": 3, "warmth": 3}


def call(state, questions, key):
    body = json.dumps({"state": state, "model": "jev-latest", "questions": questions}).encode()
    req = urllib.request.Request(URL, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fill(q, age):
    return json.loads(json.dumps(q).replace("{AGE}", AGES[age]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--age", default="adults", choices=AGES)
    ap.add_argument("--weights")
    ap.add_argument("--save"); ap.add_argument("--load"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    rub = json.load(open(os.path.join(HERE, "rubrics.json")))
    s = json.load(open(a.script))
    weights = json.load(open(a.weights)) if a.weights else DEFAULT_WEIGHTS

    sq = {k: fill(v, a.age) for k, v in rub["script_level"].items()}
    state = {"hook": s["hook"], "body": s["body"], "facts": s.get("facts", [])}
    if a.dry_run:
        print(json.dumps({"state": state, "questions": sq}, ensure_ascii=False, indent=1)[:1500]); return
    if a.load:
        raw = json.load(open(a.load))
    else:
        key = os.environ.get("TYPESAFE_API_KEY") or sys.exit("TYPESAFE_API_KEY not set")
        lines = s.get("lines", [])
        raw = {"script": call(state, sq, key)["answers"],
               "lines": [call({"line": l, "script": s["body"]}, rub["line_level"], key)["answers"] for l in lines]}
        if a.save: json.dump(raw, open(a.save, "w"), ensure_ascii=False, indent=1)

    ans = raw["script"]
    print(f"## Script judgment (age: {a.age})\n\n| dimension | value | confidence |\n|---|---|---|")
    for k, v in ans.items():
        val = v.get("score", v.get("noul")); conf = v.get("confidence", "")
        print(f"| {k} | {val:.2f} | {conf if conf == '' else f'{conf:.2f}'} |")
    tot = sum(weights.values())
    comp = sum(weights[k] * ans[k]["score"] / LEVELS[k] for k in weights if k in ans) / tot
    print(f"\n**Composite (0-1): {comp:.2f}**  weights={weights}")
    flags = []
    if ans["offer_in_first_3s"]["noul"] > 0.5: flags.append("offer stated in first 3s (breaks twist rule)")
    if ans["needs_sound"]["noul"] > 0.5: flags.append("a beat is not clear on mute")
    if ans["unverified_claim"]["noul"] > 0.5: flags.append("claim not in facts.md")
    for k, v in ans.items():
        if v.get("confidence", 1) < 0.4: flags.append(f"{k}: low confidence, review by hand")
    print("\n**Flags:** " + ("; ".join(flags) if flags else "none"))
    if raw["lines"]:
        print("\n## Lines\n\n| # | role | clarity | single-gender |\n|---|---|---|---|")
        for i, l in enumerate(raw["lines"]):
            print(f"| {i+1} | {l['line_role']['choice']} | {l['line_clarity']['score']:.1f} | {l['line_gendered']['noul']:.2f} |")


if __name__ == "__main__":
    main()
