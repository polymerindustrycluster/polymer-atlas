**Judgment calls (flagged first):** Centro North Liberty held (SITE-004403), not re-created. Captive Plastics Des Moines placed under ORG-002544 Berry Global (Captive is a Berry subsidiary) - integrator check. Bemis Clysar Camanche created as new org Clysar (no longer Bemis/Amcor). Engineered Plastic Components Kalona linked to ORG-001197. ITA-only rows with generic establishment names (Cedar Rapids, Davenport, Waterloo, Adair) left uncertain on operator identity. 3M Knoxville tape plant carried at ring 2 (adhesive coating).

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for IA: 55 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | IA sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 55 | 39 | 10 | 6 | 21 | 0 / 38 | 37 -> 75 | 26 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-005021..ORG-005041, SITE-006310..SITE-006347, EVD-027320..EVD-026729.

**STILL_UNCERTAIN (settling fact):**
- QMS-IA-13 DUPONT SPECIALTY PRODUCTS USA LLC - FORT MADISON (Fort Madison): What the DuPont Fort Madison plant makes today (NAICS mix 325211/325510/325910) and its current operator after the DuPont split.
- QMS-IA-25 HIGHLINE WARREN (Council Bluffs): Whether Highline Warren Council Bluffs makes plastic products or only blends fluids (NAICS 324191/326160).
- QMS-IA-39 Cedar Rapids (Cedar Rapids): Operator identity of the ITA establishment "Cedar Rapids", 3801 Beverly Road (NAICS 326199/423840).
- QMS-IA-45 Davenport (Davenport): Operator identity of the ITA establishment "Davenport", 1924 Comenitz Dr (NAICS 326199/424690).
- QMS-IA-47 Waterloo (Waterloo): Operator identity of the ITA establishment "Waterloo", 300 Ansborough Ave (NAICS 326199/423930).
- QMS-IA-50 Adair Manufacturing Plant (Adair): Operator of the "Adair Manufacturing Plant", 1000 Flag Road (dd2 suggests Leviat/Composite Technologies; not confirmed).

**REJECT (deciding fact):**
- QMS-IA-04 ROUSSELOT, INC.: Gelatin/collagen producer, not polymer manufacturing: ITA CY2025 NAICS 311611/311999/325998 (fetched 2026-11-04).
- QMS-IA-10 HACH COMPANY: Water-analysis reagents and instruments, not polymer: ITA CY2025 NAICS 325998 (fetched 2026-11-04).
- QMS-IA-12 AJINOMOTO HEALTH & NUTRITION NORTH AMERICA, INC.: Amino acids/biochemicals, not polymer: ITA CY2025 NAICS 325199 (fetched 2026-11-04).
- QMS-IA-15 COLORBIOTICS: Colorants for mulch/landscape, not polymer: ITA CY2025 NAICS 325130 (fetched 2026-11-04).
- QMS-IA-18 REG MASON CITY: Biodiesel, not polymer: ITA CY2025 NAICS 325199 (fetched 2026-11-04).
- QMS-IA-19 BARTON SOLVENTS INC - BETTENDORF FACILITY: Solvent distributor: ITA CY2025 primary NAICS 424690 (fetched 2026-11-04).
- QMS-IA-20 BECKER UNDERWOOD INC: Seed colorants/agri-biologicals, not polymer: ITA CY2025 NAICS 325130/325320 (fetched 2026-11-04).
- QMS-IA-21 CFI SALES INC: Tire retreading/sales, not manufacturing polymer (NAICS 326212): ITA CY2025 record (fetched 2026-11-04).
- QMS-IA-32 CRYOTECH DEICING TECHNOLOGY: Deicing chemicals, not polymer: ITA/FRS NAICS 325998 (fetched 2026-11-04).
- QMS-IA-48 Kent Pet Group, Inc.: Pet litter/products, not polymer: ITA NAICS 325998 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/ia-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
