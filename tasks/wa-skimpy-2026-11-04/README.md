**Judgment calls (flagged first):** GD-OTS Moses Lake left uncertain: its parent org exists only in unmerged PR #56 (not linkable from main) and NAICS 325998 may be energetics; Scougal Seattle placed under ORG-004491 (held HQ McCarran NV); Janicki SW plant (1476 Moore St) created under ORG-003320 next to held SITE-003764 HQ (no street) - possible overlap, integrator check; Ultra Poly Tacoma created new, NOT linked to held Ultra Poly Corp (PA); PRC-DeSoto Woodinville under ORG-000088 PPG; JELD-WEN Coatings Tukwila under ORG-002643 ring 2 low.

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for WA: 37 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | WA sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 37 | 30 | 4 | 3 | 19 | 0 / 30 | 39 -> 69 | 28 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004941..ORG-004959, SITE-006190..SITE-006219, EVD-025214..EVD-025213.

**STILL_UNCERTAIN (settling fact):**
- QMS-WA-17 GENERAL DYNAMICS OTS (Moses Lake): Whether GD-OTS Moses Lake makes polymer products (NAICS 325998, likely energetics); parent org pending in PR #56.
- QMS-WA-28 CHINOOK INDUSTRIAL PARK (Union Gap): Operator at "Chinook Industrial Park", 3400 Tacoma St, Union Gap (an industrial park name, not an operator) and what is molded there.
- QMS-WA-32 ESSEX LABORATORIES LLC (Chehalis): Whether Essex Laboratories Chehalis makes polymer products (NAICS 325998).

**REJECT (deciding fact):**
- QMS-WA-01 CH2O INCORPORATED: Water-treatment inorganic chemicals, not polymer: ITA CY2025 record NAICS 325188/325998 (fetched 2026-11-04).
- QMS-WA-10 OXARC INC PASCO: Industrial gases, not polymer: ITA CY2025 record NAICS 325120 (fetched 2026-11-04).
- QMS-WA-11 SIMPSON TACOMA: Pulp and paper mill, not polymer: ITA CY2025 record NAICS 322110-322130 (fetched 2026-11-04).
- QMS-WA-16 COMPOSITES ONE LLC VANCOUVER: Distributor, not a manufacturer: ITA CY2025 record Composites One NAICS 424610 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/wa-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
