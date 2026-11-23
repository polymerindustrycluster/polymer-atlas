#!/usr/bin/env python3
"""Build the entity_type-from-legal-name packet from data/ at BASE_REF.  python3 build.py [--out DIR]
Writes changes.csv (before/after per cell, every frame; a PR applies one frame), holds/*.csv, counts.json and the
canary (canary-25/). Nothing under data/ is touched."""
import argparse, collections, json, tempfile
from pathlib import Path
import common as C
from rules import classify

OUT = C.HERE


def build(data):
    sites = C.sites_by_org(data)
    changes, holds, counts = [], collections.defaultdict(list), collections.Counter()
    for fname, r in C.tagged(data, "organizations_*.csv"):
        frame = C.org_frame(r, sites.get(r["org_id"], []))
        value, cat, suf = classify(r)
        counts[(frame, cat)] += 1
        if cat == "fill" and frame != "outside":
            changes.append(dict(change_id=f"ET-{len(changes)+1:05d}", frame=frame, table="organizations", file=fname,
                                record_id=r["org_id"], column="entity_type", before=r["entity_type"], after=value,
                                rule="legal_name ends in a single legal-form suffix", basis=f'legal_name suffix "{suf}" -> {value}'))
        elif cat != "fill" and r["entity_type"] in ("", "unknown") or cat == "conflict_existing_value":
            holds[cat].append(dict(frame=frame, org_id=r["org_id"], legal_name=r["legal_name"], entity_type=r["entity_type"], suffix=suf,
                                   ownership_type=r["ownership_type"], stock_ticker=r["stock_ticker"], hq_state=r["hq_state"], hq_country=r["hq_country"]))
    return changes, holds, counts


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(OUT)); a = ap.parse_args()
    out = Path(a.out)
    with tempfile.TemporaryDirectory() as tmp:
        data = C.export_tree(C.base_ref(), tmp)
        changes, holds, counts = build(data)
    C.write_csv(out / "changes.csv", C.CHANGE_COLS, changes)
    (out / "holds").mkdir(exist_ok=True)
    for cat, rows in holds.items():
        C.write_csv(out / "holds" / f"{cat}.csv", list(rows[0]), rows)
    summary = {"base_ref": C.base_ref(), "unit": "organizations rows (data/organizations_*.csv), all statuses",
               "counts": {f"{f}|{c}": n for (f, c), n in sorted(counts.items())},
               "changes_by_frame": dict(collections.Counter(c["frame"] for c in changes)),
               "changes_by_value": {f"{k[0]}|{k[1]}": v for k, v in collections.Counter((c["frame"], c["after"]) for c in changes).items()}}
    (out / "counts.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary["changes_by_frame"]), len(changes))


if __name__ == "__main__":
    main()
