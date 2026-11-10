"""Stage 0: mechanical prep of RAW material about a person (files, scans, GEDCOM, notes).

usage: ingest.py <raw_dir_or_file> <research_dir>
Reads (never modifies) the raw material and writes into <research_dir>/raw/:
  NNN_<name>.txt   extracted text per file (images / scanned PDFs are only listed: read them visually
                   with render.py / contact.py)
  INDEX.md         per file: type, size, likely languages, years seen, cue counts, needs-visual flag;
                   plus a corpus summary: regions mentioned (from routing_data.json keys) and year histogram
  MINED.tsv        anchor points: file, line, cue type, years in line, snippet  (birth / residence /
                   marriage / death / military / emigration / persecution cues in he/en/de/hu/pl/fr)
This is NOT understanding. Claude then READS the material (references/intake.md) and fills
PLACES.md, PEOPLE.md, FACTS.md; plan_sources.py turns PLACES.md into a source plan.
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import IMG_EXT, lp, walk_files, short  # noqa: E402
import extract as ex  # noqa: E402

CUES = {
    "לידה": r"נולד|נולדה|לידתו|born\b|\bb\.\s*\d|geboren|\bgeb\.|született|szül\.|urodz|\bné le\b|\bnée\b|nacido|nato a",
    "מגורים": r"גר ב|התגורר|מתגורר|גרו ב|lived in|resided|residing|wohnhaft|wohnte|lakott|lakhely|mieszkał|domicil|habitait|\bwohnort\b",
    "נישואין": r"נישא|נשא את|התחתנ|married|marriage|verheiratet|heiratete|\bhochzeit|házas|nősül|ślub|\bmarié",
    "פטירה": r"נפטר|נפטרה|מת ב|נהרג|נרצח|died|death|gestorben|\bverstorben|meghalt|elhunyt|zmarł|décédé|\bd\.\s*\d",
    "שירות צבאי": r"שירת|התגייס|גויס|קצין|חייל|שבוי|שבי|army|served in|soldier|regiment|\bPOW\b|prisoner of war|militär|infanterie|regiment|honvéd|katona|k\.u\.k|k\.k\.|\bIR\s*\d+|front\b|גדוד|חזית",
    "הגירה": r"עלה |עלייה|עלו |הגר|היגר|emigrat|immigrat|\bship\b|ausgewandert|auswander|kivándorol|אנייה|ספינה|ויזה|סרטיפיקט|certificate",
    "שואה": r"גורש|גירוש|גטו|מחנה|נרצח|שואה|deport|ghetto|camp\b|auschwitz|theresienstadt|treblinka|transport\b|holocaust|deportiert|gettó|deportálás|stolperstein|אבן נגף",
    "עיסוק": r"עסק ב|סוחר|רופא|רב\b|שוחט|מורה|עורך דין|תופר|פרנס|merchant|physician|rabbi\b|teacher|lawyer|kaufmann|beruf|kereskedő|foglalkozás",
}
CUE_RE = {k: re.compile(v, re.I) for k, v in CUES.items()}
YEAR_RE = re.compile(r"\b(1[5-9]\d\d|20[0-2]\d)\b")
LANG_HINTS = {
    "גרמנית": "äöüß",
    "הונגרית": "őűáéíóú",
    "פולנית": "łąęśćżźń",
    "צ'כית": "řěčšžů",
    "רומנית": "ăâîșț",
    "צרפתית": "àèùçêëîïôû",
}
TEXT_EXT = ex.TEXT_EXT
GEDCOM_PLACE = re.compile(r"^\s*\d+\s+PLAC\s+(.+)$", re.M)


def langs(text):
    he = len(re.findall(r"[֐-׿]", text))
    la = len(re.findall(r"[A-Za-z]", text))
    cy = len(re.findall(r"[Ѐ-ӿ]", text))
    tot = max(1, he + la + cy)
    out = []
    if he / tot > 0.1:
        out.append("עברית")
    if la / tot > 0.1:
        out.append("לטינית")
    if cy / tot > 0.1:
        out.append("קירילית")
    low = text.lower()
    for name, chars in LANG_HINTS.items():
        if sum(low.count(c) for c in chars) >= 5 and la / tot > 0.1:
            out.append(name + "?")
    return ", ".join(out) or "-"


def region_keys():
    d = json.load(open(os.path.join(HERE, "routing_data.json"), encoding="utf-8"))
    res = []
    for r in d["regions"]:
        for k in r["keys"]:
            res.append((r["id"], r["name"], k.lower()))
    return res


def mentions(text, keys):
    low = text.lower()
    c = Counter()
    for rid, name, k in keys:
        if len(k) < 4:
            continue
        if re.fullmatch(r"[a-z .'\-]+", k):
            n = len(re.findall(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", low))
        else:
            n = low.count(k)
        if n:
            c[(rid, name)] += n
    return c


def safe(s):
    return re.sub(r"[^\w.\-]+", "_", s, flags=re.U)[:60]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    raw, root = sys.argv[1], sys.argv[2]
    out = os.path.join(root, "raw")
    os.makedirs(out, exist_ok=True)
    keys = region_keys()
    rows, mined = [], []
    corpus_regions, years_all = Counter(), Counter()
    n = 0
    for f in walk_files(raw, TEXT_EXT | IMG_EXT):
        n += 1
        ext = os.path.splitext(f)[1].lower()
        name = os.path.basename(f)
        size = os.path.getsize(lp(f))
        if ext in IMG_EXT:
            rows.append((n, name, "תמונה", size, "-", "-", "-", "כן: contact.py + קריאה חזותית (גב התמונה, כתב יד, חותמות)"))
            continue
        try:
            text = ex.extract(f)
        except Exception as e:  # keep going on a bad file
            rows.append((n, name, ext, size, "-", "-", "-", f"שגיאת חילוץ: {type(e).__name__}"))
            continue
        scanned = text.startswith("[SCANNED PDF")
        tf = f"{n:03d}_{safe(os.path.splitext(name)[0])}.txt"
        open(os.path.join(out, tf), "w", encoding="utf-8").write(text)
        years = Counter(YEAR_RE.findall(text))
        years_all.update(years)
        cues = Counter()
        for ln_no, line in enumerate(text.splitlines(), 1):
            if len(line.strip()) < 4:
                continue
            ys = YEAR_RE.findall(line)
            for cue, rx in CUE_RE.items():
                if rx.search(line):
                    cues[cue] += 1
                    snippet = re.sub(r"\s+", " ", line.strip())[:220]
                    mined.append((tf, ln_no, cue, ",".join(ys), snippet))
        if ext == ".ged":
            for p in GEDCOM_PLACE.findall(text):
                mined.append((tf, 0, "GEDCOM-מקום", "", p.strip()))
        reg = mentions(text, keys)
        corpus_regions.update(reg)
        yr = f"{min(years)}-{max(years)}" if years else "-"
        cs = ", ".join(f"{k}:{v}" for k, v in cues.most_common()) or "-"
        visual = "כן: PDF סרוק, לרנדר וגם לקרוא בעין" if scanned else ("בדוק תמונות מוטמעות" if ext in (".docx", ".pptx", ".html", ".htm") else "לא")
        rows.append((n, f"{name} -> {tf}", ext, size, langs(text), yr, cs, visual))
    with open(os.path.join(out, "MINED.tsv"), "w", encoding="utf-8") as f:
        f.write("file\tline\tcue\tyears\tsnippet\n")
        for r in mined:
            f.write("\t".join(str(x) for x in r) + "\n")
    with open(os.path.join(out, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(f"# אינדקס חומר גולמי\n\nמקור: `{raw}`. {n} קבצים. נוצר אוטומטית ב-`ingest.py` - הכנה מכנית, לא הבנה.\n\n")
        f.write("## קבצים\n| # | קובץ | סוג | בתים | שפות (משוער) | שנים | אותות (cue:מספר) | דורש קריאה חזותית |\n|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |\n")
        f.write("\n## אזורים שמוזכרים בחומר (לפי קטלוג המקורות; מספר אזכורים)\n")
        if corpus_regions:
            for (rid, name), c in corpus_regions.most_common():
                f.write(f"- {name} (`{rid}`): {c}\n")
        else:
            f.write("- לא זוהו אזורים מוכרים: לקרוא את החומר ולזהות בעצמך (ייתכן אזור שאינו בקטלוג - ראו `references/routing.md`)\n")
        f.write("\n## התפלגות שנים (לפי עשורים)\n")
        dec = Counter()
        for y, c in years_all.items():
            dec[int(y) // 10 * 10] += c
        for d in sorted(dec):
            f.write(f"- {d}s: {dec[d]}\n")
        f.write(f"\n## צעד הבא\nלקרוא את הקבצים (ראו `references/intake.md`), להשתמש ב-`MINED.tsv` כעוגנים, ולמלא `PLACES.md`, `PEOPLE.md`, `FACTS.md`. אחר כך: `python scripts/plan_sources.py {root}`.\n")
    print(f"ingested {n} files -> {out}/INDEX.md, MINED.tsv ({len(mined)} anchors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
