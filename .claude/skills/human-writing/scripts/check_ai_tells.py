#!/usr/bin/env python3
"""בודק טקסט (עברית או אנגלית) מול סימני כתיבה של AI ומדפיס ממצאים עם מספרי שורה.

שימוש:
  python3 check_ai_tells.py draft.md
  cat draft.md | python3 check_ai_tells.py -
  python3 check_ai_tells.py draft.md --allow-markdown   # טקסט שבו עיצוב מותר

קוד יציאה: 0 = נקי או אזהרה בלבד, 1 = יש סימנים שצריך לתקן.
סימן בודד לא מוכיח כלום. הבדיקה מחפשת הצטברות, והסימנים הקשיחים נחשבים תמיד.
"""
import argparse
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

HARD_CHARS = {
    "מקף ארוך (—)": "—",
    "מקף בינוני (–)": "–",
    "מקף עברי (־), מחליפים במקף רגיל": "־",
    "מרכאות מסולסלות/תחתונות": "“”„‘’‚",
    "רווח לא שבור צר או רווח רוחב אפס": " ​⁠",
    "סימן יוניקוד חריג (חץ, ≈, קו תיבה)": "≈─│└├→←⇒✓✔",
}
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆⬇]")
PAREN_TRANSLATION = re.compile(r"[֐-׿]{2,}\s*\([A-Za-z][A-Za-z0-9 .\-/]{1,40}\)")

NEG_PIVOT = [
    r"לא\s+רק\s+.{3,90}?\s+אלא\s+(גם\s+)?",
    r"אין\s+(מדובר|מדובר\s+כאן)\s+ב.{3,70}?\s+אלא\s+ב",
    r"(?<!\S)(זה|זו|זהו|זאת)\s+לא\s+.{2,40}?[,.]\s*(זה|זו|זהו|זאת)\s",
    r"(?i)\bnot\s+(just|only|merely)\s+.{3,70}?[,;]?\s+(but|it'?s)\b",
    r"(?i)\b(it'?s|this is|that'?s)\s+not\s+.{2,40}?[,.]\s*(it'?s|this is|that'?s)\b",
    r"(?i)\bisn'?t\s+just\b",
]
TRIAD = re.compile(r"[\w֐-׿'\"]+, [\w֐-׿'\"]+,? (?:ו[־-]?|and |or )[\w֐-׿'\"]+")

MD_PATTERNS = {
    "הדגשה בכוכביות (**)": re.compile(r"\*\*[^*\n]+\*\*"),
    "כותרת בסימני #": re.compile(r"^[ \t]{0,3}#{1,6}[ \t]", re.M),
    "תבליט": re.compile(r"^[ \t]*[-*•][ \t]+\S", re.M),
    "קו מפריד": re.compile(r"^[ \t]*(---+|\* \* \*)[ \t]*$", re.M),
    "טבלה": re.compile(r"^[ \t]*\|.+\|[ \t]*$", re.M),
    "רשימה ממוספרת": re.compile(r"^[ \t]*\d+[.)][ \t]+\S", re.M),
}

HARD_CATEGORIES = {"chatbot"}
CATEGORY_NAMES = {
    "chatbot": "שאריות מהצ'אט",
    "inflated": "ניפוח חשיבות / קלישאות",
    "filler": "מילות סירוס ומילוי",
    "connector": "מחברים וסיכומים",
    "calque": "ביטויים מתורגמים / מילות יוקרה",
    "vague_attr": "ייחוס מעורפל",
    "analysis_tail": "זנב ניתוחי (ובכך מדגיש...)",
    "hedge": "הסתייגות נוסחתית",
    "promo": "שפה שיווקית",
}


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def snippet(text, start, end, pad=25):
    s = max(0, start - pad)
    e = min(len(text), end + pad)
    return text[s:e].replace("\n", " ").strip()


def load_phrases():
    items = []
    path = HERE / "phrases.txt"
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        cat, _, rx = raw.partition("\t")
        items.append((cat, re.compile(rx, re.M)))
    return items


def sentences(text):
    plain = re.sub(r"[#*>`|]", " ", text)
    parts = re.split(r"(?<=[.!?:])\s+|\n+", plain)
    return [p for p in parts if len(p.split()) >= 2]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="נתיב לקובץ, או - לקריאה מ-stdin")
    ap.add_argument("--allow-markdown", action="store_true", help="לא לדווח על עיצוב Markdown")
    args = ap.parse_args()

    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    words = len(text.split())
    hard, soft = [], []

    for label, chars in HARD_CHARS.items():
        for m in re.finditer("[" + re.escape(chars) + "]", text):
            hard.append((line_of(text, m.start()), label, snippet(text, m.start(), m.end())))
    for m in EMOJI.finditer(text):
        hard.append((line_of(text, m.start()), "אמוג'י", snippet(text, m.start(), m.end())))
    for m in PAREN_TRANSLATION.finditer(text):
        hard.append((line_of(text, m.start()), "סוגריים מתרגמים", snippet(text, m.start(), m.end(), 5)))

    for cat, rx in load_phrases():
        for m in rx.finditer(text):
            target = hard if cat in HARD_CATEGORIES else soft
            target.append((line_of(text, m.start()), CATEGORY_NAMES.get(cat, cat), snippet(text, m.start(), m.end())))

    for pat in NEG_PIVOT:
        for m in re.finditer(pat, text, re.S):
            soft.append((line_of(text, m.start()), "שלילה והצבה (לא רק X אלא Y)", snippet(text, m.start(), m.end(), 5)))

    triads = list(TRIAD.finditer(text))
    if words and len(triads) * 1000 / words > 6 and len(triads) >= 3:
        soft.append((line_of(text, triads[0].start()), f"שלשות בצפיפות גבוהה ({len(triads)} ב-{words} מילים)", snippet(text, triads[0].start(), triads[0].end(), 5)))

    if not args.allow_markdown:
        for label, rx in MD_PATTERNS.items():
            for m in rx.finditer(text):
                soft.append((line_of(text, m.start()), f"עיצוב: {label}", snippet(text, m.start(), m.end(), 5)))

    sents = sentences(text)
    lengths = [len(s.split()) for s in sents]
    rhythm_note = ""
    if len(lengths) >= 8:
        mean = statistics.mean(lengths)
        cv = statistics.pstdev(lengths) / mean if mean else 0
        in_band = sum(1 for n in lengths if 8 <= n <= 20) / len(lengths)
        rhythm_note = f"אורך משפט ממוצע {mean:.1f} מילים, שונות {cv:.2f}, {in_band:.0%} מהמשפטים בין 8 ל-20 מילים"
        if cv < 0.40 or in_band > 0.80:
            soft.append((0, "קצב אחיד מדי", rhythm_note))

    print(f"{words} מילים, {len(sents)} משפטים")
    if rhythm_note:
        print(rhythm_note)
    for title, items in (("קשיחים (לתקן תמיד)", hard), ("רכים (לבדוק בהקשר)", soft)):
        if items:
            print(f"\n{title}: {len(items)}")
            for ln, label, snip in sorted(items):
                where = f"שורה {ln}" if ln else "כללי"
                print(f"  {where} | {label} | {snip}")

    if hard or len(soft) >= 3:
        verdict, code = "יש סימנים שצריך לתקן", 1
    elif soft:
        verdict, code = "אזהרה, בדוק את הממצאים הבודדים", 0
    else:
        verdict, code = "נקי", 0
    print(f"\nתוצאה: {verdict} (קשיחים {len(hard)}, רכים {len(soft)})")
    sys.exit(code)


if __name__ == "__main__":
    main()
