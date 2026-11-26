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
mk = lambda rid, quote, table="organizations", claim="size_band", src=T.SRC, cls="government_filing": t.ev(rid, src, quote, claim=claim, table=table, cls=cls)


def verdict(row):
    return gate.judge(row, T.idx)[:2]


def same(got, want):
    """Verdict equal; a reason is wanted among the demonstrated conflicts joined by "+" (a wrong city can also move the ZIP)."""
    return got[0] == want[0] and (got[1] == want[1] if not want[1] or got[0] != "FAIL" else want[1] in got[1].split("+"))


# (defect, row builder, expected verdict and reason) on both grains: organization row, then site row
SUITE = OK.replace("1070 EVANS AVE", "1200 EVANS AVE")
DEFECTS = [
    ("correct row", lambda r, tb: mk(r, OK, tb), ("PASS", "")),
    ("wrong borrower name", lambda r, tb: mk(r, OK.replace("HARBOR RUBBER PRODUCTS INC", "KESTREL MOLDING LLC"), tb), ("FAIL", "name_not_held")),
    ("wrong street", lambda r, tb: mk(r, OK.replace("1070 EVANS AVE", "1090 EVANS AVE"), tb), ("FAIL", "street_differs")),
    ("wrong city and ZIP", lambda r, tb: mk(r, OK.replace("AKRON, OH 44305", "CANTON, OH 44702"), tb), ("FAIL", "city_differs")),
    ("right ZIP, wrong city", lambda r, tb: mk(r, OK.replace("AKRON, OH 44305", "CANTON, OH 44305"), tb), ("FAIL", "ppp_city_differs")),
    ("right city, wrong ZIP", lambda r, tb: mk(r, OK.replace("AKRON, OH 44305", "AKRON, OH 99999"), tb), ("FAIL", "ppp_zip_differs")),
    ("garbage source_ref", lambda r, tb: mk(r, OK, tb, src="SBA PPP garbage"), ("UNINSPECTABLE", "ppp_source_ref")),
    ("truncated source_ref", lambda r, tb: mk(r, OK, tb, src="SBA PPP LoanNumber 8921367107"), ("UNINSPECTABLE", "ppp_source_ref")),
    ("impossible release date", lambda r, tb: mk(r, OK, tb, src=T.SRC.replace("2024-09-30", "2024-13-45")), ("UNINSPECTABLE", "ppp_source_ref")),
    ("wrong source class (own_site)", lambda r, tb: mk(r, OK, tb, cls="own_site"), ("UNINSPECTABLE", "ppp_source_class")),
    ("borrower is the operator plus extra words", lambda r, tb: mk(r, OK.replace("PRODUCTS INC", "PRODUCTS HOLDINGS INC"), tb), ("FAIL", "name_not_held")),
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
            assert same(got, want), (name, tb, got, want)
            print(f"{name:36s} {tb:13s} {got[0]:13s} {got[1]}")
    for name, build, want in SUITE_ROWS:
        for rid, tb in (("O-SUITE", "organizations"), ("S-SUITE", "sites")):
            got = verdict(build(rid, tb))
            assert same(got, want), (name, tb, got, want)
            print(f"{name:36s} {tb:13s} {got[0]:13s} {got[1]}")
    label = OK.replace("HARBOR RUBBER PRODUCTS INC", "KESTREL MOLDING").replace("1070", "1400")
    for rid, tb in (("O-LABEL", "organizations"), ("S-LABEL", "sites")):
        got = verdict(mk(rid, label, tb))
        assert got == ("FAIL", "name_not_held"), (tb, got)
        print(f"{'borrower is only the site label':36s} {tb:13s} {got[0]:13s} {got[1]}")
    for rid, tb in (("O-TRADE", "organizations"), ("S-TRADE", "sites")):
        got = verdict(mk(rid, OK.replace("HARBOR RUBBER PRODUCTS INC", "LAKESIDE RUBBER WORKS INC").replace("1070", "1500"), tb))
        assert got == ("PASS", ""), (tb, got)
        print(f"{'borrower is a trade name':36s} {tb:13s} {got[0]:13s} {got[1]}")
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
    # with the PPP-specific guards off (the prefix no longer dispatches), the four false passes of Codex's round 1 return on the site grain
    label = OK.replace("HARBOR RUBBER PRODUCTS INC", "KESTREL MOLDING").replace("1070", "1400")
    false_passes = {"garbage source_ref": mk("S-ONE", OK, "sites", src="SBA PPP garbage"), "own_site class": mk("S-ONE", OK, "sites", cls="own_site"),
                    "site label as borrower": mk("S-LABEL", label, "sites"), "right ZIP, wrong city": mk("S-ONE", OK.replace("AKRON, OH 44305", "CANTON, OH 44305"), "sites"),
                    "right city, wrong ZIP": mk("S-ONE", OK.replace("AKRON, OH 44305", "AKRON, OH 99999"), "sites")}
    assert all(verdict(row)[0] != "PASS" for row in false_passes.values())
    with mock.patch.object(gate, "PPP_PREFIX", "SBA PPP\0"):
        passed = {k for k, row in false_passes.items() if verdict(row) == ("PASS", "")}
        assert passed == set(false_passes), passed
    with mock.patch.object(gate, "FAMILIES", [f for f in gate.FAMILIES if f[0] != gate.PPP_PREFIX]):
        assert verdict(mk("O-ONE", OK)) == ("UNINSPECTABLE", "unknown_source_family"), "before this route no PPP row could pass"
    print("mutations: without the type whitelist a sole proprietor PASSES; without the site delegation a wrong organization street PASSES; without the PPP guards all five round-1 false passes PASS; without the family a correct row is unknown_source_family")


def main():
    run_table()
    mutations()
    result = unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
    assert result.wasSuccessful() and result.testsRun >= 20, result
    print(f"PASS: {len(DEFECTS)} planted rows and {len(SUITE_ROWS)} suite rows on two grains, 3 organization-scope holds, mutations, {result.testsRun} unit tests")


if __name__ == "__main__":
    main()
