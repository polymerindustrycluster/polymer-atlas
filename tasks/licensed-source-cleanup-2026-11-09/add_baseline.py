#!/usr/bin/env python3
"""Add the V-60 grandfather list to scripts/validate_debt_baseline.json: the evidence rows that cited a licensed
publication when V-60 was adopted (licensed_rows.csv). Idempotent.
    python3 tasks/licensed-source-cleanup-2026-11-09/add_baseline.py
"""
import csv, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
P = HERE.parents[1] / "scripts" / "validate_debt_baseline.json"
ids = sorted({r["evidence_id"] for r in csv.DictReader(open(HERE / "licensed_rows.csv", encoding="utf-8"))})
b = json.loads(P.read_text(encoding="utf-8"))
b["rules"]["V-60"] = ids
note = (" 2026-11-09: V-60 (evidence must not cite a licensed publication, AGENTS.md §5) adopted with its "
        f"{len(ids)} existing violators grandfathered; each is answered by a public-source row in "
        "tasks/licensed-source-cleanup-2026-11-09/.")
if "V-60" not in b["amended"]:
    b["amended"] += note
P.write_text(json.dumps(b, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("V-60 baseline:", len(ids), "ids")
