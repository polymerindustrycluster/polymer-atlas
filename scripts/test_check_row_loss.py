"""Tests for the row-loss guard (scripts/check_row_loss.py), including the defect it exists to catch."""
import subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_row_loss as g


class Keys(unittest.TestCase):
    def test_tables(self):
        self.assertEqual(g.table_of("data/evidence_sites_OH.csv"), "evidence")
        self.assertEqual(g.table_of("data/organizations_INTL.csv"), "org_ids")
        self.assertEqual(g.table_of("data/ecosystem.csv"), "org_ids")  # orgs may move between the two tables
        self.assertEqual(g.table_of("data/sites_US.csv"), "sites")
        self.assertEqual(g.table_of("data/registry_links.csv"), "registry_links")

    def test_registry_key_is_composite(self):
        h = ["org_id", "registry", "registry_id", "match_basis", "as_of", "site_id"]
        k = g.row_key("registry_links", h, ["ORG-1", "FRS", "110", "m", "2026-11-01", "SITE-9"])
        self.assertEqual(k, "ORG-1|FRS|110|SITE-9")

    def test_removed_and_declared(self):
        base = {"registry_links": {"a", "b", "c"}, "sites": {"S1"}}
        head = {"registry_links": {"a"}, "sites": {"S1"}}
        self.assertEqual(dict(g.removed_keys(base, head)), {"registry_links": ["b", "c"]})
        self.assertEqual(dict(g.removed_keys(base, head, {("registry_links", "b"), ("registry_links", "c")})), {})


class EndToEnd(unittest.TestCase):
    """Inject the 805528a defect into a throwaway repo and watch the guard fail, then pass once declared."""

    def run_guard(self, root, *args):
        old = g.ROOT
        g.ROOT = root
        try:
            sys.argv = ["check_row_loss.py", *args]
            return g.main()
        finally:
            g.ROOT = old

    def test_truncated_file_fails_until_declared(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True)
            git("init", "-q")
            git("config", "user.email", "t@t")
            git("config", "user.name", "t")
            (root / "data").mkdir()
            (root / "tasks").mkdir()
            links = root / "data" / "registry_links.csv"
            links.write_text("org_id,registry,registry_id,match_basis,as_of,site_id\n"
                             "ORG-1,TRI_TRIFID,T1,m,2026-10-30,\nORG-2,FRS,F2,m,2026-11-01,SITE-2\n")
            git("add", ".")
            git("commit", "-qm", "base")
            links.write_text("org_id,registry,registry_id,match_basis,as_of,site_id\nORG-2,FRS,F2,m,2026-11-01,SITE-2\n")
            self.assertEqual(self.run_guard(root, "--base", "HEAD"), 1)
            (root / "tasks" / "REMOVALS.csv").write_text("table,key,reason\nregistry_links,ORG-1|TRI_TRIFID|T1|,re-point\n")
            self.assertEqual(self.run_guard(root, "--base", "HEAD"), 0)


class ReviewFindings(unittest.TestCase):
    """Regressions for the PR #130 Codex and Grok clerk findings (rounds 1 and 2)."""

    def repo(self, d):
        git = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True)
        git("init", "-q"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
        (Path(d) / "data").mkdir(); (Path(d) / "tasks").mkdir()
        return git

    def guard(self, root, *args):
        return EndToEnd.run_guard(self, Path(root), *args)

    def test_old_manifest_does_not_authorize_a_later_loss(self):
        with tempfile.TemporaryDirectory() as d:
            git = self.repo(d); s = Path(d) / "data" / "sites_OH.csv"
            s.write_text("site_id,name\nSITE-1,a\nSITE-2,b\n"); git("add", "."); git("commit", "-qm", "1")
            s.write_text("site_id,name\nSITE-2,b\n")
            (Path(d) / "tasks" / "REMOVALS.csv").write_text("table,key,reason\nsites,SITE-1,test\n")
            git("add", "."); git("commit", "-qm", "declared removal")
            self.assertEqual(self.guard(d, "--base", "HEAD~1"), 0)
            s.write_text("site_id,name\nSITE-1,a\nSITE-2,b\n"); git("add", "."); git("commit", "-qm", "restored")
            s.write_text("site_id,name\nSITE-2,b\n")  # accidental second loss, manifest untouched
            self.assertEqual(self.guard(d, "--base", "HEAD"), 1)

    def test_redeclared_key_in_a_new_manifest_authorizes(self):
        with tempfile.TemporaryDirectory() as d:
            git = self.repo(d); s = Path(d) / "data" / "sites_OH.csv"; m = Path(d) / "tasks" / "REMOVALS.csv"
            s.write_text("site_id\nSITE-1\nSITE-2\n"); git("add", "."); git("commit", "-qm", "1")
            s.write_text("site_id\nSITE-2\n"); m.write_text("table,key,reason\nsites,SITE-1,first\n")
            git("add", "."); git("commit", "-qm", "declared")
            s.write_text("site_id\nSITE-1\nSITE-2\n"); git("add", "."); git("commit", "-qm", "restored")
            s.write_text("site_id\nSITE-2\n"); (Path(d) / "tasks" / "round2").mkdir()
            (Path(d) / "tasks" / "round2" / "REMOVALS.csv").write_text("table,key,reason\nsites,SITE-1,second\n")
            self.assertEqual(self.guard(d, "--base", "HEAD"), 0)

    def test_people_identifier_as_of_refresh_is_not_a_loss(self):
        with tempfile.TemporaryDirectory() as d:
            git = self.repo(d); p = Path(d) / "data" / "people_identifiers.csv"
            p.write_text("person_id,identifier_type,identifier_id,match_basis,as_of\nPERSON-1,ORCID,0000,x,2026-11-01\n")
            git("add", "."); git("commit", "-qm", "1")
            p.write_text("person_id,identifier_type,identifier_id,match_basis,as_of\nPERSON-1,ORCID,0000,x,2026-11-06\n")
            self.assertEqual(self.guard(d, "--base", "HEAD"), 0)

    def test_one_of_two_identical_rows_removed_is_seen(self):
        with tempfile.TemporaryDirectory() as d:
            git = self.repo(d); p = Path(d) / "data" / "inclusion_log.csv"
            p.write_text("date,record\n2026-10-28,X\n2026-10-28,X\n"); git("add", "."); git("commit", "-qm", "1")
            p.write_text("date,record\n2026-10-28,X\n")
            self.assertEqual(self.guard(d, "--base", "HEAD"), 1)

    def test_push_rollback_is_caught_with_literal(self):
        with tempfile.TemporaryDirectory() as d:
            git = self.repo(d); s = Path(d) / "data" / "sites_OH.csv"
            s.write_text("site_id\nSITE-1\n"); git("add", "."); git("commit", "-qm", "1")
            s.write_text("site_id\nSITE-1\nSITE-2\n"); git("commit", "-qam", "2")
            before = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            git("reset", "-q", "--hard", "HEAD~1")  # main moved backwards: SITE-2 is gone
            self.assertEqual(self.guard(d, "--base", before, "--literal"), 1)
            self.assertEqual(self.guard(d, "--base", before), 0)  # merge-base mode alone cannot see it

    def test_lagging_branch_is_not_blamed_for_rows_main_added(self):
        with tempfile.TemporaryDirectory() as d:
            git = self.repo(d); s = Path(d) / "data" / "sites_OH.csv"
            s.write_text("site_id\nSITE-1\n"); git("add", "."); git("commit", "-qm", "1"); git("branch", "-M", "main")
            git("checkout", "-qb", "lane")
            git("checkout", "-q", "main"); s.write_text("site_id\nSITE-1\nSITE-2\n"); git("commit", "-qam", "main adds")
            git("checkout", "-q", "lane")
            self.assertEqual(self.guard(d, "--base", "main"), 0)


if __name__ == "__main__":
    unittest.main()
