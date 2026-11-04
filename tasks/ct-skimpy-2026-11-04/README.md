**Judgment calls (flagged first):** LATICRETE Bethany left uncertain: its org was created in unmerged PR #69 (OR) - no duplicate minted; Reflexite Avon placed under ORG-003996 ORAFOL Americas (ORAFOL acquired Reflexite) - integrator check; Rexam Dispensing Thomaston left uncertain (current operator after Rexam exits); Rogers Moosup created as a third Rogers site distinct from held Killingly/Woodstock; Dymax created new (not merged with held Bomar Specialties, a different Torrington site); CKS Packaging and Flextronics orgs placed in CT shard at plant city - integrator check; Photronics rejected (photomasks).

**Base head:** origin/main `8a0f91d`. Two-source queue (QUEUE_MULTISOURCE) for CT: 42 rows considered, queue exhausted; no single-source burn-down.

| considered | VERIFIED | REJECT | STILL_UNCERTAIN | new orgs (tier C) | new sites B / C | CT sites before -> after | FRS links | paid calls |
|---|---|---|---|---|---|---|---|---|
| 42 | 31 | 2 | 9 | 25 | 0 / 31 | 46 -> 77 | 21 | 0 |

**ID ranges used (tiled from the ledger, no main rescan):** ORG-004978..ORG-005002, SITE-006250..SITE-006280, EVD-027320..EVD-025959.

**STILL_UNCERTAIN (settling fact):**
- QMS-CT-04 BRAND NU LABORATORIES INC (Meriden): Whether Brand Nu Laboratories Meriden makes polymer products (NAICS 325998/424690).
- QMS-CT-10 REXAM DISPENSING SYSTEMS (Thomaston): Current operator of the former Rexam Dispensing Systems plant at 60 Electric Ave, Thomaston (FRS/ITA name is legacy).
- QMS-CT-13 MACDERMID ENTHONE (West Haven): Whether MacDermid Enthone West Haven makes polymer products (NAICS 325998 plating chemicals).
- QMS-CT-17 DREW MARINE USA (Waterbury): Whether Drew Marine Waterbury makes polymer products (NAICS 325998/325510).
- QMS-CT-18 MILLER STEPHENSON CHEMICAL (Danbury): Whether Miller-Stephenson Danbury manufactures polymer products (release agents/coatings) or distributes (NAICS 325510/424690).
- QMS-CT-23 AZURE WATER SERVICES (West Haven): Whether Azure Water Services West Haven makes any polymer products (NAICS 325998 water treatment).
- QMS-CT-27 P I LIQUIDATING, INC. (Prospect): Whether the Prospect EPS plant (FRS name "P I Liquidating, Inc.") still operates and who runs it.
- QMS-CT-30 LATICRETE International Inc - Bethany (Bethany): LATICRETE Bethany HQ/plant (ITA 1454525 + OSHA 345693337) is witnessed, but the LATICRETE org is pending in PR #69; settling fact: PR #69 merge, then add the site under that org.
- QMS-CT-37 Phoenix Products Company (Terryville): Whether Phoenix Products Terryville manufactures polymer products (NAICS 325998/424690).

**REJECT (deciding fact):**
- QMS-CT-12 PHOTRONICS, INC.: Photomasks (semiconductor), not polymer: ITA CY2025 record NAICS 325992/334119 (fetched 2026-11-04).
- QMS-CT-24 DYNO NOBEL: Explosives, not polymer: FRS 110000315409 fetched 2026-11-04, NAICS 325920, Dyno Nobel.

Tier rules: new orgs tier C; federal-only sites tier C; tier B only with an own-site witness on a held parent. Registry links: FRS on every site with an FRS id. Licensed sources and CRM not used. validate.py passed. Packet: `tasks/ct-skimpy-2026-11-04/` (verdicts.csv, build.py, frs_fresh_2026-11-04.json).
