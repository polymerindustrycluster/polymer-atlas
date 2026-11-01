# Lane 3 report — PIC-12 capability wave, tranche 1 (2026-11-01)

This is a packet, not a data change. Evidence IDs are allocated at integration.

The lane wrote `packet.csv` (166 rows) and `verdicts.csv` (30 rows). Its tool
refused report files, so the orchestrating session saved this report from the
lane's hand-back.

- **Pin:** `665e5c5`.
- **Quotes and values:** quotes are ≤ 25 words, each checked by script as a
  whitespace-normalised substring of the fetched text. Values were checked
  against `docs/schema/vocab.json`.
- **Packing:** 20 packet rows pack several values with `;`. The orchestrator
  checked every packed value against the vocabulary and all are allowed. The
  integrator should split them to one row per value.

## Verdicts (unit: assigned Ohio site rows, n = 30)

VERIFIED 15 · STILL_UNCERTAIN 15 · REJECT 0. The VERIFIED rate is 50%, with a
Wilson 95% interval of about 33–67%.

- **VERIFIED:** SITE-000139, 000196, 000224, 000330, 000411, 000473, 000556,
  000622, 000657, 001390, 001655, 001741, 001798, 001861, 001931.
  - 14 of the 15 rest on the single-location rule.
  - SITE-001931 rests on a named plant.
- **STILL_UNCERTAIN, org-scope or off-vocab values only:** SITE-000010, 000051,
  000082, 000253, 000285, 000367, 000442, 000522, 000588, 001529, 003406.
- **STILL_UNCERTAIN, availability failures:** SITE-000116, 001432, 001703,
  002041. None is evidence of closure.

## In-vocab values proposed (unit: record × field × value)

| field | site scope | org scope | total |
|---|---:|---:|---:|
| processes | 36 | 10 | 46 |
| materials | 54 | 18 | 72 |
| markets_served | 33 | 14 | 47 |
| certifications | 8 | 3 | 11 |
| **all** | **131** | **45** | **176** |

Another 28 rows are off-vocab (`*_other_note`): markets 15, processes 7,
certifications 4, materials 2.

**Yield:**
- **Site-scope values:** 4.1 per sampled site, against the pilot's 2.6, and 8.2
  per VERIFIED site. All scopes together: 5.9 per site.
- **Markets:** present at 11 of 30 sites at site scope, and 17 of 30 counting org
  scope. The baseline for these rows was 0 of 30.
- **Blank fields filled at site scope:**
  - processes: 11 of 25 blank sites;
  - materials: 12 of 25;
  - markets: 11 of 30.

## Fetches

113 attempts: 109 by curl, 4 by WebFetch. That is 3.8 per site, with the cap of
6 respected.

- **Hard failures: 12 of 113 (10.6%).**
  - ModSecurity 406 blocks (noramcobag.com);
  - a TLS name mismatch (premier-oem.com apex; the www host recovered);
  - Cloudflare 403 blocks (lubrizol.com, wayne-dalton.com);
  - Cloudflare 502 errors (smetzertire.com; recovered on retry);
  - a captcha (akrondispersions.com).
- **Counting content-free responses too:** 18 of 113 (15.9%).
- **No bot-wall workarounds.**
- **Cost:** 7.5 fetches per VERIFIED site all-in, 4.0 per site for the VERIFIED
  sites alone.

## Vocabulary gaps (flagged, not settled)

**Markets:**
- **Automotive** with no OEM or aftermarket split: 7 sites.
- **Markets with no term:**
  - powersports, trailers and RVs;
  - chemical and mineral processing, mining and steel;
  - paper and pulp;
  - material handling;
  - food and beverage outside packaging;
  - telecom;
  - law enforcement;
  - cannabis;
  - plumbing, HVAC and hardware;
  - EV charging.
- **Stretch mappings, flagged** (the integrator may drop them):
  - hydropower → `energy_renewables_battery`
  - drinking-water components → `water_wastewater`
  - outdoor recreation → `lawn_garden_recreation`
  - clothing → `footwear_apparel`
  - cannabis bags → `packaging_consumer`

**Processes with no term:**
- PSA tape manufacture;
- fluoropolymer lining and rotolining;
- FRP dual-laminate fabrication;
- wound resin-impregnated tube stock;
- brush making;
- metal stamping;
- flexible bag converting.

**Materials with no term:** aramid and LCP fibers, mineral fillers, CPVC,
polyester fiber.

**Certifications:**
- ISO/IEC 17025 is listed on a page but has no vocabulary term.
- GREENGUARD and NSF/ANSI 61 are product certifications, not facility ones.
- ITAR is a registration, not a certificate.
- Not recorded, because no certificate was shown: ISO 9001 "compliance", CMMC
  "in progress", "ISO 9000/2000", and an NSF claim.

## Hygiene findings (not resolved — for the integrator)

**Wrong or conflicting addresses:**
1. **SITE-001798:** `zip` holds `26201`, which is the street number. The company
   prints 44146.
2. **SITE-000657 Tribotech:** the company's own address is 9217 Midwest Ave,
   Cleveland 44125. The Atlas row is 7800 Exchange St, Valley View. Confirm it is
   the same establishment before applying the site-scope values.
3. **SITE-000253 / ORG-000238 Avery Dennison:** for North America the Performance
   Tapes site gives only 250 Chester St, Painesville, not the Mentor row. The org's
   `hq_city` of Mentor is not supported.
4. **SITE-000139 FedPro:** the company prints "Cleveland 44128" for an address the
   Atlas places in Warrensville Heights. This is a mailing-city case; the county
   is the same.
5. **SITE-000330 Drummond:** "Berkshire Parkway" vs "Berkshire Industrial Park".

**Ownership and parent of record:**
6. **ORG-000051 Continental ContiTech:** the sale of ContiTech to Lone Star Funds
   was announced on 2026-07-04, subject to approval. This is a parent watch item,
   not a status change.
7. **ORG-000385 / SITE-000411 Iten Defense:** the company's own about page says it
   became part of NP Aerospace in Sept 2026. Re-check the parent of record (it is
   currently ORG-000386).
8. **ORG-000487 / SITE-000522 PFC:** the company's own site gives HQ as
   Woodbridge, CT, with Massillon as an additional plant. Check the HQ fields and
   the shard placement.
9. **ORG-000344 / SITE-000367 Fomo:** the site is the HandiFoam brand of ICP
   Building Solutions Group. Check the parent of record.

**Office rows carrying a plant ring, or the wrong address:**
10. **SITE-000442 / ORG-000413 Knight Material Technologies** (legacy name Koch
    Knight). East Canton is the corporate office, yet the row is a ring 2
    manufacturing plant.
11. **SITE-000285 CG Thermal:** the row holds the HQ address. A Production Center
    at 8950 Dutton Dr, Twinsburg may be the real plant. There is also a scope
    question, since graphite heat exchangers are the core business.
12. **SITE-003406 Covia and SITE-000051:** both are `hq_only` rows carrying a
    plant ring.
13. **SITE-001529 / ORG-000006 (RPM):** the Miles Ave plant is not named on any
    page fetched. The Tremco CPG HQ is 3735 Green Rd, Beachwood.

**Field-level problems:**
14. **SITE-000224:** carries existing values that aren't in the vocabulary:
    `large_format_additive_manufacturing`, `tooling_mold_die`.
15. **SITE-001390:** the site says both 18 and 19 presses.
16. **SITE-000556 Premier OEM:** the apex host fails TLS, so the website field
    needs `www`.
17. **SITE-001741 Dischem:** the home page is an unedited template. Only the
    products page is real content.

**Scope questions (owner):**
18. **SITE-001931 Smetzer's:** a retail tire dealer that runs a retread center.
19. **SITE-000622 Spiral Brushes:** a wire brush maker.
20. **SITE-001861 Beacon Gasket:** a distributor that cuts gaskets.
21. **SITE-000196 GBSA:** whether molding is in-house or sourced is not stated, so
    its process rows are lower confidence.

**Street addresses:** 28 of the 30 assigned rows have `street_address` blank and
the street only in `notes`.
