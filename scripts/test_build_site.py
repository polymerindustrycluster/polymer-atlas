#!/usr/bin/env python3
"""Tests for scripts/build_site.py, run against a tiny fixture database.

    python3 -m unittest scripts/test_build_site.py
"""
import csv
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
    ins("sites", SITE_COLS, site_id="SITE-000001", org_id="ORG-000001", site_name="Evil Plastics - Akron plant",
        site_type="manufacturing_plant", city="Akron", state="OH", zip="44301", county="Summit",
        ring_primary="1", naics_primary="326199", processes="injection_molding", operating_status="active",
        sources="Company site https://example.com/plant", verification_tier="A", last_verified="2026-10-30",
        street_address="1 Main St", latitude="41.08", longitude="-81.51", geocode_precision="address_interpolated",
        country="US", notes="secret note 330-555-0199")
    ins("sites", SITE_COLS, site_id="SITE-000002", org_id="ORG-000001", site_name="Evil Plastics - Annex",
        city="Akron", state="OH", county="Summit", ring_primary=None, operating_status="active",
        verification_tier="U", last_verified="2026-10-30", latitude="41.09", longitude="-81.52", country="US")
    ins("sites", SITE_COLS, site_id="SITE-000003", org_id="ORG-000003", site_name="Keystone - Erie",
        city="Erie", state="PA", county="Erie", ring_primary="2", operating_status="active",
        verification_tier="B", last_verified="2026-10-02", country="US")
    ins("sites", SITE_COLS, site_id="SITE-000004", org_id="ORG-000002", site_name="Old Rubber - Cleveland",
        city="Cleveland", state="OH", county="Cuyahoga", ring_primary="1", operating_status="closed",
        verification_tier="C", last_verified="2026-10-01", latitude="41.5", longitude="-81.7", country="US")
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
                self.assertIn("1 equipment rows", html)
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
        self.assertEqual(self.result["org_pages"], 3)
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
        self.assertEqual(len(data["rows"]), 4)  # 3 organizations + 1 ecosystem row

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
        # fixture: active tier A-C sites are SITE-000001 (A) and SITE-000003 (B)
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
        self.assertIn("https://example.com/about", org)
        self.assertIn("1 internal workflow reference omitted", org)

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

    def test_external_requests_only_on_map_page(self):
        map_html = self.read("map.html")
        self.assertIn("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js", map_html)
        self.assertIn("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css", map_html)
        self.assertIn("OpenStreetMap", self.read("map.js"))
        self.assertIn("reference data", map_html)
        pat = re.compile(r'<(?:script|link|img)\b[^>]*(?:src|href)="https?://')
        for p in self.out.rglob("*.html"):
            if p.name != "map.html":
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


def make_prospect_db(path):
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
        country="US")
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
        ("EVD-3", "organizations", "ORG-000001", "activity", "Freeze-minted org-grain row (pass 24), from the packet design",
         "directory", "https://example.org/directory", "2026-10-28", "supports_B", "lane_Z99", ""),
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


class ProspectsFixtureTest(unittest.TestCase):
    """The prospects page, its CSV, the county A-C column and the evidence section, against a fixture whose answers are known."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        make_prospect_db(tmp / "f.db")
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

    def test_one_row_per_organization_and_sites_sum_to_the_headline_set(self):
        rows = build_site.prospect_rows(self.atlas)
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {"ORG-000001", "ORG-000004", "ORG-000005", "ORG-000006", "ORG-000501"})  # eco-owned site counts
        self.assertEqual(sum(r["n_sites"] for r in rows), len(build_site.pic18_active_sites(self.atlas.sites)))
        self.assertEqual(sum(r["n_sites"] for r in rows), 5)     # not the closed, tier U or Pennsylvania-Erie site rows
        self.assertEqual(self.read("prospects.html").count("<tr data-co="), 5)

    def test_employee_band_basis_is_site_then_org_then_unknown(self):
        by = {r["id"]: r["band"] for r in build_site.prospect_rows(self.atlas)}
        self.assertEqual(by["ORG-000004"], (["50-99"], "site"))          # the site band wins over the org's 100-249
        self.assertEqual(by["ORG-000005"], (["100-249"], "org record"))
        self.assertEqual(by["ORG-000006"], ([], ""))                     # literal "unknown" is unknown
        html = self.read("prospects.html")
        self.assertIn("50-99 <span class=\"muted small\">(site)</span>", html)
        self.assertIn("100-249 <span class=\"muted small\">(org record)</span>", html)

    def test_filter_counts_and_unknown_counts(self):
        html = self.read("prospects.html")
        self.assertEqual(self.option_count(html, "band", "min50"), 2)    # 50-99 and 100-249
        self.assertEqual(self.option_count(html, "band", "min100"), 1)   # only 100-249
        self.assertEqual(self.option_count(html, "band", "_"), 3)        # ORG-000001, ORG-000006 and the ecosystem org: 5 rows - 2 with a band
        self.assertEqual(self.option_count(html, "co", "Summit"), 2)
        self.assertEqual(self.option_count(html, "proc", "injection_molding"), 2)   # site-level
        self.assertEqual(self.option_count(html, "proc", "foam_fabrication"), 1)    # org-level fallback
        self.assertEqual(self.option_count(html, "proc", "_"), 2)
        self.assertEqual(self.option_count(html, "mem", "yes"), 1)
        self.assertEqual(self.option_count(html, "mem", "no"), 4)
        for facet in ("co", "ring", "band", "proc", "mat", "mkt", "own"):
            self.assertIn(f'name="{facet}" value="_"', html)             # every filter lists its unknown count
        self.assertIn("Unknown means nothing is recorded", html)

    def test_public_member_list_wording(self):
        html = self.read("prospects.html")
        self.assertIn("<td>on the public member list</td>", html)
        self.assertIn("<td>not on the public member list</td>", html)
        self.assertIn("on the public member list", self.read("orgs/ORG-000001.html"))
        self.assertIn("not on the public member list", self.read("orgs/ORG-000003.html"))
        for p in self.out.rglob("*.html"):
            self.assertNotRegex(p.read_text(encoding="utf-8"), r"[Nn]on-member|PIC member \(", p.name)

    def test_prospects_csv(self):
        rows = list(csv.DictReader(io.StringIO(self.read("prospects.csv").lstrip("﻿"))))
        self.assertEqual(len(rows), 5)
        by = {r["org_id"]: r for r in rows}
        self.assertEqual(by["ORG-000006"]["employee_band"], "unknown")
        self.assertEqual(by["ORG-000005"]["employee_band_basis"], "org record")
        self.assertEqual(by["ORG-000001"]["public_member_list"], "on the public member list")
        self.assertEqual(by["ORG-000004"]["public_member_list"], "not on the public member list")
        self.assertTrue(by["ORG-000004"]["atlas_page"].endswith("/orgs/ORG-000004.html"))
        injected = build_site.prospects_csv([{**build_site.prospect_rows(self.atlas)[0], "name": "=HYPERLINK(1)"}], "x/")
        self.assertIn("'=HYPERLINK(1)", injected)                         # a formula is never written as a formula

    def test_every_page_links_the_release_and_the_csv(self):
        for p in self.out.rglob("*.html"):
            text = p.read_text(encoding="utf-8")
            self.assertIn("https://example.com/repo/releases/latest", text, p.name)
            self.assertIn("prospects.csv", text, p.name)

    def test_csv_download_is_in_the_shared_table_script(self):
        js = self.read("sortable.js")
        self.assertIn("Download these rows (CSV)", js)
        self.assertIn("r.hidden", js)                                      # exports the rows shown, not the hidden ones
        self.assertIn("data-nofilter", js)
        self.assertIn('id="ptable" data-nofilter', self.read("prospects.html"))

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

    def test_org_page_shows_evidence_rows_not_batch_labels(self):
        org = self.read("orgs/ORG-000001.html")
        self.assertIn('id="evidence">Evidence (3 rows for this organization)', org)   # EVD-4 cites staging: row withheld
        self.assertIn("1 evidence row citing internal workflow material omitted", org)
        for col in ("Claim", "Source class", "Strength", "Observed", "Source"):
            self.assertIn(f'<th scope="col">{col}</th>', org)
        self.assertIn("Evil Plastics exists and operates", org)
        self.assertIn("Company&#x27;s own site", org)
        self.assertIn("Supports tier A (primary source)", org)
        self.assertIn('<a href="https://example.com/about" rel="noopener nofollow">https://example.com/about</a> (own site, accessed 2026-10-30)', org)
        self.assertIn("Akron plant exists", org)                           # the site's evidence sits in its own row
        for hidden in ("sales.rep@example.com", "330-555-0142", "pass 24", "packet design", "lane_Z99", "PRIVATE-NOTE-XYZ",
                       "staging", "Atlas verification wave"):
            self.assertNotIn(hidden, org)
        self.assertEqual(org.count("(detail not shown in this view; see the source)"), 2)   # EVD-2 (email), EVD-3 (workflow words)
        self.assertIn("Roster list (a lead, not proof)", self.read("orgs/ORG-000004.html"))
        self.assertIn("No claim-level evidence rows are recorded", self.read("orgs/ORG-000003.html"))   # falls back to source text

    def test_prospect_evidence_count_matches_the_page(self):
        by = {r["id"]: r["evidence"] for r in build_site.prospect_rows(self.atlas)}
        self.assertEqual(by["ORG-000001"], 3 + 1)                           # three shown org rows + one site row
        self.assertEqual(by["ORG-000004"], 1)

    def test_street_map_and_graph_default_to_pic18(self):
        sites = json.loads(self.read("sites.json"))
        self.assertEqual(sites["cols"][6], "st")
        self.assertEqual(sites["cols"][-1], "co")
        self.assertRegex(self.read("map.html"), r'id="f-pic18" checked data-counties="Ashland,Ashtabula,')
        self.assertIn("picOnly", self.read("map.js"))


class RealDataHeadlineTest(unittest.TestCase):
    """The PIC-18 numbers on the built pages, recomputed from the canonical CSVs in data/ with the csv module alone
    (no builder helper, no SQLite): the headline, the county index total, the prospects rows and two filter counts."""

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

        def tokens(v):
            return {t.strip() for t in (v or "").split(";") if t.strip() and t.strip() != "unknown"}
        cls.summit_orgs = {o for o, ss in by.items() if any(s["county"] == "Summit" for s in ss)}
        cls.members = {o for o in by if orgs[o].get("pic_member") == "true"}
        cls.injection = set()
        for o, ss in by.items():
            t = set().union(*(tokens(s["processes"]) for s in ss)) or tokens(orgs[o].get("processes"))   # site first, else org
            if "injection_molding" in t:
                cls.injection.add(o)
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
        pro = build_site.build_prospects_page(self.ctx, build_site.prospect_rows(self.atlas))
        self.assertEqual(self.number(r"([\d,]+) such site rows", pro), expected)

    def test_prospect_rows_are_the_organizations_of_those_sites(self):
        rows = build_site.prospect_rows(self.atlas)
        self.assertEqual({r["id"] for r in rows}, set(self.by_org))
        self.assertEqual(len(rows), len(self.by_org))
        pro = build_site.build_prospects_page(self.ctx, rows)
        self.assertEqual(pro.count("<tr data-co="), len(self.by_org))
        self.assertEqual(self.number(r"<p class=\"lede\">([\d,]+) organization rows", pro), len(self.by_org))

    def test_filter_counts_match_the_csvs(self):
        pro = build_site.build_prospects_page(self.ctx, build_site.prospect_rows(self.atlas))

        def option(facet, value):
            return self.number(rf'name="{facet}" value="{value}"> <span class="t">[^<]*</span> <span class="n">(\d+)</span>', pro)
        self.assertEqual(option("co", "Summit"), len(self.summit_orgs))
        self.assertEqual(option("mem", "yes"), len(self.members))
        self.assertEqual(option("proc", "injection_molding"), len(self.injection))
        self.assertGreater(len(self.injection), 20)
        self.assertGreater(len(self.members), 10)

    def test_pages_stay_small(self):
        rows = build_site.prospect_rows(self.atlas)
        self.assertLess(len(build_site.build_prospects_page(self.ctx, rows).encode()), 2_000_000)
        self.assertLess(len(build_site.prospects_csv(rows, build_site.SITE_URL).encode()), 2_000_000)

    def test_evidence_shown_on_every_page_has_no_contacts_or_pipeline_words(self):
        shown = 0
        for table, recs in (("organizations", self.atlas.orgs), ("ecosystem", self.atlas.eco)):
            for rec in recs.values():
                # evidence tables only: a record without evidence rows falls back to its source text, as before this change
                parts = [build_site.evidence_section(self.atlas, table, rec, "organization")] \
                    if build_site.evidence_view(self.atlas, table, rec["org_id"])[0] else []
                parts += [build_site.site_evidence(self.atlas, s) for s in self.atlas.sites_by_org.get(rec["org_id"], [])
                          if build_site.evidence_view(self.atlas, "sites", s["site_id"])[0]]
                text = re.sub(r"https?://\S+", " ", re.sub(r"<[^>]+>", " ", " ".join(parts)))   # words inside a cited URL are the source's
                shown += "Evidence (" in text
                # independent of the builder's own filter; words that no legitimate source citation would contain
                pipeline = re.compile(r"\bpass[- ]\d+|packet (design|org)|verdict|minted|\bfreeze(?![a-z])|\bstaging\b|\bleg[ _]?\d|lane[ _][A-Z]?\d|"
                                      r"wave[- ]\d|integration (pass|journal)|see \w+_ref\b", re.I)
                for rx, what in ((build_site.PRIVATE_RE, "email or phone"), (pipeline, "pipeline word"),
                                 (re.compile(r"\bCRM\b"), "CRM")):
                    m = rx.search(text)
                    self.assertIsNone(m, f"{what} {m.group(0) if m else ''!r} on {rec['org_id']}")
        self.assertGreater(shown, 1000)                                    # evidence really rendered, not silently skipped


if __name__ == "__main__":
    unittest.main()
