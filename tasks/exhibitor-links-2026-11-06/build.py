#!/usr/bin/env python3
"""Exhibitor links (2026-11-06): exhibitor participation rows from organizer-published rosters, organization grain only.

    python3 tasks/exhibitor-links-2026-11-06/build.py --data-dir data --conferences ../conferences [--apply --i-am-the-integrator]

Same method as tasks/exhibitor-links-2026-11-04 (whose match.py produced this folder's matches.csv), with three
differences:
- Rosters were read in full: Map Your Show alpha lists rendered in real Chrome (local Playwright), and the other
  rosters by plain fetch. The snapshots are banked in staging (raw/tradeshows/MANIFEST.md, retrieved 2026-11-06).
- Edition city and dates come from the conferences repo's series YAML, which is checked on organizer pages, for the
  roster's edition year. They never come from the series' home city.
- The owner ruled on 2026-11-06 that publicly viewable exhibitor rosters may be read despite robots.txt or the
  platform's terms (Map Your Show section 9, Informa, Deutsche Messe).

Rows are minted only for rosters whose series is held in events.csv. An (event, org, edition_year) row already present
is skipped. Tier A: the organizer's own published roster is A-equivalent for the fact of participation (SCHEMA 4.12).
"""
import argparse, csv, sys
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402

DATE, BY = "2026-11-06", "claude-code exhibitor-links-2026-11-06"
UMBRELLA = {"EVT-000008", "EVT-000009", "EVT-000051", "EVT-000052"}  # AMI co-located expos -> EVT-000007
# A combined page that lists two co-located shows without saying which show each company exhibits at cannot support
# a per-show row: foam-expo.com lists Foam Expo and Adhesives & Bonding Expo together (79 of its 80 matches were
# already A&B 2027 exhibitors from A&B's own roster).
COMBINED = {"foam-expo-north-america"}


def edition(conf_dir, slug, year):
    p = Path(conf_dir) / "data" / "series" / f"{slug}.yaml"
    if not p.exists():
        return {}
    s = yaml.safe_load(p.read_text(encoding="utf-8"))
    return next((e for e in s["editions"] if str(e["year"]) == str(year)), {})


COUNTRY = {"DE": "Germany", "CA": "Canada", "MX": "Mexico", "GB": "United Kingdom", "FR": "France", "IT": "Italy",
           "CN": "China", "JP": "Japan", "IN": "India", "NL": "Netherlands"}


def state(ed):
    """SCHEMA 4.12.2: a USPS code for a US edition, else the full country name; empty when unknown."""
    if ed.get("country", "US") == "US":
        return ed.get("region") or ""
    return COUNTRY.get(ed["country"], "")  # shortcut: small map; add a country when a new one appears


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--conferences", required=True, help="the conferences repo checkout (edition facts)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    events = {e["event_id"]: e for e in read(data / "events.csv")}
    part = read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1
    rows, skipped = [], Counter()
    for m in read(HERE / "matches.csv"):
        ev = "EVT-000007" if m["event_id"] in UMBRELLA else m["event_id"]
        if m["conf_key"] in COMBINED:
            skipped["combined two-show roster"] += 1; continue
        if ev not in events:
            skipped["series not held"] += 1; continue
        yr = m["edition_year"]
        k = (ev, m["org_ids"], yr)
        if k in have:
            skipped["already held"] += 1; continue
        have.add(k)
        e, ed = events[ev], edition(a.conferences, m["conf_key"], yr)
        dates = f"{ed['start']} to {ed['end']}" if ed.get("start") and ed.get("end") else ""
        rows.append({"participation_id": f"EVP-{nxt:06d}", "event_id": ev, "org_id": m["org_ids"], "edition_year": yr,
                     "edition_name": "", "role": "exhibitor", "role_detail": "", "edition_dates": dates,
                     "edition_city": ed.get("city", ""), "edition_state": state(ed),
                     "evidence_source_name": f"{e['name']} {yr} exhibitor list (organizer-published roster)",
                     "evidence_source_url": m["roster_url"], "evidence_date": DATE,
                     "sources": f"{m['roster_url']} (read {DATE}; listed as \"{m['exhibitor_name']}\")",
                     "verification_tier": "A", "last_verified": DATE, "created_by": BY,
                     "notes": "Exhibitor name matched to the org by exact normalized legal/trade name. Roster read in full on "
                              f"{DATE}; for an upcoming edition it was still filling (pre-show roster)."
                              + (" Co-located AMI expos share one gallery; recorded under the umbrella event." if ev == "EVT-000007" else "")})
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
