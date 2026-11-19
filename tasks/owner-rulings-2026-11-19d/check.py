#!/usr/bin/env python3
"""Check this pass's rows without the staging harvest:
- the appended rows are in the table unchanged; none repeats an (event, org, year, role) in the table;
- every row is an EVT-000077 2026 attendee row from the one admitted list, cites it in `sources`, carries the ruling's
  note and the list's staging key, is tier A, and has an empty role_detail and empty edition fields;
- the listed name's key is held by exactly the row's organization and is its LEGAL name; the name is not on a
  controller drop list, not held by the wave 2-3 review, by #411's CONTROLLER_HOLDS, or by this pass's HOLDS.
Limit: without the staging harvest this cannot prove a name is on the page; build.py, which reads the banked page and
asserts its "final list" heading, is the provenance guarantee.
    python3 tasks/owner-rulings-2026-11-19d/check.py
"""
import csv, hashlib, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build as P  # noqa: E402  (this pass)

B, A = P.B, P.A
read = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))  # noqa: E731
packet = read(HERE / "participation_append.csv")
whole = read(ROOT / "data" / "event_participation.csv")
table = [r for r in whole if r["created_by"] == P.BY]
assert table == packet, f"table has {len(table)} rows of this pass, packet {len(packet)}; they must be identical"
counts = Counter((r["event_id"], r["org_id"], r["edition_year"], r["role"]) for r in whole)
events = {e["event_id"]: e for e in read(ROOT / "data" / "events.csv")}
by_key, orgs = B.org_index(ROOT / "data")
held = {(e, nk) for e, _role, nk in B.decisions.held_names(B.decisions.load(B.W23 / "review_decisions.csv", events, orgs))}
drops = {(d["show_key"], d["role"], d["name_sha256_16"]) for p in (B.W1, B.W23) for d in read(p / "controller_drops.csv")}
bad = []
for r in packet:
    pid = r["participation_id"]
    if (r["event_id"], r["edition_year"], r["role"], r["evidence_source_url"]) != (P.EVENT, P.YEAR, "attendee", P.URL):
        bad.append((pid, "not an EVT-000077 2026 attendee row from the admitted list"))
    if counts[(r["event_id"], r["org_id"], r["edition_year"], r["role"])] != 1:
        bad.append((pid, "duplicate (event, org, year, role) in the table"))
    if P.NOTE not in r["notes"] or f"(harvest-2026-11, {P.SHOW_KEY})" not in r["notes"]:
        bad.append((pid, "notes lack the ruling's note or the list's staging key"))
    if r["role_detail"]:
        bad.append((pid, "attendee row with a role_detail"))
    if r["edition_dates"] or r["edition_city"] or r["edition_state"]:
        bad.append((pid, "edition fields set, but the conferences repo had no 2026 edition at build time"))
    if r["verification_tier"] != "A":
        bad.append((pid, "verification_tier is not A (the organizer's own list)"))
    cited = re.fullmatch(r'(\S+) \(read [0-9-]+; listed as "(.*)"\)', r["sources"])
    if not cited or cited.group(1) != P.URL:
        bad.append((pid, "sources does not cite the list")); continue
    listed, o = cited.group(2), orgs.get(r["org_id"])
    if o is None:
        bad.append((pid, "org not active/unknown")); continue
    nk = A.name_key(listed)
    if set(by_key.get(nk, {})) != {r["org_id"]}:
        bad.append((pid, f"listed name's key is held by {sorted(by_key.get(nk, {}))}"))
    if nk != A.name_key(o["legal_name"]):
        bad.append((pid, "listed name is not the org's legal name"))
    if (P.SHOW_KEY, "attendee", hashlib.sha256(listed.encode("utf-8")).hexdigest()[:16]) in drops:
        bad.append((pid, "controller drop"))
    if (P.EVENT, nk) in held:
        bad.append((pid, "name held by the wave 2-3 review"))
    if (P.EVENT, nk) in B.CONTROLLER_HOLDS or (P.EVENT, nk) in P.HOLDS:
        bad.append((pid, "name held (CONTROLLER_HOLDS or HOLDS)"))
assert not bad, bad
print(f"OK: {len(packet)} rows, each a legal-name match from the Coatings Trends 2026 final registration list, "
      f"none held or dropped")
