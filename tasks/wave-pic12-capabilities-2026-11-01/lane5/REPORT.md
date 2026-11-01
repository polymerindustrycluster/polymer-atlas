# Lane 5 report — PIC-12 capability wave, tranche 1 (2026-11-01)

This is a packet, not a data change; evidence IDs are allocated at integration.
The lane wrote `packet.csv` (192 rows) and `verdicts.csv` (30 rows). The lane's
tool refused report files, so the orchestrating session saved this report from
the lane's hand-back.

## Run facts

- **Pin:** `665e5c5`.
- **Sources:** own-site pages only, fetched with curl. One WebFetch fallback
  returned 403 and supplied no quote.
- **Quote check:** every quote is ≤ 25 words and was checked by script as a
  whitespace-normalised substring of the saved page text. PDF pages were checked
  via `pdftotext`.
- **No bot-wall workarounds** and no disabled TLS verification.

**Caveats on specific sources:**
- **Plastipak:** the locations quotes come from JSON embedded in the page,
  decoded to text, so they are not visible-page text.
- **energyene.com:** read over plain http after its https certificate chain
  failed. Treat those quotes as less authoritative.
- **Scratch-directory collision:** lane 5 and lane 4 shared a scratch directory
  for part of the run. Lane 5 moved its fetched pages back into its own
  directory, and no lane's site assignments were affected.

## Counts

**Verdicts (unit: assigned Ohio site rows, n = 30):** VERIFIED 11 ·
STILL_UNCERTAIN 19 · REJECT 0.

VERIFIED: SITE-000025, 000065, 000101, 000179, 000208, 000238, 000271, 000603,
000673, 001717, 001888.

**In-vocab values proposed (unit: packet rows):** 169.

| field | site scope | org scope | total |
|---|---:|---:|---:|
| processes | 19 | 24 | 43 |
| materials | 43 | 37 | 80 |
| markets_served | 15 | 26 | 41 |
| certifications | 1 | 4 | 5 |
| **all** | **78** | **91** | **169** |

Another 23 rows are off-vocab (`*_other_note`): processes 9, markets 12,
certifications 2. The two certification rows are explicit NOT-RECORDED rows:
SITE-000208, whose certificate has expired, and SITE-000490, which says
"ISO-certified" with no standard named.

**Yield:**
- **Site-scope values:** 2.6 per assigned site, 7.0 per VERIFIED site.
- **All scopes:** 5.6 in-vocab values per site.
- **Markets:** present at 6 of 30 sites at site scope, and 18 of 30 counting org
  scope.
- **Org scope only:** 14 sites.

## Fetches

106 attempts, 3.5 per site; the most for any one site was 6.

- **Availability failures: 14 of 106 (13.2%).**
  - 403 blocks: Polycase, Tarkett.
  - TLS name or chain errors: prime-plastics.com, energyene.com.
  - DNS failure: www.o2regentech.com.
  - One timeout.
  - Three content-free responses.
- **Not counted as availability failures:** 3 guessed-URL misses.
- **No usable content at all (5 sites):** SITE-000343 Polycase, 001468 Elster,
  001545 O2 RegenTech, 001774 Prime, 003477 Johnsonite.
- **Unavailable is not closed.** None of these failures is closure evidence. All
  five are STILL_UNCERTAIN with a named settling fact.

## Scope rule

The 14 sites at org scope only, with the reason:
- **Cosmo:** four facilities.
- **Godfrey & Wing:** no page says Aurora makes sealant.
- **Jerico:** Wadsworth is the corporate office.
- **M&M:** plants in TN, AZ and OH.
- **Neff-Perkins:** the site says "headquarters".
- **Plastipak:** dozens of plants.
- **Qnity/Laird:** about 40 centers.
- **System Seals:** multi-center.
- **Steere:** its own site never names 350 Tacoma Ave.
- **MultiPlast:** described as a "value-added supplier".
- **Niles Building Products:** four plants.
- **RAM:** no address printed on the site.
- **EnergyEne:** aspirational wording.
- **Playground Plastics:** a Wix landing page for an `hq_only` row.

## Vocabulary gaps (flagged, not settled)

- **Automotive** with no OEM or aftermarket split: 9 sites. Godfrey & Wing alone
  maps to `automotive_oem`, because its page says "OEM".
- **Markets with no term:** aerial-lift / utility fleet, RV, flexographic
  printing, fuel cells, industrial batteries, flow control, healthcare,
  tires.
- **Processes with no term:** potting / encapsulation / casting,
  low-pressure overmolding, resin dry-blending, additive-masterbatch supply,
  tube winding / vulcanized fiber, fiberglass spray-up, guayule extraction,
  rubber molding with the type unspecified.
- **Materials with no term:** HNBR, FFKM, CSM/Hypalon, butyl, polyacrylate,
  epichlorohydrin, fluorosilicone, millable urethane, vulcanized fiber.
- **Judgment mappings, flagged in notes:**
  - "medical" → `medical_device`;
  - Sport/Recreational → `lawn_garden_recreation`;
  - UHMWPE → `polyethylene_pe`;
  - TPV → `thermoplastic_elastomers_tpe_tpu`;
  - Plastipak "Extrusion Molding" → `blow_molding_extrusion`.

## Hygiene findings (not resolved — for the integrator)

**Acquisitions and ownership:**
- **SITE-000208 / ORG-000201 Ashtabula Rubber.** The domain redirects to ASC
  Engineered Solutions ("now part of"). The ISO 9001 certificate expired
  2026-09-28. The certificate also lists **5013 Benefit Ave, Ashtabula**
  (injection molding and warehousing), which may be an unheld site.
- **SITE-003477 / ORG-001836 Johnsonite.** The domain redirects to Tarkett, and
  Tarkett's pages return 403.

**Wrong or unconfirmed addresses:**
- **SITE-000634 / ORG-000595 System Seals.** The company's own main office is
  9505 Midwest Ave, Cleveland 44125. The Atlas row is Brecksville (from EPA FRS),
  which the site never mentions.
- **SITE-001671 / ORG-001599 MultiPlast.** The company gives 5900 Harper Rd
  Suite 109, Solon; the Atlas has 33355 Station St Ste C. It may be a distributor,
  which is a scope question.
- **SITE-001417 / ORG-000588 Steere.** The 350 Tacoma Ave row is never named on
  the company's site.
- **SITE-001992 / ORG-001998 RAM.** No address appears on the company's site, so
  the North Lima address rests on directory data.

**Rows typed or ringed as the wrong kind of site:**
- **SITE-000423 / ORG-000909 Jerico.** Carried as a ring 1 manufacturing plant,
  but it is the company's corporate office. Its plants are in Minerva OH and
  Greensboro GA.
- **SITE-000532 Plastipak Medina.** Listed as both a development center and a
  manufacturing site.

**Websites:**
- **SITE-001468 / ORG-001422 Elster Perfection.** The org website is a Honeywell
  ordering portal with no Perfection content.
- **SITE-001545 / ORG-001479 O2 RegenTech.** The domain is parked. That is not
  closure evidence; the Form 5500 check comes first.
- **SITE-001774 Prime Engineered Plastics.** TLS and hosting misconfiguration;
  the site is unreachable.
- **SITE-002073 EnergyEne.** Copyright 2015, an "Australia" page title, and a
  production claim that is not settled.

**Certifications:**
- **SITE-000309 Cosmo.** One page says ISO 9001:2015 and another says 2008. The
  conflict is flagged. Which of its facilities is the Solon plant is unsettled.

**Scope and polymer-relevance questions (owner):**
- **SITE-000379 Godfrey & Wing.** The business is mainly impregnation equipment.
- **SITE-001888 NewKor.** Mostly paper and fiber tubing.
- **SITE-000128 Playground Plastics.**

**Possibly unheld sites:**
- **SITE-000101 Polymerics.** The company also lists a Kent location (1540 St.
  Clair Ave). Check whether it is held.

**Route needed:**
- **SITE-000343 Polycase.** Behind a Cloudflare challenge; capabilities need a
  human browser.
