#!/usr/bin/env python3
"""Gregstrom relocation correction (2026-11-11). One of the four findings the licensed-source cleanup lanes
surfaced in PR #258, adjudicated in tasks/licensed-source-cleanup-2-2026-11-11/: Gregstrom's own post dated
2025-07-30 says the thermoforming business merged with C&K Plastics in 2024 and the rotomolding business —
the whole remaining company — moved from Woburn, MA to Bedford, NH, with most employees moving. The Atlas
still seats the org and its only site in Woburn with thermoforming attached.

    python3 tasks/gregstrom-relocation-2026-11-11/build.py --data-dir data [--apply --i-am-the-integrator]

Changes (dated primary evidence = the company statement, AGENTS §3):
- ORG-003645: HQ fields Woburn/MA/Middlesex -> Bedford/NH/Hillsborough; the row moves from
  organizations_MA.csv to organizations_NH.csv (a record's shard follows its HQ, AGENTS §3/§4);
  description and notes corrected; the post added to sources; last_verified 2026-11-11.
- SITE-004416 (Woburn): operating_status -> closed, in place (tombstone, never delete); successor is the
  new Bedford site.
- SITE-019101 (new, allocated above the tree-wide site maximum): the Bedford establishment, hq_and_plant,
  rotational_molding only, tier C (existence and process from the company's own post; street address from
  its current place listing).
- Five evidence rows (EVD allocated above the tree-wide maximum) quoting the post verbatim; the new site
  carries both the existence and the scope leg the evidence contract requires of a create.
- One inclusion_log row recording the correction.
"""
import argparse, csv, io, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY = "2026-11-11", "spaghetti gregstrom-relocation-2026-11-11"
POST = "https://gregstrom.com/gregstrom-moves-rotomolding-business/"
MOVE_Q = "Gregstrom Corporation, a 79-year-old plastics manufacturer, is moving its rotomolding business from Woburn, Massachusetts to Bedford, New Hampshire."
MERGE_Q = "Gregstrom's relocation follows the merger of its thermoforming business with C&K Plastics in 2024. By focusing exclusively on rotational molding"


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def header(p):
    return next(csv.reader(open(p, encoding="utf-8")))


def write(p, rows):
    eol = "\r\n" if b"\r\n" in p.read_bytes()[:4096] else "\n"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header(p), lineterminator=eol, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
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

    orgs_ma, orgs_nh = read(data / "organizations_MA.csv"), read(data / "organizations_NH.csv")
    sites_ma, sites_nh = read(data / "sites_MA.csv"), read(data / "sites_NH.csv")
    org = next((r for r in orgs_ma if r["org_id"] == "ORG-003645"), None)
    assert org and org["hq_city"] == "Woburn" and org["hq_state"] == "MA", "ORG-003645 not in its expected pre-state"
    assert not any(r["org_id"] == "ORG-003645" for r in orgs_nh)
    woburn = next((r for r in sites_ma if r["site_id"] == "SITE-004416"), None)
    assert woburn and woburn["operating_status"] == "active", "SITE-004416 not active as expected"
    import glob as g
    all_sites = [r for f in g.glob(str(data / "sites_*.csv")) for r in read(Path(f))]
    new_site_id = f"SITE-{max(int(r['site_id'][5:]) for r in all_sites) + 1:06d}"
    ev_files = {f: read(f) for f in sorted(data.glob("evidence_*.csv"))}
    ev_max = max(int(e["evidence_id"][4:]) for rows in ev_files.values() for e in rows if e["evidence_id"][4:].isdigit())
    log = [f"org ORG-003645: HQ Woburn MA -> Bedford NH; shard organizations_MA -> organizations_NH",
           f"site SITE-004416: operating_status active -> closed (tombstone in place)",
           f"site {new_site_id}: new Bedford establishment (hq_and_plant, rotational_molding, tier C)"]

    org = dict(org)
    org["hq_city"], org["hq_state"], org["hq_county"] = "Bedford", "NH", "Hillsborough"
    org["description_1line"] = ("Third-generation family-owned rotational molder, founded 1946; in Woburn MA until "
                                "the 2025 relocation to Bedford NH")
    org["sources"] = org["sources"].rstrip("; ") + "; " + POST
    org["notes"] = org["notes"].rstrip() + (
        " [Relocation correction 2026-11-11] The company's own post dated 2025-07-30 announced the rotomolding "
        "business's move from Woburn MA to Bedford NH, most employees moving; its thermoforming business had merged "
        "with C&K Plastics in 2024, leaving the company rotomolding-only. HQ fields and shard follow the move; the "
        "Woburn establishment (SITE-004416) is closed and the Bedford establishment is SITE-019101. The pre-move "
        "roster's Bedford NH address, set aside in pass 18, predates the actual move.")
    org["last_verified"] = DATE

    woburn = dict(woburn)
    woburn["operating_status"] = "closed"
    woburn["notes"] = woburn["notes"].rstrip() + (
        " [Closed in the 2025 relocation — correction 2026-11-11] The company's own post dated 2025-07-30 announced "
        "the move of its rotomolding business from Woburn to Bedford NH, with most employees moving; thermoforming "
        "had merged into C&K Plastics in 2024. Successor establishment: SITE-019101 (Bedford NH). Processes and "
        "materials above are this establishment's historical record.")
    woburn["last_verified"] = DATE

    new_site = {c: "" for c in header(data / "sites_NH.csv")}
    new_site.update({
        "site_id": new_site_id, "org_id": "ORG-003645", "site_name": "Gregstrom Bedford Plant",
        "site_type": "hq_and_plant", "city": "Bedford", "state": "NH", "zip": "03110", "county": "Hillsborough",
        "county_source": "physical_address", "ring_primary": "1", "processes": "rotational_molding",
        "materials": "polyethylene_pe;polypropylene_pp", "operating_status": "active",
        "sources": f"own site gregstrom.com (relocation post, 2025-07-30): {POST}; place listing for Gregstrom Corporation, 10 Iron Horse Dr, Bedford NH",
        "verification_tier": "C", "last_verified": DATE, "created_by": BY,
        "notes": ("Created 2026-11-11 in the relocation correction: the successor establishment to SITE-004416 "
                  "(Woburn MA), closed when the company moved its rotomolding business to Bedford NH in 2025 "
                  "(company post dated 2025-07-30, quoted in this site's existence evidence row). Street address "
                  "from the company's current place listing; the post names only the towns. Thermoforming is not "
                  "carried: that business merged into C&K Plastics in 2024. Materials carried from the Woburn "
                  "record; the post states the company continues with its existing rotomolding equipment set."),
        "street_address": "10 Iron Horse Dr", "country": "US"})

    def ev(eid, table, rid, ctype, quote, shard, note):
        return shard, {"evidence_id": eid, "record_table": table, "record_id": rid, "claim_type": ctype,
                       "claim_detail": f"{ctype}, as the company's own post states it: \"{quote}\"",
                       "source_class": "own_site", "source_ref": POST, "observed_date": DATE,
                       "tier_effect": "supports_B", "created_by": BY, "notes": note}
    ev_new = [
        ev(f"EVD-{ev_max + 1:06d}", "organizations", "ORG-003645", "liveness", MOVE_Q,
           data / "evidence_organizations_NH.csv",
           "Relocation of record: the company's own post, dated 2025-07-30. Settles the stale-location finding "
           "surfaced by the licensed-source cleanup lanes (PR #258) and adjudicated 2026-11-11."),
        ev(f"EVD-{ev_max + 2:06d}", "organizations", "ORG-003645", "scope", MERGE_Q,
           data / "evidence_organizations_NH.csv",
           "The same post: thermoforming left the company in the 2024 C&K Plastics merger; the surviving scope "
           "is rotational molding only."),
        ev(f"EVD-{ev_max + 3:06d}", "sites", new_site_id, "existence", MOVE_Q,
           data / "evidence_sites_NH.csv",
           "Existence of the Bedford establishment, from the company's own relocation post dated 2025-07-30; "
           "street address rests on the place listing named in the site row's sources."),
        ev(f"EVD-{ev_max + 4:06d}", "sites", "SITE-004416", "liveness", MOVE_Q,
           data / "evidence_sites_MA.csv",
           "Closure of record for the Woburn establishment: the company's own post dated 2025-07-30 announced "
           "the business's move to Bedford NH (dated company statement, AGENTS §3). Successor: " + new_site_id + "."),
        ev(f"EVD-{ev_max + 5:06d}", "sites", new_site_id, "scope",
           "As a value-added rotomolder, Gregstrom combines quality manufacturing with design reviews, molding making, product assembly, and testing.",
           data / "evidence_sites_NH.csv",
           "Scope of the Bedford establishment as the company's own post states it (2025-07-30): rotational "
           "molding with design, assembly and testing services. The evidence contract's scope leg for the create (AGENTS §4)."),
    ]
    log += [f"evidence {e['evidence_id']} -> {r} {c} ({s.name})" for s, e in
            [(s, e) for s, e in ev_new] for r, c in [(e["record_id"], e["claim_type"])]]

    incl = {"date": DATE, "entity": "ORG-003645 / SITE-004416 / " + new_site_id, "decision": "relocation correction applied",
            "rule_cited": "AGENTS §3 (status change on dated primary evidence; shard follows HQ / physical state)",
            "researcher": "spaghetti",
            "notes": "Company post 2025-07-30: thermoforming merged into C&K Plastics (2024); rotomolding moved "
                     "Woburn MA -> Bedford NH (2025). Woburn site tombstoned closed; Bedford site created at tier C."}
    log.append("inclusion_log: +1 row (relocation correction)")

    print("\n".join(log))
    if a.apply:
        import bisect
        nh_sorted = list(orgs_nh)
        nh_sorted.insert(bisect.bisect_left([r["org_id"] for r in nh_sorted], "ORG-003645"), org)
        write(data / "organizations_MA.csv", [r for r in orgs_ma if r["org_id"] != "ORG-003645"])
        write(data / "organizations_NH.csv", nh_sorted)
        write(data / "sites_MA.csv", [woburn if r["site_id"] == "SITE-004416" else r for r in sites_ma])
        write(data / "sites_NH.csv", sites_nh + [new_site])
        by_shard = {}
        for shard, e in ev_new:
            by_shard.setdefault(shard, []).append(e)
        for shard, rows in by_shard.items():
            write(shard, ev_files[shard] + rows)
        ipath = data / "inclusion_log.csv"
        write(ipath, read(ipath) + [incl])
        print("applied")


if __name__ == "__main__":
    main()
