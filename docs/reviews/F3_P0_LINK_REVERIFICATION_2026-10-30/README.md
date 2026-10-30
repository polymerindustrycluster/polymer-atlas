# F3 — Five former P0 forward-link rejects

Pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`. Observed 2026-10-30.
Lane: `codex-f3`; draft PR [#8](https://github.com/polymerindustrycluster/polymer-atlas/pull/8).

## Result and meaning

**Five requested facilities reviewed: 3 VERIFIED, 2 STILL_UNCERTAIN, 0 REJECT.** All five facility identities and their RY2024 TRIFID/FRS pairs resolve in the official EPA extract. The two uncertain verdicts concern a complete, correctly attributed Atlas site design, **not whether these facilities exist**. Proposed tiers: one A, two B, two U candidates. No canonical rows were added or changed; no IDs allocated, relationships authored, sites merged, coordinates used as evidence, or parent strings automatically adopted.

| Facility | Verdict | Deciding or settling fact |
|---|---|---|
| Amcor, Appleton WI | STILL_UNCERTAIN | Permit names **Amcor Wisconsin LLC**, while the candidate held parent is **Amcor Flexibles North America Inc.** A non-TRI legal/operator bridge and site-specific polymer process witness must settle attribution and scope. |
| Union Carbide Technology Park, South Charleston WV | VERIFIED | 2026 WVDEP renewal identifies UCC's R&D operation; park operator independently identifies polyolefin R&D. Not the held Institute or MacCorkle sites. |
| Patrick / Alpha Systems, Elkhart IN | STILL_UNCERTAIN | Facility and Patrick acquisition are supported; **owner must resolve org grain** before attaching to any parent. ORG-002547 remains Adorn-grain. Exact Beck Drive process needs confirmation, not company-wide molding propagation. |
| AOC Tennessee Plant, Collierville TN | VERIFIED | Own site names manufacturing plant at **860 Hwy 57**; issuer's resin guide lists this plant; TRI confirms Fayette County and resin NAICS. Neither 830 colorants nor held 950 HQ is this site. |
| Teel Pipe, Baraboo WI | VERIFIED | Own facility list and exact-location certificate verify **500 Industrial Court**, with custom plastic extrusion rather than headquarters' entire capability inventory. |

`VERIFIED` is a research recommendation, **not authorization to integrate**. All five designs still require independent review, current-tree identity/duplicate checks, and an integrator. Conditional fields in U candidates must not be imported as facts. The two uncertain candidates deliberately leave `org_id`, `site_id`, status, and evidence record IDs unallocated/blank. Candidate held IDs are lookup references only, not proposed links.

## Registry identity: direct official extract, not a project echo

[Official EPA RY2024 US CSV](https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2024_US/csv), HTTP 200, 60,550,684 bytes, 77,295 **chemical-report rows**. SHA-256:
`06dfa3a67bb4c5bd38d9e9f0f7b8bff10b95254a63169423632d7f6f251e1506`.
Fetched 2026-10-30; local raw retained outside the repo at `/tmp/f3-raw/tri_2024.csv`. Download is reproducible; dynamic later revisions may have a different hash and must be rechecked. Only minimal facility identity fields are in the packet; no personal/contact columns are copied.

| TRIFID | FRS ID | Exact street | County | Chemical-report rows |
|---|---|---|---|---:|
| 54914DRLMN2621W | 110000855487 | 2621 W EVERETT ST | OUTAGAMIE | 1 |
| 25303NNCRB32003 | 110000344324 | 2001 UNION CARBIDE DRIVE | KANAWHA | 2 |
| 46516LPHSY5120B | 110008057789 | 5120 BECK DR | ELKHART | 4 |
| 38017LPHRSHIGHW | 110000911737 | 860 HWY 57 E | FAYETTE | 13 |
| 5391WTLPLS5INDU | 110071434086 | 500 INDUSTRIAL CT | SAUK | 1 |

All five IDs have zero existing registry-link matches at the pin. FRS numbers are verified as EPA's FRS cross-identifiers in this official extract, **not represented as independently downloaded FRS records**. The extract also independently resolves `25112NNCRBRTE25` / FRS `110070828292` at WV State Rt25 (Institute), and `25303NNCRB437MA` / FRS `110000745114` at 437 MacCorkle Ave SW. These differ from Technology Park in both registry identity and address. No cross-link to the two held sites is recommended.

## Facility analysis and primary witnesses

### Amcor — hold operator grain, not existence

[Wisconsin DNR facility 445008080](https://apps.dnr.wi.gov/warp_ext/am_permittracking2.aspx?id=3001551) directly establishes the named LLC, street and county, including active permits and 2026 pending applications. [Amcor's Appleton press-operator posting](https://www.amcor.com/careers/job-details/req_95783) corroborates current production recruitment but is not a substitute for the precise legal bridge or substrate/process proof. No separate Wisconsin organization is invented; ORG-000665 is merely the candidate. Proposed printing/material fields are conditional and tier U. Recommend holding until the legal operator relationship and exact-plant polymer activity are documented; do not override the permit with TRI's parent field.

### Union Carbide — R&D, not an automatically inferred resin plant

[WVDEP 2026 final-renewal fact sheet, Group 1](https://apps.dep.wv.gov/Documents/DAQ/TitleVPermits/039-00004--1-2/Final/FinalFactSheet%20R30-03900004-2026%20%28Group%201%20of%202%29.pdf) states R&D activity and **primary NAICS 325199**, unlike RY2024 TRI's 325211. Recommend the newer permit code with government-filing provenance, retaining the discrepancy visibly; no corporate NAICS inference. The same fact sheet explicitly distinguishes environmental operations and notes a common Clean Air Act source with Univation: **this is not authority to merge establishments or operators**.

[The park operator's dated tenant description](https://www.wvtechpark.com/post/tenant-spotlight-dow) supports polyolefin R&D scope at B strength. The [2026 EPA stewardship assessment](https://www.epa.gov/system/files/documents/2026-05/lts-assessment-rpt_ucc-tech-park-visit-date-10.29.25-2.20.2026.pdf) corroborates UCC ownership/control and its Dow Chemical subsidiary status, but its remediation discussion alone would not establish current polymer operations. Candidate linkage preserves the **already-held** ORG-002913 Dow Inc grain, whose notes explicitly treat UCC as a site operator. Proposed `rd_center`, producer R&D Ring 1 and thermoplastics are recommendations for reviewer confirmation, not a new owner ruling. Do not create a generic West Virginia Technology Park landlord record from this facility.

### Alpha — owner battery item remains open

[Alpha's contact page](https://alphallc.us/contact/) identifies 5120 Beck Drive; [its homepage](https://alphallc.us/) identifies multiple manufacturing divisions. [Patrick's May 3, 2021 acquisition statement](https://ir.patrickind.com/investor-news-events/press-releases/detail/197/patrick-industries-inc-completes-acquisition-of-alpha-systems-llc) says the acquired business would remain stand-alone. This does **not** establish an Adorn operator relationship. Recommendation: preserve ORG-002547 unchanged and ask owner whether to establish Alpha grain or a Patrick-wide parent with the appropriate structure; the lane makes neither decision. Proposed adhesive formulation is contingent on exact-plant evidence; no roto/blow or injection-molding capabilities are assigned here.

### AOC — manufacturing address and county separated from headquarters

[Own location page](https://aocformulations.com/en-asia/contact/locations/americas/united-states/aoc-tennessee-plant/) establishes the plant. Its linked location list distinguishes colorants at 830 and headquarters at 955; held SITE-003729 remains 950, which this lane does not correct. [AOC-issued June 2005 resin guide, hosted by a distributor](https://alpinagrate.eu/wp-content/uploads/2020/11/literature_Corrosion_Guide-AOC.pdf) lists 860 as Tennessee plant and establishes historical resin scope. [Current own Americas production description](https://aocformulations.com/en-emea/applications/aoc-united-states/) corroborates the business, not individual plant capabilities. Together with current plant listing and RY2024 filing, recommend conservative B rather than pretending the old guide is a fresh plant audit. Specific production processes are blank; thermoset resin material is the §4.7 process-or-material field. Fayette comes from the exact facility filing, not Collierville mailing-city geography. TRI's ALPHA CORP parent string is not adopted.

### Teel — only site-specific extrusion

[Teel's own facilities/history page](https://www.teel.com/about-us/) identifies the Industrial Court pipe operation and exact address. [Own-hosted ASR certificate 5750](https://www.teel.com/wp-content/uploads/2025/03/5750-Teel-Plastics-ISO-9001-Certificate-June-2024-signed.pdf), page 2, isolates custom plastic extrusion at this address. The third-party certificate is conservatively classified registry/B; the own facility/activity statements independently support the A recommendation. Teel Plastics linkage is supported beyond the TRI parent lead. The held 1060 Teel Court HQ (SITE-003711) is not the Industrial Court site. No injection molding, compounding, or laboratory-bag scope is copied across locations.

## Packet, safeguards, and limits

- `verdicts.csv`: five exactly-once results with deciding/settling facts.
- `site_design.csv`: five unallocated proposals; no new org/parent IDs; U proposals clearly gated.
- `evidence_rows.csv`: **42 claim observations**, every evidence/site ID blank. `packet_key` joins within this packet only and is not a canonical ID. Three VERIFIED designs have all seven existence/address/scope/code/parent/activity/liveness claim types. Observations for U candidates are partial and do not satisfy integration completeness.
- `registry_checks.csv`: five exact matches and row counts, all new-link IDs blank.
- `sources.json`: source URLs, fetch outcome and SHA-256 byte fingerprints where captured. A failed local Alpha contact snapshot (403) is distinct from successful web-open observation; no invented hash.
- `fingerprints.json`: hashes for every canonical data file, relevant held org/site rows, and address-dedupe results. Domain/name/operator candidates, trade-name/successor notes and all site shards were reviewed; no exact normalized street/state hit for the five proposed sites.
- `validate_packet.py`: packet/enum/empty-ID/must-have/FK-union guards, canonical byte invariance, optional official-extract recheck. This does not simulate integration or claim that blank-ID fragments pass the canonical validator.

The bounded effort covered 3 unique primary documents for Amcor, 6 for UCC including navigation pages, 5 for Alpha including one failed fetch, 4 for AOC, and 5 for Teel including two failed fetches (shared official extract counted once per facility). Search previews were discovery only; exact pages/documents were opened before evidence rows were written. Re-reading/capturing the same witness for fingerprints did not expand substantive source scope. No private CRM, licensed listing copy, or outreach. Failed Teel PDF and Elkhart municipal PDF routes establish availability limits only. **No closure/no-establishment REJECT was proposed, so the pre-REJECT Form5500 gate was not invoked**; nothing claims Form5500 absence.

Validation: pristine pinned repo and final unchanged canonical tree pass `python3 scripts/validate.py`; packet guards and full organization-shard + ecosystem/site FK-union check pass. `tasks/QUEUE.md` changes only F3's status token; all other entries byte-preserved. Main rechecked 2026-10-30 at 21:39 UTC: still the pin, no drift absorbed. Publication/readback and independent review remain distinct from integration; no merge/main push is authorized by this packet.
