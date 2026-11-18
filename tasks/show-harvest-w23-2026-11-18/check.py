#!/usr/bin/env python3
"""Check this pass without the staging harvest: the appended rows are in the table unchanged, every row's listed name
is its organization's LEGAL name, or a trade name accepted for that exact event, role, year, name and org in
review_decisions.csv (with the notes saying so), no row is one review_decisions.csv holds, and no row cites a list
the README excludes.
    python3 tasks/show-harvest-w23-2026-11-18/check.py
"""
import csv, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import atlas as A  # noqa: E402
import decisions  # noqa: E402

BY = "claude-code show-harvest-w23-2026-11-18"
read = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))  # noqa: E731
packet = read(HERE / "participation_append.csv")
table = [r for r in read(ROOT / "data" / "event_participation.csv") if r["created_by"] == BY]
assert table == packet, f"table has {len(table)} rows of this pass, packet {len(packet)}; they must be identical"

orgs = {o["org_id"]: o for f in (ROOT / "data").glob("organizations_*.csv") for o in read(f)
        if o["status"] in ("active", "unknown")}  # the set build.py matches against
events = {e["event_id"]: e for e in read(ROOT / "data" / "events.csv")}
review = decisions.load(HERE / "review_decisions.csv", events, orgs).values()  # refuses any malformed row
# keyed as build.py applies them: show (from the row's notes), event, role, year, normalized listed name and org
dkey = lambda d: (d["show_key"], d["event_id"], d["role"], d["edition_year"], A.name_key(d["listed_name"]), d["org_id"])  # noqa: E731
accepted = {dkey(d) for d in review if d["decision"] == "accept"}  # an accept needs its exact show
held = {dkey(d)[1:] for d in review if d["decision"] == "hold"}  # a hold binds the event, whatever show it came from
bad = []
for r in packet:
    listed, o = re.search(r'listed as "(.*)"\)$', r["sources"]).group(1), orgs.get(r["org_id"])
    show = re.search(r"\(harvest-2026-11, ([a-z0-9-]+:[0-9]{4})\)", r["notes"])
    if o is None or show is None:
        bad.append((r["participation_id"], "org not active/unknown, or notes lack the staging show key", listed)); continue
    k = (show.group(1), r["event_id"], r["role"], r["edition_year"], A.name_key(listed), r["org_id"])
    adjudicated = (k in accepted and A.name_key(listed) in decisions.trade_keys(o)
                   and "adjudicated the same entity by cross-family review" in r["notes"])
    if A.name_key(listed) != A.name_key(o["legal_name"]) and not adjudicated:
        bad.append((r["participation_id"], listed, o["legal_name"]))
    if k[1:] in held:
        bad.append((r["participation_id"], "held by review_decisions.csv", listed))
    if re.search(r"supporters|media[-_ ]?partners?|cooperating[-_ ]?media|corporate-education-sponsors",
                 r["evidence_source_url"], re.I):
        bad.append((r["participation_id"], "excluded list", r["evidence_source_url"]))
    if r["role"] not in ("exhibitor", "sponsor", "speaker"):
        bad.append((r["participation_id"], "role", r["role"]))
assert not bad, bad
print(f"OK: {len(packet)} rows, all legal-name or review-adjudicated trade-name matches, none from an excluded list")
