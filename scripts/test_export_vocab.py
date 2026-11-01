#!/usr/bin/env python3
"""docs/schema/vocab.json must match the validator's vocabularies exactly.

Run from the repo root:  python3 -m unittest scripts/test_export_vocab.py
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import export_vocab  # noqa: E402


class VocabParity(unittest.TestCase):
    def test_vocab_json_is_current(self):
        p = subprocess.run([sys.executable, str(ROOT / "scripts" / "export_vocab.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_every_export_resolves(self):
        consts = export_vocab.literal_constants()
        missing = [n for n in export_vocab.EXPORT if n not in consts]
        self.assertEqual(missing, [])

    def test_site_types_match_schema_table(self):
        # SCHEMA §4.5 site_type row is the authority; the validator copy must match it.
        schema = (ROOT / "docs" / "SCHEMA.md").read_text(encoding="utf-8")
        row = next(l for l in schema.splitlines() if l.startswith("| `site_type` | enum"))
        notes_cell = row.split("**MUST**", 1)[1]
        in_schema = set(re.findall(r"`([a-z_]+)`", notes_cell))
        vocab = json.loads((ROOT / "docs" / "schema" / "vocab.json").read_text())
        self.assertEqual(in_schema, set(vocab["vocabularies"]["SITE_TYPES"]["values"]))


if __name__ == "__main__":
    unittest.main()
