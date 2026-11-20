#!/usr/bin/env python3
"""Check this pass's rows without the staging sources, against every build.py rule repo data can show:
- the appended rows are in the table unchanged; none repeats an (event, org, year, role) in the table;
- every row names its list (staging key) in `notes`, and that list's event, year, role and note match the row; the
  only attendee rows are the Coatings Trends 2026 registration-list names admitted under owner ruling 2026-11-20;
- `sources` cites evidence_source_url; the listed name's key is held by exactly the row's organization and is its
  LEGAL name; the name is not held by the wave 2-3 review;
- a name under a rule (i) hold of #404, #411, #414 or this pass mints only when it prints the organization's full
  legal name, suffix included, and then carries the ruling's note; the note appears on no other row; a rule (ii)
  hold never mints;
- an abroad row (an international series, an abroad note, or a non-US edition_state) names the listed country, and
  it is the organization's HQ country; tier A; no personal pattern in role_detail.
Limit: without the staging sources this cannot prove a name is in its source; build.py, which reads them, is the
guarantee.
    python3 tasks/show-harvest-muse-leads-2026-11-20/check.py
"""
import csv, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build as P  # noqa: E402  (this pass)

N, D, A = P.N, P.D, P.A
read = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))  # noqa: E731
packet = read(HERE / "participation_append.csv")
whole = read(ROOT / "data" / "event_participation.csv")
table = [r for r in whole if r["created_by"] == P.BY]
assert table == packet, f"table has {len(table)} rows of this pass, packet {len(packet)}; they must be identical"
counts = Counter((r["event_id"], r["org_id"], r["edition_year"], r["role"]) for r in whole)
events = {e["event_id"]: e for e in read(ROOT / "data" / "events.csv")}
by_key, orgs = N.org_index(ROOT / "data")
held = {(e, nk) for e, _role, nk in N.decisions.held_names(N.decisions.load(N.W23 / "review_decisions.csv", events, orgs))}
holds = P.rule_i_holds()
USPS = N.w23.USPS
# #414's rows from the same registration list carry its one read date; the rows this pass admits from it must too
(REG_DATE,) = {r["evidence_date"] for r in whole if r["created_by"] == D.BY and r["evidence_source_url"] == D.URL}
bad = []
for r in packet:
    pid, ev = r["participation_id"], r["event_id"]
    if counts[(ev, r["org_id"], r["edition_year"], r["role"])] != 1:
        bad.append((pid, "duplicate (event, org, year, role) in the table"))
    key = re.search(r"\(muse-leads-2026-11-19, (\w+)\)", r["notes"])
    if key:
        spec = P.LISTS.get(key.group(1))
        if not spec or (spec[0], spec[1], spec[2]) != (ev, r["edition_year"], r["role"]) or spec[5] not in r["notes"]:
            bad.append((pid, "row does not match its list's event, year, role or note"))
        else:  # a list that predates its edition says so; one with an as-of date and no edition dates says that
            as_of, start = spec[3], r["edition_dates"].split(" to ")[0]
            if (bool(as_of and start and as_of < start) != ("Pre-show list" in r["notes"])
                    or bool(as_of and not start) != ("dates are not on record" in r["notes"])):
                bad.append((pid, "pre-show note and the list's as-of date disagree"))
            read = re.search(r"\(read ([0-9-]+);", r["sources"])
            if r["evidence_date"] != (as_of or (read.group(1) if read else "")):
                bad.append((pid, "evidence_date is not the list's as-of date (or, with none printed, the read date)"))
            if r["edition_name"] != P.EDITION_NAME.get(key.group(1), ""):
                bad.append((pid, "edition_name is not the name this list's edition ran under"))
    elif not (r["role"] == "attendee" and (ev, r["edition_year"]) == (D.EVENT, D.YEAR)
              and r["evidence_source_url"] == D.URL and D.NOTE in r["notes"] and P.RULING in r["notes"]
              and r["edition_name"] == ""  # and, as the list prints no as-of date, evidence_date is #414's read date
              and r["evidence_date"] == REG_DATE and f"(read {REG_DATE};" in r["sources"]):
        bad.append((pid, "row names no list, and is not an admitted registration-list attendee row"))
    if r["role"] == "attendee" and key:
        bad.append((pid, "attendee row from a Muse-lead list"))
    cited = re.fullmatch(r'(\S+) \(read [0-9-]+; listed as "(.*)"\)', r["sources"])
    if not cited or cited.group(1) != r["evidence_source_url"]:
        bad.append((pid, "sources does not cite evidence_source_url")); continue
    listed, o = cited.group(2), orgs.get(r["org_id"])
    if o is None:
        bad.append((pid, "org not active/unknown")); continue
    nk = A.name_key(listed)
    if set(by_key.get(nk, {})) != {r["org_id"]}:
        bad.append((pid, f"listed name's key is held by {sorted(by_key.get(nk, {}))}"))
    if nk != A.name_key(o["legal_name"]):
        bad.append((pid, "listed name is not the org's legal name"))
    if (ev, nk) in held:
        bad.append((pid, "name held by the wave 2-3 review"))
    under = (ev, nk) in holds
    if under and not (holds[(ev, nk)] and P.names_us_entity(listed, o["legal_name"])):
        bad.append((pid, "name held (a bare group name, or a rule (ii) hold)"))
    elif under != (P.RULING in r["notes"]):
        bad.append((pid, "owner ruling 2026-11-20 note and hold disagree"))
    if r["verification_tier"] != "A":
        bad.append((pid, "verification_tier is not A"))
    if N.PERSONAL.search(r["role_detail"]):
        bad.append((pid, "personal pattern in role_detail"))
    said = re.search(r"Edition abroad: the list gives the company's country \((.+?)\), which matches", r["notes"])
    if (events[ev]["home_region"] == "international" or "Edition abroad" in r["notes"]
            or r["edition_state"] not in USPS | {""}):
        if not said or not N.iso(said.group(1)) or N.iso(said.group(1)) != N.iso(o["hq_country"]):
            bad.append((pid, "abroad row without a listed country equal to the org's HQ country"))
        if r["edition_state"] in USPS:
            bad.append((pid, "abroad row with a USPS edition_state"))
assert not bad, bad
print(f"OK: {len(packet)} rows, each a legal-name match from a banked organizer list, none held, every abroad row's "
      f"listed country its org's HQ country")
