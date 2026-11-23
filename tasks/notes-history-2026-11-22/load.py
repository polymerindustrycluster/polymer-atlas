"""Shared loader: all organization and site shard rows with their file and line."""
import csv, glob, os
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")
def load(table):
    rows = []
    for p in sorted(glob.glob(os.path.join(DATA, f"{table}_*.csv"))):
        if p.endswith("_all.csv"):
            continue
        with open(p, newline="", encoding="utf-8") as f:
            for i, r in enumerate(csv.DictReader(f), 2):
                r["_file"] = os.path.basename(p); r["_line"] = i
                rows.append(r)
    return rows
