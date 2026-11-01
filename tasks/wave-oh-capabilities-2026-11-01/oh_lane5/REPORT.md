# Ohio capability wave, lane 5 report (2026-11-01)

This is a packet, not a data change. Nothing under `data/` or elsewhere in the repo was edited; outputs are `packet.csv`, `verdicts.csv` and this report. No `tier_effect` is proposed.

- **Pin:** assignment `oh_lane5_assignment.csv` (79 active Ohio site rows outside PIC-12, ring 1-2, blank processes or markets, parent org with an http website; the list contains two Axium rows and two CVG rows under one org each).
- **Method:** brief `tasks/wave-oh-capabilities-2026-11-01/LANE_BRIEF.md` and PIC-12 tranche 2 method. Company website only (`own_site`; certificate PDFs were read from the company's own domain). Fetches by curl through the configured proxy, page text kept, PDFs read with `pdftotext`. Vocabulary v1.7.6 (`docs/schema/vocab.json`); every in-vocab value was checked against it by script. R3c applied.
- **Quote check:** all 281 packet rows carry the exact fetched URL and a quote of 25 words or fewer; every quote was checked by script as a substring (whitespace and quote-mark normalised) of the fetched text, and all 281 passed, twice (at write time and again against the saved files). No quote came from a WebFetch summary (WebFetch was not used).
- **Privacy:** no individual names, emails or direct phones are in any row (checked by pattern scan).
- **Scratch:** `/tmp/claude-0/wave-oh/lane5/` only, one directory and one counter per site id (`<SITE>/f<n>`), fetches serialized per site behind a lock.

## Results (unit: assigned Ohio site rows, n = 79)

VERIFIED 31 (39%) | STILL_UNCERTAIN 48 | REJECT 0.

No REJECT was issued. Nothing in this lane was closure evidence; every failed fetch was treated as an availability signal.

| field (in-vocab rows) | site scope | org scope | total |
|---|---:|---:|---:|
| processes | 53 | 22 | 75 |
| materials | 70 | 23 | 93 |
| markets_served | 42 | 36 | 78 |
| certifications | 20 | 0 | 20 |
| **all** | **185** | **81** | **266** |

- **Other rows:** 15 OFF-VOCAB `*_other_note` rows (all row-level STILL_UNCERTAIN) and 5 in-vocab certification rows held at STILL_UNCERTAIN (see certificates). Packet total 281 rows: 261 VERIFIED, 20 STILL_UNCERTAIN at row level.
- **Site-scope yield:** 2.3 in-vocab values per assigned site; 6.0 per VERIFIED site; 3.4 per site counting org scope too.
- **Coverage:** 55 of 79 sites received at least one in-vocab value at some scope; 33 at site scope (31 VERIFIED, plus RTP Gahanna and INEOS Lima, which have only STILL_UNCERTAIN site-scope certification rows).
- **Markets:** 18 sites have a site-scope market; 38 have one at any scope.
- **Scope rule applied:** org-scope values (81 rows) were never pushed down to a site. A value is site scope only where a page, a certificate or a plant list names the plant, or the company site shows a single location (stated in each row's notes). A verdict is VERIFIED only with at least one in-vocab site-scope value.
- **Sites with no usable content:** 9 (Associated Plastics, CVG New Albany and CVG Chillicothe, Hamilton Polymers, Logoplaste, Expert Roto, ZeoVation, Prospira, and MEP Manufacturing which has no website on record). All are availability failures or missing data, not closure evidence.

### Certifications recorded (R3c)

| Site | Standard | Basis |
|---|---|---|
| BRP Lima | ISO 9001:2015 | Perry Johnson certificate C2025-04053 for 637 N Jackson St; valid 2025-08-07 to 2028-08-06 |
| K&B Molded Brookville | ISO 9001:2015 | EAGLE certificate 3745 for 9360 W National Rd; valid 2025-11-18 to 2028-11-17 |
| Kraton Belpre | ISO 14001:2015 (RC 14001:2023) | NSF-ISR certificate C0313225-RC8; expires 2029-05-24; scope names styrenic block copolymers at Belpre |
| Core Molding Columbus | IATF 16949:2016, ISO 14001:2015, ISO 9001:2015 | Quality page lists Columbus with these editions; certificate links 404, expiry unverified |
| Boltaron Newcomerstown | ISO 9001:2015, AS9100 Rev D, ISO 14001:2015 | Quality page and footer; certificate not read |
| Green Tokai Brookville | IATF 16949:2016, ISO 9001:2015 | Certifications page: Brookville QMS certificates dated 2025-10-21; PDFs not read |
| HTEI, Pinnacle, Westar | ISO 9001:2015 | Company page names the edition; certificate not read |
| DG Medical | FDA registered | Company page |

**Not recorded** (held as STILL_UNCERTAIN rows or in notes):
- DG Medical ISO 13485: edition not named.
- INEOS Nitriles Lima ISO 9001: edition not named.
- Kraton Belpre ISO 9001: the PDF is image-only.
- RTP Gahanna ISO 9001 and IATF 16949: no editions.
- 6S Products ISO 9001:2015: the certificate linked from its site expired 2023-10-09.
- Green Tokai ISO 14001:2015: certificate dated 2023-04-26, possibly past a three-year cycle.
- SQF (Versa Pak), BRCGS (Pinnpack) and ASI Food Safety (General Films): not in the CERTS vocabulary.

Re-check Core Molding, Boltaron, Green Tokai, HTEI, Pinnacle and Westar when a certificate is available, since expiry was not read.

## Fetches

238 fetches over 78 sites (3.0 per site; MEP Manufacturing has no website, so 0).

- **Availability failures: 18 of 238 (7.6%).**
  - HTTP 403: 5 (CVG apex and www, CVG Chillicothe, Expert Roto apex and www).
  - HTTP 500: 3 (Associated Plastics, every route).
  - Proxy 502 or CONNECT failure: 4 (ZeoVation x2, Logoplaste apex, Core Molding's first try, a Sucuri 502 that recovered).
  - TLS or HTTP/2 error with no content: 2 (Logoplaste www; E-Beam apex, which worked through www).
  - JS-only shell with no text: 3 (Hamilton Polymers 1; Prospira 2, one per host).
  - SiteGround captcha challenge, HTTP 202: 1 (Custom Seal apex, which worked through www; no captcha workaround attempted).
- **404 on guessed or stale URLs: 8**, not site failures (e.g. attachment links, guessed About paths).
- **Other waste:**
  - 3 first-pass homepages came back as undecoded gzip (ChemPrise, Model Graphics, PPC Flex). This was my tool bug (no `--compressed`); it was fixed and the three were refetched.
  - 1 certificate PDF was image-only (Kraton Belpre ISO 9001).
- **Recovered through another host route (not a bypass):** Core Molding (second try), E-Beam (www), Custom Seal (www).

### Deviations from the brief (declared)

1. **Cap exceeded once.** SITE-000744 (Axium New Albany) used 7 fetches: f7 was an accidental duplicate homepage fetch from a mistyped command; it was not used for any row. SITE-001343 (same org) relied on four pages fetched under SITE-000744 plus its own homepage.
2. **User-agent.** The 78 first-pass homepages were fetched with the header `Mozilla/5.0 (compatible; PolymerAtlasResearch/1.0)`. This names the research bot but is Mozilla-prefixed, so it may count as borderline under "no faked user-agent". Every later fetch used `PolymerAtlasResearch/1.0 (data verification; identifies as bot)`. No browser string was ever used. Nothing was retried to get past a 403 or captcha; the only second tries were different hostnames (www or apex) and different URLs.
3. **Wasted fetches** on Core Molding (two 404 attachment URLs) put it at exactly 6.
4. **SITE-002127** used all six fetches (including two certificate PDFs) to establish that the recorded website belongs to a different company, so it yielded no values.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - urethane casting (Action Rubber);
  - continuous ultrasonic welding equipment / end-effector manufacture (Agile Ultrasonics);
  - dispersing and functionalizing carbon nanomaterials (ChemPrise);
  - SMC compounding (Core Molding);
  - desiccant packet and unit-bag manufacture (Flow Dry);
  - elastomer-to-substrate / rubber-to-metal bonding (HTEI, also Action Rubber);
  - latex paint reclamation (American Paint Recyclers);
  - co-extruded film, blown vs cast unstated (General Films);
  - contract electron-beam sterilization and crosslinking (E-BEAM);
  - metal stamping (Flow Dry stamps gaskets and cap liners).
- **Materials with no term:** carbon nanotubes and graphene (ChemPrise), EVOH and EVA (General Films), PTFE read as `fluoropolymers`, FFKM/butyl/CSM/epichlorohydrin read as `specialty_elastomers` (elastomer named in each row's notes), TPO read as `thermoplastics`, silica gel desiccant.
- **Markets with no term:** military ammunition and defense packaging (none met here), carpet cushion / flooring underlay (Scottdel), automotive production-line support (Action Rubber, held off-vocab).
- **Certifications with no term:** SQF (Versa Pak), BRCGS (Pinnpack), ASI Food Safety (General Films).

## Hygiene findings (not resolved, for the integrator)

**Wrong website or identity**
1. **SITE-002127 Tech Mold & Tool Co. (ORG-002127, Tipp City).** The org website hitechmoldtool.com is Hi-Tech Mold & Tool, Inc. of Pittsfield, Massachusetts. Its NQA certificates (ISO 13485:2016 no. 18536, ISO 9001:2015 and AS9100:2016 no. 18631) name 1 Technology Drive West, Pittsfield, and the second says "Single Site". Nothing was recorded for Tipp City.
2. **SITE-001736 D M Tool & Plastics (ORG-001660).** The org website forwardthinkingent.com is Forward Thinking ENT, LLC, a music label.
3. **SITE-001765 MEP Manufacturing (ORG-001689).** The website field holds the placeholder "https://none found/".
4. **SITE-001677 Bridgestone APM.** The org website is Bridgestone's regional corporate page, not a plant page.

**Corporate-family and duplicate questions**
5. **SITE-000783 Centrex Plastics / SITE-001456 CCP Newco / American Plastics.** American Plastics' own Locations page lists 814 West Lima Street, Findlay OH (Centrex's address), Sycamore OH (207 South Griffith Street), Tiffin OH (1780 South County Road #1) and an Innovation Center at 8390 County Road 140, Findlay. Centrex (ORG-000724) and CCP Newco (ORG-001410, site americanplasticsllc.com) look like one family under two orgs.
6. **SITE-000744 and SITE-001343 Axium.** Two rows for one org. Axium lists six New Albany plants (New Albany 1-6), Apex Finishing (8300 Innovation Campus Way) and Vertix Recycling (13425 Worthington Rd NW); several look unheld. SITE-000744 is "New Albany Plant 4" (8900 Smith's Mill Rd N); SITE-001343 is 10015 Innovation Campus Way (= New Albany 6).
7. **SITE-000845 and SITE-001521 CVG.** Two Ohio rows for one org; the site returns 403 to curl.
8. **SITE-001677 Bridgestone APM and SITE-003474 Prospira America.** Both are in Upper Sandusky: a possible successor or duplicate pair between ORG-001604 and ORG-003105.
9. **SITE-001272 United Fiberglass of America.** The website is Creative Composites Group (Hill & Smith Holdings PLC); check the parent of record.
10. **SITE-001161 Retterbush Fiberglass (Piqua).** Arrowhead's own plant page says "Formerly known as Retterbush Fiberglass". Arrowhead also runs Muncie IN and a thermoforming facility.
11. **SITE-000889 Boltaron.** Org named for the legacy Empire Plastics; the company is SIMONA Boltaron Inc., 1 General Street, Newcomerstown (SIMONA AG division).
12. **SITE-000971 Inventive Extrusion Corp.** The company website is Premere Enterprises Inc. (PEI), Bolivar Industrial Park; check the legal name.
13. **SITE-000867 Drew Foam Holdings.** The website is Alleguard; check the org name against the parent.
14. **SITE-001083 ORBIS Urbana.** ORBIS is a Menasha Corporation subsidiary (HQ Oconomowoc WI); its Locations page lists Urbana under Manufacturing.
15. **SITE-001507 Nuvo Packaging.** The company website is Pinnpack, which also lists Oxnard CA. The site name differs.
16. **SITE-001236 Tech Intl.** The company is TECH Tire Repairs / Technical Rubber Company (Johnstown HQ).
17. **SITE-000912 Flow Dry.** The homepage banner says Parker Hannifin has acquired Filtration Group Corporation; check whether Flow Dry sits under Filtration Group.
18. **SITE-000962 Ineos USA Lima.** Lima appears on INEOS's certificates page under INEOS Nitriles, not "Ineos USA".

**Rows that may be offices, distribution or out of scope (scope questions for the owner)**
19. **SITE-000878 Edco.** Edco of Ohio (510 Wayne Ave, Dayton) is a facility of unstated function; HQ and the original plant are Brooklyn NY.
20. **SITE-001213 SpecTape.** The Cincinnati row is typed `office_warehouse`; the company says its converting plant is in Erlanger, Kentucky.
21. **SITE-001050 Mulhern Belting.** A conveyor-belting wholesaler with five or six locations.
22. **SITE-001060 NetProto.** A digital quoting platform with offshore mold building; Holland OH may not be a plant.
23. **SITE-001124 PolyGroup and SITE-001223 Style Crest.** A marketer of specialty polymers and a supplier of manufactured-housing siding/HVAC; neither shows a plant.
24. **SITE-001870 Diversipak and SITE-001826 Surgical Recovery Systems.** A packaging/POP design and sourcing company, and a foam-pillow product company with no address.
25. **Equipment makers and fabricators:**
    - SITE-000703 Agile Ultrasonics (ultrasonic equipment);
    - SITE-001028 Mesa ETP (storage-tank products);
    - SITE-001149 RL Industries (FRP tanks);
    - SITE-001892 Orbit (plastic fabricator);
    - SITE-001039 Model Graphics (labels);
    - SITE-001809 Custom Seal (roofing accessories);
    - SITE-001330 E-BEAM (contract irradiation);
    - SITE-001705 American Paint Recyclers (latex paint);
    - SITE-001997 Roboworld (robot protective covers).
26. **SITE-001016 Marcy Adhesives.** Its Contact page lists two Columbus addresses (43209 and 43219); the row is Lamb Ave 43209.

**Unheld plants and cross-site facts noted on company pages**
27. **SITE-001258 TMD.** Its Locations page also describes a Tiffin OH plant (1440 North Maule Road: injection molding, blow injection, assembly). That sentence was not recorded as an org value because it is plant-specific.
28. **SITE-000933 Green Tokai.** The row is Brookville Plant 1 (55 Robert Wright Dr, HQ); Plant 2 (20 Robert Wright Dr) is unheld, and Maysville KY is out of state.
29. **SITE-000819 Core Molding.** The Columbus row is the HQ plus an SMC compounding/molding plant. Cobourg ISO 14001 and Matamoros IATF certificates carry 2026 expiries (not this site).
30. **SITE-000995 Kraton Belpre.** The site also has an Innovation Center at the same address; the ISO 14001 scope covers the whole fence line.

**Label and field problems**
31. **SITE-000768 BRP.** The home page badge reads "ISO Certificate 9001:2025", but the certificate says ISO 9001:2015.
32. **SITE-001466 Scottdel.** The org is Scottdel; the company's one-page site calls itself "Scotdel Carpet Cushion" and "Scottdel Cushion".
33. **SITE-001692 6S Products.** The ISO 9001:2015 certificate linked from the company site (EAGLE no. 5478, 12800 Wenger Road, Anna) expired 2023-10-09. The link is stale or the company is no longer certified.
34. **SITE-001920 Expert Roto Molding.** The row name mixes brand and parent names (Eger Products, a division of Kaivac); the site returns 403 to curl.
35. **SITE-001705, SITE-001330, SITE-001809 and similar.** Several ring-1/2 plant rows are services or fabrication businesses outside the plastics/rubber processor scope (see item 25).
36. **SITE-001284 Versa Pak.** Its pages name SQF (since 2016) and an Interstate Milk Shippers partial-plant listing; neither has a vocabulary term.
37. **SITE-000736, SITE-000941, SITE-001006, SITE-002078, SITE-003474.** Websites unreachable or JS-only through this route (HTTP 500 on every path; JS app shell; TLS issuer error; proxy tunnel 502; JS shell). They need another route, not a closure finding.

## Per-site table (unit: assigned site rows; value counts are in-vocab rows)


| Site | Name | Verdict | Site values | Org values | OFF-VOCAB notes | Fetches |
|---|---|---|---:|---:|---:|---|
| SITE-000693 | Action Rubber Co., Inc. — Dayton | VERIFIED | 20 | 0 | 2 | 5 |
| SITE-000703 | Agile Ultrasonics — Columbus | VERIFIED | 5 | 0 | 1 | 3 |
| SITE-000714 | Amcor Rigid Packaging — Bellevue | STILL_UNCERTAIN | 0 | 3 | 0 | 2 |
| SITE-000724 | Amsty Hanging Rock — Ironton | VERIFIED | 4 | 1 | 0 | 5 |
| SITE-000736 | Associated Plastics Corp. — Ada | STILL_UNCERTAIN | 0 | 0 | 0 | 3 |
| SITE-000744 | Axium Packaging : New Albany Plant 4 | STILL_UNCERTAIN | 0 | 10 | 0 | 7 |
| SITE-000756 | BASF Corporation — Greenville | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-000768 | BRP Manufacturing Company — Lima | VERIFIED | 13 | 0 | 0 | 3 |
| SITE-000783 | Centrex Plastics, LLC — Findlay | VERIFIED | 3 | 0 | 0 | 2 |
| SITE-000792 | ChemPrise — Cincinnati | STILL_UNCERTAIN | 0 | 0 | 2 | 2 |
| SITE-000809 | Continental Structural Plastics — Carey | STILL_UNCERTAIN | 0 | 3 | 0 | 4 |
| SITE-000819 | Core Molding Technologies, Inc. — Columbus | VERIFIED | 6 | 0 | 1 | 6 |
| SITE-000832 | Creative Foam — Dayton | STILL_UNCERTAIN | 0 | 4 | 0 | 3 |
| SITE-000845 | CVG - Commercial Vehicle Group | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-000855 | DG Medical — Centerville | VERIFIED | 4 | 0 | 0 | 1 |
| SITE-000867 | Drew Foam Holdings — Lancaster | STILL_UNCERTAIN | 0 | 4 | 0 | 3 |
| SITE-000878 | Edco Supply Corporation — Dayton | STILL_UNCERTAIN | 0 | 4 | 0 | 3 |
| SITE-000889 | Empire Plastics — Newcomerstown | VERIFIED | 9 | 0 | 0 | 3 |
| SITE-000899 | Fabshapes, a Division of Polymershapes — Tipp Ci | STILL_UNCERTAIN | 0 | 4 | 0 | 3 |
| SITE-000912 | Flow Dry Technology, Inc. — Brookville | VERIFIED | 5 | 0 | 1 | 4 |
| SITE-000922 | GERRESHEIMER PRIMARY PACKAGING PLASTICS NA — Ber | STILL_UNCERTAIN | 0 | 2 | 0 | 2 |
| SITE-000933 | GREEN TOKAI CO — Brookville | VERIFIED | 2 | 3 | 0 | 6 |
| SITE-000941 | Hamilton Polymers — Leetonia | STILL_UNCERTAIN | 0 | 0 | 0 | 1 |
| SITE-000950 | High Tech Elastomers — Vandalia | VERIFIED | 16 | 0 | 1 | 5 |
| SITE-000962 | Ineos USA — Lima | STILL_UNCERTAIN | 1 | 0 | 0 | 3 |
| SITE-000971 | Inventive Extrusion Corp. — Bolivar | VERIFIED | 6 | 0 | 0 | 5 |
| SITE-000985 | K & B Molded Products, Div. of Kuhns Mold & Tool | VERIFIED | 7 | 0 | 0 | 5 |
| SITE-000995 | Kraton Corporation — Belpre | VERIFIED | 4 | 0 | 0 | 5 |
| SITE-001006 | Logoplaste Lima — Lima | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-001016 | Marcy Adhesives — Columbus | STILL_UNCERTAIN | 0 | 3 | 0 | 4 |
| SITE-001028 | Mesa ETP — Cincinnati | VERIFIED | 2 | 0 | 0 | 3 |
| SITE-001039 | MODEL GRAPHICS — West Chester | VERIFIED | 2 | 0 | 0 | 3 |
| SITE-001050 | Mulhern Belting, Inc. — Fairfield | STILL_UNCERTAIN | 0 | 0 | 0 | 3 |
| SITE-001060 | NetProto — Holland | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-001071 | Nu-Tech Polymers — Cincinnati | VERIFIED | 6 | 0 | 0 | 4 |
| SITE-001083 | ORBIS Urbana | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-001098 | Pinnacle Industrial Enterprises — Bowling Green | VERIFIED | 9 | 0 | 0 | 4 |
| SITE-001111 | PLASTIC PACKAGING TECHNOLOGIES, LLC — Columbus | STILL_UNCERTAIN | 0 | 3 | 0 | 5 |
| SITE-001124 | PolyGroup Inc. — Cincinnati | STILL_UNCERTAIN | 0 | 0 | 0 | 3 |
| SITE-001134 | Protective Packaging Solutions — Cincinnati | STILL_UNCERTAIN | 0 | 2 | 0 | 3 |
| SITE-001149 | R L Industries — Fairfield | VERIFIED | 11 | 0 | 0 | 4 |
| SITE-001161 | Retterbush Fiberglass Corp. - A division of Arro | VERIFIED | 6 | 0 | 0 | 3 |
| SITE-001170 | Ring Container Technologies — Sidney | STILL_UNCERTAIN | 0 | 3 | 0 | 2 |
| SITE-001184 | RTP Company — Gahanna | STILL_UNCERTAIN | 2 | 2 | 0 | 2 |
| SITE-001195 | Seal-Jet of Ohio — Cincinnati | VERIFIED | 6 | 0 | 0 | 1 |
| SITE-001205 | Sika Corp. — Marion | STILL_UNCERTAIN | 0 | 0 | 0 | 3 |
| SITE-001213 | SpecTape, Inc. — Cincinnati | STILL_UNCERTAIN | 0 | 5 | 0 | 2 |
| SITE-001223 | Style Crest Enterprises — Fremont | STILL_UNCERTAIN | 0 | 0 | 0 | 3 |
| SITE-001236 | Tech Intl — Johnstown | STILL_UNCERTAIN | 0 | 2 | 0 | 2 |
| SITE-001246 | TH Plastics - Bowling Green | STILL_UNCERTAIN | 0 | 5 | 0 | 3 |
| SITE-001258 | Toledo Molding & Die — Bowling Green | VERIFIED | 1 | 1 | 0 | 3 |
| SITE-001272 | United Fiberglass of America, Inc. — Springfield | VERIFIED | 2 | 0 | 0 | 5 |
| SITE-001284 | Versa Pak — Celina | VERIFIED | 5 | 0 | 1 | 4 |
| SITE-001293 | Westar Plastics, LLC — Bryan | VERIFIED | 7 | 0 | 0 | 4 |
| SITE-001330 | E-BEAM Services, Inc. — Lebanon | STILL_UNCERTAIN | 0 | 3 | 1 | 5 |
| SITE-001343 | Axium Packaging Inc — 10015 Innovation Campus Wa | STILL_UNCERTAIN | 0 | 10 | 0 | 1 |
| SITE-001447 | Graham Packaging — Findlay | STILL_UNCERTAIN | 0 | 3 | 0 | 4 |
| SITE-001456 | CCP Newco — Tiffin | STILL_UNCERTAIN | 0 | 2 | 0 | 3 |
| SITE-001466 | Scottdel — Swanton | STILL_UNCERTAIN | 0 | 0 | 1 | 1 |
| SITE-001507 | Nuvo Packaging — Columbus | STILL_UNCERTAIN | 0 | 5 | 1 | 3 |
| SITE-001521 | AdvancTEK — Chillicothe (CVG) | STILL_UNCERTAIN | 0 | 0 | 0 | 1 |
| SITE-001554 | Sun Chemical Performance Pigments - Amelia | STILL_UNCERTAIN | 0 | 2 | 0 | 3 |
| SITE-001602 | American Nitrile Operations LLC — Grove City | VERIFIED | 4 | 0 | 0 | 3 |
| SITE-001677 | Bridgestone APM Company — Upper Sandusky | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-001692 | 6S PRODUCTS LLC — Anna | VERIFIED | 2 | 0 | 0 | 4 |
| SITE-001705 | AMERICAN PAINT RECYCLERS LLC — Van Wert | VERIFIED | 1 | 0 | 1 | 1 |
| SITE-001736 | D M Tool & Plastics Inc — Lewisburg | STILL_UNCERTAIN | 0 | 0 | 0 | 1 |
| SITE-001751 | General Films Inc — Covington | VERIFIED | 6 | 0 | 2 | 4 |
| SITE-001765 | MEP Manufacturing Inc — Genoa | STILL_UNCERTAIN | 0 | 0 | 0 | 0 |
| SITE-001809 | Custom Seal, Inc. | VERIFIED | 4 | 0 | 0 | 4 |
| SITE-001826 | Surgical Recovery Systems LLC | STILL_UNCERTAIN | 0 | 2 | 0 | 2 |
| SITE-001870 | Diversipak Inc | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-001892 | Orbit Manufacturing Inc. | VERIFIED | 4 | 0 | 0 | 1 |
| SITE-001920 | Expert Roto Molding (Eger Products, a Division o | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-001997 | Roboworld, LLC | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-002051 | Savko Plastic Pipe & Fittings | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-002078 | ZeoVation, Inc. | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |
| SITE-002127 | Tech Mold & Tool Co. | STILL_UNCERTAIN | 0 | 0 | 0 | 6 |
| SITE-003474 | Prospira America — Upper Sandusky Plant | STILL_UNCERTAIN | 0 | 0 | 0 | 2 |

Verdicts and settling facts are in `verdicts.csv`; every row, quote and URL is in `packet.csv`.
