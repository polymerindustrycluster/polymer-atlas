#!/usr/bin/env python3
"""Check for ohio-statewide-labels-2026-11-22. From the repo root:  python3 tasks/ohio-statewide-labels-2026-11-22/check.py
Recomputes every cell from state + county, adds an independent assertion, fails on a planted wrong value, omission and overwrite, applies
the packet to a scratch copy (validator output identical to base, diff = packet). Exit 0 = pass."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C, rules as R
from build import classify_all


def recompute(base):
    return {(f, o["org_id"], "hq_in_scope"): after for f, o, after, _c in classify_all(base) if after}


def known():
    o = lambda s, c, l="ohio_statewide": dict(hq_state=s, hq_county=c, hq_in_scope=l)
    cases = [("Franklin -> ohio_other", o("OH", "Franklin"), set(), "ohio_other"), ("PIC-18 county held", o("OH", "Summit"), set(), ""),
             ("blank county held", o("OH", ""), set(), ""), ("non-Ohio county held", o("OH", "Wyandot / Wood"), set(), ""),
             ("other label untouched", o("OH", "Franklin", "ohio_other"), set(), ""), ("same-city site in another county held", o("OH", "Franklin"), {"Delaware"}, ""),
             ("non-Ohio state held", o("TX", "Harris"), set(), "")]
    return [(n, R.classify(r, sc)[0], w) for n, r, sc, w in cases]


def independent(base, mine):
    """Without rules.py: precision (each change: base label ohio_statewide, state OH, county named and in no PIC-18 list) and recall
    (every such base row is a change or listed in holds.csv)."""
    from regions import PIC18
    errs, rows = [], {r["org_id"]: r for _f, r in C.tagged(base, "organizations_*.csv")}
    for c in mine:
        r = rows[c["record_id"]]
        if not (r["hq_in_scope"] == "ohio_statewide" and r["hq_state"] == "OH" and r["hq_county"].strip() and r["hq_county"] not in PIC18 and c["after"] == "ohio_other"):
            errs.append(f"{c['record_id']}: {r['hq_state']!r} {r['hq_county']!r} {r['hq_in_scope']!r} -> {c['after']!r} is not an ohio_statewide relabel")
    listed = {r["org_id"] for r in C.read_csv(C.HERE / "holds.csv")}; got = {c["record_id"] for c in mine}
    for oid, r in rows.items():
        if r["hq_in_scope"] == "ohio_statewide" and oid not in got and oid not in listed:
            errs.append(f"{oid}: ohio_statewide row neither relabelled nor listed")
    return errs


if __name__ == "__main__":
    sys.exit(C.check_main(recompute, [("organizations_OH.csv", "hq_in_scope")], known, independent))
