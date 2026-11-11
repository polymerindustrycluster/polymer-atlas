#!/usr/bin/env python3
"""Merge the two "Rigoberto Advincula" people records into the older one (owner decision 2026-11-03:
duplicates merge into the older record; AGENTS section 6: a joint appointment is recorded once, at the
primary home institution; AGENTS section 3: never reuse an ID).

PERSON-000477 (Oak Ridge National Laboratory, "Governor's Chair Professor and Group Leader") and
PERSON-001402 (University of Tennessee, Knoxville, "Governor's Chair Professor") are one person: the
Governor's Chair is a single joint UT/ORNL appointment. The lead came from the 2026-11-11 ORCID pass 2
dedupe screen; neither record carries an ORCID iD, and no identifier, engagement, or evidence row
references either id.

Primary home: UT Knoxville, on the institutions' own styling (both pages read 2026-11-11). UTK's
Governor's Chairs page presents the chair and his Chemical and Biomolecular Engineering department as
home and ORNL as the joint side: "Under his dual appointment at Oak Ridge National Laboratory,
Advincula leads ORNL's macromolecular nanomaterials group in the Center for Nanophase Materials
Sciences." ORNL's staff page styles the role jointly ("Governor's Chair Professor and Group Leader at
Oak Ridge National Laboratory and University of Tennessee"). This is the PR #260 tie-break: the
institution whose page styles the other as the joint appointment is the home.

The older id (000477) is kept and re-homed to UT Knoxville (ORG-004681), mirroring #260. The survivor
takes the UTK Governor's Chairs page as its profile URL, the removed record's role (named_chair) and
its UTK programme link (PROG-000154), the name form both institutions publish ("Rigoberto Advincula";
the kept record's accented "Advíncula" is normalised to it), and the union of specialties and sources —
the ORNL staff profile stays in sources. 001402's row is removed and its id retired, never reused. The
removal is declared in this folder's REMOVALS.csv and logged in inclusion_log.csv; one parent-claim
evidence row records the re-homing.

    python3 tasks/people-dedupe-advincula-2026-11-11/build.py [--apply]
"""
import csv, io, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEEP, DROP = "PERSON-000477", "PERSON-001402"
UNI = "ORG-004681"  # University of Tennessee, Knoxville
PROG = "PROG-000154"  # UTK Materials Science and Engineering graduate programme (carried from the removed record)
URL = "https://research.utk.edu/governors-chairs/rigoberto-advincula/"
TITLE = "Governor's Chair Professor"
DATE, EVD, BY = "2026-11-11", "EVD-333030", "spaghetti people-dedupe-advincula-2026-11-11"


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
    assert "Advincula" in keep["full_name"].replace("í", "i") and "Advincula" in drop["full_name"]
    assert drop["institution_org_id"] == UNI and drop["program_org_id"] == PROG
    keep.update({"full_name": "Rigoberto Advincula", "institution_org_id": UNI, "program_org_id": PROG,
                 "role": "named_chair", "role_as_published": TITLE,
                 "public_profile_url": URL, "last_verified": DATE, "verification_tier": "A",
                 "research_specialties": union(keep["research_specialties"], drop["research_specialties"]),
                 "sources": union(URL, keep["sources"], drop["sources"])})
    people = [p for p in people if p["person_id"] != DROP]
    eh, ev, ee = read(ROOT / "data/evidence_people.csv")
    assert EVD not in {e["evidence_id"] for e in ev} and not any(e["record_id"] == DROP for e in ev)
    ev.append({"evidence_id": EVD, "record_table": "people", "record_id": KEEP, "claim_type": "parent",
               "claim_detail": f"institution_org_id {UNI}; public_profile_url {URL}; merged duplicate {DROP}",
               "source_class": "own_site", "source_ref": URL, "observed_date": DATE, "tier_effect": "supports_A",
               "created_by": BY,
               "notes": "Raw words in order: Governor's Chair for Advanced and Nanostructured Materials; "
                        "\"Under his dual appointment at Oak Ridge National Laboratory, Advincula leads ORNL's "
                        "macromolecular nanomaterials group in the Center for Nanophase Materials Sciences\""})
    lh, log, le = read(ROOT / "data/inclusion_log.csv")
    log.append({"date": DATE, "entity": f"{DROP} Rigoberto Advincula",
                "decision": f"REMOVED: duplicate of {KEEP} (same person; Governor's Chair held jointly at UT "
                            f"Knoxville and Oak Ridge National Laboratory); merged into {KEEP}, re-homed to "
                            f"{UNI}; id retired, never reused",
                "rule_cited": "owner decision 2026-11-03 (merge duplicates into the older record); AGENTS.md "
                              "section 6 (joint appointment recorded at the primary home institution); AGENTS.md "
                              "section 3 (never reuse an ID)",
                "researcher": BY,
                "notes": "Found by the 2026-11-11 ORCID pass 2 dedupe screen. Primary home set to UT Knoxville "
                         "on UTK's own styling (its Governor's Chairs page presents ORNL as his dual "
                         "appointment). Neither record carried an ORCID iD."})
    print(f"keep {KEEP} -> {UNI}; remove {DROP}; +1 evidence ({EVD}), +1 inclusion_log")
    if "--apply" in sys.argv:
        write(ROOT / "data/people.csv", ph, people, pe)
        write(ROOT / "data/evidence_people.csv", eh, ev, ee)
        write(ROOT / "data/inclusion_log.csv", lh, log, le)
        print("written")


if __name__ == "__main__":
    main()
