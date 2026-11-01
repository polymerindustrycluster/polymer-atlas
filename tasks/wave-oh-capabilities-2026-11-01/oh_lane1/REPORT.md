# Ohio wave, lane 1 report: non-PIC-12 capability wave (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report from the lane's hand-back.

- **Files:** `packet.csv` (270 rows) and `verdicts.csv` (80 rows).
- **Assignment:** `oh_lane1_assignment.csv`, 80 Ohio site rows in non-PIC-12
  counties, ring 1–2. Pin `eb79f3b`.
- **Rows and checks:** every row is `own_site`, with a URL and a quote of ≤ 25
  words. All 270 quotes passed the script's substring check; PDFs were read via
  `pdftotext`.
- **Method:** curl only, vocab v1.7.6, R3c. No bot-wall workarounds, and one
  locked scratch directory per site.
- **Privacy:** personal names and emails seen on the Maverick and San Pallets
  pages were not recorded.

## Results (unit: assigned Ohio site rows, n = 80)

VERIFIED 34 (42.5%) · STILL_UNCERTAIN 46 · REJECT 0.

| field (in-vocab, row-level VERIFIED) | site | org | total |
|---|---:|---:|---:|
| processes | 43 | 21 | 64 |
| materials | 26 | 34 | 60 |
| markets_served | 60 | 38 | 98 |
| certifications | 8 | 2 | 10 |
| **all** | **137** | **95** | **232** |

Another 13 in-vocab rows are row-level STILL_UNCERTAIN, and 25 rows are
off-vocab.

**Yield:**
- **Site-scope values:** 1.7 per assigned site, 4.0 per VERIFIED site.
- **Markets:** present at 27 of 80 sites at site scope, and 50 of 80 counting org
  scope.
- **Coverage:** 62 of 80 sites got at least one value.

**Values tied to a specific plant:**
- **American Rheinmetall:** the Amtivo annex names 1115 S Wayne St, St. Marys.
- **Superior Plastics:** the ISO 9001 certificate names 8175 Business Way, Plain
  City.
- **Intraplas:** a Van Wert plant block on its site.
- **Step2:** Perrysville is named as a plant.
- **Evercoat:** Blue Ash is named.
- **Guardian Medical:** Swanton is named.

## Certificates checked against PDFs

| Site | Standard | Valid to |
|---|---|---|
| American Rheinmetall, St. Marys | AS9100D / ISO 9001:2015 (Amtivo 267699) | 2029-02-05 |
| Superior Plastics, Plain City | ISO 9001:2015 (Amtivo 272719) | 2027-05-12 |

**Recorded from page claims instead:**
- **Woodlawn Rubber:** a page claim of ISO 9001:2015; the certificate PDF is a
  scanned image.
- **MPS and Pleasant Precision:** page claims naming current editions.

**Not recorded:** EPC's "ISO/TS 16949", which is superseded.

## Fetches

299 attempts, 3.7 per site; the cap was never exceeded.

- **Hard failures: 28 of 299 (9.4%).**
- **No usable content at all (10 sites).** These are availability failures only,
  not closure evidence:
  - Polynt / Cook Composites: 403.
  - Fox Lite: 403.
  - Midwest Plastics: 406.
  - Southeastern Container: 406.
  - NanoSperse: expired TLS certificate.
  - Nissen Chemitec: connection resets.
  - Okamoto Sandusky: resets, then 503.
  - Kittyhawk: proxy 502, then DNS failure.
  - KLW Plastics: redirects to Mauser Packaging.
  - Stronghold: parked domain.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - rubber molding with the type unstated;
  - urethane molding / casting;
  - belt-press UHMW-PE sheet;
  - metal fabrication;
  - cut / sew / heat-seal of flexible sheet;
  - upholstery;
  - sterile-barrier packaging;
  - laser cutting;
  - selective-dissolution PP recycling;
  - extrusion or film with the type unstated;
  - composite resin manufacture;
  - vinyl window fabrication;
  - poly-bag conversion.
- **Markets with no term:** promotional products, infant care, radiological /
  hazmat protective gear, signage and graphics, retail displays, military
  ammunition packaging.
- **Certifications with no term:** BRCGS.
- **Mapping calls the integrator may revisit:**
  - "Class 7" → `cleanroom_iso7`;
  - "Class 100,000" → `cleanroom_iso8`;
  - pools → `lawn_garden_recreation`;
  - military → `aerospace_defense`;
  - vinyl → `pvc`;
  - petrochemical → `energy_oil_gas`;
  - semiconductor → `electronics_electrical`;
  - PE-RT → `polyethylene_pe`.

## Hygiene findings (not resolved — for the integrator)

**Rows that are offices or HQs, and scope questions:**
1. **SITE-000803 Columbus Gasket.** The Columbus address is a "Regional Office".
   Production is at 10145 Queens Way, Chagrin Falls, plus Rockford IL.
2. **SITE-000946 HBD Industries.** A corporate suite. The Thermoid plant is
   SITE-000947 (Bellefontaine).
3. **SITE-000749 Azelis.** A chemical distributor.
4. **SITE-000777 Calorplast.** No page says it manufactures at Milford.
5. **SITE-003316 Omya and SITE-001336 Plastinuva.** Both are typed `hq_only`.
   Plastinuva is "developing" its process, so it is possibly `pre_revenue`.
6. **SITE-001201 Shepherd Color.** 4539 Dues Dr is the corporate HQ.
7. **Non-processor scope questions:** Howard Industries (toll chemical), Wolf
   Creek (steel piping), Denizen (insulation distributor, page © 2007), Powder
   Coating Specialty (coats metal), Rich Industries (sewn garments), Casco
   (mattresses).
8. **SITE-000826 Crane CPE and SITE-000872 DuPont Dayton.** No plant activity is
   named.

**Unheld or mismatched plants:**
9. **SITE-001229 Superior Plastics.** A Bellefontaine plant (106,000 sq ft) is
   unheld. A second Plain City building is at 8163 Business Way.
10. **SITE-001141 Putnam.** Three locations; the row is the Farm Products
    division.
11. **SITE-001491 Velocity.** The only printed plant is 9344 Sunrise Rd,
    Cambridge OH; the row is Mason.
12. **SITE-001517 ADS HanTech.** Typed `rd_center`. ADS names only its Hilliard
    Engineering and Technology Center.
13. **SITE-001450 and SITE-001451 Spinnaker (Troy).** Two rows at one site,
    which is a dedupe candidate. Spinnaker was acquired by Mactac in Feb 2022;
    check the parent of record.
14. **SITE-001813 Shamrock.** The company prints 633 Howard St, Mount Vernon. It
    also operates in Myrtle Beach SC.
15. **SITE-000977 Evercoat.** The footer gives 6600 Cornell Rd, Cincinnati 45242
    (Blue Ash).
16. **SITE-001010 Magnum.** The row says Devola; the company prints 801 Masonic
    Park Rd, Marietta.

**Identity, rebrand and domain problems:**
17. **SITE-000740 "Axillon Aerospace – Cincinnati".** The website resolves to
    Mearthane Products Corp (Cranston RI).
18. **SITE-000928 GMR Bolivar.** The site is served by Principal Plastics, and
    Bolivar is never named.
19. **SITE-000859.** Named "DJM Plastics"; the company is DLM Plastics.
20. **SITE-001241.** Named Teijin; the website is CSP.
21. **SITE-001685 Intraplas.** Van Wert opened in 2025, and no street is
    printed.
22. **SITE-002062 KLW.** The domain redirects to Mauser Packaging, which may
    mean an acquisition.
23. **SITE-001832 Stronghold.** Parked domain.
24. **SITE-001761 Kittyhawk.** DNS failure on one route; availability only.
25. **SITE-001055 NanoSperse.** Expired TLS certificate.

**Field-level observations:**
26. **SITE-000720 Rheinmetall.** An ISO 14001 certificate is listed by filename
    only, so it is not recorded.
27. **SITE-001914 EPC.** The ISO 13485 claim has no edition.
28. **SITE-001727 Berlekamp and SITE-001914 EPC.** Fremont is unconfirmed.

Verdicts with caveats are on Step2, Magnum, Evercoat, Intraplas, Casco, Rich,
Powder Coating Specialty and Spinnaker. Settling facts are in `verdicts.csv`.
