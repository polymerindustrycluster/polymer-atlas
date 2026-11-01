# ECHO / FRS polymer facility spine - 2026-11-01

**Status: lead product, not Atlas data.** Nothing here edits `data/`, mints a registry link, sets a tier or changes a status. Built by `scripts/build_echo_spine.py` (stdlib; re-runnable). Packet lane output: the integrator of record decides what, if anything, is applied.

## 1. Source and filter

- **Source:** EPA ECHO exporter, `https://echo.epa.gov/files/echodownloads/echo_exporter.zip` (member `ECHO_EXPORTER.csv`), retrieved 2026-11-01, zip SHA-256 `db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a`. Column dictionary: https://echo.epa.gov/tools/data-downloads (`echo_exporter_columns_7-16-2025_0.xlsx`); every column name used was checked against the extract header.
- **Rows read:** 3,233,462 ECHO exporter rows (unit: one ECHO record per row; 18,887 rows carry a blank REGISTRY_ID).
- **Scope filter (any one of):** a 6-digit NAICS code under 3252, 3255, 3259 or 326 (`core`), or a Ring 3 Primary code 333511 / 424610 / 562920 (`ring3_primary`; SCHEMA 2.2). NAICS read from `FAC_NAICS_CODES` plus the program fields `CAA_NAICS`, `CWA_NAICS`, `RCRA_NAICS`; 0 facilities enter only through a program NAICS field.
- **Active filter:** `FAC_ACTIVE_FLAG = Y`. ECHO's definition: *any associated ICIS-Air, ICIS-NPDES, RCRA or SDWA permit is in an active status* - a **permit** fact. In this extract the flag takes only the values Y and blank (no N occurs). NAICS-scoped rows by flag: Y = 15,983, N = 0, blank = 7,277 (blank rows are dropped; a blank flag is not evidence of closure - it also covers TRI/GHG-only records and lapsed permits). Of the Y rows, 63 carry a **blank REGISTRY_ID** (RCRA-only records ECHO has not linked to FRS) and are excluded because they cannot carry an FRS link; the other 15,920 have unique non-blank REGISTRY_IDs (uniqueness asserted).
- **Result:** **15,920 active, NAICS-scoped ECHO facilities** (unit: FRS registry IDs; `facilities.csv`): 14,789 `core` + 1,131 `ring3_primary`.
- **SCHEMA 2.2 signal of the best matched code** (P primary / S secondary / X exclude-by-default / U in scope but not listed in 2.2): P 12,871, S 2,446, U 479, X 124.

## 2. Match to Atlas sites

Atlas side: 5,773 site rows (all shards, any status/tier). Street key from the `street_address` column for 3,629 sites and, where that column is blank, a heuristic read of `Street...:` phrases in `notes` for a further 1,594 (total 5,223 = 90.5% of site rows have a usable street key; the rest can match only on name + zip/city).

Method per facility (first/best hit wins; operator rule, AGENTS 3): (1) normalized street + state + (zip5 or city) + name agreement = `street_exact+loc+name`; the same with a name disagreement is **POSSIBLE** (co-tenant or successor operator), unless an FRS ID in site notes or a held TRIFID for that org corroborates (`street_exact+loc+id`); (2) where the street is missing on either side, same zip5 + strong name similarity = `name_zip_street_unknown` (moderate); same city + strong name, or same zip + weaker name = POSSIBLE; (3) two Atlas sites tied at the top rank = POSSIBLE with the tie listed. Both streets present but different is never a match (a second plant is a second site). Name similarity compares the FRS name with the site name, the org legal name and trade names on distinctive tokens (generic plastics words removed).

| Verdict | Facilities (core + ring3_primary) | core only | core, signal P only | ring3_primary only |
|---|---:|---:|---:|---:|
| MATCH_SITE | 2,350 | 2,340 | 2,261 | 10 |
| POSSIBLE | 315 | 308 | 281 | 7 |
| NO_MATCH | 13,255 | 12,141 | 9,198 | 1,114 |
| **Total** | **15,920** | **14,789** | **11,740** | **1,131** |

**Match rate (unit: active NAICS-scoped ECHO facilities matched to an Atlas site row):** MATCH_SITE = 2,350 of 15,920 (**14.8%**); MATCH_SITE + POSSIBLE = 16.7%. core + signal P: 19.3% MATCH_SITE. This is a **facility-to-site match rate, not Atlas coverage**: ECHO lists permit holders only, many Atlas sites hold no EPA permit, and state-level coverage is a separate count-ratio question (see `docs/denominators/README.md`).

MATCH_SITE by basis: `street_exact+loc+name` 2,091; `street_exact+loc+id` 213; `name_zip_street_unknown` 43; `frs_id_in_notes+name+loc` 3. POSSIBLE by best basis: `street_exact+loc_name_differs` 139; `name_city_street_unknown` 70; `name_zip_weak` 50; `street_exact_locality_differs` 25; `street_exact+loc+name` 18; `trifid_org+loc_no_street` 8; `name_zip_street_unknown` 5.

Atlas sites reached by at least one MATCH_SITE facility: 2,156 distinct sites (unit: Atlas site rows); 183 of them match more than one FRS record (FRS often holds duplicate or program-specific registry IDs for one location; all are listed in `site_frs_ids`).

## 3. FRS registry-link candidates

`site_matches.csv` carries, for every MATCH_SITE row, a proposed `registry_links` row: `org_id` = the matched site's parent org, `registry` = `FRS`, `registry_id` = REGISTRY_ID verbatim, `match_basis` = `echo_exporter_<basis>:<site_id>`, `as_of` = 2026-11-01. **2,350 candidate rows** (unit: distinct org_id + FRS ID pairs): `strong` (street + zip/city + name agree) 2,091; `strong_id_corroborated_name_differs` (street + zip/city agree, FRS name differs from the Atlas names, but a held TRIFID or an FRS ID in site notes corroborates - often a former operator name) 213; `moderate` (name + zip, street unknown on a side) 46. `data/registry_links.csv` holds **0** FRS rows today, so there is no collision. A further 14 facilities tie between two Atlas sites of the **same org** at one address (`tie_same_org_possible_duplicate_sites` in `basis`; the org is unambiguous but the site is not - these look like duplicate site rows in the Atlas and are a dedupe lead; no link row is proposed for them) and 20 tie across different orgs.

**Registry-ID verification (AGENTS 4):** every REGISTRY_ID above is read from the ECHO extract's own `REGISTRY_ID` column, so none is a phantom. Separately, 241 distinct FRS-shaped IDs appear in Atlas site `notes` (written by earlier gov-data passes); 167 of them are present in the ECHO extract at all (any NAICS/flag) and 100 are in this spine. Where an ID in notes and the matched FRS record agree: 72 MATCH_SITE rows; where the site's notes name a *different* FRS ID than the one matched: 27 rows (FRS holds several IDs per location - review before minting).

### Grain flag - OWNER RULING NEEDED (not decided here)

`registry_links` is **org-keyed** (SCHEMA 4.8: `org_id MUST`, PK triple org_id + registry + registry_id; validator V-6 checks only org_id existence and `registry_id` non-empty). An FRS ID is a **facility**-grain identifier: one ID names one regulated location, and an organization with N plants holds N FRS IDs, each belonging to a different site. The existing 2,156 `TRI_TRIFID` rows have the same shape and carry the site only inside free-text `match_basis`. Options for the owner: (a) keep org-keyed rows and embed `:<site_id>` in `match_basis` (this packet's proposal; no schema change; not machine-joinable); (b) add a nullable `site_id` column to `registry_links` (schema revision; FRS and TRIFID rows could then be backfilled); (c) a separate site-keyed registry table. Under any option the integrator would also need a rule for a site with several FRS IDs and for an FRS ID shared by co-located operators (SCHEMA 5.3: one address = one site under the operator). This packet takes no position; its rows are written so that (a) can be applied mechanically and (b) can be derived from the `:<site_id>` suffix.

## 4. National discovery spine (NO_MATCH leads)

NO_MATCH = no Atlas site candidate cleared the ladder in section 2. It is a **lead, not a finding of absence**: FRS names and streets are permit-holder grade, and the Atlas may hold the plant under a different name or a street form this normalizer did not equate. Each NO_MATCH row carries a `lead_class`: `HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS` (a held site in the same city/zip has a strongly similar name but a different street - possible address variance or second plant; `lead_ref` = site IDs), `NAME_EQUALS_HELD_ORG_OTHER_LOCATION` (the normalized FRS name equals a held org's legal or trade name - likely an additional site of a held org; AGENTS 3 step 2; `lead_ref` = org IDs), `NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES` (the normalized name appears inside a held org's trade names or notes - AGENTS 3 step 4, rebrands/acquisitions; `lead_ref` = org IDs), `NET_NEW_LEAD` (none of these hit; still subject to the full AGENTS 3 dedupe incl. website domain, which ECHO does not carry). Rows with `name_noise_hint = Y` look like schools, golf clubs, municipal bodies, etc. that carry a stray NAICS.

**NO_MATCH counts (unit: active NAICS-scoped ECHO facilities with no Atlas site candidate):** 13,255 overall; core 12,141; core + SCHEMA 2.2 signal P 9,198; ring3_primary 1,114.

The lead pool is FRS records, not locations: 266 of the 9,198 core + signal-P NO_MATCH facilities share a street + zip with another such record (FRS duplicates), leaving **8,932 distinct street + zip locations** (records without a usable street count one each). By state, sorted by the QCEW gap (QCEW 2023 private establishments, NAICS 326, minus Atlas strict 326 sites - the `docs/denominators/README.md` definition, recomputed from `data/sites_*.csv` at run time). Columns: gap; ECHO active scoped facilities; MATCH_SITE; NO_MATCH, core + signal P (the lead pool); of which net-new-name leads. Full table with all states and columns: `leads_by_state.csv`.

| Gap rank | State | QCEW gap (326) | ECHO facilities | MATCH_SITE | NO_MATCH core, signal P | of which NET_NEW_LEAD |
|---:|---|---:|---:|---:|---:|---:|
| 1 | CA | 1,267 | 2,528 | 75 | 1,567 | 1,392 |
| 2 | TX | 869 | 953 | 174 | 513 | 397 |
| 3 | FL | 775 | 513 | 46 | 349 | 284 |
| 4 | MI | 772 | 878 | 85 | 590 | 492 |
| 5 | IL | 755 | 727 | 68 | 451 | 347 |
| 6 | GA | 446 | 481 | 76 | 302 | 235 |
| 7 | IN | 430 | 610 | 108 | 378 | 249 |
| 8 | WI | 408 | 350 | 66 | 227 | 179 |
| 9 | NY | 387 | 439 | 41 | 268 | 239 |
| 10 | NC | 382 | 549 | 109 | 323 | 238 |
| 11 | SC | 357 | 383 | 70 | 204 | 166 |
| 12 | NJ | 355 | 546 | 39 | 329 | 274 |
| 13 | TN | 350 | 410 | 78 | 228 | 178 |
| 14 | MN | 349 | 248 | 22 | 166 | 132 |
| 15 | MO | 331 | 367 | 46 | 228 | 183 |
| 16 | KY | 260 | 216 | 45 | 129 | 92 |
| 17 | PA | 246 | 670 | 318 | 165 | 131 |
| 18 | MA | 221 | 557 | 49 | 391 | 336 |
| 19 | AL | 219 | 316 | 38 | 192 | 145 |
| 20 | VA | 213 | 289 | 40 | 177 | 131 |

Top-gap states are the ones where the QCEW says the most establishments exist beyond the Atlas's strict NAICS-326 site count; the ECHO lead pool per state is **not** an estimate of that gap (ECHO covers permitted facilities only, and ECHO NAICS does not map one-to-one to QCEW establishments).

## 5. Liveness (signal only)

`facilities.csv` carries `last_inspection`, `last_formal_action`, `last_informal_action`, `last_penalty` (ISO dates from ECHO) and `last_activity_date` = the latest of them. Of 15,920 active scoped facilities, 11,032 have any such date and 5,332 have one within 3 years of 2026-11-01. Among the 2,350 MATCH_SITE facilities, 1,371 have activity within 3 years. `liveness_note` flags MATCH_SITE rows where the Atlas site is `closed`/`idled` while the ECHO permit is still active: **2 rows** (listed in `site_matches.csv`).

Cautions, binding on any reader: an inspection or enforcement date shows a regulator touched the permit, not that the plant runs; a **missing** date, a blank `FAC_ACTIVE_FLAG`, or a failed match is never evidence of closure (AGENTS 3, 8). A stale active-permit flag with a closed Atlas site is a *re-verification lead*. Status changes still need dated primary or near-primary evidence (AGENTS 3); this file supplies none.

## 6. Data-quality caveats

- **Permit-holder grade identity.** `FAC_NAME` is the company or permit holder name as maintained by FRS; `FAC_STREET` is as maintained by FRS. Names can be a parent, a landlord, a former operator or a site label; streets can be a mailing or permit address. Treat every match as address-level evidence for the *facility record*, not for the operator's identity (operator rule, SCHEMA 5.3).
- **NAICS is program-reported.** `FAC_NAICS_CODES` aggregates codes reported to EPA programs (and FRS reconciliation). It is a `government_filing` value **for the facility** (SCHEMA 2.1 vocabulary) and must never be copied to an organization, never decide a ring, and never overwrite a site NAICS that has its own source. Stray codes are common (see `name_noise_hint`); a code under 3259 includes explosives (325920, X signal) and inks, and 325510 includes paint retail records the Sherwin-Williams ruling excludes.
- **FRS duplicates.** One location can hold several REGISTRY_IDs; one ID can be reused for a campus. Counts of facilities are counts of FRS IDs, **not** counts of establishments (AGENTS 7).
- **County.** `county_frs` is FRS-maintained and shown for orientation only; Ohio sites need the county from the physical address (AGENTS 4), not from this column.
- **QCEW gap** is blank for GU, MP (BLS state file has no such rows in `docs/denominators/`); DC is included (BLS title "District of Columbia, not unknown"; 1 private NAICS-326 establishment, N-flagged).
- **No coordinates** are read or output (reference data, never evidence or a match key).
- **Territories and federal facilities** are included if they pass the filter (no federal exclusion applied); Atlas has no site shard for PR/VI/GU/AS/MP, so those rows are NO_MATCH by construction and have no QCEW gap here.
- **Not used:** FRS `national_single.zip` (optional in the brief; not needed for the ECHO fields above), Form 5500 / TRI cross-checks beyond held TRIFIDs, any web fetch. No verdict in this file is a REJECT or VERIFIED in the AGENTS 2.8 grammar - they are match candidates.
- **Output size.** `facilities.csv` and `site_matches.csv` are large for a PR; the integrator may prefer to split by state shard if this is applied in parts (SCHEMA Appendix C 6.5 size budget).

## 7. Reproduce

```
curl -sS -o /tmp/claude-0/echo_raw/echo_exporter.zip https://echo.epa.gov/files/echodownloads/echo_exporter.zip
python3 scripts/build_echo_spine.py --zip /tmp/claude-0/echo_raw/echo_exporter.zip --as-of 2026-11-01
```
