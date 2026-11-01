# Tranche 2 lane 7 packet: PIC-12 capability wave (2026-11-01)

**This is a packet, not a data change.** Lane t2-7 never edited `data/`, allocated IDs, committed or pushed. Outputs: `packet.csv` (387 rows), `verdicts.csv` (54 rows), this REPORT. Every row is class `own_site`, carries the exact fetched URL and a quote of 25 words or fewer, and each quote was checked programmatically as a substring of the page text I fetched (whitespace and curly-quote normalised). Vocabulary: `docs/schema/vocab.json` (v1.7.6), every in-vocab value checked programmatically; one value per row. All fetches were curl through the configured proxy (PDF certificates via pdftotext). No WebFetch, no user-agent changes, no certificate bypass, no captcha work. One WebSearch was run as a discovery lead for SITE-000013 (org website is `none_found`); it found no D & D Plastics site and nothing was assumed. Fetched text lives in `/tmp/claude-0/wave/t2_lane7/` (outside the repo). Note: repo HEAD at lane start was `c0192b8`, not the wave's pinned `665e5c5`; I did not re-derive the population.

## Results (units stated)

**Sites verdicted (unit: assigned Ohio site rows, n=54):** VERIFIED 32, STILL_UNCERTAIN 22, REJECT 0. VERIFIED = at least one in-vocab value at **site** scope that is row-level VERIFIED. No REJECT: nothing found was a dated closure or non-establishment fact; every unreachable site is an availability failure only (no Form 5500 check run, none needed).

**In-vocab values proposed (unit: packet rows, one per record, field, value):** 352 total, 345 row-level VERIFIED, 7 row-level STILL_UNCERTAIN (weak or undated).

| field | site scope | org scope | total |
|---|---|---|---|
| processes | 71 | 9 | 80 |
| materials | 102 | 27 | 129 |
| markets_served | 86 | 46 | 132 |
| certifications | 10 | 1 | 11 |
| **all** | **269** | **83** | **352** |

Plus **35 off-vocab rows** (`*_other_note`, OFF-VOCAB or unspecified, row verdict STILL_UNCERTAIN): processes_other_note 15, markets_other_note 11, certifications_other_note 6, materials_other_note 3. The 13 orgs carrying org-scope rows are listed in the table below (ORG ids). Org-scope rows use the ORG id as `record_id`; the Smithers-Oasis org rows (ORG-000057) apply to both SITE-000057 and SITE-001837.

**Measured yield**
- Site-scope capability values (processes, materials, markets) per assigned site: 259/54 = 4.8. Per VERIFIED site: 259/32 = 8.1. All in-vocab values, all scopes, per assigned site: 352/54 = 6.5.
- Sites with at least one `markets_served` value: **23/54 (43%) at site scope; 37/54 (69%) counting org scope**.
- Sites with at least one site-scope `processes` value: 23/54 (43%).
- Sites with at least one in-vocab value at some scope: 44/54 (81%). The ten with none: SITE-000013 (no website), and nine unreachable sites (SITE-000211, -000227, -000280, -000308, -000464, -001480, -001676, -002005, -002054).
- VERIFIED rate 32/54 = 59% (n=54).

**Plant-specificity (hard rule).** Org scope only, nothing pushed down: Smithers-Oasis (SITE-000057, SITE-001837), Spazzolplastica, Compking, Harwood/Coreline materials and markets, Flexsys, Iten (Plant 4 not named; 4 Ashtabula plants), Pentair Chardon, Shin-Etsu (3 Akron rows), Henkel, Ruscoe (own-site address differs from the Atlas street), LyondellBasell Composites, and the calendering/markets rows for the SILMIX operation (two-site). Tied to the plant first (tranche 2 change 3): Blair Rubber (single-site ISO 9001:2015 certificate naming 5020 Enterprise Pkwy), Steere (DQS IATF/ISO 9001 certificates naming 285 Commerce St and its annex, Smithers ISO 14001 multi-site appendix naming 487 Commerce St for tube bending), Roechling (plant page "Roechling Industrial Cleveland" plus Locations page listing 4321 Glenridge Rd), SILMIX Ohio (plant page naming 2215 International Pkwy), Harwood (Coreline facility page naming Cuyahoga Falls), OEM/Miller (division page naming 1300 Danner Dr), Permatex (overview naming the Solon plant). Single-location companies with one printed address got site scope; each row's `notes` says why.

**Certifications (R3c).** Recorded (11; Interpak's is row-level STILL_UNCERTAIN, see below): ISO 9001:2015 Blair (certificate, expires 2027-06-21), Lerner (current page names 2015), Roechling (plant page names 2015), Steere (DQS certificate, valid to 2028-06-11), Ruscoe (org scope, page names 2015 with Design); IATF 16949:2016 Clark (page, first edition, registrar SAI Global) and Steere (DQS certificate, valid to 2028-06-11); ISO 14001:2015 Steere 285 Commerce and 487 Commerce (Smithers certificate, expires 2029-02-11); nsf_certified_products Tomlinson ("most products"); iso_9001 Interpak (page names 2015 but is undated with a 2004 footer, so row-level STILL_UNCERTAIN). **Not recorded (6, as certifications_other_note):** edition-less "ISO 9001" (Custom Rubber, whose linked certificate file is named "expires-2024-09-10"; Arc Rubber, whose only named edition, ISO-9001:2000, is superseded; Iten), edition-less "IATF 16949" (OEM/Miller), Permatex ("QMS", no standard), Astro (Nadcap, plus an "ISO" badge with no standard).

## Fetches (unit: fetch attempts)

- **213 total** across 54 sites, 3.9 per site (SITE-000013 made none; SITE-001837 reuses ORG-000057's six, counted at SITE-000057); maximum 6 per org (Smithers, Harwood, Hytech). Steere's two sites together used 7 fetches: SITE-000627 5, SITE-001416 2 (certificate PDFs fetched under the site they cover); the org total exceeds 6 by one.
- Hard availability failures (403, 406, 401, 409, 502/503, 202 interstitial, TLS error, handshake failure, DNS, connection reset): **37/213 = 17.4%**. Add 2 content-free or unrelated 200s (Neo Industries' domain serves an unrelated spam page; cellocore.com serves Reptheus): **39/213 = 18.3%**.
- My own misses (not availability): 1 guessed 404 (Plastics R Unique /services), 1 duplicate homepage fetch (HKB), 1 redundant fetch (Hytech home.html returned 503 but is a duplicate of a working page; counted as a failure above).
- Sites with no usable company content from any route: **9/54 (17%)**: HEXPOL Compounding (CONNECT 502, handshake failure, DNS not resolved), Advanced Poly-Packaging (self-signed cert, 503), Carney Plastics (403 on apex/www/http), Corrosion Resistant Technologies (reset, 406), McCann Plastics (401, "Password Protected Site"), Cell-O-Core (domain now serves Reptheus), A.R.E. Accessories (HTTP 202 empty on realtruck.com and 4are.com redirect), Solutions in Polycarbonate (TLS mismatch, 503, reset), Neo Industries (spam page). All are STILL_UNCERTAIN; none is evidence of closure. SITE-000013 has no own website to fetch.
- Routes that recovered content: plain `http://` after an https certificate or handshake failure (HKB, Hytech, Synesis); the Harwood redirect to corelinerollers.com; Interpak and Cell-O-Core redirects. Certificate verification was never bypassed.

## Vocabulary gaps met (owner rulings; flagged in `*_other_note`, not settled)

- **Rubber-to-metal bonding / bonding processes** (Custom Rubber, Hytech); **rubber roller manufacture, recovering, grinding** (Harwood); **rubber lining and belt-splice materials** (Blair); **tube bending** (Steere SITE-001416; the site row's existing `tube_bending` is not in vocab).
- **Thermoset molding-compound (SMC/BMC) formulation process** (LyondellBasell; same gap lane 4 met for Lattice); **supercritical-water plastic conversion** (Seauciel); **Liquid Cure Method line, unspecified rubber molding type** (Arc, HKB, Clark, Youngstown Rubber); **twin-sheet forming** (Joslyn); **dental prosthetics fabrication** (Mabel); **wire basket spool manufacture** (Spazzolplastica); **tarp/curtain fabrication** (Electra).
- **Materials:** no rubber-chemicals/tire-additive term (Flexsys: vulcanizing agents, antidegradants); no CPVC term (Harrison, mapped to thermoplastics with note); chlorobutyl and fluorosilicone were mapped to `specialty_elastomers` with the elastomer named in notes (Blair, Wacker).
- **Markets:** no floral/horticulture term (Smithers-Oasis); no POP-display, parking/speed-bump/outdoor-products, wire-and-cable/T&D, banking-security, communications, conveyors/material-handling, power-generation, steel, trucking, firearms/military-gear, aquatic, fitness, highway/pools term; "Automotive / RV" is a combined label (Ruscoe); "Food Processing / Packaging" is a joined label (HKB); "packaging inserts" and "Packaging & Dunnage" were not mapped to a `packaging_*` term (type not stated).
- **Mapping calls the integrator may override:** "Outdoor Power Equipment" to `lawn_garden_recreation` (Cima); "solar" to `energy_renewables_battery` (Clark); "semiconductor" to `electronics_electrical` (Harrison); "aircraft/aviation/airline" not mapped to `aerospace_defense` where only "airline" or "military" appears (Arc, Custom Rubber, Clark); "military" mapped to `aerospace_defense` only where paired with "defense"/"aerospace" (Joslyn, Astro, Shin-Etsu); "home and hardware markets" to `consumer_goods_housewares` (Permatex); "Film & Plastic" processing customers to `plastics_rubber_processors` (Coreline); "medical devices (dialysis)" to `medical_device` (Tomlinson, Wacker); "plastic fabrication" to `plastics_fabrication_welding` with welding not stated (HKB, Harrison); "recreational vehicles/trailer" to `rv_powersports_trailers` (Cima, Joslyn, Montville); Permatex materials at site scope on the strength of "the NA manufacturing center is Solon".

## Hygiene findings (for the integrator; none resolved)

1. **SITE-000182 / ORG-000175 Harwood Rubber Products:** `harwoodrubber.com` redirects to corelinerollers.com (Coreline Rollers = Harwood + Rubber Right Rollers, Chelsea MA). The Cuyahoga Falls facility page confirms 1365 Orlen Ave (site-tied). Org `website` and parent/brand handling are the integrator's call.
2. **SITE-001480 / ORG-001432 Cell-O-Core:** `cellocore.com` (http only) serves Reptheus / Rep the US (Lynbrook NY, eco-friendly disposables distribution); no Cell-O-Core content. Org website field points at an unrelated business. Availability/redirect only; needs another route and a Form 5500 / dated-outcome check before any status change.
3. **SITE-002054 / ORG-002055 Neo Industries:** `neoindustriesinc.com` http serves an unrelated spam page (fake shoe-store links); the domain looks compromised or repurposed. Not evidence of closure.
4. **SITE-000211 / ORG-000103 HEXPOL Compounding:** `hexpolcompounding.com` does not resolve on http and fails TLS routes. Availability only.
5. **SITE-000365 / ORG-000343 Flexsys:** own Locations page lists 260 Springside Drive, Akron as "Headquarters and Technical Service Center"; manufacturing is at other sites (e.g. Sauget IL). The Akron row is a ring-1 `manufacturing_plant`: scope/ring is an owner ruling.
6. **SITE-000648 / ORG-000608 Tomlinson 1880 (Parma):** own site never says what is made at 11699 Brookpark Rd Unit 500 (sales contacts, 224 area-code phone); ring-1 `manufacturing_plant` unverified.
7. **SITE-001793 / ORG-001717 FlexLink:** site row's `zip` column holds `18222` (the street number); the own site prints 18222 Lanken Ave, Cleveland OH 44119. The company "markets" sourced papers/films and calls the site "headquarters and distribution facility"; ring-1 `manufacturing_plant` is a scope doubt.
8. **SITE-001593 / ORG-001528 Mabel Dental Lab:** a dental laboratory carried as a ring-1 `manufacturing_plant`; polymer content is limited to dentures, partials and guards. Scope doubt for the owner.
9. **SITE-000098 / ORG-000098 Spazzolplastica:** row is "Akron" (city unverified); own site shows USA HQ and wire-basket-spool plant at 9361 Hamilton Dr, Mentor OH 44060 and a warehouse / plastic-product manufacturing partner at 1699 Commerce Dr, Stow OH 44224 (news 2025-12-16). No Akron address.
10. **SITE-001661 / ORG-001589 Ruscoe:** own site prints 485 Kenmore Blvd, Akron 44301; the Atlas row's street is 219 East Miller Ave. Possible move or wrong address.
11. **SITE-000057 and SITE-001837 / ORG-000057 Smithers-Oasis:** own Locations page lists Kent addresses only (295 S Water St HQ; 919 Marvin St; 777 Stow St); the 2020 Front St Cuyahoga Falls row (SITE-000057) is not on it. Neither row is tied to a street on the own site.
12. **SITE-000414 / ORG-000386 Iten:** own Facilities page says 4 manufacturing locations in Ashtabula; the Atlas has SITE-000412 and SITE-000414 (Plant 4) and no plant is named on the site. Two plants may be missing.
13. **SITE-000112 Custom Rubber:** own site prints 1274 East 55th Street, Cleveland 44103; the row's zip is 44114 (FRS Payne Ave street). The row's `custom_compounding` is not stated on the pages fetched.
14. **SITE-000197 Clark Rubber & Plastics:** own site prints 8888 East Avenue, Mentor 44060; the row's FRS street is 8837 East Ave (already noted as conflicting).
15. **SITE-000127 Compking:** own site prints no street or Ohio location (phone 843-906-8049, (c) 2024); the North Randall ring-1 plant is unverified.
16. **SITE-000013 D & D Plastics:** no own website (`none_found`); one discovery search found nothing; not a REJECT.
17. **SITE-001416 / SITE-000627 Steere:** the DQS IATF/ISO 9001 annex lists 285 Commerce (plant), 350 Tacoma Ave (lab), 303 Tacoma Ave (distribution); 487 Commerce St (tube bending) appears only on the Smithers ISO 14001 multi-site appendix. The row's existing `tube_bending` process is not in vocab. Atlas lab/warehouse rows SITE-001417/-001418 exist; their street addresses are on the certificate annex (350 and 303 Tacoma Ave) for the integrator to compare.
18. **SITE-001891 OEM/Miller:** org website `oem-miller.com` redirects to ilpeaindustries.com/oem-miller/; HQ is Scottsburg IN. Parent handling is the integrator's call.
19. **SITE-000344 Electra Tarp:** a vinyl-fabric tarp and curtain maker; fabrication method not stated, so ring-1 polymer-processor scope is a doubt.
20. **SITE-001860 Astro Manufacturing:** contract metal fabricator and Nadcap painter; the "vacuum-formed plastics" in the Atlas note was not found on four pages. **SITE-001933 Synesis:** developer/marketer (exclusive distributor Network Polymers); no page says compounding happens at Creston; (c) 2010 footer. **SITE-001313 Seauciel:** pilot-stage startup (pilot trials scheduled); `hq_only` row.
21. **SITE-000072 Cima, SITE-000531 Plastics R Unique, SITE-001429 Interpak, SITE-001756 Hytech, SITE-001712 Plastic Enterprises:** pages are old or boilerplate-dated ((c) 2006, 2016, 2004, 2012-2015; Plastic Enterprises says its site is being updated). Currency is not shown; not evidence of closure. Cima's page says an air pressure switch line was acquired by Cleveland Controls.
22. **SITE-000446 Lerner:** only a P.O. Box (651, Aurora 44202) is printed; no street.
23. **SITE-000517 Pentair, SITE-001525 Henkel, SITE-003470 LyondellBasell:** global corporate sites; no page names the Atlas plant. Henkel's Locations page (carousel) showed Westlake OH, not Warrensville Heights.
24. **SITE-001724 Youngstown Rubber Products:** page is a division page of Mid-State Sales (distributor group); contact block names 519 N Meridian.

## Per-site summary

| site_id | site | verdict | site-scope cap values | site certs | org-scope values (org id) | off-vocab notes | fetches (failed) |
|---|---|---|---|---|---|---|---|
| SITE-000013 | D & D Plastics, Inc. — Akron | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-000014) | 0 | 0 (0) |
| SITE-000037 | HKB Enterprises, Inc. — Akron | VERIFIED | 14 | 0 | 0 (ORG-000037) | 2 | 5 (1) |
| SITE-000057 | Smithers-Oasis Co. — Cuyahoga Falls | STILL_UNCERTAIN | 0 | 0 | 6 (ORG-000057) | 1 | 6 (0) |
| SITE-000072 | Cima Plastics Group — Twinsburg | VERIFIED | 21 | 0 | 0 (ORG-000072) | 0 | 5 (0) |
| SITE-000098 | Spazzolplastica — Akron | STILL_UNCERTAIN | 0 | 0 | 6 (ORG-000098) | 1 | 4 (0) |
| SITE-000112 | Custom Rubber Corp. — Cleveland | VERIFIED | 16 | 0 | 0 (ORG-000113) | 3 | 4 (0) |
| SITE-000127 | Compking — North Randall | STILL_UNCERTAIN | 0 | 0 | 4 (ORG-000128) | 0 | 4 (0) |
| SITE-000138 | Permatex — Solon | VERIFIED | 2 | 0 | 2 (ORG-000138) | 1 | 5 (0) |
| SITE-000182 | Harwood Rubber Products — Cuyahoga Falls | STILL_UNCERTAIN | 0 | 0 | 10 (ORG-000175) | 1 | 6 (3) |
| SITE-000197 | Clark Rubber & Plastics — Mentor | VERIFIED | 17 | 1 | 0 (ORG-000190) | 2 | 5 (0) |
| SITE-000211 | HEXPOL Compounding — Mogadore | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-000103) | 0 | 3 (3) |
| SITE-000227 | Advanced Poly-Packaging, Inc. — Akron | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-000214) | 0 | 3 (3) |
| SITE-000247 | Arc Rubber, Inc. — Geneva | VERIFIED | 9 | 0 | 0 (ORG-000233) | 3 | 4 (0) |
| SITE-000264 | Blair Rubber — Seville | VERIFIED | 8 | 1 | 0 (ORG-000248) | 1 | 5 (0) |
| SITE-000280 | Carney Plastics Inc. — Youngstown | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-000263) | 0 | 3 (3) |
| SITE-000308 | Corrosion Resistant Technologies, Inc. — Chagrin | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-000289) | 0 | 3 (3) |
| SITE-000327 | Dott Foam Products — Avon | VERIFIED | 8 | 0 | 0 (ORG-000308) | 1 | 4 (0) |
| SITE-000344 | Electra Tarp, Inc. — Canton | VERIFIED | 4 | 0 | 0 (ORG-000323) | 1 | 4 (0) |
| SITE-000365 | Flexsys America L.P. — Akron | STILL_UNCERTAIN | 0 | 0 | 2 (ORG-000343) | 1 | 4 (0) |
| SITE-000390 | HARRISON MACHINE & PLASTIC CORP. | VERIFIED | 6 | 0 | 0 (ORG-000365) | 0 | 4 (0) |
| SITE-000414 | Iten Industries Inc. (Plant 4) | STILL_UNCERTAIN | 0 | 0 | 18 (ORG-000386) | 1 | 5 (0) |
| SITE-000428 | Joslyn Manufacturing Co., Inc. — Macedonia | VERIFIED | 17 | 0 | 0 (ORG-000399) | 2 | 5 (0) |
| SITE-000446 | Lerner Molded Plastics — Aurora | VERIFIED | 19 | 1 | 0 (ORG-000417) | 0 | 4 (0) |
| SITE-000464 | McCann Plastics — North Canton | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-000433) | 0 | 2 (2) |
| SITE-000486 | Montville Plastics & Rubber — Parkman | VERIFIED | 27 | 0 | 0 (ORG-000454) | 0 | 4 (0) |
| SITE-000517 | PENTAIR WATER PURIFICATION | STILL_UNCERTAIN | 0 | 0 | 4 (ORG-000483) | 0 | 4 (0) |
| SITE-000531 | Plastics R Unique — Wadsworth | VERIFIED | 3 | 0 | 0 (ORG-000496) | 1 | 4 (0) |
| SITE-000554 | Premier Building Solutions — Massillon | VERIFIED | 6 | 0 | 0 (ORG-000519) | 0 | 4 (0) |
| SITE-000571 | R2 Sealant Systems, LLC. — Massillon | VERIFIED | 5 | 0 | 0 (ORG-000535) | 0 | 4 (0) |
| SITE-000589 | Roechling Industrial Cleveland, L.P. | VERIFIED | 2 | 1 | 0 (ORG-000551) | 1 | 5 (0) |
| SITE-000608 | Shin-Etsu Silicones of America, Inc. — Akron | STILL_UNCERTAIN | 0 | 0 | 6 (ORG-000569) | 0 | 5 (0) |
| SITE-000627 | Steere Enterprises — Tallmadge | VERIFIED | 9 | 3 | 0 (ORG-000588) | 0 | 5 (0) |
| SITE-000648 | Tomlinson 1880 — Parma | VERIFIED | 2 | 1 | 0 (ORG-000608) | 1 | 4 (0) |
| SITE-000669 | Wacker Chemical Corp. — North Canton | VERIFIED | 4 | 0 | 5 (ORG-000628) | 1 | 5 (0) |
| SITE-001313 | Seauciel — Mentor | VERIFIED | 3 | 0 | 0 (ORG-001332) | 1 | 3 (0) |
| SITE-001416 | Steere Enterprises — Tallmadge (487 Commerce St) | VERIFIED | 1 | 1 | 0 (ORG-000588) | 1 | 2 (0) |
| SITE-001429 | Interpak, Inc. — Mentor | VERIFIED | 4 | 1 | 0 (ORG-001390) | 0 | 4 (0) |
| SITE-001480 | Cell-O-Core — Wadsworth | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-001432) | 0 | 5 (5) |
| SITE-001525 | Henkel — Warrensville Heights (LOCTITE Cleveland | STILL_UNCERTAIN | 0 | 0 | 5 (ORG-001466) | 0 | 5 (0) |
| SITE-001593 | Mabel Dental Lab — Cuyahoga Falls | VERIFIED | 2 | 0 | 0 (ORG-001528) | 1 | 4 (0) |
| SITE-001661 | The Ruscoe Company — Akron | STILL_UNCERTAIN | 0 | 0 | 10 (ORG-001589) | 1 | 4 (0) |
| SITE-001676 | A.R.E. Accessories — Mount Eaton | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-000207) | 0 | 3 (3) |
| SITE-001712 | PLASTIC ENTERPRISES — Elyria | VERIFIED | 3 | 0 | 0 (ORG-001639) | 0 | 1 (0) |
| SITE-001724 | YOUNGSTOWN RUBBER PRODUCTS — Youngstown | VERIFIED | 3 | 0 | 0 (ORG-001649) | 1 | 4 (0) |
| SITE-001756 | Hytech Silicone Products Inc — Ravenna | VERIFIED | 11 | 0 | 0 (ORG-001680) | 1 | 6 (3) |
| SITE-001793 | FlexLink, LLC | VERIFIED | 1 | 0 | 0 (ORG-001717) | 1 | 4 (0) |
| SITE-001837 | Smithers-Oasis Company (Smithers-Oasis North Ame | STILL_UNCERTAIN | 0 | 0 | 6 (ORG-000057) | 1 | 0 (0) |
| SITE-001860 | Astro Manufacturing & Design Corp | VERIFIED | 7 | 0 | 0 (ORG-001781) | 1 | 4 (0) |
| SITE-001891 | OEM/Miller (ILPEA Industries) | VERIFIED | 9 | 0 | 0 (ORG-001859) | 1 | 4 (0) |
| SITE-001933 | Synesis LLC | VERIFIED | 7 | 0 | 0 (ORG-001939) | 0 | 5 (2) |
| SITE-002005 | Solutions in Polycarbonate, LLC | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-002011) | 0 | 3 (3) |
| SITE-002054 | Neo Industries Inc | STILL_UNCERTAIN | 0 | 0 | 0 (ORG-002055) | 0 | 3 (3) |
| SITE-002090 | Pu1Tec Oh LLC | VERIFIED | 9 | 0 | 0 (ORG-002134) | 0 | 3 (0) |
| SITE-003470 | LyondellBasell Composites — Conneaut | STILL_UNCERTAIN | 0 | 0 | 5 (ORG-000735) | 1 | 5 (0) |

## Files

- `packet.csv`: 387 rows (352 in-vocab, 35 off-vocab), columns as in the pilot: record_id, record_scope, field, proposed_value, source_url, quote, observed_date, source_class, verdict, notes.
- `verdicts.csv`: 54 rows with the deciding/settling fact, fetches used, availability failures.
- Row-level `verdict` in `packet.csv` is VERIFIED for a stated in-vocab value, STILL_UNCERTAIN for an off-vocab note or a weak/undated in-vocab value (7). Site-level verdict is in `verdicts.csv`.
