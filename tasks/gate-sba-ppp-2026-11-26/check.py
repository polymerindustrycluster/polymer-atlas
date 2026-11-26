"""Named check for the binding gate's SBA PPP route: planted defects are not admitted, correct rows PASS, and each guard is the thing that
catches its defect (a mutated gate lets the defect through). Synthetic rows only; run from anywhere: python3 tasks/gate-sba-ppp-2026-11-26/check.py"""
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate
import test_check_evidence_binding as t

T = t.SbaPppRoute
T.setUpClass()
OK = T.OK
mk = lambda rid, quote, table="organizations", claim="size_band": t.ev(rid, T.SRC, quote, claim=claim, table=table, cls="government_filing")


def verdict(row):
    return gate.judge(row, T.idx)[:2]


# (defect, row builder, expected verdict and reason) on both grains: organization row, then site row
SUITE = OK.replace("1070 EVANS AVE", "1200 EVANS AVE")
DEFECTS = [
    ("correct row", lambda r, tb: mk(r, OK, tb), ("PASS", "")),
    ("wrong borrower name", lambda r, tb: mk(r, OK.replace("HARBOR RUBBER PRODUCTS INC", "KESTREL MOLDING LLC"), tb), ("FAIL", "name_not_held")),
    ("wrong street", lambda r, tb: mk(r, OK.replace("1070 EVANS AVE", "1090 EVANS AVE"), tb), ("FAIL", "street_differs")),
    ("wrong city", lambda r, tb: mk(r, OK.replace("AKRON, OH 44305", "CANTON, OH 44702"), tb), ("FAIL", "city_differs")),
    ("missing quote", lambda r, tb: mk(r, None, tb), ("UNINSPECTABLE", "no_quote")),
    ("sole proprietor", lambda r, tb: mk(r, OK.replace("Corporation;", "Sole Proprietorship;", 1), tb), ("FAIL", "ppp_individual_borrower_type")),
    ("self-employed", lambda r, tb: mk(r, OK.replace("Corporation;", "Self-Employed Individuals;", 1), tb), ("FAIL", "ppp_individual_borrower_type")),
    ("business type not stated", lambda r, tb: mk(r, OK.replace("business_type: Corporation; ", ""), tb), ("UNINSPECTABLE", "ppp_quote_fields")),
    ("suite on one side only (borrower)", lambda r, tb: mk(r, OK.replace("1070 EVANS AVE", "1070 EVANS AVE STE 110"), tb),
     ("HELD", "held_for_reading:designator_not_on_both_sides")),
    ("claim is not size_band", lambda r, tb: mk(r, OK, tb, claim="address"), ("UNINSPECTABLE", "ppp_claim_not_size_band")),
]
SUITE_ROWS = [  # record names Suite 500
    ("suite on one side only (record)", lambda r, tb: mk(r, SUITE, tb), ("HELD", "held_for_reading:designator_not_on_both_sides")),
    ("different suite", lambda r, tb: mk(r, SUITE.replace("AVE,", "AVE STE 110,"), tb), ("FAIL", "unit_differs")),
    ("same suite", lambda r, tb: mk(r, SUITE.replace("AVE,", "AVE SUITE 500,"), tb), ("PASS", "")),
]


def run_table():
    for name, build, want in DEFECTS:
        for rid, tb in (("O-ONE", "organizations"), ("S-ONE", "sites")):
            got = verdict(build(rid, tb))
            assert got == want, (name, tb, got, want)
            print(f"{name:36s} {tb:13s} {got[0]:13s} {got[1]}")
    for name, build, want in SUITE_ROWS:
        for rid, tb in (("O-SUITE", "organizations"), ("S-SUITE", "sites")):
            got = verdict(build(rid, tb))
            assert got == want, (name, tb, got, want)
            print(f"{name:36s} {tb:13s} {got[0]:13s} {got[1]}")
    for oid in ("O-TWO", "O-MI", "O-NONE"):
        got = verdict(mk(oid, OK))
        assert got == ("HELD", "held_for_reading:ppp_not_single_site_ohio_organization"), (oid, got)
        print(f"{'not single-site Ohio-only: ' + oid:36s} organizations  {got[0]:13s} {got[1]}")


def mutations():
    """Break one guard at a time; the defect it exists to catch must then PASS, or the check proves nothing."""
    individual = mk("O-ONE", OK.replace("Corporation;", "Sole Proprietorship;", 1))
    with mock.patch.object(gate, "PPP_TYPES", frozenset({"Sole Proprietorship"}) | gate.PPP_TYPES):
        assert verdict(individual) == ("PASS", ""), "type whitelist is not what stops an individual borrower"
    wrong_street = mk("O-ONE", OK.replace("1070 EVANS AVE", "1090 EVANS AVE"))
    assert verdict(wrong_street) == ("FAIL", "street_differs")
    with mock.patch.object(gate, "judge_ppp", lambda ev, idx, quote: None):  # an organization row then meets only the name leg
        assert verdict(wrong_street) == ("PASS", ""), "delegation to the active site is not what tests an organization row's street"
    with mock.patch.object(gate, "FAMILIES", [f for f in gate.FAMILIES if f[0] != gate.PPP_PREFIX]):
        assert verdict(mk("O-ONE", OK)) == ("UNINSPECTABLE", "unknown_source_family"), "before this route no PPP row could pass"
    print("mutations: without the type whitelist a sole proprietor PASSES; without the site delegation a wrong organization street PASSES; without the family a correct row is unknown_source_family")


def main():
    run_table()
    mutations()
    result = unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
    assert result.wasSuccessful() and result.testsRun >= 15, result
    print(f"PASS: {len(DEFECTS)} planted rows and {len(SUITE_ROWS)} suite rows on two grains, 3 organization-scope holds, mutations, {result.testsRun} unit tests")


if __name__ == "__main__":
    main()
