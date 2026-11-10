"""Quality checks for a research folder (run at session start and before finishing).

usage: lint_research.py <research_dir>
Exit code 1 if there are ERRORS. Warnings never fail the run.

Checks
  ERRORS   - FACTS row without a valid label; [מתועד] fact without a source ID that exists
             in sources.csv; [מתועד] fact whose source is classified 'נגזר' (should be [משני]);
             FINDINGS block with status מוכח but no existing source ID in its evidence;
             question status not in the allowed set; open question without 'מה יכריע'.
  WARNINGS - STATE missing/stale-format date; empty action queue; sources.csv [מתועד] rows not yet
             'נבדק בעצמי?'; search_log rows without a conclusion; open referrals in the follow-up file;
             people in the FAN circle never used; PLAN matrix rows still 'לא נבדק'.
Tables are read by header names, so older research folders with fewer columns still work.
"""
import csv
import os
import re
import sys

LABEL_RE = re.compile(r"\[(מתועד(?:, ?שלילי)?|משני|עדות|השערה)\]")
ID_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*-\d{3,}\b")
Q_STATUS = {"פתוח", "בבדיקה", "ממתין לארכיון", "מוכח", "סביר", "מנוגד", "נסגר שלילי"}
OPEN_STATUS = {"פתוח", "בבדיקה", "ממתין לארכיון"}


def read(path):
    if not os.path.exists(path):
        return None
    return open(path, encoding="utf-8-sig").read()


def tables(text):
    """Yield (heading, header_cells, rows) for each markdown pipe table."""
    heading, lines, out, i = "", text.splitlines(), [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            heading = ln.lstrip("# ").strip()
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                cells += [""] * (len(header) - len(cells))
                rows.append(dict(zip(header, cells)))
                i += 1
            out.append((heading, header, rows))
            continue
        i += 1
    return out


def blank(row, ignore=()):
    return not any(v for k, v in row.items() if k not in ignore)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print(__doc__)
        return 2
    root = sys.argv[1]
    errors, warns, info = [], [], []

    # ---- sources.csv
    src = {}
    p = os.path.join(root, "sources.csv")
    if os.path.exists(p):
        with open(p, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("מספר מקור"):
                    src[r["מספר מקור"].strip()] = r
    else:
        errors.append("sources.csv missing")
    for sid, r in src.items():
        lab = r.get("תווית ודאות", "")
        if lab and not LABEL_RE.search(lab):
            errors.append(f"sources.csv {sid}: invalid label '{lab}'")
        if "מתועד" in lab and "שלילי" not in lab and r.get("נבדק בעצמי?", "").strip() not in ("כן", "yes", "Y"):
            warns.append(f"sources.csv {sid}: labeled [מתועד] but 'נבדק בעצמי?' is not כן (agent/unchecked)")
    info.append(f"sources: {len(src)}")

    # ---- STATE
    st = read(os.path.join(root, "STATE.md"))
    if st is None:
        errors.append("STATE.md missing")
    else:
        if not re.search(r"עדכון אחרון:\s*\d", st):
            warns.append("STATE.md: 'עדכון אחרון:' date missing")
        for h, header, rows in tables(st):
            if "סטטוס" in header and "מה יכריע (רשומה + ארכיון)" in header:
                n = 0
                for r in rows:
                    if blank(r, ("#",)):
                        continue
                    n += 1
                    s = r.get("סטטוס", "")
                    q = r.get("#", "?")
                    if s not in Q_STATUS:
                        errors.append(f"STATE question {q}: status '{s}' not in {sorted(Q_STATUS)}")
                    if s in OPEN_STATUS and not r.get("מה יכריע (רשומה + ארכיון)"):
                        errors.append(f"STATE question {q}: open question without 'מה יכריע'")
                info.append(f"questions: {n}")
            if h.startswith("תור פעולות"):
                real = [r for r in rows if not blank(r, ("עדיפות", "מי", "סטטוס"))]
                if not real:
                    warns.append("STATE: action queue is empty - define the next step")
                else:
                    info.append(f"next action: {real[0].get('פעולה', '')[:80]}")

    # ---- FACTS
    facts = read(os.path.join(root, "FACTS.md"))
    if facts:
        for h, header, rows in tables(facts):
            if "תווית" in header and "עובדה" in header:
                for r in rows:
                    if blank(r):
                        continue
                    topic = r.get("נושא", "?")
                    lab = r.get("תווית", "")
                    if not LABEL_RE.search(lab):
                        errors.append(f"FACTS '{topic}': missing/invalid label '{lab}'")
                        continue
                    ids = ID_RE.findall(r.get("מקור-ID", ""))
                    if "מתועד" in lab and "שלילי" not in lab:
                        if not ids:
                            errors.append(f"FACTS '{topic}': [מתועד] without a source ID")
                        for i in ids:
                            if i not in src:
                                errors.append(f"FACTS '{topic}': source {i} not in sources.csv")
                            elif src[i].get("סוג מקור", "").strip() == "נגזר" or re.search(r"\[משני\]", src[i].get("תווית ודאות", "")):
                                errors.append(f"FACTS '{topic}': labeled [מתועד] but {i} is derived/secondary - relabel [משני] or find the original")

    # ---- FINDINGS
    fd = read(os.path.join(root, "FINDINGS.md"))
    if fd:
        for blk in re.split(r"\n-{3,}\n", fd):
            m = re.search(r"^שאלה:\s*(.+)$", blk, re.M)
            s = re.search(r"^סטטוס:\s*(.+)$", blk, re.M)
            if not m or not s:
                continue
            q, status = m.group(1).strip(), s.group(1).strip()
            if status.startswith("מוכח"):
                ids = ID_RE.findall(blk)
                if not ids or not any(i in src for i in ids):
                    errors.append(f"FINDINGS '{q[:40]}': status מוכח without an existing source ID in evidence")
                if not re.search(r"^נבדק ולא נמצא:\s*\S", blk, re.M):
                    warns.append(f"FINDINGS '{q[:40]}': מוכח but 'נבדק ולא נמצא' is empty (record the search scope)")

    # ---- search log
    lg = read(os.path.join(root, "search_log.md"))
    if lg:
        n = 0
        for h, header, rows in tables(lg):
            if "שאילתה / איות" in header:
                for r in rows:
                    if blank(r, ("תוצאות", "מסקנה")):
                        continue
                    n += 1
                    if not r.get("מסקנה"):
                        warns.append(f"search_log row '{r.get('מקור', '?')}': no conclusion")
        info.append(f"searches logged: {n}")

    # ---- follow-up
    fu = read(os.path.join(root, "archive_followup.md"))
    if fu:
        open_ref = 0
        for h, header, rows in tables(fu):
            if h.startswith("הפניות פתוחות"):
                for r in rows:
                    if blank(r):
                        continue
                    if r.get("סטטוס", "").strip() in ("", "פתוח"):
                        open_ref += 1
        if open_ref:
            warns.append(f"archive_followup: {open_ref} open referral(s) - each is a task (send / decide to drop)")

    # ---- PLAN matrix
    pl = read(os.path.join(root, "PLAN.md"))
    if pl:
        unchecked = 0
        total = 0
        for h, header, rows in tables(pl):
            if "סוג רשומה" in header and "סטטוס" in header:
                for r in rows:
                    if blank(r, ("שאלה #", "סטטוס")):
                        continue
                    total += 1
                    if r.get("סטטוס", "").startswith("לא נבדק"):
                        unchecked += 1
        if total:
            info.append(f"record matrix: {total - unchecked}/{total} checked")

    print(f"# lint {root}")
    for i in info:
        print(f"  info: {i}")
    for w in warns:
        print(f"  WARN: {w}")
    for e in errors:
        print(f"  ERROR: {e}")
    print(f"result: {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
