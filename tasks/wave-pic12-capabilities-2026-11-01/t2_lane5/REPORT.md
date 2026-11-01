# Lane t2-5 packet: PIC-12 capability wave, tranche 2 (2026-11-01)

**A packet, not a data change.** No `data/` edit, no ID allocation, no commit or push. Every row in `packet.csv` is `own_site`, carries the URL actually fetched and a quote of 25 words or fewer, and the quote was checked programmatically as a whitespace-normalised substring of the fetched page text (`build.py` refuses to write on any miss, over-long quote, off-vocab value, scope/ID mismatch or duplicate). Vocabulary: `docs/schema/vocab.json` v1.7.6. Org-scope rows use the ORG id as `record_id`. Scratch text and helper scripts are in `/tmp/claude-0/wave/t2_lane5/` only.

## Results (units stated)

**Sites verdicted (unit: assigned Ohio site rows, n=54):** VERIFIED 18, STILL_UNCERTAIN 36, REJECT 0. VERIFIED = at least one in-vocab value at **site** scope. No REJECT: nothing found was a dated closure or non-establishment fact; every unreachable site is an availability failure only. No Form 5500 check was needed or run.

**In-vocab values proposed (unit: packet rows, one per record, field, value): 281.**

| field | site scope | org scope | total |
|---|---|---|---|
| processes | 38 | 39 | 77 |
| materials | 39 | 47 | 86 |
| markets_served | 35 | 66 | 101 |
| certifications | 8 | 9 | 17 |
| **all** | **120** | **161** | **281** |

Plus **9 off-vocab rows** (`*_other_note`, OFF-VOCAB, row verdict STILL_UNCERTAIN): processes_other_note 8, markets_other_note 1. Row-level: 271 in-vocab rows VERIFIED, 10 STILL_UNCERTAIN (all certification rows whose edition is not named or looks wrong, see below). Packet total 290 rows. Org-scope rows span 27 organizations.

**v1.7.6 terms used (rows):** automotive_unspecified 14, medical_healthcare_general 7, food_processing_foodservice 2, thermoforming_unspecified 1, asa 1. Not met: tire_rubber_goods, specialty_elastomers, iso_45001, iso_17025.

**Measured yield**
- Site-scope capability values (processes, materials, markets): 112/54 = 2.1 per assigned site; 112/18 = 6.2 per VERIFIED site. All in-vocab values, all scopes: 281/54 = 5.2 per assigned site.
- Sites with at least one `markets_served` value: **13/54 (24%) at site scope; 38/54 (70%) counting org scope**.
- Sites with at least one site-scope `processes` value: 14/54 (26%).
- Sites with at least one in-vocab value at some scope: 44/54 (81%). The 10 with none: HEXPOL, SKF, GRAFIX, Sealed Air, Saint-Gobain, ECM, Raydar, Sietins (all unreachable), Sare (redirected to another company), ValenSil (off-vocab only).
- VERIFIED rate 18/54 = 33% (tranche 1 lane 4 was 50%; this lane had many multi-plant parents and 8 unreachable sites).

**Plant-specificity.** Site scope only where the page prints one address or names the plant: single-address companies (Akron Porcelain, Design Molded, Rubber Associates, American Foam, DermaMed, Chemsultants, Astra, V&A Process, Enpac, Foundation, IT Plastics, Sure-Foot, ValenSil), JK Plastics (one building described), Carbon Polymers (ISO 9001 compounding facility "located in Lodi, OH"), Flambeau (July 2023 news names the Sharon Center plant; blow molding), Robin Fredericksburg (locations page lists certificates per plant), Plas-Mac (footer address and certificates), Novis Works ("located in Northeastern, Ohio", single-location reading). Everything else is org scope, including every value of GEON, Americhem, Valtris, Aptyx, Henkel, DayGlo, Universal Plastics, Intralox. Where the pages print no address (ABC Plastics, B.B. Bradley, Polystar, Mercury Plastics, Koroseal, Sprosty) I did **not** assume single location and used org scope.

## Fetches (unit: fetch attempts, including WebFetch)

- **288 attempts total across 54 sites, 5.3 per site, maximum 6; the 6-fetch cap was respected for every site.**
- **Self-inflicted tooling race (disclosed):** in my first second-round wave (124 fetches) I ran several fetches for the same site in parallel; they shared a file counter, so their saved text overwrote each other and was unusable. I moved those files aside (`/tmp/claude-0/wave/t2_lane5/old_race/`), quoted nothing from them, and re-fetched serially with a per-site lock. Those 124 attempts still count against each site's 6, so the usable-content fetch count is 164 and many sites got only 2 useful pages beyond the home page. This is the main reason several sites ended at org scope (contact/locations pages lost), and several STILL_UNCERTAIN settling facts read "contact page lost to a tooling race". Valtris (two site rows, one org) was also fetched twice for the same pages.
- Hard availability failures (non-200 or content-free 200): **19/288 = 6.6% of all attempts; 19/164 = 11.6% of usable-wave attempts.** Detail: GRAFIX Cloudflare 403; Sealed Air Cloudflare challenge 403; Saint-Gobain bot verification 403; ECM Cloudflare 1014/403 (curl and WebFetch); HEXPOL CONNECT 502 on apex, TLS handshake failure on www, WebFetch ENOTFOUND; Sietins /about 403; SKF JS shell (3 characters); Raydar JS redirect to /lander (empty); Impact Sleeves one 403 (retried on another path); Ergomat one guessed 404; Intralox one empty page.
- Content-free or untrustworthy 200s: SKF, Raydar, Sietins (apex serves unrelated spam-titled content).
- Sites with no usable own-site content from any route: **8/54 (15%)**: HEXPOL, SKF, GRAFIX, Sealed Air, Saint-Gobain, ECM, Raydar, Sietins. All STILL_UNCERTAIN; none is evidence of closure. WebFetch was tried once each on HEXPOL, GRAFIX and ECM only: GRAFIX loaded as a summary (slitting, sheeting, lamination of film and sheet), which is **not quotable and not used**.
- **Not done:** no bot-wall workaround of any kind (no user-agent change, no TLS bypass, no captcha handling).

## Vocabulary gaps met (owner rulings; flagged in `*_other_note`, not settled)

- **Wax / plastic investment-casting pattern injection, 3D wax printing** (Plas-Mac, SITE-000528), and a **turbine / investment casting market**.
- **Electron-beam processing** (cross-linking, irradiation, bioburden reduction) (Mercury Plastics).
- **Specialty-chemical / polymer-additive manufacture** (Valtris: plasticizers, stabilizers, stearates) and **foundry-binder chemical blending, amine recycling** (Novis Works).
- **Thermoset BMC/SMC compound formulation** (AltraSet): same gap as tranche 1 (composites_compression_smc_bmc is part-making).
- **Aerosol formulation and contract filling** (ValenSil).
- **Conveyor-belt field service, splicing, scrap-belt recycling** (QBM); **rubber-to-metal bonding, chlorination, cryogenic de-flashing** (Rubber Associates).
- **Food-safety certifications:** SQF (Adherex nav), FSSC 22000 / BRCGS (Anita blog title): no CERTS terms.
- Judgement-call mappings the integrator may override: dip molding to latex_dipping_foaming (Aptyx); sonic welding to ultrasonic_solvent_bonding (American Foam); military/defense to aerospace_defense (Polystar, Robin, Flambeau, GEON, Pison); Sports & Recreation to toys_sporting_goods (Design Molded); water & plumbing to water_wastewater (Rubber Associates); window coverings to construction_building_products (Astra); mining/steel/cement to chemical_mining_metals_processing (QBM, Novis); wire spools and packaging tapes to packaging_industrial (ABC, Foundation, Adherex, American Foam); anti-slip tape to pressure_sensitive_tape_manufacture (Sure-Foot); slitting/converting to die_cutting_converting (DermaMed); acrylic casting chemistry to acrylic_pmma (IT Plastics, likely drop); profile extrusion inferred for welding rods (V&A, likely drop); Communications to telecom_datacom (Flambeau).

## Certifications (R3c)

17 rows. Current edition named and VERIFIED: ISO 9001 and ISO 13485 org-wide at Aptyx (2016/2015), ISO 9001:2015 org-wide at HP Manufacturing and Duramax; at site scope Plas-Mac ISO 9001:2015 and AS9100D, Robin Fredericksburg IATF 16949 (single edition). **Row-level STILL_UNCERTAIN (10):** edition not named (GEON, Carbon Polymers, Robin Fredericksburg ISO 9001 and ISO 14001, Flambeau x4 org-wide) or implausible edition (DermaMed footer "ISO 9001: 2025 / ISO 13485 : 2025": not published editions). Expired or "ISO certified"-only claims were not recorded.

## Hygiene findings (for the integrator; none resolved)

1. **SITE-000009 GEON:** own locations page puts the Westlake HQ at 25777 Detroit Rd Suite 202, Westlake 44145; the row carries FRS 6100 Oak Tree Blvd, zip 44131.
2. **SITE-000031 Akron Porcelain:** own footer prints 2739 Cory Ave; row has 2719 (FRS).
3. **SITE-000054 Americhem:** own site lists HQ 2000 Americhem Way (44221) and a separate Cuyahoga Falls plant at 155 East Steels Corners (44224); the row street (1353 Industrial Pkwy, 44310) matches neither.
4. **SITE-000108 House of Plastics:** own site prints only 3705 Carnegie Ave, the plant (SITE-000107); the Prospect Ave row is a storefront and no page names it.
5. **SITE-000122 / ORG-000123 Anita Plastics:** own pages say the Solon entity is the US trading group for Mewar Group (products made in India); address is 38790 Glenlivet Ct, Solon, while the row says Woodmere.
6. **SITE-000135 / SITE-001654 Valtris:** specialty-chemical additive maker; locations page is a JS map; one `hq_only` and one plant row share the same org pages.
7. **SITE-000209 QBM:** own site shows a conveyor-belt service and scrap-recycling company with a Northern Ohio branch; row is a ring-1 `manufacturing_plant` with `hose_belting_manufacturing`. ISO 9001:2015 is stated for Canadian branches only.
8. **SITE-000480 Aptyx ("Molded Devices of Ohio"):** own locations page lists three Ohio sites (Kent, Miamisburg, North Canton); the Atlas carries 2 sites for ORG-000449 in total, so coverage should be checked. The site name appears nowhere on the Aptyx pages.
9. **SITE-000503 Novis Works:** foundry core-binder chemicals; scope doubt for the polymer atlas.
10. **SITE-000528 Plas-Mac:** wax / plastic investment-casting pattern shop sharing an 85,000 sq ft facility with Mercury Machine; scope doubt for a ring-1 plant. The ISO 9001:2015 and AS9100D attribution rests on footer order.
11. **SITE-000568 QMD:** only address is the HQ office suite (30100 Chagrin Blvd Suite 201); row is a ring-2 `manufacturing_plant`.
12. **SITE-000586 Robin:** own site lists four Ohio plants (Winesburg Holmco, Millersburg Healthcare with ISO 13485, Fredericksburg, North Canton) plus Mexico; the Atlas has 6 sites for ORG-000549, so check Winesburg and Millersburg are carried.
13. **SITE-000623 Sprosty Bag:** reads as a packaging distributor and webstore ("Pickup in store"); manufacturing_plant scope doubt.
14. **SITE-001512 Sare Plastics / ORG-001461 Stuchell Products:** `sareplastics.com` now redirects to CPI Precision Plastics (cpipp.com, molder since 1994). No value was proposed; successor or identity question for the integrator.
15. **SITE-001570 ValenSil:** aerosol contract filler, no polymer activity stated.
16. **SITE-001673 Pison:** history page says HQ is in New York with R&D and manufacturing in Ohio; row is a ring-2 `rd_center`.
17. **SITE-001308 AltraSet:** org `website` is a Mar-Bal subdomain (`altraset.mar-bal.com`); parent relationship should be checked.
18. **SITE-002043 Sietins:** `sietins.com` serves unrelated spam-titled content (hijacked or compromised domain); **SITE-001993 Raydar:** JS redirect to a parked-style lander; **SITE-001784 ECM, SITE-000383 GRAFIX, SITE-000605 Sealed Air, SITE-001397 Saint-Gobain:** bot walls; **SITE-000172 HEXPOL:** proxy 502 / TLS failure. All availability only; the org `website` of Sietins and Raydar needs another route.
19. **Existing non-vocab values on rows:** SITE-001425 Ergomat (`molding`; `polyurethane;rubber`), SITE-001439 Sure-Foot (`frp_molding`), SITE-003465 Henkel (`adhesive and sealant formulation; cartridge filling` and the three materials).
20. **SITE-000321 DermaMed:** footer shows impossible cert editions (2025); **SITE-000338 Duramax** and **SITE-000425 JK Plastics** print no street on fetched pages.
21. **SITE-000362 Flambeau:** the plant is named Sharon Center in the news item and Wadsworth on the facilities page; row city is Wadsworth.

## Per-site summary

| site_id | site | verdict | site-scope capability values | site-scope certs | org-scope values | off-vocab | fetches |
|---|---|---|---|---|---|---|---|
| SITE-000009 | GEON - Westlake HQ | STILL_UNCERTAIN | 0 | 0 | 12 | 0 | 6 |
| SITE-000031 | Akron Porcelain & Plastics Co. — Akron | VERIFIED | 13 | 0 | 0 | 0 | 6 |
| SITE-000054 | Americhem, Inc. — Cuyahoga Falls | STILL_UNCERTAIN | 0 | 0 | 12 | 0 | 6 |
| SITE-000069 | Design Molded Plastics — Macedonia | VERIFIED | 8 | 0 | 0 | 0 | 6 |
| SITE-000086 | Rubber Associates, Inc. — Barberton | VERIFIED | 15 | 0 | 0 | 1 | 6 |
| SITE-000108 | House of Plastics — Cleveland | STILL_UNCERTAIN | 0 | 0 | 16 | 0 | 6 |
| SITE-000122 | Anita Plastics — Woodmere | STILL_UNCERTAIN | 0 | 0 | 2 | 0 | 6 |
| SITE-000135 | Valtris Specialty Chemicals — Independence | STILL_UNCERTAIN | 0 | 0 | 3 | 1 | 6 |
| SITE-000172 | HEXPOL Compounding — Solon | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 3 |
| SITE-000193 | SKF USA — Highland Heights | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 1 |
| SITE-000209 | QBM Products — Avon Lake | STILL_UNCERTAIN | 0 | 0 | 1 | 1 | 6 |
| SITE-000222 | ABC Plastics — Lodi | STILL_UNCERTAIN | 0 | 0 | 2 | 0 | 6 |
| SITE-000241 | American Foam Products — Painesville | VERIFIED | 6 | 0 | 0 | 0 | 6 |
| SITE-000255 | The B.B. Bradley Company — Painesville | STILL_UNCERTAIN | 0 | 0 | 9 | 0 | 6 |
| SITE-000278 | Carbon Polymers Company — Lodi | VERIFIED | 10 | 1 | 0 | 0 | 6 |
| SITE-000293 | Chemsultants International, Inc. — Mentor | VERIFIED | 6 | 0 | 0 | 0 | 6 |
| SITE-000321 | Dermamed Coatings, LLC — Kent | VERIFIED | 6 | 2 | 0 | 0 | 6 |
| SITE-000338 | Duramax Marine — Hiram | STILL_UNCERTAIN | 0 | 0 | 3 | 0 | 6 |
| SITE-000362 | Flambeau Sharon Center Plant | VERIFIED | 1 | 0 | 12 | 0 | 6 |
| SITE-000383 | GRAFIX — Maple Heights | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-000410 | Intralox — Twinsburg | STILL_UNCERTAIN | 0 | 0 | 2 | 0 | 6 |
| SITE-000425 | JK Plastics — Middlefield | VERIFIED | 10 | 0 | 0 | 0 | 4 |
| SITE-000443 | Koroseal Interior Products — Medina | STILL_UNCERTAIN | 0 | 0 | 1 | 0 | 6 |
| SITE-000462 | Masco (Mercury Plastics) | STILL_UNCERTAIN | 0 | 0 | 7 | 1 | 6 |
| SITE-000480 | Molded Devices of Ohio, Inc | STILL_UNCERTAIN | 0 | 0 | 7 | 0 | 6 |
| SITE-000503 | Novis Works LLC — Canton | VERIFIED | 2 | 0 | 0 | 1 | 6 |
| SITE-000528 | The Plas-mac — Solon | VERIFIED | 0 | 2 | 0 | 2 | 6 |
| SITE-000547 | Polystar Containment — Stow | STILL_UNCERTAIN | 0 | 0 | 4 | 0 | 6 |
| SITE-000568 | Q Medical Devices — Pepper Pike | STILL_UNCERTAIN | 0 | 0 | 4 | 0 | 6 |
| SITE-000586 | Robin Industries, Inc. — Fredericksburg | VERIFIED | 0 | 3 | 13 | 0 | 6 |
| SITE-000605 | Sealed Air (APS- STC) | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 1 |
| SITE-000623 | Sprosty Bag Co., Inc. — Smithville | STILL_UNCERTAIN | 0 | 0 | 5 | 0 | 6 |
| SITE-000643 | Tesla Nanocoatings — Massillon | STILL_UNCERTAIN | 0 | 0 | 5 | 0 | 6 |
| SITE-000661 | Universal Plastics Group, Inc. — Middlefield | STILL_UNCERTAIN | 0 | 0 | 7 | 0 | 6 |
| SITE-001308 | AltraSet Composite Technologies — Chagrin Falls | STILL_UNCERTAIN | 0 | 0 | 7 | 1 | 6 |
| SITE-001397 | Saint-Gobain Performance Plastics — Ravenna (Aerospace) | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 1 |
| SITE-001425 | Ergomat Inc. — Lorain | STILL_UNCERTAIN | 0 | 0 | 4 | 0 | 6 |
| SITE-001439 | Sure-foot Industries — Cleveland | VERIFIED | 4 | 0 | 0 | 0 | 6 |
| SITE-001512 | Sare Plastics — Alliance | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 6 |
| SITE-001570 | ValenSil Technologies, LLC — Avon | STILL_UNCERTAIN | 0 | 0 | 0 | 1 | 6 |
| SITE-001654 | Valtris Specialty Chemicals — Walton Hills | STILL_UNCERTAIN | 0 | 0 | 3 | 1 | 6 |
| SITE-001673 | Pison Stream Solutions Inc — Brecksville | STILL_UNCERTAIN | 0 | 0 | 4 | 0 | 6 |
| SITE-001707 | ASTRA PRODUCTS OF OHIO LTD — Ravenna | VERIFIED | 5 | 0 | 0 | 0 | 6 |
| SITE-001722 | V&A PROCESS — Lorain | VERIFIED | 12 | 0 | 0 | 0 | 6 |
| SITE-001746 | Enpac LLC — Eastlake | VERIFIED | 1 | 0 | 0 | 0 | 6 |
| SITE-001784 | ECM Performance Materials Corp | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001829 | Foundation Industries Inc | VERIFIED | 4 | 0 | 0 | 0 | 6 |
| SITE-001852 | Adherex Packaging (Adherex Group) | STILL_UNCERTAIN | 0 | 0 | 5 | 0 | 6 |
| SITE-001883 | Impact Sleeve (Sleeve Seal / ID Images) | STILL_UNCERTAIN | 0 | 0 | 8 | 0 | 6 |
| SITE-001924 | Industrial Thermoset Plastics (IT Plastics) | VERIFIED | 9 | 0 | 0 | 0 | 6 |
| SITE-001993 | Raydar of Ohio, Inc. | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-002043 | Sietins Plastics Inc (Sietins Precision) | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-002082 | DayGlo Twinsburg site | STILL_UNCERTAIN | 0 | 0 | 3 | 0 | 6 |
| SITE-003465 | Henkel — Mentor | STILL_UNCERTAIN | 0 | 0 | 3 | 0 | 6 |

(SITE-001654 shares ORG-000135 values with SITE-000135; org-scope counts above repeat for sites of the same org.)

## Files

- `packet.csv`: 290 rows (281 in-vocab, 9 off-vocab), columns as in tranche 1.
- `verdicts.csv`: 54 rows with deciding/settling fact, fetches used (all attempts, including the race-lost ones), availability failures.
