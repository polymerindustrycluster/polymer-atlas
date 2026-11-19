#!/usr/bin/env python3
"""Run every scripts/test_*.py test in parallel shards (the CI unit-test step).

`unittest discover` ran the suite serially; it took about 4 of the validate job's 4.5 minutes on 2026-11-19, mostly
test_validate.py (86 tests, each copying data/ and running the full validator). Here each discovered test runs exactly
once, in one of N subprocesses (`python -m unittest <ids>`). A test class stays whole in one shard (its setUpClass may
write shared paths: test_build_site builds build/polymer-atlas.db) unless it sets `parallel_safe = True`, which says
every test uses only its own temporary files; then its tests are spread across shards.
Exit 1 when a shard fails, when discovery reports an import error, or when the shards ran a different number of tests
than were discovered.
Usage: python3 scripts/run_tests.py [--jobs N]     (default: the CPU count)
"""
import argparse
import os
import re
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent


def tests(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from tests(t)
        else:
            yield t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    jobs = max(1, ap.parse_args().jobs)
    loader = unittest.TestLoader()
    found = list(tests(loader.discover(str(HERE), pattern="test_*.py", top_level_dir=str(HERE))))
    if loader.errors:
        print("\n".join(map(str, loader.errors)))
        print(f"run_tests: {len(loader.errors)} test modules failed to import")
        return 1
    units = {}  # unit -> test ids: one test of a parallel_safe class, else a whole class
    for t in found:
        cls = type(t)
        units.setdefault(t.id() if getattr(cls, "parallel_safe", False) else f"{cls.__module__}.{cls.__qualname__}", []).append(t.id())
    shards = [[] for _ in range(jobs)]
    for unit in sorted(units.values(), key=len, reverse=True):  # largest first, each to the lightest shard
        min(shards, key=len).extend(unit)
    shards = [s for s in shards if s]
    ids = [i for s in shards for i in s]
    assert len(ids) == len(set(ids)) == len(found), "every discovered test must be in exactly one shard"

    def run(shard):
        return subprocess.run([sys.executable, "-m", "unittest", *shard], cwd=HERE, capture_output=True, text=True)

    with ThreadPoolExecutor(len(shards)) as ex:
        results = list(ex.map(run, shards))
    ran, failed = 0, 0
    for n, r in enumerate(results, 1):
        m = re.search(r"^Ran (\d+) tests?", r.stderr, re.M)
        ran += int(m.group(1)) if m else 0
        if r.returncode or not m:
            failed += 1
            print(f"--- shard {n} of {len(shards)} FAILED (exit {r.returncode}) ---\n{r.stdout}{r.stderr}")
        else:
            print(f"shard {n}: {r.stderr.strip().splitlines()[-1]} ({m.group(0)})")
    print(f"run_tests: {len(ids)} tests discovered, {ran} run in {len(shards)} shards, {failed} shards failed")
    return 1 if failed or ran != len(ids) else 0


if __name__ == "__main__":
    sys.exit(main())
