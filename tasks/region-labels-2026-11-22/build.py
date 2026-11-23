#!/usr/bin/env python3
"""Build the hq_in_scope packet from data/ at BASE_REF.  python3 build.py [--out DIR]
changes.csv (before/after per cell), holds/<class>.csv, record_errors.csv, counts.json. Nothing under data/ is touched."""
import argparse, collections, json, tempfile
from pathlib import Path
import common as C
import rules as R

HOLD_HEAD = ["org_id", "legal_name", "hq_city", "hq_state", "hq_county", "hq_in_scope", "status", "file"]


def same_city_counties(data):
    m = {}
    for _f, s in C.tagged(data, "sites_*.csv"):
        if s["state"] == "OH" and s["county"] and s["operating_status"] != "closed":
            m.setdefault(s["city"].strip().lower(), set()).add(s["county"])
    return m


def classify_all(data):
    city = same_city_counties(data)
    for f, o in C.tagged(data, "organizations_*.csv"):
        sc = city.get(o["hq_city"].strip().lower(), set()) if o["hq_state"] == "OH" else set()
        after, cat = R.classify(o, sc)
        yield f, o, after, cat


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(C.HERE)); out = Path(ap.parse_args().out)
    changes, holds, counts = [], collections.defaultdict(list), collections.Counter()
    with tempfile.TemporaryDirectory() as tmp:
        data = C.export_tree(C.base_ref(), tmp)
        city = same_city_counties(data)
        for f, o, after, cat in classify_all(data):
            counts[cat] += 1
            # the same-city county test over EVERY Ohio-HQ row, not only the ones whose label disagrees (a city can span counties: leads, not verdicts)
            sc = city.get(o["hq_city"].strip().lower(), set())
            if o["hq_state"] == "OH" and o["hq_county"] in R.COUNTIES["OH"] and sc and o["hq_county"] not in sc and cat != "record_error_county_vs_site_county":
                holds["record_error_county_vs_site_county_label_unaffected"].append(dict(org_id=o["org_id"], legal_name=o["legal_name"], hq_city=o["hq_city"], hq_state=o["hq_state"],
                    hq_county=o["hq_county"], hq_in_scope=o["hq_in_scope"], status=o["status"], file=f))
            if after:
                changes.append(dict(change_id=f"RL-{len(changes)+1:05d}", frame="pic18", table="organizations", file=f, record_id=o["org_id"],
                                    column="hq_in_scope", before=o["hq_in_scope"], after=after, rule=cat,
                                    basis=f'hq_state=OH and hq_county={o["hq_county"]} is a PIC-18 county (scripts/regions.py)'))
            elif not cat.startswith(("agree", "skip")):
                holds[cat].append(dict(org_id=o["org_id"], legal_name=o["legal_name"], hq_city=o["hq_city"], hq_state=o["hq_state"],
                                       hq_county=o["hq_county"], hq_in_scope=o["hq_in_scope"], status=o["status"], file=f))
    C.write_csv(out / "changes.csv", C.CHANGE_COLS, changes)
    (out / "holds").mkdir(exist_ok=True)
    for cat, rows in holds.items():
        C.write_csv(out / "holds" / f"{cat}.csv", HOLD_HEAD, rows)
    rec = [dict(r, error_class=c) for c, rs in holds.items() if c.startswith(("record_error", "hold_label_outside", "hold_other")) for r in rs]
    C.write_csv(out / "record_errors.csv", ["error_class"] + HOLD_HEAD, rec)
    summary = {"base_ref": C.base_ref(), "unit": "organizations rows (data/organizations_*.csv), all statuses", "region": "PIC-18 (scripts/regions.py)",
               "counts_by_class": dict(sorted(counts.items())), "relabels_by_stored_label": dict(collections.Counter(c["before"] for c in changes))}
    (out / "counts.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(len(changes), summary["relabels_by_stored_label"], len(rec))


if __name__ == "__main__":
    main()
