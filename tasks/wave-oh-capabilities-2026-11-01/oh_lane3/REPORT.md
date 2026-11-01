# Ohio (non-PIC-12) capability wave, lane oh-3 report (2026-11-01)

This is a packet, not a data change. The lane wrote only `packet.csv`, `verdicts.csv` and this report in `tasks/wave-oh-capabilities-2026-11-01/oh_lane3/`. It proposes no `tier_effect`, allocates no IDs and edits nothing under `data/`.

- **Pin:** the lane brief's pin is `eb79f3b`. The assignment file is `oh_lane3_assignment.csv` (80 site rows).
- **Method:** the PIC-12 brief and its Tranche 2 section. Company website only (`own_site`, including certificate PDFs the site links to). Fetched with curl through the configured proxy. Vocabulary v1.7.6. R3c applied to every certification.
- **Quote check:** every quote is at most 25 words and every one of the 339 quotes passed a script check as a substring of the fetched text (whitespace and quote-style normalised). PDFs were read with `pdftotext`. Nothing was quoted from a WebFetch summary.
- **Scratch:** `/tmp/claude-0/wave-oh/lane3/`, one sub-directory per site, with a lock file so no site was ever fetched in parallel. Sites were fetched in parallel with each other, never one site with itself. No file collisions occurred.
- **Bot walls:** none were worked around. A 403, 406, 409, TLS error or connection reset was recorded as an availability failure.

## Results (unit: assigned Ohio site rows, n = 80)

VERIFIED 37 (46%) · STILL_UNCERTAIN 43 · REJECT 0.

No REJECT was issued. Every doubtful row (distributor, HQ or office, retailer, out-of-scope chemistry) is held as STILL_UNCERTAIN with a named settling fact, because scope and ring questions are owner rulings (AGENTS.md section 2 rule 9).

### Packet rows (unit: rows in `packet.csv`, n = 339)

| field | in-vocab, site scope | in-vocab, org scope | row-level held back (site scope) |
|---|--:|--:|--:|
| processes | 57 | 37 | 2 |
| materials | 62 | 34 | 2 |
| markets_served | 57 | 51 | 2 |
| certifications | 10 | 3 | 8 |
| **all** | **186** | **125** | **14** |

- **Off-vocab rows:** 14 (10 `processes_other_note`, 3 `materials_other_note`, 1 `markets_other_note`), all marked OFF-VOCAB and STILL_UNCERTAIN.
- **Row-level held back:** 14 in-vocab site-scope rows carry a row verdict of STILL_UNCERTAIN. These are certifications whose edition or site coverage is unconfirmed (Boomerang ISO 14001, Milacron ISO 9001, YUSA ISO 9001, CTL ISO 9001 and ITAR, HA-International ISO 9001, ProAmpac ISO 9001 city-level), IATF at Flex Midvale (support site only), Flex extrusion form, KP markets tied only through an expired certificate, MLB foam-molding term, ILC and AK "vinyl" read as PVC.
- **Scope split:** values are `org` scope whenever a multi-plant parent's page does not name the plant. Nothing was pushed down to a site.

### Yield

- **Site-scope in-vocab values:** 2.3 per assigned site, 5.0 per VERIFIED site (186 values over 37 sites).
- **All scopes together (in-vocab, row-level VERIFIED):** 311 values, 3.9 per assigned site.
- **Coverage:** 68 of 80 sites got at least one in-vocab value (any scope). 12 got none, and nine of those had no usable content at all (see fetches).
- **Markets:** present at site scope for 28 of 80 sites, and at any scope for 57 of 80.

## Certificates read and recorded

| Site | Standard | Scope or note | Valid to |
|---|---|---|---|
| SITE-001080 Oliver, Hamilton | ISO 13485:2016 (BSI FM 743502) | 3840 Symmes Rd; adhesive coating and slitting of medical packaging materials | 2027-05-31 |
| SITE-000897 FB Wright | ISO 9001:2015 (EAGLE 5438) | 4689 Ashley Dr; hose, gasket, belt and plastic assemblies; certificate says Hamilton | recertified 2025-12-17 (expiry not printed) |
| SITE-001231 Cohesive Components | ISO 9001:2015 (EAGLE 80) | 6156 Wesselman Rd; gaskets and seals | recertified 2026-03-25 (expiry not printed) |
| SITE-001341 Advanced Composites R&D | ISO/IEC 17025:2017 (A2LA 0749.02) | 1164 S Fourth Ave; thermoplastic resin testing | 2028-06-30 |
| SITE-001341 Advanced Composites R&D | IATF 16949:2016 (NSF-ISR 31393-TS19) | annex lists 1164 S Fourth Ave as a remote engineering/R&D location | 2027-03-24 |
| SITE-000722 ProAmpac, Cincinnati | ISO 9001:2015 | page lists Cincinnati; linked PDF has no text layer (held, row-level STILL_UNCERTAIN) | 2029-09-14 (per page) |
| SITE-000909 Flex, Midvale | IATF 16949:2016 (EAGLE 0531763) | Midvale is a Support Site of the Lafayette TN certificate only (held) | 2027 cycle (recertified 2024-07-19) |

**Not recorded, expired or unclear:**
- **KP Greenville:** the Certifications page links an ISO 9001:2015 certificate for 1671 Martindale Rd that expired 2024-07-31. It is not recorded.
- **ProAmpac Cincinnati ISO 14001** (page date 1.14.26) and **SQF** (4.11.26) are past their dates and not recorded.
- **Editions not named:** Boomerang ISO 14001, Milacron ISO 9001, YUSA ISO 9001, CTL's ISO 9001 line, HA-International's "met the standards required for ISO 9001:2015" wording. These are held at row level, not recorded as VERIFIED.
- **Not certifications:** Vision Color's "ISO Compliant Quality Management System" and Dover's "ISO-aligned best practices".

## Fetches

290 attempts, 3.6 per site (cap 6; two sites used all 6; none exceeded it). No fetch was lost to a collision.

- **Hard failures: 20 of 290 (6.9%).**
  - Connection reset: Heritage Bag, 2.
  - 403: Bena, 2.
  - 406 mod_security: Ridge, 2.
  - TLS name mismatch: Pumpmatic, 2.
  - TLS chain or expired certificate: Ashland, 2; Arthur Corp www, 1.
  - HTTP 404 on every path, plus an unresolvable alternate domain: Deltech, 4.
  - Proxy or DNS failure: bostik-us.com, 1.
  - My own guessed URLs returning 404: flex-n-gate /locations, Vision Color /iso, 2.
  - Ecosil's own /industries and /about pages returning 409: 2.
- **Empty bodies on HTTP 200: 5** (Pella root and /about-us/ are JS shells, crafttireinc.com is a site-builder shell, arthurcorp.com is a hosting placeholder, one image-only ProAmpac certificate PDF). Counted in `availability_failures` as "no text".
- **No usable content at all (9 sites):** SITE-000852 Deltech, SITE-001092 Pella, SITE-001167 Ridge, SITE-001203 Shrader/Craft Tire, SITE-001462 Heritage Bag, SITE-001499 Bena, SITE-001596 Pumpmatic, SITE-002065 Ashland (Lima), SITE-002105 Arthur Corp. All nine are STILL_UNCERTAIN. These are availability failures only, never closure evidence. The Deltech domain returning 404 on every path may mean a site change and is worth a different route.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - polyurethane pour or casting, and RIM (MLB);
  - golf-ball refinishing;
  - flexible PVC extruding line with form unstated (Chase);
  - rubber or plastic molding with the type unstated (YUSA, Bridge Components);
  - elastomeric bearing lamination and vulcanizing;
  - machinery building (Milacron);
  - self-adhering membrane manufacture (MFM);
  - slitting (Oliver);
  - packaging distribution and warehousing;
  - replacement-parts supply;
  - cast-polymer sanitaryware (AL-CO).
- **Materials with no term:** DCPD / polydicyclopentadiene, mineral-filled ethylene copolymer barrier compound (Polyfill), TPO, bullet-resistant sheet resin (Spartech).
- **Markets with no term:** signage / awards / engraving, military as distinct from aerospace (Dover), pharmacy dispensing packaging (Centor, mapped to `pharmaceutical_biotech`), golf.
- **Certifications with no term:** SQF, BRC, FSSC 22000, ISO 22000, ISO 50001, ISCC, IMS (ProAmpac, KP), NADCAP (CTL), NSF 61 product certification as a distinct item.
- **Terms used where only the closest fit exists:**
  - `hose_belting_manufacturing` for ATP plastic tubing;
  - `foam_molding_structural` for MLB integral-skin foam (held);
  - `mold_tool_making` for A.M. Toolbox additive tooling;
  - `assembly_secondary_ops` for Spartech Jaysville finishing and Legacy in-line operations;
  - `rail_transportation` for Replex buses, trucks and rail.

## Hygiene findings (not resolved, for the integrator)

**Plants, HQs and offices carrying a plant ring:**
1. **SITE-000920 Future Polytech.** The site labels Columbus 43219 "Headquarters" and prints "Made in Coldwater, OH" (45828). No Coldwater row is held under this parent.
2. **SITE-000948 Hexion (Columbus), SITE-001639 Therma-Tru (`hq_only`), SITE-001037 Milacron (Global Headquarters, Batavia).** Hexion's own timeline lists Columbus only as a history location. Milacron builds plastics machinery, so it is a scope and ring question for the owner.
3. **SITE-001221 Storopack.** The row name says Cincinnati Distribution Center. No fetched page names the site.
4. **SITE-001145 Queen City Polymers (legacy "Queen City Foam").** Cincinnati is HQ, with plants in Dayton OH, Pharr TX and Reynosa MX. The Dayton plant was not checked against the repo.
5. **SITE-001445 Champion Window.** "Champion of Cincinnati, OH 45241" reads as a showroom listing.
6. **SITE-001544 Ohio Rubber and Floors.** The site calls 1366 E Ervin Rd the "main office" with a showroom, and says only "manufactured right here in Ohio".
7. **SITE-001211 Spartech (Jaysville).** The plant page says it is a finishing and warehouse operation since 2018. The production plant is SITE-001210 (Greenville, 1050 Landsdowne Ave), already held.
8. **SITE-001341 Advanced Composites.** An R&D and lab site only (ISO 17025 lab and IATF annex), with no production.

**Unheld plants and sibling sites seen on the companies' own pages (checked against `data/sites_OH.csv` by street or name only):**
9. **Axium.** "Apex Finishing" at 8300 Innovation Campus Way, New Albany is listed on the Locations page; no held row was found. Plants 2, 3, 4, 5, 6, HQ and Vertix are held (SITE-000741 to 000745, SITE-001343, SITE-001345).
10. **Flex Technologies.** The Mt. Eaton OH injection molding and assembly site: no held row found by name or street search. The Baltic OH PVC compounding site is held as a separate org, Polyflex (ORG-001040), whereas Flex's own site calls Polyflex "a division of Flex Technologies" (parent-of-record question).
11. **Cohesive Components.** The Harrison OH distribution center (10053 Simonson Rd) is not held. It is named as an additional address on the ISO certificate.
12. **ProAmpac.** The certification page lists Middleton OH and Monroe OH facilities. Only the Cincinnati row is held for ORG-000671.

**Name, parent and identity:**
13. **SITE-000722.** The row name is AMPAC PLASTICS and the operator is ProAmpac. The org name is ProAmpac, with "AMPAC PLASTICS" as a trade name.
14. **SITE-000734.** The row reads "Ashland — Ashland" but the org site is Bostik (Arkema). Check the operator.
15. **SITE-000875.** The row reads Durez but the org site is SBHPP (Sumitomo Bakelite).
16. **SITE-000828.** The row reads Crane Plastics but the site is Engineered Profiles (2141 Fairwood Ave, Columbus).
17. **SITE-001282.** The row reads Ventra Sandusky and the org site is Flex-N-Gate.
18. **SITE-001203.** The row reads Shrader Retreading and the domain is crafttireinc.com.
19. **SITE-001231.** The row reads Sur-Seal Corporation but the operator is Cohesive Components (certificate holder "Sur-Seal LLC dba Cohesive Components Corp").
20. **SITE-001801.** The row is Thorworks Industries while the org site is SealMaster, a network of nearly 160 plants and distribution centers.
21. **SITE-000897.** The certificate says 4689 Ashley Drive, **Hamilton** OH 45011 while the row says West Chester.
22. **SITE-000841.** The company prints "Cincinnati, OH 45246-4898" but its About page says West Chester.

**Possible distributors, retailers or out-of-scope rows (scope questions for the owner, not decided):**
23. **SITE-001013 Mar-Pak.** A packaging distributor and manufacturer's rep, per its history.
24. **SITE-001763 KSE Manufacturing.** Replacement parts for sorter and conveyor equipment, "not original manufacturer's parts".
25. **SITE-001981 Osburn Offroad.** Reads as an off-road parts and graphics-kit storefront.
26. **SITE-001916 Hedstrom.** A consumer toy brand page with no plant or process statement.
27. **SITE-001745 Ecosil.** Metal-surface pretreatment chemistry, which may be outside the polymer scope.
28. **SITE-000897 FB Wright and SITE-001145 QCP** are fabricator-distributors.

**Websites and fields:**
29. **SITE-001596:** the pumpmatic.com TLS name does not match (apex and www).
30. **SITE-002105:** arthurcorp.com serves a hosting placeholder and www has an expired certificate.
31. **SITE-000852:** deltech.com returns 404 on every path tried.
32. **SITE-001445 and SITE-001453:** existing site `processes` values (`vinyl_window_manufacturing`, `cast_polymer`) are legacy non-vocab tags. SITE-001462, SITE-001499, SITE-001544, SITE-003462 and SITE-003912 also carry legacy free-text process or material values.
33. **SITE-000689:** the site's printed phone is a placeholder "(614) 123-4567" (not recorded).
34. **SITE-001887:** the printed address is 1680 US HW 20A, Swanton; the row's `street_address` is blank.

## Per-site table

Columns are site-scope VERIFIED in-vocab values, org-scope VERIFIED values, in-vocab rows held back at row level, off-vocab rows, and fetches used.

| Site | Name | Verdict | site | org | held-back | off-vocab | fetches |
|---|---|---|--:|--:|--:|--:|--:|
| SITE-000689 | A.m. Toolbox — Dublin | VERIFIED | 3 | 0 | 0 | 1 | 5 |
| SITE-000701 | Advanced Technology Products — Milford | STILL_UNCERTAIN | 0 | 7 | 0 | 0 | 5 |
| SITE-000711 | Alpine Material Solutions — Cincinnati | VERIFIED | 10 | 0 | 0 | 0 | 4 |
| SITE-000722 | AMPAC PLASTICS — Cincinnati | STILL_UNCERTAIN | 0 | 7 | 1 | 0 | 5 |
| SITE-000734 | Ashland — Ashland | STILL_UNCERTAIN | 0 | 4 | 0 | 0 | 5 |
| SITE-000742 | Axium Packaging : New Albany Plant 2 | VERIFIED | 1 | 8 | 0 | 0 | 5 |
| SITE-000754 | Bakelite Chemicals — Columbus | STILL_UNCERTAIN | 0 | 6 | 0 | 0 | 5 |
| SITE-000766 | Boomerang Rubber, Inc. — Botkins | VERIFIED | 5 | 0 | 1 | 0 | 5 |
| SITE-000780 | Centor — Berlin | VERIFIED | 3 | 0 | 0 | 0 | 6 |
| SITE-000790 | Chase Doors — Cincinnati | VERIFIED | 5 | 0 | 0 | 1 | 3 |
| SITE-000805 | Composite Technologies, Inc. — Dayton | VERIFIED | 11 | 0 | 0 | 0 | 4 |
| SITE-000817 | Cooper Standard (Bowling Green Seal) | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 4 |
| SITE-000828 | Crane Plastics — Columbus | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 4 |
| SITE-000841 | CTL Aerospace, Inc. — Cincinnati | VERIFIED | 7 | 0 | 2 | 0 | 4 |
| SITE-000852 | Deltech Polymers OpCo, LLC — Troy | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 4 |
| SITE-000864 | Dover High Performance Plastics — Dove | VERIFIED | 11 | 0 | 0 | 0 | 4 |
| SITE-000875 | Durez Corporation — Kenton | STILL_UNCERTAIN | 0 | 6 | 0 | 0 | 4 |
| SITE-000885 | Haviland Plastic Products Co. | VERIFIED | 3 | 0 | 0 | 0 | 4 |
| SITE-000897 | F.B. Wright Cincinnati — West Chester | VERIFIED | 10 | 0 | 0 | 0 | 4 |
| SITE-000909 | Flex Technologies, Inc. — Midvale | STILL_UNCERTAIN | 0 | 7 | 2 | 0 | 4 |
| SITE-000920 | Future Polytech — Columbus | STILL_UNCERTAIN | 0 | 2 | 0 | 1 | 4 |
| SITE-000930 | GOLF BALL REFURBISHERS — Loudonville | VERIFIED | 2 | 0 | 0 | 1 | 1 |
| SITE-000939 | H&h Industries — Oak Hill | VERIFIED | 3 | 0 | 0 | 0 | 5 |
| SITE-000948 | Hexion — Columbus | STILL_UNCERTAIN | 0 | 2 | 0 | 0 | 4 |
| SITE-000957 | ILLINOIS TOOL WORKS — Bryan | STILL_UNCERTAIN | 0 | 1 | 0 | 0 | 4 |
| SITE-000969 | International Laminating Corp. — Dayto | VERIFIED | 2 | 0 | 1 | 0 | 4 |
| SITE-000981 | Johns Manville International, Inc. — M | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 4 |
| SITE-000991 | Klockner Pentaplast of America, Inc. — | STILL_UNCERTAIN | 0 | 3 | 2 | 0 | 5 |
| SITE-001002 | Legacy Extrusions — Cincinnati | VERIFIED | 6 | 0 | 0 | 0 | 4 |
| SITE-001013 | Mar-Pak, Inc. — Marietta | STILL_UNCERTAIN | 0 | 0 | 0 | 1 | 4 |
| SITE-001024 | Mayco — Toledo | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 4 |
| SITE-001037 | MILACRON PLASTICS TECHNOLOGIES GROUP L | STILL_UNCERTAIN | 0 | 2 | 1 | 0 | 4 |
| SITE-001048 | MTNA — Greenville | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 4 |
| SITE-001057 | Neaton Auto Products Manufacturing — E | STILL_UNCERTAIN | 0 | 2 | 0 | 0 | 3 |
| SITE-001069 | Norwesco, Inc. — Washington Court Hous | STILL_UNCERTAIN | 0 | 5 | 0 | 0 | 3 |
| SITE-001080 | OLIVER HEALTHCARE PACKAGING — Hamilton | VERIFIED | 3 | 3 | 0 | 0 | 5 |
| SITE-001092 | Pella Corporation — Troy | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001108 | Plastic Compounders, Inc. — Cambridge | VERIFIED | 4 | 0 | 0 | 0 | 1 |
| SITE-001121 | Polyfill — Sidney | VERIFIED | 5 | 0 | 0 | 1 | 4 |
| SITE-001132 | Profusion Industries — Marietta | STILL_UNCERTAIN | 0 | 7 | 0 | 0 | 4 |
| SITE-001145 | QUEEN CITY FOAM, INCORPORATED | STILL_UNCERTAIN | 0 | 5 | 0 | 0 | 3 |
| SITE-001158 | Replex Plastics — Mount Vernon | VERIFIED | 9 | 0 | 0 | 0 | 4 |
| SITE-001167 | Ridge Corporation (Apollo) | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001181 | Rowmark — Findlay | VERIFIED | 2 | 0 | 0 | 1 | 3 |
| SITE-001192 | Savare Specialty Adhesives — Delaware | VERIFIED | 4 | 0 | 0 | 0 | 3 |
| SITE-001203 | Shrader Retreading — Greenville | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 1 |
| SITE-001211 | Spartech LLC. Jaysville | VERIFIED | 2 | 3 | 0 | 1 | 5 |
| SITE-001221 | Storopack, Inc.- Cincinnati Distributi | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 4 |
| SITE-001231 | Sur-Seal Corporation — Cincinnati | VERIFIED | 4 | 1 | 0 | 0 | 5 |
| SITE-001243 | Tencom Ltd. — Holland | VERIFIED | 8 | 0 | 0 | 0 | 4 |
| SITE-001253 | TJAR Innovations, LLC — Xenia | VERIFIED | 4 | 0 | 0 | 0 | 4 |
| SITE-001267 | Ttmco — Westerville | VERIFIED | 3 | 0 | 0 | 0 | 4 |
| SITE-001282 | Ventra Sandusky — Sandusky | STILL_UNCERTAIN | 0 | 1 | 0 | 0 | 3 |
| SITE-001291 | Vision Color, LLC — West Unity | VERIFIED | 12 | 0 | 0 | 0 | 4 |
| SITE-001304 | Yamashita Rubber/YUSA Corp — Washingto | VERIFIED | 3 | 0 | 1 | 1 | 4 |
| SITE-001341 | Advanced Composites, Inc. — 1164 South | VERIFIED | 3 | 0 | 0 | 0 | 6 |
| SITE-001445 | Champion Window — Cincinnati | STILL_UNCERTAIN | 0 | 2 | 0 | 0 | 3 |
| SITE-001453 | AL-CO Products — Latty | VERIFIED | 1 | 0 | 0 | 1 | 3 |
| SITE-001462 | Heritage Bag — Fairfield | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001499 | Bena, Inc. — Van Buren | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001519 | PPG Industries — Circleville | STILL_UNCERTAIN | 0 | 4 | 0 | 0 | 4 |
| SITE-001544 | Ohio Rubber and Floors - Van Wert | STILL_UNCERTAIN | 0 | 2 | 0 | 1 | 2 |
| SITE-001596 | Ashton Pumpmatic, Inc. — Dayton | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001639 | Therma-Tru Corp. — Maumee | STILL_UNCERTAIN | 0 | 2 | 0 | 0 | 4 |
| SITE-001687 | MFM Building Products Corp — Coshocton | VERIFIED | 1 | 0 | 0 | 1 | 4 |
| SITE-001701 | AK ATHLETIC EQUIPMENT INC — Canal Winc | VERIFIED | 3 | 0 | 1 | 0 | 4 |
| SITE-001734 | Concrete Sealants Inc — Tipp City | VERIFIED | 10 | 0 | 0 | 0 | 4 |
| SITE-001745 | Ecosil Technologies LLC — Fairfield | STILL_UNCERTAIN | 0 | 2 | 0 | 0 | 4 |
| SITE-001763 | KSE Manufacturing — Sidney | STILL_UNCERTAIN | 0 | 0 | 0 | 1 | 3 |
| SITE-001801 | Thorworks Industries Inc | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 1 |
| SITE-001817 | Champion Manufacturing, Inc. | VERIFIED | 7 | 0 | 0 | 0 | 4 |
| SITE-001863 | Bridge Components Industries Inc | VERIFIED | 3 | 0 | 0 | 1 | 2 |
| SITE-001887 | MLB Molded Urethane Products LLC | VERIFIED | 11 | 0 | 1 | 0 | 2 |
| SITE-001916 | Hedstrom Plastics — Ashland | STILL_UNCERTAIN | 0 | 1 | 0 | 0 | 3 |
| SITE-001981 | Osburn Associates Inc | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-002036 | HA-International LLC | VERIFIED | 2 | 1 | 1 | 0 | 4 |
| SITE-002065 | Ashland Inc. — Lima (ISP Lima LLC) | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-002105 | THE ARTHUR CORPORATION | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-003462 | ContiTech — Marysville (Conveyor Belt  | STILL_UNCERTAIN | 0 | 3 | 0 | 0 | 4 |
| SITE-003912 | Responsible Products Milford | STILL_UNCERTAIN | 0 | 5 | 0 | 0 | 3 |

Verdicts and settling facts per site are in `verdicts.csv`; row-level evidence is in `packet.csv`.
