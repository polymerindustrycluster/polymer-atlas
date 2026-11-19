"""run_tests.py agrees with serial `unittest discover` on the fixtures Codex used to refute its first version (PR #417
r1): a load_tests-configured instance, test output that looks like a summary, an early os._exit, a setUpClass skip,
a module fixture, the caller's working directory. Each case is a throwaway test tree run with --jobs 2."""
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "run_tests.py"

CASES = {  # name: (expected exit code, {module: source})
    "plain_failure": (1, {"test_a": "class A(unittest.TestCase):\n    def test_x(self): self.fail('no')"}),
    "load_tests_configured": (1, {"test_a": """
        class C(unittest.TestCase):
            def test_a(self): self.assertFalse(getattr(self, "flag", False))
        def load_tests(loader, suite, pattern):
            case = C("test_a"); case.flag = True
            return unittest.TestSuite([case])"""}),
    "fake_summary": (0, {"test_a": """
        class C(unittest.TestCase):
            def test_a(self): unittest.TextTestRunner().run(unittest.FunctionTestCase(lambda: None))
            def test_b(self): pass"""}),
    "early_exit": (1, {"test_a": """
        import os
        class C(unittest.TestCase):
            def test_a(self):
                unittest.TextTestRunner().run(unittest.FunctionTestCase(lambda: None)); os._exit(0)"""}),
    "class_skip": (0, {"test_a": """
        class C(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise unittest.SkipTest("resource unavailable")
            def test_a(self): self.fail("must not run")"""}),
    "module_fixture": (0, {"test_a": """
        import os
        def setUpModule(): open(os.path.join(os.path.dirname(__file__), "once.lock"), "x").close()
        class C(unittest.TestCase):
            def test_a(self): pass
        class D(unittest.TestCase):
            def test_b(self): pass"""}),
    "callers_cwd": (0, {"test_a": """
        import os
        class C(unittest.TestCase):
            def test_a(self): self.assertTrue(os.path.isfile("marker.txt"))"""}),
    "safe_class_split": (0, {"test_a": """
        class C(unittest.TestCase):
            parallel_safe = True
            def test_a(self): pass
            def test_b(self): pass
            def test_c(self): pass""", "test_b": "class D(unittest.TestCase):\n    def test_d(self): pass"}),
}


class RunTestsTest(unittest.TestCase):
    def test_matches_serial_discover(self):
        for name, (want, modules) in CASES.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                start, cwd = Path(tmp) / "tests", Path(tmp) / "cwd"
                start.mkdir(); cwd.mkdir(); (cwd / "marker.txt").touch()
                for mod, src in modules.items():
                    (start / f"{mod}.py").write_text("import unittest\n" + textwrap.dedent(src).strip() + "\n")
                p = subprocess.run([sys.executable, str(RUNNER), "--jobs", "2", "--start", str(start)],
                                   cwd=cwd, capture_output=True, text=True)
                self.assertEqual(p.returncode, want, p.stdout + p.stderr)
                if name == "safe_class_split":
                    self.assertIn("2 shards, 0 shards failed", p.stdout)


if __name__ == "__main__":
    unittest.main()
