"""Turn the person's life-footprint (PLACES.md) into a prioritized source plan (SOURCE_PLAN.md).

usage: plan_sources.py <research_dir>
Reads  <research_dir>/PLACES.md  (header lines: שנת לידה / שנת פטירה / מין, and the places table)
Reads  routing_data.json         (regions with multilingual keys, universal sources, event triggers)
Writes <research_dir>/SOURCE_PLAN.md

Matching: a row's place / alternate names / state-then / state-today are matched against region keys
(Hebrew prefixes ב/ל/מ/ה/ו/כ/ש allowed). A row may match several regions (e.g. Galicia -> Poland and Ukraine
sources) - that is intended: the right archive depends on the YEAR, so check both.
Triggers add event-based sources (e.g. WWI service for a man born 1865-1900 in Austria-Hungary).
Rows that match nothing get web-search queries: the catalog is not complete and that is expected.
Status marks: ✓ tried in real research, ◐ learned (not verified), ○ general knowledge (verify first).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lint_research import tables  # noqa: E402

YEAR = re.compile(r"(1[5-9]\d\d|20[0-2]\d)")
ACCESS_ORDER = {"online-free": 0, "online-paid": 1, "letter": 2, "onsite": 3}
STATUS_ORDER = {"V": 0, "L": 1, "G": 2}
STATUS_MARK = {"V": "✓", "L": "◐", "G": "○"}
ACCESS_LABEL = {"online-free": "מקוון חינם", "online-paid": "מקוון בתשלום", "letter": "מכתב/טופס", "onsite": "באתר/בעל פה"}
HEB_PREFIX = "בלמהוכש"


def key_regex(k):
    k = k.lower()
    if re.search(r"[֐-׿]", k):
        return re.compile(r"(?<![֐-׿])[" + HEB_PREFIX + r"]?" + re.escape(k) + r"(?![֐-׿])")
    return re.compile(r"(?<![a-zà-ž])" + re.escape(k) + r"(?![a-zà-ž])")


def load():
    d = json.load(open(os.path.join(HERE, "routing_data.json"), encoding="utf-8"))
    for r in d["regions"]:
        r["_rx"] = [key_regex(k) for k in r["keys"]]
    return d


def years_of(s):
    ys = [int(y) for y in YEAR.findall(s or "")]
    return (min(ys), max(ys)) if ys else None


def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def mark(s):
    return f"{STATUS_MARK[s['status']]}"


def fmt_src(s):
    url = f" - {s['url']}" if s.get("url") else ""
    note = f" ({s['notes']})" if s.get("notes") else ""
    return f"{mark(s)} **{s['name']}**{url} [{ACCESS_LABEL.get(s['access'], s['access'])}]{note}"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print(__doc__)
        return 1
    root = sys.argv[1]
    p = os.path.join(root, "PLACES.md")
    if not os.path.exists(p):
        print("PLACES.md missing - run new_research.py or copy templates/PLACES.md first")
        return 1
    text = open(p, encoding="utf-8").read()
    by = re.search(r"^שנת לידה:\s*(\d{4})", text, re.M)
    dy = re.search(r"^שנת פטירה:\s*(\d{4})", text, re.M)
    sx = re.search(r"^מין:\s*(ז|נ)", text, re.M)
    birth = int(by.group(1)) if by else None
    death = int(dy.group(1)) if dy else None
    sex = sx.group(1) if sx else None
    life = (birth or 1500, death or 2100)
    data = load()
    regions = {r["id"]: r for r in data["regions"]}

    rows = []
    for h, header, trs in tables(text):
        if "מקום (כפי שנכתב במקור)" in header:
            for r in trs:
                if any(v for k, v in r.items() if k != "#"):
                    rows.append(r)
    if not rows:
        print("PLACES.md has no filled rows - extract the footprint from raw/ first (references/intake.md)")
        return 1

    per_row, unmatched, trig_hits = [], [], []
    region_periods = {}   # region id -> list of (period or None, row#)
    row_events = []
    for i, r in enumerate(rows, 1):
        num = r.get("#") or str(i)
        blob = " ".join([r.get("מקום (כפי שנכתב במקור)", ""), r.get("שמות חלופיים", ""), r.get("מדינה/שיפוט אז", ""), r.get("מדינה היום", "")]).lower()
        per = years_of(r.get("מ-", "") + " " + r.get("עד", ""))
        ev = r.get("אירוע/סוג", "")
        blob_then = " ".join([r.get("מקום (כפי שנכתב במקור)", ""), r.get("שמות חלופיים", ""), r.get("מדינה/שיפוט אז", "")]).lower()
        matched = [rid for rid, reg in regions.items() if any(rx.search(blob_then) for rx in reg["_rx"])]
        weak = [rid for rid, reg in regions.items() if rid not in matched and any(rx.search(blob) for rx in reg["_rx"])]
        for rid in matched:
            region_periods.setdefault(rid, []).append((per, num))
        row_events.append((num, ev, matched, per))
        if matched or weak:
            per_row.append((num, r, matched, per, ev, weak))
        if not matched and not weak:
            unmatched.append((num, r, per))

    # triggers
    for t in data["triggers"]:
        reasons, ok = [], True
        if t.get("sex") and sex and t["sex"] != sex:
            continue
        if t.get("birth_between"):
            lo, hi = t["birth_between"]
            if birth is not None and not (lo <= birth <= hi):
                continue
            if birth is None:
                reasons.append("שנת לידה לא ידועה - לבדוק התאמה")
        if t.get("period") and not overlap(t["period"], life):
            continue
        hit_rows = []
        if t.get("regions"):
            for rid in t["regions"]:
                for per, num in region_periods.get(rid, []):
                    if t.get("period") and per is not None:
                        if t.get("since_before_end"):
                            if per[0] > t["period"][1]:
                                continue
                        elif not overlap(per, tuple(t["period"])):
                            continue
                    hit_rows.append(num + (" (תקופה לא ידועה)" if per is None and t.get("period") else ""))
            if not hit_rows:
                continue
        if t.get("event_types"):
            ev_hits = [num for num, ev, m, per in row_events if any(e in ev for e in t["event_types"])]
            if ev_hits:
                hit_rows += ev_hits
            elif not t.get("regions"):
                continue
        trig_hits.append((t, sorted(set(hit_rows)), reasons))

    # priority list
    agg = {}

    def add(s, why):
        a = agg.setdefault(s["name"], {"s": s, "why": set()})
        a["why"].add(why)

    for num, r, matched, per, ev, weak in per_row:
        for rid in matched:
            for s in regions[rid]["sources"]:
                add(s, f"שורה {num}")
    for t, hr, _ in trig_hits:
        for s in t["sources"]:
            add(s, f"טריגר: {t['name']}")
    for s in data["universal"]:
        add(s, "כללי")
    ranked = sorted(agg.values(), key=lambda a: (ACCESS_ORDER.get(a["s"]["access"], 9), STATUS_ORDER.get(a["s"]["status"], 9), -len(a["why"]), a["s"]["name"]))

    out = []
    w = out.append
    w("# תוכנית מקורות\n")
    w("> נוצר אוטומטית מ-`PLACES.md` על ידי `plan_sources.py`. לא לערוך ידנית: עורכים את `PLACES.md` ומריצים שוב.")
    w("> ✓ נוסה במחקר אמיתי · ◐ נלמד, לא אומת · ○ ידע כללי, לאמת לפני שמסתמכים. הקטלוג חלקי: מקום בלי התאמה נמצא בסוף עם חיפושים מוצעים.\n")
    w(f"אדם: לידה {birth or '?'} · פטירה {death or '?'} · מין {sex or '?'} · {len(rows)} שורות מסלול\n")
    w("## 1. סדר חיפוש מומלץ (מקוון וחינם קודם; ✓ לפני ◐ לפני ○)")
    w("| # | מקור | נגיש | למה (שורות / טריגרים) |\n|---|---|---|---|")
    for i, a in enumerate(ranked, 1):
        s = a["s"]
        w(f"| {i} | {mark(s)} {s['name']}{' - ' + s['url'] if s.get('url') else ''} | {ACCESS_LABEL.get(s['access'], s['access'])} | {'; '.join(sorted(a['why']))} |")
    w("\n## 2. לפי שורה במסלול החיים")
    for num, r, matched, per, ev, weak in per_row:
        pl = r.get("מקום (כפי שנכתב במקור)", "")
        when = f"{per[0]}-{per[1]}" if per else "תקופה לא ידועה"
        w(f"\n### שורה {num}: {pl} ({when}) · {ev or 'אירוע לא צוין'}")
        w(f"מדינה אז: {r.get('מדינה/שיפוט אז') or '?'} · היום: {r.get('מדינה היום') or '?'} · תווית: {r.get('תווית') or '?'}")
        for rid in matched:
            reg = regions[rid]
            w(f"- **{reg['name']}** - {reg['note']}")
            srcs = sorted(reg["sources"], key=lambda s: (ev and not any(e in ev for e in s["types"]), ACCESS_ORDER.get(s["access"], 9), STATUS_ORDER.get(s["status"], 9)))
            for s in srcs:
                star = "★ " if ev and any(e in ev for e in s["types"]) else ""
                w(f"  - {star}{fmt_src(s)}")
        for rid in weak:
            w(f"- (פחות סביר לתקופה: רק לפי המדינה של היום) **{regions[rid]['name']}** - רק אם הרשומה הועברה לשם או נוצרה אחרי שינוי הגבול; מקורות: " + "; ".join(s["name"] for s in regions[rid]["sources"][:3]))
        if len(matched) > 1:
            w("- שימו לב: התאמה לכמה אזורים (שינוי שיפוט). הרשומה נוצרה אצל הרשות ששלטה בשנה הרלוונטית - לבדוק בשיפוט של אותה שנה, והיום לחפש במדינה היורשת.")
        if per is None:
            w("- תקופה לא ידועה: להשלים מהחומר או לתת לשורה סטטוס 'אולי'.")
    w("\n## 3. אירועים שזוהו (טריגרים)")
    if trig_hits:
        for t, hr, reasons in trig_hits:
            w(f"\n### {t['name']}")
            w(f"שורות: {', '.join(hr) or '-'}" + (f" · הערות: {'; '.join(reasons)}" if reasons else ""))
            for s in t["sources"]:
                w(f"- {fmt_src(s)}")
    else:
        w("- אין. (בדקו שמולאו שנת לידה ומין ב-`PLACES.md`.)")
    w("\n## 4. שורות בלי התאמה בקטלוג - חיפושי רשת מוצעים")
    if unmatched:
        for num, r, per in unmatched:
            pl = r.get("מקום (כפי שנכתב במקור)", "")
            alt = [a.strip() for a in re.split(r"[;,/]", r.get("שמות חלופיים", "")) if a.strip()]
            yrs = f"{per[0]}-{per[1]}" if per else ""
            w(f"\n### שורה {num}: {pl}")
            clean = lambda x: re.sub(r'["“”?]', "", x).strip()
            for nm in [clean(x) for x in [pl] + alt[:2] if clean(x)]:
                w(f"- `\"{nm}\" Jewish records {yrs}` · `\"{nm}\" jewishgen KehilaLinks` · `\"{nm}\" yizkor book` · `site:familysearch.org/en/wiki \"{nm}\"`")
            w("- לקבוע שיפוט לפי שנה (`references/routing.md`), ואם נמצא מקור חדש: להוסיף ל-`routing_data.json` עם סטטוס ○ ו-`sources.md`.")
    else:
        w("- כל השורות הותאמו.")
    w("\n## 5. מה לעשות עם התוכנית")
    w("1. להעתיק ל-`PLAN.md`: לכל שאלה, סוגי הרשומות והארכיונים שנבחרו (מטריצת רשומות), ולרשום סדר חיפוש.")
    w("2. להתחיל ממקורות ✓ מקוונים וחינמיים. ◐ ו-○ - לאמת כתובת ותנאים לפני חיפוש ארוך או מכתב.")
    w("3. מקורות בכתב או בטופס: טיוטה למשתמש (`letters.md`).")
    w("4. אחרי סבב חיפוש: לעדכן `PLACES.md` עם מה שנמצא (מקומות חדשים!), ולהריץ שוב.")
    open(os.path.join(root, "SOURCE_PLAN.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"SOURCE_PLAN.md written: {len(ranked)} distinct sources, {len(per_row)} matched rows, {len(unmatched)} unmatched, {len(trig_hits)} triggers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
