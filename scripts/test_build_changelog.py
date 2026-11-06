"""Known-answer and adversarial change-feed checks against throwaway Git repositories."""
import csv
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_changelog as feed

ORG_FIELDS = ["org_id", "status", "verification_tier", "notes", "sources"]
SITE_FIELDS = ["site_id", "operating_status", "verification_tier", "notes"]
EVD_FIELDS = ["evidence_id", "record_table", "claim_detail", "notes"]
SECRET = "PRIVATE_CRM_NOTE person@example.com 216-555-0199"


class ChangeFeedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "SECRET_AUTHOR")
        self.git("config", "user.email", "private@example.com")
        self.org = ["ORG-000001", "active", "C", SECRET, "mailto:person@example.com"]
        self.site = ["SITE-000001", "unknown", "C", SECRET]
        self.evidence = ["EVD-000001", "sites", SECRET, SECRET]
        self.write("organizations_OH", ORG_FIELDS, [self.org])
        self.write("sites_OH", SITE_FIELDS, [self.site])
        self.write("evidence_sites_OH", EVD_FIELDS, [self.evidence])
        self.commit("PRIVATE_INITIAL_MESSAGE")

    def git(self, *args):
        return feed.git(self.repo, *args)

    def write(self, name, fields, rows):
        path = self.repo / "data" / (name + ".csv")
        path.parent.mkdir(exist_ok=True)
        with path.open("w", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(fields); writer.writerows(rows)

    def commit(self, message):
        self.git("add", "data")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD").strip()

    def test_known_answers_merge_net_diffs_privacy_and_moves(self):
        self.git("switch", "-c", "SECRET_BRANCH")
        self.org[2] = "B"
        self.write("organizations_OH", ORG_FIELDS, [self.org])
        self.commit("PRIVATE_INTERMEDIATE_MESSAGE")
        self.org[1:3] = ["closed", "A"]
        org2 = ["ORG-000002", "active", "C", SECRET, ""]
        self.write("organizations_OH", ORG_FIELDS, [org2, self.org])
        self.git("mv", "data/organizations_OH.csv", "data/organizations_PA.csv")
        self.write("evidence_organizations_PA", EVD_FIELDS, [["EVD-000002", "organizations", SECRET, SECRET]])
        self.commit("PRIVATE_FINAL_MESSAGE")
        self.git("switch", "main")
        self.git("merge", "--no-ff", "SECRET_BRANCH", "-m", "Merge pull request #7 from SECRET_BRANCH")

        self.git("switch", "-c", "SECRET_UNMERGED")
        self.write("equipment", ["equipment_id", "notes"], [["EQP-999999", SECRET]])
        self.commit("UNMERGED_PRIVATE_MESSAGE")
        self.git("switch", "main")
        # A notes-only commit stays an honest zero-category entry, without publishing the note.
        self.org[3] += " NEW_SECRET"
        self.write("organizations_PA", ORG_FIELDS, [self.org, org2])
        self.commit("PRIVATE_NOTES_MESSAGE")
        self.git("switch", "-c", "SECRET_SQUASH")
        self.write("sites_OH", SITE_FIELDS, [self.site, ["SITE-000002", "active", "B", SECRET]])
        self.commit("SECRET_SQUASH_SOURCE")
        self.git("switch", "main")
        self.git("merge", "--squash", "SECRET_SQUASH")
        self.git("commit", "-m", "PRIVATE_SQUASH_TITLE (#8)")

        # A unique ORG-id type transfer is a continuing row, not a fresh entity.
        self.write("organizations_PA", ORG_FIELDS, [self.org])
        self.write("ecosystem", ORG_FIELDS, [org2])
        self.commit("SECRET_TYPE_TRANSFER")
        entries = feed.build(self.repo, "main")
        root, merged, notes, squashed, moved = entries
        # Three hand-known outcomes: new org2, one net active→closed, one C→A (not C→B→A).
        self.assertEqual([(r["table"], r["id"]) for r in merged["created"]], [("organizations", "ORG-000002")])
        self.assertEqual([(a, b) for _, a, b in merged["status"]], [("active", "closed")])
        self.assertEqual([(a, b) for _, a, b in merged["tier"]], [("C", "A")])
        self.assertEqual(dict(merged["evidence"]), {"organizations": 1})
        self.assertEqual(len(root["created"]), 2)
        self.assertEqual(dict(root["evidence"]), {"sites": 1})
        self.assertEqual([r["id"] for r in squashed["created"]], ["SITE-000002"])
        self.assertEqual([e["pr"] for e in entries], [None, "7", None, "8", None])
        for entry in [notes, moved]:
            self.assertTrue(all(not entry[k] for k in ["created", "restored", "removed", "status", "tier", "evidence"]))

        md = (self.repo / "build/changelog/CHANGELOG.md").read_bytes()
        xml = (self.repo / "build/changelog/feed.xml").read_bytes()
        for secret in [SECRET, "SECRET", "PRIVATE", "person@example.com", "216-555-0199", "EQP-999999"]:
            self.assertNotIn(secret.encode(), md + xml)
        parsed = ET.fromstring(xml)
        atom = {"a": feed.ATOM}
        self.assertEqual(len(parsed.findall("a:entry", atom)), 5)
        ids = [e.find("a:id", atom).text for e in parsed.findall("a:entry", atom)]
        self.assertEqual(len(set(ids)), 5)
        self.assertIn("PR #7", md.decode())
        self.assertIn("1 evidence rows", md.decode())
        self.assertIn("(no PR recorded)", md.decode())
        feed.build(self.repo, "main")
        self.assertEqual(md, (self.repo / "build/changelog/CHANGELOG.md").read_bytes())
        self.assertEqual(xml, (self.repo / "build/changelog/feed.xml").read_bytes())

    def test_composite_keys_restorations_and_unrecognized_values(self):
        fields = ["org_id", "registry", "registry_id", "site_id", "notes"]
        self.write("registry_links", fields, [
            ["ORG-000001", "UEI", "FIRST", "", SECRET],
            ["ORG-000001", "UEI", "SECOND", "", SECRET],
            ["ORG-000001", "UEI", "FIRST", "SITE-000001", SECRET]])
        self.write("people_identifiers", ["person_id", "identifier_type", "identifier_id"],
                   [["PERSON-000001", "ORCID", "FIRST"], ["PERSON-000001", "ORCID", "SECOND"]])
        self.write("archive_links", ["evidence_id", "archive_ref"], [["EVD-000001", SECRET]])
        self.commit("LINKS")
        self.write("organizations_OH", ORG_FIELDS, [])
        self.write("evidence_sites_OH", EVD_FIELDS, [])
        self.commit("REMOVE")
        self.write("organizations_OH", ORG_FIELDS, [self.org])
        self.write("evidence_sites_OH", EVD_FIELDS, [self.evidence])
        self.commit("RESTORE")
        self.org[1] = SECRET
        self.org[2] = SECRET
        self.write("organizations_OH", ORG_FIELDS, [self.org])
        self.commit("REDACT")
        self.org[1:3] = ["", ""]
        self.write("organizations_OH", ORG_FIELDS, [self.org])
        self.commit("BLANK_TRANSITION")
        entries = feed.build(self.repo, "main")
        self.assertEqual(len(entries[1]["created"]), 6)
        self.assertEqual(len(entries[2]["removed"]), 2)
        self.assertEqual(len(entries[3]["restored"]), 2)
        self.assertFalse(entries[3]["created"])
        self.assertFalse(entries[3]["evidence"])
        text = (self.repo / "build/changelog/CHANGELOG.md").read_text()
        self.assertIn("ORG-000001 (3 rows)", text)
        self.assertIn("(unrecognized)", text)
        self.assertIn("(blank)", text)
        self.assertEqual(entries[-1]["status"][0][2], "")
        self.assertEqual(entries[-1]["tier"][0][2], "")
        self.assertNotIn(SECRET, text)
        self.assertNotIn("FIRST", text)

    def test_conflicting_rows_and_invalid_ids_fail_before_output(self):
        feed.build(self.repo, "main")
        out = self.repo / "build/changelog"
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        self.write("organizations_OH", ORG_FIELDS, [self.org, ["ORG-000001", "closed", "A", SECRET, ""]])
        self.commit("CONFLICT")
        with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
            feed.build(self.repo, "main")
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
        with self.assertRaisesRegex(ValueError, "invalid immutable ID"):
            feed.read_rows("data/equipment.csv", "equipment_id,notes\nprivate@example.com,hidden\n")
        with self.assertRaisesRegex(ValueError, "malformed CSV"):
            feed.read_rows("data/equipment.csv", "equipment_id,notes\nEQP-000001,hidden,extra\n")
        with self.assertRaisesRegex(ValueError, "unsupported data CSV"):
            feed.read_rows("data/private.csv", "secret\nhidden\n")
        with self.assertRaisesRegex(ValueError, "unsupported evidence target"):
            feed.read_rows("data/evidence_sites_OH.csv", "evidence_id,record_table\nEVD-000001,private\n")
        with self.assertRaisesRegex(ValueError, "missing key columns"):
            feed.read_rows("data/equipment.csv", "notes\nORG-000001\n")
        with self.assertRaisesRegex(ValueError, "missing key columns"):
            feed.read_rows("data/registry_links.csv", "org_id,notes\nORG-000001,hidden\n")
        self.assertIsNone(feed.table_of("data/organizations_all.csv"))
        self.assertIsNone(feed.table_of("data/inclusion_log.csv"))

    def test_legacy_cross_table_collisions_remain_distinct(self):
        self.write("ecosystem", ORG_FIELDS, [["ORG-000001", "active", "B", SECRET, ""]])
        self.commit("LEGACY_COLLISION")
        entries = feed.build(self.repo, "main")
        self.assertEqual([(r["table"], r["id"]) for r in entries[-1]["created"]],
                         [("ecosystem", "ORG-000001")])
        self.assertFalse(entries[-1]["tier"])
        self.assertFalse(entries[-1]["removed"])

    def test_shallow_history_and_output_symlink_refused(self):
        clone = Path(self.tmp.name) / "shallow"
        self.git("clone", "--depth=1", "--branch=main", self.repo.as_uri(), str(clone))
        with self.assertRaisesRegex(ValueError, "full main history required"):
            feed.build(clone, "main")
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.repo / "build").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "output must stay"):
            feed.build(self.repo, "main")
        self.assertEqual(list(outside.iterdir()), [])

    def test_table_namespaces_reject_private_and_wrong_table_ids(self):
        feed.build(self.repo, "main")
        out = self.repo / "build/changelog"
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        for ident in ["PRIVATE_CRM_ACQUISITION_TARGET-000002", "EQP-000002"]:
            with self.subTest(ident=ident):
                self.write("organizations_OH", ORG_FIELDS,
                           [self.org, [ident, "active", "C", "", ""]])
                self.commit("INVALID_ID")
                with self.assertRaisesRegex(ValueError, "invalid immutable ID"):
                    feed.build(self.repo, "main")
                self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
                self.git("reset", "--hard", "HEAD~1")
        for table, key in feed.KEYS.items():
            columns = sorted({key} | set(feed.COMPOSITE.get(table, ())))
            if table == "evidence":
                columns.append("record_table")
            values = {col: "" for col in columns}
            values[key] = feed.PREFIXES[key] + "-000001"
            if table == "evidence":
                values["record_table"] = "sites"
            data = ",".join(columns) + "\n" + ",".join(values[c] for c in columns) + "\n"
            self.assertEqual(len(feed.read_rows("data/" + table + ".csv", data)), 1)

    def test_leaf_symlinks_and_readonly_output_preserve_pair(self):
        feed.build(self.repo, "main")
        out = self.repo / "build/changelog"
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        outside = Path(self.tmp.name) / "outside-sentinel"
        outside.write_bytes(b"sentinel")
        for leaf in before:
            with self.subTest(leaf=leaf):
                (out / leaf).unlink()
                (out / leaf).symlink_to(outside)
                with self.assertRaisesRegex(ValueError, "not a symlink"):
                    feed.build(self.repo, "main")
                self.assertEqual(outside.read_bytes(), b"sentinel")
                (out / leaf).unlink()
                (out / leaf).write_bytes(before[leaf])
                self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
        self.org[1] = "closed"
        self.write("organizations_OH", ORG_FIELDS, [self.org])
        self.commit("STATUS_CHANGE")
        (out / "feed.xml").chmod(0o444)
        try:
            with self.assertRaises(PermissionError):
                feed.build(self.repo, "main")
            self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
        finally:
            (out / "feed.xml").chmod(0o644)

    def test_second_replace_failure_rolls_back_existing_and_new_outputs(self):
        out = self.repo / "build/changelog"
        replace = feed.os.replace
        for existing in [False, True]:
            with self.subTest(existing=existing):
                if existing:
                    feed.build(self.repo, "main")
                before = {p.name: p.read_bytes() for p in out.iterdir()} if out.exists() else {}
                calls = 0
                def fail_second(source, target):
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        raise OSError("injected publication failure")
                    return replace(source, target)
                with patch.object(feed.os, "replace", side_effect=fail_second):
                    with self.assertRaisesRegex(OSError, "injected publication"):
                        feed.publish(self.repo, out, {"CHANGELOG.md": b"new MD", "feed.xml": b"new XML"})
                self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})


if __name__ == "__main__":
    unittest.main()
