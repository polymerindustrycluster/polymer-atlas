#!/usr/bin/env python3
"""Idempotent: writes data/people.csv and data/evidence_people.csv rows for VERIFIED verdicts only.
IDs: PERSON-002400.. and EVD-394000.. allocated in verdicts.csv order. Re-running adds nothing new.
If main moved, re-run on current origin/main (never hand-merge CSVs)."""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
import common
from shard_io import append_sorted
DATA = os.path.join(common.REPO, "data")
TODAY = "2026-11-17"; BY = "atlas-w17-fac-b"
P0, E0 = 2400, 394000

def main():
    ver = [r for r in csv.DictReader(open(os.path.join(HERE, "verdicts.csv"))) if r["verdict"] == "VERIFIED"]
    people = list(csv.DictReader(open(os.path.join(DATA, "people.csv"))))
    evid = list(csv.DictReader(open(os.path.join(DATA, "evidence_people.csv"))))
    have = {(p["institution_org_id"], common.norm(p["full_name"])): p["person_id"] for p in people}
    mine = {p["person_id"] for p in people if P0 <= int(p["person_id"][7:]) <= P0 + 99}
    new_p, new_e = [], []
    for i, r in enumerate(ver):
        key = (r["institution_org_id"], common.norm(r["full_name"]))
        if key in have:
            if have[key] not in mine: raise SystemExit(f"{r['full_name']} already held as {have[key]}")
            continue
        pid = f"PERSON-{P0 + i:06d}"
        srcs = [r["public_profile_url"]] + ([r["lab_url"]] if r["lab_url"] else [])
        srcs += [u for u in (r["gate_a_url"], r["gate_b_url"]) if u and u not in srcs]
        tier = "A" if r["scope_effect"] == "supports_A" else "B"
        new_p.append({"person_id": pid, "full_name": r["full_name"], "institution_org_id": r["institution_org_id"], "program_org_id": "",
                      "role": r["role"], "role_as_published": r["role_as_published"], "research_specialties": r["research_specialties"],
                      "public_profile_url": r["public_profile_url"], "lab_url": r["lab_url"], "sources": ";".join(srcs),
                      "verification_tier": tier, "last_verified": TODAY})
        for k, (ct, url, sha, q, eff, det) in enumerate([
                ("existence", r["gate_a_url"], r["gate_a_sha256"], r["gate_a_quote"], "supports_A", f"name {r['full_name']}; role {r['role']}; title {r['role_as_published']}"),
                ("scope", r["gate_b_url"], r["gate_b_sha256"], r["gate_b_quote"], r["scope_effect"], f"Current own-institution polymer research; research_specialties {r['research_specialties']}")]):
            new_e.append({"evidence_id": f"EVD-{E0 + 2 * i + k:06d}", "record_table": "people", "record_id": pid, "claim_type": ct, "claim_detail": det,
                          "source_class": "own_site", "source_ref": url, "observed_date": TODAY, "tier_effect": eff, "created_by": BY,
                          "notes": f"Raw words in order: {q}; page sha256 {sha}"})
    if new_p:
        append_sorted(os.path.join(DATA, "people.csv"), new_p, "person_id")
        append_sorted(os.path.join(DATA, "evidence_people.csv"), new_e, "evidence_id")
    print(f"verified={len(ver)} added people={len(new_p)} evidence={len(new_e)}")

if __name__ == "__main__":
    main()
