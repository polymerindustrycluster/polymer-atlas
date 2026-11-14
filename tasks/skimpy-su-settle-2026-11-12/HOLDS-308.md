# PR #308 (CT: LATICRETE Bethany + Silgan Thomaston) — holds and retired IDs

History, all 2026-11-14, after Codex's REFUTE of PR #308 @ 0016be6 (reviews/308-atlas-clerk-codex-10.md) and its re-check @ 886bf34 (reviews/308-atlas-clerk-codex-10-recheck.md):
1. 886bf34: withdrew `SITE-020001` `materials` and `EVD-350013`.
2. c9a4090: held the whole `SITE-020001` create after six fetches found no own-site statement of what the plant makes.
3. This head: the hold is **lifted**. `SITE-020001` is back with a scope row attributed to its actual witness, the ITA filing. `materials` stays held.

## What the Silgan Thomaston records are now (unit: rows on `SITE-020001`)

Restored exactly as first pushed (6 evidence rows): `EVD-350009` (existence, own site), `EVD-350010` (address, own site), `EVD-350011` (address, FRS registry, re-fetched 2026-11-14: REXAM DISPENSING SYSTEMS, 60 ELECTRIC AVE, THOMASTON, 06787, Litchfield), `EVD-350014` (parent), `EVD-350015` (activity), `EVD-350016` (liveness).
Restored with two corrections:
- The site row: `sources` named ITA 960560 as "(REXAM DISPENSING SYSTEMS)"; the filing actually names company "Silgan Dispensing", establishment "Silgan Dispensing Systems Thomaston" (REXAM is the FRS name). Corrected to the filing's name. `materials` and `processes` blank; everything else as first pushed, except the tier below.
- The registry link `ORG-000278, FRS, 110001404944`: the FRS record is at this street, so the link is accurate for the establishment, but the first method label said `name_street_match` and the FRS name is the legacy REXAM name. Relabelled `frs_rest_registry_id_street_match:SITE-020001` (the wording the Kingspan link uses).

**New rows and changed values, all needing review:**
- `EVD-350017` (scope, `government_filing`, `supports_C`): `ring_primary` 1, industry as filed "Jars, plastics, manufacturing", NAICS 326199. Quoted from the held ITA spine (`tasks/osha-ita-2026-11-01/establishments.csv`, `establishment_id 960560`, year_filing_for 2025, submitted 2026-02-02, naics_year 2012). It states only what the filing says: no material or process inferred. This is the correctly attributed replacement for retired `EVD-350013`.
- `EVD-350018` (code, `government_filing`, `supports_B`): `naics_primary` 326199 as filed. Not a restore of `EVD-350012`: that row named the ITA establishment "REXAM DISPENSING SYSTEMS", which misstates the filing. `EVD-350012` stays retired. `supports_B` is the effect the original code row had; a government filing's ceiling allows it.
- `SITE-020001` `verification_tier` **B to C.** The controller's `supports_C` for the scope row makes the scope claim C-strength, and validate rule V-25 refuses tier B with a C-only must-have claim (reproduced). The site's scope now rests on the federal filing alone, so tier C is the honest consequence, matching the other federal-only sites in this skimpy wave. If a reviewer prefers tier B, the alternative is `EVD-350017` at `supports_B`.
- `EVD-350017` and `EVD-350018` IDs were checked free on every remote branch.

## Hold that stays: SITE-020001 `materials`

| Withdrawn | Merge-base | Reviewer's reason | What would settle it |
|---|---|---|---|
| `materials` `thermoplastics` | (row is new; empty) | The locations page identifies the plant and address, not its material; FRS returns identity and address only; NAICS 326199 does not distinguish thermoplastics from other plastics. The filing says "Jars, plastics", not a resin. | A site-specific material witness (an own-site or filed document naming the resin or material class made at 60 Electric Avenue). |

## Retired evidence IDs (never reuse)

| ID | Was | Why |
|---|---|---|
| EVD-350012 | SITE-020001 `code`, naics_primary 326199, ITA 960560 "(REXAM DISPENSING SYSTEMS)" | Misnamed the filing's establishment; replaced by `EVD-350018`. |
| EVD-350013 | SITE-020001 `scope`, "plastics manufacturing plant (federal NAICS 326199)", cited to the locations page | Claim text rested on federal NAICS, not on the cited page; replaced by `EVD-350017`, attributed to the filing. |

## Search log, kept for the record (six fetches for an own-site witness, none stating what the plant makes)
1. `https://silgandispensing.com/our-locations/` raw (HTTP 200): the address only. 2. Same page via `r.jina.ai` (200). 3. EDGAR submissions for Silgan Holdings, CIK 849869 (200). 4. FY2025 10-K on `www.sec.gov` raw: HTTP 403 (route unavailable, not evidence of absence). 5. Same 10-K via `r.jina.ai` (200, about 365,000 characters): no occurrence of "Thomaston". 6. `https://silgandispensing.com/?s=Thomaston` (200): no results. A failed fetch or an empty search is never evidence the plant makes nothing.
