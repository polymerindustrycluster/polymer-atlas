#!/usr/bin/env python3
"""Write VERIFIED rows from verdicts.csv into data/people.csv and data/evidence_people.csv (idempotent).
    python3 tasks/pic18-faculty-akron-2026-11-17/build.py [--dry-run]
IDs: PERSON-002300..002399 and EVD-393000..393999, allocated upward from the bottom of the block; a person already written (same
public_profile_url inside the block) is skipped, so a re-run on a moved origin/main adds nothing twice."""
import csv, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(HERE))
from shard_io import append_sorted
from frame import build as build_frame
from collections import Counter
import json
TODAY = "2026-11-17"; ME = "atlas-w17-fac-a"; INST = "ORG-000501"
PBLOCK = (2300, 2399); EBLOCK = (393000, 393999)

def block_max(ids, prefix, lo, hi):
    n = [int(i.split("-")[1]) for i in ids if i.startswith(prefix) and lo <= int(i.split("-")[1]) <= hi]
    return max(n) if n else lo - 1

def rows_for(v, pid, eid0):
    title = v["gate_a_quote"].removeprefix("Title: ")
    person = dict(person_id=pid, full_name=v["full_name"], institution_org_id=INST, program_org_id="", role=v["role"],
                  role_as_published=v["role_as_published"], research_specialties=v["research_specialties"],
                  public_profile_url=v["public_profile_url"], lab_url="", sources=v["public_profile_url"],
                  verification_tier="A", last_verified=TODAY)
    def ev(n, claim, detail, quote):
        return dict(evidence_id=f"EVD-{eid0 + n}", record_table="people", record_id=pid, claim_type=claim, claim_detail=detail,
                    source_class="own_site", source_ref=v["public_profile_url"], observed_date=TODAY, tier_effect="supports_A",
                    created_by=ME, notes=f"Raw words in order: {quote}")
    return person, [ev(0, "existence", f"name {v['full_name']}; role {v['role']}; title {title}", v["gate_a_quote"]),
                    ev(1, "scope", f"Current own-institution polymer research; research_specialties {v['research_specialties']}", v["gate_b_quote"])]

def main(dry=False):
    verdicts = [r for r in csv.DictReader(open(HERE / "verdicts.csv", newline="", encoding="utf-8")) if r["verdict"] == "VERIFIED"]
    people = list(csv.DictReader(open(ROOT / "data/people.csv", newline="", encoding="utf-8")))
    evid = list(csv.DictReader(open(ROOT / "data/evidence_people.csv", newline="", encoding="utf-8")))
    have = {r["public_profile_url"] for r in people if PBLOCK[0] <= int(r["person_id"][7:]) <= PBLOCK[1]}
    pn = block_max([r["person_id"] for r in people], "PERSON-", *PBLOCK) + 1
    en = block_max([r["evidence_id"] for r in evid], "EVD-", *EBLOCK) + 1
    newp, newe = [], []
    for v in sorted(verdicts, key=lambda r: r["full_name"]):
        if v["public_profile_url"] in have: continue
        p, e = rows_for(v, f"PERSON-{pn:06d}", en); pn += 1; en += len(e); newp.append(p); newe += e
    assert pn - 1 <= PBLOCK[1] and en - 1 <= EBLOCK[1]
    if not dry:
        if newp: append_sorted(ROOT / "data/people.csv", newp, "person_id"); append_sorted(ROOT / "data/evidence_people.csv", newe, "evidence_id")
    allv = list(csv.DictReader(open(HERE / "verdicts.csv", newline="", encoding="utf-8")))
    fr = list(csv.DictReader(open(HERE / "frame.csv", newline="", encoding="utf-8")))
    counts = {"verdicts": dict(Counter(r["verdict"].split()[0] for r in allv)), "persons_examined": len(allv),
              "frame_rows_by_unit": dict(Counter(r["unit"] for r in fr)), "people_rows_added": len(newp) + len(have), "evidence_rows_added": len(newe) + 2 * len(have)}
    json.dump(counts, open(HERE / "counts.json", "w"), indent=1, sort_keys=True)
    print(f"added {len(newp)} people, {len(newe)} evidence rows ({len(have)} already present)", counts)

if __name__ == "__main__":
    main("--dry-run" in sys.argv)
