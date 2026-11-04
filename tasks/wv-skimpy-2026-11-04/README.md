**Judgment calls (flagged first):** Niche Polymer org placed in the MD shard (own-site HQ Columbia MD). Silgan Triadelphia placed under held ORG-001115 Silgan Plastics; Logoplaste Inwood under held ORG-000935 (named "Logoplaste Lima" - integrator may rename to group); ISCO Martinsburg under ORG-000905 as HDPE pipe fabrication; Allnex Belmont verified ring 2 on parent identity (coating-resin company) though site NAICS is 325199; TROY Group verified ring 2 (MICR toner/inks); several 325199/325998 chemical sites left uncertain rather than rejected.

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for WV: 22 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | WV sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 22 | 15 | 2 | 5 | 8 | 0 / 15 | 31 -> 46 | 12 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004881..ORG-004888, SITE-006074..SITE-006088, EVD-023746..EVD-023739.

**STILL_UNCERTAIN (settling fact):**
- QMS-WV-05 CHEM-PAK INC (Martinsburg): Whether Chem-Pak formulates polymer coatings/adhesives at 242 Corning Way or only fills aerosols (NAICS 324191/325510/325998 mixed).
- QMS-WV-08 SI GROUP INC - SOUTH PLANT (Morgantown): Which products SI Group makes at the Morgantown South Plant (polymer additives/resins vs other intermediates; NAICS 325199).
- QMS-WV-09 ICL-IP AMERICA INC. GALLIPOLIS FERRY SITE (Gallipolis Ferry): Whether ICL-IP Gallipolis Ferry products are polymer flame-retardant additives (NAICS 325199 does not say).
- QMS-WV-12 UNION CARBIDE CORPORATION - UCC TECHNOLOGY PARK OPERATIONS (South Charleston): Whether UCC Technology Park South Charleston runs polymer production (secondary NAICS 325211) or only R&D/pilot operations.
- QMS-WV-14 AC & S, INC. (Nitro): What AC & S makes at 150 Plant Rd, Nitro (NAICS 325199/325998 - polymer or not).

**REJECT (deciding fact):**
- QMS-WV-10 INNOVATIVE WATER CARE, LLC.: Pool/water sanitizer chemicals (calcium hypochlorite), not polymer: ITA CY2025 record filed 2026-08-04 NAICS 325180 inorganic chemicals.
- QMS-WV-18 Westlake Natrium, LLC: Chlor-alkali (chlorine/caustic) plant, not polymer: ITA CY2025 record filed 2026-01-30 NAICS 325180.

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/wv-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
