#!/usr/bin/env python3
"""Mutation tests for scripts/validate.py.

Each test copies data/ into a temp dir, breaks exactly one thing, runs the
validator against the copy (ATLAS_DATA_DIR), and asserts the expected error
appears. A rule that stops firing on its mutation fails here instead of
silently letting bad rows through.

Run from the repo root:  python3 -m unittest scripts/test_validate.py
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "scripts" / "validate.py"
BASELINE = json.loads((ROOT / "scripts" / "validate_debt_baseline.json").read_text())["rules"]


def run_validator(data_dir, *args):
    env = dict(os.environ, ATLAS_DATA_DIR=str(data_dir))
    p = subprocess.run([sys.executable, str(VALIDATE), *args], env=env,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class ValidatorMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pristine = Path(cls.tmp.name) / "pristine"
        shutil.copytree(ROOT / "data", cls.pristine)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.data = Path(self.tmp.name) / f"case_{self._testMethodName}"
        shutil.copytree(self.pristine, self.data)

    def tearDown(self):
        shutil.rmtree(self.data, ignore_errors=True)

    # -- helpers ---------------------------------------------------------
    def edit_rows(self, fname, pick, mutate):
        """Mutate the first row of fname for which pick(row) is true."""
        path = self.data / fname
        with open(path, newline="", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            fields, rows = rdr.fieldnames, list(rdr)
        for r in rows:
            if pick(r):
                mutate(r)
                break
        else:
            self.fail(f"no row matched in {fname}")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        return r

    def clean_ohio_site(self, r):
        """An Ohio site with no grandfathered debt, so a new violation is new."""
        all_debt = set().union(*map(set, BASELINE.values()))
        return (r["site_id"] not in all_debt and r["naics_primary"]
                and r["county"] and r["operating_status"] == "active")

    def assert_fails_with(self, needle):
        code, out = run_validator(self.data)
        self.assertEqual(code, 1, f"validator should fail; output tail:\n{out[-2000:]}")
        self.assertIn(needle, out)

    # -- tests -----------------------------------------------------------
    def test_pristine_tree_passes(self):
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-2000:])
        self.assertIn("OK — validation passed.", out)

    def test_v45_site_type_out_of_vocab(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(site_type="factory"))
        self.assert_fails_with(f"sites {r['site_id']} site_type 'factory' not in SCHEMA §4.5 enum")

    def test_v46_site_ring_blank(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(ring_primary=""))
        self.assert_fails_with(f"sites {r['site_id']} ring_primary blank")

    def test_v47_site_naics_without_source_type(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(naics_primary_source_type=""))
        self.assert_fails_with(f"sites {r['site_id']} NAICS provenance")

    def test_v47_site_naics_source_type_out_of_vocab(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(naics_primary_source_type="own_site"))
        self.assert_fails_with(f"sites {r['site_id']} NAICS provenance source_type='own_site'")

    def test_v48_employee_band_free_text(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(employee_band_site="about 70 people"))
        self.assert_fails_with(f"sites {r['site_id']} employee_band_site 'about 70 people'")

    def test_v49_markets_served_out_of_vocab(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(markets_served="automotive"))
        self.assert_fails_with(f"sites {r['site_id']} markets_served values ['automotive']")

    def test_v50_crm_in_org_sources(self):
        all_debt = set().union(*map(set, BASELINE.values()))
        r = self.edit_rows("organizations_OH.csv", lambda r: r["org_id"] not in all_debt,
                           lambda r: r.update(sources=r["sources"] + "; PIC CRM record"))
        self.assert_fails_with(f"{r['org_id']} names the PIC CRM")

    def test_v50_crm_in_site_notes(self):
        all_debt = set().union(*map(set, BASELINE.values()))
        r = self.edit_rows("sites_OH.csv", lambda r: r["site_id"] not in all_debt,
                           lambda r: r.update(notes=(r.get("notes") or "") + " per CRM export"))
        self.assert_fails_with(f"{r['site_id']} names the PIC CRM in sites_OH.csv ['notes']")

    def test_v50_crm_in_evidence_row(self):
        r = self.edit_rows("evidence.csv", lambda r: True,
                           lambda r: r.update(claim_detail=r["claim_detail"] + " (CRM)"))
        self.assert_fails_with(f"{r['evidence_id']} names the PIC CRM in evidence.csv ['claim_detail']")

    def test_new_v176_vocab_accepted(self):
        self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                       lambda r: r.update(markets_served="automotive_unspecified;tire_rubber_goods"))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-2000:])

    def _add_link(self, row, with_site_col=True):
        path = self.data / "registry_links.csv"
        with open(path, newline="", encoding="utf-8") as f:
            rdr = csv.DictReader(f); fields = list(rdr.fieldnames); rows = list(rdr)
        if with_site_col and "site_id" not in fields:
            fields.append("site_id")
        rows.append(row)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", restval="")
            w.writeheader(); w.writerows(rows)

    def _a_site(self):
        with open(self.data / "sites_OH.csv", newline="", encoding="utf-8") as f:
            return next(r for r in csv.DictReader(f) if self.clean_ohio_site(r))

    def test_r10_site_keyed_frs_link_accepted(self):
        s = self._a_site()
        self._add_link({"org_id": s["org_id"], "registry": "FRS", "registry_id": "110000000001",
                        "match_basis": "test", "as_of": "2026-11-01", "site_id": s["site_id"]})
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-2000:])

    def test_r10_site_of_other_org_rejected(self):
        s = self._a_site()
        self._add_link({"org_id": "ORG-000001" if s["org_id"] != "ORG-000001" else "ORG-000002",
                        "registry": "FRS", "registry_id": "110000000002",
                        "match_basis": "test", "as_of": "2026-11-01", "site_id": s["site_id"]})
        self.assert_fails_with(f"site_id {s['site_id']} belongs to")

    def test_r11_ein_shape(self):
        s = self._a_site()
        self._add_link({"org_id": s["org_id"], "registry": "EIN", "registry_id": "12345",
                        "match_basis": "test", "as_of": "2026-11-01"}, with_site_col=False)
        self.assert_fails_with("EIN '12345' is not 9 digits")

    def test_fixed_baseline_row_is_reported(self):
        target = sorted(BASELINE["V-45"])[0]
        self.edit_rows(next(p.name for p in self.data.glob("sites_*.csv")
                            if target in p.read_text(encoding="utf-8")),
                       lambda r: r["site_id"] == target,
                       lambda r: r.update(site_type="manufacturing_plant"))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-2000:])
        self.assertIn(f"V-45: 1 baselined rows now pass", out)

    def test_ohio_site_without_county(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(county=""))
        self.assert_fails_with(f"{r['site_id']} Ohio site without county")

    def test_site_with_dangling_org(self):
        r = self.edit_rows("sites_OH.csv", self.clean_ohio_site,
                           lambda r: r.update(org_id="ORG-999999"))
        self.assert_fails_with(f"{r['site_id']} org_id 'ORG-999999' not found")

    def test_org_naics_without_provenance(self):
        r = self.edit_rows("organizations_OH.csv",
                           lambda r: r["naics_primary"] and r["naics_primary_source_type"],
                           lambda r: r.update(naics_primary_source_type=""))
        self.assert_fails_with(f"{r['org_id']} NAICS without provenance/confidence")

    def test_org_ring_out_of_range(self):
        r = self.edit_rows("organizations_OH.csv", lambda r: True,
                           lambda r: r.update(ring_primary="6"))
        self.assert_fails_with(f"{r['org_id']} ring_primary not 1-5")

    def test_pic_member_requires_public_list_url(self):
        r = self.edit_rows("organizations_OH.csv",
                           lambda r: r["pic_member"] != "true" and not r["membership_source_url"],
                           lambda r: r.update(pic_member="true"))
        self.assert_fails_with(f"{r['org_id']} pic_member=true without membership_source_url")


if __name__ == "__main__":
    unittest.main()
