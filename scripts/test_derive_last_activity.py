#!/usr/bin/env python3
"""Tests for scripts/derive_last_activity.py: the street test that gates every derived last_activity row, and a
fixture derivation. Run from the repo root:  python3 -m unittest scripts/test_derive_last_activity.py"""
import csv
import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("derive_last_activity", HERE / "derive_last_activity.py")
dl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dl)

SAME = [  # equal atlas.street_key
    ("5020 Enterprise Parkway", "5020 ENTERPRISE PKWY"),            # suffix abbreviation
    ("5101 21ST ST", "5101 21st Street"),                           # ordinal, suffix
    ("1719 Hwy 72 E", "1719 Hwy 72 East"),                          # direction word
    ("100 Main St Suite 4", "100 MAIN STREET"),                     # unit on one side
    ("1 Smith and Wesson Rd", "1 SMITH & WESSON ROAD"),             # & versus and (the key already collapses it)
    ("9 Elm Ave.", "9 elm avenue"),                                 # case, punctuation
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
]
NEVER = [  # blank and number-less streets are never equal, even to themselves
    ("", "1 Main St"), ("", ""), ("1 Main St", ""), ("P.O. Box 5", "P.O. BOX 5"),
    ("Chemical Plant Rd", "Chemical Plant Road"), ("1604 Building", "1604 Building Barth Street"),
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


class Derive(unittest.TestCase):
    def test_only_same_street_rows_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "data").mkdir()
            with open(tmp / "data/sites_OH.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["site_id", "street_address", "last_activity_date", "last_activity_source"])
                for sid, st in (("SITE-1", "10 Main St"), ("SITE-2", "20 Oak Ave"), ("SITE-3", ""), ("SITE-4", "5 Elm Rd")):
                    w.writerow([sid, st, "", ""])
            cols = ["record_id", "street_as_printed", "witness_date_latest", "match_tier"]
            ex = tmp / "ex.csv"
            with open(ex, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerow(["SITE-1", "10 MAIN STREET", "2024-05-01", "A"])       # same street: applied
                w.writerow(["SITE-2", "99 OAK AVENUE", "2024-05-01", "A"])        # other number: rejected
                w.writerow(["SITE-3", "1 ANY ST", "2024-05-01", "A"])             # blank site street: rejected
                w.writerow(["SITE-4", "5 ELM ROAD", "2024-05-01", "B"])           # tier B: excluded
            ita = tmp / "ita.csv"
            with open(ita, "w", newline="") as f:
                csv.writer(f).writerows([cols, ["SITE-2", "20 OAK AVE", "2023", "A"]])   # ITA: year precision
            best, stats, rejected, _files, _streets = dl.derive(tmp / "data", ex, ita)
            self.assertEqual(set(best), {"SITE-1", "SITE-2"})
            self.assertEqual(best["SITE-1"][0], date(2024, 5, 1))
            self.assertEqual(best["SITE-2"][:2], (date(2023, 12, 31), "osha_ita"))
            self.assertEqual(sorted(r[0] for r in rejected if r[1] == "inspection"), ["SITE-2", "SITE-3"])
            self.assertEqual(stats["inspection"], (1, 1, 2))


if __name__ == "__main__":
    unittest.main()
