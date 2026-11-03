"""B-VOC mapping boundaries and reconciliation failures, using the approved packet."""
import csv
import importlib.util
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vocab_rulings", ROOT / "tasks/vocab-rulings-2026-11-03/build_edits.py")
edits = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(edits)
with edits.PROPOSALS.open(encoding="utf-8", newline="") as handle:
    PROPOSALS = list(csv.DictReader(handle))
RULES = {(r["field"], r["value"]): r for r in PROPOSALS}


class VocabRulingsTests(unittest.TestCase):
    def test_multi_target_order_dedup_and_held_token(self):
        new, note, outcomes = edits.rewrite(
            "distribution;polyurethane foam production and fabrication;foam_fabrication;service;unruled",
            "", "processes", "sites", RULES)
        self.assertEqual(new, "distribution;foam_production_unspecified;foam_fabrication;unruled")
        self.assertEqual(note, "")
        self.assertEqual([status for _, status in outcomes], ["held", "changed", "changed"])

    def test_notes_preserve_original_text_and_existing_order(self):
        new, note, _ = edits.rewrite("fiberglass;ethylene;carbon black;plastic", "prior;fiberglass",
                                     "materials", "sites", RULES)
        self.assertEqual(new, "carbon_black")
        self.assertEqual(note, "prior;fiberglass;ethylene")

    def test_organization_note_holds_include_monomers(self):
        new, note, outcomes = edits.rewrite("fiberglass;ethylene;carbon black;plastic", "",
                                           "materials", "organizations", RULES)
        self.assertEqual(new, "fiberglass;ethylene;carbon_black")
        self.assertEqual(note, "")
        self.assertEqual([status for _, status in outcomes], ["held", "held", "changed", "changed"])

    def test_unruled_spelling_and_wrong_field_are_not_normalized(self):
        for field, value in (("processes", "Distribution; distribution "), ("materials", "rod;film")):
            self.assertEqual(edits.rewrite(value, "", field, "sites", RULES)[0], value)

    def test_reconciliation_rejects_unaccounted_and_stale_counts(self):
        rule = RULES["materials", "carbon black"]
        counts = defaultdict(Counter)
        counts["sites", "materials", "carbon black"].update(matched=27, changed=27)
        edits.reconcile([rule], counts)
        counts["sites", "materials", "carbon black"]["changed"] -= 1
        with self.assertRaises(AssertionError):
            edits.reconcile([rule], counts)
        counts["sites", "materials", "carbon black"]["matched"] -= 1
        with self.assertRaises(AssertionError):
            edits.reconcile([rule], counts)


if __name__ == "__main__":
    unittest.main()
