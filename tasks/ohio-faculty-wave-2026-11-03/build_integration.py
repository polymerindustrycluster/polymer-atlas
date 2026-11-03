#!/usr/bin/env python3
"""Integrate the Ohio faculty wave (2026-11-03): VERIFIED lane rows -> people.csv.

    python3 tasks/ohio-faculty-wave-2026-11-03/build_integration.py --data-dir data --lanes <dir with out*.csv> [--apply --i-am-the-integrator]

The candidate list came from the Ohio Innovation Exchange expert search, a discovery lead whose terms reserve all rights.
It is NOT committed, and nothing here cites it. Only VERIFIED rows are kept: both gates met on the university's own pages,
role in the university professor vocabulary, and no '@' in any URL. Each person is checked against people.csv on first and
last name at the same institution, and a match is held as already present. The integrator's Gate B review holds are listed
below. PERSON ids are allocated above the people.csv maximum.
"""
import argparse, csv, glob, io, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TODAY = "2026-11-03"
ROLES = {"professor", "associate_professor", "assistant_professor", "research_professor", "center_director_professor", "senior_lecturer"}
INST = {"bowling green state university": "ORG-002087", "case western reserve university": "ORG-000502",
        "cleveland state university": "ORG-000158", "ohio state university": "ORG-001284",
        "the ohio state university": "ORG-001284", "university of akron": "ORG-000501",
        "university of cincinnati": "ORG-001314", "university of dayton": "ORG-001315"}
INTEGRATOR_HOLDS = {"david mccomb": "Gate B: his page names polymers only as an example of materials his electron microscopy studies, not as his research object"}


def fl(name):
    w = [x for x in re.sub(r"\(.*?\)|[^a-z\s-]", " ", name.lower().replace(".", " ")).replace("-", " ").split() if len(x) > 1]
    return (w[0], w[-1]) if w else ("", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True); ap.add_argument("--lanes", required=True)
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir)
    people = list(csv.DictReader(open(data / "people.csv", newline="", encoding="utf-8")))
    held = {(p["institution_org_id"],) + fl(p["full_name"]): p["person_id"] for p in people}

    def held_as(oid, name):
        """Same institution and last name, and one first name a prefix of the other (Ben / Benjamin)."""
        f, l = fl(name)
        for (o, f2, l2), pid in held.items():
            if o == oid and l2 == l and (f2.startswith(f) or f.startswith(f2)):
                return pid
        return None
    nxt = max(int(p["person_id"][7:]) for p in people) + 1
    rows, holds, verified = [], [], []
    for f in sorted(glob.glob(str(Path(a.lanes) / "out*.csv"))):
        for r in csv.DictReader(open(f, newline="", encoding="utf-8")):
            if r["verdict"].strip() != "VERIFIED":
                continue
            verified.append(r)
            name = r["full_name"].strip(); oid = INST.get(r["institution"].strip().lower())
            why = []
            if not oid: why.append("institution not mapped")
            elif held_as(oid, name): why.append(f"already held as {held_as(oid, name)}")
            if r["role"].strip() not in ROLES: why.append(f"role {r['role']!r} outside the professor vocabulary")
            if any("@" in r[c] for c in ("public_profile_url", "gate_a_url", "gate_b_url")): why.append("URL embeds '@'")
            if not (r["gate_a_quote"].strip() and r["gate_b_quote"].strip()): why.append("gate quote missing")
            if " ".join(fl(name)) in INTEGRATOR_HOLDS: why.append("integrator review: " + INTEGRATOR_HOLDS[" ".join(fl(name))])
            if why:
                holds.append({"full_name": name, "institution": r["institution"], "reason": "; ".join(why)}); continue
            srcs = list(dict.fromkeys(u.strip() for u in (r["public_profile_url"], r["gate_a_url"], r["gate_b_url"]) if u.strip()))
            rows.append({"person_id": f"PERSON-{nxt:06d}", "full_name": name, "institution_org_id": oid, "program_org_id": "",
                         "role": r["role"].strip(), "role_as_published": r["role_as_published"].strip(),
                         "research_specialties": "; ".join(x.strip() for x in r["research_specialties"].split(";") if x.strip()),
                         "public_profile_url": r["public_profile_url"].strip(), "sources": ";".join(srcs),
                         "verification_tier": "A", "last_verified": TODAY})
            nxt += 1
    cols = list(people[0].keys())
    with open(HERE / "people_rows.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    with open(HERE / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["full_name", "institution", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
    vcols = ["institution", "full_name", "role", "role_as_published", "public_profile_url", "gate_a_url", "gate_a_quote", "gate_b_url", "gate_b_quote", "observed_date"]
    with open(HERE / "verified_gates.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=vcols, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(verified)
    print(f"verified {len(verified)}; people to add {len(rows)} ({rows[0]['person_id'] if rows else '-'}..{rows[-1]['person_id'] if rows else '-'}); held {len(holds)}")
    if a.apply:
        if (data.resolve() == (HERE.parents[1] / "data").resolve()) and not a.i_am_the_integrator:
            sys.exit("integrator work: pass --i-am-the-integrator")
        p = data / "people.csv"; raw = p.read_bytes()
        buf = io.StringIO(); csv.writer(buf, lineterminator="\n").writerows([[r[c] for c in cols] for r in rows])
        p.write_bytes(raw + buf.getvalue().encode("utf-8")); print("applied")


if __name__ == "__main__":
    main()
