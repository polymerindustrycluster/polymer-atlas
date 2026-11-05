#!/usr/bin/env python3
"""Integrator backlog 3 (2026-11-05): items left open by #122, #123 and #124, settled by one evidence lane
(`findings.csv`, every quote re-fetched raw and matched as a word sequence: `rawcheck.csv`).

    python3 tasks/integrator-backlog-3-2026-11-05/build.py --data-dir data [--apply --i-am-the-integrator]

Decisions, written per item:
- ACQ / MERGED: dated deals -> status, status_date, successor_org_id, the generated edge, a `parent` evidence row.
  Where only an announcement date exists it is used and noted (SCHEMA §5.4).
- DUP: one business recorded twice -> status=merged as record lineage (§4.14.2), the duplicate's name into the
  survivor's trade_names.
- HQ: same-state HQ corrections, with an `address` evidence row (no shard move).
- WEB: a domain that no longer serves the company is cleared (the old value kept in notes), or replaced by the
  company's current site when the lane established it.
Held items are listed in journal.txt.
"""
import argparse, csv, io, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY = "2026-11-05", "claude-code integrator-backlog-3-2026-11-05"
ACQ = {"pexco-perfplastics-date": ("ORG-001752", "acquired", "ORG-002534", ""),
       "johnsonite-date": ("ORG-001836", "acquired", "ORG-000131", " The date is the announcement date; no closing date was found."),
       "bway-date": ("ORG-006250", "merged", "ORG-000717", " BWAY and Mauser combined as Mauser Packaging Solutions (a corporate combination, not a record consolidation).")}
DUP = {}  # codex review 2026-11-05: KNF's shared premises and website do not prove one legal entity (AGENTS §3: when in doubt, do not merge)
HQ = {"ametek-hq": ("ORG-002556", "Berwyn", "PA", "Chester"), "clearlyclean-hq": ("ORG-002578", "Frackville", "PA", "Schuylkill")}
WEB_CLEAR = {"wbwagner-site": "ORG-002713", "hpe-site": "ORG-002203", "paddington-site": "ORG-000021"}
WEB_NEW = {"federalprocess-site": ("ORG-001812", "https://fpcintl.com/", "FPC International")}
# Two independent lanes (#124's capability lane and this one) saw these domains serve unrelated content; a cleared
# website asserts nothing about the company, so the clear does not wait on a raw-verified quote.
CLEAR_WITHOUT_RAW = {"paddington-site"}
HELD = {"84fairmount-plant": "quote not raw-verified again (the page renders by script)",
        "esschem-linwood": "the Linwood plant belongs to Esschem, Inc., a separate Justi Group company the Atlas does not hold; creating it needs its own evidence",
        "westfall-lasvegas": "Westfall no longer lists a Las Vegas location; that is not closure evidence for the held site",
        "ronaldmark-hq": "Hillside, NJ confirmed; no change",
        "knf-same": "held after codex review: one operation and address under both names, but no source states the two are one legal entity (a sister KNF Clean Room company exists)"}


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
    F = {r["item"]: r for r in read(HERE / "findings.csv")}
    raw = {r["item"]: r["raw"] for r in read(HERE / "rawcheck.csv")}
    shards = {f: read(f) for f in sorted(data.glob("organizations_*.csv"))}
    headers = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in shards}
    where = {r["org_id"]: f for f, rows in shards.items() for r in rows}
    org = {r["org_id"]: r for rows in shards.values() for r in rows}
    ev_files = {f: read(f) for f in sorted(data.glob("evidence_*.csv"))}
    eid = max(int(e["evidence_id"][4:]) for rows in ev_files.values() for e in rows if e["evidence_id"][4:].isdigit()) + 1
    rel = read(data / "relationships.csv"); rel_head = next(csv.reader(open(data / "relationships.csv", encoding="utf-8")))
    nrel = max(int(x["relationship_id"][4:]) for x in rel) + 1
    new_ev, log, touched = defaultdict(list), [], set()

    def note(oid, text):
        org[oid]["notes"] = (org[oid]["notes"] + f" | {DATE}: {text}").strip(" |")
        org[oid]["last_verified"] = DATE
        touched.add(where[oid])

    def evid(oid, claim, detail, f):
        nonlocal eid
        sc = f["source_class"].strip()
        assert sc in ("own_site", "government_filing", "press"), (oid, sc)
        new_ev[where[oid].stem.split("_", 1)[1]].append({
            "evidence_id": f"EVD-{eid:06d}", "record_table": "organizations", "record_id": oid, "claim_type": claim,
            "claim_detail": f"{detail}: \"{f['quote'].strip()}\"", "source_class": sc, "source_ref": f["source_url"].strip(),
            "observed_date": DATE, "tier_effect": "supports_B" if sc == "press" else "supports_A", "created_by": BY,
            "notes": f"integrator backlog 3 ({f['item']}); quote re-fetched raw; source dated {f['source_date'] or 'n/a'}"})
        eid += 1

    def edge(frm, typ, to, basis, eff=""):
        nonlocal nrel
        rel.append({"relationship_id": f"REL-{nrel:06d}", "from_org_id": frm, "relationship_type": typ, "to_org_id": to,
                    "effective_from": eff, "effective_to": "", "basis": basis,
                    "source_ref": f"organizations.csv: {frm}.successor_org_id + status", "created_by": BY,
                    "notes": "integrator backlog 3 2026-11-05"})
        nrel += 1

    def ok(item):
        if raw.get(item) != "yes":
            log.append(f"HELD {item}: quote not raw-verified ({raw.get(item)})"); return None
        return F[item]

    for item, (oid, status, succ, extra) in ACQ.items():
        f = ok(item)
        if not f: continue
        when = f["proposed_value"].strip()
        assert len(when) == 10 and org[oid]["status"] == "active" and org[succ]["status"] == "active", item
        org[oid].update(status=status, status_date=when, successor_org_id=succ)
        org[oid]["sources"] = (org[oid]["sources"] + "; " + f["source_url"]).strip("; ")
        note(oid, f"status {status} {when}, successor {succ} ({org[succ]['legal_name']}); the record is kept as a tombstone, and its sites stay linked historically.{extra}")
        typ = "successor_of" if status == "acquired" else "merged_into"
        edge(oid, typ, succ, f"Generated from {oid}.successor_org_id with status={status} (canonical §4.4 columns); the column is "
             "the source of truth and this edge is its derived view (§4.14.2 single-source rule).", when if status == "acquired" else "")
        evid(oid, "parent", f"{status} into {succ} ({org[succ]['legal_name']}) on {when}", f)
        log.append(f"{status.upper()} {oid} {org[oid]['legal_name']} -> {succ} on {when}")
    for item, (dup, surv, alias) in DUP.items():
        f = ok(item)
        if not f: continue
        assert org[dup]["status"] == "active" and org[surv]["status"] == "active", item
        org[dup].update(status="merged", status_date=DATE, successor_org_id=surv)
        note(dup, f"duplicate record consolidated into {surv} ({org[surv]['legal_name']}): same operation and address, 734 West Penn Pike, Tamaqua, PA.")
        names = [t for t in org[surv]["trade_names"].split(";") if t.strip()]
        if alias not in names:
            org[surv]["trade_names"] = ";".join(names + [alias]); note(surv, f"trade name {alias} added (duplicate {dup} consolidated here).")
        edge(dup, "merged_into", surv, f"Generated from {dup}.successor_org_id with status=merged (canonical §4.4 columns), integrator "
             "backlog 3. Record lineage: a dedupe consolidation of duplicate records, not a corporate merger of two distinct "
             "companies (§4.14.2); the predecessor's status_date is the tombstone-pass date, so effective_from is empty.")
        evid(surv, "existence", f"{alias} is this company", f)
        log.append(f"DUP {dup} -> {surv}")
    for item, (oid, city, st, county) in HQ.items():
        f = ok(item)
        if not f: continue
        assert f["proposed_value"].strip() == f"{city} {st}" and org[oid]["hq_state"] == st, item
        old = (org[oid]["hq_city"], org[oid]["hq_county"])
        org[oid].update(hq_city=city, hq_county=county)
        note(oid, f"HQ corrected {old[0]}, {st} -> {city}, {st} per the company's own page; the {old[0]} location is unchanged as a site if held.")
        evid(oid, "address", f"HQ {city}, {st}", f)
        log.append(f"HQ {oid} {org[oid]['legal_name']}: {old[0]} -> {city}")
    for item, oid in WEB_CLEAR.items():
        f = F[item]
        if raw.get(item) != "yes" and item not in CLEAR_WITHOUT_RAW:
            log.append(f"HELD {item}: quote not raw-verified"); continue
        assert f["proposed_value"].strip() == "NONE", item
        old = org[oid]["website"]
        org[oid]["website"] = ""
        note(oid, f"website field cleared (hygiene): {old} no longer serves the company ({f['note'][:120]}).")
        log.append(f"WEB CLEAR {oid} {org[oid]['legal_name']}: {old}")
    for item, (oid, new, alias) in WEB_NEW.items():
        f = ok(item)
        if not f: continue
        old = org[oid]["website"]
        org[oid]["website"] = new
        names = [t for t in org[oid]["trade_names"].split(";") if t.strip()]
        if alias not in names: org[oid]["trade_names"] = ";".join(names + [alias])
        note(oid, f"website {old} -> {new}: the company now trades as {alias}.")
        evid(oid, "existence", f"website {new} ({alias})", f)
        log.append(f"WEB NEW {oid}: {old} -> {new}")
    for item, why in HELD.items():
        log.append(f"HELD {item}: {why}")
    print("\n".join(log)); print(f"evidence rows {sum(len(v) for v in new_ev.values())}")
    (HERE / "journal.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    if a.apply:
        for f in touched:
            write(f, shards[f], headers[f])
        for tag, rows in new_ev.items():
            p = data / f"evidence_organizations_{tag}.csv"
            write(p, read(p) + rows, next(csv.reader(open(p, encoding="utf-8"))))
        write(data / "relationships.csv", rel, rel_head)
        print("applied")


if __name__ == "__main__":
    main()
