#!/usr/bin/env python3
"""Dedupe pairs and HQ pass 2 (2026-11-04). Stacked on #122 (ownership/status pilot).

    python3 tasks/dedupe-hq-2-2026-11-04/build.py --data-dir data [--apply --i-am-the-integrator]

Inputs: `lanes/D_out.csv` (15 pairs), `lanes/H_out.csv` (16 HQ checks), with every quote re-fetched raw and matched
as a word sequence (`rawcheck_D.csv`, `rawcheck_H.csv`). A change is applied only when its quote is raw-verified and
the integrator decision below names it. AGENTS.md §3: when in doubt, do not merge.
- HQ: an org whose HQ moves to another state moves shard, with its organization evidence rows, in the same pass
  (Appendix C §4). Logic reused from tasks/integrator-backlog-2-2026-11-04/build.py. Plants keep their site rows.
- MERGE: one business recorded twice -> the duplicate gets `status=merged`, `status_date` = this pass's date (record
  lineage, never a corporate date), `successor_org_id` = the survivor, and its generated `merged_into` edge, worded as
  a dedupe consolidation (§4.14.2). Sites stay linked to the duplicate, as in earlier consolidations.
- ACQ: the record is a business bought by the other record on a dated deal -> `status=acquired`, `status_date`,
  `successor_org_id`, and its generated `successor_of` edge, plus a `parent` evidence row.
- PARENT: `parent_org_id` + its generated `parent_of` edge, plus a `parent` evidence row.
- AMETEK: Ametek sold its Nesquehoning plant (SITE-002544, Westchester Plastics) to Niche Polymer on 2021-09-07. The
  plant and its FRS facility link move to Niche, the operator (AGENTS.md §3 step 3). ORG-002556 also holds Ametek's
  St. Louis plant, so it is Ametek itself and keeps its name and status; its Nesquehoning HQ is flagged in notes.
- WATCH: `monitor_watch=true` for two announced, not yet closed, plant closures (a queue flag, never a status change).
"""
import argparse, csv, io, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY = "2026-11-04", "claude-code dedupe-hq-2-2026-11-04"
HQ = {  # org_id: (hq_city, hq_state, hq_county); every new HQ is outside Ohio, so hq_in_scope = national_us
    "ORG-001108": ("Mount Pleasant", "TN", "Maury"), "ORG-001082": ("Oakland", "TN", "Fayette"),
    "ORG-001118": ("Enka", "NC", "Buncombe"), "ORG-001193": ("Washington", "PA", "Washington"),
    "ORG-001093": ("Winona", "MN", "Winona"), "ORG-001489": ("Parsippany", "NJ", "Morris"),
    "ORG-003420": ("Tempe", "AZ", "Maricopa"), "ORG-004957": ("Fairfield", "CA", "Solano"),
    "ORG-002643": ("Charlotte", "NC", "Mecklenburg"), "ORG-005041": ("Hickory", "NC", "Catawba"),
    "ORG-003943": ("Huntersville", "NC", "Mecklenburg"),
}
MERGE = {"ORG-002323": "ORG-002324", "ORG-002384": "ORG-002325"}  # duplicate -> survivor
ACQ = {"ORG-000484": ("ORG-002534", "2021-12-01"), "ORG-000492": ("ORG-004564", "2023-02-02")}
ACQ_NOTE = {"ORG-000492": " The date is the buyer's release date ('announced today'); the closing date is not stated (SCHEMA §5.4)."}
# Cross-family refute (grok + codex, deep, 2026-11-04) of the first build: held after review.
COUNCIL_HELD = {
    "ORG-001813": "council: the record bundles Formco, a separate 2018 acquisition by Molded Devices, so it is not simply a duplicate of Aptyx",
    "ORG-006171": "council: the quote is Tekni-Plex buying Dunn Industries; whether 'Tekniplex Healthcare' is only the former Dunn business is open",
}
PARENT = {"ORG-000119": "ORG-007802"}
AMETEK = ("ORG-002556", "ORG-004886", "2021-09-07", "SITE-002544", "Ametek Westchester Plastics")
WATCH = {"ORG-000870": "H.B. Fuller announced the closure of its Paducah, KY plant (expected Q1 2027)",
         "ORG-003702": "INOAC announced the closure of its Livingston plant (expected April 2027)"}
PAIR = {"ORG-002323": "ORG-002324|ORG-002323", "ORG-002384": "ORG-002384|ORG-002325", "ORG-001813": "ORG-001813|ORG-000449",
        "ORG-000484": "ORG-002534|ORG-000484", "ORG-000492": "ORG-004564|ORG-000492", "ORG-006171": "ORG-006171|ORG-001148",
        "ORG-000119": "ORG-000119|ORG-007802", "ORG-002556": "ORG-002556|ORG-004886"}
WANT = {"ORG-002323": "SAME_ENTITY", "ORG-002384": "SAME_ENTITY", "ORG-001813": "SAME_ENTITY", "ORG-000484": "PLANT_OF",
        "ORG-000492": "PLANT_OF", "ORG-006171": "PLANT_OF", "ORG-000119": "B_PARENT_OF_A", "ORG-002556": "DIFFERENT"}


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(p, rows, header):
    eol = "\r\n" if p.exists() and b"\r\n" in p.read_bytes()[:4096] else "\n"
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
    D = {r["pair_id"]: r for r in read(HERE / "lanes/D_out.csv")}
    H = {r["record_id"]: r for r in read(HERE / "lanes/H_out.csv")}
    rawD = {r["pair_id"]: r["raw"] for r in read(HERE / "rawcheck_D.csv")}
    rawH = {r["record_id"]: r["raw"] for r in read(HERE / "rawcheck_H.csv")}
    shards = {f: read(f) for f in sorted(data.glob("organizations_*.csv"))}
    headers = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in shards}
    where = {r["org_id"]: f for f, rows in shards.items() for r in rows}
    org = {r["org_id"]: r for rows in shards.values() for r in rows}
    ev_files = {f: read(f) for f in sorted(data.glob("evidence_*.csv"))}
    ev_head = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in ev_files}
    eid = max(int(e["evidence_id"][4:]) for rows in ev_files.values() for e in rows if e["evidence_id"][4:].isdigit()) + 1
    rel = read(data / "relationships.csv"); rel_head = next(csv.reader(open(data / "relationships.csv", encoding="utf-8")))
    nrel = max(int(x["relationship_id"][4:]) for x in rel) + 1
    new_ev, log, touched, ev_touched = defaultdict(list), [], set(), set()

    def tag(oid):
        return where[oid].stem.split("_", 1)[1]

    def note(oid, text):
        org[oid]["notes"] = (org[oid]["notes"] + f" | {DATE}: {text}").strip(" |")
        org[oid]["last_verified"] = DATE
        touched.add(where[oid])

    def evid(table, rid, shard, claim, detail, src):
        nonlocal eid
        sc = src["source_class"].strip()
        assert sc in ("own_site", "government_filing", "press"), (rid, sc)
        new_ev[data / f"evidence_{table}_{shard}.csv"].append({
            "evidence_id": f"EVD-{eid:06d}", "record_table": table, "record_id": rid, "claim_type": claim,
            "claim_detail": f"{detail}: \"{src['quote'].strip()}\"", "source_class": sc, "source_ref": src["source_url"].strip(),
            "observed_date": DATE, "tier_effect": "supports_B" if sc == "press" else "supports_A", "created_by": BY,
            "notes": "dedupe/HQ pass 2 2026-11-04; quote re-fetched raw"})
        eid += 1

    def edge(frm, typ, to, owner, basis):
        nonlocal nrel
        rel.append({"relationship_id": f"REL-{nrel:06d}", "from_org_id": frm, "relationship_type": typ, "to_org_id": to,
                    "effective_from": org[owner]["status_date"] if typ == "successor_of" else "", "effective_to": "",
                    "basis": basis, "source_ref": f"organizations.csv: {owner}." + ("parent_org_id" if typ == "parent_of" else "successor_org_id + status"),
                    "created_by": BY, "notes": "dedupe/HQ pass 2 2026-11-04"})
        nrel += 1

    def pair_ok(oid):
        p = PAIR[oid]
        if D[p]["outcome"] != WANT[oid] or rawD.get(p) != "yes":
            log.append(f"HELD {oid}: lane outcome {D[p]['outcome']} / raw {rawD.get(p)}"); return None
        return D[p]

    # HQ moves
    for oid, (city, st, county) in HQ.items():
        f = H[oid]
        if not (f["verdict"].strip() == "CONFIRMED" and rawH.get(oid) == "yes" and f["proposed_value"].strip() == f"{city} {st}"):
            log.append(f"HELD {oid}: HQ finding not confirmed, not raw-verified, or not {city} {st}"); continue
        r = org[oid]
        old = (r["hq_city"], r["hq_state"])
        r.update(hq_city=city, hq_state=st, hq_county=county, hq_in_scope="national_us", hq_country="US")
        note(oid, f"HQ corrected {old[0]}, {old[1]} -> {city}, {st} per the company's own page ({f['item']}); the {old[0]} plant is unchanged.")
        old_f, new_f = where[oid], data / f"organizations_{st}.csv"
        if new_f != old_f:
            shards[old_f].remove(r); shards.setdefault(new_f, read(new_f)); headers.setdefault(new_f, headers[old_f])
            shards[new_f].append(r); shards[new_f].sort(key=lambda x: x["org_id"]); where[oid] = new_f; touched.add(new_f)
            old_e, new_e = data / f"evidence_organizations_{old_f.stem.split('_', 1)[1]}.csv", data / f"evidence_organizations_{st}.csv"
            moving = [e for e in ev_files.get(old_e, []) if e["record_id"] == oid]
            if moving:
                ev_files[old_e] = [e for e in ev_files[old_e] if e["record_id"] != oid]
                ev_files.setdefault(new_e, read(new_e)); ev_head.setdefault(new_e, ev_head[old_e]); ev_files[new_e] += moving
                ev_touched.update({old_e, new_e})  # both sides rewritten, or the moved rows would exist twice (V-22)
            log.append(f"MOVED {oid} {old_f.name} -> {new_f.name} with {len(moving)} evidence rows")
        evid("organizations", oid, st, "address", f"HQ {city}, {st}", f)
        log.append(f"HQ {oid} {r['legal_name']}: {old} -> {(city, st)}")
    # duplicate consolidations
    for dup, surv in MERGE.items():
        p = pair_ok(dup)
        if not p: continue
        assert org[dup]["status"] == "active" and org[surv]["status"] == "active" and not org[dup]["successor_org_id"], dup
        org[dup].update(status="merged", status_date=DATE, successor_org_id=surv)
        org[dup]["sources"] = (org[dup]["sources"] + "; " + p["source_url"]).strip("; ")
        note(dup, f"duplicate record consolidated into {surv} ({org[surv]['legal_name']}): {p['note'][:160]}")
        edge(dup, "merged_into", surv, dup, f"Generated from {dup}.successor_org_id with status=merged (canonical §4.4 columns), "
             "dedupe/HQ pass 2. Record lineage: a dedupe consolidation of duplicate records, not a corporate merger of two "
             "distinct companies (§4.14.2); the predecessor's status_date is the tombstone-pass date and is never restated "
             "as a corporate date, so effective_from is empty.")
        log.append(f"MERGE {dup} {org[dup]['legal_name']} -> {surv} {org[surv]['legal_name']}")
    # dated acquisitions
    for oid, (succ, when) in ACQ.items():
        p = pair_ok(oid)
        if not p: continue
        assert org[oid]["status"] == "active" and org[succ]["status"] == "active", oid
        org[oid].update(status="acquired", status_date=when, successor_org_id=succ)
        org[oid]["sources"] = (org[oid]["sources"] + "; " + p["source_url"]).strip("; ")
        note(oid, f"status acquired {when}, successor {succ} ({org[succ]['legal_name']}); the record is kept as a tombstone, and its sites stay linked historically." + ACQ_NOTE.get(oid, ""))
        edge(oid, "successor_of", succ, oid, f"Generated from {oid}.successor_org_id with status=acquired (canonical §4.4 columns); "
             "the column is the source of truth and this edge is its derived view (§4.14.2 single-source rule).")
        evid("organizations", oid, tag(oid), "parent", f"acquired by {succ} ({org[succ]['legal_name']}) on {when}", p)
        log.append(f"ACQ {oid} {org[oid]['legal_name']} -> {succ} on {when}")
    for oid, parent in PARENT.items():
        p = pair_ok(oid)
        if not p: continue
        assert not org[oid]["parent_org_id"].strip(), oid
        org[oid]["parent_org_id"] = parent
        note(oid, f"parent set to {parent} ({org[parent]['legal_name']}).")
        edge(parent, "parent_of", oid, oid, f"Generated from {oid}.parent_org_id (canonical §4.4 column); the column is the source "
             "of truth and this edge is its derived view (§4.14.2 single-source rule).")
        evid("organizations", oid, tag(oid), "parent", f"parent {parent} ({org[parent]['legal_name']})", p)
        log.append(f"PARENT {oid} -> {parent}")
    oid, succ, when, site, name = AMETEK
    p = pair_ok(oid)
    if p:
        # Council (2026-11-04): the record also holds Ametek's St. Louis plant (SITE-004583), so it is Ametek itself, not
        # the sold business. Only the sold plant moves; the org keeps its name and status, and its HQ is flagged.
        r = org[oid]
        assert r["status"] == "active" and r["legal_name"] == "Ametek", oid
        note(oid, f"the Nesquehoning plant {site} (Westchester Plastics) was sold to {succ} ({org[succ]['legal_name']}) on "
                  f"{when} and moves to that operator. This record's HQ (Nesquehoning, PA) came from that plant and is not "
                  "Ametek's HQ: a finding for the next HQ pass.")
        site_files = {f: read(f) for f in sorted(data.glob("sites_*.csv"))}
        hit = [(f, s) for f, rows in site_files.items() for s in rows if s["site_id"] == site]
        assert len(hit) == 1 and hit[0][1]["org_id"] == oid, site
        f, s = hit[0]
        s["org_id"] = succ
        s["notes"] = (s["notes"] + f" | {DATE}: operator corrected {oid} -> {succ} ({org[succ]['legal_name']}); Ametek sold the plant on {when}.").strip(" |")
        s["last_verified"] = DATE
        write(f, site_files[f], next(csv.reader(open(f, encoding="utf-8")))) if a.apply else None
        links = read(data / "registry_links.csv")
        moved = [l for l in links if l["site_id"] == site and l["org_id"] == oid]
        for l in moved:  # a facility-grain registry ID follows its site to the operator (V-6, R10)
            l["org_id"] = succ
        if a.apply and moved:
            write(data / "registry_links.csv", links, next(csv.reader(open(data / "registry_links.csv", encoding="utf-8"))))
        evid("sites", site, s["state"], "parent", f"operator {succ} ({org[succ]['legal_name']})", p)
        log.append(f"REGISTRY {len(moved)} facility link(s) on {site} -> {succ}")
        log.append(f"AMETEK {oid}: plant {site} (sold {when}) -> {succ}; org unchanged, HQ flagged")
    for oid, why in WATCH.items():
        assert org[oid]["monitor_watch"] == "false", oid
        org[oid]["monitor_watch"] = "true"
        note(oid, f"monitor_watch set: {why}; verified operating today by the 2026-11-04 state wave. Re-verify when the watch fires.")
        log.append(f"WATCH {oid} {org[oid]['legal_name']}")
    for oid, why in COUNCIL_HELD.items():
        log.append(f"HELD {oid} {org[oid]['legal_name']}: {why}")
    for pid, r in D.items():
        if not any(PAIR[k] == pid for k in PAIR):
            log.append(f"HELD pair {pid}: {r['outcome']} (raw {rawD.get(pid)}): {r['note'][:150]}")
    for rid, r in H.items():
        if rid not in HQ:
            log.append(f"KEPT/HELD HQ {rid} {r['item']}: {r['verdict']} {r['current_value']} -> {r['proposed_value']} (raw {rawH.get(rid)})")
    print("\n".join(log)); print(f"evidence rows {sum(len(v) for v in new_ev.values())}; relationship rows {nrel - 1 - max(int(x['relationship_id'][4:]) for x in read(data / 'relationships.csv'))}")
    (HERE / "journal.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    if a.apply:
        for f in touched:
            write(f, shards[f], headers[f])
        for p, rows in new_ev.items():
            ev_files.setdefault(p, read(p) if p.exists() else []); ev_head.setdefault(p, next(csv.reader(open(p, encoding="utf-8"))) if p.exists() else list(rows[0]))
            ev_files[p] += rows; ev_touched.add(p)
        for f in ev_touched:
            write(f, ev_files[f], ev_head[f])
        write(data / "relationships.csv", rel, rel_head)
        print("applied")


if __name__ == "__main__":
    main()
