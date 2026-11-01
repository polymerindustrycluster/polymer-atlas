# Tranche 2, lane 4 report — PIC-12 capability wave (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so
the orchestrating session saved this report from the lane's hand-back. Neither
the lane nor this report proposes a `tier_effect`.

- **Pin:** `c0192b8` at lane start.
- **Rows and checks:** every row is `own_site` (company website or the
  certificate PDFs it links), with a URL and a quote of ≤ 25 words. All 345
  quotes passed the script's substring check; PDFs were read via `pdftotext`.
- **Method:** curl only, with no bot-wall workarounds. Vocabulary v1.7.6; R3c
  applied.

## Results (unit: assigned Ohio site rows, n = 55)

VERIFIED 30 (55%) · STILL_UNCERTAIN 25 · REJECT 0.

| field (in-vocab rows) | site | org | total |
|---|---:|---:|---:|
| processes | 47 | 28 | 75 |
| materials | 68 | 33 | 101 |
| markets_served | 39 | 82 | 121 |
| certifications | 16 | 6 | 22 |
| **all** | **170** | **149** | **319** |

- **Off-vocab rows:** 26.
- **Row-level STILL_UNCERTAIN in-vocab rows:** 2 (Gmr's "ISE 9001:2015" typo;
  TTH's ITAR listing with no registration number).

**Yield:**
- **Site-scope values:** 2.8 per assigned site, 5.1 per VERIFIED site. All
  scopes together: 5.8 per site.
- **Markets:** present at 19 of 55 sites at site scope, and 39 of 55 counting
  org scope.
- **Coverage:** 46 of 55 sites got at least one value.

**Certificates checked against PDFs and recorded:**

| Site | Standard | Valid to |
|---|---|---|
| Novagard | ISO 9001 / IATF 16949 | 2027-05-30 |
| Alttran | ISO 9001 | 2028-07-13 |
| Aurora | ISO 9001 | 2028-10-02 |
| Mar-Bal | ISO 9001 | 2028-02-28 |
| GEON | ISO 9001 | 2029-04-13 |
| Eckart | ISO 9001 | 2027-06-03 |
| Hygenic | ISO 13485 (Intertek) | 2027-10-06 |
| Killian | ISO 9001 | 2026-12-18 |

- **Killian** is current but expires seven weeks after this pass. Re-check at
  renewal.
- **Eckart's ISO 14001** expired 2026-08-04 and is not recorded.

## Fetches

197 attempts, 3.6 per site.

- **Cap exceeded:** two sites took 7 fetches, both because of a file-collision
  bug in the lane's tooling. 11 fetches were lost to that bug, the important
  pages were refetched, and no quote came from an overwritten file.
- **Hard failures: 12 of 197 (6.1%).**
  - Sealed Air: 403.
  - Nova Films: RunCloud WAF block.
  - HyComp: TLS name mismatch.
  - Quikey: HTTP/2 protocol error.
  - HEXPOL: proxy 502 / TLS failure.
  - Molding Dynamics: apex TLS alert (recovered via www).
- **No usable content at all (5 sites):** Nova Films, Sealed Air, HyComp, Quikey,
  HEXPOL. These are availability failures only, not closure evidence.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - co-extruded film with blown or cast unstated;
  - machinery building;
  - metal stamping;
  - urethane casting;
  - belt splicing;
  - filter-fabric fabrication;
  - strapping manufacture;
  - open molding.
- **Materials with no term:** PEI/ULTEM, PPO, effect pigments, polymer additives
  (plasticizers, stabilizers, biocides), CPVC.
- **Markets with no term:** military / defense packaging, law enforcement, POP
  displays, floral packaging, resin producers, equine / pet, government docks.
- **Certifications with no term:** RCMS, BRCGS, SQF. "Aligned to AS9100" is not a
  certification.

## Hygiene findings (not resolved — for the integrator)

**Unheld plants and wrong addresses:**
1. **SITE-000008 / ORG-000009 Myers / Akro-Mils.** Akro-Mils says it operates a
   manufacturing facility in Wadsworth (Medina County), and that plant is
   unheld. No page ties molding to the Akron row, and its rotational molding
   belongs to other subsidiaries.
2. **SITE-000085 Ohio Precision Molding.** The domain redirects to Design Molded
   Plastics (8220 Bavaria Dr E, Macedonia), and Barberton is never mentioned.
   This could be a rebrand, a move or an acquisition.
3. **SITE-000525 / ORG-000490 Philpott.** Brunswick is the corporate HQ, sales
   and distribution site. The Manufacturing Center at 375 Gentry Dr, Aurora is
   unheld, and the Mogadore row (SITE-000524) is never printed on the company's
   site.
4. **SITE-000026 Hygenic.** The certificate's main site is 1245 Home Ave, Akron
   44310; the row carries an FRS address. A third plant is in Cedarburg, WI.
5. **SITE-000134 Novagard.** The company's own address is 5109 Hamilton Ave,
   Cleveland; the row has an FRS street of 2720 E 79th St. The warehouse at 2160
   W 106th St is unheld.
6. **SITE-003622 Eckart.** The certificate annexes list a Perry, OH site (3767
   Lane Rd) that is unheld.

**Rows that are HQs, offices or out of scope (scope questions for the owner):**
7. **SITE-000545 Polymer Packaging.** North Canton is the HQ and warehouse;
   manufacturing is in Allendale, MI.
8. **SITE-000584 Rhein Chemie Chardon.** LANXESS lists 145 Parker Ct as a
   "Representative Office". SITE-003468 is "Plant 2".
9. **SITE-000602 Scott Bader.** North American manufacturing is in Canada; the
   Stow row is probably an office.
10. **SITE-000477 MMI Textiles.** Brooklyn is the HQ and distribution center; the
    first plant is in Lenoir, NC (2021). It is a textile company.
11. **Equipment makers and fabricators:** Litzler (machinery), Lamports (filter
    fabric), Akron Belting (belt fabrication and distribution).
12. **SITE-001438 CREO.** Mogadore is not on the company's facility list.

**Duplicates and identity:**
13. **SITE-000599 and SITE-000680 (ORG-000638).** Both rows sit at 474 Newell
    St, Painesville. One address should be one site, so this is a dedupe
    candidate.
14. **SITE-000067.** The row is named "Taylor Made Pipe Plugs", which is a
    product. The company is R.C. Graham Co. LLC (Hand-Tite), with a Hudson
    mailing address and an Aurora shipping address.
15. **SITE-001743 Dudick.** Pages call it "a division of Carboline". Check the
    parent of record.
16. **SITE-001846.** The org name is Rubber Mold Design LLC, but the company's
    site is Dalin Mold & Machine.
17. **SITE-000359.** The row name is the legacy "Ferro Polymer Additives"; the
    org website is Valtris.

**Websites and labels:**
18. **SITE-000119 Molding Dynamics.** The org `website` (molding-dynamics.net)
    fails TLS; the live domain is moldingdynamics.net.
19. **SITE-000378 Gmr.** The domain resolves to principalplasticsinc.com, and no
    street address is printed.
20. **SITE-003464 GEON.** The building labels for Bldg 426 and Bldg 438 are
    swapped between the Locations page and the certificate annex.

**Field-level problems:**
21. **Existing values outside the vocabulary:** SITE-001424, 001438, 001543,
    003464, 003622.
22. **SITE-000190 Die-Cut.** The company prints 1801 E 30th St, Cleveland 44114;
    the row has no street.
23. **SITE-000566 Protectoplas.** The About page is template filler.

**Not recorded or unreachable:**
24. **Global corporate sites with no Ohio plant tie:** SITE-000171 PPG, SITE-001394
    LyondellBasell, SITE-001720 Sealed Air.
25. **SITE-000337 Duracote.** "Aligned to AS9100" is not recorded.
26. **SITE-000502 Nova Films.** Behind a WAF; needs another route.

The per-site table is in the lane's hand-back. Verdicts and settling facts are in
`verdicts.csv`.
