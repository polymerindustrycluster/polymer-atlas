"""Every published table needs a COUNTS.md unit, and sharded tables must publish as one merged export."""
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
