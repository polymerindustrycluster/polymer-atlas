#!/usr/bin/env python3
"""Two-family review packet for the 2026-11-19e year_founded fills (review_packet.md). Facts come from the raw GLEIF
records, sources.csv and current main; nothing is typed by hand except the question.
    python3 -I tasks/owner-rulings-2026-11-19e/review_packet.py"""
import csv, json
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
outc = list(csv.DictReader(open(T / "outcomes.csv", encoding="utf-8")))
src = list(csv.DictReader(open(T / "sources.csv", encoding="utf-8")))
orgs = {r["org_id"]: r for p in (ROOT / "data").glob("organizations_*.csv") for r in csv.DictReader(open(p, encoding="utf-8"))}
L = ["# Review: 3 `year_founded` fills from GLEIF (owner ruling 2026-11-19e)", "",
     "**Your job: try to REFUTE each fill.** Answer per row `SOUND`, `DOUBT` or `WRONG` with one line of reason, then an "
     "overall verdict. Judge only from the facts below.", "",
     "**Rules in force.**",
     "- SCHEMA `year_founded`: \"Legal-entity formation year where a source states it\". Owner ruling 2026-11-19: the "
     "formation year of the legal entity the record describes, even when the business is older or the entity was later "
     "renamed (older business year goes in the note). Not covered: a conversion, a re-incorporation into a new entity, a "
     "predecessor's charter, or a placeholder date.",
     "- #406 used GLEIF `entity.creationDate` only when GLEIF's legal or HQ address named the organization's HQ city and "
     "state. These three failed that gate. Owner ruling 2026-11-19e: a second source's SAME verdict (Muse, 2026-11-19) "
     "plus a re-read quote from the company's own page may stand in for the address gate.",
     "- Registry evidence caps at `supports_B`; none of these organizations is tier A.", ""]
for o in outc:
    oid, lei = o["org_id"], o["lei"]
    org = orgs[oid]
    e = json.loads((ROOT / "tasks/gleif-founded-2026-11-19/raw" / f"{lei}.json").read_text(encoding="utf-8"))["data"]["attributes"]
    ent = e["entity"]
    if o["outcome"] != "filled":
        continue
    la, ha = ent.get("legalAddress") or {}, ent.get("headquartersAddress") or {}
    prev = [n.get("name") for n in ent.get("otherNames") or [] if n.get("type") == "PREVIOUS_LEGAL_NAME"]
    L += [f"## {org['legal_name']} ({oid}) → year_founded {ent['creationDate'][:4]}", "",
          f"- **Our record:** legal name \"{org['legal_name']}\"; HQ field {org['hq_city']}, {org['hq_state']}; tier "
          f"{org['verification_tier']}; website {org.get('website', '')}.",
          f"- **GLEIF {lei}:** legal name \"{ent['legalName']['name']}\"; jurisdiction {ent.get('jurisdiction')}; "
          f"registeredAs {ent.get('registeredAs')}; entity status {ent.get('status')}; LEI registration "
          f"{e['registration'].get('status')}; creationDate {ent['creationDate'][:10]}; previous legal names: "
          f"{prev or 'none'}.",
          f"- **GLEIF addresses:** legal {', '.join(la.get('addressLines') or [])}, {la.get('city')}, {la.get('region')}; "
          f"HQ {', '.join(ha.get('addressLines') or [])}, {ha.get('city')}, {ha.get('region')}.",
          "- **GLEIF field-modification history:** the creation date was never changed to a different value "
          "(the history starts at LEI issuance and cannot see earlier corporate history)."]
    for s in src:
        if s["org_id"] == oid:
            L.append(f"- **{s['role']} quote** ({s['read']}): \"{s['quote']}\" — {s['url']}")
    L.append("")
L += ["## Held before review (for context; tell us if any hold is wrong)", ""]
for o in outc:
    if o["outcome"] == "held":
        L.append(f"- {o['legal_name']} ({o['org_id']}), GLEIF {o['gleif_creation']}: {o['reason']}")
L += ["", "**Known limits.** Muse's SAME verdicts and notes are leads, not evidence; only the quotes above were re-read. "
      "ALPLA's record names the legal entity ALPLA Inc. but carries its Lima, Ohio plant in the HQ field (the entity's "
      "HQ is McDonough, GA); fixing HQ fields is a separate follow-up and not part of this change.", "",
      "Reply format: one line per fill `ORG-xxxxxx: SOUND|DOUBT|WRONG — reason`, then `OVERALL: SOUND|UNSOUND`."]
(T / "review_packet.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(len(L), "lines")
