**Judgment calls (flagged first):** No Cray Valley row is in the CO two-source queue (hold respected by default). Lexmark org placed in KY shard and Carestream org in NY shard (HQ researcher knowledge) - integrator check; Lexmark Longmont and Carestream Windsor verified ring 2 (toner / coated film); Plastics Design & Mfg Denver and Englewood placed under one new org; Pretred Aurora matched to held SITE-004338 (held row has no street) - not re-created; held KONG org ORG-001391 shows county Stark for Golden (pre-existing data issue, not edited).

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for CO: 30 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | CO sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 30 | 24 | 2 | 4 | 15 | 0 / 23 | 24 -> 47 | 17 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004914..ORG-004928, SITE-006141..SITE-006163, EVD-025292..EVD-024579.

**STILL_UNCERTAIN (settling fact):**
- QMS-CO-04 BOULDER SCIENTIFIC CO - MEAD FACILITY (Mead): Whether Boulder Scientific Mead makes polymer-scope products (polyolefin catalysts are not polymers; NAICS 325199/325412).
- QMS-CO-07 ERA - A WATERS COMPANY (Golden): Whether ERA (Waters) Golden makes any polymer products (NAICS 325998 reference standards).
- QMS-CO-10 MOLECULAR PRODUCTS - LOUISVILLE PLANT (Louisville): Whether Molecular Products Louisville makes polymer products (NAICS 325998; CO2 absorbents are inorganic).
- QMS-CO-11 BOULDER SCIENTIFIC COMPANY LLC (Longmont): Whether Boulder Scientific Longmont makes polymer-scope products (NAICS 325199).

**REJECT (deciding fact):**
- QMS-CO-05 KMG ELECTRONIC CHEMICALS INC: Electronic-grade acids (inorganic), not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).
- QMS-CO-14 JORDAN PROCESS LLC: Medicinal/botanical chemicals, not polymer: ITA CY2025 record NAICS 325411 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/co-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
