"""run_tests.py exits as serial `python -m unittest discover -s scripts` does, on the fixtures Codex used to refute it
(PR #417 r1 and r2): load_tests hooks that configure instances, wrap the suite or change between discoveries; output
that looks like a summary, or is not UTF-8; a setUpClass skip; a module fixture; the caller's working directory and
import path. Each case runs in a fresh throwaway tree per arm. The one intended difference: a test that calls
os._exit(0) ends serial discovery with exit 0, and fails the runner (no result file)."""
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "run_tests.py"
HEAD = "import unittest, sys, os\nfrom unittest.mock import patch\nfrom pathlib import Path\n"

CASES = {
    "plain_failure": {"test_a": "class A(unittest.TestCase):\n    def test_x(self): self.fail('no')"},
    "load_tests_configured": {"test_a": """
        class C(unittest.TestCase):
            def test_a(self): self.assertFalse(getattr(self, "flag", False))
        def load_tests(loader, suite, pattern):
            case = C("test_a"); case.flag = True
            return unittest.TestSuite([case])"""},
    "fake_summary": {"test_a": """
        class C(unittest.TestCase):
            def test_a(self): unittest.TextTestRunner().run(unittest.FunctionTestCase(lambda: None))
            def test_b(self): pass"""},
    "class_skip": {"test_a": """
        class C(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise unittest.SkipTest("resource unavailable")
            def test_a(self): self.fail("must not run")"""},
    "module_fixture": {"test_a": """
        def setUpModule(): open(os.path.join(os.path.dirname(__file__), "once.lock"), "x").close()
        class C(unittest.TestCase):
            def test_a(self): pass
        class D(unittest.TestCase):
            def test_b(self): pass"""},
    "callers_cwd": {"test_a": """
        class C(unittest.TestCase):
            def test_a(self): self.assertTrue(os.path.isfile("marker.txt"))"""},
    "safe_class_split": {"test_a": """
        class C(unittest.TestCase):
            parallel_safe = True
            def test_a(self): pass
            def test_b(self): pass
            def test_c(self): pass""", "test_b": "class D(unittest.TestCase):\n    def test_d(self): pass"},
    "suite_hook": {"test_a": """
        class Wrapper(unittest.TestSuite):
            def run(self, result, debug=False):
                with patch.dict(os.environ, {"EXPECTED_MODE": "strict"}):
                    return super().run(result, debug)
        class C(unittest.TestCase):
            def test_policy(self): self.assertNotEqual(os.getenv("EXPECTED_MODE"), "strict")
        def load_tests(loader, tests, pattern):
            return Wrapper([tests])"""},
    "import_path": {"__init__": "", "project_helper": "expected = 42", "test_a": """
        from scripts.project_helper import expected
        class C(unittest.TestCase):
            def test_x(self): self.assertEqual(expected, 42)"""},
    "rediscovered_ids": {"test_a": """
        class C(unittest.TestCase):
            def test_a(self): pass
            def test_b(self): self.fail("must run")
        def load_tests(loader, tests, pattern):
            flag = Path("catalog.cache")
            second = "test_a" if flag.exists() else "test_b"
            flag.touch()
            return unittest.TestSuite([C("test_a"), C(second)])"""},
    "hook_called_once": {"test_a": """
        class C(unittest.TestCase):
            def test_a(self): pass
        def load_tests(loader, tests, pattern):
            mark = Path("hook.called")
            if mark.exists(): raise RuntimeError("load_tests ran twice")
            mark.touch()
            return tests"""},
    "binary_log": {"test_a": """
        class C(unittest.TestCase):
            def test_output(self): sys.stdout.buffer.write(bytes([255, 10]))"""},
    "stable_ids_changed_state": {"test_a": """
        class C(unittest.TestCase):
            def test_payload(self): self.assertNotEqual(self.mode, "cold")
        def load_tests(loader, tests, pattern):
            mark = Path("fixtures.cache")
            case = C("test_payload")
            case.mode = "warm" if mark.exists() else "cold"
            mark.touch()
            return unittest.TestSuite([case])"""},
}


def run(modules, parallel):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir()
        (root / "marker.txt").touch()
        for mod, src in modules.items():
            (root / "scripts" / f"{mod}.py").write_text(HEAD + textwrap.dedent(src).strip() + "\n")
        cmd = ([str(RUNNER), "--jobs", "2", "--start", "scripts"] if parallel
               else ["-m", "unittest", "discover", "-s", "scripts", "-p", "test_*.py"])
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        p = subprocess.run([sys.executable, *cmd], cwd=root, env=env, capture_output=True)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")


class RunTestsTest(unittest.TestCase):
    def test_exits_as_serial_discover(self):
        for name, modules in CASES.items():
            with self.subTest(name):
                serial, _ = run(modules, False)
                code, out = run(modules, True)
                self.assertEqual(code, serial, out)
                if name == "safe_class_split":
                    self.assertIn("in 2 shards, 0 shards failed", out)

    def test_early_exit_fails(self):
        code, out = run({"test_a": """
            class C(unittest.TestCase):
                def test_a(self): os._exit(0)"""}, True)
        self.assertEqual(code, 1, out)
        self.assertIn("no result file", out)


if __name__ == "__main__":
    unittest.main()
