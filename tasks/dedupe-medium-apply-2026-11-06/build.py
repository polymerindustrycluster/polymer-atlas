#!/usr/bin/env python3
"""Apply the merged #254 verdicts (tasks/dedupe-medium-2026-11-06) to data/. Idempotent builder.

    python3 tasks/dedupe-medium-apply-2026-11-06/build.py [--data-dir data] [--dry-run]

Scope (controller task, integrator designation): the `to_apply` org folds, site folds and repoint_site actions of the
packet, minus the held cluster(s) in HOLD. Nothing else: the 9 hold_operator rows and the 2 STILL_UNCERTAIN org questions
(Carlisle, Jushi) are untouched. Rules (AGENTS §3, §4): never delete a record.
- Org fold: the absorbed org gets status=merged, status_date, a source, successor_org_id = survivor; its sites move to the
  survivor; its generated `merged_into` edge is appended to relationships.csv from the canonical columns (V-27 parity);
  no hand-authored edge.
- Site fold: the duplicate site row is tombstoned in place (operating_status=closed, a note naming the surviving site,
  pass-16 Tredegar precedent); the survivor keeps its id and gets a note naming the absorbed row.
- Repoint: site org_id moves to the operator, with a `parent` evidence row (EVD-333000..333999) citing the operator fact and
  the old org named in notes. A moved site's capability rows (V-31) and facility-grain registry links (V-6, R10) follow it.
Re-running on an applied tree changes nothing. When main moves, check out main's data files and re-run (never hand-merge).
"""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from shard_io import append_sorted  # noqa: E402

csv.field_size_limit(10 ** 9)
PACKET = ROOT / "tasks/dedupe-medium-2026-11-06"
DATE = "2026-11-06"
BY = "claude-code dedupe-medium-apply-2026-11-06"
EVD_FIRST = 333000
REL_FIRST = 470          # REL-000460..469 were allocated to the backlog sweep (BOARD 2026-11-06 10:35)

# Held after the registry check (see README "Holds"): cluster -> reason. The cluster's org fold and its repoint are skipped.
HOLD = {
    "SND-0101": "GLEIF lists U.S. Farathane Corporation (Michigan, LEI 549300P7GW6TNUHX2L07, entity-supplied, registration "
                "lapsed 2014) and U.S. Farathane, LLC (Delaware file 5360808, formed 2013-07-02, LEI 549300HLVY1RVM0MPI20, "
                "fully corroborated, active) as separate legal entities; no conversion record. Not settled, so no fold.",
}

# Evidence witnesses per repointed site, in row order. frs = EPA FRS REST row (raw/frs_<id>.json); press = cached page.
WITNESS = {
    "SITE-002964": [("frs", "110000386494")], "SITE-002968": [("frs", "110000386029")],
    "SITE-002962": [("frs", "110070207889")], "SITE-002965": [("frs", "110000388937")],
    "SITE-000168": [("frs", "110000386920")], "SITE-001530": [("frs", "110000387554")],
    "SITE-006423": [("frs", "110071944474")],
    "SITE-003477": [("frs", "110009662855"), ("press", "floordaily")],
    "SITE-003478": [("frs", "110000385244"), ("press", "floordaily")],
    "SITE-002868": [("press", "gemspring"), ("press", "goodyear")],
    "SITE-002870": [("press", "gemspring"), ("press", "goodyear")],
}
PRESS = {  # key -> (url, source_class, quote, what it dates)
    "floordaily": ("https://www.floordaily.net/flooring-news/tarkett-announces-acquisition-of-johnsonite/", "press",
                   "Tarkett announced the acquisition of Johnsonite of Chagrin Falls, OH", "Tarkett acquired Johnsonite (announced 2005-12-08)"),
    "gemspring": ("https://www.gemspring.com/gemspring-capital-completes-acquisition-of-the-goodyear-tire-rubber-companys-polymer-chemicals-business", "press",
                  "The acquisition includes two manufacturing plants in Houston and Beaumont, Texas",
                  "a Gemspring affiliate completed the acquisition of Goodyear's polymer chemicals business on 2025-11-03"),
    "goodyear": ("https://news.goodyear.com/2025-11-03-Goodyear-Completes-Divestiture-of-Chemical-Business", "press",
                 "effective Oct. 31, 2025", "the Goodyear Chemical divestiture to a Gemspring affiliate was effective 2025-10-31"),
}
BASIS_TEXT = {"shared_frs_id": "same EPA FRS id", "same_street": "same street address", "street_variant": "same street, spelling variant",
              "same_city_streetless": "the operator's one plant in that city"}
ORG_WHY = {
    "ORG-005115": "same legal name, HQ and website (dpcpipe.com): one corporation recorded twice",
    "ORG-001792": "Crown Foam Technologies is a brand division of Ludlow Composites at the same address (2100 Commerce Drive); the company's own history page says Ludlow is the parent name",
}
ORG_SOURCE = {
    "ORG-005115": "https://www.dpcpipe.com/ (Diamond Plastics Corporation, 1212 Johnstown Road, Grand Island NE; read 2026-11-06)",
    "ORG-001792": "https://www.ludlowcomp.com/about-ludlow-composites (Crown Foam Technologies is a division; Ludlow is the parent name; read 2026-11-06)",
}
CARRY_TRADE = {"ORG-000937": "Crown Foam Technologies"}   # division name carried to the surviving org (B-ALIAS)


PERSIST = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/dedupe-medium-apply-2026-11-06")
SOURCES = [  # (id, url, cached text file, quote): pages cited by evidence rows and org sources; quotes re-checked raw by check.py
    ("S1", PRESS["floordaily"][0], "floordaily-johnsonite.txt", PRESS["floordaily"][2]),
    ("S2", PRESS["gemspring"][0], "gemspring-pr.txt", PRESS["gemspring"][2]),
    ("S3", PRESS["goodyear"][0], "goodyear-divest.txt", PRESS["goodyear"][2]),
    ("S4", "https://www.ludlowcomp.com/about-ludlow-composites", "ludlow-about.txt",
     "began operating the Ludlow name as the parent company"),
    ("S5", "https://www.dpcpipe.com/", "dpc-home.txt", "Diamond Plastics Corporation 1212 Johnstown Road Grand Island, NE 68803"),
]


def write_sources():
    import hashlib
    with open(HERE / "sources.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "url", "file", "sha256", "retrieved", "quote"])
        for sid, url, fn, quote in SOURCES:
            f = PERSIST / fn
            if not f.exists():
                sys.exit(f"missing cached page {f}")
            w.writerow([sid, url, fn, hashlib.sha256(f.read_bytes()).hexdigest(), DATE, quote])


def read_rows(p):
    raw = Path(p).read_bytes().decode("utf-8")
    rdr = csv.DictReader(io.StringIO(raw, newline=""))
    return list(rdr), rdr.fieldnames, ("\r\n" if "\r\n" in raw[:4096] else "\n"), raw


def write_rows(p, rows, header, eol):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator=eol, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    Path(p).write_bytes(buf.getvalue().encode("utf-8"))


def add_note(row, text):
    row["notes"] = (row.get("notes", "") + f" | {DATE}: {text}").strip(" |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-journal", action="store_true", help="used by check.py's idempotence test on a temp copy")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    log = []

    pairs, _, _, _ = read_rows(PACKET / "pairs.csv")
    acts, _, _, _ = read_rows(PACKET / "operator_actions.csv")
    org_folds = [p for p in pairs if p["level"] == "org" and p["verdict"] == "DUPLICATE_OF" and p["state"] == "to_apply" and p["cluster"] not in HOLD]
    site_folds = [p for p in pairs if p["level"] == "site" and p["verdict"] == "DUPLICATE_OF" and p["state"] == "to_apply" and p["cluster"] not in HOLD]
    repoints = [x for x in acts if x["action"] == "repoint_site" and x["state"] == "to_apply" and x["cluster"] not in HOLD]
    for c, why in HOLD.items():
        log.append(f"HOLD {c}: {why}")

    # ---- load tables (round-trip is byte-identical for every file we may rewrite; verified below)
    files = {}

    def load(path):
        path = Path(path)
        if path not in files:
            rows, header, eol, raw = read_rows(path)
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=header, lineterminator=eol, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
            if buf.getvalue() != raw:
                sys.exit(f"{path.name}: csv round trip is not byte-identical; refusing to rewrite it")
            files[path] = dict(rows=rows, header=header, eol=eol, dirty=False)
        return files[path]

    org_by, org_file, site_by, site_file = {}, {}, {}, {}
    for f in sorted(data.glob("organizations_*.csv")):
        for r in load(f)["rows"]:
            org_by[r["org_id"]], org_file[r["org_id"]] = r, f
    for f in sorted(data.glob("sites_*.csv")):
        for r in load(f)["rows"]:
            site_by[r["site_id"]], site_file[r["site_id"]] = r, f
    caps, links = load(data / "site_capabilities.csv"), load(data / "registry_links.csv")
    rels = load(data / "relationships.csv")

    def touch(f):
        files[f]["dirty"] = True

    # ---- org folds
    new_rel, moved_sites, link_moves = [], {}, []
    existing_edges = {(r["from_org_id"], r["relationship_type"], r["to_org_id"]) for r in rels["rows"]}
    for p in org_folds:
        dup = p["record_b"] if p["survivor"] == p["record_a"] else p["record_a"]
        surv = p["survivor"]
        d, s = org_by[dup], org_by[surv]
        if d["status"] == "merged" and d["successor_org_id"] == surv:
            log.append(f"SKIP (applied) org fold {dup} -> {surv}")
        else:
            assert d["status"] == "active" and not d["successor_org_id"] and s["status"] == "active", (dup, surv)
            d.update(status="merged", status_date=DATE, successor_org_id=surv, last_verified=DATE)
            d["sources"] = (d["sources"] + "; " + ORG_SOURCE[dup]).strip("; ")
            add_note(d, f"duplicate record consolidated into {surv} ({s['legal_name']}): {ORG_WHY[dup]}. Kept as a tombstone, never deleted; "
                        f"its sites move to the survivor (dedupe-medium apply, PR #254 verdict {p['cluster']}).")
            add_note(s, f"absorbs duplicate record {dup} ({d['legal_name']}) (dedupe-medium apply, PR #254 verdict {p['cluster']}).")
            s["last_verified"] = DATE
            if surv in CARRY_TRADE:
                tn = [t for t in s["trade_names"].split(";") if t.strip()]
                if CARRY_TRADE[surv] not in [t.strip() for t in tn]:
                    s["trade_names"] = "; ".join(tn + [CARRY_TRADE[surv]])
            touch(org_file[dup])
            touch(org_file[surv])
            log.append(f"ORG FOLD {dup} {d['legal_name']} -> {surv} {s['legal_name']}")
        if (dup, "merged_into", surv) not in existing_edges:
            new_rel.append({"relationship_id": "", "from_org_id": dup, "relationship_type": "merged_into", "to_org_id": surv,
                            "effective_from": "", "effective_to": "",
                            "basis": f"Generated from {dup}.successor_org_id with status=merged (canonical §4.4 columns), dedupe-medium apply. "
                                     "Record lineage: a dedupe consolidation of duplicate records, not a corporate merger of two distinct companies "
                                     "(§4.14.2); the predecessor's status_date is the tombstone-pass date and is never restated as a corporate date, "
                                     "so effective_from is empty.",
                            "source_ref": f"organizations.csv: {dup}.successor_org_id + status", "created_by": BY,
                            "notes": f"dedupe-medium apply {DATE} (PR #254 verdict {p['cluster']})"})
        for sid, sr in site_by.items():
            if sr["org_id"] == dup:
                moved_sites[sid] = (dup, surv)

    # ---- repoints (target of every repoint action) and absorbed-org sites
    for x in repoints:
        moved_sites[x["record"]] = (site_by[x["record"]]["org_id"] if x["record"] not in moved_sites else moved_sites[x["record"]][0], x["target"])
    for sid, (old, new) in sorted(moved_sites.items()):
        r = site_by[sid]
        if r["org_id"] == new:
            log.append(f"SKIP (applied) move {sid} -> {new}")
            continue
        assert r["org_id"] == old, (sid, r["org_id"], old)
        r["org_id"] = new
        add_note(r, f"operator corrected {old} ({org_by[old]['legal_name']}) -> {new} ({org_by[new]['legal_name']}) (dedupe-medium apply, PR #254).")
        r["last_verified"] = DATE
        touch(site_file[sid])
        for c in caps["rows"]:
            if c["site_id"] == sid:
                assert c["org_id"] == old, c["capability_id"]
                c["org_id"] = new
                touch(data / "site_capabilities.csv")
        for l in links["rows"]:
            if l["site_id"] == sid:
                assert l["org_id"] == old, (sid, l)
                link_moves.append((f"{l['org_id']}|{l['registry']}|{l['registry_id']}|{l['site_id']}", new))
                l["org_id"] = new          # facility-grain registry ID follows its site to the operator (V-6, R10)
                touch(data / "registry_links.csv")
        log.append(f"MOVE {sid} {old} -> {new}")

    # ---- site folds
    for p in site_folds:
        dup = p["record_b"] if p["survivor"] == p["record_a"] else p["record_a"]
        surv = p["survivor"]
        d, s = site_by[dup], site_by[surv]
        if d["operating_status"] == "closed" and f"duplicate of {surv}" in d["notes"]:
            log.append(f"SKIP (applied) site fold {dup} -> {surv}")
            continue
        assert d["operating_status"] != "closed" and not any(l["site_id"] == dup for l in links["rows"]), dup
        was = d["operating_status"]
        bt = BASIS_TEXT[p["basis"]]
        add_note(d, f"RETIRED (dedupe-medium apply, PR #254 verdict {p['cluster']}): duplicate of {surv} ({s['site_name']}) - same establishment ({bt}; "
                    f"{d['city']}, {d['state']}); closed as a merged-duplicate tombstone (pass-16 Tredegar precedent); the plant itself is held once, as {surv}. Row never deleted.")
        d["operating_status"] = "closed"
        d["last_verified"] = DATE
        add_note(s, f"absorbs duplicate site {dup} ({d['site_name']}; type {d['site_type']}, tier {d['verification_tier']}, status {was} "
                    f"before this fold) - same establishment ({bt}) (dedupe-medium apply, PR #254 verdict {p['cluster']}); the folded row stays as a tombstone.")
        s["last_verified"] = DATE
        touch(site_file[dup])
        touch(site_file[surv])
        log.append(f"SITE FOLD {dup} -> {surv}")

    # ---- evidence rows for the repoints
    ev_new = {}
    eid = EVD_FIRST
    have = {(e["record_id"], e["source_ref"]) for f in sorted(data.glob("evidence_sites_*.csv")) for e in read_rows(f)[0] if e["created_by"] == BY}
    for x in repoints:
        sid, new = x["record"], x["target"]
        old = moved_sites[sid][0]
        shard = site_file[sid].stem.split("_", 1)[1]
        for kind, key in WITNESS[sid]:
            if kind == "frs":
                url = f"https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id={key}&output=JSON"
                j = json.loads((HERE / "raw" / f"frs_{key}.json").read_text())["Results"]["FRSFacility"][0]
                detail = (f"EPA FRS registrant \"{j['FacilityName']}\" at {j['LocationAddress']}, {j['CityName']} {j['StateAbbr']} (registry id {key}) names the operator "
                          f"of this establishment: {new} ({org_by[new]['legal_name']}), not {old} ({org_by[old]['legal_name']})")
                row = dict(source_class="government_filing", source_ref=url, observed_date=DATE, tier_effect="supports_B")
            else:
                url, sc, quote, what = PRESS[key]
                detail = f"{what}: \"{quote}\"; operator of this establishment is {new} ({org_by[new]['legal_name']}), no longer {old} ({org_by[old]['legal_name']})"
                row = dict(source_class=sc, source_ref=url, observed_date=DATE, tier_effect="supports_B")
            if (sid, row["source_ref"]) in have:
                continue
            row.update(evidence_id=f"EVD-{eid:06d}", record_table="sites", record_id=sid, claim_type="parent", claim_detail=detail, created_by=BY,
                       notes=f"dedupe-medium apply {DATE} (PR #254 verdict {x['cluster']}); operator-only observation; page read {DATE}, raw copy in tasks/dedupe-medium-apply-2026-11-06")
            ev_new.setdefault(data / f"evidence_sites_{shard}.csv", []).append(row)
            eid += 1
    n_ev = sum(len(v) for v in ev_new.values())
    rel_base = max([int(x["relationship_id"][4:]) for x in rels["rows"]] + [REL_FIRST - 1]) + 1
    for i, r in enumerate(new_rel):
        r["relationship_id"] = f"REL-{rel_base + i:06d}"

    log.append(f"EVIDENCE rows {n_ev} (EVD-{EVD_FIRST:06d}..EVD-{eid - 1:06d}); RELATIONSHIP rows {len(new_rel)}")
    print("\n".join(log))
    if a.dry_run:
        return
    changed = bool(new_rel or ev_new or any(t["dirty"] for t in files.values()))
    for f, t in files.items():
        if t["dirty"]:
            write_rows(f, t["rows"], t["header"], t["eol"])
    for f, rows in ev_new.items():
        append_sorted(f, rows, "evidence_id")
    if new_rel:
        append_sorted(data / "relationships.csv", new_rel, "relationship_id")
    if changed and not a.no_journal:
        (HERE / "journal.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
        write_sources()
    if link_moves and not a.no_journal:  # check_row_loss keys registry_links by org|registry|id|site: a re-point shows as one removal + one add
        rem = HERE / "REMOVALS.csv"
        with open(rem, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["table", "key", "reason"])
            for key, new in sorted(link_moves):
                w.writerow(["registry_links", key, f"facility-grain link follows its site to the operator {new} (V-6, R10); dedupe-medium apply, PR #254 repoint_site"])


if __name__ == "__main__":
    main()
