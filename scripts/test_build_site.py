#!/usr/bin/env python3
"""Tests for scripts/build_site.py, run against a tiny fixture database.

    python3 -m unittest scripts/test_build_site.py
"""
import csv
import html as html_lib
import io
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site  # noqa: E402

XSS_NAME = "<script>alert(1)</script> Plastics & Co"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")

ORG_COLS = ["org_id", "legal_name", "trade_names", "parent_org_id", "ultimate_parent_name", "entity_type",
            "ring_primary", "ring_secondary", "hq_city", "hq_state", "hq_county", "naics_primary",
            "naics_primary_source_type", "naics_confidence", "processes", "materials", "markets_served",
            "employee_band_ohio", "website", "description_1line", "pic_relevance", "status", "status_date",
            "successor_org_id", "sources", "verification_tier", "last_verified", "created_by", "notes",
            "year_founded", "stock_ticker", "ownership_type", "certifications", "pic_member",
            "membership_source_url"]
SITE_COLS = ["site_id", "org_id", "site_name", "site_type", "city", "state", "zip", "county", "ring_primary",
             "naics_primary", "naics_primary_source_type", "naics_confidence", "processes", "processes_other_note",
             "materials", "materials_other_note",
             "markets_served", "employee_band_site", "operating_status", "sources", "verification_tier",
             "last_verified", "created_by", "notes", "street_address", "latitude", "longitude",
             "geocode_precision", "country"]
ECO_COLS = ["org_id", "legal_name", "ecosystem_subtype", "polymer_program_name", "city", "state", "county",
            "website", "description_1line", "pic_relevance", "status", "sources", "verification_tier",
            "last_verified", "notes", "parent_institution_org_id", "polymer_program_url"]
PROG_COLS = ["program_id", "institution_org_id", "program_name", "program_type", "level", "url", "city",
             "state", "county", "status", "verification_tier", "sources", "notes"]
PEOPLE_COLS = ["person_id", "full_name", "institution_org_id", "role", "role_as_published",
               "research_specialties", "public_profile_url", "sources", "verification_tier", "last_verified"]
REL_COLS = ["relationship_id", "from_org_id", "relationship_type", "to_org_id", "basis", "notes"]


def make_db(path):
    con = sqlite3.connect(path)
    for name, cols in (("organizations", ORG_COLS), ("sites", SITE_COLS), ("ecosystem", ECO_COLS),
                       ("programs", PROG_COLS), ("people", PEOPLE_COLS), ("relationships", REL_COLS)):
        con.execute(f'CREATE TABLE "{name}" ({", ".join(chr(34) + c + chr(34) + " TEXT" for c in cols)})')

    def ins(name, cols, **kw):
        con.execute(f'INSERT INTO "{name}" ({",".join(kw)}) VALUES ({",".join("?" * len(kw))})', list(kw.values()))

    ins("organizations", ORG_COLS, org_id="ORG-000001", legal_name=XSS_NAME, trade_names="Evil Plastics;Zed Rubber",
        entity_type="corporation_private", ring_primary="1", hq_city="Akron", hq_state="OH", hq_county="Summit",
        naics_primary="326199", naics_primary_source_type="directory_assigned", naics_confidence="medium",
        processes="injection_molding;extrusion", website="https://example.com", status="active",
        description_1line="Molds things.", pic_relevance="potential_member;research_partner",
        sources="Company site https://example.com/about; CRM conflict adjudication ORG-000001 (staging working/x.csv)",
        verification_tier="A", last_verified="2026-10-30", created_by="fixture",
        notes="Contact Jane Doe jane.doe@example.com or 330-555-0142 (home 12 Elm St)", pic_member="true",
        membership_source_url="https://polymerindustrycluster.org/members")
    ins("organizations", ORG_COLS, org_id="ORG-000002", legal_name="Old Rubber Co", ring_primary="1",
        hq_city="Akron", hq_state="OH", status="acquired", status_date="2026-01-15",
        successor_org_id="ORG-000001", sources="Trade press", verification_tier="C", last_verified="2026-10-01")
    ins("organizations", ORG_COLS, org_id="ORG-000003", legal_name="Keystone Compounds", ring_primary="2",
        hq_city="Erie", hq_state="PA", status="active", verification_tier="B", last_verified="2026-10-02",
        description_1line="Exists only in the CRM record.", sources="Directory https://example.org/k")
    ins("organizations", ORG_COLS, org_id="ORG-000004", legal_name="Standalone Compounds",
        status="active", processes="injection_molding;extrusion")
    ins("sites", SITE_COLS, site_id="SITE-000001", org_id="ORG-000001", site_name="Evil Plastics - Akron plant",
        site_type="manufacturing_plant", city="Akron", state="OH", zip="44301", county="Summit",
        ring_primary="1", naics_primary="326199", processes="injection_molding", operating_status="active",
        sources="Company site https://example.com/plant", verification_tier="A", last_verified="2026-10-30",
        street_address="1 Main St", latitude="41.08", longitude="-81.51", geocode_precision="address_interpolated",
        country="US", notes="secret note 330-555-0199")
    ins("sites", SITE_COLS, site_id="SITE-000002", org_id="ORG-000001", site_name="Evil Plastics - Annex",
        city="Akron", state="OH", county="Summit", ring_primary=None, operating_status="active",
        processes="blow_molding", materials="legacy_<custom>", markets_served="marine",
        verification_tier="U", last_verified="2026-10-30", latitude="41.09", longitude="-81.52", country="US")
    ins("sites", SITE_COLS, site_id="SITE-000003", org_id="ORG-000003", site_name="Keystone - Erie",
        city="Erie", state="PA", county="Erie", ring_primary="2", operating_status="active",
        processes="compounding_formulation", verification_tier="C", last_verified="2026-10-02", country="US")
    ins("sites", SITE_COLS, site_id="SITE-000004", org_id="ORG-000002", site_name="Old Rubber - Cleveland",
        city="Cleveland", state="OH", county="Cuyahoga", ring_primary="1", operating_status="closed",
        processes="extrusion", verification_tier="C", last_verified="2026-10-01", latitude="41.5", longitude="-81.7",
        country="US")
    ins("ecosystem", ECO_COLS, org_id="ORG-000501", legal_name="University of Akron",
        ecosystem_subtype="university_college", city="Akron", state="OH", county="Summit", status="active",
        verification_tier="A", last_verified="2026-10-29", sources="https://www.uakron.edu",
        notes="internal only", pic_relevance="potential_member")
    ins("programs", PROG_COLS, program_id="PROG-000001", institution_org_id="ORG-000501",
        program_name="Polymer Science", program_type="degree", level="doctoral", city="Akron", state="OH",
        county="Summit", status="active", verification_tier="A", url="https://www.uakron.edu/polymer")
    ins("people", PEOPLE_COLS, person_id="PERSON-000001", full_name="Ada Researcher", institution_org_id="ORG-000501",
        role="professor", role_as_published="Professor of Polymer Science",
        research_specialties="polymer_synthesis;rheology", public_profile_url="https://www.uakron.edu/ada",
        verification_tier="A", last_verified="2026-10-29")
    ins("people", PEOPLE_COLS, person_id="PERSON-000002", full_name="Bo Embedded",
        institution_org_id="ORG-000501", role="professor", role_as_published="Professor",
        public_profile_url="https://example.edu/people/bo.embedded@example.edu", verification_tier="A")
    con.commit()
    con.close()


QCEW_CSV = (
    "year,area_fips,area_title,industry_code,own_code,agglvl_code,annual_avg_estabs,annual_avg_emplvl,"
    "total_annual_wages,avg_annual_pay,disclosure_code\n"
    '2023,39153,"Summit County, Ohio",326,5,75,76,4328,265177336,61264,\n'
    '2024,39153,"Summit County, Ohio",326,5,75,70,4000,250000000,60000,\n'
    '2023,39035,"Cuyahoga County, Ohio",326,5,75,,,,,N\n'
)


class WellFormed(HTMLParser):
    VOID = {"meta", "link", "br", "hr", "img", "input", "area", "base", "col", "source", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append((tag, self.getpos()))
        else:
            self.stack.pop()


class BuildSiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        cls.db = tmp / "fixture.db"
        make_db(cls.db)
        qcew = tmp / "qcew.csv"
        qcew.write_text(QCEW_CSV, encoding="utf-8")
        cls.out = tmp / "site"
        cls.result = build_site.build_site(
            cls.db, cls.out, qcew, repo_url="https://example.com/repo",
            git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def all_text_files(self):
        return [p for p in self.out.rglob("*") if p.is_file() and p.suffix in {".html", ".json", ".js", ".css"}]

    def test_nonempty_equipment_renders_source_cell(self):
        for source in ("https://example.edu/equipment", ""):
            with self.subTest(source=source):
                html = build_site.equipment_block([{"name": "DSC", "equipment_class": "dsc",
                                                   "access_mode": "not_stated", "source_ref": source}])
                self.assertIn("(1 equipment row)", html)
                self.assertIn('<th scope="row">DSC</th>', html)
                self.assertIn("host page</a></td></tr>" if source else "<td></td></tr>", html)

    def test_pages_exist(self):
        for rel in ["index.html", "map.html", "search.html", "sites.json", "orgs.json", "style.css",
                    "map.js", "search.js", "counties/index.html", "experts.html", "experts.js", "experts.json"]:
            self.assertTrue((self.out / rel).is_file(), rel)
        for c in build_site.PIC12:
            self.assertTrue((self.out / "counties" / f"{c.lower()}.html").is_file(), c)
        for oid in ["ORG-000001", "ORG-000002", "ORG-000003", "ORG-000501"]:
            self.assertTrue((self.out / "orgs" / f"{oid}.html").is_file(), oid)
        self.assertEqual(self.result["org_pages"], 4)
        self.assertEqual(self.result["eco_pages"], 1)
        self.assertEqual(self.result["map_sites"], 3)  # three fixture sites carry coordinates

    def test_every_page_is_well_formed(self):
        for p in self.out.rglob("*.html"):
            wf = WellFormed()
            wf.feed(p.read_text(encoding="utf-8"))
            wf.close()
            self.assertEqual(wf.errors, [], p.name)
            self.assertEqual(wf.stack, [], p.name)

    def test_html_escaping(self):
        for rel in ["orgs/ORG-000001.html", "counties/summit.html", "counties/index.html"]:
            self.assertNotIn("<script>alert(1)", self.read(rel), rel)
        org = self.read("orgs/ORG-000001.html")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; Plastics &amp; Co", org)
        self.assertIn("&lt;script&gt;alert(1)", self.read("counties/summit.html"))
        # the only <script> tags in any page are our own src= includes
        for p in self.out.rglob("*.html"):
            for m in re.finditer(r"<script\b[^>]*>", p.read_text(encoding="utf-8")):
                self.assertIn("src=", m.group(0), p.name)

    def test_search_index_is_data_not_markup(self):
        data = json.loads(self.read("orgs.json"))
        names = [r[data["cols"].index("name")] for r in data["rows"]]
        self.assertIn(XSS_NAME, names)      # raw in JSON; the JS renders it with textContent
        self.assertNotIn("innerHTML", self.read("search.js"))
        self.assertNotIn("innerHTML", self.read("map.js"))
        self.assertEqual(len(data["rows"]), 5)  # 4 organizations + 1 ecosystem row

    def test_company_fields_show_union_with_value_level_provenance(self):
        def fields(oid):
            return self.read(f"orgs/{oid}.html").split('<dl class="fields">', 1)[1].split("</dl>", 1)[0]

        company = fields("ORG-000001")
        processes = re.search(r"<dt>Processes</dt><dd>(.*?)</dd>", company)[1]
        self.assertRegex(processes, r"extrusion[^<]*<span[^>]*>\(Company row\)")
        self.assertEqual(processes.count("injection molding"), 1)
        self.assertRegex(processes, r"injection molding.*?Company row.*?Evil Plastics - Akron plant.*?Tier A</span>")
        self.assertRegex(processes, r"blow molding.*?Evil Plastics - Annex.*?Tier U</span>.*?unverified candidate")
        self.assertRegex(company, r"<dt>Materials</dt><dd>.*?legacy &lt;custom&gt;.*?Evil Plastics - Annex.*?Tier U")
        self.assertRegex(company, r"<dt>Markets served</dt><dd>.*?marine.*?Evil Plastics - Annex.*?Tier U")
        self.assertRegex(fields("ORG-000003"), r"<dt>Processes</dt><dd>.*?compounding formulation.*?Keystone - Erie.*?Tier C</span>.*?single secondary source")
        self.assertNotIn("<dt>Processes</dt>", fields("ORG-000002"))
        self.assertIn("<dt>Processes</dt><dd>injection molding, extrusion</dd>", fields("ORG-000004"))
        self.assertIn("<dt>Processes</dt><dd>extrusion</dd>", self.read("orgs/ORG-000002.html"))

    def test_county_page_has_a_jump_line_to_its_long_sections(self):
        page = self.read("counties/summit.html")
        for anchor in ("sites", "programs", "ecosystem"):
            self.assertEqual(page.count(f'href="#{anchor}"'), 1, anchor)
            self.assertEqual(page.count(f'id="{anchor}"'), 1, anchor)                  # the target exists, once

    def test_counts_carry_unit_and_filter(self):
        idx = self.read("index.html")
        cards = re.findall(r'<div class="big">([\d,]+)</div><div class="unit">([^<]+)</div>'
                           r'<div class="filter">([^<]+)</div>', idx)
        self.assertEqual(len(cards), idx.count('class="big"'))
        self.assertGreaterEqual(len(cards), 6)
        for num, unit, filt in cards:
            self.assertTrue(re.search(r"rows", unit), unit)
            self.assertTrue(re.search(r"status|tiers|Ring 5", filt), filt)
        by_unit = {u: n for n, u, _ in cards}
        # fixture: active tier A-C sites are SITE-000001 (A) and SITE-000003 (C)
        self.assertEqual(by_unit["Site rows"], "2")
        self.assertEqual(by_unit["Ohio site rows"], "1")
        self.assertEqual(by_unit["Organization rows (parents)"], "2")
        self.assertIn("Tier U", idx)
        summit = self.read("counties/summit.html")
        self.assertIn('<div class="big">2</div><div class="unit">Site rows</div>', summit)
        self.assertIn("operating status active; all verification tiers", summit)
        self.assertIn("Tier A", summit)
        self.assertNotIn("Old Rubber - Cleveland", summit)    # closed, other county

    def test_qcew_benchmark_is_labelled(self):
        summit = self.read("counties/summit.html")
        self.assertIn("count", summit)
        self.assertIn("not matched coverage", summit)
        self.assertIn("4,328", summit)           # 2023 employment, not the 2024 row
        self.assertNotIn("4,000", summit)
        cuy = self.read("counties/cuyahoga.html")
        self.assertIn("withheld", cuy)           # suppressed cell is not shown as zero
        self.assertIn("not a zero", self.read("counties/index.html"))

    def test_no_personal_data_published(self):
        for p in self.all_text_files():
            text = p.read_text(encoding="utf-8")
            self.assertIsNone(EMAIL_RE.search(text), f"email-like string in {p.name}")
            self.assertIsNone(PHONE_RE.search(text), f"phone-like string in {p.name}")
            for private in ("Jane Doe", "12 Elm St", "secret note", "potential_member", "potential member",
                            "internal only"):
                self.assertNotIn(private, text, f"{private!r} leaked into {p.name}")

    def test_people_only_on_institution_page(self):
        inst = self.read("orgs/ORG-000501.html")
        self.assertIn("Ada Researcher", inst)
        self.assertIn("Professor of Polymer Science", inst)
        self.assertIn("polymer synthesis, rheology", inst)
        self.assertIn('href="https://www.uakron.edu/ada"', inst)
        self.assertIn("Bo Embedded", inst)
        self.assertNotIn("bo.embedded", inst)    # URL embedding an email is not published
        for p in self.out.rglob("*.html"):
            if p.name != "ORG-000501.html":
                self.assertNotIn("Ada Researcher", p.read_text(encoding="utf-8"), p.name)
        self.assertFalse(any("PERSON" in p.name for p in self.out.rglob("*")))

    def test_experts_finder_carries_public_professional_fields_only(self):
        import json
        d = json.loads(self.read("experts.json"))
        self.assertEqual(set(d), {"insts", "people", "programs"})
        by_name = {p[0]: p for p in d["people"]}
        self.assertEqual(set(by_name), {"Ada Researcher", "Bo Embedded"})
        for p in d["people"]:
            self.assertEqual(len(p), 6)            # name, role, specialties, institution id, profile URL, engagement modes
            self.assertNotIn("@", p[4])            # a URL embedding an email is dropped
            self.assertIn(p[3], d["insts"])
        self.assertIn("rheology", by_name["Ada Researcher"][2])
        self.assertEqual(by_name["Bo Embedded"][4], "")
        for oid, row in d["insts"].items():
            self.assertEqual(len(row), 4)
            self.assertIn(row[3], {"edu", "lab", "other"})
        html = self.read("experts.html")
        self.assertIn("researcher records", html)  # unit named (AGENTS.md section 7)
        self.assertNotIn("Ada Researcher", html)   # names reach the page only through the finder data

    def test_specialty_display_labels(self):
        n = build_site.norm_specialty
        self.assertEqual(n("polyethylene_pe"), "polyethylene (PE)")
        self.assertEqual(n("injection_molding"), "injection molding")
        self.assertEqual(n("Polymer physics."), "polymer physics")
        self.assertEqual(n("BioMEMS"), "BioMEMS")
        self.assertEqual(n("other_specified_in_notes"), "")
        self.assertEqual(build_site.specs_of(["rheology", "Rheology", "polymer_physics"]), ["polymer physics", "rheology"])

    def test_crm_and_staging_references_withheld(self):
        for p in self.out.rglob("*.html"):
            text = p.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\bCRM\b", p.name)
            self.assertNotIn("staging working", text, p.name)
        org = self.read("orgs/ORG-000001.html")
        self.assertIn("https://example.com/about", org)      # the link stays
        self.assertNotIn("conflict adjudication", org)         # the prose around it never does
        self.assertNotIn("Company site", org)

    def test_tombstone_marked_with_successor_link(self):
        page = self.read("orgs/ORG-000002.html")
        self.assertIn("Tombstone record: acquired", page)
        self.assertIn("2026-01-15", page)
        self.assertIn('href="ORG-000001.html"', page)

    def test_site_ring_inherited_flagged(self):
        sites = json.loads(self.read("sites.json"))
        c = {n: i for i, n in enumerate(sites["cols"])}
        row = next(r for r in sites["rows"] if r[c["id"]] == "SITE-000002")
        self.assertEqual(row[c["ring"]], "1")
        self.assertEqual(row[c["inh"]], 1)
        self.assertIn("*", self.read("counties/summit.html"))

    def test_leaflet_is_vendored_and_osm_tiles_are_the_only_external_request(self):
        map_html = self.read("map.html")
        self.assertIn('href="vendor/leaflet/leaflet.css"', map_html)
        self.assertIn('src="vendor/leaflet/leaflet.js"', map_html)
        self.assertNotIn("unpkg.com", map_html)
        self.assertIn("tile.openstreetmap.org", self.read("map.js"))
        self.assertIn("reference data", map_html)
        pat = re.compile(r'<(?:script|link|img)\b[^>]*(?:src|href)="https?://')
        for p in self.out.rglob("*.html"):
            self.assertIsNone(pat.search(p.read_text(encoding="utf-8")), p.name)

    def test_index_provenance_and_license(self):
        idx = self.read("index.html")
        self.assertIn("CC BY 4.0", idx)
        self.assertIn("abc1234", idx)
        self.assertIn("2026-11-01", idx)
        self.assertIn("https://example.com/repo", idx)

    def test_css_supports_dark_mode_and_mobile(self):
        css = self.read("style.css")
        self.assertIn("prefers-color-scheme: dark", css)
        self.assertIn("max-width:600px", css)
        self.assertIn('name="viewport"', self.read("index.html"))


EVID_COLS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
             "observed_date", "tier_effect", "created_by", "notes"]


def make_directory_db(path):
    """The shared fixture plus four more PIC-18 organizations, an ecosystem-owned PIC-18 site and an evidence table."""
    make_db(path)
    con = sqlite3.connect(path)
    con.execute(f'CREATE TABLE "evidence" ({", ".join(chr(34) + c + chr(34) + " TEXT" for c in EVID_COLS)})')

    def ins(name, **kw):
        con.execute(f'INSERT INTO "{name}" ({",".join(kw)}) VALUES ({",".join("?" * len(kw))})', list(kw.values()))
    ins("organizations", org_id="ORG-000004", legal_name="Stark Molders", ring_primary="1", hq_city="Canton", hq_state="OH",
        status="active", verification_tier="B", employee_band_ohio="100-249", website="https://stark.example.com",
        ownership_type="family_owned", processes="extrusion")
    ins("organizations", org_id="ORG-000005", legal_name="Portage Foam", ring_primary="2", hq_city="Ravenna", hq_state="OH",
        status="active", verification_tier="B", employee_band_ohio="100-249", processes="foam_fabrication",
        ownership_type="unknown")
    ins("organizations", org_id="ORG-000006", legal_name="Medina Mystery", hq_city="Medina", hq_state="OH", status="active",
        verification_tier="C")
    ins("sites", site_id="SITE-000005", org_id="ORG-000004", site_name="Stark Molders - Canton", city="Canton", state="OH",
        county="Stark", ring_primary="1", processes="injection_molding", employee_band_site="50-99",
        operating_status="active", verification_tier="A", last_verified="2026-10-30", country="US")
    ins("sites", site_id="SITE-000006", org_id="ORG-000005", site_name="Portage Foam - Ravenna", city="Ravenna", state="OH",
        county="Portage", ring_primary="2", operating_status="active", verification_tier="B", last_verified="2026-10-30",
        country="US", street_address="500 Portage Rd")
    ins("sites", site_id="SITE-000007", org_id="ORG-000006", site_name="Medina Mystery - Medina", city="Medina", state="OH",
        county="Medina", employee_band_site="unknown", operating_status="active", verification_tier="C",
        last_verified="2026-10-30", country="US")
    ins("sites", site_id="SITE-000008", org_id="ORG-000501", site_name="Univ of Akron - Lab", city="Akron", state="OH",
        county="Summit", ring_primary="5", operating_status="active", verification_tier="A", last_verified="2026-10-30",
        country="US")
    ev = [  # (id, table, record, claim, detail, class, ref, date, effect, created_by, notes)
        ("EVD-1", "organizations", "ORG-000001", "existence", "Evil Plastics exists and operates", "own_site",
         "https://example.com/about (own site, accessed 2026-10-30)", "2026-10-30", "supports_A", "lane_Z99", "PRIVATE-NOTE-XYZ"),
        ("EVD-2", "organizations", "ORG-000001", "scope", 'page quote: "Email: sales.rep@example.com PH: 330-555-0142"', "own_site",
         "https://example.com/contact", "2026-10-29", "supports_A", "lane_Z99", ""),
        ("EVD-3", "organizations", "ORG-000001", "activity", "Jane Roe (President) and John Poe (Vice President) run the plant",
         "directory", "https://example.org/directory https://www.linkedin.com/in/jane-roe", "2026-10-28", "supports_B", "lane_Z99", ""),
        ("EVD-4", "organizations", "ORG-000001", "address", "Akron address", "directory",
         "see (staging working/x.csv) for the page", "2026-10-28", "supports_B", "lane_Z99", ""),
        ("EVD-5", "sites", "SITE-000001", "existence", "Akron plant exists", "government_filing",
         "OSHA ITA Form 300A CY2025 establishment 123456", "2026-10-30", "supports_A", "lane_Z99", ""),
        ("EVD-6", "organizations", "ORG-000004", "existence", "Stark Molders exists", "harvest_roster",
         "https://example.org/roster", "2026-10-30", "supports_B", "lane_Z99", ""),
    ]
    for e in ev:
        ins("evidence", **dict(zip(EVID_COLS, e)))
    con.commit()
    con.close()


VB_COLS = ["record_table", "record_id", "field", "value", "basis", "evidence_id", "basis_date"]


def add_value_basis(db, rows):
    con = sqlite3.connect(db)
    con.execute(f'CREATE TABLE "value_basis" ({", ".join(chr(34) + c + chr(34) + " TEXT" for c in VB_COLS)})')
    con.executemany("INSERT INTO value_basis VALUES (?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()


class ValueBasisDisplayTest(unittest.TestCase):
    """SCHEMA 4.24: the site shows each value's label and never shows a withheld value (planted: SITE-000002 blow_molding)."""
    ROWS = [("sites", "SITE-000001", "processes", "injection_molding", "stated", "EVD-1", "2026-11-24"),
            ("sites", "SITE-000002", "processes", "blow_molding", "not_found_pending_refetch", "EVD-2", "2026-11-24"),
            ("sites", "SITE-000002", "markets_served", "marine", "filing", "EVD-3", "2026-11-20"),
            ("organizations", "ORG-000001", "processes", "extrusion", "not_yet_checked", "EVD-4", "")]

    @classmethod
    def build(cls, tmp, rows):
        make_db(tmp / "f.db")
        if rows:
            add_value_basis(tmp / "f.db", rows)
        out = tmp / "site"
        build_site.build_site(tmp / "f.db", out, None, repo_url="https://example.com/repo",
                              git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")
        return {p.relative_to(out).as_posix(): p.read_text(encoding="utf-8", errors="replace") for p in out.rglob("*") if p.is_file()}

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            cls.plain = cls.build(Path(a), [])
            cls.labelled = cls.build(Path(b), cls.ROWS)

    def test_control_the_planted_value_is_on_the_site_without_a_basis_table(self):
        self.assertTrue(any("blow molding" in t or "blow_molding" in t for t in self.plain.values()))

    def test_withheld_value_appears_in_no_output_file(self):  # planted defect: a not_found_pending_refetch value shown
        hits = [f for f, t in self.labelled.items() if "blow molding" in t.lower() or "blow_molding" in t]
        self.assertEqual(hits, [])

    def test_other_values_stay_and_carry_their_labels(self):
        org = self.labelled["orgs/ORG-000001.html"]
        self.assertRegex(org, r"injection molding.{0,200}stated")
        self.assertRegex(org, r"extrusion.{0,400}not yet checked")
        self.assertRegex(org, r"marine.{0,400}from a filing")
        directory = json.loads(self.labelled["directory.json"])["rows"]
        row = next(r for r in directory if r["id"] == "ORG-000001")
        self.assertIn("injection molding (stated)", row["show"]["proc"])

    def test_directory_csv_carries_the_labels(self):
        rows = list(csv.DictReader(io.StringIO(self.labelled["directory.csv"].lstrip("\ufeff"))))
        row = next(r for r in rows if r["org_id"] == "ORG-000001")
        self.assertEqual(row["processes_value_basis"], "injection molding: stated")
        self.assertIn("processes_value_basis", self.plain["directory.csv"].splitlines()[0])
        self.assertEqual(next(r for r in csv.DictReader(io.StringIO(self.plain["directory.csv"].lstrip("\ufeff"))))["processes_value_basis"], "")


class DirectoryFixtureTest(unittest.TestCase):
    """The directory page, its CSV, the county A-C column and the evidence section, against a fixture whose answers are known."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        make_directory_db(tmp / "f.db")
        cls.out = tmp / "site"
        build_site.build_site(tmp / "f.db", cls.out, None, repo_url="https://example.com/repo",
                              git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")
        con = sqlite3.connect(f"file:{tmp / 'f.db'}?mode=ro", uri=True)
        cls.atlas = build_site.Atlas(con)
        con.close()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def option_count(self, html, facet, value):
        m = re.search(rf'name="{facet}" value="{re.escape(value)}"> <span class="t">[^<]*</span> <span class="n">(\d+)</span>', html)
        self.assertIsNotNone(m, f"{facet}={value}")
        return int(m.group(1))

    def test_one_row_per_organization_and_county_and_sites_sum_to_the_headline_set(self):
        rows = build_site.directory_rows(self.atlas)
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))                    # each fixture organization has sites in one county
        self.assertEqual(set(ids), {"ORG-000001", "ORG-000004", "ORG-000005", "ORG-000006", "ORG-000501"})  # eco-owned site counts
        self.assertEqual(sum(r["n_sites"] for r in rows), len(build_site.pic18_active_sites(self.atlas.sites)))
        self.assertEqual(sum(r["n_sites"] for r in rows), 5)     # not the closed, tier U or Pennsylvania-Erie site rows

    def test_employee_band_basis_is_site_then_org_then_unknown(self):
        by = {r["id"]: r["band"] for r in build_site.directory_rows(self.atlas)}
        self.assertEqual(by["ORG-000004"], (["50-99"], "site"))          # the site band wins over the org's 100-249
        self.assertEqual(by["ORG-000005"], (["100-249"], "org record"))
        self.assertEqual(by["ORG-000006"], ([], ""))                     # literal "unknown" is unknown
        shown = {r["id"]: r["show"]["band"] for r in json.loads(self.read("directory.json"))["rows"]}
        self.assertEqual(shown["ORG-000004"], "50-99 (site)")
        self.assertEqual(shown["ORG-000005"], "100-249 (org record)")
        self.assertEqual(shown["ORG-000006"], "unknown")

    def test_filter_counts_and_unknown_counts(self):
        html = self.read("directory.html")
        self.assertEqual(self.option_count(html, "band", "min50"), 2)    # 50-99 and 100-249
        self.assertEqual(self.option_count(html, "band", "min100"), 1)   # only 100-249
        self.assertEqual(self.option_count(html, "band", "_"), 3)        # ORG-000001, ORG-000006 and the ecosystem org: 5 rows - 2 with a band
        self.assertEqual(self.option_count(html, "co", "Summit"), 2)
        self.assertEqual(self.option_count(html, "proc", "injection_molding"), 2)   # site-level
        self.assertEqual(self.option_count(html, "proc", "foam_fabrication"), 1)    # org-level fallback
        self.assertEqual(self.option_count(html, "proc", "_"), 2)
        for facet in ("co", "ring", "band", "proc", "mat", "mkt", "own"):
            self.assertIn(f'name="{facet}" value="_"', html)             # every filter lists its unknown count
        self.assertIn("Unknown means nothing is recorded", html)

    def test_public_member_list_wording(self):
        self.assertIn("on the public member list", self.read("orgs/ORG-000001.html"))   # the flag, with its source link
        self.assertNotIn("public member list", self.read("orgs/ORG-000003.html"))        # absence is never stated
        for p in self.out.rglob("*.html"):
            self.assertNotRegex(p.read_text(encoding="utf-8"), r"[Nn]on-member|PIC member \(", p.name)

    def test_directory_csv(self):
        rows = list(csv.DictReader(io.StringIO(self.read("directory.csv").lstrip("\ufeff"))))
        self.assertEqual(len(rows), 5)
        by = {r["org_id"]: r for r in rows}
        self.assertEqual(by["ORG-000006"]["employee_band"], "unknown")
        self.assertEqual(by["ORG-000005"]["employee_band_basis"], "org record")
        self.assertTrue(by["ORG-000004"]["atlas_page"].endswith("/orgs/ORG-000004.html"))
        injected = build_site.directory_csv([{**build_site.directory_rows(self.atlas)[0], "name": "=HYPERLINK(1)"}], "x/")
        self.assertIn("'=HYPERLINK(1)", injected)                         # a formula is never written as a formula

    def test_every_page_links_the_release_and_the_csv(self):
        for p in self.out.rglob("*.html"):
            text = p.read_text(encoding="utf-8")
            self.assertIn("https://example.com/repo/releases/latest", text, p.name)
            self.assertIn("directory.csv", text, p.name)

    def test_csv_download_is_in_the_shared_table_script(self):
        js = self.read("sortable.js")
        self.assertIn("Download these rows (CSV)", js)
        self.assertIn("r.hidden", js)                                      # exports the rows shown, not the hidden ones
        self.assertIn("data-nofilter", js)
        self.assertIn('id="dtable"', self.read("directory.html"))
        self.assertIn("data-nocsv", self.read("directory.html"))           # the page exports its own filtered rows, not the 50 on screen
        self.assertIn("hits.forEach", self.read("directory.js"))

    # ---- ATLAS-39: the public directory replaces the prospects page ----

    def fixture_summary(self):
        """County and ring tallies recomputed from the fixture's own site rows, with plain loops (no builder helper)."""
        by_county, by_ring = {}, {}
        for s in self.atlas.sites:
            if not (s["state"] == "OH" and s["county"] in build_site.PIC12 and s["operating_status"] == "active"
                    and s["verification_tier"] in ("A", "B", "C")):
                continue
            for table, key in ((by_county, s["county"]), (by_ring, s["_ring"] or "unknown")):
                orgs, n = table.get(key, (set(), 0))
                table[key] = (orgs | {s["org_id"]}, n + 1)
        return by_county, by_ring

    def summary_rows(self, html, kind):
        """{label: (organization rows, site rows)} read from the summary table whose caption starts with kind."""
        table = re.search(rf"<table[^>]*><caption>[^<]*{kind}[^<]*</caption>.*?</table>", html, re.S)
        self.assertIsNotNone(table, kind)
        out = {}
        for m in re.finditer(r'<tr><th scope="row">(?:<a [^>]*>)?([^<]+)(?:</a>)?</th><td class="num">(\d+)</td><td class="num">(\d+)</td></tr>',
                             table.group(0)):
            out[html_lib.unescape(m.group(1)).split(":")[0]] = (int(m.group(2)), int(m.group(3)))
        return out

    def test_no_prospect_or_pitch_wording_on_the_built_site(self):
        for p in self.out.rglob("*"):
            if p.is_file() and p.name != "prospects.html" and p.suffix in {".html", ".js", ".json", ".css", ".csv"} \
                    and "vendor" not in p.relative_to(self.out).parts:        # vendored libraries are not our wording ("pitch" is a camera angle)
                self.assertNotRegex(p.read_text(encoding="utf-8-sig"), r"(?i)prospect|pitch", str(p.relative_to(self.out)))

    def test_prospects_urls_still_work(self):
        stub = self.read("prospects.html")
        self.assertIn('<noscript><meta http-equiv="refresh" content="0; url=directory.html"></noscript>', stub)
        self.assertIn('<script src="prospects.js"></script>', stub)
        self.assertIn("location.search", self.read("prospects.js"))      # saved filters travel to the directory
        self.assertIn('<a href="directory.html">', stub)
        self.assertEqual((self.out / "prospects.csv").read_bytes(), (self.out / "directory.csv").read_bytes())

    def test_summary_is_the_first_content_of_the_directory(self):
        main = self.read("directory.html").split("<main", 1)[1]
        self.assertIn("Northeast Ohio polymer companies", main.split("</h1>", 1)[0])
        before_form = main.split("<form", 1)[0]
        self.assertEqual(before_form.count("<table"), 2)                    # county and ring tables, nothing else, before the filters
        self.assertTrue(before_form.index("<table") < before_form.index("</table>") < before_form.rindex("<table"))
        self.assertRegex(before_form, r"<caption>[^<]*county[^<]*</caption>")
        self.assertRegex(before_form, r"<caption>[^<]*ring[^<]*</caption>")

    def test_summary_counts_match_the_site_rows_and_name_their_unit(self):
        html = self.read("directory.html")
        by_county, by_ring = self.fixture_summary()
        for kind, expected in (("county", by_county), ("ring", by_ring)):
            got = self.summary_rows(html, kind)
            self.assertGreaterEqual(len(got), 3)
            for label, (orgs, n) in expected.items():
                key = label if kind == "county" else ("Ring not recorded" if label == "unknown" else f"Ring {label}")
                self.assertEqual(got[key], (len(orgs), n), f"{kind} {label}")
        self.assertIn("owners with an active tier A-C site row in that county or ring", html)
        self.assertIn("4 organization records and\n1 ecosystem records", html)   # the unit is the owner, with the 787 + 7 split spelled out
        total = re.search(r"<th scope=\"row\">All PIC-18</th><td class=\"num\">(\d+)</td><td class=\"num\">(\d+)</td>", html)
        self.assertEqual((int(total.group(1)), int(total.group(2))), (5, 5))
        self.assertIn("counted in each", html)                              # an organization in two counties is counted in both

    def test_directory_list_is_data_not_markup_and_capped_at_50(self):
        html = self.read("directory.html")
        self.assertEqual(html.count("<tr data-"), 0)                        # no organization row is in the page itself
        self.assertRegex(self.read("directory.js"), r"var PAGE = 50;")
        rows = json.loads(self.read("directory.json"))["rows"]
        by_county, _ = self.fixture_summary()
        self.assertEqual(len(rows), sum(len(o) for o, _ in by_county.values()))   # one entry per organization row and county
        self.assertEqual([r["co"] for r in rows], sorted(r["co"] for r in rows))   # grouped by county
        main = next(r for r in rows if r["id"] == "ORG-000001")
        self.assertIn("1 Main St, Akron, OH 44301", main["addr"])
        stark = next(r for r in rows if r["id"] == "ORG-000004")
        self.assertEqual(stark["addr"], ["Street not recorded, Canton, OH"])

    def test_member_badge_is_the_public_flag_only(self):
        rows = {r["id"]: r for r in json.loads(self.read("directory.json"))["rows"]}
        self.assertTrue(rows["ORG-000001"]["member"])
        self.assertFalse(rows["ORG-000004"]["member"])
        self.assertIn("PIC member", self.read("directory.js"))
        self.assertIn('name="mem" value="yes"', self.read("directory.html"))           # the filter: Yes / No, from the public flag only
        self.assertIn('name="mem" value="no"', self.read("directory.html"))
        self.assertIn('"not on the public member list" is not the same as "not a member"', self.read("directory.html"))   # the caveat, as the prospects page had it
        for p in self.out.rglob("*"):
            if p.is_file() and p.suffix in {".html", ".js", ".json", ".css", ".csv"} and p.name != "directory.html":
                self.assertNotIn("not on the public member list", p.read_text(encoding="utf-8-sig"), p.name)   # never on a record page, the CSV or the data

    def test_homepage_menu_and_footer_point_to_the_directory(self):
        home = self.read("index.html")
        self.assertEqual(home.count('href="directory.html"'), 3)            # menu, button, Explore card
        self.assertIn("Northeast Ohio polymer companies", home)
        self.assertIn('href="directory.csv"', self.read("search.html"))

    def test_directory_csv_has_addresses_and_the_public_flag(self):
        rows = list(csv.DictReader(io.StringIO(self.read("directory.csv").lstrip("\ufeff"))))
        self.assertEqual(len(rows), len(json.loads(self.read("directory.json"))["rows"]))
        by = {(r["org_id"], r["pic18_counties"]): r for r in rows}
        self.assertEqual(by[("ORG-000001", "Summit")]["public_member_list"], "yes")
        self.assertEqual(by[("ORG-000004", "Stark")]["public_member_list"], "")
        self.assertIn("1 Main St, Akron, OH 44301", by[("ORG-000001", "Summit")]["pic18_site_addresses"])
        self.assertEqual(by[("ORG-000004", "Stark")]["pic18_site_addresses"], "Street not recorded, Canton, OH")

    def test_every_pic18_site_street_is_in_directory_csv(self):
        """Site grain: each PIC-18 active tier A-C site row's street sits in the address cell of its owner-and-county row."""
        rows = {(r["org_id"], r["pic18_counties"]): r for r in csv.DictReader(io.StringIO(self.read("directory.csv").lstrip("\ufeff")))}
        sites = build_site.pic18_active_sites(self.atlas.sites)
        self.assertEqual(len(sites), 5)
        with_street = 0
        for s in sites:
            cell = rows[(s["org_id"], s["county"])]["pic18_site_addresses"]
            if (s.get("street_address") or "").strip():
                with_street += 1
                self.assertIn(s["street_address"].strip(), cell, s["site_id"])
            else:
                self.assertIn("Street not recorded", cell, s["site_id"])
        self.assertEqual(with_street, 2)                                   # SITE-000001 and SITE-000006 carry a street; the other three do not

    def test_without_javascript_the_directory_lists_every_row_on_static_county_pages(self):
        html = self.read("directory.html")
        noscript = "".join(re.findall(r"<noscript>(.*?)</noscript>", html, re.S))   # the shell adds a style-only one for the phone menu
        self.assertIn('href="directory.csv"', noscript)
        self.assertIn('href="directory/summit.html"', noscript)
        self.assertIn('<div id="dfind" hidden>', html)                     # search and filters stay hidden until the script runs
        self.assertNotIn("Loading the list", html)                         # the status text is the script's, not the page's
        seen = []
        for f in sorted((self.out / "directory").glob("*.html")):
            page = f.read_text(encoding="utf-8")
            rows = re.findall(r'<tr><th scope="row"><a href="../orgs/(ORG-\d+)\.html">', page)
            self.assertLessEqual(len(rows), 50, f.name)
            seen += [(r, f.stem) for r in rows]
        self.assertEqual(len(seen), len(json.loads(self.read("directory.json"))["rows"]))   # every row, once
        summit = self.read("directory/summit.html")
        self.assertIn("1 Main St, Akron, OH 44301", summit)
        self.assertIn('<span class="badge">PIC member</span>', summit)
        self.assertIn('href="../directory.html"', summit)

    def test_county_index_a_to_c_column_sums_to_the_headline(self):
        idx = self.read("counties/index.html")
        total = re.search(r'PIC-18 total</th><td></td><td class="num"><strong>([\d,]+)</strong>', idx)
        self.assertIsNotNone(total)
        self.assertEqual(int(total.group(1).replace(",", "")), len(build_site.pic18_active_sites(self.atlas.sites)))
        home = self.read("index.html")
        card = re.search(r'<div class="big">([\d,]+)</div><div class="unit">PIC-18 county site rows', home)
        self.assertEqual(card.group(1), total.group(1))
        self.assertIn("tiers A-C (headline basis)", idx)

    def test_county_pages_have_process_and_band_tables_with_unknown(self):
        stark = self.read("counties/stark.html")
        self.assertIn("Stark County site rows by process (Ohio; operating status active; tiers A-C)", stark)
        self.assertIn("Unknown (no process recorded on the site row)", stark)
        self.assertIn("Stark County site rows by employee band", stark)
        medina = self.read("counties/medina.html")
        self.assertRegex(medina, r"Unknown \(no site band and no parent band\)</th>.*?<strong>|data-sort=\"1\">1</td>")
        portage = self.read("counties/portage.html")
        self.assertRegex(portage, r'<th scope="row">100-249</th><td class="num">0</td><td class="num">1</td><td class="num">1</td>')

    def test_org_page_shows_structured_evidence_only(self):
        org = self.read("orgs/ORG-000001.html")
        self.assertIn('id="evidence">Evidence (4 rows for this organization; 1 more row listed with its sites above)', org)
        for col in ("Claim", "Source class", "Strength", "Observed", "Source"):
            self.assertIn(f'<th scope="col">{col}</th>', org)
        self.assertIn("<td>Exists</td>", org)                               # claim type, not claim text
        self.assertIn("Company&#x27;s own site", org)
        self.assertIn("Supports tier A (primary source)", org)
        self.assertIn('<a href="https://example.com/about" rel="noopener nofollow">https://example.com/about</a>', org)
        self.assertIn('<a href="https://example.org/directory"', org)
        self.assertIn("<td>2026-10-30</td>", org)
        for hidden in ("(own site, accessed", "linkedin.com", "lane_Z99", "PRIVATE-NOTE-XYZ", "staging", "Atlas verification wave"):
            self.assertNotIn(hidden, org)
        self.assertIn("<td>&mdash;</td>", org)                              # EVD-4 cites no link: nothing is printed instead
        self.assertIn("Roster list (a lead, not proof)", self.read("orgs/ORG-000004.html"))
        ob = self.read("orgs/ORG-000003.html")
        self.assertIn("No claim-level evidence rows are recorded", ob)       # falls back to source links
        self.assertIn('href="https://example.org/k"', ob)
        self.assertNotIn("Directory https", ob)

    def test_no_evidence_claim_text_on_any_generated_page_or_csv(self):
        details = [r["claim_detail"] for rows in self.atlas.evidence.values() for r in rows]
        self.assertGreaterEqual(len(details), 6)
        texts = [p.read_text(encoding="utf-8") for p in list(self.out.rglob("*.html")) + [self.out / "directory.csv", self.out / "directory.json"]]
        for d in details:
            for t in texts:
                self.assertNotIn(d, t)
                self.assertNotIn(build_site.esc(d), t)
        for private in ("Jane Roe", "John Poe", "sales.rep@example.com", "330-555-0142", "Akron plant exists", "Freeze"):
            for t in texts:
                self.assertNotIn(private, t)

    def test_directory_evidence_count_matches_the_page(self):
        by = {r["id"]: r["evidence"] for r in build_site.directory_rows(self.atlas)}
        self.assertEqual(by["ORG-000001"], 4 + 1)                           # four org rows + one site row
        self.assertEqual(by["ORG-000004"], 1)

    def test_street_map_and_graph_default_to_pic18(self):
        sites = json.loads(self.read("sites.json"))
        self.assertEqual(sites["cols"][6], "st")
        self.assertEqual(sites["cols"][11], "co")
        self.assertRegex(self.read("map.html"), r'id="f-pic18" checked data-counties="Ashland,Ashtabula,')
        self.assertIn("picOnly", self.read("map.js"))


class DirectoryCompaniesTest(unittest.TestCase):
    """ATLAS-40 first-user fixes: counts are companies (distinct organizations), the member filter, old ?member=no links."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        make_directory_db(tmp / "f.db")
        con = sqlite3.connect(tmp / "f.db")
        cols = ["site_id", "org_id", "site_name", "city", "state", "county", "ring_primary", "processes", "operating_status", "verification_tier", "country"]
        con.execute(f"INSERT INTO sites ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                    ["SITE-000099", "ORG-000004", "Stark Molders - Akron", "Akron", "OH", "Summit", "1", "extrusion", "active", "A", "US"])
        con.commit()
        con.close()
        cls.out = tmp / "site"
        build_site.build_site(tmp / "f.db", cls.out, None, repo_url="https://example.com/repo",
                              git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")
        cls.rows = json.loads((cls.out / "directory.json").read_text(encoding="utf-8"))["rows"]
        cls.html = (cls.out / "directory.html").read_text(encoding="utf-8")
        cls.js = (cls.out / "directory.js").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def option(self, facet, value):
        m = re.search(rf'name="{facet}" value="{value}"> <span class="t">[^<]*</span> <span class="n">(\d+)</span>', self.html)
        self.assertIsNotNone(m, f"{facet}={value}")
        return int(m.group(1))

    def test_an_owner_in_two_counties_is_two_rows_and_one_company(self):
        ids = [r["id"] for r in self.rows]
        self.assertEqual(ids.count("ORG-000004"), 2)
        self.assertGreater(len(ids), len(set(ids)))
        with_ext = {r["id"] for r in self.rows if "extrusion" in r["tok"]["proc"]}
        self.assertIn("ORG-000004", with_ext)
        self.assertEqual(self.option("proc", "extrusion"), len(with_ext))                 # counted once, not once per county row
        ring1_rows = [r for r in self.rows if "1" in r["tok"]["ring"]]
        self.assertEqual(self.option("ring", "1"), len({r["id"] for r in ring1_rows}))   # ORG-000004 has a ring-1 row in each county
        self.assertLess(self.option("ring", "1"), len(ring1_rows))
        self.assertEqual(self.option("co", "Summit"), len({r["id"] for r in self.rows if r["co"] == "Summit"}))

    def test_member_filter_is_the_public_flag_and_its_caveat_is_on_the_page(self):
        by = {r["id"]: r for r in self.rows}
        self.assertTrue(by["ORG-000001"]["member"])
        self.assertFalse(by["ORG-000004"]["member"])
        self.assertTrue(all("mem" not in r["tok"] for r in self.rows))                       # the data file carries no member token, least of all "no"
        self.assertIn("r.tok.mem = [r.member ? 'yes' : 'no']", self.js)                      # the filter derives from the public badge flag in the page script
        self.assertEqual(self.option("mem", "yes") + self.option("mem", "no"), len(set(by)))   # every company is one or the other, once
        self.assertIn('<div class="banner note">', self.html)
        self.assertIn('is not the same as "not a member"', self.html)
        self.assertIn("mem: 'member'", self.js)                                              # ?member=no (an old prospects link) applies the filter
        self.assertIn("location.replace('directory.html' + location.search", (self.out / "prospects.js").read_text(encoding="utf-8"))

    def test_status_line_names_companies_then_rows(self):
        self.assertIn("' companies ('", self.js)
        self.assertIn("', one per owner and county).'", self.js)
        self.assertNotIn("rows (one per owner and county).'", self.js.replace(", one per owner and county).'", ""))   # the old row-only line is gone
        self.assertIn("Counts are companies.", self.html)
        self.assertIn("var lost = Object.keys(counts[f]['_'] || {}).filter(function (id) { return !companies[id]; }).length;", self.js)   # left out = no row on the list
        self.assertIn("' with unknown ' + NAME[f] + ' in at least one county'", self.js)
        self.assertIn("Unknown in at least one county (nothing recorded)", self.html)
        self.assertIn("Every filter except the member flag", self.html)
        self.assertIn('A row with the "PIC member" badge is on the public member list. A row without it is not marked either way', self.html)
        self.assertNotIn('is marked "on the public member list" or', self.html)                # the list shows a badge for Yes only; help must not promise a row label for No
        doc = (Path(build_site.__file__).resolve().parent.parent / "docs" / "SITE_HOWTO.md").read_text(encoding="utf-8")
        self.assertIn("each lists its unknown count except the member flag", doc)


class RealDataHeadlineTest(unittest.TestCase):
    """The PIC-18 numbers on the built pages, recomputed from the canonical CSVs in data/ with the csv module alone
    (no builder helper, no SQLite): the headline, the county index total, the directory rows, the summary tables and two filter counts."""

    @classmethod
    def setUpClass(cls):
        root = build_site.ROOT
        subprocess.run([sys.executable, str(root / "scripts" / "build_sqlite.py")], check=True, capture_output=True, cwd=root)
        con = sqlite3.connect(f"file:{root / 'build' / 'polymer-atlas.db'}?mode=ro", uri=True)
        cls.atlas = build_site.Atlas(con)
        con.close()
        cls.ctx = build_site.Ctx(cls.atlas, build_site.load_qcew(build_site.DEFAULT_QCEW),
                                 {"sha": "test", "date": "2026-11-16", "dirty": False}, build_site.DEFAULT_REPO,
                                 "2026-11-16", "2026-11-16")
        data = root / "data"

        def read(pattern):
            for f in sorted(data.glob(pattern)):
                with open(f, newline="", encoding="utf-8") as fh:
                    yield from csv.DictReader(fh)
        pic18 = set(build_site.PIC12)
        cls.sites = [r for r in read("sites_*.csv") if r["state"] == "OH" and r["county"] in pic18
                     and r["operating_status"] == "active" and r["verification_tier"] in ("A", "B", "C")]
        orgs = {r["org_id"]: r for r in read("organizations_*.csv")}
        orgs.update({r["org_id"]: r for r in read("ecosystem.csv")})
        by = {}
        for s in cls.sites:
            by.setdefault(s["org_id"], []).append(s)

        # SCHEMA 4.24: a value whose basis is not_found_pending_refetch is on no page, so the oracle drops it too (read from the CSV, not from the generator)
        withheld = {(r["record_table"], r["record_id"], r["field"], r["value"]) for r in read("value_basis.csv") if r["basis"] == "not_found_pending_refetch"}

        def tokens(v, table=None, rid=None, field="processes"):
            return {t.strip() for t in (v or "").split(";") if t.strip() and t.strip() != "unknown" and (table, rid, field, t.strip()) not in withheld}
        cls.eco_ids = {r["org_id"] for r in read("ecosystem.csv")}
        by_key = {}
        for s in cls.sites:
            by_key.setdefault((s["org_id"], s["county"]), []).append(s)
        cls.by_key = by_key                                                # one directory row per organization and county
        cls.summit_orgs = {o for o, c in by_key if c == "Summit"}
        cls.member_rows = {k for k in by_key if orgs[k[0]].get("pic_member") == "true"}
        cls.injection = set()
        for (o, c), ss in by_key.items():
            t = set().union(*(tokens(s["processes"], "sites", s["site_id"]) for s in ss)) or tokens(orgs[o].get("processes"), "organizations", o)   # site first, else org
            if "injection_molding" in t:
                cls.injection.add((o, c))
        cls.by_org = by

    def number(self, pattern, html):
        m = re.search(pattern, html)
        self.assertIsNotNone(m, pattern)
        return int(m.group(1).replace(",", ""))

    def test_headline_and_county_total_match_the_csvs(self):
        expected = len(self.sites)
        self.assertGreater(expected, 800)                                  # an empty read must fail, not pass
        home = build_site.build_index(self.ctx)
        self.assertEqual(self.number(r'<div class="big">([\d,]+)</div><div class="unit">PIC-18 county site rows', home), expected)
        idx = build_site.build_counties_index(self.ctx)
        self.assertEqual(self.number(r'PIC-18 total</th><td></td><td class="num"><strong>([\d,]+)</strong>', idx), expected)
        page = build_site.build_directory_page(self.ctx, build_site.directory_rows(self.atlas))
        self.assertEqual(self.number(r"([\d,]+) such site rows", page), expected)

    def test_directory_rows_are_the_organizations_and_counties_of_those_sites(self):
        rows = build_site.directory_rows(self.atlas)
        self.assertEqual({r["id"] for r in rows}, set(self.by_org))
        self.assertEqual({(r["id"], r["county"]) for r in rows}, set(self.by_key))
        self.assertEqual(len(rows), len(self.by_key))
        self.assertGreater(len(self.by_key), len(self.by_org))             # some organizations have sites in two counties
        page = build_site.build_directory_page(self.ctx, rows)
        self.assertEqual(page.count("<tr data-"), 0)                       # at most 50 rows are ever drawn, by directory.js
        self.assertEqual(self.number(r"<p class=\"lede\">([\d,]+) owners", page), len(self.by_org))
        n_eco = len(set(self.by_org) & self.eco_ids)
        self.assertGreater(n_eco, 0)
        self.assertEqual(self.number(r"([\d,]+) organization records and", page), len(self.by_org) - n_eco)   # the unit's two parts
        self.assertEqual(self.number(r"([\d,]+) ecosystem records", page), n_eco)
        static = build_site.directory_static_pages(self.ctx, rows)       # the no-JavaScript path holds every row, 50 a page
        counts = [len(re.findall(r'<tr><th scope="row"><a href="../orgs/', h)) for h in static.values()]
        self.assertEqual(sum(counts), len(self.by_key))
        self.assertLessEqual(max(counts), 50)

    def test_directory_csv_carries_every_site_street(self):
        """Site grain: every PIC-18 site row's street, recomputed from the site CSVs, is in its owner-and-county row."""
        rows = {(r["org_id"], r["pic18_counties"]): r["pic18_site_addresses"]
                for r in csv.DictReader(io.StringIO(build_site.directory_csv(build_site.directory_rows(self.atlas), build_site.SITE_URL)))}
        streets = 0
        for s in self.sites:
            cell = rows[(s["org_id"], s["county"])]
            if s["street_address"].strip():
                streets += 1
                self.assertIn(s["street_address"].strip(), cell, s["site_id"])
            else:
                self.assertIn("Street not recorded", cell, s["site_id"])
        self.assertGreater(streets, 600)                                   # most site rows have a street; an empty read must fail

    def test_summary_tables_match_the_csvs(self):
        page = build_site.build_directory_page(self.ctx, build_site.directory_rows(self.atlas))
        county = re.search(r"<caption>[^<]* by county</caption>.*?</table>", page, re.S).group(0)
        got = {m.group(1): (int(m.group(2).replace(",", "")), int(m.group(3).replace(",", "")))
               for m in re.finditer(r'<th scope="row"><a href="directory\.html\?county=[^"]+">([^<]+)</a></th><td class="num">([\d,]+)</td><td class="num">([\d,]+)</td>', county)}
        for c in {c for _, c in self.by_key}:
            orgs = {o for o, k in self.by_key if k == c}
            self.assertEqual(got[c], (len(orgs), sum(len(ss) for (o, k), ss in self.by_key.items() if k == c)), c)
        self.assertEqual(sum(n for _, n in got.values()), len(self.sites))   # site rows add up to the headline
        self.assertEqual(sum(n for n, _ in got.values()), len(self.by_key))  # organization rows per county add up to the rows
        self.assertEqual(got["Summit"][0], len(self.summit_orgs))

    def test_filter_counts_match_the_csvs(self):
        rows = build_site.directory_rows(self.atlas)
        pro = build_site.build_directory_page(self.ctx, rows)

        def option(facet, value):
            return self.number(rf'name="{facet}" value="{value}"> <span class="t">[^<]*</span> <span class="n">(\d+)</span>', pro)
        self.assertEqual(option("co", "Summit"), len(self.summit_orgs))
        self.assertEqual(option("proc", "injection_molding"), len({o for o, _ in self.injection}))   # companies, not owner-and-county rows
        self.assertEqual(option("mem", "yes"), len({o for o, _ in self.member_rows}))
        self.assertEqual(option("mem", "no"), len({o for o, _ in self.by_key}) - len({o for o, _ in self.member_rows}))
        self.assertGreater(len(self.injection), 20)
        self.assertGreater(len(self.member_rows), 10)
        listed = json.loads(json.dumps(build_site.directory_json(rows)))["rows"]
        self.assertEqual({(r["id"], r["co"]) for r in listed if r["member"]}, self.member_rows)   # the badge is the public flag

    def test_pages_stay_small(self):
        rows = build_site.directory_rows(self.atlas)
        self.assertLess(len(build_site.build_directory_page(self.ctx, rows).encode()), 100_000)   # was 777 KB with every row inline
        self.assertLess(len(json.dumps(build_site.directory_json(rows)).encode()), 2_000_000)
        self.assertLess(len(build_site.directory_csv(rows, build_site.SITE_URL).encode()), 2_000_000)

    def test_no_evidence_claim_text_on_any_organization_page(self):
        """Free text cannot be made safe by a pattern filter (it names people): no claim_detail may reach any page."""
        checked = leaks = 0
        for table, recs, build in (("organizations", self.atlas.orgs, build_site.build_org_page),
                                   ("ecosystem", self.atlas.eco, build_site.build_eco_page)):
            for rec in recs.values():
                rows = list(self.atlas.evidence.get((table, rec["org_id"]), []))
                for s in self.atlas.sites_by_org.get(rec["org_id"], []):
                    rows += self.atlas.evidence.get(("sites", s["site_id"]), [])
                # Fields the page shows by design can repeat a claim: an address claim repeats the site address, and many
                # scope claims repeat the organization's one-line description. Short values (a code, a street) can also be a
                # shown field, so only longer claim text that is not one of those shown names or descriptions is checked.
                shown = " | ".join(str(rec.get(k) or "") for k in ("legal_name", "trade_names", "description_1line", "ultimate_parent_name"))
                shown += " | " + " | ".join(str(x.get("site_name") or "") for x in self.atlas.sites_by_org.get(rec["org_id"], []))
                details = {r["claim_detail"] for r in rows if r["claim_type"] != "address"
                           and len(r["claim_detail"] or "") >= 40 and r["claim_detail"] not in shown}
                if not details:
                    continue
                page = build(self.ctx, rec)
                checked += len(details)
                bad = [d for d in details if d in page or build_site.esc(d) in page]
                self.assertEqual(bad, [], f"claim text on the page of {rec['org_id']}")
                leaks += len(bad)
        self.assertGreater(checked, 5000)                                  # the guard really ran over the evidence
        csv_text = build_site.directory_csv(build_site.directory_rows(self.atlas), build_site.SITE_URL)
        for rows in self.atlas.evidence.values():
            for r in rows[:2]:
                if len(r["claim_detail"] or "") >= 40:
                    self.assertNotIn(r["claim_detail"], csv_text)

    def test_evidence_tables_print_urls_not_citation_prose(self):
        shown = 0
        for table, recs in (("organizations", self.atlas.orgs), ("ecosystem", self.atlas.eco)):
            for rec in recs.values():
                rows = self.atlas.evidence.get((table, rec["org_id"]), [])
                if not rows:
                    continue
                html = build_site.evidence_table(rows, "x")
                shown += 1
                self.assertNotRegex(html, r"@[A-Za-z0-9-]+\.[A-Za-z]")             # no email address in any cell or link
                self.assertNotRegex(html, r"linkedin\.com/(in|pub)/")
        self.assertGreater(shown, 1000)


NAV_LABELS = ["Find companies", "Map", "Counties", "Research & programs", "About the data"]
GRAPH_PAGES = ("index", "map", "events")


class ShellParser(HTMLParser):
    """What a page offers a visitor before its own content: stylesheet, skip link and its target, nav, landmarks."""

    def __init__(self):
        super().__init__()
        self.css, self.skip, self.nav, self.menu_buttons, self.landmarks, self.ids = [], [], [], 0, set(), set()
        self.scripts, self._in_nav, self._li_depth, self._text, self.headers = [], False, 0, None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "link" and a.get("rel") == "stylesheet":
            self.css.append(a.get("href", ""))
        if tag == "a" and "skip" in (a.get("class") or "").split():
            self.skip.append(a.get("href"))
        if tag in ("main", "footer"):
            self.landmarks.add(tag)
        if tag == "header":
            self.headers += 1
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "nav" and a.get("aria-label") == "Main":
            self._in_nav = True
        if tag == "a" and self._in_nav:
            self._text = []
        if tag == "button" and a.get("aria-expanded") is not None and a.get("aria-controls"):
            self.menu_buttons += 1

    def handle_endtag(self, tag):
        if tag == "nav":
            self._in_nav = False
        if tag == "a" and self._text is not None:
            self.nav.append(html_lib.unescape("".join(self._text)).strip())
            self._text = None

    def handle_data(self, data):
        if self._text is not None:
            self._text.append(data)


class SiteShellTest(unittest.TestCase):
    """ATLAS-40: every built HTML page, the three graph pages included, is the same site (one shell, one stylesheet)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        make_directory_db(tmp / "f.db")
        cls.out = tmp / "site"
        build_site.build_site(tmp / "f.db", cls.out, None, repo_url="https://example.com/repo",
                              git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")
        scripts = Path(__file__).resolve().parent
        (cls.out / "graph").mkdir()
        for name, script in (("index", "build_graph.py"), ("map", "build_geo_graph.py"), ("events", "build_events_3d.py")):
            subprocess.run([sys.executable, str(scripts / script), "--out", str(cls.out / "graph" / f"{name}.html")],
                           check=True, capture_output=True)
        cls.pages = sorted(cls.out.rglob("*.html"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def parsed(self, path):
        p = ShellParser()
        p.feed(path.read_text(encoding="utf-8"))
        return p

    def test_the_inspected_set_has_every_kind_of_page(self):
        names = {str(p.relative_to(self.out)) for p in self.pages}
        for rel in ("index.html", "404.html", "prospects.html", "directory.html", "map.html", "search.html", "experts.html", "skyline.html",
                    "counties/index.html", "counties/summit.html", "orgs/ORG-000001.html", "orgs/ORG-000501.html",
                    "graph/index.html", "graph/map.html", "graph/events.html"):
            self.assertIn(rel, names)
        self.assertTrue(any(n.startswith("directory/") for n in names))

    def test_every_html_page_has_the_shared_stylesheet_skip_link_nav_main_and_footer(self):
        for path in self.pages:
            with self.subTest(page=str(path.relative_to(self.out))):
                p = self.parsed(path)
                self.assertEqual([c.rsplit("/", 1)[-1] for c in p.css],
                                 ["style.css", "leaflet.css"] if path.name == "map.html" and path.parent == self.out else ["style.css"])
                self.assertFalse([c for c in p.css if c.startswith("http")])
                self.assertEqual(p.skip, ["#main"])
                self.assertIn("main", p.ids)
                self.assertEqual(p.landmarks, {"main", "footer"})
                self.assertEqual(p.headers, 1)
                self.assertEqual(p.nav, NAV_LABELS)
                self.assertEqual(p.menu_buttons, 1)                      # phones: a Menu button, not a clipped strip
                text = path.read_text(encoding="utf-8")
                self.assertIn("directory.csv", text)                     # the footer's two takeaways, on every page
                self.assertIn("releases/latest", text)
                self.assertTrue(any(s.rsplit("/", 1)[-1] == "shell.js" for s in p.scripts))   # the button works on every page

    def test_graph_pages_carry_no_second_set_of_tokens_or_chrome(self):
        for name in GRAPH_PAGES:
            text = (self.out / "graph" / f"{name}.html").read_text(encoding="utf-8")
            with self.subTest(page=name):
                self.assertNotIn(":root", text)                           # tokens come from style.css only
                self.assertNotIn("@font-face", text)
                self.assertNotIn("claude:", text)
                self.assertRegex(text, r"(?s)<head>.*<title>.*</title>.*</head>.*<body")   # title in the head, not the body
                self.assertNotRegex(text, r"--ring[1-5x]")                # one Ring 1-5 palette: --r1..--r5

    def test_home_hero_is_static(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("three.min.js", home)
        self.assertNotIn('id="skyline"', home)
        self.assertIn("<h1", home)
        self.assertIn('href="skyline.html"', home)                          # the 3D view is one click away, on its own page
        sky = (self.out / "skyline.html").read_text(encoding="utf-8")
        self.assertIn("vendor/three.min.js", sky)                          # three.js loads there and nowhere else
        self.assertIn("skyline.js", sky)
        for rel in ("skyline.js", "skyline.json", "vendor/three.min.js"):
            self.assertTrue((self.out / rel).is_file(), rel)

    def test_no_one_row_plurals_on_any_built_page(self):
        bad = re.compile(r"\b1 (?:[a-z]+ )?(?:rows|sites|programs|organizations|institutions|researchers)\b(?! (?:per|in|with))", re.I)
        for path in self.pages:
            for m in bad.finditer(re.sub(r"<[^>]+>", " ", path.read_text(encoding="utf-8"))):
                self.fail(f"{path.relative_to(self.out)}: {m.group(0)!r}")
        # the case exists in this fixture, so the check above could have failed
        org = (self.out / "orgs" / "ORG-000004.html").read_text(encoding="utf-8")
        self.assertRegex(org, r"Sites \(1 site row[;)]")

    def test_no_site_row_wording_that_points_the_wrong_way(self):
        self.assertNotIn("more on its site rows below", (self.out / "orgs" / "ORG-000001.html").read_text(encoding="utf-8"))

    def test_table_toolbar_sits_above_the_table_with_count_download_and_copy_link(self):
        js = (self.out / "sortable.js").read_text(encoding="utf-8")
        for needle in ("Download these rows (CSV)", "Copy link", "tbar"):
            self.assertIn(needle, js)
        self.assertRegex(js, r"insertBefore\(bar, wrap\)")                 # above the table, not after it
        self.assertNotRegex(js, r"insertBefore\(p, wrap\.nextSibling\)")   # the old below-the-table download paragraph
        self.assertNotRegex(js, r"(?:rows|row match)[\"']\s*;?\s*$|\+ ['\"] rows['\"]")   # counts go through plural()

    def test_street_map_dots_read_the_same_ring_palette_as_the_key(self):
        js = (self.out / "map.js").read_text(encoding="utf-8")
        self.assertNotRegex(js, r"'[1-5x]'\s*:\s*'#")                      # no second hex palette for the dots
        self.assertIn("'--r' + k", js)                                     # they read --r1..--r5, --rx, the tokens the key uses
        css = (self.out / "style.css").read_text(encoding="utf-8")
        for k in "12345x":
            self.assertRegex(css, rf"--r{k}:#[0-9a-f]{{6}}")

    def test_atlas_wide_search_stays_one_click_from_find_companies_and_home(self):
        for rel in ("directory.html", "index.html"):
            self.assertIn('href="search.html"', (self.out / rel).read_text(encoding="utf-8"), rel)

    def test_toolbar_does_not_depend_on_sorting(self):
        js = (self.out / "sortable.js").read_text(encoding="utf-8")
        self.assertNotRegex(js, r"hasAttribute\('data-nosort'\)\) return")   # data-nosort removes the sort buttons only
        county = next((self.out / "directory").glob("*.html")).read_text(encoding="utf-8")
        self.assertRegex(county, r"<table data-nosort>")                   # the 50-row county pages get count, download and copy link
        self.assertNotIn("data-nocsv", county)
        self.assertIn('id="dtable" class="stack" data-nosort data-nofilter data-nocsv', (self.out / "directory.html").read_text(encoding="utf-8"))   # the list has its own toolbar

    @staticmethod
    def external_refs(text):
        """Every src/href on a script, link, img, iframe or source tag that names another host, read by an HTML parser
        (a regex is fooled by a '>' inside an earlier attribute value)."""
        found = []

        class P(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "link", "img", "iframe", "source", "video", "audio", "embed", "object"):
                    for name, value in attrs:
                        v = (value or "").strip().lower()
                        if name in ("src", "href", "data", "poster", "srcset") and re.match(r"(?:https?:)?//", v):
                            found.append(f"<{tag} {name}={value}>")
        p = P()
        p.feed(text)
        p.close()
        return found

    def test_the_external_reference_check_catches_every_way_to_write_one(self):
        for sample in ('<script src="https://x.example/a.js"></script>', "<script src='https://x.example/a.js'></script>",
                       "<script src=https://x.example/a.js></script>", '<link rel="stylesheet" href="//x.example/a.css">',
                       "<img alt='' src='http://x.example/a.png'>", '<script defer SRC = "https://x.example/a.js">',
                       '<script title="Maps > Layers" src="https://example.invalid/lib.js"></script>',
                       "<script title='a > b' data-x=\"c > d\" src='//example.invalid/lib.js'></script>"):
            self.assertTrue(self.external_refs(sample), sample)
        for sample in ('<script src="shell.js"></script>', "<link rel='stylesheet' href='style.css'>", '<a href="https://github.com/x">x</a>',
                       '<script title="https://x.example" src="a.js"></script>'):
            self.assertFalse(self.external_refs(sample), sample)

    def test_no_page_or_script_asks_another_host_for_anything_but_osm_tiles(self):
        for path in self.pages:
            refs = self.external_refs(path.read_text(encoding="utf-8"))
            self.assertEqual(refs, [], str(path.relative_to(self.out)))
        js_pat = re.compile(r"""(?:fetch\(|importScripts\(|\.src\s*=|new URL\()\s*[`"']https?://""")
        for path in self.out.rglob("*.js"):
            if "vendor" in path.relative_to(self.out).parts:
                continue
            text = path.read_text(encoding="utf-8")
            for m in js_pat.finditer(text):
                self.assertIn("tile.openstreetmap.org", text[m.start():m.end() + 40], path.name)

    def test_vendored_libraries_are_published_with_license_and_checksums(self):
        for lib in build_site.VENDOR_LIBS:
            sums = (self.out / "vendor" / lib / "SHA256SUMS").read_text(encoding="utf-8")
            self.assertRegex(sums, r"registry integrity sha512-")
            self.assertTrue((self.out / "vendor" / lib / "LICENSE").is_file(), lib)

    def test_each_explorer_page_names_files_that_exist_and_holds_no_data(self):
        for name, boot, data in (("index", "graph.js", "graph.json"), ("map", "map-network.js", "map-network.json"),
                                 ("events", "trade-shows.js", "trade-shows.json")):
            path = self.out / "graph" / f"{name}.html"
            text = path.read_text(encoding="utf-8")
            with self.subTest(page=name):
                self.assertLess(len(text), 60_000)                        # the data is fetched on a big screen, never shipped to a phone
                self.assertNotRegex(text, r"<script(?![^>]*\bsrc=)[^>]*>")  # no inline script, no inline JSON
                libs = re.search(r'data-libs="([^"]*)"', text).group(1).split()
                self.assertEqual(re.search(r'data-boot="([^"]*)"', text).group(1), boot)
                for rel in [*libs, boot, data]:
                    self.assertTrue((path.parent / rel).is_file(), rel)   # each resolves, relative to the page
                self.assertIn('class="viz-summary"', text)                # a phone gets a summary with the ring legend
                self.assertIn("Ring 1", text)
                self.assertIn('href="../directory.html"', text)           # and the way to the company list
                self.assertIn('href="../search.html"', text)              # and to the Atlas-wide search
                self.assertNotIn("same companies", text)                  # the list is the 18 PIC counties, not every company on the graph
                self.assertIn("18 PIC counties", text)

    def test_explorer_loader_skips_phones_and_the_legend_wording(self):
        js = (self.out / "explorer.js").read_text(encoding="utf-8")
        self.assertIn("719.98", js)                                        # below 720 px: nothing is loaded
        geo = (self.out / "graph" / "map-network.js").read_text(encoding="utf-8")
        self.assertIn("if (vw < 10 || vh < 10) return;", geo)                # a hidden stage (shrunk to a phone) is not drawn
        self.assertEqual(geo.count("ctx.arc("), geo.count("Math.max(0, "))    # every arc radius is clamped at zero
        self.assertRegex(js, r"narrow\.addEventListener\('change'")        # and it loads when the window grows past 720 px (rotate, resize)
        graph = (self.out / "graph" / "graph.js").read_text(encoding="utf-8")
        self.assertNotIn("Not on the public member list", graph)           # absence from the public list is never stated (AGENTS 5.1)
        for rel in ("graph.js", "map-network.js", "trade-shows.js"):
            text = (self.out / "graph" / rel).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"--ring[1-5x]")
            self.assertNotIn("producers & processors", text)               # ring names come from RINGS

    def test_every_built_script_parses(self):
        import shutil
        node = shutil.which("node")
        self.assertIsNotNone(node, "node is needed to syntax-check the built scripts")     # a missing check must not look like a pass
        scripts = [p for p in self.out.rglob("*.js") if "vendor" not in p.relative_to(self.out).parts]
        self.assertGreater(len(scripts), 10)
        for path in scripts:
            r = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"{path.relative_to(self.out)}: {r.stderr[:300]}")

    def test_phone_menu_toggles_aria_expanded(self):
        js = (self.out / "shell.js").read_text(encoding="utf-8")
        self.assertIn("aria-expanded", js)
        self.assertIn("Escape", js)

    def test_graph_pages_have_a_plain_text_route_and_a_way_back_in_the_shell(self):
        for name in GRAPH_PAGES:
            text = (self.out / "graph" / f"{name}.html").read_text(encoding="utf-8")
            with self.subTest(page=name):
                self.assertIn('<main id="main"', text)
                self.assertIn('href="../directory.html"', text)           # the company list (18 PIC counties)



def luminance(hex_color):
    c = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class BlockingFixesTest(unittest.TestCase):
    """ATLAS-40 PR 3: addresses where the first user looks, the accessibility failures the audit measured, readable vocabulary labels."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        make_directory_db(tmp / "f.db")
        cls.out = tmp / "site"
        build_site.build_site(tmp / "f.db", cls.out, None, repo_url="https://example.com/repo",
                              git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def tokens(self, css, dark):
        block = re.search(r"@media \(prefers-color-scheme: dark\)\{\s*:root\{(.*?)\}\s*\}", css, re.S).group(1) if dark else re.search(r":root\{(.*?)\}", css, re.S).group(1)
        return dict(re.findall(r"--([a-z0-9-]+):(#[0-9a-fA-F]{6})", block))

    def test_county_sites_table_has_street_and_zip_as_recorded_never_invented(self):
        html = self.read("counties/summit.html")
        self.assertIn('<th scope="col">Street address</th><th scope="col">City</th><th scope="col">ZIP</th>', html)
        self.assertIn("<td>1 Main St</td><td>Akron</td><td>44301</td>", html)                       # the recorded street and ZIP
        self.assertEqual(html.count("<td>Street not recorded</td>"), 2)                             # the two Summit rows with no street say so

    def test_street_map_data_popup_and_list_carry_the_address(self):
        data = json.loads(self.read("sites.json"))
        self.assertEqual(data["cols"][-2:], ["street", "zip"])
        by = {r[0]: r for r in data["rows"]}
        self.assertEqual(by["SITE-000001"][-2:], ["1 Main St", "44301"])
        self.assertEqual(by["SITE-000002"][-2:], ["", ""])                                          # no street recorded: empty, not guessed
        js = self.read("map.js")
        self.assertIn("'Address: '", js)
        self.assertIn("Street not recorded", js)
        self.assertIn("Show on map", js)                                                            # the keyboard route to every dot
        self.assertIn("'aria-label': 'Show on map: '", js)                                          # the accessible name starts with the visible words
        self.assertIn('id="maplist"', self.read("map.html"))

    def test_search_results_carry_the_address_of_a_single_site_organization(self):
        data = json.loads(self.read("orgs.json"))
        addr = {r[0]: r[data["cols"].index("addr")] for r in data["rows"]}
        self.assertEqual(addr["ORG-000005"], "Address: 500 Portage Rd, Ravenna, OH")
        self.assertEqual(addr["ORG-000004"], "Address: Street not recorded, Canton, OH")
        self.assertEqual(addr["ORG-000001"], "2 active site rows: addresses on its page")           # two sites: the count, not a guess at which
        self.assertEqual(addr["ORG-000002"], "")                                                    # closed: no active site row
        self.assertIn("r[C.addr]", self.read("search.js"))

    def test_search_page_does_not_steal_focus_from_the_skip_link(self):
        self.assertNotIn("autofocus", self.read("search.html"))

    def test_contrast_of_the_active_tab_and_zero_count_options_in_both_schemes(self):
        css = self.read("style.css")
        self.assertIn(".xtabs button[aria-pressed=true]{background:var(--accent);color:var(--accent-fg)}", css)
        self.assertNotRegex(css, r"label\.opt\.zero\{[^}]*opacity")
        self.assertIn("label.opt.zero{color:var(--muted)}", css)
        for dark in (False, True):
            t = self.tokens(css, dark)
            self.assertGreaterEqual(contrast(t["accent-fg"], t["accent"]), 4.5, ("active tab", dark))
            self.assertGreaterEqual(contrast(t["muted"], t["panel"]), 4.5, ("zero-count option", dark))

    def test_checkboxes_and_sort_buttons_meet_the_24px_target(self):
        css = self.read("style.css")
        self.assertIn("input[type=checkbox],input[type=radio]{width:24px;height:24px", css)
        self.assertIn(".viz input[type=checkbox]{accent-color:var(--accent);margin:0;width:24px;height:24px", css)
        self.assertRegex(css, r"th\[aria-sort\] button\.sort\{[^}]*min-height:24px")

    def test_stacked_phone_cards_take_their_hidden_sort_buttons_out_of_the_tab_order(self):
        js = self.read("sortable.js")
        self.assertRegex(js, r"tabIndex = phone\.matches && table\.classList\.contains\('stack'\) \? -1 : 0")

    def test_vocab_labels_are_schema_tokens_and_read_as_words(self):
        schema = (Path(build_site.__file__).resolve().parent.parent / "docs" / "SCHEMA.md").read_text(encoding="utf-8")
        for token in build_site.VOCAB_LABELS:
            self.assertIn(f"`{token}`", schema, token)                                              # a label for a token, never a new term
        self.assertEqual(build_site.vocab("corporation_public;llc"), "public corporation, LLC")
        self.assertEqual(build_site.vocab("automotive_unspecified"), "automotive (OEM or aftermarket not stated)")
        self.assertEqual(build_site.vocab("injection_molding;pet_petg"), "injection molding, PET / PETG")   # unmapped words and SPEC_LABELS still work

    def test_labels_show_on_the_organization_page_not_the_slug(self):
        build_site_html = self.read("orgs/ORG-000001.html")
        self.assertNotIn("corporation private", build_site_html)
        self.assertIn("private corporation", build_site_html)

    def test_directory_search_matches_street_and_city_and_keeps_the_find_fragment(self):
        js = self.read("directory.js")
        self.assertIn("r.name + ' ' + r.addr.join(' ')", js)
        self.assertIn("+ location.hash);", js)
        self.assertIn("Name, street or city contains", self.read("directory.html"))

    def test_experts_finder_has_sortable_downloadable_tables_and_one_population(self):
        js = self.read("experts.js")
        self.assertIn("window.atlasTable(t)", js)                                                   # the shared sort and toolbar on the browse table
        self.assertIn("xcsv", js)
        self.assertIn('id="xcsv"', self.read("experts.html"))
        self.assertNotIn("D.pc[", js)                                                               # the browse table counts the matched records, not all of them
        self.assertIn("window.atlasTable = function", self.read("sortable.js"))
        self.assertIn("u.set('kind', kind)", js)                                                    # Copy link holds every selection ...
        self.assertIn("u.set('view'", js)
        self.assertIn("pick('show', 'both')", js)                                                   # ... and the page reads them back

    def test_show_more_sites_keeps_keyboard_focus_and_grouped_process_labels_make_no_claim_of_both(self):
        self.assertIn("added.querySelector('a').focus()", self.read("map.js"))
        self.assertEqual(build_site.vocab("latex_dipping_foaming"), "latex dipping / foaming")   # the schema's one grouped category, not two claims
        for token in ("assembly_secondary_ops", "die_cutting_converting", "rubber_mixing_compounding", "potting_encapsulation_casting"):
            self.assertNotIn(" & ", build_site.vocab(token), token)

    def test_trade_show_space_key_leaves_focused_buttons_alone(self):
        script = (Path(build_site.__file__).resolve().parent / "build_events_3d.py").read_text(encoding="utf-8")
        self.assertIn('closest("input, select, textarea, button, a, summary, .participants")', script)

    def test_home_hero_does_not_say_all_states_for_a_count_that_includes_other_countries(self):
        home = self.read("index.html")
        self.assertNotIn("across all states", home)
        self.assertIn("all locations held, not only US states", home)



class RefuteFixesTest(unittest.TestCase):
    """ATLAS-40 PR 4: findings of the completion refute (geography labels, phone directory order, privacy filters, HOWTO claims)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        make_directory_db(tmp / "f.db")
        con = sqlite3.connect(tmp / "f.db")
        crm = "https://example.invalid/crm-source"
        con.execute("UPDATE organizations SET sources=? WHERE org_id='ORG-000002'", ("PIC CRM " + crm,))
        con.execute("UPDATE organizations SET sources=? WHERE org_id='ORG-000003'",
                    ("Directory https://example.org/k; CRM export https://example.invalid/crm2; staging working/x.csv",))
        con.execute("UPDATE people SET public_profile_url=?", ("https://example.invalid/profile?mail=fixture%40example.invalid",))
        con.execute("UPDATE sites SET country='CA' WHERE site_id='SITE-000006'")
        con.execute("UPDATE organizations SET description_1line=? WHERE org_id='ORG-000006'",
                    ("Designed endpoint parent (verification wave 1, lane CF adjudication s4): Fixture Co.",))
        con.execute("UPDATE organizations SET description_1line='Makes foam parts.' WHERE org_id='ORG-000005'")
        con.execute("UPDATE organizations SET website='none_found' WHERE org_id='ORG-000004'")
        con.execute("UPDATE organizations SET processes='other_specified_in_notes;extrusion' WHERE org_id='ORG-000005'")
        con.commit()
        con.close()
        cls.out = tmp / "site"
        build_site.build_site(tmp / "f.db", cls.out, None, repo_url="https://example.com/repo",
                              git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")
        cls.crm = crm
        cls.profile = "https://example.invalid/profile?mail=fixture%40example.invalid"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def test_geography_of_a_count_is_named_not_called_all_states(self):
        self.assertEqual(build_site.geo_note([{"country": "US"}, {"country": "CA"}, {"country": "GB"}]), "1 in the US, 2 elsewhere")
        for rel in ("index.html", "skyline.html"):
            self.assertNotIn("all states", self.read(rel), rel)
        home = self.read("index.html")
        self.assertRegex(home, r"Site rows by ring \(operating status active; tiers A-C; all locations held: \d+ in the US, [1-9]\d* elsewhere\)")
        self.assertRegex(self.read("skyline.html"), r"\d+ in the US, [1-9]\d* elsewhere")

    def test_directory_summary_is_a_block_that_starts_closed_on_a_phone_so_the_list_follows_the_tab_order(self):
        html = self.read("directory.html")
        self.assertIn('<details class="dsummary" id="counts" open>', html)         # open on a desktop and without JavaScript
        self.assertIn('href="#counts"', html)                                        # the way to the county counts from the top
        self.assertNotIn('href="#find"', html)                                       # no shortcut into the part that is hidden without JavaScript
        css = self.read("style.css")
        self.assertNotIn(".dpage", css)                                              # no CSS reordering: visual order is document order
        self.assertNotRegex(css, r"dsummary\{[^}]*order")
        js = self.read("directory.js")
        self.assertIn("if (summary) summary.open = false;", js)
        self.assertRegex(js, r"details\.facet'\), function \(d\) \{ d\.open = false; \}")
        self.assertLess(html.index('id="counts"'), html.index('id="dfind"'))          # document order: summary, then the finder and list

    def test_embeds_email_sees_every_encoding(self):
        for u in ("https://x.example/p?mail=a@b.example", "https://x.example/p?mail=a%40b.example", "https://x.example/p?mail=a%2540b.example"):
            self.assertTrue(build_site.embeds_email(u), u)
            self.assertIsNone(build_site.safe_href(u), u)
        self.assertFalse(build_site.embeds_email("https://x.example/people/jane-roe"))

    def test_crm_marked_sources_never_render_and_the_omitted_count_is_stated(self):
        page = self.read("orgs/ORG-000002.html")
        self.assertNotIn(self.crm, page)
        self.assertNotIn("PIC CRM", page)
        self.assertIn("1 source entry left out of this view because it refers to internal material", page)
        k = self.read("orgs/ORG-000003.html")
        self.assertIn("https://example.org/k", k)                                     # the public entry stays
        self.assertNotIn("crm2", k)
        self.assertIn("2 source entries left out of this view because they refer to internal material", k)
        for p in self.out.rglob("*.html"):
            self.assertNotIn(self.crm, p.read_text(encoding="utf-8"), p.name)

    def test_encoded_email_in_a_profile_url_is_published_nowhere(self):
        self.assertNotIn(self.profile, self.read("experts.json"))
        self.assertNotIn("fixture%40example", self.read("experts.json"))
        for p in (self.out / "orgs").glob("*.html"):
            self.assertNotIn("fixture%40example", p.read_text(encoding="utf-8"), p.name)

    def test_source_classifier_catches_routine_private_labels_and_keeps_the_public_member_list(self):
        private = ("PIC crm https://example.invalid/a", "workshop/internal/reader.csv https://example.invalid/b", "staging/x.csv https://example.invalid/c",
                   "CRM export https://example.invalid/d", "working/x.csv", "internal/notes https://example.invalid/e")
        for e in private:
            self.assertEqual(build_site.source_urls(e), [], e)
            self.assertEqual(build_site.omitted_sources(e), 1, e)
        keep = "Public PIC member list https://polymerindustrycluster.org/members; Company site https://example.com/about"
        self.assertEqual(build_site.source_urls(keep), ["https://polymerindustrycluster.org/members", "https://example.com/about"])
        self.assertEqual(build_site.omitted_sources(keep), 0)
        for ordinary in ("University course page https://example.edu/education/workshop/session.pdf",
                         "Plant page https://example.com/internal/about", "Public university workshop announcement https://example.edu/workshop", "Internal Revenue Service filing https://irs.example/f",
                         "Staging area plant page https://example.com/staging"):
            self.assertEqual(build_site.omitted_sources(ordinary), 0, ordinary)
            self.assertEqual(len(build_site.source_urls(ordinary)), 1, ordinary)
        self.assertEqual(build_site.lede("Exists only in the pic crm record."), build_site.lede("Exists only in the PIC CRM record."))
        self.assertIn("withheld", build_site.lede("Exists only in the pic crm record."))

    def test_description_with_build_wording_is_withheld_on_the_page_and_in_the_graph(self):
        leak = self.read("orgs/ORG-000006.html")
        self.assertNotIn("verification wave", leak)
        self.assertNotIn("lane CF", leak)
        self.assertIn("withheld from this view because it may refer to internal material", leak)
        ok = self.read("orgs/ORG-000005.html")
        self.assertIn('<p class="lede">Makes foam parts.</p>', ok)                        # an ordinary description still shows
        self.assertTrue(build_site.internal_wording("Designed endpoint parent (verification wave 1, lane CF adjudication s4)"))
        self.assertTrue(build_site.internal_wording("Rung 1 carried by the packet; CHANGED from wave 7"))
        self.assertFalse(build_site.internal_wording("Injection molder of automotive parts."))

    def test_source_classifier_both_directions_on_astras_six_citations(self):
        cases = [("Public university workshop announcement https://example.invalid/education/course", True),
                 ("Public PIC member list https://example.invalid/members", True),
                 ("Internal Revenue Service filing https://example.invalid/filing", True),
                 ("Staging area plant page https://example.invalid/plant", True),
                 ("workshop/internal/reader.csv https://example.invalid/private", False),
                 ("Public university course https://example.invalid/education/workshop/session.pdf", True),
                 ("AHFA workshop PDF https://www.ahfa.us/Portals/0/workshop/2024/session.pdf", True),
                 ("staging/working/x.csv", False)]
        for text, public in cases:
            self.assertEqual(build_site.omitted_sources(text), 0 if public else 1, text)
            self.assertEqual(bool(build_site.source_urls(text)), public, text)

    def test_temporary_record_ids_are_withheld_from_descriptions(self):
        for text in ("Maker of foam (NEW:MJ-07) in Ohio", "NEW:AB-123 parent"):
            self.assertTrue(build_site.internal_wording(text), text)
            self.assertIn("withheld", build_site.lede(text))
        self.assertFalse(build_site.internal_wording("Makes NEW England clam shells; ID: MJ-07"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("bg", Path(build_site.__file__).resolve().parent / "build_graph.py")
        bg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bg)
        self.assertEqual(bg.public_description("Parent (NEW:MJ-07)"), "")

    def test_build_prose_families_are_withheld_everywhere_the_description_is_shown(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("bg", Path(build_site.__file__).resolve().parent / "build_graph.py")
        bg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bg)
        families = {
            "staged": ["Own site footer: 401 Milford Parkway (matches staged address)", "Staged domain still fails to resolve", "Re-derived from staged tooling"],
            "rung": ["Rung 1 (own website) carried. Own site: molding", "Rung 3 (DOL Form 5500) carried the address", "Rung 4 only; ladder rungs not reached"],
            "unchanged": ["UNCHANGED (VERIFIED B). Own site opened"],
            "browser_open": ["Own site read by browser_open: injection molding"],
            "retry": ["RETRY RECOVERED: own site now loads"],
            "requeue": ["Requeue after the timeout; maker of foam", "requeued for a second read"],
            "settling": ["Settling fact met by a dated filing", "Both settling facts obtained", "The settling primary source named in the prior fact was obtained",
                         "The settling witness is the operator's own postings", "Both settling legs now obtained"],
            "verdict": ["CHANGED (was STILL_UNCERTAIN). Own-site retry failed again", "STILL_UNCERTAIN until the filing is read"],
        }
        for family, texts in families.items():
            for text in texts:
                self.assertTrue(build_site.internal_wording(text), (family, text))
                self.assertIn("withheld", build_site.lede(text), text)
                self.assertEqual(bg.public_description(text), "", text)
                self.assertTrue(build_site.release_withheld("organizations", "description_1line", text), text)
        for ordinary in ("Anti-slip step, walkway and ladder covers", "Settling tanks and ponds for water treatment", "Changed ownership in 2019 (acquired by a family firm)", "Maker of stair treads and staircases"):
            self.assertFalse(build_site.internal_wording(ordinary), ordinary)

    def test_internal_wording_filter_is_the_blind_audit_scan(self):
        root = Path(build_site.__file__).resolve().parent.parent
        src = (root / "tasks" / "blind-audit-11-2026-11-17" / "sample.py").read_text(encoding="utf-8")
        pattern = re.search(r"^LEAK = re\.compile\((r'.*'), re\.I\)$", src, re.M).group(1)
        self.assertEqual(eval(pattern), build_site.INTERNAL_RE.pattern)                   # reused, not a second scan

    def test_raw_data_markers_are_not_shown_as_words(self):
        page = self.read("orgs/ORG-000004.html")
        self.assertNotIn("none_found", page)
        self.assertIn("No website found", page)
        five = self.read("orgs/ORG-000005.html")
        self.assertNotIn("other specified in notes", five)
        self.assertIn("other (specified in the record&#x27;s notes, which are not published)", five.replace("&#39;", "&#x27;"))
        self.assertNotIn("other specified in notes", self.read("directory.json"))

    def test_stacked_phone_headers_keep_their_names_and_their_sort_buttons_take_no_focus(self):
        css = self.read("style.css")
        self.assertNotIn("table.stack thead button.sort{display:none}", css)           # hiding the button hid the column name from screen readers
        self.assertRegex(self.read("sortable.js"), r"tabIndex = phone\.matches && table\.classList\.contains\('stack'\) \? -1 : 0")   # it just takes no focus

    def test_skyline_loads_nothing_heavy_on_a_phone(self):
        html = self.read("skyline.html")
        self.assertIn('data-libs="vendor/three.min.js" data-boot="skyline.js"', html)
        self.assertNotRegex(html, r'<script[^>]*src="(?:vendor/three\.min\.js|skyline\.js)"')   # only explorer.js, and only from 720 px up
        self.assertIn('class="viz-summary"', html)
        self.assertIn("hero-sky{display:none!important}", self.read("style.css"))

    def test_layout_shift_and_long_task_fixes_are_in_place(self):
        css = self.read("style.css")
        self.assertIn("#browse{min-height:100vh}", css)
        self.assertIn("#chips{min-height:5.6rem}", css)
        self.assertIn('rel="preload" href="fonts/lato-400-latin.woff2"', self.read("index.html"))
        self.assertIn("new IntersectionObserver", self.read("sortable.js"))               # pages with dozens of tables enhance them as they near the screen

    def test_howto_preview_names_every_page_that_fetches_data(self):
        doc = (Path(build_site.__file__).resolve().parent.parent / "docs" / "SITE_HOWTO.md").read_text(encoding="utf-8")
        for page in ("`directory.html`", "`experts.html`", "`skyline.html`", "`search.html`", "`map.html`"):
            self.assertIn(page, doc.split("## Preview locally")[1].split("## What is deliberately not published")[0])

    def test_skyline_page_has_a_labelled_pause_button(self):
        html = self.read("skyline.html")
        self.assertRegex(html, r'<button class="btn" type="button" id="sky-play">Pause rotation</button>')
        css = self.read("style.css")
        self.assertIn(".viz-summary .btn.primary{background:var(--accent);color:var(--accent-fg)}", css)   # the skyline's phone summary sits outside .viz: white-on-paper buttons failed axe

    def test_404_base_comes_from_the_one_site_url_constant_and_howto_says_where_it_works(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(build_site, "SITE_URL", "https://example.org/atlas/"):
                build_site.build_site(Path(self.tmp.name) / "f.db", Path(tmp) / "site", None, repo_url="https://example.com/repo",
                                      git={"sha": "abc1234", "date": "2026-11-01", "dirty": False}, today="2026-11-01")
            page = (Path(tmp) / "site" / "404.html").read_text(encoding="utf-8")
        refs = re.findall(r'(?:href|src)="(/[^"]*)"', page)
        self.assertTrue(refs)
        self.assertTrue(all(r.startswith("/atlas/") for r in refs), [r for r in refs if not r.startswith("/atlas/")])   # moved with SITE_URL, nothing hardcoded
        self.assertNotIn("/polymer-atlas/", page.replace("https://example.org/atlas/", ""))
        doc = (Path(build_site.__file__).resolve().parent.parent / "docs" / "SITE_HOWTO.md").read_text(encoding="utf-8")
        self.assertIn("`404.html` takes its base from `SITE_URL`", doc)

    def test_howto_publishing_recipes_build_the_graph_pages_and_no_claim_is_left_that_the_audit_refuted(self):
        doc = (Path(build_site.__file__).resolve().parent.parent / "docs" / "SITE_HOWTO.md").read_text(encoding="utf-8")
        self.assertNotRegex(doc, r"python3 scripts/build_site\.py\ncd build/site")
        self.assertIn("python3 scripts/build_pages.py          # the whole site", doc)
        self.assertIn("netlify deploy --dir build/pages", doc)
        for gone in ("so a phone transfers only the small page", "The only page that loads three.js;", "all links are relative, so a project sub-path works.",
                     "keeping the query string and hash (`prospects.js`, with a refresh tag for no-JavaScript)", "the script only reads"):
            self.assertNotIn(gone, doc)


if __name__ == "__main__":
    unittest.main()
