#!/usr/bin/env python3
"""Turn the R13 band set (band_updates.csv, status APPLY + action fill) into a
hash-checked cell-edit packet for scripts/apply_p1_crm_scrub.py --packet-dir.

    python3 tasks/bands-apply-2026-11-02/build_edits.py --data-dir <pre-pass data dir>

Per row: the band column (sites.employee_band_site / organizations.employee_band_ohio)
and a BAND-SOURCE notes append that names the source filing and its date (the
provenance route used for bands, since SCHEMA §4.13 has no size claim_type).
Each cell is checked against the change set's `existing_band`; any drift is held.
REVIEW / SKIP / noop rows are never edited.
"""
import argparse, csv, hashlib
from pathlib import Path

csv.field_size_limit(10 ** 9)
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BANDS = ROOT / "tasks" / "integration-ready-oh-pa-2026-11-02" / "band_updates.csv"
BAND_VOCAB = {"1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+"}


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    data = Path(a.data_dir)
    where = {}
    for p in sorted(data.glob("sites_*.csv")) + sorted(data.glob("organizations_*.csv")):
        key = "site_id" if p.name.startswith("sites_") else "org_id"
        for r in read(p):
            where[r[key]] = (p.name, r)
    sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
    edits, holds = [], []
    for b in read(BANDS):
        if b["status"] != "APPLY" or b["action"] != "fill":
            continue
        rid = b["record_id"]
        col = "employee_band_site" if b["record_table"] == "sites" else "employee_band_ohio"
        if rid not in where:
            holds.append({"record_id": rid, "reason": "record not held"}); continue
        fname, r = where[rid]
        if r.get(col, "") != b["existing_band"]:
            holds.append({"record_id": rid, "reason": f"drift: {col} is {r.get(col)!r}, set expected {b['existing_band']!r}"}); continue
        if b["pick_band"] not in BAND_VOCAB:
            holds.append({"record_id": rid, "reason": f"pick {b['pick_band']!r} outside vocabulary"}); continue
        why = f"R13 pick {b['pick_band']} from {b['pick_source']} ({b['employee_count_source_date']}); refs {b['packet_refs']}"
        edits.append({"file": fname, "row_id": rid, "column": col, "old_sha256": sha(r[col]), "new_value": b["pick_band"],
                      "edit_class": f"BAND_{'SITE' if col == 'employee_band_site' else 'ORG_OHIO'}_{b['pick_source'].upper()}", "rationale": why})
        notes = r["notes"]
        edits.append({"file": fname, "row_id": rid, "column": "notes", "old_sha256": sha(notes),
                      "new_value": (notes.rstrip() + " " if notes.strip() else "") + b["notes_append"],
                      "edit_class": "BAND_SOURCE_NOTE", "rationale": "band provenance (source + date)"})
    cols = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]
    with open(OUT / "edits.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(edits)
    with open(OUT / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["record_id", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
    from collections import Counter
    print("edits", len(edits), dict(Counter(e["edit_class"] for e in edits)), "holds", len(holds))


if __name__ == "__main__":
    main()
