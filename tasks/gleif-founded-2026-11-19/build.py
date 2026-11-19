#!/usr/bin/env python3
"""year_founded from GLEIF for LEI-linked organizations (SCHEMA: "Legal-entity formation year where a source states
it"). GLEIF LEI-CDF `entity.creationDate` is the legal entity's formation date; data is CC0.

A blank year_founded is filled only when the organization's registry_links LEI record (raw copy in raw/<LEI>.json,
fetched 2026-11-19 from api.gleif.org) passes every gate:
  - the organization is active and its year_founded is blank;
  - the LEI entity status is ACTIVE;
  - the entity is US-registered (legal address country US);
  - the legal or headquarters address names the organization's HQ city AND state;
  - entity.creationDate is present;
  - the organization is not tier A (registry evidence caps at supports_B; V-25 would refuse it).
Every other link is written to link_findings.csv with the failed gate: a possible wrong LEI link, never changed here.
Evidence: one `existence` row per fill, source_class registry, tier_effect supports_B (the registry ceiling).

    python3 tasks/gleif-founded-2026-11-19/build.py [--apply]
"""
import csv, io, json, re, sys
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
DATE, BY, EVD0 = "2026-11-19", "claude-code gleif-founded-2026-11-19", 399000  # above main and every open PR


def read(p):
    raw = p.read_bytes(); eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    r = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    return r.fieldnames, list(r), eol


def write(p, head, rows, eol):
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=head, lineterminator=eol); w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


norm = lambda s: re.sub(r"[^a-z]", "", (s or "").lower())
# Integrator holds after review: a renamed or reorganized LEI may carry a predecessor entity's formation date.
HOLD = {"ORG-000925": "Kraton: the LEI was renamed from Kraton Polymers LLC to Kraton Corporation (2023); the 10-K says the "
                      "corporation was incorporated in 2009, succeeding a 2003 LLC (codex refute 2026-11-19)"}


def gate(org, ent):
    """None when the link may be used, else the first failed gate."""
    if org["org_id"] in HOLD:
        return "HELD: " + HOLD[org["org_id"]]
    if org["status"] != "active":
        return "organization not active"
    if org["year_founded"].strip():
        return "year_founded already set"
    if org["verification_tier"] == "A":  # a registry caps at supports_B, which V-25 refuses as a tier A record's support
        return "REGISTRY_CEILING: tier A organization (registry evidence caps at supports_B)"
    if ent.get("status") != "ACTIVE":
        return f"LEI entity status {ent.get('status')}"
    la, ha = ent.get("legalAddress") or {}, ent.get("headquartersAddress") or {}
    if la.get("country") != "US":
        return f"LEI entity registered outside the US ({la.get('country')}, jurisdiction {ent.get('jurisdiction')})"
    want = (norm(org["hq_city"]), "US-" + org["hq_state"].strip().upper())
    if not any((norm(a.get("city")), a.get("region")) == want for a in (la, ha)):
        return (f"LEI address ({la.get('city')}, {la.get('region')}; HQ {ha.get('city')}, {ha.get('region')}) "
                f"does not match the organization's HQ ({org['hq_city']}, {org['hq_state']})")
    if not (ent.get("creationDate") or "")[:4].isdigit():
        return "no entity.creationDate in the LEI record"
    return None


def main():
    links = [r for r in csv.DictReader(open(ROOT / "data/registry_links.csv", encoding="utf-8")) if r["registry"] == "LEI"]
    shards = sorted((ROOT / "data").glob("organizations_*.csv"))
    loaded = {p: read(p) for p in shards if not p.name.endswith("_all.csv")}
    org_at = {r["org_id"]: (p, r) for p, (_, rows, _) in loaded.items() for r in rows}
    fills, findings = [], []
    for l in sorted(links, key=lambda r: r["org_id"]):
        if l["org_id"] not in org_at:
            continue
        _, org = org_at[l["org_id"]]
        ent = json.loads((T / "raw" / f"{l['registry_id']}.json").read_text(encoding="utf-8"))["data"]["attributes"]["entity"]
        why = gate(org, ent)
        if why is None:
            fills.append((l, org, ent))
        elif why not in ("year_founded already set", "organization not active"):
            findings.append({"org_id": l["org_id"], "legal_name": org["legal_name"], "lei": l["registry_id"],
                             "lei_legal_name": ent["legalName"]["name"], "failed_gate": why})
    ev_by_shard = {}
    for i, (l, org, ent) in enumerate(fills):
        year = ent["creationDate"][:4]
        org["year_founded"] = year
        shard = org_at[l["org_id"]][0].name.replace("organizations_", "evidence_organizations_")
        ev_by_shard.setdefault(shard, []).append(dict(
            evidence_id=f"EVD-{EVD0 + i:06d}", record_table="organizations", record_id=l["org_id"], claim_type="existence",
            claim_detail=f"year_founded={year}: GLEIF LEI {l['registry_id']} entity.creationDate {ent['creationDate'][:10]} "
                         f"({ent['legalName']['name']}, {ent.get('jurisdiction')})",
            source_class="registry", source_ref=f"https://api.gleif.org/api/v1/lei-records/{l['registry_id']}",
            observed_date=DATE, tier_effect="supports_B", created_by=BY,
            notes=f"Legal-entity formation year per SCHEMA year_founded. Fetched {DATE}; raw copy "
                  f"tasks/gleif-founded-2026-11-19/raw/{l['registry_id']}.json. Gates: entity ACTIVE, US-registered, "
                  f"legal or HQ address matches the organization's HQ city and state."))
    with open(T / "link_findings.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["org_id", "legal_name", "lei", "lei_legal_name", "failed_gate"], lineterminator="\n")
        w.writeheader(); w.writerows(findings)
    print(f"LEI links {len(links)}; fills {len(fills)}; link findings {len(findings)}")
    if "--apply" in sys.argv and fills:
        for p, (head, rows, eol) in loaded.items():
            if any(org_at[l['org_id']][0] == p for l, _, _ in fills):
                write(p, head, rows, eol)
        for shard, rows in ev_by_shard.items():
            p = ROOT / "data" / shard
            head, have, eol = read(p)
            ids = {r["evidence_id"] for r in have}
            write(p, head, have + [r for r in rows if r["evidence_id"] not in ids], eol)
        print("written")


if __name__ == "__main__":
    main()
