**Judgment calls (flagged first):** IFS Coatings Ardmore placed under held ORG-002633 Ifs Industries Inc. (Reading PA) as the same powder-coatings group - integrator check; American Phoenix Lawton placed under ORG-003969 as rubber compounding (NAICS 325998); Berry Pryor under ORG-002544; Goodyear Lawton under ORG-000003; 3M Technical Ceramics rejected on NAICS + name (ceramics).

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for OK: 23 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | OK sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 23 | 13 | 6 | 4 | 6 | 0 / 13 | 29 -> 42 | 11 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004889..ORG-004894, SITE-006089..SITE-006101, EVD-026808..EVD-023879.

**STILL_UNCERTAIN (settling fact):**
- QMS-OK-01 DELTA FAUCET OF OKLAHOMA (Chickasha): Whether Delta Faucet Chickasha molds or compounds polymer parts (NAICS 325211/325998 listed) vs metal faucet work only, and the parent org (Masco) record.
- QMS-OK-09 ML PRODUCTS LLC (Noble): What ML Products makes at 1101 E Maguire Rd, Noble (NAICS 325212/326299 vs 339113 medical devices).
- QMS-OK-15 OKLAHOMA CITY SITE (Yukon): Operator and products of the Yukon "Oklahoma City Site" at 100 N Mustang Rd Bldg 200 (NAICS 325211/325992).
- QMS-OK-17 SHEET VINYL FLOORING MFG FACILITY (Stillwater): Current operator (AHF Products ORG-004124 or other) of the Stillwater sheet vinyl flooring plant at 4115 N Perkins Rd.

**REJECT (deciding fact):**
- QMS-OK-06 NORIT ACTIVATED CARBON: Activated carbon, not polymer: FRS/ITA CY2025 (filed 2026-02-26) Norit Activated Carbon, NAICS 325998.
- QMS-OK-12 CHEMTRADE REFINERY SERVICES, INC.: Refinery sulfuric-acid services, not polymer: ITA CY2025 (filed 2026-02-27) NAICS 325180.
- QMS-OK-13 DEEPWATER CHEMICALS, INC.: Iodine/inorganic chemicals, not polymer: ITA CY2025 (filed 2026-08-11) NAICS 325180.
- QMS-OK-14 WOODWARD IODINE CORPORATION: Iodine production, not polymer: ITA CY2025 (filed 2026-01-23) NAICS 325180.
- QMS-OK-16 SPECIALTY GAS MFG PLT: Industrial gases, not polymer: ITA CY2025 (filed 2026-02-26) NAICS 325120.
- QMS-OK-19 3M TECHNICAL CERAMICS: Technical ceramics (boron nitride), not polymer: FRS 110056581275 fetched 2026-11-04, NAICS 325180/331419, name 3M Technical Ceramics.

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/ok-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
