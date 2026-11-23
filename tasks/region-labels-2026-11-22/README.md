# hq_in_scope region labels — 2026-11-22 (applied in this PR: frame `pic18`)

**Why:** the company-owner review (8 of 20 PIC-18 companies labelled with the retired 12-county region or as other Ohio). Built on `origin/main` 393c3895.
Unit: `organizations` rows, all statuses. Region is a parameter: `rules.py` reads `scripts/regions.py` `REGION` (PIC-18).

## What the field means (and the conflict I am not settling)
SCHEMA §4.4 enum is `ne_ohio | ohio_other | national_us | international`, with `ne_ohio` defined by a 20-county list (incl. Carroll, Holmes) marked "confirm once, then freeze".
AGENTS.md §8 (owner ruling 2026-11-03) says the 19-county list is superseded by PIC-18 and also says "tag records with the county, never a region". The data holds two values
outside the enum (`pic12`, 224 rows; `ohio_statewide`, 94 rows). I read `ne_ohio` as "HQ county is in PIC-18", the only reading consistent with AGENTS §8 and with the 698 existing `ne_ohio` rows (all in PIC-18 counties). That reading is Question 1.

## Rule (only rows with `hq_state` = OH are recomputed)
county in PIC-18 → `ne_ohio`; other valid Ohio county → `ohio_other` (county validity from the repo's own county shapes, `scripts/assets/us-atlas`).
**Relabel only** where the stored label is `pic12`, `ohio_other` or `ohio_statewide` on a PIC-18 county and no Ohio site in the same city sits in a different county.

## Yield
| Class | rows | action |
|---|---|---|
| `pic12` on a PIC-18 county | **224** | → `ne_ohio` |
| `ohio_other` on a PIC-18 county | **78** | → `ne_ohio` (Ashland 9, Columbiana 8, Erie 10, Huron 13, Richland 5, Tuscarawas 28; plus 5 in PIC-12 counties: Ashtabula 1, Lorain 1, Medina 2, Stark 1) |
| `ohio_statewide` on a PIC-18 county | **10** | → `ne_ohio` |
| **Total relabels (all frame `pic18`; none in other Ohio)** | **312** | |
| agree | 1,381 | none |
| `ohio_statewide` on a non-PIC-18 Ohio county | 79 | hold: value is outside the enum and undefined (`ohio_other`?) |
| PIC-18 county but label says `national_us`/`international` | 4 | hold: HQ city/state/county say Ohio, label says elsewhere; verify at a source |
| non-PIC-18 Ohio county but label `national_us` | 2 | hold (same) |
| Ohio county blank / label blank | 8 / 1 | hold |
| `hq_state` blank (national and international shards) | 288 | not recomputable |

**Record errors to verify at a source, not relabel (`record_errors.csv`, 20 rows):** 3 non-Ohio HQ with an Ohio county (Nashville TN + Summit — ORG-000011; Houston TX + Ashtabula — ORG-000007;
Golden CO + Stark — ORG-001391); 9 non-Ohio HQ carrying an Ohio label (e.g. ORG-000372 Huntsman, TX, `ne_ohio`; the DuPont Circleville plant row with a Delaware HQ); 1 county field that is a list (ORG-001147); 4 + 2 Ohio rows whose label says outside Ohio (above).

## Canary (25 rows, `canary-25/frame.csv`)
19 relabels (8 `pic12`, 8 `ohio_other`, 3 `ohio_statewide`) and 6 holds/record errors. Read as the owner: every relabel is a company whose own city is in the county shown
(Dover → Tuscarawas, Sandusky → Erie, Norwalk → Huron, Alliance → Stark, Minerva → Stark). Both review-named records are in (ORG-000955 Dover, ORG-000011 held as a record error). One worth a look: **ORG-001029 PPC Flex** (HQ Alliance, Stark; its only plant is in Franklin County) relabels on its HQ county, which is what the field says.

## Check (`python3 tasks/region-labels-2026-11-22/check.py`)
Recomputes all 312 cells from state + county **and** an independent assertion (after = `ne_ohio` iff `hq_state` OH, county in `regions.PIC18`, label one of the three; recall: every such base row is a change or listed), fails on a planted wrong value, omission and overwrite (verified), requires identical validator output on a scratch apply (exit 0, 245 lines) and a cell-for-cell diff. 10 known-answer cases, including a same-city-site county conflict that must hold (run over every Ohio-HQ row it finds one lead, ORG-002077 Beavercreek recorded as Greene with a site row in Montgomery, listed in `record_errors.csv`; a city can span counties, so it is a lead).

## Reading of `ne_ohio` (SCHEMA v1.19.2) and what stays open
SCHEMA §4.4 now says `ne_ohio` = HQ county in PIC-18, pointing at `scripts/regions.py`. The basis is AGENTS.md §8 alone (owner ruling 2026-11-03: PIC-18 is the reporting region, earlier county lists superseded, every script reads `regions.py`); the old schema list differed from PIC-18 only by Carroll and Holmes. Reviewers should judge that reading; one sentence of §8 ("tag records with the county, never a region") is in tension with a region-valued field and is left untouched.
Not decided here (owner's): the enum values `pic12` / `ohio_statewide` (94 `ohio_statewide` rows remain, outside PIC-18, held); the 4 + 2 Ohio rows whose label says outside Ohio.

## Leads to verify at a source (not relabelled, `record_errors.csv`, 20 rows)
3 non-Ohio HQ with an Ohio county (ORG-000011 Nashville TN + Summit; ORG-000007 Houston TX + Ashtabula; ORG-001391 Golden CO + Stark); 9 non-Ohio HQ carrying an Ohio label (e.g. ORG-000372 TX `ne_ohio`); 1 county field that is a list (ORG-001147); 4 + 2 Ohio rows whose label says outside Ohio; 1 same-city county lead (ORG-002077). A failed fetch is not evidence either way.

## Applying
`BASE_REF` pins the commit the packet was built on. PRs open one at a time and other lanes write the same shards (size PR #468 on `sites_OH.csv`; process lanes on `processes`; a notes lane on `notes`): **rebuild on the then-current main (`BASE_REF`, `python3 build.py`, `check.py`) at apply time**, apply frame `pic18`. `common.apply_changes` refuses any cell whose current value is not the packet's `before`.
Not checked: no canary row was compared against a source (legal names, HQ cities and counties are taken as recorded); city→county was not verified for Ohio rows beyond the repo's own site rows.
