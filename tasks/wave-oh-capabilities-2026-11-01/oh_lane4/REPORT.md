# Ohio wave, lane 4 report (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report, condensed, from the lane's hand-back.

- **Pin:** `eb79f3b`.
- **Assignment:** 80 active Ohio site rows outside PIC-12, ring 1–2.
- **Rows and checks:** every row is `own_site`. All 228 quotes passed the
  script's substring check against the exact `source_url`.
- **Method:** vocab v1.7.6 and R3c. No bot-wall workarounds. No personal data
  recorded.

## Results (unit: assigned site rows, n = 80)

VERIFIED 30 (37.5%) · STILL_UNCERTAIN 50 · REJECT 0.

| field | site | org | total |
|---|---:|---:|---:|
| processes | 45 | 23 | 68 |
| materials | 20 | 20 | 40 |
| markets_served | 39 | 56 | 95 |
| certifications | 8 | 4 | 12 |
| **all** | **112** | **103** | **215** |

- **Other rows:** 13 off-vocab rows; 2 row-level STILL_UNCERTAIN.
- **Markets:** present at 20 of 80 sites at site scope, and 47 of 80 counting org
  scope.
- **Coverage:** 64 of 80 sites got at least one value.
- **Why the VERIFIED share is lower:** the scope rule held. Most assignments are
  multi-plant parents whose pages name no plant activity (Axium, ALPLA, Ampacet,
  Graham, FXI, Cooper Standard, Tenneco, IAC).
- **Site scope by single-location inference:** listed in each row's notes. The
  integrator may demote these.

## Certificates checked against PDFs

| Site | Standard | Valid to |
|---|---|---|
| Denney (SITE-000854) | AS9100D / ISO 9001:2015 | 2027-09-09 |
| PTC Enterprises (SITE-001990) | ISO 9001:2015 | 2027-09-03 |
| Vernay Yellow Springs (SITE-001283) | ISO 9001:2015 (Sales / R&D / Lab) | 2027-03-31 |
| Vernay Yellow Springs (SITE-001283) | IATF 16949 (remote support only) | 2027-03-05 |

The integrator may decline the Vernay IATF row.

**Not recorded:**
- **Superseded editions:** Tetra (ISO 9002, QS-9000, ISO/TS), EPC (ISO/TS).
- **No edition named:** Netherland Rubber, Resinoid.
- **Typo:** Minco ("ISO 2001:2015").
- **Wrong plant:** the Flex Technologies IATF certificate names Lafayette TN and
  Midvale OH, not Baltic.

## Fetches

212 attempts (2.65 per site; the cap was never exceeded).

- **Flagged attempts:** 19 (9.0%).
- **No usable content at all (10 sites):** Danfoss, Hamilton Caster, JP
  Industrial, Trimas/Rieke, Schuetz, BriskHeat, Ludlow/Crown Foam, Plymouth Foam,
  Catexel, Moriroku. These are availability failures only.
- **Not used:** `rieke.com` belongs to an unrelated company.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - film / glovebag fabrication;
  - flexographic plate making;
  - cast polymer / solid surface;
  - cut-and-sew and foam-in-place;
  - fitment manufacturing;
  - micro-composite fiber;
  - recycling with the type unstated.
- **Materials with no term:** TPO (exists only in CAP_MATERIAL), polymer-bonded
  cast stone.
- **Markets with no term:** material handling / waste, coatings resins,
  childcare equipment, aquaculture / lab tanks.
- **Nearest-term mappings, flagged in row notes:**
  - recreation → `lawn_garden_recreation`;
  - corrugated printing plates → `packaging_industrial`;
  - food supplier → `food_processing_foodservice`;
  - bedding → `furniture_office`.

## Hygiene findings (not resolved — for the integrator)

**Office, dealer or out-of-scope rows (scope questions for the owner):**
1. **SITE-000755 Hedstrom.** Ashland is the main office and distribution center.
2. **SITE-000735 ASK Chemicals.** 495 Metro Place S, Dublin looks like an
   office.
3. **SITE-001204 Shrader Tire & Oil.** A tire and fleet dealer.
4. **SITE-001222 Storopack.** The row is a service center.
5. **SITE-001283 Vernay.** Sales / R&D / Lab only; manufacturing is in Georgia.
6. **SITE-001342 Advanced Composites.** Typed `warehouse_distribution`, yet ring
   2.
7. **SITE-001328 ALTA.** No plant is named.
8. **SITE-001598 RAM Precision.** A metal CNC shop.
9. **SITE-000910 Flexoplate.** A printing-plate shop.
10. **SITE-001803 Woodrow.** A label and nameplate converter.
11. **SITE-001110 Plastic Lumber Store.** A retailer.
12. **SITE-001234 U.S. Plastic / Tamco.** A catalog distributor.
13. **SITE-001146 Queen City Polymers.** A distributor and fabricator; plants in
    Dayton, Pharr TX and Reynosa MX.
14. **SITE-000791 Chatelain.** "We've moved" to 535 6th St, Findlay.
15. **SITE-001822 Lancaster.** A tableware supplier.

**Unheld or mismatched sites:**
16. **SITE-001689 Quanex.** 800 Cochran Ave is "Extruded Solutions"; a "Mixing"
    site at 804 Byesville Rd may be unheld.
17. **SITE-001038 Minco.** ASPM is at 900 Falls Creek Dr, Vandalia; Minco Tool &
    Mold, Dayton, may be unheld.
18. **SITE-001160 Resinoid.** Hebron is the molding division; phenolic materials
    are made in Skokie IL.
19. **SITE-001005 Liquibox.** Upper Sandusky is fitments; an Ashland OH bag and
    bottle plant is listed.
20. **SITE-000743 Axium.** Six New Albany plants plus Apex Finishing and Vertix
    Recycling. Check which are held.
21. **SITE-000712 ALPLA Lima.** "Base Plant"; no product is stated.
22. **SITE-001255 TJC Polymers.** The site prints 3100 Research Blvd, Dayton;
    the org HQ is Kettering.

**Identity and websites:**
23. **SITE-001169 Rieke.** `trimaspackaging.com` returns 406.
24. **SITE-001122 Polyflex Baltic.** Baltic is never named.
25. **SITE-004225 Benvic.** "Trinity Plant" is not on the company's site.
26. **SITE-000886, SITE-001764, SITE-001026.** These are trade names: The Soak
    Factory, ChildBrite, Aptyx.
27. **SITE-001464 Medal.** The site is lorem ipsum filler.

**Field-level problems:**
28. **Existing values outside the vocabulary:** ORG-001197 `tooling_mold_die`,
    Medal `3d_printing`, ORG-001485 free text.

Settling facts are in `verdicts.csv`.
