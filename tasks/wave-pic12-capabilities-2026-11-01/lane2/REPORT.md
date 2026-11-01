# Lane 2 report — PIC-12 capability wave, tranche 1 (2026-11-01)

This is a packet, not a data change. Evidence IDs are allocated at integration,
and no `tier_effect` is proposed.

The lane wrote `packet.csv` (241 rows) and `verdicts.csv` (30 rows). Its tool
refused report files, so the orchestrating session saved this report from the
lane's hand-back.

- **Pin:** `665e5c5`. The Ohio shards were unchanged at hand-back (`76dc218`).
- **Sources:** every row is `own_site` and carries a URL and a quote of ≤ 25
  words. All quotes were checked by script as substrings of the saved page text.
  WebFetch was used three times as a second route and never quoted.

## Counts (unit: the 30 assigned Ohio site rows)

VERIFIED 16 · STILL_UNCERTAIN 14 · REJECT 0, so the VERIFIED rate is 53%.

| field | site | org | total |
|---|---:|---:|---:|
| processes | 21 | 36 | 57 |
| materials | 30 | 47 | 77 |
| markets_served | 21 | 33 | 54 |
| certifications | 9 | 10 | 19 |
| **all** | **81** | **126** | **207** |

Another 34 rows are off-vocab (`*_other_note`).

**Yield:**
- **Site-scope values:** 2.4 per sampled site, 4.5 per VERIFIED site. All
  scopes together: 6.9 per site.
- **Markets:** present at 9 of 30 sites at site scope, and 20 of 30 counting org
  scope. The baseline was 0 of 30.
- **Coverage:** 27 of 30 sites yielded at least one in-vocab value.

**Org scope only (12 sites, nothing pushed down), with the reason:**
- **Vibrantz:** 20+ plants.
- **Mantaline:** this row is a warehouse location.
- **Roto Polymers:** facilities in five countries.
- **Synthomer:** global group.
- **ORBIS:** about 16 plants.
- **Foundation Wellness:** HQ, a distribution center and a Vietnam site.
- **Treemen:** two buildings.
- **SOPREMA:** six US sites, none labelled as a plant.
- **Zehrco-Giancola:** nine facilities.
- **Axion:** no address given.
- **Action SuperAbrasive:** Kent plus a Swiss HQ.
- **Hy-Ko:** eight facilities.

**Site scope earned from certificates or plant-named pages:**
- **SITE-002092 Kongsberg:** SGS ISO 9001 / IATF certificates name 301 Olive St.
- **SITE-001316 Shin-Etsu:** the ISO 14001 scope names 963 Evans Ave.
- **SITE-000361 Flambeau:** a Middlefield plant page.

## Fetches

122 attempts (119 curl, 3 WebFetch), 4.1 per site, with the cap of 6 enforced in
code.

- **Hard failures: 7 of 122 (5.7%).**
  - a self-signed certificate (splastics.com);
  - an expired certificate (castnylon.com);
  - a transient HTTP 500.
- **Content-free responses:** 3 more.
- **No usable content at all (2 sites):** SITE-000040 Spectrum Plastics and
  SITE-000281 Cast Nylons. Both are certificate problems on the company's side.
  They are availability failures, not closure evidence, and the lane did not try
  to route around them.
- **No bot walls were met.**
- **Cost:** 7.6 fetches per VERIFIED site all-in.

## Vocabulary gaps (flagged, not settled)

- **Automotive** with no OEM or aftermarket split: 8 sites.
- **Markets with no term:** lighting; hardware retail channel; the rotomolding
  industry as a customer; industrial automation; off-road tire and track repair.
- **Processes with no term:**
  - pigment and colorant dispersion;
  - vacuum metallization / PVD;
  - metal machining and stamping;
  - thermoforming with the type unstated.
- **Materials with no term:**
  - ASA, butyl, PPS, PEI, PMMA, PBT, PAR;
  - TPV and TPO as separate terms;
  - SBS-modified bitumen;
  - polyester and vinyl ester resins;
  - DAP, DCPD;
  - solid-surface acrylic.
- **Certifications:**
  - ISO 45001 and the RCMS Statement of Conformity have no vocabulary term.
  - "ISO certified since 1999" with no standard named is not recorded.
- **Existing row value outside the vocabulary:** SITE-001511 carries
  `compounding`.

## Hygiene findings (not resolved — for the integrator)

**Row type, ring or scope:**
- **SITE-000077 Mantaline (Twinsburg).** The company's own IATF certificate lists
  this address as a supporting location for "Distribution, Warehousing" only. The
  row is a ring 1 plant with `rubber_extrusion`. Manufacturing is at Mantua,
  which is SITE-003471, plus Hiram (unheld) and San Antonio.
- **SITE-000403 Infinity Composites.** An online supply store; no manufacturing
  is stated.
- **SITE-001921 GlueTread.** The formula is made with a contract adhesive
  manufacturer.
- **Scope or polymer-relevance questions (owner):**
  - **SITE-001851 Action SuperAbrasive:** grinding wheels with resin bonds.
  - **SITE-001791 Axion:** mainly a metal CNC shop. Its website is stored with no
    scheme.
  - **SITE-000111 Trico:** plastic is one of three materials machined.
  - **SITE-001649 Bright Idea:** also resells goods.
  - **SITE-002028 Whip Guide:** no page says who molds the product.
- **SITE-000546 PolyStamp.** A Florida area code, and no page says production is
  in Youngstown.
- **SITE-000136 Roto Polymers.** `pulverizing_grinding_resin` is not stated on
  any page, and the address appears only in Wix metadata.
- **SITE-000322 Desenco.** The site is stale: copyright 2003–2004, newest dated
  item 2013.

**Ohio establishments listed on companies' own sites with no Atlas site row** (no
create proposed):
- **ORG-000611 Treemen:** 100 Eastgate Industrial Dr, North Lima 44452.
- **ORG-000077 Mantaline:** 6969 Constance Dr, Hiram 44234.
- **ORG-000007 Vibrantz:** 4150 East 56th St, Cleveland 44105.
- **ORG-000050 Synthomer:** Beachwood (address not read).

**Parent or ownership:**
- **ORG-001388 Hy-Ko.** The company's own press release of 2020-07-21 says
  Midwest Fastener acquired it. The Atlas has no parent.
- **ORG-000576 Soft-Lite.** Its own page says it is "a business of Harvey
  Building Products Corporation". The Atlas has no parent.

**Other:**
- **SITE-001316 Shin-Etsu.** The ISO 14001 scope covers three Atlas rows (963
  and 1030 Evans Ave, 1150 Damar Dr). The lane did not split values across them.
- **SITE-000361 Flambeau.** ISO 13485 and IATF stay at org scope.
- **Unconfirmed, not recorded:** Kongsberg's ISO 14001 (the PDF is unreadable).
- **Not recorded as facility certifications:** product claims such as "FDA
  compliant" and "UL-listed".
- **Mechanical VERIFIED verdicts with flags:** SITE-000403, SITE-001921,
  SITE-000322.
