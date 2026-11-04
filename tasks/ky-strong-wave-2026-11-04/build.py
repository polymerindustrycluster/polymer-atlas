#!/usr/bin/env python3
"""STRONG wave, Kentucky (2026-11-04): mint the verified creates from the lane verdicts.

    python3 tasks/ky-strong-wave-2026-11-04/build.py --data-dir data [--apply --i-am-the-integrator]

Inputs, all in this folder:
- lanes/I*/verdicts.csv;
- rawcheck.csv: the integrator re-fetched each own_url raw and checked own_quote word for word;
- lanes/I*/input.csv: the lead-fusion STRONG clusters with their federal source ids.

Federal facts come from the OSHA ITA and OSHA inspection packets in tasks/osha-ita-2026-11-01 and
tasks/osha-spine-2026-11-01, both bulk government extracts, so they are cited as government_filing. ECHO/FRS ids are
kept in notes only: a registry row would need a fresh dated fetch (SCHEMA §4.13 grep rule).

The conventions follow the UT pilot (#41):
- a site with a federal source plus a raw-verified own-site witness is tier B;
- a site on federal sources only is tier C;
- a new organization is tier C.

A lane's tier-B claim whose quote failed the raw check drops to C, and its own-site evidence is not minted.
Ids start above every id used by open PRs at build time: ORG-005101, SITE-006401, EVD-077010.
"""
import argparse, csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE.parent
sys.path.insert(0, str(TASKS / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
import atlas as A  # noqa: E402

DATE, BY = "2026-11-04", "claude-code ky-strong-wave-2026-11-04"
ORG0, SITE0, EVD0 = 8201, 11751, 124001  # disjoint per-state block
CA_PROV = {"AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK"}
US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    voc = json.load(open(HERE.parents[1] / "docs/schema/vocab.json", encoding="utf-8"))["vocabularies"]
    VP, VM = set(voc["PROCESSES"]["values"]), set(voc["MATERIALS"]["values"])
    ita = {r["establishment_id"]: r for r in read(TASKS / "osha-ita-2026-11-01/establishments.csv")}
    osha = {r["est_key"]: r for r in read(TASKS / "osha-spine-2026-11-01/establishments.csv")}
    raw = {r["cluster_id"]: r["raw"] for r in read(HERE / "rawcheck.csv")}
    clusters = {r["cluster_id"]: r for f in HERE.glob("lanes/L*/input.csv") for r in read(f)}
    verdicts = sorted((r for f in sorted(HERE.glob("lanes/L*/verdicts.csv")) for r in read(f)),
                      key=lambda r: r["verdict"].strip() != "VERIFIED_NEW_ORG")  # new orgs first
    new_org_by_cluster = {}
    orgs = {r["org_id"]: r for f in data.glob("organizations_*.csv") for r in read(f)}
    nid, sid, eid = ORG0, SITE0, EVD0
    org_rows, site_rows, ev, holds = defaultdict(list), [], defaultdict(list), []
    new_org_by_name = {}

    def E(shard, table, rid, claim, detail, cls, ref, eff, note=""):
        nonlocal eid
        ev[shard].append({"evidence_id": f"EVD-{eid:06d}", "record_table": table, "record_id": rid, "claim_type": claim,
                          "claim_detail": detail, "source_class": cls, "source_ref": ref, "observed_date": DATE,
                          "tier_effect": eff, "created_by": BY, "notes": note})
        eid += 1

    for v in verdicts:
        verdict = v["verdict"].strip()
        if not verdict.startswith("VERIFIED"):
            continue
        c = clusters[v["cluster_id"]]
        ids = dict(x.split(":", 1) for x in c["sources_with_ids"].split(";") if ":" in x)
        fed = []
        for i in [x for x in c["sources_with_ids"].split(";") if x.startswith("ITA:")]:
            e = ita.get(i.split(":", 1)[1])
            if e:
                fed.append(("ita", f"OSHA ITA Form 300A CY{e['year_filing_for'] or '2025'} establishment {e['establishment_id']} ({e['establishment_name']})",
                            e["naics_code"], e["date_submitted"][:10]))
        for i in [x for x in c["sources_with_ids"].split(";") if x.startswith("OSHA:")]:
            e = osha.get(i.split(":", 1)[1])
            if e and e["latest_activity_nr"]:
                fed.append(("osha", f"OSHA inspection {e['latest_activity_nr']} ({e['name']}), https://www.osha.gov/ords/imis/establishment.inspection_detail?id={e['latest_activity_nr']}",
                            e["naics_latest"], e["latest_inspection"][:10]))
        if not fed:
            holds.append({"cluster_id": v["cluster_id"], "reason": "no ITA or OSHA row resolvable in the packets"}); continue
        own_ok = raw.get(v["cluster_id"]) == "yes" and v["own_url"].strip().startswith("http")
        tier = "B" if (v["tier"].strip() == "B" and own_ok) else "C"
        eff = "supports_B" if tier == "B" else "supports_C"
        procs = ";".join(t for t in re.split(r"[;,]\s*", v["processes"]) if t in VP) if own_ok else ""
        mats = ";".join(t for t in re.split(r"[;,]\s*", v["materials"]) if t in VM) if own_ok else ""
        naics = (v["naics_primary"] or fed[0][2] or "").strip()[:6]
        ring = "2" if naics[:4] in ("3252", "3255", "3259") else "1"
        echo = f" ECHO/FRS {ids['ECHO']}." if "ECHO" in ids else ""
        if verdict == "VERIFIED_NEW_ORG":
            key = A.name_key(v["org_legal_name"])  # AGENTS §3 normalized name: one org per name across lanes
            if key in new_org_by_name:
                oid = new_org_by_name[key]
            else:
                st = v["org_hq_state"].strip().upper()
                shard = st if st in US_STATES else ("INTL" if st else "US")
                oid = f"ORG-{nid:06d}"; nid += 1; new_org_by_name[key] = oid; new_org_by_cluster[v["cluster_id"]] = oid
                name = v["org_legal_name"].strip()
                et = "llc" if re.search(r"\bL\.?L\.?C\b", name, re.I) else "corporation_private" if re.search(r"\b(inc|corp|corporation|company|co)\b\.?", name, re.I) else "unknown"
                org_rows[shard].append({
                    "org_id": oid, "legal_name": name, "entity_type": et, "ring_primary": ring,
                    "hq_city": v["org_hq_city"].strip(), "hq_state": st if (st in US_STATES or st in CA_PROV) else "",
                    "hq_county": v["org_hq_county"].strip() if st in US_STATES else "",
                    "hq_country": "US" if st in US_STATES else "CA" if st in CA_PROV else {"GERMANY": "DE", "JAPAN": "JP", "SOUTH KOREA": "KR", "KOREA": "KR", "INDIA": "IN", "CANADA": "CA", "TURKEY": "TR", "UNITED KINGDOM": "GB", "UK": "GB", "FRANCE": "FR", "ITALY": "IT", "NETHERLANDS": "NL", "SWITZERLAND": "CH", "CHINA": "CN", "MEXICO": "MX", "BELGIUM": "BE", "AUSTRIA": "AT", "SWEDEN": "SE"}.get(st, ""),
                    "hq_in_scope": "international" if shard == "INTL" else "national_us",
                    "naics_primary": naics, "naics_primary_source_type": "government_filing", "naics_primary_source_name": fed[0][1].split(" (")[0],
                    "naics_confidence": "medium", "processes": procs, "materials": mats, "website": v["org_website"].strip(),
                    "description_1line": f"Polymer manufacturer with a Kentucky establishment in {v['city'] or c['city']} (NAICS {naics}).",
                    "pic_relevance": "potential_member", "status": "active",
                    "sources": "; ".join(([v["own_url"].strip()] if own_ok else []) + [f[1] for f in fed]),
                    "verification_tier": "C", "last_verified": DATE, "created_by": BY,
                    "notes": (f"Created {DATE} in the Kentucky STRONG wave (tasks/ky-strong-wave-2026-11-04) from lead-fusion "
                              f"cluster {v['cluster_id']} (STRONG: {c['sources_with_ids']}). Tier C at birth (AGENTS §3 step 5).{echo} "
                              + (v["note"] or "")[:300]).strip(),
                    "last_activity_evidence_date": max(f[3] for f in fed), "liveness_signal": "operating_evidence", "monitor_watch": "false"})
                ef = f"evidence_organizations_{shard}.csv"
                src_own = v["own_url"].strip() if own_ok else fed[0][1]
                cls_own = "own_site" if own_ok else "government_filing"
                E(ef, "organizations", oid, "existence", f"name {name}", cls_own, src_own, "supports_C")
                E(ef, "organizations", oid, "address", f"establishment at {v['street'] or c['street']}, {v['city'] or c['city']}, KY", "government_filing", fed[0][1], "supports_C")
                E(ef, "organizations", oid, "scope", f"ring_primary {ring}: " + (f"\"{v['own_quote'].strip()}\"" if own_ok else f"federal NAICS {naics} only"), cls_own, src_own, "supports_C")
                E(ef, "organizations", oid, "code", f"naics_primary {naics} ({fed[0][1].split(' (')[0]})", "government_filing", fed[0][1], "supports_C")
                E(ef, "organizations", oid, "activity", "operating at its Kentucky establishment", "government_filing", fed[-1][1], "supports_C")
                E(ef, "organizations", oid, "liveness", f"latest federal record {max(f[3] for f in fed)}", "government_filing", fed[-1][1], "supports_C")
        else:
            oid = v["held_org_id"].strip()
            if oid.upper().startswith("NEW:"):
                oid = new_org_by_cluster.get(oid.split(":", 1)[1].strip(), oid)
            if oid not in orgs:
                holds.append({"cluster_id": v["cluster_id"], "reason": f"held_org_id {oid!r} not found"}); continue
        s = f"SITE-{sid:06d}"; sid += 1
        street, city = (v["street"] or c["street"]).strip(), (v["city"] or c["city"]).strip()
        zip_, county = (v["zip"] or c["zip5"]).strip(), (v["county"] or c["county"]).strip()
        oname = orgs[oid]["legal_name"] if oid in orgs else v["org_legal_name"].strip()
        site_rows.append({"site_id": s, "org_id": oid, "site_name": (v["site_name"] or f"{oname} - {city}").strip(),
                          "site_type": "manufacturing_plant", "city": city, "state": "KY", "zip": zip_, "county": county,
                          "ring_primary": ring, "naics_primary": naics, "naics_primary_source_type": "government_filing",
                          "naics_confidence": "medium", "processes": procs, "materials": mats, "operating_status": "active",
                          "sources": "; ".join(([v["own_url"].strip()] if own_ok else []) + [f[1] for f in fed]),
                          "verification_tier": tier, "last_verified": DATE, "created_by": BY,
                          "notes": (f"Created {DATE} in the Kentucky STRONG wave from lead-fusion cluster {v['cluster_id']} "
                                    f"(STRONG: {c['sources_with_ids']}).{echo} Tier {tier}: " + ("federal + raw-verified own-site witness. " if tier == "B" else "federal sources" + ("" if own_ok else "; own-site quote not raw-verified") + ". ")
                                    + (v["note"] or "")[:300]).strip(),
                          "street_address": street, "county_source": "physical_address" if county else "", "country": "US"})
        ef = "evidence_sites_KY.csv"
        E(ef, "sites", s, "existence", f"{oname} establishment at {street}, {city}", "government_filing", fed[0][1], eff, "federal establishment record")
        if own_ok:
            E(ef, "sites", s, "existence", f"named by the operator: \"{v['own_quote'].strip()}\"", "own_site", v["own_url"].strip(), eff)
        E(ef, "sites", s, "address", f"{street}, {city}, KY {zip_}", "government_filing", fed[-1][1], eff)
        E(ef, "sites", s, "code", f"naics_primary {naics}", "government_filing", fed[0][1], eff)
        E(ef, "sites", s, "scope", (f"\"{v['own_quote'].strip()}\"" if own_ok else f"federal NAICS {naics} only; no raw-verified own-site read"),
          "own_site" if own_ok else "government_filing", v["own_url"].strip() if own_ok else fed[0][1], eff)
        E(ef, "sites", s, "parent", f"org_id {oid} ({oname}); the federal establishment record names the operator", "own_site" if own_ok else "government_filing",
          v["own_url"].strip() if own_ok else fed[0][1], eff)
        E(ef, "sites", s, "activity", "manufacturing operations at the site", "government_filing", fed[-1][1], eff)
        E(ef, "sites", s, "liveness", f"latest federal record {max(f[3] for f in fed)}", "government_filing", fed[-1][1], eff)
    n_ev = sum(len(x) for x in ev.values())
    with open(HERE / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["cluster_id", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
    print(f"orgs {sum(len(x) for x in org_rows.values())} {dict((k, len(x)) for k, x in org_rows.items())}; sites {len(site_rows)} "
          f"{Counter(r['verification_tier'] for r in site_rows)}; evidence {n_ev} (EVD-{EVD0:06d}..EVD-{eid - 1:06d}); holds {len(holds)}")
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        for shard, rows in org_rows.items():
            append_rows(data / f"organizations_{shard}.csv", rows)
        append_rows(data / "sites_KY.csv", site_rows)
        for name, rows in ev.items():
            append_rows(data / name, rows)
        print("applied")


if __name__ == "__main__":
    main()
