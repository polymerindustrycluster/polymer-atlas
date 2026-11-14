"""Revert the #256 Tarkett repoints per owner ruling H-TARKETT (a), 2026-11-12. Idempotent: python3 build.py [--apply]."""
import csv, io, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITES = ROOT / "data" / "sites_OH.csv"
FROM, TO = "ORG-000131", "ORG-001836"
NOTE = ("2026-11-14: org_id reverted ORG-000131 -> ORG-001836 per owner ruling H-TARKETT (a), 2026-11-12 "
        "(tasks/owner-rulings-2026-11-12, PR #313): hold until a dated primary legal-name bridge equates filed "
        "operator Tarkett USA Inc. with ORG-000131 Tarkett North America. The #256 repoint (2026-11-06) predated the "
        "ruling; its evidence rows stay as observations.")
TARGETS = ("SITE-003477", "SITE-003478")

text = SITES.read_text(encoding="utf-8")
reader = csv.DictReader(io.StringIO(text, newline=""))
header, rows = reader.fieldnames, list(reader)
changed = 0
for r in rows:
    if r["site_id"] in TARGETS:
        if r["org_id"] == TO and NOTE in r["notes"]:
            continue
        assert r["org_id"] == FROM, (r["site_id"], r["org_id"])
        r["org_id"] = TO
        r["notes"] = (r["notes"] + " | " + NOTE) if r["notes"] else NOTE
        changed += 1
assert sum(r["site_id"] in TARGETS for r in rows) == 2
print(f"rows to change: {changed}")
if "--apply" in sys.argv and changed:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    SITES.write_bytes(buf.getvalue().encode("utf-8"))
    print("applied")
