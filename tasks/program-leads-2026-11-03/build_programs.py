#!/usr/bin/env python3
"""Program rows from the OH/PA program-lead lanes (lanes/P1, lanes/P2), integrator-reviewed, 2026-11-03.

    python3 tasks/program-leads-2026-11-03/build_programs.py --data-dir data [--apply --i-am-the-integrator]
        -> program_rows.csv, evidence_append.csv

Each row below passed the named-program test (SCHEMA 4.11 prong a: polymer or plastics by name) on the institution's
own page, and its evidence quote was re-read word for word on that page by the integrator on 2026-11-03. Every other
lane VERIFIED row is held in holds.csv. PROG ids are allocated above programs.csv's max. EVD ids start above
EVD-020271, because open PR #26 already uses EVD-020270 and EVD-020271.
"""
import argparse, csv, hashlib, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402

TODAY, BY = "2026-11-03", "claude-code program-leads-2026-11-03"
EVD_FLOOR = 20271
BEHREND = dict(institution_org_id="ORG-002779", city="Erie", state="PA", county="Erie")
PCT = dict(institution_org_id="ORG-002780", city="Williamsport", state="PA", county="Lycoming")
PROGRAMS = [  # (fields, evidence quote)
    (dict(BEHREND, program_name="Polymer Engineering and Science, B.S.", program_type="degree", credential_types="bs",
          level="bachelor", unit_department="School of Engineering",
          url="https://bulletins.psu.edu/undergraduate/colleges/behrend/polymer-engineering-science-bs/",
          engagement_modes="student_projects_capstone", geography_served="pennsylvania",
          notes="Distinct from PROG-000035 (Plastics Engineering Technology, B.S., PLET): the bulletin lists PES as its "
                "own major at the Erie campus, with three senior-project courses (PES 446W-448W). Lead: ABET listing "
                "(crosswalk leads.csv)."),
     "The relationships between polymer processing and chemical and micro structure/property development will be emphasized"),
    (dict(BEHREND, program_name="Plastics Training Academy", program_type="training", credential_types="", level="none",
          unit_department="Community and Workforce Programs",
          url="https://behrend.psu.edu/community-and-workforce-programs/plastics-training-academy/courses",
          engagement_modes="training_seats_open_enrollment", geography_served="national",
          notes="Short-term injection-molding courses with a published 2026 schedule and registration. Found beside a "
                "Behrend lead, not named by one."),
     "Penn State Behrend's Plastics Training Academy, which has offered programs for nearly thirty years, is highly regarded by plastics experts"),
    (dict(PCT, program_name="Polymer Technology", program_type="degree", credential_types="aas_associate", level="associate",
          unit_department="", url="https://www.pct.edu/academics/et/polymer-engineering/polymer-technology",
          engagement_modes="internships_coops", geography_served="pennsylvania", admissions_status="admitting",
          notes="A.A.S., ABET ETAC-accredited (the page states it). Page states open and rolling admission and an "
                "internship section. Distinct from PROG-000036 (the B.S.). Lead: ABET listing (crosswalk leads.csv)."),
     "Plastics and polymers have the power to transform tomorrow."),
    (dict(PCT, program_name="Polymer Processing", program_type="certificate", credential_types="certificate",
          level="certificate", unit_department="", url="https://www.pct.edu/academics/et/polymer-engineering/polymer-processing",
          engagement_modes="training_seats_open_enrollment", geography_served="pennsylvania",
          notes="One-year certificate for polymer machine operators, with a credit pathway to the Polymer Engineering "
                "Technology B.S. and a high-school pathway. Found on the program index beside the ABET leads."),
     "At Penn College, we primarily study plastics, classified as a type of polymer."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    progs = read(data / "programs.csv")
    ev = [r for f in sorted(data.glob("evidence*.csv")) for r in read(f)]
    held = {(p["institution_org_id"], re.sub(r"\W", "", p["program_name"].lower())) for p in progs}
    nxt = max(int(p["program_id"][5:]) for p in progs) + 1
    evd = max([EVD_FLOOR] + [int(e["evidence_id"][4:]) for e in ev if re.fullmatch(r"EVD-\d+", e["evidence_id"])]) + 1
    rows, evs = [], []
    for f, quote in PROGRAMS:
        assert (f["institution_org_id"], re.sub(r"\W", "", f["program_name"].lower())) not in held, f["program_name"]
        pid = f"PROG-{nxt:06d}"; nxt += 1
        rows.append(dict(f, program_id=pid, public_door_url=f["url"], status="active", sources=f["url"],
                         verification_tier="A", last_verified=TODAY, pic_relevance="partner", created_by=BY,
                         notes=f"Created {TODAY} (program-leads OH/PA wave). " + f["notes"]))
        for ct, detail in (("existence", f"{f['program_name']} exists as recorded, per the institution's own current page."),
                           ("scope", f"Polymer scope by name (SCHEMA 4.11 prong a): \"{quote}\"")):
            evs.append({"evidence_id": f"EVD-{evd:06d}", "record_table": "programs", "record_id": pid, "claim_type": ct,
                        "claim_detail": detail, "source_class": "own_site", "source_ref": f["url"],
                        "observed_date": TODAY, "tier_effect": "supports_A", "created_by": BY, "notes": ""}); evd += 1
    # SCHEMA 4.11 rollup (validator V-16): the institution's polymer_program_name / _url follow its program rows.
    prec = {"degree": 0, "center": 1, "certificate": 2, "apprenticeship": 3, "training": 4, "lab_facility": 5, "course": 6}
    eco = {r["org_id"]: r for r in read(data / "ecosystem.csv")}
    edits = []
    for oid in sorted({r["institution_org_id"] for r in rows}):
        srt = sorted([p for p in progs + rows if p["institution_org_id"] == oid and p.get("status") != "tombstoned"],
                     key=lambda p: (prec[p["program_type"]], p["program_name"].strip().lower()))
        for col, val in (("polymer_program_name", "; ".join(p["program_name"].strip() for p in srt)),
                         ("polymer_program_url", srt[0]["url"].strip())):
            if eco[oid][col] != val:
                edits.append({"file": "ecosystem.csv", "row_id": oid, "column": col,
                              "old_sha256": hashlib.sha256(eco[oid][col].encode()).hexdigest(), "new_value": val,
                              "edit_class": "PROGRAM_ROLLUP", "rationale": "SCHEMA 4.11 rollup after new program rows"})
    with open(HERE / "edits.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"],
                           lineterminator="\n"); w.writeheader(); w.writerows(edits)
    print(f"rollup edits {len(edits)} (apply with scripts/apply_p1_crm_scrub.py --packet-dir)")
    for name, cols, rs in (("program_rows.csv", list(progs[0].keys()), rows), ("evidence_append.csv", list(ev[0].keys()), evs)):
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n"); w.writeheader(); w.writerows(rs)
    print(f"programs {len(rows)} ({rows[0]['program_id']}-{rows[-1]['program_id']}); evidence {len(evs)} "
          f"({evs[0]['evidence_id']}-{evs[-1]['evidence_id']})")
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "programs.csv", rows)
        append_rows(data / "evidence_programs.csv", evs)
        print("applied")


if __name__ == "__main__":
    main()
