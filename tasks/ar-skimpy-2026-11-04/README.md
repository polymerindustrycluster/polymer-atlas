**Judgment calls (flagged first):** United Industries Bentonville and Rogers placed under one new org; Cooper Tire Texarkana matched to held SITE-002873 (not re-created); Georg Fischer Little Rock placed under ORG-002291 Georg Fischer LLC (GF Harvel) - integrator check; BPREX Delta under ORG-002544 Berry; Cryovac Rogers under ORG-000566 Sealed Air; Creative Foam Products (NLR) and River Bend Industries (Fort Smith) created new, NOT linked to held Creative Foam Corp (OH) / River Bend Molding (Ozark) - names differ.

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for AR: 36 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | AR sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 36 | 27 | 3 | 6 | 12 | 0 / 26 | 41 -> 67 | 26 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004929..ORG-004940, SITE-006164..SITE-006189, EVD-025574..EVD-024859.

**STILL_UNCERTAIN (settling fact):**
- QMS-AR-21 ENVIRAPAC MONTICELLO, LLC (Monticello): What Envirapac Monticello makes (NAICS 325998/321999) - polymer or not.
- QMS-AR-24 BUILDING MATERIALS MANUFACTURING LLC. (Arkadelphia): Operator identity (GAF/BMCA or other) and product of Building Materials Manufacturing LLC Arkadelphia (NAICS 325991).
- QMS-AR-25 LYCUS LTD. (El Dorado): What Lycus Ltd. makes at El Dorado (NAICS 325199/325411) - polymer or not.
- QMS-AR-26 ECOTECH ENTERPRISES, INC (Scott): Whether Ecotech Enterprises Scott manufactures polymer products or distributes (NAICS 325998/424690).
- QMS-AR-34 Little Rock - 03 (Little Rock): Operator identity of ITA establishment "Little Rock - 03" at 6901 Lindsey Rd (NAICS 326199).
- QMS-AR-35 Production Assistance Link (North Little Rock): Whether Production Assistance Link NLR manufactures polymer products (NAICS 325998).

**REJECT (deciding fact):**
- QMS-AR-08 LANXESS CORP - CENTRAL PLANT: Bromine and inorganic chemicals, not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).
- QMS-AR-17 ENVIRO TECH CHEMICAL SERVICES - PLANT 6: Water-treatment/inorganic chemicals, not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).
- QMS-AR-23 GREAT LAKES CHEMICAL WEST PLANT: Bromine chemicals, not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/ar-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
