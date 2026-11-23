"""Tests for the nightly watch (scripts/nightly_watch.py): one planted case per finding a-g that must fire, one clean
day that must pass, and API failures that must fail, never pass quietly."""
import json, os, subprocess, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_row_loss
import nightly_watch as nw


def clean():
    """A quiet day: one data PR with two review records, a successful validate that finished before the merge."""
    return {
        "ref": "origin/main", "since": "2026-11-20T11:17:00Z", "until": "2026-11-21T11:17:00Z", "base": "aaaaaaaaaa",
        "head": "bbbbbbbbbb", "errors": [], "task_folders": ["evidence-fix-2026-11-20", "alpha-lane-pass-3"],
        "commits": [{"sha": "bbbbbbbbbb", "date": "2026-11-21T01:00:00Z", "subject": "s", "pr": 10, "data_files": 2,
                     "evidence_added": {"claude-code evidence-fix-2026-11-20": 40}, "links_added": 5, "removed": {}}],
        "prs": [{"number": 10, "merged_at": "2026-11-21T01:00:00Z", "merge_sha": "bbbbbbbbbb", "head_sha": "cccccccccc",
                 "review_records": 2, "data_files": 2, "train_member": False,
                 "validate": {"status": "completed", "conclusion": "success", "started_at": "2026-11-21T00:40:00Z",
                              "completed_at": "2026-11-21T00:45:00Z"}}],
        "unknown": {"before": {"n": 800, "proc": 300, "mkt": 300, "band": 400},
                    "after": {"n": 800, "proc": 290, "mkt": 300, "band": 400}},
        "main_validate": {"conclusion": "success", "created_at": "2026-11-21T01:00:05Z", "head_sha": "bbbbbbbbbb"},
    }


def letters(facts):
    findings, _ = nw.analyze(facts)
    return {f[1] for f in findings}  # "[a] ..." -> "a"


class Planted(unittest.TestCase):
    def test_clean_day_passes(self):
        text, code = nw.report(clean())
        self.assertEqual(code, 0, text)
        self.assertIn("PASS", text)
        for line in ("commits: 1 first-parent", "pull requests: #10", "rows added: 40 evidence", "5 registry links"):
            self.assertIn(line, text)  # it always says what it inspected

    def test_a_evidence_rows_per_label_and_per_pr(self):
        f = clean()
        f["commits"][0]["evidence_added"] = {"claude-code evidence-fix-2026-11-20": 1001}
        findings, _ = nw.analyze(f)
        self.assertEqual({x[1] for x in findings}, {"a"})
        self.assertEqual(len(findings), 2)  # the label and the PR both exceed the limit
        f = clean()  # the same rows split over two PRs under one label: the label total still fires
        f["commits"] += [dict(f["commits"][0], sha="dddddddddd", pr=11, evidence_added={"claude-code evidence-fix-2026-11-20": 600})]
        f["commits"][0]["evidence_added"] = {"claude-code evidence-fix-2026-11-20": 600}
        self.assertEqual(letters(f), {"a"})

    def test_a_registry_links_per_pr(self):
        f = clean()
        f["commits"][0]["links_added"] = 6837
        self.assertEqual(letters(f), {"a"})

    def test_a_counts_a_batch_that_was_reverted_the_same_window(self):
        f = clean()  # +23,564 then a revert: the revert shows as removals (declared), the batch must still fire
        f["commits"].append(dict(f["commits"][0], sha="eeeeeeeeee", pr=12, data_files=3, evidence_added={}, links_added=0))
        f["commits"][0]["evidence_added"] = {"claude-code evidence-fix-2026-11-20": 23564}
        self.assertIn("a", letters(f))

    def test_b_no_review_record_or_only_one(self):
        for n in (0, 1):
            f = clean()
            f["prs"][0]["review_records"] = n
            self.assertEqual(letters(f), {"b"}, n)

    def test_b_ignores_prs_that_do_not_touch_data(self):
        f = clean()
        f["prs"][0]["data_files"] = 0
        f["prs"][0]["review_records"] = 0
        self.assertEqual(letters(f), set())

    def test_c_merged_before_validate_finished_failed_or_never_ran(self):
        f = clean(); f["prs"][0]["validate"]["completed_at"] = "2026-11-21T01:03:00Z"
        self.assertEqual(letters(f), {"c"})
        f = clean(); f["prs"][0]["validate"]["conclusion"] = "failure"
        self.assertEqual(letters(f), {"c"})
        f = clean(); f["prs"][0]["validate"] = {"status": "in_progress", "conclusion": None, "started_at": "2026-11-21T00:50:00Z", "completed_at": None}
        self.assertEqual(letters(f), {"c"})
        f = clean(); f["prs"][0]["validate"] = None
        self.assertEqual(letters(f), {"c"})

    def test_c_ignores_a_merge_train_member_but_not_the_train_pr(self):
        f = clean(); f["prs"][0]["validate"] = None; f["prs"][0]["train_member"] = True
        self.assertEqual(letters(f), set())

    def test_d_main_validate_not_success(self):
        f = clean(); f["main_validate"]["conclusion"] = "failure"
        self.assertEqual(letters(f), {"d"})

    def test_e_three_data_prs_and_no_unknown_count_fell(self):
        f = clean()
        for n in (11, 12):
            f["commits"].append(dict(f["commits"][0], sha=f"{n:010d}", pr=n, evidence_added={}, links_added=0))
            f["prs"].append(dict(f["prs"][0], number=n, merge_sha=f"{n:010d}"))
        f["unknown"]["after"] = dict(f["unknown"]["before"])
        self.assertEqual(letters(f), {"e"})
        f["unknown"]["after"]["proc"] -= 1  # one count fell: quiet
        self.assertEqual(letters(f), set())

    def test_f_label_names_no_tasks_folder(self):
        f = clean()
        f["commits"][0]["evidence_added"] = {"some-harness mystery-wave": 3}
        self.assertEqual(letters(f), {"f"})

    def test_f_grandfathered_label_is_quiet_but_a_new_one_fires(self):
        f = clean()
        f["commits"][0]["evidence_added"] = {"old-wave-label": 3}
        f["label_baseline"] = ["old-wave-label"]
        self.assertEqual(letters(f), set())
        f["commits"][0]["evidence_added"] = {"old-wave-label-2": 3}
        self.assertEqual(letters(f), {"f"})

    def test_f_label_rule(self):
        folders = ["size-band-evidence-2026-11-03", "bandb"]
        self.assertTrue(nw.label_names_a_folder("claude-code size-band-evidence-2026-11-03", folders))
        self.assertFalse(nw.label_names_a_folder("spaghetti-burndown-batch2-2026-11-21", folders))
        self.assertFalse(nw.label_names_a_folder("bandb", folders))  # too short to name anything

    def test_g_rows_removed_without_a_removals_entry(self):
        f = clean()
        f["commits"][0]["removed"] = {"evidence": {"n": 34094, "e.g.": ["EVD-1", "EVD-2"]}}
        self.assertEqual(letters(f), {"g"})


BACKFILL = Path(__file__).resolve().parents[1] / "tasks" / "nightly-watch-2026-11-22" / "backfill"


class KnownAnswer(unittest.TestCase):
    """The committed 11:17 UTC night windows on main: the 2026-11-21/22 incident fires, 2026-11-16..18 stays quiet."""

    def letters(self, name):
        return letters(json.loads((BACKFILL / f"night-{name}.json").read_text()))

    def test_incident_nights_fire_a_b_c_e(self):
        self.assertTrue({"b", "c", "e"} <= self.letters("2026-11-21"))
        self.assertTrue({"a", "b", "c", "e"} <= self.letters("2026-11-22"))
        self.assertTrue({"a", "b", "c", "e"} <= self.letters("2026-11-22-partial"))

    def test_quiet_nights_raise_only_b(self):  # b: the review-record convention began 2026-11-22
        for n in ("2026-11-17", "2026-11-18", "2026-11-19"):
            self.assertEqual(self.letters(n), {"b"}, n)


class CouldNotInspect(unittest.TestCase):
    def test_errors_fail_without_findings(self):
        f = clean(); f["errors"] = ["GitHub: gh api: HTTP 502"]
        text, code = nw.report(f)
        self.assertEqual(code, 2)
        self.assertIn("could not inspect", text)
        self.assertNotIn("PASS", text)

    def test_findings_beat_errors_in_exit_code(self):
        f = clean(); f["errors"] = ["x"]; f["main_validate"]["conclusion"] = "failure"
        self.assertEqual(nw.report(f)[1], 1)


class RealGit(unittest.TestCase):
    """collect() on a throwaway repo: rows are counted per commit from git, and a gh failure surfaces as an error."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        env = {**os.environ, "GIT_COMMITTER_DATE": "2026-11-01T00:00:00Z"}
        run = lambda *a: subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, env=env)
        run("init", "-q", "-b", "main"); run("config", "user.email", "t@example.com"); run("config", "user.name", "t")
        (d / "data").mkdir(); (d / "tasks" / "evidence-fix-2026-11-20").mkdir(parents=True)
        (d / "tasks" / "evidence-fix-2026-11-20" / "README.md").write_text("x\n")
        hdr = "evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes,address_role\n"
        (d / "data" / "evidence_organizations_OH.csv").write_text(hdr)
        run("add", "."); run("commit", "-q", "-m", "base")
        rows = "".join(f"EVD-{i},organizations,ORG-1,existence,d,own_site,u,2026-11-21,supports_A,claude evidence-fix-2026-11-20,,\n" for i in range(3))
        (d / "data" / "evidence_organizations_OH.csv").write_text(hdr + rows)
        env.pop("GIT_COMMITTER_DATE")  # the second commit is dated now, inside the window
        run("add", "."); run("commit", "-q", "-m", "add three")
        self.d = d
        self.patches = [mock.patch.object(nw, "ROOT", d), mock.patch.object(check_row_loss, "ROOT", d)]
        for p in self.patches:
            p.start(); self.addCleanup(p.stop)

    def window(self):
        now = datetime.now(timezone.utc)
        return datetime(2026, 11, 10, tzinfo=timezone.utc), now

    def test_collect_counts_rows_and_a_gh_failure_fails_the_run(self):
        errors = []
        with mock.patch.object(nw, "gh", side_effect=RuntimeError("gh api: HTTP 502")):
            facts = nw.collect("main", *self.window(), "o/r", errors)
        # base resolves to the root commit, so the one later commit is the window
        self.assertEqual(len(facts["commits"]), 1)
        self.assertEqual(facts["commits"][0]["evidence_added"], {"claude evidence-fix-2026-11-20": 3})
        self.assertEqual(facts["task_folders"], ["evidence-fix-2026-11-20"])
        text, code = nw.report(facts)
        self.assertEqual(code, 2, text)
        self.assertIn("HTTP 502", text)

    def test_unresolvable_window_start_is_an_error_not_zero_commits(self):
        errors = []
        facts = nw.collect("main", datetime(2000, 1, 1, tzinfo=timezone.utc), self.window()[1], "o/r", errors)
        self.assertTrue(errors)
        self.assertEqual(nw.report(facts)[1], 2)

    def test_g_real_row_removal_needs_a_removals_entry(self):
        d, git = self.d, lambda *a: subprocess.run(["git", "-C", str(self.d), *a], check=True, capture_output=True, text=True).stdout.strip()
        ev = d / "data" / "evidence_organizations_OH.csv"
        lines = ev.read_text().splitlines(keepends=True)
        ev.write_text("".join(lines[:-1]))  # drop EVD-2, nothing declared
        git("add", "."); git("commit", "-q", "-m", "drop a row")
        with mock.patch.object(nw, "gh", side_effect=RuntimeError("x")):
            facts = nw.collect("main", *self.window(), "o/r", [])
        self.assertEqual(facts["commits"][-1]["removed"]["evidence"]["e.g."], ["EVD-2"])
        self.assertIn("g", {x[1] for x in nw.analyze(facts)[0]})
        (d / "tasks" / "evidence-fix-2026-11-20" / "REMOVALS.csv").write_text("table,key,reason\nevidence,EVD-1,declared\n")
        ev.write_text("".join(lines[:-2]))  # drop EVD-1, declared in this same commit
        git("add", "."); git("commit", "-q", "-m", "drop a declared row")
        with mock.patch.object(nw, "gh", side_effect=RuntimeError("x")):
            facts = nw.collect("main", *self.window(), "o/r", [])
        self.assertEqual(facts["commits"][-1]["removed"], {})

    def test_merge_train_member_and_gh_facts(self):
        """A PR merged into a train branch is judged from its own merge commit; its rows ride on the train's commit."""
        d, git = self.d, lambda *a: subprocess.run(["git", "-C", str(self.d), *a], check=True, capture_output=True, text=True).stdout.strip()
        git("checkout", "-q", "-b", "train", "HEAD~1")
        f = d / "data" / "people.csv"; f.write_text("person_id\nP1\n")
        git("add", "."); git("commit", "-q", "-m", "member")
        member = git("rev-parse", "HEAD")
        git("checkout", "-q", "main"); git("merge", "-q", "--no-ff", "-m", "train", "train")
        train = git("rev-parse", "HEAD")
        prs = [{"number": 5, "mergedAt": "2026-11-21T01:00:00Z", "mergeCommit": {"oid": member}, "headRefOid": "h" * 40,
                "comments": [{"body": "**Review record**\nok", "createdAt": "2026-11-21T00:30:00Z"},
                             {"body": "**Review record**\nlate", "createdAt": "2026-11-21T02:00:00Z"}]},
               {"number": 6, "mergedAt": "2026-11-21T01:05:00Z", "mergeCommit": {"oid": train}, "headRefOid": "i" * 40, "comments": []}]
        run = {"status": "completed", "conclusion": "success", "started_at": "2026-11-21T00:10:00Z", "completed_at": "2026-11-21T00:15:00Z"}
        def fake_gh(*a):
            if a[:2] == ("pr", "list"):
                return json.dumps(prs)
            if "check-runs" in a[2]:
                return json.dumps(run) + "\n"
            return json.dumps({"conclusion": "success", "created_at": "2026-11-21T01:06:00Z", "head_sha": "x"})
        errors = []
        with mock.patch.object(nw, "gh", side_effect=fake_gh):
            facts = nw.collect("main", datetime(2026, 11, 10, tzinfo=timezone.utc), datetime.now(timezone.utc), "o/r", errors)
        by = {p["number"]: p for p in facts["prs"]}
        self.assertEqual(errors, [])
        self.assertTrue(by[5]["train_member"]); self.assertFalse(by[6]["train_member"])
        self.assertEqual((by[5]["data_files"], by[5]["review_records"]), (1, 1))  # the late record does not count
        self.assertEqual(by[5]["validate"]["conclusion"], "success")
        self.assertEqual({x[1] for x in nw.analyze(facts)[0]}, {"b"})  # one record only; the setUp label names its tasks/ folder


if __name__ == "__main__":
    unittest.main()
