#!/usr/bin/env python3
"""Ownership and status, round 2 (2026-11-05). Reused from tasks/ownership-status-2026-11-04/build.py: the hygiene and
group-domain steps are dropped and the decision maps are replaced.

    python3 tasks/ownership-status-2-2026-11-05/build.py --data-dir data [--apply --i-am-the-integrator]

Inputs: `lanes/O3..O6_out.csv` (four research lanes over `lead_pool_2.csv`, 136 organizations), `rawcheck.csv`
(every lane quote re-fetched raw, word-sequence match).
An ownership change is applied only when its lane quote is raw-verified and the integrator decision below names it.
Decisions are written out per org, so the rule for each is in one place:
- PARENT: still operates under its own name, owned by a held org -> `parent_org_id` + its generated `parent_of` edge.
- ULT: owned by an org the Atlas does not hold -> `ultimate_parent_name`.
- ACQ: bought and folded into a held org (asset purchase) -> `status=acquired`, `status_date`, `successor_org_id` and
  the generated `successor_of` edge. The record is never deleted (AGENTS.md §3).
- WEB: the lane established the business's current own site, and the quote is from that site.
- TRADE: a new brand for the same business goes into `trade_names` (the legal name is not changed).
- CONFIRM: the Atlas already has the parent; an evidence row is added.
Every applied change gets one evidence row carrying the lane quote (`parent` for ownership, `existence` for websites).
Held rows and their reasons are printed and written to `journal.txt`.
"""
import argparse, csv, io, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY = "2026-11-05", "claude-code ownership-status-2-2026-11-05"
# Immediate owner held in the Atlas, quote naming both parties.
PARENT = {"ORG-004082": "ORG-003922", "ORG-002692": "ORG-004243", "ORG-004045": "ORG-007026",
          "ORG-004567": "ORG-004606"}
# Owner not held; only where ultimate_parent_name is empty and the buyer is the top of its chain.
ULT = {"ORG-002992": "CHT Group", "ORG-002355": "RG Group", "ORG-004267": "Wynnchurch Capital", "ORG-004067": "Karman Space & Defense",
       "ORG-004076": "MacLean Investment Partners", "ORG-002144": "AeroVironment, Inc.", "ORG-002618": "Keter Group",
       "ORG-002171": "Carlisle Companies Inc.", "ORG-003979": "ENEOS Holdings, Inc."}
ACQ = {}
# Website fills for records whose non-site value #122/#126 cleared, and same-business domain migrations or rebrands. A
# US subsidiary's site swapped for a foreign parent's group site is not applied.
WEB = {"ORG-004084", "ORG-002487", "ORG-002726", "ORG-004083", "ORG-004079", "ORG-004065", "ORG-002690", "ORG-002729", "ORG-004069",
       "ORG-004085", "ORG-002249", "ORG-002004", "ORG-002404",
       "ORG-001908", "ORG-002066", "ORG-003348", "ORG-003480", "ORG-003859", "ORG-004001", "ORG-004161", "ORG-004274", "ORG-004570",
       "ORG-002312", "ORG-003671", "ORG-003908", "ORG-004581", "ORG-002886", "ORG-003186", "ORG-003373", "ORG-003502", "ORG-004073",
       "ORG-001992", "ORG-002204", "ORG-002898", "ORG-003335", "ORG-003515", "ORG-003850", "ORG-003167", "ORG-004606"}
# Cross-family refute (grok + codex, deep, 2026-11-04) of the first build: rows whose quote does not carry the
# specific change are held. `parent_org_id` records ownership, so a completed-acquisition quote supports it (Foster,
# dlhBOWLES, Berry); a facility, brand-bundle or division-transfer quote does not.
COUNCIL_HELD = {}  # filled after the cross-family review
TRADE = {"ORG-003348": "Resilient Structures", "ORG-003167": "UPM Adhesive Materials", "ORG-004606": "APN Performance Coatings"}
CONFIRM = set()
HELD = {
    "ORG-002203": "Pexco bought HPE (2019), but the only quote is Plastics News, a licensed source usable as a lead only (AGENTS.md §5)",
    "ORG-003117": "the lane names Georg Fischer Corp.; the held GF record (ORG-002291, GF Harvel) may be a sibling, not the parent",
    "ORG-003701": "the quote is about Brückner buying the Hennecke Group; it does not name the Bridgeville entity",
    "ORG-003704": "quote not raw-verified (Sur-Seal)",
    "ORG-004356": "quote not raw-verified (Atlantic Footcare)",
    "ORG-004621": "rebranded National Manufacturing Group, which the Atlas already holds as ORG-007026: a duplicate for the dedupe pass",
    "ORG-001993": "absorbed into Kreate, which matches two held records (ORG-001568, ORG-001842); resolve which first",
    "ORG-002038": "absorbed into Rumpke, which the Atlas does not hold",
    "ORG-004364": "absorbed into Wolf Home Products, which the Atlas does not hold",
    "ORG-002013": "absorbed into Kodiak Chemical, which the Atlas does not hold",
    "ORG-002040": "absorbed into StockPKG (Omaha), which the Atlas does not hold",
    "ORG-002020": "Beacon Industries bought the Rossford coatings facility; whether Electro Prime itself survives is open",
    "ORG-004230": "NuSil continues as an Avantor company; ultimate parent already Avantor, Inc.",
    "ORG-003328": "the quote is Patrick Industries buying the parent (Leisure Product Enterprises); the layers' dates differ",
    "ORG-004160": "2020 buyer quoted, but a 2024 report says the plant changed hands again",
    "ORG-003462": "Novamont is itself owned by Versalis (Eni), so it is not the ultimate parent",
    "ORG-003430": "Thiele Technologies is itself owned by Barry-Wehmiller, so it is not the ultimate parent",
    "ORG-004604": "Profile Products' own ownership was not checked, so the ultimate parent is open",
    "ORG-004066": "the immediate buyer is Holcim Building Envelope; the ultimate parent (Holcim) was not quoted",
    "ORG-001974": "the site carries injected gambling spam; possibly compromised, so not used",
    "ORG-002687": "dropstirs.com product site; whether it is Medical Precision Plastics' own site is unconfirmed",
}
GROUP_DOMAIN = []
LICENSED = re.compile(r"plasticsnews\.com|rubbernews\.com|dnb\.com|zoominfo\.com|data-axle\.com|dataaxle\.com", re.I)
DIRECT = re.compile(r"linkedin\.com", re.I)  # a social post is not the company's own site: press ceiling


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(p, rows, header):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


def dom(u):
    return re.sub(r"^(https?://)?(www\.|mail\.)?", "", (u or "").strip().lower()).split("/")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    if a.apply and data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
        sys.exit("editing the real data/ is integrator work; pass --i-am-the-integrator")
    lane = {r["org_id"]: r for f in sorted(HERE.glob("lanes/O*_out.csv")) for r in read(f)}
    raw = {r["org_id"]: r["raw"] for r in read(HERE / "rawcheck.csv")}
    shards = {f: read(f) for f in sorted(data.glob("organizations_*.csv"))}
    headers = {f: next(csv.reader(open(f, encoding="utf-8"))) for f in shards}
    where = {r["org_id"]: f for f, rows in shards.items() for r in rows}
    org = {r["org_id"]: r for rows in shards.values() for r in rows}
    held_dom = defaultdict(set)
    for oid, r in org.items():
        if dom(r["website"]):
            held_dom[dom(r["website"])].add(oid)
    ev_all = [e for f in sorted(data.glob("evidence*.csv")) for e in read(f)]
    eid = max(int(e["evidence_id"][4:]) for e in ev_all if e["evidence_id"][4:].isdigit()) + 1  # AGENTS §3: above the max
    ev_head = list(ev_all[0].keys())
    new_ev, log = defaultdict(list), []
    rel = read(data / "relationships.csv"); rel_head = next(csv.reader(open(data / "relationships.csv", encoding="utf-8")))
    nrel = max(int(x["relationship_id"][4:]) for x in rel) + 1

    def note(oid, text):
        r = org[oid]
        r["notes"] = (r["notes"] + f" | {DATE}: {text}").strip(" |")

    def evid(oid, claim, detail):
        nonlocal eid
        L = lane[oid]
        sc = "press" if DIRECT.search(L["source_url"]) else L["source_class"].strip()
        assert sc in ("own_site", "government_filing", "press"), (oid, sc)
        new_ev[where[oid].stem.split("_", 1)[1]].append({
            "evidence_id": f"EVD-{eid:06d}", "record_table": "organizations", "record_id": oid, "claim_type": claim,
            "claim_detail": f"{detail}: \"{L['quote'].strip()}\"", "source_class": sc, "source_ref": L["source_url"].strip(),
            "observed_date": DATE, "tier_effect": "supports_B" if sc == "press" else "supports_A", "created_by": BY,
            "notes": f"ownership-status pilot 2026-11-04; lane outcome {L['outcome']}, event date {L['event_date'] or 'n/a'}; quote re-fetched raw"})
        eid += 1

    def gen_edge(frm, typ, to, col_owner, col):
        nonlocal nrel
        rel.append({"relationship_id": f"REL-{nrel:06d}", "from_org_id": frm, "relationship_type": typ, "to_org_id": to,
                    "effective_from": org[col_owner]["status_date"] if typ == "successor_of" else "",
                    "basis": f"Generated from {col_owner}.{col} (canonical §4.4 column); the column is the source of truth and this edge is its derived view (§4.14.2 single-source rule).",
                    "source_ref": f"organizations.csv: {col_owner}.{col}", "created_by": BY, "notes": "ownership-status pilot 2026-11-04"})
        nrel += 1

    def ready(oid):
        if raw.get(oid) != "yes":
            log.append(f"HELD {oid}: quote not raw-verified ({raw.get(oid)})"); return False
        if LICENSED.search(lane[oid]["source_url"]):  # AGENTS.md §5: licensed sources are leads only, never cited
            log.append(f"HELD {oid}: source is a licensed publication ({lane[oid]['source_url'][:60]})"); return False
        return True

    for oid, parent in PARENT.items():
        r = org[oid]
        if not ready(oid): continue
        assert not r["parent_org_id"].strip() and parent in org and parent != oid, (oid, r["parent_org_id"])
        r["parent_org_id"], r["last_verified"] = parent, DATE
        gen_edge(parent, "parent_of", oid, oid, "parent_org_id")
        note(oid, f"parent set to {parent} ({org[parent]['legal_name']}), ownership-status pilot.")
        evid(oid, "parent", f"parent {parent} ({org[parent]['legal_name']})")
        log.append(f"PARENT {oid} {r['legal_name']} -> {parent} {org[parent]['legal_name']}")
    for oid, name in ULT.items():
        r = org[oid]
        if not ready(oid): continue
        if r["ultimate_parent_name"].strip() == name:
            log.append(f"SKIP {oid}: ultimate parent already {name}"); continue
        old = r["ultimate_parent_name"]
        r["ultimate_parent_name"], r["last_verified"] = name, DATE
        note(oid, f"ultimate parent {old or '(blank)'} -> {name}, ownership-status pilot.")
        evid(oid, "parent", f"ultimate parent {name}")
        log.append(f"ULT {oid} {r['legal_name']}: {old!r} -> {name!r}")
    for oid, (succ, when) in ACQ.items():
        r = org[oid]
        if not ready(oid): continue
        assert r["status"] == "active" and succ in org and lane[oid]["event_date"] == when, oid
        r["status"], r["status_date"], r["successor_org_id"], r["last_verified"] = "acquired", when, succ, DATE
        r["sources"] = (r["sources"] + "; " + lane[oid]["source_url"]).strip("; ")
        gen_edge(oid, "successor_of", succ, oid, "successor_org_id")
        note(oid, f"status acquired {when}, successor {succ} ({org[succ]['legal_name']}); the record is kept as a tombstone, "
                  "and its sites stay linked historically until the successor's site linkage is reviewed.")
        evid(oid, "parent", f"acquired by {succ} ({org[succ]['legal_name']}) on {when}")
        log.append(f"ACQ {oid} {r['legal_name']} -> {succ} on {when}")
    for oid in sorted(WEB):
        r, L = org[oid], lane[oid]
        if not ready(oid): continue
        new, d = L["new_website"].strip(), dom(L["new_website"])
        if dom(L["source_url"]) != d:
            log.append(f"HELD {oid}: quote is not from the new site"); continue
        if held_dom.get(d, set()) - {oid}:
            log.append(f"HELD {oid}: {d} already held by {sorted(held_dom[d] - {oid})} (possible duplicate)"); continue
        if dom(r["website"]) == d:
            log.append(f"SKIP {oid}: website already {d}"); continue
        old = r["website"]
        r["website"], r["last_verified"] = f"https://{d}/", DATE
        held_dom[d].add(oid)
        note(oid, f"website {old or '(blank)'} -> https://{d}/ (ownership-status pilot: the old domain redirected or was empty).")
        evid(oid, "existence", f"website https://{d}/")
        log.append(f"WEB {oid} {r['legal_name']}: {old or '(blank)'} -> https://{d}/")
    for oid, name in TRADE.items():
        r = org[oid]
        if not ready(oid): continue
        names = [t.strip() for t in r["trade_names"].split(";") if t.strip()]
        if name not in names:
            r["trade_names"] = ";".join(names + [name])
            log.append(f"TRADE {oid}: + {name}")
    for oid in sorted(CONFIRM):
        if not ready(oid): continue
        evid(oid, "parent", f"parent {org[oid]['parent_org_id']} ({org[org[oid]['parent_org_id']]['legal_name']})")
        log.append(f"CONFIRM {oid}: parent {org[oid]['parent_org_id']} evidence row")
    for oid, why in {**HELD, **COUNCIL_HELD}.items():
        log.append(f"HELD {oid} {org[oid]['legal_name']}: {why}")
    for h in (read(HERE / "website_hygiene.csv") if (HERE / "website_hygiene.csv").exists() else []):  # round 1 only
        oid, act, why = h["org_id"], h["action"], h["reason"]
        r = org[oid]
        old = r["website"]
        if act == "CLEAR":
            r["website"] = ""
            note(oid, f"website field cleared (hygiene): it held {why}, not the organization's own site: {old}")
        elif act == "ROOT":
            d = dom(old)
            assert "." in d and " " not in d, (oid, old)
            r["website"] = f"https://{d}/"
            note(oid, f"website trimmed to the root domain (hygiene): it held an {why}: {old}")
        elif act == "FLAG":
            note(oid, f"website check needed (hygiene): {why}.")
        else:
            raise SystemExit(f"unknown hygiene action {act}")
        log.append(f"HYGIENE {act} {oid}: {old[:70]!r} -> {r['website']!r}")
    for oid in GROUP_DOMAIN:
        note(oid, "website is the corporate group's domain, not a plant-specific site (owner ruling 2026-11-04: allowed, flagged).")
        log.append(f"GROUPFLAG {oid} {org[oid]['legal_name']}: {org[oid]['website']}")
    print("\n".join(log)); print(f"evidence rows {sum(len(v) for v in new_ev.values())}; relationship rows added {nrel - 1 - max(int(x['relationship_id'][4:]) for x in read(data / 'relationships.csv'))}")
    (HERE / "journal.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    if a.apply:
        for f, rows in shards.items():
            write(f, rows, headers[f])
        for tag, rows in new_ev.items():
            p = data / f"evidence_organizations_{tag}.csv"
            write(p, (read(p) if p.exists() else []) + rows, next(csv.reader(open(p, encoding="utf-8"))) if p.exists() else ev_head)
        write(data / "relationships.csv", rel, rel_head)
        print("applied")


if __name__ == "__main__":
    main()
