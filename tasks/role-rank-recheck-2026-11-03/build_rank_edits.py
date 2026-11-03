#!/usr/bin/env python3
"""Turn the rank re-check lanes (lanes/batch*_out.csv) into hash-checked edits.

Only UPDATE verdicts are applied: `role` and `role_as_published` change together,
and the page(s) the lane read are added to `sources` when not already cited.
The new role must be in the SCHEMA 4.9 vocabulary (validator-enforced), and the
title must read as a printed title. KEEP and CANNOT_CONFIRM rows are left as is.

    python3 tasks/role-rank-recheck-2026-11-03/build_rank_edits.py --data-dir data
"""
import argparse, csv, hashlib, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLES = {"professor", "associate_professor", "assistant_professor", "research_professor", "center_director_professor",
         "senior_lecturer", "research_scientist", "staff_scientist", "research_engineer", "senior_scientist",
         "distinguished_scientist", "group_leader", "senior_research_engineer", "associate_scientist", "division_director",
         "assistant_scientist", "named_chair"}


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data-dir", required=True); a = ap.parse_args()
    P = {p["person_id"]: p for p in csv.DictReader(open(Path(a.data_dir) / "people.csv", newline="", encoding="utf-8"))}
    edits, held = [], []
    for f in sorted((HERE / "lanes").glob("batch*_out.csv")):
        for r in csv.DictReader(open(f, newline="", encoding="utf-8")):
            if r["verdict"].strip() != "UPDATE":
                continue
            pid, p = r["person_id"].strip(), P.get(r["person_id"].strip())
            role, title = r["new_role"].strip(), r["new_role_as_published"].strip()
            if not p or role not in ROLES or not title or '"' in title or re.match(r"[a-z]", title):
                held.append((pid, role, title)); continue
            why = f"rank re-check 2026-11-03: current official page(s) {r['url_1'][:90]} {r['url_2'][:90]}".strip()
            edits.append({"file": "people.csv", "row_id": pid, "column": "role", "old_sha256": sha(p["role"]), "new_value": role,
                          "edit_class": "RANK_RECHECK_ROLE", "rationale": why})
            edits.append({"file": "people.csv", "row_id": pid, "column": "role_as_published", "old_sha256": sha(p["role_as_published"]),
                          "new_value": title, "edit_class": "RANK_RECHECK_TITLE", "rationale": why})
            cited = {u.strip().rstrip("/") for u in [p["public_profile_url"]] + p["sources"].split(";") if u.strip()}
            add = [u.strip() for u in (r["url_1"], r["url_2"]) if u.strip().startswith("http") and u.strip().rstrip("/") not in cited]
            if add:
                edits.append({"file": "people.csv", "row_id": pid, "column": "sources", "old_sha256": sha(p["sources"]),
                              "new_value": ";".join([p["sources"]] + add) if p["sources"] else ";".join(add),
                              "edit_class": "RANK_RECHECK_SOURCE", "rationale": "cite the page(s) the rank was read from"})
    with open(HERE / "edits.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"], lineterminator="\n")
        w.writeheader(); w.writerows(edits)
    print(f"edits {len(edits)} over {len({e['row_id'] for e in edits})} people; held {held}")


if __name__ == "__main__":
    main()
