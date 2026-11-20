#!/usr/bin/env python3
"""Write the cross-family refute bundle for the pilot packet: brief + per-record fields, proposed rows, saved page text.

    python review_bundle.py <atlas repo> <corpus dir>   -> <corpus>/review_bundle.md, <corpus>/review_schema.json
"""
import csv, glob, json, sys
from pathlib import Path

atlas, corpus = Path(sys.argv[1]), Path(sys.argv[2])
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
recs = {}
for f in glob.glob(str(atlas / "data" / "organizations_*.csv")) + glob.glob(str(atlas / "data" / "sites_*.csv")):
    for r in rd(f):
        recs[r.get("site_id") or r["org_id"]] = r
rows = rd(corpus / "packet_rows.csv")
fetch = {r["record_id"]: r for r in rd(corpus / "fetch.csv")}

BRIEF = """# Refute brief: Polymer Atlas evidence-backfill pilot (2026-11-20)

You are an adversarial reviewer. Your job is to find proposed evidence rows that are WRONG. Do not be generous.

Each proposed row claims that the cited page, on the record's OWN website, witnesses one fact about an existing record
(an organization, or a site = one physical establishment of an operator organization). Rows are permanent once
merged (append-only), so a doubtful row must be rejected. The quote was cut verbatim from the saved page text below.

Claim definitions (Atlas SCHEMA section 4.13):
- existence (organization): the page shows this entity IS the entity the record claims (its legal or trade name, as
  the company itself, not merely mentioned as a customer, partner, acquirer or acquiree).
- existence (site): the operator's own page shows the operator has THIS establishment at THIS street address.
- address (organization): the page states the organization's HQ is in the record's hq_city/hq_state. A sales office,
  distributor, branch, or a different company's address is NOT the HQ.
- address (site): the page prints this site's street address and city.
- liveness: the entity was operating at the observed date. The only witness offered is a live own site with a current
  copyright year. Reject when the copyright belongs to a different entity (a parent or acquirer), or when the page
  shows the entity was closed, sold, merged or absorbed.

Reject (UNSOUND) when, for example: the page is really about a parent, acquirer or successor company; there are signs the
record's entity was acquired or renamed (another company's email domain or branding, "part of", "acquired"); the
quoted address belongs to another entity or is not the HQ; the name match is coincidental or partial (another company
with a similar name); the site address on the page differs from the record (number, street or city); or the quote
does not actually support the claim.

Return one verdict per proposed row: SOUND or UNSOUND, plus a one-sentence reason that names the specific text. Judge only
from the material below. Do not browse.
"""

out = [BRIEF]
for rid in dict.fromkeys(r["record_id"] for r in rows):
    r = recs[rid]
    op = recs.get(r.get("org_id")) if rid.startswith("SITE-") else None
    out.append(f"\n---\n## {rid} ({'site' if op else 'organization'}, tier {r['verification_tier']})")
    if op:
        out.append(f"- site_name: {r['site_name']}\n- street_address: {r.get('street_address')}\n- city/state/zip: {r.get('city')}, {r.get('state')} {r.get('zip')}\n"
                   f"- operator: {op['org_id']} {op['legal_name']} (trade names: {op.get('trade_names') or '-'}; website {op.get('website')})")
    else:
        out.append(f"- legal_name: {r['legal_name']}\n- trade_names: {r.get('trade_names') or '-'}\n- hq: {r.get('hq_city')}, {r.get('hq_state')}\n"
                   f"- website: {r.get('website')}\n- ultimate_parent_name: {r.get('ultimate_parent_name') or '-'}")
    out.append(f"- cited URL (fetched {fetch[rid]['retrieved']}): {fetch[rid]['final_url'] or fetch[rid]['url']}\n\n### Proposed rows")
    for x in rows:
        if x["record_id"] == rid:
            out.append(f"- [{x['claim_type']}] {x['claim_detail']}")
    page = (corpus / "pages" / f"{rid}.txt").read_text(encoding="utf-8")
    out.append(f"\n### Saved page text (first 6000 of {len(page)} chars)\n```\n{page[:6000]}\n```")
(corpus / "review_bundle.md").write_text("\n".join(out), encoding="utf-8")
schema = {"type": "object", "additionalProperties": False, "required": ["verdicts"], "properties": {"verdicts": {"type": "array", "items": {
    "type": "object", "additionalProperties": False, "required": ["record_id", "claim_type", "verdict", "reason"],
    "properties": {"record_id": {"type": "string"}, "claim_type": {"type": "string", "enum": ["existence", "address", "liveness"]},
                   "verdict": {"type": "string", "enum": ["SOUND", "UNSOUND"]}, "reason": {"type": "string"}}}}}}
(corpus / "review_schema.json").write_text(json.dumps(schema, indent=1), encoding="utf-8")
print(f"bundle: {len(rows)} rows on {len(set(r['record_id'] for r in rows))} records, {len(chr(10).join(out))} chars")
