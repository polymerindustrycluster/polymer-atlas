# Ohio capability wave, lane oh-8 report (2026-11-01)

This is a packet, not a data change. The lane wrote only `packet.csv`, `verdicts.csv` and this report. It did not edit `data/`, allocate IDs, commit or push, and it proposes no `tier_effect`.

- **Pin:** `2dc8ee5` at lane end (the wave brief pins its candidate set at `eb79f3b`).
- **Assignment:** `oh_lane8_assignment.csv`, 79 Ohio site rows outside PIC-12, ring 1-2.
- **Method:** curl only, through the configured proxy, with no bot-wall workarounds (no faked user-agent, no TLS bypass, no captcha work). Every row is `own_site` (company website, or certificate PDFs it links, read with `pdftotext`). Vocabulary v1.7.6; R3c applied.
- **Quote check:** all 236 quotes are 25 words or fewer and were checked by script as substrings of the fetched text (whitespace-normalised). The same script checked every in-vocab value against `docs/schema/vocab.json`.
- **Scratch:** `/tmp/claude-0/wave-oh/lane8/` only, one lock file per site. No site was fetched in parallel with itself.

## Results (unit: assigned Ohio site rows, n = 79)

VERIFIED 37 (47%) · STILL_UNCERTAIN 42 · REJECT 0.

| Packet rows (unit: rows in `packet.csv`) | site scope | org scope | total |
|---|---:|---:|---:|
| in-vocab, row verdict VERIFIED | 109 | 84 | 193 |
| in-vocab, row verdict STILL_UNCERTAIN | 11 | 1 | 12 |
| off-vocab `*_other_note` rows | 23 | 8 | 31 |
| **all rows** | **143** | **93** | **236** |

In-vocab VERIFIED rows by field:

| field | site | org | total |
|---|---:|---:|---:|
| processes | 38 | 16 | 54 |
| materials | 32 | 35 | 67 |
| markets_served | 30 | 33 | 63 |
| certifications | 9 | 0 | 9 |
| **all** | **109** | **84** | **193** |

**Yield:**
- **Site-scope in-vocab values:** 1.4 per assigned site (109 / 79), 2.9 per VERIFIED site (109 / 37). All scopes together: 2.4 per assigned site (193 / 79).
- **Coverage:** 37 of 79 sites got at least one site-scope in-vocab value. 57 of 79 got at least one in-vocab value at any scope (own-site or org rows).
- **Markets:** present at site scope for 18 sites.
- **Why the yield is lower than the PIC-12 tranche 2 lane (VERIFIED 55%):** 10 sites could not be read at all (below), and many more are plants of global parents (Amcor, DuPont, Autoneum, Huhtamaki, CNG, Alleguard, Woodbridge, GVS, Bostik, Mauser/BWAY, Kenda and others) whose corporate sites have no plant list. For these the lane stopped at org scope rather than push values down.

**R3c certificate review (unit: certifications):**

| Site | Standard | Valid to | Recorded |
|---|---|---|---|
| SITE-000966 Integris (Hebron) | ISO 9001:2015 with Design (Smithers PDF) | 2029-10-07 | yes |
| SITE-000966 Integris (Hebron) | AS9100:2016 with Design (Smithers PDF) | 2029-10-07 | yes |
| SITE-001129 SIMONA PMC (Findlay) | ISO 9001:2015 (Bureau Veritas PDF) | 2027-03-12 | yes |
| SITE-001044 Moore Industries (Montpelier) | ISO 9001:2015 (certificate PDF) | 2028-12-15 | yes |
| SITE-001176 Robin Holmco (Winesburg) | ISO 9001:2015 (Smithers PDF) | 2027-07-16 | yes |
| SITE-001176 Robin Holmco (Winesburg) | IATF 16949:2016 (Smithers PDF) | 2027-07-16 | yes |
| SITE-000799 Coexcell, SITE-000728 Earthfirst, SITE-000936 Guardian | ISO 9001:2015 (page text, no PDF) | not shown | yes (page names the 2015 edition) |
| SITE-001009 Kasai Upper Sandusky | IATF 16949:2016 (cert 07731) | 2024-06-15 | **no, expired** |
| SITE-001009 Kasai Upper Sandusky | ISO 14001:2015 (cert 11225) | 2021-06-10 | **no, expired** |

- **Kasai:** its awards page still links both Upper Sandusky certificates, and both are expired. This is a currency finding for the integrator.
- **Held back as STILL_UNCERTAIN (not recorded):**
  - **American Colors:** the homepage says "ISO 9001-2015 registered" for Sandusky, but the linked SAI Global certificate expired 2024-06-30 and no newer one was found.
  - **RheTech Colors:** "ISO 9001 and ISO 14001 certified" with no edition or certificate; its ISO 17025 lab has no site tie.
  - **AeroBlast:** "ISO 9001 certified", no edition.
  - **BCM Inks:** ISO 9001:2015 "achieved", with no date or certificate.
  - **Wurms:** "QMS follows ISO 9001:2015".
  - **Boomerang Rubber:** "IS0 14001-certified", no edition.
  - **Convertapax:** "SAI Global audited", no standard.
- **Holmco ISO 14001:** the Robin Holmco certificate PDF is an image with no extractable text, so it was not recorded.

## Fetches

213 attempts for 79 sites, 2.7 per site, never more than 6.

- **Failures: 24 of 213 (11.3%).**
  - **10 sites gave no usable content at all.** All are availability failures, not closure evidence:

    | Site | Failure |
    |---|---|
    | ISO Technologies | connection reset, apex and www |
    | Nagase ChemteX | HTTP 406, apex and www |
    | Nifco America | HTTP 406, www and apex |
    | Pac Worldwide | HTTP 403 |
    | Syensqo (Solvay Marietta) | HTTP 403 |
    | Parker (Parker Lord Dayton) | HTTP 403 |
    | Delaware Paint | self-signed certificate, apex and www |
    | Kardol | HTTP 403 |
    | Performance Additives | proxy CONNECT 502, twice |
    | Fouty & Co | TLS name mismatch, apex and www |

  - **Other failures:**
    - Four guessed URLs returned 404: `amcor.com/about/locations`, `cnginc.com/locations/`, and `dupont.com/about/locations.html` (once for each of the two DuPont sites). A guessed path that 404s says nothing about the company.
    - Two 403s on secondary pages: `bostik.com/usa/en/` and `en.t-umg.com/corporate/global-base/`.
    - Two near-empty pages: L and C Plastic Bags' Locations page (image-based, 144 characters of text) and the Holmco ISO 14001 PDF (image-only).
- **Wasted fetch:** SITE-001105 Plaskolite fetch #2 repeated the homepage by my error. It is counted in `fetches_used` and the lane did not refetch it.
- **Shared pages:** SITE-000849 and SITE-000871 (both DuPont) and SITE-000775 and SITE-002086 (both Mauser) each fetched the same corporate page, so each site's fetch count is its own.

## Vocabulary gaps (flagged, not settled)

- **Processes with no term:**
  - rubber molding with the method unstated (Holmco, Boomerang);
  - urethane and silicone casting or molding (Hamilton Custom Molding);
  - thermoset molding with the press type unstated (DimcoGray);
  - PSA label-stock coating and converting (Spinnaker; `pressure_sensitive_tape_manufacture` is tape);
  - polypropylene dissolution purification (PureCycle; fits neither pyrolysis nor solvolysis);
  - blast-media size reduction (AeroBlast);
  - raw nitrile and polyisoprene latex production (U.S. Medical Glove);
  - woven fiberglass roving (ValuTex);
  - nanotube growth (NAWAH);
  - inorganic pigment and ceramic stain manufacture (Mason Color Works);
  - headliner forming (Kasai);
  - phenol, acetone and AMS production (ALTIVIA);
  - R&D and testing services (PTI);
  - ABS compounding with the type unstated (Techno-UMG).
- **Materials with no term:** TPO (it exists only in `CAP_MATERIAL`; flagged at Wurms and Electro-General), woven fiberglass reinforcement, carbon nanotube nanomaterials, and an unnamed "photodegradable polymer".
- **Markets with no term:** law enforcement armor, forestry and reforestation, corrugated packaging converters, the Mauser "Small Packaging" segment, and ceramics.
- **Certifications with no term:** SQF (Earthfirst, 2450 Marilyn Ln).
- **Judgement calls on existing terms:**
  - `specialty_elastomers` used for butyl (Guardian, Edge Adhesives) and polyisoprene (U.S. Medical Glove).
  - `markets_served` "medical" without "device" mapped to `medical_healthcare_general`.
  - "Vehicle manufacturers" mapped to `automotive_oem` (Autoneum, org scope).
  - Mauser's "Industrial Packaging" segment label mapped to `packaging_industrial` (Gahanna).

## Hygiene findings (not resolved, for the integrator)

**Rows that are HQs, offices, or probably not polymer plants (scope questions for the owner):**
1. **SITE-001105 Plaskolite.** The row is the 400 W Nationwide Blvd HQ suite; no plant page was found.
2. **SITE-001240 Techno-UMG.** Blue Ash is an HQ office suite (Suite 120); its Ohio compounding facility has no street.
3. **SITE-001153 Rage.** The Locations page labels Hilliard (3949 Lyman Dr) "CORPORATE OFFICE". Lewis Center (8250 Green Meadows Dr N) is a separate Ohio facility; the lane did not check whether it is held.
4. **SITE-000988 Kenda.** Reynoldsburg is American Kenda Rubber / Americana Tire (distribution); the manufacturing is overseas.
5. **SITE-000927 GLS.** The org website is Composites One, a distributor, with no GLS or manufacturing text.
6. **SITE-001217 Starwin.** A 5-axis machining shop for military aircraft, with "advanced composites" the only polymer tie.
7. **SITE-000945 ALTIVIA Haverhill.** A phenol, acetone and AMS complex; commodity chemicals rather than polymer processing.
8. **SITE-001019 Mason Color Works.** Inorganic pigments and ceramic stains; the plastics-pigment line is real but secondary.
9. **SITE-001769 Nationwide Concrete Restoration.** A floor installer that also makes its own epoxy.
10. **SITE-002061 Fouty & Co.** A waterjet job shop; the site was unreachable.

**Plants not tied to the row:**
11. **SITE-000728 Earthfirst (Columbus).** The Blown Film Facility at 2450 Marilyn Ln holds the blown-film activity and the SQF certification and the lane did not check whether it is held. The held row (2400 Marilyn Ln) is the Tentor/cast film facility and holds ISO 9001:2015.
12. **SITE-001580 U.S. Medical Glove.** Fetched pages name the Harvard IL campus and a new "Ohio MSA Manufacturing Hub" / "Cincinnati facility", never Chillicothe. Check whether a Cincinnati-area Ohio site is unheld.
13. **SITE-000835 Wurms.** The Contact page lists Plastics Operations - JC at 18163 Snider Rd, Jackson Center, so the row is tied; the wood and upholstery plants are in New Washington, OH.
14. **SITE-001009 Kasai.** The Ohio ISO 14001 and IATF certificates linked on the awards page are expired.
15. **SITE-000903 Fiber-Tech and SITE-002023 ValuTex.** There are two Fiber-Tech Washington Court House plants (2000 and 2351 Kenskill Ave) with no activity split; ValuTex (2302 Kenskill) is a Fiber-Tech sister.

**Identity, redirects and websites:**
16. **SITE-000747 AZEK.** The org website azekco.com now redirects to James Hardie (acquisition), so the parent of record needs a check.
17. **SITE-000761 Venture Packaging.** The org website is Amcor global; the row name is Venture Packaging.
18. **SITE-000916 Fowler.** The company's pages are served on `foxvalleypain.net`, not a Fowler domain.
19. **SITE-001277 Valfilm.** The org website is the Portuguese-language Valgroup (Brazil) site, with no Findlay text.
20. **SITE-001812 Miami Valley Plastics.** The About page also says "New Paris, Ohio" next to the Eldorado address.
21. **SITE-001726 BCM Inks.** The row is named Blue Ash but the company's only printed address is 161 Commerce Blvd, Loveland. The existing site notes already record the move.
22. **SITE-000775 Mauser Monroe.** The row is named BWAY Corporation and the page gives only a "Small Packaging" label, so plastic versus steel is unsettled.

**Field-level problems:**
23. **SITE-000717 American Colors.** The existing `processes` value `pigment_dispersion` is off-vocab; the in-vocab term is `pigment_colorant_dispersion`.
24. **SITE-001250 Thermodyn.** The About page says it also distributes Chesterton products, so rubber-roll catalog items may be resold; its values stay STILL_UNCERTAIN.

**Unreachable (availability only, not evidence):** ISO Technologies, Nagase ChemteX, Nifco, Pac, Syensqo/Solvay Marietta, Parker (Parker Lord Dayton), Delaware Paint, Kardol, Performance Additives, Fouty (see Fetches).

## Per-site outcome

The per-site verdict and the settling or deciding fact for every site is in `verdicts.csv`. The 37 VERIFIED sites:

- 000717 American Colors
- 000728 Earthfirst
- 000799 Coexcell
- 000813 Convertapax
- 000835 Wurms
- 000858 DimcoGray
- 000882 Electro-General
- 000916 Fowler
- 000936 Guardian
- 000966 Integris
- 001009 Kasai
- 001019 Mason
- 001033 Midwest Molding
- 001044 Moore
- 001077 Ohio Valley Gasket
- 001115 PTI
- 001129 SIMONA PMC
- 001137 ProVia
- 001164 RheTech
- 001176 Robin Holmco
- 001187 Edge Adhesives
- 001208 Toppan
- 001217 Starwin
- 001264 RPUI
- 001288 Vinyl Design
- 001459 Electra Form
- 001635 Kreate
- 001697 AeroBlast
- 001726 BCM
- 001769 Nationwide Concrete
- 001812 Miami Valley Plastics
- 001830 Licensed Specialty Products
- 001879 Hamilton Custom Molding
- 002023 ValuTex
- 002086 Mauser Gahanna
- 002133 PureCycle
- 003704 Rural Path
