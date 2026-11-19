#!/usr/bin/env python3
"""Check this pass without the staging harvest, against every build.py rule that repo data can show:
- the appended rows are in the table unchanged, and no (event, org, year, role) appears twice in the whole table;
- `sources` cites the row's evidence_source_url; the notes name a staging show that is a series of the row's event
  (the AMI umbrella mapping applied), and that show and role are not a combined-list exclusion (COMBINED);
- the listed name's key is held by exactly the row's organization and is its LEGAL name; the name is not on a
  controller drop list for that show and role, and not held at the event (CONTROLLER_HOLDS or the wave 2-3 review);
- an `attendee` row comes only from an ATTENDEE_LISTS list, for that list's own event, with that list's note and an
  empty role_detail; any other row is an alt-text name and says so; no role_detail carries a personal pattern;
- no row cites a media-partner or not-an-event list.
Limit: without the staging harvest this cannot prove a row came from its list; build.py, which reads the banked
pages, is the provenance guarantee.
    python3 tasks/show-harvest-rulings-2026-11-19/check.py
"""
import csv, hashlib, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402  (this pass's build: its constants and the wave 2-3 gates it loads)

A, decisions = B.A, B.decisions
read = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))  # noqa: E731
packet = read(HERE / "participation_append.csv")
whole = read(ROOT / "data" / "event_participation.csv")
table = [r for r in whole if r["created_by"] == B.BY]
assert table == packet, f"table has {len(table)} rows of this pass, packet {len(packet)}; they must be identical"
counts = Counter((r["event_id"], r["org_id"], r["edition_year"], r["role"]) for r in whole)

events = {e["event_id"]: e for e in read(ROOT / "data" / "events.csv")}
by_key, orgs = B.org_index(ROOT / "data")
held = {(e, nk) for e, _role, nk in decisions.held_names(decisions.load(B.W23 / "review_decisions.csv", events, orgs))}
held |= set(B.CONTROLLER_HOLDS)
drops = {(d["show_key"], d["role"], d["name_sha256_16"]) for p in (B.W1, B.W23) for d in read(p / "controller_drops.csv")}
slug_event = {s.strip(): e["event_id"] for e in events.values() for s in (e.get("pic_events_slug") or "").split(";")
              if s.strip()}
bad = []
for r in packet:
    pid, url = r["participation_id"], r["evidence_source_url"]
    if counts[(r["event_id"], r["org_id"], r["edition_year"], r["role"])] != 1:
        bad.append((pid, "duplicate (event, org, year, role) in the table"))
    cited = re.fullmatch(r'(\S+) \(read [0-9-]+; listed as "(.*)"\)', r["sources"])
    if not cited or cited.group(1) != url:
        bad.append((pid, "sources does not cite evidence_source_url")); continue
    listed, o = cited.group(2), orgs.get(r["org_id"])
    show = re.search(r"\(harvest-2026-11, (" + decisions.SHOW_KEY + r")\)", r["notes"])
    if o is None or show is None:
        bad.append((pid, "org not active/unknown, or notes lack the staging show key")); continue
    show = show.group(1)
    ev = slug_event.get(show.split(":")[0], "")
    if B.UMBRELLA.get(ev, ev) != r["event_id"]:
        bad.append((pid, f"notes' show {show} is not a series of {r['event_id']}"))
    if (show.split(":")[0], r["role"]) in B.COMBINED:
        bad.append((pid, "combined-list exclusion (COMBINED)"))
    if (show, r["role"], hashlib.sha256(listed.encode("utf-8")).hexdigest()[:16]) in drops:
        bad.append((pid, "controller drop"))
    nk = A.name_key(listed)
    if set(by_key.get(nk, {})) != {r["org_id"]}:
        bad.append((pid, f"listed name's key is held by {sorted(by_key.get(nk, {}))}"))
    if nk != A.name_key(o["legal_name"]):
        bad.append((pid, "listed name is not the org's legal name"))
    if (r["event_id"], nk) in held:
        bad.append((pid, "held name"))
    if r["role"] == "attendee":
        event, note = B.ATTENDEE_LISTS.get(url, ("", "\0"))
        if event != r["event_id"] or note not in r["notes"]:
            bad.append((pid, "attendee row not from an ATTENDEE_LISTS list for its event, or without its note"))
        if r["role_detail"]:
            bad.append((pid, "attendee row with a role_detail"))
    elif r["role"] not in B.ROLES or "logo's alt text" not in r["notes"]:
        bad.append((pid, "non-attendee row is not an alt-text name"))
    if B.PERSONAL.search(r["role_detail"]):
        bad.append((pid, "personal pattern in role_detail"))
    if B.MEDIA_PARTNERS.search(url) or url in B.NOT_EVENT_LISTS:
        bad.append((pid, "excluded list"))
assert not bad, bad
print(f"OK: {len(packet)} rows, each a legal-name match from an admitted list, none held, dropped or excluded")
