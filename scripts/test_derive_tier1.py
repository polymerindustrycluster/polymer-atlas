#!/usr/bin/env python3
"""Tests for scripts/derive_tier1.py.

Fixture tests build a minimal data dir in a tempdir. The parity test copies the
real data/ (read-only), applies the refresh to the copy, and asserts that
scripts/validate.py then reports zero V-29 drift: that is the check that this
script and the validator's derive_tier1_set implement the same SCHEMA §4.4 rules.

Run from the repo root:  python3 -m unittest scripts/test_derive_tier1.py
"""
import contextlib
import csv
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("derive_tier1", HERE / "derive_tier1.py")
dt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dt)

ORG_COLS = ["org_id", "legal_name", "stock_ticker", "employee_band_ohio", "tier1_qualifier",
            "tier1_qualifier_basis", "notes"]
SITE_COLS = ["site_id", "org_id", "state", "operating_status"]
REG_COLS = ["org_id", "registry", "registry_id", "match_basis", "as_of"]


def write(path, cols, rows, nl="\n"):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator=nl)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = dt.main(argv)
    return code, out.getvalue()


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        write(self.d / "organizations_OH.csv", ORG_COLS, [
            # loses employees_250plus (band dropped below 250); public_parent clause kept verbatim
            {"org_id": "ORG-000001", "legal_name": "Lose Co", "stock_ticker": "XYZ", "employee_band_ohio": "100-249",
             "tier1_qualifier": "public_parent;employees_250plus",
             "tier1_qualifier_basis": "public_parent: stock_ticker=XYZ (NYSE, parent); employees_250plus: employee_band_ohio=500-999",
             "notes": "has, a comma\nand a newline"},
            # gains employees_250plus
            {"org_id": "ORG-000002", "legal_name": "Gain Co", "employee_band_ohio": "250-499"},
            # already correct: untouched
            {"org_id": "ORG-000003", "legal_name": "Steady Co", "employee_band_ohio": "5000+",
             "tier1_qualifier": "employees_250plus",
             "tier1_qualifier_basis": "employees_250plus: employee_band_ohio=5000+"},
            # gains public_parent via parent filer + national_footprint (closed site excluded)
            {"org_id": "ORG-000004", "legal_name": "Sub Co"},
            # stale basis only (band moved within 250+)
            {"org_id": "ORG-000005", "legal_name": "Basis Co", "employee_band_ohio": "250-499",
             "tier1_qualifier": "employees_250plus",
             "tier1_qualifier_basis": "employees_250plus: employee_band_ohio=1000-4999"},
        ])
        write(self.d / "organizations_TX.csv", ORG_COLS, [
            {"org_id": "ORG-000006", "legal_name": "Texas Co", "tier1_qualifier": "", "tier1_qualifier_basis": ""},
        ], nl="\r\n")
        write(self.d / "sites_OH.csv", SITE_COLS, [
            {"site_id": "SITE-000001", "org_id": "ORG-000004", "state": "OH", "operating_status": "active"},
            {"site_id": "SITE-000002", "org_id": "ORG-000006", "state": "OH", "operating_status": "active"}])
        write(self.d / "sites_PA.csv", SITE_COLS, [
            {"site_id": "SITE-000003", "org_id": "ORG-000004", "state": "PA", "operating_status": "active"}])
        write(self.d / "sites_MI.csv", SITE_COLS, [
            {"site_id": "SITE-000004", "org_id": "ORG-000004", "state": "MI", "operating_status": ""}])
        write(self.d / "sites_IN.csv", SITE_COLS, [
            {"site_id": "SITE-000005", "org_id": "ORG-000004", "state": "IN", "operating_status": "closed"}])
        write(self.d / "registry_links.csv", REG_COLS, [
            {"org_id": "ORG-000004", "registry": "SEC_CIK_PARENT_FILER", "registry_id": "0000000001",
             "match_basis": "edgar_ex21_subsidiary_of_filer:Big Parent, Inc.", "as_of": "2026-10-28"},
            {"org_id": "ORG-000004", "registry": "TRI_TRIFID", "registry_id": "12345ABCDE12345", "as_of": "2026-10-28"}])
        self.before = {p.name: p.read_bytes() for p in self.d.glob("*.csv")}

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self, name):
        return {r["org_id"]: r for r in read_csv(self.d / name)}

    def test_check_reports_drift_and_writes_nothing(self):
        code, out = run(["--data-dir", str(self.d)])
        self.assertEqual(code, 1)
        self.assertIn("organizations with qualifier drift: 3", out)
        self.assertIn("lose:employees_250plus: 1", out)
        self.assertIn("stale canonical basis clause only: 1", out)
        self.assertEqual(self.before, {p.name: p.read_bytes() for p in self.d.glob("*.csv")})

    def test_write_applies_derivation_and_basis(self):
        code, _ = run(["--data-dir", str(self.d), "--write"])
        self.assertEqual(code, 0)
        r = self.rows("organizations_OH.csv")
        self.assertEqual(r["ORG-000001"]["tier1_qualifier"], "public_parent")
        self.assertEqual(r["ORG-000001"]["tier1_qualifier_basis"], "public_parent: stock_ticker=XYZ (NYSE, parent)")
        self.assertEqual(r["ORG-000001"]["notes"], "has, a comma\nand a newline")
        self.assertEqual(r["ORG-000002"]["tier1_qualifier"], "employees_250plus")
        self.assertEqual(r["ORG-000002"]["tier1_qualifier_basis"], "employees_250plus: employee_band_ohio=250-499")
        self.assertEqual(r["ORG-000004"]["tier1_qualifier"], "public_parent;tri_reporter;national_footprint")
        self.assertEqual(r["ORG-000004"]["tier1_qualifier_basis"],
                         "public_parent: sec_cik_parent_filer=0000000001 (Big Parent, Inc.); "
                         "tri_reporter: registry_links TRI_TRIFID; national_footprint: states=MI,OH,PA (3)")
        # stale-basis row untouched without --refresh-basis
        self.assertEqual(r["ORG-000005"]["tier1_qualifier_basis"], "employees_250plus: employee_band_ohio=1000-4999")
        # untouched file stays byte-identical (CRLF file)
        self.assertEqual(self.before["organizations_TX.csv"], (self.d / "organizations_TX.csv").read_bytes())
        # idempotent
        self.assertEqual(run(["--data-dir", str(self.d)])[0], 0)

    def test_refresh_basis(self):
        run(["--data-dir", str(self.d), "--write", "--refresh-basis"])
        r = self.rows("organizations_OH.csv")
        self.assertEqual(r["ORG-000005"]["tier1_qualifier_basis"], "employees_250plus: employee_band_ohio=250-499")
        self.assertEqual(r["ORG-000003"]["tier1_qualifier_basis"], "employees_250plus: employee_band_ohio=5000+")

    def test_only_changed_rows_and_columns_differ(self):
        run(["--data-dir", str(self.d), "--write"])
        old = list(csv.reader(io.StringIO(self.before["organizations_OH.csv"].decode(), newline="")))
        with open(self.d / "organizations_OH.csv", newline="", encoding="utf-8") as fh:
            new = list(csv.reader(fh))
        h = old[0]
        changed = {h[i] for a, b in zip(old, new) for i, (x, y) in enumerate(zip(a, b)) if x != y}
        self.assertEqual(changed, {"tier1_qualifier", "tier1_qualifier_basis"})

    def test_packet(self):
        pk = self.d / "packet"
        run(["--data-dir", str(self.d), "--packet", str(pk)])
        rows = read_csv(pk / "changes.csv")
        self.assertEqual([r["org_id"] for r in rows], ["ORG-000001", "ORG-000002", "ORG-000004"])
        self.assertEqual(list(rows[0].keys()), dt.CHANGE_COLS)

    def test_real_data_guard(self):
        with self.assertRaises(SystemExit) as cm:
            with contextlib.redirect_stderr(io.StringIO()):
                dt.main(["--write"])
        self.assertEqual(cm.exception.code, 2)


class ParityWithValidatorTest(unittest.TestCase):
    """Apply to a copy of the real data/ and require zero V-29 drift from validate.py."""

    def test_validator_reports_no_drift_after_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "data"
            shutil.copytree(ROOT / "data", d)
            with contextlib.redirect_stdout(io.StringIO()):
                dt.main(["--data-dir", str(d), "--write", "--refresh-basis"])
            env = dict(os.environ, ATLAS_DATA_DIR=str(d))
            p = subprocess.run([sys.executable, str(HERE / "validate.py")], env=env, capture_output=True, text=True)
            out = p.stdout + p.stderr
            self.assertEqual(p.returncode, 0, out[-2000:])
            self.assertNotIn("drift: stored", out)
            self.assertEqual(run(["--data-dir", str(d), "--refresh-basis"])[0], 0)


if __name__ == "__main__":
    unittest.main()
