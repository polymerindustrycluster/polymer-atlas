#!/usr/bin/env python3
"""Tests for scripts/site_skyline.py (home-page 3D skyline data).

The key property: albers_usa() must reproduce d3.geoAlbersUsa so site points land
inside the vendored us-atlas state shapes. Run: python3 -m unittest scripts/test_site_skyline.py
"""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("site_skyline", HERE / "site_skyline.py")
sk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sk)
PIC12 = {"Ashtabula", "Cuyahoga", "Geauga", "Lake", "Lorain", "Mahoning", "Medina", "Portage", "Stark", "Summit",
         "Trumbull", "Wayne"}


class SkylineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = sk.topology_lines(PIC12)

    def test_projection_matches_us_atlas(self):
        for lon, lat in [(-81.519, 41.081), (-84.512, 39.103), (-80.65, 41.10), (-83.0, 40.0)]:  # Akron, Cincinnati, Youngstown, Columbus
            self.assertTrue(sk.point_in_rings(*sk.albers_usa(lon, lat), self.lines["ohio_rings"]), (lon, lat))
        for lon, lat in [(-79.996, 40.441), (-83.046, 42.331), (-87.63, 41.88)]:          # Pittsburgh, Detroit, Chicago
            self.assertFalse(sk.point_in_rings(*sk.albers_usa(lon, lat), self.lines["ohio_rings"]), (lon, lat))

    def test_outside_lower48_is_skipped(self):
        self.assertIsNone(sk.albers_usa(-149.9, 61.2))   # Anchorage
        self.assertIsNone(sk.albers_usa(-157.85, 21.3))  # Honolulu
        self.assertIsNone(sk.albers_usa(2.35, 48.85))    # Paris

    def test_hexbins_conserve_counts(self):
        pts = [(100 + i % 50, 200 + i % 30, "1", "Akron", "OH", True) for i in range(500)]
        hexes = sk.hexbins(pts, 7.0)
        self.assertEqual(sum(h[2] for h in hexes), 500)
        self.assertEqual(hexes, sorted(hexes, key=lambda h: -h[2]))

    def test_payload_fields(self):
        sites = [{"latitude": "41.081", "longitude": "-81.519", "city": "AKRON", "state": "OH", "county": "Summit", "_ring": "1"},
                 {"latitude": "61.2", "longitude": "-149.9", "city": "Anchorage", "state": "AK", "county": "", "_ring": "1"},
                 {"latitude": "", "longitude": "", "city": "X", "state": "OH", "county": "Summit", "_ring": "1"}]
        p = sk.payload(sites, lambda s: s["_ring"], PIC12)
        self.assertEqual(p["n"], 1)
        self.assertEqual(p["outside_frame"], 1)
        self.assertEqual(p["hex"][0][4], 1)          # PIC-12 flag
        self.assertIn("Akron, OH", p["hex"][0][5])
        self.assertTrue(p["borders"] and p["pic12"])


if __name__ == "__main__":
    unittest.main()
