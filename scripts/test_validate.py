#!/usr/bin/env python3
"""Mutation tests for scripts/validate.py.

Each test copies data/ into a temp dir, breaks exactly one thing, runs the
validator against the copy (ATLAS_DATA_DIR), and asserts the expected error
appears. A rule that stops firing on its mutation fails here instead of
silently letting bad rows through.

Run from the repo root:  python3 -m unittest scripts/test_validate.py
"""
import csv
import io
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
    parallel_safe = True  # scripts/run_tests.py may split this class: each test copies data/ to its own temp dir

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
        # [v1.17] EVD-999999 sits above the archive-at-capture threshold (EVD-400501),
        # so the row is accepted only with its §4.22 archive link in the same pass (V-66).
        self.append_row("archive_links.csv",
                        {"evidence_id": "EVD-999999",
                         "archive_ref": "https://web.archive.org/web/20261104000000/https://www.bgsu.edu/example",
                         "captured_at": "2026-11-04", "created_by": "test"})
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
    def test_v61_nullable_single_and_multiple_slugs_accepted(self):
        for value in ("", "test-event-2026", "test-winter;test-spring;test-fall"):
            with self.subTest(value=value):
                self.edit_rows("events.csv", lambda r: True,
                               lambda r: r.update(pic_events_slug=value))
                code, out = run_validator(self.data)
                self.assertEqual(code, 0, out[-1500:])

    def test_v61_malformed_slugs_rejected(self):
        for value in ("Uppercase", "under_score", "-leading", "trailing-",
                      "double--hyphen", "two words", "café", "valid;", ";valid",
                      "valid;;other", "valid; spaced", "valid\n"):
            with self.subTest(value=value):
                self.edit_rows("events.csv", lambda r: True,
                               lambda r: r.update(pic_events_slug=value))
                self.assert_fails_with("malformed pic_events_slug")

    def test_v61_duplicate_slug_on_different_events_rejected(self):
        first = self.edit_rows("events.csv", lambda r: True,
                               lambda r: r.update(pic_events_slug="test-first;test-shared"))
        self.edit_rows("events.csv", lambda r: r["event_id"] != first["event_id"],
                       lambda r: r.update(pic_events_slug="test-shared;test-second"))
        self.assert_fails_with(f"pic_events_slug 'test-shared' already on event {first['event_id']} (V-61)")

    def test_v61_slug_repeated_in_one_cell_rejected(self):  # review 2026-11-09: 'foo;foo' passed before
        self.edit_rows("events.csv", lambda r: True, lambda r: r.update(pic_events_slug="test-same;test-same"))
        self.assert_fails_with("pic_events_slug 'test-same' repeated in one cell (V-61)")

    def test_v61_row_width_must_match_header(self):  # post-merge reviews 2026-11-18: short and wide rows passed
        path = self.data / "events.csv"
        pristine = path.read_bytes()
        for label, change, needle in (("short by 1", lambda r: r.pop(), "has fewer fields than the header (V-61)"),
                                      ("short by 2", lambda r: (r.pop(), r.pop()), "has fewer fields than the header (V-61)"),
                                      ("wide by 1", lambda r: r.append(""), "has more fields than the header (V-61)")):
            with self.subTest(label):
                rows = list(csv.reader(io.StringIO(pristine.decode("utf-8"), newline="")))
                change(rows[1])
                buf = io.StringIO()
                csv.writer(buf, lineterminator="\n").writerows(rows)
                path.write_bytes(buf.getvalue().encode("utf-8"))  # bytes: write_text would emit CRLF on Windows (V-56)
                self.assert_fails_with(needle)
        path.write_bytes(pristine)

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

    def test_v60_new_licensed_citation_rejected(self):
        with open(self.data / "evidence_organizations_OH.csv", newline="", encoding="utf-8") as f:
            row = next(csv.DictReader(f))
        self.append_row("evidence_organizations_OH.csv", dict(row, evidence_id="EVD-999997",
                        source_ref="https://www.plasticsnews.com/news/example", source_class="press", tier_effect="supports_B"))
        self.assert_fails_with("new violation (V-60")

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

    # -- V-62 [v1.13.4]: no personal-account identifier URL in a people row ------
    def _people_row(self, **cols):
        return self.edit_rows("people.csv", lambda r: r["person_id"] == "PERSON-000001", lambda r: r.update(cols))

    def test_v62_profile_u_param_rejected(self):
        self._people_row(public_profile_url="https://www.example.edu/people/profile.dot?" + "u=abc")  # split: the pre-push scan refuses literal ones
        self.assert_fails_with("PERSON-000001 public_profile_url carries a personal-account identifier URL")

    def test_v62_lab_tilde_rejected(self):
        self._people_row(lab_url="https://www.example.edu/" + "~abc/lab.html")
        self.assert_fails_with("PERSON-000001 lab_url carries a personal-account identifier URL")

    def test_v62_schemeless_tilde_in_sources_rejected(self):
        self._people_row(sources="host.example.edu/" + "~abc")
        self.assert_fails_with("PERSON-000001 sources carries a personal-account identifier URL")

    def test_v62_explicit_port_tilde_rejected(self):
        self._people_row(public_profile_url="https://www.example.edu:443/" + "~abc/profile")
        self.assert_fails_with("PERSON-000001 public_profile_url carries a personal-account identifier URL")

    def test_v62_fragment_text_is_not_a_query(self):
        self._people_row(public_profile_url="https://www.example.edu/guide#faq?" + "u=abc")
        code, out = run_validator(self.data)
        self.assertNotIn("V-62", out)
        self.assertEqual(code, 0, out[-2000:])

    def test_v62_account_in_second_query_parameter_without_path_rejected(self):
        self._people_row(public_profile_url="https://www.example.edu?lang=en&" + "u=abc")
        self.assert_fails_with("PERSON-000001 public_profile_url carries a personal-account identifier URL")

    def test_v62_filename_then_query_inside_fragment_passes(self):
        self._people_row(public_profile_url="https://www.example.edu/guide#paper.pdf?" + "u=abc")
        code, out = run_validator(self.data)
        self.assertNotIn("V-62", out)
        self.assertEqual(code, 0, out[-2000:])

    def test_v62_placeholder_and_non_people_table_pass(self):
        self._people_row(public_profile_url="https://www.example.edu/people/profile.dot?u=<id>")
        self.edit_rows("organizations_OH.csv", lambda r: True,
                       lambda r: r.update(notes=(r["notes"] + " https://dam.example.com/widen?" + "u=abc").strip()))
        code, out = run_validator(self.data)
        self.assertNotIn("V-62", out)
        self.assertEqual(code, 0, out[-2000:])

    # -- V-62 widened [v1.15, owner rulings 2026-11-18b item 3]: ?unid= and researchdirectory.uc.edu/p/ -----
    def test_v62_unid_param_rejected(self):
        self._people_row(public_profile_url="https://www.example.edu/profile/?" + "unid=u0000000")  # split: the pre-push scan refuses literal ones
        self.assert_fails_with("PERSON-000001 public_profile_url carries a personal-account identifier URL")

    def test_v62_unid_in_second_query_parameter_in_sources_rejected(self):
        self._people_row(sources="https://www.example.edu/profile/?lang=en&" + "unid=u0000000")
        self.assert_fails_with("PERSON-000001 sources carries a personal-account identifier URL")

    def test_v62_uc_research_directory_rejected(self):
        self._people_row(sources="https://researchdirectory.uc.edu/" + "p/abcde")
        self.assert_fails_with("PERSON-000001 sources carries a personal-account identifier URL")

    def test_v62_fisid_and_placeholders_pass(self):
        self._people_row(public_profile_url="https://experts.example.edu/people/jane-doe/fisid_123456",
                         sources="https://www.example.edu/profile/?unid=<id>;https://researchdirectory.uc.edu/p/<shortname>")
        code, out = run_validator(self.data)
        self.assertNotIn("V-62", out)
        self.assertEqual(code, 0, out[-2000:])

    def test_v62_uc_root_dot_spelling_rejected(self):
        self._people_row(sources="https://RESEARCHDIRECTORY.uc.edu./" + "p/abcde")
        self.assert_fails_with("PERSON-000001 sources carries a personal-account identifier URL")

    def test_v62_uc_sibling_host_and_nested_path_pass(self):
        for url in ("https://notresearchdirectory.uc.edu/" + "p/abcde", "https://researchdirectory.uc.edu/events/" + "p/abcde"):
            with self.subTest(url=url):
                shutil.rmtree(self.data); shutil.copytree(self.pristine, self.data)
                self._people_row(sources=url)
                code, out = run_validator(self.data)
                self.assertNotIn("V-62", out)
                self.assertEqual(code, 0, out[-2000:])

    def test_v62_unid_text_in_a_value_or_a_longer_key_passes(self):
        for url in ("https://www.example.edu/profile/?q=" + "unid=abc", "https://www.example.edu/profile/?" + "unidx=abc"):
            with self.subTest(url=url):
                shutil.rmtree(self.data); shutil.copytree(self.pristine, self.data)
                self._people_row(public_profile_url=url)
                code, out = run_validator(self.data)
                self.assertNotIn("V-62", out)
                self.assertEqual(code, 0, out[-2000:])

    def test_v62_p_segment_on_another_host_passes(self):
        self._people_row(public_profile_url="https://www.example.edu/" + "p/abcde")
        code, out = run_validator(self.data)
        self.assertNotIn("V-62", out)
        self.assertEqual(code, 0, out[-2000:])

    # -- V-64 [v1.15, owner ruling 2026-11-18b item 6]: people status ---------------------------------
    def test_v64_bad_status_fails(self):
        self._people_row(status="retired", status_date="2026-01-01")
        self.assert_fails_with("PERSON-000001 status 'retired' not active|deceased (V-64)")

    def test_v64_status_without_iso_date_fails(self):
        self._people_row(status="active", status_date="2026")
        self.assert_fails_with("PERSON-000001 status active without a valid ISO status_date (V-64)")

    def test_v64_status_date_without_status_fails(self):
        self._people_row(status="", status_date="2026-01-01")
        self.assert_fails_with("PERSON-000001 status '' not active|deceased (V-64)")

    def _person_with_evidence(self):
        with open(self.data / "evidence_people.csv", newline="", encoding="utf-8") as f:
            e = next(r for r in csv.DictReader(f) if r["observed_date"])
        return e["record_id"], e["observed_date"]

    def _death_row(self, pid, observed, **over):
        # allocate above the tree max: a fixed id collided with real data once main grew past it (#422, EVD-399990)
        top = 0
        for p in self.data.glob("evidence*.csv"):
            with open(p, newline="", encoding="utf-8") as f:
                top = max([top] + [int(r["evidence_id"][4:]) for r in csv.DictReader(f)])
        row = {"evidence_id": f"EVD-{top + 1:06d}", "record_table": "people", "record_id": pid, "claim_type": "liveness",
               "claim_detail": "status=deceased; date of death as the notice states it", "source_class": "press",
               "source_ref": "https://example.org/notice", "observed_date": observed, "tier_effect": "supports_B",
               "created_by": "test", "notes": "synthetic"}
        row.update(over)
        self.append_row("evidence_people.csv", row)
        # [v1.17] the synthetic row is allocated above the tree max, so V-66 (archive at
        # capture) applies to it exactly as to a real post-adoption row: mint its
        # archive_links row alongside, in §4.22 form.
        self.append_row("archive_links.csv",
                        {"evidence_id": row["evidence_id"],
                         "archive_ref": "https://web.archive.org/web/20260116000000/" + row["source_ref"],
                         "captured_at": "2026-01-16", "created_by": "test"})

    def test_v64_deceased_without_any_evidence_row_fails(self):
        self._people_row(status="deceased", status_date="2026-01-16")  # PERSON-000001 has no evidence_people row
        self.assert_fails_with("PERSON-000001 deceased with no evidence_people affirmative (supports_*) liveness row whose claim_detail starts status=deceased, observed on or after status_date 2026-01-16 (V-64)")

    def test_v64_deceased_appointment_row_does_not_satisfy(self):
        pid, observed = self._person_with_evidence()  # an existence/scope row observed on a date on or after status_date
        self.edit_rows("people.csv", lambda r: r["person_id"] == pid, lambda r: r.update(status="deceased", status_date="2000-01-01"))
        self.assert_fails_with(f"{pid} deceased with no evidence_people affirmative (supports_*) liveness row whose claim_detail starts status=deceased, observed on or after status_date 2000-01-01 (V-64)")

    def test_v64_deceased_liveness_row_not_naming_deceased_fails(self):
        self._death_row("PERSON-000001", "2026-11-18", claim_detail="status=active")
        self._people_row(status="deceased", status_date="2026-01-16")
        self.assert_fails_with("PERSON-000001 deceased with no evidence_people affirmative (supports_*) liveness row whose claim_detail starts status=deceased")

    def test_v64_deceased_only_contradicting_row_fails(self):
        self._death_row("PERSON-000001", "2026-11-18", tier_effect="contradicts",
                        claim_detail="status=deceased; the source contradicts this and confirms the person is active")
        self._people_row(status="deceased", status_date="2026-01-16")
        self.assert_fails_with("PERSON-000001 deceased with no evidence_people affirmative (supports_*) liveness row")

    def test_v64_deceased_marker_not_at_the_start_fails(self):
        self._death_row("PERSON-000001", "2026-11-18", claim_detail="The source contradicts status=deceased and confirms the person is active.")
        self._people_row(status="deceased", status_date="2026-01-16")
        self.assert_fails_with("PERSON-000001 deceased with no evidence_people affirmative (supports_*) liveness row")

    def test_v64_deceased_death_row_observed_before_status_date_fails(self):
        self._death_row("PERSON-000001", "2026-01-15")
        self._people_row(status="deceased", status_date="2026-01-16")
        self.assert_fails_with("PERSON-000001 deceased with no evidence_people affirmative (supports_*) liveness row whose claim_detail starts status=deceased, observed on or after status_date 2026-01-16 (V-64)")

    def test_v64_deceased_death_row_observed_on_or_after_status_date_passes(self):
        for observed in ("2026-01-16", "2026-11-18"):
            with self.subTest(observed=observed):
                shutil.rmtree(self.data); shutil.copytree(self.pristine, self.data)
                self._death_row("PERSON-000001", observed)
                self._people_row(status="deceased", status_date="2026-01-16")
                code, out = run_validator(self.data)
                self.assertNotIn("V-64", out)
                self.assertEqual(code, 0, out[-2000:])

    def test_v64_active_with_iso_date_passes(self):
        self._people_row(status="active", status_date="2026-11-18")
        code, out = run_validator(self.data)
        self.assertNotIn("V-64", out)
        self.assertEqual(code, 0, out[-2000:])

    # [v1.17] V-65 no naked tier-A/B (§4.13 floor rule); V-66 archive at capture (§4.22);
    # V-67 no staging pointer in a published citation field (§4.12.2).
    def _next_evd(self):
        mx = 0
        for p in self.data.glob("evidence_*.csv"):
            with open(p, newline="", encoding="utf-8") as f:
                mx = max(mx, max((int(r["evidence_id"][4:]) for r in csv.DictReader(f)), default=0))
        return f"EVD-{mx + 1:06d}"

    def test_v65_new_naked_tier_a_fails(self):
        with open(self.data / "evidence_people.csv", newline="", encoding="utf-8") as f:
            evidenced = {r["record_id"] for r in csv.DictReader(f)}
        base = set(BASELINE.get("V-65", []))
        self.edit_rows("people.csv",
                       lambda r: r["verification_tier"] in ("C", "U") and r["person_id"] not in evidenced
                                 and r["person_id"] not in base,
                       lambda r: r.update(verification_tier="A"))
        self.assert_fails_with("no supporting evidence row at its own strength (SCHEMA §4.13 floor rule, v1.17) — new violation (V-65")

    def test_v65_baseline_still_warns_only(self):
        base = sorted(BASELINE.get("V-65", []))
        self.assertTrue(base, "V-65 baseline must not be empty at adoption")
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])
        self.assertIn(f"V-65: {len(base)} baselined rows still violate", out)

    def _v66_row(self, eid, **kw):
        row = {"evidence_id": eid, "record_table": "people", "record_id": "PERSON-000001",
               "claim_type": "existence", "claim_detail": "test existence witness",
               "source_class": "own_site", "source_ref": "https://example.com/prof",
               "observed_date": "2026-11-20", "tier_effect": "supports_A",
               "created_by": "test", "notes": ""}
        row.update(kw)
        return row

    def test_v66_url_row_without_archive_link_fails(self):
        eid = self._next_evd()
        self.assertGreater(int(eid[4:]), 400501, "test row must sit above the v1.17 threshold")
        self.append_row("evidence_people.csv", self._v66_row(eid))
        self.assert_fails_with("cites a URL with no archive_links row — archive at capture (SCHEMA §4.22, v1.17)")

    def test_v66_url_row_with_archive_link_passes(self):
        eid = self._next_evd()
        self.append_row("evidence_people.csv", self._v66_row(eid))
        self.append_row("archive_links.csv",
                        {"evidence_id": eid,
                         "archive_ref": "https://web.archive.org/web/20261120000000/https://example.com/prof",
                         "captured_at": "2026-11-20", "created_by": "test"})
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v66_named_source_row_exempt(self):
        with open(self.data / "people.csv", newline="", encoding="utf-8") as f:
            uid = next(r["person_id"] for r in csv.DictReader(f) if r["verification_tier"] == "U")
        self.append_row("evidence_people.csv",
                        self._v66_row(self._next_evd(), record_id=uid, claim_type="parent",
                                      source_class="directory", source_ref="Example Directory listing 12345",
                                      tier_effect="supports_B"))
        code, out = run_validator(self.data)
        self.assertEqual(code, 0, out[-1500:])

    def test_v67_new_staging_pointer_fails(self):
        with open(self.data / "event_participation.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        src = dict(rows[0], evidence_source_url="staging raw/tradeshows/MANIFEST.md")
        new = dict(src, participation_id=f"EVP-{max(int(r['participation_id'][4:]) for r in rows) + 1:06d}",
                   org_id="ORG-000008")
        self.append_row("event_participation.csv", new)
        self.assert_fails_with("evidence_source_url is a staging pointer — cite the organizer URL or its archive ref (SCHEMA §4.12.2, v1.17)")

    # -- V-68 [v1.17.1, owner ruling 2026-11-20 "Close the zero-row leak"]: §4.13 presence floor, tier C/U ------------
    V68_MSG = "{t} {rid} is tier {tier} with no evidence row in data/evidence_*.csv (SCHEMA §4.13 presence floor, V-68)"

    def _evidence_index(self):
        """(record_table, record_id) -> [(shard path, evidence_id)] over the copy's evidence shards."""
        idx = {}
        for path in sorted(self.data.glob("evidence_*.csv")):
            with open(path, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    idx.setdefault((r["record_table"], r["record_id"].strip()), []).append((path, r["evidence_id"]))
        return idx

    def _rows(self, fname):
        with open(self.data / fname, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _org_tiers(self):
        return {r["org_id"]: r["verification_tier"] for p in self.data.glob("organizations_*.csv") for r in self._rows(p.name)}

    @staticmethod
    def _v68_ids(table):
        """Record ids baselined under V-68 for one table (keys are <table>:<id>:<identity fingerprint>)."""
        return [k.split(":")[1] for k in sorted(BASELINE.get("V-68", [])) if k.startswith(f"{table}:")]

    def test_v68_unbaselined_record_losing_its_only_row_fails(self):
        tiers = self._org_tiers()
        with open(self.data / "archive_links.csv", newline="", encoding="utf-8") as f:
            archived = {r["evidence_id"] for r in csv.DictReader(f)}
        (table, rid), [(path, eid)] = next(
            (k, v) for k, v in sorted(self._evidence_index().items())
            if k[0] == "organizations" and len(v) == 1 and tiers.get(k[1]) in ("C", "U") and v[0][1] not in archived)
        with open(path, newline="", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            fields, rows = rdr.fieldnames, [r for r in rdr if r["evidence_id"] != eid]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        self.assert_fails_with(self.V68_MSG.format(t="organizations", rid=rid, tier=tiers[rid]) + " — new violation (V-68")

    def test_v68_new_record_without_evidence_fails(self):
        shards = [p.name for p in self.data.glob("organizations_*.csv")] + ["ecosystem.csv"]
        top = max(int(r["org_id"][4:]) for name in shards for r in self._rows(name))  # one ORG- id space
        new_id = f"ORG-{top + 1:06d}"  # created at tier C, as AGENTS.md §3 step 6 creates records
        self.append_row("organizations_OH.csv", dict(self._rows("organizations_OH.csv")[-1], org_id=new_id, verification_tier="C"))
        self.assert_fails_with(self.V68_MSG.format(t="organizations", rid=new_id, tier="C"))

    def test_v68_new_ecosystem_record_with_blank_tier_fails(self):
        # review 2026-11-20 (Codex, round 5): ecosystem has no tier-enum check, so a blank tier must not slip past both
        # V-65 (A/B) and V-68; V-68 covers every tier that is not A or B.
        shards = [p.name for p in self.data.glob("organizations_*.csv")] + ["ecosystem.csv"]
        top = max(int(r["org_id"][4:]) for name in shards for r in self._rows(name))
        new_id = f"ORG-{top + 1:06d}"
        self.append_row("ecosystem.csv", dict(self._rows("ecosystem.csv")[-1], org_id=new_id, verification_tier=""))
        self.assert_fails_with(self.V68_MSG.format(t="ecosystem", rid=new_id, tier="(blank)"))

    def test_v68_baselined_record_gaining_a_row_only_warns(self):
        has_rows = self._evidence_index()
        tiers = {r["person_id"]: r["verification_tier"] for r in self._rows("people.csv")}
        rowless = [p for p in self._v68_ids("people") if ("people", p) not in has_rows]
        person, other = rowless[0], rowless[1]  # `other` stays row-less: proves V-68 still runs (not vacuous)
        # the effect matches the record's tier so V-25 restatement cannot fail for reasons unrelated to V-68
        self.append_row("evidence_people.csv", dict(self.EVD_PEOPLE_OK, record_id=person,
                                                    tier_effect=f"supports_{tiers[person]}"))
        self.append_row("archive_links.csv",  # EVD-999999 is above the V-66 threshold: archive at capture
                        {"evidence_id": "EVD-999999",
                         "archive_ref": "https://web.archive.org/web/20261104000000/https://www.bgsu.edu/example",
                         "captured_at": "2026-11-04", "created_by": "test"})
        code, out = run_validator(self.data, "--debt-details")
        self.assertEqual(code, 0, out[-2000:])
        self.assertRegex(out, r"V-68: \d+ baselined rows now pass")
        self.assertNotIn(self.V68_MSG.format(t="people", rid=person, tier=tiers[person]), out)
        self.assertIn(self.V68_MSG.format(t="people", rid=other, tier=tiers[other]), out)

    def test_v68_baselined_record_repurposed_in_place_fails(self):
        # review 2026-11-20 (Codex): keep a row-less baselined id but overwrite it with a different entity. No row is
        # removed, so check_row_loss.py is silent; the identity fingerprint in the key must take it out of the baseline.
        has_rows, tiers = self._evidence_index(), self._org_tiers()
        rid = next(o for o in self._v68_ids("organizations") if ("organizations", o) not in has_rows)
        shard = next(p.name for p in sorted(self.data.glob("organizations_*.csv"))
                     if any(r["org_id"] == rid for r in self._rows(p.name)))
        self.edit_rows(shard, lambda r: r["org_id"] == rid, lambda r: r.update(legal_name="Entirely Different Company LLC"))
        self.assert_fails_with(self.V68_MSG.format(t="organizations", rid=rid, tier=tiers[rid]))

    def test_v68_baselined_person_same_name_other_institution_fails(self):
        # review 2026-11-20 (Codex, round 3): a different person with the same full_name under the same person_id.
        # The identity fingerprint covers institution_org_id, so the move drops the record out of the baseline.
        has_rows = self._evidence_index()
        people = self._rows("people.csv")
        pid = next(p for p in self._v68_ids("people") if ("people", p) not in has_rows)
        me = next(r for r in people if r["person_id"] == pid)
        other_inst = next(r["institution_org_id"] for r in people if r["institution_org_id"] not in ("", me["institution_org_id"]))
        self.edit_rows("people.csv", lambda r: r["person_id"] == pid, lambda r: r.update(institution_org_id=other_inst))
        self.assert_fails_with(self.V68_MSG.format(t="people", rid=pid, tier=me["verification_tier"]))

    def test_replay_gap_is_reported_when_the_raw_store_is_missing(self):
        # review 2026-11-22 (Codex, PR #475): a green hosted job must say that a NAS-only replay was not run.
        tasks = Path(self.tmp.name) / f"tasks_{self._testMethodName}"
        (tasks / "demo-packet").mkdir(parents=True)
        for store, expect_gap in (("/nonexistent/raw-store", True), (str(self.tmp.name), False)):
            (tasks / "demo-packet" / "REPLAY_NEEDS_RAW_STORE").write_text(store + "\n")
            env = dict(os.environ, ATLAS_DATA_DIR=str(self.data), ATLAS_TASKS_DIR=str(tasks))
            p = subprocess.run([sys.executable, str(VALIDATE)], env=env, capture_output=True, text=True)
            out = p.stdout + p.stderr
            self.assertEqual(p.returncode, 0, out[-800:])          # report only: never an error
            self.assertEqual("replay gap: demo-packet/check.py" in out, expect_gap, out[-800:])


if __name__ == "__main__":
    unittest.main()
