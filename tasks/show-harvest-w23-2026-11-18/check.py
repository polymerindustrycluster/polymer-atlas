#!/usr/bin/env python3
"""Check this pass without the staging harvest: the appended rows are in the table unchanged; each row's notes name a
staging show that is a series of the row's event; every row's listed name is its organization's LEGAL name, or a
trade name accepted for that exact show, event, role, year, name and org in review_decisions.csv (with the notes
saying so); no row carries a name review_decisions.csv holds at that event (any year, show or org); and no row cites
a list the README excludes. Limit: without the staging harvest this cannot prove a row came from its list; build.py,
which reads the banked pages, is the provenance guarantee, and this checks the committed rows against its rules.
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
review = decisions.load(HERE / "review_decisions.csv", events, orgs)  # refuses any malformed row
# keyed as build.py applies them: show (from the row's notes), event, role, year, normalized listed name and org
accepted, held = decisions.accepted_keys(review), decisions.held_names(review)  # one definition, in decisions.py
slug_event = {s.strip(): e["event_id"] for e in events.values() for s in (e.get("pic_events_slug") or "").split(";")
              if s.strip()}
bad = []
for r in packet:
    listed, o = re.search(r'listed as "(.*)"\)$', r["sources"]).group(1), orgs.get(r["org_id"])
    show = re.search(r"\(harvest-2026-11, (" + decisions.SHOW_KEY + r")\)", r["notes"])
    if o is None or show is None:
        bad.append((r["participation_id"], "org not active/unknown, or notes lack the staging show key", listed)); continue
    show = show.group(1)
    if slug_event.get(show.split(":")[0]) != r["event_id"]:  # the row's show must be a series of its event
        bad.append((r["participation_id"], f"notes' show {show} is not a series of {r['event_id']}", listed))
    nk = A.name_key(listed)
    adjudicated = ((show, r["event_id"], r["role"], r["edition_year"], nk, r["org_id"]) in accepted
                   and nk in decisions.trade_keys(o)
                   and "adjudicated the same entity by cross-family review" in r["notes"])
    if nk != A.name_key(o["legal_name"]) and not adjudicated:
        bad.append((r["participation_id"], listed, o["legal_name"]))
    if (r["event_id"], r["role"], nk) in held:
        bad.append((r["participation_id"], "held by review_decisions.csv", listed))
    if re.search(r"supporters|media[-_ ]?partners?|cooperating[-_ ]?media|corporate-education-sponsors",
                 r["evidence_source_url"], re.I):
        bad.append((r["participation_id"], "excluded list", r["evidence_source_url"]))
    if r["role"] not in ("exhibitor", "sponsor", "speaker"):
        bad.append((r["participation_id"], "role", r["role"]))
assert not bad, bad
print(f"OK: {len(packet)} rows, all legal-name or review-adjudicated trade-name matches, none from an excluded list")
