**Judgment calls (flagged first):** Superfos Cumberland placed under ORG-002544 Berry Global (Berry Superfos; Berry now part of Amcor) - integrator check; Solo Cup Federalsburg placed under ORG-002441 Dart Container (Dart owns Solo); Adell Plastics Halethorpe under ORG-004184 Adell Polymers; Braden Sutphin Ink org placed in OH shard (Cleveland HQ, researcher knowledge, not own-site read) - integrator check; Gore Elk Mills 1 matched to held SITE-005554 (not re-created); Sun Chemical Williamsport verified ring 2 low on its secondary ink NAICS; Congoleum Finksburg latest federal record 2020.

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for MD: 29 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | MD sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 29 | 21 | 6 | 2 | 9 | 0 / 20 | 25 -> 45 | 19 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004905..ORG-004913, SITE-006121..SITE-006140, EVD-025292..EVD-024305.

**STILL_UNCERTAIN (settling fact):**
- QMS-MD-04 RICCA CHEMICAL CO. (Pocomoke City): Whether Ricca Chemical Pocomoke City makes any polymer products (NAICS 325998 lab reagents).
- QMS-MD-28 DBA SSI (Hollywood): Legal operator behind "DBA SSI" at 43985 Commerce Ave, Hollywood MD and what plastics/rubber products it makes.

**REJECT (deciding fact):**
- QMS-MD-03 COLONIAL METALS INC - TRIUMPH INDUSTRIAL PARK BLDG 20: Metal powders/inorganic chemicals, not polymer: ITA CY2025 record NAICS 325180/331492 (fetched 2026-11-04).
- QMS-MD-05 W R GRACE AND CO – CURTIS BAY WORKS: Silica and catalysts (inorganic), not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).
- QMS-MD-09 USALCO LLC: Aluminum-based water-treatment chemicals, not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).
- QMS-MD-12 CITRUS & ALLIED ESSENCES LTD: Flavors/fragrances, not polymer: ITA CY2025 record NAICS 311999/325620 (fetched 2026-11-04).
- QMS-MD-13 TILLEY DISTRIBUTION: Chemical distributor, not a manufacturer: ITA CY2025 record NAICS 424690 (fetched 2026-11-04).
- QMS-MD-14 HUBER, J.M. CORPORATION: Inorganic minerals/silica, not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/md-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
