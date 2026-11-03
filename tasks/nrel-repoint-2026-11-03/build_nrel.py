#!/usr/bin/env python3
"""Apply packet for the 18 NLR (formerly NREL) people records, under owner rulings B-NLR-1 (a) and B-NLR-2 (a),
ruled 2026-11-03 (README.md).

    python3 tasks/nrel-repoint-2026-11-03/build_nrel.py --data-dir data
        -> edits.csv (apply with scripts/apply_p1_crm_scrub.py --packet-dir)

VERIFIED (lane_out.csv, every title and polymer quote found verbatim on the raw page, raw_check.csv):
  public_profile_url -> the research-hub.nlr.gov profile; sources -> that profile, the polymer page, and any old
  nrel.gov citation that still loads at the same path on nlr.gov (url_map.csv live_with_name); dead citations drop;
  role_as_published -> NLR's printed title; role kept (B-NLR-1 a), except where the printed title is itself a
  vocabulary rank (ROLE_FROM_TITLE); tier unchanged; last_verified -> today.
STILL_UNCERTAIN: verification_tier -> U (SCHEMA 4.9, vanished profile); live same-path citations re-pointed to
  nlr.gov, dead ones kept as the record's only sources; last_verified -> today. Stdlib only.
"""
import argparse, csv, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
TODAY = "2026-11-03"
ROLE_FROM_TITLE = {"PERSON-000646": "senior_scientist"}  # prints "Senior Scientist, Materials Science"
EDIT_COLS = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    data = Path(ap.parse_args().data_dir)
    lane = {r["person_id"]: r for r in read(HERE / "lane_out.csv")}
    raw = {r["person_id"]: r for r in read(HERE / "raw_check.csv")}
    live = {(r["person_id"], r["old_url"]): r["new_url"] for r in read(HERE / "url_map.csv")
            if r["status"] == "live_with_name"}
    dead = {(r["person_id"], r["old_url"]) for r in read(HERE / "url_map.csv") if r["status"] != "live_with_name"}
    people = {r["person_id"]: r for r in read(data / "people.csv") if r["person_id"] in lane}
    assert len(people) == len(lane) == 18, (len(people), len(lane))

    edits = []
    for pid, p in people.items():
        l = lane[pid]
        old_srcs = [s.strip() for s in p["sources"].split(";") if s.strip()]
        if l["verdict"] == "VERIFIED":
            r = raw[pid]
            assert r["title_found"] == "yes" and r["polymer_found"] == "yes", pid
            kept = [live.get((pid, s), s) for s in old_srcs if (pid, s) not in dead]
            srcs = list(dict.fromkeys([l["title_url"], l["polymer_url"] or l["title_url"]] + kept))
            new = {"public_profile_url": (l["title_url"], "PROFILE_REPOINT"),
                   "sources": (";".join(srcs), "PROFILE_REPOINT"),
                   "role_as_published": (l["role_as_published"], "ROLE_TITLE_EXACT"),
                   "last_verified": (TODAY, "REVERIFIED")}
            if pid in ROLE_FROM_TITLE:
                new["role"] = (ROLE_FROM_TITLE[pid], "ROLE_FROM_TITLE")
            why = f"NREL renamed NLR 2025-12-01; re-verified {TODAY} on {l['title_url']} (B-NLR-1 a)"
        else:
            new = {"public_profile_url": (live.get((pid, p["public_profile_url"]), p["public_profile_url"]),
                                          "PROFILE_REPOINT"),
                   "sources": (";".join(live.get((pid, s), s) for s in old_srcs), "PROFILE_REPOINT"),
                   "verification_tier": ("U", "TIER_DROP"),
                   "last_verified": (TODAY, "REVERIFIED")}
            why = f"cited nrel.gov page gone, no NLR page settles it (B-NLR-2 a; SCHEMA 4.9): {l['note'][:160]}"
        for col, (val, cls) in new.items():
            if p[col] != val:
                edits.append({"file": "people.csv", "row_id": pid, "column": col,
                              "old_sha256": hashlib.sha256(p[col].encode()).hexdigest(),
                              "new_value": val, "edit_class": cls, "rationale": why})
    with open(HERE / "edits.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=EDIT_COLS, lineterminator="\n"); w.writeheader(); w.writerows(edits)
    from collections import Counter
    print(len(edits), "edits on", len({e["row_id"] for e in edits}), "people records", dict(Counter(e["edit_class"] for e in edits)))


if __name__ == "__main__":
    main()
