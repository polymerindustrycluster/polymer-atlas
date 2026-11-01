# Ohio capability wave, lane 2 report (2026-11-01)

This is a packet, not a data change. The lane did not edit `data/`, allocate IDs, commit or push. It proposes no `tier_effect`.

- **Pin:** repo HEAD `990919b` at lane start. The wave population is pinned at `eb79f3b`.
- **Assignment:** `oh_lane2_assignment.csv`, 80 Ohio site rows outside PIC-12 (ring 1-2, blank `processes` or `markets_served`, parent org with an http website).
- **Method:** the PIC-12 tranche 2 method, with vocabulary v1.7.6 and R3c. Every row is `own_site` (company website, or the certificate PDFs it links). Fetches were curl only, through the configured proxy. PDFs were read with `pdftotext`. No faked user-agents, TLS bypass or captcha workarounds.
- **Quote check:** all 388 quotes are 25 words or fewer and passed a script check as substrings of the saved page text. The check normalises Unicode, zero-width spaces and whitespace, because some pages carry zero-width characters and PDFs carry ligatures.
- **Scratch:** `/tmp/claude-0/wave-oh/lane2/` only. Each site had its own numbered, locked files. Fetches ran in parallel across sites and never in parallel within one site, so no file collisions occurred.

## Results (unit: assigned Ohio site rows, n = 80)

**VERIFIED 42 (52.5%) · STILL_UNCERTAIN 38 · REJECT 0.**

| field (in-vocab rows) | site scope | org scope | total |
|---|---:|---:|---:|
| processes | 82 | 28 | 110 |
| materials | 62 | 31 | 93 |
| markets_served | 73 | 43 | 116 |
| certifications | 19 | 9 | 28 |
| **all** | **236** | **111** | **347** |

- **Row-level STILL_UNCERTAIN, in-vocab rows:** 18 of the 347. 13 are certification or cleanroom rows (ISO 9001 named without an edition at 6 sites, ISO 13485 and IATF at PMC, IATF at Superior Trim, ITAR and FDA at Velocity, plus APS's "Class 100,000 cleanroom" mapped to `cleanroom_iso8` and "FDA certification" mapped to `fda_registered`). The other 5 are:
  - Capital Resin "amino resins" mapped to melamine/urea-formaldehyde;
  - National Metal Shapes "vinyl mouldings";
  - Spartech "sheet and roll stock" mapped to sheet extrusion;
  - Wavelock "vacuum molding" mapped to vacuum forming;
  - Dura Temp's rotational-molding mold-release market (a distribution line, not plant output).
- **Off-vocab rows (`*_other_note`, marked OFF-VOCAB):** 41. They are 24 processes, 8 certifications, 5 materials and 4 markets.
- **A VERIFIED verdict** means at least one in-vocab site-scope row is VERIFIED. This holds for all 42 (checked by script).

**Yield:**
- **Site-scope VERIFIED values:** 225, which is 2.8 per assigned site and 5.4 per VERIFIED site.
- **All scopes together** (in-vocab rows, including row-level STILL_UNCERTAIN): 347, or 4.3 per site.
- **Coverage:** 66 of 80 sites got at least one in-vocab row.
- **Markets:** present at site scope at 29 of 80 sites, and at 53 of 80 counting org scope.
- **Typical site-scope winners:** single-address companies (injection molders, fabricators, film and foam converters) and plants named on a plant-list page.

**Scope conventions used:**
- **Org scope:** multi-plant parents with no page tying the capability to this address. Of the 38 STILL_UNCERTAIN sites, 21 carry org-scope in-vocab values only, 3 carry only row-level STILL_UNCERTAIN site values (Dura Temp, Milacron, Wavelock), and 14 carry no in-vocab value (the 10 unreachable sites plus Avient/Plast-O-Meric, Fresh Products, Dominator and OH 4).
- **City-grain site scope (named in the packet notes; the integrator may demote them):**
  - Axium (New Albany): the history timeline names Plants 2, 3, 4 and 5, and the PCR plant, in New Albany. The row has no street and the campus lists 8 addresses.
  - Spartech (Greenville): plant pages name two Greenville plants, and the row has no street.
  - DK Manufacturing (Frazeysburg): the facilities page lists the plant, but the activity is a company-wide statement.
  - TekniPlex (Holland): lab equipment listed under the Global Innovation Center.

## Certificates and certification currency (R3c)

| Site | Standard | Evidence | Valid to |
|---|---|---|---|
| PCPI Plastics (SITE-001091) | ISO 9001:2015 | certificate PDF, same address | 2029-02-28 |
| Primary Packaging (SITE-001131) | ISO 9001:2015 | certificate PDF, Bolivar address | 2029-10-22 (from 2026-10-23) |
| Extol of Ohio (SITE-000896) | ISO 9001:2015 | page states certificate no. and date; PDF not fetched | 2029-08-27 |
| Golden Eagle (SITE-000929) | SQF Edition 9 | certificate PDF, Milford site | 2027-04-04 (not recorded; no SQF term in vocab) |

**Recorded on a named edition, certificate not fetched:**
- Decorative Paint: ISO 9001:2015 and IATF 16949:2016.
- B&B Molded: ISO 9001:2015.
- World Class Plastics: ISO 9001:2015.
- K. Wm. Beach: ISO 9001:2015 and ISO 14001:2015.
- Renegade: ISO 9001:2015 and AS9100D.

**Not recorded:**
- **APS (SITE-000700):** ISO 9001:2008 is a superseded edition. Flagged only.
- **First Choice Packaging (SITE-000906):** BRC "Issue 6, August 2019" is superseded. The home-page footer reads "ISO 9001- 20015", a typo. The ISO row is row-level STILL_UNCERTAIN.
- **Velocity Group:** "ISO 9001:2016" is not a published edition. ITAR and FDA are listed with no registration number, so both rows are STILL_UNCERTAIN.
- **IC3D (SITE-000956):** ISO 9001 and AS9100 are marked "Pending".
- **Wavelock (SITE-001638):** IATF certificates cover the three Japanese plants only. No Ohio certificate is shown.
- **"ISO 9001 certified" with no edition:** recorded as row-level STILL_UNCERTAIN for Capital Resin, Rubbertec, First Choice, Thermoid (Bellefontaine), Milacron (Mt. Orab) and PMC (ISO 13485 and IATF, org scope).

## Fetches

353 attempts, 4.4 per site. Per site: 1 site used 1; 7 used 2; 16 used 3; 3 used 4; 40 used 5; 13 used 6. **No site exceeded the cap of 6.**

**Failures: 34 of 353 (9.6%).**
- **Route or availability failures (27):**
  - 14 × HTTP 403: Cloudflare or CloudFront blocks at H.B. Fuller, Magnum Tapes, Kansai Helios and three Westlake pages; Americas Styrenics "Malware detected"; Inno-Pak.
  - 5 × HTTP 406: Mod Security at 31 INC and Ridge.
  - 6 × connection reset or TLS: Aries (3 connection resets) and Ashland (3 "unable to get local issuer certificate").
  - 1 × timeout: TekniPlex, which succeeded on a retry via the www host.
  - 1 × HTTP 500: Titan's guessed /about/locations.
- **HTTP 404 (7):** 5 URLs I guessed and 2 stale site links.

**10 sites yielded no usable content.** All 10 are availability failures only, never closure evidence:
- SITE-000687 31 INC
- SITE-000721 Americas Styrenics
- SITE-000733 Aries
- SITE-000938 H.B. Fuller
- SITE-001011 Magnum Tapes
- SITE-001166 Ridge
- SITE-001686 Kansai Helios
- SITE-002064 Ashland
- SITE-003327 Budenheim (a script-rendered shell with one word of text)
- SITE-003899 Inno-Pak

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - nitrogen gas-assist injection molding;
  - drape forming;
  - unspecified molding/casting;
  - "welding/bonding" with no type stated;
  - chemical toll manufacturing in reactors;
  - metal stamping;
  - composite spray-up;
  - composite resin manufacture;
  - prepreg and adhesive-film manufacture;
  - plastics-machinery manufacture;
  - heavy-duty bag converting and slitting;
  - liquid filling (AeroFlexx);
  - cast polymer / cultured marble;
  - film-insert molding and wrapping with decorative film;
  - recycled-rubber mat and bumper manufacture;
  - laser cutting and engraving;
  - "thermo-rubber" injection molding.
- **Materials with no term:** PBT, PEI, PPS, PES, PI, PPA, PSU, PPSU, HTN; polyimide, bismaleimide and cyanate-ester resin systems; "polyolefins" with PE/PP unstated; proprietary hot-glass-handling composites.
- **Markets with no term:**
  - mining;
  - glass-container manufacturing;
  - aluminum extrusion and can fabrication;
  - commercial trucking fleets;
  - construction, mining and forestry equipment tires.
  - Commercial-truck OEM interiors (Superior Trim Springfield) were mapped to `automotive_oem` with a note.
- **Certifications with no term:** FSSC 22000/GFSI, BRCGS, SQF, SOCMA ChemStewards.
- **Equivalence question:** "Class 100,000 cleanroom" (APS) is US Fed Std 209E wording. It is not an ISO 14644 class statement, so the `cleanroom_iso8` row is row-level STILL_UNCERTAIN.
- **Mapping choices the integrator may revisit:**
  - "Medical & Pharma" produced both `medical_healthcare_general` and `pharmaceutical_biotech`.
  - "Home & Fabric Care" packaging mapped to `packaging_consumer`.
  - Whirlpool as a customer was left as `consumer_goods_housewares` because the page says "consumer products".

## Hygiene findings (not resolved, for the integrator)

**Rows that are HQs, offices, labs or not plants (scope questions for the owner):**
1. **SITE-001117 PMC SMART Solutions.** The contact page labels 9825 Kenwood Rd Suite 302, Blue Ash "Company Headquarters". The only "Manufacturing Location" is Shelbyville, Indiana. The row is typed manufacturing_plant.
2. **SITE-001242 TekniPlex.** The row is the Global Innovation Center, an R&D and pilot lab, typed manufacturing_plant.
3. **SITE-001035 Milacron Mt. Orab.** The Mt. Orab row is on the locations page as "ISO 9001 Certified". Milacron is a plastics-machinery maker, so the row is equipment manufacturing. Global HQ is 4165 Half Acre Rd, Batavia (check whether it is held).
4. **SITE-001444 AeroFlexx.** The page says AeroFlexx fills product at West Chester. No forming or converting is stated.
5. **SITE-001452 Agean Bath.** The row address (9756 Princeton Glendale Rd) is the "Cincinnati Showroom", and the page calls it West Chester or Cincinnati in different places. The site claims "Local Manufacturing" without a plant address. Hilliard and Dayton showrooms are also listed.
6. **SITE-001461 Fresh Products.** The About page says over 95% of products are made in Toledo. 30600 Oregon Rd, Perrysburg is printed as "Fresh Products Office". The row carries `injection_molding`, which nothing fetched confirms.
7. **SITE-002099 OH 4 Industries.** This is a cup-holder brand. Its own page says an outside Ohio manufacturer molds the product. No plant is indicated at the row address.
8. **SITE-001915 ProVia.** Walnut Creek is labelled Corporate HQ in a review widget. No page names a plant process.
9. **SITE-000918 Franklin.** 2020 Bruck St is labelled Corporate Headquarters only.
10. **SITE-001220 Storopack.** Cincinnati is labelled "Head Office (Packaging)", with no production statement.
11. **SITE-000764 Bob Sumerel Tire.** This is a commercial tire dealer and service group with 24 locations. Retreading is stated for "all locations" but Dover is not named.
12. **SITE-001056 National Metal Shapes.** Mostly metal floor trim (zinc, brass, aluminum) with water-jet and powder-coat services, plus "vinyl mouldings". The polymer scope is in question.
13. **SITE-000851 Decorative Paint.** The site paints plastics. Molding is done "via strategic partners", so `injection_molding` was not recorded.
14. **SITE-000874 Dura Temp.** Hot-glass-handling composites and distributed lubricants. No vocab process or polymer is stated.
15. **SITE-000956 IC3D** and **SITE-000733 Aries** are typed hq_only. IC3D does large-format 3D printing in Columbus per its own pages. The Aries site was unreachable.
16. **SITE-001699 Dominator Race Products.** This is a parts shop. The only capability text is a navigation label "Composite Body Panels".

**Unheld or ambiguous plants and addresses:**
17. **SITE-000789 CNG.** "Lexington Campus" is five plants at 230 Industrial Dr. CNG also lists Ohio plants at 1188 S Houk Rd, Delaware; 8333 Navarre Rd SE, Massillon (Stark County, PIC-12); and 2355 W 4th St, Ontario (44906). Check whether they are held.
18. **SITE-000741 Axium.** The locations page lists 8 New Albany addresses, including Apex Finishing (8300 Innovation Campus Way) and Vertix Recycling (13425 Worthington Rd NW). The row has no street.
19. **SITE-001210 Spartech.** There are two Greenville plants. Greenville is at 1050 Landsdowne Ave. Jaysville (6010 Jaysville-St Johns Rd) is a finishing and warehousing site. The row has no street, and one address should be one site.
20. **SITE-001230 Superior Trim.** The Springfield row maps to 5225 Prosperity Dr. Findlay has a main plant (2151 Industrial Dr), Formed Products (5500 Fostoria Rd) and Molded Products. Check whether they are held.
21. **SITE-000860 DK Manufacturing.** A second facility is listed in Lancaster, OH. Check whether it is held.
22. **SITE-001857 American Plastic.** Review text says "go to their new address on McKinley (not Delashmut)". Check for a stale Delashmut address row.

**Identity, parent and website mismatches:**
23. **SITE-000827.** The org name is Crane Performance Siding L L C North, and the website is Westlake Royal Building Products. The name is not printed on the surviving pages.
24. **SITE-001144.** The row is "LMI Custom Mixing". The page is Quanex Custom Mixing, ex-LMI, and prints no town.
25. **SITE-001107.** The row is "Plast-O-Meric", under Avient's website.
26. **SITE-001699.** The org name is AEROTECH STYLING INC and the site is Dominator Race Products.
27. **SITE-002034.** `unitedconvertinginc.com` serves StockPKG Films pages (`stockpkgfilms.com`). That is a rebrand or new-owner redirect. The phone area code is Nebraska, and no street was printed on the fetched pages.
28. **SITE-001686.** The org website is a `.eu` Kansai Helios domain behind a Cloudflare challenge. A US site may exist.
29. **SITE-000947 Thermoid.** HBD/Thermoid lists three plants (Bellefontaine OH, Chanute KS, Oneida TN). Only the Ohio plant is in scope here.
30. **SITE-001638 Wavelock.** The page names "Nagoya and Ohio plants" for molding. The IATF certificate list omits Ohio.

**Field-level problems:**
31. **Existing values outside the vocabulary:** SITE-001452 `cast_polymer`; SITE-003327 free-text processes and materials; SITE-003899 free-text processes and materials.
32. **Stale pages:** JMS Composites (SITE-000980) footer is 2019. IC3D's capabilities PDF is a 2017 upload. Allied Plastics' healthcare page is a COVID-era story.

## Per-site results

| site_id | site | verdict | site-scope in-vocab rows | org-scope in-vocab rows | off-vocab rows | fetches (failed) |
|---|---|---|---:|---:|---:|---|
| SITE-000687 | 31 INC — Newcomerstown | STILL_UNCERTAIN | 0 | 0 | 0 | 3 (3) |
| SITE-000700 | Advanced Plastic Systems — Gahanna | VERIFIED | 5 | 0 | 2 | 5 (0) |
| SITE-000710 | Allied Plastics — Toledo | VERIFIED | 10 | 0 | 1 | 4 (0) |
| SITE-000721 | Americas Styrenics — Marietta | STILL_UNCERTAIN | 0 | 0 | 0 | 3 (3) |
| SITE-000733 | Aries Science and Technology LLC — Columbus | STILL_UNCERTAIN | 0 | 0 | 0 | 3 (3) |
| SITE-000741 | Axium Packaging Inc — New Albany | VERIFIED | 6 | 5 | 1 | 5 (0) |
| SITE-000751 | B&B Molded Products Inc. — Defiance | VERIFIED | 20 | 0 | 2 | 6 (0) |
| SITE-000764 | Bob Sumerel Tire Co — Dover | STILL_UNCERTAIN | 0 | 2 | 1 | 6 (0) |
| SITE-000778 | Capital Resin Corporation (CRC) | VERIFIED | 9 | 0 | 2 | 5 (0) |
| SITE-000789 | Charter Next Generation — Lexington Campus | STILL_UNCERTAIN | 0 | 7 | 1 | 3 (0) |
| SITE-000804 | Comfort Line — Toledo | VERIFIED | 3 | 0 | 0 | 5 (0) |
| SITE-000816 | CoolSeal USA — Perrysburg | VERIFIED | 5 | 0 | 0 | 5 (0) |
| SITE-000827 | CRANE PERFORMANCE SIDING L L C NORTH — Colum... | STILL_UNCERTAIN | 0 | 2 | 0 | 5 (3) |
| SITE-000840 | CSP North Baltimore | STILL_UNCERTAIN | 0 | 5 | 1 | 6 (0) |
| SITE-000851 | Decorative Paint Inc. — Montpelier | VERIFIED | 8 | 0 | 1 | 5 (0) |
| SITE-000860 | Dk Manufacturing Frayezburg — Frazeysburg | VERIFIED | 2 | 1 | 0 | 5 (0) |
| SITE-000874 | Dura Temp — Holland | STILL_UNCERTAIN | 1 | 0 | 3 | 6 (0) |
| SITE-000884 | Elledge Gasketing & Supply Co. — Lewis Center | VERIFIED | 4 | 0 | 1 | 5 (0) |
| SITE-000896 | Extol of Ohio — Norwalk | VERIFIED | 4 | 0 | 0 | 5 (0) |
| SITE-000906 | First Choice Packaging — Fremont | VERIFIED | 8 | 0 | 1 | 5 (0) |
| SITE-000918 | Franklin Adhesives & Polymers — Columbus | STILL_UNCERTAIN | 0 | 4 | 0 | 6 (0) |
| SITE-000929 | Golden Eagle Extrusions, Inc. — Milford | VERIFIED | 7 | 0 | 2 | 5 (0) |
| SITE-000938 | H B FULLER CO — Blue Ash | STILL_UNCERTAIN | 0 | 0 | 0 | 2 (2) |
| SITE-000947 | HBD/Thermoid, Inc. — Bellefontaine | VERIFIED | 2 | 5 | 0 | 6 (0) |
| SITE-000956 | IC3D, Inc. — Columbus | VERIFIED | 5 | 0 | 1 | 5 (0) |
| SITE-000968 | International Cushioning Company — Fremont | STILL_UNCERTAIN | 0 | 3 | 0 | 5 (0) |
| SITE-000980 | JMS Composites — Springfield | VERIFIED | 14 | 0 | 1 | 5 (0) |
| SITE-000990 | Klarity Medical Products, Inc — Heath | VERIFIED | 1 | 0 | 0 | 5 (0) |
| SITE-001001 | Lear Corporation - Hebron | STILL_UNCERTAIN | 0 | 2 | 0 | 3 (1) |
| SITE-001011 | Magnum Tapes & Films — Marietta | STILL_UNCERTAIN | 0 | 0 | 0 | 2 (2) |
| SITE-001023 | Maverick Molding — Blue Ash | VERIFIED | 1 | 0 | 2 | 1 (0) |
| SITE-001035 | Milacron — Mt. Orab | STILL_UNCERTAIN | 1 | 1 | 1 | 3 (0) |
| SITE-001047 | MTM Molded Products Company (Factory - 01) | VERIFIED | 1 | 0 | 0 | 5 (0) |
| SITE-001056 | National Metal Shapes Inc. — Delaware | STILL_UNCERTAIN | 0 | 2 | 1 | 5 (0) |
| SITE-001068 | Northwestern Ohio Foam Packaging, Inc. — Wau... | VERIFIED | 7 | 0 | 0 | 5 (1) |
| SITE-001079 | Olan Plastics, Inc. — Canal Winchester | VERIFIED | 6 | 0 | 1 | 3 (0) |
| SITE-001091 | Pcpi Plastics — De Graff | VERIFIED | 4 | 0 | 0 | 5 (0) |
| SITE-001107 | Plast-O-Meric, Inc. — North Baltimore | STILL_UNCERTAIN | 0 | 0 | 0 | 2 (0) |
| SITE-001117 | Pmc Smart Solutions — Blue Ash | STILL_UNCERTAIN | 0 | 19 | 1 | 6 (0) |
| SITE-001131 | Primary Packaging, Inc. — Bolivar | VERIFIED | 5 | 0 | 1 | 6 (0) |
| SITE-001144 | LMI Custom Mixing | STILL_UNCERTAIN | 0 | 6 | 0 | 3 (0) |
| SITE-001157 | Renegade Materials Corp. — Miamisburg | VERIFIED | 5 | 0 | 2 | 5 (0) |
| SITE-001166 | Ridge Corporation — Pataskala | STILL_UNCERTAIN | 0 | 0 | 0 | 2 (2) |
| SITE-001178 | Roppe Holding (American Thermoplastic Extrus... | STILL_UNCERTAIN | 0 | 3 | 0 | 5 (0) |
| SITE-001191 | Sapper Plastics — Piketon | VERIFIED | 3 | 0 | 0 | 3 (0) |
| SITE-001202 | Shirley K's — Zanesville | VERIFIED | 14 | 0 | 0 | 5 (0) |
| SITE-001210 | Spartech — Greenville | VERIFIED | 4 | 1 | 2 | 5 (0) |
| SITE-001220 | Storopack — Cincinnati | STILL_UNCERTAIN | 0 | 1 | 0 | 3 (0) |
| SITE-001230 | SUPERIOR TRIM SPRINGFIELD DIV | VERIFIED | 2 | 1 | 1 | 6 (0) |
| SITE-001242 | TekniPlex, Inc. - Global Innovation Center | VERIFIED | 5 | 2 | 0 | 4 (1) |
| SITE-001252 | Titan Tire — Bryan | STILL_UNCERTAIN | 0 | 2 | 1 | 3 (1) |
| SITE-001266 | Trinity Specialty Compounding — West Unity | STILL_UNCERTAIN | 0 | 5 | 0 | 6 (1) |
| SITE-001281 | Ventek Solutions — Findlay | STILL_UNCERTAIN | 0 | 9 | 0 | 5 (0) |
| SITE-001290 | Vinylmax OH — Hamilton | VERIFIED | 3 | 0 | 0 | 5 (0) |
| SITE-001303 | World Class Plastics, Inc. — Russells Point | VERIFIED | 8 | 0 | 0 | 5 (0) |
| SITE-001340 | Advanced Composites, Inc. — 2680 Ross Street | STILL_UNCERTAIN | 0 | 4 | 0 | 5 (0) |
| SITE-001444 | AeroFlexx — West Chester | STILL_UNCERTAIN | 0 | 3 | 1 | 2 (0) |
| SITE-001452 | Agean Marble — West Chester | STILL_UNCERTAIN | 0 | 1 | 1 | 4 (0) |
| SITE-001461 | Fresh Products — Perrysburg | STILL_UNCERTAIN | 0 | 0 | 0 | 5 (0) |
| SITE-001492 | Velocity Group — Cambridge | VERIFIED | 1 | 7 | 0 | 6 (0) |
| SITE-001518 | PPG Industries — Delaware | STILL_UNCERTAIN | 0 | 2 | 0 | 2 (1) |
| SITE-001541 | Vanguard Paints & Finishes — Marietta | VERIFIED | 4 | 0 | 0 | 6 (0) |
| SITE-001592 | Impact Printing and Design — Columbus | VERIFIED | 10 | 0 | 0 | 5 (0) |
| SITE-001638 | Wavelock Advanced Technology Inc. — Montpelier | STILL_UNCERTAIN | 1 | 0 | 2 | 5 (0) |
| SITE-001686 | Kansai Helios Coatings — Johnstown | STILL_UNCERTAIN | 0 | 0 | 0 | 2 (2) |
| SITE-001699 | AEROTECH STYLING INC — Lyons | STILL_UNCERTAIN | 0 | 0 | 0 | 5 (0) |
| SITE-001728 | BMF Devices Inc — Miamisburg | VERIFIED | 2 | 0 | 0 | 5 (0) |
| SITE-001744 | Durable Corporation — Norwalk | VERIFIED | 4 | 0 | 1 | 5 (0) |
| SITE-001762 | Kohlfab Custom Plastics Fabrication Inc — Da... | VERIFIED | 5 | 0 | 1 | 3 (0) |
| SITE-001799 | P&T Products Inc | VERIFIED | 3 | 0 | 0 | 5 (0) |
| SITE-001814 | Valley Plastics Company Inc. | VERIFIED | 7 | 0 | 0 | 5 (0) |
| SITE-001857 | American Plastics Distributors (American Pla... | VERIFIED | 3 | 0 | 0 | 5 (0) |
| SITE-001885 | K. Wm. Beach Manufacturing Co. Inc. | VERIFIED | 11 | 0 | 0 | 5 (0) |
| SITE-001915 | ProVia Walnut Creek Facility | STILL_UNCERTAIN | 0 | 3 | 0 | 5 (0) |
| SITE-001949 | Diffused Gas Technologies Inc | VERIFIED | 2 | 0 | 0 | 3 (0) |
| SITE-002034 | StockPKG, Inc. (StockPKG Films), successor o... | STILL_UNCERTAIN | 0 | 3 | 0 | 5 (1) |
| SITE-002064 | Ashland Inc. — Columbus (ISP Chemicals LLC) | STILL_UNCERTAIN | 0 | 0 | 0 | 3 (3) |
| SITE-002099 | OH 4 INDUSTRIES LLC | STILL_UNCERTAIN | 0 | 0 | 1 | 6 (0) |
| SITE-003327 | Budenheim USA - Mansfield | STILL_UNCERTAIN | 0 | 0 | 0 | 3 (1) |
| SITE-003899 | Inno-Pak Headquarters and Manufacturing Faci... | STILL_UNCERTAIN | 0 | 0 | 0 | 3 (3) |
