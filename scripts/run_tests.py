#!/usr/bin/env python3
"""Run every scripts/test_*.py test in parallel shards (the CI unit-test step).

`unittest discover` ran the suite serially; it took about 4 of the validate job's 4.5 minutes on 2026-11-19, mostly
test_validate.py (86 tests, each copying data/ and running the full validator). Here every discovered test runs exactly
once, in one of N worker processes. Each worker repeats the discovery and runs its share of those same test objects
(so a `load_tests` hook keeps its configuration), from the caller's working directory, and writes a result file the
parent checks: every assigned test started (or its setUpClass / setUpModule raised SkipTest), and none failed.
Test output is never parsed.

A test module stays whole in one shard, so its setUpModule and setUpClass run once (test_build_site builds
build/polymer-atlas.db). The exception is a class that sets `parallel_safe = True`, saying every test uses only its own
temporary files: its tests are dealt out one by one across shards.

Usage: python3 scripts/run_tests.py [--jobs N] [--start DIR]     (default: the CPU count; scripts/)
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.util import strclass

HERE = Path(__file__).resolve().parent


def discover(start):
    loader = unittest.TestLoader()
    suite = loader.discover(str(start), pattern="test_*.py", top_level_dir=str(start))

    def flat(s):
        for t in s:
            yield from (flat(t) if isinstance(t, unittest.TestSuite) else [t])
    return list(flat(suite)), loader.errors


class Result(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.started, self.fixture_skips = set(), set()

    def startTest(self, test):
        self.started.add(test.id())
        super().startTest(test)

    def addSkip(self, test, reason):
        if not isinstance(test, unittest.TestCase):  # "setUpClass (mod.Cls)" or "setUpModule (mod)" raised SkipTest
            self.fixture_skips.add(test.id())
        super().addSkip(test, reason)


def worker(start, ids_file, out_file):
    want = set(json.loads(Path(ids_file).read_text()))
    found, errors = discover(start)
    pick = [t for t in found if t.id() in want]
    r = unittest.TextTestRunner(resultclass=Result, verbosity=2).run(unittest.TestSuite(pick))
    skipped = r.fixture_skips
    unaccounted = [t.id() for t in pick if t.id() not in r.started
                   and f"setUpClass ({strclass(type(t))})" not in skipped and f"setUpModule ({type(t).__module__})" not in skipped]
    Path(out_file).write_text(json.dumps({
        "assigned": len(want), "picked": len(pick), "unaccounted": unaccounted, "import_errors": len(errors),
        "skipped": len(r.skipped), "ok": r.wasSuccessful()}))


def shards_of(found, jobs):
    whole, safe = {}, []
    for t in found:
        if getattr(type(t), "parallel_safe", False):
            safe.append(t.id())
        else:
            whole.setdefault(type(t).__module__, []).append(t.id())
    shards = [[] for _ in range(jobs)]
    for unit in sorted(whole.values(), key=len, reverse=True):  # largest module first, each to the lightest shard
        min(shards, key=len).extend(unit)
    for i, tid in enumerate(safe):  # the slow validator tests: an equal share per shard
        shards[i % jobs].append(tid)
    return [s for s in shards if s]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--start", default=str(HERE))
    ap.add_argument("--worker", nargs=2, metavar=("IDS_JSON", "OUT_JSON"), help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.worker:
        return worker(a.start, *a.worker)
    found, errors = discover(a.start)
    if errors:
        print("\n".join(map(str, errors)))
        print(f"run_tests: {len(errors)} test modules failed to import")
        return 1
    ids = [t.id() for t in found]
    if len(ids) != len(set(ids)):
        print("run_tests: duplicate test ids (a load_tests hook?); a shard cannot address them; run unittest discover")
        return 1
    shards = shards_of(found, max(1, a.jobs))
    assert sorted(i for s in shards for i in s) == sorted(ids), "every discovered test must be in exactly one shard"

    with tempfile.TemporaryDirectory() as tmp:
        def run(n):
            ids_file, out_file = Path(tmp) / f"ids{n}.json", Path(tmp) / f"out{n}.json"
            ids_file.write_text(json.dumps(shards[n]))
            t0 = time.monotonic()
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--start", a.start, "--worker",
                                str(ids_file), str(out_file)], capture_output=True, text=True)
            res = json.loads(out_file.read_text()) if out_file.exists() else None
            return p, res, time.monotonic() - t0

        with ThreadPoolExecutor(len(shards)) as ex:
            results = list(ex.map(run, range(len(shards))))
    failed = 0
    for n, (p, res, secs) in enumerate(results):
        why = ("no result file (the worker exited early)" if res is None
               else f"{len(res['unaccounted'])} assigned tests never ran" if res["unaccounted"]
               else f"found {res['picked']} of {res['assigned']} assigned tests" if res["picked"] != res["assigned"]
               else "import errors" if res["import_errors"]
               else "tests failed" if not res["ok"] or p.returncode
               else "")
        if why:
            failed += 1
            print(f"--- shard {n + 1} of {len(shards)} FAILED: {why} (exit {p.returncode}) ---\n{p.stdout}{p.stderr}")
        else:
            print(f"shard {n + 1}: OK, {res['assigned']} tests, {res['skipped']} skipped, {secs:.0f} s")
    print(f"run_tests: {len(ids)} tests discovered in {len(shards)} shards, {failed} shards failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
