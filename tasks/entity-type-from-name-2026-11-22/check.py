#!/usr/bin/env python3
"""Check for entity-type-from-name-2026-11-22. From the repo root:  python3 tasks/entity-type-from-name-2026-11-22/check.py
Recomputes every proposed cell from the base rows (BASE_REF) with rules.classify, fails on a planted wrong value, a planted
omission and a planted overwrite of a non-blank cell, applies the packet to a scratch copy and requires the validator output
to be identical to the base's, and requires the scratch diff to equal the packet cell for cell. Exit 0 = pass."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
from rules import classify


def recompute(base):
    sites = C.sites_by_org(base)
    out = {}
    for f, r in C.tagged(base, "organizations_*.csv"):
        value, cat, _ = classify(r)
        if cat == "fill" and C.org_frame(r, sites.get(r["org_id"], [])) != "outside":
            out[(f, r["org_id"], "entity_type")] = value
    return out


def known():
    mk = lambda n, c="US", s="OH", t="", e="unknown": dict(legal_name=n, hq_country=c, hq_state=s, stock_ticker=t, entity_type=e)
    cases = [("LLC", mk("Foo Plastics LLC"), "llc"), ("L.L.C.", mk("Foo, L.L.C."), "llc"), ("LP", mk("Foo Polymers LP"), "partnership"),
             ("LLP", mk("Foo Polymers, LLP"), "partnership"), ("Inc fills (v1.19.4)", mk("Foo Inc."), "corporation"), ("Corp fills (v1.19.4)", mk("Foo Corp"), "corporation"),
             ("Ltd held", mk("Foo Ltd."), ""), ("dba held", mk("Foo LLC dba Bar"), ""), ("conflict held", mk("Foo Co., LLC"), ""),
             ("foreign held", mk("Foo LLC", c="CA", s="ON"), ""), ("ticker held", mk("Foo LLC", t="FOO"), ""),
             ("Inc fills corporation", mk("Foo Inc."), "corporation"), ("Incorporated", mk("Foo, Incorporated"), "corporation"),
             ("Corp", mk("Foo Corp."), "corporation"), ("Corporation", mk("Foo Corporation"), "corporation"),
             ("Co. stays unknown", mk("Foo Co."), ""), ("Company stays unknown", mk("Foo Company"), ""), ("Limited stays unknown", mk("Foo Limited"), ""),
             ("name-word Co with Inc", mk("Smith & Co., Inc."), "corporation"), ("two corporate forms held", mk("Foo Corp. Inc."), ""),
             ("corporation ticker held (public is not guessed)", mk("Foo Inc.", t="FOO"), ""), ("Inc over corporation_private untouched", mk("Foo Inc.", e="corporation_private"), ""),
             ("known value kept", mk("Foo LLC", e="corporation_private"), ""), ("no suffix", mk("Foo Plastics"), "")]
    return [(n, classify(r)[0], w) for n, r, w in cases]


def independent(base, mine):
    """Written without rules.py: precision (every change is a blank/unknown cell whose name ends in a standalone LLC, LP or Inc/Corp form)
    and recall (every Ohio-frame LLC-ending blank/unknown row is either a change or listed in holds/)."""
    import csv, re
    llc = re.compile(r"(?i)[\s,](l\.?l\.?c\.?|limited liability company)\s*$")
    lp = re.compile(r"(?i)[\s,](l\.?l\.?l\.?p\.?|l\.?l\.?p\.?|l\.?p\.?|limited partnership|limited liability partnership)\s*$")
    corp = re.compile(r"(?i)[\s,](inc\.?|incorporated|corp\.?|corporation)\s*$")
    import json
    enum = set(json.loads((C.ROOT / "docs/schema/vocab.json").read_text())["vocabularies"]["ENTITY_TYPE"]["values"])
    errs, rows = [], {r["org_id"]: r for _f, r in C.tagged(base, "organizations_*.csv")}
    for c in mine:
        r, n = rows[c["record_id"]], rows[c["record_id"]]["legal_name"].strip()
        if r["entity_type"] not in ("", "unknown"):
            errs.append(f"{c['record_id']}: base cell {r['entity_type']!r} is not blank/unknown")
        if "corporation" not in enum or c["after"] not in enum:
            errs.append(f"{c['record_id']}: {c['after']!r} is not in the entity_type enum in docs/schema/vocab.json")
        if not ((c["after"] == "llc" and llc.search(n)) or (c["after"] == "partnership" and lp.search(n) and not llc.search(n))
                or (c["after"] == "corporation" and corp.search(n) and not llc.search(n) and not lp.search(n))):
            errs.append(f"{c['record_id']}: {n!r} does not end in a {c['after']} form")
    held = {r["org_id"] for p in (C.HERE / "holds").glob("*.csv") for r in C.read_csv(p)}
    got = {c["record_id"] for c in mine}
    sites = C.sites_by_org(base)
    for oid, r in rows.items():
        if r["entity_type"] in ("", "unknown") and (llc.search(r["legal_name"].strip()) or lp.search(r["legal_name"].strip()) or corp.search(r["legal_name"].strip())) \
                and C.org_frame(r, sites.get(oid, [])) != "outside" and oid not in got and oid not in held:
            errs.append(f"{oid} {r['legal_name']!r}: ends in a legal form but is neither a change nor a listed hold")
    return errs


if __name__ == "__main__":
    sys.exit(C.check_main(recompute, [("organizations_OH.csv", "entity_type")], known, independent))
