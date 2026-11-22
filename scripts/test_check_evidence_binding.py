"""Tests for scripts/check_evidence_binding.py.

Every case is a synthetic string shaped like a real evidence row (controller instruction 2026-11-22: no source quote
text outside data/); the comment on each case names the real row it models. Planted defects must FAIL; true matches
must PASS; what cannot be inspected must be UNINSPECTABLE, never PASS.
"""
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

import check_evidence_binding as b

ROOT = Path(__file__).resolve().parents[1]

ORGS = [
    {"org_id": "ORG-1", "legal_name": "Harbor Plastics, Inc.", "trade_names": "Lakeside Plastics", "hq_city": "Cleveland",
     "hq_state": "OH"},
    {"org_id": "ORG-2", "legal_name": "Northfield Chemical Inc.", "trade_names": "", "hq_city": "Midland", "hq_state": "MI"},
    {"org_id": "ORG-3", "legal_name": "Riverbend Medical, Inc.", "trade_names": "", "hq_city": "San Clemente",
     "hq_state": "CA"},
    {"org_id": "ORG-4", "legal_name": "Containment Systems, Inc.", "trade_names": "", "hq_city": "Conroe", "hq_state": "TX"},
    {"org_id": "ORG-5", "legal_name": "Gulfstar Enterprises LLC", "trade_names": "", "hq_city": "Houston", "hq_state": "TX"},
    {"org_id": "ORG-6", "legal_name": "Crest Chemical LP", "trade_names": "", "hq_city": "Houston", "hq_state": "TX"},
    {"org_id": "ORG-7", "legal_name": "Tamarack Rubber Company", "trade_names": "", "hq_city": "Akron", "hq_state": "OH"},
    {"org_id": "ORG-8", "legal_name": "Kestrel Molding LLC", "trade_names": "", "hq_city": "Troy", "hq_state": "AL"},
    {"org_id": "ORG-9", "legal_name": "Alder Composites Corporation", "trade_names": "", "hq_city": "Chula Vista",
     "hq_state": "CA"},
    {"org_id": "ORG-10", "legal_name": "Pinecrest Foam Holdings", "trade_names": "", "hq_city": "Dallas", "hq_state": "TX"},
    {"org_id": "ORG-11", "legal_name": "Pinecrest Foam LLC", "trade_names": "", "parent_org_id": "ORG-10",
     "hq_city": "Dallas", "hq_state": "TX"},
    {"org_id": "ORG-12", "legal_name": "Armacor LLC", "trade_names": "", "hq_city": "Mebane", "hq_state": "NC"},
    {"org_id": "ORG-13", "legal_name": "C U E of West Virginia", "trade_names": "", "hq_city": "Mount Hope",
     "hq_state": "WV"},
    {"org_id": "ORG-14", "legal_name": "Meridian Coatings Co.", "trade_names": "", "hq_city": "Longview", "hq_state": "TX",
     "notes": "Dated operator change: RY2024 operator Eastgate Polymers US Inc; Meridian completion July 2026."},
]
SITES = [
    # two sibling sites of one operator, a few hundred metres apart (models SITE-000107 / SITE-000108)
    {"site_id": "S-CARN", "org_id": "ORG-1", "site_name": "Harbor Plastics — Cleveland", "city": "Cleveland",
     "street_address": "3705 Carnegie Avenue"},
    {"site_id": "S-PROS", "org_id": "ORG-1", "site_name": "Lakeside Plastics — Cleveland", "city": "Cleveland",
     "street_address": "3746 Prospect Ave E"},
    {"site_id": "S-VIC", "org_id": "ORG-2", "site_name": "Northfield — Victoria Site", "city": "Victoria",
     "street_address": "2697 Old Bloomington Rd N"},
    {"site_id": "S-RR", "org_id": "ORG-3", "site_name": "Riverbend Medical - Round Rock Plant", "city": "Round Rock",
     "street_address": "4020 N Mays Street"},
    {"site_id": "S-BAK", "org_id": "ORG-4", "site_name": "Containment Systems - Bakersfield", "city": "Bakersfield",
     "street_address": "2600 Pegasus Dr"},
    {"site_id": "S-PAS", "org_id": "ORG-7", "site_name": "Tamarack - Pasadena Plant", "city": "Pasadena",
     "street_address": "13441 Bay Area Blvd"},
    {"site_id": "S-AVON", "org_id": "ORG-7", "site_name": "Tamarack - Avon Lake", "city": "Avon Lake",
     "street_address": "554 Moore Rd"},
    {"site_id": "S-PLAQ", "org_id": "ORG-7", "site_name": "Tamarack - Plaquemine Plant", "city": "Plaquemine",
     "street_address": "26270 HWY 405"},
    {"site_id": "S-EJ", "org_id": "ORG-7", "site_name": "Tamarack - East Jordan", "city": "East Jordan",
     "street_address": "6400 M-32 Highway"},
    {"site_id": "S-BLANK", "org_id": "ORG-7", "site_name": "Tamarack - Wickliffe", "city": "Wickliffe",
     "street_address": ""},
    {"site_id": "S-STE100", "org_id": "ORG-7", "site_name": "Tamarack - Columbus", "city": "Columbus",
     "street_address": "191 American Blvd, Suite 100"},
    {"site_id": "S-STE140", "org_id": "ORG-7", "site_name": "Tamarack - Raleigh", "city": "Raleigh",
     "street_address": "2560 White Oak Circle Suite 140"},
    {"site_id": "S-STE200", "org_id": "ORG-7", "site_name": "Tamarack - Goodyear", "city": "Goodyear",
     "street_address": "4320 S. Cotton Ln, Suite 200"},
    {"site_id": "S-BLDG", "org_id": "ORG-7", "site_name": "Tamarack - West Deptford", "city": "West Deptford",
     "street_address": "286 Mantua Grove Rd Building # 1"},
    {"site_id": "S-ONE", "org_id": "ORG-7", "site_name": "Tamarack - Neenah", "city": "Neenah",
     "street_address": "One Innovation Drive"},
    {"site_id": "S-198A", "org_id": "ORG-7", "site_name": "Tamarack - New Bern", "city": "New Bern",
     "street_address": "198A Bosch Blvd"},
    {"site_id": "S-GRID", "org_id": "ORG-7", "site_name": "Tamarack - Oconomowoc", "city": "Oconomowoc",
     "street_address": "N44 W33341 Watertown Plank Rd"},
    {"site_id": "S-PARK", "org_id": "ORG-7", "site_name": "Tamarack - Neodesha", "city": "Neodesha",
     "street_address": "Twin Rivers Industrial Park"},
    {"site_id": "S-AND", "org_id": "ORG-7", "site_name": "Tamarack - Berwick", "city": "Berwick",
     "street_address": "9th & Bomboy Lane"},
    {"site_id": "S-RANGE", "org_id": "ORG-7", "site_name": "Tamarack - Erie", "city": "Erie",
     "street_address": "1201-1205 Main St"},
    {"site_id": "S-ORD", "org_id": "ORG-7", "site_name": "Tamarack - Wadsworth", "city": "Wadsworth",
     "street_address": "300 First Street"},
    {"site_id": "S-AOC", "org_id": "ORG-8", "site_name": "Kestrel - Valparaiso", "city": "Valparaiso",
     "street_address": "955 Evans Ave"},
    {"site_id": "S-CT", "org_id": "ORG-8", "site_name": "Kestrel - East Haven plant", "city": "East Haven",
     "street_address": "30 Tyler Street Ext"},
    {"site_id": "S-ARM", "org_id": "ORG-12", "site_name": "Armacor - Conover", "city": "Conover",
     "street_address": "1004 Keisler Rd"},
    {"site_id": "S-PIN", "org_id": "ORG-11", "site_name": "Pinecrest Foam - Lancaster", "city": "Lancaster",
     "street_address": "400 Industrial Dr"},
    {"site_id": "S-MER", "org_id": "ORG-14", "site_name": "Meridian - Longview", "city": "Longview",
     "street_address": "300 Kodak Blvd"},
    {"site_id": "S-CUE", "org_id": "ORG-13", "site_name": "CUE - Mount Hope", "city": "Mount Hope",
     "street_address": "250 Price Hill Road"},
    {"site_id": "S-NC", "org_id": "ORG-7", "site_name": "Tamarack - Fayetteville", "city": "Fayetteville",
     "street_address": "6650 Ramsey St"},
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
            f"permit_number(s): 73082; TXD000000001; program(s): IHW; status(es): ACTIVE; source_record_key: RN=RN1")


def ev(rid, source, quote, claim="existence", table="sites", eid="EVD-T"):
    detail = f"site of 'x' at recorded address; quote: {quote}" if quote is not None else "existence (own site)"
    return {"evidence_id": eid, "record_table": table, "record_id": rid, "claim_type": claim, "claim_detail": detail,
            "source_ref": source, "created_by": "test", "_at": "data/evidence_test.csv:2"}


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
        self.check(ev("S-PROS", OSHA, "HARBOR PLASTICS, 3705 CARNEGIE AVE., CLEVELAND, OH 44115"), "FAIL",
                   "street_differs")

    def test_sibling_street_on_wrong_site_address(self):  # EVD-427648
        self.check(ev("S-PROS", OSHA, "HARBOR PLASTICS, 3705 CARNEGIE AVE., CLEVELAND, OH 44115", "address"), "FAIL",
                   "street_differs")

    def test_sibling_quote_true_on_its_own_site(self):  # EVD-427645: the same quote binds to the Carnegie site
        self.check(ev("S-CARN", OSHA, "HARBOR PLASTICS, 3705 CARNEGIE AVE., CLEVELAND, OH 44115"), "PASS")

    def test_swapped_quote_between_siblings_fails(self):  # planted: a correct Prospect quote moved to Carnegie
        q = "Lakeside Plastics, 3746 Prospect Avenue East, Cleveland, OH 44115"
        self.check(ev("S-PROS", ITA, q), "PASS")
        self.check(ev("S-CARN", ITA, q), "FAIL", "street_differs")

    def test_former_operator_permit(self):  # EVD-457493: former operator's permit at the held street
        self.check(ev("S-VIC", TCEQ, permit("Eastgate Polymers, Inc.", "EASTGATE VICTORIA PLANT",
                                            "2697 OLD BLOOMINGTON RD N, VICTORIA, TX 77905", "VICTORIA")),
                   "FAIL", "name_not_held")

    def test_held_name_plus_other_entity_words(self):  # EVD-455899: a fleet-services affiliate is another operator
        info = self.check(ev("S-RR", TCEQ, permit("Riverbend Medical Fleet Services, LLC", "OTSUKA RIVERBEND MEDICAL",
                                                  "4020 N MAYS ST, ROUND ROCK, TX 78664", "WILLIAMSON")),
                          "FAIL", "name_not_held")
        self.assertIn("leading_run", info["name_alt"])

    def test_other_company_at_exact_street(self):  # EVD-449620, EVD-450128: shared FRS key, different name
        self.check(ev("S-BAK", RCRA, "OWENSBY FIBERGLAS CORP; 2600 PEGASUS DRIVE, BAKERSFIELD, CA 93308" + ECHO_TAIL),
                   "FAIL", "name_not_held")

    def test_unheld_facility_label(self):  # EVD-457589: neither permittee nor facility label is held
        self.check(ev("S-BAK", TCEQ, permit("Belmar Manufacturing Company, Inc.", "BAKERSFIELD BELMAR",
                                            "2600 PEGASUS DR, BAKERSFIELD, CA 93308")), "FAIL", "name_not_held")

    def test_hq_from_service_station_permit(self):  # EVD-457167 / EVD-457135: a store's permit is not an HQ
        for fac in ("ADVANCE AUTO PARTS 6841", "BELLAIRE SERVICE CENTER"):
            self.check(ev("ORG-5", TCEQ, permit("Gulfstar Enterprises LLC", fac, "8600 W BELLFORT AVE, HOUSTON, TX 77071"),
                          "address", "organizations"), "FAIL", "hq_from_facility_or_permit")

    def test_hq_from_permit_named_for_company(self):  # EVD-457177: facility label names the company, still a permit
        self.check(ev("ORG-5", TCEQ, permit("Gulfstar Enterprises LLC", "GULFSTAR ENTERPRISE",
                                            "100 MAIN ST, HOUSTON, TX 77002"), "address", "organizations"),
                   "FAIL", "hq_from_facility_or_permit")

    def test_short_name_inside_another(self):  # first-cut token subset: a one-word brand inside another name
        for permittee in ("CREST", "BELLAIRE CREST"):
            self.check(ev("ORG-6", TCEQ, permit(permittee, "STORE 12", "1 MAIN ST, HOUSTON, TX 77002"),
                          table="organizations"), "FAIL", "name_not_held")

    def test_permit_at_other_street(self):  # EVD-455507: an auto service centre permit filed on a plant
        self.check(ev("S-PAS", TCEQ, permit("Tamarack Rubber Company", "TAMARACK AUTO SERVICE CENTER",
                                            "514E SOUTHMORE AVE, PASADENA, TX 77502"), "address"),
                   "FAIL", "street_differs")

    def test_neighbouring_number(self):  # EVD-432662: 552 vs 554 on one road
        self.check(ev("S-AVON", ITA, "Tamarack, 552 Moore Road, Avon Lake, OH 44012"), "FAIL", "street_differs")

    def test_same_number_other_road(self):  # EVD-426678: the first cut passed number + generic word
        info = self.check(ev("S-PLAQ", OSHA, "TAMARACK RUBBER CO, 26270 LOUISIANA HWY 1 SOUTH, PLAQUEMINE, LA 70764"),
                          "FAIL", "street_differs")
        self.assertEqual(info["street_limit"], "same_number_other")

    def test_po_box_is_no_street(self):  # EVD-431900
        self.check(ev("S-EJ", ITA, "Tamarack Rubber Co, PO BOX 575, East Jordan, MI 49770"), "FAIL", "quote_no_street")

    def test_city_only_permit_address(self):  # EVD-454757: Ohio EPA layer prints city + ZIP only
        self.check(ev("S-AVON", OHEPA, "permittee: Tamarack Rubber Co; address: Avon Lake, OH 44012; county: Lorain; "
                                       "permit_number(s): 3GR00000*BG"), "FAIL", "quote_no_street")

    def test_record_without_street(self):  # EVD-454759
        self.check(ev("S-BLANK", OHEPA, "permittee: Tamarack Rubber Co; address: 29400 Lakeland Blvd, Wickliffe, OH "
                                        "44092; county: Lake"), "FAIL", "record_no_street")

    def test_suite_conflict(self):  # 463 review: SITE-000514 (suite 100 vs 300), SITE-019015 (140 vs 120)
        self.check(ev("S-STE100", ITA, "Tamarack Rubber Co, 191 American Blvd Suite 300, Columbus, OH 43230"),
                   "FAIL", "unit_differs")
        self.check(ev("S-STE140", OSHA, "TAMARACK RUBBER CO, 2560 WHITE OAK CIR STE 120, RALEIGH, NC 27609"),
                   "FAIL", "unit_differs")

    def test_hq_from_fmcsa_filed_address(self):  # EVD-453316: SCHEMA §4.8 S-5
        q = "Legal Name: KESTREL MOLDING LLC; DBA Name: —; Physical Address: 1 SANDERS ROAD, TROY, AL 36079; Status: ACTIVE"
        self.check(ev("ORG-8", FMCSA, q, "address", "organizations"), "FAIL", "hq_from_s5_identity_source")

    def test_hq_from_state_filing(self):  # EVD-458107: S-5 (a state filing's address may be an agent's)
        q = "legal_name: KESTREL MOLDING LLC; entity_type: Stock; principal_address: 210 MAIN DRIVE TROY, AL 36079"
        self.check(ev("ORG-8", STATE, q, "address", "organizations"), "FAIL", "hq_from_s5_identity_source")

    def test_hq_wrong_city_from_entity_source(self):  # planted: an entity-address source in another city
        q = "recipient_name: ALDER COMPOSITES CORP; recipient_uei: X; recipient_address: 9 A ST, SAN DIEGO, CA 92101"
        self.check(ev("ORG-9", USASP, q, "address", "organizations"), "FAIL", "hq_city_state_differs")

    def test_leading_run_is_strict_fail(self):  # EVD-445712: held name + plant label; owner question
        info = self.check(ev("S-ARM", NPDES, "ARMACOR LLC-CONOVER PLANT; 1004 KEISLER RD, CONOVER, NC 28613" + ECHO_TAIL),
                          "FAIL", "name_not_held")
        self.assertIn("leading_run", info["name_alt"])

    def test_facility_label_only_is_strict_fail(self):  # EVD-457497 / EVD-456891: permittee is another legal string
        info = self.check(ev("S-ARM", TCEQ, permit("Armacor APO, Inc.", "ARMACOR", "1004 KEISLER RD, CONOVER, NC 28613")),
                          "FAIL", "name_not_held")
        self.assertIn("facility_label", info["name_alt"])

    def test_parent_name_is_strict_fail(self):  # parent's name on a subsidiary's site; owner question
        info = self.check(ev("S-PIN", ITA, "Pinecrest Foam Holdings, 400 Industrial Dr, Lancaster, PA 17601"),
                          "FAIL", "name_not_held")
        self.assertIn("parent", info["name_alt"])

    def test_predecessor_in_notes_is_strict_fail(self):  # EVD-450005: predecessor named only in notes
        info = self.check(ev("S-MER", RCRA, "EASTGATE POLYMERS US; 300 KODAK BLVD, LONGVIEW, TX 75602" + ECHO_TAIL),
                          "FAIL", "name_not_held")
        self.assertIn("notes", info["name_alt"])

    def test_dotted_initials_is_strict_fail(self):  # EVD-445061: name_key keeps the dots' spaces
        info = self.check(ev("S-CUE", NPDES, "C.U.E. OF WEST VIRGINIA; 250 PRICE HILL ROAD, MT. HOPE, WV 25880" + ECHO_TAIL),
                          "PASS")
        self.assertEqual(info, {})  # "c u e of west virginia" is held verbatim here; spacing measured when it is not
        info = self.check(ev("S-CUE", NPDES, "CUE OF WEST VIRGINIA; 250 PRICE HILL ROAD, MT. HOPE, WV 25880" + ECHO_TAIL),
                          "FAIL", "name_not_held")
        self.assertIn("spacing", info["name_alt"])

    def test_street_key_limits_are_measured_not_passed(self):  # controller: report, do not widen street_key
        self.assertEqual(self.check(ev("S-RANGE", ITA, "Tamarack, 1203 Main St, Erie, PA 16501"), "FAIL",
                                    "street_differs")["street_limit"], "number_in_recorded_range")
        self.assertEqual(self.check(ev("S-ORD", ITA, "Tamarack, 300 1st Street, Wadsworth, OH 44281"), "FAIL",
                                    "street_differs")["street_limit"], "number_word")

    # ---- true matches: must PASS

    def test_echo_true_match(self):  # EVD-442346
        self.check(ev("S-BAK", RCRA, "CONTAINMENT SYSTEMS INC; 2600 PEGASUS DRIVE, BAKERSFIELD, CA 93308" + ECHO_TAIL),
                   "PASS")

    def test_permit_true_match(self):  # EVD-456335
        self.check(ev("S-PAS", TCEQ, permit("Tamarack Rubber Company", "TAMARACK RUBBER",
                                            "13441 BAY AREA BLVD, PASADENA, TX 77507")), "PASS")

    def test_fmcsa_site_true_match(self):  # EVD-454689
        q = "Legal Name: KESTREL MOLDING LLC; DBA Name: —; Physical Address: 955 EVANS AVENUE, VALPARAISO, IN 46383"
        self.check(ev("S-AOC", FMCSA, q), "PASS")

    def test_osha_establishment_company_pair(self):  # EVD-431182: "AOC, AOC" is establishment, company
        self.check(ev("S-AOC", ITA, "KESTREL, KESTREL MOLDING, 955 Evans Ave, Valparaiso, IN 46383"), "PASS")

    def test_osha_four_digit_zip(self):  # EVD-430557: the ZIP lost its leading zero
        self.check(ev("S-CT", ITA, "Kestrel Molding LLC, 30 Tyler St Ext, East Haven, CT 6512"), "PASS")

    def test_osha_mangled_zips_parse(self):  # EVD-430785, EVD-431015: "317E6" and a 9-digit ZIP
        for z in ("317E6", "065121129"):
            self.check(ev("S-CT", ITA, f"Kestrel Molding LLC, 30 Tyler St Ext, East Haven, CT {z}"), "PASS")

    def test_echo_parenthetical_with_semicolon(self):  # EVD-441359: "(XYZ; FORMERLY ...)" is not a field break
        self.check(ev("S-BAK", RCRA, "CONTAINMENT SYSTEMS INC (CSI; FORMERLY TANKCO); 2600 PEGASUS DR, BAKERSFIELD, "
                                     "CA 93308" + ECHO_TAIL), "PASS")

    def test_ampersand_and_intersection(self):  # EVD-428624
        self.check(ev("S-AND", OSHA, "TAMARACK RUBBER CO, 9TH AND BOMBOY LANE, BERWICK, PA 18603"), "PASS")

    def test_same_suite_and_one_sided_unit(self):  # EVD-430253; a unit on one side only is not a conflict
        self.check(ev("S-STE200", ITA, "Tamarack, 4320 S. Cotton Ln, Suite 200, Goodyear, AZ 85338"), "PASS")
        self.check(ev("S-BLDG", NPDES, "TAMARACK RUBBER CO; 286 MANTUA GROVE ROAD, WEST DEPTFORD TWP, NJ 08066"
                      + ECHO_TAIL), "PASS")

    def test_civic_number_forms(self):  # 463 review: SITE-004431, SITE-011463, SITE-004620 are real civic numbers
        self.check(ev("S-ONE", ITA, "Tamarack Rubber Co, One Innovation Dr, Neenah, WI 54956"), "PASS")
        self.check(ev("S-198A", ITA, "Tamarack Rubber Co, 198A BOSCH BLVD, New Bern, NC 28562"), "PASS")
        self.check(ev("S-GRID", OSHA, "TAMARACK RUBBER CO, N44 W33341 WATERTOWN PLANK ROAD, OCONOMOWOC, WI 53066"), "PASS")

    def test_org_existence_from_permit(self):  # EVD-457166: the permit witnesses the permittee's existence
        self.check(ev("ORG-5", TCEQ, permit("Gulfstar Enterprises LLC", "ADVANCE AUTO PARTS 6841",
                                            "8600 W BELLFORT AVE, HOUSTON, TX 77071"), table="organizations"), "PASS")

    def test_org_existence_from_state_filing(self):  # EVD-458053
        q = "legal_name: KESTREL MOLDING LLC; entity_type: FOREIGN LIMITED LIABILITY COMPANY; status: Active"
        self.check(ev("ORG-8", STATE, q, table="organizations"), "PASS")

    def test_hq_from_usaspending(self):  # EVD-459301
        q = ("recipient_name: TAMARACK RUBBER CO; recipient_uei: X; parent_recipient_name: TAMARACK RUBBER CO; "
             "recipient_address: 210 CARPENTER DAM RD, AKRON, OH 443018219; award_count: 1")
        self.check(ev("ORG-7", USASP, q, "address", "organizations"), "PASS")

    def test_hq_from_sbir_full_state_name(self):  # EVD-458829
        q = "firm_name: ALDER COMPOSITES CORPORATION; uei: X; address: 651 ANITA ST STE B8, CHULA VISTA, California 91911"
        self.check(ev("ORG-9", SBIR, q, "address", "organizations"), "PASS")

    # ---- uninspectable: never PASS

    def test_no_civic_number(self):  # equal keys naming only a park cannot tell two places apart
        self.check(ev("S-PARK", ITA, "Tamarack Rubber Co, Twin Rivers Industrial Park, Neodesha, KS 66757"),
                   "UNINSPECTABLE", "no_civic_number")

    def test_shifted_columns(self):  # EVD-455505: NC DEQ layer puts a region code in permittee
        q = ("permittee: 3; facility: Tamarack Rubber Company; address: 6650 Ramsey Street, Fayetteville, NC 28311; "
             "county: 2600050; permit_number(s): 3705100050")
        info = self.check(ev("S-NC", NCDEQ, q), "UNINSPECTABLE", "operator_not_a_name")
        self.assertEqual(info["if_facility_operator"], "PASS")

    def test_uninspectable_classes(self):
        self.check(ev("S-NC", "https://example.com/locations", "We operate a plant at 6650 Ramsey St"),
                   "UNINSPECTABLE", "free_text_web_quote")
        self.check(ev("S-NC", "https://example.com/", None), "UNINSPECTABLE", "no_quote")
        self.check(ev("PERSON-1", "https://example.edu/", "x", table="people"), "UNINSPECTABLE", "other_table")
        self.check(ev("S-NONE", ITA, "x, 1 A St, B, OH 44101"), "UNINSPECTABLE", "record_not_found")
        self.check(ev("ORG-7", "examplecompany.com", "made from natural rubber", table="organizations"),
                   "UNINSPECTABLE", "unknown_source_family")
        self.check(ev("S-NC", RCRA, "TAMARACK RUBBER CO; NO ADDRESS PRINTED; FRS registry 1"), "UNINSPECTABLE",
                   "parse_failed")


class GateMechanics(unittest.TestCase):
    parallel_safe = True

    def test_changed_rows_sees_new_and_repointed(self):
        base = [ev("S-PROS", ITA, "q", eid="EVD-1"), ev("S-PROS", ITA, "q", eid="EVD-2")]
        head = [ev("S-PROS", ITA, "q", eid="EVD-1"), ev("S-CARN", ITA, "q", eid="EVD-2"), ev("S-CARN", ITA, "q", eid="EVD-3")]
        self.assertEqual([e["evidence_id"] for e in b.changed_rows(base, head)], ["EVD-2", "EVD-3"])

    def test_waivers(self):
        ok = [("tasks/x/BINDING_WAIVERS.csv", "evidence_id,reason,reviewer\nEVD-1,campus address,owner 2026-11-22\n")]
        self.assertEqual(b.load_waivers(ok)["EVD-1"][2], "owner 2026-11-22")
        for bad in ("evidence_id,reason\nEVD-1,x\n", "evidence_id,reason,reviewer\nEVD-1,x,\n"):
            with self.assertRaises(ValueError):
                b.load_waivers([("tasks/x/BINDING_WAIVERS.csv", bad)])

    def test_provenance_folder_named_by_created_by(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "lane-a").mkdir()
            (Path(d) / "lane-a" / "check.py").write_text("")
            (Path(d) / "lane-b").mkdir()  # a folder without check.py does not count
            def has(t): return (Path(d) / t / "check.py").is_file()
            rows = [dict(ev("S-PROS", ITA, "q"), created_by=c) for c in ("claude-code lane-a", "lane-b", "lane-b", "../x")]
            self.assertEqual(b.provenance_missing(rows, has), {"lane-b": 2, "../x": 1})


def has_commits(*shas):
    return all(subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{s}^{{commit}}"],
                              capture_output=True).returncode == 0 for s in shas)


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
        self.assertIn("23564 rows added or re-pointed", out)

    def test_batch6_has_no_provenance_folder(self):
        code, out = self.run_main("--provenance-since", "6a76e923", "--head", "17834918")
        self.assertEqual(code, 1)
        self.assertIn("MISSING tasks/<folder>/check.py for created_by 'spaghetti-batch6-2026-11-22' (23564 rows)", out)


if __name__ == "__main__":
    unittest.main()
