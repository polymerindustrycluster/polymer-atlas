#!/usr/bin/env python3
"""Second re-review: withheld existence/address rows whose rejection may rest only on grounds the owner ruled on
2026-11-20 (contact-page address; short-name existence). Fresh judgment under the amended brief; prior verdicts are
not shown. Each record carries a window of the saved page around every quote, plus its Atlas site count.

    python rereview2_bundle.py <atlas repo> <corpus dir>   -> <corpus>/review_rereview2.md
"""
import csv, glob, re, sys
from collections import Counter
from pathlib import Path

atlas, corpus = Path(sys.argv[1]), Path(sys.argv[2])
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
T = Path(__file__).resolve().parent
EXCLUDE = {"ORG-002409", "ORG-001874"}  # both families: wrong entity (acquirer / parent page), not a ruled ground
recs = {}
for f in glob.glob(str(atlas / "data" / "organizations_*.csv")) + glob.glob(str(atlas / "data" / "sites_*.csv")):
    for r in rd(f):
        recs[r.get("site_id") or r["org_id"]] = r
nsites = Counter(r["org_id"] for f in glob.glob(str(atlas / "data" / "sites_*.csv")) for r in rd(f))
want = {(w["record_id"], w["claim_type"]) for w in rd(T / "withheld.csv")
        if w["claim_type"] in ("existence", "address") and w["record_id"] not in EXCLUDE}
rows = [r for r in rd(T / "packet_rows.csv") if (r["record_id"], r["claim_type"]) in want]

BRIEF = (corpus / "review_bundle.md").read_text(encoding="utf-8").split("\n---\n")[0].rstrip() + """

## Owner rulings, 2026-11-20 (binding; they amend the definitions above)

1. **Contact-page address.** For an organization that shows a SINGLE address on its own site (no other plants,
   offices or locations listed on the page), that address on its own contact or footer block witnesses the HQ city
   and state even without the word "headquarters". If the page lists several locations, the HQ claim still needs an
   explicit headquarters or corporate-office label.
2. **Short name.** Existence is identity, not legal form: the company's own page styling itself by its trade name or
   its legal name without the suffix (Inc, LLC, Co.) witnesses existence. It does NOT cover a page that presents a
   different legal entity, a parent, an acquirer, or a name that only coincidentally resembles the record.

Each record below shows a window of the saved page around each quote, not the whole page.
"""
out = [BRIEF]
for rid in dict.fromkeys(r["record_id"] for r in rows):
    r = recs[rid]
    op = recs.get(r.get("org_id")) if rid.startswith("SITE-") else None
    out.append(f"\n---\n## {rid} ({'site' if op else 'organization'}, tier {r['verification_tier']})")
    if op:
        out.append(f"- site_name: {r['site_name']}\n- street_address: {r.get('street_address')}\n- city/state: {r.get('city')}, {r.get('state')}\n"
                   f"- operator: {op['org_id']} {op['legal_name']} (trade names: {op.get('trade_names') or '-'})")
    else:
        out.append(f"- legal_name: {r['legal_name']}\n- trade_names: {r.get('trade_names') or '-'}\n- hq: {r.get('hq_city')}, {r.get('hq_state')}\n"
                   f"- website: {r.get('website')}\n- sites held for this organization in the Atlas: {nsites.get(rid, 0)}")
    out.append("\n### Proposed rows")
    page = (corpus / "pages" / f"{rid}.txt").read_text(encoding="utf-8")
    spans = []
    for x in rows:
        if x["record_id"] == rid:
            out.append(f"- [{x['claim_type']}] {x['claim_detail']}")
            q = x["claim_detail"].split("quote: ", 1)[1]
            m = re.search(r"\s+".join(re.escape(w) for w in q.split()), page)
            spans.append((max(0, m.start() - 1200), min(len(page), m.end() + 1200)))
    spans.sort()
    merged = [list(spans[0])]
    for a, b in spans[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    for a, b in merged:
        out.append(f"\n### Page text window (chars {a}-{b} of {len(page)})\n```\n{page[a:b]}\n```")
text = "\n".join(out)
(corpus / "review_rereview2.md").write_text(text, encoding="utf-8")
(T / "rereview2_brief.md").write_text(BRIEF + "\n", encoding="utf-8", newline="\n")
print(f"{len(rows)} rows on {len({r['record_id'] for r in rows})} records; {len(text.encode())} bytes")
