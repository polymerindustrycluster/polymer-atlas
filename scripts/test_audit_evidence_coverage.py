"""Regression fixtures for read-only inventory semantics, not company facts."""
import csv
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("audit_evidence_coverage.py"))
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def record(table="organizations", rid="ORG-000001", status="active", **kwargs):
    key = "operating_status" if table == "sites" else "status"
    return {(table, rid): {key: status, "verification_tier": "A", "legal_name": "Fixture", **kwargs}}


def ev(claim="existence", effect="supports_A", observed="2026-10-29", table="organizations", rid="ORG-000001", sc="own_site", eid="EVD-000001"):
    return dict(evidence_id=eid, record_table=table, record_id=rid, claim_type=claim,
                tier_effect=effect, observed_date=observed, source_class=sc)


class CoverageTests(unittest.TestCase):
    def test_no_rows_not_failure_or_queue(self):
        result = audit.analyze(record(last_verified="2026-10-30"), [])
        self.assertEqual(result["summary"][0]["no_rows_history_unknown"], 1)
        self.assertEqual(result["review_queue_total"], 0)
        self.assertEqual(result["gaps_among_records_with_rows"], [])

    def test_partial_rows_are_gaps_not_validity_verdicts(self):
        result = audit.analyze(record(), [ev()])
        self.assertEqual(result["summary"][0]["started_with_gaps"], 1)
        row = result["review_queue"][0]
        self.assertEqual(row["missing_claim_rows"], ["activity", "address", "code", "liveness", "scope"])
        self.assertNotIn("verdict", row)

    def test_current_value_claim_rules(self):
        self.assertEqual(audit.expected_claims("programs", {"cip_code": ""}), {"existence", "scope"})
        self.assertEqual(audit.expected_claims("programs", {"cip_code": "15.0611"}), {"existence", "scope", "code"})
        self.assertNotIn("liveness", audit.expected_claims("sites", {"operating_status": "unknown"}))
        self.assertIn("parent", audit.expected_claims("sites", {}))
        self.assertNotIn("parent", audit.expected_claims("organizations", {"parent_org_id": "ORG-000002"}))

    def test_same_day_contradiction_not_resolved_by_support(self):
        result = audit.analyze(record(), [ev(), ev(effect="contradicts", eid="EVD-000002")])
        self.assertEqual(result["review_queue"][0]["contradicted_claims"], ["existence"])

    def test_newer_support_resolves_date_signal(self):
        result = audit.analyze(record(), [ev(observed="2026-10-30"), ev(effect="contradicts", eid="EVD-000002")])
        self.assertEqual(result["review_queue"][0]["contradicted_claims"], [])

    def test_contradiction_only_is_not_support(self):
        result = audit.analyze(record(), [ev(effect="contradicts")])
        self.assertEqual(result["review_queue"][0]["unsupported_present_claims"], ["existence"])

    def test_platform_scope_not_support(self):
        result = audit.analyze(record(), [ev(claim="scope", effect="supports_C", sc="platform_category")])
        self.assertEqual(result["review_queue"][0]["unsupported_present_claims"], ["scope"])

    def test_optional_parent_contradiction_is_still_reviewed(self):
        result = audit.analyze(record(), [ev("parent", "contradicts")])
        self.assertEqual(result["review_queue"][0]["contradicted_claims"], ["parent"])

    def test_unknown_status_liveness_contradiction_is_reviewed(self):
        result = audit.analyze(record(status="unknown"), [ev("liveness", "contradicts")])
        self.assertEqual(result["review_queue"][0]["contradicted_claims"], ["liveness"])

    def test_full_claim_presence_does_not_imply_no_contradiction(self):
        rows = [ev(c, table="programs", rid="PROG-000001", eid=f"EVD-{i:06d}") for i, c in enumerate(("existence", "scope"), 1)]
        rows.append(ev("scope", "contradicts", table="programs", rid="PROG-000001", eid="EVD-000003"))
        result = audit.analyze(record("programs", "PROG-000001"), rows)
        self.assertEqual(result["summary"][0]["claim_rows_present"], 1)
        self.assertEqual(result["summary"][0]["records_with_current_contradiction"], 1)

    def test_table_qualified_ids_do_not_collide(self):
        records = record() | record("ecosystem")
        result = audit.analyze(records, [ev()])
        self.assertEqual(result["summary"][0]["table"], "ecosystem")
        self.assertEqual(result["summary"][0]["no_rows_history_unknown"], 1)
        self.assertEqual(result["summary"][1]["started_with_gaps"], 1)

    def test_retired_records_counted_but_not_queued(self):
        result = audit.analyze(record(status="merged"), [ev()])
        self.assertEqual(result["summary"][0]["records"], 1)
        self.assertEqual(result["review_queue_total"], 0)

    def test_limit_and_order_are_deterministic(self):
        records = record(rid="ORG-000002") | record()
        rows = [ev(rid="ORG-000002", eid="EVD-000002"), ev()]
        self.assertEqual(audit.analyze(records, rows, 1)["review_queue"][0]["record_id"], "ORG-000001")
        self.assertEqual(audit.analyze(records, rows, 0)["review_queue_total"], 2)
        self.assertEqual(audit.analyze(records, rows, 0)["review_queue"], [])
        with self.assertRaises(ValueError):
            audit.analyze(records, rows, -1)

    def test_cli_no_data_mutation_and_manifest(self):
        data = Path(__file__).resolve().parents[1] / "data"
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob("*.csv")}
        command = [sys.executable, str(Path(__file__).with_name("audit_evidence_coverage.py")), "--as-of", "2026-10-30", "--limit", "2"]
        run = subprocess.run(command, check=True, capture_output=True, text=True)
        result = json.loads(run.stdout)
        self.assertLessEqual(len(result["review_queue"]), 2)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob("*.csv")})
        self.assertTrue(all(before[r["path"]] == r["sha256"] for r in result["input_manifest"]))
        self.assertEqual(run.stdout, subprocess.run(command, check=True, capture_output=True, text=True).stdout)

    def test_invalid_date_fails_closed(self):
        command = [sys.executable, str(Path(__file__).with_name("audit_evidence_coverage.py")), "--as-of", "2026"]
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_generated_export_excluded_and_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            for table, (pattern, id_col, _) in audit.TABLES.items():
                filename = pattern.replace("*", "OH")
                (p / filename).write_text(f"{id_col},verification_tier\nID-{table},A\n")
            (p / "organizations_all.csv").write_text("org_id,verification_tier\nGENERATED,A\n")
            (p / "evidence.csv").write_text("evidence_id,record_table,record_id,claim_type,tier_effect,source_class,observed_date\n")
            records, rows, manifest = audit.inventory(p)
            self.assertEqual(len(records), 4)
            self.assertNotIn("organizations_all.csv", [r["path"] for r in manifest])
            (p / "organizations_PA.csv").write_text("org_id,verification_tier\nID-organizations,A\n")
            with self.assertRaises(ValueError):
                audit.inventory(p)

    def test_missing_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                audit.inventory(Path(temp))


if __name__ == "__main__":
    unittest.main()
