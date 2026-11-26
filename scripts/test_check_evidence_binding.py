"""Tests for scripts/check_evidence_binding.py.

Every case is a synthetic string shaped like a real evidence row (controller instruction 2026-11-22: no source quote
text outside data/); the comment on each case names the real row it models. Planted defects must FAIL; structured true matches
must PASS; a web quote without a replayed proof is READ_REQUIRED at best; what cannot be inspected is UNINSPECTABLE. Each Codex
finding on PR #467 has its counterexample here (the README maps finding -> test).
"""
import contextlib
import csv
import gzip
import hashlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_evidence_binding as b

ROOT = Path(__file__).resolve().parents[1]

ORGS = [
    {"org_id": "ORG-1", "legal_name": "Harbor Plastics, Inc.", "trade_names": "Lakeside Plastics", "hq_city": "Cleveland",
     "hq_state": "OH"},
    {"org_id": "ORG-2", "legal_name": "Northfield Chemical Inc.", "trade_names": "", "hq_city": "Midland", "hq_state": "MI",
     "website": "(own-site contact page)"},  # notes in the website field are not a domain
    {"org_id": "ORG-3", "legal_name": "Riverbend Medical, Inc.", "trade_names": "", "hq_city": "San Clemente",
     "hq_state": "CA"},
    {"org_id": "ORG-4", "legal_name": "Containment Systems, Inc.", "trade_names": "", "hq_city": "Conroe", "hq_state": "TX"},
    {"org_id": "ORG-5", "legal_name": "Gulfstar Enterprises LLC", "trade_names": "", "hq_city": "Houston", "hq_state": "TX"},
    {"org_id": "ORG-6", "legal_name": "Crest Chemical LP", "trade_names": "", "hq_city": "Houston", "hq_state": "TX"},
    {"org_id": "ORG-7", "legal_name": "Tamarack Rubber Company", "trade_names": "", "hq_city": "Akron", "hq_state": "OH",
     "website": "https://www.tamarackrubber.example/about"},
    {"org_id": "ORG-8", "legal_name": "Kestrel Molding LLC", "trade_names": "", "hq_city": "Troy", "hq_state": "AL",
     "website": "https://kestrelmolding.wixsite.com/home"},  # a site on a shared platform host
    {"org_id": "ORG-9", "legal_name": "Alder Composites Corporation", "trade_names": "", "hq_city": "Chula Vista",
     "hq_state": "CA"},
    {"org_id": "ORG-10", "legal_name": "Pinecrest Industries", "trade_names": "", "hq_city": "Dallas", "hq_state": "TX"},
    {"org_id": "ORG-11", "legal_name": "Pinecrest Foam LLC", "trade_names": "", "parent_org_id": "ORG-10",
     "hq_city": "Dallas", "hq_state": "TX"},
    {"org_id": "ORG-12", "legal_name": "Armacor LLC", "trade_names": "", "hq_city": "Mebane", "hq_state": "NC"},
    {"org_id": "ORG-13", "legal_name": "B R T of West Virginia", "trade_names": "", "hq_city": "Mount Hope",
     "hq_state": "WV"},
    {"org_id": "ORG-14", "legal_name": "Meridian Coatings Co.", "trade_names": "", "hq_city": "Longview", "hq_state": "TX",
     "notes": "Dated operator change: RY2024 operator Eastgate Polymers US Inc; Meridian completion July 2026."},
    {"org_id": "ORG-15", "legal_name": "Acme Polymer", "trade_names": "", "hq_city": "Center", "hq_state": "OH",
     "website": "https://acmepolymer.example/", "ultimate_parent_name": "Acme Polymer Holdings"},
    {"org_id": "ORG-16", "legal_name": "Acme Molding", "trade_names": "", "hq_city": "Dover", "hq_state": "OH",
     "website": "https://acme.pages.dev/"},
    {"org_id": "ORG-17", "legal_name": "Acme Resin LLC", "trade_names": "", "hq_city": "Dover", "hq_state": "OH",
     "ultimate_parent_name": "Acme Resin Inc"},  # Codex r3 finding 5: the parent's key equals the subsidiary's
    {"org_id": "ORG-18", "legal_name": "Zephyr Plastics Inc", "trade_names": "", "hq_city": "Dover", "hq_state": "OH",
     "ultimate_parent_name": "Zephyr Plastics Inc"},  # a self-reference is not a parent
]
SITES = [
    # two sibling sites of one operator, a few hundred metres apart (models SITE-000107 / SITE-000108)
    {"site_id": "S-CARN", "org_id": "ORG-1", "site_name": "Harbor Plastics — Cleveland", "city": "Cleveland", "state": "OH",
     "street_address": "4105 Marlowe Avenue"},
    {"site_id": "S-PROS", "org_id": "ORG-1", "site_name": "Lakeside Plastics — Cleveland", "city": "Cleveland", "state": "OH",
     "street_address": "4188 Quarry Ave E"},
    {"site_id": "S-VIC", "org_id": "ORG-2", "site_name": "Northfield — Victoria Site", "city": "Victoria", "state": "TX",
     "street_address": "3812 Old Mission Rd N"},
    {"site_id": "S-RR", "org_id": "ORG-3", "site_name": "Riverbend Medical - Round Rock Plant", "city": "Round Rock", "state": "TX",
     "street_address": "5155 N Garner Street"},
    {"site_id": "S-BAK", "org_id": "ORG-4", "site_name": "Containment Systems - Bakersfield", "city": "Bakersfield", "state": "CA",
     "street_address": "3300 Orion Dr"},
    {"site_id": "S-PAS", "org_id": "ORG-7", "site_name": "Tamarack - Pasadena Plant", "city": "Pasadena", "state": "TX",
     "street_address": "15520 Shoreline Blvd"},
    {"site_id": "S-AVON", "org_id": "ORG-7", "site_name": "Tamarack - Sheffield Lake", "city": "Sheffield Lake", "state": "OH",
     "street_address": "736 Hollis Rd"},
    {"site_id": "S-PLAQ", "org_id": "ORG-7", "site_name": "Tamarack - Plaquemine Plant", "city": "Plaquemine", "state": "LA",
     "street_address": "31840 HWY 617"},
    {"site_id": "S-EJ", "org_id": "ORG-7", "site_name": "Tamarack - East Jordan", "city": "East Jordan", "state": "MI",
     "street_address": "7150 M-88 Highway"},
    {"site_id": "S-BLANK", "org_id": "ORG-7", "site_name": "Tamarack - Wickliffe", "city": "Wickliffe", "state": "OH",
     "street_address": ""},
    {"site_id": "S-STE100", "org_id": "ORG-7", "site_name": "Tamarack - Columbus", "city": "Columbus", "state": "OH",
     "street_address": "377 Commerce Blvd, Suite 100"},
    {"site_id": "S-STE140", "org_id": "ORG-7", "site_name": "Tamarack - Raleigh", "city": "Raleigh", "state": "NC",
     "street_address": "4870 Birch Hollow Circle Suite 140"},
    {"site_id": "S-STE200", "org_id": "ORG-7", "site_name": "Tamarack - Goodyear", "city": "Goodyear", "state": "AZ",
     "street_address": "6120 S. Juniper Ln, Suite 200"},
    {"site_id": "S-BLDG", "org_id": "ORG-7", "site_name": "Tamarack - West Fenwick", "city": "West Fenwick", "state": "OH",
     "street_address": "518 Fenwick Grove Rd Building # 1"},
    {"site_id": "S-ONE", "org_id": "ORG-7", "site_name": "Tamarack - Neenah", "city": "Neenah", "state": "WI",
     "street_address": "One Heron Drive"},
    {"site_id": "S-198A", "org_id": "ORG-7", "site_name": "Tamarack - New Bern", "city": "New Bern", "state": "NC",
     "street_address": "212B Larkin Blvd"},
    {"site_id": "S-GRID", "org_id": "ORG-7", "site_name": "Tamarack - Oconomowoc", "city": "Oconomowoc", "state": "WI",
     "street_address": "N52 W24411 Cedar Plank Rd"},
    {"site_id": "S-PARK", "org_id": "ORG-7", "site_name": "Tamarack - Neodesha", "city": "Neodesha", "state": "KS",
     "street_address": "Willow Bend Industrial Park"},
    {"site_id": "S-AND", "org_id": "ORG-7", "site_name": "Tamarack - Berwick", "city": "Berwick", "state": "PA",
     "street_address": "7th & Ashcroft Lane"},
    {"site_id": "S-RANGE", "org_id": "ORG-7", "site_name": "Tamarack - Erie", "city": "Erie", "state": "PA",
     "street_address": "2201-2205 Elm St"},
    {"site_id": "S-ORD", "org_id": "ORG-7", "site_name": "Tamarack - Wadsworth", "city": "Wadsworth", "state": "OH",
     "street_address": "4417 First Street"},
    {"site_id": "S-AOC", "org_id": "ORG-8", "site_name": "Kestrel - Valparaiso", "city": "Valparaiso", "state": "IN",
     "street_address": "1180 Dorsey Ave"},
    {"site_id": "S-CT", "org_id": "ORG-8", "site_name": "Kestrel - East Haven plant", "city": "East Haven", "state": "CT",
     "street_address": "77 Marsh Street Ext"},
    {"site_id": "S-ARM", "org_id": "ORG-12", "site_name": "Armacor - Conover", "city": "Conover", "state": "NC",
     "street_address": "2380 Holland Rd"},
    {"site_id": "S-PIN", "org_id": "ORG-11", "site_name": "Pinecrest Foam - Lancaster", "city": "Lancaster", "state": "PA",
     "street_address": "4471 Tanner Dr"},
    {"site_id": "S-MER", "org_id": "ORG-14", "site_name": "Meridian - Longview", "city": "Longview", "state": "TX",
     "street_address": "2650 Prairie Blvd"},
    {"site_id": "S-CUE", "org_id": "ORG-13", "site_name": "BRT - Mount Hope", "city": "Mount Hope", "state": "WV",
     "street_address": "940 Aspen Hill Road"},
    {"site_id": "S-LET", "org_id": "ORG-7", "site_name": "Tamarack - Dunmore", "city": "Dunmore", "state": "PA",
     "street_address": "2210 C Larkspur Rd."},
    {"site_id": "S-NC", "org_id": "ORG-7", "site_name": "Tamarack - Fayetteville", "city": "Fayetteville", "state": "NC",
     "street_address": "5530 Bragg Ridge St"},
    # Codex counterexamples (review of PR #467)
    {"site_id": "S-1604", "org_id": "ORG-7", "site_name": "Tamarack - Dalton", "city": "Dalton", "state": "GA",
     "street_address": "2718 Building"},  # models EVD-431716 / SITE-002988: a building number, no street
    {"site_id": "S-BLDGA", "org_id": "ORG-7", "site_name": "Tamarack - Kent", "city": "Kent", "state": "OH",
     "street_address": "10 Industrial Pkwy Building A Suite 100"},
    {"site_id": "S-POBOX", "org_id": "ORG-7", "site_name": "Tamarack - Lima", "city": "Lima", "state": "OH",
     "street_address": "Post Office Box 12"},
    {"site_id": "S-OHIO", "org_id": "ORG-7", "site_name": "Tamarack - Marion", "city": "Marion", "state": "OH",
     "street_address": "88 Quarry Bend Rd"},
    {"site_id": "S-OAK1", "org_id": "ORG-15", "site_name": "Acme Polymer - Oak St", "city": "Dover", "state": "OH",
     "street_address": "321 Oak Street, Suite 100"},
    {"site_id": "S-OAK2", "org_id": "ORG-15", "site_name": "Acme Polymer - Oak Ave", "city": "Dover", "state": "OH",
     "street_address": "321 Oak Avenue, Suite 300"},
    {"site_id": "S-OAK3", "org_id": "ORG-15", "site_name": "Acme Polymer - Oak", "city": "Dover", "state": "OH",
     "street_address": "321 Oak Street"},
    {"site_id": "S-OAK4", "org_id": "ORG-15", "site_name": "Acme Polymer - Oak Bldg", "city": "Dover", "state": "OH",
     "street_address": "321 Oak Street, Building A"},
    {"site_id": "S-BASE", "org_id": "ORG-15", "site_name": "Acme Polymer - Basement", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "30 Larch Way, Basement Level"},
    {"site_id": "S-LVL", "org_id": "ORG-15", "site_name": "Acme Polymer - Level", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "40 Larch Way, Level 2"},
    {"site_id": "S-PLANT2", "org_id": "ORG-15", "site_name": "Acme Polymer - Plant 2", "city": "Dover", "state": "OH",
     "street_address": "77 Kiln Rd"},
    {"site_id": "S-PHOLD", "org_id": "ORG-15", "site_name": "Acme Polymer Holdings - Elm Works", "city": "Dover",
     "state": "OH", "county": "Tuscarawas", "street_address": "9 Elm Rd"},  # a site named for its parent
    {"site_id": "S-PAREN", "org_id": "ORG-15", "site_name": "Acme Polymer - Hub", "city": "Cleveland (Solon)",
     "state": "OH", "zip": "44139", "street_address": "5 Hub Rd"},  # a second locality in parentheses
    # Codex r3 counterexamples (synthetic)
    {"site_id": "S-TWA", "org_id": "ORG-15", "site_name": "Acme Polymer - Larch Dover", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "640 Larch Way"},  # finding 2: one street, two plants, one ZIP
    {"site_id": "S-TWB", "org_id": "ORG-15", "site_name": "Acme Polymer - Larch Dayton", "city": "Dayton", "state": "OH",
     "zip": "44699", "street_address": "640 Larch Way"},
    {"site_id": "S-B1A", "org_id": "ORG-15", "site_name": "Acme Polymer - 1-A", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "15 Larch Way, Bldg. 1-A"},  # finding 3
    {"site_id": "S-BN", "org_id": "ORG-15", "site_name": "Acme Polymer - North", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "16 Larch Way, Building North"},
    {"site_id": "S-UA", "org_id": "ORG-15", "site_name": "Acme Polymer - Unit A", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "17 Larch Way, Unit A, Room 1"},
    {"site_id": "S-SOLON", "org_id": "ORG-15", "site_name": "Acme Polymer - Solon", "city": "Cleveland (Solon)",
     "state": "OH", "zip": "44139", "street_address": "8 Aurora Rd"},  # finding 4
    {"site_id": "S-KDIV", "org_id": "ORG-15", "site_name": "Acme Polymer - Kestrel Division", "city": "Dover",
     "state": "OH", "zip": "44699", "street_address": "12 Birch Ln"},
    {"site_id": "S-ARES", "org_id": "ORG-17", "site_name": "Acme Resin - Dover", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "20 Birch Ln"},  # finding 5
    {"site_id": "S-ZEP", "org_id": "ORG-18", "site_name": "Zephyr Plastics - Dover", "city": "Dover", "state": "OH",
     "zip": "44699", "street_address": "22 Birch Ln"},
    {"site_id": "S-ZIP", "org_id": "ORG-15", "site_name": "Acme Polymer - Zip", "city": "Dover", "state": "OH",
     "street_address": "43000 Oak Street"},
    {"site_id": "S-PAGES", "org_id": "ORG-16", "site_name": "Acme Molding - Plant", "city": "Dover", "state": "OH",
     "street_address": "12 Kiln Rd"},
]

OSHA = "OSHA inspection bulk (DOL data catalog), activity_nr 300000001"
ITA = "OSHA ITA Form 300A bulk (osha.gov/itadata), establishment_id 500001"
RCRA = "EPA ECHO RCRAInfo bulk (echo.epa.gov program files), handler XXR000000001 (FRS 110000000001)"
NPDES = "EPA ECHO ICIS-NPDES bulk (echo.epa.gov program files), facility 3600000001 (FRS 110000000002)"
TCEQ = "TCEQ Central Registry (Coastal & East Texas, data.texas.gov tzyg-j7q4), RN=RN100000001"
OHEPA = "Ohio EPA NPDES GIS layer 2 (NPDES industrial stormwater), core_place_id=500001"
NCDEQ = "NC DEQ ArcGIS (services2.arcgis.com/x) AQ_Permited_Facilities, OBJECTID=1"
FMCSA = "FMCSA Company Census bulk file (vintage 2026-11-20), USDOT 1000001"
STATE = "state-entity-files-bulk, CT/ct_business_master.csv, entity_id 0000001"
USASP = "USAspending bulk contract archives FY2015-2026 (2026-11-06 generation), recipient key AAAAAAAAAAA1"
SBIR = "SBIR/STTR bulk award file (data.www.sbir.gov), firm key ALDER COMPOSITES CORPORATION|CHULA VISTA|CA|"
ECHO_TAIL = "; FRS registry 110000000001; RCRAInfo handler XXR000000001; NAICS 326199; status: generator=1"


def permit(permittee, facility, addr, county="HARRIS"):
    return (f"permittee: {permittee}; facility: {facility}; address: {addr}; county: {county}; "
            f"permit_number(s): 90001; program(s): QQX; status(es): SYNTHETIC; source_record_key: RN=RN1")


def ev(rid, source, quote, claim="existence", table="sites", eid="EVD-T", cls="registry"):
    detail = f"synthetic claim t1; quote: {quote}" if quote is not None else "existence (own site)"
    return {"evidence_id": eid, "record_table": table, "record_id": rid, "claim_type": claim, "claim_detail": detail,
            "source_ref": source, "source_class": cls, "created_by": "test", "_at": "data/evidence_test.csv:2"}


class Verdicts(unittest.TestCase):
    parallel_safe = True

    @classmethod
    def setUpClass(cls):
        cls.idx = b.Index(SITES, ORGS)

    def check(self, row, verdict, reason=""):
        v, why, info = b.judge(row, self.idx)
        self.assertEqual((v, why), (verdict, reason), info)
        return info

    # ---- planted defects: every one must FAIL (spotcheck w1122 and the 463 review)

    def test_sibling_street_on_wrong_site_existence(self):  # EVD-427647: Carnegie quote on the Prospect site
        self.check(ev("S-PROS", OSHA, "HARBOR PLASTICS, 4105 MARLOWE AVE., CLEVELAND, OH 44199"), "FAIL",
                   "street_differs")

    def test_sibling_street_on_wrong_site_address(self):  # EVD-427648
        self.check(ev("S-PROS", OSHA, "HARBOR PLASTICS, 4105 MARLOWE AVE., CLEVELAND, OH 44199", "address"), "FAIL",
                   "street_differs")

    def test_sibling_quote_true_on_its_own_site(self):  # EVD-427645: the same quote binds to the Carnegie site
        self.check(ev("S-CARN", OSHA, "HARBOR PLASTICS, 4105 MARLOWE AVE., CLEVELAND, OH 44199"), "PASS")

    def test_swapped_quote_between_siblings_fails(self):  # planted: a correct Prospect quote moved to Carnegie
        q = "Lakeside Plastics, 4188 Quarry Avenue East, Cleveland, OH 44199"
        self.check(ev("S-PROS", ITA, q), "PASS")
        self.check(ev("S-CARN", ITA, q), "FAIL", "street_differs")

    def test_former_operator_permit(self):  # EVD-457493: former operator's permit at the held street
        self.check(ev("S-VIC", TCEQ, permit("Eastgate Polymers, Inc.", "EASTGATE VICTORIA PLANT",
                                            "3812 OLD MISSION RD N, VICTORIA, TX 77909", "VICTORIA")),
                   "FAIL", "name_not_held")

    def test_held_name_plus_other_entity_words(self):  # EVD-455899: a fleet-services affiliate is another operator
        info = self.check(ev("S-RR", TCEQ, permit("Riverbend Medical Fleet Services, LLC", "HARBORVIEW RIVERBEND MEDICAL",
                                                  "5155 N GARNER ST, ROUND ROCK, TX 78699", "WILLIAMSON")),
                          "FAIL", "name_not_held")
        self.assertIn("leading_run", info["name_alt"])

    def test_other_company_at_exact_street(self):  # EVD-449620, EVD-450128: shared FRS key, different name
        self.check(ev("S-BAK", RCRA, "OWENSBY FIBERGLAS CORP; 3300 ORION DRIVE, BAKERSFIELD, CA 93399" + ECHO_TAIL),
                   "FAIL", "name_not_held")

    def test_unheld_facility_label(self):  # EVD-457589: neither permittee nor facility label is held
        self.check(ev("S-BAK", TCEQ, permit("Belmar Manufacturing Company, Inc.", "BAKERSFIELD BELMAR",
                                            "3300 ORION DR, BAKERSFIELD, CA 93399")), "FAIL", "name_not_held")

    def test_hq_from_service_station_permit(self):  # EVD-457167 / EVD-457135: a store's permit is not an HQ
        for fac in ("CORNER AUTO SUPPLY 4417", "WESTCHASE SERVICE CENTER"):
            self.check(ev("ORG-5", TCEQ, permit("Gulfstar Enterprises LLC", fac, "9150 W KESSLER AVE, HOUSTON, TX 77099"),
                          "address", "organizations"), "FAIL", "hq_from_facility_or_permit")

    def test_hq_from_permit_named_for_company(self):  # EVD-457177: facility label names the company, still a permit
        self.check(ev("ORG-5", TCEQ, permit("Gulfstar Enterprises LLC", "GULFSTAR ENTERPRISE",
                                            "7740 HARWIN CT, HOUSTON, TX 77098"), "address", "organizations"),
                   "FAIL", "hq_from_facility_or_permit")

    def test_short_name_inside_another(self):  # first-cut token subset: a one-word brand inside another name
        for permittee in ("CREST", "BELLAIRE CREST"):
            self.check(ev("ORG-6", TCEQ, permit(permittee, "STORE 12", "16 RUSK ALY, HOUSTON, TX 77098"),
                          table="organizations"), "FAIL", "name_not_held")

    def test_permit_at_other_street(self):  # EVD-455507: an auto service centre permit filed on a plant
        self.check(ev("S-PAS", TCEQ, permit("Tamarack Rubber Company", "TAMARACK AUTO SERVICE CENTER",
                                            "622E WESTLAKE AVE, PASADENA, TX 77598"), "address"),
                   "FAIL", "street_differs")

    def test_neighbouring_number(self):  # EVD-432662: 552 vs 554 on one road
        self.check(ev("S-AVON", ITA, "Tamarack Rubber, 734 Hollis Road, Sheffield Lake, OH 44098"), "FAIL", "street_differs")

    def test_same_number_other_road(self):  # EVD-426678: the first cut passed number + generic word
        info = self.check(ev("S-PLAQ", OSHA, "TAMARACK RUBBER CO, 31840 STATE HWY 9 SOUTH, PLAQUEMINE, LA 70799"),
                          "FAIL", "street_differs")
        self.assertEqual(info["street_limit"], "same_number_other")

    def test_po_box_is_no_street(self):  # EVD-431900
        self.check(ev("S-EJ", ITA, "Tamarack Rubber Co, PO BOX 9183, East Jordan, MI 49799"), "FAIL", "quote_no_street")

    def test_city_only_permit_address(self):  # EVD-454757: Ohio EPA layer prints city + ZIP only
        self.check(ev("S-AVON", OHEPA, "permittee: Tamarack Rubber Co; address: Sheffield Lake, OH 44098; county: Lorain; "
                                       "permit_number(s): 3GR00000*BG"), "FAIL", "quote_no_street")

    def test_record_without_street(self):  # EVD-454759
        self.check(ev("S-BLANK", OHEPA, "permittee: Tamarack Rubber Co; address: 30770 Euclid Bend Blvd, Wickliffe, OH "
                                        "44099; county: Lake"), "FAIL", "record_no_street")

    def test_suite_conflict(self):  # 463 review: SITE-000514 (suite 100 vs 300), SITE-019015 (140 vs 120)
        self.check(ev("S-STE100", ITA, "Tamarack Rubber Co, 377 Commerce Blvd Suite 300, Columbus, OH 43299"),
                   "FAIL", "unit_differs")
        self.check(ev("S-STE140", OSHA, "TAMARACK RUBBER CO, 4870 BIRCH HOLLOW CIR STE 120, RALEIGH, NC 27699"),
                   "FAIL", "unit_differs")

    def test_hq_from_fmcsa_filed_address(self):  # EVD-453316: SCHEMA §4.8 S-5
        q = "Legal Name: KESTREL MOLDING LLC; DBA Name: —; Physical Address: 45 GRANGER ROAD, TROY, AL 36099; Status: ACTIVE"
        self.check(ev("ORG-8", FMCSA, q, "address", "organizations"), "FAIL", "hq_from_s5_identity_source")

    def test_hq_from_state_filing(self):  # EVD-458107: S-5 (a state filing's address may be an agent's)
        q = "legal_name: KESTREL MOLDING LLC; entity_type: Stock; principal_address: 318 LARCH DRIVE TROY, AL 36099"
        self.check(ev("ORG-8", STATE, q, "address", "organizations"), "FAIL", "hq_from_s5_identity_source")

    def test_hq_wrong_city_from_entity_source(self):  # planted: an entity-address source in another city
        q = "recipient_name: ALDER COMPOSITES CORP; recipient_uei: X; recipient_address: 9 QUILL ST, SAN DIEGO, CA 92199"
        self.check(ev("ORG-9", USASP, q, "address", "organizations"), "FAIL", "hq_city_state_differs")

    def test_leading_run_is_strict_fail(self):  # EVD-445712: held name + plant label; owner question
        info = self.check(ev("S-ARM", NPDES, "ARMACOR LLC-CONOVER PLANT; 2380 HOLLAND RD, CONOVER, NC 28699" + ECHO_TAIL),
                          "FAIL", "name_not_held")
        self.assertIn("leading_run", info["name_alt"])

    def test_facility_label_only_is_strict_fail(self):  # EVD-457497 / EVD-456891: permittee is another legal string
        info = self.check(ev("S-ARM", TCEQ, permit("Armacor APO, Inc.", "ARMACOR", "2380 HOLLAND RD, CONOVER, NC 28699")),
                          "FAIL", "name_not_held")
        self.assertIn("facility_label", info["name_alt"])

    def test_parent_name_is_strict_fail(self):  # parent's name on a subsidiary's site: a lead, never a machine bind
        self.check(ev("S-PIN", ITA, "Pinecrest Industries, 4471 Tanner Dr, Lancaster, PA 17699"), "FAIL", "parent_name_lead")

    def test_predecessor_in_notes_is_strict_fail(self):  # EVD-450005: predecessor named only in notes
        info = self.check(ev("S-MER", RCRA, "EASTGATE POLYMERS US; 2650 PRAIRIE BLVD, LONGVIEW, TX 75699" + ECHO_TAIL),
                          "FAIL", "name_not_held")
        self.assertIn("notes", info["name_alt"])

    def test_dotted_initials_is_strict_fail(self):  # EVD-445061: name_key keeps the dots' spaces
        info = self.check(ev("S-CUE", NPDES, "B.R.T. OF WEST VIRGINIA; 940 ASPEN HILL ROAD, MT. HOPE, WV 25899" + ECHO_TAIL),
                          "PASS")
        self.assertNotIn("name_alt", info)  # "b r t of west virginia" is held verbatim; spacing measured when not
        info = self.check(ev("S-CUE", NPDES, "BRT OF WEST VIRGINIA; 940 ASPEN HILL ROAD, MT. HOPE, WV 25899" + ECHO_TAIL),
                          "FAIL", "name_not_held")
        self.assertIn("spacing", info["name_alt"])

    def test_street_key_limits_are_measured_not_passed(self):  # controller: report, do not widen street_key
        self.assertEqual(self.check(ev("S-RANGE", ITA, "Tamarack Rubber, 2203 Elm St, Erie, PA 16599"), "FAIL",
                                    "street_differs")["street_limit"], "number_in_recorded_range")
        self.assertEqual(self.check(ev("S-ORD", ITA, "Tamarack Rubber, 4417 1st Street, Wadsworth, OH 44299"), "FAIL",
                                    "street_differs")["street_limit"], "number_word")

    # ---- true matches: must PASS

    def test_echo_true_match(self):  # EVD-442346
        self.check(ev("S-BAK", RCRA, "CONTAINMENT SYSTEMS INC; 3300 ORION DRIVE, BAKERSFIELD, CA 93399" + ECHO_TAIL),
                   "PASS")

    def test_permit_true_match(self):  # EVD-456335
        self.check(ev("S-PAS", TCEQ, permit("Tamarack Rubber Company", "TAMARACK RUBBER",
                                            "15520 SHORELINE BLVD, PASADENA, TX 77599")), "PASS")

    def test_fmcsa_site_true_match(self):  # EVD-454689
        q = "Legal Name: KESTREL MOLDING LLC; DBA Name: —; Physical Address: 1180 DORSEY AVENUE, VALPARAISO, IN 46399"
        self.check(ev("S-AOC", FMCSA, q), "PASS")

    def test_osha_name_is_one_name(self):  # EVD-431182 shape; Codex 5: a name field is never split on commas
        info = self.check(ev("S-AOC", ITA, "KESTREL, KESTREL MOLDING, 1180 Dorsey Ave, Valparaiso, IN 46399"), "FAIL",
                          "name_not_held")
        self.assertIn("comma_part", info["name_alt"])  # measured: an owner question, never a pass
        info = self.check(ev("S-OAK3", OSHA, "OTHER OPERATOR, ACME POLYMER, 321 OAK ST, DOVER, OH 44699"), "FAIL",
                          "name_not_held")
        self.assertIn("comma_part", info["name_alt"])

    def test_corporate_form_extension(self):  # owner ruling 2026-11-22: structured site rows whose street passes
        info = self.check(ev("S-OAK3", ITA, "Acme Polymer USA Holdings, 321 Oak St, Dover, OH 44699"), "PASS")
        self.assertEqual(info["name_basis"], "corporate_form")
        self.check(ev("S-OAK3", ITA, "Acme Polymer Services, 321 Oak St, Dover, OH 44699"), "FAIL", "name_not_held")
        self.check(ev("S-OAK3", ITA, "Acme Polymer USA, 99 Oak St, Dover, OH 44699"), "FAIL",
                   "name_not_held+street_differs")  # only when the street already passes
        self.check(ev("ORG-15", TCEQ, permit("Acme Polymer LP", "DOVER", "321 OAK ST, DOVER, OH 44699"),
                      table="organizations"), "FAIL", "name_not_held")  # no street test on an organization row
        self.check(ev("S-RR", TCEQ, permit("Riverbend Medical Fleet Services, LLC", "X", "5155 N GARNER ST, ROUND ROCK, "
                                           "TX 78699")), "FAIL", "name_not_held")  # EVD-455899 shape stays FAIL
        self.check(ev("S-PIN", ITA, "Pinecrest Industries Group, 4471 Tanner Dr, Lancaster, PA 17699"), "FAIL",
                   "parent_name_lead")  # a parent's name plus a form word
        info = self.check(ev("S-PIN", ITA, "Pinecrest Foam Holdings, 4471 Tanner Dr, Lancaster, PA 17699"), "PASS")
        self.assertEqual(info["name_basis"], "corporate_form")  # the rule as ruled: held "Pinecrest Foam" + Holdings
        self.check(ev("S-OAK3", ITA, "Acme Polymer Holdings, 321 Oak St, Dover, OH 44699"), "FAIL",
                   "parent_name_lead")  # Codex r2 finding 4: the recorded ultimate parent's own name

    def test_permittee_is_one_name(self):  # Codex 5: "Other Operator, Acme Polymer" in a permittee field
        self.check(ev("S-OAK3", TCEQ, permit("Other Operator, Acme Polymer", "DOVER", "321 OAK ST, DOVER, OH 44699")),
                   "FAIL", "name_not_held")

    def test_building_number_is_not_a_street(self):  # Codex 3: EVD-431716 / SITE-002988 shape must not pass
        self.check(ev("S-1604", OSHA, "TAMARACK RUBBER CO, 2718 BUILDING KESWICK STREET, DALTON, GA 30799"),
                   "UNINSPECTABLE", "no_civic_number")

    def test_shared_building_other_suite(self):  # Codex 3: building A with suite 100 vs suite 300
        self.check(ev("S-BLDGA", ITA, "Tamarack Rubber, 10 Industrial Pkwy Bldg A Ste 300, Kent, OH 44299"), "FAIL",
                   "unit_differs")
        self.check(ev("S-BLDGA", ITA, "Tamarack Rubber, 10 Industrial Pkwy Building A Suite 100, Kent, OH 44299"), "PASS")

    def test_spelled_out_po_box_both_sides(self):  # Codex 3: a mailbox on both sides names no place
        self.check(ev("S-POBOX", ITA, "Tamarack Rubber, Post Office Box 12, Lima, OH 45899"), "UNINSPECTABLE", "no_civic_number")

    def test_other_state_fails(self):  # Codex 3: an explicit other state is contrary evidence
        self.check(ev("S-OHIO", ITA, "Tamarack Rubber, 88 Quarry Bend Rd, Marion, TX 75699"), "FAIL", "state_differs")
        self.check(ev("S-OHIO", TCEQ, permit("Tamarack Rubber Company", "MARION", "88 QUARRY BEND RD, MARION, Texas 75699")),
                   "FAIL", "state_differs")
        self.check(ev("S-OHIO", ITA, "Tamarack Rubber, 88 Quarry Bend Rd, Marion, OH 43399"), "PASS")

    def test_designators_and_place_conflicts(self):  # owner split / Codex r2 finding 2: explicit contrary facts
        self.check(ev("S-OAK1", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, STE. 300, DOVER, OH 44699")),
                   "FAIL", "unit_differs")  # the dotted unit reaches the designator test
        self.check(ev("S-OAK1", ITA, "Acme Polymer, 321 Oak St, Ste. 100, Dover, OH 44699"), "PASS")
        self.check(ev("S-OAK4", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, BUILDING B, DOVER, OH 44699")),
                   "FAIL", "unit_differs")
        self.check(ev("S-OAK4", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, BLDG. A, DOVER, OH 44699")), "PASS")
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, DAYTON, OH 45402")),
                   "FAIL", "city_differs")
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, DOVER, TX")), "FAIL", "state_differs")
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, FL 33101")), "FAIL",
                   "state_differs")  # "FL" after the street is Florida, not a floor
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, DOVER OHIO")), "PASS")
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, DAYTON")), "FAIL", "city_differs")
        self.check(ev("S-BLDG", OSHA, "TAMARACK RUBBER CO, 518 FENWICK GROVE RD BLDG 1, WEST FENWICK TWP, OH 44299"),
                   "PASS")  # "Twp" and "Mt." are spellings, not other places

    def test_parenthetical_city_and_zip5(self):  # controller ruling 2026-11-22: either city part, or equal ZIP5s
        for place in ("SOLON, OH 44139", "CLEVELAND, OH 44139", "Solon, OH", "SOLON, OH 44146", "BEDFORD, OH 44139-2201"):
            self.check(ev("S-PAREN", TCEQ, permit("Acme Polymer", "X", f"5 HUB RD, {place}")), "PASS")
        self.check(ev("S-PAREN", TCEQ, permit("Acme Polymer", "X", "5 HUB RD, BEDFORD, OH 44146")), "FAIL", "city_differs")
        self.check(ev("S-PAREN", TCEQ, permit("Acme Polymer", "X", "5 HUB RD, SOLON, PA 44139")), "FAIL", "state_differs")

    # ---- Codex round 3 on 9205837e (owner ruling 2026-11-22, "strict floor, then merge"): each counterexample is not PASS

    def test_r3_1_locality_must_match_positively(self):
        oak = lambda place: ev("S-OAK3", TCEQ, permit("Acme Polymer", "X", f"321 OAK ST{place}"))  # noqa: E731
        self.check(oak(", DAYTON, TX 44699"), "FAIL", "state_differs+city_differs")
        self.check(oak(", DAYTON, TX 44699 1234"), "FAIL", "state_differs+city_differs")  # a space ZIP+4 hides nothing
        self.check(oak(", DOVER, TX 44699 1234"), "FAIL", "state_differs")
        self.check(oak(", OH 45402"), "HELD", "held_for_reading:locality_not_matched")  # no city, another ZIP
        self.check(oak(""), "HELD", "held_for_reading:locality_not_read")  # a bare street
        self.check(oak(", DOVER, OH"), "PASS")

    def test_r3_1_historical_zip_forms_pass(self):
        # The ten historical rows that passed without the locality call (EVD-455166, EVD-455167, EVD-456396, EVD-456397,
        # EVD-458684, EVD-458685, EVD-458686, EVD-458687 with a space ZIP+4; EVD-458756, EVD-458757 ending in a dash) now
        # pass through same_locality(). Synthetic strings of the same shapes:
        for place in (", DOVER, OH 44699 1594", ", DOVER, Ohio -", ", DOVER, OH 44699-1594", ", DOVER, OH 446991594",
                      ", DOVER, OH 44699-"):
            self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", f"22 BIRCH LN{place}")), "PASS")

    def test_r3_2_one_quote_two_records(self):
        for sid in ("S-TWA", "S-TWB"):  # Dayton's permit matches Dayton by city and Dover by ZIP: it passes on neither
            info = self.check(ev(sid, TCEQ, permit("Acme Polymer", "X", "640 LARCH WAY, DAYTON, OH 44699")), "HELD",
                              "held_for_reading:passes_on_two_records")
            self.assertEqual(info["also_passes_on"], {"S-TWA": "S-TWB", "S-TWB": "S-TWA"}[sid])
        self.check(ev("S-TWA", TCEQ, permit("Acme Polymer", "X", "640 LARCH WAY, DAYTON, OH 44601")), "FAIL",
                   "city_differs")

    def test_r3_3_building_and_unit_designators(self):
        self.check(ev("S-B1A", TCEQ, permit("Acme Polymer", "X", "15 LARCH WAY, BLDG. 1-B, DOVER, OH 44699")), "FAIL",
                   "unit_differs")
        self.check(ev("S-B1A", TCEQ, permit("Acme Polymer", "X", "15 LARCH WAY, BLDG 1A, DOVER, OH 44699")), "PASS")
        self.check(ev("S-BN", TCEQ, permit("Acme Polymer", "X", "16 LARCH WAY, BUILDING SOUTH, DOVER, OH 44699")),
                   "FAIL", "unit_differs")
        self.check(ev("S-UA", TCEQ, permit("Acme Polymer", "X", "17 LARCH WAY, UNIT. B, ROOM 1, DOVER, OH 44699")), "FAIL",
                   "unit_differs")
        self.check(ev("S-UA", TCEQ, permit("Acme Polymer", "X", "17 LARCH WAY, UNIT A, RM. 2, DOVER, OH 44699")), "FAIL",
                   "unit_differs")
        self.check(ev("S-UA", TCEQ, permit("Acme Polymer", "X", "17 LARCH WAY, UNIT A, RM 1, DOVER, OH 44699")), "PASS")
        self.check(ev("S-UA", TCEQ, permit("Acme Polymer", "X", "17 LARCH WAY, UNIT A, ROOM 1, BLDG 3, DOVER, OH 44699")),
                   "HELD", "held_for_reading:designator_not_on_both_sides")  # the building is on one side only
        self.check(ev("S-OAK4", TCEQ, permit("Acme Polymer", "DOVER", "321 OAK ST, BLDG. B, DOVER, OH 44699")), "FAIL",
                   "unit_differs")  # control: Building A against Bldg. B

    def test_r3_4_parenthetical_city_is_not_a_name(self):
        self.check(ev("S-SOLON", TCEQ, permit("Solon", "X", "8 AURORA RD, SOLON, OH 44139")), "FAIL", "name_not_held")
        self.check(ev("S-SOLON", TCEQ, permit("Cleveland", "X", "8 AURORA RD, SOLON, OH 44139")), "FAIL", "name_not_held")
        self.check(ev("S-SOLON", TCEQ, permit("Acme Polymer", "X", "8 AURORA RD, SOLON, OH 44139")), "PASS")
        self.check(ev("S-KDIV", TCEQ, permit("Kestrel Division", "X", "12 BIRCH LN, DOVER, OH 44699")), "PASS")  # control

    def test_r3_5_parent_key_equal_to_own(self):
        self.check(ev("S-ARES", TCEQ, permit("Acme Resin Inc", "X", "20 BIRCH LN, DOVER, OH 44699")), "HELD",
                   "held_for_reading:name_equals_parent_key")
        self.check(ev("S-ARES", TCEQ, permit("Acme Resin LLC", "X", "20 BIRCH LN, DOVER, OH 44699")), "PASS")
        self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", "22 BIRCH LN, DOVER, OH 44699")), "PASS")

    # ---- Codex round 4 on 3e091665: two more constructed passes under the strict floor

    def test_r4_1_one_sided_street_suffix(self):  # Codex r4: EVD-999981 / SITE-999981 (S-BASE here) and two neighbours each side
        for sid, street in (("S-BASE", "30 LARCH WAY"), ("S-LVL", "40 LARCH WAY")):  # the record names a level, the quote does not
            self.check(ev(sid, TCEQ, permit("Acme Polymer", "X", f"{street}, DOVER, OH 44699")), "HELD",
                       "held_for_reading:street_suffix_unexplained")
        self.check(ev("S-BASE", TCEQ, permit("Acme Polymer", "X", "30 LARCH WAY, BASEMENT LEVEL, DOVER, OH 44699")),
                   "HELD", "held_for_reading:street_suffix_unexplained+locality_not_read")  # repeating it does not explain it
        for suffix in ("LOWER LEVEL", "MEZZANINE"):  # the quote names a level, the record does not
            self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", f"22 BIRCH LN, {suffix}, DOVER, OH 44699")),
                       "HELD", "held_for_reading:locality_not_read")
        self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", "22 BIRCH LN, DOVER, OH 44699")), "PASS")  # control

    def test_r4_2_second_state_or_zip_in_the_locality(self):  # Codex r4: EVD-999984 / SITE-999984 (S-ZEP here) and neighbours
        for place in (", DAYTON TX 75001, OH 44699", ", DAYTON TX 75001 OH 44699", ", TX, OH 44699",
                      ", DAYTON, TX 75001, OH 44699", ", DAYTON TX, OH 44699", ", DOVER, OH 44699, 44601",
                      ", DAYTON TX 75001, TOWNSHIP OF, OH 44699", ", TX, TOWNSHIP OF, OH 44699",
                      ", DAYTON TX, TOWNSHIP OF, OH 44699"):  # Codex r5: the ECHO "TOWNSHIP OF" form
            self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", f"22 BIRCH LN{place}")), "HELD",
                       "held_for_reading:locality_not_read")
        self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", "22 BIRCH LN, OH 44699, TX 75001")), "FAIL",
                   "state_differs+city_differs")  # a printed other state stays a demonstrated conflict
        self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", "22 BIRCH LN, DOVER, OH 44699")), "PASS")  # control
        self.check(ev("S-ZEP", TCEQ, permit("Zephyr Plastics Inc", "X", "22 BIRCH LN, DOVER, TOWNSHIP OF, OH 44699")),
                   "PASS")  # control: the clean ECHO "TOWNSHIP OF" form still passes

    def test_r3_6_parentheses_are_not_dropped(self):
        for name in ("Acme Polymer (operated by Quill Resins)", "Acme Polymer (Storage Division)"):
            self.check(ev("S-OAK3", TCEQ, permit(name, "X", "321 OAK ST, DOVER, OH 44699")), "HELD",
                       "held_for_reading:name_with_parenthetical")
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer Services", "X", "321 OAK ST, DOVER, OH 44699")), "FAIL",
                   "name_not_held")
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer USA", "X", "321 OAK ST, DOVER, OH 44699")), "PASS")
        self.check(ev("S-OAK3", TCEQ, permit("Acme Polymer", "X", "321 OAK ST (REAR), DOVER, OH 44699")), "HELD",
                   "held_for_reading:address_with_parenthetical")

    def test_bare_site_label_is_not_the_operator(self):  # owner ruling 2026-11-22, "drop generic labels only"
        for name in ("Plant 2", "Dover", "Tuscarawas County", "North Works", "Ohio"):  # labels, city, county, state
            info = self.check(ev("S-PHOLD", TCEQ, permit(name, "X", "9 ELM RD, DOVER, OH 44699")), "FAIL", "name_not_held")
            self.assertNotIn("name_basis", info, name)
        self.check(ev("S-PLANT2", TCEQ, permit("Plant 2", "X", "77 KILN RD, DOVER, OH 44699")), "FAIL", "name_not_held")
        info = self.check(ev("S-PLANT2", TCEQ, permit("Acme Polymer Plant 2", "X", "77 KILN RD, DOVER, OH 44699")), "PASS")
        self.assertEqual(info["name_basis"], "site_name_other")  # the label beside the operator's own name still binds
        info = self.check(ev("S-AVON", ITA, "Tamarack, 736 Hollis Rd, Sheffield Lake, OH 44098"), "PASS")
        self.assertEqual(info["name_basis"], "site_name_lead")  # a brand or short trading name is a held name

    def test_parent_name_is_a_lead_on_every_path(self):  # owner ruling 2026-11-22, "fail everywhere"
        for name in ("Acme Polymer Holdings", "Acme Polymer Holdings Inc"):  # in the site name, and + a form word
            self.check(ev("S-PHOLD", TCEQ, permit(name, "X", "9 ELM RD, DOVER, OH 44699")), "FAIL", "parent_name_lead")
        self.check(ev("S-PHOLD", TCEQ, permit("Acme Polymer", "X", "9 ELM RD, DOVER, OH 44699")), "PASS")

    def test_osha_four_digit_zip(self):  # EVD-430557: the ZIP lost its leading zero
        self.check(ev("S-CT", ITA, "Kestrel Molding LLC, 77 Marsh St Ext, East Haven, CT 6599"), "PASS")

    def test_osha_mangled_zips_parse(self):  # EVD-430785, EVD-431015: "317E6" and a 9-digit ZIP
        for z in ("317E6", "065991129"):
            self.check(ev("S-CT", ITA, f"Kestrel Molding LLC, 77 Marsh St Ext, East Haven, CT {z}"), "PASS")

    def test_echo_parenthetical_with_semicolon(self):  # EVD-441359: "(XYZ; FORMERLY ...)" is not a field break
        # Owner ruling 2026-11-22, "strict floor": the parenthetical is kept in the name, so the name is held only once it
        # is dropped: HELD for a reader, never PASS (was PASS before the floor).
        self.check(ev("S-BAK", RCRA, "CONTAINMENT SYSTEMS INC (CSI; FORMERLY TANKCO); 3300 ORION DR, BAKERSFIELD, "
                                     "CA 93399" + ECHO_TAIL), "HELD", "held_for_reading:name_with_parenthetical")

    def test_ampersand_and_intersection(self):  # EVD-428624
        self.check(ev("S-AND", OSHA, "TAMARACK RUBBER CO, 7TH AND ASHCROFT LANE, BERWICK, PA 18699"), "PASS")

    def test_same_suite_and_one_sided_unit(self):  # EVD-430253; a unit on one side only is no conflict, and no match
        self.check(ev("S-STE200", ITA, "Tamarack Rubber, 6120 S. Juniper Ln, Suite 200, Goodyear, AZ 85399"), "PASS")
        # Owner ruling 2026-11-22, "strict floor": a designator stated on one side only is HELD (was PASS before the floor).
        self.check(ev("S-BLDG", NPDES, "TAMARACK RUBBER CO; 518 FENWICK GROVE ROAD, WEST FENWICK TWP, OH 44299"
                      + ECHO_TAIL), "HELD", "held_for_reading:designator_not_on_both_sides")

    def test_civic_number_forms(self):  # 463 review: SITE-004431, SITE-011463, SITE-004620 are real civic numbers
        self.check(ev("S-ONE", ITA, "Tamarack Rubber Co, One Heron Dr, Neenah, WI 54999"), "PASS")
        self.check(ev("S-198A", ITA, "Tamarack Rubber Co, 212B LARKIN BLVD, New Bern, NC 28599"), "PASS")
        self.check(ev("S-GRID", OSHA, "TAMARACK RUBBER CO, N52 W24411 CEDAR PLANK ROAD, OCONOMOWOC, WI 53099"), "PASS")

    def test_org_existence_from_permit(self):  # EVD-457166: the permit witnesses the permittee's existence
        self.check(ev("ORG-5", TCEQ, permit("Gulfstar Enterprises LLC", "CORNER AUTO SUPPLY 4417",
                                            "9150 W KESSLER AVE, HOUSTON, TX 77099"), table="organizations"), "PASS")

    def test_org_existence_from_state_filing(self):  # EVD-458053
        q = "legal_name: KESTREL MOLDING LLC; entity_type: SYNTHETIC TYPE Q; status: Synthetic"
        self.check(ev("ORG-8", STATE, q, table="organizations"), "PASS")

    def test_hq_from_usaspending(self):  # EVD-459301
        q = ("recipient_name: TAMARACK RUBBER CO; recipient_uei: X; parent_recipient_name: TAMARACK RUBBER CO; "
             "recipient_address: 880 MILLRACE RD, AKRON, OH 443998219; award_count: 1")
        self.check(ev("ORG-7", USASP, q, "address", "organizations"), "PASS")

    def test_hq_from_sbir_full_state_name(self):  # EVD-458829
        q = "firm_name: ALDER COMPOSITES CORPORATION; uei: X; address: 1294 PALOMA ST STE C4, CHULA VISTA, California 91999"
        self.check(ev("ORG-9", SBIR, q, "address", "organizations"), "PASS")

    # ---- uninspectable: never PASS

    def test_no_civic_number(self):  # equal keys naming only a park cannot tell two places apart
        self.check(ev("S-PARK", ITA, "Tamarack Rubber Co, Willow Bend Industrial Park, Neodesha, KS 66799"),
                   "UNINSPECTABLE", "no_civic_number")

    def test_shifted_columns(self):  # EVD-455505: NC DEQ layer puts a region code in permittee
        q = ("permittee: 3; facility: Tamarack Rubber Company; address: 5530 Bragg Ridge Street, Fayetteville, NC 28399; "
             "county: 2600099; permit_number(s): 3705199999")
        info = self.check(ev("S-NC", NCDEQ, q), "UNINSPECTABLE", "operator_not_a_name")
        self.assertEqual(info["if_facility_operator"], "PASS")

    def test_uninspectable_classes(self):
        self.check(ev("S-NC", "https://example.com/", None), "UNINSPECTABLE", "no_quote")
        self.check(ev("PERSON-1", "https://example.edu/", "x", table="people"), "UNINSPECTABLE", "other_table")
        self.check(ev("S-NONE", ITA, "x, 1 Q St, B, OH 44199"), "UNINSPECTABLE", "record_not_found")
        self.check(ev("ORG-7", "examplecompany.com", "sells foam blocks", table="organizations"),
                   "UNINSPECTABLE", "unknown_source_family")
        self.check(ev("S-NC", RCRA, "TAMARACK RUBBER CO; NO ADDRESS PRINTED; FRS registry 1"), "UNINSPECTABLE",
                   "parse_failed")


    # ---- web quotes: FAIL or READ_REQUIRED, never PASS (controller ruling A, 2026-11-22)

    def web(self, rid, url, quote, cls="own_site", claim="existence", table="sites"):
        return ev(rid, url, quote, claim, table, cls=cls)

    def test_web_own_site_with_street_is_read_required(self):  # mechanics clear, still a reading
        self.check(self.web("S-NC", "https://careers.tamarackrubber.example/plants",
                            "Our Fayetteville plant, 5530 Bragg Ridge Street, makes hose."), "READ_REQUIRED",
                   "mechanics_clear")
        self.check(self.web("S-ONE", "http://tamarackrubber.example/neenah", "Visit us at 1 Heron Dr, Neenah",
                            claim="address"), "READ_REQUIRED", "mechanics_clear")  # number word vs digit
        self.check(self.web("S-LET", "https://www.tamarackrubber.example/", "Street Address: 2210 LARKSPUR ROAD"),
                   "READ_REQUIRED", "mechanics_clear")  # "2210 C": the letter belongs to the civic number

    def test_web_sibling_sites_one_quote(self):  # Codex 4: one quote naming the second sibling's address
        q = "Acme Polymer, 321 Oak Avenue, Suite 300, Dover OH"
        self.check(self.web("S-OAK1", "https://acmepolymer.example/sites", q), "FAIL", "unit_differs")
        self.check(self.web("S-OAK2", "https://acmepolymer.example/sites", q), "READ_REQUIRED", "mechanics_clear")
        self.check(self.web("S-OAK1", "https://acmepolymer.example/sites", "321 Oak Street, Suite 300"), "FAIL",
                   "unit_differs")  # the suite alone changed
        self.check(self.web("S-OAK3", "https://acmepolymer.example/sites", "321 Oak Avenue, Dover"), "READ_REQUIRED",
                   "mechanics_clear")  # another suffix is left to the reader: "Tampa E Blvd" must not FAIL
        self.check(self.web("S-OAK3", "https://acmepolymer.example/", "321 Tampa East Blvd"), "FAIL",
                   "street_absent_from_quote")

    def test_web_area_code_and_zip_are_not_civic_numbers(self):  # Codex 4
        self.check(self.web("S-OAK3", "https://acmepolymer.example/", "Call (321) 555-0100. Visit 99 Oak Street"),
                   "FAIL", "street_absent_from_quote")
        self.check(self.web("S-ZIP", "https://acmepolymer.example/", "12 Oak Street, Dover, OH 43000"),
                   "FAIL", "street_absent_from_quote")

    def test_web_other_operator_or_tenant_never_passes(self):  # Codex 5
        self.check(self.web("ORG-15", "https://news.example/a", "Acme Polymer Services opened a plant", cls="press",
                            table="organizations"), "READ_REQUIRED", "mechanics_clear")
        self.check(self.web("S-OAK3", "https://acmepolymer.example/history",
                            "Acme Polymer formerly ran 321 Oak Street; Neighbor Resins operates it now"),
                   "READ_REQUIRED", "mechanics_clear")
        self.check(self.web("S-PAGES", "https://other-molder.pages.dev/", "12 Kiln Rd"), "FAIL", "not_own_site")
        self.check(self.web("S-PAGES", "https://acme.pages.dev/plant", "12 Kiln Rd"), "READ_REQUIRED", "mechanics_clear")

    def test_web_platform_host_and_path(self):  # ruling A: on a platform host, host AND path must match
        self.check(self.web("ORG-8", "https://kestrelmolding.wixsite.com/home/contact", "Kestrel molds caps",
                            table="organizations"), "READ_REQUIRED", "mechanics_clear")
        for url in ("https://othermolder.wixsite.com/home", "https://kestrelmolding.wixsite.com/other",
                    "https://www.linkedin.com/company/tamarack"):
            self.check(self.web("ORG-8", url, "Kestrel molds caps", table="organizations"), "FAIL", "not_own_site")
        self.assertFalse(b.own_domain(("sites.google.com", "view/x"), ("sites.google.com", "")))  # bare root
        self.assertTrue(b.own_domain(("na.tamarack.example", ""), ("tamarack.example", "about")))

    def test_web_satellite_plant_as_hq(self):  # Codex 6: an organization address quote is always a reading
        self.check(self.web("ORG-15", "https://acmepolymer.example/contact",
                            "Our Center, OH plant; headquarters: 9 Main St, Dayton, OH", claim="address",
                            table="organizations"), "READ_REQUIRED", "mechanics_clear")

    def test_web_off_domain_and_street_failures(self):
        self.check(self.web("S-NC", "https://hosedepot.example/brands/tamarack", "5530 Bragg Ridge St, Fayetteville"),
                   "FAIL", "not_own_site")
        self.check(self.web("S-NC", "https://www.tamarackrubber.example/", "Our plant at 812 Cedar Mill Rd"),
                   "FAIL", "street_absent_from_quote")
        self.check(self.web("S-NC", "https://hosedepot.example/", "Tamarack Rubber, Fayetteville NC"),
                   "FAIL", "street_absent_from_quote+not_own_site")
        info = self.check(self.web("S-NC", "https://www.tamarackrubber.example/", "5530 Braggridge Street"),
                          "FAIL", "street_absent_from_quote")
        self.assertEqual(info.get("street_limit"), "spacing")  # measured, never passing
        info = self.check(self.web("S-NC", "https://tamarackhose.example/", "5530 Bragg Ridge St"), "FAIL", "not_own_site")
        self.assertEqual(info.get("name_alt"), "name_in_host")

    def test_web_read_required_reasons(self):
        self.check(self.web("ORG-7", "https://rubberdirectory.example/m/77", "A hose and belting maker in Akron",
                            cls="press", table="organizations"), "READ_REQUIRED", "name_absent_from_quote")
        self.check(self.web("ORG-2", "https://northfield.example/", "Northfield makes resins", table="organizations"),
                   "READ_REQUIRED", "no_record_website")
        self.check(self.web("S-BLANK", "https://www.tamarackrubber.example/", "Our Wickliffe plant"),
                   "READ_REQUIRED", "web_record_no_street")
        self.check(self.web("S-NC", "https://state.example/registry/1", "TAMARACK RUBBER CO, 5530 BRAGG RIDGE ST",
                            cls="government_filing"), "READ_REQUIRED", "web_class_untested")

    def test_no_url_row_is_ever_pass(self):  # ruling A as a property over every fixture record, class and claim
        quotes = ("Tamarack Rubber Company, 5530 Bragg Ridge Street", "Acme Polymer, 321 Oak Street, Suite 100",
                  "Kestrel Molding LLC, 1180 Dorsey Ave", "Headquarters: 880 Millrace Rd, Akron, OH")
        urls = ("https://www.tamarackrubber.example/", "https://acmepolymer.example/", "https://acme.pages.dev/",
                "https://kestrelmolding.wixsite.com/home", "https://directory.example/x")
        recs = [(s["site_id"], "sites") for s in SITES] + [(o["org_id"], "organizations") for o in ORGS]
        for rid, table in recs:
            for url in urls:
                for q in quotes:
                    for cls in ("own_site", "directory", "press", "registry", "government_filing"):
                        for claim in ("existence", "address", "scope"):
                            v = b.judge(ev(rid, url, q, claim, table, cls=cls), self.idx)[0]
                            self.assertNotEqual(v, "PASS", (rid, url, q, cls, claim))


class ProgramAndEcosystemVerdicts(unittest.TestCase):
    def test_structured_claims_bind_to_the_record_and_locality(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "data").mkdir()
            (tree / "data/programs.csv").write_text(
                "program_id,program_name,institution_org_id,city,state\n"
                "PROG-T1,Polymer Training Center,ORG-T1,Dover,OH\n")
            (tree / "data/ecosystem.csv").write_text(
                "org_id,legal_name,city,state,record_grain,office_name,parent_institution_org_id\n"
                "ORG-T1,Acme Institute,Dover,OH,institution,,\n"
                "ORG-T2,Acme Licensing Office,Dover,OH,office,Licensing Office,ORG-T1\n")
            with patch.object(b, "TREE", tree):
                idx = b.Index.load()
            for table, rid, name in (("programs", "PROG-T1", "Polymer Training Center"),
                                     ("ecosystem", "ORG-T1", "Acme Institute"),
                                     ("ecosystem", "ORG-T2", "Licensing Office")):
                for claim in ("existence", "scope", "address"):
                    for operator, place, verdict in (
                        (name, "Dover, OH", "PASS"),
                        ("Another Institution", "Dover, OH", "FAIL"),
                        (name, "Cleveland, OH", "FAIL"),
                        (name, "Dover, DE", "FAIL"),
                    ):
                        with self.subTest(table=table, claim=claim, operator=operator, place=place):
                            quote = f"recipient_name: {operator}; recipient_address: 100 Elm St, {place}"
                            row = ev(rid, "USAspending bulk synthetic", quote, claim, table)
                            self.assertEqual(b.judge(row, idx)[0], verdict)
                with self.subTest(table=table, claim="code"):
                    quote = f"recipient_name: {name}; recipient_address: 100 Elm St, Dover, OH"
                    row = ev(rid, "USAspending bulk synthetic", quote, "code", table)
                    self.assertEqual(b.judge(row, idx)[0], "UNINSPECTABLE")

            quote = "recipient_name: Acme Institute; recipient_address: 100 Elm St, Dover, OH"
            self.assertEqual(b.judge(ev("PROG-T1", "USAspending bulk synthetic", quote, table="programs"), idx)[0],
                             "FAIL")
            self.assertEqual(b.judge(ev("ORG-T2", "USAspending bulk synthetic", quote, table="ecosystem"), idx)[:2],
                             ("FAIL", "parent_name_lead"))
            self.assertEqual(b.judge(ev("ORG-T1", "USAspending bulk synthetic", quote, table="organizations"), idx)[:2],
                             ("UNINSPECTABLE", "record_not_found"))


class GateMechanics(unittest.TestCase):
    parallel_safe = True

    def test_any_column_edit_regates(self):  # ruling D / Codex 2: source_class and created_by edits included
        base = [ev("S-PROS", ITA, "q", eid=f"EVD-{n}") for n in range(1, 6)]
        head = [dict(base[0]), dict(base[1], record_id="S-CARN"), dict(base[2], source_class="own_site"),
                dict(base[3], created_by="lane-b"), dict(base[4], notes="x"), ev("S-CARN", ITA, "q", eid="EVD-9")]
        head[0]["_at"] = "data/evidence_moved.csv:9"  # a row that only moved shard or line is unchanged
        self.assertEqual([e["evidence_id"] for e in b.changed_rows(base, head)],
                         ["EVD-2", "EVD-3", "EVD-4", "EVD-5", "EVD-9"])
        migrated = [dict(e, address_role="") for e in base]  # a schema column added empty edits no row
        self.assertEqual(b.changed_rows(base, migrated), [])
        migrated[0]["address_role"] = "plant"  # filling it does
        self.assertEqual([e["evidence_id"] for e in b.changed_rows(base, migrated)], ["EVD-1"])

    def test_label_names_its_folder_exactly(self):  # ruling E
        self.assertEqual(b.label_folder("lane-a-2026-11-22"), "lane-a-2026-11-22")
        self.assertEqual(b.label_folder("claude-code lane-a-2026-11-22"), "lane-a-2026-11-22")
        for label in ("claude-code lane-a extra", "p2-apply (integrator)", "../x", "a b c", ""):
            self.assertEqual(b.label_folder(label), "", label)

    def test_provenance_rules(self):  # ruling E / Codex 7
        checks = {"lane-a": b"print('ok')\n", "lane-b": b"  \n", "lane-old": b"print(1)\n", "lane-a-2026-11-22": b"x"}
        on_base = {"lane-old"}

        def problems(labels, base_labels=()):
            rows = [dict(ev("S-PROS", ITA, "q"), created_by=c) for c in labels]
            return b.provenance_problems(rows, set(base_labels), lambda f: f in on_base,
                                         lambda f: checks.get(f, b"").strip())
        self.assertEqual(problems(["lane-a", "claude-code lane-a"]), [])
        for label, why in (("lane-b", "MISSING tasks/lane-b/check.py"),  # whitespace-only check.py
                           ("claude-code lane-a extra", "names no folder"),  # extra token
                           ("lane", "MISSING tasks/lane/check.py"),  # a prefix of a folder is not that folder
                           ("lane-a-2026-11-21", "MISSING tasks/lane-a-2026-11-21/check.py"),  # different date
                           ("codex lane-old", "already exists on the base")):  # a new label borrowing a folder
            self.assertIn(why, problems([label])[0], label)
        self.assertEqual(problems(["lane-old"], base_labels=["lane-old"]), [])  # presence only: nothing is executed

    def test_tree_reads_refuse_symlinks_and_escapes(self):  # ruling F
        with tempfile.TemporaryDirectory() as d:
            t = Path(d) / "tree"
            (t / "tasks" / "lane-a").mkdir(parents=True)
            (Path(d) / "secret").write_text("x")
            (t / "tasks" / "lane-a" / "check.py").symlink_to(Path(d) / "secret")
            (t / "tasks" / "lane-a" / "README.md").write_text("ok")
            old, b.TREE = b.TREE, t
            try:
                self.assertIsNone(b.tasks_file(None, "tasks/lane-a/check.py"))
                self.assertIsNone(b.tasks_file(None, "tasks/../secret"))
                self.assertEqual(b.tasks_file(None, "tasks/lane-a/README.md"), b"ok")
            finally:
                b.TREE = old

    def test_tree_fails_closed(self):  # ruling F: a symlinked shard
        with tempfile.TemporaryDirectory() as d:
            t = Path(d) / "tree"
            (t / "data").mkdir(parents=True)
            (Path(d) / "outside.csv").write_text("evidence_id\nEVD-1\n")
            (t / "data" / "evidence_x.csv").symlink_to(Path(d) / "outside.csv")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(b.main(["--all", "--tree", str(t)]), 2)

    def test_held_rows_fail_the_gate(self):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d)
            (t / "data").mkdir()
            (t / "data" / "organizations_OH.csv").write_text(
                "org_id,legal_name,trade_names,website,hq_city,hq_state\n"
                "ORG-T1,Acme Polymer,,https://acmepolymer.example/,Dover,OH\n")
            (t / "data" / "sites_OH.csv").write_text("site_id,org_id,site_name,city,state,street_address\n")
            (t / "data" / "evidence_t.csv").write_text(
                "evidence_id,record_table,record_id,claim_type,claim_detail,source_ref,source_class,created_by\n"
                "EVD-T1,organizations,ORG-T1,existence,synthetic claim; quote: Acme Polymer makes parts.,"
                "https://acmepolymer.example/about,own_site,lane-t\n")
            head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = b.main(["--new-since", head.strip(), "--tree", str(t)])
        self.assertEqual(code, 1, out.getvalue())
        self.assertIn("READ_REQUIRED", out.getvalue())
        self.assertIn("BINDING_PROOF.csv", out.getvalue())

    def test_report_counts_sum(self):
        res = [{"verdict": v, "reason": "", "created_by": "x", "source_family": "url"} for v in b.VERDICTS]
        with contextlib.redirect_stdout(io.StringIO()):
            b.report(res, len(b.VERDICTS))
            with self.assertRaises(AssertionError):
                b.report(res, len(b.VERDICTS) + 1)

    def test_audit_sample_admits_nothing(self):
        res = [{"evidence_id": f"EVD-{n}", "verdict": "PASS" if n % 4 else "FAIL", "created_by": "lane-a"}
               for n in range(100)]
        pick = b.audit_sample(res, 10, "7")["lane-a"]
        self.assertEqual(len(pick), 10)
        self.assertTrue(all(r["verdict"] == "PASS" for r in pick))
        self.assertEqual(pick, b.audit_sample(list(reversed(res)), 10, "7")["lane-a"])  # order-free
        self.assertNotEqual(pick, b.audit_sample(res, 10, "8")["lane-a"])  # the seed moves it


def has_commits(*shas):
    return all(subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{s}^{{commit}}"],
                              capture_output=True).returncode == 0 for s in shas)


class WebProofs(unittest.TestCase):
    SOURCE = "https://acmepolymer.example/about"
    QUOTE = "Acme Polymer makes components for the automotive industry."
    CAPTURE = f"<main><p>Markets</p><p>{QUOTE}</p></main>".encode()
    FOLDER = "tasks/lane-t/"
    BASE = "0" * 40
    PR_HEAD = "1" * 40

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tree = Path(temp.name).resolve()
        (self.tree / "data").mkdir()
        (self.tree / self.FOLDER).mkdir(parents=True)
        (self.tree / self.FOLDER / "README.md").write_text("Built by: Codex\n")
        (self.tree / self.FOLDER / "check.py").write_text("raise SystemExit('PR script executed')\n")
        (self.tree / "data/organizations_OH.csv").write_text(
            "org_id,legal_name,trade_names,website\n"
            "ORG-T1,Acme Polymer,,https://acmepolymer.example/\n"
            "ORG-T2,Acme Polymer II,,https://acmepolymer.example/\n")
        with (self.tree / "data/organizations_OH.csv").open() as f:
            self.base_orgs = list(csv.DictReader(f))
        self.base_tables = {}
        self.ev = dict(evidence_id="EVD-T1", record_table="organizations", record_id="ORG-T1",
                       claim_type="activity", claim_detail=f"markets_served=automotive; quote: {self.QUOTE}",
                       source_ref=self.SOURCE, source_class="own_site", created_by="codex lane-t",
                       observed_date="2026-11-23", tier_effect="supports_A")
        self.proof = dict(evidence_id="EVD-T1", record_id="ORG-T1", claim_sha256=b.claim_sha256(self.ev),
                          capture=self.SOURCE, capture_date="2026-11-23", reader_date="2026-11-23",
                          capture_sha256=hashlib.sha256(self.CAPTURE).hexdigest(), quote_offset=8,
                          verdict="VERIFIED", reader_family="Gemini Hydrogen")
        self.capture = self.CAPTURE
        self.fetch_error = None

    def archive(self, timestamp, *, duplicate=False):
        day = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}"
        prefix = "https://web.archive.org/web/"
        indexed = f"{prefix}{timestamp}/{self.SOURCE}"
        self.proof.update(capture=f"{prefix}{timestamp}id_/{self.SOURCE}", capture_date=day)
        line = f"EVD-T1,{indexed},{day},codex lane-t\n"
        (self.tree / "data/archive_links.csv").write_text(
            "evidence_id,archive_ref,captured_at,created_by\n" + line * (2 if duplicate else 1))

    def run_gate(self, *, proof_bytes=None, mode="--verify-proofs", git_read=None, pr_head=PR_HEAD, held_proof=False):
        with (self.tree / "data/evidence_t.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, self.ev)
            writer.writeheader()
            writer.writerow(self.ev)
        p = self.tree / self.FOLDER / "BINDING_PROOF.csv"
        if proof_bytes is None:
            with p.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, b.PROOF_COLS)
                writer.writeheader()
                writer.writerow(self.proof)
        else:
            p.write_bytes(proof_bytes)
        out = io.StringIO()
        rows = b.rows
        args = [mode, self.BASE]
        if pr_head is not None:
            args.extend(["--tree", str(self.tree), "--pr-head", pr_head])

        def tree_rows(ref, pattern):
            if ref:
                return self.base_orgs if pattern == "organizations_*.csv" else self.base_tables.get(pattern, [])
            return rows(ref, pattern)

        tasks_file = b.tasks_file

        def read_task(ref, path):
            return tasks_file(None if held_proof and ref == self.BASE else ref, path)

        with (
            contextlib.redirect_stdout(out),
            patch.object(b, "tasks_file", side_effect=read_task),
            patch.object(b, "resolve_base", return_value=self.BASE),
            patch.object(b, "rows", side_effect=tree_rows),
            patch.object(b, "git", side_effect=git_read, return_value=f"{self.BASE} {self.PR_HEAD}\n2026-11-23\n") as git,
            patch.object(b, "fetch_url", return_value=self.capture, side_effect=self.fetch_error) as fetch,
        ):
            code = b.main(args)
        self.git = git
        self.fetch = fetch
        return code, out.getvalue()

    def assert_held(self, problem, **kwargs):
        code, out = self.run_gate(**kwargs)
        self.assertEqual(code, 1, out)
        self.assertIn(problem, out)
        self.assertNotIn("web_proof_replayed", out)

    def test_valid_live_and_archived_proofs(self):
        for stamp in (None, "20241123013000"):  # inclusive two-calendar-year boundary
            with self.subTest(stamp=stamp):
                if stamp:
                    self.archive(stamp)
                code, out = self.run_gate()
                self.assertEqual(code, 0, out)
                self.assertIn("1 PASS", out)
                self.fetch.assert_called_once_with(self.proof["capture"])

    def test_program_and_ecosystem_web_rows_require_proof_replay(self):
        for table, rid, column, values in (
            ("programs", "PROG-T1", "program_id", {"program_name": "Polymer Training Center", "url": self.SOURCE}),
            ("ecosystem", "ORG-T3", "org_id", {"legal_name": "Acme Institute", "record_grain": "institution",
                                             "website": "https://acmepolymer.example/"}),
            ("ecosystem", "ORG-T4", "org_id", {"legal_name": "Acme Institute Office", "record_grain": "office",
                                             "tto_url": self.SOURCE, "website": "https://acmepolymer.example/"}),
        ):
            with self.subTest(record=rid):
                filename = f"{table}.csv"
                record = {column: rid, "city": "Dover", "state": "OH", **values}
                self.base_tables[filename] = [record]
                with (self.tree / "data" / filename).open("w", newline="") as f:
                    writer = csv.DictWriter(f, record)
                    writer.writeheader()
                    writer.writerow(record)
                self.ev.update(record_table=table, record_id=rid, claim_type="scope", source_ref=self.SOURCE)
                self.proof.update(record_id=rid, claim_sha256=b.claim_sha256(self.ev), capture=self.SOURCE)
                self.assert_held("no proof line", proof_bytes=(",".join(b.PROOF_COLS) + "\n").encode())
                code, out = self.run_gate()
                self.assertEqual(code, 0, out)
                self.assertIn("web_proof_replayed", out)
                for address, expected in (
                    ("100 Harp Lane, Dover, OH 44622", "web_proof_replayed"),
                    ("100 Harp Lane, Cleveland, OH 44114", "locality_differs"),
                    ("Acme Office 100 Harp Lane Dover, OH 44622", "locality_not_matched"),
                ):
                    with self.subTest(address=address):
                        self.ev.update(claim_type="address", claim_detail=f"campus address; quote: {address}")
                        self.capture = f"<main>{address}</main>".encode()
                        self.proof.update(claim_sha256=b.claim_sha256(self.ev), quote_offset=0,
                                          capture_sha256=hashlib.sha256(self.capture).hexdigest())
                        code, out = self.run_gate()
                        self.assertEqual(code, int(expected != "web_proof_replayed"), out)
                        self.assertIn(expected, out)
                self.ev.update(claim_type="scope", claim_detail=f"markets_served=automotive; quote: {self.QUOTE}")
                self.capture = self.CAPTURE
                self.proof.update(quote_offset=8, capture_sha256=hashlib.sha256(self.capture).hexdigest())
                if "website" not in values or values["record_grain"] == "office":
                    self.ev["source_ref"] = "https://acmepolymer.example/another-program"
                    self.proof.update(capture=self.ev["source_ref"], claim_sha256=b.claim_sha256(self.ev))
                    self.assert_held("not_own_site")
                    self.fetch.assert_not_called()

    def test_backdated_observation_cannot_admit_a_2014_archive(self):
        self.archive("20140531000000")
        self.ev["observed_date"] = "2014-06-01"
        self.proof["claim_sha256"] = b.claim_sha256(self.ev)
        self.assert_held("more than 30 days from merge commit committer date")
        self.fetch.assert_not_called()

    def test_observation_beyond_30_days_from_merge_is_held(self):
        for observed in ("2026-10-23", "2026-10-14", "2027-01-02"):
            with self.subTest(observed=observed):
                self.ev["observed_date"] = observed
                self.proof["claim_sha256"] = b.claim_sha256(self.ev)
                self.assert_held("more than 30 days from merge commit committer date")
                self.fetch.assert_not_called()

    def test_observation_within_30_days_of_merge_passes(self):
        for observed, stamp in (("2026-10-24", None), ("2026-11-13", "20241113000000")):
            with self.subTest(observed=observed):
                self.ev["observed_date"] = observed
                self.proof["claim_sha256"] = b.claim_sha256(self.ev)
                if stamp:
                    self.archive(stamp)  # Exactly two years from observed_date, older if measured from the merge.
                code, out = self.run_gate()
                self.assertEqual(code, 0, out)
                self.assertIn("1 PASS", out)
                self.git.assert_called_once_with("show", "--no-patch", "--format=%P%n%cs", "--end-of-options",
                                                 "HEAD^{commit}", "--", worktree=self.tree)
                self.fetch.assert_called_once()

    def test_forged_head_date_cannot_admit_a_proof(self):
        def git(*args, **kwargs):
            return subprocess.check_output(["git", "-C", str(self.tree), *args], text=True, **kwargs).strip()

        git("init", "-q")
        empty = git("mktree", input="")
        identity = dict(os.environ, GIT_AUTHOR_NAME="Synthetic", GIT_AUTHOR_EMAIL="synthetic@example.com",
                        GIT_COMMITTER_NAME="Synthetic", GIT_COMMITTER_EMAIL="synthetic@example.com")

        def commit(message, day, *parents):
            return git("commit-tree", empty, "-m", message, *parents,
                       env=dict(identity, GIT_AUTHOR_DATE=day, GIT_COMMITTER_DATE=day))

        forged_day = "2014-06-01T08:00:00+00:00"
        merge_day = "2026-11-23T08:00:00+00:00"
        base = commit("base", merge_day)
        forged = commit("PR head", forged_day, "-p", base)
        merge = commit("GitHub merge", merge_day, "-p", base, "-p", forged)
        git("update-ref", "HEAD", merge)
        self.archive("20140531000000")
        self.ev["observed_date"] = "2014-06-01"
        self.proof["claim_sha256"] = b.claim_sha256(self.ev)
        for mode, pr_head in (("--verify-proofs", forged), ("--new-since", None)):
            with self.subTest(mode=mode), patch.object(b, "ROOT", self.tree):
                self.assert_held("more than 30 days from merge commit committer date",
                                 git_read=b.git, pr_head=pr_head, mode=mode)
                self.fetch.assert_not_called()

    def test_unreadable_merge_fails_closed(self):
        error = subprocess.CalledProcessError(128, "git show", stderr="missing merge commit")
        code, out = self.run_gate(git_read=error)
        self.assertEqual(code, 2, out)
        self.assertIn("could not inspect proof inputs", out)
        self.fetch.assert_not_called()

    def test_nonmerge_checkout_fails_closed(self):
        code, out = self.run_gate(git_read=lambda *args, **kwargs: f"{self.BASE}\n2026-11-23\n")
        self.assertEqual(code, 2, out)
        self.assertIn("requires a two-parent merge commit", out)
        self.fetch.assert_not_called()

    def test_merge_with_wrong_second_parent_fails_closed(self):
        code, out = self.run_gate(pr_head="2" * 40)
        self.assertEqual(code, 2, out)
        self.assertIn("merge commit's second parent differs from the pinned PR head", out)
        self.fetch.assert_not_called()

    def test_repointed_row(self):
        self.ev["record_id"] = "ORG-T2"
        self.assert_held("proof record_id or claim_sha256 differs")
        self.fetch.assert_not_called()

    def test_edited_quote_or_claim(self):
        detail = self.ev["claim_detail"]
        for edited in (detail.replace("components", "parts"), detail.replace("automotive;", "medical;")):
            with self.subTest(edited=edited):
                self.ev["claim_detail"] = edited
                self.assert_held("proof record_id or claim_sha256 differs")
                self.fetch.assert_not_called()

    def test_edited_observation_date(self):
        self.ev["observed_date"] = "2026-11-22"
        self.assert_held("proof record_id or claim_sha256 differs")
        self.fetch.assert_not_called()

    def test_edited_tier_effect(self):
        self.ev["tier_effect"] = "supports_B"
        self.assert_held("proof record_id or claim_sha256 differs")
        self.fetch.assert_not_called()

    def website_fixture(self, quote="Acme Polymer operates at 12 Rubber Lane, Akron, OH 44301.",
                        *, website="https://acme.example/", source="https://locations.acme.example/akron", state="OH"):
        path = self.tree / "data/organizations_OH.csv"
        path.write_text(
            "org_id,legal_name,trade_names,website,hq_city,hq_state\n"
            f"ORG-T1,Acme Polymer,,{website},Akron,{state}\n"
            "ORG-T2,Acme Polymer II,,https://acmepolymer.example/,,\n")
        self.ev.update(source_ref=source, claim_detail=f"Akron location; quote: {quote}")
        self.capture = f"<main>{quote}</main>".encode()
        self.proof.update(capture=source, claim_sha256=b.claim_sha256(self.ev), quote_offset=0,
                          capture_sha256=hashlib.sha256(self.capture).hexdigest())

    def test_website_fill_without_evidence(self):
        self.website_fixture()
        self.ev["record_id"] = "ORG-T2"
        self.base_tables["evidence_*.csv"] = [self.ev.copy()]
        self.assert_held("no own-site evidence")
        self.fetch.assert_not_called()

    def test_website_fill_evidence_on_another_domain(self):
        self.website_fixture(source=self.SOURCE)
        self.assert_held("no same-domain own-site evidence")
        self.fetch.assert_not_called()

    def test_website_fill_quote_without_held_name(self):
        self.website_fixture("An unrelated company operates at 12 Rubber Lane, Akron, OH 44301.")
        self.assert_held("no same-domain quote contains a held name")
        self.fetch.assert_not_called()

    def test_website_fill_quote_without_ohio_locality(self):
        for quote in ("Acme Polymer makes plastic components.", "Acme Polymer operates in Akron, NY.",
                      "Acme Polymer operates in Akron, new york.", "Acme Polymer operates in Akron, ny.",
                      "Acme Polymer serves all of Ohio.", "Acme Polymer ships products to OH and PA."):
            with self.subTest(quote=quote):
                self.website_fixture(quote)
                self.assert_held("no held-name quote contains an Ohio locality")
                self.fetch.assert_not_called()

    def test_website_fill_held_proof(self):
        self.website_fixture()
        self.proof["verdict"] = "STILL_UNCERTAIN"
        self.assert_held("no own-site witness passed capture replay")
        self.fetch.assert_not_called()

    def test_website_fill_with_gate_held_observation(self):
        self.website_fixture()
        self.ev["observed_date"] = "2026-01-23"
        self.proof.update(claim_sha256=b.claim_sha256(self.ev), capture_date="2026-01-23", reader_date="2026-01-24")
        code, out = self.run_gate()
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"HELD +observed_date more than 30 days")
        self.assertIn("no own-site witness passed capture replay", out)
        self.fetch.assert_not_called()

    def test_website_fill_requires_ohio_footprint(self):
        self.website_fixture(state="NY")
        self.assert_held("no held Ohio headquarters or site")
        self.fetch.assert_not_called()

    def test_website_fill_with_replayed_live_proof(self):
        self.website_fixture()
        code, out = self.run_gate()
        self.assertEqual(code, 0, out)
        self.assertIn("1/1 website fills passed", out)
        self.fetch.assert_called_once_with(self.proof["capture"])

    def test_website_fill_rejects_other_tenant_of_public_namespace(self):
        for suffix in ("k12.oh.us", "blogspot.com", "org.ck"):
            with self.subTest(suffix=suffix):
                self.website_fixture(website=f"https://acme.{suffix}/", source=f"https://other.{suffix}/about")
                self.assert_held("no same-domain own-site evidence")
                self.fetch.assert_not_called()

    def test_website_fill_requires_the_cited_page(self):
        self.website_fixture()
        self.proof["capture"] = "https://locations.acme.example/about"
        self.assert_held("capture differs from the row's cited page")
        self.fetch.assert_not_called()

    def test_new_organization_website_with_replayed_proof(self):
        self.base_orgs = self.base_orgs[1:]
        self.website_fixture("Acme Polymer operates at 12 Rubber Lane, Hudson, Ohio.")
        code, out = self.run_gate()
        self.assertEqual(code, 0, out)
        self.assertIn("1/1 website fills passed", out)

    def test_website_fill_with_unchanged_evidence_in_base(self):
        self.website_fixture("Acme Polymer operates in Akron.")
        self.ev["observed_date"] = "2026-01-23"
        self.proof.update(claim_sha256=b.claim_sha256(self.ev), capture_date="2026-01-23", reader_date="2026-01-24")
        self.base_tables["evidence_*.csv"] = [self.ev.copy()]
        self.assert_held("no own-site witness passed capture replay")
        self.fetch.assert_not_called()
        code, out = self.run_gate(held_proof=True)
        self.assertEqual(code, 0, out)
        self.assertIn("1/1 website fills passed", out)
        self.fetch.assert_called_once_with(self.proof["capture"])

    def test_unchanged_blanked_or_none_found_website_needs_no_evidence(self):
        for website in ("https://acmepolymer.example/", "", "none_found"):
            with self.subTest(website=website):
                self.website_fixture(website=website)
                self.base_tables["evidence_*.csv"] = [self.ev.copy()]
                code, out = self.run_gate()
                self.assertEqual(code, 0, out)
                self.fetch.assert_not_called()

    def test_edited_website_cannot_be_used_for_proof(self):
        path = self.tree / "data/organizations_OH.csv"
        path.write_text(path.read_text().replace("acmepolymer.example", "other.example"))
        self.ev["source_ref"] = "https://other.example/about"
        self.proof.update(capture=self.ev["source_ref"], claim_sha256=b.claim_sha256(self.ev))
        self.assert_held("record website differs from base")
        self.fetch.assert_not_called()

    def test_record_absent_from_base_is_held(self):
        self.base_orgs = []
        code, out = self.run_gate()
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"HELD +record absent from base")
        self.fetch.assert_not_called()

    def test_short_quote_is_held(self):
        self.ev["claim_detail"] = "synthetic market claim; quote: Markets"
        self.proof.update(claim_sha256=b.claim_sha256(self.ev), quote_offset=0)
        self.assert_held("quote must contain at least 20 characters")
        self.fetch.assert_not_called()

    def test_live_capture_requires_https(self):
        self.ev["source_ref"] = self.SOURCE.replace("https://", "http://")
        self.proof.update(capture=self.ev["source_ref"], claim_sha256=b.claim_sha256(self.ev))
        self.assert_held("live capture must use HTTPS")
        self.fetch.assert_not_called()

    def test_gzip_capture_by_header_and_magic(self):
        raw = gzip.compress(self.CAPTURE)
        for encoding in ("gzip", "", "identity"):
            with self.subTest(encoding=encoding):
                self.assertEqual(b.decode_capture(raw, encoding), self.CAPTURE)
        with self.assertRaises(gzip.BadGzipFile):
            b.decode_capture(self.CAPTURE, "gzip")

    def test_gzip_capture_cannot_expand_past_byte_limit(self):
        with patch.object(b, "MAX_CAPTURE_BYTES", 64):
            raw = gzip.compress(b"x" * (b.MAX_CAPTURE_BYTES + 1))
            self.assertLess(len(raw), b.MAX_CAPTURE_BYTES)
            with self.assertRaisesRegex(ValueError, "decoded capture exceeds byte limit"):
                b.decode_capture(raw, "gzip")

    def test_fetch_rejects_redirects_before_reading_body(self):
        for status in (301, 302):
            with (
                self.subTest(status=status),
                patch.object(b.socket, "getaddrinfo", return_value=[(None, None, None, None, ("93.184.216.34", 443))]),
                patch.object(b.http.client, "HTTPSConnection") as connect,
            ):
                response = connect.return_value.getresponse.return_value.__enter__.return_value
                response.status = status
                with self.assertRaisesRegex(ValueError, f"capture returned HTTP {status}"):
                    b.fetch_url(self.SOURCE)
                connect.assert_called_once()
                response.read.assert_not_called()

    def test_quote_only_in_page_chrome(self):
        for tag in ("header", "nav", "footer"):
            with self.subTest(tag=tag):
                self.capture = f"<main><p>Markets</p><{tag}>{self.QUOTE}</{tag}></main>".encode()
                self.proof["capture_sha256"] = hashlib.sha256(self.capture).hexdigest()
                self.assert_held("not at that offset in the capture's main text")
        self.assertEqual(b.capture_text(b'<div role="main"><div>Markets</div> Industry</div>Outside'),
                         "Markets Industry")
        self.assertEqual(b.capture_text(b'<div role="contentinfo"><div>Nested</div>Footer</div>Body'), "Body")
        self.assertEqual(b.capture_text(b'<div id="site-footer">Footer</div><p>Body</p>'), "Body")

    def test_divi_body_and_empty_main_replay(self):
        for shell in (
            '<html class="site-header-shell"><body class="et_fixed_nav et_show_nav et_header_style_left">{}</body></html>',
            '<body><main> </main>{}</body>',
        ):
            with self.subTest(shell=shell):
                self.capture = shell.format(
                    f"<header>Site Header</header><p>{self.QUOTE}</p><footer>Site Footer</footer>"
                ).encode()
                self.proof.update(capture_sha256=hashlib.sha256(self.capture).hexdigest(), quote_offset=0)
                code, out = self.run_gate()
                self.assertEqual(code, 0, out)
                self.assertIn("1 PASS", out)

    def test_empty_capture_cannot_replay(self):
        self.capture = f'<body><main> </main><footer>{self.QUOTE}</footer></body>'.encode()
        self.proof.update(capture_sha256=hashlib.sha256(self.capture).hexdigest(), quote_offset=0)
        self.assert_held("not at that offset in the capture's main text")

    def test_capture_digest_mismatch(self):
        self.capture += b"\n"
        self.assert_held("capture_sha256 does not match")

    def test_fetch_failure(self):
        self.fetch_error = TimeoutError("planted timeout")
        for mode in ("--new-since", "--verify-proofs"):
            with self.subTest(mode=mode):
                self.assert_held("could not inspect capture: planted timeout", mode=mode)
                self.fetch.assert_called_once()

    def test_archived_market_capture_older_than_two_years(self):
        self.archive("20241122000000")
        self.assert_held("outside the two years ending on observed_date")
        self.fetch.assert_not_called()

    def test_archived_existence_capture_older_than_two_years(self):
        self.ev.update(claim_type="existence", claim_detail=f"company existence; quote: {self.QUOTE}")
        self.proof["claim_sha256"] = b.claim_sha256(self.ev)
        self.archive("20130601000000")
        self.assert_held("outside the two years ending on observed_date")
        self.fetch.assert_not_called()

    def test_capture_off_record_website(self):
        self.proof["capture"] = "https://other.example/about"
        self.assert_held("capture not_own_site")
        self.fetch.assert_not_called()

    def test_duplicate_archive_evidence_id(self):
        self.archive("20261122000000", duplicate=True)
        self.assert_held("duplicate archive evidence_id EVD-T1")
        self.fetch.assert_not_called()

    def test_invalid_utf8_in_the_proof_file(self):
        self.assert_held("invalid UTF-8", proof_bytes=(",".join(b.PROOF_COLS) + "\n").encode() + b"\xff")
        self.fetch.assert_not_called()

    def test_same_family_reading_is_held(self):
        self.proof["reader_family"] = "OpenAI"
        self.assert_held("different known model families")
        self.fetch.assert_not_called()

    def test_web_street_unit_conflict_outranks_proof(self):
        (self.tree / "data/sites_OH.csv").write_text(
            "site_id,org_id,site_name,street_address\nSITE-T1,ORG-T1,Acme Polymer,52 Basin Rd Suite 22\n")
        self.ev.update(record_table="sites", record_id="SITE-T1", claim_type="address",
                       claim_detail="street; quote: Acme Polymer operates at 52 Basin Rd Suite 31.")
        self.proof.update(record_id="SITE-T1", claim_sha256=b.claim_sha256(self.ev))
        self.assert_held("unit_differs")
        self.fetch.assert_not_called()

    def test_private_capture_address_is_refused_before_connecting(self):
        with patch.object(b.socket, "getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 443))]), \
                patch.object(b.http.client, "HTTPSConnection") as connect:
            with self.assertRaisesRegex(ValueError, "public unicast"):
                b.fetch_url(self.SOURCE)
            connect.assert_not_called()


@unittest.skipUnless(has_commits("6a76e923", "17834918"), "known-answer commits not in this clone (CI fetches all)")
class KnownAnswer(unittest.TestCase):
    """Batch 6 (PR #458, 6a76e923..17834918) added 23,564 rows with every check green; this gate must block it."""

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = b.main(list(args))
        return code, out.getvalue()

    def test_batch6_is_blocked(self):
        code, out = self.run_main("--new-since", "6a76e923", "--head", "17834918")
        self.assertEqual(code, 1)
        self.assertIn("23564 rows added or changed", out)
        self.assertIn("HELD, READ_REQUIRED or UNINSPECTABLE", out)

    def test_batch6_has_no_provenance_folder(self):
        code, out = self.run_main("--provenance-since", "6a76e923", "--head", "17834918")
        self.assertEqual(code, 1)
        self.assertIn("MISSING tasks/spaghetti-batch6-2026-11-22/check.py for created_by 'spaghetti-batch6-2026-11-22' "
                      "(23564 rows)", out)

    def test_fleet_services_row_still_fails(self):  # owner ruling 2026-11-22: the real EVD-455899 stays FAIL
        evs = {e["evidence_id"]: e for e in b.rows("17834918", "evidence_*.csv")}
        self.assertEqual(b.judge(evs["EVD-455899"], b.Index.load("17834918"))[:2], ("FAIL", "name_not_held"))

    def test_building_number_row_does_not_pass(self):  # Codex 3: the real row the #463 guard holds
        evs = {e["evidence_id"]: e for e in b.rows("17834918", "evidence_*.csv")}
        v, why, _ = b.judge(evs["EVD-431716"], b.Index.load("17834918"))
        self.assertEqual((evs["EVD-431716"]["record_id"], v, why), ("SITE-002988", "UNINSPECTABLE", "no_civic_number"))


class G8Routes(unittest.TestCase):
    def setUp(self):
        self.org = dict(org_id="O", legal_name="Harbor + Reed Materials LLC", hq_city="Cleveland", hq_state="OH")
        self.site = dict(site_id="S", org_id="O", city="Valley View", state="OH", zip="44125", county="Cuyahoga",
                         street_address="")

    def verdict(self, quote, *, ref="EPA ECHO RCRAInfo", cls="registry", claim="existence",
                table="sites", other=()):
        idx = b.Index([self.site], [self.org, *other])
        return b.judge(ev("S" if table == "sites" else "O", ref, quote, claim, table, cls=cls), idx)[:2]

    def test_registry_variant_and_blank_street(self):
        q = "facility_name: Harbor & Reed Materials, Inc.; address: 16 Canal Rd, Valley View, OH 44125; county: Cuyahoga"
        self.assertEqual(self.verdict(q), ("PASS", "registry_variant+blank_street_registry"))
        for old, new in (("Materials", "Material"), ("Valley View", "Cleveland"), ("44125", "44126"),
                         ("Cuyahoga", "Summit")):
            with self.subTest(old=old):
                self.assertNotEqual(self.verdict(q.replace(old, new))[0], "PASS")
        self.assertNotEqual(self.verdict(q, claim="scope")[0], "PASS")

    def test_postal_city_requires_exact_street_zip_and_county(self):
        self.site["street_address"] = "16 Canal Road"
        q = "facility_name: Harbor and Reed Materials LLC; address: 16 Canal Rd, Cleveland, OH 44125; county: Cuyahoga"
        self.assertEqual(self.verdict(q), ("PASS", "registry_variant+mailing_city"))
        for old, new in (("16 ", "18 "), ("44125", "44126"), ("Cuyahoga", "Summit"), ("Cleveland", "Akron")):
            with self.subTest(old=old):
                self.assertNotEqual(self.verdict(q.replace(old, new))[0], "PASS")

    def test_press_dateline_only_admits_existence_after_replay(self):
        q = "Cleveland, OH – Harbor and Reed Materials LLC announced a new facility on Friday."
        kwargs = dict(ref="https://rubberworld.com/example/", cls="press", table="organizations")
        self.assertEqual(self.verdict(q, **kwargs), ("READ_REQUIRED", "press_dateline"))
        self.assertNotEqual(self.verdict(q, claim="address", **kwargs)[1], "press_dateline")
        self.assertNotEqual(self.verdict(q.replace("Cleveland", "Akron"), **kwargs)[1], "press_dateline")

    def test_kent_wrapper_keeps_body_and_strips_chrome(self):
        data = (b'<div id="page" class="header-util-ct-3"><div class="site-header">Navigation</div>'
                b'<main>Facility Details</main><footer>Footer</footer></div>')
        self.assertEqual(b.capture_text(data), "Facility Details")
        self.assertEqual(b.capture_text(data.replace(b"<main>", b"<p>").replace(b"</main>", b"</p>")),
                         "Facility Details")

    def test_ita_prefix_is_unique_and_has_a_held_site(self):
        prefix = "Coastal Advanced Industrial Compounds Group"
        self.assertEqual(len(prefix), 43)
        self.org.update(legal_name=prefix + " Ohio, Inc.", hq_city="Valley View")
        self.site["street_address"] = "16 Canal Road"
        quote = f"company_name: {prefix}; establishment_name: Valley View Office; address: 16 Canal Rd, Valley View, OH 44125"
        kwargs = dict(ref="OSHA ITA CY2021 establishment id 123", table="organizations")
        self.assertEqual(self.verdict(quote, **kwargs), ("PASS", "ita_cy2021_unique_prefix_and_establishment"))
        other = dict(self.org, org_id="OTHER", legal_name=prefix + " Texas, Inc.")
        self.assertNotEqual(self.verdict(quote, other=[other], **kwargs)[0], "PASS")
        self.assertNotEqual(self.verdict(quote.replace(prefix, prefix[:-1]), **kwargs)[0], "PASS")
        self.assertNotEqual(self.verdict(quote.replace("16 Canal", "17 Canal"), **kwargs)[0], "PASS")

    def replay(self, row, capture, quote, text, idx):
        row.update(observed_date="2026-11-23", tier_effect="supports_C")
        original = row["source_ref"].removeprefix("SEC EDGAR ")
        proof = dict(record_id=row["record_id"], claim_sha256=b.claim_sha256(row), verdict="VERIFIED",
                     reader_family="Gemini", reader_date="2026-11-23", capture=original, capture_date="2026-11-23",
                     capture_sha256=hashlib.sha256(capture).hexdigest(), quote_offset=str(text.index(quote)))
        observed = b.proof_date(row["observed_date"])
        return b.proof_problem(proof, row, idx, idx, None, observed, "codex", lambda _: capture)

    def test_press_replay_requires_publication_date(self):
        idx = b.Index([], [self.org])
        quote = "Cleveland, OH – Harbor and Reed Materials LLC announced a new facility on Friday."
        row = ev("O", "https://rubberworld.com/example/", quote, table="organizations", cls="press")
        html = f'<head><meta property="article:published_time" content="2025-10-14T05:38:00-04:00"></head><main>{quote}</main>'
        self.assertEqual(self.replay(row, html.encode(), quote, quote, idx), "")
        self.assertIn("publication date", self.replay(row, f"<main>{quote}</main>".encode(), quote, quote, idx))

    def test_edgar_submissions_and_full_filing_require_held_cik(self):
        self.site.update(street_address="16 Canal Road", site_type="hq_only")
        link = dict(org_id="O", registry="SEC_CIK", registry_id="0000123456")
        idx = b.Index([self.site], [self.org], links=[link])
        address = dict(street1="16 CANAL RD", street2=None, city="CLEVELAND", stateOrCountry="OH", zipCode="44125")
        quote = json.dumps(address)
        capture = json.dumps(dict(cik="0000123456", addresses=dict(business=address)))
        source = "https://data.sec.gov/submissions/CIK0000123456.json"
        row = ev("S", source, quote, claim="address", cls="government_filing")
        self.assertEqual(b.judge(row, idx)[:2], ("READ_REQUIRED", "sec_edgar"))
        self.assertEqual(self.replay(row, capture.encode(), quote, capture, idx), "")
        wrong = capture.replace("0000123456", "0000123457")
        self.assertIn("linked filer", self.replay(row, wrong.encode(), quote, wrong, idx))
        row["source_ref"] = source.replace("123456", "123457")
        self.assertIn("sole held CIK", self.replay(row, wrong.encode(), quote, wrong, idx))

        business = "\t\tSTREET 1: 16 CANAL RD\n\t\tCITY: CLEVELAND\n\t\tSTATE: OH\n\t\tZIP: 44125\n"
        filing = ("<SEC-HEADER>\nFILER:\n\tCOMPANY DATA:\n\t\tCENTRAL INDEX KEY: 0000123456\n"
                  "\tBUSINESS ADDRESS:\n" + business + "</SEC-HEADER>")
        quote = b.norm_space(business)
        src = "SEC EDGAR https://www.sec.gov/Archives/edgar/data/123456/000012345626000001/0000123456-26-000001.txt"
        row = ev("S", src, quote, claim="address", cls="government_filing")
        self.assertEqual(b.judge(row, idx)[:2], ("READ_REQUIRED", "sec_edgar"))
        self.assertEqual(self.replay(row, filing.encode(), quote, b.norm_space(filing), idx), "")
        wrong = filing.replace("0000123456", "0000123457")
        self.assertIn("linked filer", self.replay(row, wrong.encode(), quote, b.norm_space(wrong), idx))


class V120Routes(unittest.TestCase):
    def setUp(self):
        self.org = dict(org_id="O", legal_name="C4 Harbor Polymers LLC", trade_names="")
        self.site = dict(site_id="S", org_id="O", city="Valley View", state="OH", zip="44125",
                         street_address="", notes="")
        self.head_site = dict(self.site, street_address="160 OH-45")
        self.head_org = dict(self.org)
        self.filing = ev("S", "OSHA inspection activity_nr 300000001",
                         "C4 Harbor Polymers LLC, 160 SR 45, Valley View, OH 44125",
                         claim="address", eid="EVD-000001", cls="government_filing")
        self.filing["address_role"] = "physical"
        self.base_evidence = [self.filing]
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = Path(tmp.name)

    def map_row(self, *, provider="google-places", name=None, city="Valley View", street="160 OH-45"):
        name = name or self.org["legal_name"]
        if provider == "google-places":
            raw = dict(id="placeABC", displayName={"text": name},
                       postalAddress=dict(regionCode="US", administrativeArea="OH",
                                          locality=city, addressLines=[street]))
        else:
            raw = dict(type="Feature", id="placeABC",
                       properties=dict(theme="places", type="place", names={"primary": name},
                                       addresses=[dict(freeform=street, locality=city, region="US-OH", country="US")]))
        body = json.dumps(raw).encode()
        digest = hashlib.sha256(body).hexdigest()
        path = self.store / "raw" / "map-listings" / provider / (digest + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        row = ev("S", f"{provider} placeABC", None, claim="address", cls="platform_category", eid="EVD-000002")
        detail = f"{street}; quote: name: {name}; street: {street}; city: {city}; state: OH"
        row.update(claim_detail=detail, address_role="", tier_effect="supports_C",
                   notes=f"capture_sha256: {digest}; second_source: EVD-000001")
        return row, path

    def run_gate(self, *evs, parents=(), replay=False):
        base = b.Index([self.site], [self.org, *parents])
        head = b.Index([self.head_site], [self.head_org, *parents])
        out = io.StringIO()

        def rows(ref, table):
            if table == "archive_links.csv":
                return []
            return self.base_evidence if ref == "base" else [*self.base_evidence, *evs]

        with (patch.object(b, "resolve_base", return_value="base"),
              patch.object(b, "rows", side_effect=rows),
              patch.object(b.Index, "load", side_effect=lambda ref=None: base if ref == "base" else head),
              contextlib.redirect_stdout(out)):
            status = b.main(["--verify-proofs", "base"] + (["--map-store", str(self.store)] if replay else []))
        return status, out.getvalue()

    def test_replayed_listing_and_held_filing_agree_on_route(self):
        for provider in ("google-places", "overture-maps-places"):
            with self.subTest(provider=provider):
                row, _ = self.map_row(provider=provider)
                for replay in (False, True):
                    status, output = self.run_gate(row, replay=replay)
                    self.assertEqual(status, 0, output)
                    self.assertIn("map_listing_street_bound", output)

    def test_listing_defects_block_admission(self):
        for change, reason in [
            ({"name": "Other Operator"}, "map_operator_not_held"),
            ({"city": "Cleveland"}, "map_city_or_state_differs"),
            ({"street": "161 OH-45"}, "map_second_street_differs"),
            ({"street": "160 OH-46"}, "map_second_street_differs"),
        ]:
            with self.subTest(change=change):
                row, _ = self.map_row(**change)
                self.head_site["street_address"] = row["claim_detail"].partition(";")[0]
                status, output = self.run_gate(row)
                self.assertEqual(status, 1, output)
                self.assertIn(reason, output)
        self.head_site["street_address"] = "160 OH-45"
        row, path = self.map_row()
        for change, reason in [
            ({"address_role": "mailing"}, "map_address_role"),
            ({"tier_effect": "supports_B"}, "map_claim_or_ceiling"),
            ({"claim_detail": row["claim_detail"].replace("160 OH-45;", "999 Main St;", 1)}, "map_street_not_filled_as_listed"),
        ]:
            with self.subTest(change=change):
                status, output = self.run_gate(dict(row, **change))
                self.assertEqual(status, 1, output)
                self.assertIn(reason, output)
        self.site["street_address"] = "160 SR 45"
        self.assertIn("map_base_street_already_held", self.run_gate(row)[1])
        self.site["street_address"] = ""
        self.filing["address_role"] = "mailing"
        self.assertIn("map_second_source_unbound", self.run_gate(row)[1])
        self.filing["address_role"] = "physical"
        for body in (b"invalid", None):
            if body is None:
                path.unlink()
            else:
                path.write_bytes(body)
            status, output = self.run_gate(row, replay=True)
            self.assertEqual(status, 1, output)
            self.assertIn("map_capture_unreplayable", output)

    def test_listing_requires_an_independent_base_lead(self):
        row, _ = self.map_row()
        for origin, reason in [
            ("Ohio EPA", "map_listing_street_bound"),
            ("2026-11-14 Google Maps scrape", "map_second_source_same_provider"),
            ("unknown discovery", "map_second_source_unknown_origin"),
        ]:
            with self.subTest(origin=origin):
                lead = f"Street (per {origin}): 160 State Route 45"
                self.site["notes"] = lead
                proposal = dict(row, notes=row["notes"].replace("EVD-000001", f"lead: {lead}"))
                status, output = self.run_gate(proposal)
                self.assertEqual(status, 0 if origin == "Ohio EPA" else 1, output)
                self.assertIn(reason, output)
        self.site["notes"] = ""
        self.head_site["notes"] = lead
        self.assertIn("map_second_source_unbound", self.run_gate(proposal)[1])

    def test_listing_reuses_the_dated_epa_frs_note_shape(self):
        row, _ = self.map_row()
        lead = ("Address 2026-10-28 (gov-data pipeline, EPA FRS facility 123456789012, STRONG match): "
                "160 State Route 45, Valley View, OH 44125")
        self.site["notes"] = lead + " (the sites schema has no street column, so the street address is recorded here)."
        row["notes"] = row["notes"].replace("EVD-000001", f"lead: {lead}")
        status, output = self.run_gate(row)
        self.assertEqual(status, 0, output)
        self.assertIn("map_listing_street_bound", output)

    def test_own_site_witness_requires_the_held_domain_and_street(self):
        row, _ = self.map_row()
        self.org["website"] = self.head_org["website"] = "https://example.com"
        self.filing.update(source_class="own_site", source_ref="https://example.com/contact",
                           claim_detail="quote: Address 160 State Route 45, Valley View, OH 44125")
        status, output = self.run_gate(row)
        self.assertEqual(status, 0, output)
        self.filing["source_ref"] = "https://unrelated.example"
        self.assertIn("map_second_source_unbound", self.run_gate(row)[1])

    def variant(self, label="C 4 Harbor Polymers Manufacturing Company", agency="OSHA"):
        self.site["street_address"] = self.head_site["street_address"] = "160 OH-45"
        source = ("OSHA inspection activity_nr 300000001" if agency == "OSHA"
                  else "EPA ECHO RCRAInfo handler XXR000000001")
        addr = "160 State Route 45, Valley View, OH 44125"
        quote = f"{label}, {addr}" if agency == "OSHA" else f"{label}; {addr}; facility record"
        row = ev("O", source, quote, table="organizations", eid="EVD-000002", cls="government_filing")
        self.head_org["trade_names"] = marker = f"{label} ({agency} filing name)"
        row["claim_detail"] = f"trade_names + {marker}; quote: {quote}"
        return row

    def test_filing_variant_positive_for_both_agencies(self):
        for agency in ("OSHA", "EPA"):
            with self.subTest(agency=agency):
                status, output = self.run_gate(self.variant(agency=agency))
                self.assertEqual(status, 0, output)
                self.assertIn("filing_name_variant_bound", output)

    def test_filing_variant_rejects_parent_and_missing_word(self):
        for label, reason in [
            ("C 4 Harbor Polymers Manufacturing Company", "filing_variant_parent_name"),
            ("C 4 Harbor Manufacturing Company", "filing_variant_distinctive_words_missing"),
        ]:
            with self.subTest(label=label):
                row = self.variant(label)
                self.org["parent_org_id"] = "P"
                parent = dict(org_id="P", legal_name="C4 Harbor Polymers Manufacturing LLC")
                status, output = self.run_gate(row, parents=[parent])
                self.assertEqual(status, 1, output)
                self.assertIn(reason, output)

    def test_filing_variant_rejects_unheld_street_mail_and_private_names(self):
        row = self.variant()
        detail = row["claim_detail"]
        for old, new in [("Route 45", "Route 46"), ("Valley View", "Cleveland"), ("160 State Route 45", "PO Box 16")]:
            with self.subTest(new=new):
                status, output = self.run_gate(dict(row, claim_detail=detail.replace(old, new)))
                self.assertEqual(status, 1, output)
        self.site["street_address"] = ""
        self.assertIn("filing_variant_site_not_held", self.run_gate(row)[1])
        self.org["legal_name"] = "Jane Example"
        row = self.variant("Jane Example LLC")
        status, output = self.run_gate(row)
        self.assertEqual(status, 1, output)
        self.assertIn("filing_variant_private_address_screen", output)

    def test_marked_alias_cannot_bypass_gate_without_evidence(self):
        self.variant()
        status, output = self.run_gate()
        self.assertEqual(status, 1, output)
        self.assertIn("filing variant addition has no matching evidence row", output)


class OhioRouteStreets(unittest.TestCase):
    def test_state_route_spellings_in_both_directions(self):
        for form in ("160 OH-45", "160 SR 45", "160 State Route 45"):
            with self.subTest(form=form):
                self.assertTrue(b.same_street("160 OH-45", form))
                self.assertTrue(b.same_street(form, "160 OH-45"))
                self.assertFalse(b.same_street("160 OH-46", form))
                self.assertFalse(b.same_street(form, "160 OH-46"))
                self.assertFalse(b.same_street("160 US-45", form))
        self.assertFalse(b.same_street("OH-45", "SR 45"))


class LinkedInCompanyRoute(unittest.TestCase):
    """SCHEMA §4.13 `linkedin_company`: one closed labelled field of the subject's own About section, read only in the label-line/value-line layout,
    in a capture the row names by sha256. Synthetic only; the capture shape is the one of the reviewed Muse package."""
    URL = "https://www.linkedin.com/company/harbor-plastics"
    TITLE = "[1] Harbor Plastics, Inc. | LinkedIn (" + URL + ")"
    INTRO = "Harbor Plastics molds engineered thermoplastic parts for packaging."
    PAIRS = (("Website", ""), ("Industry", "Plastics Manufacturing"), ("Company size", "5,001-10,000 employees"), ("Headquarters", "Cleveland, Ohio"),
             ("Type", "Privately Held"), ("Founded", "1986"), ("Specialties", "Injection molding, Thermoforming, Extrusion"))

    def about_page(self, *blocks, title=None, extra=""):
        """A capture whose About section is exactly `blocks` (paragraphs, a multi-line string is one paragraph) separated by blank lines."""
        return ((title or self.TITLE) + "\nPage crawled less than a minute ago (2026-11-25 14:32 UTC).\n## Plastics Manufacturing\n\n## About us\n\n" + "\n\n".join(blocks)
                + "\n\n## Locations\n\n## Updates\n\n## Similar pages\n\nOther Chemical Co\n\nChemical Manufacturing in Dayton, Ohio\n" + extra)

    def pairs(self, **change):
        return [x for label, value in self.PAIRS for x in (label, change.get(label, value)) if x != ""] if not change else [
            x for label, value in self.PAIRS for x in ((label, change[label]) if label in change else (label, value)) if x != ""]

    def page(self, title=None, intro=None, drop=(), extra="", **change):
        blocks = [intro or self.INTRO]
        for label, value in self.PAIRS:
            if label in drop:
                continue
            blocks += [label] + [change.get(label, value)] * (label in change or value != "") if False else [label, change.get(label, value)] if (label in change or value) else [label]
        return self.about_page(*blocks, title=title, extra=extra)

    def setUp(self):
        self.idx = b.Index(SITES, ORGS)
        self.store = Path(tempfile.mkdtemp(prefix="li-store-"))
        (self.store / "raw/linkedin").mkdir(parents=True)

    def capture(self, text=None):
        data = (self.page() if text is None else text).encode()
        digest = hashlib.sha256(data).hexdigest()
        (self.store / f"raw/linkedin/{digest}.txt").write_bytes(data)
        return digest

    def row(self, head="industry: Plastics Manufacturing", quote="Industry, Plastics Manufacturing", claim="activity", rid="ORG-1", url=None, table="organizations", digest=None):
        r = ev(rid, url or self.URL, "", claim, table, cls="linkedin_company")
        r["claim_detail"] = f"{head}; quote: {quote}"
        r["notes"] = f"capture_sha256: {digest}; acquisition: guest" if digest else ""
        return r

    def inputs(self, *digests):
        body = "".join(f"{d}  raw/linkedin/{d}.txt\n" for d in digests).encode()
        return lambda path: body if path == "tasks/test/INPUTS.sha256" else None

    def replay(self, row, *named, store="default"):
        result = dict(evidence_id=row["evidence_id"], reason="linkedin_needs_capture", verdict="HELD")
        b.check_linkedin_routes([result], {row["evidence_id"]: row}, self.idx, self.store if store == "default" else store, self.inputs(*named))
        return result["verdict"], result["reason"]

    def run_row(self, text=None, **kw):
        digest = self.capture(text)
        return self.replay(self.row(digest=digest, **kw), digest)

    def test_floor_fails_profile_site_grain_claim_and_personal_data(self):
        cases = {
            "profile URL": (self.row(url="https://www.linkedin.com/in/some-person"), "linkedin_profile"),
            "old public profile URL": (self.row(url="https://www.linkedin.com/pub/some-person/1/2/3"), "linkedin_profile"),
            "upper-case profile path": (self.row(url="https://www.linkedin.com/IN/some-person"), "linkedin_profile"),
            "not a LinkedIn company page": (self.row(url="https://example.org/company/harbor"), "linkedin_not_company_page"),
            "staff list under the company": (self.row(url=self.URL + "/people"), "linkedin_not_company_page"),
            "query string on the page URL": (self.row(url=self.URL + "?trk=x"), "linkedin_not_company_page"),
            "http not https": (self.row(url=self.URL.replace("https", "http")), "linkedin_not_company_page"),
            "site-grain claim": (self.row(rid="S-CARN", table="sites"), "linkedin_not_org_grain"),
            "claim type not org grain": (self.row(claim="parent"), "linkedin_claim_not_allowed"),
            "address claim that is not the HQ city": (self.row(head="street address", claim="address"), "linkedin_address_not_hq_city"),
            "hq_city with a county": (self.row(head="hq_city + hq_county (Summit)", quote="Cleveland, Summit County", claim="address"), "linkedin_address_not_hq_city"),
            "hq_city with a street in the quote": (self.row(head="hq_city Cleveland", quote="Headquarters, 123 Main Street, Cleveland, Ohio 44301", claim="address"), "linkedin_address_not_hq_city"),
            "Ohio band from a company-wide size": (self.row(head="employee_band_ohio 50-99 (self-declared)", quote="Company size, 51-200 employees", claim="size_band"), "linkedin_size_not_organization_wide"),
            "size band not named self-declared": (self.row(head="employee_band_global 5000+", quote="Company size, 5,001-10,000 employees", claim="size_band"), "linkedin_size_band_not_named_self_declared"),
            "band from a straddling bracket": (self.row(head="employee_band_global 1000-4999 (self-declared)", quote="Company size, 1,001-5,000 employees", claim="size_band"), "linkedin_size_bracket_straddles_band"),
            "band from 0-1": (self.row(head="employee_band_global 1-9 (self-declared)", quote="Company size, 0-1 employees", claim="size_band"), "linkedin_size_bracket_straddles_band"),
            "email in the quote": (self.row(quote="Industry, Plastics Manufacturing info@harbor.example"), "linkedin_personal_data"),
            "parenthesised role": (self.row(quote="Industry, Plastics Manufacturing; Jane Smith (CEO)"), "linkedin_personal_data"),
            "wrong bracket as the witness": (self.row(head="linkedin_size_bracket 5,001-10,000 (self-declared)", quote="Company size, 51-200 employees", claim="size_band"), "linkedin_size_bracket_not_in_quote"),
            "Company size alone": (self.row(head="linkedin_size_bracket 5,001-10,000 (self-declared)", quote="Company size", claim="size_band"), "linkedin_size_quote_has_no_bracket"),
            "inverted bracket claim": (self.row(head="linkedin_size_bracket 51-20 (self-declared)", quote="Company size, 51-20 employees", claim="size_band"), "linkedin_size_bracket_not_in_quote"),
            "inverted bracket as a band": (self.row(head="employee_band_global 10-49 (self-declared)", quote="Company size, 51-20 employees", claim="size_band"), "linkedin_size_bracket_straddles_band"),
        }
        for n, tail in enumerate(("Jane Smith, CEO", "CEO Jane M. Smith", "CEO Jane O'Connor", "CEO Mary-Jane Smith", "ceo Jane Smith", "CEO José García", "Plant Manager Robert Lee",
                                  "Managing Director Robert Lee", "founded by Robert Lee", "Call (216)555-0100", "Call 2165550100", "Call +1 216 555 0100", "Contact: Jane Smith")):
            cases[f"personal data {n}: {tail}"] = (self.row(quote="Industry, Plastics Manufacturing " + tail), "linkedin_personal_data")
        for name, (row, reason) in cases.items():
            with self.subTest(name):
                self.assertEqual(b.judge(row, self.idx)[:2], ("FAIL", reason))

    def test_every_judge_return_carries_its_detail_through_judge_all(self):
        rows = [self.row(claim="size_band", head="linkedin_size_bracket 5,001-10,000 (self-declared)", quote="Company size, 5,001-10,000 employees"),  # valid control
                self.row(claim="size_band", head="linkedin_size_bracket 5,001-10,000 (self-declared)", quote="Company size"),
                self.row(claim="size_band", head="linkedin_size_bracket 5,001-10,000 (self-declared)", quote="Company size, 51-200 employees"),
                self.row(claim="size_band", head="employee_band_global 1000-4999 (self-declared)", quote="Company size, 1,001-5,000 employees"),
                self.row(head="specialties: Extrusion", quote="Specialties, Extrusion")]
        for n, r in enumerate(rows):
            r["evidence_id"] = f"EVD-L{n}"
        out = {r["evidence_id"]: (r["verdict"], r["reason"]) for r in b.judge_all(rows, self.idx)}  # a three-value unpack error would lose the whole batch
        self.assertEqual(out, {"EVD-L0": ("HELD", "linkedin_needs_capture"), "EVD-L1": ("FAIL", "linkedin_size_quote_has_no_bracket"),
                               "EVD-L2": ("FAIL", "linkedin_size_bracket_not_in_quote"), "EVD-L3": ("FAIL", "linkedin_size_bracket_straddles_band"),
                               "EVD-L4": ("HELD", "linkedin_specialties_needs_reading")})

    def test_generic_title_cased_copy_is_not_personal_data(self):
        for tail in ("Contact Us Today", "Director Operations Manager", "Customer Service Manager Support Team", "Our Founder Story Page"):
            self.assertEqual(b.judge(self.row(quote="Industry, Plastics Manufacturing " + tail), self.idx)[:2], ("HELD", "linkedin_needs_capture"), tail)

    def test_a_free_description_is_held_for_reading_never_passed_by_machine(self):
        row = self.row(head="what the page says the company does", quote="Harbor Plastics molds engineered thermoplastic parts for packaging.")
        self.assertEqual(b.judge(row, self.idx)[:2], ("HELD", "linkedin_description_needs_reading"))

    def test_each_closed_field_replays_and_specialties_never_passes_by_machine(self):
        spec = {
            "industry": self.row(),
            "founded": self.row(head="founded: 1986", quote="Founded, 1986", claim="existence"),
            "size band 5000+": self.row(head="employee_band_global 5000+ (self-declared)", quote="Company size, 5,001-10,000 employees", claim="size_band"),
            "size bracket": self.row(head="linkedin_size_bracket 5,001-10,000 (self-declared)", quote="Company size, 5,001-10,000 employees", claim="size_band"),
        }
        digest = self.capture()
        for name, row in spec.items():
            with self.subTest(name):
                row["notes"] = f"capture_sha256: {digest}; acquisition: guest"
                self.assertEqual(self.replay(row, digest), ("PASS", "linkedin_company_replayed"))
        row = self.row(digest=digest, head="specialties: Extrusion", quote="Specialties, Injection molding, Thermoforming, Extrusion")
        self.assertEqual(b.judge(row, self.idx)[:2], ("HELD", "linkedin_specialties_needs_reading"))  # held at the floor, so the replay never runs
        self.assertEqual(self.replay(row, digest), ("HELD", "linkedin_specialties_needs_reading"))

    def test_the_layout_is_closed_and_a_label_word_elsewhere_is_never_a_label(self):
        jane = "Our managing director is Jane Example."
        flat = "Industry, Plastics Manufacturing, Company size, 51-200 employees, Headquarters, Cleveland, Ohio, Type, Privately Held, Founded, 1986, Specialties"
        cases = {
            "a name on the line after a value": (self.page(Industry="Plastics Manufacturing\n" + jane), dict(), "linkedin_field_ambiguous"),
            "a name on the line after Founded": (self.page(Founded="1986\n" + jane), dict(head="founded: 1986", quote="Founded, 1986", claim="existence"), "linkedin_field_ambiguous"),
            "the flattened one-line layout": (self.about_page(self.INTRO, "Website", flat), dict(), "linkedin_field_not_in_line_layout"),
            "Automotive Industry inside Specialties, no Industry field": (self.page(drop=("Industry",), Specialties="Rubber Products, Automotive Industry, Extrusion"),
                                                                           dict(head="industry: Extrusion", quote="Industry, Extrusion"), "linkedin_field_not_in_line_layout"),
            "subsidiary industry in prose, no Industry field": (self.page(drop=("Industry",), intro="Harbor Films, our subsidiary: Industry, Plastic Films."),
                                                                dict(head="industry: Plastic Films", quote="Industry, Plastic Films"), "linkedin_field_not_in_line_layout"),
            "a label that appears twice": (self.about_page(self.INTRO, "Industry", "Plastics Manufacturing", "Industry", "Resin Compounding"), dict(), "linkedin_field_ambiguous"),
            "a second About section repeating the label": (self.page(extra="").replace("## Locations", "## About us\n\nIndustry\n\nResin Compounding\n\n## Locations"), dict(), "linkedin_field_ambiguous"),
        }
        for name, (page, kw, reason) in cases.items():
            with self.subTest(name):
                self.assertEqual(self.run_row(page, **kw), ("HELD", reason))
        l_lines = ("[1] Harbor Plastics, Inc. | LinkedIn (" + self.URL + ")\nL0: ## Plastics Manufacturing\nL2: ## About us\nL4: " + self.INTRO + "\nL6: Website\nL8:\nL10: Industry\n"
                   "L12: Plastics Manufacturing\nL14: Company size, 51-200 employees, Headquarters, Cleveland, Ohio\nL16: ## Locations\n")
        self.assertEqual(self.run_row(l_lines), ("PASS", "linkedin_company_replayed"))  # the `L<n>:` capture: a gap in the numbers is a paragraph break
        consecutive = l_lines.replace("L12: Plastics Manufacturing\nL14:", "L12: Plastics Manufacturing\nL13: Our managing director is Jane Example.\nL15:")
        self.assertEqual(self.run_row(consecutive), ("HELD", "linkedin_field_ambiguous"))

    def test_the_quote_is_exactly_one_labelled_field_as_the_capture_shows_it(self):
        bad = {
            "prose before the field (Jane Example)": "Our managing director is Jane Example. Industry, Plastics Manufacturing",
            "prose after the field": "Industry, Plastics Manufacturing, Company size",
            "a second field in the quote": "Industry, Plastics Manufacturing, Company size, 5,001-10,000 employees",
            "all-uppercase quote": "INDUSTRY, PLASTICS MANUFACTURING",
            "value differs from the field": "Industry, Chemical Manufacturing",
            "short quote": "Industry",
        }
        for name, quote in bad.items():
            with self.subTest(name):
                self.assertEqual(self.run_row(quote=quote), ("FAIL", "linkedin_quote_not_exact_field"))
        self.assertEqual(self.run_row(self.page(Industry="Plastics Manufacturing "), quote="Industry,  Plastics Manufacturing"), ("PASS", "linkedin_company_replayed"))  # whitespace is normalized

    def test_each_field_value_is_closed(self):
        cases = {
            "industry not in LinkedIn's published list": (self.page(Industry="Plastic Fabrication Magic"), dict(head="industry: Plastic Fabrication Magic", quote="Industry, Plastic Fabrication Magic"), "linkedin_industry_not_listed"),
            "founded is not a year": (self.page(Founded="Since 1986"), dict(head="founded: 1986", quote="Founded, Since 1986", claim="existence"), "linkedin_founded_not_a_year"),
            "size is not a LinkedIn bracket": (self.page(**{"Company size": "51-199 employees"}), dict(head="linkedin_size_bracket 51-199 (self-declared)", quote="Company size, 51-199 employees", claim="size_band"), "linkedin_size_not_a_linkedin_bracket"),
            "size with a second number": (self.page(**{"Company size": "5,001-10,000 employees, 2,000 in Ohio"}), dict(head="linkedin_size_bracket 5,001-10,000 (self-declared)", quote="Company size, 5,001-10,000 employees, 2,000 in Ohio", claim="size_band"), "linkedin_size_not_a_linkedin_bracket"),
        }
        for name, (page, kw, reason) in cases.items():
            with self.subTest(name):
                self.assertEqual(self.run_row(page, **kw), ("HELD", reason))
        self.assertEqual(self.run_row(head="industry: Resin Compounding", quote="Industry, Plastics Manufacturing"), ("FAIL", "claim_value_not_in_field"))
        self.assertEqual(self.run_row(head="linkedin_size_bracket 51-200 (self-declared)", quote="Company size, 5,001-10,000 employees", claim="size_band"), ("FAIL", "claim_value_not_in_field"))

    def test_hq_city_is_always_held_for_reading_even_when_the_record_holds_it(self):
        """Codex round 4: a record whose hq_city was set to the page's city in the same PR must not corroborate it. No hq_city row passes by machine."""
        for held_city, page_value, city in (("North Service Alley", "North Service Alley, Ohio", "North Service Alley"), ("Cleveland", "Cleveland, Ohio", "Cleveland"),
                                            ("Cleveland", "Dayton, Ohio", "Dayton")):
            orgs = [dict(o, hq_city=held_city) if o["org_id"] == "ORG-1" else o for o in ORGS]
            self.idx = b.Index(SITES, orgs)
            row = self.row(head=f"hq_city {city}", quote=f"Headquarters, {page_value}", claim="address", digest=self.capture(self.page(Headquarters=page_value)))
            with self.subTest(page_value):
                self.assertEqual(b.judge(row, self.idx)[:2], ("HELD", "linkedin_hq_city_needs_reading"))
                self.assertEqual(self.replay(row, row["notes"].split(";")[0].split(": ")[1]), ("HELD", "linkedin_hq_city_needs_reading"))
                self.assertEqual(b.linkedin_result(row, self.idx, self.store, self.inputs(row["notes"].split(";")[0].split(": ")[1]))[:2], ("HELD", "linkedin_hq_city_needs_reading"))

    def test_a_signed_in_marker_anywhere_refuses_the_capture(self):
        self.assertEqual(self.run_row(self.page(extra="All products are designed in Ohio.\n")), ("PASS", "linkedin_company_replayed"))  # prose, not a marker
        for marker in ("You are signed in.", "Signed in as Jane", "Sign out"):
            with self.subTest(marker):
                self.assertEqual(self.run_row(self.page(extra=marker + "\n")), ("FAIL", "capture_not_guest"))
        digest = self.capture()
        row = self.row(digest=digest)
        row["notes"] = f"capture_sha256: {digest}"  # the row does not state a guest acquisition
        self.assertEqual(self.replay(row, digest), ("HELD", "linkedin_capture_not_cited"))

    def test_a_parent_roll_up_never_passes_for_its_child_even_after_name_normalization(self):
        parent = "https://www.linkedin.com/company/acme-resin"
        for rid, title, url in (("ORG-17", "Acme Resin Inc", parent), ("ORG-11", "Pinecrest Industries", "https://www.linkedin.com/company/pinecrest-industries")):
            page = self.page(title=f"[1] {title} | LinkedIn ({url})")
            verdict, reason = self.run_row(page, rid=rid, url=url)
            self.assertNotEqual(verdict, "PASS", rid)
            self.assertIn(reason, ("capture_names_parent", "linkedin_name_equals_parent_key"), rid)
        page = self.page(title=f"[1] Pinecrest Industries | LinkedIn ({url})")
        self.assertEqual(self.run_row(page, rid="ORG-10", url=url, head="founded: 1986", quote="Founded, 1986", claim="existence"), ("PASS", "linkedin_company_replayed"))

    def test_real_muse_title_variants_replay_and_the_row_names_its_capture(self):
        for title in (self.TITLE, "[4774708568839730714] Harbor Plastics, Inc. (" + self.URL + ")", "Harbor Plastics, Inc. | LinkedIn (" + self.URL + "/)"):
            with self.subTest(title=title):
                self.assertEqual(self.run_row(self.page(title=title)), ("PASS", "linkedin_company_replayed"))
        good, other = self.capture(), self.capture(self.page(Industry="Rubber Products Manufacturing"))
        row_good, row_other = self.row(digest=good), self.row(digest=other)
        for order in ((good, other), (other, good)):  # the verdict does not depend on the manifest order
            self.assertEqual(self.replay(row_good, *order), ("PASS", "linkedin_company_replayed"))
            self.assertEqual(self.replay(row_other, *order), ("FAIL", "linkedin_quote_not_exact_field"))

    def test_a_missing_or_unnamed_capture_is_held_never_passed(self):
        digest = self.capture()
        row = self.row(digest=digest)
        self.assertEqual(self.replay(row, digest, store=None), ("HELD", "linkedin_store_not_given"))
        self.assertEqual(self.replay(row), ("HELD", "linkedin_capture_not_in_inputs"))  # INPUTS.sha256 does not name the cited digest
        (self.store / f"raw/linkedin/{digest}.txt").write_bytes(self.page().encode() + b"tampered")
        self.assertEqual(self.replay(row, digest), ("HELD", "linkedin_capture_unreadable"))  # digest mismatch
        self.assertEqual(self.run_row(self.page(title="[1] Harbor Plastics | LinkedIn (https://www.linkedin.com/company/another-page)")), ("FAIL", "capture_is_another_page"))
        self.assertEqual(self.run_row(self.TITLE), ("HELD", "linkedin_field_not_in_line_layout"))  # title only, no newline: no crash

    def test_size_brackets_nest_or_set_no_band(self):
        for bracket, band in (("5,001-10,000", "5000+"), ("10,001+", "5000+"), ("0-1", ""), ("2-10", ""), ("11-50", ""), ("51-200", ""), ("201-500", ""), ("501-1,000", ""), ("1,001-5,000", ""),
                              ("51-20", ""), ("10-49", "10-49")):
            self.assertEqual(b.linkedin_bracket_band(bracket), band, bracket)

    def test_url_kinds(self):
        for url, kind in (("https://www.linkedin.com/company/acme/", "company"), ("https://uk.linkedin.com/company/acme/about", "company"),
                          ("https://www.linkedin.com/in/x", "profile"), ("https://www.linkedin.com/%69n/x", "profile"), ("https://lnkd.in/x", "other"),
                          ("https://www.linkedin.com/showcase/acme", "other"), ("https://www.linkedin.com/company/acme/people", "other")):
            self.assertEqual(b.linkedin_url_kind(url), kind, url)


class SbaPppRoute(unittest.TestCase):
    """SBA PPP size_band rows (SCHEMA §1 R13 source 4, §4.13): `borrower_name; business_type; address`, judged on the record's
    name, street and locality. Synthetic only. Planted defects must not PASS; a correct row must."""
    SRC = "SBA PPP LoanNumber 8921367107 (public_150k_plus_240930.csv, release 2024-09-30)"
    OK = "borrower_name: HARBOR RUBBER PRODUCTS INC; business_type: Corporation; address: 1070 EVANS AVE, AKRON, OH 44305"

    @classmethod
    def setUpClass(cls):
        def site(sid, oid, street, status="active", state="OH", city="Akron", zip_="44305"):
            return dict(site_id=sid, org_id=oid, site_name="Plant", city=city, state=state, zip=zip_, street_address=street,
                        operating_status=status, country="US")
        orgs = [dict(org_id=f"O-{n}", legal_name=name, trade_names="") for n, name in (
            ("ONE", "Harbor Rubber Products Inc"), ("TWO", "Harbor Rubber Products Inc"), ("MI", "Harbor Rubber Products Inc"),
            ("SUITE", "Harbor Rubber Products Inc"), ("NONE", "Harbor Rubber Products Inc"), ("LABEL", "Harbor Rubber Products Inc"),
            ("NOZIP", "Harbor Rubber Products Inc"))]
        orgs.append(dict(org_id="O-TRADE", legal_name="Tamarack Holdings Inc", trade_names="Lakeside Rubber Works; Harbor Tire"))
        cls.idx = b.Index([
            site("S-ONE", "O-ONE", "1070 Evans Ave"),
            site("S-TWO-A", "O-TWO", "1100 Evans Ave"), site("S-TWO-B", "O-TWO", "9 Other Rd"),
            site("S-MI", "O-MI", "1110 Evans Ave"), site("S-MI-OLD", "O-MI", "5 Old St", status="inactive", state="MI", city="Troy", zip_="48083"),
            site("S-SUITE", "O-SUITE", "1200 Evans Ave, Suite 500"),
            site("S-DEAD", "O-NONE", "1300 Evans Ave", status="inactive"),
            dict(site("S-LABEL", "O-LABEL", "1400 Evans Ave"), site_name="Kestrel Molding"),  # a site label that is not the operator's name
            site("S-TRADE", "O-TRADE", "1500 Evans Ave"), site("S-NOZIP", "O-NOZIP", "1600 Evans Ave", zip_="")], orgs)

    def row(self, rid, quote, table="organizations", claim="size_band", src=None, cls="government_filing"):
        return ev(rid, src or self.SRC, quote, claim=claim, table=table, cls=cls)

    def check(self, row, verdict, reason=""):
        v, why, info = b.judge(row, self.idx)
        self.assertEqual((v, why), (verdict, reason), info)

    def both(self, quote, verdict, reason="", org="O-ONE", site="S-ONE"):
        self.check(self.row(org, quote), verdict, reason)
        self.check(self.row(site, quote, table="sites"), verdict, reason)

    def fails(self, quote, reason, org="O-ONE", site="S-ONE"):
        """FAIL on both grains, the named reason among the demonstrated conflicts (a wrong city also moves the ZIP)."""
        for rid, table in ((org, "organizations"), (site, "sites")):
            v, why, info = b.judge(self.row(rid, quote, table=table), self.idx)
            self.assertEqual(v, "FAIL", (why, info))
            self.assertIn(reason, why.split("+"))

    def test_correct_row_passes_on_organization_and_site(self):
        self.both(self.OK, "PASS")

    def test_every_whitelisted_type_passes_and_the_sba_double_space_is_read(self):
        for kind in ("Corporation", "Subchapter S Corporation", "Limited  Liability Company(LLC)", "Partnership",
                     "Limited Liability Partnership"):
            self.both(self.OK.replace("Corporation;", kind + ";", 1), "PASS")

    def test_wrong_borrower_name(self):
        self.both(self.OK.replace("HARBOR RUBBER PRODUCTS INC", "KESTREL MOLDING LLC"), "FAIL", "name_not_held")

    def test_wrong_street(self):
        self.both(self.OK.replace("1070 EVANS AVE", "1090 EVANS AVE"), "FAIL", "street_differs")

    def test_wrong_city_and_zip(self):
        self.fails(self.OK.replace("AKRON, OH 44305", "CANTON, OH 44702"), "city_differs")

    def test_city_and_zip_are_not_alternatives(self):  # Codex #572 r1: same_locality accepts either, the rule is name, street and city
        self.fails(self.OK.replace("AKRON, OH 44305", "CANTON, OH 44305"), "ppp_city_differs")  # right ZIP, wrong city
        self.fails(self.OK.replace("AKRON, OH 44305", "AKRON, OH 99999"), "ppp_zip_differs")  # right city, wrong ZIP
        self.both(self.OK.replace("AKRON, OH 44305", "AKRON, OH 44305-1234"), "PASS")  # ZIP+4 agrees on ZIP5
        for quote in (self.OK.replace("AKRON, OH 44305", "AKRON, OH"), self.OK.replace("AKRON, OH 44305", "AKRON")):
            for rid, table in (("O-ONE", "organizations"), ("S-ONE", "sites")):
                v, why, _ = b.judge(self.row(rid, quote, table=table), self.idx)
                self.assertNotEqual(v, "PASS", (quote, why))

    def test_a_quote_without_a_city_is_held_even_when_the_zip_matches(self):  # Codex #572 r2: "OH 44305" passed on ZIP alone
        for quote in (self.OK.replace("AKRON, OH 44305", "OH 44305"), self.OK.replace("AKRON, OH 44305", ", OH 44305"),
                      self.OK.replace("AKRON, OH 44305", "OH, 44305")):
            self.both(quote, "HELD", "held_for_reading:ppp_quote_city_missing")
        # a record that holds no ZIP still needs the quoted city
        for rid, table in (("O-NOZIP", "organizations"), ("S-NOZIP", "sites")):
            v, why, _ = b.judge(self.row(rid, self.OK.replace("1070 EVANS AVE", "1600 EVANS AVE").replace("AKRON, OH 44305", "OH"), table=table), self.idx)
            self.assertEqual(v, "HELD", why)
            self.assertIn("ppp_quote_city_missing", why)
        # a record that holds no ZIP is judged on the city alone
        self.both(self.OK.replace("1070 EVANS AVE", "1600 EVANS AVE"), "PASS", org="O-NOZIP", site="S-NOZIP")
        self.fails(self.OK.replace("1070 EVANS AVE", "1600 EVANS AVE").replace("AKRON", "CANTON"), "city_differs", org="O-NOZIP", site="S-NOZIP")

    def test_source_ref_must_be_the_documented_form(self):  # Codex #572 r1: the prefix alone dispatched
        for ref in ("SBA PPP garbage", "SBA PPP LoanNumber 8921367107", "SBA PPP LoanNumber 8921367107 (public_150k_plus_240930.csv)",
                    "SBA PPP LoanNumber 89213671 (public_150k_plus_240930.csv, release 2024-09-30)",
                    "SBA PPP LoanNumber 8921367107 (public_150k_plus_240930.csv, release 2024-13-45)",
                    "SBA PPP LoanNumber 8921367107 (public_150k_plus_240930, release 2024-09-30)",
                    self.SRC + " extra", "SBA PPP LoanNumber 8921367107 (a b.csv, release 2024-09-30)"):
            for rid, table in (("O-ONE", "organizations"), ("S-ONE", "sites")):
                self.check(self.row(rid, self.OK, table=table, src=ref), "UNINSPECTABLE", "ppp_source_ref")

    def test_source_class_must_be_government_filing(self):  # Codex #572 r1: own_site passed without an own-site URL or capture
        for cls in ("own_site", "registry", "directory", "press", "platform_category", "linkedin_company"):
            for rid, table in (("O-ONE", "organizations"), ("S-ONE", "sites")):
                v, why, _ = b.judge(self.row(rid, self.OK, table=table, cls=cls), self.idx)
                self.assertEqual((v, why), ("UNINSPECTABLE", "ppp_source_class") if cls != "linkedin_company" else (v, why))
                self.assertNotEqual(v, "PASS", cls)

    def test_borrower_must_be_an_operator_name_not_a_site_label(self):  # Codex #572 r1: held_keys includes the site label
        label = self.OK.replace("HARBOR RUBBER PRODUCTS INC", "KESTREL MOLDING").replace("1070", "1400")
        self.both(label, "FAIL", "name_not_held", org="O-LABEL", site="S-LABEL")
        for name in ("LAKESIDE RUBBER WORKS INC", "HARBOR TIRE LLC"):  # trade names
            self.both(self.OK.replace("HARBOR RUBBER PRODUCTS INC", name).replace("1070", "1500"), "PASS", org="O-TRADE", site="S-TRADE")
        self.both(self.OK.replace("HARBOR RUBBER PRODUCTS INC", "TAMARACK HOLDINGS INC").replace("1070", "1500"), "PASS", org="O-TRADE", site="S-TRADE")
        # the held name plus extra corporate words is not the held name here
        self.both(self.OK.replace("HARBOR RUBBER PRODUCTS INC", "HARBOR RUBBER PRODUCTS HOLDINGS INC"), "FAIL", "name_not_held")

    def test_wrong_state(self):
        self.both(self.OK.replace("OH 44305", "MI 44305"), "FAIL", "state_differs")

    def test_missing_quote(self):
        for rid, table in (("O-ONE", "organizations"), ("S-ONE", "sites")):
            self.check(self.row(rid, None, table=table), "UNINSPECTABLE", "no_quote")

    def test_individual_borrower_types_fail(self):
        for kind in ("Sole Proprietorship", "Self-Employed Individuals", "Independent Contractors", "Individual", "Non-Profit Organization", ""):
            self.both(self.OK.replace("Corporation;", kind + ";", 1), "FAIL", "ppp_individual_borrower_type")

    def test_business_type_must_be_stated(self):
        self.both("borrower_name: HARBOR RUBBER PRODUCTS INC; address: 1070 EVANS AVE, AKRON, OH 44305", "UNINSPECTABLE", "ppp_quote_fields")

    def test_extra_or_missing_fields_are_not_read(self):
        self.both(self.OK + "; jobs_reported: 24", "UNINSPECTABLE", "ppp_quote_fields")
        self.both("borrower_name: HARBOR RUBBER PRODUCTS INC; business_type: Corporation", "UNINSPECTABLE", "ppp_quote_fields")

    def test_one_sided_suite_is_held_and_a_conflicting_suite_fails(self):
        self.both(self.OK.replace("1070 EVANS AVE", "1070 EVANS AVE STE 110"), "HELD",
                  "held_for_reading:designator_not_on_both_sides")  # borrower names a suite the record lacks
        suite = self.OK.replace("1070 EVANS AVE", "1200 EVANS AVE")
        self.both(suite, "HELD", "held_for_reading:designator_not_on_both_sides", org="O-SUITE", site="S-SUITE")  # record names a suite the borrower omits
        self.both(suite.replace("AVE,", "AVE STE 110,"), "FAIL", "unit_differs", org="O-SUITE", site="S-SUITE")  # SPR Therapeutics' case
        self.both(suite.replace("AVE,", "AVE SUITE 500,"), "PASS", org="O-SUITE", site="S-SUITE")

    def test_the_same_quote_passing_on_two_site_records_is_held(self):
        idx = b.Index([dict(site_id=f"S-{n}", org_id="O-ONE", site_name="Plant", city="Akron", state="OH", zip="44305",
                            street_address="1070 Evans Ave", operating_status="active", country="US") for n in "AB"],
                      [dict(org_id="O-ONE", legal_name="Harbor Rubber Products Inc", trade_names="")])
        self.assertEqual(b.judge(self.row("S-A", self.OK, table="sites"), idx)[:2], ("HELD", "held_for_reading:passes_on_two_records"))
        self.assertEqual(b.judge(self.row("O-ONE", self.OK), idx)[:2], ("HELD", "held_for_reading:ppp_not_single_site_ohio_organization"))

    def test_only_size_band_claims_are_read(self):
        for claim in ("address", "existence", "scope", "activity"):
            self.check(self.row("S-ONE", self.OK, table="sites", claim=claim), "UNINSPECTABLE", "ppp_claim_not_size_band")

    def test_organization_must_be_single_site_and_ohio_only(self):
        hold = "held_for_reading:ppp_not_single_site_ohio_organization"
        for oid in ("O-TWO", "O-MI", "O-NONE"):  # two active sites, a held site in Michigan, no active site
            self.check(self.row(oid, self.OK), "HELD", hold)

    def test_other_tables_are_not_read(self):
        self.check(ev("O-ONE", self.SRC, self.OK, claim="size_band", table="equipment", cls="government_filing"), "UNINSPECTABLE", "other_table")

    def test_the_2026_11_16_row_format_has_no_quote_and_stays_held(self):
        row = ev("O-ONE", "https://data.sba.gov/sites/default/files/distribution/SBA-OCA-2022-07-001/public_150k_plus_240930.csv (SBA PPP LoanNumber 8921367107)",
                 None, claim="size_band", table="organizations", cls="government_filing")
        row["claim_detail"] = 'employee_band_ohio=10-49; SBA PPP BorrowerName="HARBOR RUBBER PRODUCTS INC"; JobsReported="24"'
        self.check(row, "UNINSPECTABLE", "no_quote")


if __name__ == "__main__":
    unittest.main()
