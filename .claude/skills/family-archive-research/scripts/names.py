"""Name-variant generator for Central/Eastern European Jewish genealogy.

HEURISTIC helper: it produces *candidates to search*, never conclusions. Always
verify a hit against the record (parents, place, dates). For a true phonetic
index use the JewishGen Daitch-Mokotoff Soundex tool online; this script is the
quick offline companion that also covers Hebrew-script spelling and OCR errors.

usage:
  names.py surname Schwarz            # Latin-script surname variants
  names.py surname שפיצר              # Hebrew-script spelling + OCR confusions
  names.py given Heinrich             # Hebrew/secular given-name equivalents
  names.py given יצחק                 # reverse lookup
  names.py order "Adler Henrik"       # Hungarian/Western name-order variants
  options: --max N (default 60)
"""
import itertools
import re
import sys
import unicodedata

# ---------- Latin-script surname variants ----------
# Each group lists spellings that can stand for the same sound across
# German / Hungarian / Polish / Yiddish / Russian / English orthographies.
# Longest keys are matched first (see _tokenize).
GROUPS = [
    # sh-sound
    ["sch", "sh", "sz", "s", "š"],      # Hungarian "s" = sh; Polish "sz" = sh; German "sch"
    # ts-sound
    ["tz", "z", "cz", "c", "ts", "tc"],  # Hungarian "c" = ts; Polish "cz" = ch (see below) but written for ts in German
    # ch-sound (as in "church")
    ["tsch", "cs", "ch", "č", "tch"],
    # v/w
    ["w", "v"],
    # diphthong "eye"
    ["ei", "ey", "ai", "ay", "aj", "ej"],
    ["ie", "i", "y", "ij"],
    ["gy", "dj", "dy"],
    ["ow", "ov", "off", "ev", "eff"],
    ["mann", "man"],
    ["berg", "burg", "perg", "borg"],
    ["stein", "shtein", "sztejn", "stajn"],
]

# One-way rules: a spelling that is only ever *simplified* in other records
# (never the reverse), so we do not generate noise like Adler -> Adtler.
DIRECTED = {
    "ck": ["k", "c"], "ph": ["f"], "th": ["t"], "dt": ["t"], "ss": ["s", "ß"], "ß": ["ss", "s"],
    "ä": ["ae", "a", "e"], "ö": ["oe", "o"], "ü": ["ue", "u"],
    "ae": ["ä", "a", "e"], "oe": ["ö", "o"], "ue": ["ü", "u"],
}

# Initial clusters: German "sp"/"st" are pronounced "shp"/"sht".
INITIALS = [
    ["sp", "schp", "szp", "shp"],
    ["st", "scht", "szt", "sht"],
]

_KEYS = sorted({k for g in GROUPS for k in g} | set(DIRECTED), key=lambda s: (-len(s), s))
_GROUP_OF = {}
for g in GROUPS:
    for k in g:
        _GROUP_OF.setdefault(k, []).append(g)


def _strip_diacritics(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _tokenize(word):
    """Greedy split into known grapheme units and single letters."""
    out, i = [], 0
    while i < len(word):
        for k in _KEYS:
            if word.startswith(k, i) and (k in _GROUP_OF or k in DIRECTED):
                out.append(k)
                i += len(k)
                break
        else:
            out.append(word[i])
            i += 1
    return out


def latin_variants(name, limit=60):
    name = name.strip().lower()
    base = name
    out = {name: 0}
    # initial clusters
    for grp in INITIALS:
        for k in grp:
            if name.startswith(k):
                for alt in grp:
                    if alt != k:
                        out[alt + name[len(k):]] = out.get(alt + name[len(k):], 1)
    toks = _tokenize(base)
    options = []
    for t in toks:
        opts = {t}
        for g in _GROUP_OF.get(t, []):
            opts.update(g)
        opts.update(DIRECTED.get(t, []))
        options.append(sorted(opts, key=lambda x: (x != t, x)))
    # limit blowup: allow at most 2 substitutions per variant
    combos = []
    for idx_set in itertools.chain([()], itertools.combinations(range(len(toks)), 1), itertools.combinations(range(len(toks)), 2)):
        pools = []
        for i, t in enumerate(toks):
            pools.append([x for x in options[i] if x != t] if i in idx_set else [t])
        if idx_set and any(len(p) == 0 for p in pools):
            continue
        for combo in itertools.product(*pools):
            combos.append(("".join(combo), len(idx_set)))
        if len(combos) > 5000:
            break
    for v, n in combos:
        out.setdefault(v, n)
    ranked = sorted(out.items(), key=lambda kv: (kv[1], sum(ord(c) > 127 for c in kv[0]), len(kv[0]), kv[0]))
    ascii_name = _strip_diacritics(name)
    if ascii_name != name:
        ranked.insert(1, (ascii_name, 0))
    seen, res = set(), []
    for v, _ in ranked:
        if v not in seen:
            seen.add(v)
            res.append(v.capitalize())
    return res[:limit]


# ---------- Hebrew-script variants ----------
HEB_FINAL = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
HEB_UNFINAL = {v: k for k, v in HEB_FINAL.items()}
# Visually or phonetically confusable letters (OCR / spelling).
OCR_PAIRS = ["דר", "וי", "הח", "חת", "הת", "בכ", "גנ", "גז", "וז", "וןן", "יו", "כנ", "מס", "ןו", "עצ", "פס", "צל", "קף", "רך", "שמ", "אע", "טפ"]
OCR_MAP = {}
for pair in OCR_PAIRS:
    for a, b in itertools.permutations(pair, 2):
        OCR_MAP.setdefault(a, set()).add(b)


def _is_hebrew(s):
    return bool(re.search("[֐-׿]", s))


def hebrew_variants(name, limit=60):
    """Plene/defective spelling (add/remove י, ו), final -ר/-ער, OCR single swaps."""
    name = re.sub("[֑-ׇ]", "", name.strip())  # drop niqqud
    out = {name: 0}
    # plene/defective: add or remove י/ו inside the word
    for i, c in enumerate(name):
        if c in "יו" and 0 < i < len(name) - 1:
            out.setdefault(name[:i] + name[i + 1:], 1)
    for i in range(1, len(name)):
        for m in "יו":
            out.setdefault(name[:i] + m + name[i:], 1)
    # final -ער / -ר
    if name.endswith("ער"):
        out.setdefault(name[:-2] + "ר", 1)
    elif name.endswith("ר"):
        out.setdefault(name[:-1] + "ער", 1)
    # שׁ/ס alternation for foreign sibilants
    for i, c in enumerate(name):
        if c in "שס":
            out.setdefault(name[:i] + ("ס" if c == "ש" else "ש") + name[i + 1:], 2)
    # OCR single substitutions (marked lower priority), on the base spelling
    # and on its -ער/-ר counterpart (e.g. שפיצער -> שפילער)
    bases = [name]
    if name.endswith("ער"):
        bases.append(name[:-2] + "ר")
    elif name.endswith("ר"):
        bases.append(name[:-1] + "ער")
    for base in bases:
        for i, c in enumerate(base):
            cc = HEB_FINAL.get(c, c)          # final form -> regular letter, for lookup
            for alt in OCR_MAP.get(cc, ()):
                if i == len(base) - 1:
                    alt = HEB_UNFINAL.get(alt, alt)  # regular -> final form at word end
                out.setdefault(base[:i] + alt + base[i + 1:], 3)
    ranked = sorted(out.items(), key=lambda kv: (kv[1], len(kv[0]), kv[0]))
    return [v for v, _ in ranked][:limit]


# ---------- Given-name equivalents (heuristic) ----------
# Hebrew/Yiddish name -> secular names used in German, Hungarian, Polish,
# Russian, English records. These are COMMON pairings, not rules; a person may
# have any secular name. Use them only to widen a search.
GIVEN = {
    "אברהם": ["Abraham", "Abram", "Avrom", "Adolf"],
    "יצחק": ["Isaac", "Isak", "Itzig", "Ignaz", "Ignác", "Izsák"],
    "יעקב": ["Jakob", "Jacob", "Jacques", "Jankel", "Kuba", "Koppel", "Jakab"],
    "יוסף": ["Josef", "Joseph", "József", "Józef", "Josl"],
    "משה": ["Moses", "Moritz", "Mór", "Max", "Mojżesz", "Moische"],
    "מרדכי": ["Max", "Markus", "Márkus", "Mordche", "Motl", "Mordko"],
    "שלמה": ["Salomon", "Salamon", "Zalman", "Solomon", "Szlama"],
    "צבי": ["Hirsch", "Hersch", "Hermann", "Heinrich", "Henrik", "Cwi"],
    "אהרן": ["Aron", "Aaron", "Aharon"],
    "בנימין": ["Benjamin", "Benő", "Beni", "Wolf"],
    "זאב": ["Wolf", "Velvel", "Vilmos", "Ze'ev"],
    "דב": ["Ber", "Bär", "Berl", "Bernhard", "Bernát", "Berthold"],
    "אריה": ["Leib", "Löw", "Leo", "Leopold", "Lipót", "Arie"],
    "חיים": ["Chaim", "Hayim", "Hyman", "Viktor", "Vitale"],
    "מנחם": ["Mendel", "Mendl", "Manó", "Menachem"],
    "מאיר": ["Meyer", "Mayer", "Majer", "Meir"],
    "אליעזר": ["Lazar", "Lazarus", "Lázár", "Leizer", "Eleazar"],
    "שמואל": ["Samuel", "Sámuel", "Sigmund", "Zsigmond", "Schmil", "Szmul", "Samu"],
    "שמעון": ["Simon", "Simeon", "Szymon", "Schimon"],
    "נתן": ["Nathan", "Náthán", "Natan", "Nuta"],
    "אליהו": ["Elias", "Elijah", "Illés", "Eli"],
    "יהודה": ["Juda", "Judah", "Jehuda", "Leib", "Löb", "Lajos", "Ludwig"],
    "ישראל": ["Israel", "Izrael", "Srul", "Isidor", "Izidor"],
    "פנחס": ["Pinkus", "Pinkas", "Pinchas"],
    "שרגא": ["Feivel", "Fischel", "Shraga", "Philipp", "Fülöp"],
    "שרה": ["Sara", "Sára", "Sári", "Sarolta", "Charlotte"],
    "רבקה": ["Rebekka", "Rebecca", "Riwka", "Riki", "Regina"],
    "רחל": ["Rahel", "Rachel", "Rachela"],
    "לאה": ["Lea", "Léa", "Lenke"],
    "חנה": ["Hanna", "Hannah", "Chana", "Johanna", "Anna"],
    "חיה": ["Chaja", "Klara", "Viktoria", "Lili"],
    "חוה": ["Eva", "Éva", "Chawa"],
    "מלכה": ["Malka", "Amalie", "Malvine", "Mali"],
    "גיטל": ["Gitel", "Gisela", "Gizella", "Gitta", "Gizi"],
    "פייגא": ["Fanny", "Fáni", "Fajga", "Fejga"],
    "דבורה": ["Debora", "Dóra", "Dwojra", "Dobe"],
    "מרים": ["Mirjam", "Maria", "Mariska", "Marie"],
    "אסתר": ["Esther", "Eszter", "Estera", "Etel", "Ethel"],
    "ציפורה": ["Zipora", "Cipora", "Cili", "Cecília"],
}


def _norm(s):
    return _strip_diacritics(s).lower()


def given_lookup(name):
    name = re.sub("[֑-ׇ]", "", name.strip())
    res = []
    if _is_hebrew(name):
        # also try the first word of a compound name (e.g. 'יצחק צבי')
        for part in name.split():
            if part in GIVEN:
                res.append((part, GIVEN[part]))
    else:
        n = _norm(name)
        for heb, secs in GIVEN.items():
            if any(_norm(s) == n for s in secs):
                res.append((heb, [s for s in secs if _norm(s) != n]))
    return res


def order_variants(name):
    """Hungarian (family-first) vs Western order, plus comma form."""
    parts = name.replace(",", " ").split()
    if len(parts) < 2:
        return [name]
    first, last = parts[0], " ".join(parts[1:])
    return [f"{first} {last}", f"{last} {first}", f"{first}, {last}", f"{last}, {first}"]


def main(argv):
    if len(argv) < 3 or argv[1] not in ("surname", "given", "order"):
        print(__doc__)
        return 1
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    limit = 60
    if "--max" in argv:
        limit = int(argv[argv.index("--max") + 1])
    mode, name = argv[1], argv[2]
    if mode == "surname":
        vs = hebrew_variants(name, limit) if _is_hebrew(name) else latin_variants(name, limit)
        print(f"# variants for {name} ({len(vs)}) - candidates only; verify each hit against parents/place/dates")
        print("\n".join(vs))
    elif mode == "given":
        res = given_lookup(name)
        if not res:
            print(f"no entry for {name} (table is partial; add pairs you confirm in a document)")
        for k, v in res:
            print(f"{k}: " + ", ".join(v))
    else:
        print("\n".join(order_variants(name)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
