**Judgment calls (flagged first):** Carestream White City left uncertain because its parent org exists only in unmerged PR #64 (no duplicate minted); Ultimate RB sites placed under held ORG-002171 "ULTIMATE RB" (held HQ shows Delphos OH - integrator check); Franklin International Portland under ORG-000850 Franklin Adhesives & Polymers (Columbus OH); Xerox org placed in CT shard and Laticrete org in CT shard (HQ researcher knowledge) - integrator check; Xerox Wilsonville verified ring 2 low (toner/solid ink).

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for OR: 38 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | OR sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 38 | 30 | 0 | 8 | 18 | 0 / 30 | 33 -> 63 | 21 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004960..ORG-004977, SITE-006220..SITE-006249, EVD-025574..EVD-025561.

**STILL_UNCERTAIN (settling fact):**
- QMS-OR-02 ECS (Grants Pass): Legal operator behind FRS/ITA name "ECS" at 3560 Rogue River Hwy, Grants Pass (NAICS 326130/326199).
- QMS-OR-08 CARESTREAM HEALTH, INC. (White City): Carestream White City film plant verified by FRS 110000488623 + ITA 144608 but parent Carestream Health org is pending in PR #64; settling fact: PR #64 merge (then link, no duplicate org).
- QMS-OR-09 TRUEHQ (Hillsboro): What TrueHQ Hillsboro makes (NAICS 325998) - polymer or not.
- QMS-OR-12 CENTRAL OREGON PROCESSING, LLC (Prineville): What Central Oregon Processing Prineville makes (NAICS 325998) - polymer or not.
- QMS-OR-14 FRONT AVE (Portland): Operator identity and products at "Front Ave", 5740 NW Front Ave, Portland (NAICS 325998/424690).
- QMS-OR-23 BULK NATURAL LLC (Portland): What Bulk Natural LLC Portland makes (NAICS 325998) - polymer or not.
- QMS-OR-30 PX1 (Hillsboro): Operator identity and products of "PX1", 5950 NE Starr Blvd, Hillsboro (NAICS 325998).
- QMS-OR-37 Woodburn (Woodburn): Operator identity of ITA establishment "Woodburn" at 2257 Progress Way (NAICS 326121/326122).

**REJECT (deciding fact):**
- none

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/or-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
