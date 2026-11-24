#!/usr/bin/env python3
"""The downloadable release withholds what the site withholds (ATLAS-40 round 2, finding 1).

    python3 -m unittest scripts/test_site_release.py
"""
import csv
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site  # noqa: E402
import export_release  # noqa: E402

HELD_DESC = "Designed endpoint parent (verification wave 1, lane CF adjudication s4): Fixture Co."
HELD_NOTE = "Source: list. see NEW:HUNTSMAN:S05 in running text (L5 packet) and more"
TOKEN = "NEW:AB-12"
OK_DESC = "Injection molder of automotive parts."
OK_NOTE = "Created from the company site in an integration pass."   # ordinary note wording is not withheld: only descriptions and temporary ids


def write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


class ReleaseWithholdingTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.dir = Path(d.name)

    def test_the_test_is_the_sites_test(self):
        for table, field, value, held in (
                ("organizations", "description_1line", HELD_DESC, True), ("organizations", "description_1line", OK_DESC, False),
                ("ecosystem", "description_1line", "Exists only in the PIC CRM record.", True),
                ("organizations", "notes", HELD_NOTE, True), ("sites", "notes", OK_NOTE, False),
                ("inclusion_log", "entity", TOKEN, True), ("evidence", "claim_detail", f"see {TOKEN}", True),
                ("evidence", "notes", "NEW:HUNTSMAN:S05 sits in an evidence note", True),
                ("evidence", "claim_detail", "legal name for NEW:CSW", True), ("evidence", "notes", "duplicate design NEW:L4-12.", True),
                ("evidence", "claim_detail", "see NEW:A-12", True), ("sites", "notes", "NEWSITE:X-1 pending", True),
                ("sites", "notes", "", False)):
            self.assertEqual(build_site.release_withheld(table, field, value), held, (table, field, value))

    def test_planted_values_are_absent_from_every_csv_and_the_sqlite_and_a_normal_value_survives(self):
        org = self.dir / "organizations_all.csv"
        write(org, ["org_id", "legal_name", "description_1line", "notes"],
              [["ORG-1", "A", HELD_DESC, OK_NOTE], ["ORG-2", "B", OK_DESC, HELD_NOTE], ["ORG-3", "C", OK_DESC, f"x {TOKEN} y"],
               ["ORG-4", "D", OK_DESC, f"Earlier text: {HELD_DESC}"]])
        log = self.dir / "inclusion_log.csv"
        write(log, ["entity", "notes"], [[TOKEN, "n"], ["ORG-9", OK_NOTE]])
        db = self.dir / "polymer-atlas.db"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE organizations (org_id TEXT, description_1line TEXT, notes TEXT)")
        con.executemany("INSERT INTO organizations VALUES (?,?,?)", [("ORG-1", HELD_DESC, OK_NOTE), ("ORG-2", OK_DESC, HELD_NOTE), ("ORG-3", OK_DESC, f"x {TOKEN} y"), ("ORG-4", OK_DESC, f"Earlier text: {HELD_DESC}")])
        con.execute("CREATE TABLE evidence (evidence_id TEXT, claim_detail TEXT, source_ref TEXT, tier_effect TEXT)")
        con.executemany("INSERT INTO evidence VALUES (?,?,?,?)", [("EVD-1", f"claim {TOKEN}", "https://example.org/a", "supports_A"),
                                                                  ("EVD-2", "ordinary claim", "PKT-020 org design NEW:superior-sto", "supports_C")])
        con.execute("CREATE TABLE sites (site_id TEXT, notes TEXT)")                       # a held description pasted whole into another record's notes
        con.executemany("INSERT INTO sites VALUES (?,?)", [("SITE-1", f"Operator text: {HELD_DESC} (copied)"), ("SITE-2", OK_NOTE)])
        con.commit()
        con.close()
        canonical = {p: p.read_bytes() for p in (org, log, db)}
        out = self.dir / "release"
        out.mkdir()
        for p in (org, log, db):
            (out / p.name).write_bytes(p.read_bytes())
        held = export_release.held_pattern(out / "polymer-atlas.db")
        self.assertIsNotNone(held)
        self.assertRegex(f"x {HELD_DESC} y", held)
        self.assertEqual(export_release.withhold_csv(out / "organizations_all.csv", "organizations", held), 4)   # held description, held note, note with a token, note holding a copy
        self.assertEqual(export_release.withhold_csv(out / "inclusion_log.csv", "inclusion_log", held), 1)       # the token in `entity`
        self.assertEqual(export_release.withhold_db(out / "polymer-atlas.db", held), 7)                          # the four organization cells, the two evidence cells and the site note holding a copy
        zpath = self.dir / "bundle.zip"
        with zipfile.ZipFile(zpath, "w") as z:
            for p in sorted(out.iterdir()):
                z.write(p, p.name)
        with zipfile.ZipFile(zpath) as z:
            blobs = {m: z.read(m) for m in z.namelist()}
        for member, blob in blobs.items():
            for planted in (HELD_DESC, "NEW:HUNTSMAN:S05", TOKEN, "verification wave", "Fixture Co."):
                self.assertNotIn(planted.encode(), blob, (member, planted))      # CSVs and the SQLite file, including its free pages
        self.assertIn(OK_DESC.encode(), blobs["organizations_all.csv"])
        self.assertIn(OK_NOTE.encode(), blobs["organizations_all.csv"])
        self.assertIn(OK_DESC.encode(), blobs["polymer-atlas.db"])
        con = sqlite3.connect(out / "polymer-atlas.db")
        for evd, claim, ref, tier in con.execute("SELECT * FROM evidence ORDER BY evidence_id"):
            self.assertTrue(claim and ref, evd)                              # a graded evidence row keeps both required fields (SCHEMA 4.13, V-22)
            self.assertTrue(tier.startswith("supports_"), evd)
        self.assertEqual(con.execute("SELECT claim_detail, source_ref FROM evidence WHERE evidence_id='EVD-1'").fetchone(), (export_release.WITHHELD, "https://example.org/a"))
        self.assertEqual(con.execute("SELECT source_ref FROM evidence WHERE evidence_id='EVD-2'").fetchone()[0], export_release.WITHHELD)
        self.assertEqual(con.execute("SELECT description_1line FROM organizations WHERE org_id='ORG-1'").fetchone()[0], "")   # outside evidence the cell is blank
        con.close()
        rows = list(csv.DictReader((out / "organizations_all.csv").open(newline="", encoding="utf-8")))
        self.assertEqual([r["org_id"] for r in rows], ["ORG-1", "ORG-2", "ORG-3", "ORG-4"])   # rows are kept; only cells are blanked
        self.assertEqual(rows[0]["description_1line"], "")
        for p, before in canonical.items():
            self.assertEqual(p.read_bytes(), before)                          # the canonical inputs are untouched

    def test_a_withheld_evidence_cell_in_a_csv_reads_the_marker_and_the_row_stays_complete(self):
        p = self.dir / "evidence_all.csv"
        write(p, ["evidence_id", "claim_detail", "source_ref", "tier_effect"], [["E1", "legal name for NEW:CSW", "https://example.org/x", "supports_A"], ["E2", "ok", "PKT-1 NEW:A-12", "supports_C"]])
        self.assertEqual(export_release.withhold_csv(p, "evidence"), 2)
        rows = list(csv.DictReader(p.open(newline="", encoding="utf-8")))
        for r in rows:
            self.assertTrue(r["claim_detail"] and r["source_ref"], r)
        self.assertEqual((rows[0]["claim_detail"], rows[1]["source_ref"]), (export_release.WITHHELD, export_release.WITHHELD))

    def test_a_file_with_nothing_to_withhold_keeps_its_exact_bytes(self):
        p = self.dir / "programs.csv"
        write(p, ["program_id", "notes"], [["P1", OK_NOTE]])
        before = p.read_bytes()
        self.assertEqual(export_release.withhold_csv(p, "programs"), 0)
        self.assertEqual(p.read_bytes(), before)

    def test_main_applies_it_to_every_copy(self):
        src = (Path(export_release.__file__)).read_text(encoding="utf-8")
        self.assertIn('withhold_db(RELEASE / "polymer-atlas.db", held)', src)
        self.assertEqual(src.count("withhold_csv(RELEASE"), 2)              # merged exports and single tables
        self.assertEqual(src.count("withhold_csv(RELEASE / path, t, held)") + src.count('f"{t}.csv", t, held)'), 2)   # the held-value pattern reaches every call
        self.assertIn("Cells blanked:", src)


if __name__ == "__main__":
    unittest.main()
