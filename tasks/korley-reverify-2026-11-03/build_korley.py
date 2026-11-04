#!/usr/bin/env python3
"""Re-verify PERSON-000719 (LaShanda T. J. Korley): she moved from the University of Delaware to NYU (2026-11-03).

    python3 tasks/korley-reverify-2026-11-03/build_korley.py --data-dir data
        -> edits.csv (apply with scripts/apply_p1_crm_scrub.py --packet-dir), inclusion_log_append.csv

Evidence, read 2026-11-03 from the institution's own pages:
  * https://engineering.nyu.edu/faculty/lashanda-korley prints "Chemical and Biomolecular Engineering Department
    Chair" and "Professor", and says "Before joining NYU, Dr. Korley was a Distinguished Professor of Engineering at
    the University of Delaware".
  * https://engineering.nyu.edu/news/new-chemical-and-biomolecular-engineering-chair-lashanda-korley-bridges-polymer-science
    (posted August 19, 2026) names her chair of NYU Tandon's Department of Chemical and Biomolecular Engineering,
    "an accomplished polymer scientist" who "joins NYU from the University of Delaware".
The record is updated in place (handoff 2026-11-03: never a second record): institution -> ORG-004705 New York
University, the printed title, the NYU profile URL, NYU pages as sources. The 2024 UDaily article stays as the
dated source for her listed research areas; the Delaware faculty listing is dropped as stale. Stdlib only.
"""
import argparse, csv, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
PID, NYU = "PERSON-000719", "ORG-004705"
PROFILE = "https://engineering.nyu.edu/faculty/lashanda-korley"
NEWS = ("https://engineering.nyu.edu/news/new-chemical-and-biomolecular-engineering-chair-lashanda-korley-"
        "bridges-polymer-science")
UDAILY = "https://www.udel.edu/udaily/2024/september/plastics-innovation-lashanda-korley-sustainability/"
NEW = {"institution_org_id": NYU,
       "role": "professor",
       "role_as_published": "Chemical and Biomolecular Engineering Department Chair; Professor",
       "public_profile_url": PROFILE,
       "sources": ";".join([PROFILE, NEWS, UDAILY]),
       "verification_tier": "A",
       "last_verified": "2026-11-03"}
EDIT_COLS = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    data = Path(ap.parse_args().data_dir)
    with open(data / "people.csv", newline="", encoding="utf-8") as fh:
        p = next(r for r in csv.DictReader(fh) if r["person_id"] == PID)
    with open(data / "ecosystem.csv", newline="", encoding="utf-8") as fh:
        assert any(r["org_id"] == NYU for r in csv.DictReader(fh)), "NYU must be a held institution"
    edits = [{"file": "people.csv", "row_id": PID, "column": c, "old_sha256": hashlib.sha256(p[c].encode()).hexdigest(),
              "new_value": v, "edit_class": "PERSON_MOVED",
              "rationale": f"moved from the University of Delaware to NYU: {PROFILE}; {NEWS} (posted 2026-08-19)"}
             for c, v in NEW.items() if p[c] != v]
    log = [{"date": "2026-11-03", "entity": f"{PID} {p['full_name']}",
            "decision": f"UPDATED in place: institution {p['institution_org_id']} -> {NYU} (New York University); "
                        "one record, never a second",
            "rule_cited": "handoff 2026-11-03 item 3; SCHEMA 4.9 (institution's own pages; person_id never reused)",
            "researcher": "claude-code korley-reverify-2026-11-03",
            "notes": "NYU Tandon profile and dated announcement (2026-08-19) both state she joined from Delaware"}]
    for name, cols, rows in (("edits.csv", EDIT_COLS, edits),
                             ("inclusion_log_append.csv", ["date", "entity", "decision", "rule_cited", "researcher", "notes"], log)):
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"edits: {len(edits)} ({', '.join(e['column'] for e in edits)})")


if __name__ == "__main__":
    main()
