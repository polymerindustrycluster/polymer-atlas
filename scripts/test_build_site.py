#!/usr/bin/env python3
"""Tests for scripts/build_site.py, run against a tiny fixture database.

    python3 -m unittest scripts/test_build_site.py
"""
import json
import re
import sqlite3
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
             "naics_primary", "naics_primary_source_type", "naics_confidence", "processes", "materials",
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
            self.assertEqual(len(p), 5)            # name, role, specialties, institution id, profile URL
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


if __name__ == "__main__":
    unittest.main()
