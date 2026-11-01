# Pennsylvania wave, lane 6 report (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report, condensed, from the lane's hand-back.

- **Files:** `packet.csv` (292 rows) and `verdicts.csv` (61 rows).
- **Rows and checks:** every row is `own_site`; certificate PDFs were read with
  `pdftotext`. Quotes are ≤ 25 words and script-checked twice.
- **Method:** vocab v1.7.6 and R3c. curl with its default user agent, with no
  bot-wall workarounds.

## Results (unit: assigned PA site rows, n = 61)

VERIFIED 30 (49%) · STILL_UNCERTAIN 31 · REJECT 0.

| field (in-vocab) | site | org | total |
|---|---:|---:|---:|
| processes | 57 | 26 | 83 |
| materials | 45 | 19 | 64 |
| markets_served | 58 | 36 | 94 |
| certifications | 15 | 4 | 19 |
| **all** | **175** | **85** | **260** |

- **Other rows:** 32 off-vocab rows; 5 in-vocab rows are row-level
  STILL_UNCERTAIN.
- **Coverage:** 45 of 61 sites got at least one value.
- **Markets:** present at site scope at 22 sites.

## Certificates checked against PDFs (site scope)

| Site | Standard | Valid to |
|---|---|---|
| SITE-002517 Phillystran / WireCo, 151 Commerce Dr | ISO 9001:2015 | 2029-01-24 |
| SITE-002658 Polymics | ISO 9001:2015 | 2028-04-05 |
| SITE-002737 GEON Croydon (annex) | ISO 9001:2015 | 2029-04-13 |
| SITE-002808 Augustine | AS9100D + ISO 9001:2015 | **2026-11-19** (re-check at renewal) |
| SITE-002820 Drug Plastics Kittanning | ISO 15378:2017 (off-vocab) | 2028-11-12 |
| SITE-002835 Neville Chemical | ISO 9001:2015 | 2028-04-24 |

**Not recorded:**
- **SITE-002851 York Imperial:** no edition named.
- **SITE-002225 TAFCO:** no standard named.
- **SITE-002502 PTR:** the ISO text belongs to another company.

## Fetches

211 attempts (3.5 per site; the cap was never exceeded).

- **Hard failures: 16 of 211 (7.6%).**
- **No usable content at all (9 sites).** These are availability failures only:
  - Alex Color;
  - Chase (Vercel checkpoint);
  - Precise Plastics;
  - EAM-Mosca;
  - Mahantango;
  - Medical Precision Plastics;
  - Parker;
  - Westlake Royal;
  - Zurn.
- **Global parents with no entry for the assigned address:** Avient, PPG, Amcor,
  Hexion, MCAM, LANXESS.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - fiber rope;
  - laser engraving of sleeves;
  - cast urethane;
  - monomer synthesis;
  - metal injection molding;
  - molded FRP grating;
  - vinyl window fabrication;
  - lathe-cut rubber;
  - RIM;
  - glass mat;
  - co-packing;
  - cultured marble;
  - vinyl statuary.
- **Materials with no term:** PBI, PPS, PEI, PPSU, PEKK, polyimide; aramid / LCP
  / UHMWPE fibers; acrylic and methacrylate monomers; hydrocarbon resins.
- **Markets with no term:** supplements, coatings and ink formulators, corrugated
  paper, metal forming, motorsports, material handling.
- **Certifications with no term:** ISO 15378, RCMS.

## Hygiene findings (not resolved — for the integrator)

**Wrong or unheld rows:**
1. **SITE-002724 Wacker Allentown.** Not described on the company's site.
2. **SITE-002348 Tiger Door.** The company's contact page gives Brownsville TX
   (Phoenix Door Systems), so it may have moved or changed owner.
3. **SITE-002526 Regency Plus.** The company prints 2000 Locust Gap Hwy; the row
   says 1024.
4. **SITE-002385 Gellner.** The company prints 105 Tide Rd; the row says 151. The
   operator is Gellner Industrial LLC.
5. **SITE-002356 McClarin.** The company prints 15 Industrial Dr and names three
   plants.
6. **SITE-003425 Superior Huntingdon.** The address on the company's site
   conflicts with the row.
7. **SITE-002607 Adams.** The address is unconfirmed.
8. **SITE-002251 Penn Color Hatfield.** A design center; HQ is Doylestown.
9. **SITE-002170 Bedford.** North and South facilities, with no streets printed.
10. **SITE-002799 and SITE-002797 Graham.** 505 and 500 Windsor St; a possible
    duplicate.
11. **SITE-002775 Graham North East.** A warehouse row, not named on Graham's
    pages.
12. **SITE-002820 Drug Plastics.** The website on file is a certificate PDF, and
    other plants are listed.
13. **SITE-002517 United Ropeworks.** 141 Commerce Dr is unheld.
14. **SITE-002699 Suscon.** Typed `office_hq`; it does co-packing; a Vero Beach
    FL site is listed.
15. **SITE-002203 Luminite.** Typed `office_hq`, but manufacturing is in the same
    building.
16. **SITE-004377 LANXESS.** Production is at Neville Island, 3499 Grand Ave,
    which is unheld.

**Website, identity and scope issues:**
17. **Org website is not an own site:** SITE-002474, 002607, 002678, 002194,
    002820. SITE-002451 points to the Dutch parent.
18. **Names:**
    - "Tmp Acuisitions New" is TMP / TAFCO;
    - SITE-002730 still says PolyOne;
    - SITE-002737 is GEON Croydon.
19. **SITE-003723 Zurn Erie.** No street on the row.
20. **Scope questions (owner):** STTC (tire chain), TAFCO (walk-in coolers),
    Rynone (countertops), Vinylux (upcycled records), HT Bauerle (metal and
    plastics shop).
21. **SITE-002688 Arkema West Chester.** The Sartomer monomer plant.
