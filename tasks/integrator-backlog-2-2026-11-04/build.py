#!/usr/bin/env python3
"""Integrator backlog 2 (2026-11-04): HQ corrections that the state lanes flagged on held records. Each was confirmed by
a dedicated evidence lane (`findings.csv`) and its quote re-fetched raw and found word for word (`rawcheck.csv`; the
route is NAS Firecrawl, or Jina Reader where Firecrawl could not fetch the page).

    python3 tasks/integrator-backlog-2-2026-11-04/build.py --data-dir data [--apply --i-am-the-integrator]

A record whose HQ state changes moves to its new shard in the same pass, with its organization evidence rows
(Appendix C §4); shards stay id-ascending (V-36). A file committed with CRLF line endings is written back with CRLF,
so the diff shows only the changed rows. `tier1_qualifier` is derived and is not touched. Its plants keep their site
rows, because an HQ move changes no site.
Reused from tasks/integrator-backlog-2026-11-04/build.py: the parent and ultimate-parent steps are dropped and the HQ
map is replaced.
"""
import argparse, csv, io, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY = "2026-11-04", "claude-code integrator-backlog-2-2026-11-04"
HQ = {  # org_id: (hq_city, hq_state, hq_county, finding item); every new HQ is outside Ohio, so hq_in_scope = national_us
    "ORG-000340": ("Baraboo", "WI", "Sauk", "flambeau-hq"),
    "ORG-000620": ("Holyoke", "MA", "Hampden", "universal-plastics-hq"),
    "ORG-000760": ("Kentwood", "MI", "Kent", "corvac-hq"),
    "ORG-000769": ("Fenton", "MI", "Genesee", "creative-foam-hq"),
    "ORG-000984": ("Atlanta", "GA", "Fulton", "wincup-hq"),
    "ORG-001151": ("Mendon", "MI", "St. Joseph", "th-plastics-hq"),
    "ORG-002462": ("Asheboro", "NC", "Randolph", "technimark-hq"),
    "ORG-002534": ("Alpharetta", "GA", "Fulton", "pexco-hq"),
    "ORG-002535": ("Somerville", "MA", "Middlesex", "rogers-foam-hq"),
    "ORG-006188": ("La Habra", "CA", "Orange", "vip-rubber-hq"),
    "ORG-002261": ("Los Angeles", "CA", "Los Angeles", "jm-eagle-hq"),
}


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(p, rows, header):
    eol = "\r\n" if b"\r\n" in p.read_bytes()[:4096] else "\n" if p.exists() else "\n"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator=eol, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
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
    raw = {r["item"]: r["raw"] for r in read(HERE / "rawcheck.csv")}
    find = {}
    for r in read(HERE / "findings.csv"):
        if r["item"] in {v[3] for v in HQ.values()} and r["field"] == "hq_city/hq_state":
            find.setdefault(r["item"], r)
    shards = {f: read(f) for f in sorted(data.glob("organizations_*.csv"))}
    headers = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in shards}
    where = {r["org_id"]: f for f, rows in shards.items() for r in rows}
    ev_files = {f: read(f) for f in sorted(data.glob("evidence_organizations_*.csv"))}
    ev_head = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in ev_files}
    ev_all = [e for f in sorted(data.glob("evidence*.csv")) for e in read(f)]
    # AGENTS §3: above the max of main AND every open PR. #117 holds EVD-078028..078090 and #116 tops out at EVD-112175
    # (scan of 2026-11-04), so this block starts at 113001.
    eid = max([113000] + [int(e["evidence_id"][4:]) for e in ev_all if e["evidence_id"][4:].isdigit()]) + 1
    new_ev, log, touched, ev_touched = defaultdict(list), [], set(), set()

    for oid, (city, st, county, item) in HQ.items():
        f = find.get(item)
        if not (f and f["verdict"].strip() == "CONFIRMED" and raw.get(item, "").startswith("yes")):
            log.append(f"HELD {oid} {item}: finding not confirmed or quote not raw-verified"); continue
        r = next(x for x in shards[where[oid]] if x["org_id"] == oid)
        old = (r["hq_city"], r["hq_state"])
        r.update(hq_city=city, hq_state=st, hq_county=county, hq_in_scope="national_us", hq_country="US", last_verified=DATE)
        r["notes"] = (r["notes"] + f" | {DATE}: HQ corrected {old[0]}, {old[1]} -> {city}, {st} per the company's own page ({item}); the {old[0]} plant is unchanged.").strip(" |")
        old_f, new_f = where[oid], data / f"organizations_{st}.csv"
        touched.add(old_f)
        if new_f != old_f:
            shards[old_f].remove(r); shards.setdefault(new_f, read(new_f)); headers.setdefault(new_f, headers[old_f])
            shards[new_f].append(r); shards[new_f].sort(key=lambda x: x["org_id"]); where[oid] = new_f; touched.add(new_f)
            old_e, new_e = data / f"evidence_organizations_{old_f.stem.split('_', 1)[1]}.csv", data / f"evidence_organizations_{st}.csv"
            moving = [e for e in ev_files.get(old_e, []) if e["record_id"] == oid]
            if moving:
                ev_files[old_e] = [e for e in ev_files[old_e] if e["record_id"] != oid]
                ev_files.setdefault(new_e, read(new_e)); ev_head.setdefault(new_e, ev_head[old_e]); ev_files[new_e] += moving
                ev_touched.update({old_e, new_e})  # both sides are rewritten, or the moved rows would exist twice (V-22)
            log.append(f"MOVED {oid} {old_f.name} -> {new_f.name} with {len(moving)} evidence rows")
        new_ev[f"evidence_organizations_{st}.csv"].append({
            "evidence_id": f"EVD-{eid:06d}", "record_table": "organizations", "record_id": oid, "claim_type": "address",
            "claim_detail": f"HQ {city}, {st}: \"{f['quote'].strip()}\"", "source_class": f["source_class"].strip(),
            "source_ref": f["source_url"].strip(), "observed_date": DATE,
            "tier_effect": "supports_B" if f["source_class"].strip() == "press" else "supports_A", "created_by": BY,
            "notes": f"integrator backlog 2 ({item}); raw check {raw[item]}; source dated {f.get('source_date') or 'n/a'}"})
        eid += 1
        log.append(f"HQ {oid}: {old} -> {(city, st)}")
    print("\n".join(log)); print(f"evidence rows {sum(len(v) for v in new_ev.values())}")
    (HERE / "journal.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    if a.apply:
        for f in touched:
            write(f, shards[f], headers[f])
        for name, rows in new_ev.items():
            p = data / name
            ev_files.setdefault(p, read(p)); ev_head.setdefault(p, next(csv.reader(open(p, encoding="utf-8")))); ev_files[p] += rows
        for f in {data / n for n in new_ev} | ev_touched:
            write(f, ev_files[f], ev_head[f])
        print("applied")


if __name__ == "__main__":
    main()
