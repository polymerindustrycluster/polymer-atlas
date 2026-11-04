**Judgment calls (flagged first):** Cresline-West Phoenix placed under ORG-002517 Cresline Plastic Pipe Company (same pipe group; held record shows PA) - integrator check; Tech Group Tempe under ORG-002772 West Pharmaceutical (d/b/a West); Dunn-Edwards org placed in AZ shard at the Phoenix plant city; Polyglass Phoenix verified ring 2 (polymer-modified roofing coatings/membranes); Vinyltech Corp (Phoenix PVC pipe) created new, NOT linked to held Vinyltech International LLC (OH) - different company; Brooklyn Bedding verified on secondary NAICS 326150 (foam), low.

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for AZ: 27 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | AZ sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 27 | 19 | 4 | 4 | 10 | 0 / 19 | 24 -> 43 | 13 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004895..ORG-004904, SITE-006102..SITE-006120, EVD-026378..EVD-024091.

**STILL_UNCERTAIN (settling fact):**
- QMS-AZ-01 FUJIFILM ELECTRONIC MATERIALS (Mesa): Whether Fujifilm Electronic Materials Mesa makes polymer materials (photoresists/polyimides) or only inorganic process chemicals (NAICS 325180-325998 mix).
- QMS-AZ-11 SHIN- ETSU MICROSI INC (Phoenix): Whether Shin-Etsu MicroSi Phoenix makes polymer products (photoresists/encapsulants) on site or only distributes (NAICS 325199/424690).
- QMS-AZ-23 CRM of America LLC (Mesa): Witnessed by ITA 224680 + OSHA 348264797 (rubber products, NAICS 326299) but NOT created: the legal name "CRM of America" trips validate.py rule V-50 (PIC CRM); integrator to decide naming. Settling fact: an accepted naming for this org.
- QMS-AZ-25 TRC-Tucson Blvd (Tucson): Operator identity of "TRC-Tucson Blvd" (6351 S Tucson Blvd) and whether coatings/rubber products are made there.

**REJECT (deciding fact):**
- QMS-AZ-02 PACIFIC SCIENTIFIC EMC WILLIS: Energetic devices/explosives, not polymer: FRS 110039401652 and ITA CY2025 record, NAICS 325920 (fetched 2026-11-04).
- QMS-AZ-13 MORTON SALT CO - GLENDALE: Salt, not polymer: ITA CY2025 record Morton Salt Glendale, NAICS 311942/325998 (fetched 2026-11-04).
- QMS-AZ-15 EARTH PROTECTION SERVICES: Hazardous-waste services, not polymer: ITA CY2025 record NAICS 562112/562211 (fetched 2026-11-04).
- QMS-AZ-22 Hasa Inc. - Eloy: Pool chlorine (sodium hypochlorite), not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/az-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
