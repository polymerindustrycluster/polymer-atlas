# Lead fusion: polymer establishments not in the Atlas, ranked by independent federal sources - 2026-11-01

**Status: discovery-lead product, not Atlas data.** Packet lane output (AGENTS.md section 2 rule 7): nothing here edits `data/`, allocates an Atlas ID, sets a tier or changes a status. `cluster_id` values (`LF-<state>-<seq>`) are local keys of this run, never Atlas IDs. Built by `scripts/build_lead_fusion.py` (stdlib; deterministic; imports the normalizers and `dedupe` of `scripts/atlas.py`). As-of date 2026-11-01.

**Every row is a lead only. It is not evidence that an establishment exists, operates or is in scope.** Several source families naming one address raises the odds that the establishment exists and operated; it proves nothing about ring, NAICS or scope (AGENTS section 4 evidence contract; SCHEMA 2.1: NAICS never decides a ring). Each lead still needs the full create path: website-domain dedupe (none of the six sources carries a domain, so AGENTS section 3 step 1 has NOT been run for any lead), name, street and trade-name dedupe on the integrator's own pass, primary-source existence and scope evidence rows (SCHEMA 4.13), tier U/C at birth, ring and scope rulings (owner rulings, AGENTS 2.9), and ID allocation above the tree-wide maximum by the integrator of record.

## Summary

- **Source rows in (unit: packet records, verdict NO_MATCH + POSSIBLE):** 38,390 (36,917 NO_MATCH + 1,473 POSSIBLE) from six source families; 226 with no US state are held, 38,164 clustered.
- **Clusters out (unit: candidate establishments):** 31,492 raw clusters; 599 dropped as already held in the current Atlas; 30,893 survivors; **26,372 polymer-lead clusters in `clusters.csv`**: **STRONG (>= 3 families) 991, CORROBORATED (2) 3,088, SINGLE (1) 22,293**.
- **STRONG clusters, top states (unit: clusters):** MI 106; CA 78; IL 61; MA 56; IN 53; MN 48; WI 47; TX 42; NC 35; NY 34. Among the ten QCEW-gap states: CA 78; TX 42; FL 25; MI 106; IL 61; GA 34; IN 53; WI 47; NY 34; NC 35; OH 20, PA 18.
- **Reconciliation (rule 10):** all six families reconcile exactly with the published NO_MATCH, POSSIBLE and total counts; the ITA-vs-OSHA overlap differs from the ITA packet's own figure for identified rule-level reasons (section 3).
- **Observed false-cluster rate:** 0 FALSE and 0 DOUBTFUL of 30 random multi-source clusters; stratified over the weaker merge bases 0 FALSE and 2 DOUBTFUL of 40 (section 4).
- **Use:** verify STRONG clusters with a plant-grade family first; each still needs the full create path.

## 1. Method

**Inputs (rows with verdict NO_MATCH, and POSSIBLE carried separately).** Six source families, each read from its packet's match file joined to its row file: **ITA** (OSHA Form 300A CY2025, `tasks/osha-ita-2026-11-01`), **OSHA** inspections 2019+ (`osha-spine-2026-11-01`), **ECHO** (EPA ECHO/FRS active NAICS-scoped facilities, `echo-frs-spine-2026-11-01`), **F5500** (Form 5500 / 5500-SF sponsor EINs, `form5500-spine-2026-11-01`), **USASPEND** (USAspending contract recipients, the USAspending part of `federal-leads-2026-11-01`; the openFDA rows are not used), **PATENT** (PatentsView assignees, OH and PA only, `patents-pilot-2026-11-01`). Per row: name variants, street, city, state, ZIP5, NAICS codes, EIN (ITA and Form 5500 only; ITA EINs only when `ein_quality` is ok or zero_padded), a size input and the latest activity date.

| Family | Agency | Address grade | Size input | Activity date | NAICS input |
|---|---|---|---|---|---|
| ITA | DOL-OSHA | plant (worksite) | annual average employees (establishment) | `date_submitted` of the CY2025 filing | employer-entered code |
| OSHA | DOL-OSHA | plant (inspected worksite) | `nr_in_estab` at the latest valid inspection | latest inspection open date | inspector-recorded, all codes seen |
| ECHO | EPA | plant (permit address) | none | `last_activity_date` | program-reported scope codes |
| F5500 | DOL-EBSA | HQ / mailing | active plan participants (employer level) | `latest_date_received` | filer-chosen padded group code (e.g. 326100) |
| USASPEND | USAspending/SAM | HQ / SAM-registered | none | none (obligations are a FY22-26 window, not a date) | award-level NAICS mix |
| PATENT | USPTO | HQ-grade, city only | none | last grant date | none (CPC C08/B29/C09J/C09D/B60C) |

**Not clustered, held (unit: source rows).** Rows whose state is blank or not a USPS code (foreign and no-state USAspending recipients; the AGENTS section 3 foreign-site rule: no lawful shard without an owner/schema ruling) are never clustered or scored: F5500 NO_MATCH 2; USASPEND NO_MATCH 222; USASPEND POSSIBLE 2 (total 226).

**Clustering** (never across states; union-find; cluster IDs asserted unique; every input row lands in exactly one cluster). Edges, in order:

1. **street + ZIP5** (strong): same normalized street (`atlas.street_key`; must start with a house number; PO boxes never keyed), same state, same ZIP5; or street + city when either side has no ZIP5. **Name guard:** the two rows' names must be compatible (equal normalized name; or the distinctive tokens - generic words such as plastics/industries/products removed - equal, nested, Jaccard >= 0.5 or equal first token; or near-identical spelling). A same-address pair with incompatible names is a co-tenant or rebrand (the Atlas's POSSIBLE class): it is **not merged** and is counted as blocked.
2. **house number + ZIP5 + a shared street word + a firm name match** (medium): catches street spelling variance across sources (`US-43` vs `US Hwy 43`).
3. **weak rows** (no usable street, or an HQ-grade source: Form 5500, USAspending, patents) are first merged with each other on the same normalized name + city or ZIP5 (refused when both sides carry a real, different street), then **attached to a located plant-grade cluster only when exactly one such cluster shares their EIN + city/ZIP5 (ITA <-> Form 5500) or their name + city/ZIP5 (name attach only when the weak row has no street of its own)**. When more than one candidate cluster exists the row is left unattached (ambiguous), and a weak row that carries a real street different from the plant's is a different address of the same employer: it stays its own cluster and is cross-referenced in `related_clusters` (`same_name_other_street:` or, for an EIN, `same_ein_other_street:`). An employer-level row must never fuse two plants of one company.
Deliberate deviation from the brief: the brief lists name + city + state as a medium rule. Applied to two plant-grade rows with *different* known streets it would merge two plants of one company (a second site is a second site, AGENTS section 3), so name + locality is used only where at least one side lacks a plant street (rule 3). EIN + city is likewise applied cross-family only (ITA <-> Form 5500): two ITA establishments with one EIN in one city are two establishments.

**Atlas snapshot used:** the working tree at run time: 4,443 organization + ecosystem rows, 5,773 site rows, 3,636 with a `street_address` (5,236 with a usable street key counting the `Street...:` phrase in notes). The source packets matched against 5,773 site rows with 3,629 `street_address` values, so any address added to the Atlas since is caught here.

**Atlas re-check (the current `data/`, not the packets' snapshot).** Using `atlas.name_key` / `atlas.street_key` and the `atlas.dedupe` step logic, indexed (self-tested against `atlas.dedupe()` on 200 random clusters: 0 name-step and 0 street-step mismatches; the run aborts on any mismatch), a cluster is **dropped as already held** when: (a) a held site has the same street key in the same locality (street from `street_address`, else the `Street...:` phrase in notes) and a name that agrees with the site, its org or its trade names; (b) a held org whose normalized legal/trade name equals a cluster name, whose HQ or site states include the cluster state, holds a site in the same city/ZIP5 whose street is equal or unknown; (c) the same through an EIN that a packet tied to a held org (ITA MATCH_SITE rows, Form 5500 MATCH rows); (d) an ECHO tri_id equals a held `TRI_TRIFID` registry link with a verified (non-fuzzy) basis. Weaker hits **do not drop**; they are flags: `COTENANT_AT_HELD_SITE` (held site at this street, name differs), `STREET_MATCH_LOCALITY_DIFFERS`, `HELD_ORG_NAME_OTHER_LOCATION` / `HELD_ORG_EIN_OTHER_LOCATION` (a held org of this name or EIN has no site here: likely a new site of a held org), `TRIFID_FUZZY_HELD_ORG`, `NOTES_OR_TRADE_NAME_MENTION` (AGENTS section 3 step 4; flag only). `related_clusters` lists, without merging, other clusters at the same street under an incompatible name (`colocated_other_name:`; a co-tenant or a rebrand) and same-name / same-EIN clusters at a different street of the same city (`same_name_other_street:`, `same_ein_other_street:`).

**Scoring** (`score`, higher = more certain; each term is a column or derivable from one): `10 x n_sources` (distinct source families with a NO_MATCH row) `+ 4 x n_agencies` (ITA and OSHA are both DOL-OSHA, so they count as one agency) `+ 3 x` families whose NAICS is core polymer (3252/3255/3259/326, not 325920 alone) `+ 2` when two families agree on one 4-digit core prefix `+` recency of the latest dated activity (3 within 1 year of the as-of date, 2 within 3 years, 1 within 5 years) `+` size (3 for 250+, 2 for 100-249, 1 for 50-99; establishment-grain ITA first, then OSHA, then employer-level Form 5500) `- 4` if no plant-grade family (ITA, OSHA, ECHO) is among the sources (only HQ-grade Form 5500 / USAspending / patents: no worksite address confirms an establishment) `- 3` if any member row is a POSSIBLE (an Atlas candidate hit is unresolved) `- 5` if every coded row is 325920 explosives `- 3` for an ECHO name-noise hint on a single-source cluster. `class`: **STRONG** >= 3 families, **CORROBORATED** = 2, **SINGLE** = 1, counted over NO_MATCH rows only (a family that has only POSSIBLE rows is listed in `possible_only_families`, not counted). Independence caveat: ITA and OSHA inspections are different OSHA datasets (employer-filed vs compliance-officer record), and ITA/Form 5500 are both employer filings, so `n_agencies` sits beside `n_sources`; ITA and OSHA NAICS are both OSHA-channel codes (the ITA report's own caution).

## 2. Counts (units named)

### 2.1 Source rows in

| Family | Packet rows (unit: source records) | NO_MATCH rows read | POSSIBLE rows read | Held, no US state | Rows clustered |
|---|---:|---:|---:|---:|---:|
| ITA | 11,194 | 9,145 | 346 | 0 | 9,491 |
| OSHA | 6,473 | 5,256 | 246 | 0 | 5,502 |
| ECHO | 15,920 | 13,255 | 315 | 0 | 13,570 |
| F5500 | 5,897 | 4,581 | 418 | 2 | 4,997 |
| USASPEND | 4,756 | 4,450 | 77 | 224 | 4,303 |
| PATENT | 414 | 230 | 71 | 0 | 301 |
| **All** | 44,654 | **36,917** | **1,473** | 226 | **38,164** |

Unit: a source record is one packet row (ITA establishment_ID, OSHA aggregation key, FRS registry ID, Form 5500 sponsor EIN, USAspending UEI, PatentsView assignee). One physical establishment legitimately appears under several records and several families, which is exactly what the fusion measures. 38,390 NO_MATCH + POSSIBLE source rows were read; 38,164 entered clustering.

### 2.2 Clusters out

- **Raw candidate-establishment clusters** (unit: clusters of source rows, US states and territories only): **31,492** from 38,164 rows (assertions passed: cluster IDs unique, every row in exactly one cluster, no cluster spans two states).
- Cluster size (unit: source rows per cluster): 1 row: 26,557; 2 rows: 3,568; 3 rows: 1,089; 4 rows: 211; 5 rows: 54; 6 rows: 8; 7 rows: 2; 8 rows: 1; 9 or more: 2 (largest 11).
- Distinct source families per raw cluster (any verdict): 1: 27,029; 2: 3,369; 3: 963; 4: 120; 5: 11.
- Successful merges by edge basis (unit: union operations): `ein+name_locality` 24; `ein_locality` 61; `housenum_zip_name` 889; `name_locality` 86; `street_city_zip_differs` 189; `street_zip` 5,378; `weak_name_locality` 45.
- Name/locality candidates **refused because a real street differs** (unit: clusters or pairs): `ein_attach_refused_street_differs` 12; `name_attach_refused_street_differs` 130; `weak_both_have_street` 22. Such rows stay separate clusters.
- Same-address row pairs **blocked by the name guard** (unit: row pairs; co-tenants/rebrands, not merged): 2,297. Weak (employer-level or street-less) clusters left unattached because more than one plant cluster qualified (unit: clusters): 12.
- **Atlas re-check drops (unit: clusters; source rows in parentheses):** 599 clusters (853 rows) are already held in the current Atlas:
  - `held_trifid_verified`: 361 clusters (514 rows)
  - `held_site_street_name`: 110 clusters (146 rows)
  - `held_org_name_local_site`: 78 clusters (116 rows)
  - `held_org_ein+name_local_site`: 29 clusters (47 rows)
  - `held_org_ein_local_site`: 21 clusters (30 rows)
- Survivors: **30,893 clusters**, by polymer-lead eligibility (`core` = a NO_MATCH row with core NAICS 3252/3255/3259/326, 325920 alone excluded; `ring3_primary` = only a Ring 3 Primary code; `patent_cpc_only` = patent assignee with polymer CPC and no NAICS): core 24,908; out_of_core_naics 3,405; ring3_primary 1,240; possible_only 836; explosives_325920_only 280; patent_cpc_only 224.
- **Survivors not carried to the lead table (unit: clusters / source rows):** `explosives_325920_only` 280 clusters / 334 rows; `out_of_core_naics` 3,405 clusters / 3,565 rows; `possible_only` 836 clusters / 938 rows. `out_of_core_naics` = ITA value-chain rows (distributors, tire retail, basic chemicals, machinery) with no core-NAICS row from any family; `possible_only` = clusters whose every row is a POSSIBLE (an Atlas candidate hit already exists; resolve in the packets' own POSSIBLE review). Nothing was ruled out of scope (scope is an owner ruling, AGENTS 2.9): these are simply not polymer-NAICS discovery leads for this table.

### 2.3 Lead table: `clusters.csv` = **26,372 clusters** (unit: candidate establishments not in the current Atlas, polymer-lead eligible)

| Class | Clusters | Share |
|---|---:|---:|
| STRONG | 991 | 3.8% |
| CORROBORATED | 3,088 | 11.7% |
| SINGLE | 22,293 | 84.5% |
| **Total** | **26,372** | |

Families confirming (unit: clusters): 1 families: 22,293; 2 families: 3,088; 3 families: 878; 4 families: 103; 5 families: 10.
Clusters containing each family (NO_MATCH rows): ITA 5,351; OSHA 4,916; ECHO 12,538; F5500 4,477; USASPEND 4,054; PATENT 229.
Most common STRONG family sets (unit: clusters): ITA;OSHA;ECHO 416; ITA;OSHA;F5500 147; ITA;ECHO;F5500 140; OSHA;ECHO;F5500 103; ITA;OSHA;ECHO;F5500 78; ITA;F5500;USASPEND 20; ITA;ECHO;USASPEND 20; ECHO;F5500;USASPEND 11.
STRONG clusters by distinct agencies (unit: clusters): 2 agencies: 567; 3 agencies: 403; 4 agencies: 21.
Plant-grade families (ITA/OSHA/ECHO worksite addresses) per cluster (unit: clusters): STRONG 1: 38; 2: 439; 3: 514; CORROBORATED 0: 76; 1: 1,000; 2: 2,012. A cluster with 0 plant-grade families is HQ-grade evidence only (flag `hq_grade_sources_only`, score -4).
Atlas relation of the lead table (unit: clusters): `NET_NEW` 25,180; `HELD_ORG_OTHER_LOCATION` 1,167; `ADDRESS_AT_HELD_SITE_NAME_DIFFERS` 25. `HELD_ORG_OTHER_LOCATION` = a held org of this name or EIN exists in the state with no site at this location (likely a new SITE of an existing org, a different create path from a net-new org).

### 2.4 By state (unit: clusters in `clusters.csv`)

| State | STRONG | CORROBORATED | SINGLE | Total | of which NET_NEW |
|---|---:|---:|---:|---:|---:|
| MI | 106 | 198 | 1,119 | 1,423 | 1,352 |
| CA | 78 | 262 | 3,352 | 3,692 | 3,646 |
| IL | 61 | 195 | 1,081 | 1,337 | 1,278 |
| MA | 56 | 88 | 700 | 844 | 826 |
| IN | 53 | 145 | 696 | 894 | 817 |
| MN | 48 | 119 | 446 | 613 | 588 |
| WI | 47 | 125 | 537 | 709 | 663 |
| TX | 42 | 233 | 1,468 | 1,743 | 1,655 |
| NC | 35 | 110 | 675 | 820 | 766 |
| GA | 34 | 147 | 781 | 962 | 913 |
| NY | 34 | 81 | 806 | 921 | 908 |
| NJ | 32 | 91 | 883 | 1,006 | 983 |
| TN | 31 | 90 | 474 | 595 | 569 |
| KY | 29 | 79 | 236 | 344 | 326 |
| FL | 25 | 103 | 901 | 1,029 | 1,011 |
| VA | 24 | 51 | 509 | 584 | 572 |
| AL | 24 | 61 | 354 | 439 | 415 |
| OH | 20 | 98 | 963 | 1,081 | 856 |
| CT | 19 | 41 | 269 | 329 | 323 |
| PA | 18 | 91 | 898 | 1,007 | 903 |
| MO | 15 | 63 | 475 | 553 | 536 |
| SC | 14 | 80 | 420 | 514 | 488 |
| KS | 13 | 38 | 221 | 272 | 252 |
| WA | 12 | 28 | 338 | 378 | 373 |
| IA | 11 | 52 | 237 | 300 | 288 |

Top 25 of 54 states by STRONG count shown; all states are in `clusters.csv`. The QCEW gap states (`docs/denominators/README.md`: QCEW 2023 private establishments, NAICS 326, minus Atlas strict 326 sites) rank CA, TX, FL, MI, IL, GA, IN, WI, NY, NC highest; lead counts here are **not** an estimate of that gap (the sources cover inspected, permitted, plan-sponsoring or contract-winning units; QCEW counts reporting units of every size).

`top_leads_by_state.csv` holds the top 50 clusters per state by `score` (ties: more sources, larger size band, more recent activity) for CA, TX, FL, MI, IL, GA, IN, WI, NY, NC, OH, PA, with `state_rank`; it includes every class, so a state with fewer than 50 multi-source leads is filled with CORROBORATED then SINGLE rows. Rows per state: CA 50; TX 50; FL 50; MI 50; IL 50; GA 50; IN 50; WI 50; NY 50; NC 50; OH 50; PA 50. The patents pilot covers OH and PA only, so only those two states can carry a sixth family.

## 3. Reconciliation against each source packet's published counts (AGENTS section 2 rule 10)

| Family | Published NO_MATCH | Read NO_MATCH | Published POSSIBLE | Read POSSIBLE | Published total | Read total | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| ITA | 9,145 | 9,145 | 346 | 346 | 11,194 | 11,194 | reconciles |
| OSHA | 5,256 | 5,256 | 246 | 246 | 6,473 | 6,473 | reconciles |
| ECHO | 13,255 | 13,255 | 315 | 315 | 15,920 | 15,920 | reconciles |
| F5500 | 4,581 | 4,581 | 418 | 418 | 5,897 | 5,897 | reconciles |
| USASPEND | 4,450 | 4,450 | 77 | 77 | 4,756 | 4,756 | reconciles |
| PATENT | 230 | 230 | 71 | 71 | 414 | 414 | reconciles |

Published figures are copied from each packet's REPORT.md (ITA section 3: 9,145 / 346 of 11,194; OSHA section 3: 5,256 / 246 of 6,473; ECHO section 2: 13,255 / 315 of 15,920; Form 5500 section 4: 4,581 / 418 of 5,897; USAspending section 3: 4,450 NO_MATCH + 77 POSSIBLE_REVIEW of 4,756; patents section 3: 230 / 71 of 414). **Result: all six families reconcile exactly (NO_MATCH, POSSIBLE and total), row for row.**

Sub-split checks: ITA NO_MATCH in core-family scope classes (core_P/S/X/unlisted) 4,921 vs published 4,921 (ok); ITA core_P NO_MATCH 4,376 vs published 4,376 (ok); ECHO core NO_MATCH 12,141 vs published 12,141 and ring3_primary 1,114 vs 1,114 (ok). Record-ID uniqueness (rule 10b) is asserted on load per source (ITA establishment_ID, OSHA est_key, FRS registry_id, Form 5500 EIN, UEI, assignee_id) and across families on the `family:id` key; every input row lands in exactly one cluster (asserted). The inputs are source rows, not build-pass allocation rows, so rule 10a's creation-class whitelist has no marker, flip, repoint or fold rows to exclude.

**Cross-check against the ITA packet's own `cross_source` field (rule 10c: a conflicting count is investigated, not explained away).** The ITA report published 1,003 of 4,376 core_P NO_MATCH ITA establishments as also listed by the inspection lane (`BOTH_SOURCES`) plus 138 `BOTH_ADDRESS_NAME_DIFFERS`. Re-derived from the ITA `site_matches.csv` over the same 4,376 rows: `cross_source` = BOTH_ADDRESS_NAME_DIFFERS 138; BOTH_SOURCES 1,003; ITA_ONLY 3,235. The fusion puts an ITA core_P NO_MATCH row in a cluster that holds an OSHA NO_MATCH row as follows (ITA-reported `cross_source` | cluster holds an OSHA NO_MATCH row): BOTH_ADDRESS_NAME_DIFFERS | False: 116; BOTH_ADDRESS_NAME_DIFFERS | True: 22; BOTH_SOURCES | False: 18; BOTH_SOURCES | True: 985; ITA_ONLY | False: 3,066; ITA_ONLY | True: 169. Same, counting an OSHA row of any verdict: BOTH_ADDRESS_NAME_DIFFERS | False: 116; BOTH_ADDRESS_NAME_DIFFERS | True: 22; BOTH_SOURCES | False: 18; BOTH_SOURCES | True: 985; ITA_ONLY | False: 3,064; ITA_ONLY | True: 171.

Where the two disagree (unit: ITA core_P NO_MATCH rows). The ITA packet says BOTH_SOURCES but the fusion has no OSHA NO_MATCH row in the cluster: same street, names incompatible (name guard): 12; street / ZIP spelling beyond the merge rules, or no OSHA street key: 6. The ITA packet says ITA_ONLY or BOTH_ADDRESS_NAME_DIFFERS but the fusion joined an OSHA row, by edge basis: BOTH_ADDRESS_NAME_DIFFERS via `housenum_zip_name`: 1; BOTH_ADDRESS_NAME_DIFFERS via `housenum_zip_name+street_zip`: 5; BOTH_ADDRESS_NAME_DIFFERS via `street_zip`: 16; ITA_ONLY via `ein+name_locality+housenum_zip_name+street_zip`: 1; ITA_ONLY via `ein_locality+housenum_zip_name`: 1; ITA_ONLY via `housenum_zip_name`: 79; ITA_ONLY via `housenum_zip_name+name_locality`: 1; ITA_ONLY via `housenum_zip_name+street_city_zip_differs`: 2; ITA_ONLY via `housenum_zip_name+street_zip`: 76; ITA_ONLY via `name_locality`: 5; ITA_ONLY via `name_locality+street_zip`: 2; ITA_ONLY via `weak_name_locality`: 2.

**Reading of the cross-check.** The ITA packet's published figures reproduce exactly from its own file (1,003 BOTH_SOURCES, 138 BOTH_ADDRESS_NAME_DIFFERS, 3,235 ITA_ONLY), so there is no count error to chase. The fusion's ITA-OSHA overlaps differ from the packet's because the two use different join rules, and the differences have identified causes. (i) The fusion is looser on address spelling: its house-number + ZIP5 + shared-street-word edge and its same-street-same-city edge that tolerates a ZIP5 disagreement join rows the ITA ladder left as ITA_ONLY ('Dr' vs 'Ave', 'N' vs 'S' Van Dyke, '4378 South M-18' vs '4378 M18', a mistyped ZIP). I read 28 of these joins by hand during development (14 ITA_ONLY and 14 BOTH_ADDRESS_NAME_DIFFERS): all were one address and one company. (ii) The fusion is stricter on names where the street is equal: the ITA packet counts a pair as BOTH_SOURCES on a street match plus agreement on either of ITA's two name fields, while the fusion needs a compatible name among all name variants of both rows; the 12 BOTH_SOURCES rows it does not join are same-address rows under incompatible names (Amcor / Berry Global, USG / United States Gypsum, Return Polymers / Butler-MacDonald, Zip-Pak / ITW with a ZIP typo ...), which are kept apart and cross-referenced in `related_clusters` (`colocated_other_name:`). (iii) Six BOTH_SOURCES rows differ in street form beyond the merge rules (for example a street written only as a PO box, or `#6 Capper Drive`, which `atlas.street_key` strips to nothing). Net: ITA core_P NO_MATCH rows that share a cluster with an OSHA NO_MATCH row are higher in the fusion than the packet's 1,003 plus 138; the extra joins are explained by (i), the shortfall by (ii) and (iii). Nothing was explained away: each class has a count above.

## 4. Cluster quality: false-cluster audit

**Hand-style audit of 30 random multi-source clusters** (the 30 clusters with the smallest `sha1(fingerprint + 'audit')` among the 4,079 lead-table clusters with at least 2 families, where the fingerprint is a hash of the member row keys, so the draw is deterministic and stable when unrelated clusters change; each is printed in 4.1 with its rows and judged on address, name, city/ZIP and identifiers by reading the rows, not by re-running the clustering rule):

- **OK** (all rows plausibly one establishment): 30; **DOUBTFUL** (plausible, but a step I would not accept without a primary check): 0; **FALSE** (rows from different establishments merged): 0.
- **Observed false-cluster rate: 0/30 = 0.0%** (95% Wilson interval 0.0% to 11.4%); counting DOUBTFUL as false: 0/30 = 0.0%. A sample of 30 cannot resolve a rate below roughly 10%; read it as an order of magnitude.
- **Automatic screen over all 4,079 lead-table clusters with at least 2 families:** 29 (0.7%) contain a row whose names are incompatible with every row of every other family (it joined by address or EIN, not by name). This is an upper-bound suspect flag, not a false rate: ECHO facility labels, ITA plant labels and parent-versus-operator names legitimately differ.
- **Cost of the name guard:** 2,297 same-address row pairs were not merged because the names are incompatible (4.2 samples them).

### 4.1 Audit sample (printed)

```
LF-CA-00993 [e15009e0]  rows=2 families=ITA,ECHO edge_bases=housenum_zip_name
  ITA      1468401          | North America Vista / Jeld-Wen Inc. | 2760-B Progress St | Vista, CA 92083 | naics 326199 | ein 930496342 | NO_MATCH
  ECHO     110057054191     | JELD-WEN INC | 2760 PROGRESS ST, SUITE B | VISTA, CA 92083 | naics 326199 | ein - | NO_MATCH
```
Verdict: **OK** - '2760-B' vs 'Suite B': one address.

```
LF-CA-01162 [b8517f5b]  rows=2 families=ECHO,F5500 edge_bases=street_zip
  ECHO     110066544314     | MAGSPHERE INC | 1993 LOCUST ST | PASADENA, CA 91107 | naics 325211 | ein - | NO_MATCH
  F5500    954163360        | MAGSPHERE, INC. | 1993 LOCUST ST | PASADENA, CA 91107 | naics 325900 | ein 954163360 | NO_MATCH
```
Verdict: **OK**

```
LF-CA-02867 [2bb7a223]  rows=2 families=ITA,F5500 edge_bases=street_zip
  ITA      878414           | Argo Chemical, Inc. | 30933 Imperial Street | Bakersfield, CA 93263 | naics 424690 | ein 953631863 | NO_MATCH
  F5500    953631863        | ARGO CHEMICAL, INC. | 30933 IMPERIAL STREET | BAKERSFIELD, CA 93263 | naics 325900 | ein 953631863 | NO_MATCH
```
Verdict: **OK**

```
LF-GA-00388 [ce6a8169]  rows=3 families=ITA,OSHA,ECHO edge_bases=housenum_zip_name
  ITA      1479817          | Enchem America, Inc. | 648 Highway 334 | Commerce, GA 30530 | naics 325998 | ein - | NO_MATCH
  OSHA     OSHAE-96ef309a70 | ENCHEM AMERICA, INC. | 648 GEORGIA 334 | COMMERCE, GA 30530 | naics 325998 | ein - | NO_MATCH
  ECHO     110072045046     | ENCHEM AMERICA INC | 648 GA HWY 334 | COMMERCE, GA 30530 | naics 325998 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-IA-00146 [b7e12718]  rows=2 families=OSHA,ECHO edge_bases=street_zip
  OSHA     OSHAE-7e882ea11f | DECKER PACKAGING, INC. | 1104 2ND AVE | COUNCIL BLUFFS, IA 51501 | naics 326111 | ein - | NO_MATCH
  ECHO     110070207154     | DECKER PLASTICS INC | 1104 2ND AVE | COUNCIL BLUFFS, IA 51501 | naics 326111 | ein - | NO_MATCH
```
Verdict: **OK** - Decker Packaging / Decker Plastics at one address (a name change at one plant, not two plants).

```
LF-IL-00995 [b280902e]  rows=3 families=ITA,OSHA edge_bases=street_zip
  ITA      120812           | Lyondellbasell Morris Site / Lyondellbasell | 8805 North Tabler Rd | Morris, IL 60450 | naics 325211 | ein - | NO_MATCH
  OSHA     OSHAE-5638a966d9 | LYONDELL BASELL INDUSTRIES | 8805 NORTH TABLER ROAD | MORRIS, IL 60450 | naics 325211 | ein - | NO_MATCH
  OSHA     OSHAE-6ae749daad | LYONDELLBASELL INDUSTRIES | 8805 NORTH TABLER ROAD | MORRIS, IL 60450 | naics 325211 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-KY-00008 [e50daef7]  rows=2 families=ITA,ECHO edge_bases=street_zip
  ITA      799094           | Clariant Corporation South / Clariant Corporation | 4900 Crittenden Drive | Louisville, KY 40209 | naics 325180 | ein 561356629 | NO_MATCH
  ECHO     110000378378     | CLARIANT CORPORATION, LOUISVILLE SOUTH PLANT | 4900 CRITTENDEN DRIVE | LOUISVILLE, KY 40209 | naics 325998 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-LA-00234 [9f0343f5]  rows=3 families=OSHA,ECHO,F5500 edge_bases=street_zip
  OSHA     OSHAE-8bb953597c | CORNERSTONE CHEMICAL COMPANY, LLC | 10800 RIVER ROAD | WESTWEGO, LA 70094 | naics 325211,325212 | ein - | NO_MATCH
  ECHO     110049249075     | CORNERSTONE CHEMICAL CO LLC | 10800 RIVER RD | WAGGAMAN, LA 70094 | naics 325211 325998 326199 | ein - | NO_MATCH
  F5500    273966965        | CORNERSTONE CHEMICAL COMPANY | 10800 RIVER ROAD | WAGGAMAN, LA 70094 | naics 325900 | ein 273966965 | NO_MATCH
```
Verdict: **OK** - Westwego / Waggaman postal names, same street and ZIP.

```
LF-MA-00039 [7017b98b]  rows=3 families=ECHO,F5500 edge_bases=street_zip
  ECHO     110000310690     | SAVOGRAN COMPANY | 259 LENOX STREET | NORWOOD, TOWN OF, MA 02062 | naics 325510 | ein - | NO_MATCH
  ECHO     110070631183     | SAVOGRAN COMPANY | 259 LENOX ST | NORWOOD, MA 02062 | naics 325510 | ein - | NO_MATCH
  F5500    041810570        | THE SAVOGRAN COMPANY | 259 LENOX STREET UNIT 6201 | NORWOOD, MA 02062 | naics 325500 | ein 041810570 | NO_MATCH
```
Verdict: **OK**

```
LF-MA-00548 [0388adb0]  rows=4 families=ITA,F5500,USASPEND edge_bases=street_zip
  ITA      1414580          | Accutech Packaging, Inc. | 157 GREEN STREET | Foxboro, MA 02035 | naics 326112 | ein 043022162 | NO_MATCH
  ITA      1414581          | Accutech Packaging, Inc. - West St / Accutech Packaging, Inc. | 157 GREEN STREET | Foxboro, MA 02035 | naics 326199 | ein 043022162 | NO_MATCH
  F5500    043022162        | ACCUTECH PACKAGING, INC. | 157 GREEN STREET | FOXBORO, MA 02035 | naics 326100 | ein 043022162 | NO_MATCH
  USASPEND HGV6K3W41RX3     | ACCUTECH PACKAGING, INC. | 157 GREEN ST | FOXBORO, MA 02035 | naics 326130,326112 | ein - | NO_MATCH
```
Verdict: **OK** - Two ITA filings at one address (a 'West St' label on the second).

```
LF-MD-00028 [1d11a356]  rows=3 families=ITA,ECHO,F5500 edge_bases=street_zip
  ITA      1440509          | Baltimore Plant / USALCO, LLC | 2601 Cannery Avenue | Baltimore, MD 21226 | naics 325180 | ein 271125234 | NO_MATCH
  ECHO     110000867161     | USALCO LLC | 2601 CANNERY AVE | CURTIS BAY, MD 21226 | naics 325998 | ein - | NO_MATCH
  F5500    271125234        | USALCO, LLC | 2601 CANNERY AVENUE | BALTIMORE, MD 21226 | naics 325900 | ein 271125234 | NO_MATCH
```
Verdict: **OK** - Baltimore / Curtis Bay postal names, same street and ZIP.

```
LF-MI-00113 [ac53df13]  rows=3 families=OSHA,ECHO,F5500 edge_bases=street_zip
  OSHA     OSHAE-aec6004439 | DIVERSIFIED ENGINEERING & PLASTICS LLC | 1801 WILDWOOD AVE | JACKSON, MI 49202 | naics 326199 | ein - | NO_MATCH
  ECHO     110000822771     | DIVERSIFIED ENGINEERING & PLASTICS LLC | 1801 WILDWOOD AVENUE | JACKSON, MI 49202 | naics 326199 | ein - | NO_MATCH
  F5500    274523742        | DIVERSIFIED ENGINEERING & PLASTICS, LLC | 1801 WILDWOOD AVENUE | JACKSON, MI 49202 | naics 326100 | ein 274523742 | NO_MATCH
```
Verdict: **OK**

```
LF-MI-00848 [e0079bd0]  rows=2 families=ITA,F5500 edge_bases=street_zip
  ITA      1355187          | The DECC Company | 1266 Wallen Ave SW | Grand Rapids, MI 49507 | naics 325510 | ein 381723933 | NO_MATCH
  F5500    381723933        | THE DECC COMPANY, INC. | 1266 WALLEN AVENUE SW | GRAND RAPIDS, MI 49507 | naics 325500 | ein 381723933 | NO_MATCH
```
Verdict: **OK**

```
LF-MI-00874 [be818d62]  rows=2 families=ITA,F5500 edge_bases=street_zip
  ITA      204533           | Midwest Plastic Engineering, Inc. | 1501 Progress St. | Sturgis, MI 49091 | naics 326199 | ein 382112796 | NO_MATCH
  F5500    382112796        | MIDWEST PLASTIC ENGINEERING INC | 1501 PROGRESS ST | STURGIS, MI 49091 | naics 326100 | ein 382112796 | NO_MATCH
```
Verdict: **OK**

```
LF-MI-01231 [10b3a910]  rows=2 families=ITA,OSHA edge_bases=street_zip
  ITA      175745           | Faith Plastics LLC / Faith Plastics, LLC | 239 E. Main St. | Marcellus, MI 49067 | naics 326199 | ein 461636714 | NO_MATCH
  OSHA     OSHAE-0177aa0c12 | FAITH PLASTICS | 239 E MAIN ST | MARCELLUS, MI 49067 | naics 326199 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-MI-01244 [bcbb7b72]  rows=2 families=ITA,OSHA edge_bases=housenum_zip_name
  ITA      304082           | Flexfab LLC - Main / Flexfab | 1699 W. M-43 Highway | Hastings, MI 49058 | naics 326220 | ein 381674842 | NO_MATCH
  OSHA     OSHAE-17d0c16e07 | FLEXFAB LLC | 1699 W M43 HWY | HASTINGS, MI 49058 | naics 326220 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-MN-00208 [829efa2b]  rows=2 families=OSHA,ECHO edge_bases=street_zip
  OSHA     OSHAE-03828bca24 | MINNESOTA DIVERSIFIED INDUSTRIES INC | 11270 HWY 37 | HIBBING, MN 55746 | naics 326199 | ein - | NO_MATCH
  ECHO     110070260569     | MINNESOTA DIVERSIFIED INDUSTRIES INC | 11270 HIGHWAY 37 | HIBBING, MN 55746 | naics 326130 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-MN-00288 [aca246c5]  rows=2 families=ITA,F5500 edge_bases=street_zip
  ITA      899105           | HQ Facility / Lakeview Industries, Inc. | 2100 Commerce Drive | Carver, MN 55315 | naics 326291 | ein 411427378 | NO_MATCH
  F5500    411427378        | LAKEVIEW INDUSTRIES, INC. | 2100 COMMERCE DRIVE | CARVER, MN 55315 | naics 326200 | ein 411427378 | NO_MATCH
```
Verdict: **OK** - ITA 'HQ Facility' label; Form 5500 sponsor at the same street.

```
LF-MO-00241 [c7347cc1]  rows=3 families=ITA,OSHA,ECHO edge_bases=street_zip
  ITA      548398           | JM Eagle PCO / JM Eagle | 6500 N. Brown Station Rd | Columbia, MO 65202 | naics 326122 | ein 840895616 | NO_MATCH
  OSHA     OSHAE-cba2edc6eb | JM EAGLE | 6500 N BROWN STATION RD | COLUMBIA, MO 65202 | naics 326122 | ein - | NO_MATCH
  ECHO     110038041053     | J M EAGLE, INC. | 6500 N. BROWN STATION ROAD | COLUMBIA, MO 65202 | naics 326122 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-NC-00259 [411dc8ce]  rows=3 families=ITA,ECHO edge_bases=street_zip
  ITA      952381           | Clear Path Recycling, LLC. | 3500 Cedar Creek Rd. | Fayetteville, NC 28312 | naics 325991 | ein 832978147 | NO_MATCH
  ECHO     110039574092     | CLEAR PATH RECYCLING, LLC | 3500 CEDAR CREEK RD | FAYETTEVILLE, NC 28312 | naics 325991 326199 | ein - | NO_MATCH
  ECHO     110041271922     | CLEAR PATH RECYCLING, LLC | 3500 CEDAR CREEK RD | FAYETTEVILLE, NC 28312 | naics 325991 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-ND-00009 [00dcba43]  rows=2 families=OSHA,ECHO edge_bases=street_zip
  OSHA     OSHAE-4366ad1c15 | ICE CRYSTAL ENGINEERING | 5074 165TH AVENUE SOUTHEAST | KINDRED, ND 58051 | naics 325998 | ein - | NO_MATCH
  ECHO     110038859054     | ICE CRYSTAL ENGINEERING | 5074 165TH AVENUE SE | KINDRED, ND 58051 | naics 325998 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-NY-00096 [943cef0e]  rows=2 families=ITA,ECHO edge_bases=street_zip
  ITA      960475           | Transcontinental Packaging Brooklyn / TC Transcontinental | 975 Essex Street | Brooklyn, NY 11208 | naics 326111 | ein 112327083 | NO_MATCH
  ECHO     110000809046     | TRANSCONTINENTAL ULTRA FLEX INC. | 975 ESSEX ST | BROOKLYN, NY 11208 | naics 326111 326112 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-NY-00377 [db340bb5]  rows=2 families=ITA,ECHO edge_bases=street_zip
  ITA      1567190          | NA Syracuse / HB Fuller | 3584 Walters Road | Syracuse, NY 13209 | naics 325520 | ein 275492324 | NO_MATCH
  ECHO     110071679300     | HB FULLER SYRACUSE | 3584 WALTERS RD | SYRACUSE, NY 13209 | naics 325520 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-OR-00176 [1e3990b1]  rows=2 families=ITA,OSHA edge_bases=street_zip
  ITA      1460688          | DRAVON MEDICAL | 11465 SE HIGHWAY 212 | CLACKAMAS, OR 97015 | naics 326111 | ein 931020493 | NO_MATCH
  OSHA     OSHAE-3f20239e24 | DRAVON MEDICAL INC | 11465 SE HIGHWAY 212 | CLACKAMAS, OR 97015 | naics 326111 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-TN-00284 [01e042be]  rows=2 families=ITA,ECHO edge_bases=street_zip
  ITA      158581           | Woodbridge Chattanooga Formed Plastics | 51 Lost Mound Drive Suite 115 | Chattanooga, TN 37406 | naics 326150 | ein 461500241 | NO_MATCH
  ECHO     110070060793     | WOODBRIDGE CHATTANOOGA FORMED PLASTICS LP (PLANT #1) | 51 LOST MOUND DRIVE | CHATTANOOGA, TN 37406 | naics 326140 326150 | ein - | NO_MATCH
```
Verdict: **OK**

```
LF-TN-00358 [280a4bac]  rows=2 families=ITA,F5500 edge_bases=street_zip
  ITA      939926           | BEENE HOLDINGS, INC. / BEENE HOLDINGS, INC | 213 DENNIS STREET | ATHENS, TN 37303 | naics 326199 | ein 620520388 | NO_MATCH
  F5500    620520388        | BEENE HOLDINGS, INC. | 213 DENNIS ST. | ATHENS, TN 37303 | naics 326100 | ein 620520388 | NO_MATCH
```
Verdict: **OK**

```
LF-TN-00368 [ff281869]  rows=3 families=ITA,OSHA,F5500 edge_bases=street_zip
  ITA      1560001          | Hamilton Plastics | 2641 Riverport Rd | Chattanooga, TN 37406 | naics 326111 | ein 621281383 | NO_MATCH
  OSHA     OSHAE-227342fbcc | HAMILTON PLASTICS, INC. | 2641 RIVERPORT ROAD | CHATTANOOGA, TN 37406 | naics 326111 | ein - | NO_MATCH
  F5500    621281383        | HAMILTON PLASTICS, INC. | 2641 RIVERPORT ROAD | CHATTANOOGA, TN 37406 | naics 326100 | ein 621281383 | NO_MATCH
```
Verdict: **OK**

```
LF-UT-00140 [724078db]  rows=2 families=ITA,OSHA edge_bases=housenum_zip_name
  ITA      1274825          | A.R. Arena Products Inc.  UTAH / A.R. Arena Products Inc. | 216 N 700 W Building 4C Bay 5 | OGDEN, UT 84404 | naics 326111 | ein 161204957 | NO_MATCH
  OSHA     OSHAE-a307e61b5f | A.R. ARENA PRODUCTS, INC. | 216 W 700 N BLDG 4C, BAY 5 | OGDEN, UT 84404 | naics 326199 | ein - | NO_MATCH
```
Verdict: **OK** - Utah grid address written 216 N 700 W vs 216 W 700 N (transposed), same building and bay.

```
LF-WA-00212 [426a1670]  rows=2 families=ITA,F5500 edge_bases=street_zip
  ITA      411106           | Moses Lake Industries / Moses Lake Industries, Inc. | 8248 Randolph Road NE | Moses Lake, WA 98837 | naics 325193 | ein - | NO_MATCH
  F5500    911252522        | MOSES LAKE INDUSTRIES | 8248 RANDOLPH ROAD NE | MOSES LAKE, WA 98837 | naics 325900 | ein 911252522 | NO_MATCH
```
Verdict: **OK**

```
LF-WV-00060 [4fb3afb6]  rows=3 families=ITA,OSHA,ECHO edge_bases=street_zip
  ITA      958826           | ISCO Industries, Inc - Martinsburg / ISCO industries, Inc | 701 Mid Atlantic Parkway | Martinsburg, WV 25404 | naics 326191 | ein - | NO_MATCH
  OSHA     OSHAE-d0f884b6b7 | ISCO INDUSTRIES, INC. | 701 MID ATLANTIC PARKWAY | MARTINSBURG, WV 25404 | naics 326191 | ein - | NO_MATCH
  ECHO     110070646040     | ISCO INDUSTRIES LLC | 701 MID ATLANTIC PARKWAY | MARTINSBURG, WV 25404 | naics 326122 | ein - | NO_MATCH
```
Verdict: **OK**

### 4.1b Stratified supplement: the weaker merge bases

The random draw is dominated by `street_zip` merges (the strongest basis). To measure the weaker bases, up to 8 further multi-source clusters were drawn per basis (same fingerprint ordering, salted by basis name; a cluster can carry several bases, so strata overlap) and judged the same way. Population = lead-table clusters with at least 2 families whose `cluster_basis` contains the basis.

| Basis | Population (clusters) | Drawn | OK | DOUBTFUL | FALSE |
|---|---:|---:|---:|---:|---:|
| `housenum_zip_name` | 699 | 8 | 8 | 0 | 0 |
| `street_city_zip_differs` | 159 | 8 | 8 | 0 | 0 |
| `name_locality` | 65 | 8 | 8 | 0 | 0 |
| `ein_locality` | 76 | 8 | 8 | 0 | 0 |
| `weak_name_locality` | 29 | 8 | 6 | 2 | 0 |

```
[housenum_zip_name] LF-IA-00094 [653657b2]  rows=2 families=OSHA,ECHO edge_bases=housenum_zip_name
  OSHA     OSHAE-4a98cea671 | CRYOTECH DEICING TECHNOLOGY | 6103 ORTHOWAY | FORT MADISON, IA 52627 | naics 325998 | ein - | NO_MATCH
  ECHO     110011273317     | CRYOTECH DEICING TECHNOLOGY | 6103 ORTHO WAY | FORT MADISON, IA 52627 | naics 325998 | ein - | NO_MATCH
```
Verdict: **OK**

```
[housenum_zip_name] LF-IL-00122 [ede2a496]  rows=4 families=ITA,OSHA,ECHO edge_bases=housenum_zip_name,street_city_zip_differs,street_zip
  ITA      1302405          | SIKA UGL United Gilsonite Laboratories / SIKA UGL United Gilsoni | 550 Capital Way | Jacksonville, IL 62650 | naics 325510 | ein - | NO_MATCH
  OSHA     OSHAE-11ec0906dd | UNITED GILSONITE LABORATORIES, INC. | 550 CAPITAL WAY | JACKSONVILLE, IL 62650 | naics 325510 | ein - | NO_MATCH
  OSHA     OSHAE-c105e30581 | SIKA CORPORATION | 550 CAPITOL WAY | JACKSONVILLE, IL 62650 | naics 325510 | ein - | NO_MATCH
  ECHO     110000439650     | SIKA CORPORATION | 550 CAPITOL WAY | JACKSONVILLE, IL 62651 | naics 325510 | ein - | NO_MATCH
```
Verdict: **OK** - 'Capital' vs 'Capitol' Way; Sika acquired United Gilsonite (one plant).

```
[housenum_zip_name] LF-KS-00113 [738e0bc5]  rows=3 families=ITA,ECHO edge_bases=housenum_zip_name,street_zip
  ITA      1565280          | Pitt Plastics, Inc. / Inteplast Group | 1400 East Atkinson Ave. | Pittsburg, KS 66762 | naics 326111 | ein 480782135 | NO_MATCH
  ITA      1565427          | Pitt Plastics - Pittsburg Kansas / Inteplast Group | 1400 E. Atkinson Ave. | Pittsburg, KS 66762 | naics 326111 | ein 480782135 | NO_MATCH
  ECHO     110055253755     | PITT PLASTICS, INC. | 1400 ATKINSON AVE. | PITTSBURG, KS 66762 | naics 326199 | ein - | NO_MATCH
```
Verdict: **OK**

```
[housenum_zip_name] LF-MI-00368 [dff91565]  rows=2 families=ECHO,F5500 edge_bases=housenum_zip_name
  ECHO     110007586914     | PAUL MURPHY PLASTICS CO | 15301 E 11 MILE RD | ROSEVILLE, MI 48066 | naics 326121 | ein - | NO_MATCH
  F5500    381719734        | PAUL MURPHY PLASTICS COMPANY | 15301 ELEVEN MILE ROAD | ROSEVILLE, MI 48066 | naics 326100 | ein 381719734 | NO_MATCH
```
Verdict: **OK**

```
[housenum_zip_name] LF-MI-01103 [512cbe01]  rows=2 families=ITA,USASPEND edge_bases=housenum_zip_name
  ITA      1286854          | Cayman Chemical Inc / CAYMAN CHEMICAL COMPANY | 1180 E Ellsworth | ANN ARBOR, MI 48108 | naics 325199 | ein 840845784 | NO_MATCH
  USASPEND T1ZHJRGR7TF4     | CAYMAN CHEMICAL CO INC | 1180 E ELLSWORTH RD | ANN ARBOR, MI 48108 | naics 325998 | ein - | NO_MATCH
```
Verdict: **OK**

```
[housenum_zip_name] LF-OH-00072 [511d16f3]  rows=2 families=OSHA,ECHO edge_bases=housenum_zip_name
  OSHA     OSHAE-74fe5a5dbc | BEMIS COMPANY, INC. | 1972 AKRON PENNINSULA ROAD | AKRON, OH 44313 | naics 325211 | ein - | NO_MATCH
  ECHO     110000389473     | BEMIS COMPANY INC | 1972 AKRON PENISULA ROAD | AKRON, OH 44313 | naics 326112 | ein - | NO_MATCH
```
Verdict: **OK**

```
[housenum_zip_name] LF-OK-00198 [710a2b15]  rows=2 families=ITA,USASPEND edge_bases=housenum_zip_name
  ITA      158200           | Tulsa-Peoria / Airgas USA, LLC | 31 N. Peoria | Tulsa, OK 74120 | naics 424690 | ein 560732648 | NO_MATCH
  USASPEND E9JEP9ACJHD1     | AIRGAS USA, LLC | 31 N PEORIA AVE | TULSA, OK 74120 | naics 325992 | ein - | NO_MATCH
```
Verdict: **OK**

```
[housenum_zip_name] LF-TN-00256 [64e3110a]  rows=2 families=ITA,ECHO edge_bases=housenum_zip_name
  ITA      948980           | Ideal Chemical & Supply Co | 4025 AIR PARK | MEMPHIS, TN 38118 | naics 424690 | ein 620245980 | NO_MATCH
  ECHO     110062843892     | IDEAL CHEMICAL & SUPPLY CO | 4025 AIR PARK STREET | MEMPHIS, TN 38118 | naics 325998 | ein - | NO_MATCH
```
Verdict: **OK**

```
[street_city_zip_differs] LF-AL-00238 [bdc62d50]  rows=2 families=ITA,ECHO edge_bases=street_city_zip_differs
  ITA      893140           | KW Plastics of Troy | 1 Sanders Road | Troy, AL 36079 | naics 325991 | ein - | NO_MATCH
  ECHO     110070828266     | KW PLASTICS | 1 SANDERS RD | TROY, AL 36081 | naics 325991 | ein - | NO_MATCH
```
Verdict: **OK**

```
[street_city_zip_differs] LF-GA-00033 [bea3b0d3]  rows=5 families=ITA,OSHA,ECHO edge_bases=street_city_zip_differs,street_zip
  ITA      693675           | Millwork & Panel LLC- Social Circle / CertainTeed LLC | 200 Ronthor Drive | Social Circle, GA 30025 | naics 326199 | ein 320613145 | NO_MATCH
  OSHA     OSHAE-6214022b6c | MILLWORK & PANEL LLC | 200 RONTHOR DRIVE | SOCIAL CIRCLE, GA 30025 | naics 326199 | ein - | NO_MATCH
  OSHA     OSHAE-fd6cfd6c71 | CERTAINTEED GYPSUM AND CEILING MANUFACTURING, INC | 200 RONTHOR DRIVE | SOCIAL CIRCLE, GA 30025 | naics 326199 | ein - | NO_MATCH
  ECHO     110000357382     | MILLWORK & PANEL- SOCIAL CIRCLE | 200 RONTHOR DR. | SOCIAL CIRCLE, GA 30025 | naics 326121 326199 | ein - | NO_MATCH
  ECHO     110070159245     | MILLWORK & PANEL, LLC - SOCIAL CIRCLE GA PLANT | 200 RONTHOR DR | SOCIAL CIRCLE, GA 30255 | naics 326199 | ein - | NO_MATCH
```
Verdict: **OK** - Millwork & Panel / CertainTeed (owner) at one address.

```
[street_city_zip_differs] LF-GA-00080 [a80e7b4f]  rows=3 families=OSHA,ECHO,F5500 edge_bases=street_city_zip_differs,street_zip
  OSHA     OSHAE-ec014ca03a | AUSTIN URETHANE, INC. | 122 CRISP DRIVE | AMERICUS, GA 31709 | naics 326150 | ein - | NO_MATCH
  ECHO     110000741001     | AUSTIN URETHANE INC. | 122 CRISP DRIVE | AMERICUS, GA 31719 | naics 326150 | ein - | NO_MATCH
  F5500    581269426        | AUSTIN URETHANE, LLC | 122 CRISP DRIVE | AMERICUS, GA 31719 | naics 326100 | ein 581269426 | NO_MATCH
```
Verdict: **OK**

```
[street_city_zip_differs] LF-MA-00004 [e0a1472c]  rows=2 families=ECHO,USASPEND edge_bases=street_city_zip_differs
  ECHO     110000308257     | CYALUME TECHNOLOGIES INC. | 96 WINDSOR STREET | WEST SPRINGFIELD, MA 01090 | naics 325998 | ein - | NO_MATCH
  USASPEND JHNVAB4HLEB8     | CYALUME TECHNOLOGIES INC | 96 WINDSOR ST | WEST SPRINGFIELD, MA 01089 | naics 325211 | ein - | NO_MATCH
```
Verdict: **OK**

```
[street_city_zip_differs] LF-NC-00005 [3abdab36]  rows=2 families=ITA,ECHO edge_bases=street_city_zip_differs
  ITA      1528924          | AXALTA COATING SYSTEMS | 1717 ENGLISH ROAD | High Point, NC 27262 | naics 325510 | ein - | NO_MATCH
  ECHO     110000345760     | AXALTA COATING SYSTEMS U.S.A., LLC 2 | 1717 ENGLISH RD | HIGH POINT, NC 27261 | naics 325510 | ein - | NO_MATCH
```
Verdict: **OK**

```
[street_city_zip_differs] LF-NC-00709 [85d8e201]  rows=2 families=ITA,OSHA edge_bases=street_city_zip_differs
  ITA      1505651          | Rempac LLC | 2005 STARLITE DR. | LUMBERTON, NC 28360 | naics 326150 | ein - | NO_MATCH
  OSHA     OSHAE-2599eb4b5e | REMPAC LLC | 2005 STARLITE DR. | LUMBERTON, NC 28358 | naics 326150 | ein - | NO_MATCH
```
Verdict: **OK**

```
[street_city_zip_differs] LF-NY-00324 [5a2edb75]  rows=3 families=ITA,OSHA,ECHO edge_bases=street_city_zip_differs,street_zip
  ITA      879504           | Schluter Systems, LP / Schluter Systems | 194 Pleasant Ridge Road | Plattsburgh, NY 12972 | naics 326199 | ein 141772376 | NO_MATCH
  OSHA     OSHAE-5163937e20 | SCHLUTER SYSTEMS L.P. | 194 PLEASANT RIDGE ROAD | PLATTSBURGH, NY 12901 | naics 326199 | ein - | NO_MATCH
  ECHO     110055301061     | SCHLUTER SYSTEMS LP | 194 PLEASANT RIDGE RD | PLATTSBURGH, NY 12901 | naics 326199 | ein - | NO_MATCH
```
Verdict: **OK**

```
[street_city_zip_differs] LF-TX-01380 [e8f88e5d]  rows=3 families=ITA,OSHA edge_bases=street_city_zip_differs,street_zip
  ITA      1475156          | SAG  CTSC 057  El Paso TX / The Goodyear Tire & Rubber Company | 1459 BESSEMER DR | EL PASO, TX 79936 | naics 441330 | ein 340253240 | NO_MATCH
  ITA      1475300          | SAG  CTSC 330  El Paso TX Production / The Goodyear Tire & Rubbe | 1459 BESSEMER DR | EL PASO, TX 79936 | naics 441330 | ein 340253240 | NO_MATCH
  OSHA     OSHAE-c085485283 | THE GOODYEAR TIRE & RUBBER COMPANY | 1459 BESSEMER DR | EL PASO, TX 79938 | naics 326212 | ein - | NO_MATCH
```
Verdict: **OK** - Goodyear service centre: two ITA labels plus an OSHA inspection record at one address.

```
[name_locality] LF-CT-00074 [152680f8]  rows=4 families=ITA,OSHA,ECHO,F5500 edge_bases=name_locality,street_zip
  ITA      1182603          | The Colt's Plastics Company, Inc. | 969 North Main Street | Dayville, CT 06241 | naics 326199 | ein - | NO_MATCH
  OSHA     OSHAE-42002dee74 | COLT'S PLASTICS COMPANY, INC. | 969 NORTH MAIN STREET | DAYVILLE, CT 06241 | naics 326199 | ein - | NO_MATCH
  ECHO     110005968845     | COLTS PLASTICS CO | 969 NORTH MAIN STREET | KILLINGLY (DAYVILLE), CT 06241 | naics 326160 326299 | ein - | NO_MATCH
  F5500    060756769        | COLTS PLASTICS COMPANY, INC. | P.O. BOX 429 | DAYVILLE, CT 06241 | naics 326100 | ein 060756769 | NO_MATCH
```
Verdict: **OK**

```
[name_locality] LF-GA-00124 [bd698dfb]  rows=6 families=OSHA,ECHO,F5500 edge_bases=name_locality,street_city_zip_differs,street_zip
  OSHA     OSHAE-565ee70120 | VERNAY MANUFACTURING, INC. | 804 GREENBELT PKWY | GRIFFIN, GA 30224 | naics 326299 | ein - | NO_MATCH
  OSHA     OSHAE-b746311f46 | VERNAY LABORATORIES, INC. | 804 GREENBELT PARKWAY | GRIFFIN, GA 30224 | naics 326299 | ein - | NO_MATCH
  OSHA     OSHAE-faa0f215a7 | VERNAY MANUFACTURING, INC. | 804 GREENBELT PKWY | GRIFFIN, GA 30223 | naics 326299 | ein - | NO_MATCH
  ECHO     110001426644     | VERNAY MANUFACTURING | 804 GREENBELT PARKWAY | GRIFFIN, GA 30223 | naics 326299 | ein - | NO_MATCH
  F5500    310511184        | VERNAY LABORATORIES, INC. | 804 GREENBELT PARKWAY | GRIFFIN, GA 30223 | naics 326200 | ein 310511184 | POSSIBLE
  F5500    310511814        | VERNAY LABORATORIES, INC. | PO BOX 758 | GRIFFIN, GA 30224 | naics 326100 | ein 310511814 | POSSIBLE
```
Verdict: **OK** - Two Form 5500 EINs (both POSSIBLE rows) under one Vernay entity; one plant.

```
[name_locality] LF-KS-00062 [f9885546]  rows=4 families=ITA,OSHA,ECHO,F5500 edge_bases=name_locality,street_zip
  ITA      517252           | Neodesha Plastics, Inc. | 1206 Worley Drive | Neodesha, KS 66757 | naics 326199 | ein 480835418 | NO_MATCH
  OSHA     OSHAE-8a4147554f | NEODESHA PLASTICS INC. / NEODESHA PLASTICS, INC. | 1206 WORLEY DRIVE | NEODESHA, KS 66757 | naics 326199 | ein - | NO_MATCH
  ECHO     110007287097     | NEODESHA PLASTICS | TWIN RIVERS INDUSTRIAL PARK | NEODESHA, KS 66757 | naics 326199 | ein - | NO_MATCH
  F5500    480835418        | NEODESHA PLASTICS, INC. | 1206 WORLEY DRIVE | NEODESHA, KS 66757 | naics 326100 | ein 480835418 | NO_MATCH
```
Verdict: **OK**

```
[name_locality] LF-LA-00194 [85f3eccd]  rows=2 families=ITA,ECHO edge_bases=name_locality
  ITA      1076547          | CSP Innovations Louisiana, LLC | 26755 Hwy 371 | Sarepta, LA 71071 | naics 326199 | ein 721511176 | NO_MATCH
  ECHO     110020560506     | CSP INNOVATIONS LOUISIANA, LLC | PLASTICS | SAREPTA, LA 71071 | naics 326199 | ein - | NO_MATCH
```
Verdict: **OK**

```
[name_locality] LF-MA-00331 [913a2a9a]  rows=3 families=ITA,OSHA,ECHO edge_bases=name_locality,street_zip
  ITA      1003732          | Ludlow / Advanced Drainage Systems | stoneybrook industrial park 58 Wyomi | Ludlow, MA 01056 | naics 326122 | ein 510105665 | NO_MATCH
  OSHA     OSHAE-043c0c38b0 | ADVANCED DRAINAGE SYSTEMS, INC | 58 WYOMING STREET | LUDLOW, MA 01056 | naics 326122 | ein - | NO_MATCH
  ECHO     110032730784     | ADVANCED DRAINAGE SYSTEM | 58 WYOMING ST | LUDLOW, MA 01056 | naics 325211 326122 | ein - | NO_MATCH
```
Verdict: **OK**

```
[name_locality] LF-MI-00376 [1e43cec6]  rows=3 families=OSHA,ECHO,F5500 edge_bases=housenum_zip_name,name_locality
  OSHA     OSHAE-0f6ee0003b | MCPHERSON PLASTICS INC | 1347 MICHIGAN M89 | OTSEGO, MI 49078 | naics 326199 | ein - | NO_MATCH
  ECHO     110008457277     | MCPHERSON PLASTICS INC | 1347 M 89 | OTSEGO, MI 49078 | naics 325211 | ein - | NO_MATCH
  F5500    381911198        | MCPHERSON PLASTICS, INC. | PO BOX 58 | OTSEGO, MI 49078 | naics 326100 | ein 381911198 | NO_MATCH
```
Verdict: **OK** - '1347 Michigan M89' vs '1347 M 89': one address.

```
[name_locality] LF-PA-00357 [cbdfbed5]  rows=2 families=OSHA,F5500 edge_bases=name_locality
  OSHA     OSHAE-f4da0d65ec | HAYES IVY MANUFACTURING, INC | 6273 ROUTE 309 | NEW TRIPOLI, PA 18066 | naics 326199 | ein - | NO_MATCH
  F5500    221831574        | HAYES-IVY MANUFACTURING, INC. / UNITED SERVICE COMPANY | P.O. BOX 455 | NEW TRIPOLI, PA 18066 | naics 326100 | ein 221831574 | NO_MATCH
```
Verdict: **OK**

```
[name_locality] LF-SC-00175 [9a5f3bdc]  rows=2 families=ECHO,F5500 edge_bases=name_locality
  ECHO     110017114852     | WELLMAN PLASTICS RECYCLING LLC | 520 KINGSBURG HIGHWAY | JOHNSONVILLE, SC 29555 | naics 325211 | ein - | NO_MATCH
  F5500    263552985        | WELLMAN PLASTICS RECYCLING, LLC | PO BOX 188 | JOHNSONVILLE, SC 29555 | naics 325200 | ein 263552985 | NO_MATCH
```
Verdict: **OK**

```
[ein_locality] LF-IA-00210 [0b0b3d4e]  rows=2 families=ITA,F5500 edge_bases=ein_locality
  ITA      1475550          | HiRail Inc. | 100 Kraiburg Blvd | Lisbon, IA 52253 | naics 326299 | ein 934004798 | NO_MATCH
  F5500    934004798        | HIRAIL INC. | 100 KRAIBERG BLVD | LISBON, IA 52253 | naics 326200 | ein 934004798 | NO_MATCH
```
Verdict: **OK**

```
[ein_locality] LF-IL-00682 [91b4a97e]  rows=3 families=ITA,OSHA,F5500 edge_bases=ein_locality,street_zip
  ITA      805521           | Tiger Dylac, St. Charles, IL. / Tiger Drylac, USA, INC. | 3945 Swenson Ave. | St. Charles, IL 60174 | naics 325510 | ein 330081441 | NO_MATCH
  OSHA     OSHAE-f378b375df | TIGER DRYLAC USA, INC. / TIGER DRYLAC USA INC | 3945 SWENSON AVE | SAINT CHARLES, IL 60174 | naics 325510 | ein - | NO_MATCH
  F5500    330081441        | TIGER DRYLAC U.S.A, INC. | 3855 SWENSON AVENUE | SAINT CHARLES, IL 60174 | naics 325500 | ein 330081441 | NO_MATCH
```
Verdict: **OK** - 3945 vs 3855 Swenson Ave: same company, street and EIN; plausibly one campus.

```
[ein_locality] LF-MI-00248 [d6dd08e9]  rows=4 families=ITA,OSHA,ECHO,F5500 edge_bases=ein_locality,street_zip
  ITA      919524           | Highland Plastics, Inc. | 525 N 2nd St | Shepherd, MI 48883 | naics 326112 | ein 382977128 | NO_MATCH
  OSHA     OSHAE-b02bfe9689 | HIGHLAND PLASTICS INC | 525 N 2ND ST | SHEPHERD, MI 48883 | naics 326113 | ein - | NO_MATCH
  ECHO     110003570975     | HIGHLAND PLASTICS INC-SHEPHERD | 525 N 2ND ST | SHEPHERD, MI 48883 | naics 326199 | ein - | NO_MATCH
  F5500    382977128        | HIGHLAND PLASTICS, INC. | 525 NORTH SECOND ST P.O. BOX 99 | SHEPHERD, MI 48883 | naics 326100 | ein 382977128 | NO_MATCH
```
Verdict: **OK**

```
[ein_locality] LF-MN-00227 [44e5dc64]  rows=2 families=ITA,F5500 edge_bases=ein_locality
  ITA      1335084          | CPK-MN / Cryopak, Inc. | 10200 Valley View Rd | Eden Prairie, MN 55344 | naics 326140 | ein 223073399 | NO_MATCH
  F5500    223073399        | INTEGREON GLOBAL INC. | 10200 VALLEY VIEW ROAD SUITE 101 | EDEN PRAIRIE, MN 55344 | naics 326100 | ein 223073399 | NO_MATCH
```
Verdict: **OK** - Cryopak (ITA) and its parent Integreon Global (Form 5500 sponsor) share EIN and street.

```
[ein_locality] LF-NY-00509 [24c19b1c]  rows=2 families=ITA,F5500 edge_bases=ein_locality
  ITA      1255706          | FINGER LAKES EXTRUSION | 2437 ROUTE 21 | CANANDAIGUA, NY 14424 | naics 326121 | ein 161539424 | NO_MATCH
  F5500    161539424        | FINGER LAKES EXTRUSION CORP | 2437 ROUTE 21 NORTH | CANANDAIGUA, NY 14424 | naics 326100 | ein 161539424 | NO_MATCH
```
Verdict: **OK**

```
[ein_locality] LF-NY-00528 [be591fa9]  rows=5 families=ITA,OSHA,F5500,USASPEND edge_bases=ein+name_locality,housenum_zip_name,street_zip
  ITA      1273516          | Mechanical Rubber Products, Co., Inc. | 77 Forester Ave | Warwick, NY 10990 | naics 325212 | ein 223374334 | NO_MATCH
  OSHA     OSHAE-6c87b7501b | MECHANICAL RUBBER PRODUCTS COMPANY, INC. | 77 FORESTER AVENUE | WARWICK, NY 10990 | naics 326291 | ein - | NO_MATCH
  OSHA     OSHAE-92445da1bb | MECHANICAL RUBBER COMPANY, INC. | 77 FORESTER AVENUE | WARWICK, NY 10990 | naics 326299 | ein - | NO_MATCH
  F5500    223374334        | MECHANICAL RUBBER PRODUCTS | PO BOX 593 | WARWICK, NY 10990 | naics 326200 | ein 223374334 | NO_MATCH
  USASPEND Z897SBK6MMB3     | MECHANICAL RUBBER PRODUCTS COMPANY, INC. | 77 FORESTER AVE STE1 | WARWICK, NY 10990 | naics 325211,326121,326291 | ein - | NO_MATCH
```
Verdict: **OK**

```
[ein_locality] LF-OR-00135 [91823e60]  rows=2 families=ITA,F5500 edge_bases=ein_locality
  ITA      1455830          | Chemwest Systems, Inc. | 15865 SW 72nd Ave Blgd C | Portland, OR 97224 | naics 326199 | ein 931102726 | NO_MATCH
  F5500    931102726        | CHEMWEST SYSTEMS, INC. | 15865 SW 72ND AVENUE BULIDING C | PORTLAND, OR 97224 | naics 326100 | ein 931102726 | NO_MATCH
```
Verdict: **OK**

```
[ein_locality] LF-WI-00026 [377476dc]  rows=3 families=ITA,ECHO,F5500 edge_bases=ein+name_locality,street_zip
  ITA      953860           | ChemDesign Products, Inc. | 2 Stanton St | Marinette, WI 54143 | naics 325199 | ein 205669856 | NO_MATCH
  ECHO     110000421080     | CHEMDESIGN PRODUCTS, INC. | 2 STANTON STREET | MARINETTE, WI 54143 | naics 325998 | ein - | NO_MATCH
  F5500    205669856        | CHEMDESIGN PRODUCTS, INC. | TWO STANTON STREET | MARINETTE, WI 54143 | naics 325900 | ein 205669856 | NO_MATCH
```
Verdict: **OK**

```
[weak_name_locality] LF-MI-00226 [d58502dd]  rows=2 families=ECHO,F5500 edge_bases=weak_name_locality
  ECHO     110002046535     | GENESEE POLYMERS CORPORATION | G-4099 SOUTH DORT HIGHWAY | BURTON, MI 48529 | naics 325998 | ein - | NO_MATCH
  F5500    382467226        | GENESEE POLYMERS CORPORATION | G 4133 S DORT HIGHWAY | BURTON, MI 48529 | naics 325900 | ein 382467226 | NO_MATCH
```
Verdict: **DOUBTFUL** - 4099 vs 4133 S Dort Hwy, Burton: same company and road, different house numbers; attached on name + city only.

```
[weak_name_locality] LF-PA-01082 [daaee7df]  rows=2 families=USASPEND,PATENT edge_bases=weak_name_locality
  USASPEND HA3GWLK3JK58     | EVOQUA WATER TECHNOLOGIES LLC | 210 SIXTH AVE STE 3300 | PITTSBURGH, PA 15222 | naics 325998 | ein - | NO_MATCH
  PATENT   c3f232e9-de4a-45 | Evoqua Water Technologies LLC |  | Pittsburgh, PA  | naics  | ein - | NO_MATCH
```
Verdict: **OK** - HQ-grade evidence only (USAspending SAM address and a patent assignee city).

```
[weak_name_locality] LF-PR-00022 [05d248b9]  rows=3 families=OSHA,ECHO,F5500 edge_bases=weak_name_locality
  OSHA     OSHAE-2f30a77baa | NYPRO PUERTO RICO INC | CARR #15 KM 25.4 AVE LUIS MU?OZ MAR? | CAYEY, PR 00736 | naics 326199 | ein - | NO_MATCH
  ECHO     110023128694     | NYPRO PUERTO RICO INC | ST #15 KM 25.4 LUIS MUNOZ MARIN AVE | CAYEY, PR 00737 | naics 326121 326199 | ein - | NO_MATCH
  F5500    660320194        | NYPRO PUERTO RICO, INC. | KM 25.4 LUIS MUNOZ RIVERA AVE | CAYEY, PR 00737 | naics 326100 | ein 660320194 | NO_MATCH
```
Verdict: **OK** - Km 25.4 on PR-15 in all three rows.

```
[weak_name_locality] LF-PR-00024 [e85ac39d]  rows=2 families=ITA,ECHO edge_bases=weak_name_locality
  ITA      46812            | MAPEI CARIBE, Inc. / MAPEI Corporation | HC-3 Box 7006 | Dorado, PR 00646 | naics 325520 | ein - | NO_MATCH
  ECHO     110038910113     | MAPEI CARIBE | RD 2 KM 26.2 ESPINOSA WARD | DORADO, PR 00646 | naics 325520 | ein - | NO_MATCH
```
Verdict: **DOUBTFUL** - Rural-route and km-marker addresses in Dorado PR on both sides; no comparable street key.

```
[weak_name_locality] LF-PR-00035 [ea0c33a3]  rows=3 families=OSHA,ECHO edge_bases=weak_name_locality
  OSHA     OSHAE-20a0510e16 | TECHNO PLASTICS INDUSTRIES INC. | ROAD 402, KM 0.6 | ANASCO, PR 00610 | naics 326199 | ein - | NO_MATCH
  OSHA     OSHAE-807ecdd0b1 | TECHNO PLASTICS INDUSTRIES INC. | CARR. 402 KM 0.6, SECTOR INDUSTRIAL  | ANASCO, PR 00610 | naics 326199 | ein - | NO_MATCH
  ECHO     110071064018     | TECHNO PLASTICS INDUSTRIES, INC. | CARR. PR-402, KM 0.6 | ANASCO, PR 00610 | naics 326111 | ein - | NO_MATCH
```
Verdict: **OK** - Km 0.6 on PR-402 in all three rows.

```
[weak_name_locality] LF-PR-00045 [87911678]  rows=2 families=ITA,F5500 edge_bases=weak_name_locality
  ITA      663115           | IDI Caribe Inc. / IDI Caribe, Inc. | Bo. Coqui Carr #3 Km. 153.5 | Aguirre, PR 00704 | naics 325211 | ein 660419091 | NO_MATCH
  F5500    660419091        | IDI CARIBE INC | PO BOX 400 | AGUIRRE, PR 00704 | naics 326100 | ein 660419091 | NO_MATCH
```
Verdict: **OK**

```
[weak_name_locality] LF-WV-00031 [f9946c32]  rows=4 families=ITA,ECHO,F5500 edge_bases=ein+name_locality,street_zip,weak_name_locality
  ITA      1312032          | AC&S, Inc | 150 Plant Road | Nitro, WV 25143 | naics 325998 | ein 550661163 | NO_MATCH
  ECHO     110013694038     | AC&S INC | W 19TH ST. | NITRO, WV 25143 | naics 325998 | ein - | NO_MATCH
  ECHO     110070273168     | AC & S, INC. | 150 PLANT ROAD | NITRO, WV 25143 | naics 325998 | ein - | NO_MATCH
  F5500    550661163        | AC & S, INC | WEST 19TH STREET | NITRO, WV 25143 | naics 325900 | ein 550661163 | NO_MATCH
```
Verdict: **OK**

```
[weak_name_locality] LF-WV-00050 [44184384]  rows=2 families=ITA,ECHO edge_bases=weak_name_locality
  ITA      359679           | Nitro / Brenntag Mid-South | Plant Rd. PO Box 309 | Nitro, WV 25143 | naics 424690 | ein 610504545 | NO_MATCH
  ECHO     110070634757     | BRENNTAG MID-SOUTH, INC | PLANT RD | NITRO, WV 25143 | naics 325998 | ein - | NO_MATCH
```
Verdict: **OK** - ITA is a chemical distributor (424690), ECHO carries 325998; same plant road in Nitro.

### 4.2 Sample of same-address pairs blocked by the name guard

- ITA `McKenzie Creative Brands / McKenzie Sports Pro` vs ECHO `MARTIN INDUSTRIES` at `1135 Montgomery Avenue`, Albemarle, NC 28001 (street_zip)
- ITA `IPG - Colfax / Oldcastle Infrastructure` vs ECHO `NATIONAL PIPE AND PLASTICS` at `9609 W. Market Street`, Colfax, NC 27235 (street_zip)
- OSHA `MOLDING SOLUTIONS, INC.` vs OSHA `MPI-ST. LOUIS LLC` at `300 NORTH CUMMINGS LANE`, WASHINGTON, IL 61571 (street_zip)
- OSHA `C.K.S. PACKAGING, INC.` vs ECHO `ALTIUM PACKAGING - ARDEN, NC` at `9 TRIDENT DRIVE`, ARDEN, NC 28704 (street_zip)
- OSHA `SANDERSON PIPE CORPORATION` vs ECHO `TEXAS UNITED PIPE` at `11627 NORTH HOUSTON ROSSLYN ROAD`, HOUSTON, TX 77086 (street_zip)
- OSHA `AUSTIN FOAM PLASTICS, INC.` vs OSHA `TDG STAFFING LLC` at `2933 A.W. GRIMES BLVD.`, PFLUGERVILLE, TX 78660 (street_zip)
- OSHA `TEKNIPLEX CONSUMER PRODUCTS` vs ECHO `PHOENIX PACKAGING` at `4800 LINA LANE`, DUBLIN, VA 24084 (street_zip)
- OSHA `TESSY PLASTICS LLC` vs F5500 `TOTAL PLASTIC SOLUTIONS, LLC` at `231 JEFFERSON RIDGE PKWY`, LYNCHBURG, VA 24501 (street_zip)
- ECHO `AQUATIC LEISURE TECHNOLOGIES, INC.` vs ECHO `MOLDED FIBER GLASS ALABAMA LLC` at `200 HATTAWAY ROAD`, OPP, AL 36467 (street_zip)
- ECHO `CLARIANT CORPORATION - PALO ALTO` vs ECHO `SUD CHEMIE` at `3350 W BAYSHORE RD`, PALO ALTO, CA 94303 (street_zip)
- ECHO `FLUORON, INC` vs F5500 `SPECTRUM LAB HOLDINGS LLC` at `505 BLUE BALL RD BLDG 120`, ELKTON, MD 21921 (street_zip)
- ECHO `ANGUS KIDDE FIRE` vs USASPEND `NATIONAL FOAM INC` at `141 JUNNY ROAD`, ANGIER, NC 27501 (street_zip)
- ECHO `INDEX PACKAGING, INC., D/B/A AVILITE` vs ECHO `NASHUA CORPORATION - MERRIMACK FACIITY` at `59 DANIEL WEBSTER HWY`, MERRIMACK, NH 03054 (street_zip)
- USASPEND `ZLC SOLUTIONS LLC` vs USASPEND `F & D FEDERAL LLC` at `161 FORT EVANS RD NE STE 250`, LEESBURG, VA 20176 (street_zip)

Of these 14 blocked pairs, my reading is that roughly 8 are one establishment under a successor, parent or brand name (Alto Ingredients / Williams Ethanol Services at the Pekin plant, Spartech / PolyOne, JM Eagle / PW Eagle, PRET Advanced Materials / Wellman Plastics Recycling, Champion X / Nalco Champion, Chem-Aqua / NCH, American Plastics / Vinylex, TG Missouri) and roughly 6 are unrelated co-tenants (Compliance Staffing / Turnstone, Clean Earth / Sedgwick, Acrylic Source / All Source Plus, Enstall / PanelClaw, FRX Polymers / Triton Systems, U.S. Smokeless Tobacco / Philip Morris). That is the price of the name guard: it forgoes some true same-establishment merges (those lose a family and rank lower) to avoid fusing co-tenants. The pairs are not lost: they are listed in each cluster's `related_clusters`. (The TG Missouri pair was a normalizer gap, 'T G' vs 'TG', fixed by the no-space name rule in this run, so it no longer appears blocked.)

### 4.3 Examples of clusters dropped as already held (up to 4 per reason)

- `held_org_name_local_site`
  - LF-AL-00107 TORAY COMPOSITE MATERIALS AMERICA, INC. (DECATUR, AL; ITA,ECHO) -> ORG-002963 Toray Composite Materials America, Inc. / SITE-003428 (site street unknown)
  - LF-AL-00433 Master Extrusion (Albertville, AL; ITA,OSHA) -> ORG-003498 Master Extrusion, LLC / SITE-003922 (site street unknown)
  - LF-AL-00459 CALCEAN MINERALS AND MATERIALS LLC (GADSDEN, AL; OSHA) -> ORG-003787 Calcean Minerals and Materials LLC / SITE-004228 (site street unknown)
  - LF-AR-00044 HERMANN COMPANIES, INC. D/B/A ANCHOR PAC (PARAGOULD, AR; OSHA,ECHO) -> ORG-002945 Anchor Packaging LLC / SITE-003402 (site street unknown)
- `held_trifid_verified`
  - LF-AL-00108 INEOS STYROLUTION AMERICA, LLC (DECATUR, AL; ITA,ECHO) -> 35602PLYSRPOBOX -> ORG-003155
  - LF-AL-00134 SABIC INNOVATIVE PLASTICS US LLC (LOWNDESBORO, AL; OSHA,ECHO) -> 36752GPLSTONEPL -> ORG-003161
  - LF-AL-00152 ARKEMA INC - MOBILE FACILITY (AXIS, AL; ECHO) -> 36505MTCHMHWY43 -> ORG-002224
  - LF-AL-00194 POLYPLEX USA LLC (DECATUR, AL; ITA,ECHO) -> 3560WPLYPL31MAL -> ORG-003160
- `held_site_street_name`
  - LF-AL-00156 HWASEUNG AUTOMOTIVE USA LLC (ENTERPRISE, AL; OSHA,ECHO) -> SITE-005747 (ORG-004397)
  - LF-AL-00467 H S AUTOMOTIVE ALABAMA INC (ENTERPRISE, AL; OSHA) -> SITE-005747 (ORG-004397)
  - LF-AR-00159 LB AMFUEL LLC (MAGNOLIA, AR; F5500) -> SITE-005662 (ORG-004344)
  - LF-AZ-00039 S.R. SMITH (TUCSON, AZ; ITA,ECHO) -> SITE-005610 (ORG-004250)
- `held_org_ein_local_site`
  - LF-CA-03078 AmSty (TORRANCE, CA; ITA) -> ORG-000670 Americas Styrenics LLC / SITE-004852
  - LF-ID-00037 Dupont Burley XPS (BURLEY, ID; ITA) -> ORG-000785 DDP Specialty Electronic Materials US 5, LLC / SITE-004876
  - LF-IN-00668 Myers Industries/Elkhart Plastics (Middlebury, IN; ITA,OSHA) -> ORG-000009 Myers Industries Inc. / SITE-002908 (site street unknown)
  - LF-LA-00463 HoneywellLA04 (Carville, LA; ITA) -> ORG-002874 Solstice Advanced Materials Inc. / SITE-003025
- `held_org_ein+name_local_site`
  - LF-CO-00143 AVIENT - ADVANCED COMPOSITES-POLYSTRAND (ENGLEWOOD, CO; ITA,OSHA,ECHO) -> ORG-000001 Avient Corporation / SITE-002886 (site street unknown)
  - LF-IL-01287 Avient Corporation (McHenry, IL; ITA,OSHA) -> ORG-000001 Avient Corporation / SITE-002889 (site street unknown)
  - LF-LA-00378 Tokai Carbon CB (Addis, LA; ITA) -> ORG-002940 Tokai Carbon CB Ltd. / SITE-003252 (site street unknown)
  - LF-MA-00661 Modern Dispersions Inc (Leominster, MA; ITA,OSHA) -> ORG-002955 Modern Dispersions, Inc. / SITE-003415 (site street unknown)

## 5. Caveats (binding on any reader)

- **Leads only.** No cluster is a verdict in the AGENTS 2.8 grammar (not VERIFIED, REJECT, STILL_UNCERTAIN, DUPLICATE_OF). A multi-source cluster is more likely to be a real, operating establishment; it is not proof, not a scope claim, not a ring, not a tier.
- **Source families are not fully independent.** ITA and OSHA inspections are both DOL-OSHA; ITA and Form 5500 are employer self-filings; USAspending and Form 5500 addresses are registered or HQ-grade and often not the plant (they confirm an address only when they equal a plant-grade street). Patents only place an assignee in a city. A single-source cluster can be a real plant that sits in only one dataset.
- **NAICS is a signal, not a company fact** (AGENTS section 4): ITA/OSHA NAICS are OSHA-channel, ECHO NAICS is program-reported, Form 5500 codes are filer-chosen padded groups (326100, 325900 ...), USAspending NAICS describes the contract, not the firm. `core_naics_families` counts agreement of signals only; none of it may populate `naics_primary`.
- **Form 5500 rows are employers, not establishments**; the participant band is a plan-size input (SCHEMA R7f) at employer level, shown only as `size_basis = F5500 ...` when no establishment-grain size exists.
- **Privacy (AGENTS section 6).** Form 5500 sponsors whose street line the source packet withheld (no entity designator and fewer than 10 participants: a possible home address) carry no street here and are flagged `form5500_street_withheld_privacy_possible_individual`; the name and EIN of such a row are carried over from the packet as published and should be treated as possibly an individual's: do not research or publish them without a business-entity check. No emails, phones, officers or inventors are carried.
- **Coordinates were never read.** `county` is the ECHO FRS county (or the PatentsView county) shown for orientation only; Ohio counties need the physical address (AGENTS section 4).
- **Clustering is conservative on purpose.** Street spelling variance beyond rule 2, a rebranded or co-tenant operator at one address, and plant addresses that differ by building number are left as separate clusters, so some real multi-source establishments are undercounted as SINGLE. The opposite risk (false merges) is measured in section 4.
- **Dropped clusters are not verdicts either.** They were dropped because the current Atlas already holds a record at that address/name/EIN/TRIFID; a wrong drop is possible, mainly where a held org's same-city site has an unknown street (rule b). `--dump-dropped PATH` regenerates the drop list.
- **No website-domain dedupe was possible** (AGENTS section 3 step 1): none of the six sources carries a domain. Every lead must be domain-checked, and re-checked against the Atlas as it stands at integration time (the Atlas moves between passes).
- **Registry identifiers** (EINs in `eins`, ECHO registry IDs and UEIs inside `sources_with_ids`) are lead keys; an identifier seen only in this project's files mints no registry link (AGENTS section 4 phantom rule). EINs are public business-filer IDs carried over from the ITA and Form 5500 packets; no personal data is carried (the Form 5500 street lines the source withheld for privacy stay blank).
- **Territories and no-state rows**: USPS territories (PR, GU, ...) cluster like states; foreign and no-state recipients are held (section 1).
- **Counting honesty (AGENTS section 7):** every count above names its unit. 'Clusters' are candidate establishments built from source records, not verified establishments and not Atlas sites; they are not comparable with QCEW establishment counts.

## 6. Reproduce

```
python3 scripts/build_lead_fusion.py --as-of 2026-11-01            # writes clusters.csv, top_leads_by_state.csv, REPORT.md
python3 scripts/build_lead_fusion.py --audit-print --no-write      # print the 30-cluster audit sample
python3 scripts/build_lead_fusion.py --dump-dropped /path/dropped.csv --no-write
```
Inputs are the committed packet CSVs under `tasks/` and the current `data/`; no network, no credentials. REPORT.md is regenerated by the script; the hand-review verdicts of section 4 and the two discussion notes are stored in `AUDIT_VERDICTS` / `AUDIT_NOTES` in the script so a re-run reproduces them (a changed input changes the sample, and unreviewed clusters then show as UNREVIEWED).
