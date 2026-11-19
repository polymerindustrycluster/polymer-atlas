#!/usr/bin/env python3
"""Run every scripts/test_*.py test in parallel shards (the CI unit-test step).

`unittest discover` ran the suite serially; it took about 4 of the validate job's 4.5 minutes on 2026-11-19, mostly
test_validate.py (86 tests, each copying data/ and running the full validator). Here every test runs once, in one of
N worker processes, with the import path of `python -m unittest discover -s scripts` (the caller's working directory,
then the start directory).

The parent lists the tests without calling any module's `load_tests` hook. A module that has one is loaded once,
whole, in one worker, so the hook and the suite it returns run exactly as under serial discovery. Any other module is
run whole in one worker too, so its setUpModule and setUpClass run once (test_build_site builds
build/polymer-atlas.db), except a class that sets `parallel_safe = True`, saying every test uses only its own
temporary files: its tests are dealt out one by one across shards.

Each worker writes a result file after its run; test output is never parsed. The parent fails a shard with no result
file (an early exit), with failures or errors, or where an assigned test did not run exactly once (a test whose
setUpClass or setUpModule raised SkipTest counts as run). A module that raises SkipTest on import counts as one skip,
as in serial discovery, and a run with no test and no skip exits 5, as unittest does. Test modules are imported twice:
once by the parent to list them, once by the worker that runs them.

Usage: python3 scripts/run_tests.py [--jobs N] [--start DIR]     (default: the CPU count; scripts/)
"""
import argparse
import functools
import importlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATTERN = "test_*.py"


def import_path(start):
    sys.path[0] = os.getcwd()  # as `python -m unittest`: the caller's directory, not this script's
    sys.path.insert(0, str(start))


class Lister(unittest.TestLoader):
    """Discovery that never calls a load_tests hook: a hooked module is only noted, and later loaded by one worker."""

    def __init__(self):
        super().__init__()
        self.hooked = []

    def loadTestsFromModule(self, module, *, pattern=None):
        if callable(getattr(module, "load_tests", None)):
            self.hooked.append(module.__name__)
            return self.suiteClass()
        return super().loadTestsFromModule(module, pattern=pattern)


class Result(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.started, self.fixture_skips = [], set()

    def startTest(self, test):
        self.started.append(test.id())
        super().startTest(test)

    def addSkip(self, test, reason):
        if not isinstance(test, unittest.TestCase):  # "setUpClass (mod.Cls)" or "setUpModule (mod)" raised SkipTest
            self.fixture_skips.add(test.id())
        super().addSkip(test, reason)


def worker(start, unit_file, out_file):
    import_path(start)
    unit = json.loads(Path(unit_file).read_text())
    loader = unittest.TestLoader()
    loader._top_level_dir = str(start)  # as during discovery: a package hook's own loader.discover() keeps this root

    def case(module, qualname, method):  # as loadTestsFromTestCase builds it (loadTestsFromName would call a staticmethod)
        return functools.reduce(getattr, qualname.split("."), importlib.import_module(module))(method)
    suite = unittest.TestSuite(
        [loader.loadTestsFromModule(importlib.import_module(m), pattern=PATTERN) for m in unit["modules"]]
        + [case(*c[:3]) for c in unit["cases"]])
    r = unittest.TextTestRunner(resultclass=Result, verbosity=2).run(suite)
    ran = Counter(r.started)

    def skipped_by_fixture(tid):
        cls = tid.rsplit(".", 1)[0]
        return f"setUpClass ({cls})" in r.fixture_skips or f"setUpModule ({cls.rsplit('.', 1)[0]})" in r.fixture_skips
    wrong = [c[3] for c in unit["cases"] if ran[c[3]] != 1 and not (ran[c[3]] == 0 and skipped_by_fixture(c[3]))]
    Path(out_file).write_text(json.dumps({"wrong": wrong, "ran": r.testsRun, "skipped": len(r.skipped),
                                          "errors": len(loader.errors), "ok": r.wasSuccessful()}))


def shards_of(found, hooked, jobs):
    whole, safe = {}, []
    for t in found:
        c = [type(t).__module__, type(t).__qualname__, t._testMethodName, t.id()]
        if getattr(type(t), "parallel_safe", False):
            safe.append(c)
        else:
            whole.setdefault(type(t).__module__, []).append(c)
    shards = [{"modules": [], "cases": [], "n": 0} for _ in range(jobs)]
    for m in hooked:  # its test count is unknown until its hook runs; weigh it as one
        s = min(shards, key=lambda s: s["n"])
        s["modules"].append(m)
        s["n"] += 1
    for unit in sorted(whole.values(), key=len, reverse=True):  # largest module first, each to the lightest shard
        s = min(shards, key=lambda s: s["n"])
        s["cases"] += unit
        s["n"] += len(unit)
    for i, c in enumerate(safe):  # the slow validator tests: an equal share per shard
        shards[i % jobs]["cases"].append(c)
    return [s for s in shards if s["modules"] or s["cases"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--start", default=str(HERE))
    ap.add_argument("--worker", nargs=2, metavar=("UNIT_JSON", "OUT_JSON"), help=argparse.SUPPRESS)
    a = ap.parse_args()
    start = Path(a.start).resolve()
    if a.worker:
        return worker(start, *a.worker)
    import_path(start)
    lister = Lister()
    found = list(flat(lister.discover(str(start), pattern=PATTERN, top_level_dir=str(start))))
    if lister.errors:
        print("\n".join(map(str, lister.errors)))
        print(f"run_tests: {len(lister.errors)} test modules failed to import")
        return 1
    module_skips = [t for t in found if type(t).__module__ == "unittest.loader"]  # a module raised SkipTest on import
    found = [t for t in found if t not in module_skips]
    ids = [t.id() for t in found]
    if len(ids) != len(set(ids)):
        print("run_tests: duplicate test ids; a shard cannot address them; run unittest discover")
        return 1
    shards = shards_of(found, lister.hooked, max(1, a.jobs))
    assert sorted(c[3] for s in shards for c in s["cases"]) == sorted(ids), "every listed test must be in exactly one shard"

    with tempfile.TemporaryDirectory() as tmp:
        def run(n):
            unit_file, out_file = Path(tmp) / f"unit{n}.json", Path(tmp) / f"out{n}.json"
            unit_file.write_text(json.dumps(shards[n]))
            t0 = time.monotonic()
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--start", str(start), "--worker",
                                str(unit_file), str(out_file)], capture_output=True)
            res = json.loads(out_file.read_text()) if out_file.exists() else None
            return p, res, time.monotonic() - t0

        with ThreadPoolExecutor(max(1, len(shards))) as ex:
            results = list(ex.map(run, range(len(shards))))
    failed, ran, skipped = 0, 0, len(module_skips)
    for n, (p, res, secs) in enumerate(results):
        why = ("no result file (the worker exited early)" if res is None
               else f"{len(res['wrong'])} assigned tests did not run exactly once" if res["wrong"]
               else "tests failed to load" if res["errors"]
               else "tests failed" if not res["ok"] or p.returncode
               else "")
        if why:
            failed += 1
            out = (p.stdout + p.stderr).decode("utf-8", "replace")
            print(f"--- shard {n + 1} of {len(shards)} FAILED: {why} (exit {p.returncode}) ---\n{out}")
        else:
            ran += res["ran"]
            skipped += res["skipped"]
            print(f"shard {n + 1}: OK, {res['ran']} tests, {res['skipped']} skipped, {secs:.0f} s")
    print(f"run_tests: {len(ids)} tests listed + {len(lister.hooked)} load_tests modules in {len(shards)} shards, "
          f"{failed} shards failed")
    if failed:
        return 1
    if ran == 0 and skipped == 0:  # as unittest since 3.12
        print("NO TESTS RAN")
        return 5
    return 0


def flat(suite):
    for t in suite:
        yield from (flat(t) if isinstance(t, unittest.TestSuite) else [t])


if __name__ == "__main__":
    sys.exit(main())
