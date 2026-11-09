#!/usr/bin/env python3
"""Merge the two "Jie Xu" people records into the older one (owner decision 2026-11-03: duplicates merge into the
older record; AGENTS §6: a joint appointment is recorded once, at the primary home institution).

PERSON-000597 (Argonne, research scientist) and PERSON-000812 (University of Chicago, assistant professor) are one
person. 000812's own cited page styles her "Asst. Prof., UChicago Pritzker School of Molecular Engineering (joint
appointment at Argonne)", and the 2026-11-09 ORCID pass matched both records to one ORCID record. Her UChicago PME
directory page (read raw 2026-11-09) titles her "Assistant Professor of Molecular Engineering, UChicago Pritzker
School of Molecular Engineering", so the university is the home institution and the lab appointment is the joint one.

The older id (000597) is kept and re-homed to the university. 000812's row is removed, and its id is retired and never
reused. Sources and specialties are unioned, and the removal is logged in inclusion_log.csv. One parent-claim
evidence row records the re-homing.

    python3 tasks/people-dedupe-jie-xu-2026-11-09/build.py [--apply]
"""
import csv, io, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEEP, DROP = "PERSON-000597", "PERSON-000812"
UNI = "ORG-004660"  # University of Chicago
URL = "https://pme.uchicago.edu/faculty/jie-xu"
TITLE = "Assistant Professor of Molecular Engineering, UChicago Pritzker School of Molecular Engineering"
DATE, EVD, BY = "2026-11-09", "EVD-333028", "claude-code people-dedupe-jie-xu-2026-11-09"


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
    assert keep["full_name"] == drop["full_name"] == "Jie Xu"
    keep.update({"institution_org_id": UNI, "role": "assistant_professor", "role_as_published": TITLE,
                 "public_profile_url": URL, "last_verified": DATE,
                 "research_specialties": union(keep["research_specialties"], drop["research_specialties"]),
                 "sources": union(URL, keep["sources"], drop["sources"])})
    people = [p for p in people if p["person_id"] != DROP]
    eh, ev, ee = read(ROOT / "data/evidence_people.csv")
    assert EVD not in {e["evidence_id"] for e in ev} and not any(e["record_id"] == DROP for e in ev)
    ev.append({"evidence_id": EVD, "record_table": "people", "record_id": KEEP, "claim_type": "parent",
               "claim_detail": f"institution_org_id {UNI}; public_profile_url {URL}; merged duplicate {DROP}",
               "source_class": "own_site", "source_ref": URL, "observed_date": DATE, "tier_effect": "supports_A",
               "created_by": BY, "notes": "Raw words in order: " + TITLE})  # the page's words only (grok, #260)
    lh, log, le = read(ROOT / "data/inclusion_log.csv")
    log.append({"date": DATE, "entity": f"{DROP} Jie Xu",
                "decision": f"REMOVED: duplicate of {KEEP} (same person; University of Chicago assistant professor with a "
                            f"joint Argonne appointment); merged into {KEEP}, re-homed to {UNI}; id retired, never reused",
                "rule_cited": "owner decision 2026-11-03 (merge duplicates into the older record); AGENTS.md section 6 "
                              "(joint appointment recorded at the primary home institution); AGENTS.md section 3 (never reuse an ID)",
                "researcher": BY, "notes": "Found by the 2026-11-09 ORCID pass (both records matched one ORCID record)."})
    print(f"keep {KEEP} -> {UNI}; remove {DROP}; +1 evidence, +1 inclusion_log")
    if "--apply" in sys.argv:
        write(ROOT / "data/people.csv", ph, people, pe)
        write(ROOT / "data/evidence_people.csv", eh, ev, ee)
        write(ROOT / "data/inclusion_log.csv", lh, log, le)
        print("written")


if __name__ == "__main__":
    main()
