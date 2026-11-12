# Ohio PIC-18 processes/materials + site_capabilities — batch b01 (2026-11-12)

Worker: grok (branch `agent/grok/oh-capabilities-2026-11-12-b01`). Claim line added in `tasks/QUEUE.md` under the 2026-11-04 claude-code "PIC-18 capability pass" line.

**Stale claim note.** The `claimed:claude-code 2026-11-04` PIC-18 capability pass has had no capability PR since #124 (2026-11-05; earlier #92 folded into #108, and #117). claude-code's latest PR (#261, 2026-11-09) is people/dedupe work. This batch treats the claim as stale. It does not release it. The frame avoids nothing claude-code has open.

## Frame
`frame.csv`: the first 100 rows of a 306-row frame, in county order (Summit, Portage, Stark first), sorted by site_id within each county. A row qualifies when it is:
- an active Ohio site in the PIC-18 counties;
- ring_primary 1–2;
- blank `processes` or blank `materials`;
- owned by an org with a website;
- the org's **only** Atlas site (all shards).

## Method
1. `scripts/capfetch.py` fetches the homepage plus up to 5 same-host pages (capabilities/services/products/materials/about first). The fetch is curl via proxy, at most 6 pages per site, and skips careers/jobs pages. Hiring sites are never witnesses.
2. `scripts/capextract.py` matches a conservative phrase map onto SCHEMA §3.1/§3.2 terms. It keeps a ≤25-word window and checks it as an exact substring of the normalized raw text.
3. `scripts/capfilter.py` drops windows with no first-person or capability context, menu strings and questions, leaving `candidates.csv` (83).
4. Every candidate was then judged by hand (`scripts/b01_cap_dec.csv`). Only clauses that state the company's own process or material were accepted, each with a hand-trimmed quote that is re-asserted as a raw substring with a SHA-256 match.

## Rules applied
- **Fill-blank-only.** A §3 column is written only if it was blank on main. Non-blank columns are left alone.
- **Grain.**
  - *site*: the company has one Atlas site, its pages show no other-state address, and they don't describe multiple locations. Site columns are filled, and so are org columns when blank. One `site_capabilities` row is minted per §3.6 term (company_disclosed).
  - *org*: corporate sites of multi-location companies, e.g. ACE Cryogenic ("two locations"), Impact Sleeves (Locations page), CG Thermal, Fomo/ICP, Technoform, MACtac, Koch Knight, PFC. Org columns are filled only, and only if blank; in this batch every one of them was already populated, so nothing was written.
- **§3.6 mapping.**
  - Materials map 1:1 when the term is in CAP_MATERIAL.
  - custom_compounding and compounding_unspecified map to `compounding`.
  - composites_frp, recycling_unspecified and insert_overmolding have no §3.6 term, so they get no CAP row.
- **Evidence.** Each value gets one evidence row:
  - `claim_type=scope`, `own_site`, `supports_A`.
  - The claim_detail carries the quote. Notes carry the raw SHA-256.
  - Tier, ring, NAICS and status are unchanged.

## Results
| | count |
|---|---|
| frame rows | 100 (86 with ≥1 page loaded; 394 pages) |
| accepted term decisions | 27 (`verdicts.csv`) |
| sites gaining a §3 tag | **11** (11% yield) |
| site evidence rows | 18 (EVD-345000..) |
| org evidence rows | 4 |
| site_capabilities rows | 14 (CAP-001000–CAP-001013) |

Candidates that were not minted are in `not_minted.csv`, each with a reason. The main reasons:
- the column was already populated;
- the clause names a customer's process, a market, an end use, equipment or a nav label rather than the company's own process or material.

These are not REJECT verdicts on records. Fetch failures (14 sites with no page loaded) mean the source was unavailable, not that the capability is absent.

## Yield stop
The batch yield is 11%, below CAMPAIGN's 20% stop rule, so **no b02 follows on this route**. The remaining 206 frame rows are in the working frame. If this lane continues, it needs a different source, such as product-catalog PDFs or permits/TRI for site-grain process facts, or a ruling that allows nav-level capability lists ("Capabilities: Injection Molding") as own-site witnesses.

## Leads
- Ohio Precision Molding SITE-000085: the website on file is designmolded.com (Design Molded Plastics SITE-000069). This repeats the Lane A address-first lead; nothing was minted.

## CI
The CI `validate` job fails on main too (docs/schema/vocab.json is stale; test_audit_evidence_coverage errors on EVD-333167). Not touched here, per instruction. `python3 scripts/validate.py` passes locally, and `scripts/check_row_loss.py --base origin/main` is OK.
