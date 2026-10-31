# F5 public-count audit — pinned post-TRI snapshot

> **Final F5 reconciliation, 2026-10-31:** [Completed count/accounting report](F5_FINAL_RECONCILIATION_2026-10-31.md) reproduces PIC-12 326 = 367 and resolves all seven link cases as six documented freeze holds plus one corrected applied link—not missing facilities. The 3252/3259 values 52/62 are incomplete published-cell sums. Earlier blocker statements below are historical.

> **2026-10-31 source update:** [Reconciliation results](F5_SOURCE_RECONCILIATION_2026-10-31.md) now reproduce PA/OH state benchmarks, the 1,797-facility ledger and all 2,199 creation-map rows. PIC-12 aggregate cells and seven ledger link-outcome discrepancies remain open. Earlier missing-source statements below are historical.

> **23:22 UTC continuation:** The [reconciliation addendum](F5_RECONCILIATION_ADDENDUM_2026-10-30.md) verifies the newly published creation map at current main. Coverage/denominator and full campaign-ledger gaps remain explicitly open; canonical data is unchanged.

Pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`, observed 2026-10-30 21:32 UTC.
This is a read-only count audit, not fresh entity verification. No canonical data,
schema, status, tier, identifier or relationship was changed.

## Current inventory (all rows, all statuses and tiers)

Organization rows: **4,179**; site rows: **5,770**. Organization rows include
subsidiaries and tombstones: neither count means unique ultimate parents or
currently operating manufacturers. Sites include HQs, R&D and warehouses.

| Canonical record unit | All rows, no filter |
|---|---:|
| `code_assignments.csv` rows | 61 |
| `ecosystem.csv` rows | 206 |
| `event_participation.csv` rows | 782 |
| `events.csv` rows | 71 |
| `evidence.csv` rows | 12,876 |
| `inclusion_log.csv` rows | 83 |
| `members.csv` rows | 60 |
| `people.csv` rows | 73 |
| `programs.csv` rows | 73 |
| `ref_code_map.csv` rows | 39 |
| `ref_codes.csv` rows | 79 |
| `registry_links.csv` rows | 2,373 |
| `relationships.csv` rows | 335 |
| `site_capabilities.csv` rows | 497 |

| Table | A | B | C | U |
|---|---:|---:|---:|---:|
| Organization rows, all statuses | 1029 | 2540 | 587 | 23 |
| Site rows, all statuses | 982 | 3002 | 1327 | 459 |

All organization statuses: active 4,127; unknown 9; merged 22; acquired 12;
closed 5; pre_revenue 4. All site statuses: active 5,641; unknown 69; closed
57; active_idled_partial 1; pre_revenue 1; idled 1. Unknown is not active.
The HQ residual shard has 163 organization rows; it is not a site geography.

## Ohio / Pennsylvania / PIC-12 — numerator restatement

**Unit: Atlas site rows.** Primary cut = `operating_status` in
`{active, unknown}` AND `verification_tier` in `{A,B,C}`. Recorded cut = same
status filter, any tier. Geography uses physical `state`, plus recorded county
for PIC-12, never an organization's HQ. NAICS uses the site's own
`naics_primary.startswith(code)`; no parent inheritance or secondary-code matching.
No ring or site-type restriction. Blank NAICS is excluded from family rows.
These are count comparisons, **not matched-facility coverage or recall**.

| Geography | NAICS prefix | Primary A–C sites | Recorded any-tier sites | Unknown-status sites within recorded |
|---|---|---:|---:|---:|
| OH | 3252 | 82 | 98 | 4 |
| OH | 325211 | 63 | 77 | 3 |
| OH | 325212 | 16 | 18 | 1 |
| OH | 3259 | 79 | 91 | 3 |
| OH | 325991 | 51 | 57 | 1 |
| OH | 326 | 815 | 988 | 40 |
| OH | 3261 | 648 | 789 | 31 |
| OH | 3262 | 167 | 199 | 9 |
| PA | 3252 | 86 | 86 | 0 |
| PA | 325211 | 75 | 75 | 0 |
| PA | 325212 | 9 | 9 | 0 |
| PA | 3259 | 24 | 24 | 0 |
| PA | 325991 | 22 | 22 | 0 |
| PA | 326 | 396 | 396 | 0 |
| PA | 3261 | 347 | 347 | 0 |
| PA | 3262 | 49 | 49 | 0 |
| PIC-12 | 3252 | 41 | 46 | 2 |
| PIC-12 | 325211 | 27 | 30 | 1 |
| PIC-12 | 325212 | 13 | 15 | 1 |
| PIC-12 | 3259 | 49 | 56 | 2 |
| PIC-12 | 325991 | 33 | 34 | 1 |
| PIC-12 | 326 | 423 | 437 | 15 |
| PIC-12 | 3261 | 325 | 335 | 11 |
| PIC-12 | 3262 | 98 | 102 | 4 |

Across all NAICS (including blanks), the same primary/recorded cuts give OH
1,527/1,953 sites, PA 774/774 sites and PIC-12 835/996 sites. Blank-NAICS
primary/recorded sites are respectively OH 65/160, PA 136/136 and PIC-12 27/94.
The PIC-12 recorded 996 is a coincidence, not the historical framework's 996.

### Official denominator verification and limits

The [Ohio DJFS annual 2023 QCEW table, page 3](https://prod-ohlmi.mt.gov/_docs/QCEW/annual_n/2023_RS20311N.pdf)
was re-opened on 2026-10-30: average establishments 326 = 890, 3261 = 706,
3262 = 184, 3252 = 115, 3259 = 153. The displayed industrial-sector table is
under its Private Sector heading. Its footnote says employer reports through
2024-06-01; subtotals may differ because of rounding. This is a dated published
benchmark, not a 2026 denominator. The [BLS open-data documentation](https://www.bls.gov/cew/additional-resources/open-data/home.htm)
is the source for annual area extracts; a reproducible private-sector pull must
select year 2023, quarter A, area 39000/42000, own_code 5, industry_code, and
annual_avg_estabs, preserving disclosure flags.

| OH NAICS | Primary / official establishments | Primary count ratio | Recorded / official establishments | Recorded count ratio |
|---|---:|---:|---:|---:|
| 326 | 815/890 | 91.6% | 988/890 | 111.0% |
| 3261 | 648/706 | 91.8% | 789/706 | 111.8% |
| 3262 | 167/184 | 90.8% | 199/184 | 108.2% |
| 3252 | 82/115 | 71.3% | 98/115 | 85.2% |
| 3259 | 79/153 | 51.6% | 91/153 | 59.5% |

**PA denominator BLOCKED:** the national-spine denominator file is not in this
public tree; direct official 2023 annual API area 42000 and industry 326 requests
were inaccessible through the research tool. No PA denominator or percentage is
invented. Settling action: supply the banked QCEW-2023 PA extract plus metadata,
or retrieve the official annual extract and verify the filters above. PA's 396
NAICS-326 sites are a numerator, not 396 companies and not a coverage percentage.

**PIC-12 denominator reproduction BLOCKED:** the earlier report records QCEW-2023
326 = 367 (3261 283; 3262 84), 3252 = 52 and 3259 = 62–63. Its underlying
`staging/working/denominators_pic12.csv` and `denominators_notes.md` are not in the
public tree. These remain *historically reported*, not newly verified denominators.
Conditional arithmetic only: 423/367 = 115.3% primary and 437/367 = 119.1%
recorded. Neither is republished as verified coverage. Retrieve the banked county
extracts and verify all county FIPS (especially Ashtabula 39007, not Ashland
39005) before using county ratios. Do not blend CBP and QCEW suppressed cells.
325991 remains without a verified denominator here; missing does not mean zero
or prove that an official source can never publish the cell.

A ratio above 100% is not excess discovery or proof of completeness: the Atlas
includes non-manufacturing sites and inferred NAICS, unlike the official frame;
it also compares a 2026 inventory with a 2023 annual average. The old pass-10
31-site/7-vintage/8-residual decomposition cannot be carried to this pin without
its missing reconciliation inputs and a new analysis. No matched ratio is claimed.

### PIC-12 county numerators (same status/tier/NAICS-326 cuts)

| County, OH | Primary sites | Recorded sites |
|---|---:|---:|
| Ashtabula | 25 | 25 |
| Cuyahoga | 81 | 85 |
| Geauga | 33 | 33 |
| Lake | 34 | 36 |
| Lorain | 23 | 23 |
| Mahoning | 21 | 21 |
| Medina | 18 | 18 |
| Portage | 48 | 50 |
| Stark | 30 | 31 |
| Summit | 91 | 96 |
| Trumbull | 5 | 5 |
| Wayne | 14 | 14 |

## TRI final accounting: separate universes

The queue's post-TRI campaign statement reports **1,797 facilities verdicted
exactly once: 1,657 VERIFIED + 84 REJECT + 56 STILL_UNCERTAIN = 1,797** for passes
20–25. Arithmetic closes. The underlying campaign worklist/verdict ledger is not
in this public tree, so exact-once membership and verdict provenance cannot be
independently reconstructed from canonical records. This is campaign-reported
accounting, not 1,797 new sites or 1,657 new organizations.

Canonical `registry_links.csv`, filtered to `registry == TRI_TRIFID`, instead has
**2,153 link rows, 2,147 distinct registry_id strings, and 1,193 distinct org_id
strings** (all statuses, no site filter). Registry rows are organization-linked,
not a one-row-per-site table. Do not equate these counts with the campaign
worklist, number of creations, national TRI facilities or completeness. Repeated
TRIFIDs are flagged for review only; no dedupe or parent change is authorized.
The full registry table has 2,373 rows; evidence.csv has 12,876 append-only rows.

## Complete public-document audit / disposition register

Every quantitative passage in the eight existing docs and README is classified
below. Historical figures are preserved, not overwritten with today's inventory.
No current status is inferred from a historical source or experiment.

| Document / quantitative passages | Disposition at this pin |
|---|---|
| README: ~600/1,100+/900+ scoping narrative; scaffold 8 + 3 | Replace ambiguous opening claims with definition-first text; label seed 8 organization + 3 ecosystem rows as historical, not current. Add current all-row inventory. |
| COVERAGE_PIC12: every pass-5–12 total, tier mix, county/family table, ratio, gap and decomposition | Historical snapshots, not current; all current-cut numerators restated above/JSON. Underlying old numerator snapshots and denominator files are not all present; don't pretend to rerun them from this pin. 415/429 and 412/428 appear in different sections; neither is today's 423/437. Cuyahoga 85−81 is 4, not the narrative's 5 Tier-U sites. The 3259 62–63 rounding explanation is not independently established by the available files. |
| EVIDENCE_COVERAGE_AUDIT: tier table, missing-claim counts, 1,666-record queue, 25-row sample, fingerprints | Preserve b67b192 historical report; rerun unchanged tool into F5_EVIDENCE_COVERAGE_2026-10-30.md with fresh pin/digests. The bounded eligible queue is now 3,971 records, not 1,666; missing evidence is not a violation verdict. |
| CODEX_PARTNER_MATCHING: 1,483 sites/22 programs; 89 pairs/43 sites/4 programs; 18/71 geography; test/reference totals | Preserve b67b192 snapshot and its test results. Current unchanged matcher gives 1,486 eligible OH sites, 22 eligible OH programs, 194 pairs over 54 sites and 7 programs; 38 same-county and 156 same-state pairs. These are algorithmic candidate pairs, not actual partnerships, coverage or conversion rates. Old 14,237 references/8,018 IDs are historical validation metrics, not today's inventory. |
| SUMMIT_COUNTY_PILOT: 99 rows, all source totals/overlaps, 98–99 dedupe range; extrapolations, staffing and external claims | Recount its published candidate table: 99 rows; source A/B/C/D totals 20/29/51/18; unique-only 14/17/42/10; 83 single-source and 16 multi-source. Three (not two) rows have 3 sources: Goodyear, ARDL, Americhem. Correct that arithmetic explicitly, leaving harvest date intact. 99 remains candidate rows, not verified unique establishments; probable duplicate remains unresolved. 130–180 Summit / statewide and density estimates are historical unvalidated hypotheses, not coverage benchmarks. External staffing/source-list estimates lack banked inputs here. |
| SOURCE_COUNT_RECONCILIATION: all Ohio totals, ranges, employment, vendor/list sizes, source availability, prices and national comparisons | Dated 2026-10-28 scoping/source claims, not current Atlas totals. OH official 890/706/184/115/153 reverified above. 890+115=1,005; +153=1,158 ceiling, not isolated compounding. 865+86+10+35=996 closes but numerical reproduction is not proof of the framework author's provenance; the CBP extract and methodology attribution are unavailable here. Firm estimates, pro-rations and 1,200–2,800 mixed-unit headline recommendation must not be reused as verified statistics. Other external counts/prices remain historical reported claims, not newly fetched/confirmed. |
| SOURCES: measured ~8%/~38%/~41%/~20%, 57 permits/0 verified, historical 890/996/616, geography error percentages | Pipeline-scout results have no row-level sample ledgers in this tree; retain as historical reported precision/yield, not source recall or current coverage. 890 official anchor verified; 996 arithmetic not provenance proof; 616 is the source-reported cleaned study count, not today's Atlas. No fabricated denominator or sample size. |
| OPEN_ISSUES: 12/19 counties, ~99 candidates/4 source types, workflow history | Frozen geography rules are not statistical estimates; ~99 candidate claim is historical pilot (table recount above). Old workflow/access statements are historical; local gates are reported separately, not inferred CI. |
| SCHEMA: every threshold, enum/version/section number and historical birth/split count | No edits: normative thresholds are not dataset counts; birth/split numbers remain historical. Explicitly flag in PR: legacy present-tense dormant TRI language cannot describe today's 2,153 links; any wording clarification belongs to a separate schema revision, not F5. |

### Corrections that must travel with older quotations

- The old Summit three-source row says 2 (2.0%); its own table supports 3/99
  (3.0%). This is a table-count correction, not a new harvest or entity merge.
- Old Cuyahoga primary/recorded 81/85 implies 4 excluded-tier records, not 5.
- The old coverage example's “covers 412 of 367” is not a matched-facility
  fraction. The new figures remain numerator/benchmark comparisons only.
- Exact reproduction of an external aggregate does not establish its historical
  provenance. Do not turn the 996 numerical match into a proven attribution.
- Neither a heterogeneous candidate pilot nor commercial estimates justify a
  firm-count range or a claim that a paid spine is logically required.

## Reproduction and input fingerprints

Run from a clean checkout of the pin. The following standard-library snippet
reads only canonical CSVs; redirect output outside `data/`. The exact output is
[F5_COUNTS_2026-10-30.json](F5_COUNTS_2026-10-30.json), including a SHA-256 manifest
for every canonical CSV. Filters are literal; source SHA is stated above.

```python
import csv, json, hashlib, collections
from pathlib import Path
D=Path('data')
def rows(pattern):
 return [r for p in sorted(D.glob(pattern)) for r in csv.DictReader(p.open())]
S,O=rows('sites_*.csv'),rows('organizations_*.csv')
P=set('Ashtabula Cuyahoga Geauga Lake Lorain Mahoning Medina Portage Stark Summit Trumbull Wayne'.split())
def countcut(rr):
 rr=[r for r in rr if r['operating_status'] in ('active','unknown')]
 return {'primary_A_B_C':sum(r['verification_tier'] in ('A','B','C') for r in rr),'recorded_any_tier':len(rr),'unknown_status':sum(r['operating_status']=='unknown' for r in rr)}
out={'raw_tables':{p.name:len(list(csv.DictReader(p.open()))) for p in sorted(D.glob('*.csv')) if not p.name.startswith(('sites_','organizations_'))},'raw_organizations':len(O),'raw_sites':len(S),'org_tiers':dict(collections.Counter(r['verification_tier'] for r in O)),'site_tiers':dict(collections.Counter(r['verification_tier'] for r in S)),'org_status':dict(collections.Counter(r['status'] for r in O)),'site_status':dict(collections.Counter(r['operating_status'] for r in S)),'coverage':{}}
for area in ['OH','PA','PIC-12']:
 ss=[r for r in S if (r['state']==area if area!='PIC-12' else r['state']=='OH' and r['county'] in P)]
 out['coverage'][area]={'raw_rows':len(ss),'all_naics':countcut(ss),'families':{code:countcut([r for r in ss if r['naics_primary'].startswith(code)]) for code in ['326','3261','3262','3252','3259','325211','325212','325991']},'blank_naics':countcut([r for r in ss if not r['naics_primary']])}
out['pic12_counties_326']={c:countcut([r for r in S if r['state']=='OH' and r['county']==c and r['naics_primary'].startswith('326')]) for c in sorted(P)}
T=[r for r in rows('registry_links.csv') if r['registry']=='TRI_TRIFID']
out['tri']={'link_rows':len(T),'distinct_registry_ids':len(set(r['registry_id'] for r in T)),'distinct_org_ids':len(set(r['org_id'] for r in T))}
out['input_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.glob('*.csv'))}
print(json.dumps(out,indent=2,sort_keys=True))
```

```sh
python3 scripts/validate.py
python3 scripts/build_sqlite.py
python3 scripts/audit_evidence_coverage.py --as-of 2026-10-30 --snapshot-ref eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05 --limit 25 --format markdown
python3 scripts/match_program_capabilities.py > /tmp/f5-match.json
python3 -m unittest discover -s scripts -p 'test_*.py'
git diff --exit-code eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05 -- data/ docs/SCHEMA.md scripts/
```

Matcher input-manifest SHA-256: `614f123ad86026f53ef7b07e735ffa53cc5291a80f80593b8cdc15a96c19ebd9`.

## Integration and review limits

Only README/docs and the required F5 claim change. No inclusion-log rows or
verification tiers change. Owner-only scope/grain questions and repeated TRI
links are not settled here. Missing historical inputs remain explicit blockers
for re-verification; denominator availability failures are not evidence of zero.
Do not mark this as a fully reverified denominator dataset. Recheck main before
integration; do not absorb unrelated changes into the pin's calculations.
