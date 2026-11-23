#!/usr/bin/env python3
"""Tests for scripts/matching.py, the repo's one street test (moved from test_derive_last_activity.py with the guard
it pins; shared by scripts/derive_last_activity.py and scripts/check_evidence_binding.py)."""
import unittest

import matching as dl

SAME = [  # equal atlas.street_key
    ("5020 Enterprise Parkway", "5020 ENTERPRISE PKWY"),            # suffix abbreviation
    ("5101 21ST ST", "5101 21st Street"),                           # ordinal, suffix
    ("1719 Hwy 72 E", "1719 Hwy 72 East"),                          # direction word
    ("100 Main St Suite 4", "100 MAIN STREET"),                     # unit on one side
    ("1 Smith and Wesson Rd", "1 SMITH & WESSON ROAD"),             # & versus and (the key already collapses it)
    ("9 Elm Ave.", "9 elm avenue"),                                 # case, punctuation
    ("198A Bosch Blvd", "198A Bosch Blvd"),                         # SITE-011463: house number with a letter
    ("N44 W33341 Watertown Plank Rd", "N44 W33341 WATERTOWN PLANK ROAD"),  # SITE-004620: grid address
    ("One Innovation Drive", "One Innovation Dr"),                  # SITE-004431: leading number word
    ("191 American Blvd, Suite 100", "191 American Blvd Suite 100"),  # same suite on both sides
    ("191 American Blvd, Suite 100", "191 American Blvd"),          # suite on one side only
    ("1700A Old Mansfield Road", "1700A OLD MANSFIELD RD"),         # alphanumeric house number (SITE-000620)
    ("94A Dries Rd.", "94A Dries Road"),                            # SITE-002625
    ("222W 33Rd St", "222W 33RD st"),                               # SITE-008309
    ("W188 N11707 Maple Road", "W188 N11707 MAPLE ROAD"),           # Wisconsin grid (SITE-010184)
    ("N7660 Industrial Rd", "N7660 Industrial Rd"),                 # SITE-010157
    ("One Centro Way", "ONE CENTRO WAY"),                           # number word (SITE-004403)
    ("Spur 119 East", "SPUR 119 E"),                                # highway with a digit token (SITE-003175)
]
DIFFERENT = [  # true mismatches: the date must not move to this site
    ("217 Thweatt Blvd", "568 THWEATT BLVD."),                      # same street, other house number
    ("554 Moore Rd", "552 Moore Road"),                             # off by two
    ("200 INDUSTRIAL PARKWAY", "220 Park Drive"),
    ("279 Pike County Lake Road", "110 HENDERSON HWY"),             # other number and street
    ("1214 W Highway 84", "1214 W GILA BEND HWY"),                  # same number, other street
    ("33 Stiles Avenue", "33 STILES LANE"),                         # same name, other street type
    ("105 E MAPLE ST", "105 EAST MAPLE AVENUE"),
    ("1675 Navarre Rd SE", "1675 Navarre Rd SW"),                   # other direction
    ("630 US HIGHWAY 150 E", "630 US Highway 130 East"),
    ("10955 Highway 138", "10955 COUNTY ROAD 138"),                 # highway versus county road
    ("1243 170th St", "1243 270TH ST."),
    ("191 American Blvd, Suite 100", "191 American Blvd Suite 300"),            # SITE-000514: suites differ
    ("2560 White Oak Circle Suite 140", "2560 White Oak Circle Suite 120"),   # SITE-019015: suites differ
    ("4285 RIDER TRL N - SUITE 150", "4285 Rider Trail N, Suite 200"),
    ("12 Oak St Unit B", "12 Oak Street Unit C"),
]
NEVER = [  # blank and number-less streets are never equal, even to themselves
    ("", "1 Main St"), ("", ""), ("1 Main St", ""), ("P.O. Box 5", "P.O. BOX 5"),
    ("PO Box 123", "PO BOX 123"), ("P.O. Box 123", "P.O. Box 123"), ("P O Box 123", "P O BOX 123"), ("Post Office Box 123", "POST OFFICE BOX 123"),
    ("PO Box123", "PO BOX123"), ("P.O.Box 5", "P.O.Box 5"), ("POB12", "POB12"), ("Post Office Box123", "Post Office Box123"),   # no space or boundary after
    ("POB 123", "POB 123"), ("P.O.B. 123", "P.O.B. 123"), ("PO Box 123, Akron", "PO Box 123 Akron"),   # every PO box spelling, even when equal
    ("Chemical Plant Rd", "Chemical Plant Road"), ("1604 Building", "1604 Building Barth Street"),
    ("BIDA Complex Building 350, 3rd and Oak St.", "BIDA COMPLEX #350 3RD & OAK STREET"),  # equal key, no civic number (SITE-002182)
    ("Freeport Center Bldg Z-13", "FREEPORT CENTER BUILDING Z-13"),                        # building name (SITE-005976)
    ("1790 Building", "1790 Building, Washington St."),             # building name: key collapses to "1790" (SITE-003187)
    ("3206 #6 Road", "3206 #6 RD"),                                 # street_key limit: the key collapses to "3206" (SITE-003780)
]
KNOWN_MISSES = [  # real variants atlas.street_key does not collapse; rejected on purpose, listed as follow-ups in the README
    ("ONE PLASTICS DR", "1 Plastics Drive"),                        # number word
    ("1025-1055 W 8th St", "1040 W 8th St"),                        # number inside a recorded range
    ("2251/2450/2451 Dix Rd", "2450 Dix Road"),                     # number inside a recorded list
    ("1400 NE Douglas St", "1400 N.E. Douglas Street"),             # dotted direction pair
    ("1719 Hwy 72 E", "1719 US HWY 72 EAST"),                       # US prefix on a highway
    ("3500 Washington Rd", "3500 EAST WASHINGTON RD"),              # direction on one side only
    ("3425 Stanwood Blvd", "3425 STANDWOOD BLVD"),                  # one-letter misspelling
]


class SameStreet(unittest.TestCase):
    def test_same(self):
        for site, printed in SAME:
            with self.subTest(site=site, printed=printed):
                self.assertTrue(dl.same_street(site, printed))
                self.assertTrue(dl.same_street(printed, site))

    def test_different(self):
        for site, printed in DIFFERENT:
            with self.subTest(site=site, printed=printed):
                self.assertFalse(dl.same_street(site, printed))

    def test_blank_or_numberless_never_equal(self):
        for site, printed in NEVER:
            with self.subTest(site=site, printed=printed):
                self.assertFalse(dl.same_street(site, printed))

    def test_known_misses_stay_rejected(self):
        """Pins today's behaviour. If atlas.street_key is widened, these flip: move the rows to SAME on purpose."""
        for site, printed in KNOWN_MISSES:
            with self.subTest(site=site, printed=printed):
                self.assertFalse(dl.same_street(site, printed))

    def test_designators(self):  # owner split of PR #467, Codex r2 finding 2
        self.assertEqual(dl.buildings("10 Elm St Bldg. 2, Building A"), {"2", "a"})
        self.assertTrue(dl.designators_conflict("321 Oak St Building A", "321 Oak St Bldg B"))
        self.assertTrue(dl.designators_conflict("321 Oak St Suite 100", "321 Oak St Ste. 300"))
        self.assertFalse(dl.designators_conflict("321 Oak St Building A", "321 Oak St Bldg. A Ste 5"))
        self.assertFalse(dl.designators_conflict("321 Oak St", "321 Oak St Building B"))  # one-sided: no conflict
        self.assertFalse(dl.same_street("321 Oak St, Building A", "321 Oak St, Building B"))


class GenericLabels(unittest.TestCase):  # owner ruling 2026-11-22, "drop generic labels only": one test per word class
    def test_facility_words(self):
        for w in dl.GENERIC_LABELS["facility"]:
            self.assertTrue(dl.generic_label(w), w)
        self.assertTrue(dl.generic_label("plant warehouse"))
        self.assertTrue(dl.generic_label("main plant"))  # "main" added by the owner, 2026-11-22

    def test_numbers_and_ordinals(self):
        for k in ("plant 2", "plant no 2", "plant #2", "2nd plant", "plant two", "third building", "unit 4"):
            self.assertTrue(dl.generic_label(k), k)

    def test_compass_words(self):
        for w in dl.GENERIC_LABELS["compass"]:
            self.assertTrue(dl.generic_label(f"{w} plant"), w)

    def test_us_states(self):
        for k in ("ohio", "oh", "north carolina", "new york plant", "west virginia works"):
            self.assertTrue(dl.generic_label(k), k)
        self.assertFalse(dl.generic_label("puerto rico"))  # a territory is not on the list

    def test_city_and_county(self):
        self.assertTrue(dl.generic_label("dover", city="Dover"))
        self.assertTrue(dl.generic_label("tuscarawas county plant", county="Tuscarawas"))
        self.assertFalse(dl.generic_label("dover", city="Akron"))

    def test_names_are_not_labels(self):
        for k in ("tamarack", "acme polymer", "main street plastics", "bonar plastics", "polymer works", "3m dover", ""):
            self.assertFalse(dl.generic_label(k), k)


class Locality(unittest.TestCase):  # controller ruling 2026-11-22: same state, and city (either parenthetical part) or ZIP5
    def test_parenthetical_city(self):
        self.assertEqual(dl.city_keys("Cleveland (Solon)"), {"cleveland", "solon"})
        for q in ("Solon", "CLEVELAND", "solon"):
            self.assertTrue(dl.same_locality("Cleveland (Solon)", "OH", "", q, "oh", ""), q)
            self.assertFalse(dl.city_differs("Cleveland (Solon)", "", q, ""), q)
        self.assertFalse(dl.same_locality("Cleveland (Solon)", "OH", "", "Bedford", "OH", ""))
        self.assertTrue(dl.city_differs("Cleveland (Solon)", "", "Bedford", ""))

    def test_zip5(self):
        for z in ("44139", "44139-2201", "441392201", " 44139 "):
            self.assertEqual(dl.zip5(z), "44139", z)
        for z in ("", "6599", "317E6", "H4R 2P2", "4413", "00000", "00000-0000"):
            self.assertEqual(dl.zip5(z), "", z)  # unreadable ZIPs never match
        self.assertFalse(dl.same_zip5("", ""))
        self.assertTrue(dl.same_locality("Cleveland", "OH", "44139", "Bedford", "OH", "44139-2201"))
        self.assertFalse(dl.city_differs("Cleveland", "44139", "Bedford", "44139-2201"))
        self.assertTrue(dl.city_differs("Cleveland", "44139", "Bedford", "44146"))

    def test_state_is_required(self):
        self.assertFalse(dl.same_locality("Solon", "OH", "44139", "Solon", "PA", "44139"))
        self.assertFalse(dl.same_locality("Solon", "", "44139", "Solon", "", "44139"))

    def test_missing_city_is_not_contrary(self):
        self.assertFalse(dl.city_differs("", "", "Solon", ""))
        self.assertFalse(dl.city_differs("Solon", "", "", ""))
        self.assertFalse(dl.city_differs("Summit County", "", "Akron", ""))  # a county is not a city


class StrictDesignators(unittest.TestCase):  # owner ruling 2026-11-22, "strict floor" (Codex r3 finding 3); gate only
    def test_equal(self):
        for a, b in (("1 Elm St", "1 Elm St"), ("1 Elm St, Suite 100", "1 Elm St Ste. 100"), ("1 Elm St Bldg. 1-A", "1 Elm St, Bldg 1A"),
                     ("1 Elm St, 2nd Floor", "1 Elm St Fl 2"), ("1 Elm St Building # 1", "1 Elm St, Bldg 1")):
            self.assertEqual(dl.designators_compare(a, b), "equal", (a, b))

    def test_conflict(self):
        for a, b in (("1 Elm St Bldg. 1-A", "1 Elm St Bldg. 1-B"), ("1 Elm St Building North", "1 Elm St Building South"),
                     ("1 Elm St Unit A", "1 Elm St Unit. B"), ("1 Elm St Room 1", "1 Elm St Rm. 2")):
            self.assertEqual(dl.designators_compare(a, b), "conflict", (a, b))

    def test_unequal_is_neither(self):
        for a, b in (("1 Elm St, Suite 100", "1 Elm St"), ("1 Elm St #12", "1 Elm St, Unit 12"), ("1 Elm St Suite", "1 Elm St Suite")):
            self.assertEqual(dl.designators_compare(a, b), "unequal", (a, b))  # one-sided, other kind, or unreadable

    def test_same_street_reads_whole_building(self):
        self.assertEqual(dl.buildings("15 Larch Way, Bldg. 1-A"), {"1a"})
        self.assertFalse(dl.same_street("15 Larch Way, Bldg. 1-A", "15 Larch Way, Bldg. 1-B"))

    def test_zip_forms_and_parenthetical_labels(self):
        for z in ("44706 1594", "44706-", "44706-1594", "447061594"):
            self.assertEqual(dl.zip5(z), "44706", z)
        self.assertTrue(dl.generic_label("solon", city="Cleveland (Solon)"))
        self.assertTrue(dl.generic_label("cleveland", city="Cleveland (Solon)"))


class CorporateForm(unittest.TestCase):
    """Owner ruling 2026-11-22: a held name plus corporate-form words only."""

    def test_admits_corporate_form_words_only(self):
        from atlas import name_key
        held = name_key("Acme Polymer")
        for q in ("Acme Polymer USA", "Acme Polymer, L.L.C.", "Acme Polymer U.S. Holdings", "Acme Polymer North America",
                  "Acme Polymer Group Ltd", "Acme Polymer Americas LP"):
            self.assertTrue(dl.corporate_form_extension(held, name_key(q)), q)
        for q in ("Acme Polymer Services", "Acme Polymer Fleet Services LLC", "Acme Polymer North", "Acme Polymers USA",
                  "Acme Polymer", "Acme", "Other Acme Polymer USA", "Acme Polymer USA Plant 2"):
            self.assertFalse(dl.corporate_form_extension(held, name_key(q)), q)


if __name__ == "__main__":
    unittest.main()
