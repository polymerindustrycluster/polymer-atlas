#!/usr/bin/env python3
"""Integrator backlog (2026-11-04): HQ corrections, a parent link and ultimate-parent updates found by earlier lanes and
confirmed by a dedicated evidence lane (`findings.csv`; each quote re-fetched raw: `rawcheck.csv`).

    python3 tasks/integrator-backlog-2026-11-04/build.py --data-dir data [--apply --i-am-the-integrator]

Every change carries an evidence row.
- HQ corrections. BASF (OH→NJ) and BioVerde (OH→TX) move to their new shard, with their organization evidence
  rows, in the same pass (Appendix C §4). Pretium and MonoSol change city within their shard. `tier1_qualifier` is
  derived and is not touched here; the derivation re-runs separately.
- Parent link. AltraSet (ORG-001327) gets `parent_org_id` ORG-000430 (Mar-Bal) and its generated `parent_of` edge,
  for V-27 parity.
- Ultimate parents. Ashtabula Rubber, Flexsys, HC Companies and PlayCore: dated releases or own pages.

Held, notes only:
- BASF's 60/40 joint venture: the page does not name the LLC.
- ContiTech: the sale is announced, not closed.
- Viskase Osceola: no site row is held.
- HEXPOL: the identity is not confirmed.

Evidence ids start above EVD-077000, a block clear of open PRs and the reserved state ranges.
"""
import argparse, csv, io, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY, EVD0 = "2026-11-04", "claude-code integrator-backlog-2026-11-04", 77001
HQ = {  # org_id: (hq_city, hq_state, hq_county, hq_in_scope, finding item)
    "ORG-000698": ("Florham Park", "NJ", "Morris", "national_us", "basf-hq"),
    "ORG-000097": ("Houston", "TX", "Harris", "national_us", "bioverde-hq"),
    "ORG-000523": ("St. Louis", "MO", None, None, "pretium-hq"),
    "ORG-004456": ("Portage", "IN", "Porter", None, "monosol-hq"),
}
PARENT = {"ORG-001327": ("ORG-000430", "altraset-parent")}
ULT = {"ORG-000201": ("ASC Engineered Solutions", "ashtabula-rubber-owner"),
       "ORG-000343": ("One Rock Capital Partners", "flexsys-owner"),
       "ORG-000366": ("Platinum Equity", "hc-companies-owner"),
       "ORG-003666": ("Court Square Capital Partners", "aquaworx-parent")}


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return rows


def write(p, rows, header):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    if a.apply and data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
        sys.exit("editing the real data/ is integrator work; pass --i-am-the-integrator")
    find = {}
    raw = {r["item"]: r["raw"] for r in read(HERE / "rawcheck.csv")}
    for r in read(HERE / "findings.csv"):
        find.setdefault(r["item"], r)
    shards = {f: read(f) for f in sorted(data.glob("organizations_*.csv"))}
    headers = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in shards}
    where = {r["org_id"]: f for f, rows in shards.items() for r in rows}
    ev_files = {f: read(f) for f in sorted(data.glob("evidence_organizations_*.csv"))}
    ev_head = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in ev_files}
    new_ev, log, eid = defaultdict(list), [], EVD0

    def ok(item):
        f = find.get(item)
        return f and f["verdict"].strip() == "CONFIRMED" and raw.get(item) == "yes"

    def evid(oid, claim, item, detail, tag):
        nonlocal eid
        f = find[item]
        new_ev[tag].append({"evidence_id": f"EVD-{eid:06d}", "record_table": "organizations", "record_id": oid, "claim_type": claim,
                            "claim_detail": f"{detail} \"{f['quote'].strip()}\"", "source_class": f["source_class"].strip(),
                            "source_ref": f["source_url"].strip(), "observed_date": DATE,
                            "tier_effect": "supports_B" if f["source_class"].strip() == "press" else "supports_A",
                            "created_by": BY, "notes": f"integrator backlog 2026-11-04 ({item}); source dated {f.get('source_date') or 'n/a'}"})
        eid += 1

    def row(oid):
        return next(r for r in shards[where[oid]] if r["org_id"] == oid)

    for oid, (city, st, county, scope, item) in HQ.items():
        if not ok(item):
            log.append(f"HELD {oid} {item}: finding not confirmed or quote not raw-verified"); continue
        r = row(oid)
        old = (r["hq_city"], r["hq_state"])
        r["hq_city"], r["hq_state"] = city, st
        if county: r["hq_county"] = county
        if scope: r["hq_in_scope"] = scope
        r["last_verified"] = DATE
        r["notes"] = (r["notes"] + f" | {DATE}: HQ corrected {old[0]}, {old[1]} -> {city}, {st} per the company's own page ({item}).").strip(" |")
        old_f = where[oid]; new_f = data / f"organizations_{st}.csv"
        if new_f != old_f:  # Appendix C §4: move the record (and its org evidence rows) in the same pass
            shards[old_f].remove(r); shards.setdefault(new_f, read(new_f)); headers.setdefault(new_f, headers[old_f])
            shards[new_f].append(r); shards[new_f].sort(key=lambda x: x["org_id"]); where[oid] = new_f  # V-36: ids ascending
            old_e, new_e = data / f"evidence_organizations_{old_f.stem.split('_', 1)[1]}.csv", data / f"evidence_organizations_{st}.csv"
            moving = [e for e in ev_files.get(old_e, []) if e["record_id"] == oid]
            ev_files[old_e] = [e for e in ev_files[old_e] if e["record_id"] != oid]
            ev_files.setdefault(new_e, read(new_e)); ev_head.setdefault(new_e, ev_head[old_e]); ev_files[new_e] += moving
            log.append(f"MOVED {oid} {old_f.name} -> {new_f.name} with {len(moving)} evidence rows")
        evid(oid, "address", item, f"HQ {city}, {st}:", f"evidence_organizations_{st}.csv")
        log.append(f"HQ {oid}: {old} -> {(city, st)}")
    rel = read(data / "relationships.csv"); rel_head = next(csv.reader(open(data / "relationships.csv", encoding="utf-8")))
    nrel = max(int(x["relationship_id"][4:]) for x in rel) + 1
    for oid, (parent, item) in PARENT.items():
        if not ok(item):
            log.append(f"HELD {oid} {item}"); continue
        r = row(oid)
        r["parent_org_id"], r["last_verified"] = parent, DATE
        rel.append({"relationship_id": f"REL-{nrel:06d}", "from_org_id": parent, "relationship_type": "parent_of", "to_org_id": oid,
                    "basis": f"Generated from {oid}.parent_org_id (canonical §4.4 column); the column is the source of truth and this edge is its derived view (§4.14.2 single-source rule).",
                    "source_ref": f"organizations.csv: {oid}.parent_org_id", "created_by": BY, "notes": f"integrator backlog 2026-11-04 ({item})"})
        nrel += 1
        evid(oid, "parent", item, f"parent {parent}:", f"evidence_organizations_{where[oid].stem.split('_', 1)[1]}.csv")
        log.append(f"PARENT {oid} -> {parent}")
    for oid, (name, item) in ULT.items():
        if not ok(item):
            log.append(f"HELD {oid} {item}"); continue
        r = row(oid)
        old = r["ultimate_parent_name"]
        r["ultimate_parent_name"], r["last_verified"] = name, DATE
        r["notes"] = (r["notes"] + f" | {DATE}: ultimate parent {old or '(blank)'} -> {name} ({item}).").strip(" |")
        evid(oid, "parent", item, f"ultimate parent {name}:", f"evidence_organizations_{where[oid].stem.split('_', 1)[1]}.csv")
        log.append(f"ULT {oid}: {old!r} -> {name!r}")
    print("\n".join(log)); print(f"evidence rows {sum(len(v) for v in new_ev.values())}")
    (HERE / "journal.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    if a.apply:
        for f, rows in shards.items():
            write(f, rows, headers[f])
        for name, rows in new_ev.items():
            ev_files.setdefault(data / name, read(data / name)); ev_files[data / name] += rows
            ev_head.setdefault(data / name, next(csv.reader(open(data / name, encoding="utf-8"))))
        for f, rows in ev_files.items():
            write(f, rows, ev_head[f])
        write(data / "relationships.csv", rel, rel_head)
        print("applied")


if __name__ == "__main__":
    main()
