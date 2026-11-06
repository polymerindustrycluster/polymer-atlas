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


if __name__ == "__main__":
    unittest.main()
