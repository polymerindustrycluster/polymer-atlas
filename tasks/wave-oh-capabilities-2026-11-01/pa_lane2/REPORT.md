# Pennsylvania wave, lane 2 report (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report, condensed, from the lane's hand-back.

- **Files:** `packet.csv` (277 rows) and `verdicts.csv` (62 rows).
- **Rows and checks:** every row is `own_site`, with a URL and a quote of ≤ 25
  words, script-checked. Vocabulary v1.7.6 and R3c applied.
- **One exception:** the Arkema ISO/IEC 17025 row has an empty quote, because
  the PDF is image-only. It is held as row-level STILL_UNCERTAIN.
- **Method:** curl only, with no bot-wall workarounds. No personal data was
  recorded.

## Results (unit: assigned PA site rows, n = 62)

VERIFIED 27 (44%) · STILL_UNCERTAIN 35 · REJECT 0.

| field (VERIFIED in-vocab) | site | org | total |
|---|---:|---:|---:|
| processes | 34 | 15 | 49 |
| materials | 35 | 45 | 80 |
| markets_served | 38 | 38 | 76 |
| certifications | 20 | 5 | 25 |
| **all** | **127** | **103** | **230** |

- **Other rows:** 30 in-vocab rows are row-level STILL_UNCERTAIN, and 17 are
  off-vocab.
- **Markets:** present at 16 of 62 sites at site scope.
- **Coverage:** 43 of 62 sites got at least one value.

## Certificates

| Site | Standard | Valid to | Recorded |
|---|---|---|---|
| SITE-002189 Arkema Birdsboro | ISO 9001:2015 (SGS) | 2029-09-21 | yes |
| SITE-002227 Pacer / DPR | ISO 9001:2015 | 2029-11-08 | yes, but the issue date 2026-11-09 is after this pass, so confirm |
| SITE-002240 J-Lok | ISO 9001:2015 | 2027–2028 | yes |
| SITE-002573 CW Thomas | AS9100D | 2028-09-18 | yes |
| SITE-002822 Executool | ISO 9001 / 13485 | 2025-10-16 | no, expired |
| SITE-002846 Specialty Tires | ISO 9001 | 2026-04-17 | no, expired |

Editions named on current pages but no certificate PDF read (recorded as page
claims): Kydex Bloomsburg, C&J, Biocoat, Fusion, Oliver Feasterville, Westlake
(org scope).

## Fetches

228 attempts (3.7 per site; the cap was never exceeded).

- **Failures: 19 of 228 (8.3%).**
- **No usable content at all (9 sites):** 002137, 002165, 002172, 002313,
  002380, 002601, 002682, 002691, 002783. These are availability failures only.
- **Repurposed domain:** `hpeplasticextrusions.com` (SITE-002165) now serves
  unrelated content.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - meltblown nonwovens;
  - liquid natural rubber;
  - grinding wheels;
  - urethane / RTV casting;
  - resin cartridges;
  - fiberglass sign panels;
  - pouch converting;
  - cultured marble;
  - metallic soaps;
  - milling equipment.
- **Materials with no term:** CPVC.
- **Markets with no term:** paper mills, outdoor signage.
- **Certifications with no term:** SQF, ISO class 5 cleanroom.

## Hygiene findings (not resolved — for the integrator)

**Wrong websites and addresses:**
1. **SITE-002295 Precision Polymers.** The website belongs to a Reynoldsburg,
   OH company, not to the Erie, PA establishment.
2. **SITE-002172, 002380, 002720, 002682, 002592.** The org website is a
   directory, permit PDF or news article, not an own site.
3. **SITE-002197 Kydex.** The company prints 6685 Low St; the row has 4411 Old
   Berwick Rd.
4. **SITE-002618 Ammeraal.** 1157 Arnold Rd is a sales and service location;
   the row is 500 Brentwood Dr.
5. **SITE-002663 New Holland Tire.** The street is 100 Jodi Dr, not a PO box.
6. **SITE-002440.** The street is garbled.
7. **Wrong ZIP:** SITE-002810, 002822, 002828.
8. **Blank street or ZIP:** 002822, 002840, 002846, 002853, 004558.

**Sites not on the company's own location list:**
9. **SITE-002254 Reilly Foam:** Eagleville.
10. **SITE-002714 SPX Cooling:** York.
11. **SITE-002370 Technetics:** no PA site listed.
12. **SITE-002777 Lanxess:** Pittsburgh.

**HQ or office rows:**
13. **SITE-002358 McClarin.** Hanover is the HQ.
14. **SITE-004558 Norac.** Ambler is HQ and R&D; production is in Helena AR.
15. **SITE-002609 Ultra-Poly.** Typed `office_hq`, but it is the main plant.

**Identity, rebrand and ownership:**
16. **SITE-002412 Safeguard.** Same address as Reilly Foam's office.
17. **SITE-002529 Monadnock.** Acquired by Precision Products Group (news dated
    2026-10-09).
18. **SITE-002732 and SITE-002789.** One org (ORG-001408), Consolidated Container
    / Altium.
19. **Rebrands and divisions:**
    - SITE-002739: UGL is now Sika;
    - SITE-002783: LORD is Parker;
    - SITE-002771: PolyOne is Avient;
    - SITE-002759: Valspar is Sherwin-Williams;
    - SITE-002726: Innocor is FXI;
    - SITE-002801: Maui Cup / Letica is Amcor.
20. **SITE-002765 BASF Monaca.** NAICS 212322 looks wrong.

**Typing and scope:**
21. **Site-type questions:** SITE-002496 C&J is a molding plant typed
    `tool_shop`. Also check 002295, 002801 and 002380.
22. **Thin polymer relevance:** 002324 CMC, 002646 Kerrico, 002703 Hushcore,
    002336 Pannier.
