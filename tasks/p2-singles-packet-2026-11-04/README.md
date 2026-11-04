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

## Counts (rows), pass 11
| Verdict | Rows |
|---|---|
| VERIFIED | 161 (149 distinct sites) |
| REJECT | 71 |
| STILL_UNCERTAIN | 163 |
| ALREADY_HELD | 29 |

Not yet witness-checked: CHECK 0, stale (no federal activity since 2019) 0, small inspection-only 0. Their settling facts are by class.

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
- Pass 4 (remaining CHECK rows):
  - Two-federal-source VERIFIED rows use two different agencies or programs: DE-014 (EPA TRI + FRS) and UT-143 (FDA + EPA TRI).
  - NV-120 CPI Trade Dr is VERIFIED by address under PLI, which bought it in 2015; the operator change is flagged.
  - RI-201 SpillTech: the address comes from the company's own Chemtex acquisition notice.
  - UT-234 Liberty Tire: tire recycling counted as polymer.
  - NH-040 Carbon Felt: carbon composites counted.
  - DE-001 FBK/D&B: street number differs.
  - Out-of-scope or no-plant rejects use the company's own site as the dated (fetch-date) fact: UT-160 JM Eagle (distribution center), UT-236 Champion (service location), NH-198 Integra (warehouse, per its 2025 environmental report).

## Pass 5 judgment calls
- DE-019 is VERIFIED on Qnity's own Bellevue Rd CMP pages. Its filed No. 50 may be on the same campus as DE-014 (451) and DE-018 (575). They are not merged; flagged.
- DE-016 GE solar and DE-025 Chemours TiO2 are rejected on dated closures; both are also out of polymer scope.
- NH-058 PFE is rejected on its own services page: it does testing and consulting, not manufacturing.
- NH-048 Vaupell and NH-060 Haydon Kerk: the company's own site gives a different street in the same town. Both are STILL_UNCERTAIN, with the date they left the filed street as the settling fact.


## Integrator application (2026-11-04, PR pending)
Applied: 151 establishments created (149 from VERIFIED rows after address-merge groups, plus 5 integrator-ruled rows below, minus 3 fence holds). 15 sites landed under existing orgs; the rest created new orgs. All rows tier B (own-site witness) or C, evidence rows carry the packet witness.

Integrator rulings on the packet's open questions:
- UT-230 Danone (West Jordan): IN — captive cup thermoforming is in-house polymer manufacturing (Catexel precedent); site created Ring 3, tier C, on the Utah DAQ permit.
- ID-252 Badraun/EPSCO: IN — powder-coating job shop, Ring 3 per the 2026-10-29 B5 ruling; created on the successor's own-site witness. NV-105 Armorcoat: scope ruled IN (Ring 3) but evidence is directories-only — stays STILL_UNCERTAIN; settling fact is now evidence-only (a company witness).
- NV-119 Sterling Nevada (plain concrete): REJECTED — no polymer witness (contrast NV-103 Armorock polymer concrete: scope IN, stays uncertain on evidence).
- UT-149 May Foundry: REJECTED — metal foundry, no polymer operation witnessed. NH-067 Janco Electronics: REJECTED — contract electronics assembly is not polymer processing. NV-363 Somar: REJECTED — general X-ray-supplies wholesale, not polymer-goods trade.
- UT-412 LGG Industrial: IN — hose/gasket distribution is polymer-goods distribution (Summit Glove precedent, Ring 3); created as a distribution branch on its own location page.
- UT-132 + UT-415 (Whitewater, Lindon): DUPLICATES of SITE-008188, created from PR #77 — no new rows. UT-161 + UT-162 (5574 Leo Park Rd): ruled ONE establishment (T.J. Products / Industrial Rubber Products Utah), still STILL_UNCERTAIN — directories only.
- NV-332 Peterson Products: VERIFIED at the company's own current address, 15 Airpark Vista Blvd (the filed No. 10 is the 2015 address). UT-405 Magic Vac: created at its own current Woods Cross address; the filed Midvale establishment was not created.
- NV-345 TIKE dba Welch Plastics: VERIFIED; its Chapter 11 filing (2:25-bk-16736, 2025-11-06) is noted on the site record — a filing is not a closure. UT-408 BestDrive: stays STILL_UNCERTAIN (undated inactive listing is not a deciding fact).
- HELD under the owner fence (2026-10-29: DuPont/Qnity + Rohm and Haas until the spin settles): P2-DE-014, P2-DE-015, P2-DE-019 — not created. Flagged to the owner: the Qnity spin completed 2025-11-01, so the fence's condition may have lapsed.
- Counties are blank on the created sites (the frame extract carried none for these rows; not guessed).
