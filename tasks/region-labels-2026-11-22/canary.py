#!/usr/bin/env python3
"""25-row canary for the region packet (stratified; the review-named records first), shown as the owner sees the row."""
import hashlib, tempfile
import common as C
from build import classify_all

PLAN = [("relabel_pic12", 8), ("relabel_ohio_other", 8), ("relabel_ohio_statewide", 3), ("hold_label_outside_ohio_but_ohio_pic18_county", 2),
        ("record_error_county_not_in_state", 2), ("hold_ohio_statewide_undefined", 1), ("record_error_ohio_label_on_non_ohio_state", 1)]
NAMED = ["ORG-000011", "ORG-000955", "ORG-001029"]
h = lambda s: hashlib.sha1(("canary-rl-" + s).encode()).hexdigest()
with tempfile.TemporaryDirectory() as tmp:
    data = C.export_tree(C.base_ref(), tmp)
    sites = C.sites_by_org(data)
    pool = {}
    for f, o, after, cat in classify_all(data):
        pool.setdefault(cat, []).append((o, after))
    rows = []
    for cat, n in PLAN:
        c = sorted(pool[cat], key=lambda t: h(t[0]["org_id"]))
        c = [t for t in c if t[0]["org_id"] in NAMED] + [t for t in c if t[0]["org_id"] not in NAMED]
        for o, after in c[:n]:
            ss = sites.get(o["org_id"], [])
            rows.append(dict(org_id=o["org_id"], category=cat, legal_name=o["legal_name"], hq_city=o["hq_city"], hq_state=o["hq_state"], hq_county=o["hq_county"],
                             hq_in_scope_before=o["hq_in_scope"], hq_in_scope_after=after, site_counties=";".join(sorted({s["county"] for s in ss if s["state"] == "OH"})),
                             status=o["status"]))
    C.write_csv(C.HERE / "canary-25" / "frame.csv", list(rows[0]), rows)
    for x in rows:
        print(f'{x["org_id"]:11} {x["category"][:30]:30} {x["legal_name"][:34]:34} {x["hq_city"][:14]:14} {x["hq_state"]:3} {x["hq_county"][:11]:11} {x["hq_in_scope_before"]:14}->{x["hq_in_scope_after"] or "(hold)":9} sites:{x["site_counties"][:22]}')
