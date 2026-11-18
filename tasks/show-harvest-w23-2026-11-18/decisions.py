"""Load review_decisions.csv (the cross-family review of PR #384) for build.py and check.py, refusing any bad row.

Every row must have all 8 fields non-empty; decision `hold` or `accept`; a participation role; a 4-digit year; a
show_key whose series is the row's event_id (events.csv `pic_events_slug`); an org_id the Atlas holds; and a key
(show_key, role, edition_year, normalized listed name) no other row uses. A `hold` names the org the listed name is
the legal name of; an `accept` names the org the listed name is a trade name of. Any failure stops the caller.
"""
import csv
import re

import atlas as A  # callers put scripts/ on sys.path

FIELDS = ["decision", "show_key", "event_id", "role", "edition_year", "listed_name", "org_id", "reason"]


def trade_keys(org):
    return {A.name_key(t) for t in (org.get("trade_names") or "").split(";") if t.strip()}


def load(path, events, orgs):
    """-> {(show_key, role, edition_year, name_key(listed_name)): row}"""
    rows = list(csv.reader(open(path, encoding="utf-8", newline="")))
    if not rows or rows[0] != FIELDS:
        raise SystemExit(f"{path.name}: header must be {','.join(FIELDS)}")
    slug_event = {s.strip(): e["event_id"] for e in events.values()
                  for s in (e.get("pic_events_slug") or "").split(";") if s.strip()}
    out, errors = {}, []
    for n, cells in enumerate(rows[1:], 2):
        if len(cells) != len(FIELDS) or not all(c.strip() for c in cells):
            errors.append(f"line {n}: needs {len(FIELDS)} non-empty fields"); continue
        d = dict(zip(FIELDS, cells))
        org, name = orgs.get(d["org_id"]), A.name_key(d["listed_name"])
        key = (d["show_key"], d["role"], d["edition_year"], name)
        problems = [msg for bad, msg in (
            (d["decision"] not in ("hold", "accept"), "decision must be hold or accept"),
            (d["role"] not in ("exhibitor", "sponsor", "speaker"), "role must be exhibitor, sponsor or speaker"),
            (not re.fullmatch(r"\d{4}", d["edition_year"]), "edition_year must be 4 digits"),
            (slug_event.get(d["show_key"].split(":")[0]) != d["event_id"], "show_key's series is not event_id"),
            (org is None, "org_id is not an active/unknown organization"),
            (key in out, "duplicate key (show_key, role, edition_year, listed name)"),
            (org is not None and d["decision"] == "hold" and name != A.name_key(org["legal_name"]),
             "hold: listed name is not this org's legal name"),
            (org is not None and d["decision"] == "accept" and name not in trade_keys(org),
             "accept: listed name is not one of this org's trade names"),
        ) if bad]
        if problems:
            errors.append(f"line {n}: " + "; ".join(problems)); continue
        out[key] = d
    if errors:
        raise SystemExit(f"{path.name}: " + " | ".join(errors))
    return out
