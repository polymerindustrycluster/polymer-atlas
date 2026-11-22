#!/usr/bin/env python3
"""Regenerate every number in this folder's README from pinned commits, and fail if any differs.

Pinned refs: main at the branch cut (8f30ce0f, still holding the batches); main after the batches were withdrawn
and #463 landed (393c3895); the two quarantined integration batches as the rows PR #457 and PR #458 added
(4ee02127 -> 17834918). Labels for the spotcheck calibration (S/reviews/w1122-spotcheck.md, Appendices A
and B) are carried by evidence_id only, never quote text. Writes notes_name_rows.csv (the owner list) beside itself.

Usage: python3 tasks/evidence-binding-gate-2026-11-22/check.py [--first-cut PATH/verdicts.csv]
  --first-cut  the controller's first-cut verdicts.csv (outside the repo); adds the reconciliation table.
"""
import argparse
import ast
import csv
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
import check_evidence_binding as b  # noqa: E402

MAIN, CURRENT, BATCH_BASE, BATCH_HEAD = "8f30ce0f", "393c3895", "4ee02127", "17834918"
APPENDIX_A = {"EVD-431206": "CANNOT_TELL", "EVD-430188": "DIFFERENT_ADDRESS", "EVD-427648": "DIFFERENT_ADDRESS", "EVD-431826": "DIFFERENT_ADDRESS", "EVD-429348": "DIFFERENT_ADDRESS", "EVD-432372": "DIFFERENT_ADDRESS", "EVD-431544": "DIFFERENT_ADDRESS", "EVD-425964": "DIFFERENT_ADDRESS", "EVD-426070": "DIFFERENT_ADDRESS", "EVD-431900": "CANNOT_TELL", "EVD-429356": "DIFFERENT_ADDRESS", "EVD-434334": "DIFFERENT_ADDRESS", "EVD-425566": "DIFFERENT_ADDRESS", "EVD-426904": "DIFFERENT_ADDRESS", "EVD-429620": "DIFFERENT_ADDRESS", "EVD-430124": "DIFFERENT_ADDRESS", "EVD-432898": "DIFFERENT_ADDRESS", "EVD-430102": "DIFFERENT_ADDRESS", "EVD-427536": "DIFFERENT_ADDRESS", "EVD-431964": "DIFFERENT_ADDRESS", "EVD-429062": "DIFFERENT_ADDRESS", "EVD-428624": "SAME_PLACE", "EVD-429422": "DIFFERENT_ADDRESS", "EVD-430448": "DIFFERENT_ADDRESS", "EVD-427956": "DIFFERENT_ADDRESS", "EVD-432662": "DIFFERENT_ADDRESS", "EVD-432758": "DIFFERENT_ADDRESS", "EVD-434376": "DIFFERENT_ADDRESS", "EVD-430300": "DIFFERENT_ADDRESS", "EVD-429950": "DIFFERENT_ADDRESS", "EVD-435460": "DIFFERENT_ADDRESS", "EVD-428370": "DIFFERENT_ADDRESS", "EVD-428802": "DIFFERENT_ADDRESS", "EVD-426602": "CANNOT_TELL", "EVD-434936": "DIFFERENT_ADDRESS", "EVD-435244": "DIFFERENT_ADDRESS", "EVD-429388": "DIFFERENT_ADDRESS", "EVD-433872": "CANNOT_TELL", "EVD-430308": "DIFFERENT_ADDRESS", "EVD-429120": "DIFFERENT_ADDRESS", "EVD-431512": "DIFFERENT_ADDRESS", "EVD-431466": "DIFFERENT_ADDRESS", "EVD-427406": "DIFFERENT_ADDRESS", "EVD-434052": "DIFFERENT_ADDRESS", "EVD-431968": "DIFFERENT_ADDRESS", "EVD-431076": "CANNOT_TELL", "EVD-428318": "DIFFERENT_ADDRESS", "EVD-431352": "DIFFERENT_ADDRESS", "EVD-427348": "DIFFERENT_ADDRESS", "EVD-434836": "DIFFERENT_ADDRESS", "EVD-427280": "DIFFERENT_ADDRESS", "EVD-434024": "DIFFERENT_ADDRESS", "EVD-431524": "DIFFERENT_ADDRESS", "EVD-429428": "DIFFERENT_ADDRESS", "EVD-428032": "DIFFERENT_ADDRESS", "EVD-426068": "DIFFERENT_ADDRESS", "EVD-426334": "DIFFERENT_ADDRESS", "data/evidence_sites_VA.csv:417": "DIFFERENT_ADDRESS", "EVD-428870": "DIFFERENT_ADDRESS", "EVD-429916": "DIFFERENT_ADDRESS"}  # noqa: E501
APPENDIX_B = {"EVD-443796": "MATCH", "EVD-442346": "MATCH", "EVD-439366": "MATCH", "EVD-449620": "DEFECT", "EVD-440898": "MATCH", "EVD-447490": "MATCH", "EVD-436578": "MATCH", "EVD-442068": "MATCH", "EVD-448086": "MATCH", "EVD-438364": "MATCH", "EVD-444906": "MATCH", "EVD-449054": "MATCH", "EVD-450226": "MATCH", "EVD-450128": "DEFECT", "EVD-445324": "MATCH", "EVD-450336": "MATCH", "EVD-447830": "MATCH", "EVD-446818": "MATCH", "EVD-448254": "MATCH", "EVD-449402": "MATCH", "EVD-446086": "MATCH", "EVD-454689": "MATCH", "EVD-454304": "MATCH", "EVD-454414": "MATCH", "EVD-453992": "MATCH", "EVD-454525": "MATCH", "EVD-454479": "MATCH", "EVD-457497": "MATCH", "EVD-456335": "MATCH", "EVD-457493": "DEFECT", "EVD-455899": "DEFECT", "EVD-457589": "DEFECT", "EVD-456891": "MATCH", "EVD-428884": "MATCH", "EVD-432074": "MATCH", "EVD-427874": "MATCH", "EVD-431182": "MATCH", "EVD-435496": "MATCH", "EVD-427788": "MATCH", "EVD-434612": "MATCH"}  # noqa: E501
EXPECTED = {
    'alt_would_pass.comma_part': 142,
    'alt_would_pass.facility_label': 156,
    'alt_would_pass.leading_run': 1969,
    'alt_would_pass.notes': 824,
    'alt_would_pass.parent': 44,
    'alt_would_pass.spacing': 138,
    'alt_would_pass.token_subset': 2527,
    'appendix_A.CANNOT_TELL->FAIL': 5,
    'appendix_A.DIFFERENT_ADDRESS->FAIL': 54,
    'appendix_A.SAME_PLACE->PASS': 1,
    'appendix_B.DEFECT->FAIL': 5,
    'appendix_B.MATCH->FAIL': 9,
    'appendix_B.MATCH->PASS': 26,
    'batches.FAIL': 13029,
    'batches.PASS': 20577,
    'batches.READ_REQUIRED': 344,
    'batches.UNINSPECTABLE': 144,
    'batches.needs_proof_line': 488,
    'batches.needs_proof_line_with_archive_link': 344,
    'batches.rows': 34094,
    'batches.spaghetti-batch5-2026-11-22.FAIL': 3374,
    'batches.spaghetti-batch5-2026-11-22.PASS': 6792,
    'batches.spaghetti-batch5-2026-11-22.READ_REQUIRED': 176,
    'batches.spaghetti-batch5-2026-11-22.UNINSPECTABLE': 10,
    'batches.spaghetti-batch6-2026-11-22.FAIL': 9645,
    'batches.spaghetti-batch6-2026-11-22.PASS': 13785,
    'batches.spaghetti-batch6-2026-11-22.UNINSPECTABLE': 134,
    'batches.spaghetti-burndown-batch1-2026-11-21.FAIL': 6,
    'batches.spaghetti-burndown-batch1-2026-11-21.READ_REQUIRED': 116,
    'batches.spaghetti-burndown-batch2-2026-11-21.FAIL': 4,
    'batches.spaghetti-burndown-batch2-2026-11-21.READ_REQUIRED': 52,
    'current_main.FAIL': 218,
    'current_main.READ_REQUIRED': 2765,
    'current_main.UNINSPECTABLE': 44433,
    'current_main.needs_proof_line': 47198,
    'current_main.needs_proof_line_with_archive_link': 6735,
    'current_main.rows': 47416,
    'fail_state_differs': 0,
    'hq_s5_would_pass.FMCSA Company Census': 284,
    'hq_s5_would_pass.state-entity-files-bulk': 343,
    'main_all.FAIL': 13247,
    'main_all.PASS': 20577,
    'main_all.READ_REQUIRED': 3109,
    'main_all.UNINSPECTABLE': 44577,
    'main_all.rows': 81510,
    'main_without_batches.FAIL': 218,
    'main_without_batches.READ_REQUIRED': 2765,
    'main_without_batches.UNINSPECTABLE': 44433,
    'main_without_batches.rows': 47416,
    'mutant.comma_split_names.caught': True,
    'mutant.edit_some_columns.caught': True,
    'mutant.hq_from_any_source.caught': True,
    'mutant.no_state_test.caught': True,
    'mutant.no_unit_test.caught': True,
    'mutant.number_only_streets.caught': True,
    'mutant.proof_any_archive_ref.caught': True,
    'mutant.proof_digest_form.caught': True,
    'mutant.proof_no_index_line.caught': True,
    'mutant.proof_no_quote_ok.caught': True,
    'mutant.proof_quote_unchecked.caught': True,
    'mutant.proof_same_family.caught': True,
    'mutant.proof_width.caught': True,
    'mutant.provenance_borrowed_folder.caught': True,
    'mutant.provenance_not_run.caught': True,
    'mutant.token_subset_names.caught': True,
    'mutant.web_any_domain.caught': True,
    'mutant.web_any_suffix.caught': True,
    'mutant.web_civic_only.caught': True,
    'mutant.web_name_unchecked.caught': True,
    'mutant.web_no_unit_test.caught': True,
    'mutant.web_pass.caught': True,
    'mutant.web_platform_as_domain.caught': True,
    'notes_rows': 934,
    'pass_basis.org': 18259,
    'pass_basis.site_name_lead': 1320,
    'pass_basis.site_name_other': 998,
    'pass_site_city_not_in_quote': 238,
    'people.no_quote/institution_has_no_website': 35,
    'people.no_quote/off_institution_domain': 23,
    'people.no_quote/on_institution_domain': 676,
    'shifted_if_facility.FAIL name_not_held': 8,
    'shifted_if_facility.PASS': 90,
    'street_limit.different_number': 924,
    'street_limit.number_in_recorded_range': 14,
    'street_limit.number_word': 92,
    'street_limit.same_number_other': 1270,
    'street_limit.same_number_token_subset': 1528,
    'street_limit.same_street_other_number': 236,
    'test_segments_leaked': 0,
    'web.PASS': 0,
    'web.not_own_site.name_in_host': 60,
    'web.street_absent.spacing': 20,
    'web_batch1_4.FAIL not_own_site': 101,
    'web_batch1_4.FAIL street_absent_from_quote': 104,
    'web_batch1_4.FAIL street_absent_from_quote+not_own_site': 5,
    'web_batch1_4.FAIL unit_differs+not_own_site': 2,
    'web_batch1_4.READ_REQUIRED mechanics_clear': 1541,
    'web_batch1_4.READ_REQUIRED name_absent_from_quote': 8,
    'web_batch1_4.READ_REQUIRED no_record_website': 181,
    'web_batch1_4.READ_REQUIRED record_street_no_civic_number': 8,
    'web_batch1_4.READ_REQUIRED web_class_untested': 80,
    'web_batch1_4.READ_REQUIRED web_record_no_street': 638,
    'web_batch1_4.rows': 2668,
    'web_other.FAIL not_own_site': 3,
    'web_other.FAIL street_absent_from_quote': 3,
    'web_other.READ_REQUIRED mechanics_clear': 276,
    'web_other.READ_REQUIRED no_record_website': 2,
    'web_other.READ_REQUIRED web_class_untested': 31,
    'web_other.rows': 315,
}  # regenerate by emptying this dict and re-running


TESTS = HERE.parents[1] / "scripts" / "test_check_evidence_binding.py"
BOILERPLATE = re.compile(r"^(?:synthetic claim|existence|naics|sic|status|program|permit_number|county|source_record_key|frs "
                         r"registry|rcrainfo handler|entity_type|dba name|award_count|recipient_uei|uei|ectypes)", re.I)
MUTANTS = {  # name: (file, original fragment, loosened replacement); each must make the planted-defect tests fail
    "token_subset_names": ("g", "    if not qkeys & held:\n", "    if not any(set(q.split()) <= set(h.split()) or "
                           "set(h.split()) <= set(q.split()) for q in qkeys for h in held):\n"),
    "comma_split_names": ("g", 'return {k for n in names for k in (name_key(n), name_key(PAREN_RE.sub(" ", n))) if k}',
                          'return {k for n in names for x in n.split(",") for k in (name_key(x),) if k}'),
    "number_only_streets": ("g", '    if rk != qk:\n        return "street_differs"',
                            '    if rk.split()[:1] != qk.split()[:1]:\n        return "street_differs"'),
    "no_unit_test": ("m", "    return not (ua and ub and ua != ub)", "    return True"),
    "no_state_test": ("g", '        if q_st in STATE_NAMES.values() and rec.get("state")',
                      '        if False and rec.get("state")'),
    "hq_from_any_source": ("g", '        if basis == "facility":', '        if False:'),
    "web_pass": ("g", '    return "READ_REQUIRED", why or "mechanics_clear", info',
                 '    return ("READ_REQUIRED", why, info) if why else ("PASS", "", info)'),
    "web_any_domain": ("g", "        elif not any(own_domain(src, w) for w in sites):", "        elif False:"),
    "web_platform_as_domain": ("g", "    if on_platform(sh) or on_platform(wh):", "    if False:"),
    "web_civic_only": ("g", "if x == num and (street_at(i + 1) or (", "if x == num and (True or ("),
    "web_any_suffix": ("g", "return q[j:j + 1] == words[:1] and not (k and", "return q[j:j + 1] == words[:1] and not (False and"),
    "web_no_unit_test": ("g", '    return "unit_differs" if all(conflicts(i) for i in hits) else ""', '    return ""'),
    "web_name_unchecked": ("g", '        if not any(f" {k} " in q for k in idx.held_keys(table, ev["record_id"])):',
                           "        if False:"),
    "edit_some_columns": ("g", '        return {k: v for k, v in e.items() if k != "_at" and v}',
                          '        return {k: v for k, v in e.items() if k in ("record_id", "claim_detail") and v}'),
    "proof_quote_unchecked": ("g", "    if capture_text(data)[off:off + n] != quote:", "    if False:"),
    "proof_any_archive_ref": ("g", "        if cap != archive_ref:", "        if False:"),
    "proof_no_index_line": ("g", '        if not archive_ref:\n            return "no data', '        if False:\n            return "no data'),
    "proof_no_quote_ok": ("g", "    if not quote:\n", "    if False:\n"),
    "proof_same_family": ("g", "    if rf == builder:", "    if False:"),
    "proof_digest_form": ("g", 'if not re.fullmatch(r"[0-9a-f]{64}", sha) or len(set(sha)) == 1:', "if False:"),
    "proof_width": ("g", "        if len(row) != len(PROOF_COLS):", "        if False:"),
    "provenance_borrowed_folder": ("g", "        elif label not in base_labels and base_has_folder(folder):", "        elif False:"),
    "provenance_not_run": ("g", "        if code != 0:", "        if False:"),
}
BATCH14 = re.compile(r"^spaghetti-(burndown-batch[1-4]|drift-rewitness|nourl-cleared)-")  # the 2,846 burn-down web rows
PEOPLE_LABEL = "spaghetti evidence-backfill-w1-2026-11-19"


def test_segments():
    """Every comma/semicolon segment (10+ chars, not field boilerplate) of every string literal in the test file."""
    lits = [n.value for n in ast.walk(ast.parse(TESTS.read_text(encoding="utf-8")))
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    segs = {x.strip() for lit in lits for x in re.split(r"[;,]", lit)}
    return {x for x in segs if len(x) >= 10 and not BOILERPLATE.match(x) and " " in x  # street-, ID- or name-like
            and (re.search(r"\d", x) or len(x.split()) >= 3) and x != "permittee: 3"}  # the defect pattern itself


def leaked(segments, blob):
    return sorted(x for x in segments if x.lower() in blob)


def run_mutants():
    """Copy the gate and its tests, loosen one rule per copy, and return {mutant: failing test count}."""
    caught = {}
    target = {"g": "check_evidence_binding.py", "m": "matching.py"}
    for name, (where, old, new) in MUTANTS.items():
        with tempfile.TemporaryDirectory() as d:
            for f in ("check_evidence_binding.py", "test_check_evidence_binding.py", "matching.py"):
                text = (HERE.parents[1] / "scripts" / f).read_text(encoding="utf-8")
                text = text.replace("ROOT = Path(__file__).resolve().parents[1]", f"ROOT = Path({str(HERE.parents[1])!r})")
                text = text.replace('sys.path.insert(0, str(ROOT / "scripts"))', 'sys.path.insert(1, str(ROOT / "scripts"))')
                text = text.replace("sys.path.insert(0, str(Path(__file__).resolve().parent))",
                                    f"sys.path.insert(1, {str(HERE.parents[1] / 'scripts')!r})")
                if f == target[where]:
                    assert text.count(old) == 1, f"mutant {name}: anchor not found once"
                    text = text.replace(old, new)
                (Path(d) / f).write_text(text, encoding="utf-8")
            out = subprocess.run([sys.executable, "-m", "unittest", "test_check_evidence_binding.Verdicts",
                                  "test_check_evidence_binding.Proofs", "test_check_evidence_binding.GateMechanics"],
                                 cwd=d, capture_output=True, text=True).stderr
            assert re.search(r"^Ran \d+ tests", out, re.M), f"mutant {name}: the tests did not run\n{out[-2000:]}"
            caught[name] = len(re.findall(r"^(?:FAIL|ERROR): ", out, re.M))
    return caught


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

    cur_evs = b.rows(CURRENT, "evidence_*.csv")
    cur_res = b.judge_all(cur_evs, b.Index.load(CURRENT))
    main_evs = b.rows(MAIN, "evidence_*.csv")
    main_res = b.judge_all(main_evs, b.Index.load(MAIN))
    assert len(main_res) == len(main_evs) == len({e["evidence_id"] for e in main_evs})
    q_evs = b.changed_rows(b.rows(BATCH_BASE, "evidence_*.csv"), b.rows(BATCH_HEAD, "evidence_*.csv"))
    q_res = b.judge_all(q_evs, b.Index.load(BATCH_HEAD))
    q_ids = {r["evidence_id"] for r in q_res}
    rest = [r for r in main_res if r["evidence_id"] not in q_ids]

    for name, res in (("current_main", cur_res), ("main_all", main_res), ("main_without_batches", rest),
                      ("batches", q_res)):
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
    print("\nbatches by source family (" + " / ".join(b.VERDICTS) + ")")
    for k, c in sorted(fam.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {sum(c.values()):6d}  " + " / ".join(f"{c[v]:6d}" for v in b.VERDICTS) + f"  {k}")

    # owner questions: what each alternative reading would pass (measured on the batches; nothing here passes)
    name_fail = [r for r in q_res if "name_not_held" in r["reason"]]
    alts = Counter(x for r in name_fail for x in r["name_alt"].split(";") if x)
    show("batches: name_not_held rows by alternative basis (a row may have several)", alts, len(name_fail))
    only_name = [r for r in q_res if r["reason"] == "name_not_held"]
    for basis in ("leading_run", "facility_label", "parent", "notes", "spacing", "token_subset", "comma_part"):
        n = sum(basis in r["name_alt"].split(";") for r in only_name)
        got[f"alt_would_pass.{basis}"] = n
        print(f"  would PASS if {basis} counted (row's only defect is the name): {n}")
    notes_rows = [r for r in name_fail if "notes" in r["name_alt"].split(";")]
    got["notes_rows"] = len(notes_rows)
    with open(HERE / "notes_name_rows.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
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
    sd = [r["evidence_id"] for r in q_res if "state_differs" in r["reason"].split("+")]
    got["fail_state_differs"] = len(sd)
    print(f"batches: site rows failing on a quoted state other than the record's: {len(sd)} (e.g. {', '.join(sd[:4])})")
    basis = Counter(r["name_basis"] for r in q_res if r["verdict"] == "PASS")
    show("batches: PASS rows by name basis (quoted form / held name that matched)", basis)
    got.update({f"pass_basis.{k}": v for k, v in basis.items()})
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

    # per-row proof a PR would owe: every READ_REQUIRED or UNINSPECTABLE row; how many have an archive_links capture
    for name, res, ref in (("batches", q_res, BATCH_HEAD), ("current_main", cur_res, CURRENT)):
        archive = {r["evidence_id"] for r in b.rows(ref, "archive_links.csv")}
        un = [r["evidence_id"] for r in res if r["verdict"] not in ("PASS", "FAIL")]
        got[f"{name}.needs_proof_line"] = len(un)
        got[f"{name}.needs_proof_line_with_archive_link"] = sum(e in archive for e in un)
        print(f"\n{name}: {len(un)} rows would need a proof line; {got[f'{name}.needs_proof_line_with_archive_link']} "
              f"of them have a data/archive_links.csv capture")

    # web quotes on main (controller ruling 2026-11-22): the burn-down batch 1-4 family and everything else
    web = [r for r in cur_res if r["source_family"] == "url" and r["reason"] not in ("no_quote", "other_table")]
    for name, res in (("web_batch1_4", [r for r in web if BATCH14.match(r["created_by"])]),
                      ("web_other", [r for r in web if not BATCH14.match(r["created_by"])])):
        show(f"{name}: verdict", table(res))
        show(f"{name}: verdict and reason", Counter(f"{r['verdict']} {r['reason']}".strip() for r in res))
        got[f"{name}.rows"] = len(res)
        got.update({f"{name}.{r}": n for r, n in Counter(f"{r['verdict']} {r['reason']}".strip() for r in res).items()})
        tc = Counter(f"{r['record_table']} {r['claim_type']} {r['verdict']}" for r in res)
        show(f"{name}: record table, claim type, verdict", tc)
    got["web.PASS"] = sum(r["verdict"] == "PASS" for r in web)  # ruling A: must be 0
    got["web.not_own_site.name_in_host"] = sum(r["name_alt"] == "name_in_host" for r in web)
    got["web.street_absent.spacing"] = sum(r["street_limit"] == "spacing" for r in web)
    print(f"web FAIL rows an owner reading would pass: sister domain carrying a held name "
          f"{got['web.not_own_site.name_in_host']}; street present once spacing is ignored {got['web.street_absent.spacing']}")

    # the 734 people rows: no quote, so only the domain test could run; measured against the institution's website
    people = {r["person_id"]: r for r in b.rows(CURRENT, "people.csv")}
    idx = b.Index.load(CURRENT)
    pc = Counter()
    for e in (e for e in cur_evs if e["created_by"].strip() == PEOPLE_LABEL):
        p = people[e["record_id"]]
        inst = b.record_websites(idx, "organizations", idx.orgs.get(p["institution_org_id"]) or {})
        src = b.host_path(e["source_ref"])
        has_quote = bool(e["claim_detail"].partition("quote:")[2].strip())
        pc[("quote" if has_quote else "no_quote") + "/" + ("institution_has_no_website" if not inst else
           "on_institution_domain" if any(b.own_domain(src, w) for w in inst) else "off_institution_domain")] += 1
    show(f"people rows ({PEOPLE_LABEL}): quote and source domain against the institution's website", pc)
    got.update({f"people.{k}": n for k, n in pc.items()})

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

    # no source quote text in the tests (controller instruction 2026-11-22): plant one real fragment and watch it fail
    blob = "\n".join(e["claim_detail"] for e in b.rows(BATCH_HEAD, "evidence_*.csv")).lower()
    segs = test_segments()
    hits = leaked(segs, blob)
    real = next(x.strip() for e in q_evs if "; " in e["claim_detail"] for x in e["claim_detail"].split(";")[1:2])
    assert leaked(segs | {real}, blob), "leak guard failed to catch a planted real fragment"
    print(f"\nleak guard: {len(segs)} test string segments checked against {BATCH_HEAD} claim_detail text; "
          f"{len(hits)} found" + (": " + "; ".join(hits) if hits else ""))
    got["test_segments_leaked"] = len(hits)
    caught = run_mutants()
    print("mutants (planted-defect tests failing when one rule is loosened): " +
          ", ".join(f"{k}={v}" for k, v in caught.items()))
    got.update({f"mutant.{k}.caught": v > 0 for k, v in caught.items()})

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
