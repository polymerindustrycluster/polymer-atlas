"""Tests for scripts/atlas.py. Fixture CSV trees are built in a tempdir; only the
last test touches the real data/ (read-only smoke test)."""
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("atlas", HERE / "atlas.py")
atlas = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(atlas)

ORG_COLS = ["org_id", "legal_name", "trade_names", "successor_org_id", "hq_city", "hq_state", "website",
            "status", "verification_tier", "notes"]
ECO_COLS = ["org_id", "legal_name", "city", "state", "website", "status", "verification_tier", "notes"]
SITE_COLS = ["site_id", "org_id", "site_name", "city", "state", "zip", "street_address", "operating_status",
             "verification_tier", "site_group_id", "country", "processes_other_note", "materials_other_note"]
EVD_COLS = ["evidence_id", "record_table", "record_id", "claim_type", "source_class", "observed_date",
            "tier_effect", "source_ref"]
REL_COLS = ["relationship_id", "from_org_id", "relationship_type", "to_org_id", "basis"]
REG_COLS = ["org_id", "registry", "registry_id", "match_basis", "as_of"]


def write(d, name, cols, rows):
    with open(Path(d) / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def org(i, name, **kw):
    return {"org_id": i, "legal_name": name, "status": "active", "verification_tier": "B", **kw}


def site(i, o, street, city="Akron", state="OH", **kw):
    return {"site_id": i, "org_id": o, "site_name": f"{o} site", "street_address": street, "city": city, "state": state,
            "operating_status": "active", "verification_tier": "B", "country": "US", **kw}


def build_tree(d):
    write(d, "organizations_OH.csv", ORG_COLS, [
        org("ORG-000001", "The Acme Plastics, Inc.", trade_names="Acme; OldCo Plastics", website="https://www.acme-plastics.com/about",
            hq_city="Akron", hq_state="OH"),
        org("ORG-000004", "Beta Rubber & Polymer LLC", website="http://beta-rubber.com", hq_city="Canton", hq_state="OH",
            notes="Acquired Gamma Seals in 2020", successor_org_id="ORG-000900"),
        org("ORG-000005", "Linkedin Page Co", website="https://www.linkedin.com/company/linkedin-page-co", hq_state="OH"),
    ])
    write(d, "organizations_TX.csv", ORG_COLS, [
        org("ORG-000900", "Delta Holdings Corporation", successor_org_id="ORG-000901", hq_city="Houston", hq_state="TX",
            website="https://delta.example.com"),
        org("ORG-000901", "Epsilon Group", hq_city="Dallas", hq_state="TX", status="active"),
    ])
    write(d, "organizations_US.csv", ORG_COLS, [org("ORG-000020", "Residual Resins", website="https://us.beta-rubber.com")])
    write(d, "ecosystem.csv", ECO_COLS, [
        org("ORG-000502", "Univ Polymer Center", city="Akron", state="OH", website="https://uakron.edu/polymers")])
    write(d, "sites_OH.csv", SITE_COLS, [
        site("SITE-000001", "ORG-000001", "100 North Main Street, Suite 4", zip="44301", site_group_id="GRP-000001"),
        site("SITE-000002", "ORG-000004", "55 Oak Ave", city="Canton", zip="44702", site_group_id="GRP-000001"),
    ])
    write(d, "sites_TX.csv", SITE_COLS, [
        site("SITE-000010", "ORG-000900", "100 N Main St", city="Houston", state="TX", zip="77001"),
        site("SITE-000500", "ORG-000902", "9 Dangling Rd", city="Houston", state="TX"),   # org 902 does not exist
    ])
    write(d, "evidence.csv", EVD_COLS, [
        {"evidence_id": "EVD-000001", "record_table": "organizations", "record_id": "ORG-000001", "claim_type": "existence",
         "source_class": "own_site", "observed_date": "2026-10-01", "tier_effect": "supports_A", "source_ref": "https://x"},
        {"evidence_id": "EVD-000007", "record_table": "organizations", "record_id": "ORG-009999", "claim_type": "existence",
         "source_class": "own_site", "observed_date": "2026-10-01", "tier_effect": "supports_A", "source_ref": "https://y"},
    ])
    write(d, "relationships.csv", REL_COLS, [
        {"relationship_id": "REL-000003", "from_org_id": "ORG-000004", "relationship_type": "successor_of", "to_org_id": "ORG-000900",
         "basis": "generated"}])
    write(d, "registry_links.csv", REG_COLS, [
        {"org_id": "ORG-000001", "registry": "TRI_TRIFID", "registry_id": "44301ACME", "match_basis": "x", "as_of": "2026-10-01"}])


def run(argv, data_dir):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = atlas.main(["--data-dir", str(data_dir)] + argv)
    return rc, out.getvalue(), err.getvalue()


def tree_hash(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).glob("*")):
        h.update(p.name.encode() + p.read_bytes() + str(p.stat().st_mtime_ns).encode())
    return h.hexdigest()


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.d = self._tmp.name
        build_tree(self.d)


class NextIdTests(FixtureCase):
    def rep(self, prefix):
        rc, out, _ = run(["next-id", prefix, "--json"], self.d)
        self.assertEqual(rc, 0)
        return json.loads(out)["prefixes"][0]

    def test_org_namespace_spans_shards_and_ecosystem_and_never_fills_gaps(self):
        r = self.rep("ORG")
        self.assertEqual(r["max_id"], "ORG-000901")           # TX shard holds the max
        self.assertEqual(r["next_id"], "ORG-000902")          # gaps (000002, 000003...) are not reused
        self.assertEqual(r["count"], 7)                       # 3 OH + 2 TX + 1 US + 1 ecosystem
        self.assertEqual(sorted(r["pk_columns"]), ["ecosystem.org_id", "organizations.org_id"])

    def test_foreign_key_columns_do_not_count_toward_max_but_are_reported(self):
        # evidence.record_id points at ORG-009999 (no such record); sites TX points at ORG-000902
        r = self.rep("ORG")
        self.assertEqual(r["max_id"], "ORG-000901")
        self.assertIn("ORG-009999", r["referenced_above_max"])
        self.assertEqual(r["next_id"], "ORG-000902")
        self.assertEqual(r["next_id_avoiding_refs"], "ORG-010000")
        self.assertTrue(any("exceed the primary-key max" in w for w in r["warnings"]))

    def test_width_preserved_and_other_prefixes_discovered(self):
        self.assertEqual(self.rep("SITE")["next_id"], "SITE-000501")
        self.assertEqual(self.rep("EVD")["next_id"], "EVD-000008")
        self.assertEqual(self.rep("REL")["next_id"], "REL-000004")
        rc, out, _ = run(["next-id", "--all", "--json"], self.d)
        self.assertEqual({p["prefix"] for p in json.loads(out)["prefixes"]}, {"ORG", "SITE", "EVD", "REL", "GRP"})

    def test_shared_group_ids_are_not_duplicates(self):
        r = self.rep("GRP")
        self.assertEqual(r["next_id"], "GRP-000002")
        self.assertEqual(r["duplicates"], {})

    def test_duplicate_primary_key_across_shards_is_flagged(self):
        write(self.d, "organizations_PA.csv", ORG_COLS, [org("ORG-000004", "Collision Corp", hq_state="PA")])
        r = self.rep("ORG")
        self.assertIn("ORG-000004", r["duplicates"])
        self.assertEqual(sorted(r["duplicates"]["ORG-000004"]), ["organizations_OH.csv", "organizations_PA.csv"])

    def test_audit_lists_dangling_references(self):
        rc, out, _ = run(["next-id", "--all", "--audit", "--json"], self.d)
        dang = json.loads(out)["dangling_references"]
        self.assertIn("ORG-009999", dang["evidence.record_id"])
        self.assertIn("ORG-000902", dang["sites.org_id"])

    def test_unknown_prefix(self):
        rc, _, err = run(["next-id", "NOPE"], self.d)
        self.assertEqual(rc, 2)
        self.assertIn("unknown prefix", err)

    def test_text_output(self):
        rc, out, _ = run(["next-id", "org"], self.d)
        self.assertEqual(rc, 0)
        self.assertIn("ORG-000902", out)


class ReadOnlyTests(FixtureCase):
    def test_no_subcommand_modifies_the_tree(self):
        before = tree_hash(self.d)
        for argv in (["next-id", "--all", "--audit"], ["dedupe-check", "--name", "Acme", "--domain", "acme-plastics.com",
                     "--street", "100 N Main"], ["show", "ORG-000001"], ["show", "SITE-000001", "--json"],
                     ["shard-of", "--hq-state", "OH"]):
            run(argv, self.d)
        self.assertEqual(before, tree_hash(self.d))


class NormalizerTests(unittest.TestCase):
    def test_domain_key(self):
        k = atlas.domain_key
        self.assertEqual(k("HTTPS://WWW.Acme.com/about?x=1"), "acme.com")
        self.assertEqual(k("acme.com:8080/"), "acme.com")
        self.assertEqual(k(""), "")
        self.assertEqual(k("https://www.linkedin.com/company/foo/"), "linkedin.com/company/foo")

    def test_name_key(self):
        k = atlas.name_key
        self.assertEqual(k("The Acme Plastics, Inc."), "acme plastics")
        self.assertEqual(k("ACME  Plastics Co."), "acme plastics")
        self.assertEqual(k("Beta Rubber & Polymer LLC"), "beta rubber and polymer")
        self.assertEqual(k("The Company"), "the company")     # never normalize to empty

    def test_site_name_key_strips_only_a_trailing_city_suffix(self):
        k = atlas.site_name_key
        self.assertEqual(k("IFS Coatings - Ardmore", "Ardmore"), "ifs coatings")
        self.assertEqual(k("IFS Coatings \u2014 ARDMORE", "Ardmore"), "ifs coatings")     # SCHEMA default uses the em dash
        self.assertEqual(k("IFS Coatings (Ardmore)", "Ardmore"), "ifs coatings")
        self.assertEqual(k("Boomerang Rubber, Inc. \u2014 Botkins (Dinsmore St. Campus)", "Botkins"), "boomerang rubber")
        self.assertEqual(k("Acme \u2014 Akron (Plant 2)", "Akron"), "acme")
        self.assertEqual(k("IFS Coatings - Annex", "Ardmore"), "ifs coatings annex")        # suffix is not the city
        self.assertEqual(k("Orange County Plastics", "Orange"), "orange county plastics")   # no separator, nothing stripped
        self.assertEqual(k("IFS Coatings - Ardmore", ""), "ifs coatings ardmore")           # no city, nothing stripped

    def test_street_key(self):
        k = atlas.street_key
        self.assertEqual(k("100 North Main Street, Suite 4"), k("100 N. Main St"))
        self.assertEqual(k("55 Oak Avenue #12"), "55 oak ave")
        self.assertEqual(k("1200 State Road Unit B"), "1200 state rd")
        self.assertNotEqual(k("100 N Main St"), k("100 S Main St"))


class DedupeTests(FixtureCase):
    def dd(self, *argv):
        rc, out, _ = run(["dedupe-check", "--json", *argv], self.d)
        return rc, json.loads(out)

    def ids(self, res, step):
        return [h["id"] for h in res["steps"][step - 1]["hits"]]

    def test_domain_hit_stops_at_step_1_and_later_steps_still_listed(self):
        rc, res = self.dd("--domain", "http://acme-plastics.com/x", "--name", "Acme Plastics")
        self.assertEqual(rc, 1)
        self.assertEqual(res["stop_at_step"], 1)
        self.assertEqual(self.ids(res, 1), ["ORG-000001"])
        self.assertEqual(self.ids(res, 2), ["ORG-000001"])    # information-only, still reported

    def test_domain_checks_ecosystem_and_subdomains_not_platform_hosts(self):
        _, res = self.dd("--domain", "https://www.uakron.edu")
        self.assertEqual(self.ids(res, 1), ["ORG-000502"])
        _, res = self.dd("--domain", "beta-rubber.com")
        self.assertEqual(sorted(self.ids(res, 1)), ["ORG-000004", "ORG-000020"])   # exact + subdomain
        self.assertEqual({h["match"].split(":")[0] for h in res["steps"][0]["hits"]}, {"domain exact", "domain subdomain"})
        _, res = self.dd("--domain", "https://www.linkedin.com/company/other-firm")
        self.assertEqual(self.ids(res, 1), [])

    def test_name_normalization_and_trade_names(self):
        _, res = self.dd("--name", "ACME PLASTICS LLC")
        self.assertEqual(self.ids(res, 2), ["ORG-000001"])
        _, res = self.dd("--name", "oldco plastics")
        self.assertEqual(self.ids(res, 2), ["ORG-000001"])
        self.assertIn("trade_names", res["steps"][1]["hits"][0]["match"])
        _, res = self.dd("--name", "beta rubber and polymer")
        self.assertEqual(self.ids(res, 2), ["ORG-000004"])

    def test_step4_notes_substring_and_successor_chain_to_terminal(self):
        _, res = self.dd("--name", "Gamma Seals")
        self.assertEqual(res["stop_at_step"], 4)
        h = res["steps"][3]["hits"][0]
        self.assertEqual(h["id"], "ORG-000004")
        self.assertEqual(h["successor_chain"], ["ORG-000900", "ORG-000901"])
        self.assertEqual(h["successor_end"], "terminal")
        self.assertIn("Epsilon Group", h["successor_terminal"])

    def test_successor_chain_cycle_and_dangling(self):
        by = {"A": [{"successor_org_id": "B"}], "B": [{"successor_org_id": "A"}], "C": [{"successor_org_id": "Z"}]}
        self.assertEqual(atlas.successor_chain("A", by), (["B", "A"], "cycle"))
        self.assertEqual(atlas.successor_chain("C", by), (["Z"], "dangling"))

    def test_street_match_normalizes_and_uses_locality(self):
        _, res = self.dd("--street", "100 N. Main St.", "--city", "Akron", "--state", "OH", "--zip", "44301")
        self.assertEqual(self.ids(res, 3), ["SITE-000001"])
        other = [h["id"] for h in res["steps"][2]["other_localities"]]
        self.assertEqual(other, ["SITE-000010"])              # same street text, Houston: listed, not counted
        self.assertEqual(res["steps"][2]["hits"][0]["operator"], "The Acme Plastics, Inc.")
        _, res = self.dd("--street", "100 North Main Street Suite 9")        # no locality: both count
        self.assertEqual(sorted(self.ids(res, 3)), ["SITE-000001", "SITE-000010"])

    def add_sites(self, *rows):
        write(self.d, "sites_IN.csv", SITE_COLS, [site(i, o, st, city=c, state="IN", site_name=n) for i, o, st, c, n in rows])

    def test_step5_site_name_hit_reports_operator_and_street(self):
        # known answer: SITE-006097 "IFS Coatings - Ardmore" sits under "Ifs Industries Inc.", so steps 1-4 miss it
        self.add_sites(("SITE-006097", "ORG-000001", "3430 Cypert Way", "Ardmore", "IFS Coatings - Ardmore"),
                       ("SITE-006098", "ORG-000004", "1 Elm St", "Canton", "IFS Coatings \u2014 Canton"),
                       ("SITE-006099", "ORG-000020", "2 Elm St", "Peru", "IFS Coatings (Peru)"))
        rc, res = self.dd("--name", "IFS Coatings")
        self.assertEqual((rc, res["stop_at_step"]), (1, 5))
        self.assertEqual(self.ids(res, 2) + self.ids(res, 4), [])
        self.assertEqual(self.ids(res, 5), ["SITE-006097", "SITE-006098", "SITE-006099"])
        h = res["steps"][4]["hits"][0]
        self.assertEqual((h["org_id"], h["operator"], h["street"]), ("ORG-000001", "The Acme Plastics, Inc.", "3430 Cypert Way"))
        _, out, _ = run(["dedupe-check", "--name", "IFS Coatings"], self.d)
        self.assertIn("STOP at step 5", out)
        self.assertIn("street: 3430 Cypert Way", out)

    def test_step5_near_misses_do_not_match(self):
        self.add_sites(("SITE-006097", "ORG-000001", "3430 Cypert Way", "Ardmore", "IFS Coatings Group - Ardmore"),
                       ("SITE-006098", "ORG-000004", "1 Elm St", "Canton", "IFS Coatings - Annex"),     # suffix is not the city
                       ("SITE-006099", "ORG-000020", "2 Elm St", "Peru", "Ifs Holdings - Peru"))
        _, res = self.dd("--name", "IFS Coatings")
        self.assertEqual(self.ids(res, 5), [])
        self.assertIsNone(res["stop_at_step"])
        # a query carrying its own city suffix matches a bare site_name when --city is given
        self.add_sites(("SITE-006100", "ORG-000001", "3430 Cypert Way", "Ardmore", "IFS Coatings"))
        _, res = self.dd("--name", "IFS Coatings - Ardmore", "--city", "Ardmore")
        self.assertEqual(self.ids(res, 5), ["SITE-006100"])

    def test_no_hits_exit_zero_and_requires_a_query(self):
        rc, res = self.dd("--name", "Totally Unknown Widgets", "--domain", "nowhere.invalid")
        self.assertEqual(rc, 0)
        self.assertIsNone(res["stop_at_step"])
        rc, _, err = run(["dedupe-check"], self.d)
        self.assertEqual(rc, 2)

    def test_text_output_has_stop_and_information_headers(self):
        rc, out, _ = run(["dedupe-check", "--domain", "acme-plastics.com", "--name", "Acme"], self.d)
        self.assertEqual(rc, 1)
        self.assertIn("STOP at step 1", out)
        self.assertIn("for information", out)


class ShowTests(FixtureCase):
    def test_org_shows_sites_evidence_relationships_registry(self):
        rc, out, _ = run(["show", "ORG-000001", "--json"], self.d)
        res = json.loads(out)
        self.assertEqual(rc, 0)
        self.assertEqual(res["records"][0]["file"], "organizations_OH.csv")
        self.assertEqual([s["site_id"] for s in res["sites"]], ["SITE-000001"])
        self.assertEqual([e["evidence_id"] for e in res["evidence"]], ["EVD-000001"])
        self.assertEqual(res["registry_links"][0]["registry"], "TRI_TRIFID")
        rc, out, _ = run(["show", "ORG-000900", "--json"], self.d)
        res = json.loads(out)
        self.assertEqual(res["relationships"][0]["relationship_id"], "REL-000003")
        self.assertEqual(res["successor_chain"]["chain"], ["ORG-000901"])

    def test_site_shows_parent_org_and_ecosystem_org_found(self):
        _, out, _ = run(["show", "SITE-000002", "--json"], self.d)
        self.assertEqual(json.loads(out)["parent_org"][0]["id"], "ORG-000004")
        rc, out, _ = run(["show", "ORG-000502"], self.d)
        self.assertEqual(rc, 0)
        self.assertIn("table=ecosystem", out)

    def test_missing_id_exit_1_but_reports_references(self):
        rc, out, _ = run(["show", "ORG-009999"], self.d)
        self.assertEqual(rc, 1)
        self.assertIn("evidence.record_id", out)

    def test_text_output(self):
        rc, out, _ = run(["show", "SITE-000001"], self.d)
        self.assertIn("-- parent org: ORG-000001", out)
        self.assertIn("-- evidence rows (0)", out)


class ShardOfTests(FixtureCase):
    def test_usps_states(self):
        for st, tag in (("ohio"[:2], "OH"), (" tx ", "TX"), ("DC", "DC"), ("PR", "PR")):
            self.assertEqual(atlas.shard_of("org", st, None)[:2], (tag, "ok"))
            self.assertEqual(atlas.shard_of("site", st, None)[:2], (tag, "ok"))

    def test_non_usps_state_needs_country(self):
        tag, status, note = atlas.shard_of("org", "QC", None)
        self.assertEqual((tag, status), (None, "needs_country"))
        self.assertIn("org_shard", note)
        rc, out, _ = run(["shard-of", "--hq-state", "QC"], self.d)
        self.assertEqual(rc, 3)

    def test_org_rules(self):
        self.assertEqual(atlas.shard_of("org", "QC", "CA")[:2], ("INTL", "ok"))
        self.assertEqual(atlas.shard_of("org", "", "")[:2], ("US", "ok"))
        self.assertEqual(atlas.shard_of("org", "", "United States")[:2], ("US", "ok"))
        self.assertEqual(atlas.shard_of("org", "", "BE")[:2], ("INTL", "ok"))

    def test_site_rules_have_no_residual(self):
        self.assertEqual(atlas.shard_of("site", "ON", "CA")[:2], ("INTL", "ok"))
        self.assertEqual(atlas.shard_of("site", "", "US")[:2], (None, "unplaceable"))
        self.assertEqual(atlas.shard_of("site", "ZZ", "")[:2], (None, "unplaceable"))
        rc, out, _ = run(["shard-of", "--site-state", "", "--country", ""], self.d)
        self.assertEqual(rc, 4)
        self.assertIn("UNPLACEABLE", out)

    def test_cli_reports_file_and_existence_json(self):
        rc, out, _ = run(["shard-of", "--hq-state", "TX", "--json"], self.d)
        res = json.loads(out)
        self.assertEqual((res["file"], res["file_exists"]), ("data/organizations_TX.csv", True))
        res = json.loads(run(["shard-of", "--site-state", "WY", "--json"], self.d)[1])
        self.assertEqual((res["file"], res["file_exists"]), ("data/sites_WY.csv", False))

    def test_exactly_one_state_option(self):
        self.assertEqual(run(["shard-of"], self.d)[0], 2)
        self.assertEqual(run(["shard-of", "--hq-state", "OH", "--site-state", "OH"], self.d)[0], 2)

    def test_usps_state_with_foreign_country_warns(self):
        _, _, note = atlas.shard_of("org", "CA", "CA")
        self.assertIn("WARNING", note)


class RealDataSmoke(unittest.TestCase):
    @unittest.skipUnless((HERE.parent / "data" / "organizations_OH.csv").exists(), "real data not present")
    def test_cli_runs_against_real_data(self):
        p = subprocess.run([sys.executable, str(HERE / "atlas.py"), "next-id", "ORG", "--json"], capture_output=True, text=True,
                           cwd=HERE.parent)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads(p.stdout)["prefixes"][0]
        self.assertGreater(int(r["next_id"].split("-")[1]), int(r["max_id"].split("-")[1]))
        self.assertEqual(r["duplicates"], {})


class StreetKey(unittest.TestCase):
    """street_key must not collapse a real street to '' (L3 finding on #164: '#6 Capper Drive' -> '' matched another blank)."""

    def test_leading_hash_building_number(self):
        self.assertEqual(atlas.street_key("#6 Capper Drive"), "6 capper dr")

    def test_unit_first_then_street(self):
        self.assertEqual(atlas.street_key("Suite 100, 200 Main St"), "200 main st")
        self.assertEqual(atlas.street_key("200 Main St, Suite 100"), "200 main st")
        self.assertEqual(atlas.street_key("200 Main St #4"), "200 main st")

    def test_digit_free_comma_street_keeps_whole_string(self):
        self.assertEqual(atlas.street_key("Ironstone House, Ironstone Way"), "ironstone house ironstone way")

    def test_digit_free_street_before_numbered_part_is_kept(self):
        # Codex on #197: SITE-016517 "Five Bottle Drive, SR 352"; postal-code control from SITE-002457/002459
        self.assertEqual(atlas.street_key("Five Bottle Drive, SR 352"), "five bottle dr sr 352")
        self.assertNotEqual(atlas.street_key("Lenni Rd., Lenni, PA 19052"), atlas.street_key("West Lenni Rd., Lenni, PA 19052"))

    def test_unit_only_is_empty(self):
        self.assertEqual(atlas.street_key("Unit 4"), "")
        self.assertEqual(atlas.street_key(""), "")


if __name__ == "__main__":
    unittest.main()
