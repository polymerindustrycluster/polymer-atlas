#!/usr/bin/env python3
"""Check for region-labels-2026-11-22. From the repo root:  python3 tasks/region-labels-2026-11-22/check.py
Recomputes every proposed hq_in_scope cell from the base row's HQ state and county (rules.py + scripts/regions.py), fails on a
planted wrong value, a planted omission and a planted overwrite, applies the packet to a scratch copy and requires identical
validator output and a cell-for-cell diff. Exit 0 = pass."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C, rules as R
from build import classify_all


def recompute(base):
    return {(f, o["org_id"], "hq_in_scope"): after for f, o, after, _cat in classify_all(base) if after}


def known():
    o = lambda s, c, l: dict(hq_state=s, hq_county=c, hq_in_scope=l)
    cases = [("Summit pic12 -> ne_ohio", o("OH", "Summit", "pic12"), set(), "ne_ohio"), ("Huron ohio_other -> ne_ohio", o("OH", "Huron", "ohio_other"), set(), "ne_ohio"),
             ("Tuscarawas ohio_statewide -> ne_ohio", o("OH", "Tuscarawas", "ohio_statewide"), set(), "ne_ohio"),
             ("agreeing row untouched", o("OH", "Summit", "ne_ohio"), set(), ""), ("Franklin ohio_other agrees", o("OH", "Franklin", "ohio_other"), set(), ""),
             ("Nashville TN with Summit is a record error", o("TN", "Summit", "national_us"), set(), ""),
             ("national_us label on a PIC-18 county is held", o("OH", "Summit", "national_us"), set(), ""),
             ("county contradicted by a same-city site is held", o("OH", "Summit", "pic12"), {"Franklin"}, ""),
             ("not an Ohio county is held", o("OH", "Wyandot / Wood", "ohio_other"), set(), ""), ("blank county held", o("OH", "", "ohio_other"), set(), "")]
    return [(n, R.classify(r, sc)[0], w) for n, r, sc, w in cases]


def independent(base, mine):
    """Written without rules.py: precision (after == ne_ohio iff hq_state OH and hq_county in PIC-18 and the label was one of the three
    that contradict that) and recall (every such base row is a change or is listed in holds/ or record_errors.csv)."""
    from regions import PIC18
    errs, rows = [], {r["org_id"]: r for _f, r in C.tagged(base, "organizations_*.csv")}
    for c in mine:
        r = rows[c["record_id"]]
        if not (c["after"] == "ne_ohio" and r["hq_state"] == "OH" and r["hq_county"] in PIC18 and r["hq_in_scope"] in ("pic12", "ohio_other", "ohio_statewide")):
            errs.append(f"{c['record_id']}: state {r['hq_state']!r} county {r['hq_county']!r} label {r['hq_in_scope']!r} -> {c['after']!r} is not a PIC-18 relabel")
    listed = {r["org_id"] for p in (C.HERE / "holds").glob("*.csv") for r in C.read_csv(p)} | {r["org_id"] for r in C.read_csv(C.HERE / "record_errors.csv")}
    got = {c["record_id"] for c in mine}
    for oid, r in rows.items():
        if r["hq_state"] == "OH" and r["hq_county"] in PIC18 and r["hq_in_scope"] in ("pic12", "ohio_other", "ohio_statewide") and oid not in got and oid not in listed:
            errs.append(f"{oid}: PIC-18 county, label {r['hq_in_scope']!r}, neither relabelled nor listed")
    return errs


if __name__ == "__main__":
    sys.exit(C.check_main(recompute, [("organizations_OH.csv", "hq_in_scope")], known, independent))
