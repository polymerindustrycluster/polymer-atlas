# Lane 1 report — PIC-12 capability wave, tranche 1 (2026-11-01)

This is a packet, not a data change. Evidence IDs are allocated when the
integrator applies it.

- **Files:** the lane wrote `packet.csv` (158 rows, all source_class `own_site`)
  and `verdicts.csv` (30 rows). The lane's tool refused report files, so the
  orchestrating session saved this report from the lane's hand-back.
- **Checks:** a script confirmed every quote is a substring of the curl-fetched
  page text, and every value is in `docs/schema/vocab.json`. No failures. No
  quote comes from WebFetch or WebSearch.
- **Pin:** `665e5c5`. `data/sites_OH.csv` and `data/organizations_OH.csv` were
  unchanged at hand-back (`bd9ac8e`).

## 1. Verdicts (unit: assigned Ohio site rows, n = 30)

VERIFIED 11 · STILL_UNCERTAIN 19 · REJECT 0.

**VERIFIED** (at least one in-vocab process, material or market value at site
scope; certifications alone don't count): SITE-000184, 000244, 000276, 000318,
000353, 000574, 000683, 001421, 001484, 001632, 001721.

**STILL_UNCERTAIN, by cause.** The settling fact for each is in `verdicts.csv`.
- **Own site unreachable (9):** 000002, 000070, 000106, 000212, 000393, 000427,
  001675, 001779, 002004.
- **Org website is a third-party directory (1):** 000036.
- **Multi-plant; nothing ties a capability to this plant, so org scope only
  (8):** 000132, 000461, 000501, 000540, 000610, 000646, 001840, 002083.
- **No in-vocab value stated (1):** 001899.

There is no REJECT. No dated page gave a deciding fact, and no failed fetch is
treated as evidence of closure.

## 2. In-vocab values proposed (unit: packet rows, one per record × field × value)

| field | site scope | org scope | total |
|---|---:|---:|---:|
| processes | 15 | 22 | 37 |
| materials | 39 | 18 | 57 |
| markets_served | 15 | 30 | 45 |
| certifications | 2 | 1 | 3 |
| **all** | **71** | **71** | **142** |

Another 17 rows are off-vocab (`*_other_note`, marked OFF-VOCAB / NOT MAPPED):
processes 5, markets 10, certifications 1. That makes 158 rows in all.

**Mapping judgments.** Each is flagged in that row's notes for the integrator:
- polyester strapping → `pet_petg`
- EPS → `foam_molding_bead` / `polystyrene_ps_hips`
- TPER/TPV → TPE/TPU
- vinyl window assembly → `assembly_secondary_ops`
- wire insulation → `extrusion_wire_cable_coating`
- cement/adhesive manufacture → `adhesive_sealant_formulation`
- water filtration → `water_wastewater`
- SMC/BMC molding → `composites_compression_smc_bmc`

**Yield:**
- **Per site:** 69 site-scope capability values (processes, materials, markets)
  over 30 sites is 2.3 per site, or 6.3 per VERIFIED site. Counting every
  in-vocab value at either scope, it is 4.7 per site.
- **Markets:** present at site scope at 6 of 30 sites (20%), and at 14 of 30
  (47%) counting org scope.
- **VERIFIED rate:** 11 of 30 (37%), below the pilot's 48%, mainly because of the
  9 unreachable sites.
- **Concentration:** three sites that publish a resin or elastomer table
  (000184, 000574, 001632) supply 40 of the 69 site-scope values.

## 3. Fetch-failure rate

The lane made 92 per-site deduplicated fetches over 30 sites, 3.1 per site.
The most for any one site was 6, so the per-site cap held.

- **Unusable responses: 21 of 92 (22.8%).** That is 19 hard failures plus 2
  pages that returned 200 with no content.
- **Hard failures:**
  - Cloudflare or WAF 403 blocks (Lubrizol, Tarkett for Johnsonite, Speedline);
  - TLS handshake or certificate-name failures (Plastic Materials, Premier
    Aerosol);
  - a proxy CONNECT 502 (HEXPOL);
  - a GoDaddy for-sale page (Sherwood);
  - WebFetch 503s.
- **The lane's own errors** (guessed URLs that 404'd or redirected): 5 of 92.
- **No usable own-company content:** 9 of 30 sites, plus 000036, which loads but
  is a directory.
- **No bot wall was bypassed:** no spoofed user agent and no TLS bypass.
- **Leads only:** two WebSearch lookups (Win Plastic, Sherwood) were used as
  leads, never as evidence.

## 4. Vocabulary gaps (owner rulings; flagged in `*_other_note` rows, not settled)

**Markets:**
- "Automotive" with no OEM or aftermarket split: 000184, 000132, 000610, 001632,
  and PPG "Automotive Refinish".
- Foodservice and food processing, which are not packaging: 000353, 000184.
- "Medical" without "device": 000184, 000683, 001632.
- Power, utility and communications conduit: 000276.
- Generic "Packaging": 000610, 001632, 000646.
- No market term for nuclear, semiconductor, HVAC, data center, valve/flow, or
  promotional inflatables.

**Processes with no term:**
- pressure-sensitive tape manufacture (000610);
- PTFE-coated fabric fabrication (000353);
- rPET resin production with the method unstated (000540);
- fabric inflatable fabrication (001899);
- molded rubber with the method unstated (000184);
- aerosol filling (001779).

**Certifications not in the vocabulary:** AIB International, SFI (000646).

## 5. Hygiene findings (not resolved — for the integrator)

**Website and scope problems:**
- **SITE-000036 / ORG-000036 (Win Plastic).** The org `website` is a directory
  (extrudedplastics.com). Search leads put the plant in Cuyahoga Falls (the Atlas
  says Akron), and a trade-press headline reports a closure. Closure still needs a
  dated primary page plus the Form 5500 check. Recommend re-verification.
- **SITE-002004 / ORG-002010 (Sherwood).** The domain is parked (GoDaddy
  for-sale). That is not closure evidence; the Form 5500 check comes first.
- **SITE-000106 / ORG-000107.** The own domain is an "under construction"
  placeholder.
- **SITE-000646 / ORG-000606.** Green Bay Packaging acquired Third Dimension in
  2020, and the org `website` is now the acquirer's domain. The division reports
  six Ohio facilities, but only Geneva is held. It is mainly a corrugated and
  display business, which is a scope flag.
- **SITE-000427 / ORG-000131.** Johnsonite is a Tarkett brand, and Tarkett's site
  returns 403 (route blocked).

**Possible duplicate or unheld sites:**
- **SITE-000683 and SITE-001725 (Zehrco-Giancola, Ashtabula, ORG-000640).** Two
  active plant rows in one city carry different rings (2 vs 1), while the
  company's site lists one Ohio address. Possible duplicate.
- **SITE-001840 vs SITE-000114 (ORG-000115).** The own site names only 1265
  Babbitt Rd (Euclid). The Mentor row's notes cite that site even though it never
  names Mentor.
- **SITE-000540 / ORG-000506.** The company's contact page also lists Green
  (Summit County) and Clyde, and neither appears to be held.
- **SITE-000461 / ORG-000430 (Mar-Bal).** The facilities page doesn't list
  Willoughby, where the Atlas holds SITE-003472. "UL recognized" on the site is a
  product claim, not a facility certification.

**Rows whose plant or role is unclear:**
- **SITE-001484 / ORG-001436.** The org `website` is the distributor parent; the
  plant evidence is on polariswindows.com.
- **SITE-000610 / ORG-000571 (Shurtape).** It isn't clear whether the Avon
  address is a plant or an office.
- **SITE-000501 / ORG-000469.** A promotional-products storefront. Plant versus
  reseller is open.
- **SITE-000353 / ORG-000332 (Essentialware) and SITE-001899 / ORG-001891
  (Inflatable Images).** Scope questions for the owner.
- **SITE-002083 / ORG-000088.** The parent sits in the PA shard. PPG's pages name
  no Euclid facility.

**Field-level problems:**
- Off-vocab values already on rows: `coatings_formulation` (SITE-001421,
  ORG-001382; the vocab spelling is `coating_formulation`) and
  `vinyl_window_manufacturing` (SITE-001484).
- Several rows keep the street address in `notes` with `street_address` blank:
  000036, 000106, 000132, 000184, 000212, 000427, 000461.

## 6. Scope rule

Org scope only, never pushed down to a site, for 8 multi-plant sites. Site scope
was used only where a page names the plant, or where the company lists a single
address. The basis is quoted in each row's notes.
