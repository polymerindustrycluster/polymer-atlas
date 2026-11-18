"""Injection tests for ipeds_build.file_years against the committed raw file: each wrong year map must be refused, and
a hand edit to a generated table must fail the parity check (V-63). Ported from polymer-programs-db."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import ipeds_build

RAW = json.load(open(ipeds_build.ROOT / "data" / "ipeds" / "raw_ipeds_national.json", encoding="utf-8"))


def run(raw=RAW, relabel=None):
    with mock.patch.object(ipeds_build, "URBAN_RELABEL", relabel if relabel is not None else ipeds_build.URBAN_RELABEL):
        return ipeds_build.file_years(copy.deepcopy(raw))


class YearLabelTests(unittest.TestCase):
    def test_correct_map_builds_1991_2023(self):
        _, years = run()
        self.assertEqual((years[0], years[-1], len(years)), (1991, 2023, 33))

    def test_urban_2019_stays_and_2021_moves_back(self):
        rows, _ = run()
        served = {}
        for r in rows:
            served.setdefault(r["year"], set()).add(r.get("source") or "urban")
        self.assertEqual(served[2020], {"urban"})
        self.assertTrue(all(s.startswith("NCES") for s in served[2022] | served[2023]))

    def refuses(self, why, **kw):
        with self.assertRaises(SystemExit) as cm:
            run(**kw)
        self.assertIn(why, str(cm.exception))

    def test_no_relabel_clashes(self):
        self.refuses("two served years", relabel={})

    def test_partial_relabel_clashes(self):
        self.refuses("two served years", relabel={2021: 2020})

    def test_swapped_relabel_is_out_of_order(self):
        self.refuses("out of served order", relabel={2021: 2021, 2022: 2020})

    def test_overshift_clashes(self):
        self.refuses("two served years", relabel={2019: 2018, 2021: 2020, 2022: 2021})

    def test_cross_family_map_clashes(self):
        self.refuses("two served years", relabel={2021: 2020, 2022: 2022, 2023: 2021, 2024: 2023})

    def test_interior_hole_is_refused(self):
        raw = copy.deepcopy(RAW)
        raw["rows"] = [r for r in raw["rows"] if not (r["year"] == 2010 and not r.get("source"))]
        self.refuses("holes at [2010]", raw=raw)

    def test_truncated_nces_year_is_missing_at_end(self):
        raw = copy.deepcopy(RAW)
        before = len(raw["rows"])
        raw["rows"] = [r for r in raw["rows"] if not (r.get("source") or "").upper().startswith("NCES C2024_A")]
        self.assertLess(len(raw["rows"]), before)
        self.refuses("missing at an end", raw=raw)

    def test_quarantine_refuses_one_changed_count(self):
        raw = copy.deepcopy(RAW)
        row = next(r for r in raw["rows"] if r["year"] == 2020 and not r.get("source") and r["awards"] > 0)
        row["awards"] += 1
        self.refuses("no longer repeats", raw=raw)

    def test_quarantine_refuses_a_partial_2020(self):
        raw = copy.deepcopy(RAW)
        first = next(i for i, r in enumerate(raw["rows"]) if r["year"] == 2020 and not r.get("source") and r["awards"])
        del raw["rows"][first]
        self.refuses("no longer repeats", raw=raw)


class ParityTests(unittest.TestCase):
    def test_committed_tables_match_the_raw_file(self):
        self.assertEqual(ipeds_build.mismatches(ipeds_build.ROOT / "data"), [])

    def test_a_hand_edit_to_any_table_is_detected(self):
        want = ipeds_build.expected(ipeds_build.ROOT / "data")
        for name, text in want.items():
            with tempfile.TemporaryDirectory() as d:
                d = Path(d); (d / "ipeds").mkdir()
                (d / "ipeds" / "raw_ipeds_national.json").write_text(json.dumps(RAW), encoding="utf-8")
                for n, t in want.items():
                    (d / n).write_bytes(t.encode("utf-8"))
                self.assertEqual(ipeds_build.mismatches(d), [])  # an untouched copy passes
                lines = text.split("\n")
                lines[1] += "1"  # one character added to one data row
                (d / name).write_bytes("\n".join(lines).encode("utf-8"))
                self.assertEqual(ipeds_build.mismatches(d), [name])


if __name__ == "__main__":
    unittest.main()
