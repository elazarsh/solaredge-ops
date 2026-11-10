"""Merge agents/<ID>_sources.csv rows into the research folder's sources.csv.

usage: merge_sources.py <research_dir>
Skips source IDs that already exist. Rows from agents are marked
'נבדק בעצמי?' = לא (the main session sets it to כן after seeing the record itself).
"""
import csv
import glob
import os
import sys


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    root = sys.argv[1]
    main_path = os.path.join(root, "sources.csv")
    with open(main_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    ids = {r.get("מספר מקור", "") for r in rows}
    added = 0
    for p in sorted(glob.glob(os.path.join(root, "agents", "*_sources.csv"))):
        for r in read(p):
            rid = r.get("מספר מקור", "")
            if not rid or rid in ids:
                continue
            r["נבדק בעצמי?"] = "לא"
            rows.append({k: r.get(k, "") for k in fields})
            ids.add(rid)
            added += 1
    with open(main_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"merged {added} new source rows into {main_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
