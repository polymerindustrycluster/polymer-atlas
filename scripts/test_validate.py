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
    def test_site_other_note_columns_required(self):
        for column in ("processes_other_note", "materials_other_note"):
            with self.subTest(column=column):
                path = sorted(self.data.glob("sites_*.csv"))[0]
                original = path.read_bytes()
                with path.open(newline="", encoding="utf-8") as handle:
                    reader = csv.DictReader(handle)
                    fields, rows = reader.fieldnames, list(reader)
                with path.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=[f for f in fields if f != column],
                                            extrasaction="ignore", lineterminator="\n")
                    writer.writeheader()
                    writer.writerows(rows)
                self.assert_fails_with(f"missing v1.9.1 column {column}")
                path.write_bytes(original)

    def append_row(self, fname, row):
        path = self.data / fname
        with open(path, newline="", encoding="utf-8") as f:
            fields = next(csv.reader(f))
        with open(path, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields, lineterminator="\n").writerow(row)

    EQP_OK = {"equipment_id": "EQP-000001", "host_org_id": "ORG-000501", "site_id": "", "program_id": "",
              "name": "Capillary rheometer", "equipment_class": "rheometer_capillary", "access_mode": "not_stated",
              "source_ref": "https://www.uakron.edu/example-equipment", "observed_date": "2026-11-03",
              "withdrawn_date": "", "created_by": "test", "notes": ""}

    def test_v56_crlf_data_file(self):
        p = self.data / "relationships.csv"
        p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assert_fails_with("(V-56)")

    def test_v57_non_usps_state_without_country(self):
        self.edit_rows("organizations_INTL.csv", lambda r: r["hq_country"].strip(),
                       lambda r: r.update(hq_state="QC", hq_country=""))
        self.assert_fails_with("(V-57)")

    def test_v52_equipment_row_accepted(self):
        with (self.data / "equipment.csv").open(newline="", encoding="utf-8") as handle:
            next_id = max((int(r["equipment_id"][4:]) for r in csv.DictReader(handle)), default=0) + 1
        self.append_row("equipment.csv", dict(self.EQP_OK, equipment_id=f"EQP-{next_id:06d}"))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v52_equipment_class_out_of_vocab(self):
        self.append_row("equipment.csv", dict(self.EQP_OK, equipment_class="spectrometer"))
        self.assert_fails_with("not in the \u00a73.7 vocabulary (V-52)")

    def test_v52_equipment_needs_host_page_url(self):
        self.append_row("equipment.csv", dict(self.EQP_OK, source_ref="Ohio Innovation Exchange listing"))
        self.assert_fails_with("source_ref must be the host's own page URL (V-52)")

    def test_v53_engagement_rejects_email_url(self):
        self.append_row("people_engagement.csv", {"engagement_id": "ENG-000001", "person_id": "PERSON-000001",
                        "mode": "consulting", "source_ref": "https://example.edu/people/someone@example.edu",
                        "observed_date": "2026-11-03", "withdrawn_date": "", "created_by": "test", "notes": ""})
        self.assert_fails_with("no email (V-53)")

    def test_v53_engagement_mode_out_of_vocab(self):
        self.append_row("people_engagement.csv", {"engagement_id": "ENG-000001", "person_id": "PERSON-000001",
                        "mode": "available_for_hire", "source_ref": "https://example.edu/people/x",
                        "observed_date": "2026-11-03", "withdrawn_date": "", "created_by": "test", "notes": ""})
        self.assert_fails_with("not in the \u00a74.20 vocabulary (V-53)")

    def test_v55_process_token_out_of_vocab(self):
        base = set(BASELINE.get("V-55", []))
        self.edit_rows("sites_OH.csv",
                       lambda r: r["site_id"] not in base,
                       lambda r: r.update(processes="not_a_process_token"))
        self.assert_fails_with("not in SCHEMA §3.1/§3.2 vocabulary")

    def test_v55_baselined_row_only_warns(self):
        base = sorted(BASELINE.get("V-55", []))
        self.assertTrue(base, "V-55 baseline must not be empty")
        target = base[0]
        idcol = "site_id" if target.startswith("SITE") else "org_id"
        pat = "sites_*.csv" if target.startswith("SITE") else "organizations_*.csv"
        hit = None
        for path in sorted(self.data.glob(pat)):
            with open(path, newline="", encoding="utf-8") as f:
                if any(r[idcol] == target for r in csv.DictReader(f)):
                    hit = path.name; break
        self.assertIsNotNone(hit, f"{target} not found in any shard")
        self.edit_rows(hit,
                       lambda r: r[idcol] == target,
                       lambda r: r.update(processes="not_a_process_token"))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    # [v1.10] people as a §4.13 evidence class: rows ride evidence_people.csv.
    EVD_PEOPLE_OK = {"evidence_id": "EVD-999999", "record_table": "people", "record_id": "PERSON-000001",
                     "claim_type": "existence", "claim_detail": "styled professor on the institution's page",
                     "source_class": "own_site", "source_ref": "https://www.bgsu.edu/example",
                     "observed_date": "2026-11-04", "tier_effect": "supports_A",
                     "created_by": "test", "notes": ""}

    def test_v110_people_evidence_row_accepted(self):
        self.append_row("evidence_people.csv", dict(self.EVD_PEOPLE_OK))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v110_people_evidence_dangling_person(self):
        self.append_row("evidence_people.csv", dict(self.EVD_PEOPLE_OK, record_id="PERSON-999999"))
        self.assert_fails_with("record_id does not resolve in people (V-22)")

    def test_v110_evidence_bad_table_still_rejected(self):
        self.append_row("evidence_people.csv", dict(self.EVD_PEOPLE_OK, record_table="persons"))
        self.assert_fails_with("bad record_table (V-22)")

    def test_v110_people_scope_restates_tier(self):
        # PERSON-000001 is tier A; a must-have scope claim supported only at
        # C strength caps the record (V-25), at people grain as elsewhere.
        self.append_row("evidence_people.csv", dict(self.EVD_PEOPLE_OK, claim_type="scope",
                        claim_detail="polymer research stated for this person",
                        source_class="own_site", source_ref="https://www.bgsu.edu/example",
                        tier_effect="supports_C"))
        self.assert_fails_with("must-have claim scope supported only at C strength but tier is A (V-25)")

    def test_v110_people_scope_needs_own_site(self):
        self.append_row("evidence_people.csv", dict(self.EVD_PEOPLE_OK, claim_type="scope",
                        source_class="press", source_ref="https://example.com/news", tier_effect="supports_B"))
        self.assert_fails_with("people scope must be observed on the institution's own page (own_site) (V-22)")

    def test_v110_people_address_has_no_referent(self):
        self.append_row("evidence_people.csv", dict(self.EVD_PEOPLE_OK, claim_type="address"))
        self.assert_fails_with("claim_type address has no people-grain referent (V-22)")

    # [v1.10] §4.21 person identifier links (ORCID), enforced by V-54.
    PIL_OK = {"person_id": "PERSON-000001", "identifier_type": "ORCID",
              "identifier_id": "0000-0002-1825-0097", "match_basis": "orcid_on_institution_page",
              "as_of": "2026-11-04"}

    def test_v54_orcid_link_accepted(self):
        self.append_row("people_identifiers.csv", dict(self.PIL_OK))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v54_orcid_shape(self):
        self.append_row("people_identifiers.csv", dict(self.PIL_OK, identifier_id="0000-0002-1825-009"))
        self.assert_fails_with("is not a 4x4 ORCID iD (V-54)")

    # [v1.12] Crosswalk shape/uniqueness and attendee vocabulary.
    def test_v60_nullable_single_and_multiple_slugs_accepted(self):
        for value in ("", "test-event-2026", "test-winter;test-spring;test-fall"):
            with self.subTest(value=value):
                self.edit_rows("events.csv", lambda r: True,
                               lambda r: r.update(pic_events_slug=value))
                code, out = run_validator(self.data)
                self.assertEqual(code, 0, out[-1500:])

    def test_v60_malformed_slugs_rejected(self):
        for value in ("Uppercase", "under_score", "-leading", "trailing-",
                      "double--hyphen", "two words", "café", "valid;", ";valid",
                      "valid;;other", "valid; spaced", "valid\n"):
            with self.subTest(value=value):
                self.edit_rows("events.csv", lambda r: True,
                               lambda r: r.update(pic_events_slug=value))
                self.assert_fails_with("malformed pic_events_slug")

    def test_v60_duplicate_slug_on_different_events_rejected(self):
        first = self.edit_rows("events.csv", lambda r: True,
                               lambda r: r.update(pic_events_slug="test-first;test-shared"))
        self.edit_rows("events.csv", lambda r: r["event_id"] != first["event_id"],
                       lambda r: r.update(pic_events_slug="test-shared;test-second"))
        self.assert_fails_with(f"pic_events_slug 'test-shared' already on event {first['event_id']} (V-60)")

    def test_v19_attendee_accepted(self):
        self.edit_rows("event_participation.csv", lambda r: True,
                       lambda r: r.update(role="attendee"))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v19_attendees_typo_rejected(self):
        self.edit_rows("event_participation.csv", lambda r: True,
                       lambda r: r.update(role="attendees"))
        self.assert_fails_with("bad role (V-19)")

    # [v1.11] V-58 newsroom / LinkedIn columns; V-59 archive links.
    @staticmethod
    def _has_site(r):
        return r["website"].startswith("https://") and r["website"].count("/") <= 3

    def test_v58_newsroom_on_own_domain_accepted(self):
        def mut(r):
            r["newsroom_url"] = r["website"].rstrip("/") + "/news/"
        self.edit_rows("organizations_OH.csv", self._has_site, mut)
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v58_newsroom_off_domain_rejected(self):
        self.edit_rows("organizations_OH.csv", self._has_site, lambda r: r.update(newsroom_url="https://www.prnewswire.com/news/acme/"))
        self.assert_fails_with("newsroom_url must be on the website's own domain (V-58)")

    def test_v58_linkedin_shape(self):
        self.edit_rows("organizations_OH.csv", self._has_site, lambda r: r.update(linkedin_url="https://www.linkedin.com/in/someone/"))
        self.assert_fails_with("linkedin_url is not a linkedin.com/company/ page URL (V-58)")

    def test_v58_linkedin_dot_segment_rejected(self):  # codex review: /company/.. resolves to the LinkedIn root
        self.edit_rows("organizations_OH.csv", self._has_site, lambda r: r.update(linkedin_url="https://www.linkedin.com/company/.."))
        self.assert_fails_with("linkedin_url is not a linkedin.com/company/ page URL (V-58)")

    def test_v58_malformed_urls_rejected_without_crash(self):  # codex review: no host, bad port, broken IPv6 bracket
        def mut(r):
            r["newsroom_feed_url"] = "https:///feeds.example/rss.xml"
            r["newsroom_url"] = "https://[example.com/news"
        self.edit_rows("organizations_OH.csv", self._has_site, mut)
        code, out = run_validator(self.data)
        self.assertEqual(code, 1, out[-1500:])
        self.assertIn("newsroom_feed_url is not an http(s) URL (V-58)", out)
        self.assertIn("newsroom_url is not an http(s) URL (V-58)", out)
        self.assertNotIn("Traceback", out)

    def test_v58_two_level_suffix_is_not_one_domain(self):  # codex review: alpha.org.uk vs beta.org.uk
        def mut(r):
            r["website"], r["newsroom_url"] = "https://alpha.org.uk/", "https://beta.org.uk/news"
        self.edit_rows("organizations_OH.csv", self._has_site, mut)
        self.assert_fails_with("newsroom_url must be on the website's own domain (V-58)")

    def _an_evidence_row(self):
        with open(self.data / "evidence_organizations_OH.csv", newline="", encoding="utf-8") as f:
            r = next(e for e in csv.DictReader(f) if e["source_ref"].startswith("http"))
        return r["evidence_id"], r["source_ref"]

    def _arc(self, eid, ref):
        return {"evidence_id": eid, "archive_ref": f"https://web.archive.org/web/20261105120000/{ref}",
                "captured_at": "2026-11-05", "created_by": "test"}

    def test_v59_archive_link_accepted(self):
        self.append_row("archive_links.csv", self._arc(*self._an_evidence_row()))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v59_archive_ref_shape(self):
        eid, ref = self._an_evidence_row()
        self.append_row("archive_links.csv", dict(self._arc(eid, ref), archive_ref="https://archive.ph/abc"))
        self.assert_fails_with("archive_ref is not a web.archive.org capture URL (V-59)")

    def test_v59_archive_must_capture_the_cited_page(self):  # codex review: binding to the evidence row's URL
        eid, _ = self._an_evidence_row()
        self.append_row("archive_links.csv", self._arc(eid, "https://unrelated.example/"))
        self.assert_fails_with("archive_ref captures a different page than the evidence row cites (V-59)")

    def test_v59_archive_dangling_and_duplicate(self):
        eid, ref = self._an_evidence_row()
        self.append_row("archive_links.csv", self._arc(eid, ref))
        self.append_row("archive_links.csv", self._arc(eid, ref))
        self.append_row("archive_links.csv", self._arc("EVD-999998", ref))
        code, out = run_validator(self.data)
        self.assertEqual(code, 1, out[-1500:])
        self.assertIn("one row per evidence id (V-59)", out)
        self.assertIn("evidence_id 'EVD-999998' does not resolve (V-59)", out)

    def test_v54_orcid_rejects_fullwidth_digits(self):
        self.append_row("people_identifiers.csv", dict(self.PIL_OK, identifier_id="００００-０００２-１８２５-００９７"))
        self.assert_fails_with("is not a 4x4 ORCID iD (V-54)")

    def test_v54_orcid_one_row_per_value(self):
        self.append_row("people_identifiers.csv", dict(self.PIL_OK))
        self.append_row("people_identifiers.csv", dict(self.PIL_OK, person_id="PERSON-000002"))
        self.assert_fails_with("one row per identifier value (V-54)")

    def test_v54_dangling_person(self):
        self.append_row("people_identifiers.csv", dict(self.PIL_OK, person_id="PERSON-999999"))
        self.assert_fails_with("does not resolve (V-54)")

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
        r = self.edit_rows("evidence_ecosystem.csv", lambda r: True,
                           lambda r: r.update(claim_detail=r["claim_detail"] + " (CRM)"))
        self.assert_fails_with(f"{r['evidence_id']} names the PIC CRM in evidence_ecosystem.csv ['claim_detail']")

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
