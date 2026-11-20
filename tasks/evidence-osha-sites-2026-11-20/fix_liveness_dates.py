#!/usr/bin/env python3
"""One-off correction (2026-11-20): this lane's liveness rows carry the filing's period end as observed_date.

SCHEMA §4.13: for a filing, observed_date is "the filing's own as-of / period date where the row's force depends on
it, with the retrieval date in notes"; owner ruling 8 makes a liveness row's witnessed date the covered period's end.
The rows were first written with the retrieval date (2026-11-20, which their notes keep). A 2025 Form 300A covers
calendar 2025, so the date becomes 2025-12-31. Existence and address rows keep the retrieval date, as earlier OSHA ITA
lanes did. Edits only the observed_date field of the listed IDs' lines, and asserts the count.

    python3 tasks/evidence-osha-sites-2026-11-20/fix_liveness_dates.py      (from the repo root)
"""
import csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD, NEW = "2026-11-20", "2025-12-31"
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))
targets = {}
for name in ("applied.csv", "applied_part3.csv"):
    targets.update({x["evidence_id"]: x["_shard"] for x in rd(HERE / name) if x["claim_type"] == "liveness"})
done = 0
for shard in sorted(set(targets.values())):
    path = ROOT / "data" / f"evidence_sites_{shard}.csv"
    lines = path.read_text(encoding="utf-8").split("\n")
    for i, line in enumerate(lines):
        eid = line.split(",", 1)[0]
        if targets.get(eid) == shard:
            row = next(csv.reader([line]))
            assert row[3] == "liveness" and row[7] in (OLD, NEW), (eid, row[3], row[7])
            if row[7] == OLD:
                cut = line.index(f",{OLD},{row[8]},")  # observed_date is followed by tier_effect
                lines[i] = line[:cut] + f",{NEW}," + line[cut + len(OLD) + 2:]
                assert next(csv.reader([lines[i]]))[7] == NEW and next(csv.reader([lines[i]]))[:7] == row[:7]
            done += 1
    path.write_text("\n".join(lines), encoding="utf-8", newline="")
assert done == len(targets), f"found {done} of {len(targets)} liveness rows"
for name in ("applied.csv", "applied_part3.csv", "packet_rows.csv"):
    rows = rd(HERE / name)
    for x in rows:
        if x["claim_type"] == "liveness":
            x["observed_date"] = NEW
    with open(HERE / name, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(f"liveness observed_date -> {NEW} on {done} rows")
