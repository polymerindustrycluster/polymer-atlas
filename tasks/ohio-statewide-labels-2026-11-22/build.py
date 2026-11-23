#!/usr/bin/env python3
"""Build the ohio_statewide -> ohio_other packet from data/ at BASE_REF.  python3 build.py"""
import collections, json, tempfile
import common as C, rules as R

HOLD_HEAD = ["org_id", "legal_name", "hq_city", "hq_state", "hq_county", "hq_in_scope", "status", "file"]


def classify_all(data):
    city = {}
    for _f, s in C.tagged(data, "sites_*.csv"):
        if s["state"] == "OH" and s["county"] and s["operating_status"] != "closed":
            city.setdefault(s["city"].strip().lower(), set()).add(s["county"])
    for f, o in C.tagged(data, "organizations_*.csv"):
        after, cat = R.classify(o, city.get(o["hq_city"].strip().lower(), set()) if o["hq_state"] == "OH" else set())
        yield f, o, after, cat


def main():
    out = C.HERE; changes, holds, counts = [], [], collections.Counter()
    with tempfile.TemporaryDirectory() as tmp:
        data = C.export_tree(C.base_ref(), tmp)
        for f, o, after, cat in classify_all(data):
            counts[cat] += 1
            if after:
                changes.append(dict(change_id=f"OS-{len(changes)+1:05d}", frame="ohio_rest", table="organizations", file=f, record_id=o["org_id"],
                                    column="hq_in_scope", before="ohio_statewide", after=after, rule=cat,
                                    basis=f'hq_state=OH, hq_county={o["hq_county"]} is a named Ohio county outside PIC-18 (scripts/regions.py)'))
            elif cat != "not_ohio_statewide":
                holds.append(dict(org_id=o["org_id"], legal_name=o["legal_name"], hq_city=o["hq_city"], hq_state=o["hq_state"], hq_county=o["hq_county"],
                                  hq_in_scope=o["hq_in_scope"], status=o["status"], file=f, hold_class=cat))
    C.write_csv(out / "changes.csv", C.CHANGE_COLS, changes)
    C.write_csv(out / "holds.csv", HOLD_HEAD + ["hold_class"], holds)
    (out / "counts.json").write_text(json.dumps({"base_ref": C.base_ref(), "unit": "organizations rows (data/organizations_*.csv), all statuses",
                                                 "counts": dict(sorted(counts.items()))}, indent=1) + "\n")
    print(len(changes), len(holds), dict(counts))


if __name__ == "__main__":
    main()
