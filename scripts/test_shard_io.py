#!/usr/bin/env python3
"""append_sorted writes atomically: a write cut short must leave the original shard byte-identical."""
import os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import shard_io

ORIGINAL = b"evidence_id,note\nEVD-000001,a\nEVD-000002,b\n"


class AppendSortedAtomic(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "evidence_x.csv"; self.path.write_bytes(ORIGINAL)

    def test_append_works(self):
        shard_io.append_sorted(self.path, [{"evidence_id": "EVD-000003", "note": "c"}], "evidence_id")
        self.assertEqual(self.path.read_bytes(), ORIGINAL + b"EVD-000003,c\n")
        self.assertEqual(os.listdir(self.tmp.name), ["evidence_x.csv"])

    def test_write_cut_short_leaves_original_intact(self):
        def cut(fd): raise OSError("simulated short write")
        with patch.object(shard_io.os, "fsync", side_effect=cut):
            with self.assertRaises(OSError):
                shard_io.append_sorted(self.path, [{"evidence_id": "EVD-000003", "note": "c"}], "evidence_id")
        self.assertEqual(self.path.read_bytes(), ORIGINAL)
        self.assertEqual(os.listdir(self.tmp.name), ["evidence_x.csv"], "temp file must be cleaned up")

    def test_truncating_write_leaves_original_intact(self):
        real_open = open
        def short_open(f, mode="r", *a, **k):
            fh = real_open(f, mode, *a, **k)
            if str(f).endswith(".tmp"):
                w = fh.write
                def short(data): w(data[: len(data) // 2]); raise OSError("short write")
                fh.write = short
            return fh
        with patch("builtins.open", short_open):
            with self.assertRaises(OSError):
                shard_io.append_sorted(self.path, [{"evidence_id": "EVD-000003", "note": "c"}], "evidence_id")
        self.assertEqual(self.path.read_bytes(), ORIGINAL)


if __name__ == "__main__":
    unittest.main()
