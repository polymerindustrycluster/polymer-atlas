"""Every published table needs a COUNTS.md unit, and sharded tables must publish as one merged export."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_release as er  # noqa: E402


class ReleaseTables(unittest.TestCase):
    def test_every_table_has_a_unit(self):
        tables = set(er.SHARDED) | set(er.single_tables())
        self.assertEqual(sorted(t for t in tables if t not in er.UNIT), [])

    def test_no_shard_is_published_as_a_single_table(self):
        shards = [t for t in er.single_tables() if t.split("_")[0] in er.SHARDED]
        self.assertEqual(shards, [])

    def test_organization_release_columns_are_additive(self):
        cols = ["org_id", "processes", "materials", "markets_served"]
        orgs = [
            dict(zip(cols, ["ORG-000001", "", "", ""])),
            dict(zip(cols, ["ORG-000002", "extrusion; blow_molding", "", "marine"])),
            dict(zip(cols, ["ORG-000003", "extrusion", "", ""])),
        ]
        sites = [
            dict(zip(cols, ["ORG-000001", "injection_molding", "legacy_token", "marine"]),
                 operating_status="unknown"),
            dict(zip(cols, ["ORG-000002", "extrusion;injection_molding", "", ""]),
                 operating_status="active"),
            dict(zip(cols, ["ORG-000002", "thermoforming", "", "medical_device"]),
                 operating_status="closed"),
        ]
        outputs = ["processes_incl_sites", "materials_incl_sites", "markets_served_incl_sites"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "organizations_all.csv"
            er.write_organization_export(path, cols, orgs, sites)
            header, rows = er.read_csv(path)
        self.assertEqual(header, cols + outputs)
        self.assertEqual([{c: row[c] for c in cols} for row in rows], orgs)
        self.assertEqual([[row[c] for c in outputs] for row in rows], [
            ["injection_molding", "legacy_token", "marine"],
            ["extrusion;blow_molding;injection_molding", "", "marine"],
            ["extrusion", "", ""],
        ])
        self.assertIn("site rows", er.infer_field("organizations", outputs[0], [""])["description"])


if __name__ == "__main__":
    unittest.main()


class ValueBasisRelease(unittest.TestCase):
    """SCHEMA 4.24 in the release bundle: a withheld value leaves the organization and site rows, evidence text and the basis table."""

    def fixture_db(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(__import__("shutil").rmtree, d, True)
        con = sqlite3.connect(d / "r.db")
        for sql in ("CREATE TABLE organizations (org_id TEXT, processes TEXT, markets_served TEXT)",
                    "CREATE TABLE sites (site_id TEXT, org_id TEXT, processes TEXT, markets_served TEXT)",
                    "CREATE TABLE evidence (evidence_id TEXT, record_table TEXT, record_id TEXT, claim_detail TEXT, notes TEXT)",
                    "CREATE TABLE site_capabilities (capability_id TEXT, site_id TEXT, capability_type TEXT, term TEXT)",
                    "CREATE TABLE value_basis (record_table TEXT, record_id TEXT, field TEXT, value TEXT, basis TEXT, evidence_id TEXT, basis_date TEXT)"):
            con.execute(sql)
        con.execute("INSERT INTO organizations VALUES ('ORG-1', 'extrusion', 'marine')")
        con.execute("INSERT INTO sites VALUES ('SITE-1', 'ORG-1', 'blow_molding;lamination', 'marine')")
        con.executemany("INSERT INTO evidence VALUES (?,?,?,?,?)", [
            ("EVD-1", "sites", "SITE-1", "sites.processes includes blow_molding (own-site disclosure)", "Born from the tag 'blow_molding'"),
            ("EVD-2", "organizations", "ORG-1", "organizations.processes includes blow_molding (org scope)", None),
            ("EVD-3", "sites", "SITE-1", "sites.processes includes lamination (own-site disclosure)", "lamination read on the page"),
            ("EVD-4", "sites", "SITE-9", "sites.processes includes blow_molding (another plant)", "independent claim at another record")])
        con.executemany("INSERT INTO site_capabilities VALUES (?,?,?,?)", [
            ("CAP-1", "SITE-1", "process", "blow_molding"), ("CAP-2", "SITE-1", "process", "lamination"),
            ("CAP-3", "SITE-9", "process", "blow_molding")])
        con.executemany("INSERT INTO value_basis VALUES (?,?,?,?,?,?,?)", [
            ("sites", "SITE-1", "processes", "blow_molding", "not_found_pending_refetch", "EVD-1", "2026-11-24"),
            ("sites", "SITE-1", "processes", "lamination", "stated", "EVD-3", "2026-11-24"),
            ("sites", "SITE-1", "markets_served", "marine", "not_yet_checked", "EVD-3", "")])
        con.commit()
        con.close()
        return d

    def canonical(self, d):
        con = sqlite3.connect(d / "r.db")
        cols = ("record_table", "record_id", "field", "value", "basis", "evidence_id", "basis_date")
        rows = [dict(zip(cols, (c or "" for c in r))) for r in con.execute(f"SELECT {', '.join(cols)} FROM value_basis")]
        con.close()
        return rows

    def test_stale_database_basis_table_stops_the_release(self):  # planted defect (review 2026-11-24): same row count, swapped status
        d = self.fixture_db()
        canon = self.canonical(d)
        canon[0]["basis"], canon[1]["basis"] = canon[1]["basis"], canon[0]["basis"]
        with self.assertRaises(SystemExit) as stop:
            er.withhold_values_db(d / "r.db", canon)
        self.assertIn("differs from data/value_basis.csv", str(stop.exception))

    def test_database_copy_drops_the_withheld_value_and_labels_the_rest(self):
        d = self.fixture_db()
        keys, _ = er.withhold_values_db(d / "r.db", self.canonical(d))
        self.assertEqual(keys, {("sites", "SITE-1", "processes", "blow_molding")})
        con = sqlite3.connect(d / "r.db")
        self.assertEqual(con.execute("SELECT processes FROM sites").fetchone(), ("lamination",))
        self.assertEqual(con.execute("SELECT processes, markets_served FROM organizations").fetchone(), ("extrusion", "marine"))
        self.assertEqual(sorted(con.execute("SELECT value, label FROM value_basis")), [("lamination", "stated"), ("marine", "not yet checked")])
        ev = dict(con.execute("SELECT evidence_id, claim_detail FROM evidence"))
        self.assertEqual((ev["EVD-1"], ev["EVD-2"]), (er.WITHHELD, er.WITHHELD))   # the site's row and its organization's row name it
        self.assertIn("lamination", ev["EVD-3"])
        self.assertEqual(dict(con.execute("SELECT evidence_id, notes FROM evidence"))["EVD-1"], er.WITHHELD)   # the note repeats the value
        self.assertIn("independent claim", dict(con.execute("SELECT evidence_id, notes FROM evidence"))["EVD-4"])   # another record keeps its own claim
        self.assertEqual(sorted(con.execute("SELECT capability_id FROM site_capabilities")), [("CAP-2",), ("CAP-3",)])   # the site's tag copy leaves
        con.close()
        self.assertNotIn(b"Born from the tag", (d / "r.db").read_bytes())             # VACUUM left no copy of the blanked note in a free page

    def test_csv_copies(self):
        d = self.fixture_db()
        sites, evid, basis = d / "sites.csv", d / "evidence.csv", d / "value_basis.csv"
        sites.write_text("site_id,org_id,processes,markets_served\nSITE-1,ORG-1,blow_molding;lamination,marine\n")
        evid.write_text("evidence_id,record_table,record_id,claim_detail\nEVD-1,sites,SITE-1,x includes blow_molding\nEVD-3,sites,SITE-1,x includes lamination\n")
        basis.write_text("record_table,record_id,field,value,basis,evidence_id,basis_date\n"
                         "sites,SITE-1,processes,blow_molding,not_found_pending_refetch,EVD-1,2026-11-24\n"
                         "sites,SITE-1,processes,lamination,filing,EVD-3,2026-11-24\n")
        keys = {("sites", "SITE-1", "processes", "blow_molding")}
        er.withhold_values_csv(sites, "sites", keys, {"SITE-1": "ORG-1"})
        er.withhold_values_csv(evid, "evidence", keys, {"SITE-1": "ORG-1"})
        er.value_basis_release_csv(basis)
        cap = d / "caps.csv"
        cap.write_text("capability_id,site_id,capability_type,term\nCAP-1,SITE-1,process,blow_molding\nCAP-2,SITE-1,process,lamination\nCAP-3,SITE-9,process,blow_molding\n")
        er.withhold_values_csv(cap, "site_capabilities", keys, {"SITE-1": "ORG-1"})
        self.assertEqual(cap.read_text().splitlines()[1:], ["CAP-2,SITE-1,process,lamination", "CAP-3,SITE-9,process,blow_molding"])
        self.assertEqual(sites.read_text().splitlines()[1], "SITE-1,ORG-1,lamination,marine")
        self.assertEqual(evid.read_text().splitlines()[1:], [f"EVD-1,sites,SITE-1,{er.WITHHELD}", "EVD-3,sites,SITE-1,x includes lamination"])
        self.assertEqual(basis.read_text().splitlines(), ["record_table,record_id,field,value,basis,evidence_id,basis_date,label",
                                                           "sites,SITE-1,processes,lamination,filing,EVD-3,2026-11-24,from a filing"])
