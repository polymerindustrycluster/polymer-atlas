#!/usr/bin/env python3
"""ROR holds from the programs-db crosswalk (2026-11-03): verdicts for the 10 held institutions.

    python3 tasks/ror-holds-2026-11-03/build_ror.py --data-dir data
        -> edits.csv (scripts/apply_p1_crm_scrub.py --packet-dir), evidence_append.csv, verdicts.csv

Each verdict was made from ROR's own record (api.ror.org, candidates.csv from find_ror.py) and, for a rename, the
institution's own page:
  * ORG-004775 Purdue University Indianapolis -> 0482ksk80 "Purdue University in Indianapolis", active, US-IN.
  * ORG-004636 Edmonds College -> 00vhfbm88 "Edmonds Community College", active, US-WA. Same college: the board
    renamed it "Edmonds College" in April 2020 (edmonds.edu, Tritons Blog).
  * ORG-004625 WSU Tech -> 01j933b41 "Wichita Area Technical College", active, US-KS. Same college: "WSU Tech,
    formerly Wichita Area Technical College" (wsutech.edu news); affiliated with Wichita State on 2018-07-01.
The other seven are held (verdicts.csv): no ROR record of their own. Stdlib only.
"""
import argparse, csv, glob, hashlib, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TODAY = "2026-11-03"
BY = "claude-code ror-holds-2026-11-03"
EDMONDS_RENAME = "https://www.edmonds.edu/about-edmonds/news/tritons-blog/why-the-college-changed-its-name.html"
WSU_RENAME = "https://wsutech.edu/news/wsu-tech-president-named-national-board"
MINT = {  # org_id: (ror, rename page or None, ROR name, why)
    "ORG-004775": ("0482ksk80", None, "Purdue University in Indianapolis", "name agrees; active, US-IN"),
    "ORG-004636": ("00vhfbm88", EDMONDS_RENAME, "Edmonds Community College",
                   "ROR carries the pre-2020 name; the college's own page records the April 2020 rename to Edmonds College"),
    "ORG-004625": ("01j933b41", WSU_RENAME, "Wichita Area Technical College",
                   "ROR carries the pre-2018 name; the college's own page says 'WSU Tech, formerly Wichita Area Technical College'"),
}
HOLD = {
    "ORG-002779": "ROR record 01ky71w68 (Penn State Behrend) is withdrawn; its successor is 04p491231 Pennsylvania State "
                  "University, the parent. A campus never carries the parent's ROR (V-14), so no ROR id.",
    "ORG-002780": "Pennsylvania College of Technology has no ROR record: name searches return other schools "
                  "(ROR 'Penn College' 03m7qwy32 is William Penn University, Oskaloosa IA).",
    "ORG-004635": "The Landing School has no ROR record (name search returns only unrelated design schools).",
    "ORG-004672": "Connecticut State Community College (the 2023 merger of 12 colleges) has no ROR record; the crosswalk "
                  "candidate 014a8dd26 is Capital Community College, one of the merged colleges, not the same organization.",
    "ORG-004777": "ROR has Rutgers University (05vt9qd57) but no Camden campus record; the parent's ROR is not a campus's.",
    "ORG-004778": "ROR has Rutgers University (05vt9qd57) but no New Brunswick campus record; the parent's ROR is not a campus's.",
    "ORG-004779": "ROR has Rutgers University (05vt9qd57) but no Newark campus record; the parent's ROR is not a campus's.",
}
EDIT_COLS = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]
EVD_COLS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
            "observed_date", "tier_effect", "created_by", "notes"]
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    data = Path(ap.parse_args().data_dir)
    eco = {r["org_id"]: r for r in csv.DictReader(open(data / "ecosystem.csv", encoding="utf-8"))}
    held = {r["ror_id"] for r in eco.values() if r["ror_id"]}
    evd = max(int(re.sub(r"\D", "", r["evidence_id"])) for f in glob.glob(str(data / "evidence_*.csv"))
              for r in csv.DictReader(open(f, encoding="utf-8")))
    holds = list(csv.DictReader(open(ROOT / "tasks" / "programs-db-crosswalk-2026-11-03" / "holds.csv", encoding="utf-8")))
    assert {h["org_id"] for h in holds} == set(MINT) | set(HOLD), "every hold gets exactly one verdict"
    edits, evidence, verdicts = [], [], []
    for oid, (ror, rename, ror_name, why) in MINT.items():
        r, url = eco[oid], "https://ror.org/" + ror
        assert not r["ror_id"] and url not in held, (oid, "already linked or ROR id already held")
        edits.append({"file": "ecosystem.csv", "row_id": oid, "column": "ror_id", "old_sha256": sha(r["ror_id"]),
                      "new_value": url, "edit_class": "ROR_LINK",
                      "rationale": f"ROR hold resolved at api.ror.org {TODAY}: {ror_name} ({ror}); {why}"})
        add = [url] + ([rename] if rename else [])
        edits.append({"file": "ecosystem.csv", "row_id": oid, "column": "sources", "old_sha256": sha(r["sources"]),
                      "new_value": "; ".join([r["sources"].strip()] + add) if r["sources"].strip() else "; ".join(add),
                      "edit_class": "ROR_LINK_SOURCE", "rationale": "cite the ROR record behind ror_id"
                      + (" and the institution's own rename page" if rename else "")})
        if rename:
            evd += 1
            evidence.append({"evidence_id": f"EVD-{evd:06d}", "record_table": "ecosystem", "record_id": oid,
                             "claim_type": "existence",
                             "claim_detail": f"{r['legal_name']} is the institution ROR {ror} records under its former name "
                                             f"'{ror_name}'; the institution's own page states the rename.",
                             "source_class": "own_site", "source_ref": rename, "observed_date": TODAY,
                             "tier_effect": "supports_B", "created_by": BY,
                             "notes": "identity link for ror_id (former name in ROR); the record's tier is unchanged"})
        verdicts.append({"org_id": oid, "legal_name": r["legal_name"], "verdict": "LINKED", "ror_id": url, "reason": why})
    for oid, why in HOLD.items():
        verdicts.append({"org_id": oid, "legal_name": eco[oid]["legal_name"], "verdict": "HOLD", "ror_id": "", "reason": why})
    for name, cols, rows in (("edits.csv", EDIT_COLS, edits), ("evidence_append.csv", EVD_COLS, evidence),
                             ("verdicts.csv", ["org_id", "legal_name", "verdict", "ror_id", "reason"], verdicts)):
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"linked {len(MINT)}, held {len(HOLD)}; edits {len(edits)}, evidence rows {len(evidence)}")


if __name__ == "__main__":
    main()
