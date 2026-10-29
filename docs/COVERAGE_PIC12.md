# PIC-12 Coverage Report — Atlas establishments vs. official denominators

**Update (2026-10-29, integration pass 8):** Recomputed from the local
repo at its post-integration-pass-8 state (1,627 organizations / 1,726
sites / 58 ecosystem records; org tiers A 581 / B 881 / C 141 / U 24).
Headline PIC-12 NAICS 326 coverage (unit: establishments — Atlas sites,
operating status active/unknown; denominator QCEW 2023, 367): primary
cut (tiers A–C) **180 (49.0%) → 320 (87.2%)**; recorded cut (any tier)
**253 (68.9%) → 436 (118.8%)**. Pass 8 was a conversion pass: the
site-tier burn-down (96 upgrades) and the lane-2 NAICS coding of the
blank-NAICS backlog (513 sites) contribute most of the gain, ahead of
the wave 4–7 creations. **The recorded cut now exceeds the QCEW-2023
denominator** (436 recorded against 367): the recorded frame counts every
recorded candidate including Tier U rows, and the pass-8 coding of the
blank-NAICS backlog plus post-2023 openings push it past the 2023
denominator — the primary cut remains the headline measure. Basis note:
the "before" figures are this report's previously published post-pass-7
figures. Every Atlas figure in the tables below has been recomputed at
the post-pass-8 state; denominators are unchanged. Two pass-8
integrator determinations are journaled in the pass-8 integration log
(a same-operator dedupe conversion and a Ring 5 schema-assert hold);
they move the org/site/ecosystem totals by one each against the prep
projection and do not change any coverage figure's method. The FIPS correction note below is
retained verbatim.

**Computed 2026-10-29** from the local repo copy at its post-integration-pass-8
state (1,627 organizations / 1,726 sites / 58 ecosystem records; org tiers
A 581 / B 881 / C 141 / U 24). **Publication status: this state is NOT yet on
GitHub** — the pass-8 push is pending central validation, and the
public repo shows the post-pass-7 state (1,402 organizations / 1,581 sites /
57 ecosystem). Every number below describes the local files, and says so.

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
| **326** Plastics & rubber products | **320** | **436** | **367** | **87.2%** | **118.8%** |
| 3261 Plastics products | 242 | 338 | 283 | 85.5% | 119.4% |
| 3262 Rubber products | 78 | 98 | 84 | 92.9% | 116.7% |
| **3252** Resin, synthetic rubber, fibers (325211+325212+325220) | **38** | **43** | **52** | **73.1%** | **82.7%** |
| **3259** Other chemical products (incl. 325991) | **38** | **46** | **62–63** | **60.3%–61.3%** | **73.0%–74.2%** |
| 325991 Custom compounding (subset of 3259) | 27 | 28 | *no official denominator* | — | — |

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
  sites in Ohio = 669 of QCEW Ohio 890 (**75.2%**); 3252-family 77 of 115
  (67.0%); 3259-family 56 of 153 (36.6%). PIC-12's 326 coverage (87.2%
  primary) now runs ahead of the statewide figure — pass 8's conversions
  (site-tier burn-down + lane-2 NAICS coding) were PIC-12-weighted.

## 3. County table — NAICS 326 family

Unit: establishments. Atlas columns are sites in the stated cut with
`naics_primary` in 3261/3262. QCEW denominators are published for all 12
counties (QCEW 2023, private, annual average; denominators notes §3.4), so
every county carries a percentage.

| County | Atlas primary | Atlas recorded | QCEW 326 | Primary % | Recorded % | of which QCEW 3261 / 3262 |
|---|---|---|---|---|---|---|
| Ashtabula | 18 | 20 | 21 | 85.7% | 95.2% | 17 / 4 |
| Cuyahoga | 68 | 101 | 65 | 104.6% | 155.4% | 58 / 7 |
| Geauga | 21 | 31 | 28 | 75.0% | 110.7% | 21 / 7 |
| Lake | 21 | 35 | 23 | 91.3% | 152.2% | 17 / 6 |
| Lorain | 18 | 23 | 18 | 100.0% | 127.8% | 15 / 3 |
| Mahoning | 15 | 18 | 19 | 78.9% | 94.7% | 17 / 2 |
| Medina | 15 | 18 | 21 | 71.4% | 85.7% | 12 / 9 |
| Portage | 34 | 44 | 35 | 97.1% | 125.7% | 27 / 8 |
| Stark | 23 | 27 | 30 | 76.7% | 90.0% | 27 / 3 |
| Summit | 73 | 103 | 76 | 96.1% | 135.5% | 48 / 28 |
| Trumbull | 5 | 5 | 13 | 38.5% | 38.5% | 11 / 2 |
| Wayne | 9 | 11 | 18 | 50.0% | 61.1% | 13 / 5 |
| **PIC-12** | **320** | **436** | **367** | **87.2%** | **118.8%** | **283 / 84** |

Read on the outliers:

- **Ashtabula — corrected 2026-10-29.** The first version of this report
  showed Ashtabula exceeding its denominator in both cuts (157.1% /
  214.3%). That was an artifact, not a measurement: the denominators had
  been read from BLS area 39005 (Ashland County) instead of 39007
  (Ashtabula). Against the true denominator of 21, Ashtabula stands at
  85.7% primary / 95.2% recorded (post-pass-8 recomputation) — a
  well-covered county with a small genuine discovery gap (1 establishments)
  plus 2 Tier U sites of backlog. See the correction note at the head of this report and
  `denominators_notes.md` §3.5.
- **Trumbull remains the thinnest county in PIC-12** (38.5% primary / 38.5%
  recorded) — a genuine discovery gap, not a backlog artifact: there are
  only 5 recorded NAICS-326 sites against 13 expected.
- **Cuyahoga is the largest absolute gap**: 68 primary / 101 recorded
  against 65 expected. It holds the region's biggest denominator and its
  coverage is backlog-shaped (33 of the recorded NAICS-326 sites are
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
| Cuyahoga | 7 | 16 (CBP) | 1 | 3 (QCEW) | 7 | 1 (QCEW) |
| Geauga | 2 | 3 (QCEW) | 0 | 4 (QCEW) | 0 | 1 (QCEW) |
| Lake | 2 | 4 (CBP) | 0 | suppressed | 1 | suppressed |
| Lorain | 2 | 4 (CBP) | 0 | suppressed | 3 | 3 (QCEW) |
| Mahoning | 0 | suppressed | 0 | suppressed | 0 | suppressed |
| Medina | 3 | 3 (CBP) | 0 | 1 (QCEW) | 1 | suppressed |
| Portage | 2 | 3 (QCEW) | 2 | 2 (QCEW) | 2 | 3 (CBP) |
| Stark | 0 | suppressed | 0 | 1 (QCEW) | 3 | 2 (QCEW) |
| Summit | 6 | 8 (CBP) | 6 | 4 (CBP) | 9 | 5 (CBP) |
| Trumbull | 2 | suppressed | 0 | suppressed | 0 | suppressed |
| Wayne | 0 | 1 (QCEW) | 2 | 1 (QCEW) | 0 | 1 (QCEW) |
| **PIC-12** | **26** | *43 published + 3 suppressed counties* | **11** | *16 published + 5 suppressed counties* | **27** | *16 published + 5 suppressed counties* |

## 5. Scope — where the two sides do not measure the same thing

- **Atlas scope exceeds the denominators' scope.** The QCEW denominators
  cover only establishments whose *primary* NAICS is 326/3252/3259.
  The Atlas's 625 primary-cut PIC-12 sites decompose as: **396** carrying
  a 326/3252/3259 primary NAICS (the only sites that enter §2), **210**
  carrying a primary NAICS outside those families (machinery,
  distribution, testing, services), and **19** carrying no primary
  NAICS at all. By ring, the same 625 are Ring 1: 326, Ring 2: 130,
  Ring 3: 118, Ring 4: 40, Ring 5: 6, ring unassigned: 5. Everything
  outside the 230 has no denominator in this framework and is never
  ratioed.
- **Denominator scope exceeds the Atlas's scope.** QCEW counts every
  UI-covered establishment in the code, including establishments of firms
  the Atlas has not discovered yet, establishments whose polymer activity
  is captive inside another industry's plant (invisible to any
  NAICS-based list, including this one), and establishments that closed
  between 2023 and 2026. A coverage figure below 100% is therefore the
  expected steady state, not a defect to be explained away.
- **Classification is not shared.** Of the 320 primary-cut PIC-12
  NAICS-326 sites, the NAICS provenance is: researcher-inferred 150, directory-assigned 141, government-filing 28, company-disclosed 1.
  QCEW/Census assign primary NAICS independently; the denominators notes
  (§4.3) show the two official systems disagreeing with each other on the
  same rubber shops (e.g., Summit 326299: CBP 20 vs. QCEW 9). Some of the
  per-county gap — in both directions — is classification, not presence
  or absence.

## 6. How to quote this

- ✅ "The Atlas's verified PIC-12 file (sites, operating status
  active/unknown, tiers A–C) covers 320 of the 367 plastics and rubber
  manufacturing establishments QCEW counted in the 12 counties in 2023 —
  87.2%; counting every recorded candidate including unverified Tier U
  rows, 436 (118.8%)."
- ✅ "Rubber (3262) is the best-covered PIC-12 segment at verified tiers:
  78 of 84 (92.9%). Custom compounding (325991) has 27 verified PIC-12
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

1. **Tier U backlog (the largest single gap).** 266 recorded PIC-12 sites
   (operating status active/unknown) sit at Tier U and are excluded from
   the primary cut — the primary cut (625 sites) is 70% of the
   recorded PIC-12 universe (891 sites). Statewide the excluded Tier U
   count is 536 sites. Closing this gap is verification work, not
   discovery work.
2. **Blank NAICS.** 19 of 625 primary-cut PIC-12 sites (3.0%) — and
   86 of 891 recorded PIC-12 sites (9.7%) — carry no `naics_primary`
   and are invisible to every NAICS-matched ratio in this report. Some
   are genuinely outside the denominator families; until they are coded,
   the split is unknown, so all §2 ratios are computed only over
   NAICS-carrying sites.
3. **Blank county — settled, then three new parcel-queue sites.**
   The four pass-5 FDA parcel-flagged sites were settled from parcel
   evidence in pass 6 (SITE-001573 Cuyahoga, SITE-001583 Hamilton,
   SITE-001587 Pickaway, SITE-001614 Lake), and the final flagged site,
   SITE-001634 (IEG, Bellefontaine), was settled as **Logan County** in
   pass 8 from the Logan County parcel fabric (parcel
   11-076-00-00-041-004) — no Ohio site in the repo carries an
   unsettled blank county from the pre-pass-8 population. The owner's
   2026-10-29 ruling permits a blank county only for sites whose notes
   carry the `parcel candidate queue` marker (validator warning, not
   error). Pass 8 created exactly three such sites, each an
   address-verified establishment on a county-straddling city whose
   parcel record is the settling route: SITE-001850 (ACSIC Ingredients,
   Dublin), SITE-001895 (Qube Corporation, Chagrin Falls), SITE-001907
   (World Resource Solutions, Plain City). These three are the
   validator's entire warning set and are excluded from county tables
   until their parcel sweeps land.
4. **Geocode-uncertain counties — 77 site rows.** The geocode
   SUSPECT/NO_MATCH adjudication closed 169 rows: 86 counties confirmed,
   6 corrected (applied in pass 5), and **77 STILL_UNCERTAIN** — 70 of
   them repo sites whose recorded county stands (no point evidence ever
   contradicted it) but could not be corroborated at address tier, plus
   7 staging-only rows. Their settling route is a county parcel-fabric
   situs hit per site. Until then, county-level counts in §3 carry this
   uncertainty inside them.
5. **Thin counties.** Trumbull (5 recorded NAICS-326 sites vs. 13
   expected) and Wayne (11 vs. 18) are discovery gaps; Cuyahoga (101
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
recomputed at the post-pass-7 and post-pass-8 local states on 2026-10-29; PIC-12
county membership per AGENTS.md §8; denominator aggregates per
`staging/working/denominators_notes.md` §3.3–§3.4 (QCEW 2023, private
ownership, annual averages; Ashtabula and derived totals as corrected
2026-10-29, §3.5) and per-cell values per
`staging/working/denominators_pic12.csv`. Companion reconciliation of the
statewide published figures (890 / 996 / 616) is in
`docs/SOURCE_COUNT_RECONCILIATION.md`.*
