"""Load review_decisions.csv (the cross-family review of PR #384) for build.py and check.py, refusing any bad row.

Every row must have all 8 fields non-empty with no surrounding spaces; decision `hold` or `accept`; a participation
role; an ASCII 4-digit year; a show_key of the form `<slug>:<4 digits>` whose series is the row's event_id (events.csv
`pic_events_slug`) and, when the caller passes the staging show list, one of those shows; an org_id among `orgs` (the
caller passes active/unknown organizations); and a key no other row uses, at show grain (show_key, role, year,
normalized name) and at event grain (event_id, role, year, normalized name). A `hold` names the org the listed name
is the legal name of; an `accept` names the org the listed name is a trade name of. No name may be both held and
accepted at one event. Any failure stops the caller.

How the callers apply them (one definition, here): a hold binds its normalized name at its event for EVERY year,
show and organization, because the reason for a hold (the name does not pin one entity) does not depend on any of
them; an accept binds only its exact show, event, role, year, name and organization. Holds broad, accepts narrow.
"""
import csv
import re

import atlas as A  # callers put scripts/ on sys.path

FIELDS = ["decision", "show_key", "event_id", "role", "edition_year", "listed_name", "org_id", "reason"]
SHOW_KEY = r"[a-z0-9]+(-[a-z0-9]+)*:[0-9]{4}"


def trade_keys(org):
    return {A.name_key(t) for t in (org.get("trade_names") or "").split(";") if t.strip()}


def held_names(review):
    """{(event_id, role, name_key)}: a hold binds every year, show and organization at its event."""
    return {(d["event_id"], d["role"], A.name_key(d["listed_name"])) for d in review.values() if d["decision"] == "hold"}


def accepted_keys(review):
    """{(show_key, event_id, role, edition_year, name_key, org_id)}: an accept binds exactly this."""
    return {(d["show_key"], d["event_id"], d["role"], d["edition_year"], A.name_key(d["listed_name"]), d["org_id"])
            for d in review.values() if d["decision"] == "accept"}


def load(path, events, orgs, shows=None):
    """-> {(show_key, role, edition_year, name_key(listed_name)): row}"""
    rows = list(csv.reader(open(path, encoding="utf-8", newline="")))
    if not rows or rows[0] != FIELDS:
        raise SystemExit(f"{path.name}: header must be {','.join(FIELDS)}")
    slug_event = {s.strip(): e["event_id"] for e in events.values()
                  for s in (e.get("pic_events_slug") or "").split(";") if s.strip()}
    out, event_keys, errors = {}, set(), []
    for n, cells in enumerate(rows[1:], 2):
        if len(cells) != len(FIELDS) or not all(c.strip() and c == c.strip() for c in cells):
            errors.append(f"line {n}: needs {len(FIELDS)} non-empty fields without surrounding spaces"); continue
        d = dict(zip(FIELDS, cells))
        org, name = orgs.get(d["org_id"]), A.name_key(d["listed_name"])
        key = (d["show_key"], d["role"], d["edition_year"], name)
        event_key = (d["event_id"], d["role"], d["edition_year"], name)
        problems = [msg for bad, msg in (
            (d["decision"] not in ("hold", "accept"), "decision must be hold or accept"),
            (d["role"] not in ("exhibitor", "sponsor", "speaker"), "role must be exhibitor, sponsor or speaker"),
            (not re.fullmatch(r"[0-9]{4}", d["edition_year"]), "edition_year must be 4 ASCII digits"),
            (not re.fullmatch(SHOW_KEY, d["show_key"]), "show_key must be <slug>:<4 digits>"),
            (slug_event.get(d["show_key"].split(":")[0]) != d["event_id"], "show_key's series is not event_id"),
            (shows is not None and d["show_key"] not in shows, "show_key is not a harvested show"),
            (org is None, "org_id is not an active/unknown organization"),
            (key in out, "duplicate key (show_key, role, edition_year, listed name)"),
            (event_key in event_keys, "duplicate key (event_id, role, edition_year, listed name)"),
            (org is not None and d["decision"] == "hold" and name != A.name_key(org["legal_name"]),
             "hold: listed name is not this org's legal name"),
            (org is not None and d["decision"] == "accept" and name not in trade_keys(org),
             "accept: listed name is not one of this org's trade names"),
        ) if bad]
        if problems:
            errors.append(f"line {n}: " + "; ".join(problems)); continue
        out[key] = d
        event_keys.add(event_key)
    both = held_names(out) & {(k[1], k[2], k[4]) for k in accepted_keys(out)}
    if both:
        errors.append(f"a name is both held and accepted at one event: {sorted(both)}")
    if errors:
        raise SystemExit(f"{path.name}: " + " | ".join(errors))
    return out
