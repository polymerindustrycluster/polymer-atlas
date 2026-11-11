#!/usr/bin/env python3
"""Merge the two "Miguel Modestino" people records into the older one (owner decision 2026-11-03: duplicates
merge into the older record; AGENTS section 3: never reuse an ID).

PERSON-001187 ("Miguel Antonio Modestino", sourced to two NYU news articles) and PERSON-001260 ("Miguel
Modestino", sourced to his NYU Tandon faculty page) are one person: same name, same institution
(ORG-004705, NYU), same field. The lead came from the 2026-11-11 ORCID pass 2 dedupe screen
(tasks/people-orcid-2-2026-11-11/README.md); neither record carries an ORCID iD, and no identifier,
engagement, or evidence row references either id.

The older id (001187) is kept, at the same institution (no re-homing). The survivor takes the faculty page
as its profile URL and its current styling, read 2026-11-11: "Sustainable Engineering Initiative Director
and Associate Professor of Chemical and Biomolecular Engineering" (the page styles him "Miguel A.
Modestino", consistent with the kept record's fuller "Miguel Antonio Modestino"). Specialties and sources
are unioned; 001260's row is removed and its id retired, never reused. The removal is declared in this
folder's REMOVALS.csv and logged in inclusion_log.csv; one parent-claim evidence row records the merge.

    python3 tasks/people-dedupe-modestino-2026-11-11/build.py [--apply]
"""
import csv, io, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEEP, DROP = "PERSON-001187", "PERSON-001260"
ORG = "ORG-004705"  # New York University
URL = "https://engineering.nyu.edu/faculty/miguel-modestino"
TITLE = "Sustainable Engineering Initiative Director and Associate Professor of Chemical and Biomolecular Engineering"
DATE, EVD, BY = "2026-11-11", "EVD-333029", "spaghetti people-dedupe-modestino-2026-11-11"


def read(path):
    raw = path.read_bytes()
    eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    rdr = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    return rdr.fieldnames, list(rdr), eol


def write(path, head, rows, eol):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=head, lineterminator=eol); w.writeheader(); w.writerows(rows)
    path.write_bytes(buf.getvalue().encode("utf-8"))


def union(*vals):
    out = []
    for v in vals:
        out += [x.strip() for x in v.split(";") if x.strip() and x.strip() not in out]
    return ";".join(out)


def main():
    ph, people, pe = read(ROOT / "data/people.csv")
    by = {p["person_id"]: p for p in people}
    if DROP not in by:
        print("already merged"); return
    keep, drop = by[KEEP], by[DROP]
    assert "Modestino" in keep["full_name"] and "Modestino" in drop["full_name"]
    assert keep["institution_org_id"] == drop["institution_org_id"] == ORG
    keep.update({"role": "associate_professor", "role_as_published": TITLE,
                 "public_profile_url": URL, "last_verified": DATE,
                 "research_specialties": union(keep["research_specialties"], drop["research_specialties"]),
                 "sources": union(URL, keep["sources"], drop["sources"])})
    people = [p for p in people if p["person_id"] != DROP]
    eh, ev, ee = read(ROOT / "data/evidence_people.csv")
    assert EVD not in {e["evidence_id"] for e in ev} and not any(e["record_id"] == DROP for e in ev)
    ev.append({"evidence_id": EVD, "record_table": "people", "record_id": KEEP, "claim_type": "parent",
               "claim_detail": f"institution_org_id {ORG}; public_profile_url {URL}; merged duplicate {DROP}",
               "source_class": "own_site", "source_ref": URL, "observed_date": DATE, "tier_effect": "supports_A",
               "created_by": BY, "notes": "Raw words in order: " + TITLE})
    lh, log, le = read(ROOT / "data/inclusion_log.csv")
    log.append({"date": DATE, "entity": f"{DROP} Miguel Modestino",
                "decision": f"REMOVED: duplicate of {KEEP} (same person; NYU Tandon chemical and biomolecular "
                            f"engineering professor — one record sourced to NYU news articles, one to his faculty "
                            f"page); merged into {KEEP}; id retired, never reused",
                "rule_cited": "owner decision 2026-11-03 (merge duplicates into the older record); AGENTS.md "
                              "section 3 (never reuse an ID)",
                "researcher": BY, "notes": "Found by the 2026-11-11 ORCID pass 2 dedupe screen (same name, "
                                           "same institution). Neither record carried an ORCID iD."})
    print(f"keep {KEEP} at {ORG}; remove {DROP}; +1 evidence ({EVD}), +1 inclusion_log")
    if "--apply" in sys.argv:
        write(ROOT / "data/people.csv", ph, people, pe)
        write(ROOT / "data/evidence_people.csv", eh, ev, ee)
        write(ROOT / "data/inclusion_log.csv", lh, log, le)
        print("written")


if __name__ == "__main__":
    main()
