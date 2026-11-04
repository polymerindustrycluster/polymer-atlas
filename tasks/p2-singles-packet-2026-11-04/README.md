# P2 single-source federal candidates: UT/DE/ID/NH/RI/NV (packet-only)

Base: main 9708c3a. No data files are edited. All evidence was fetched on 2026-11-04.

## Method
1. Rebuilt the federal frame with `tasks/federal-frame-2026-11-04/build_frame.py`. The patched copy is `build_frame_patched.py`, with only the MAIN/OUT paths changed. Inputs are the 2026-11-01 echo-frs-spine, osha-ita and osha-spine packets.
2. Kept the single-source classes C_ECHO, C_ITA and C_INSP for the 6 states, restricted to polymer NAICS (326*, 325211/212/510/520/910/991). That gives 424 rows (pid `P2-ST-nnn`).
3. Ran a name+city hint check against main because the frame dedupe misses held sites. 29 rows are ALREADY_HELD; see `held_map.txt` for the pid → SITE mapping.
4. Triage:
   - X_nonmfg (21): stores, distribution centres, banks.
   - U_stale (98): latest activity before 2019, or undated.
   - U_small (81): INSP-only rows with fewer than 20 employees.
   - CHECK: everything else.
5. Witness-checked the own sites of the largest CHECK rows, ordered by employees then recency, plus their address-duplicates. That covered 36 rows. The other CHECK rows are STILL_UNCERTAIN, each with a settling fact.

## Counts (rows), pass 3
| Verdict | Rows |
|---|---|
| VERIFIED | 85 (73 distinct sites) |
| REJECT | 37 |
| STILL_UNCERTAIN | 273 |
| ALREADY_HELD | 29 |

Witness-checking went largest employers first, down to roughly 20 employees in the CHECK class. Rows still marked "Not witness-checked yet" carry the settling fact "own-site page naming the plant, or a second federal source".

## Rulings applied (integrator, 2026-11-04)
- Hiring-site postings are not witnesses. Latham (UT-378/220), Zenith/Mayzon (DE-243), Cornerstone (NH-180) and Corning (UT-217) moved back to STILL_UNCERTAIN.
- Address-first dedupe is accepted. Each merge is flagged in the `address_merge_group` column.
- Wrong-state rows carry `correct_state`: ID-172→IA, NV-207→AZ, NH-188→MA.

## Other judgment calls
- UT-138/238 (Convergent) defers to PR #77.
- Autajon Nashua (NH-258) is rejected as out of polymer scope, based on its own site's product description.
- Chem-Tainer Cranston (RI-260) is rejected on its RI Secretary of State revocation dated 2020-12-30.
- Fetch failure was treated as availability, not absence. No licensed sources were used.
- Additional address merges (all flagged in `address_merge_group`): UT-134/380 NRP Jones, UT-226/397 Eric'sons, UT-231/400 Blue Diamond, NH-261/264 Grimco, NH-064/268 Spartech-Tufpak, NV-304/321 Laddawn, UT-228/394 WCI/Sheergard.
- City-only own-site matches accepted as VERIFIED, with the street unconfirmed: ID-249 Cordova, NH-265 American Durafilm.
- Mixed or partial polymer share accepted as VERIFIED: UT-384 MIRO, UT-393 WhiteClouds, NV-312 Click Bond (adhesive-bonded fasteners), DE-245 Wilmington Fibre (non-metallic fabrication), RI-274 Fielding (zinc + plastic).
- NH-268/064 Spartech-Tufpak is VERIFIED on two federal sources (EPA ICIS-Air + OSHA), not on its own site.
- State-agency pages (NV GOED, Nevada OSHA review board, Utah DAQ) were not counted as federal or own-site witnesses (NV-311, NV-315, UT-230).
- UT-230 (Danone yogurt plant, captive cup thermoforming) needs a scope ruling.
- RI-271 RBC Warwick is rejected on its RI SOS dissolution dated 2020-12-17. Cranston is a lead.
