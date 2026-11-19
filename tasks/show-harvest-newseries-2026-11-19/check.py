#!/usr/bin/env python3
"""Check this pass without the staging harvest, against every build.py rule that repo data can show:
- the appended rows are in the table unchanged, and none repeats an (event, org, year, role) in the table;
- every row is for one of the 27 series #409 seeded; `sources` cites the row's evidence_source_url; the notes name a
  staging show that is a series of the row's event;
- the listed name's key is held by exactly the row's organization and is its LEGAL name; the name is not on a
  controller drop list for that show and role, and not held by the wave 2-3 review or CONTROLLER_HOLDS;
- an `attendee` row comes only from an ATTENDEE_LISTS list, for that list's own event and edition year, with that
  list's note and an empty role_detail; any other row is an exhibitor, sponsor or speaker; no role_detail carries a
  personal pattern;
- no row cites a media-partner or not-an-event list, a list awaiting an owner ruling (OWNER_PENDING), or an undated
  list (UNDATED_LISTS); a row carries the SUPPLEMENT note exactly when its name is a SUPPLEMENT entry for its list;
- an abroad row (an international series, an abroad note, or a non-US edition_state) names the listed country, and
  that country is the organization's HQ country; its edition_state is never a USPS code (ICERP's conferences edition
  is keyed US/IN).
Limit: without the staging harvest this cannot prove a row came from its list; build.py, which reads the banked
pages, is the provenance guarantee.
    python3 tasks/show-harvest-newseries-2026-11-19/check.py
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
drops = {(d["show_key"], d["role"], d["name_sha256_16"]) for p in (B.W1, B.W23) for d in read(p / "controller_drops.csv")}
slug_event = {s.strip(): e["event_id"] for e in events.values() for s in (e.get("pic_events_slug") or "").split(";")
              if s.strip()}
USPS = B.w23.USPS
bad = []
for r in packet:
    pid, url, ev = r["participation_id"], r["evidence_source_url"], r["event_id"]
    if ev not in B.NEW_EVENTS:
        bad.append((pid, "event is not one of the series #409 seeded"))
    if counts[(ev, r["org_id"], r["edition_year"], r["role"])] != 1:
        bad.append((pid, "duplicate (event, org, year, role) in the table"))
    cited = re.fullmatch(r'(\S+) \(read [0-9-]+; listed as "(.*)"\)', r["sources"])
    if not cited or cited.group(1) != url:
        bad.append((pid, "sources does not cite evidence_source_url")); continue
    listed, o = cited.group(2), orgs.get(r["org_id"])
    show = re.search(r"\(harvest-2026-11, (" + decisions.SHOW_KEY + r")\)", r["notes"])
    if o is None or show is None:
        bad.append((pid, "org not active/unknown, or notes lack the staging show key")); continue
    show = show.group(1)
    if slug_event.get(show.split(":")[0], "") != ev:
        bad.append((pid, f"notes' show {show} is not a series of {ev}"))
    if (show, r["role"], hashlib.sha256(listed.encode("utf-8")).hexdigest()[:16]) in drops:
        bad.append((pid, "controller drop"))
    nk = A.name_key(listed)
    if set(by_key.get(nk, {})) != {r["org_id"]}:
        bad.append((pid, f"listed name's key is held by {sorted(by_key.get(nk, {}))}"))
    if nk != A.name_key(o["legal_name"]):
        bad.append((pid, "listed name is not the org's legal name"))
    if (ev, nk) in held:
        bad.append((pid, "name held by the wave 2-3 review"))
    if (ev, nk) in B.CONTROLLER_HOLDS:
        bad.append((pid, "name held (CONTROLLER_HOLDS)"))
    if url in B.OWNER_PENDING:
        bad.append((pid, "list awaits an owner ruling (OWNER_PENDING)"))
    if (show, r["role"]) in B.UNDATED_LISTS:
        bad.append((pid, "list names no edition year (UNDATED_LISTS)"))
    supplemented = listed in B.SUPPLEMENT.get((show, r["role"]), [])
    if supplemented != (B.SUPPLEMENT_NOTE in r["notes"]):
        bad.append((pid, "SUPPLEMENT note and SUPPLEMENT entry disagree"))
    if r["role"] == "attendee":
        event, year, note = B.ATTENDEE_LISTS.get(url, ("", "", "\0"))
        if event != ev or year != r["edition_year"] or note not in r["notes"]:
            bad.append((pid, "attendee row not from an ATTENDEE_LISTS list for its event and year, or without its "
                             "note"))
        if r["role_detail"]:
            bad.append((pid, "attendee row with a role_detail"))
    elif r["role"] not in B.ROLES:
        bad.append((pid, "role not admitted"))
    if B.PERSONAL.search(r["role_detail"]):
        bad.append((pid, "personal pattern in role_detail"))
    if B.MEDIA_PARTNERS.search(url) or url in B.NOT_EVENT_LISTS:
        bad.append((pid, "excluded list"))
    said = re.search(r"Edition abroad: the list gives the company's country \((.+?)\), which matches", r["notes"])
    if (events[ev]["home_region"] == "international" or "Edition abroad" in r["notes"]
            or r["edition_state"] not in USPS | {""}):
        if not said or not B.iso(said.group(1)) or B.iso(said.group(1)) != B.iso(o["hq_country"]):
            bad.append((pid, "abroad row without a listed country equal to the org's HQ country"))
        if r["edition_state"] in USPS:
            bad.append((pid, "abroad row with a USPS edition_state"))
assert not bad, bad
print(f"OK: {len(packet)} rows, each a legal-name match from an admitted list, none held, dropped or excluded; "
      f"every abroad row's listed country is its org's HQ country")
