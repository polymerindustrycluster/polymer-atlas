**Judgment calls (flagged first):** Held, not re-created: Colormasters Albertville (SITE-003970), Aptar CSP Auburn (SITE-003048), AlphaPet Decatur (SITE-003956), Tarkett Florence (SITE-005840), SABIC Burkville/Lowndesboro 1 Plastics Dr (SITE-005093), HB&G Troy (SITE-005852). Hwaseung Automotive 101 Development Dr Enterprise created as a second site under ORG-004397 HS Automotive Alabama (held site is 100 Sonata Dr). Heritage Plastics Sylacauga linked to ORG-003188 Heritage Plastics (Picayune MS) on name match - integrator check. Letica Lanett placed under ORG-002544 Berry Global (FRS name says Berry subsidiary). KW Plastics container facility created as a second Troy site under ORG-003189. Indorama Decatur rejected as monomer (PTA) chemicals on primary NAICS; Indorama Athens recycling kept under ORG-004245. Concours Technology (mold maker, 333511) carried at ring 2 as mold_tool_making. Lenzing Axis lyocell (cellulosic fiber) left uncertain on scope.

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for AL: 78 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | AL sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 78 | 58 | 11 | 9 | 29 | 0 / 52 | 56 -> 108 | 47 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-005042..ORG-005070, SITE-006348..SITE-006399, EVD-026730..EVD-027319.

**STILL_UNCERTAIN (settling fact):**
- QMS-AL-01 BRUDERER INC (Huntsville): Whether Bruderer Inc. Huntsville makes plastic products (ITA NAICS 326199) or only builds/services stamping presses (333513).
- QMS-AL-09 LENZING FIBERS INC. (Axis): Whether Lenzing Axis (lyocell cellulosic fiber, NAICS 325220) is in atlas polymer scope.
- QMS-AL-22 BASF CORP (Mc Intosh): Whether BASF McIntosh makes any polymer (FRS lists 325211) or only chemicals (primary 325199).
- QMS-AL-30 LOUISIANA-PACIFIC CORP (Selma): What Louisiana-Pacific Selma makes under NAICS 325991 (resin compounding or wood products only).
- QMS-AL-37 PEMCO (Leesburg): Whether Pemco Leesburg makes any polymer coating or only porcelain-enamel frit (NAICS 327112/325510).
- QMS-AL-43 NELSON BROTHERS SPECIALTY CHEMICALS, LLC (Parrish): Which polymer products, if any, Nelson Brothers Specialty Chemicals Parrish makes under NAICS 325211 (vs explosives 325920).
- QMS-AL-52 MOBILE ROSIN OIL CO INC (Mobile): Whether Mobile Rosin Oil makes rosin resin (FRS 325211) or only rosin chemicals (325191).
- QMS-AL-53 PLASMINE TECHNOLOGY INC (Bay Minette): Which Plasmine Technology Bay Minette products, if any, are polymers (FRS lists 325211; primary 325998).
- QMS-AL-64 KINPAK, INC. (Montgomery): Whether Kinpak Montgomery makes polymer (FRS lists 325211) or only blends and packages fluids.

**REJECT (deciding fact):**
- QMS-AL-16 WESTPOINT STEVENS-GREENVILLE: Home textiles plant, not polymer: ITA CY2025 primary NAICS 314120 (fetched 2026-11-04).
- QMS-AL-21 INDORAMA DECATUR SITE: Aromatic monomer (PTA) chemical plant: ITA CY2025 primary NAICS 325199, not polymer manufacturing (fetched 2026-11-04).
- QMS-AL-32 TATE & LYLE SUCRALOSE INC: Sucralose sweetener, not polymer: ITA CY2025 NAICS 325998 (fetched 2026-11-04).
- QMS-AL-39 NELSON BROTHERS, LLC - SAMOSET FACILITY: Explosives plant: ITA CY2025 NAICS 325920 (fetched 2026-11-04).
- QMS-AL-40 LEMOYNE SITE: Inorganic chemicals: ITA CY2025 primary NAICS 325180 (fetched 2026-11-04).
- QMS-AL-46 OCI ALABAMA LLC: Inorganic chemicals: ITA CY2025 primary NAICS 325180 (fetched 2026-11-04).
- QMS-AL-57 WATER SCIENCE TECHNOLOGIES LLC: Water-treatment chemicals: ITA CY2025 NAICS 325998 (fetched 2026-11-04).
- QMS-AL-58 YS, INC.: Inorganic chemicals: ITA CY2025 NAICS 325180 (fetched 2026-11-04).
- QMS-AL-59 GOODYEAR AUTO SERVICE CENTER #2293: Retail auto service center: ITA CY2025 NAICS 441330 (fetched 2026-11-04).
- QMS-AL-73 Archon Fibers LLC: Carpet/textile fiber mill: ITA primary NAICS 314110 (fetched 2026-11-04).
- QMS-AL-74 Ultratec Special Effects: Pyrotechnics: ITA primary NAICS 325920 (fetched 2026-11-04).

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/al-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
