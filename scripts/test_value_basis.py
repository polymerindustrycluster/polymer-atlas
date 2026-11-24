"""Tests for scripts/value_basis.py (SCHEMA §4.24). Fixture trees only: no row, quote or page here is real.

Planted defects each fail with the message of the rule they name: the planted input is corrupted, the table is
regenerated or compared, and the specific line is asserted (editing the table alone would trip only the freshness rule).
"""
import csv
import hashlib
import atexit
import shutil
import tempfile
import unittest
from pathlib import Path

import check_evidence_binding as gate
import value_basis as vb

EVD_COLS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
            "observed_date", "tier_effect", "created_by", "notes", "address_role"]
PROOF_COLS = ["evidence_id", "record_id", "claim_sha256", "capture", "capture_date", "capture_sha256", "quote_offset",
              "verdict", "reader_family", "reader_date"]
QUOTE = "We run custom compounding lines in our Akron plant."
PAGE = f"<html><body><main><p>Welcome. {QUOTE} Call us.</p></main></body></html>".encode()
OFFSET = gate.capture_text(PAGE).index(QUOTE)


def write(path, rows, cols):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows([{c: r.get(c, "") for c in cols} for r in rows])


def ev(eid, rid, detail, table="sites", cls="own_site", claim="activity", effect="supports_B", by="claude lane1",
       ref="https://acme.example/p"):
    return {"evidence_id": eid, "record_table": table, "record_id": rid, "claim_type": claim, "claim_detail": detail,
            "source_class": cls, "source_ref": ref, "observed_date": "2026-11-20", "tier_effect": effect, "created_by": by}


class Tree:
    """A throwaway repository root: ORG-1 with two sites; SITE-1 holds the values under test."""

    def __init__(self, evidence, site_processes="custom_compounding", site_markets="", verdict_rows=None, readme=None,
                 page_url="https://www.acme.example/p/", requested_url=None):
        self.root = Path(tempfile.mkdtemp())
        atexit.register(shutil.rmtree, self.root, ignore_errors=True)
        d = self.root / "data"
        write(d / "organizations_OH.csv", [{"org_id": "ORG-1", "processes": "extrusion_profile", "markets_served": ""}],
              ["org_id", "processes", "markets_served"])
        write(d / "sites_OH.csv", [{"site_id": "SITE-1", "org_id": "ORG-1", "processes": site_processes,
                                    "markets_served": site_markets}], ["site_id", "org_id", "processes", "markets_served"])
        write(d / "evidence_sites_OH.csv", evidence, EVD_COLS)
        if verdict_rows is not None:
            f = self.root / "tasks" / "rq" / "VALUE_VERDICTS.csv"
            write(f, verdict_rows, list(vb.VERDICT_COLS))
            if page_url:
                write(f.parent / "VALUE_PAGES.csv", [{"page_sha256": hashlib.sha256(PAGE).hexdigest(), "page_url": page_url,
                                                      "requested_url": requested_url or ""}],
                      list(vb.PAGE_COLS) + (["requested_url"] if requested_url else []))
            (f.parent / "README.md").write_text(readme if readme is not None else
                                                "Read on: 2026-11-24\nRead by: Codex GPT-6.2 Sol\nChecked by: Gemini Hydrogen\n")

    def add_proof(self, evrow, **over):
        folder = self.root / "tasks" / "lane1"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "README.md").write_text("Built by: Codex GPT-6.2 Sol\n")
        row = {"evidence_id": evrow["evidence_id"], "record_id": evrow["record_id"], "claim_sha256": gate.claim_sha256(evrow),
               "capture": "https://web.archive.org/web/20261120000000id_/https://acme.example/p", "capture_date": "2026-11-20",
               "capture_sha256": hashlib.sha256(PAGE).hexdigest(), "quote_offset": str(OFFSET), "verdict": "VERIFIED",
               "reader_family": "Claude Sonnet 5.5", "reader_date": "2026-11-21", **over}
        write(folder / "BINDING_PROOF.csv", [row], PROOF_COLS)

    def basis(self, pages=None):
        rows, problems, info = vb.generate(self.root / "data", self.root / "tasks", pages)
        return {(r["record_table"], r["record_id"], r["field"], r["value"]): (r["basis"], r["evidence_id"], r["basis_date"])
                for r in rows}, problems, info

    def check(self):
        return vb.check(self.root / "data", self.root / "tasks")[0]

    def write_table(self):
        rows, problems, _ = vb.generate(self.root / "data", self.root / "tasks")
        assert not problems, problems
        (self.root / "data" / "value_basis.csv").write_text(vb.render(rows))

    def lines(self, mutate):
        path = self.root / "data" / "value_basis.csv"
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        mutate(rows)
        write(path, rows, vb.COLS)


KEY = ("sites", "SITE-1", "processes", "custom_compounding")
QUOTED = f"processes=custom_compounding; quote: {QUOTE}"


class Basis(unittest.TestCase):
    def test_unquoted_named_row_is_not_yet_checked(self):
        t = Tree([ev("EVD-1", "SITE-1", "sites.processes includes custom_compounding (own-site disclosure)")])
        self.assertEqual(t.basis()[0][KEY], ("not_yet_checked", "EVD-1", ""))

    def test_value_no_row_names_is_not_yet_checked_with_an_empty_evidence_id_and_is_counted(self):
        t = Tree([ev("EVD-1", "SITE-1", "sites.processes includes lamination")])
        got, _, info = t.basis()
        self.assertEqual(got[KEY], ("not_yet_checked", "", ""))
        self.assertEqual(info["unnamed"][("sites", "processes")], 1)

    def test_own_record_row_is_preferred_to_an_organization_row_as_the_standing_evidence(self):
        t = Tree([ev("EVD-1", "ORG-1", "processes=custom_compounding", table="organizations"),
                  ev("EVD-2", "SITE-1", "processes=custom_compounding")])
        self.assertEqual(t.basis()[0][KEY], ("not_yet_checked", "EVD-2", ""))

    def test_org_row_gives_a_site_at_most_not_yet_checked(self):
        e = ev("EVD-1", "ORG-1", QUOTED, table="organizations")
        t = Tree([e])
        t.add_proof(e)
        self.assertEqual(t.basis()[0][KEY][0], "not_yet_checked", "grain: a corporate row never settles a plant value")

    def test_contradicts_row_is_never_a_source(self):
        t = Tree([ev("EVD-1", "SITE-1", QUOTED, effect="contradicts")])
        self.assertEqual(t.basis()[0][KEY], ("not_yet_checked", "", ""))

    def test_platform_category_row_is_never_a_source(self):
        t = Tree([ev("EVD-1", "SITE-1", "processes=custom_compounding", cls="platform_category")])
        self.assertEqual(t.basis()[0][KEY], ("not_yet_checked", "", ""))

    def test_verified_proof_makes_stated(self):
        e = ev("EVD-1", "SITE-1", QUOTED)
        t = Tree([e])
        t.add_proof(e)
        self.assertEqual(t.basis()[0][KEY], ("stated", "EVD-1", "2026-11-21"))

    def test_proof_for_an_edited_row_voids_the_reading(self):
        e = ev("EVD-1", "SITE-1", QUOTED)
        t = Tree([e])
        t.add_proof(e, claim_sha256="0" * 64)
        self.assertEqual(t.basis()[0][KEY][0], "not_yet_checked")

    def test_proof_needs_a_different_reader_family(self):
        e = ev("EVD-1", "SITE-1", QUOTED)
        t = Tree([e])
        t.add_proof(e, reader_family="Codex GPT-6.2 Sol")
        self.assertEqual(t.basis()[0][KEY][0], "not_yet_checked")

    def test_quoted_row_without_a_proof_is_not_stated(self):
        t = Tree([ev("EVD-1", "SITE-1", QUOTED)])
        self.assertEqual(t.basis()[0][KEY][0], "not_yet_checked")

    def test_row_naming_two_values_does_not_state_either(self):
        e = ev("EVD-1", "SITE-1", f"processes=custom_compounding; lamination; quote: {QUOTE}")
        t = Tree([e], site_processes="custom_compounding;lamination")
        t.add_proof(e)
        got = t.basis()[0]
        self.assertEqual({got[KEY][0], got[("sites", "SITE-1", "processes", "lamination")][0]}, {"not_yet_checked"})

    def test_government_filing_row_with_words_is_filing(self):
        t = Tree([ev("EVD-1", "SITE-1", QUOTED, cls="government_filing")])
        self.assertEqual(t.basis()[0][KEY], ("filing", "EVD-1", "2026-11-20"))

    def test_filing_row_asserting_another_value_does_not_certify_this_one(self):  # planted defect (review 2026-11-24)
        t = Tree([ev("EVD-1", "SITE-1", "processes=lamination; quote: Our competitors use custom_compounding and we do not.", cls="government_filing")],
                 site_processes="lamination;custom_compounding")
        got = t.basis()[0]
        self.assertEqual((got[("sites", "SITE-1", "processes", "lamination")][0], got[KEY][0]), ("filing", "not_yet_checked"))

    def test_filing_row_without_filing_words_is_not_filing(self):  # planted defect
        t = Tree([ev("EVD-1", "SITE-1", "processes=custom_compounding; process excerpt:", cls="government_filing")])
        self.assertEqual(t.basis()[0][KEY][0], "not_yet_checked")

    def test_filing_whose_excerpt_names_the_token_but_whose_head_does_not_is_not_filing(self):  # planted defect (review round 2)
        t = Tree([ev("EVD-1", "SITE-1", "process excerpt: Only our competitors do custom_compounding; this facility does not.", cls="government_filing")])
        self.assertEqual(t.basis()[0][KEY][0], "not_yet_checked")

    def test_filing_row_with_an_excerpt_is_filing(self):
        t = Tree([ev("EVD-1", "SITE-1", 'processes custom_compounding authorized for the site; process excerpt: "P006, Compounding and Extruding"', cls="government_filing")])
        self.assertEqual(t.basis()[0][KEY][0], "filing")

    def test_proof_row_asserting_another_value_does_not_state_this_one(self):  # planted defect
        e = ev("EVD-1", "SITE-1", f"processes=lamination; quote: {QUOTE}")
        t = Tree([e], site_processes="lamination;custom_compounding")
        t.add_proof(e)
        got = t.basis()[0]
        self.assertEqual((got[("sites", "SITE-1", "processes", "lamination")][0], got[KEY][0]), ("stated", "not_yet_checked"))

    def test_government_filing_that_restates_the_record_is_not_filing(self):
        t = Tree([ev("EVD-1", "SITE-1", "site activity per site row: processes [custom_compounding]", cls="government_filing")])
        self.assertEqual(t.basis()[0][KEY][0], "not_yet_checked")

    def test_filing_outranks_a_not_yet_checked_row_and_precedence_ties_take_the_lowest_evidence_id(self):
        t = Tree([ev("EVD-2", "SITE-1", "processes=custom_compounding"),
                  ev("EVD-3", "SITE-1", QUOTED, cls="government_filing"), ev("EVD-1", "SITE-1", "processes=custom_compounding")])
        self.assertEqual(t.basis()[0][KEY], ("filing", "EVD-3", "2026-11-20"))

    def test_generation_is_deterministic(self):
        t = Tree([ev("EVD-2", "SITE-1", "processes=custom_compounding"), ev("EVD-1", "SITE-1", "processes=custom_compounding")])
        a, b = vb.generate(t.root / "data", t.root / "tasks")[0], vb.generate(t.root / "data", t.root / "tasks")[0]
        self.assertEqual(vb.render(a), vb.render(b))
        self.assertEqual(next(r for r in a if r["value"] == "custom_compounding")["evidence_id"], "EVD-1")


def verdict(cls, quote="", offset="", sha=None, key=KEY, page="p.html"):
    return {"owner": "ORG-1", "record_table": key[0], "record_id": key[1], "field": key[2], "value": key[3], "class": cls,
            "quote": quote, "page_path": page, "page_sha256": sha or hashlib.sha256(PAGE).hexdigest(), "offset": offset,
            "grain": "plant", "note": "read"}


class Verdicts(unittest.TestCase):
    NAMED = [ev("EVD-1", "SITE-1", "sites.processes includes custom_compounding")]

    def tree(self, rows, manifest=None, **kw):
        t = Tree(self.NAMED, verdict_rows=rows, **kw)
        self.store(t, manifest or (kw.get("page_url", "https://www.acme.example/p/"), kw.get("requested_url") or kw.get("page_url", "https://www.acme.example/p/")))
        return t

    @staticmethod
    def store(t, manifest):
        """A page store: p.html plus the corpus manifest entry (final_url, url) the sidecar's URLs are checked against."""
        (t.root / "pages").mkdir(exist_ok=True)
        (t.root / "pages" / "p.html").write_bytes(PAGE)
        d = t.root / "pages" / "pic18-corpus-2026-11-16" / "ORG-1"
        write(d / "manifest.csv", [{"raw_file": "../p.html", "url": manifest[1], "final_url": manifest[0], "status": "ok"}],
              ["raw_file", "url", "final_url", "status"])

    def test_stated_verdict_replays_against_the_stored_page(self):
        t = self.tree([verdict("STATED", QUOTE, str(OFFSET))])
        got, problems, info = t.basis(t.root / "pages")
        self.assertEqual((got[KEY], problems), (("stated", "EVD-1", "2026-11-24"), []))
        self.assertEqual(info["stated_not_replayed"], 0)

    def test_stated_verdict_whose_quote_is_not_on_the_page_fails(self):  # planted defect
        t = self.tree([verdict("STATED", QUOTE.replace("custom", "bespoke"), str(OFFSET))])
        got, problems, _ = t.basis(t.root / "pages")
        self.assertTrue(any("does not replay" in p and "not at that offset" in p for p in problems), problems)
        self.assertEqual(got[KEY][0], "not_yet_checked")

    def test_stated_verdict_with_a_wrong_offset_or_sha_fails(self):  # planted defect
        for bad in (verdict("STATED", QUOTE, str(OFFSET + 1)), verdict("STATED", QUOTE, str(OFFSET), sha="a" * 64)):
            t = self.tree([bad])
            self.assertTrue(any("does not replay" in p for p in t.basis(t.root / "pages")[1]))

    def test_without_a_page_store_the_unreplayed_count_is_reported_not_hidden(self):
        t = self.tree([verdict("STATED", QUOTE, str(OFFSET))])
        self.assertEqual(t.basis()[2]["stated_not_replayed"], 1)

    def test_page_path_cannot_leave_the_store(self):
        t = self.tree([verdict("STATED", QUOTE, str(OFFSET), page="../../outside.html")])
        self.assertTrue(any("does not replay" in p for p in t.basis(t.root / "pages")[1]))

    def test_not_stated_and_implied_map_to_withheld_and_implied(self):
        for cls, basis in (("NOT_STATED", "not_found_pending_refetch"), ("IMPLIED", "implied")):
            self.assertEqual(self.tree([verdict(cls)]).basis()[0][KEY][0], basis)

    def test_no_page_line_gives_no_label(self):
        row = verdict("NO_PAGE")
        row.update(quote="", page_path="", page_sha256="", offset="")
        self.assertEqual(self.tree([row]).basis()[0][KEY][0], "not_yet_checked")

    def test_verified_proof_outranks_not_stated(self):
        e = ev("EVD-1", "SITE-1", QUOTED)
        t = Tree([e], verdict_rows=[verdict("NOT_STATED")])
        t.add_proof(e)
        self.assertEqual(t.basis()[0][KEY][0], "stated")

    def test_not_stated_outranks_not_yet_checked(self):
        self.assertEqual(self.tree([verdict("NOT_STATED")]).basis()[0][KEY][0], "not_found_pending_refetch")

    def test_packet_without_a_second_family_check_publishes_nothing(self):
        for readme in ("Read on: 2026-11-24\nRead by: Codex GPT-6.2 Sol\n",
                       "Read on: 2026-11-24\nRead by: Codex GPT-6.2 Sol\nChecked by: Codex GPT-6.2 Astra\n"):
            got, problems, _ = self.tree([verdict("NOT_STATED")], readme=readme).basis()
            self.assertEqual(got[KEY][0], "not_yet_checked")
            self.assertTrue(any("publishes no label" in p for p in problems))

    def test_verdict_for_a_value_the_record_does_not_hold_is_a_problem(self):
        row = verdict("NOT_STATED", key=("sites", "SITE-1", "processes", "lamination"))
        self.assertTrue(any("does not hold" in p for p in self.tree([row]).basis()[1]))

    def test_contradicting_verdict_classes_on_one_date_is_an_error_not_a_pick(self):
        t = self.tree([verdict("IMPLIED"), verdict("NOT_STATED")])
        self.assertTrue(any("share the latest read date" in p for p in t.basis()[1]))

    def test_verdict_for_a_value_no_row_names_stops_the_generator(self):  # review 2026-11-24: a checked NOT_STATED must not vanish
        t = Tree([ev("EVD-1", "SITE-1", "unrelated row")], verdict_rows=[verdict("NOT_STATED")])
        self.assertTrue(any("no bound row on its own record" in p for p in t.basis()[1]))

    def test_stated_verdict_with_only_organization_evidence_is_refused(self):  # planted defect
        t = Tree([ev("EVD-1", "ORG-1", "processes=custom_compounding", table="organizations")],
                 verdict_rows=[verdict("STATED", QUOTE, str(OFFSET))])
        Verdicts.store(t, ("https://www.acme.example/p/", "https://www.acme.example/p/"))
        got, problems, _ = t.basis(t.root / "pages")
        self.assertTrue(any("not only its organization" in p for p in problems), problems)
        self.assertEqual(got[KEY][0], "not_yet_checked")

    def test_stated_verdict_whose_page_is_on_a_site_no_bound_row_cites_is_refused(self):  # planted defect (review round 2): the south plant's page
        t = self.tree([verdict("STATED", QUOTE, str(OFFSET))], page_url="https://other.example/south-plant")
        got, problems, _ = t.basis(t.root / "pages")
        self.assertTrue(any("is not on a site any bound row" in p for p in problems), problems)
        self.assertEqual(got[KEY][0], "not_yet_checked")

    def test_verdict_on_another_page_of_the_cited_site_gives_no_label(self):  # planted defect (review round 3): /north row, /south quote
        for cls, quote, offset in (("STATED", QUOTE, str(OFFSET)), ("NOT_STATED", "", ""), ("IMPLIED", "", "")):
            t = self.tree([verdict(cls, quote, offset)], page_url="https://acme.example/south")
            got, problems, info = t.basis(t.root / "pages")
            self.assertEqual((got[KEY], problems, info["verdict_unbound"]), (("not_yet_checked", "EVD-1", ""), [], [KEY]), cls)

    def test_positive_control_row_citing_the_south_page_gives_stated(self):
        t = Tree([ev("EVD-1", "SITE-1", "processes=custom_compounding", ref="https://acme.example/south")],
                 verdict_rows=[verdict("STATED", QUOTE, str(OFFSET))], page_url="https://www.acme.example/south")
        Verdicts.store(t, ("https://www.acme.example/south", "https://www.acme.example/south"))
        self.assertEqual(t.basis(t.root / "pages")[0][KEY], ("stated", "EVD-1", "2026-11-24"))

    def test_recorded_redirect_to_the_cited_page_counts_as_that_page(self):
        t = self.tree([verdict("STATED", QUOTE, str(OFFSET))], page_url="https://acme.example/final", requested_url="https://acme.example/p")
        self.assertEqual(t.basis(t.root / "pages")[0][KEY][0], "stated")

    def test_forged_page_url_or_requested_url_fails_the_manifest_check(self):  # planted defects (review round 4)
        true = ("https://rpm.example/final", "https://rpm.example/req")
        t = Tree(self.NAMED, verdict_rows=[verdict("NOT_STATED")], page_url="https://acme.example/p", requested_url="https://acme.example/p")
        self.store(t, true)   # the manifest says the page is rpm.example's; the sidecar claims it is the cited acme.example page
        got, problems, _ = t.basis(t.root / "pages")
        self.assertTrue(any("corpus manifest records" in p for p in problems), problems)
        forged_page = self.tree([verdict("NOT_STATED")], manifest=("https://rpm.example/final", "https://acme.example/p"), page_url="https://acme.example/p")
        self.assertTrue(any("corpus manifest records" in p for p in forged_page.basis(forged_page.root / "pages")[1]))
        forged_req = self.tree([verdict("NOT_STATED")], manifest=("https://acme.example/final", "https://rpm.example/req"),
                               page_url="https://acme.example/final", requested_url="https://acme.example/p")
        self.assertTrue(any("corpus manifest records" in p for p in forged_req.basis(forged_req.root / "pages")[1]))

    def test_true_pair_passes_the_manifest_check_and_a_different_page_gives_not_yet_checked(self):  # the RPM case, honestly recorded
        t = self.tree([verdict("NOT_STATED")], manifest=("https://acme.example/south", "https://acme.example/south"),
                      page_url="https://acme.example/south", requested_url="")
        got, problems, info = t.basis(t.root / "pages")
        self.assertEqual((got[KEY][0], problems, info["verdict_unbound"]), ("not_yet_checked", [], [KEY]))

    def test_missing_manifest_entry_fails_and_no_store_reports_the_count(self):
        t = self.tree([verdict("NOT_STATED")])
        (t.root / "pages" / "pic18-corpus-2026-11-16" / "ORG-1" / "manifest.csv").unlink()
        self.assertTrue(any("no entry for the page" in p for p in t.basis(t.root / "pages")[1]))
        self.assertEqual(self.tree([verdict("NOT_STATED")]).basis()[2]["page_urls_not_checked"], 1)

    def test_stated_verdict_without_a_page_url_is_refused(self):
        t = self.tree([verdict("STATED", QUOTE, str(OFFSET))], page_url="")
        self.assertTrue(any("no VALUE_PAGES.csv entry" in p for p in t.basis(t.root / "pages")[1]))

    def test_stated_verdict_rests_on_the_row_that_cites_the_pages_site(self):
        t = Tree([ev("EVD-1", "SITE-1", "processes=custom_compounding", ref="https://other.example/x"),
                  ev("EVD-2", "SITE-1", "processes=custom_compounding", ref="https://acme.example/p")], verdict_rows=[verdict("STATED", QUOTE, str(OFFSET))])
        Verdicts.store(t, ("https://www.acme.example/p/", "https://www.acme.example/p/"))
        self.assertEqual(t.basis(t.root / "pages")[0][KEY], ("stated", "EVD-2", "2026-11-24"))

    def test_implied_verdict_may_rest_on_organization_evidence(self):
        t = Tree([ev("EVD-1", "ORG-1", "processes=custom_compounding", table="organizations")], verdict_rows=[verdict("IMPLIED")])
        self.assertEqual(t.basis()[0][KEY], ("implied", "EVD-1", "2026-11-24"))

    def test_verdict_for_another_owner_grain_or_page_folder_is_refused(self):  # planted defects
        for over in ({"owner": "ORG-9"}, {"grain": "company"}, {"page_path": "corpus/ORG-9/p.html"}):
            t = Tree(self.NAMED, verdict_rows=[{**verdict("NOT_STATED"), **over}])
            got, problems, _ = t.basis()
            self.assertTrue(any("labels only its own record" in p for p in problems), (over, problems))
            self.assertEqual(got[KEY][0], "not_yet_checked")


class Check(unittest.TestCase):
    """check() compares the table with a fresh generation and names each defect."""

    def setUp(self):
        self.t = Tree([ev("EVD-1", "SITE-1", "processes=custom_compounding"),
                       ev("EVD-2", "SITE-1", "sites.markets_served includes medical_device")], site_markets="medical_device")
        self.t.write_table()

    def problems(self):
        return self.t.check()

    def test_a_fresh_table_passes(self):
        self.assertEqual(self.problems(), [])

    def test_hand_edited_basis_fails(self):  # planted defect
        self.t.lines(lambda rows: rows[0].update(basis="stated"))
        self.assertTrue(any("never hand-edited" in p for p in self.problems()))

    def test_value_with_no_row_fails(self):  # planted defect
        self.t.lines(lambda rows: rows.pop())
        self.assertTrue(any("has no basis row" in p for p in self.problems()))

    def test_duplicate_key_fails(self):  # planted defect
        self.t.lines(lambda rows: rows.append(dict(rows[0])))
        self.assertTrue(any("duplicate key" in p for p in self.problems()))

    def test_row_for_a_value_the_record_does_not_hold_fails(self):  # planted defect
        self.t.lines(lambda rows: rows.append({**rows[0], "value": "lamination"}))
        self.assertTrue(any("does not hold" in p for p in self.problems()))

    def test_stated_row_with_no_proof_fails(self):  # planted defect: a stated row the evidence cannot back
        self.t.lines(lambda rows: rows[0].update(basis="stated", basis_date="2026-11-24"))
        self.assertTrue(any("generation gives not_yet_checked" in p for p in self.problems()))

    def test_stale_proof_after_an_evidence_edit_is_caught_on_regeneration(self):  # planted defect
        e = ev("EVD-1", "SITE-1", QUOTED)
        t = Tree([e])
        t.add_proof(e)
        t.write_table()
        self.assertEqual(t.check(), [])
        write(t.root / "data" / "evidence_sites_OH.csv", [{**e, "claim_detail": QUOTED + " (edited)"}], EVD_COLS)
        self.assertTrue(any("stated" in p and "not_yet_checked" in p for p in t.check()))

    def test_published_value_no_row_names_still_needs_its_row(self):  # planted defect: the unnamed value's row removed
        t = Tree([ev("EVD-1", "SITE-1", "unrelated row")])
        t.write_table()
        self.assertEqual(t.check(), [])
        t.lines(lambda rows: rows.clear())
        self.assertTrue(any("has no basis row" in p and "custom_compounding" in p for p in t.check()))

    def test_unnamed_value_row_carrying_an_evidence_id_or_a_stronger_basis_fails(self):  # planted defect
        t = Tree([ev("EVD-1", "SITE-1", "unrelated row")])
        t.write_table()
        t.lines(lambda rows: rows[0].update(evidence_id="EVD-1"))
        self.assertTrue(any("never hand-edited" in p for p in t.check()))

    def test_missing_table_and_bad_header_fail(self):
        (self.t.root / "data" / "value_basis.csv").write_text("record_table,record_id\n")
        self.assertTrue(any("header must be" in p for p in self.problems()))
        (self.t.root / "data" / "value_basis.csv").unlink()
        self.assertTrue(any("is missing" in p for p in self.problems()))


class RepoTable(unittest.TestCase):
    def test_the_committed_table_equals_a_fresh_generation(self):
        problems, info = vb.check()
        self.assertEqual(problems, [])
        self.assertGreater(info["held"], 0)


if __name__ == "__main__":
    unittest.main()
