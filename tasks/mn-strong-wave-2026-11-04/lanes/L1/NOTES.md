# Lane L1 notes (STRONG wave, MN, 2026-11-04)

16 clusters in, 16 verdict rows out (`verdicts.csv`). No `data/` edits, no git.

## Counts
- VERIFIED_NEW_ORG: 12 (00164, 00076, 00113, 00045, 00303, 00253, 00246, 00192, 00309, 00283, 00083, 00340)
- VERIFIED_NEW_SITE: 3 (00001 under ORG-003178, 00058 under ORG-003943, 00127 under ORG-001093)
- REJECT: 1 (00361 Apex Water and Process, scope)
- STILL_UNCERTAIN: 0
- DUPLICATE_OF: 0

## Tier convention used
`tier` is the record-level tier the brief assigns: NEW_ORG rows carry C. Each NEW_ORG note states "site-level tier B" where a federal source plus an own-site witness exist, so the integrator can set the site row to B and the organization to C. NEW_SITE rows carry B (own-site witness) or C (00001, federal plus state regulator only).

## Quote handling
Every `own_quote` was copied from a page I fetched. A script re-fetched each `own_url` and checked the words:
- Visible-text match: all except those below.
- 00303 ProMed: the quote is the page's meta/og description (raw HTML only), not visible body text.
- 00253 Steinwall: scripted re-fetch failed (connection closed); the text was copied from the TinyFish fetch of the same page.
- 00283 Action Plastics: the quote is the home page `<title>`; it matched visible text in the check.
- 00001 3M: no own-site quote (see below).

## Items for the integrator
1. HQ disagreement (00058): wilbertplastics.com prints corporate HQ Huntersville, NC; ORG-003943 carries Belmont, NC. White Bear Lake is on the own-site thermoforming page, but the street comes from federal rows only.
2. Two-org dedupe hit (00058): trade name 'Wilbert Plastic Services' matches ORG-003943 (Wilbert, Inc., NC) and ORG-001197 (EPC, Bellevue OH). I chose ORG-003943 from its recorded adjudication (EPC bought only the two automotive injection plants).
3. Parent-vs-site choice (00127): ITA says `RTP COMPANY DBA WIMAN CORPORATION` and wimancorp.com calls RTP its parent, so I placed it under ORG-001093 (RTP Company). A separate Wiman org with RTP as parent is a valid alternative. Street corrected to the own-site form (Industrial Blvd, federal says Road).
4. Same-address pair (00192): Federal Package Network (fplabs.com) and Federal Plastics Corp (federalplasticscorp.com) both claim 8100 Powers Blvd; Flextool Corp is the dba parent in federal rows. One site, one org recorded; integrator to decide whether Federal Plastics Corp is a second org or a brand.
5. 3M (00001): only federal rows plus MPCA ("produces ... abrasives, chemicals, polymers, resins, and tapes"). 3M's own pages name Cottage Grove only for "Insulation and emission control products". 3M announced exit of all PFAS manufacturing (fluoropolymers included) by end of 2025; no closure of the site found, and a 2026-05-17 MN suit still calls it a manufacturing plant. Processes, materials and NAICS left blank.
6. Scope calls that rest on existing rulings: 00045 Ceramic Industrial Coatings (wood and industrial coatings; Ring 2 coatings rule; binder chemistry not stated on the pages; Canlak Coatings Inc. bought it 2023-11-29, parent unheld) and 00164 pinta acoustic (melamine foam fabricator; Ring 1 foam fabrication). 00361 Apex was a scope REJECT (water-treatment services, no polymer); no owner ruling needed unless someone argues water-treatment polymers are in scope.
7. Counties not in the federal row and supplied from the city: Remer (Cass), Rogers and Hopkins and Plymouth (Hennepin), Anoka, Coon Rapids (Anoka), St. Michael (Wright). Integrator to confirm.
8. Entity-name uncertainty: 00083 (federal LLC, BBB lists Inc.), 00340 (federal Plasman Precision Parts LLC, D&B says USA Inc., site brand is TPM/Thermotech Precision Molding). 00340 HQ left blank because the site never states one; 3 of its 4 plants are in Mexico.
9. Other sites seen but not in this packet: Stern Rubber (Aitkin, plus a stated "three facilities in Minnesota"), Wiman HQ at 4110 Clearwater Rd Saint Cloud, ProMed (Maple Grove, Dorado PR), Steinwall warehouse at 11225 Xeon St NW.
10. No closures found for any cluster. No Form 5500 check was needed (no REJECT for closure).

## Dedupe record
`atlas.py dedupe-check` (name + street, all shards): zero hits for 15 clusters; step-2 hits for 00058 only. 00001 resolved from the cluster's own `fusion_refs` (ORG-003178; its MN sites are Maplewood, Fairmont, Hutchinson only). Brand/domain/common-name sweeps of the organization and site shards (rg) found nothing for: pinta, sonex, illbruck, robinson rubber, stern rubber, zhongli, apex water, ceram-traz, canlak, promed, steinwall, tsi plastics, federal plastics/package, flextool, fplabs, midstate, action plastics, quality extrusion, plasman, tpm, thermotech. Wiman hit RTP Company (ORG-001093).

## Fetch notes
Direct fetches (TinyFish and a local stripper) worked for all own sites. Blocked: sternrubber.com /about-stern-rubber and /contact (bot wall; other Stern URLs fetched fine), promedmolding.com /contact and /about (bot wall; blog and home pages fine), pca.state.mn.us (Radware; read through Jina), 3m.com OEM resources page (403; read through Jina). A failed fetch was never used as evidence.
