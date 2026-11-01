# Ohio non-PIC-12 capability wave, lane 6 report (2026-11-01)

This is a packet, not a data change. The lane wrote only to `tasks/wave-oh-capabilities-2026-11-01/oh_lane6/` and did not edit `data/`, allocate IDs, commit or push.

- **Pin:** repo HEAD `990919b` at lane start (candidate population pinned at `eb79f3b`).
- **Assignment:** `oh_lane6_assignment.csv`, 79 active Ohio site rows outside the PIC-12 counties (ring 1-2, blank `processes` or `markets_served`).
- **Method:** `own_site` only (company website and the certificate PDFs it links), curl through the configured proxy with the standard CA bundle and `--compressed`, no user-agent change and no bot-wall workaround. Vocabulary v1.7.6 (`docs/schema/vocab.json`); R3c applied. Page text kept per site under `/tmp/claude-0/wave-oh/lane6/f/` with per-site locked filenames and no parallel fetches for one site; the 6-fetch cap held at every site (maximum 6).
- **Checks:** all 362 packet rows carry a URL and a quote of 25 words or fewer. A script confirmed every quote is a whitespace-normalised substring of the fetched text for that URL (PDFs read with `pdftotext`). A second script confirmed every in-vocab value is in the vocabulary for its field, one value per row, and every other row is a `*_other_note` row marked OFF-VOCAB. No personal email, direct phone or individual name is recorded.
- **Shared fetches:** SITE-000745 and SITE-001344 are two Axium Packaging rows with the same org website. SITE-001344's own homepage fetch duplicated one SITE-000745 fetch; its verdict also reads the 4 SITE-000745 pages.

## Results (unit: assigned Ohio site rows, n = 79)

VERIFIED 41 (52%) · STILL_UNCERTAIN 38 · REJECT 0.

VERIFIED means at least one in-vocab value at site scope. No page gave a deciding fact for REJECT, and a failed fetch is never closure evidence.

| field (in-vocab rows, verdict VERIFIED) | site scope | org scope | total |
|---|---:|---:|---:|
| processes | 68 | 32 | 100 |
| materials | 73 | 45 | 118 |
| markets_served | 56 | 46 | 102 |
| certifications | 12 | 0 | 12 |
| **all** | **209** | **123** | **332** |

- **Rows by kind (362 total):** 332 VERIFIED in-vocab, 12 row-level STILL_UNCERTAIN in-vocab, 18 OFF-VOCAB `*_other_note` rows (10 processes, 3 materials, 3 certifications, 2 markets).
- **Row-level STILL_UNCERTAIN in-vocab rows (12):**
  - Certifications held for no named edition or no certificate: Anomatic (ISO 9001, ISO 14001), Plas-Tanks and Proto Plastics (ISO 9001), KLINGER (ISO 9001 with no edition).
  - Certification held for a stale statement: Deimling/jeliho (a December 2017 conformance statement).
  - Certifications held for no named standard: Tech-Way (clean room "Class 7 and 8", no ISO 14644 named).
  - Site tie or in-house production not established: Mark One (injection molding), Axium Apex Finishing (decoration, tied by facility name only), Medallion/Rubber-Seal (coating formulation), Cabbage Cases (ABS).
- **Yield:**
  - Site-scope values: 2.6 per assigned site, 5.1 per VERIFIED site.
  - All scopes together: 4.2 values per assigned site.
  - Sites with at least one in-vocab value at any scope: 68 of 79.
  - Markets at site scope at 27 sites; at any scope at 54 sites.
- **Richest sites (site-scope values):** DRS Industries 19, Basilius 17, Proto Plastics 16, Tech-Way 12, Krom International 10.

### Certificates and certification pages recorded

| Site | Standard | Basis | Valid to |
|---|---|---|---|
| Advanced Composites (Sidney) | ISO 9001:2015 | NSF-ISR certificate PDF, 1062 S Fourth Ave | 2027-03-24 |
| Advanced Composites (Sidney) | ISO/IEC 17025:2017 | A2LA scope PDF, Ohio Main Plant | 2028-06-30 |
| Advanced Composites (Sidney) | ISO 14001:2015, ISO 45001:2018, IATF 16949:2016 | Certifications page, "Ohio Facility" header (PDFs not fetched) | n/a |
| Basilius (Toledo) | ISO 9001:2015 | NSF-ISR certificate PDF, 4338 South Ave | 2029-06-27 |
| Sperry & Rice (Killbuck) | ISO 9001:2015 with Design | Smithers certificate PDF, 1088 N Main St | 2028-11-05 |
| Tech-Way (Franklin) | ISO 9001:2015 | EAGLE certificate PDF, 301 Industrial Dr; the edition comes from the site's link label because the PDF text layer omits it | 2027-07-15 |
| Atalys (Cloverdale) | ISO 13485:2016 | Locations page, Cloverdale block | n/a |
| SeaGate (Waterville) | ISO 9001:2015 | Locations and ISO pages | n/a |
| Eagle Composites (West Chester) | AS9100D, ISO 9001:2015 | Quality page | n/a |

No expired certificate was found. Page-level rows say in `notes` that the certificate was not fetched.

## Fetches

250 attempts, 3.2 per site (range 1 to 6: 1 site used 1, 15 used 2, 38 used 3, 21 used 4, 3 used 5, 1 used 6).

- **Hard failures: 2 of 250 (0.8%).** gkpackaging.com and www.gkpackaging.com both fail TLS with a certificate name mismatch. That site has no usable content and is an availability failure only.
- **404 on a guessed path: 2 (Cabbage Cases `/about-us/`, Altum `/about/`).** These cost a fetch and carry no evidence either way.
- **Fetches that returned HTTP 200 but no usable plant text (5):**
  - Epsilyte's homepage first came back as a compressed body, because the early script lacked `--compressed`; it was refetched.
  - ACP's Company Locations page and AkzoNobel's Locations page render only in JavaScript or images; Liquibox's Locations page is a map with no plant text; Altum's homepage is a frameset pointing to altumcomposites.com (followed, as the org's own frame source).
- **Script defect found and fixed mid-run:** a curl error message containing a newline inflated one site's fetch counter (GK Packaging). The log was repaired; the cap was never exceeded.

## Vocabulary gaps and mapping calls (flagged, not settled)

**Processes with no term (OFF-VOCAB rows):**
- aluminum anodizing and vacuum metallization (Anomatic);
- label and shrink-sleeve printing (Century Label);
- chrome plating (Creative Liquid Coatings);
- impregnation and infiltration sealing (Diamant);
- "surface treatment" (Hub Plastics, undefined);
- RTP vessel fabrication (Plas-Tanks);
- cultured-marble and solid-surface casting (Creative Products);
- PCM microencapsulation (Microtek);
- doctor-blade manufacture (Timco);
- flexographic plate making (E.C. Shaw);
- co-extruded film and multi-core extrusion (New Tech Plastics, Engineered Profiles), covered only by the nearest term.

**Materials with no term:**
- carbon black (only in CAP_MATERIAL, not MATERIALS);
- PBT, PPS, PEI, Tritan co-polyester (Proto Plastics, Basilius);
- TPO (Absolute Polymers; in CAP_MATERIAL only);
- shape-memory polymer tooling resin (Hawthorn Aero);
- unnamed casting and sealing resins (Diamant).

**Markets with no term:** paper industry (Timco), law enforcement (Basilius, ArmorSource), government/military packaging (Solo Products), textiles and cold chain (Microtek).

**Certifications with no term:** FSSC 22000 (Axium), ASME RTP-1 (Plas-Tanks), ISO 17712 / C-TPAT (United Security Seals), Interstate Milk Shippers listing and Drug Master File (Hub Plastics), Nadcap and AS13100 (Eagle).

**Mapping calls the integrator may reverse:**
- "military" or "military and law enforcement" mapped to `aerospace_defense` (Basilius, ArmorSource, Vi-Cas aerospace);
- "vinyl" mapped to `pvc` (Vi-Cas, Gilkey);
- PTFE and PVDF mapped to `fluoropolymers`;
- EPS mapped to `polystyrene_ps_hips`;
- "extruded EPS resin technology" mapped to `compounding_extrusion` (Epsilyte Piqua);
- "Vacuum Form" mapped to `thermoforming_vacuum` (Corvac);
- resin manufacture mapped to `polymerization` (LRBG, Alpek);
- "blow injection" mapped to `blow_molding_injection` (TMD Tiffin);
- heavy-duty suspension OEMs mapped to `automotive_oem` (Mullins).

## Not recorded, by design

- ISO 9001 and ISO 14001 "certified" claims with no edition or certificate (Anomatic, Plas-Tanks, KLINGER).
- Conformance statements that are not certification (Proto Plastics, Deimling/jeliho 2017).
- Product compliance claims (FDA-grade, UL, IMS dairy listing).
- Values from a corporate or global page with no plant tie: kept at org scope only. AkzoNobel, Amcor, Sealed Air/Liquibox, Sun Chemical, BASF, Cooper Standard, Flex-N-Gate and Sherwin-Williams yielded at most org-scope values or none.

## Per-site table

| Site | County | Verdict | Site-scope values | Org-scope values | Fetches |
|---|---|---|---:|---:|---:|
| SITE-000694 Advanced Composites, Inc. — Sidney | Shelby | VERIFIED | 7 | 3 | 6 |
| SITE-000704 AKZO NOBEL COATINGS INC — Huron | Erie | STILL_UNCERTAIN | 0 | 1 | 3 |
| SITE-000715 Amcor Rigid Packaging — Napoleon | Henry | STILL_UNCERTAIN | 0 | 3 | 3 |
| SITE-000726 Anomatic Corporation — Blacklick | Franklin | VERIFIED | 1 | 2 | 4 |
| SITE-000737 Atalys Ottoville — Cloverdale | Putnam | VERIFIED | 4 | 1 | 4 |
| SITE-000745 Axium Packaging : New Albany Plant 5 | Licking | STILL_UNCERTAIN | 0 | 11 | 4 |
| SITE-000757 Basilius Inc. — Toledo | Lucas | VERIFIED | 17 | 0 | 4 |
| SITE-000772 Buckhorn, Inc. — Milford | Clermont | STILL_UNCERTAIN | 0 | 3 | 4 |
| SITE-000785 Century Label — Bowling Green | Wood | VERIFIED | 2 | 0 | 3 |
| SITE-000793 Choice Adhesives — Cincinnati | Hamilton | STILL_UNCERTAIN | 0 | 4 | 3 |
| SITE-000810 Continental Structural Plastic/Teijin | Wood | STILL_UNCERTAIN | 0 | 4 | 3 |
| SITE-000823 Corvac Composites — Greenfield | Highland | STILL_UNCERTAIN | 0 | 3 | 3 |
| SITE-000833 Creative Liquid Coatings, Inc. Montpelier | Williams | STILL_UNCERTAIN | 0 | 8 | 4 |
| SITE-000846 D.S. Brown — North Baltimore | Wood | VERIFIED | 1 | 0 | 3 |
| SITE-000856 Diamant Polymers Inc. — Cincinnati | Hamilton | STILL_UNCERTAIN | 0 | 0 | 5 |
| SITE-000868 DRS Industries, Inc. — Holland | Lucas | VERIFIED | 19 | 0 | 3 |
| SITE-000879 Edge Plastics — Mansfield | Richland | VERIFIED | 3 | 0 | 3 |
| SITE-000891 Engineered Profiles, Ironton | Lawrence | STILL_UNCERTAIN | 0 | 8 | 5 |
| SITE-000900 Fenner Dunlop — Port Clinton | Ottawa | VERIFIED | 1 | 4 | 3 |
| SITE-000913 Foam Concepts & Design, Inc. — Hamilton | Butler | VERIFIED | 9 | 0 | 3 |
| SITE-000923 Gilkey Window Company, Inc. Cincinnati — C | Hamilton | VERIFIED | 3 | 0 | 2 |
| SITE-000934 Greenfield Precision Plastics, LLC — Green | Highland | VERIFIED | 4 | 0 | 3 |
| SITE-000942 Harmony Systems & Service, Inc. — Piqua | Miami | VERIFIED | 5 | 0 | 3 |
| SITE-000951 Hub Plastics — Blacklick | Franklin | VERIFIED | 1 | 11 | 3 |
| SITE-000964 Innovative Plastic Molders, Inc. — Vandali | Montgomery | VERIFIED | 3 | 0 | 3 |
| SITE-000972 IPL Inc. — Urbana | Clark | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-000986 Kamco Industries, Inc. West Unity | Williams | STILL_UNCERTAIN | 0 | 2 | 3 |
| SITE-000996 Krom International — Celina | Mercer | VERIFIED | 10 | 0 | 3 |
| SITE-001007 LRBG Chemicals USA, Inc. — Toledo | Lucas | VERIFIED | 4 | 0 | 3 |
| SITE-001017 Mark One Manufacturing — Minster | Auglaize | STILL_UNCERTAIN | 0 | 0 | 4 |
| SITE-001029 Meteor Sealing Systems — Dover | Tuscarawas | STILL_UNCERTAIN | 0 | 5 | 3 |
| SITE-001041 MOLTEN (NORTH AMERICA) CORP | Hancock | STILL_UNCERTAIN | 0 | 4 | 3 |
| SITE-001051 Mullins Rubber Products, Inc. — Riverside | Montgomery | VERIFIED | 4 | 0 | 2 |
| SITE-001061 New Tech Plastics, Inc. — Covington | Miami | VERIFIED | 7 | 0 | 3 |
| SITE-001075 Octal Extrusions Corporation — Cincinnati  | Butler | STILL_UNCERTAIN | 0 | 3 | 3 |
| SITE-001084 Orion Engineered Carbons — Belpre | Washington | STILL_UNCERTAIN | 0 | 1 | 3 |
| SITE-001103 Plas-Tanks Industries, Inc. — Hamilton | Butler | VERIFIED | 5 | 0 | 4 |
| SITE-001113 Plastic Recycling Technology II, Inc. | Van Wert | STILL_UNCERTAIN | 0 | 2 | 2 |
| SITE-001126 Polysource LLC dba Epsilyte — Piqua | Miami | VERIFIED | 6 | 0 | 4 |
| SITE-001135 Proto Plastics, Inc. — Tipp City | Miami | VERIFIED | 16 | 0 | 4 |
| SITE-001150 R & S Technologies, Inc. — Bellevue | Huron | VERIFIED | 5 | 0 | 4 |
| SITE-001162 Return Polymers (Green Recycling) | Clinton | STILL_UNCERTAIN | 0 | 4 | 3 |
| SITE-001171 RJ Plastics Displays and Machining — North | Wood | VERIFIED | 3 | 0 | 2 |
| SITE-001185 Rubber-Seal Medallion — Dayton | Montgomery | VERIFIED | 2 | 0 | 2 |
| SITE-001196 Sealed Air — Ashland | Ashland | STILL_UNCERTAIN | 0 | 2 | 3 |
| SITE-001206 Silgan Plastics — Ottawa | Putnam | STILL_UNCERTAIN | 0 | 7 | 3 |
| SITE-001214 Sperry & Rice Manufacturing, LLC — Killbuc | Holmes | VERIFIED | 7 | 0 | 4 |
| SITE-001224 SumiRiko Inc. — Bluffton | Allen | VERIFIED | 2 | 0 | 4 |
| SITE-001237 Tech-Way Industries, Inc. — Franklin | Warren | VERIFIED | 12 | 0 | 4 |
| SITE-001247 TH Plastics - Findlay Ohio | Hancock | STILL_UNCERTAIN | 0 | 7 | 3 |
| SITE-001259 Toledo Molding & Die — Tiffin | Seneca | VERIFIED | 3 | 1 | 4 |
| SITE-001274 United Security Seals — Columbus | Franklin | STILL_UNCERTAIN | 0 | 0 | 3 |
| SITE-001286 Vi-Cas Mfg. Co., Inc. — Cincinnati | Hamilton | VERIFIED | 4 | 0 | 3 |
| SITE-001294 Western Ohio Packaging — Sidney | Shelby | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-001332 Hawthorn Aero — Miamisburg | Montgomery | VERIFIED | 3 | 0 | 3 |
| SITE-001344 Axium Packaging Inc — 8300 Innovation Camp | Franklin | STILL_UNCERTAIN | 0 | 11 | 2 |
| SITE-001448 Graham Packaging — Mason | Warren | STILL_UNCERTAIN | 0 | 4 | 4 |
| SITE-001457 Creative Products — Holland | Lucas | VERIFIED | 1 | 0 | 2 |
| SITE-001467 Solo Products — Cincinnati | Hamilton | STILL_UNCERTAIN | 0 | 4 | 3 |
| SITE-001514 Tremco CPG — Ashland | Ashland | STILL_UNCERTAIN | 0 | 2 | 3 |
| SITE-001523 Cabbage Cases — Columbus | Franklin | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-001555 Sun Chemical Performance Pigments - Cincin | Hamilton | STILL_UNCERTAIN | 0 | 1 | 3 |
| SITE-001633 Deimling/jeliho Plastics, Inc. — Amelia | Clermont | VERIFIED | 4 | 0 | 2 |
| SITE-001681 KLINGER Thermoseal — Sidney | Shelby | VERIFIED | 4 | 0 | 4 |
| SITE-001693 ABSOLUTE POLYMERS INC — Salem | Columbiana | VERIFIED | 6 | 0 | 4 |
| SITE-001706 ARMORSOURCE LLC — Hebron | Licking | VERIFIED | 1 | 0 | 4 |
| SITE-001737 Dandy Products Inc — Goshen | Clermont | STILL_UNCERTAIN | 0 | 0 | 3 |
| SITE-001752 GK Packaging Inc — Plain City | Madison | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-001766 Microtek Laboratories Inc — Moraine | Montgomery | VERIFIED | 2 | 0 | 3 |
| SITE-001810 Eagle Composites LLC | Butler | VERIFIED | 7 | 0 | 5 |
| SITE-001827 Timco Products Inc | Union | STILL_UNCERTAIN | 0 | 0 | 3 |
| SITE-001872 E.C. Shaw Company | Hamilton | STILL_UNCERTAIN | 0 | 0 | 4 |
| SITE-001901 Seagate Plastics | Lucas | VERIFIED | 3 | 5 | 4 |
| SITE-001925 Cooper Standard Industrial and Specialty G | Tuscarawas | STILL_UNCERTAIN | 0 | 1 | 2 |
| SITE-002006 South Coast Specialty Chemicals LLC | Miami | VERIFIED | 3 | 0 | 2 |
| SITE-002058 Altum LLC | Franklin | VERIFIED | 5 | 0 | 3 |
| SITE-002080 BASF Whitehouse plant site | Lucas | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-002130 Ventra Salem LLC | Columbiana | STILL_UNCERTAIN | 0 | 1 | 3 |
| SITE-003475 Sherwin-Williams — Columbus Plant | Franklin | STILL_UNCERTAIN | 0 | 1 | 1 |

## Hygiene findings (not resolved, for the integrator)

1. **SITE-000694** Company Locations page text is empty (JS/image); Ohio facility named only in certificate material. Page lists Tennessee, Ohio and Mexico facilities.
2. **SITE-000704** AkzoNobel homepage announces an Axalta merger ("Axanzo", EGM 2026-11-30); watch for parent/identity change.
3. **SITE-000715** Amcor site row has no street address; site name says Amcor Rigid Packaging — Napoleon but no fetched page names Napoleon.
4. **SITE-000726** Anomatic is mainly an aluminum anodizer of cosmetic/spirits/pharma packaging; the Blacklick plant is its injection-molding site. Atlas row has no street; New Albany HQ is 8880 Innovation Campus Way.
5. **SITE-000737** Site row named "Atalys Ottoville — Cloverdale": plant address is Cloverdale OH 45827 (Putnam Co.), not Ottoville; no street on the row. HQ is Rochester NY.
6. **SITE-000745** Axium home page says "22 manufacturing sites"; Locations page says "33 facilities". SITE-000745 (Plant 5) has no street on the row; the Locations page lists 8 New Albany addresses (New Albany 1-6, Apex Finishing, 13425 Worthington Rd NW).
7. **SITE-000772** SITE-000772: only Milford address on buckhorninc.com is "400 TechneCenter Drive, Suite 215" (office suite) - likely HQ/office, not a plant. Buckhorn is a Myers Industries company (check parent ORG-000009 link).
8. **SITE-000785** Scope question for owner: Century Label is a label/shrink-sleeve printer (CMC Group division); no resin processing stated, so Ring 1-2 placement is doubtful (R9).
9. **SITE-000810** SITE-000810 has no city or street (county Wood only); org ORG-001147 site is thecsp.com (CSP, a Teijin company); only Auburn Hills MI is printed.
10. **SITE-000833** SITE-000833 has no street on the row; company lists Montpelier OH as Plant #6 at 1701 Magda Dr. Corporate office and Plants 1-3 are in Kendallville IN. Home page text says flagship facility is 316,000 sq ft without naming the city; home page says machines from 100 to 3600 tons while the Injection Molding page says 100 to 5000 tons.
11. **SITE-000846** D.S. Brown site pages give no process or material text (expansion joints/bearings are likely elastomeric but not stated); resources page is a document index.
12. **SITE-000856** diamant-polymer.com prints no US street address or phone; the US site may be a sales/service office (site_type check).
13. **SITE-000868** DRS pages print "Toledo, OH"; Atlas row city is Holland. Home page says "we have the certifications……." with none named (not recorded).
14. **SITE-000891** Engineered Profiles prints two Ohio addresses: 2141 Fairwood Ave, Columbus 43207 and 575 Private Rd 1125, Ironton 45638. Check whether the Columbus location is held in the Atlas.
15. **SITE-000900** Fenner Dunlop also runs a Toledo OH belting plant (named on the same page); check whether it is held. Row has no street.
16. **SITE-000913** Site pages say Cincinnati, Ohio; Atlas row says Hamilton (no street on either).
17. **SITE-000923** Scope question: Gilkey is a window fabricator/installer; no extrusion or molding is stated (Ring placement doubtful, R9). The homepage text contains injected unrelated "online casino" copy (possible site compromise).
18. **SITE-000951** Contact page lists two Blacklick addresses (725 Reynoldsburg-New Albany Rd, and 254 North Street) plus Geneva OH (700 Pro-Gram Pkwy) and Barnhart MO; SITE-000951 has no street. Check whether 254 North Street is a separate site.
19. **SITE-000964** About page header says "Dayton, Ohio"; row is Vandalia (45377).
20. **SITE-000972** IPL Locations page labels the Urbana OH address (1765 W County Line Rd, 43078) "Dayton, Ohio".
21. **SITE-000986** Org website for ORG-000916 is the Japanese parent (kumi.co.jp); the West Unity entry is "KAMCO Industries,Inc., 1001 East Jackson Street".
22. **SITE-001017** Mark One Manufacturing describes global supply-chain/partner-factory sourcing ("why partnering with the right factory is important"); Minster may be an engineering/sourcing office rather than a plant (R9 check). Process mix is castings, stamping, machining - mostly metal.
23. **SITE-001041** Molten site is Japanese-language only; Findlay base address 1835 Industrial Drive is listed under 海外拠点 with no activity; row has no street.
24. **SITE-001051** Mullins site prints only a P.O. Box (24830, Dayton 45424); row says Riverside with street 2949 Valley St. The site is two static pages.
25. **SITE-001061** New Tech Plastics was acquired by Flexible Packaging Partners (FPP) in February 2025 (About page): check parent of record.
26. **SITE-001075** SITE-001075 (Octal Extrusions, West Chester area OH): the org website (alpekpolyester.com) lists no Ohio location; the Locations page shows Octal only in Oman. Possible closed, sold or mis-parented site; needs identity check.
27. **SITE-001103** Plas-Tanks fabricates thermoset (fiberglass) vessels, a fabrication business: check Ring 1-2 fit (R9).
28. **SITE-001113** PRT Contact page gives no city names: addresses 5682 East Ponce De Leon Ave and 9054 North County Road 25A; Atlas row is Van Wert OH. Identify which is Ohio.
29. **SITE-001126** SITE-001126 has no street on the row; the Epsilyte page gives 555 East Statler Rd, Piqua OH 45356.
30. **SITE-001150** R&S Technologies is mainly a machine shop (CNC, waterjet, sprockets); injection molding is a secondary line (the Capabilities page lists a 120-ton press among the machinery).
31. **SITE-001162** SITE-001162 (Return Polymers / Green Recycling, Wilmington OH): the company Locations page lists no Wilmington OH site (Ashland OH, Dowagiac MI, Indianapolis IN, Corsicana TX). Not closure evidence; identity/address check needed.
32. **SITE-001171** Scope question: RJ Plastics is a machining/fabrication and display shop with a warehouse, not a resin processor (R9 / ring check). The Contact page carries individual names and emails (not recorded).
33. **SITE-001185** Site name "Rubber-Seal Medallion — Dayton" and org website medallionrefinish.com: brand is Medallion Refinish by Rubber-Seal Products; row has no street, company prints 5751 North Webster St, Dayton 45414. Mostly automotive refinish coatings (Ring placement check).
34. **SITE-001196** Row name "Sealed Air — Ashland" but org website is liquibox.com (Liquibox, a Sealed Air business); check parent/brand of record.
35. **SITE-001214** Certificate address is 1088 North Main Street, Killbuck 44637-9504; row has no street.
36. **SITE-001237** Tech-Way is a Type 07 FFL (firearms manufacturer) as well as a molder; its site lists paintball/airsoft conversion kits (consider ITAR/defense context only if stated).
37. **SITE-001259** TMD Tiffin street is "North Maule Road" per the company page; row has no street. Manufacturing page lists only 1429 Coining Dr, Toledo.
38. **SITE-001274** SITE-001274: United Security Seals mainly makes lead and wire (metal) tamper seals plus plastic seals; "C-TPAT / ISO 17712" is a seal-standard claim, not a facility certificate. Ring 1-2 fit to confirm.
39. **SITE-001294** SITE-001294 (Western Ohio Packaging, Sidney): TRG Packaging and Display Solutions is a corrugated/containerboard converter (branch 2450 Campbell Road, Sidney); no plastics or rubber process stated. Ring 1-2 doubt (R9).
40. **SITE-001344** SITE-001344 (8300 Innovation Campus Way) is labeled "Apex Finishing" on the company Locations page.
41. **SITE-001457** Existing row value cast_polymer is outside the process vocabulary (flag for the integrator). Scope question: cultured marble/solid-surface may be mineral-filled resin casting; Ring 1-2 fit to confirm.
42. **SITE-001467** Solo Products presents mainly as a distributor of reusable plastic containers plus die cutting/CNC services; no street address on the pages fetched (Atlas has 838 Reedy Street).
43. **SITE-001514** Org website for ORG-000006 is RPM International (corporate); the Tremco CPG site is tremcocpg.com. The RPM Tremco brand pages name no Ashland plant.
44. **SITE-001523** SITE-001523 Cabbage Cases: custom ATA shipping-case builder / Pelican dealer; polymer processing is not stated (Ring 1-2 doubt, R9).
45. **SITE-001633** Home page still carries COVID-19 "essential workforce" text (stale content); no street address on fetched pages.
46. **SITE-001681** KLINGER gaskets are mostly compressed fiber/graphite/metallic; polymer content is PTFE/rubber-coated metal. Check Ring fit.
47. **SITE-001693** Absolute Polymers material page lists several resin names with no text (images); copyright 2019 on every page (stale).
48. **SITE-001706** ArmorSource pages say "composite materials expertise" but name no resin, fiber or molding process; no Hebron street printed on the pages fetched.
49. **SITE-001737** SITE-001737 Dandy Products: equestrian/veterinary padding, flooring and barn equipment (Dandy Products & MAC Sports International, LLC footer); manufacturing process not stated. Ring 1-2 doubt.
50. **SITE-001752** SITE-001752 / ORG-001676: org website gkpackaging.com fails TLS name check on both the apex and www hosts; correct domain unknown.
51. **SITE-001766** Microtek pages announce "Alexium Acquires Microtek from Cavu Group": check parent of record. Specialty-chemical microcapsules; Ring fit to confirm.
52. **SITE-001827** Timco Products makes paper-machine doctor blades from composite material supplied by Joh. Clouth: Ring 1-2 fit doubtful (R9).
53. **SITE-001872** SITE-001872 E.C. Shaw Company: flexographic prepress plates, mounting tapes and cast bronze plaques; Ring 1-2 doubt (R9). Second location in Phoenix AZ.
54. **SITE-001901** SeaGate is part of Grupo Verzatec (home page); injection molding and CNC are in Addison, MI.
55. **SITE-002006** South Coast prints a headquarters at 3415 E US RT 36, Piqua and Plant 1 at 1710 Commerce Drive; "Plant 1" implies other plants. Check whether the HQ address is held.
56. **SITE-002058** altumllc.com is a frameset pointing to altumcomposites.com; the Atlas org website should be updated. Site prints only "Canal Winchester, 43110" (Atlas street: 92 Elm St Ste B).
57. **SITE-002080** SITE-002080 is an rd_center row (BASF Whitehouse plant site); the BASF US locations page names no Whitehouse site in text.
58. **SITE-002130** Row is "Ventra Salem LLC" under org website flex-n-gate.com; the NA Activities page names Ventra only in a link label.

Verdicts and settling facts for every site are in `verdicts.csv`; the evidence rows are in `packet.csv`.
