# Ohio (non-PIC-12) capability wave, lane 7 report (2026-11-01)

This is a packet, not a data change. Nothing under `data/` or any other repo file was edited, nothing was committed or pushed, and no IDs were allocated. The lane proposes no `tier_effect`.

- **Assignment:** `oh_lane7_assignment.csv`, 79 Ohio site rows (78 organizations with 79 sites; ORG-000651 ADS has two rows). Unit for every count below: assigned site rows, n = 79, unless another unit is named.
- **Method:** the PIC-12 wave method with the Tranche 2 changes. Own-site sources only (`own_site`, including certificate PDFs the sites link, read with `pdftotext`). Vocabulary v1.7.6. R3c applied. At most 6 fetches per site (hard-capped in the fetch tool).
- **Quote check:** all 360 packet rows carry a URL and a quote of 25 words or fewer. A script checked every quote as a substring of the fetched text of that exact fetch, after removing whitespace, zero-width characters and curly-quote variants. All 360 pass. The same script checked every in-vocab value against `docs/schema/vocab.json` and rejected pipe-split quotes.
- **Tooling:** curl with the default user agent through the configured proxy; no WebFetch summaries. Scratch was `/tmp/claude-0/wave-oh/lane7/` only, with one directory and one lock per site and numbered filenames (`f1`, `f2`, ...), so no fetch overwrote another. No parallel fetches were made for any one site.

## Results (unit: assigned Ohio site rows, n = 79)

VERIFIED 44 (56%) · STILL_UNCERTAIN 35 · REJECT 0.

VERIFIED means at least one in-vocab value at site scope. A check script confirmed that every VERIFIED site has one and every other site has none.

| field (in-vocab rows) | site | org | total |
|---|---:|---:|---:|
| processes | 75 | 45 | 120 |
| materials | 70 | 26 | 96 |
| markets_served | 60 | 38 | 98 |
| certifications | 20 | 6 | 26 |
| **all** | **225** | **115** | **340** |

- **Off-vocab rows:** 20 (9 `processes_other_note`, 7 `markets_other_note`, 4 `certifications_other_note`), all marked OFF-VOCAB and STILL_UNCERTAIN at row level.
- **Row-level STILL_UNCERTAIN in-vocab rows:** 15, all certifications held under R3c because the page names the standard with no edition and no certificate was fetched (SITE-000880 x3 at Robin's Healthcare Division, SITE-000997 x3 at Kurz-Kasch, SITE-001260 x3 at Tom Smith where the page says "aligned with the requirements of", ORG-000804 x3 at DSG-Canusa, ORG-000727 Century Mold IATF, SITE-001175 ISO 13485, SITE-001207 Snyder ISO 9001).
- **Rows counted once per organization:** org-scope rows for ORG-000651 (ADS) sit on SITE-000696 only.

**Yield:**
- Site-scope VERIFIED values: 214 in-vocab rows across 44 sites, which is 2.7 per assigned site and 4.9 per VERIFIED site.
- All in-vocab rows together: 4.3 per assigned site.
- Coverage: 64 of 79 sites got at least one in-vocab value at either scope.
- Markets: present at 28 of 79 sites at site scope, and 44 of 79 counting org scope.

**Certificates read from PDFs and recorded:**

| Site | Standard | Valid to |
|---|---|---|
| SITE-000880 Robin Industries (Healthcare Division, 3500 State Route 39) | ISO 13485:2016 (Smithers) | 2028-03-25 |
| SITE-001032 Midwest Elastomers (700 Industrial Dr, Wapakoneta) | ISO 9001:2015 (Perry Johnson) | 2027-03-29 |
| SITE-001216 Standridge Color (Defiance is Site #3 on the multi-site certificate) | ISO 9001:2015 (Bureau Veritas) | 2027-06-05 |
| ORG-000905 ISCO Industries (Louisville KY; annex lists no Ohio site) | ISO 9001:2015 (NSF-ISR) | 2027-11-03 |
| SITE-001052 Multi-Plastics (Lewis Center) | AIB food-contact inspection, scope "slitting of plastic film", inspected 2026-03-18 | no expiry printed (off-vocab, not a CERTS value) |

- **Not recorded, expired:** Ohio Foam's ISO 9001:2015 certificate (BSI FM 524343, expiry 2025-08-05) is still linked from its site. It is held as an off-vocab note.
- **Not recorded, superseded:** Superb Industries ("ISO/TS16949") and Tool Mate ("ISO 9002:1994 compliant"). DSG-Canusa's "ISO 9100" is not recorded (probably AS9100 mistyped, and no AS9100 certificate was seen).
- **Renewal watch:** every certificate above runs past the end of 2026; the earliest expiry is Midwest Elastomers (2027-03-29).

## Fetches

314 attempts across 78 sites with a usable URL (4.0 per site, none over the 6 cap). SITE-001768 has no fetch because its website field is a placeholder.

**Hard failures: 20 of 314 (6.4%):**
- HTTP 403: 5 (Apache www, a Cloudflare "Just a moment" page; Dimex x2; Performance Plastics/Pexco x2, a Cloudflare "Sorry, you have been blocked" page).
- Connection reset: 5 (HTI Plastics x2, Kar-Del x2, Magnum Molding's Our Work page).
- TLS: 2 (Apache apex, handshake failure; Next Resins www, self-signed certificate).
- Proxy CONNECT 502: 2 (KN Rubber, both hosts).
- HTTP 404: 3 (one URL the lane guessed for Covestro; two dead internal links on the Xstream Kayaks site).
- HTTP 500: 1 (Entrotech Contact page).
- HTTP 202 with a captcha challenge: 1 (Multi-Plastics, an `http://` PDF link).
- HTTP 200 with an error-page body: 1 (Next Resins apex, 87 characters).

**No usable content at all (8 sites):** Apache (000727), Dimex (000857), HTI Plastics (000952), Kar-Del (000987), KN Rubber (001474), Performance Plastics/Pexco (001828), Next Resins (001926), and Molding Technologies (001768, no valid URL). These are availability failures only. None is closure evidence and none gets a REJECT.

**Fetches wasted on already-seen pages: 23 of 314 (7%).** My auto-selection of follow-up links picked the home page again for several small sites. Those sites then had fewer fetches left for plant pages.

**Two things to know about the fetch route:**
- **Multi-Plastics AIB certificate.** The `http://` link on its certificates page returned a SiteGround captcha challenge (HTTP 202, empty body). I then requested the `https://` form of the same file, which returned the PDF with no challenge. No captcha was solved or bypassed. The 202 is counted as a failure above.
- **WinCup home page.** The server returned Brotli-compressed bytes without being asked. I decoded the already-fetched bytes locally (a `brotli` pip install; no second fetch) to get the text. The tool now sends `--compressed`.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - metal stamping, coining and deep drawing (Integral, Superb);
  - slitting of plastic film (Multi-Plastics Lewis Center);
  - twin-sheet thermoforming (Techniform);
  - film extrusion with blown or cast unstated, plus knitting and weaving (Snyder);
  - pouch and bag converting (Dazpak);
  - casting of filled polyester / cultured marble (Custom Cast Marbleworks);
  - cementitious stone-veneer casting (ProVia's Cherry Ridge plant, not a polymer process).
- **Materials with no term:** polyolefin unspecified (DSG-Canusa heat-shrink tubing; I recorded fluoropolymer and elastomer only), "olefins" (Standridge, mapped to `thermoplastics`), EPS as a distinct material (mapped to `polystyrene_ps_hips` plus `foams_polymeric`).
- **Markets with no term:**
  - military and defense packaging (Dazpak) and military foam (Ohio Foam);
  - sandblasting resist and contamination-control flooring (Hartco);
  - commercial-vehicle interiors (Superior Trim);
  - residential outdoor furniture, which could be `furniture_office`, `lawn_garden_recreation` or `consumer_goods_housewares` (Berlin Gardens);
  - recreational kayaks (Five Star);
  - bedding, craft and sealing foam (Ohio Foam);
  - heavy truck (Tom Smith);
  - tent, awning and sign-media fabrics (Snyder).
- **Certifications with no term:** AIB International food-contact inspection (Multi-Plastics); ISO 50001 (DSG-Canusa). "Aligned with" a standard is not a certification (Tom Smith).

## Hygiene findings (not resolved, for the integrator)

**Duplicates and identity:**
1. **SITE-000880 and SITE-001175.** Both are the Robin Industries Healthcare Division plant at 3500 State Route 39 (the certificate says Berlin, OH 44610; the rows say Millersburg 44654). Atlas notes already record SITE-001175 as a retired duplicate folded into SITE-000880, yet it passed the "active" candidate filter. The orgs (ORG-000814 Elasto-Tec and ORG-000549 Robin Industries Healthcare) both use robin-industries.com. Robin's other Ohio plants (Holmco in Winesburg, Fredericksburg, the North Canton development center) were not checked against the holdings. SITE-001175 spent one fetch on a duplicate page and reached the 6-fetch cap before the certificate PDF, so its ISO 13485 row defers to the SITE-000880 certificate.
2. **SITE-000811.** The row name is "Continental Tire North America — Bryan" but the org (ORG-001155) is Titan Tire Corporation of Bryan, its website is titan-intl.com, and Titan's own Contact page lists the Bryan plant (927 S Union St).
3. **SITE-001828.** performanceplastics.com redirects to pexco.com ("Performance Plastics is now part of Pexco"); both fetches were Cloudflare-blocked, so the rebrand or acquisition is unconfirmed.
4. **SITE-002060.** The org is "Five Star Plastics" but the website is Xstream Kayaks (a 2013-era page with dead internal links).
5. **SITE-000935.** The org is Greenville Technology Inc., but Moriroku's group site lists "MTNA Greenville Plant, 5755 State Route 571 East" under Moriroku Technology North America, whose head office is in Marysville, OH (15000 Industrial Parkway).
6. **SITE-001768.** The org website is the placeholder `https://none found/`.

**Rows that are HQs, offices or out of scope (scope questions for the owner):**
7. **SITE-000696 ADS Hilliard.** The FY2026 Sustainability Report calls Hilliard the headquarters with a new Engineering and Technology Center (R&D). It names Pandora, OH (SITE-001696) and Yoakum, TX as production sites. Neither row got a process value.
8. **SITE-001276 Univenture.** The Contact address is 2545 Farmers Drive, Suite 370, Columbus; the About page says sales and manufacturing operate from its Marysville, OH headquarters. The Marysville plant looks unheld.
9. **SITE-001333 Matrix Adhesives.** Westerville is "550 Polaris Pkwy Ste 110", an office suite; "Onsite Mixing" is at the customer's facility.
10. **SITE-001114 PSG.** The only address is a "Corporate Office" in Worthington, and the pages describe resin development, not manufacturing.
11. **SITE-002019 Tool Mate.** The address is a "Head Office" with split office/remote hours and UPS shipping, and "manufactured to your specifications" names no plant.
12. **SITE-001515 Goodyear Development Center.** The row is an R&D center; no fetched Goodyear page mentions Hebron.
13. **SITE-001877 Gem City Tire.** This is a tire dealer and service chain (nine locations) that lists retreading as a service that "may vary by location".
14. **SITE-001458 Custom Cast Marbleworks.** It casts filled-polyester cultured marble and solid surface, so check whether it is in polymer scope.
15. **SITE-001753 Grit Guard.** No process or material is stated; confirm it is a polymer maker at Bellefontaine.
16. **SITE-001345 Axium.** The row address, 13425 Worthington Road NW, is Axium's "Vertix Recycling" facility, so the row is a recycling facility, not a packaging plant. Axium's Locations page lists six more New Albany buildings (New Albany 1 to 6, plus Apex Finishing at 8300 Innovation Campus Way) that may be unheld.
17. **SITE-001136 ProVia.** The New Philadelphia plant does window and patio-door profile lamination (629 Wabash Ave NW). ProVia's Contact page lists other Ohio plants (Walnut Creek, Sugarcreek, Baltic, Strasburg, Cherry Ridge) that may be unheld.
18. **SITE-001152 Superior Trim.** Its Locations page lists a main plant (2151 Industrial Dr), Formed Products (5500 Fostoria Rd, this row), Molded Products (2100 Fostoria Rd) and Springfield OH (5225 Prosperity Dr); the others may be unheld.
19. **SITE-001248 TH Plastics.** Four plants (Mendon MI, Bowling Green, Findlay, Tiffin); no page assigns processes to Tiffin.
20. **SITE-001128 Precision Polymers.** It names two Reynoldsburg buildings (6919 and 6830 Americana Pkwy); one address is one site.

**Websites and stale content:**
21. **SITE-000892 Entrotech** ((c) 2012-2017; Contact page returned HTTP 500) and **SITE-001186 Rubber-Tech** ((c) 1998, no address).
22. **SITE-001076 Ohio Foam.** Its linked ISO 9001 certificate expired 2025-08-05.
23. **SITE-001227 Superb.** The quality page still cites ISO/TS16949.
24. **SITE-000738 Tigerpoly.** Its certification claims (ISO 9001:2015 and 14001:2015) are on a page with a (c) 2019 footer and no certificate.
25. **SITE-001062 WinCup.** The Contact page lists Mount Sterling, OH among eight plants, but the "Cup Plant Spec Sheets" page lists only NJ, GA, IL and MO. That is not closure evidence.
26. **SITE-000869 DSG-Canusa.** The Locations prose says "Loveland, Ohio" while the address block is 9391 Seward Road, Fairfield.
27. **SITE-000974 ISCO.** The ISO 9001 annex lists no Ohio location, so Byesville is not an ISO-registered site per that certificate.

**Scope calls in the packet:**
- **Weak site-scope calls (integrator may demote):** SITE-000848 Dazpak laminating (Ohio named, Columbus is the only Ohio site); SITE-000965 Integral (three plants in Troy, plant not named); SITE-001199 Sekisui Kenton `foam_molding_bead` (type inferred from the company's EPS/Piocelan foam); SITE-001345 Axium `packaging_consumer`; SITE-001216 Standridge Defiance processes (the certificate's scope cell is merged beside the site list); SITE-000925 Global Foam and SITE-000760 Berlin Gardens (small single shops with no street address printed).
- **35 sites have no site-scope value.** For 8 of them no page was reachable. For most of the rest (Akzo, Amcor, Covestro, Formica, Goodyear, Sun Chemical, Flint, Johns Manville, Sherwin-Williams, Deflecto, AZEK, TH Plastics and others) no page ties a capability to the plant, so any value stays org scope. Each settling fact is in `verdicts.csv`.

**Privacy:** no personal names, emails or direct-dial numbers were recorded. Several Contact pages (Woodwright, TH Plastics, Phoenix) carry named staff with emails and direct lines; none of that is in any quote or note.

## Per-site table (unit: site rows; values are in-vocab rows with row verdict VERIFIED at site scope, and org-scope rows recorded once per organization)

| Site | Name (assignment) | Verdict | Site values | Org values | Fetches |
|---|---|---|---:|---:|---:|
| SITE-000696 | Advanced Drainage Systems — Hilliard | STILL_UNCERTAIN | 0 | 3 | 4 |
| SITE-000705 | AkzoNobel Coatings Inc. — Columbus | STILL_UNCERTAIN | 0 | 2 | 3 |
| SITE-000716 | Amcor Rigid Packaging — New Albany | STILL_UNCERTAIN | 0 | 2 | 3 |
| SITE-000727 | Apache Inc. — Cincinnati | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-000738 | Tigerpoly Manufacturing, Inc. - Grove City | VERIFIED | 10 | 0 | 4 |
| SITE-000746 | Azek Building Products — Wilmington | STILL_UNCERTAIN | 0 | 2 | 4 |
| SITE-000760 | Berlin Gardens LLC — Millersburg | VERIFIED | 2 | 0 | 4 |
| SITE-000774 | Building Composites — Moraine | VERIFIED | 4 | 0 | 4 |
| SITE-000786 | Century Mold — Monroe | VERIFIED | 2 | 7 | 4 |
| SITE-000797 | Clyde Foam LLC — Clyde | VERIFIED | 4 | 0 | 4 |
| SITE-000811 | Continental Tire North America — Bryan | VERIFIED | 1 | 1 | 3 |
| SITE-000824 | Covestro — Hebron | STILL_UNCERTAIN | 0 | 1 | 4 |
| SITE-000834 | Creative Plastic Concepts — Sycamore | VERIFIED | 2 | 0 | 2 |
| SITE-000848 | Dazpak — Columbus | VERIFIED | 1 | 5 | 5 |
| SITE-000857 | Dimex LLC — Marietta | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-000869 | DSG-Canusa — Fairfield | STILL_UNCERTAIN | 0 | 10 | 4 |
| SITE-000880 | ELASTO-TEC INC. — Millersburg | VERIFIED | 2 | 13 | 6 |
| SITE-000892 | ENTROTECH INC — Columbus | STILL_UNCERTAIN | 0 | 0 | 5 |
| SITE-000901 | FENNER DUNLOP LLC - TOLEDO | VERIFIED | 1 | 5 | 6 |
| SITE-000914 | Formica — Cincinnati (Evendale) | STILL_UNCERTAIN | 0 | 0 | 4 |
| SITE-000925 | Global Foam Company — Dayton | VERIFIED | 4 | 0 | 4 |
| SITE-000935 | Greenville Technology — Greenville | STILL_UNCERTAIN | 0 | 3 | 4 |
| SITE-000944 | Hartco, Inc. — Cincinnati | VERIFIED | 3 | 0 | 6 |
| SITE-000952 | Hueter Toledo, Inc. — Bellevue | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-000965 | Integral Manufacturing — Troy | VERIFIED | 3 | 0 | 5 |
| SITE-000974 | ISCO Industries, Inc - Byesville | STILL_UNCERTAIN | 0 | 6 | 5 |
| SITE-000987 | Kar-Del Plastics, Inc. — Ashland | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-000997 | Kurz-Kasch Inc. — Newcomerstown | VERIFIED | 3 | 0 | 6 |
| SITE-001008 | Ludlow Composites — Fremont | VERIFIED | 4 | 0 | 3 |
| SITE-001018 | Marne Plastics, LLC — Grove City | VERIFIED | 10 | 0 | 4 |
| SITE-001032 | Midwest Elastomers Inc. — Wapakoneta | VERIFIED | 16 | 0 | 5 |
| SITE-001043 | Mondo Polymer Technologies — Reno | VERIFIED | 10 | 0 | 3 |
| SITE-001052 | Multi-Plastics Inc. — Lewis Center | VERIFIED | 2 | 5 | 6 |
| SITE-001062 | New Wincup Holdings, INC — Mount Sterling | STILL_UNCERTAIN | 0 | 3 | 4 |
| SITE-001076 | Ohio Foam Corp. — Bucyrus | VERIFIED | 10 | 0 | 5 |
| SITE-001085 | Ohio Steel Industries Inc - OSI Plastics Delawar | VERIFIED | 2 | 3 | 4 |
| SITE-001104 | Plas-tec — Edon | VERIFIED | 4 | 0 | 4 |
| SITE-001114 | Plastic Selection Group, Inc. — Worthington | VERIFIED | 7 | 0 | 4 |
| SITE-001128 | Precision Polymers, Inc. — Reynoldsburg | VERIFIED | 9 | 0 | 4 |
| SITE-001136 | ProVia New Philadelphia Facility | VERIFIED | 2 | 0 | 6 |
| SITE-001152 | RADAR LOVE DBA SUPERIOR TRIM - FORMED PRODUCTS | STILL_UNCERTAIN | 0 | 3 | 4 |
| SITE-001163 | Revere Plastics Systems — Clyde | VERIFIED | 5 | 0 | 4 |
| SITE-001175 | Robin Industries Healthcare | VERIFIED | 1 | 4 | 6 |
| SITE-001186 | Rubber-Tech, Inc. — Dayton | STILL_UNCERTAIN | 0 | 2 | 4 |
| SITE-001199 | Sekisui Kasei USA Inc. — Kenton | VERIFIED | 1 | 4 | 6 |
| SITE-001207 | Snyder Manufacturing, Inc. — Dover | VERIFIED | 5 | 0 | 4 |
| SITE-001216 | Standridge Color — Defiance | VERIFIED | 4 | 2 | 6 |
| SITE-001227 | SUPERB INDUSTRIES INC — Sugarcreek | VERIFIED | 8 | 0 | 5 |
| SITE-001239 | Techniform Industries, Inc. — Fremont | VERIFIED | 11 | 0 | 4 |
| SITE-001248 | TH Plastics - Tiffin | STILL_UNCERTAIN | 0 | 9 | 4 |
| SITE-001260 | Tom Smith Industries — Englewood | VERIFIED | 6 | 0 | 4 |
| SITE-001276 | Univenture — Columbus | STILL_UNCERTAIN | 0 | 2 | 3 |
| SITE-001287 | USA Vinyl — Groveport | VERIFIED | 3 | 0 | 4 |
| SITE-001300 | Wolf Composite Solutions — Columbus | VERIFIED | 9 | 0 | 4 |
| SITE-001333 | Matrix Adhesives Group — Westerville | STILL_UNCERTAIN | 0 | 2 | 4 |
| SITE-001345 | Axium Packaging Inc — 13425 Worthington Road NW | VERIFIED | 4 | 6 | 5 |
| SITE-001449 | Deflecto — Dover | STILL_UNCERTAIN | 0 | 0 | 5 |
| SITE-001458 | Custom Cast Marbleworks — Evendale | VERIFIED | 2 | 0 | 5 |
| SITE-001474 | KN Rubber — Wapakoneta | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-001515 | Goodyear Development Center — Hebron | STILL_UNCERTAIN | 0 | 0 | 3 |
| SITE-001527 | TSP Inc. — Batavia | VERIFIED | 9 | 0 | 4 |
| SITE-001556 | Sun Chemical Performance Pigments - Cincinnati ( | STILL_UNCERTAIN | 0 | 4 | 3 |
| SITE-001634 | IEG Plastics, LLC — Bellefontaine | VERIFIED | 8 | 0 | 4 |
| SITE-001683 | Flint Group North America Corporation — Lebanon | STILL_UNCERTAIN | 0 | 1 | 3 |
| SITE-001696 | Advanced Drainage Systems, Inc. — Pandora | STILL_UNCERTAIN | 0 | 0 | 4 |
| SITE-001713 | Johns Manville — Defiance | STILL_UNCERTAIN | 0 | 0 | 3 |
| SITE-001738 | David E Easterday & Co Inc — Wilmot | VERIFIED | 2 | 0 | 5 |
| SITE-001753 | Grit Guard Inc — Bellefontaine | STILL_UNCERTAIN | 0 | 0 | 4 |
| SITE-001768 | Molding Technologies Ltd — Hebron | STILL_UNCERTAIN | 0 | 0 | 0 |
| SITE-001811 | Magnum Molding Inc. | VERIFIED | 1 | 0 | 3 |
| SITE-001828 | Performance Plastics Ltd. (now part of Pexco) | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-001877 | Gem City Tire Inc | STILL_UNCERTAIN | 0 | 1 | 4 |
| SITE-001902 | Stark's Plastics | VERIFIED | 9 | 0 | 4 |
| SITE-001926 | Next Specialty Resins, Inc. (Next Resins) | STILL_UNCERTAIN | 0 | 0 | 2 |
| SITE-002019 | Tool Mate Corp | STILL_UNCERTAIN | 0 | 2 | 4 |
| SITE-002060 | Five Star Plastics | STILL_UNCERTAIN | 0 | 1 | 3 |
| SITE-002085 | MAUSER PACKAGING SOLUTIONS | VERIFIED | 1 | 1 | 4 |
| SITE-002132 | Phoenix Technologies International, LLC - Bowlin | VERIFIED | 7 | 0 | 6 |
| SITE-003476 | Sherwin-Williams — Cincinnati Paint (General Pol | STILL_UNCERTAIN | 0 | 0 | 3 |

Verdicts, settling facts and per-site fetch counts are in `verdicts.csv`; all rows with URLs and quotes are in `packet.csv`.
