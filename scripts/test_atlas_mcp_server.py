#!/usr/bin/env python3
"""Tests for scripts/atlas_mcp_server.py.

Calls the tool functions directly against a tiny fixture SQLite database built
in a temp dir; the real build/polymer-atlas.db is never required.  The one
wiring test (build_server) is skipped if the `mcp` package is not installed.

    python3 -m unittest scripts/test_atlas_mcp_server.py
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import atlas_mcp_server as srv  # noqa: E402

ORG_COLS = ["org_id", "legal_name", "trade_names", "parent_org_id", "ring_primary", "hq_city",
            "hq_state", "website", "status", "successor_org_id", "verification_tier"]
SITE_COLS = ["site_id", "org_id", "site_name", "site_type", "street_address", "city", "state",
             "zip", "county", "ring_primary", "naics_primary", "processes", "materials",
             "operating_status", "verification_tier"]
ECO_COLS = ["org_id", "legal_name", "city", "state", "website", "status", "verification_tier",
            "parent_institution_org_id"]
PEOPLE_COLS = ["person_id", "full_name", "institution_org_id", "program_org_id", "role",
               "role_as_published", "research_specialties", "public_profile_url", "sources",
               "verification_tier", "last_verified", "secret_email"]  # extra col must never leak
PROG_COLS = ["program_id", "institution_org_id", "program_name", "program_type", "level",
             "credential_types", "unit_department", "description_1line", "research_areas",
             "specialty_processes", "specialty_materials", "admissions_status", "city", "state",
             "county", "status", "url", "sources", "verification_tier", "last_verified"]
EVD_COLS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail",
            "source_class", "source_ref", "observed_date", "tier_effect"]
REL_COLS = ["relationship_id", "from_org_id", "relationship_type", "to_org_id", "effective_from",
            "effective_to", "basis", "source_ref"]
REG_COLS = ["org_id", "registry", "registry_id", "match_basis", "as_of"]
CAP_COLS = ["capability_id", "site_id", "org_id", "capability_type", "term", "provenance",
            "source_ref", "observed_date", "withdrawn_date"]
EVT_COLS = ["event_id", "name", "organizer_org_id"]
EVP_COLS = ["participation_id", "event_id", "org_id", "edition_year", "role", "verification_tier"]


def _make(con, name, cols, rows):
    con.execute(f'CREATE TABLE {name} ({", ".join(c + " TEXT" for c in cols)})')
    con.executemany(f'INSERT INTO {name} VALUES ({",".join("?" * len(cols))})', rows)


def build_fixture(path: Path) -> None:
    con = sqlite3.connect(path)
    _make(con, "organizations", ORG_COLS, [
        ("ORG-000001", "Acme Plastics Inc", "Acme; Acme Molding", None, "1", "Akron", "OH", "https://acme-plastics.com", "active", None, "A"),
        ("ORG-000002", "Acme Holdings LLC", None, None, "3", "Dallas", "TX", "https://acmeholdings.example", "active", None, "B"),
        ("ORG-000003", "Beta Rubber Co", None, "ORG-000002", "1", "Canton", "OH", None, "active", None, "B"),
        ("ORG-000004", "100% Poly_mer", None, None, "2", "Erie", "PA", None, "closed", "ORG-000001", "U"),
    ])
    _make(con, "sites", SITE_COLS, [
        ("SITE-000001", "ORG-000001", "Acme Akron", "manufacturing_plant", "1 Main St", "Akron", "OH", "44301", "Summit", "1", "326199", "injection_molding;extrusion", "thermoplastics", "active", "A"),
        ("SITE-000002", "ORG-000001", "Acme Canton", "manufacturing_plant", "2 Main St", "Canton", "OH", "44702", "Stark", None, "326199", "blow_molding", "thermoplastics;elastomers_rubber", "active", "B"),
        ("SITE-000003", "ORG-000003", "Beta Canton", "manufacturing_plant", "3 Main St", "Canton", "OH", "44702", "Stark", "1", "326211", "extrusion_profile", "elastomers_rubber", "closed", "B"),
        ("SITE-000004", "ORG-000002", "Acme Dallas HQ", "headquarters", "4 Main St", "Dallas", "TX", "75001", "Dallas", "3", "551114", None, None, "active", "B"),
        ("SITE-000005", "ORG-000001", "Acme Erie", "manufacturing_plant", "5 Main St", "Erie", "PA", "16501", "Erie", "1", "3261", "inject_ion", None, "active", "C"),
    ])
    _make(con, "ecosystem", ECO_COLS, [
        ("ORG-000501", "University of Akron", "Akron", "OH", "https://uakron.edu", "active", "A", None),
        ("ORG-000502", "Akron Polymer Training Center", "Akron", "OH", None, "active", "U", "ORG-000501"),
    ])
    _make(con, "people", PEOPLE_COLS, [
        ("PERSON-000001", "Ada Lovelace", "ORG-000501", "PROG-000001", "professor", "Professor of Polymer Science",
         "polymer_synthesis;recycling_circularity", "https://uakron.edu/ada", "https://uakron.edu/ada", "A", "2026-10-29", "ada@private.example"),
        ("PERSON-000002", "Grace Hopper", "ORG-000501", None, "associate_professor", "Associate Professor",
         "coatings", "https://uakron.edu/grace", "https://uakron.edu/grace", "A", "2026-10-29", "grace@private.example"),
    ])
    _make(con, "programs", PROG_COLS, [
        ("PROG-000001", "ORG-000501", "Polymer Engineering BS", "degree", "bachelor", "bs", "Engineering", "Polymer engineering degree",
         "polymer_synthesis", "extrusion", "thermoplastics", "admitting", "Akron", "OH", "Summit", "active", "https://uakron.edu/p", "https://uakron.edu/p", "A", "2026-10-30"),
        ("PROG-000002", "ORG-000501", "Marine Biology", "degree", "bachelor", "bs", "Biology", "Fish", None, None, None, "admitting", "Akron", "OH", "Summit", "active", None, "x", "B", "2026-10-30"),
    ])
    con.execute("CREATE VIEW institution_programs AS SELECT p.*, e.legal_name AS institution_name "
                "FROM programs p LEFT JOIN ecosystem e ON e.org_id = p.institution_org_id")
    _make(con, "evidence", EVD_COLS, [
        ("EVD-000001", "organizations", "ORG-000001", "existence", "Acme exists", "own_site", "https://acme-plastics.com", "2026-10-30", "supports_A"),
        ("EVD-000002", "sites", "SITE-000001", "existence", "plant exists", "own_site", "https://acme-plastics.com/akron", "2026-10-30", "supports_A"),
        ("EVD-000003", "organizations", "ORG-000002", "existence", "Holdings exists", "sos", "https://sos.example", "2026-10-30", "supports_B"),
    ])
    _make(con, "relationships", REL_COLS, [
        ("REL-000001", "ORG-000002", "parent_of", "ORG-000003", None, None, "generated", "organizations.csv"),
    ])
    _make(con, "registry_links", REG_COLS, [("ORG-000001", "LEI", "ABC123", "exact", "2026-10-28")])
    _make(con, "site_capabilities", CAP_COLS, [
        ("CAP-000001", "SITE-000001", "ORG-000001", "process", "injection_molding", "company_disclosed", "https://acme-plastics.com", "2026-10-29", None),
        ("CAP-000002", "SITE-000002", "ORG-000001", "material", "elastomers_rubber", "company_disclosed", "https://acme-plastics.com", "2026-10-29", None),
        ("CAP-000003", "SITE-000003", "ORG-000003", "material", "elastomers_rubber", "directory_assigned", "https://dir.example", "2026-10-29", "2026-10-31"),
    ])
    con.execute("CREATE VIEW org_capability_rollup AS SELECT org_id, capability_type, term, count(*) AS site_count, "
                "max(observed_date) AS latest_observed_date FROM site_capabilities GROUP BY org_id, capability_type, term")
    _make(con, "events", EVT_COLS, [("EVT-000001", "NPE", "ORG-000501")])
    _make(con, "event_participation", EVP_COLS, [("EPA-000001", "EVT-000001", "ORG-000001", "2024", "exhibitor", "B")])
    con.commit()
    con.close()


class AtlasToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls._tmp.name) / "fixture.db"
        build_fixture(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        srv.configure(self.db)

    # ---- provenance -------------------------------------------------------
    def test_as_of_on_every_tool(self):
        for res in (
            srv.search_organizations("acme"), srv.get_record("ORG-000001"), srv.find_sites(),
            srv.find_capabilities("rubber"), srv.find_programs(), srv.find_people(),
            srv.run_select("select 1 as x"), srv.schema_info(),
        ):
            self.assertIn("as_of", res)
            self.assertIn("git_head", res["as_of"])
            self.assertRegex(res["as_of"]["db_built_utc"], r"^\d{4}-\d\d-\d\dT")
            self.assertIn("cite", res["as_of"])

    def test_missing_db_has_helpful_error(self):
        srv.configure(Path(self._tmp.name) / "nope.db")
        with self.assertRaises(srv.AtlasError) as cm:
            srv.schema_info()
        self.assertIn("build_sqlite.py", str(cm.exception))

    # ---- search_organizations --------------------------------------------
    def test_search_name_and_trade_names(self):
        r = srv.search_organizations("acme")
        self.assertEqual(r["total_matching"], 2)
        self.assertEqual({x["org_id"] for x in r["rows"]}, {"ORG-000001", "ORG-000002"})
        r = srv.search_organizations("molding")  # trade name only
        self.assertEqual([x["org_id"] for x in r["rows"]], ["ORG-000001"])

    def test_search_filters_and_limit(self):
        self.assertEqual([x["org_id"] for x in srv.search_organizations("acme", state="tx")["rows"]], ["ORG-000002"])
        self.assertEqual([x["org_id"] for x in srv.search_organizations("acme", ring=1)["rows"]], ["ORG-000001"])
        self.assertEqual(srv.search_organizations("acme", limit=1)["returned"], 1)
        self.assertEqual(srv.search_organizations("acme", limit=1)["total_matching"], 2)

    def test_search_like_wildcards_are_literal(self):
        self.assertEqual(srv.search_organizations("%")["total_matching"], 1)  # only '100% Poly_mer'
        self.assertEqual(srv.search_organizations("poly_mer")["total_matching"], 1)
        self.assertEqual(srv.search_organizations("polyxmer")["total_matching"], 0)

    def test_search_domain_and_ecosystem(self):
        self.assertEqual(srv.search_organizations("acme-plastics.com")["rows"][0]["org_id"], "ORG-000001")
        self.assertEqual(srv.search_organizations("akron")["total_matching"], 0)
        r = srv.search_organizations("akron", include_ecosystem=True)
        self.assertEqual(r["total_matching"], 2)
        self.assertTrue(all(x["record_table"] == "ecosystem" and x["ring_primary"] == "5" for x in r["rows"]))

    def test_search_requires_query(self):
        with self.assertRaises(srv.AtlasError):
            srv.search_organizations("  ")

    # ---- get_record -------------------------------------------------------
    def test_get_org_links(self):
        r = srv.get_record("org-000002")
        self.assertEqual(r["record"]["legal_name"], "Acme Holdings LLC")
        self.assertEqual([c["org_id"] for c in r["children"]], ["ORG-000003"])
        self.assertEqual(r["sites_total"], 1)
        self.assertEqual(r["evidence"]["total"], 1)
        self.assertEqual(r["relationships"][0]["relationship_id"], "REL-000001")
        r = srv.get_record("ORG-000003")
        self.assertEqual(r["parent"]["org_id"], "ORG-000002")
        r = srv.get_record("ORG-000004")
        self.assertEqual(r["successor"]["org_id"], "ORG-000001")
        r = srv.get_record("ORG-000001")
        self.assertEqual(r["registry_links"][0]["registry"], "LEI")
        self.assertEqual(r["sites_total"], 3)
        self.assertTrue(r["capability_rollup"])
        self.assertEqual(r["event_participation"][0]["event_id"], "EVT-000001")

    def test_get_ecosystem_org(self):
        r = srv.get_record("ORG-000501")
        self.assertEqual(r["record_table"], "ecosystem")
        self.assertEqual([p["program_id"] for p in r["programs"]], ["PROG-000001", "PROG-000002"])
        self.assertEqual(r["people_total"], 2)
        r = srv.get_record("ORG-000502")
        self.assertEqual(r["parent_institution"]["org_id"], "ORG-000501")

    def test_get_other_ids(self):
        r = srv.get_record("SITE-000001")
        self.assertEqual(r["organization"]["org_id"], "ORG-000001")
        self.assertEqual(r["evidence"]["total"], 1)
        self.assertEqual(r["capabilities"][0]["term"], "injection_molding")
        self.assertEqual(srv.get_record("PROG-000001")["people"][0]["person_id"], "PERSON-000001")
        self.assertEqual(srv.get_record("EVD-000002")["subject"]["site_id"], "SITE-000001")
        self.assertEqual(srv.get_record("REL-000001")["to_org"]["org_id"], "ORG-000003")
        self.assertEqual(srv.get_record("CAP-000001")["site"]["site_id"], "SITE-000001")
        self.assertEqual(srv.get_record("EVT-000001")["participation_total"], 1)

    def test_person_record_exposes_only_public_columns(self):
        r = srv.get_record("PERSON-000001")
        self.assertEqual(set(r["record"]), set(srv.PEOPLE_PUBLIC_COLUMNS))
        self.assertNotIn("secret_email", r["record"])
        self.assertEqual(r["institution"]["org_id"], "ORG-000501")
        self.assertEqual(r["program"]["program_id"], "PROG-000001")
        # nested people lists on other records are filtered too
        for p in srv.get_record("ORG-000501")["people"] + srv.get_record("PROG-000001")["people"]:
            self.assertNotIn("secret_email", p)

    def test_get_record_errors(self):
        for bad in ("", "FOO-000001", "ORG-999999", "SITE-999999"):
            with self.assertRaises(srv.AtlasError, msg=bad):
                srv.get_record(bad)

    # ---- find_sites -------------------------------------------------------
    def ids(self, res):
        return [r["site_id"] for r in res["rows"]]

    def test_find_sites_defaults_to_active(self):
        r = srv.find_sites()
        self.assertEqual(r["total_matching"], 4)
        self.assertNotIn("SITE-000003", self.ids(r))
        self.assertEqual(srv.find_sites(operating_status="any")["total_matching"], 5)
        self.assertEqual(srv.find_sites(operating_status=None)["total_matching"], 5)
        self.assertEqual(self.ids(srv.find_sites(operating_status="closed")), ["SITE-000003"])

    def test_find_sites_geo_and_naics(self):
        self.assertEqual(self.ids(srv.find_sites(state="oh", county="Stark County")), ["SITE-000002"])
        self.assertEqual(self.ids(srv.find_sites(state="OH", county="summit")), ["SITE-000001"])
        self.assertEqual(set(self.ids(srv.find_sites(naics_prefix="3261"))), {"SITE-000001", "SITE-000002", "SITE-000005"})
        with self.assertRaises(srv.AtlasError):
            srv.find_sites(naics_prefix="32x")

    def test_find_sites_process_is_token_match_not_substring(self):
        self.assertEqual(self.ids(srv.find_sites(process="extrusion")), ["SITE-000001"])  # not extrusion_profile (closed anyway)
        self.assertEqual(self.ids(srv.find_sites(process="extrusion", operating_status="any")), ["SITE-000001"])
        self.assertEqual(self.ids(srv.find_sites(process="molding")), [])               # substring of injection_molding
        self.assertEqual(self.ids(srv.find_sites(process="injection_molding")), ["SITE-000001"])
        self.assertEqual(self.ids(srv.find_sites(process="INJECTION_MOLDING; extrusion")), ["SITE-000001"])
        self.assertEqual(self.ids(srv.find_sites(process="injection_molding;blow_molding")), [])
        self.assertEqual(self.ids(srv.find_sites(process="injectionxmolding")), [])      # '_' not a wildcard

    def test_find_sites_material_token_match(self):
        self.assertEqual(self.ids(srv.find_sites(material="elastomers_rubber")), ["SITE-000002"])
        self.assertEqual(set(self.ids(srv.find_sites(material="thermoplastics"))), {"SITE-000001", "SITE-000002"})
        self.assertEqual(self.ids(srv.find_sites(material="plastics")), [])

    def test_find_sites_ring_falls_back_to_org(self):
        # SITE-000002 has NULL ring_primary; operating org ORG-000001 is Ring 1
        self.assertIn("SITE-000002", self.ids(srv.find_sites(ring="1")))
        self.assertEqual(self.ids(srv.find_sites(ring=3)), ["SITE-000004"])

    def test_find_sites_total_vs_limit_and_unit(self):
        r = srv.find_sites(limit=1)
        self.assertEqual((r["returned"], r["total_matching"]), (1, 4))
        self.assertIn("sites", r["unit"])
        self.assertEqual(r["rows"][0]["org_name"], "Acme Plastics Inc")

    # ---- find_capabilities -----------------------------------------------
    def test_find_capabilities(self):
        r = srv.find_capabilities("rubber")
        self.assertEqual([x["capability_id"] for x in r["rows"]], ["CAP-000002"])  # CAP-3 withdrawn
        r = srv.find_capabilities("rubber", include_withdrawn=True)
        self.assertEqual(r["total_matching"], 2)
        self.assertEqual(r["distinct_sites_matching"], 2)
        self.assertEqual(srv.find_capabilities("rubber", state="TX")["total_matching"], 0)
        self.assertEqual(srv.find_capabilities("injection")["rows"][0]["org_name"], "Acme Plastics Inc")
        with self.assertRaises(srv.AtlasError):
            srv.find_capabilities("")

    # ---- find_programs / find_people -------------------------------------
    def test_find_programs(self):
        r = srv.find_programs("polymer")
        self.assertEqual([p["program_id"] for p in r["rows"]], ["PROG-000001"])
        self.assertEqual(r["rows"][0]["institution_name"], "University of Akron")
        self.assertEqual(srv.find_programs(state="OH")["total_matching"], 2)
        self.assertEqual(srv.find_programs("thermoplastics")["total_matching"], 1)
        self.assertEqual(srv.find_programs(state="TX")["total_matching"], 0)

    def test_find_people_public_columns_only(self):
        r = srv.find_people()
        self.assertEqual(r["total_matching"], 2)
        allowed = set(srv.PEOPLE_PUBLIC_COLUMNS) | {"institution_name"}
        for row in r["rows"]:
            self.assertLessEqual(set(row), allowed)
            self.assertNotIn("secret_email", row)
        self.assertNotIn("private.example", repr(r))

    def test_find_people_filters(self):
        self.assertEqual([p["full_name"] for p in srv.find_people(specialty="recycling_circularity")["rows"]], ["Ada Lovelace"])
        self.assertEqual(srv.find_people(specialty="recycling")["total_matching"], 0)  # token, not substring
        self.assertEqual(srv.find_people(institution="akron")["total_matching"], 2)
        self.assertEqual(srv.find_people(institution="ORG-000501", specialty="coatings")["rows"][0]["full_name"], "Grace Hopper")
        self.assertEqual(srv.find_people(institution="Ohio State")["total_matching"], 0)

    # ---- run_select -------------------------------------------------------
    def test_run_select_ok(self):
        r = srv.run_select("SELECT count(*) AS n FROM sites WHERE state='OH'")
        self.assertEqual(r["rows"], [{"n": 3}])
        self.assertEqual(r["columns"], ["n"])
        r = srv.run_select("WITH t AS (SELECT state FROM sites) SELECT state, count(*) c FROM t GROUP BY 1 ORDER BY 1;")
        self.assertEqual(r["returned"], 3)
        r = srv.run_select("select 'a;b' as x -- trailing comment\n;  ")
        self.assertEqual(r["rows"], [{"x": "a;b"}])
        r = srv.run_select("select site_id from sites where has_token(processes, 'extrusion')")
        self.assertEqual([x["site_id"] for x in r["rows"]], ["SITE-000001"])

    def test_run_select_row_cap(self):
        r = srv.run_select("SELECT site_id FROM sites", limit=2)
        self.assertEqual((r["returned"], r["truncated"]), (2, True))
        r = srv.run_select("SELECT site_id FROM sites", limit=10)
        self.assertEqual((r["returned"], r["truncated"]), (5, False))
        r = srv.run_select("WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i+1 FROM n WHERE i<5000) SELECT i FROM n", limit=10**6)
        self.assertEqual(r["returned"], srv.MAX_RUN_SELECT_ROWS)
        self.assertTrue(r["truncated"])

    def test_run_select_rejects_writes_and_ddl(self):
        bad = [
            "INSERT INTO sites (site_id) VALUES ('SITE-X')",
            "insert into organizations select * from organizations",
            "UPDATE sites SET city='X'",
            "DELETE FROM sites",
            "REPLACE INTO sites (site_id) VALUES ('X')",
            "DROP TABLE sites",
            "CREATE TABLE t (a)",
            "ALTER TABLE sites ADD COLUMN z",
            "ATTACH DATABASE ':memory:' AS m",
            "ATTACH DATABASE '/tmp/evil.db' AS evil",
            "DETACH DATABASE main",
            "PRAGMA query_only=OFF",
            "PRAGMA writable_schema=ON",
            "PRAGMA journal_mode=DELETE",
            "VACUUM",
            "VACUUM INTO '/tmp/copy.db'",
            "BEGIN",
            "COMMIT",
            "EXPLAIN SELECT 1",
            "",
            "   ;  ",
            "-- only a comment",
        ]
        for sql in bad:
            with self.subTest(sql=sql), self.assertRaises(srv.AtlasError):
                srv.run_select(sql)

    def test_run_select_rejects_cte_wrapped_writes(self):
        for sql in (
            "WITH t AS (SELECT 1) INSERT INTO sites (site_id) SELECT 'X' FROM t",
            "WITH t AS (SELECT 1) UPDATE sites SET city='X'",
            "WITH t AS (SELECT 1) DELETE FROM sites",
        ):
            with self.subTest(sql=sql), self.assertRaises(srv.AtlasError):
                srv.run_select(sql)
        self.assertEqual(srv.run_select("select count(*) n from sites")["rows"], [{"n": 5}])

    def test_run_select_rejects_multiple_statements(self):
        for sql in (
            "SELECT 1; SELECT 2",
            "SELECT 1; DELETE FROM sites",
            "SELECT 1;; SELECT 2",
            "SELECT 1; -- c\nSELECT 2",
            "SELECT 1 /* c */ ; /* d */ DROP TABLE sites",
            "SELECT 'x'; 'y'",
        ):
            with self.subTest(sql=sql), self.assertRaises(srv.AtlasError):
                srv.run_select(sql)

    def test_run_select_hidden_write_inside_comment_or_string_is_inert(self):
        r = srv.run_select("SELECT 'DELETE FROM sites; DROP TABLE sites' AS s /* ; DELETE FROM sites */")
        self.assertEqual(r["rows"][0]["s"], "DELETE FROM sites; DROP TABLE sites")
        self.assertEqual(srv.run_select("select count(*) n from sites")["rows"], [{"n": 5}])

    def test_connection_is_physically_read_only(self):
        con = srv._connect()
        try:
            for stmt in ("DELETE FROM sites", "CREATE TABLE zz (a)", "INSERT INTO sites (site_id) VALUES ('X')"):
                with self.subTest(stmt=stmt), self.assertRaises(sqlite3.OperationalError):
                    con.execute(stmt)
            self.assertEqual(con.execute("PRAGMA query_only").fetchone()[0], 1)
        finally:
            con.close()
        # and the file itself is untouched
        chk = sqlite3.connect(self.db)
        self.assertEqual(chk.execute("select count(*) from sites").fetchone()[0], 5)
        chk.close()

    def test_mode_ro_even_without_query_only(self):
        uri = f"file:{self.db.as_posix()}?mode=ro"
        con = sqlite3.connect(uri, uri=True)
        with self.assertRaises(sqlite3.OperationalError):
            con.execute("DELETE FROM sites")
        con.close()

    # ---- schema_info ------------------------------------------------------
    def test_schema_info(self):
        r = srv.schema_info()
        by = {t["name"]: t for t in r["tables"]}
        self.assertEqual(by["sites"]["rows"], 5)
        self.assertEqual(by["sites"]["type"], "table")
        self.assertIn("site_id", by["sites"]["columns"])
        self.assertEqual(by["institution_programs"]["type"], "view")
        self.assertIn("docs/SCHEMA.md", r["docs"]["schema"])
        self.assertIn("AGENTS.md", r["docs"]["protocol"])
        self.assertIn("unit", r["counting_honesty"])
        self.assertIn("§7", r["counting_honesty"])
        self.assertIn("read-only", r["read_only"])
        self.assertIn("PR/packet", r["read_only"])

    # ---- MCP wiring -------------------------------------------------------
    def test_build_server_registers_all_tools_read_only(self):
        try:
            import anyio
            server = srv.build_server()
        except ImportError:
            self.skipTest("mcp package not installed")
        tools = anyio.run(server.list_tools)
        self.assertEqual({t.name for t in tools}, {f.__name__ for f in srv.TOOLS})
        self.assertEqual(len(tools), 8)
        for t in tools:
            self.assertTrue(t.annotations and t.annotations.read_only_hint, t.name)


if __name__ == "__main__":
    unittest.main()
