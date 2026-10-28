#!/usr/bin/env python3
"""Build build/polymer-atlas.db from the canonical CSVs. Stdlib only.
The CSVs are the source of truth; this file is a generated artifact."""
import csv, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "polymer-atlas.db"
TABLES = {"organizations": "organizations.csv", "sites": "sites.csv",
          "ecosystem": "ecosystem.csv", "inclusion_log": "inclusion_log.csv"}

OUT.parent.mkdir(exist_ok=True)
if OUT.exists():
    OUT.unlink()
con = sqlite3.connect(OUT)
for table, fname in TABLES.items():
    with open(ROOT / "data" / fname, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames
        rows = [[(r[c] or None) for c in cols] for r in rdr]
    coldef = ", ".join(f'"{c}" TEXT' for c in cols)
    con.execute(f'CREATE TABLE "{table}" ({coldef})')
    con.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" * len(cols))})', rows)
    print(f"{table}: {len(rows)} rows")
con.execute("CREATE VIEW ohio_sites AS SELECT * FROM sites WHERE state='OH'")
con.commit(); con.close()
print(f"Built {OUT}")
