#!/usr/bin/env python3
"""ממיין את תיקיית ההורדות. ברירת מחדל: dry-run (לא מזיז כלום).
  python sort_downloads.py            # תצוגה מקדימה בלבד
  python sort_downloads.py --apply    # ביצוע (מעביר בלבד, אף פעם לא מוחק)
  python sort_downloads.py --undo     # מחזיר הכול למקום המקורי לפי היומן
"""
import argparse, hashlib, os, re, shutil, sys
from collections import defaultdict
from datetime import datetime

OUT = "המלצה_למחיקה"
SORTED = "מסודר"
LOG = "_log.tsv"

DEL = {
    "wa": ("1_תמונות_ווצאפ_4_באוקטובר", "תמונות שחולצו מקובץ zip של שיחת ווצאפ מתאריך היעד"),
    "dup": ("2_קבצים_כפולים", "עותקים זהים בתוכן לקובץ אחר. העותק השני נשאר במקומו. פירוט ב-_log.tsv"),
    "empty": ("3_קבצים_ריקים", "קבצים בגודל 0 בייט"),
    "tmp": ("4_הורדות_שלא_הושלמו_וזמניים", "קבצי הורדה חלקיים או זמניים (crdownload, tmp, part...)"),
    "apk": ("5_קבצי_התקנה_APK", "קבצי התקנה של אפליקציות. אם האפליקציה כבר מותקנת, אפשר למחוק"),
    "wazip": ("6_ארכיון_ווצאפ_שכבר_חולץ", "קובץ zip של ווצאפ שכבר חולץ ממנו התוכן"),
}
TYPES = {
    "תמונות": "jpg jpeg png gif webp heic bmp",
    "סרטונים": "mp4 mkv mov avi 3gp webm",
    "אודיו": "mp3 m4a wav ogg opus aac flac amr",
    "מסמכים": "pdf doc docx xls xlsx ppt pptx txt odt ods csv rtf epub",
    "ארכיונים": "zip rar 7z tar gz",
}
EXT2TYPE = {e: t for t, es in TYPES.items() for e in es.split()}
IMG = set(TYPES["תמונות"].split())
TMP = {"crdownload", "tmp", "part", "download", "temp", "partial", "cache"}
COPY_RE = re.compile(r"\(\d+\)|copy|העתק", re.I)


def ext(p):
    return os.path.splitext(p)[1].lower().lstrip(".")


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def unique(dst):
    if not os.path.exists(dst):
        return dst
    b, e = os.path.splitext(dst)
    i = 1
    while os.path.exists(f"{b}_{i}{e}"):
        i += 1
    return f"{b}_{i}{e}"


def scan(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != OUT and not d.startswith(".")]
        for n in fn:
            if n.startswith("."):
                continue
            p = os.path.join(dp, n)
            if os.path.islink(p):
                continue
            try:
                yield p, os.stat(p)
            except OSError:
                pass


def plan(root, month, day, year):
    name_re = re.compile(r"(?<!\d)(\d{4})[-_.]?%02d[-_.]?%02d(?!\d)" % (month, day))
    files = list(scan(root))
    claimed, rest = {}, []
    for p, st in files:
        n, e = os.path.basename(p), ext(p)
        m = name_re.search(n)
        by_name = bool(m) and int(m.group(1)) == year
        d = datetime.fromtimestamp(st.st_mtime)
        by_time = (d.year, d.month, d.day) == (year, month, day)
        if e in IMG and (by_name or by_time):
            claimed[p] = ("wa", "")
        elif st.st_size == 0:
            claimed[p] = ("empty", "")
        elif e in TMP:
            claimed[p] = ("tmp", "")
        elif e == "apk":
            claimed[p] = ("apk", "")
        elif e == "zip" and "whatsapp" in n.lower():
            claimed[p] = ("wazip", "")
        else:
            rest.append((p, st))
    by_size = defaultdict(list)
    for p, st in rest:
        by_size[st.st_size].append((p, st))
    for group in by_size.values():
        if len(group) < 2:
            continue
        by_hash = defaultdict(list)
        for p, st in group:
            try:
                by_hash[sha1(p)].append((p, st))
            except OSError:
                pass
        for same in by_hash.values():
            if len(same) < 2:
                continue
            same.sort(key=lambda x: (bool(COPY_RE.search(os.path.basename(x[0]))),
                                     x[0].count(os.sep), x[1].st_mtime, len(x[0])))
            for p, _ in same[1:]:
                claimed[p] = ("dup", same[0][0])
    sizes = {p: st.st_size for p, st in files}
    moves = [(p, k, x) for p, (k, x) in claimed.items()]
    for p, st in rest:  # מיון לפי סוג: רק קבצים שנמצאים ישירות בשורש
        if p not in claimed and os.path.dirname(p) == root:
            moves.append((p, "sort:" + EXT2TYPE.get(ext(p), "אחר"), ""))
    return moves, sizes


def dest_dir(root, kind):
    if kind.startswith("sort:"):
        return os.path.join(root, SORTED, kind[5:])
    return os.path.join(root, OUT, DEL[kind][0])


def summarize(moves, sizes, root, report):
    by = defaultdict(list)
    for p, k, x in moves:
        by[k].append(p)
    lines = []
    for k in list(DEL) + sorted(k for k in by if k.startswith("sort:")):
        ps = by.get(k, [])
        if not ps:
            continue
        mb = sum(sizes.get(p, 0) for p in ps) / 1048576
        title = DEL[k][0] if k in DEL else "מסודר/" + k[5:]
        lines.append(f"\n== {title}: {len(ps)} קבצים, {mb:.1f}MB")
        for p in ps[:5]:
            lines.append("   " + os.path.relpath(p, root))
        if len(ps) > 5:
            lines.append(f"   ... ועוד {len(ps) - 5}")
    with open(report, "w", encoding="utf-8") as f:
        for p, k, x in moves:
            f.write(f"{k}\t{os.path.relpath(p, root)}\t{x}\n")
    print("\n".join(lines))
    print(f"\nדוח מלא: {report}")


def apply(moves, root):
    out = os.path.join(root, OUT)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, LOG), "a", encoding="utf-8") as log:
        for p, k, x in moves:
            d = dest_dir(root, k)
            os.makedirs(d, exist_ok=True)
            dst = unique(os.path.join(d, os.path.basename(p)))
            shutil.move(p, dst)
            log.write(f"{datetime.now().isoformat()}\t{k}\t{p}\t{dst}\t{x}\n")
    for k, (folder, why) in DEL.items():
        d = os.path.join(out, folder)
        if os.path.isdir(d):
            with open(os.path.join(d, "_למה.txt"), "w", encoding="utf-8") as f:
                f.write(why + "\n")


def undo(root):
    log = os.path.join(root, OUT, LOG)
    if not os.path.exists(log):
        sys.exit("אין יומן. אין מה להחזיר.")
    rows = [l.rstrip("\n").split("\t") for l in open(log, encoding="utf-8")]
    n = 0
    for r in reversed(rows):
        src, dst = r[2], r[3]
        if os.path.exists(dst) and not os.path.exists(src):
            os.makedirs(os.path.dirname(src), exist_ok=True)
            shutil.move(dst, src)
            n += 1
    os.replace(log, log + ".undone")
    print(f"הוחזרו {n} קבצים.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/storage/downloads"))
    ap.add_argument("--date", default="10-04", help="MM-DD של תמונות הווצאפ")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--undo", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        sys.exit(f"התיקייה לא נמצאה: {root}\nהרצת termux-setup-storage?")
    if a.undo:
        return undo(root)
    month, day = map(int, a.date.split("-"))
    print("סורק...")
    moves, sizes = plan(root, month, day, a.year)
    summarize(moves, sizes, root, os.path.expanduser("~/דוח_מיון.txt"))
    if not a.apply:
        print("\nזו הייתה תצוגה מקדימה, לא הוזז כלום. להרצה אמיתית: --apply")
        return
    if input(f"\nלהעביר {len(moves)} קבצים? (כן/לא): ").strip() != "כן":
        return print("בוטל.")
    apply(moves, root)
    print("בוצע. להחזרה: python sort_downloads.py --undo")


if __name__ == "__main__":
    main()
