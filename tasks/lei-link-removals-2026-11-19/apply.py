#!/usr/bin/env python3
"""Remove three LEI links that point at a different company of the same name (README.md). Every other registry row is kept,
including Delco's UEI, which USAspending places at the Akron shop. Byte-preserving: same header, line endings and order.
    python3 tasks/lei-link-removals-2026-11-19/apply.py"""
import csv, io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "data" / "registry_links.csv"
DROP = {("ORG-000174", "LEI", "549300QMYW171MP1PL50"),  # Vertex, Inc. (Mogadore seals) -> Vertex, Inc. (PA tax software)
        ("ORG-000780", "LEI", "549300PFONU4YY4GYS55"),  # Custom Molded Products (Wilmington OH molder) -> CMP (Newnan GA pool/spa)
        ("ORG-001383", "LEI", "5493008QN54WVMZHGF61")}  # Delco, LLC (Akron machining) -> Delco LLC (Willingboro NJ real estate)
raw = P.read_bytes()
eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
r = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
rows = list(r)
keep = [x for x in rows if (x["org_id"], x["registry"], x["registry_id"]) not in DROP]
assert len(rows) - len(keep) == len(DROP), f"expected to drop {len(DROP)}, would drop {len(rows) - len(keep)}"
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=r.fieldnames, lineterminator=eol); w.writeheader(); w.writerows(keep)
P.write_bytes(buf.getvalue().encode("utf-8"))
print(f"registry_links: {len(rows)} -> {len(keep)}")
