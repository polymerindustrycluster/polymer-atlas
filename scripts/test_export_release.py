"""Every published table needs a COUNTS.md unit, and sharded tables must publish as one merged export."""
import sys
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


if __name__ == "__main__":
    unittest.main()
