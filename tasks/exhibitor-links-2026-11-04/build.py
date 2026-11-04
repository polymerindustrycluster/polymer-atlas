#!/usr/bin/env python3
"""Exhibitor links (2026-11-04): exhibitor participation rows from organizer-published rosters, organization grain only.

    python3 tasks/exhibitor-links-2026-11-04/build.py --data-dir data [--apply --i-am-the-integrator]

Input `matches.csv` is produced by the integrator, in two steps:
1. Each roster page was fetched rendered (NAS Firecrawl, full page).
2. Exhibitor names were taken from the link text of exhibitor or booth detail links. The match was an exact
   `scripts/atlas.py name_key` on legal or trade names; a key held by two organizations was not matched.

Rows are minted only for rosters whose series is held in `events.csv`. Five co-located AMI expos share one
MapYourShow gallery, so their names go to the umbrella event, EVT-000007, once. An (event, org, edition_year) row
already present is skipped. The edition year is read from the roster host where it encodes one (pweus26 → 2026;
camx2027 → 2027).

Tier A: the organizer's own published roster is A-equivalent for the fact of participation (SCHEMA §4.12).
Rosters were read on 2026-11-04. MapYourShow galleries returned only their first page, so the rows are a partial
roster.
"""
import argparse, csv, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402

DATE, BY = "2026-11-04", "claude-code exhibitor-links-2026-11-04"
UMBRELLA = {"EVT-000008", "EVT-000009", "EVT-000051", "EVT-000052"}  # AMI co-located expos -> EVT-000007
OVERRIDE = {"SAMPE 2026": "EVT-000035"}  # held series the name map missed (events lane, 2026-11-04)
# Not linked by design: MD&M West/Midwest (excluded by owner ruling 2026-10-30, SCHEMA 4.12.1 seam 3); RAPID + TCT,
# Chemspec Europe, Automotive Testing Expo (fail the named-subject test: no polymer subject).


def year_of(url, fallback):
    m = re.search(r"(?:[a-z]+)(20\d\d|\d\d)\.mapyourshow|/(?:[A-Z]+)(20\d\d|\d\d)/|(20\d\d)", url)
    y = next((g for g in (m.groups() if m else ()) if g), "")
    return ("20" + y if len(y) == 2 else y) or fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    events = {e["event_id"]: e for e in read(data / "events.csv")}
    part = read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1
    # edition city/dates from the 2026-11-04 conferences refresh (organizer pages, raw-checked), not the series home
    eds = {(r["key"], r["year"]): r for r in read(HERE / "editions.csv")}
    rows, skipped = [], Counter()
    for m in read(HERE / "matches.csv"):
        ev = OVERRIDE.get(m["conf_key"]) or ("EVT-000007" if m["event_id"] in UMBRELLA else m["event_id"])
        if ev not in events:
            skipped["series not held"] += 1; continue
        yr = year_of(m["roster_url"], m["edition_year"])
        k = (ev, m["org_ids"], yr)
        if k in have:
            skipped["already held"] += 1; continue
        have.add(k)
        e = events[ev]
        ed = eds.get((m["conf_key"], yr), {})
        dates = f"{ed['start']} to {ed['end']}" if ed.get("start") and ed.get("end") else ""
        rows.append({"participation_id": f"EVP-{nxt:06d}", "event_id": ev, "org_id": m["org_ids"], "edition_year": yr,
                     "edition_name": "", "role": "exhibitor", "role_detail": "", "edition_dates": dates,
                     "edition_city": ed.get("city", ""), "edition_state": ed.get("region", ""),
                     "evidence_source_name": f"{e['name']} {yr} exhibitor list (organizer-published roster)",
                     "evidence_source_url": m["roster_url"], "evidence_date": DATE,
                     "sources": f"{m['roster_url']} (read {DATE}; listed as \"{m['exhibitor_name']}\")",
                     "verification_tier": "A", "last_verified": DATE, "created_by": BY,
                     "notes": "Exhibitor name matched to the org by exact normalized legal/trade name. Roster read pre-show where the edition is upcoming; partial where the gallery paginates."
                              + (" Co-located AMI expos share one gallery; recorded under the umbrella event." if m["event_id"] in UMBRELLA else "")})
        nxt += 1
    with open(HERE / "participation_append.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(part[0].keys()), extrasaction="ignore", lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"participation rows {len(rows)}; by event {Counter(r['event_id'] for r in rows).most_common()}; skipped {dict(skipped)}")
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "event_participation.csv", rows)
        print("applied")


if __name__ == "__main__":
    main()
