# PR #308 (CT: LATICRETE Bethany + Silgan Thomaston) — holds and retired IDs

Two withdrawals after Codex's REFUTE of PR #308 @ 0016be6 (reviews/308-atlas-clerk-codex-10.md) and its re-check @ 886bf34 (reviews/308-atlas-clerk-codex-10-recheck.md).
What stays in this PR: `SITE-020000` (LATICRETE International, Bethany) and `EVD-350000` to `EVD-350008` (9 evidence rows). Nothing in the Silgan site remains.

## Hold: the SITE-020001 create (Silgan Dispensing Systems Thomaston, 60 Electric Avenue, Thomaston, CT 06787; parent held ORG-000278)

| Item | State |
|---|---|
| Site row | `SITE-020001` withdrawn from `data/sites_CT.csv`. **ID retired, never reuse.** |
| Evidence rows | `EVD-350009`, `EVD-350010`, `EVD-350011`, `EVD-350012`, `EVD-350014`, `EVD-350015`, `EVD-350016` removed from `data/evidence_sites_CT.csv`, plus `EVD-350013` removed on 2026-11-14 (first pass). All eight **retired, never reuse**. |
| Registry link | The row `ORG-000278, FRS, 110001404944` ("frs_rest_registry_id_name_street_match:SITE-020001") removed from `data/registry_links.csv`: it existed only to support this site. |
| Cells withdrawn earlier | `materials` `thermoplastics` (first pass; no material witness). |

Why: the first re-check found the site had no scope evidence once `EVD-350013` (NAICS text attributed to the locations page) was withdrawn. The same re-check asked for a correctly attributed scope witness or a hold of the whole create.

Search for a witness, 2026-11-14, six fetches (the lane cap), none a plant-level primary signal:
1. `https://silgandispensing.com/our-locations/` raw (HTTP 200): lists "Silgan Dispensing Systems Thomaston Corporation, 60 Electric Avenue, Thomaston, CT 06787" with no product or process.
2. The same page through `r.jina.ai` (HTTP 200): same text.
3. EDGAR submissions for Silgan Holdings (CIK 849869) (HTTP 200): located the FY2025 10-K.
4. The FY2025 10-K on `www.sec.gov` raw: HTTP 403 (route unavailable; not evidence of absence).
5. The same 10-K through `r.jina.ai` (HTTP 200, about 365,000 characters): no occurrence of "Thomaston"; segment text only, no plant-level scope.
6. `https://silgandispensing.com/?s=Thomaston` (HTTP 200): "no results were found".

Verdict grammar (AGENTS §2 rule 8): **STILL_UNCERTAIN** for a polymer-scope claim on this establishment. Neither a failed fetch nor an empty search is evidence the plant does not operate. NAICS 326199 from ITA 960560 and the FRS identity (110001404944, still named REXAM DISPENSING SYSTEMS) stay as leads in the first-pass notes of this file only; they do not establish what the plant makes.

What would settle it: an own-site or filed primary document stating what the Thomaston plant makes: a Silgan Dispensing product or site page, a datasheet or catalogue naming Thomaston as the production site, or a state or federal filing for the establishment that names the product. Then a new create (new site ID and evidence IDs from the lane block) with a scope row attributed to that witness.

## Earlier withdrawals (first pass, 2026-11-14), kept for the record

| Site | Cell | Withdrawn value | Merge-base value | Reviewer's reason |
|---|---|---|---|---|
| SITE-020001 | `materials` | `thermoplastics` | (row was new; empty) | The own locations page identifies the plant and address, not its material; FRS returns identity/address only; NAICS 326199 does not distinguish thermoplastics from other plastics. |

| Evidence ID | Was | Why withdrawn |
|---|---|---|
| EVD-350013 | SITE-020001 `scope`, "ring_primary 1; plastics manufacturing plant (federal NAICS 326199)", cited to the locations page | Claim text rested on federal NAICS, not on the cited page. |
