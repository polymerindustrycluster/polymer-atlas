#!/usr/bin/env python3
"""year_founded from GLEIF for LEI links whose address gate failed in #406 but which a second source confirmed.

Owner ruling 2026-11-19e: for these links, Muse's SAME verdict (2026-11-19) plus a re-read quote from the company's own
page may stand in for #406's address gate. Plastipak is excluded by the same ruling (its only quote is third-party).
Every other #406 gate still runs, live against current main: organization active, year_founded blank, not tier A
(registry evidence caps at supports_B), LEI entity ACTIVE and US-registered, creationDate present. A candidate that
is not held and trips a gate stops the build. Raw LEI records: tasks/gleif-founded-2026-11-19/raw/ (fetched
2026-11-19, CC0); field-modification history: raw/ here. Quotes: sources.csv (re-read 2026-11-20).

    python3 -I tasks/owner-rulings-2026-11-19e/build.py [--apply]
"""
import csv, io, json, sys
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
RAW406 = ROOT / "tasks/gleif-founded-2026-11-19/raw"
DATE, BY, EVD0 = "2026-11-20", "claude-code owner-rulings-2026-11-19e", 400500  # main max EVD-400365 at branch time

CAND = ["ORG-000566", "ORG-000664", "ORG-000965", "ORG-001033", "ORG-001080", "ORG-001128", "ORG-001471"]
# Held before review: the company's own source states a different year, or the ruling excludes the row.
HOLD = {"ORG-001033": "owner ruling 2026-11-19e: Plastipak's only web quote is a third-party page (ndt.org)",
        "ORG-000566": "Sealed Air's own 10-K says it 'was incorporated in Delaware in 1960'; GLEIF dates Delaware file "
                      "2586601 to 1996-01-29. A possible successor or reorganization, which the formation-year ruling "
                      "does not cover",
        "ORG-001080": "Ridge's own site says it 'was incorporated in 2004'; GLEIF gives 1994-02-14 under the former "
                      "name Techna Composites Incorporated (Ohio charter 864734). Ohio SOS was in maintenance on "
                      "2026-11-20, so the charter could not be read",
        "ORG-001471": "MSI Express's FAQ says it was 'formed through the merger of Express Packaging (founded in 1988) "
                      "and Manufacturing Solutions International (founded in 2008)'; GLEIF's 1998-12-31 is a year-end "
                      "date (the Struktol placeholder pattern) and Ohio SOS (charter 1054053) was unreachable",
        # review hold: only rows BOTH families judged SOUND are applied (review_codex.txt, review_gemini.txt)
        "ORG-000965": "Antigravity DOUBT (codex SOUND): Molten's own page says it 'extended its business to ... the United "
                      "States, in December 1991', which the reviewer read as failing to corroborate GLEIF's 1990-11-01"}


def read(p):
    raw = p.read_bytes(); eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    r = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    return r.fieldnames, list(r), eol


def write(p, head, rows, eol):
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=head, lineterminator=eol); w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


def gate(org, ent, mods):
    """None when the link may be used, else the failed gate (#406's gates without the address gate)."""
    if org["status"] != "active":
        return "organization not active"
    if org["year_founded"].strip():
        return "year_founded already set"
    if org["verification_tier"] == "A":
        return "REGISTRY_CEILING: tier A organization"
    if ent.get("status") != "ACTIVE":
        return f"LEI entity status {ent.get('status')}"
    if (ent.get("legalAddress") or {}).get("country") != "US":
        return "LEI entity registered outside the US"
    if not (ent.get("creationDate") or "")[:4].isdigit():
        return "no entity.creationDate in the LEI record"
    vals = {m["attributes"]["valueNew"][:10] for m in mods if m["attributes"]["field"].endswith("EntityCreationDate")}
    if vals - {ent["creationDate"][:10]}:
        return f"creationDate changed in GLEIF's history: {sorted(vals)}"
    return None


def main():
    src = list(csv.DictReader(open(T / "sources.csv", encoding="utf-8")))
    lei_of = {l["org_id"]: l["registry_id"] for l in csv.DictReader(open(ROOT / "data/registry_links.csv", encoding="utf-8"))
              if l["registry"] == "LEI"}
    loaded = {p: read(p) for p in sorted((ROOT / "data").glob("organizations_*.csv"))}
    org_at = {r["org_id"]: (p, r) for p, (_, rows, _) in loaded.items() for r in rows}
    fills, out = [], []
    for oid in CAND:
        p, org = org_at[oid]
        lei = lei_of[oid]
        ent = json.loads((RAW406 / f"{lei}.json").read_text(encoding="utf-8"))["data"]["attributes"]["entity"]
        mods = json.loads((T / "raw" / f"{lei}.field-modifications.json").read_text(encoding="utf-8"))["data"] \
            if oid not in HOLD else []
        why = "HELD: " + HOLD[oid] if oid in HOLD else gate(org, ent, mods)
        tie = [s for s in src if s["org_id"] == oid and s["role"] == "tie"]
        if why is None and not tie:
            why = "no re-read own-site quote ties the LEI entity to the organization"
        assert why is None or oid in HOLD, (oid, why)  # a candidate that is not held must pass every gate
        year = ent["creationDate"][:4] if ent.get("creationDate") else ""
        out.append({"org_id": oid, "legal_name": org["legal_name"], "lei": lei, "gleif_creation": ent.get("creationDate", "")[:10],
                    "outcome": "filled" if why is None else "held", "reason": why or ""})
        if why is None:
            fills.append((p, org, lei, ent, tie, [s for s in src if s["org_id"] == oid and s["role"] == "year"]))
    ev_by_shard = {}
    for i, (p, org, lei, ent, tie, yr) in enumerate(fills):
        year = ent["creationDate"][:4]
        org["year_founded"] = year
        shard = p.name.replace("organizations_", "evidence_organizations_")
        note = (f"Legal-entity formation year per SCHEMA year_founded (owner ruling 2026-11-19). GLEIF's addresses do not "
                f"name the organization's HQ; per owner ruling 2026-11-19e the link is confirmed by a second source (Muse, "
                f"2026-11-19: SAME) and the company's own page, re-read {DATE}: \"{tie[0]['quote']}\" ({tie[0]['url']}).")
        if yr:
            note += f" Year context: \"{yr[0]['quote']}\" ({yr[0]['url']})."
        note += (f" GLEIF field-modification history shows no change to the creation date. Raw copies: "
                 f"tasks/gleif-founded-2026-11-19/raw/{lei}.json and tasks/owner-rulings-2026-11-19e/raw/.")
        ev_by_shard.setdefault(shard, []).append(dict(
            evidence_id=f"EVD-{EVD0 + i:06d}", record_table="organizations", record_id=org["org_id"], claim_type="existence",
            claim_detail=f"year_founded={year}: GLEIF LEI {lei} entity.creationDate {ent['creationDate'][:10]} "
                         f"({ent['legalName']['name']}, {ent.get('jurisdiction')})",
            source_class="registry", source_ref=f"https://api.gleif.org/api/v1/lei-records/{lei}",
            observed_date=DATE, tier_effect="supports_B", created_by=BY, notes=note))
    with open(T / "outcomes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out)
    print(f"candidates {len(CAND)}; fills {len(fills)}; held {len(CAND) - len(fills)}")
    if "--apply" in sys.argv and fills:
        for p, (head, rows, eol) in loaded.items():
            if any(f[0] == p for f in fills):
                write(p, head, rows, eol)
        for shard, rows in ev_by_shard.items():
            p = ROOT / "data" / shard
            head, have, eol = read(p)
            ids = {r["evidence_id"] for r in have}
            assert not ids & {r["evidence_id"] for r in rows}, "evidence id collision"
            write(p, head, have + rows, eol)
        print("written")


if __name__ == "__main__":
    main()
