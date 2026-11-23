#!/usr/bin/env python3
"""Apply packet.csv to the evidence shards (run once, from the repo root): rows get EVD-482000 upward (lane reserve 482000..482999),
sorted by (record_table, record_id, claim_type), and are appended to data/evidence_<table>_OH.csv (every record in this frame is an Ohio
record, so its home shard is OH). Writes applied_ids.csv (evidence_id -> record, claim). Refuses to run twice or past the reserve."""
import csv
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COLS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref", "observed_date",
        "tier_effect", "created_by", "notes", "address_role"]
FIRST, LAST = 482000, 482999
rows = sorted(csv.DictReader(open(HERE / "packet.csv", newline="", encoding="utf-8")), key=lambda r: (r["record_table"], r["record_id"], r["claim_type"]))
assert 0 < len(rows) <= LAST - FIRST + 1
shard = {"sites": ROOT / "data/evidence_sites_OH.csv", "organizations": ROOT / "data/evidence_organizations_OH.csv"}
existing = {r["evidence_id"] for f in ROOT.glob("data/evidence_*.csv") for r in csv.DictReader(open(f, newline="", encoding="utf-8"))}
if any(FIRST <= int(i[4:]) <= LAST for i in existing):
    sys.exit("EVD-482000..482999 already used in data/: refusing to apply twice")
out, ids = {t: [] for t in shard}, []
for n, r in enumerate(rows):
    eid = f"EVD-{FIRST + n}"
    assert eid not in existing
    out[r["record_table"]].append({**{c: r[c] for c in COLS if c != "evidence_id"}, "evidence_id": eid})
    ids.append((eid, r["record_table"], r["record_id"], r["claim_type"]))
for t, rs in out.items():
    with open(shard[t], newline="", encoding="utf-8") as f:
        assert next(csv.reader(f)) == COLS, f"{shard[t]} header differs"
    raw = shard[t].read_bytes()
    with open(shard[t], "a", newline="", encoding="utf-8") as f:
        if not raw.endswith(b"\n"):
            f.write("\n")
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writerows(rs)
with open(HERE / "applied_ids.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["evidence_id", "record_table", "record_id", "claim_type"])
    w.writerows(ids)
print(len(ids), "rows appended:", {t: len(v) for t, v in out.items()}, ids[0][0], "..", ids[-1][0])
