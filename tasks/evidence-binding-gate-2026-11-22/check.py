#!/usr/bin/env python3
"""Regenerate every number in this folder's README from pinned commits, and fail if any differs.

Pinned refs: main at the branch cut (8f30ce0f); the two quarantined integration batches as the rows PR #457 and
PR #458 added (4ee02127 -> 17834918). Labels for the spotcheck calibration (S/reviews/w1122-spotcheck.md, Appendices A
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
    'batches.FAIL': 12891,
    'batches.PASS': 20899,
    'batches.UNINSPECTABLE': 304,
    'batches.needs_proof_line': 304,
    'batches.needs_proof_line_with_archive_link': 178,
    'batches.rows': 34094,
    'batches.spaghetti-batch5-2026-11-22.FAIL': 3364,
    'batches.spaghetti-batch5-2026-11-22.PASS': 6870,
    'batches.spaghetti-batch5-2026-11-22.UNINSPECTABLE': 118,
    'batches.spaghetti-batch6-2026-11-22.FAIL': 9517,
    'batches.spaghetti-batch6-2026-11-22.PASS': 13925,
    'batches.spaghetti-batch6-2026-11-22.UNINSPECTABLE': 122,
    'batches.spaghetti-burndown-batch1-2026-11-21.FAIL': 6,
    'batches.spaghetti-burndown-batch1-2026-11-21.PASS': 90,
    'batches.spaghetti-burndown-batch1-2026-11-21.UNINSPECTABLE': 26,
    'batches.spaghetti-burndown-batch2-2026-11-21.FAIL': 4,
    'batches.spaghetti-burndown-batch2-2026-11-21.PASS': 14,
    'batches.spaghetti-burndown-batch2-2026-11-21.UNINSPECTABLE': 38,
    'hq_s5_would_pass.FMCSA Company Census': 284,
    'hq_s5_would_pass.state-entity-files-bulk': 343,
    'main_all.FAIL': 13095,
    'main_all.PASS': 22605,
    'main_all.UNINSPECTABLE': 45810,
    'main_all.needs_proof_line': 45810,
    'main_all.needs_proof_line_with_archive_link': 5363,
    'main_all.rows': 81510,
    'main_without_batches.FAIL': 204,
    'main_without_batches.PASS': 1706,
    'main_without_batches.UNINSPECTABLE': 45506,
    'main_without_batches.rows': 47416,
    'mutant.hq_from_any_source.caught': True,
    'mutant.no_unit_test.caught': True,
    'mutant.number_only_streets.caught': True,
    'mutant.proof_any_archive_ref.caught': True,
    'mutant.proof_quote_unchecked.caught': True,
    'mutant.token_subset_names.caught': True,
    'mutant.web_any_domain.caught': True,
    'mutant.web_civic_only.caught': True,
    'mutant.web_name_unchecked.caught': True,
    'notes_rows': 982,
    'pass_basis.comma_part/org': 118,
    'pass_basis.comma_part/site_name_lead': 24,
    'pass_basis.web_quote': 166,
    'pass_basis.whole/org': 18343,
    'pass_basis.whole/site_name_lead': 1314,
    'pass_basis.whole/site_name_other': 934,
    'pass_site_city_not_in_quote': 242,
    'pass_site_state_differs': 0,
    'people.no_quote/institution_has_no_website': 35,
    'people.no_quote/off_institution_domain': 23,
    'people.no_quote/on_institution_domain': 676,
    'shifted_if_facility.FAIL name_not_held': 4,
    'shifted_if_facility.PASS': 94,
    'street_limit.different_number': 934,
    'street_limit.number_in_recorded_range': 14,
    'street_limit.number_word': 92,
    'street_limit.same_number_other': 1274,
    'street_limit.same_number_token_subset': 1552,
    'street_limit.same_street_other_number': 236,
    'test_segments_leaked': 0,
    'web.not_own_site.name_in_host': 67,
    'web.street_absent.spacing': 12,
    'web_batch1_4.FAIL not_own_site': 113,
    'web_batch1_4.FAIL street_absent_from_quote': 93,
    'web_batch1_4.FAIL street_absent_from_quote+not_own_site': 4,
    'web_batch1_4.PASS': 1642,
    'web_batch1_4.UNINSPECTABLE hq_absent_from_quote': 12,
    'web_batch1_4.UNINSPECTABLE name_absent_from_quote': 9,
    'web_batch1_4.UNINSPECTABLE no_record_website': 192,
    'web_batch1_4.UNINSPECTABLE record_street_no_civic_number': 8,
    'web_batch1_4.UNINSPECTABLE web_class_untested': 96,
    'web_batch1_4.UNINSPECTABLE web_record_no_street': 677,
    'web_batch1_4.rows': 2846,
    'web_other.FAIL not_own_site': 9,
    'web_other.FAIL street_absent_from_quote': 5,
    'web_other.PASS': 230,
    'web_other.UNINSPECTABLE hq_absent_from_quote': 1,
    'web_other.UNINSPECTABLE name_absent_from_quote': 8,
    'web_other.UNINSPECTABLE no_record_website': 5,
    'web_other.UNINSPECTABLE web_class_untested': 35,
    'web_other.UNINSPECTABLE web_record_no_street': 100,
    'web_other.UNINSPECTABLE web_site_row_no_street_claim': 108,
    'web_other.rows': 501,
    'web_pass_bound.domain': 1824,
    'web_pass_bound.name_1w': 15,
    'web_pass_bound.name_2w': 17,
    'web_pass_bound.name_3w': 12,
    'web_pass_bound.name_4w': 3,
    'web_pass_bound.name_5w': 1,
}  # regenerate by emptying this dict and re-running


TESTS = HERE.parents[1] / "scripts" / "test_check_evidence_binding.py"
BOILERPLATE = re.compile(r"^(?:site of 'x'|existence|naics|sic|status|program|permit_number|county|source_record_key|frs "
                         r"registry|rcrainfo handler|entity_type|dba name|award_count|recipient_uei|uei|ectypes)", re.I)
MUTANTS = {  # name: (original line fragment, loosened replacement) — each must make the planted-defect tests fail
    "token_subset_names": ("    if not qkeys & held:\n", "    if not any(set(q.split()) <= set(h.split()) or set(h.split())"
                           " <= set(q.split()) for q in qkeys for h in held):\n"),
    "number_only_streets": ('    if rk != qk:\n        return "street_differs"',
                            '    if rk.split()[:1] != qk.split()[:1]:\n        return "street_differs"'),
    "no_unit_test": ('    return "unit_differs" if ru and qu and not ru & qu else ""', '    return ""'),
    "hq_from_any_source": ('        if basis == "facility":', '        if False:'),
    "web_any_domain": ("        elif not any(own_domain(src, w) for w in sites):", "        elif False:"),
    "web_civic_only": ('    return "" if parts[0] in q and (not parts[1] or parts[1] in q) else',
                       '    return "" if parts[0] in q else'),
    "web_name_unchecked": ("        if not hits:\n", "        if False:\n"),
    "proof_quote_unchecked": ("    if quote and text[off:off + n] != quote:", "    if False:"),
    "proof_any_archive_ref": ("        if archive_ref and cap != archive_ref:", "        if False:"),
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
    for name, (old, new) in MUTANTS.items():
        with tempfile.TemporaryDirectory() as d:
            for f in ("check_evidence_binding.py", "test_check_evidence_binding.py", "atlas.py", "build_echo_spine.py"):
                text = (HERE.parents[1] / "scripts" / f).read_text(encoding="utf-8")
                text = text.replace("ROOT = Path(__file__).resolve().parents[1]", f"ROOT = Path({str(HERE.parents[1])!r})")
                if f == "check_evidence_binding.py":
                    assert text.count(old) == 1, f"mutant {name}: anchor not found once"
                    text = text.replace(old, new)
                (Path(d) / f).write_text(text, encoding="utf-8")
            out = subprocess.run([sys.executable, "-m", "unittest", "test_check_evidence_binding.Verdicts",
                                  "test_check_evidence_binding.GateMechanics"], cwd=d, capture_output=True, text=True).stderr
            caught[name] = len(re.findall(r"^FAIL: ", out, re.M))
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
    sd = [r["evidence_id"] for r in pass_sites if r["state_differs"]]
    got["pass_site_state_differs"] = len(sd)
    print(f"batches: site PASS rows whose quoted state differs from the record's: {len(sd)}")
    basis = Counter(r["name_basis"] or "web_quote" for r in q_res if r["verdict"] == "PASS")
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

    # per-row proof a PR would owe: every UNINSPECTABLE row; how many already have an archive_links capture
    for name, res, ref in (("batches", q_res, BATCH_HEAD), ("main_all", main_res, MAIN)):
        archive = {r["evidence_id"] for r in b.rows(ref, "archive_links.csv")}
        un = [r["evidence_id"] for r in res if r["verdict"] == "UNINSPECTABLE"]
        got[f"{name}.needs_proof_line"] = len(un)
        got[f"{name}.needs_proof_line_with_archive_link"] = sum(e in archive for e in un)
        print(f"\n{name}: {len(un)} rows would need a proof line; {got[f'{name}.needs_proof_line_with_archive_link']} "
              f"of them have a data/archive_links.csv capture")

    # web quotes on main (controller ruling 2026-11-22): the burn-down batch 1-4 family and everything else
    web = [r for r in main_res if r["source_family"] == "url" and r["reason"] not in ("no_quote", "other_table")]
    for name, res in (("web_batch1_4", [r for r in web if BATCH14.match(r["created_by"])]),
                      ("web_other", [r for r in web if not BATCH14.match(r["created_by"])])):
        show(f"{name}: verdict", table(res))
        show(f"{name}: verdict and reason", Counter(f"{r['verdict']} {r['reason']}".strip() for r in res))
        got[f"{name}.rows"] = len(res)
        got.update({f"{name}.{r}": n for r, n in Counter(f"{r['verdict']} {r['reason']}".strip() for r in res).items()})
        tc = Counter(f"{r['record_table']} {r['claim_type']} {r['verdict']}" for r in res)
        show(f"{name}: record table, claim type, verdict", tc)
    wb = Counter(r["web_bound"] for r in web if r["verdict"] == "PASS")
    show("web PASS rows on main by what bound them (name_Nw: shortest held name matched, in words; +street_gap: civic "
         "number and first street word not within two tokens)", wb)
    got.update({f"web_pass_bound.{k}": n for k, n in wb.items()})
    got["web.not_own_site.name_in_host"] = sum(r["name_alt"] == "name_in_host" for r in web)
    got["web.street_absent.spacing"] = sum(r["street_limit"] == "spacing" for r in web)
    print(f"web FAIL rows an owner reading would pass: sister domain carrying a held name "
          f"{got['web.not_own_site.name_in_host']}; street present once spacing is ignored {got['web.street_absent.spacing']}")

    # the 734 people rows: no quote, so only the domain test could run; measured against the institution's website
    people = {r["person_id"]: r for r in b.rows(MAIN, "people.csv")}
    idx = b.Index.load(MAIN)
    pc = Counter()
    for e in (e for e in main_evs if e["created_by"].strip() == PEOPLE_LABEL):
        p = people[e["record_id"]]
        inst = b.record_websites(idx, "organizations", idx.orgs.get(p["institution_org_id"]) or {})
        src = b.domain_key(e["source_ref"])
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
