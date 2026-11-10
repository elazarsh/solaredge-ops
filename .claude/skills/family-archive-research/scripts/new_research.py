"""Scaffold a research folder for a new person from templates/.

usage: new_research.py <slug> --name "Display name" [--dir research] [--force]
  creates <dir>/<slug>/ with STATE, PLAN, PEOPLE, TIMELINE, FACTS, FINDINGS,
  search_log, archive_followup, sources.csv and the folders agents/, answers/, FOUND/.
Refuses to overwrite an existing folder unless --force (existing files are kept).
"""
import argparse
import datetime
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(os.path.dirname(HERE), "templates")


def today_str():
    d = datetime.date.today()
    try:
        sys.path.insert(0, HERE)
        import hebdate
        return hebdate.fmt(d.year, d.month, d.day)
    except Exception:
        return d.strftime("%d.%m.%Y")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--name", required=True)
    ap.add_argument("--dir", default="research")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"[\w\-]+", a.slug):
        sys.exit("slug must be letters/digits/-/_ only (no spaces or slashes)")
    root = os.path.join(a.dir, a.slug)
    if os.path.exists(root) and not a.force:
        sys.exit(f"{root} already exists - open its STATE.md instead (or pass --force to add missing files)")
    os.makedirs(root, exist_ok=True)
    for sub in ("agents", "answers", "FOUND", "raw"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    today = today_str()
    made = []
    for f in sorted(os.listdir(TEMPLATES)):
        dst = os.path.join(root, f)
        if os.path.exists(dst):
            continue
        if f.endswith(".csv"):
            shutil.copyfile(os.path.join(TEMPLATES, f), dst)
        else:
            t = open(os.path.join(TEMPLATES, f), encoding="utf-8").read()
            open(dst, "w", encoding="utf-8").write(t.replace("{{NAME}}", a.name).replace("{{TODAY}}", today))
        made.append(f)
    print(f"created {root}/: " + ", ".join(made))
    print("next: python scripts/ingest.py <raw material> " + root + "  (then fill PLACES.md, run plan_sources.py)")


if __name__ == "__main__":
    main()
