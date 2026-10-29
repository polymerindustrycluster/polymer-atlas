# PIC-12 Coverage Report — Atlas establishments vs. official denominators

**Update (2026-10-29, integration pass 7):** Recomputed from the local
repo at its post-integration-pass-7 state (1,403 organizations / 1,582
sites / 57 ecosystem records; org tiers A 514 / B 769 / C 94 / U 26).
Headline PIC-12 NAICS 326 coverage (unit: establishments — Atlas sites,
operating status active/unknown; denominator QCEW 2023, 367): primary
cut (tiers A–C) **143 (39.0%) → 180 (49.0%)**; recorded cut (any tier)
**216 (58.9%) → 253 (68.9%)**. Basis note: the "before" figures are this
report's previously published figures, computed at its post-pass-5
basis; by the same cuts the post-pass-6 local file already stood at
145 / 218, so the deltas above are doc-to-doc, not pass-7-only. Every
Atlas figure in the tables below has been recomputed at the post-pass-7
state; denominators are unchanged. The FIPS correction note below is
retained verbatim.

**Computed 2026-10-29** from the local repo copy at its post-integration-pass-7
state (1,403 organizations / 1,582 sites / 57 ecosystem records; org tiers
A 514 / B 769 / C 94 / U 26). **Publication status: this state is NOT yet on
GitHub** — the pass-7 push is pending central validation, and the
public repo shows the post-pass-6 state (1,285 organizations / 1,458 sites /
56 ecosystem). Every number below describes the local files, and says so.

**Denominators:** BLS QCEW 2023, annual-average establishments, private
ownership (`own_code=5`), as compiled in
`staging/working/denominators_pic12.csv` and documented in
`staging/working/denominators_notes.md`. QCEW is the single source for every
headline ratio (it is complete for NAICS 326/3261/3262 in all 12 counties and
reproduces the project's statewide anchors exactly: Ohio 326 = 890). CBP 2023
figures are **not** used as denominators — CBP county sums are lower bounds
because of cell withholding (denominators notes §3–§4). The denominators file
mixes CBP and QCEW cell-by-cell at 6-digit detail; per its caveat 1, mixed
sums are never used as denominators here.

**Correction (2026-10-29):** the denominators compilation originally read
Ashtabula County from BLS area 39005 — which is Ashland County; Ashtabula is
39007. Every "Ashtabula" denominator in the first version of this report was
Ashland data. The denominators file and notes have been corrected from a
fresh QCEW pull (see `denominators_notes.md` §3.5), and this report's
Ashtabula row, the PIC-12 totals, and all ratios derived from them have been
corrected in step: the PIC-12 NAICS 326 denominator is **367**, not 353, and
headline coverage is **39.0%** primary / **58.9%** recorded, not 40.5% /
61.2%. The Ashtabula ratios published earlier (157% / 214%) were artifacts
of the FIPS slip and are withdrawn. All other counties' figures were
re-validated against the fresh pull and are unchanged.

---

## 1. Units and filters (read before quoting anything)

- **Unit, both sides: establishments** — a physical location. Atlas side =
  rows of `data/sites.csv`. (Organizations are never the unit in this report;
  per AGENTS.md §7, no count here is a "company" count.)
- **Primary cut (the headline measure):** Atlas sites with
  `operating_status` ∈ {active, unknown}, `verification_tier` ∈ {A, B, C},
  and `county` in PIC-12. Tier per SCHEMA §4.1 is the tier of a record's
  weakest must-have field; Tier U candidates are excluded from headline
  totals by SCHEMA §5.7, so they are excluded here too.
- **Recorded cut (upper bound, supplementary):** the same sites at **any**
  tier, including Tier U. This is a working figure, not a headline count —
  it exists to show how much of the gap is verification backlog rather than
  undiscovered establishments.
- **NAICS matching:** a site counts toward a denominator family only if its
  own `naics_primary` falls in that family. Sites with blank `naics_primary`
  are invisible to every ratio below (quantified in §6).
- **Geography:** PIC-12 per AGENTS.md §8 — Ashtabula, Cuyahoga, Geauga,
  Lake, Lorain, Mahoning, Medina, Portage, Stark, Summit, Trumbull, Wayne.
  County is the site's recorded county (physical address), never mailing
  city.
- **Vintage mismatch, stated once and true throughout:** denominators are
  2023 (QCEW annual 2023); the Atlas snapshot is 2026-10-29. Three years of
  establishment births/deaths sit inside every ratio. QCEW small cells are
  annual averages and carry ±2 rounding (denominators notes caveat 4).

## 2. Headline — PIC-12 totals

| NAICS family | Atlas primary cut (sites) | Atlas recorded cut (sites) | QCEW 2023 denominator (establishments, PIC-12) | Primary coverage | Recorded coverage |
|---|---|---|---|---|---|
| **326** Plastics & rubber products | **180** | **253** | **367** | **49.0%** | **68.9%** |
| 3261 Plastics products | 137 | 186 | 283 | 48.4% | 65.7% |
| 3262 Rubber products | 43 | 67 | 84 | 51.2% | 79.8% |
| **3252** Resin, synthetic rubber, fibers (325211+325212+325220) | **24** | **31** | **52** | **46.2%** | **59.6%** |
| **3259** Other chemical products (incl. 325991) | **26** | **32** | **62–63** | **41.3–41.9%** | **50.8–51.6%** |
| 325991 Custom compounding (subset of 3259) | 18 | 23 | *no official denominator* | — | — |

- 325991 has **no official 6-digit anchor** (denominators notes caveat 7):
  the denominators file's per-county cells for 325991 sum to 16 published
  establishments across 7 counties, but that sum mixes CBP and QCEW cells
  and 5 county cells are suppressed (unknown, not zero), so it is a
  mixed-source lower bound, **not** a denominator. No ratio is quoted. The
  county detail is in §4.
- The 3259 PIC-12 denominator is carried as **62–63**: the fresh-pull
  county cells sum to 62; the originally compiled total was 63. The
  one-establishment difference is annual-average rounding across cells
  (compounded by the §3.5 county correction, which removed one
  establishment from this family's PIC-12 cells), so the coverage figures
  are stated as ranges across the two sums.
- Statewide context (same cuts, same sources): Atlas primary-cut NAICS-326
  sites in Ohio = 450 of QCEW Ohio 890 (**50.6%**); 3252-family 59 of 115
  (51.3%); 3259-family 40 of 153 (26.1%). PIC-12's 326 coverage (49.0%
  primary) is in line with the statewide figure — the PIC-12 build is not
  systematically ahead of the rest-of-Ohio build at verified tiers.

## 3. County table — NAICS 326 family

Unit: establishments. Atlas columns are sites in the stated cut with
`naics_primary` in 3261/3262. QCEW denominators are published for all 12
counties (QCEW 2023, private, annual average; denominators notes §3.4), so
every county carries a percentage.

| County | Atlas primary | Atlas recorded | QCEW 326 | Primary % | Recorded % | of which QCEW 3261 / 3262 |
|---|---|---|---|---|---|---|
| Ashtabula | 15 | 19 | 21 | 71.4% | 90.5% | 17 / 4 |
| Cuyahoga | 24 | 41 | 65 | 36.9% | 63.1% | 58 / 7 |
| Geauga | 13 | 19 | 28 | 46.4% | 67.9% | 21 / 7 |
| Lake | 12 | 15 | 23 | 52.2% | 65.2% | 17 / 6 |
| Lorain | 16 | 16 | 18 | 88.9% | 88.9% | 15 / 3 |
| Mahoning | 8 | 11 | 19 | 42.1% | 57.9% | 17 / 2 |
| Medina | 9 | 13 | 21 | 42.9% | 61.9% | 12 / 9 |
| Portage | 18 | 28 | 35 | 51.4% | 80.0% | 27 / 8 |
| Stark | 17 | 20 | 30 | 56.7% | 66.7% | 27 / 3 |
| Summit | 38 | 59 | 76 | 50.0% | 77.6% | 48 / 28 |
| Trumbull | 2 | 3 | 13 | 15.4% | 23.1% | 11 / 2 |
| Wayne | 8 | 9 | 18 | 44.4% | 50.0% | 13 / 5 |
| **PIC-12** | **180** | **253** | **367** | **49.0%** | **68.9%** | **283 / 84** |

Read on the outliers:

- **Ashtabula — corrected 2026-10-29.** The first version of this report
  showed Ashtabula exceeding its denominator in both cuts (157.1% /
  214.3%). That was an artifact, not a measurement: the denominators had
  been read from BLS area 39005 (Ashland County) instead of 39007
  (Ashtabula). Against the true denominator of 21, Ashtabula stands at
  71.4% primary / 90.5% recorded (post-pass-7 recomputation) — a
  well-covered county with a small genuine discovery gap (2 establishments)
  plus 4 Tier U sites of backlog. See the correction note at the head of this report and
  `denominators_notes.md` §3.5.
- **Trumbull is the thinnest county in PIC-12** (15.4% primary / 23.1%
  recorded) — a genuine discovery gap, not a backlog artifact: there are
  only 3 recorded NAICS-326 sites against 13 expected.
- **Cuyahoga is the largest absolute gap**: 24 primary / 41 recorded
  against 65 expected. It holds the region's biggest denominator and its
  coverage is backlog-shaped (17 of the recorded NAICS-326 sites are
  still Tier U).

## 4. Upstream detail — 325211 / 325212 / 325991 by county (no ratios)

Atlas column = primary-cut sites with that `naics_primary`. Denominator
column = the denominators file's cell for that county × code, with its
source; **suppressed cells are shown as "suppressed — unknown," never as
zero** (97 of the file's 240 cells are suppressed in both sources, as
corrected 2026-10-29). No
percentages are computed in this table: the cells mix CBP and QCEW by
design (denominators notes §2), so per the file's caveat 1 they are
context, not denominators.

| County | 325211 Atlas | 325211 denom. cell | 325212 Atlas | 325212 denom. cell | 325991 Atlas | 325991 denom. cell |
|---|---|---|---|---|---|---|
| Ashtabula | 0 | 1 (QCEW) | 0 | suppressed | 1 | suppressed |
| Cuyahoga | 6 | 16 (CBP) | 0 | 3 (QCEW) | 3 | 1 (QCEW) |
| Geauga | 2 | 3 (QCEW) | 0 | 4 (QCEW) | 0 | 1 (QCEW) |
| Lake | 2 | 4 (CBP) | 0 | suppressed | 1 | suppressed |
| Lorain | 2 | 4 (CBP) | 0 | suppressed | 3 | 3 (QCEW) |
| Mahoning | 0 | suppressed | 0 | suppressed | 0 | suppressed |
| Medina | 2 | 3 (CBP) | 0 | 1 (QCEW) | 0 | suppressed |
| Portage | 2 | 3 (QCEW) | 1 | 2 (QCEW) | 2 | 3 (CBP) |
| Stark | 0 | suppressed | 0 | 1 (QCEW) | 3 | 2 (QCEW) |
| Summit | 2 | 8 (CBP) | 1 | 4 (CBP) | 5 | 5 (CBP) |
| Trumbull | 2 | suppressed | 0 | suppressed | 0 | suppressed |
| Wayne | 0 | 1 (QCEW) | 2 | 1 (QCEW) | 0 | 1 (QCEW) |
| **PIC-12** | **20** | *43 published + 3 suppressed counties* | **4** | *16 published + 5 suppressed counties* | **18** | *16 published + 5 suppressed counties* |

## 5. Scope — where the two sides do not measure the same thing

- **Atlas scope exceeds the denominators' scope.** The QCEW denominators
  cover only establishments whose *primary* NAICS is 326/3252/3259.
  The Atlas's 443 primary-cut PIC-12 sites decompose as: **230** carrying
  a 326/3252/3259 primary NAICS (the only sites that enter §2), **102**
  carrying a primary NAICS outside those families (machinery,
  distribution, testing, services), and **111** carrying no primary
  NAICS at all. By ring, the same 443 are Ring 1: 229, Ring 2: 93,
  Ring 3: 74, Ring 4: 38, Ring 5: 4, ring unassigned: 5. Everything
  outside the 230 has no denominator in this framework and is never
  ratioed.
- **Denominator scope exceeds the Atlas's scope.** QCEW counts every
  UI-covered establishment in the code, including establishments of firms
  the Atlas has not discovered yet, establishments whose polymer activity
  is captive inside another industry's plant (invisible to any
  NAICS-based list, including this one), and establishments that closed
  between 2023 and 2026. A coverage figure below 100% is therefore the
  expected steady state, not a defect to be explained away.
- **Classification is not shared.** Of the 180 primary-cut PIC-12
  NAICS-326 sites, the NAICS provenance is: directory-assigned 112,
  researcher-inferred 58, government-filing 10, company-disclosed 0.
  QCEW/Census assign primary NAICS independently; the denominators notes
  (§4.3) show the two official systems disagreeing with each other on the
  same rubber shops (e.g., Summit 326299: CBP 20 vs. QCEW 9). Some of the
  per-county gap — in both directions — is classification, not presence
  or absence.

## 6. How to quote this

- ✅ "The Atlas's verified PIC-12 file (sites, operating status
  active/unknown, tiers A–C) covers 180 of the 367 plastics and rubber
  manufacturing establishments QCEW counted in the 12 counties in 2023 —
  49.0%; counting every recorded candidate including unverified Tier U
  rows, 253 (68.9%)."
- ✅ "Rubber (3262) is the best-covered PIC-12 segment at verified tiers:
  43 of 84 (51.2%). Custom compounding (325991) has 18 verified PIC-12
  sites; no official denominator exists for that code."
- ❌ Do not quote a single "coverage" number without its cut (primary vs.
  recorded), its unit (establishments/sites), and its denominator
  (QCEW 2023).
- ❌ Do not quote the 325991 figure against the denominators file's
  16-cell sum — that sum is mixed-source with suppressed cells and is not
  a denominator, however tidy the coincidence looks.
- ❌ Do not convert any figure here into "companies." One company with
  three PIC-12 plants is three establishments in every number above.

## 7. Known gaps (quantified)

1. **Tier U backlog (the largest single gap).** 366 recorded PIC-12 sites
   (operating status active/unknown) sit at Tier U and are excluded from
   the primary cut — the primary cut (443 sites) is 55% of the
   recorded PIC-12 universe (809 sites). Statewide the excluded Tier U
   count is 637 sites. Closing this gap is verification work, not
   discovery work.
2. **Blank NAICS.** 111 of 443 primary-cut PIC-12 sites (25.1%) — and
   364 of 809 recorded PIC-12 sites (45.0%) — carry no `naics_primary`
   and are invisible to every NAICS-matched ratio in this report. Some
   are genuinely outside the denominator families; until they are coded,
   the split is unknown, so all §2 ratios are computed only over
   NAICS-carrying sites.
3. **Blank county — 4 sites.** Four Ohio sites promoted in pass 5 from
   the FDA Ring-4 lane carry a parcel flag in place of a county (county
   is assigned from the physical address by parcel evidence, never
   inferred from city — AGENTS.md §4), and are therefore excluded from
   every county table above: SITE-001573 Health-Mor, Inc. — Brooklyn
   (Tier B); SITE-001583 Enable Injections, Inc. — Springdale (Tier A);
   SITE-001587 Health Care Logistics, Inc. — Circleville (Tier A);
   SITE-001614 STERIS Corporation — Mentor (Tier B). Two of the cities
   (Brooklyn, Mentor) lie inside PIC-12 counties and two (Springdale,
   Circleville) outside, but no county is assigned until the parcel
   sweep settles each address. These 4 sites are also the repo's only
   current `validate.py` failures (the "Ohio site without county" rule);
   a validator exception for parcel-flagged sites is an open owner
   decision.
4. **Geocode-uncertain counties — 77 site rows.** The geocode
   SUSPECT/NO_MATCH adjudication closed 169 rows: 86 counties confirmed,
   6 corrected (applied in pass 5), and **77 STILL_UNCERTAIN** — 70 of
   them repo sites whose recorded county stands (no point evidence ever
   contradicted it) but could not be corroborated at address tier, plus
   7 staging-only rows. Their settling route is a county parcel-fabric
   situs hit per site. Until then, county-level counts in §3 carry this
   uncertainty inside them.
5. **Thin counties.** Trumbull (3 recorded NAICS-326 sites vs. 13
   expected) and Wayne (9 vs. 18) are discovery gaps; Cuyahoga (41
   recorded vs. 65) is principally a verification-backlog gap (see §3).
6. **Suppressed denominator cells.** 97 of the denominators file's 240
   county × code cells are published by neither CBP nor QCEW and are
   recorded as suppressed, not zero (denominators notes §5, as corrected
   2026-10-29). At 6-digit
   detail (tire codes 326211/326212 in 10 of 12 counties; 326191 nearly
   everywhere) there is often **no denominator at all** — Atlas records
   in those cells stand on their own evidence and are never "over
   coverage" for exceeding an unpublished count.

---

*Method note: all Atlas figures were computed directly from
`data/sites.csv` at the post-pass-5 local state on 2026-10-29, and
recomputed at the post-pass-7 local state on 2026-10-29; PIC-12
county membership per AGENTS.md §8; denominator aggregates per
`staging/working/denominators_notes.md` §3.3–§3.4 (QCEW 2023, private
ownership, annual averages; Ashtabula and derived totals as corrected
2026-10-29, §3.5) and per-cell values per
`staging/working/denominators_pic12.csv`. Companion reconciliation of the
statewide published figures (890 / 996 / 616) is in
`docs/SOURCE_COUNT_RECONCILIATION.md`.*
