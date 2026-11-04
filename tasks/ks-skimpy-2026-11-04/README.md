**Judgment calls (flagged first):** Held matches not re-created: Spears Caney (SITE-005204, 1220 vs 1200 S State), KBK Rush Center (SITE-005229, North Facility - possible second plant), Goodyear Topeka (SITE-002865), Sherwin-Williams Andover (SITE-004938), Onyx Belvue (SITE-005790), Great Lakes Polymer Kingman (SITE-005872). Wichita Fiber Glass Systems left uncertain: NOV org pending in PR #57. Camso Emporia Overlander site created under ORG-003093 as a second Emporia site (held one is 1601 E South Ave). Calmar Winfield placed under ORG-000278 Silgan Dispensing (Silgan bought the WestRock/MWV dispensing business) - integrator check. Marvin KC under ORG-003330 Marvin Composites. Central Plastics McPherson created new, not linked to GF Central Plastics (OK). Carlisle Power Transmission Fort Scott left uncertain (operator now likely Timken).

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for KS: 44 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | KS sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 44 | 35 | 4 | 5 | 18 | 0 / 29 | 48 -> 77 | 23 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-005003..ORG-005020, SITE-006281..SITE-006309, EVD-025960..EVD-026299.

**STILL_UNCERTAIN (settling fact):**
- QMS-KS-07 AIROSOL CO INC (Neodesha): Whether Airosol Co. Neodesha formulates polymer products or only fills aerosols (NAICS 325998).
- QMS-KS-12 CARLISLE POWER TRANSMISSION PRODUCTS (Fort Scott): Current operator (Timken Belts or Carlisle) of the Fort Scott power-transmission belt plant, 4505 Campbell Dr.
- QMS-KS-13 A & M PRODUCTS (Spring Hill): What A & M Products Spring Hill makes (NAICS 325998/327992) - polymer or not.
- QMS-KS-40 Wichita Fiber Glass Systems (Wichita): Wichita Fiber Glass Systems (ITA 1459584 + OSHA 345572960) is witnessed, but the NOV Inc. parent org is pending in PR #57; settling fact: PR #57 merge.
- QMS-KS-41 Main RC (Olathe): Operator identity and products of "Main RC", 1001 W Highway 56, Olathe (NAICS 326199).

**REJECT (deciding fact):**
- QMS-KS-14 HARCROS CHEMICALS INC. - KANSAS CITY: Chemical distributor, not polymer manufacturing: ITA CY2025 record NAICS 424690 (fetched 2026-11-04).
- QMS-KS-22 HODGDON POWDER COMPANY: Smokeless powder (explosives), not polymer: ITA CY2025 record NAICS 325920 (fetched 2026-11-04).
- QMS-KS-23 JACAM MFG. - ORGANOCLAY PROCESSING: Organoclay (modified clay minerals), not polymer: ITA CY2025 record NAICS 327992/424690 (fetched 2026-11-04).
- QMS-KS-24 TIMILON CORPORATION: Inorganic adsorbent chemicals, not polymer: ITA CY2025 record NAICS 325180 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/ks-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
