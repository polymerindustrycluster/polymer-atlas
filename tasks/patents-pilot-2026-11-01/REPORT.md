# Patents pilot: innovation layer and discovery leads, Ohio and Pennsylvania (2026-11-01)

Packet lane output. Nothing here edits `data/`, allocates IDs, or creates records.
Every NO_MATCH row is a **discovery lead**, not a record.

## 1. Route used

| Route | Result |
|---|---|
| (a) PatentsView PatentSearch API, `search.patentsview.org/api/v1/patent/` | **Not usable.** The egress proxy refused the CONNECT (policy denial, 502), so no request reached the host and no key was transmitted. `data.patentsview.org` is refused the same way. USPTO's 2026-03-18 notice says PatentsView migrated to the USPTO Open Data Portal (ODP) on 2026-03-20 and that the PatentSearch API pauses, with no new API location or restart date given. `patentsview.org` now 301-redirects to `data.uspto.gov/support/transition-guide/patentsview`. Whether `USPTO_API_KEY` is a PatentsView key was therefore not testable. |
| (b) USPTO ODP API, `api.uspto.gov` | **Works for the Bulk Data (datasets) API.** `GET https://api.uspto.gov/api/v1/datasets/products/search?q=patentsview` with header `X-API-KEY: <KEY>` returns HTTP 200 and lists six PatentsView products (PVGPATDIS, PVANNUAL, PVSORTED, PVGPATTXT, PVPGPUBDIS, PVPGPUBTXT; all through 2025-12-31). Without the key it returns 401. I did not test the ODP patent file-wrapper (application search) endpoints, because they carry no disambiguated assignee table. |
| (c) PatentsView bulk tables | **This is what was used, delivered through (b).** Product `PVGPATDIS` ("PatentsView Granted Patent Disambiguated Data"), file list at `https://api.uspto.gov/api/v1/datasets/products/PVGPATDIS?includeFiles=true`. A file request `.../datasets/products/files/PVGPATDIS/<file>` (with `X-API-KEY: <KEY>`) answers 302 to a short-lived signed `data.uspto.gov/files/...` URL. That signed URL was fetched **without** the key, so the key was sent only to `api.uspto.gov`. |

Files pulled (raw copies stay outside the repo, in `/tmp/claude-0/patents_raw/pvgpatdis/`): `g_patent`, `g_assignee_disambiguated`, `g_cpc_current`, `g_location_disambiguated` (about 1.1 GB zipped). `g_patent` and `g_cpc_current` sizes matched the ODP listing byte for byte; the other two were read to the end without a zip error.

**Data currency:** the latest grant date in the files is **2025-12-30** (PatentsView Q4 2025 release). "Latest" in this pilot therefore means 2025-12-30. Grants in 2026 are not covered.

## 2. Method

1. Patents: `g_patent` rows with `patent_date` 2021-01-01 or later and `withdrawn` not 1: 1,819,277 patents (all types).
2. CPC filter: any `g_cpc_current` row (inventional or additional, any sequence) whose `cpc_subclass` starts with `C08` or `B29`, or equals `C09J`, `C09D` or `B60C`: **67,452 patents** nationwide.
3. Location: `g_location_disambiguated` rows with country US and state OH or PA (3,013 location ids). An assignee counts when **its own** location on that patent is in OH or PA (not merely the inventor).
4. Aggregate per `assignee_id` (PatentsView disambiguated id). Organization assignees only; 8 patents have an OH/PA individual assignee and no organization. They are excluded and not in the counts below.
5. Matching: `scripts/atlas.py` `dedupe()` (the code behind `dedupe-check`), imported read-only, on the PatentsView name and up to 3 name variants. Domain is unknown, so step 1 and step 3 were skipped. It searches `organizations_*.csv` and `ecosystem.csv` together, so universities and labs were checked against `ecosystem.csv` in the same pass.
   - **MATCH_ORG**: step 2 hit (normalized name equals `legal_name` or a `trade_names` value). `matches.csv` gives `org_id` and the step.
   - **POSSIBLE**: no step 2 hit, but one of: step 4 substring hit; token-prefix match (one name's tokens begin the other's); token overlap (Jaccard 0.6 or higher, or 3+ shared tokens with Jaccard 0.45 or higher); or near-identical spelling (similarity 0.9 or higher). Candidates are listed, up to 6. This class is noisy by design. Treat it as a review list, never as a merge.
   - **NO_MATCH**: none of the above.

Deliverables in this folder: `assignees.csv` (414 rows), `matches.csv` (414 rows), this file.

## 3. Counts (units named)

| Measure | Value |
|---|---|
| Granted US patents, 2021-01-01 to 2025-12-30, with C08, B29, C09J, C09D or B60C in current CPC, nationwide | 67,452 |
| Of those, patents with at least one **organization** assignee located in OH or PA | **2,839 patents** |
| Unique disambiguated organization assignees located in OH or PA on those patents | **414 assignees** (230 OH-primary, 184 PA-primary by most frequent location; 3 have both OH and PA locations) |
| Assignee-patent pairs (an assignee/patent pair counts once; co-assigned patents appear under each assignee) | 2,849 |
| Assignees by PatentsView type | 404 US company or organization (this code also holds universities and nonprofits), 5 foreign company, 4 US federal government, 1 US state government |

### Match rates (unit: unique OH/PA assignees, then patents by assignee-patent pair)

| Class | Assignees | % of 414 | Assignee-patent pairs | % of 2,849 |
|---|---|---|---|---|
| MATCH_ORG | 113 (101 in `organizations`, 12 in `ecosystem`) | 27.3% | 955 | 33.5% |
| POSSIBLE | 71 | 17.1% | 759 | 26.6% |
| NO_MATCH | 230 (109 OH, 121 PA) | 55.6% | 1,135 | 39.8% |

By state of primary location: OH has 78 MATCH_ORG, 43 POSSIBLE, 109 NO_MATCH. PA has 35 MATCH_ORG, 28 POSSIBLE, 121 NO_MATCH.

Of the 113 MATCH_ORG, 111 are `active`, 1 `acquired` (Omnova Solutions, successor chain to ORG-000050 Synthomer, Inc.), 1 `unknown`. One match (J-LOK Co.) also has a second step-2 hit (ORG-004545 JLOK Corp), flagged in `note`.

Of the 230 NO_MATCH assignees, 129 hold exactly one patent and 101 hold two or more.

## 4. Top 25 NO_MATCH leads by patent count

Patent counts are patents in the filtered CPC set with the assignee located in OH/PA. CPC mix shows the top three subclasses.

| # | Assignee (PatentsView name) | City, State | Patents | CPC mix | First to last grant | PV type |
|---|---|---|---|---|---|---|
| 1 | The Procter & Gamble Company | Cincinnati, OH | 333 | B29C:193;B29L:147;B29K:126 | 2021-01-12 to 2025-12-30 | us_company |
| 2 | SWIMC LLC | Cleveland, OH | 107 | C09D:106;C08F:37;C08K:35 | 2021-01-12 to 2025-11-25 | us_company |
| 3 | General Electric Company | Evendale, OH | 81 | B29C:66;C09D:10;B29D:5 | 2024-07-23 to 2025-12-23 | us_company |
| 4 | Dentsply Sirona Inc. | York, PA | 44 | B29C:21;C08L:17;C08F:8 | 2021-01-26 to 2025-12-09 | us_company |
| 5 | United States of America as represented by the Secretary of the Air Force | Patterson, OH | 44 | C08G:27;B29C:21;B29K:18 | 2021-01-26 to 2025-08-05 | us_federal_gov |
| 6 | IMFLUX INC. | Hamilton, OH | 32 | B29C:32;B29K:10 | 2021-01-19 to 2024-09-24 | us_company |
| 7 | THE PENN STATE RESEARCH FOUNDATION | State College, PA | 19 | C08L:9;B29C:7;C08G:4 | 2021-04-06 to 2025-09-02 | foreign_company |
| 8 | Workhorse Group Inc. | Sharonville, OH | 18 | B29C:18;B29K:18;B29L:18 | 2022-01-11 to 2025-11-25 | us_company |
| 9 | DANA HEAVY VEHICLE SYSTEMS GROUP, LLC | Maumee, OH | 13 | B60C:12;B29C:1;B29L:1 | 2021-03-02 to 2024-07-30 | us_company |
| 10 | Global Graphene Group, Inc. | Dayton, OH | 13 | C08K:9;C09D:8;C08G:5 | 2021-04-06 to 2024-04-23 | us_company |
| 11 | THE SECANT GROUP, LLC | Telford, PA | 13 | C08G:6;B29C:3;C08J:3 | 2021-02-16 to 2025-10-14 | us_company |
| 12 | Matthews International Corporation | Pittsburgh, PA | 10 | B29C:10;B29L:4;B29K:1 | 2021-06-08 to 2025-09-16 | us_company |
| 13 | LMS Co., Ltd. | Marion, OH | 7 | C09D:7 | 2021-01-26 to 2024-01-02 | foreign_company |
| 14 | Pilot Polymer Technologies, Inc. | Pittsburgh, PA | 7 | C08F:7;C08G:3;C08J:3 | 2021-01-26 to 2022-09-13 | us_company |
| 15 | Vitro Flat Glass LLC | Acmetonia, PA | 7 | C09D:6;B29D:1;C08K:1 | 2022-08-30 to 2025-05-06 | us_company |
| 16 | Cagent Vascular, Inc. | Wayne, PA | 6 | B29C:6;B29L:5 | 2021-06-22 to 2025-07-15 | us_company |
| 17 | Devicor Medical Products, Inc. | Cincinnati, OH | 6 | C08J:4;B29C:2 | 2021-05-04 to 2025-02-18 | us_company |
| 18 | Nanotronics Imaging, Inc. | Cuyahoga Falls, OH | 6 | B29C:6 | 2021-08-10 to 2025-10-21 | us_company |
| 19 | POWDERMET, INC. | Euclid, OH | 6 | C08J:6;C08K:6;B29C:2 | 2021-07-06 to 2023-10-31 | us_company |
| 20 | Thomas Jefferson University | Philadelphia, PA | 6 | C08J:4;C08K:4;C09D:2 | 2021-02-09 to 2024-05-07 | us_company |
| 21 | TRUCAPSOL LLC | Bethlehem, PA | 6 | C08F:5;C08L:5;C08G:4 | 2022-10-11 to 2025-01-07 | us_company |
| 22 | X-Card Holdings, LLC | West Chester, PA | 6 | C08L:4;B29C:2;B29K:2 | 2021-07-13 to 2023-01-24 | us_company |
| 23 | CNH Industrial America LLC | New Holland, PA | 5 | B60C:4;B29C:1;B29D:1 | 2021-02-23 to 2024-02-13 | us_company |
| 24 | F&S Tool, Inc. | Erie, PA | 5 | B29C:5;B29L:2;B29K:1 | 2021-02-16 to 2025-07-15 | us_company |
| 25 | Kineticure, LLC | Miamisburg, OH | 5 | B29C:5;B29L:3 | 2021-01-26 to 2025-07-22 | us_company |

Reading notes (analyst remarks, not Atlas facts):
- **SWIMC LLC** looks like an IP-holding entity (its mix is 106 of 107 patents in C09D coatings). The Atlas already holds ORG-000132 The Sherwin-Williams Company, but dedupe-check does not link them and I did not self-rule it. Whether SWIMC belongs to that parent is a question for a primary source (an SEC filing or a company page), so hold it as a lead.
- **The Procter & Gamble Company** and **General Electric Company** (Evendale is GE Aerospace, the B29C hits are additive and composite processes) are large non-polymer parents. They surface because of CPC B29, not because they are polymer processors. Scope is an owner question; I did not decide it.
- **United States of America as represented by the Secretary of the Air Force** (Patterson, OH) is a federal-government assignee for the Air Force Research Laboratory at Wright-Patterson. Whether it belongs in `ecosystem.csv` is a scope and people-records question under AGENTS.md §6; not decided here.
- **The Penn State Research Foundation** is mislabelled "foreign_company" in the PatentsView type code. The Atlas holds Pennsylvania State University rows in `ecosystem.csv` (ORG-002775, ORG-002779, ORG-002785), but the matcher did not link the Foundation to them. This is a likely near-miss for human review.
- Spelling variants in the source are not corrected by PatentsView: "Coopper Tire & Rubber Company" appears as POSSIBLE for ORG-001425 Cooper Tire & Rubber Company, and "The Goodyear Tire & Robber Company" and "THE GOODYEAR RUBBER & TIRE COMPANY" appear as POSSIBLE for ORG-000003. These are the same companies in all likelihood, but the pilot lists them as POSSIBLE because the tool does not link them.

## 5. Caveats (binding for any downstream use)

1. **Assignee location is the HQ-grade address the patent lists, not a plant.** A patent assignee address is usually a corporate or legal address. It says nothing about where manufacturing happens. Ohio county, site and ring must come from site-level sources.
2. **Patents are leads. They never prove that a company, an establishment or a manufacturing site exists, and never support a scope claim.** A NO_MATCH row is a name and a city. Scope is unknown until verified against a primary source (AGENTS.md §4 evidence contract; the §2 rule 8 verdict grammar applies to any follow-up lane). Coordinates, cities and counties in these files are reference data.
3. The CPC filter is broad. C08 and B29 hit medical devices, consumer goods, aerospace and universities. Presence in the list does not mean the assignee is a polymer or plastics firm.
4. Assignee disambiguation is PatentsView's, and it errs both ways (it splits some entities, such as "PPG Industries Ohio, Inc." versus the parent, and merges others). I did not reconcile parents and subsidiaries; subsidiary names are not folded into parents. Parent-of-record questions stay with the Atlas parent (AGENTS.md §2 rule 8).
5. **A patent grant date is not a status fact.** The last grant date is not evidence that a company is operating or has closed (AGENTS.md §3 status-change rule).
6. The window ends 2025-12-30. A 2026 refresh needs the next PatentsView release on ODP.
7. Matching is name-only, since no domain is known. It can produce false matches and false misses. It also never treats a patent hit as satisfying the dedupe checks of AGENTS.md §3 for a create: a lead that becomes a candidate record still needs the full §3 order (domain, name, street address, trade names).
8. "Persons" in this data (inventors) are not used, stored or exported. Only organization assignees are in the outputs. No individual names appear in the deliverables, which is consistent with AGENTS.md §6.

## 6. Source terms and licensing

- Source: USPTO Open Data Portal, Bulk Data product **PVGPATDIS** (PatentsView Granted Patent Disambiguated Data), release containing data through 2025-12-31. Files accessed through the ODP datasets API with a personal ODP API key.
- PatentsView data has been published under a Creative Commons Attribution 4.0 licence (cite PatentsView / USPTO). I **did not re-verify** the licence text under ODP in this session. Confirm it on the ODP product page or `data@uspto.gov` before publishing derived data, and cite as "PatentsView, USPTO" in the evidence row.
- The ODP API key is a per-user credential. It is read from the environment only and appears in no repo file. Documented URLs use `<KEY>`. ODP applies its own rate limits and terms of use, not reviewed here.
- This is **not** a licensed-source problem under AGENTS.md §5: PatentsView is a federal open dataset. Even so, a patent-derived fact enters the Atlas only as a lead or, in a later lane, through an evidence row to the primary patent record (patent number plus grant date).
- Reproducibility: the procedure above plus the pinned file list is enough to rerun. The helper scripts are in the session scratchpad, not the repo. If the owner wants them kept, they belong in `scripts/` in a follow-up PR (I did not add them).

## 7. Suggested next steps (proposals, not actions)

1. Review the 71 POSSIBLE rows (most are corporate-form variants of held parents: Rohm and Haas, PPG Industries Ohio, Lubrizol, Owens Corning, Avery Dennison, Braskem, universities) and record the dedupe decisions through the integrator of record.
2. Verification lanes for the top NO_MATCH leads that are plausibly polymer firms: IMFLUX (Hamilton, OH, injection molding), Global Graphene Group (Dayton, OH), The Secant Group (Telford, PA), Pilot Polymer Technologies (Pittsburgh), Powdermet (Euclid, OH), Kineticure (Miamisburg, OH), AGR International (Butler, PA), X-Card Holdings (West Chester, PA), and others. Each needs an own-site and registry check before any record exists.
3. Owner rulings needed (propose as battery items, do not self-rule): whether large non-polymer parents that surface only through CPC B29 belong in scope; whether federal-lab and university-foundation assignees belong in `ecosystem.csv`; whether to store patent counts as an Atlas innovation field (D-05) and, if so, in what table and under what vocabulary revision.
4. Expansion path: the same four files cover every state; change the state filter in step 3. The Q-over-Q refresh arrives with new PatentsView releases on ODP.
