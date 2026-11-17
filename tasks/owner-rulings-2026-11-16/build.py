"""Apply owner ruling R-AFFOA (2026-11-16): clear the inferred polymer_program flag on ORG-013503. Idempotent."""
import csv, io, sys
from pathlib import Path

P = Path(__file__).resolve().parents[2] / "data" / "ecosystem.csv"
r = csv.DictReader(io.StringIO(P.read_text(encoding="utf-8"), newline=""))
header, rows = r.fieldnames, list(r)
hit = [x for x in rows if x["org_id"] == "ORG-013503"]
assert len(hit) == 1
changed = hit[0]["polymer_program"] == "true"
if changed:
    hit[0]["polymer_program"] = ""
print("cells to change:", int(changed))
if "--apply" in sys.argv and changed:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    P.write_bytes(buf.getvalue().encode("utf-8"))
