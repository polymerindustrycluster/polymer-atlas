# Pennsylvania wave, lane 1 report (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report, condensed, from the lane's hand-back.

- **Files:** `packet.csv` (322 rows) and `verdicts.csv` (62 rows).
- **Pin:** `cb1304d`.
- **Rows and checks:** every row is `own_site`. Quotes are ≤ 25 words and were
  script-checked twice. Vocabulary v1.7.6 and R3c applied.
- **Method:** curl only. Plain http was used only after connection-level TLS
  errors, never to get around an invalid certificate.
- **Privacy:** no personal data recorded.

## Results (unit: assigned PA site rows, n = 62)

VERIFIED 23 (37%) · STILL_UNCERTAIN 39 · REJECT 0.

| field (VERIFIED in-vocab) | site | org | total |
|---|---:|---:|---:|
| processes | 47 | 27 | 74 |
| materials | 67 | 47 | 114 |
| markets_served | 52 | 36 | 88 |
| certifications | 6 | 4 | 10 |
| **all** | **172** | **114** | **286** |

- **Other rows:** 8 in-vocab rows are row-level STILL_UNCERTAIN, and 28 are
  off-vocab.
- **Coverage:** 48 of 62 sites got at least one value.
- **Markets:** present at 16 of 62 sites at site scope, and 37 of 62 counting org
  scope.
- **Why so many are uncertain:** most rows belong to multi-plant parents, so
  their values stay at org scope.

## Certificates read against documents

| Site | Standard | Valid to |
|---|---|---|
| Donaldson, Feasterville (annex to the Ivyland certificate) | ISO 9001:2015, BSI FM 90608 | 2029-09-30 |
| Drug Plastics, Boyertown | ISO 15378:2017 (off-vocab) | 2028-11-12 |

- **Donaldson:** the Atlas row cites the superseded certificate, which expired
  2026-10-02. The IATF certificate does not list Feasterville.
- **Not recorded:** the superseded ISO 9001:2008 at Reubes and Crosslink.

## Fetches

247 attempts (4.0 per site; the cap was never exceeded).

- **Availability failures: 24 of 247 (9.7%).**
- **No usable content at all (5 sites):** Performax, American Additive (Vercel
  challenge; not worked around), Industrial Floor, General Plastics, Custom
  Molds.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - plastisol dip and slush molding;
  - slabstock PU foam;
  - polyester fiber;
  - film with blown or cast unstated;
  - wax blending;
  - rubber molding with the type unstated;
  - machinery building;
  - bulk terminal.
- **Materials with no term:** polyester fiber, PEI, PPS, PEKK, PESU / PSU /
  PPSU, SAN, Noryl, EVA, CPVC, EPS, PDCPD, LCP, polymer-modified bitumen.
- **Markets with no term:** filtration fabrics; mobility / built environment.
- **Certifications with no term:** ISO 15378, FSSC 22000, ISO class 5
  cleanrooms.

## Hygiene findings (not resolved — for the integrator)

**Identity, relocation and status:**
1. **SITE-002701 Spadone.** Its own page says it relocated its offices and
   manufacturing to the Troester facility near Akron, OH in April 2026.
   - The Willow Grove row may be closed. Run the Form 5500 check before any
     status change.
   - The Akron facility may be an Ohio lead.
2. **SITE-002171 Green Garden.** The domain redirects to an unrelated site.
3. **SITE-002617 US Plastic Moldings.** The company says it is in Statesville,
   NC; the Quakertown row is uncorroborated.
4. **SITE-002679 Profile Plastics.** The pages print only Canton, OH; the
   Warminster row looks like an identity mismatch.
5. **SITE-002495.** The company at that address is Advantage Mold & Design
   (tooling).
6. **SITE-002332 Freeport Terminals.** A bulk transload terminal, so a scope
   question.
7. **SITE-002719 FB Leopold.** Polymer relevance is unproven.

**Hubs, offices and type mismatches:**
8. **SITE-002852 Graham Lancaster.** HQ; the flagship plant is York.
9. **SITE-002188 STTC York.** The retread plant is not tied to York.
10. **SITE-002196 Kleerdex.** Typed `office`; it is Sekisui Kydex.
11. **SITE-002311 Packaging Technology.** Typed `distribution_center`, but it does
    vacuum forming.
12. **SITE-002608 Adams.** Typed `office_hq`; the website on file is a ThomasNet
    URL (the own site is adamsmfg.com).
13. **SITE-002226 Rose Plastic.** "California, PA" versus Coal Center.
14. **SITE-002827 KNF.** Tamaqua is the HQ among three plants.
15. **SITE-002660 Highwood.** The company prints 87 Tide Rd.
16. **SITE-002357 McClarin.** The footer prints 15 Industrial Dr, and the company
    names three plants against five Atlas rows.
17. **SITE-002457 Westlake.** "Multiple PA facilities" against two Atlas rows.
18. **Not mentioned on corporate pages:** Avery Mill Hall, PPG Allison Park,
    Sherwin-Williams Rochester, Valspar Pittsburgh.

**Addresses and websites:**
19. **SITE-002322 Donaldson.** The annex says 1731 Loretta Ave; the row has 1741.
20. **SITE-002475 Keystone Foam.** The company's address is 5358 PA-982, Derry.
21. **SITE-002349 and SITE-002821.** The org websites are a permit folder and a
    certificate PDF.
22. **SITE-002788 MFG Union City.** Two entities at one address.
23. **SITE-002845 Retal Donora.** No street on the row; the plant is operating
    (October 2026 press release).
24. **SITE-002377 Polyglass.** "555 Oakridge Rd".
25. **SITE-002590 Crosslink.** No street printed; the badge is stale.
26. **SITE-004026 Riverdale and SITE-002712 Proxie Models.** Thin content.
