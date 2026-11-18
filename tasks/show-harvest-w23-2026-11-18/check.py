#!/usr/bin/env python3
"""Check this pass without the staging harvest: the appended rows are in the table unchanged, every row's listed name
is its organization's LEGAL name (never a trade-name-only hit), and no row cites a list the README excludes.
    python3 tasks/show-harvest-w23-2026-11-18/check.py
"""
import csv, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import atlas as A  # noqa: E402

BY = "claude-code show-harvest-w23-2026-11-18"
read = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))  # noqa: E731
packet = read(HERE / "participation_append.csv")
table = [r for r in read(ROOT / "data" / "event_participation.csv") if r["created_by"] == BY]
assert table == packet, f"table has {len(table)} rows of this pass, packet {len(packet)}; they must be identical"

legal = {o["org_id"]: o["legal_name"] for f in (ROOT / "data").glob("organizations_*.csv") for o in read(f)}
bad = []
for r in packet:
    listed = re.search(r'listed as "(.*)"\)$', r["sources"]).group(1)
    if A.name_key(listed) != A.name_key(legal[r["org_id"]]):
        bad.append((r["participation_id"], listed, legal[r["org_id"]]))
    if re.search(r"supporters|media[-_ ]?partners?|cooperating[-_ ]?media|corporate-education-sponsors",
                 r["evidence_source_url"], re.I):
        bad.append((r["participation_id"], "excluded list", r["evidence_source_url"]))
    if r["role"] not in ("exhibitor", "sponsor", "speaker"):
        bad.append((r["participation_id"], "role", r["role"]))
assert not bad, bad
print(f"OK: {len(packet)} rows, all legal-name matches, none from an excluded list")
