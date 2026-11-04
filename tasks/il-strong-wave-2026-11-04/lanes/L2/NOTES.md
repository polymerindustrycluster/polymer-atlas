# Lane L2 notes (IL STRONG wave, 2026-11-04)

20 clusters, 20 rows in `verdicts.csv`.

| Verdict | Tier | Count |
|-|-|-|
| VERIFIED_NEW_ORG | C | 7 (Nemera, Packaging Personified, Sandstrom, G J Nikolas, Secon, Tiger Drylac, Vanseal/VRC) |
| VERIFIED_NEW_SITE | B | 1 (Amcor Mundelein under ORG-000665) |
| VERIFIED_NEW_SITE | C | 1 (Plastipak Champaign under ORG-001033, federal only) |
| STILL_UNCERTAIN | none | 11 |
| REJECT / DUPLICATE_OF | none | 0 |

## Method limits
- Tools: WebFetch and WebSearch only; WebFetch summarises pages, so quotes were taken only from spans the fetcher returned verbatim. The integrator should re-fetch each `own_url` and confirm the words.
- Fetcher blocked (HTTP 403 or TLS/DNS failure) on seymourpaint.com, romanproducts.com, foremantool.com subpages, Business Wire and the Cadillac Products domain. A failed fetch was treated as no evidence, so those rows are STILL_UNCERTAIN, not REJECT. Seymour, Roman and Cadillac look likely in scope and are worth a re-fetch from another network.
- Dedupe: `current_atlas_hits` (org-level only) were read with `atlas.py show`. No site-level duplicates. Held-org matches used: Plastipak ORG-001033, Amcor ORG-000665; Pactiv ORG-002537 and Sika ORG-001114 would be the parents if their rows resolve. ORG-002395 (Fabri Kal) and ORG-001577 (Master Builders Solutions) are name-variant hits, not parents.

## Judgement calls to review
- Coatings makers (Sandstrom, G J Nikolas, Tiger Drylac) are verified under the PIC coatings-are-Ring-2 rule. None of their pages names a resin or binder, so no resin terms were tagged. If the integrator wants binder evidence, these three drop to STILL_UNCERTAIN.
- Plastipak Champaign: plastipak.com never names Champaign, so processes are blank (no parent-capability inheritance, SCHEMA B14). Verified on federal sources plus the held org's own-site scope; a stricter reading would call it STILL_UNCERTAIN.
- Vanseal: process statement is VRC company-wide. The new organization may belong under VRC Engineered Solutions (Milwaukee corporate office) instead of Vanseal.
- Packaging Personified: the pages do not say which of its two plants (Carol Stream IL, Sparta MI) runs the extruders.
- Phoenix Converting (Flex Pack): Chapter 11 filed 2026-07-20 (N.D. Ill. 1:26-bk-11935) is not a closure; held as STILL_UNCERTAIN pending post-petition status.
- Yoshino: the Illinois State Fire Marshal UST record says Closed; that is a tank status, not a plant closure. No company site found.
- Counties filled from geography where the federal row was blank: Libertyville (Lake), Red Bud (Randolph), St. Charles (Kane), Springfield (Sangamon).
- Federal row gave `HQ` for none of the new orgs; org HQ fields are blank where the fetched own pages did not state them.
