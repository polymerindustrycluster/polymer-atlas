# Pennsylvania wave, lane 3 report (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so the
orchestrating session saved this report, condensed, from the lane's hand-back.

- **Files:** `packet.csv` (280 rows) and `verdicts.csv` (62 rows).
- **Rows and checks:** every row is `own_site`, with quotes of ≤ 25 words,
  script-checked. Vocabulary v1.7.6 and R3c applied.
- **Method:** curl only, with no bot-wall workarounds.
- **Discovery searches:** two web searches were used to find company domains
  only (Fluoro-Plastics, Pella). Every quote comes from a curl-fetched page.

## Results (unit: assigned PA site rows, n = 62)

VERIFIED 26 (42%) · STILL_UNCERTAIN 36 · REJECT 0.

| field (in-vocab; 7 row-level STILL_UNCERTAIN) | site | org | total |
|---|---:|---:|---:|
| processes | 47 | 23 | 70 |
| materials | 48 | 28 | 76 |
| markets_served | 58 | 52 | 110 |
| certifications | 12 | 4 | 16 |
| **all** | **165** | **107** | **272** |

- **Other rows:** 8 off-vocab rows.
- **Coverage:** 49 of 62 sites got at least one value.

## Certificates read

| Site | Standard | Valid to |
|---|---|---|
| SITE-002255 Reilly Foam, King of Prussia | ISO 9001:2015 + ISO 13485:2016 | 2027-01-17 |
| SITE-002619 Brentwood | ISO 9001:2015 (BSI) | 2028-06-19 |
| SITE-002619 Brentwood | IATF 16949:2016 | 2028-04-29 |
| SITE-002576 Fluoro-Plastics | ISO 9001:2015 (DEKRA) | 2029-06-30 |

Recorded from the company's own statements: Adhesives Research (ISO 13485 / ISO
9001), Esstech, Namsco; Westlake and UPPI at org scope.

Not recorded: conformance-only or edition-less claims at Mason Rubber, Evolution,
Accu-Mold, PCI Labs, Tri-State, Bioplast and M&Q.

## Fetches

208 attempts (3.4 per site).

- **Hard failures: 24 of 208 (11.5%).**
- **No usable content at all (13 sites).** These are availability failures only:
  - Filmtech;
  - Rodon;
  - AGC;
  - Behr;
  - Parker/LORD;
  - Ug Plast;
  - Sudarshan;
  - Superior Tire;
  - FRP Fabricators;
  - Sun Star;
  - Resin Enterprise;
  - Fenner;
  - W.B. Wagner (the domain now serves gambling content).

## Vocabulary gaps (flagged, not settled)

- **Processes:** open-cast urethane, carpet cushion, window and door assembly,
  monomer / photoinitiator synthesis, PTFE skiving.
- **Materials:** methacrylates, CompositWood, CPVC, PPO / PEI.
- **Markets:** military (separate from aerospace), fire protection, building
  services, textiles, semiconductor.
- **Certifications:** SQF, FSSC 22000, HALAL, KOF-K.

## Hygiene findings (not resolved — for the integrator)

**Wrong websites or identity:**
1. **SITE-002190 Arkema Bristol.** Bristol is not on Arkema's PA production
   list.
2. **SITE-002576 Fluoro-Plastics.** The website on file is a Thomasnet page; the
   real site is fluoropolymerproducts.com.
3. **SITE-002706 W.B. Wagner.** The domain is hijacked.
4. **SITE-002854 "Quality Plastics – Erie".** The website describes an Ohio
   company.
5. **SITE-002804 Ensinger and SITE-002693 Liberty.** The websites on file are a
   directory page and a datasheet PDF.
6. **SITE-002603.** The company is Interstate Window & Door.
7. **SITE-002198 Steve Shannon Tire.** A retail tire chain.

**Address mismatches:**
8. **SITE-002593 Door Guard.** The company prints 506 Parkway View Dr.
9. **SITE-002693 Liberty Pultrusions.** The company prints 575 Lebanon School
   Rd.
10. **SITE-002784 MCAM.** The company prints 900 North South Rd.

**Duplicates and extra holdings:**
11. **Westlake.** Two Lenni rows (SITE-002457 and 002459) and duplicate orgs
    (ORG-002472 and 002473).
12. **Washington Penn.** Three "Eighty Four" rows: SITE-002740, 002741, 002742.
13. **Brentwood.** Reading plants at 825 Morgantown Rd and 500 Spring Ridge Dr
    may be unheld.
14. **SITE-002551 Namsco.** A second New Kensington building.

**HQ, office or distributor rows (owner questions):**
15. UPPI, Whirley, PPG HQ, Shawnee (distributor), Resin Enterprise and Behr
    (distribution), J&K Foam (suite office).
16. **SITE-002343 Adhesives Research.** Typed `lab_r_and_d`, but it is the global
    HQ and holds certificates.

**Thin or doubtful polymer relevance:**
17. Craigg, Tri City Marble, L&S (template site).

**Ownership and identity:**
18. **SITE-002734.** LORD is now part of Parker.
19. **Large parents with no plant tie:** FXI, JM, Altium, ADS, Styropek (legacy
    row name "BVPV Styrenics").
