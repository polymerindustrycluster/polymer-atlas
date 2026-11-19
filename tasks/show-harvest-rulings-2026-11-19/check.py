#!/usr/bin/env python3
"""Check this pass without the staging harvest: the appended rows are in the table unchanged; `sources` cites the
row's evidence_source_url; the listed name's key is held by exactly the row's organization and is its LEGAL name;
an `attendee` row comes only from a list in build.py ATTENDEE_LISTS and carries that list's note; any other row is
an alt-text name and says so; no row carries a name held at its event (build.py CONTROLLER_HOLDS or the wave 2-3
review); each row's notes name a staging show that is a series of its event (the AMI umbrella mapping applied).
Limit: without the staging harvest this cannot prove a row came from its list; build.py, which reads the banked
pages, is the provenance guarantee, and this checks the committed rows against its rules.
    python3 tasks/show-harvest-rulings-2026-11-19/check.py
"""
import csv, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402  (this pass's build: its constants and the wave 2-3 gates it loads)

A, decisions = B.A, B.decisions
read = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))  # noqa: E731
packet = read(HERE / "participation_append.csv")
table = [r for r in read(ROOT / "data" / "event_participation.csv") if r["created_by"] == B.BY]
assert table == packet, f"table has {len(table)} rows of this pass, packet {len(packet)}; they must be identical"

events = {e["event_id"]: e for e in read(ROOT / "data" / "events.csv")}
by_key, orgs = B.org_index(ROOT / "data")
held = decisions.held_names(decisions.load(B.W23 / "review_decisions.csv", events, orgs)) | set(B.CONTROLLER_HOLDS)
slug_event = {s.strip(): e["event_id"] for e in events.values() for s in (e.get("pic_events_slug") or "").split(";")
              if s.strip()}
bad = []
for r in packet:
    pid = r["participation_id"]
    cited = re.fullmatch(r'(\S+) \(read [0-9-]+; listed as "(.*)"\)', r["sources"])
    if not cited or cited.group(1) != r["evidence_source_url"]:
        bad.append((pid, "sources does not cite evidence_source_url")); continue
    listed, o = cited.group(2), orgs.get(r["org_id"])
    show = re.search(r"\(harvest-2026-11, (" + decisions.SHOW_KEY + r")\)", r["notes"])
    if o is None or show is None:
        bad.append((pid, "org not active/unknown, or notes lack the staging show key")); continue
    ev = slug_event.get(show.group(1).split(":")[0], "")
    if B.UMBRELLA.get(ev, ev) != r["event_id"]:
        bad.append((pid, f"notes' show {show.group(1)} is not a series of {r['event_id']}"))
    nk = A.name_key(listed)
    if set(by_key.get(nk, {})) != {r["org_id"]}:
        bad.append((pid, f"listed name's key is held by {sorted(by_key.get(nk, {}))}"))
    if nk != A.name_key(o["legal_name"]):
        bad.append((pid, "listed name is not the org's legal name"))
    if (r["event_id"], r["role"], nk) in held:
        bad.append((pid, "held name"))
    if r["role"] == "attendee":
        if B.ATTENDEE_LISTS.get(r["evidence_source_url"], "\0") not in r["notes"]:
            bad.append((pid, "attendee row not from an ATTENDEE_LISTS list, or without its note"))
    elif r["role"] not in B.ROLES or "logo's alt text" not in r["notes"]:
        bad.append((pid, "non-attendee row is not an alt-text name"))
    if B.MEDIA_PARTNERS.search(r["evidence_source_url"]) or r["evidence_source_url"] in B.NOT_EVENT_LISTS:
        bad.append((pid, "excluded list"))
assert not bad, bad
print(f"OK: {len(packet)} rows, each a legal-name match from an admitted list, none held or excluded")
