"""check_pr_rules: one planted violation per rule that must fail, one compliant case that must pass, the nine
counterexamples from Codex's round-1 review of PR #466, and the git collectors run against a throwaway repository.
Synthetic PRs only."""
import copy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check_pr_rules as c

HEAD = "a" * 40
OLD = "b" * 40
CHECKED = "- **What it checked:** the diff against the rule text and the planted cases\n"
AUDIT = "Label: {label}\nResult: {result}\nSample: 50 rows read\nReviewers: Codex, Gemini\n"


def record(model, sha=HEAD, verdict="APPROVE", harness="Harness", checked=CHECKED, at=None):
    at = f" at `{sha}`" if at is None else at
    return (f"**Review record** (owner ruling 2026-11-22, item 3)\n\n- **Verifier:** {harness}, {model}, default tier.\n"
            f"- **Verdict:** {verdict}{at}, round 1, zero open findings.\n{checked}")


GOOD = {
    "pr": {"number": 7, "head_sha": HEAD, "branch": "agent/claude-code/x", "body": "Built by: Claude Code, Anthropic\n\nrest"},
    "comments": [record("GPT-6.2 Astra"), record("Gemini 4 Hydrogen")],
    "changed_files": ["data/evidence_organizations_OH.csv", "tasks/x/INPUTS.sha256", "tasks/x/README.md"],
    "added_files": ["tasks/x/INPUTS.sha256"],
    "added_evidence_rows": 10, "added_registry_links": 0, "added_decisions_lines": [],
    "main_labels": ["old-lane", "audited-lane"], "baseline_labels": ["old-lane"],
    "audit_texts": {"tasks/y/AUDIT.md": AUDIT.format(label="audited-lane", result="PASS")},
    "inputs_files": {"tasks/x/INPUTS.sha256": "# c\n" + "0" * 64 + "  raw/osha/file.csv\n"},
    "inputs_repo_ok": {},
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


def docs_pr(**kw):
    return mutated(**{"changed_files": ["docs/x.md"], "added_files": [], "added_evidence_rows": 0, **kw})


class TestCompliant(unittest.TestCase):
    def test_compliant_data_pr_passes_and_prints_what_it_inspected(self):
        rc, out = run(GOOD)
        self.assertEqual(rc, 0, out)
        self.assertIn("inspected:", out)
        self.assertIn("hashes themselves are NOT checked", out)

    def test_non_code_pr_needs_one_record(self):
        self.assertEqual(run(docs_pr(comments=[record("GPT-6.2 Astra")]))[0], 0)

    def test_repo_path_in_inputs_passes_when_it_is_a_file(self):
        f = mutated(inputs_files={"tasks/x/INPUTS.sha256": "0" * 64 + "  tasks/x/README.md\n"},
                    inputs_repo_ok={"tasks/x/README.md": True})
        self.assertEqual(run(f)[0], 0)


class TestRules1And4(unittest.TestCase):
    def test_one_family_on_data_pr_fails(self):
        rc, out = run(mutated(comments=[record("GPT-6.2 Astra")]))
        self.assertEqual(rc, 1)
        self.assertIn("1 family(ies) approved", out)

    def test_two_records_same_family_count_once(self):
        self.assertEqual(run(mutated(comments=[record("GPT-6.2 Astra"), record("GPT-6 Luna")]))[0], 1)

    def test_refute_does_not_count(self):
        self.assertEqual(run(mutated(comments=[record("GPT-6.2 Astra", verdict="REFUTE"), record("Gemini 4 Hydrogen")]))[0], 1)

    def test_non_record_comment_ignored(self):
        self.assertEqual(run(mutated(comments=["LGTM, approve at " + HEAD, record("Gemini 4 Hydrogen")]))[0], 1)

    def test_scripts_only_pr_needs_two(self):
        self.assertEqual(run(docs_pr(changed_files=["scripts/x.py"], comments=[record("GPT-6.2 Astra")]))[0], 1)

    def test_missing_built_by_line_fails(self):
        rc, out = run(mutated(pr={"body": "no builder line"}))
        self.assertEqual(rc, 1)
        self.assertIn("Built by", out)

    def test_builder_is_only_reviewer_family_fails(self):
        rc, out = run(docs_pr(comments=[record("Opus 5.5")]))
        self.assertEqual(rc, 1)
        self.assertIn("other than the builder", out)

    # --- Codex r1 finding 1: workflow and checker changes get the two-family bar
    def test_workflow_only_change_needs_two_families(self):
        self.assertEqual(run(docs_pr(changed_files=[".github/workflows/pr-rules.yml"], comments=[record("GPT-6.2 Astra")]))[0], 1)
        self.assertEqual(run(docs_pr(changed_files=[".github/workflows/pr-rules.yml"],
                                     comments=[record("GPT-6.2 Astra"), record("Gemini 4 Hydrogen")]))[0], 0)

    def test_checker_change_needs_two_families(self):
        self.assertEqual(run(docs_pr(changed_files=["scripts/check_pr_rules.py"], comments=[record("GPT-6.2 Astra")]))[0], 1)

    # --- finding 2: latest record per verifier governs; the SHA is read only from the verdict line
    def test_later_refute_at_head_withdraws_approval(self):
        cs = [record("GPT-6.2 Astra"), record("Gemini 4 Hydrogen"), record("Gemini 4 Hydrogen", verdict="REFUTE")]
        rc, out = run(mutated(comments=cs))
        self.assertEqual(rc, 1)
        self.assertIn("withdraws google", out)

    def test_later_approval_after_refute_restores(self):
        cs = [record("GPT-6.2 Astra"), record("Gemini 4 Hydrogen", verdict="REFUTE"), record("Gemini 4 Hydrogen")]
        self.assertEqual(run(mutated(comments=cs))[0], 0)

    def test_refute_by_another_model_of_the_family_blocks_the_family(self):
        cs = [record("GPT-6.2 Astra"), record("Gemini 4 Hydrogen"), record("Gemini 4 Argon", verdict="REFUTE")]
        self.assertEqual(run(mutated(comments=cs))[0], 1)

    def test_abbreviated_sha_with_full_sha_later_in_the_line_is_not_an_approval(self):
        bad = record("Gemini 4 Hydrogen", at=f" at `{OLD[:8]}` (current head {HEAD} not reviewed)")
        rc, out = run(mutated(comments=[record("GPT-6.2 Astra"), bad]))
        self.assertEqual(rc, 1)
        self.assertIn("without a full 40-character SHA", out)

    def test_stale_head_does_not_count(self):
        rc, out = run(mutated(comments=[record("GPT-6.2 Astra", sha=OLD), record("Gemini 4 Hydrogen")]))
        self.assertEqual(rc, 1)
        self.assertIn("stale", out)

    # --- finding 3: family from the model; model, verdict+SHA and what was checked are all required
    def test_same_model_under_two_family_labels_is_one_family(self):
        cs = [record("GPT-6.2 Astra", harness="OpenAI Codex"), record("GPT-6.2 Astra", harness="Google Gemini")]
        self.assertEqual(run(mutated(comments=cs))[0], 1)

    def test_record_without_a_model_does_not_count(self):
        no_model = ("**Review record**\n\n- **Verifier:** Google\n- **Verdict:** APPROVE at `" + HEAD + "`\n" + CHECKED)
        rc, out = run(mutated(comments=[record("GPT-6.2 Astra"), no_model]))
        self.assertEqual(rc, 1)
        self.assertIn("no recognised model", out)

    def test_unknown_model_does_not_count(self):
        self.assertEqual(run(mutated(comments=[record("GPT-6.2 Astra"), record("Mystery Bot 9")]))[0], 1)

    def test_record_without_what_it_checked_does_not_count(self):
        rc, out = run(mutated(comments=[record("GPT-6.2 Astra"), record("Gemini 4 Hydrogen", checked="")]))
        self.assertEqual(rc, 1)
        self.assertIn("What it checked", out)

    def test_muse_maps_to_meta(self):
        self.assertEqual(c.family_of("Muse Spark"), "meta")
        self.assertEqual(c.family_of("Fable 5.2"), "anthropic")

    def test_empty_changed_file_list_is_not_inspected(self):
        rc, out = run(mutated(changed_files=[]))
        self.assertEqual(rc, 1)
        self.assertIn("NOT INSPECTED", out)


class TestRule5(unittest.TestCase):
    def test_over_cap_without_waiver_fails(self):
        rc, out = run(mutated(added_evidence_rows=1001))
        self.assertEqual(rc, 1)
        self.assertIn("size cap", out)

    def test_registry_links_over_cap_fails(self):
        self.assertEqual(run(mutated(added_registry_links=1001))[0], 1)

    def test_at_cap_passes(self):
        self.assertEqual(run(mutated(added_evidence_rows=1000))[0], 0)

    # --- finding 4: exact branch name on an added DECISIONS.md line
    def test_waiver_must_name_exactly_this_branch(self):
        self.assertEqual(run(mutated(added_evidence_rows=3000, added_decisions_lines=["- size waiver for agent/other/y"]))[0], 1)
        longer = ["- size waiver for agent/claude-code/x-extra: 3000 rows"]
        self.assertEqual(run(mutated(added_evidence_rows=3000, added_decisions_lines=longer))[0], 1)
        prefix = ["- size waiver for agent/claude-code/x/more: 3000 rows"]
        self.assertEqual(run(mutated(added_evidence_rows=3000, added_decisions_lines=prefix))[0], 1)
        mine = ["- Size waiver: agent/claude-code/x adds 3000 rows, owner approved"]
        self.assertEqual(run(mutated(added_evidence_rows=3000, added_decisions_lines=mine))[0], 0)

    def test_unaudited_label_blocks_a_data_pr(self):
        rc, out = run(mutated(main_labels=["old-lane", "audited-lane", "new-lane"]))
        self.assertEqual(rc, 1)
        self.assertIn("new-lane", out)

    def test_label_substring_in_audit_is_not_an_audit(self):
        f = mutated(main_labels=["lane"], baseline_labels=[], audit_texts={"tasks/y/AUDIT.md": AUDIT.format(label="audited-lane", result="PASS")})
        self.assertEqual(run(f)[0], 1)

    def test_audit_gate_not_applied_without_data_change(self):
        self.assertEqual(run(docs_pr(main_labels=["new-lane"], comments=[record("GPT-6.2 Astra")]))[0], 0)

    def test_missing_audit_facts_fail_instead_of_pass(self):
        f = mutated()
        del f["main_labels"]
        rc, out = run(f)
        self.assertEqual(rc, 1)
        self.assertIn("NOT INSPECTED", out)

    # --- finding 5 (audit defined by structure) and (a)
    def audited(self, text, labels=("new-lane",)):
        return mutated(main_labels=list(labels), baseline_labels=[], audit_texts={"tasks/y/AUDIT.md": text})

    def test_pending_audit_does_not_count(self):
        rc, out = run(self.audited(AUDIT.format(label="new-lane", result="PENDING")))
        self.assertEqual(rc, 1)
        self.assertIn("exactly PASS or FAIL", out)
        self.assertEqual(run(self.audited("Audit of new-lane is pending."))[0], 1)

    def test_audit_missing_sample_or_reviewers_does_not_count(self):
        for drop in ("Sample", "Reviewers"):
            text = "\n".join(ln for ln in AUDIT.format(label="new-lane", result="PASS").splitlines() if not ln.startswith(drop))
            self.assertEqual(run(self.audited(text))[0], 1, drop)

    def test_fail_audit_blocks(self):
        rc, out = run(self.audited(AUDIT.format(label="new-lane", result="FAIL")))
        self.assertEqual(rc, 1)
        self.assertIn("Result: FAIL", out)

    def test_fail_audit_blocks_even_a_grandfathered_label(self):
        f = self.audited(AUDIT.format(label="old-lane", result="FAIL"), labels=("old-lane",))
        f["baseline_labels"] = ["old-lane"]
        self.assertEqual(run(f)[0], 1)

    def test_valid_pass_audit_clears_label_and_several_labels_per_file(self):
        self.assertEqual(run(self.audited(AUDIT.format(label="new-lane; other lane", result="PASS"), labels=("new-lane", "other lane")))[0], 0)


class TestRule6(unittest.TestCase):
    def inputs(self, line, repo_ok=None):
        return mutated(inputs_files={"tasks/x/INPUTS.sha256": line + "\n"}, inputs_repo_ok=repo_ok or {})

    def test_rows_without_inputs_file_fail(self):
        self.assertEqual(run(mutated(added_files=[], inputs_files={}))[0], 1)

    def test_malformed_line_fails(self):
        rc, out = run(self.inputs("deadbeef  raw/x.csv"))
        self.assertEqual(rc, 1)
        self.assertIn("bad lines", out)

    # --- finding 8
    def test_absolute_dot_dotdot_and_directory_paths_fail(self):
        for path in ("../secret", "/etc/passwd", "C:\\Users\\x\\raw.csv", "C:/x/raw.csv", "\\\\server\\share\\f", ".", "..",
                     "raw/../../x", "raw/./x", "raw/", "raw//x", "raw\\osha\\x.csv"):
            self.assertEqual(run(self.inputs("0" * 64 + "  " + path))[0], 1, path)

    def test_repo_path_must_exist_as_a_file(self):
        line = "0" * 64 + "  tasks/x/missing.csv"
        self.assertEqual(run(self.inputs(line, {"tasks/x/missing.csv": False}))[0], 1)
        rc, out = run(self.inputs(line, {}))
        self.assertEqual(rc, 1)
        self.assertIn("NOT INSPECTED", out)

    def test_provenance_path_accepted(self):
        self.assertEqual(run(self.inputs("0" * 64 + "  provenance/osha/2026/x.csv"))[0], 0)

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


class TestWorkflow(unittest.TestCase):
    """Finding 1 and 9: the workflow judges a PR with the base branch's checker and re-judges on comment edits."""

    text = (Path(__file__).resolve().parent.parent / ".github/workflows/pr-rules.yml").read_text()

    def test_uses_pull_request_target_and_never_the_pr_tree(self):
        self.assertIn("pull_request_target", self.text)
        self.assertNotRegex(self.text, r"(?m)^\s*pull_request:")
        for bad in ("pull_request.head", "head.sha", "head_ref", "refs/pull/${{"):
            self.assertNotIn(bad, self.text)
        self.assertNotRegex(self.text, r"(?m)^\s*ref:")  # actions/checkout stays on the default (base) ref

    def test_comment_edits_and_deletions_re_evaluate(self):
        for kind in ("created", "edited", "deleted"):
            self.assertIn(kind, self.text)
        self.assertNotIn("gh run rerun", self.text)  # selects by PR number via the API, not by run or SHA


class TestCollectors(unittest.TestCase):
    """The collectors against a real repository: identity counting, quoted multiline fields, failed reads."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old_repo, c.REPO = c.REPO, Path(self.tmp.name)
        self.addCleanup(setattr, c, "REPO", self.old_repo)
        self.root = Path(self.tmp.name)

    def g(self, *a):
        subprocess.run(["git", "-C", self.tmp.name, "-c", "user.name=t", "-c", "user.email=t@example.org", *a],
                       check=True, capture_output=True)

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def base_repo(self):
        self.g("init", "-q", "-b", "main")
        self.write("data/evidence_X.csv", "evidence_id,note,created_by\nE1,,lane-a\nE2,,lane-b\n")
        self.write("data/registry_links.csv", "org_id,registry,registry_id,match_basis,as_of,site_id\nO1,UEI,U1,exact,2026-11-01,\n")
        self.write("tasks/y/AUDIT.md", AUDIT.format(label="lane-a", result="PASS"))
        self.write(c.BASELINE, "# c\nlane-b\n")
        self.write("DECISIONS.md", "# d\n")
        self.g("add", "."); self.g("commit", "-qm", "base")
        self.g("checkout", "-q", "-b", "pr")

    def test_row_counts_labels_and_multiline_fields(self):
        self.base_repo()
        self.write("data/evidence_X.csv", 'evidence_id,note,created_by\nE1,,lane-a\nE2,,lane-b\nE3,,"lane-c"\n"E4","a\nb",lane-c\n')
        self.g("commit", "-qam", "head")
        self.assertEqual(c.added_rows("main", "pr", "data/evidence_X.csv", ("evidence_id",)), 2)
        self.assertEqual(c.labels_at("main"), ["lane-a", "lane-b"])
        self.assertEqual(c.labels_at("pr"), ["lane-a", "lane-b", "lane-c"])

    # --- finding 7
    def test_registry_metadata_edit_is_not_a_new_link(self):
        self.base_repo()
        self.write("data/registry_links.csv", "org_id,registry,registry_id,match_basis,as_of,site_id\nO1,UEI,U1,fuzzy,2026-11-22,\nO2,UEI,U2,exact,2026-11-22,\n")
        self.g("commit", "-qam", "head")
        self.assertEqual(c.added_rows("main", "pr", "data/registry_links.csv", c.REGISTRY_IDENTITY), 1)

    def test_path_absent_at_base_is_zero_rows_not_an_error(self):
        self.base_repo()
        self.write("data/evidence_NEW.csv", "evidence_id,note,created_by\nE9,,lane-z\n")
        self.g("add", "."); self.g("commit", "-qm", "new shard")
        self.assertEqual(c.added_rows("main", "pr", "data/evidence_NEW.csv", ("evidence_id",)), 1)
        self.assertEqual(c.added_rows("pr", "main", "data/evidence_NEW.csv", ("evidence_id",)), 0)

    # --- finding 6
    def test_failed_read_of_a_tracked_path_raises(self):
        self.base_repo()
        real = c._git

        def broken(*args):
            if args[0] == "show":
                return subprocess.CompletedProcess(args, 128, "", "fatal: bad object")
            return real(*args)

        with mock.patch.object(c, "_git", broken):
            with self.assertRaises(c.InspectionError):
                c.labels_at("main")
            with self.assertRaises(c.InspectionError):
                c.added_rows("main", "pr", "data/registry_links.csv", c.REGISTRY_IDENTITY)

    def test_collect_reports_a_failed_read_and_the_run_fails(self):
        self.base_repo()
        self.write("data/evidence_X.csv", "evidence_id,note,created_by\nE1,,lane-a\nE2,,lane-b\nE3,,lane-c\n")
        self.g("commit", "-qam", "head")
        head = subprocess.run(["git", "-C", self.tmp.name, "rev-parse", "pr"], capture_output=True, text=True).stdout.strip()
        meta = {"headRefOid": head, "headRefName": "pr", "baseRefName": "main", "body": "Built by: Claude Code, Anthropic",
                "comments": [{"body": record("GPT-6.2 Astra")}, {"body": record("Gemini 4 Hydrogen", sha=head)}]}
        meta["comments"][0]["body"] = record("GPT-6.2 Astra", sha=head)
        real = c._git

        def broken_main_csv(*args):
            if args[0] == "show" and args[1] == "main:data/evidence_X.csv":
                return subprocess.CompletedProcess(args, 128, "", "fatal: bad object")
            return real(*args)

        with mock.patch.object(c, "gh_json", return_value=meta):
            f = c.collect(1, "main")
            self.assertEqual(f["added_evidence_rows"], 1)
            self.assertEqual(f["main_labels"], ["lane-a", "lane-b"])
            self.assertEqual(f["uninspectable"], [])
            with mock.patch.object(c, "_git", broken_main_csv):
                f2 = c.collect(1, "main")
        self.assertTrue(f2["uninspectable"])
        self.assertEqual(c.run(f2, lambda s: None), 1)

    def test_collect_end_to_end_inputs_decisions_and_audit(self):
        self.base_repo()
        self.write("data/evidence_X.csv", "evidence_id,note,created_by\nE1,,lane-a\nE2,,lane-b\nE3,,lane-c\n")
        self.write("tasks/z/INPUTS.sha256", "0" * 64 + "  raw/x.csv\n" + "1" * 64 + "  tasks/y/AUDIT.md\n" + "2" * 64 + "  tasks/y\n")
        self.write("DECISIONS.md", "# d\n- size waiver pr\n")
        self.g("add", "."); self.g("commit", "-qm", "head")
        head = subprocess.run(["git", "-C", self.tmp.name, "rev-parse", "pr"], capture_output=True, text=True).stdout.strip()
        meta = {"headRefOid": head, "headRefName": "pr", "baseRefName": "main", "body": "x", "comments": []}
        with mock.patch.object(c, "gh_json", return_value=meta):
            f = c.collect(1, "main")
        self.assertEqual(f["uninspectable"], [])
        self.assertEqual(f["added_decisions_lines"], ["- size waiver pr"])
        self.assertEqual(f["inputs_repo_ok"], {"tasks/y/AUDIT.md": True, "tasks/y": False})  # a directory is not a file
        self.assertEqual(f["baseline_labels"], ["lane-b"])
        self.assertEqual(list(f["audit_texts"]), ["tasks/y/AUDIT.md"])
        self.assertEqual(f["inputs_files"]["tasks/z/INPUTS.sha256"].count("\n"), 3)
