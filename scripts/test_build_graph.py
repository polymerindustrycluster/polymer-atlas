#!/usr/bin/env python3
"""Tests for scripts/build_graph.py: privacy whitelist, tag vocabulary, edge integrity.

Run from the repo root:  python3 -m unittest scripts/test_build_graph.py
"""
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("build_graph", HERE / "build_graph.py")
bg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bg)

# AGENTS.md section 6: only these public fields may reach the page
ALLOWED = {"id", "k", "g", "l", "r", "c", "s", "n", "oh", "p", "m", "w", "d", "x"}


class BuildGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.edges = bg.build_graph()

    def test_only_whitelisted_fields(self):
        extra = {k for n in self.nodes for k in n} - ALLOWED
        self.assertEqual(extra, set(), f"non-whitelisted fields written to the page: {extra}")

    def test_no_people_or_notes(self):
        blob = json.dumps(self.nodes)
        self.assertNotIn("PERSON-", blob)
        self.assertNotRegex(blob, r"\bCRM\b")
        self.assertNotRegex(blob, r"(?<![A-Za-z])working/")  # workshop paths live only in notes/sources

    def test_vocabulary_tags_are_in_vocabulary(self):
        voc = bg.vocab()
        for n in self.nodes:
            if n["k"] in voc and not n.get("x"):
                self.assertIn(n["id"].split(":", 1)[1], voc[n["k"]], n["id"])

    def test_edges_reference_nodes_and_are_unique(self):
        self.assertEqual(len(self.edges), len(set(self.edges)))
        for i, j, t in self.edges:
            self.assertTrue(0 <= i < j < len(self.nodes), (i, j, t))

    def test_page_renders(self):
        html = bg.page(self.nodes[:5], [], fragment=True)
        self.assertTrue(html.startswith("<title>"))
        self.assertNotIn("__DATA__", html)


class GeoAndEventsTests(unittest.TestCase):
    """The map hybrid and the 3D events page reuse build_graph(); check their own outputs."""

    @classmethod
    def setUpClass(cls):
        def load(name):
            spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m
        cls.geo = load("build_geo_graph").build_data()
        cls.ev = load("build_events_3d").build_data()

    def test_geo_fields_whitelisted(self):
        self.assertEqual({k for s in self.geo["sites"] for k in s} - {"n", "o", "c", "s", "y", "p", "la", "lo"}, set())
        self.assertEqual({k for o in self.geo["orgs"] for k in o} - {"id", "l", "r", "c", "s", "w", "d", "m", "t"}, set())
        self.assertNotRegex(json.dumps(self.geo), r"\bCRM\b")

    def test_geo_refs_valid(self):
        n_o, n_t = len(self.geo["orgs"]), len(self.geo["tags"])
        for s in self.geo["sites"]:
            self.assertTrue(0 <= s["o"] < n_o)
            self.assertTrue(-90 <= s["la"] <= 90 and -180 <= s["lo"] <= 180)
        for o in self.geo["orgs"]:
            self.assertTrue(all(0 <= t < n_t for t in o["t"]))

    def test_events_links_and_fields(self):
        ids = {n["id"] for n in self.ev["nodes"]}
        self.assertEqual(len(ids), len(self.ev["nodes"]))
        for l in self.ev["links"]:
            self.assertIn(l["source"], ids)
            self.assertIn(l["target"], ids)
            self.assertIn(l["role"], {"exhibitor", "sponsor", "speaker", "organizer", "host", "attendee"})  # SCHEMA 4.12.2 role enum (v1.12)
        self.assertNotIn("PERSON-", json.dumps(self.ev))


if __name__ == "__main__":
    unittest.main()
