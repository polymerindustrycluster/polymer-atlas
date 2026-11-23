"""check_pr_rules: one planted violation per check that must fail, one compliant case that must pass, the
counterexamples from Codex's two review rounds on PR #466, and the git collectors run against a throwaway repository.
The checker reads no PR comment and no review record (owner ruling 2026-11-22). Synthetic PRs only."""
import copy
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check_pr_rules as c

HEAD = "a" * 40
OLD = "b" * 40
AUDIT = "Label: {label}\nResult: {result}\nSample: 50 rows read\nReviewers: Codex, Gemini\n"


GOOD = {
    "pr": {"number": 7, "head_sha": HEAD, "branch": "agent/claude-code/x"},
    "changed_files": ["data/evidence_organizations_OH.csv", "tasks/x/INPUTS.sha256", "tasks/x/README.md"],
    "added_files": ["tasks/x/INPUTS.sha256"],
    "added_evidence_rows": 10, "added_registry_links": 0, "added_decisions_lines": [],
    "main_labels": ["old-lane", "audited-lane"], "baseline_labels": ["old-lane"],
    "audit_texts": {"tasks/y/AUDIT.md": AUDIT.format(label="audited-lane", result="PASS")},
    "inputs_files": {"tasks/x/INPUTS.sha256": "# c\n" + "0" * 64 + "  raw/osha/file.csv\n"},
    "inputs_repo_ok": {},
    "replay_scripts": ["tasks/x/check.py"],
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

    def test_non_data_pr_passes_without_any_record(self):
        self.assertEqual(run(docs_pr())[0], 0)

    def test_empty_changed_file_list_is_not_inspected(self):
        rc, out = run(mutated(changed_files=[]))
        self.assertEqual(rc, 1)
        self.assertIn("NOT INSPECTED", out)

    def test_no_review_record_is_read_anywhere(self):
        # owner ruling 2026-11-22: review is practice; neither the facts nor the checker carry comments or PR bodies
        src = (Path(__file__).resolve().parent / "check_pr_rules.py").read_text()
        for gone in ("review_votes", "family_of", "counted_families", "Built by", '"comments"', "issue_comment"):
            self.assertNotIn(gone, src)
        self.assertEqual(run(mutated(comments=["**Review record** REFUTE"]))[0], 0)  # an unused fact changes nothing
        # the one mention of a Review record is the fixed NOT RUN sentence; it is printed, never read from a comment



    def test_repo_path_in_inputs_passes_when_it_is_a_file(self):
        f = mutated(inputs_files={"tasks/x/INPUTS.sha256": "0" * 64 + "  tasks/x/README.md\n"},
                    inputs_repo_ok={"tasks/x/README.md": True})
        self.assertEqual(run(f)[0], 0)


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
    def waiver(self, line):
        return run(mutated(added_evidence_rows=3000, added_decisions_lines=[line]))[0]

    def test_waiver_compares_the_complete_branch_field_for_equality(self):
        base = "agent/claude-code/x"
        for suffix in ("+alternate", "-extra", "/more", ".y", ",", ";", "@x", "#1", "%", "=y", "'", ")", "}", "_", "!", "&",
                       "$", "(", "{", "x", "..", ".lock", "\u00e9"):
            self.assertEqual(self.waiver(f"- Size waiver: branch={base}{suffix} adds 3000 rows"), 1, suffix)
        self.assertEqual(self.waiver("- size waiver: branch=agent/other/y adds 3000 rows"), 1)
        self.assertEqual(self.waiver("- size waiver for agent/claude-code/x (no branch= field)"), 1)
        self.assertEqual(self.waiver("- branch=agent/claude-code/x adds 3000 rows (no waiver words)"), 1)
        self.assertEqual(self.waiver("- Size waiver: xbranch=agent/claude-code/x"), 1)
        self.assertEqual(self.waiver("- Size waiver: branch=agent/claude-code/x adds 3000 rows, owner approved"), 0)
        self.assertEqual(self.waiver("- size waiver: branch=agent/other/y and branch=agent/claude-code/x"), 0)

    def test_unaudited_label_blocks_a_data_pr(self):
        rc, out = run(mutated(main_labels=["old-lane", "audited-lane", "new-lane"]))
        self.assertEqual(rc, 1)
        self.assertIn("new-lane", out)

    def test_label_substring_in_audit_is_not_an_audit(self):
        f = mutated(main_labels=["lane"], baseline_labels=[], audit_texts={"tasks/y/AUDIT.md": AUDIT.format(label="audited-lane", result="PASS")})
        self.assertEqual(run(f)[0], 1)

    def test_audit_gate_not_applied_without_data_change(self):
        self.assertEqual(run(docs_pr(main_labels=["new-lane"]))[0], 0)

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
                     "raw/../../x", "raw/./x", "raw/", "raw//x", "raw\\osha\\x.csv", "provenance/", "provenance//x"):
            self.assertEqual(run(self.inputs("0" * 64 + "  " + path))[0], 1, path)

    def test_the_store_itself_is_not_a_file(self):
        # the bare word names the store (finding 4): below raw/ or provenance/ needs at least one component
        for word in ("raw", "provenance"):
            line = "0" * 64 + "  " + word
            self.assertEqual(run(self.inputs(line, {word: False}))[0], 1, word)
            self.assertEqual(run(self.inputs(line))[0], 1, word)  # also not inspected as a repo path
        self.assertFalse(c.in_store("raw") or c.in_store("provenance"))
        self.assertTrue(c.in_store("raw/x") and c.in_store("provenance/a/b.csv"))

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
    """The workflow judges a PR with the base branch's checker, and reads no comment."""

    text = (Path(__file__).resolve().parent.parent / ".github/workflows/pr-rules.yml").read_text()

    def test_uses_pull_request_target_and_evaluate_never_checks_out_the_pr(self):
        self.assertIn("pull_request_target", self.text)
        self.assertNotRegex(self.text, r"(?m)^\s*pull_request:")
        evaluate = self.text[:self.text.index("\n  gate-run:")]
        publish = self.text[self.text.index("\n  publish-binding-gate:"):]
        for part in (evaluate, publish):
            for bad in ("pull_request.head", "head.sha", "head_ref", "refs/pull/${{"):
                self.assertNotIn(bad, part)
            self.assertNotRegex(part, r"(?m)^\s*ref:")  # actions/checkout stays on the default (base) ref

    def test_no_comment_trigger_and_no_comment_reading(self):
        self.assertNotRegex(self.text, r"(?m)^\s*issue_comment:")
        self.assertNotIn("github.event.issue", self.text)
        self.assertNotIn("github.event.comment", self.text)


class TestReplayNotRun(unittest.TestCase):
    NOTE = "source replay not run in hosted CI: needs the shared store; it is run by the reviewers and recorded in the Review record comment"

    def test_pr_adding_evidence_row_and_check_py_prints_not_run(self):
        rc, out = run(mutated(added_evidence_rows=1))
        self.assertEqual(rc, 0, out)  # the conclusion stays as the other rules decide
        self.assertIn("NOT RUN: tasks/x/check.py", out)
        self.assertIn("NOT RUN: " + self.NOTE, out)
        self.assertTrue(c.replay_not_run(mutated(added_evidence_rows=1)))

    def test_registry_links_and_a_missing_check_py_also_print_it(self):
        rc, out = run(mutated(added_evidence_rows=0, added_registry_links=2, replay_scripts=[]))
        self.assertIn("NOT RUN: the PR adds or changes no tasks/*/check.py", out)
        self.assertIn(self.NOTE, out)

    def test_docs_only_pr_does_not(self):
        rc, out = run(docs_pr(replay_scripts=[]))
        self.assertEqual(rc, 0)
        self.assertNotIn("NOT RUN", out)
        self.assertFalse(c.replay_not_run(docs_pr()))

    def test_unknown_replay_facts_fail_the_run(self):
        f = mutated(added_evidence_rows=1)
        del f["replay_scripts"]
        self.assertEqual(run(f)[0], 1)

    def test_collect_names_added_and_changed_check_py(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            g = lambda *a: subprocess.run(["git", "-C", t, "-c", "user.name=t", "-c", "user.email=t@example.org", *a], check=True, capture_output=True)
            g("init", "-q", "-b", "main")
            (root / "data").mkdir()
            (root / "tasks/a").mkdir(parents=True)
            (root / "data/evidence_X.csv").write_text("evidence_id,created_by\nE1,l\n")
            (root / "tasks/a/check.py").write_text("1\n")
            (root / "tasks/a/other.py").write_text("1\n")
            (root / "tasks/c").mkdir()
            (root / "tasks/c/check.py").symlink_to("../a/check.py")  # tracked symlink at base; the PR makes it a regular file (git status T)
            (root / c.BASELINE).parent.mkdir(parents=True, exist_ok=True)
            (root / c.BASELINE).write_text("l\n")
            g("add", "-A"); g("commit", "-qm", "b"); g("checkout", "-q", "-b", "pr")
            (root / "data/evidence_X.csv").write_text("evidence_id,created_by\nE1,l\nE2,l\n")
            (root / "tasks/a/check.py").write_text("2\n")
            (root / "tasks/a/other.py").write_text("2\n")
            (root / "tasks/c/check.py").unlink()
            (root / "tasks/c/check.py").write_text("3\n")
            (root / "tasks/b").mkdir()
            (root / "tasks/b/check.py").write_text("1\n")
            (root / "tasks/b/sub").mkdir()
            (root / "tasks/b/sub/check.py").write_text("1\n")
            g("add", "-A"); g("commit", "-qm", "h")
            head = subprocess.run(["git", "-C", t, "rev-parse", "pr"], capture_output=True, text=True).stdout.strip()
            old, c.REPO = c.REPO, root
            try:
                with mock.patch.object(c, "gh_json", return_value={"headRefOid": head, "headRefName": "pr", "baseRefName": "main"}):
                    f = c.collect(1, "main")
            finally:
                c.REPO = old
        # tasks/c/check.py is a type change (symlink -> regular file): a replay the PR supplies, so it is named too
        self.assertEqual(sorted(f["replay_scripts"]), ["tasks/a/check.py", "tasks/b/check.py", "tasks/c/check.py"])  # not other.py, not tasks/b/sub/


class TestBindingGateJob(unittest.TestCase):
    """The only job that checks out PR content holds no token, keeps no credential, and runs main's gate on it."""

    text = TestWorkflow.text
    job = text[text.index("\n  gate-run:"):text.index("\n  publish-binding-gate:")]
    publish = text[text.index("\n  publish-binding-gate:"):]

    def test_gate_job_has_no_token_and_no_persisted_credential_on_either_checkout(self):
        self.assertIn("permissions: {}", self.job)
        self.assertEqual(self.job.count("persist-credentials: false"), 2)
        self.assertEqual(self.job.count("actions/checkout@v4"), 2)
        for bad in ("GH_TOKEN", "github.token", "secrets.", "GITHUB_TOKEN", "checks: write"):
            self.assertNotIn(bad, self.job)

    def test_pr_is_checked_out_as_data_into_pr_and_main_runs_exactly_two_gate_modes(self):
        self.assertIn("ref: refs/pull/${{ env.PR }}/merge", self.job)
        self.assertIn("path: pr", self.job)
        self.assertIn("for mode in --new-since --provenance-since; do", self.job)
        self.assertIn('scripts/check_evidence_binding.py "$mode" "$BASE" --tree pr', self.job)
        self.assertIn("gate not yet on main", self.job)
        self.assertNotIn("python3 pr/", self.job)  # nothing is run from the PR tree
        self.assertIn("fetch-depth: 0", self.job)

    def test_no_isolation_probe_no_proof_fetch_no_neutral_result(self):
        for bad in ("verify-proofs", "unshare", "docker", "sysctl", "setpriv", "skipped", "neutral"):
            self.assertNotIn(bad, self.job.lower())
        self.assertNotIn("neutral", self.text.lower().replace("never neutral", ""))

    def test_exactly_one_check_is_named_binding_gate_and_one_pr_rules(self):
        # a job's check run takes the job's name (or its `name:`); the published runs are posted by the script by name
        yml = self.text
        jobs = re.findall(r"(?m)^  ([\w-]+):", yml[yml.index("\njobs:"):])
        self.assertEqual(jobs, ["evaluate", "gate-run", "publish-binding-gate"])
        self.assertNotRegex(yml, r"(?m)^\s+name:\s*(binding-gate|pr-rules)\s*$")  # no job `name:` that collides
        self.assertIn("needs: gate-run", self.publish)
        self.assertIn("needs.gate-run.result", self.publish)
        self.assertNotIn("needs.binding-gate", yml)

    def test_only_the_publish_job_holds_a_token(self):
        self.assertIn("checks: write", self.publish)
        self.assertEqual(self.text.count("checks: write"), 2)  # evaluate (top level) and publish; never the gate job


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
        meta = {"headRefOid": head, "headRefName": "pr", "baseRefName": "main"}
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
        meta = {"headRefOid": head, "headRefName": "pr", "baseRefName": "main"}
        with mock.patch.object(c, "gh_json", return_value=meta):
            f = c.collect(1, "main")
        self.assertEqual(f["uninspectable"], [])
        self.assertEqual(f["added_decisions_lines"], ["- size waiver pr"])
        self.assertEqual(f["inputs_repo_ok"], {"tasks/y/AUDIT.md": True, "tasks/y": False})  # a directory is not a file
        self.assertEqual(f["baseline_labels"], ["lane-b"])
        self.assertEqual(list(f["audit_texts"]), ["tasks/y/AUDIT.md"])
        self.assertEqual(f["inputs_files"]["tasks/z/INPUTS.sha256"].count("\n"), 3)

    def test_repo_input_is_looked_up_literally(self):
        # Codex r3: ":README.md" is a git pathspec that matched README.md; it must not pass as an input name
        self.base_repo()
        self.write("README.md", "x\n")
        self.write("data/evidence_X.csv", "evidence_id,note,created_by\nE1,,lane-a\nE2,,lane-b\nE3,,lane-c\n")
        names = (":README.md", "./README.md", "README.md/", ":(top)README.md", "READ*.md", "README.md")
        self.write("tasks/z/INPUTS.sha256", "".join("0" * 64 + "  " + n + "\n" for n in names))
        self.g("add", "."); self.g("commit", "-qm", "head")
        head = subprocess.run(["git", "-C", self.tmp.name, "rev-parse", "pr"], capture_output=True, text=True).stdout.strip()
        with mock.patch.object(c, "gh_json", return_value={"headRefOid": head, "headRefName": "pr", "baseRefName": "main"}):
            f = c.collect(1, "main")
        self.assertEqual(f["inputs_repo_ok"], {":README.md": False, ":(top)README.md": False, "READ*.md": False, "README.md": True})
        rc, out = run(f)
        self.assertEqual(rc, 1)
        self.assertIn("bad lines", out)  # "./README.md" and "README.md/" fail the path grammar before any lookup
