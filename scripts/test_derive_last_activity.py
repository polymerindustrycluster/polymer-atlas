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
            with open(tmp / "data/sites_OH.csv", "a", newline="") as f:
                csv.writer(f).writerow(["SITE-5", "2560 White Oak Circle Suite 140", "", ""])
            with open(ex, "a", newline="") as f:
                csv.writer(f).writerow(["SITE-5", "2560 White Oak Circle Suite 140", "2022-05-13", "A"])   # same suite: applied
            with open(ita, "a", newline="") as f:
                csv.writer(f).writerow(["SITE-5", "2560 White Oak Circle Suite 120", "2023", "A"])        # other suite: rejected
            best, stats, rejected, _files, _streets = dl.derive(tmp / "data", ex, ita)
            self.assertEqual(set(best), {"SITE-1", "SITE-2", "SITE-5"})
            self.assertEqual(best["SITE-5"][:2], (date(2022, 5, 13), "osha_inspection"))
            self.assertEqual(best["SITE-1"][0], date(2024, 5, 1))
            self.assertEqual(best["SITE-2"][:2], (date(2023, 12, 31), "osha_ita"))
            self.assertEqual(sorted(r[0] for r in rejected if r[1] == "inspection"), ["SITE-2", "SITE-3"])
            self.assertEqual(stats["inspection"], (2, 1, 2))


if __name__ == "__main__":
    unittest.main()
