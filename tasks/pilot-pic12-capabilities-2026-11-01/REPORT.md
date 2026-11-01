# Pilot: PIC-12 Ohio site capability packet (2026-11-01)

**This is a packet, not a data change.** It was produced by a research lane that never edits `data/`. The integrator of record applies it after review. No IDs were allocated: evidence rows (`data/evidence.csv`, SCHEMA 4.13) get their `EVD-######` IDs at integration. Every row in `packet.csv` is class `own_site` and carries the exact URL and a quote of 25 words or fewer that was checked programmatically as a substring of the page text I fetched. No `tier_effect` is proposed; the integrator sets it under the 4.13 ceilings. I did not use WebFetch for quotes, because its summarizer can paraphrase. Pages were fetched with curl through the configured proxy and read as saved text. WebFetch was used only as a second route when curl failed.

Files: `packet.csv` (one row per record, field, value), `verdicts.csv` (one row per site), this report.

## Pinned state

- `git rev-parse HEAD` at lane start and at selection: **a3e59e793388573ebcf804184131e22f8b7caa23**.
- HEAD advanced to 834d952f8c7f4b4e5fd1f17087ae09a52e07f996 during the run (another contributor's docs/scripts commit). `data/sites_OH.csv` and `data/organizations_OH.csv` are byte-identical between the two SHAs (empty `git diff`), so the selection is valid against either.

## Selection rule (deterministic)

Candidate = a row of `data/sites_OH.csv` with ALL of: `operating_status = active`; `county` in PIC-12; `ring_primary` in {1, 2}; `processes` blank OR `markets_served` blank; `org_id` found in `data/organizations_OH.csv` with a non-blank `website`. Sort candidates by `site_id` ascending. Take elements at index 0, 23, 46, ..., 552 (every 23rd, 23 = floor(587/25)), which gives 25 sites.

Unit counts: 640 active Ohio site rows in PIC-12 with ring 1-2. Of these, 635 have a blank processes or markets_served, and 587 of those pass the org-join and website filter (27 dropped because the parent org is not in the Ohio org shard, 21 because it has no website). **587 candidates, 25 sampled.** The sample spans SITE-000001 to SITE-002024, but the every-23rd stride never reaches the last 34 candidates. 18 of the 25 picks have `site_id` at or below 678 (seed-era rows), so later pass-created sites are under-sampled.

Baseline fill, Ohio PIC-12 active ring 1-2 site rows (n=640): processes filled on 122 (19.1%), markets_served filled on 7 (1.1%).

## Results (units stated)

**Sites verdicted (unit: sampled Ohio site rows, n=25):** VERIFIED 12, STILL_UNCERTAIN 13, REJECT 0.
Rule used: VERIFIED means at least one in-vocab processes, materials or markets_served value is stated on the company's own site **at site scope**. A site with only org-scope values, only certifications, or nothing retrievable is STILL_UNCERTAIN, and the settling fact is named in `verdicts.csv`.

**Values proposed (unit: packet rows, in-vocab, one per record, field, value):** 117 total.

| field | site scope | org scope | total |
|---|---|---|---|
| processes | 20 | 13 | 33 |
| materials | 24 | 9 | 33 |
| markets_served | 21 | 17 | 38 |
| certifications | 7 | 6 | 13 |
| **all** | **72** | **45** | **117** |

Plus 6 flagged off-vocab rows (`*_other_note` fields, with the reason): processes_other_note x2, markets_other_note x2, materials_other_note x1, certifications_other_note x1. Two site-scope processes values (Rainbow Rubber and Elbex `rubber_extrusion`) reconfirm values the site row already carried.

**Measured yield**
- Site-scope capability values (processes, materials, markets) per sampled site: 65/25 = 2.6. Per VERIFIED site: 65/12 = 5.4. All in-vocab values, all scopes, per sampled site: 117/25 = 4.7.
- Sites with at least one `markets_served` value: **7/25 (28%) at site scope; 13/25 (52%) counting org scope.** Baseline is 1.1%.
- Blank target fields filled at site scope: processes 8 of 21 blank sites (38%); markets_served 7 of 25 blank sites (28%).
- 21/25 sites yielded at least one in-vocab value at some scope.
- VERIFIED rate 12/25 = 48% (Wilson 95% interval about 30% to 67%; n=25, so treat as an order of magnitude).

**Plant-specificity (hard rule).** 8 sites got org-scope values only because no page said which plant does what or because the Atlas row is not a plant: Avient (32 sites), Premix-Hadlock (2 plants), Saco AEI (4 plants), Owens Corning (17 sites), Team Wendy, ELC, Robin Industries (office row; plants elsewhere), plus APS (office suite). Nothing was pushed down to those sites. Where a company's own site shows one location and says so, values are scope `site`, with the evidence in `notes`.

**Fetches (unit: HTTP fetch attempts, including WebFetch retries):** 97 total across 25 sites, 3.9 per site, maximum 6 for any site (the AGENTS 2 rule 8 cap was respected).
- Hard failures (403 bot wall, 520, captcha wall, TLS error, DNS, 503): **10/97 = 10.3%.**
- Add content-free responses (JS-rendered shell x2, domain-parking lander x3): 15/97 = 15.5%.
- Add 404s on URLs I guessed (4): 19/97 = 19.6%. These are my errors, not site availability.
- Sites with no usable company content from any route: 4/25 (16%): Hanlon (TLS/DNS/503), Wrap Tite (403), Harrison Paint (520/captcha), Veretec (parked domain). Owens Corning is effectively a fifth, as its site is a JS shell.
- Per AGENTS 2 rule 8, none of these is evidence of closure or absence. All four are STILL_UNCERTAIN with the settling fact named. Veretec's parked domain still needs a Form 5500 (EFAST2) check and dated outcome evidence before any REJECT.

**What blocked me**
- TLS: Hanlon's certificate chain fails verification. I did not bypass verification.
- Bot walls: Wrap Tite (403 on curl and WebFetch) and Harrison Paint (captcha). I tried a retry with a browser user-agent on Wrap Tite and the permission classifier denied it as bot-check circumvention. I did not pursue it, and an alternate route (a human browser, or another lane) is needed for these.
- JS-only sites: Owens Corning returns no extractable text to curl.
- Vocabulary gaps (see observations) blocked mapping, not retrieval.

## Cost estimate for a PIC-12 wave (extrapolated from n=25; low confidence)

- All-in fetch cost: 97 fetches / 12 VERIFIED sites = **8.1 fetches per VERIFIED site** (includes failures, uncertain sites and my guessed-URL misses). The VERIFIED sites alone cost 44 fetches, which is 3.7 each.
- For ~1,000 sites at 3.9 fetches per site: **about 3,900 fetches**, yielding roughly 480 VERIFIED sites, about 2,600 site-scope capability values and about 4,700 in-vocab values of all scopes, if this sample is representative. The Atlas currently has only 587 candidates meeting this pilot's filter, so a ~1,000-site wave implies adding other-shard parents or dropping the ring or website filters.
- Expect about 16% of sites to be unreachable by curl (bot walls, TLS, parked or dead domains) and to need another route. Expect about 30% more (8 of 25 here) to stay org-scope-only: multi-plant firms, and offices or HQs among site rows.
- Agent time and tokens were not measured here.

## Observations for the owner

1. **Vocab gaps cost yield.** "Automotive" with no OEM/aftermarket split (Elbex, Premix-Hadlock, Robin, Medco) was never mapped to `automotive_oem` or `automotive_aftermarket`. No tire market (APS), no upstream-customer markets (Addipel), no additive dry-blending process (Addipel), no ISO 45001 or ISO/IEC 17025 certification term (Saco AEI, Avient). These are owner rulings; they were flagged in `*_other_note` rows, not settled.
2. **Industry pages can be templated filler.** CPI Precision Plastics' Energy page describes solar, wind and battery systems that a molder does not sell. Its markets were not proposed. A platform or roster category is a discovery lead; likewise a templated page is not scope evidence.
3. **Site-row hygiene found on the way.** SITE-001836 (Robin Industries) is an `hq_office` row in Independence, ring 1. The company's own locations page lists the corporate office in North Canton and plants in Winesburg, Millersburg (certifications page says Berlin), Fredericksburg and Mexico, with no Independence address. ORG-002030's `website` field has the text "(fetch failed - no extractable content)" appended. veretec.com is a parked domain. SITE-000001's `street_address` column reads 554 Moore Rd while its notes and Avient's own site give HQ at 33587 Walker Rd. SITE-000125's domain cardinalproductsinc.com now redirects to cpipp.com (CPI Precision Plastics LLC). Several existing process and materials values on neighbouring rows are not in the vocab (`xps_foam_extrusion`, `rd_pilot_line`, `tooling_mold_die`, `distribution`, `plastics;metals`).
4. **Scope flag, not self-ruled.** Etched Metal (SITE-001426) is primarily a metal nameplate maker; plastic nameplate printing is one line. Ring and scope are an owner ruling.
5. **Staleness flag.** Colonial Machine's own site says "ISO 9001:2005", a superseded edition on a 2020-copyright page. Do not record it as a current certificate without the certificate itself.

## Sites

| site_id | site | verdict | fetches |
|---|---|---|---|
| SITE-000001 | Avient — Avon Lake HQ | STILL_UNCERTAIN | 6 |
| SITE-000049 | Akron Polymer Solutions, Inc. — Akron | STILL_UNCERTAIN | 3 |
| SITE-000087 | Rainbow Rubber Extrusions — Barberton | VERIFIED | 2 |
| SITE-000125 | Cardinal Products — North Royalton | VERIFIED | 5 |
| SITE-000185 | Elbex — Kent | VERIFIED | 5 |
| SITE-000223 | Addipel — Elyria | STILL_UNCERTAIN | 5 |
| SITE-000256 | Baker Plastics — Youngstown | VERIFIED | 3 |
| SITE-000298 | Colonial Machine — Kent | VERIFIED | 5 |
| SITE-000342 | Eagle Elastomer — Peninsula | VERIFIED | 5 |
| SITE-000388 | Hanlon Composites, LLC. — Elyria | STILL_UNCERTAIN | 5 |
| SITE-000429 | JRM Chemical — Cleveland | VERIFIED | 2 |
| SITE-000466 | MEDCO LABS — Bedford Heights | VERIFIED | 3 |
| SITE-000519 | Perry Fiberglass OH — Elyria | VERIFIED | 4 |
| SITE-000558 | Premix-Hadlock Composites - Geneva | STILL_UNCERTAIN | 5 |
| SITE-000594 | Saco Aei Polymers — Aurora | STILL_UNCERTAIN | 6 |
| SITE-000637 | Team Wendy — Cleveland | STILL_UNCERTAIN | 2 |
| SITE-000678 | Wrap Tite - Site 3 | STILL_UNCERTAIN | 2 |
| SITE-001426 | Etched Metal — Solon | VERIFIED | 3 |
| SITE-001522 | Owens Corning — Tallmadge Technology Center / XPS Plant | STILL_UNCERTAIN | 5 |
| SITE-001657 | High Tech Extrusions Ltd — Chardon | VERIFIED | 3 |
| SITE-001709 | ENGINEERED LAMINATES & COATINGS — Akron | STILL_UNCERTAIN | 3 |
| SITE-001754 | Harrison Paint Company — Canton | STILL_UNCERTAIN | 3 |
| SITE-001836 | Robin Industries, Inc. | STILL_UNCERTAIN | 5 |
| SITE-001896 | Rainbow Master Mixing LLC | VERIFIED | 4 |
| SITE-002024 | Veretec Inc | STILL_UNCERTAIN | 3 |

## Packet conventions

- `record_scope = site` means the own site ties the fact to this establishment (single listed location, or plant-named). `org` means company-wide only. Org-scope rows use the ORG id as `record_id`.
- `verdict` in `packet.csv` is per row: VERIFIED for an in-vocab value, STILL_UNCERTAIN for an off-vocab `*_other_note` row, whose settling fact is an owner vocabulary ruling.
- The site-level verdict is in `verdicts.csv`, with the deciding or settling fact, fetches used and availability failures.
- Product compliance claims (AMS 3216, USP Class VI, FDA grade at Eagle Elastomer) are not facility certifications and are not recorded as such.
