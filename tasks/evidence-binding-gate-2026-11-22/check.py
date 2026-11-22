#!/usr/bin/env python3
"""Regenerate every number in this folder's README from pinned commits, and fail if any differs.

Pinned refs: main at the branch cut (8f30ce0f); the two quarantined integration batches as the rows PR #457 and
PR #458 added (4ee02127 -> 17834918). Labels for the spotcheck calibration (S/reviews/w1122-spotcheck.md, Appendices A
and B) are carried by evidence_id only, never quote text. Writes notes_name_rows.csv (the owner list) beside itself.

Usage: python3 tasks/evidence-binding-gate-2026-11-22/check.py [--first-cut PATH/verdicts.csv]
  --first-cut  the controller's first-cut verdicts.csv (outside the repo); adds the reconciliation table.
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
import check_evidence_binding as b  # noqa: E402

MAIN, BATCH_BASE, BATCH_HEAD = "8f30ce0f", "4ee02127", "17834918"
APPENDIX_A = {"EVD-431206": "CANNOT_TELL", "EVD-430188": "DIFFERENT_ADDRESS", "EVD-427648": "DIFFERENT_ADDRESS", "EVD-431826": "DIFFERENT_ADDRESS", "EVD-429348": "DIFFERENT_ADDRESS", "EVD-432372": "DIFFERENT_ADDRESS", "EVD-431544": "DIFFERENT_ADDRESS", "EVD-425964": "DIFFERENT_ADDRESS", "EVD-426070": "DIFFERENT_ADDRESS", "EVD-431900": "CANNOT_TELL", "EVD-429356": "DIFFERENT_ADDRESS", "EVD-434334": "DIFFERENT_ADDRESS", "EVD-425566": "DIFFERENT_ADDRESS", "EVD-426904": "DIFFERENT_ADDRESS", "EVD-429620": "DIFFERENT_ADDRESS", "EVD-430124": "DIFFERENT_ADDRESS", "EVD-432898": "DIFFERENT_ADDRESS", "EVD-430102": "DIFFERENT_ADDRESS", "EVD-427536": "DIFFERENT_ADDRESS", "EVD-431964": "DIFFERENT_ADDRESS", "EVD-429062": "DIFFERENT_ADDRESS", "EVD-428624": "SAME_PLACE", "EVD-429422": "DIFFERENT_ADDRESS", "EVD-430448": "DIFFERENT_ADDRESS", "EVD-427956": "DIFFERENT_ADDRESS", "EVD-432662": "DIFFERENT_ADDRESS", "EVD-432758": "DIFFERENT_ADDRESS", "EVD-434376": "DIFFERENT_ADDRESS", "EVD-430300": "DIFFERENT_ADDRESS", "EVD-429950": "DIFFERENT_ADDRESS", "EVD-435460": "DIFFERENT_ADDRESS", "EVD-428370": "DIFFERENT_ADDRESS", "EVD-428802": "DIFFERENT_ADDRESS", "EVD-426602": "CANNOT_TELL", "EVD-434936": "DIFFERENT_ADDRESS", "EVD-435244": "DIFFERENT_ADDRESS", "EVD-429388": "DIFFERENT_ADDRESS", "EVD-433872": "CANNOT_TELL", "EVD-430308": "DIFFERENT_ADDRESS", "EVD-429120": "DIFFERENT_ADDRESS", "EVD-431512": "DIFFERENT_ADDRESS", "EVD-431466": "DIFFERENT_ADDRESS", "EVD-427406": "DIFFERENT_ADDRESS", "EVD-434052": "DIFFERENT_ADDRESS", "EVD-431968": "DIFFERENT_ADDRESS", "EVD-431076": "CANNOT_TELL", "EVD-428318": "DIFFERENT_ADDRESS", "EVD-431352": "DIFFERENT_ADDRESS", "EVD-427348": "DIFFERENT_ADDRESS", "EVD-434836": "DIFFERENT_ADDRESS", "EVD-427280": "DIFFERENT_ADDRESS", "EVD-434024": "DIFFERENT_ADDRESS", "EVD-431524": "DIFFERENT_ADDRESS", "EVD-429428": "DIFFERENT_ADDRESS", "EVD-428032": "DIFFERENT_ADDRESS", "EVD-426068": "DIFFERENT_ADDRESS", "EVD-426334": "DIFFERENT_ADDRESS", "data/evidence_sites_VA.csv:417": "DIFFERENT_ADDRESS", "EVD-428870": "DIFFERENT_ADDRESS", "EVD-429916": "DIFFERENT_ADDRESS"}  # noqa: E501
APPENDIX_B = {"EVD-443796": "MATCH", "EVD-442346": "MATCH", "EVD-439366": "MATCH", "EVD-449620": "DEFECT", "EVD-440898": "MATCH", "EVD-447490": "MATCH", "EVD-436578": "MATCH", "EVD-442068": "MATCH", "EVD-448086": "MATCH", "EVD-438364": "MATCH", "EVD-444906": "MATCH", "EVD-449054": "MATCH", "EVD-450226": "MATCH", "EVD-450128": "DEFECT", "EVD-445324": "MATCH", "EVD-450336": "MATCH", "EVD-447830": "MATCH", "EVD-446818": "MATCH", "EVD-448254": "MATCH", "EVD-449402": "MATCH", "EVD-446086": "MATCH", "EVD-454689": "MATCH", "EVD-454304": "MATCH", "EVD-454414": "MATCH", "EVD-453992": "MATCH", "EVD-454525": "MATCH", "EVD-454479": "MATCH", "EVD-457497": "MATCH", "EVD-456335": "MATCH", "EVD-457493": "DEFECT", "EVD-455899": "DEFECT", "EVD-457589": "DEFECT", "EVD-456891": "MATCH", "EVD-428884": "MATCH", "EVD-432074": "MATCH", "EVD-427874": "MATCH", "EVD-431182": "MATCH", "EVD-435496": "MATCH", "EVD-427788": "MATCH", "EVD-434612": "MATCH"}  # noqa: E501
EXPECTED = {
    'alt_would_pass.facility_label': 154,
    'alt_would_pass.leading_run': 1829,
    'alt_would_pass.notes': 868,
    'alt_would_pass.parent': 46,
    'alt_would_pass.spacing': 142,
    'alt_would_pass.token_subset': 2409,
    'appendix_A.CANNOT_TELL->FAIL': 5,
    'appendix_A.DIFFERENT_ADDRESS->FAIL': 54,
    'appendix_A.SAME_PLACE->PASS': 1,
    'appendix_B.DEFECT->FAIL': 5,
    'appendix_B.MATCH->FAIL': 8,
    'appendix_B.MATCH->PASS': 27,
    'batches.FAIL': 12871,
    'batches.PASS': 20733,
    'batches.UNINSPECTABLE': 490,
    'batches.rows': 34094,
    'batches.spaghetti-batch5-2026-11-22.FAIL': 3354,
    'batches.spaghetti-batch5-2026-11-22.PASS': 6808,
    'batches.spaghetti-batch5-2026-11-22.UNINSPECTABLE': 190,
    'batches.spaghetti-batch6-2026-11-22.FAIL': 9517,
    'batches.spaghetti-batch6-2026-11-22.PASS': 13925,
    'batches.spaghetti-batch6-2026-11-22.UNINSPECTABLE': 122,
    'batches.spaghetti-burndown-batch1-2026-11-21.UNINSPECTABLE': 122,
    'batches.spaghetti-burndown-batch2-2026-11-21.UNINSPECTABLE': 56,
    'hq_s5_would_pass.FMCSA Company Census': 284,
    'hq_s5_would_pass.state-entity-files-bulk': 343,
    'main_all.FAIL': 12871,
    'main_all.PASS': 20733,
    'main_all.UNINSPECTABLE': 47906,
    'main_all.rows': 81510,
    'main_without_batches.UNINSPECTABLE': 47416,
    'main_without_batches.rows': 47416,
    'notes_rows': 982,
    'shifted_if_facility.FAIL name_not_held': 4,
    'shifted_if_facility.PASS': 94,
    'street_limit.different_number': 934,
    'street_limit.same_street_other_number': 236,
    'pass_site_city_not_in_quote': 242,
    'street_limit.number_in_recorded_range': 14,
    'street_limit.number_word': 92,
    'street_limit.same_number_other': 1274,
    'street_limit.same_number_token_subset': 1552,
}  # regenerate by emptying this dict and re-running


def table(results, key="verdict"):
    return Counter(r[key] for r in results)


def show(title, counter, total=None):
    total = total if total is not None else sum(counter.values())
    print(f"\n{title} (n={total})")
    for k, n in counter.most_common():
        print(f"  {n:7d}  {100 * n / total:5.1f}%  {k or '-'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first-cut", help="controller's first-cut verdicts.csv")
    a = ap.parse_args()
    got = {}

    main_evs = b.rows(MAIN, "evidence_*.csv")
    main_res = b.judge_all(main_evs, b.Index.load(MAIN))
    assert len(main_res) == len(main_evs) == len({e["evidence_id"] for e in main_evs})
    q_evs = b.changed_rows(b.rows(BATCH_BASE, "evidence_*.csv"), b.rows(BATCH_HEAD, "evidence_*.csv"))
    q_res = b.judge_all(q_evs, b.Index.load(BATCH_HEAD))
    q_ids = {r["evidence_id"] for r in q_res}
    rest = [r for r in main_res if r["evidence_id"] not in q_ids]

    for name, res in (("main_all", main_res), ("main_without_batches", rest), ("batches", q_res)):
        show(f"{name}: verdict", table(res))
        got.update({f"{name}.{k}": v for k, v in table(res).items()})
        got[f"{name}.rows"] = len(res)
    for label, c in sorted(defaultdict(Counter, {k: table([r for r in q_res if r["created_by"] == k])
                                                  for k in {r["created_by"] for r in q_res}}).items()):
        show(f"batches, created_by {label}", c)
        got.update({f"batches.{label}.{k}": v for k, v in c.items()})
    show("batches: FAIL and UNINSPECTABLE by reason", table([r for r in q_res if r["verdict"] != "PASS"], "reason"))
    fam = defaultdict(Counter)
    for r in q_res:
        fam[r["source_family"]][r["verdict"]] += 1
    print("\nbatches by source family (PASS / FAIL / UNINSPECTABLE)")
    for k, c in sorted(fam.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {sum(c.values()):6d}  {c['PASS']:6d} / {c['FAIL']:6d} / {c['UNINSPECTABLE']:6d}  {k}")

    # owner questions: what each alternative reading would pass (measured on the batches; nothing here passes)
    name_fail = [r for r in q_res if "name_not_held" in r["reason"]]
    alts = Counter(x for r in name_fail for x in r["name_alt"].split(";") if x)
    show("batches: name_not_held rows by alternative basis (a row may have several)", alts, len(name_fail))
    only_name = [r for r in q_res if r["reason"] == "name_not_held"]
    for basis in ("leading_run", "facility_label", "parent", "notes", "spacing", "token_subset"):
        n = sum(basis in r["name_alt"].split(";") for r in only_name)
        got[f"alt_would_pass.{basis}"] = n
        print(f"  would PASS if {basis} counted (row's only defect is the name): {n}")
    notes_rows = [r for r in name_fail if "notes" in r["name_alt"].split(";")]
    got["notes_rows"] = len(notes_rows)
    with open(HERE / "notes_name_rows.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["evidence_id", f"path_line_at_{BATCH_HEAD}", "record_table", "record_id", "reason", "name_alt"])
        for r in notes_rows:
            w.writerow([r["evidence_id"], r["at"], r["record_table"], r["record_id"], r["reason"], r["name_alt"]])
    lim = defaultdict(list)
    for r in q_res:
        if "street_differs" in r["reason"]:
            lim[r["street_limit"] or "different_number"].append(r["evidence_id"])
    print("\nbatches: street_differs rows by street_key limit class (examples by evidence_id)")
    for k, ids in sorted(lim.items(), key=lambda kv: -len(kv[1])):
        got[f"street_limit.{k}"] = len(ids)
        print(f"  {len(ids):6d}  {k:26s} {', '.join(ids[:4])}")
    pass_sites = [r for r in q_res if r["verdict"] == "PASS" and r["record_table"] == "sites"]
    cnq = [r["evidence_id"] for r in pass_sites if r["city_not_in_quote"]]
    got["pass_site_city_not_in_quote"] = len(cnq)
    print(f"\nbatches: site PASS rows whose quote does not print the record's city: {len(cnq)} of {len(pass_sites)} "
          f"(e.g. {', '.join(cnq[:4])})")
    hq = [r for r in q_res if r["record_table"] != "sites" and r["claim_type"] == "address"]
    hqc = Counter((r["source_family"], r["reason"] or "PASS") for r in hq)
    print("\nbatches: organization address rows by source family and verdict reason")
    for (f_, why), n in hqc.most_common():
        print(f"  {n:6d}  {f_:28s} {why}")
    s5_only = Counter(r["source_family"] for r in hq if r["reason"] == "hq_from_s5_identity_source")
    got.update({f"hq_s5_would_pass.{k}": v for k, v in s5_only.items()})
    shifted = Counter(r["if_facility_operator"] for r in q_res if r["reason"] == "operator_not_a_name")
    show("batches: shifted-column rows if the facility label were the operator", shifted)
    got.update({f"shifted_if_facility.{k}": v for k, v in shifted.items()})

    # calibration against the spotcheck's labelled draws
    by_id = {r["evidence_id"]: r for r in q_res}
    by_at = {r["at"]: r for r in q_res}
    for name, labels in (("appendix_A", APPENDIX_A), ("appendix_B", APPENDIX_B)):
        c = Counter((lab, (by_id.get(k) or by_at.get(k) or {"verdict": "MISSING"})["verdict"]) for k, lab in labels.items())
        show(f"calibration {name}: (spotcheck label, gate verdict)", Counter({f"{x} -> {y}": n for (x, y), n in c.items()}))
        got.update({f"{name}.{x}->{y}": n for (x, y), n in c.items()})

    if a.first_cut:
        fc = {r["evidence_id"]: r["verdict"] for r in csv.DictReader(open(a.first_cut, encoding="utf-8"))}
        head_res = {r["evidence_id"]: r for r in b.judge_all(b.rows(BATCH_HEAD, "evidence_*.csv"),
                                                             b.Index.load(BATCH_HEAD))}
        missing = [k for k in fc if k not in head_res]
        assert not missing, f"{len(missing)} first-cut rows absent at {BATCH_HEAD}"
        cross = Counter((fc[k].split("_")[0] if fc[k].startswith(("FAIL", "FREETEXT")) else fc[k],
                         head_res[k]["verdict"]) for k in fc)
        show(f"first cut ({len(fc)} rows at {BATCH_HEAD}) -> this gate", Counter({f"{x} -> {y}": n for (x, y), n in
                                                                               cross.items()}))
        fb = [k for k in fc if k in q_ids]
        n_fail = sum(fc[k].startswith("FAIL") for k in fb)
        print(f"  first cut FAIL share on the batch rows: {n_fail}/{len(fb)} = {100 * n_fail / len(fb):.1f}%")

    bad = {k: (EXPECTED.get(k), v) for k, v in got.items() if EXPECTED and EXPECTED.get(k) != v}
    bad.update({k: (v, None) for k, v in EXPECTED.items() if k not in got})
    if not EXPECTED:
        print("\nEXPECTED = " + repr(dict(sorted(got.items()))))
        return 0
    for k, (want, have) in sorted(bad.items()):
        print(f"MISMATCH {k}: README says {want}, now {have}")
    print(f"\ncheck: {'FAIL' if bad else 'OK'} ({len(got)} numbers compared)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
