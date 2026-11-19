#!/usr/bin/env python3
"""Apply owner ruling 2026-11-19d item 1: the Coatings Trends & Technologies Summit 2026 "final list of registered
companies" (PCI Magazine, the organizer) is an attendee list for the 2026 edition (EVT-000077).

#411 held this one list in OWNER_PENDING. This build reads it from the same banked staging JSON and applies the same
gates as #411 (tasks/show-harvest-newseries-2026-11-19/build.py), which it imports:
- the name is on the banked page; not on a controller drop list; not held by the wave 2-3 review;
- not held by #411's CONTROLLER_HOLDS at EVT-000077 (name-key holds: every listed form, every role and year);
- a legal-name match to exactly one active/unknown organization; trade-name hits are held (trade_name_holds.csv);
- no (event, org, year, role) the table already holds. role_detail stays empty, as for every attendee row.
    python3 tasks/owner-rulings-2026-11-19d/build.py --data-dir data --harvest <staging> [--apply --i-am-the-integrator]
"""
import argparse, csv, hashlib, importlib.util, json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
# #411's build (its gates, holds and helpers), loaded under its own name: both task folders call theirs build.py
_spec = importlib.util.spec_from_file_location("newseries_build", HERE.parent / "show-harvest-newseries-2026-11-19" / "build.py")
B = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B)

A = B.A
BY = "claude-code owner-rulings-2026-11-19d"
EVENT, YEAR = "EVT-000077", "2026"
SHOW_KEY = "coatings-trends-and-technologies-summit:2027"  # the harvest's staging key for this organizer site
URL = "https://www.pcimag.com/coatings-conference/registered-companies"
HEADING = "Below is the final list of registered companies for Coatings Trends & Tecnologies Summit 2026."
NOTE = ("Attendee: the organizer's \"final list of registered companies for Coatings Trends & Tecnologies Summit 2026\" "
        "(sic); the page adds that the list \"does not denote the total number of registered attendees\". A final "
        "registration list counts as attendance under owner ruling 2026-11-19d.")
HOLDS = {  # rule (i), as #411's CONTROLLER_HOLDS: a bare group name whose Atlas record is the group's US entity
    (EVENT, A.name_key("Arkema")): B.US_ARM + " (Arkema Inc.; the group is French; held at SAMPE in #404 too)",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--harvest", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data, hv = Path(a.data_dir).resolve(), Path(a.harvest).resolve()
    events = {e["event_id"]: e for e in B.read(data / "events.csv")}
    by_key, orgs = B.org_index(data)
    held = {(e, nk) for e, _role, nk in B.decisions.held_names(B.decisions.load(B.W23 / "review_decisions.csv", events, orgs))}
    drops = {(r["show_key"], r["role"], r["name_sha256_16"]) for p in (B.W1, B.W23) for r in B.read(p / "controller_drops.csv")}
    part = B.read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"], p["role"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1

    d = json.loads((hv / "out" / "coatings-trends-and-technologies-summit_2027.json").read_text(encoding="utf-8"))
    assert d["show_key"] == SHOW_KEY
    (L,) = [x for x in d["lists"] if x["source_url"] == URL]
    assert L["role"] == "attendee" and str(L["list_edition_year"]) == YEAR and L["complete"], L["role"]
    raw = (hv / L["raw_file"]).read_text(encoding="utf-8", errors="replace")
    assert HEADING in raw, "the banked page no longer carries the 'final list' heading"
    page = B.text(raw, True)

    rows, holds, skip, hit = [], [], Counter(), set()
    for c in L["companies"]:
        name = c["name"].strip()
        if B.norm(name) not in page:
            skip["name not on the page"] += 1; continue
        if (SHOW_KEY, "attendee", hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]) in drops:
            skip["controller drop"] += 1; continue
        nk = A.name_key(name)
        if (EVENT, nk) in held:
            skip["held by the wave 2-3 review"] += 1; continue
        if (EVENT, nk) in B.CONTROLLER_HOLDS:
            skip["held (#411 CONTROLLER_HOLDS)"] += 1; continue
        if (EVENT, nk) in HOLDS:
            hit.add((EVENT, nk))
            skip["held (HOLDS)"] += 1; continue
        hits = by_key.get(nk, {})
        if len(hits) != 1:
            skip["no Atlas organization" if not hits else "ambiguous name key"] += 1; continue
        org, kind = next(iter(hits.items()))
        if kind == "trade":
            holds.append({"event_id": EVENT, "edition_year": YEAR, "role": "attendee", "listed_name": name,
                          "org_id": org, "legal_name": orgs[org]["legal_name"],
                          "trade_names": orgs[org].get("trade_names", ""), "source_url": URL})
            skip["trade-name hit, held"] += 1; continue
        k = (EVENT, org, YEAR, "attendee")
        if k in have:
            skip["already a row, or a second listing of the same org"] += 1; continue
        have.add(k)
        rows.append({
            "participation_id": f"EVP-{nxt:06d}", "event_id": EVENT, "org_id": org, "edition_year": YEAR,
            "edition_name": "", "role": "attendee", "role_detail": "", "edition_dates": "", "edition_city": "",
            "edition_state": "",
            "evidence_source_name": f"{events[EVENT]['name']} {YEAR} attendee list (organizer-published)",
            "evidence_source_url": URL, "evidence_date": d["retrieved"],
            "sources": f"{URL} (read {d['retrieved']}; listed as \"{name}\")",
            "verification_tier": "A", "last_verified": d["retrieved"], "created_by": BY,
            "notes": f"Attendee name matched to the org by exact normalized legal name; list banked in staging "
                     f"(harvest-2026-11, {SHOW_KEY}). The staging key's year (2027) is the harvest's edition label; "
                     f"the row year follows the year printed in the source. {NOTE}"})
        nxt += 1

    assert sum(skip.values()) + len(rows) == len(L["companies"]) == 224, "every listed name is accounted for"
    assert hit == set(HOLDS), f"HOLDS that matched no listing: {sorted(set(HOLDS) - hit)}"
    for fname, rs, cols in (("participation_append.csv", rows, list(part[0].keys())),
                            ("trade_name_holds.csv", holds, list(holds[0]) if holds else ["listed_name"])):
        with open(HERE / fname, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
            w.writeheader(); w.writerows(rs)
    print(f"rows {len(rows)}; trade-name holds {len(holds)}; skipped {dict(skip)}")
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        B.append_rows(data / "event_participation.csv", rows)
        print("applied")


if __name__ == "__main__":
    main()
