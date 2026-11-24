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


def real_descriptions():
    """Every description_1line in the canonical organization, ecosystem and program rows."""
    csv.field_size_limit(10**9)
    data = Path(build_site.__file__).resolve().parent.parent / "data"
    out = {}
    for path in sorted(data.glob("organizations_*.csv")) + [data / "ecosystem.csv", data / "programs.csv"]:
        if path.name.endswith("_all.csv"):
            continue
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("description_1line"):
                    out[r.get("org_id") or r.get("program_id")] = r["description_1line"]
    return out


class ProcessLexiconTests(unittest.TestCase):
    """ATLAS-40 lexicon pass: process wording is withheld by the one shared test, or allowed with a reason (tasks/site-lexicon-2026-11-23)."""

    FAMILIES = {
        "verification timing": ["Own site live at verification: injection molding", "Company site crawled the day of verification lists the plant",
                                "Thomasnet pages crawled within the last six months", "directory verified from the operator's facility list"],
        "settling": ["Own website settles identity and product line", "Identity and activity settled by own site", "Two primary government witnesses plus the filing",
                     "Polymer line witnessed on own domain"],
        "workflow": ["CHANGED (VERIFIED C -> B). Retry 2026-10-29: the domain still fails", "Own site fetched live 2026-10-29 lists this address",
                     "Re-fetch of the own site returned HTTP 403 this session", "so the verdict rests on dated government evidence", "TODO confirm the address"],
        "tier": ["No own site found. Tier C: identity from a directory", "Own site prints no street address, capping tier at C", "tier held at B on the recorded site"],
        "opened": ["Own website (opened): 'CUSTOM PLASTIC INJECTION MOLDING'", "Own site opened: custom sheet fabrication", "Own website (opened in full): est. 1946",
                   "Own site (live, opened 2026-10-29): ISO 9001:2015 certified"],
        "ladder and pass": ["passes the Ring 3 general-engineering gate on a claimed specialty", "Own site in full: manufactures bollard covers", "(carried at course grain as PROG-000034)"],
    }
    ORDINARY = ["Tier-1 automotive supplier of interior trim", "Privately held maker of intensive-use furniture", "The plant opened in 1995 and holds OSHA VPP Star status",
                "Trinseo opened its North America Innovation Center in Exton", "OSHA inspection 1717099.015 (opened Dec 18, 2023) inspected the plant",
                "expert witness consulting", "A Thomas Verified supplier profile", "Lane's own literature lists a Carlisle facility", "Anti-slip step and ladder covers",
                "Small-batch maker of coatings", "Clinical-stage development of antimicrobial coatings"]

    def test_each_family_is_withheld_by_the_one_shared_test(self):
        for family, texts in self.FAMILIES.items():
            for text in texts:
                self.assertTrue(build_site.internal_wording(text), (family, text))
                self.assertTrue(build_site.release_withheld("organizations", "description_1line", text), text)
                self.assertIn("withheld", build_site.lede(text), text)

    def test_ordinary_uses_pass(self):
        for text in self.ORDINARY:
            self.assertFalse(build_site.internal_wording(text), text)

    def test_no_shown_description_has_an_unclassified_process_word(self):
        """The wider watch list over every real description: a hit must be withheld or covered by PROSE_ALLOW."""
        stray = {k: build_site.unclassified_process_words(v) for k, v in real_descriptions().items() if build_site.unclassified_process_words(v)}
        self.assertEqual(stray, {})

    def test_every_allow_entry_has_a_reason_and_is_used_on_a_real_description(self):
        descriptions = [v for v in real_descriptions().values() if not build_site.internal_wording(v)]
        for rx, why in build_site.PROSE_ALLOW:
            self.assertTrue(why.strip(), rx.pattern)
            self.assertTrue(any(rx.search(v) for v in descriptions), f"unused allowance: {why}")          # a stale entry dies here

    def test_named_records_are_withheld(self):
        d = real_descriptions()
        for org in ("ORG-001997", "ORG-002044", "ORG-002045", "ORG-002178", "ORG-002201", "ORG-002204", "ORG-001714", "ORG-001715", "ORG-001719",
                    "ORG-001720", "ORG-001722", "ORG-001922", "ORG-003111"):
            self.assertTrue(build_site.internal_wording(d[org]), org)

    def test_a_role_line_with_build_wording_falls_back_to_the_vocabulary_role(self):
        self.assertEqual(build_site.published_role({"role_as_published": "Professor of Chemistry", "role": "professor"}), "Professor of Chemistry")
        self.assertEqual(build_site.published_role({"role_as_published": "Professor. Both pages fetched/searched 2026-11-04.", "role": "professor"}), "professor")
        self.assertEqual(build_site.published_role({"role_as_published": "", "role": "research_staff"}), "research staff")

    def test_a_withheld_description_is_also_withheld_where_it_is_copied_without_its_temporary_id(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        db = d / "x.db"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE organizations (org_id TEXT, description_1line TEXT, notes TEXT)")
        con.execute("INSERT INTO organizations VALUES ('O1', 'Singapore tire group parent of Giti Tire (USA) Ltd. in Ohio (NEW:MJ-07).', '')")
        con.execute("INSERT INTO organizations VALUES ('O2', 'Fine.', 'Designed endpoint parent: Singapore tire group parent of Giti Tire (USA) Ltd. in Ohio')")
        con.commit()
        con.close()
        held = export_release.held_pattern(db)
        self.assertEqual(export_release.withhold_db(db, held), 2)
        con = sqlite3.connect(db)
        self.assertEqual(con.execute("SELECT notes FROM organizations WHERE org_id='O2'").fetchone()[0], "")
        con.close()


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
        with (out / "organizations_all.csv").open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([r["org_id"] for r in rows], ["ORG-1", "ORG-2", "ORG-3", "ORG-4"])   # rows are kept; only cells are blanked
        self.assertEqual(rows[0]["description_1line"], "")
        for p, before in canonical.items():
            self.assertEqual(p.read_bytes(), before)                          # the canonical inputs are untouched

    def test_a_withheld_evidence_cell_in_a_csv_reads_the_marker_and_the_row_stays_complete(self):
        p = self.dir / "evidence_all.csv"
        write(p, ["evidence_id", "claim_detail", "source_ref", "tier_effect"], [["E1", "legal name for NEW:CSW", "https://example.org/x", "supports_A"], ["E2", "ok", "PKT-1 NEW:A-12", "supports_C"]])
        self.assertEqual(export_release.withhold_csv(p, "evidence"), 2)
        with p.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
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
