# Pennsylvania wave, lane 4 report (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report, condensed, from the lane's hand-back.

- **Files:** `packet.csv` (372 rows) and `verdicts.csv` (61 rows).
- **Source class:** every row is `own_site` except 2 Magee rows from a
  Trelleborg press release (`press`, row-level STILL_UNCERTAIN).
- **Checks:** quotes are ≤ 25 words and script-checked. Vocabulary v1.7.6 and
  R3c applied.
- **Method:** curl only, with no bot-wall workarounds.
- **Privacy:** no personal data recorded. One founder's name was dropped from a
  quote.

## Results (unit: assigned PA site rows, n = 61)

VERIFIED 32 (52%) · STILL_UNCERTAIN 29 · REJECT 0.

| field (row-level VERIFIED) | site | org | total |
|---|---:|---:|---:|
| processes | 47 | 36 | 83 |
| materials | 58 | 51 | 109 |
| markets_served | 65 | 50 | 115 |
| certifications | 26 | 3 | 29 |
| **all** | **196** | **140** | **336** |

- **Other rows:** 6 in-vocab rows are row-level STILL_UNCERTAIN, and 30 are
  off-vocab.
- **Markets:** present at 22 of 61 sites at site scope, and 44 of 61 counting org
  scope.
- **Coverage:** 52 of 61 sites got at least one value.

## Certificates read from the document (each names the row address)

| Site | Standard | Valid to |
|---|---|---|
| Specialty Roller, Berwick | ISO 9001:2015 | 2028-04-03 |
| Mold Specialties, Hershey | ISO 9001:2015 | 2027-06-22 |
| Holbrook Tool, Meadville | ISO 9001:2015 + ISO 13485:2016 | 2029-03-31 |
| Rogers Foam, Morrisville (annex) | ISO 9001:2015 | 2027-09-19 |
| Precision Polymer, Pottstown | ISO 9001:2015 | 2029-09-30 |
| A-Lok, Tullytown | ISO 9001:2015 | 2028-12-12 |
| Crescent, New Freedom | ISO 13485:2016 | 2027-09-05 |
| Crescent, New Freedom | ITAR (DDTC letter) | 2027-01-31 |

- **Corry Rubber:** ISO 9001 and IATF 16949 are valid to Dec 2026, so re-check at
  renewal.
- **Not recorded:** Gemini ("compliant"), MCAM (no standard named), Kenson
  AS9100 (no revision named), Pittsburgh Plastics ISO 13485 (no edition named).

## Fetches

243 requests (4.0 per site; the cap was never exceeded).

- **Failures: 24 of 243 (9.9%).** These are availability failures only.
- **No usable content at all (4 sites):** Aline, Hydrojet (hosting suspended),
  Polyflo, Magee (WAF block).

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - roll covering;
  - open casting;
  - dip and slush molding;
  - belt fabrication;
  - open molding;
  - rubber-to-metal bonding;
  - vinyl window fabrication;
  - foundry cores;
  - textile weaving;
  - untyped extrusion;
  - thermoset resin compounding.
- **Materials with no term:** PEI, PSU, PPSU, PPS, PES, PBT, PPA, PPE+PS.
- **Markets with no term:** kiosks, POP displays, entertainment masks, sports
  surfacing, utilities, orthopedic cushioning, foundries.
- **Certifications with no term:** SQF, IMS, SMETA, NACE CIP.

## Hygiene findings (not resolved — for the integrator)

**Identity, redirects and ownership:**
1. **SITE-002400 Tubro.** The domain redirects to Polymershapes, a distributor.
2. **SITE-004259 PolyVisions.** The domain redirects to Bemis Associates (MA).
3. **SITE-002684 Magee.** Acquired by Trelleborg (press release 2024-12-04).
   Check the parent of record.
4. **SITE-002498 Holbrook.** "An Allegheny Performance Plastics Company"; check
   the parent.
5. **SITE-002585 Siltco.** The live site is Mutual Industries.
6. **SITE-002767 ITW.** The website never names Montgomeryville.
7. **SITE-002707 C-P Converters.** A second York facility is unheld. NAICS 114100
   is wrong.
8. **SITE-002831 Millet.** The US site is milletplastics.us (21 Lebanon Valley
   Pkwy).
9. **SITE-002779.** The name is misspelled "Sherman-Williams".

**Wrong or conflicting addresses:**
10. **SITE-002604 Plastic Dip Moldings.** The company prints 2345 Milford Square
    Pike, Quakertown.
11. **SITE-002694 Colorcon.** The company lists 420 Moyer Blvd. Harleysville HQ
    and Chalfont look unheld. NAICS 238900 is wrong.
12. **SITE-002741 and SITE-002791 Washington Penn.** The Arden plant is at 2080 N
    Main St, and HQ at 480 Johnson Rd.
13. **SITE-002304 APT.** America's Lane. **SITE-002249 Arbonite:** ZIP 18902.
    **SITE-002595 IRP:** Greentree.

**Unheld plants:**
14. **MFG Union City (two plants).**
15. **Crescent:** 224 N Constitution Ave.
16. **Precision Polymer:** 824 Queen St.
17. **Pecora:** Hatfield distribution center.
18. **Graham:** York plant and Graham Recycling.

**Scope questions (owner):**
19. **SITE-002201 C&G Arms.** Firearms holsters, with NAICS 325211.
20. **SITE-002353 Kore Mart.** Foundry cores.
21. **SITE-003257 Bally Ribbon.** Textile.
22. **Distributors and fabricators:** L.M. Robbins, IRP.
23. **SITE-002256 ColorRite.** Distribution.
24. **SITE-002716 W.R. Meadows.** Office and warehouse.
25. **SITE-002249 Arbonite.** An applicator.

**Field-level and other:**
26. **SITE-002722.** Still named "Consolidated Container" under ORG-001408
    (Altium), with no NAICS.
27. **SITE-002139 Fuling.** Typed `office_hq`, but it is a plant.
28. **SITE-002192 KER.** Press counts conflict (fifteen versus twenty-two).
