#!/usr/bin/env python3
"""Replay the packet from hashed snapshots and prove the two age/recency controls."""
import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B


def selftest():
    site = dict(site_id="SITE-test", org_id="ORG-test", street_address="1 Elm St")
    active = Counter({"ORG-test": 1})

    def filing(d, count, rid, kind="insp"):
        fields = dict(open_date=d, nr_in_estab=str(count), rid=rid, estab_name="Acme Plastics")
        if kind == "ita":
            fields.update(year_filing_for=d[:4], annual_average_employees=str(count),
                          establishment_name="Acme Plastics", company_name="", ein="", size="", submitted="")
        entry = dict(kind=kind, names=["Acme Plastics"], r=fields)
        return entry, "exact", "Acme Plastics"

    old = filing("2015-12-31", 20, "stale")
    ita = filing("2016-12-31", 20, "old", "ita")
    newer = filing("2024-01-01", 70, "new")
    boundary = filing("2016-11-23", 20, "boundary")

    def decide(ita_rows, insp_rows):
        return B.decide(site, dict(ita=ita_rows, insp=insp_rows), active, {}, {})

    result, losing = decide([], [old])
    if result[:2] != ("hold", "stale_over_10_years") or losing:
        raise AssertionError("planted 2015 filing was not rejected as stale")
    result, _ = decide([], [boundary])
    if result[0] != "fill":
        raise AssertionError("filing exactly on the cutoff was rejected")
    result, _ = decide([ita], [])
    if result[0] != "fill" or result[1]["band"] != "10-49":
        raise AssertionError("eligible baseline filing did not set its band")
    result, losing = decide([ita], [newer])
    if result[0] != "fill" or result[1]["band"] != "50-99" or losing != [(ita[0], newer[0])]:
        raise AssertionError("planted newer contradictory filing did not displace the old band")
    print("Controls PASS: 2015 filing held, cutoff accepted, newer adjacent band wins")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=B.DEFAULT_STORE)
    parser.add_argument("--selftest", action="store_true", help="run only the planted controls")
    args = parser.parse_args()
    selftest()
    if args.selftest:
        return
    with TemporaryDirectory(prefix="atlas-size-replay-") as tmp:
        work = Path(tmp)
        data = work / "tree"
        data.mkdir()
        with subprocess.Popen(["git", "archive", B.BASE, "data"], cwd=B.ROOT, stdout=subprocess.PIPE) as archive:
            subprocess.run(["tar", "-xf", "-", "-C", str(data)], stdin=archive.stdout, check=True)
            if archive.wait():
                raise RuntimeError(f"could not export pinned data at {B.BASE}")
        subprocess.run([sys.executable, "-I", str(HERE / "build.py"), "--store", str(args.store),
                        "--data-dir", str(data / "data"), "--out", str(work / "replay")], check=True)
        for name in B.OUTPUTS:
            if (HERE / name).read_bytes() != (work / "replay" / name).read_bytes():
                raise AssertionError(f"{name} differs from replay")
    print(f"Replay PASS: {len(B.OUTPUTS)} artifacts match byte-for-byte")


if __name__ == "__main__":
    main()
