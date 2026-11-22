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


if __name__ == "__main__":
    unittest.main()
