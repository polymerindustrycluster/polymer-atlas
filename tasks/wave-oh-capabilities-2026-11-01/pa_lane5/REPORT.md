# Pennsylvania wave, lane 5 report (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report, condensed, from the lane's hand-back.

- **Files:** `packet.csv` (380 rows) and `verdicts.csv` (61 rows).
- **Rows and checks:** every row is `own_site`. All 380 quotes are ≤ 25 words
  and script-checked.
- **Method:** vocab v1.7.6 and R3c.
- **Discovery searches:** three searches were run for Thomasnet-only orgs. They
  returned directory listings only, and nothing from them was recorded.

## Results (unit: assigned PA site rows, n = 61)

VERIFIED 33 (54%) · STILL_UNCERTAIN 28 · REJECT 0.

| field (in-vocab) | site | org | total |
|---|---:|---:|---:|
| processes | 62 | 39 | 101 |
| materials | 79 | 40 | 119 |
| markets_served | 55 | 64 | 119 |
| certifications | 9 | 8 | 17 |
| **all** | **205** | **151** | **356** |

- **Other rows:** 24 off-vocab rows; 7 in-vocab rows are row-level
  STILL_UNCERTAIN.
- **Coverage:** 50 of 61 sites got at least one value.

## Certificates checked against PDFs

| Site | Standard | Valid to |
|---|---|---|
| SITE-002717 Amrize Youngwood (LRQA) | ISO 9001:2015 | 2027-10-10 |
| SITE-002756 Synthomer Jefferson Hills (BV, multi-site) | ISO 9001:2015 | 2027-09-14 |
| SITE-002768 LTL / Americhem Morrisville (EAGLE) | ISO 9001:2015 | 2027-10-21 |
| SITE-002850 Westmoreland Latrobe (Intertek) | ISO 9001:2015 | 2027-09-12 |

**Not recorded:**
- **GeorgeKo:** ISO 9001:2008, superseded.
- **Hanes Erie, Munot, MFG:** "ISO certified" with no standard named.
- **Ultra-Poly:** only a staff biography mentions ISO.
- **Kenson:** the linked "certificate" is a newsletter.
- **Synthomer ISCC PLUS:** off-vocab; valid to 2026-12-18.

## Fetches

248 attempts (4.1 per site; the cap was never exceeded).

- **Hard failures: 14 of 248 (5.6%).**
- **No usable content at all (5 sites):** Chase, Meadville, Pac, IFS, General
  Foam. General Foam's domain registration has expired (undated).
- **No own site found (3 sites):** Pandalai, National Rubber, Gellner. Each has
  only a Thomasnet URL.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - polyiso board;
  - cultured marble;
  - phenolic wheel molding;
  - PU casting / centrifugal molding;
  - cup forming;
  - film with blown or cast unstated;
  - bag converting;
  - tolling;
  - metal stamping.
- **Materials with no term:** TPO, PPE / PPO, CPVC, PBT, LCP, PPS,
  polysulfone, hydrocarbon resins.
- **Markets with no term:** retail displays / POP, kiosks, PPE / fire shelters,
  motorsports, autobody tools, greenhouse panels.
- **Certifications with no term:** ISCC PLUS, APR-PCR-101, AAMA / FGIA VCL, SQF.

## Hygiene findings (not resolved — for the integrator)

**Stale or wrong addresses:**
1. **SITE-002169 Kenson.** Moved in 2019 to 2835 Darlington Rd, Beaver Falls;
   the row is Warrendale.
2. **SITE-002709 New Concept.** At 320 Busser Rd, Emigsville since 2007.
3. **SITE-002472 Central Distribution.** The company prints 427 Martin Ave,
   Highspire and 11B Meadow Ln, Lancaster.
4. **SITE-002430 Maugus / NNBC.** 505 E Fulton St, Lancaster.
5. **SITE-002606 Custom Inserts.** 16 Chestnut St, not 56.
6. **SITE-002742 Washington Penn.** 1604 State Route 136.
7. **SITE-002182 Ultra-Poly.** Berwick appears only in the company's history.
8. **SITE-002250 Penn Color.** The contact page lists Hatfield, and the NAICS
   236220 is wrong.
9. **SITE-002156 Superior Transparent.** The domain redirects to EKHO, and
   Ardmore is not listed.
10. **Missing streets:** SITE-002807 GeorgeKo (4861 W 23rd St, Erie) and
    SITE-002825 Munot (2935 W 17th St, Erie).

**Unheld plants and sites named by companies:**
11. **SITE-002717 Amrize:** Mt Joy distribution center.
12. **SITE-002762 MFG:** Construction & Water Products, Union City.
13. **SITE-002742 / 002792 Washington Penn:** 480 Johnson Rd HQ, VBAT 1500 Weirich
    Ave.
14. **SITE-002798 Graham:** Lancaster HQ.
15. **SITE-003673 Kerotest:** PE valves are made in Mansura LA.
16. **SITE-002843 Race Tires:** Unicoi TN.

**Parent, name or identity:**
17. **SITE-002365 US Liner.** Now Transtex Composites.
18. **SITE-002305 Arbco.** Colson Group.
19. **SITE-002768 LTL.** Americhem.
20. **SITE-002774 Consolidated Container.** Now Altium.
21. **SITE-002723 Drew Foam.** The website is Alleguard, and the NAICS 237900 is
    wrong.
22. **SITE-002750 Bemis.** The website is Amcor.
23. **SITE-002586 SRC.** Trades as Stockwell Elastomerics; typed `office_hq`, but
    production is on site.

**Scope and typing questions (owner):**
24. **Distributors or fabricators:** SITE-002472, 002819, 002404, 002606.
25. **Window assembler:** SITE-002613.
26. **Decorators or applicators:** SITE-002319, 002512.
27. **Coatings maker:** SITE-002780.
28. **Tire service center:** SITE-002736.
29. **Metal valves:** SITE-003673.
30. **Molders typed `tool_shop`:** SITE-002597, 002449, 002257.
