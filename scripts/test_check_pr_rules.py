"""check_pr_rules: one planted violation per rule that must fail, one compliant case that must pass, and the git
collectors run against a throwaway repository. Synthetic PRs only."""
import copy
import subprocess
import tempfile
import unittest
from pathlib import Path

import check_pr_rules as c

HEAD = "a" * 40
OLD = "b" * 40


def record(verifier, sha=HEAD, verdict="APPROVE"):
    return (f"**Review record** (owner ruling 2026-11-22, item 3)\n\n- **Verifier:** {verifier}, default tier.\n"
            f"- **Verdict:** {verdict} at `{sha}`, round 1, zero open findings.\n- **What it checked:** x\n")


GOOD = {
    "pr": {"number": 7, "head_sha": HEAD, "branch": "agent/claude-code/x", "body": "Built by: Claude Code, Anthropic\n\nrest"},
    "comments": [record("OpenAI Codex, GPT-6.2 Astra"), record("Google Gemini, 4 Hydrogen")],
    "changed_files": ["data/evidence_organizations_OH.csv", "tasks/x/INPUTS.sha256", "tasks/x/README.md"],
    "added_files": ["tasks/x/INPUTS.sha256"],
    "added_evidence_rows": 10, "added_registry_links": 0, "added_decisions_lines": [],
    "main_labels": ["old-lane", "audited-lane"], "baseline_labels": ["old-lane"],
    "audit_texts": {"tasks/y/AUDIT.md": "Audit of audited-lane: 20 rows read."},
    "inputs_files": {"tasks/x/INPUTS.sha256": "# c\n" + "0" * 64 + "  raw/osha/file.csv\n"},
}


def run(f):
    lines = []
    return c.run(f, lines.append), "\n".join(lines)


def mutated(**kw):
    f = copy.deepcopy(GOOD)
    for k, v in kw.items():
        if k == "pr":
            f["pr"].update(v)
        else:
            f[k] = v
    return f


class TestCompliant(unittest.TestCase):
    def test_compliant_data_pr_passes_and_prints_what_it_inspected(self):
        rc, out = run(GOOD)
        self.assertEqual(rc, 0, out)
        self.assertIn("inspected:", out)
        self.assertIn("hashes themselves are NOT checked", out)

    def test_non_data_pr_needs_one_record(self):
        f = mutated(changed_files=["docs/x.md"], added_files=[], added_evidence_rows=0, comments=[record("OpenAI Codex, GPT-6.2 Astra")])
        self.assertEqual(run(f)[0], 0)


class TestRules1And4(unittest.TestCase):
    def test_one_family_on_data_pr_fails(self):
        rc, out = run(mutated(comments=[record("OpenAI Codex, GPT-6.2 Astra")]))
        self.assertEqual(rc, 1)
        self.assertIn("1 family(ies) approved", out)

    def test_two_records_same_family_count_once(self):
        self.assertEqual(run(mutated(comments=[record("OpenAI Codex, GPT-6.2 Astra"), record("OpenAI Codex, GPT-6 Luna")]))[0], 1)

    def test_stale_head_does_not_count(self):
        rc, out = run(mutated(comments=[record("OpenAI Codex, A", sha=OLD), record("Google Gemini, B")]))
        self.assertEqual(rc, 1)
        self.assertIn("stale", out)

    def test_refute_does_not_count(self):
        self.assertEqual(run(mutated(comments=[record("OpenAI Codex, A", verdict="REFUTE"), record("Google Gemini, B")]))[0], 1)

    def test_unknown_family_does_not_count(self):
        rc, out = run(mutated(comments=[record("Mystery Bot, v1"), record("Google Gemini, B")]))
        self.assertEqual(rc, 1)
        self.assertIn("not recognised", out)

    def test_non_record_comment_ignored(self):
        self.assertEqual(run(mutated(comments=["LGTM, approve at " + HEAD, record("Google Gemini, B")]))[0], 1)

    def test_scripts_only_pr_needs_two(self):
        f = mutated(changed_files=["scripts/x.py"], added_files=[], added_evidence_rows=0, comments=[record("OpenAI Codex, A")])
        self.assertEqual(run(f)[0], 1)

    def test_missing_built_by_line_fails(self):
        rc, out = run(mutated(pr={"body": "no builder line"}))
        self.assertEqual(rc, 1)
        self.assertIn("Built by", out)

    def test_builder_is_only_reviewer_family_fails(self):
        f = mutated(changed_files=["docs/x.md"], added_files=[], added_evidence_rows=0,
                    comments=[record("Anthropic Claude, Opus 5.5")])
        rc, out = run(f)
        self.assertEqual(rc, 1)
        self.assertIn("other than the builder", out)


class TestRule5(unittest.TestCase):
    def test_over_cap_without_waiver_fails(self):
        rc, out = run(mutated(added_evidence_rows=1001))
        self.assertEqual(rc, 1)
        self.assertIn("size cap", out)

    def test_registry_links_over_cap_fails(self):
        self.assertEqual(run(mutated(added_registry_links=1001))[0], 1)

    def test_at_cap_passes(self):
        self.assertEqual(run(mutated(added_evidence_rows=1000))[0], 0)

    def test_waiver_must_name_this_branch(self):
        other = ["- size waiver for agent/other/y: 3000 rows"]
        self.assertEqual(run(mutated(added_evidence_rows=3000, added_decisions_lines=other))[0], 1)
        mine = ["- Size waiver: agent/claude-code/x adds 3000 rows, owner approved"]
        self.assertEqual(run(mutated(added_evidence_rows=3000, added_decisions_lines=mine))[0], 0)

    def test_unaudited_label_blocks_a_data_pr(self):
        rc, out = run(mutated(main_labels=["old-lane", "audited-lane", "new-lane"]))
        self.assertEqual(rc, 1)
        self.assertIn("new-lane", out)

    def test_label_substring_in_audit_is_not_an_audit(self):
        f = mutated(main_labels=["lane"], baseline_labels=[], audit_texts={"tasks/y/AUDIT.md": "audited-lane only"})
        self.assertEqual(run(f)[0], 1)

    def test_audit_gate_not_applied_without_data_change(self):
        f = mutated(changed_files=["docs/x.md"], added_files=[], added_evidence_rows=0, main_labels=["new-lane"],
                    comments=[record("OpenAI Codex, A")])
        self.assertEqual(run(f)[0], 0)

    def test_missing_audit_facts_fail_instead_of_pass(self):
        f = mutated()
        del f["main_labels"]
        rc, out = run(f)
        self.assertEqual(rc, 1)
        self.assertIn("NOT INSPECTED", out)


class TestRule6(unittest.TestCase):
    def test_rows_without_inputs_file_fail(self):
        self.assertEqual(run(mutated(added_files=[], inputs_files={}))[0], 1)

    def test_malformed_line_fails(self):
        f = mutated(inputs_files={"tasks/x/INPUTS.sha256": "deadbeef  raw/x.csv\n"})
        rc, out = run(f)
        self.assertEqual(rc, 1)
        self.assertIn("malformed", out)

    def test_escaping_or_absolute_path_fails(self):
        for path in ("../secret", "/etc/passwd"):
            self.assertEqual(run(mutated(inputs_files={"tasks/x/INPUTS.sha256": "0" * 64 + "  " + path + "\n"}))[0], 1, path)

    def test_registry_links_also_need_inputs(self):
        self.assertEqual(run(mutated(added_evidence_rows=0, added_registry_links=5, added_files=[], inputs_files={}))[0], 1)

    def test_no_rows_no_inputs_needed(self):
        f = mutated(added_evidence_rows=0, added_files=[], inputs_files={}, changed_files=["data/organizations_OH.csv"])
        self.assertEqual(run(f)[0], 0)

    def test_unreadable_inputs_file_fails(self):
        self.assertEqual(run(mutated(inputs_files={"tasks/x/INPUTS.sha256": None}))[0], 1)


class TestUninspectable(unittest.TestCase):
    def test_collection_failure_fails_the_run(self):
        rc, out = run({"uninspectable": ["gh pr view failed"]})
        self.assertEqual(rc, 1)
        self.assertIn("COULD NOT COLLECT", out)

    def test_empty_facts_fail(self):
        self.assertEqual(run({})[0], 1)


class TestCollectors(unittest.TestCase):
    """added_rows and labels_at against a real repository; header-only and multiline-quoted rows included."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old_repo, c.REPO = c.REPO, Path(self.tmp.name)
        self.addCleanup(setattr, c, "REPO", self.old_repo)

    def g(self, *a):
        subprocess.run(["git", "-C", self.tmp.name, "-c", "user.name=t", "-c", "user.email=t@example.org", *a],
                       check=True, capture_output=True)

    def test_row_counts_and_labels(self):
        d = Path(self.tmp.name) / "data"
        d.mkdir()
        self.g("init", "-q", "-b", "main")
        (d / "evidence_X.csv").write_text('evidence_id,note,created_by\nE1,,lane-a\nE2,,lane-b\n')
        (d / "registry_links.csv").write_text("org_id,registry\nO1,UEI\n")
        self.g("add", "."); self.g("commit", "-qm", "base")
        (d / "evidence_X.csv").write_text('evidence_id,note,created_by\nE1,,lane-a\nE2,,lane-b\nE3,,"lane-c"\n"E4","a\nb",lane-c\n')
        (d / "registry_links.csv").write_text("org_id,registry\nO1,UEI\nO2,FRS\n")
        self.g("commit", "-qam", "head")
        self.assertEqual(c.added_rows("HEAD~1", "HEAD", "data/evidence_X.csv", "evidence_id"), 2)
        self.assertEqual(c.added_rows("HEAD~1", "HEAD", "data/registry_links.csv", None), 1)
        self.assertEqual(c.labels_at("HEAD~1"), ["lane-a", "lane-b"])
        self.assertEqual(c.labels_at("HEAD"), ["lane-a", "lane-b", "lane-c"])


if __name__ == "__main__":
    unittest.main()
