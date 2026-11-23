#!/usr/bin/env python3
"""Pick the 25-row canary (stratified; the two review-named records first) and print each row as its owner sees it."""
import csv, hashlib, sys, tempfile
import common as C
from rules import classify

PLAN = [("fill:corporation:pic18", 13), ("fill:llc:pic18", 3), ("fill:partnership:pic18", 1), ("fill:ohio_rest", 2), ("held_corporate_suffix:pic18", 3),
        ("held_ticker_conflict:pic18", 1), ("held_conflicting_forms:pic18", 1), ("held_dba_form:pic18", 1)]
NAMED = ["ORG-001921", "ORG-001777", "ORG-002037", "ORG-000446", "ORG-001641", "ORG-001578", "ORG-000577"]
h = lambda s: hashlib.sha1(("canary-et-" + s).encode()).hexdigest()

with tempfile.TemporaryDirectory() as tmp:
    data = C.export_tree(C.base_ref(), tmp)
    sites = C.sites_by_org(data)
    pool = {}
    for f, r in C.tagged(data, "organizations_*.csv"):
        fr = C.org_frame(r, sites.get(r["org_id"], []))
        v, cat, suf = classify(r)
        if r["entity_type"] not in ("", "unknown") or fr == "outside":
            continue
        key = f"fill:{v}:pic18" if cat == "fill" and fr == "pic18" else ("fill:ohio_rest" if cat == "fill" else f"{cat}:{fr}")
        pool.setdefault(key, []).append((r, v, cat, suf, fr))
    pick = []
    for key, n in PLAN:
        c = sorted(pool.get(key, []), key=lambda t: h(t[0]["org_id"]))
        named = [t for t in c if t[0]["org_id"] in NAMED]
        pick += (named + [t for t in c if t not in named])[:n]
    rows = []
    for r, v, cat, suf, fr in pick:
        rows.append(dict(org_id=r["org_id"], frame=fr, category=cat, suffix=suf, legal_name=r["legal_name"], entity_type_before=r["entity_type"],
                         entity_type_after=v, ownership_type=r["ownership_type"], hq=f'{r["hq_city"]}, {r["hq_state"]} ({r["hq_county"]})',
                         website=r["website"], description_1line=r["description_1line"][:160]))
    C.write_csv(C.HERE / "canary-25" / "frame.csv", list(rows[0]), rows)
    print(len(rows))
    for x in rows:
        print(f'{x["org_id"]:11} {x["category"]:26} {x["legal_name"][:52]:52} | {x["entity_type_after"] or "-":11} | {x["hq"][:34]:34} | {x["description_1line"][:90]}')
