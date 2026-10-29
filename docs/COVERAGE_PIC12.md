# PIC-12 Coverage Report — Atlas establishments vs. official denominators

**Update (2026-10-29, integration pass 9):** Recomputed from the local
repo at its post-integration-pass-9 state (1,758 organizations / 1,862
sites / 58 ecosystem records; org tiers A 620 / B 954 / C 160 / U 24).
Headline PIC-12 NAICS 326 coverage (unit: establishments — Atlas sites,
operating status active/unknown; denominator QCEW 2023, 367): primary
cut (tiers A–C) **320 (87.2%) → 347 (94.6%)**; recorded cut (any tier)
**436 (118.8%) → 463 (126.2%)**. Pass 9 applied the wave-7 requeue,
wave-8 and wave-9 verdicts (131 organization creations +
136 site creations), consolidated two duplicate pairs
pass 8 itself had created (Pioneer/Revere; ENPRESS/Polymer & Steel —
the latter removes one double-counted PIC-12 326 establishment from
the active counts), filled the Qube site's Geauga county, retired the
Original Mattress Factory record on a Ring-4 gate re-run and the
Kennick/Kowalski site on a scope adjudication (B5-contingent). **The
recorded cut exceeds the QCEW-2023 denominator** (463 recorded against
367): the recorded frame counts every recorded candidate including
Tier U rows, and the pass-8 coding of the blank-NAICS backlog plus
post-2023 openings push it past the 2023 denominator — the primary cut
remains the headline measure. Basis note: the "before" figures are
this report's previously published post-pass-8 figures. Every Atlas
figure in the tables below has been recomputed at the post-pass-9
state; denominators are unchanged. The FIPS correction note below is
retained verbatim.

**Computed 2026-10-29** from the local repo copy at its post-integration-pass-9
state (1,758 organizations / 1,862 sites / 58 ecosystem records; org tiers
A 620 / B 954 / C 160 / U 24). **Publication status: this state is NOT yet on
GitHub** — the pass-9 push is executed centrally by the coordinator
after validation, and the public repo shows the post-pass-8 state
(1,627 organizations / 1,726 sites / 58 ecosystem, commit 54752ffe).
Every number below describes the local files, and says so.

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
| **326** Plastics & rubber products | **347** | **463** | **367** | **94.6%** | **126.2%** |
| 3261 Plastics products | 264 | 360 | 283 | 93.3% | 127.2% |
| 3262 Rubber products | 83 | 103 | 84 | 98.8% | 122.6% |
| **3252** Resin, synthetic rubber, fibers (325211+325212+325220) | **38** | **43** | **52** | **73.1%** | **82.7%** |
| **3259** Other chemical products (incl. 325991) | **41** | **49** | **62–63** | **65.1%–66.1%** | **77.8%–79.0%** |
| 325991 Custom compounding (subset of 3259) | 30 | 31 | *no official denominator* | — | — |

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
  sites in Ohio = 719 of QCEW Ohio 890 (**80.8%**); 3252-family 77 of 115
  (67.0%); 3259-family 66 of 153 (43.1%). PIC-12's 326 coverage (94.6%
  primary) runs ahead of the statewide figure.

## 3. County table — NAICS 326 family

Unit: establishments. Atlas columns are sites in the stated cut with
`naics_primary` in 3261/3262. QCEW denominators are published for all 12
counties (QCEW 2023, private, annual average; denominators notes §3.4), so
every county carries a percentage.

| County | Atlas primary | Atlas recorded | QCEW 326 | Primary % | Recorded % | of which QCEW 3261 / 3262 |
|---|---|---|---|---|---|---|
| Ashtabula | 20 | 22 | 21 | 95.2% | 104.8% | 17 / 4 |
| Cuyahoga | 70 | 103 | 65 | 107.7% | 158.5% | 58 / 7 |
| Geauga | 24 | 34 | 28 | 85.7% | 121.4% | 21 / 7 |
| Lake | 22 | 36 | 23 | 95.7% | 156.5% | 17 / 6 |
| Lorain | 18 | 23 | 18 | 100.0% | 127.8% | 15 / 3 |
| Mahoning | 18 | 21 | 19 | 94.7% | 110.5% | 17 / 2 |
| Medina | 17 | 20 | 21 | 81.0% | 95.2% | 12 / 9 |
| Portage | 38 | 48 | 35 | 108.6% | 137.1% | 27 / 8 |
| Stark | 26 | 30 | 30 | 86.7% | 100.0% | 27 / 3 |
| Summit | 79 | 109 | 76 | 103.9% | 143.4% | 48 / 28 |
| Trumbull | 5 | 5 | 13 | 38.5% | 38.5% | 11 / 2 |
| Wayne | 10 | 12 | 18 | 55.6% | 66.7% | 13 / 5 |
| **PIC-12** | **347** | **463** | **367** | **94.6%** | **126.2%** | **283 / 84** |

Read on the outliers:

- **Ashtabula — corrected 2026-10-29.** The first version of this report
  showed Ashtabula exceeding its denominator in both cuts (157.1% /
  214.3%). That was an artifact, not a measurement: the denominators had
  been read from BLS area 39005 (Ashland County) instead of 39007
  (Ashtabula). Against the true denominator of 21, Ashtabula stands at
  95.2% primary / 104.8% recorded (post-pass-9 recomputation) — a
  well-covered county with a small genuine discovery gap (-1 establishments)
  plus 2 Tier U sites of backlog. See the correction note at the head of this report and
  `denominators_notes.md` §3.5.
- **Trumbull remains the thinnest county in PIC-12** (38.5% primary / 38.5%
  recorded) — a genuine discovery gap, not a backlog artifact: there are
  only 5 recorded NAICS-326 sites against 13 expected.
- **Cuyahoga is the largest absolute gap**: 70 primary / 103 recorded
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
| Stark | 0 | suppressed | 0 | 1 (QCEW) | 4 | 2 (QCEW) |
| Summit | 6 | 8 (CBP) | 6 | 4 (CBP) | 10 | 5 (CBP) |
| Trumbull | 2 | suppressed | 0 | suppressed | 0 | suppressed |
| Wayne | 0 | 1 (QCEW) | 2 | 1 (QCEW) | 1 | 1 (QCEW) |
| **PIC-12** | **26** | *43 published + 3 suppressed counties* | **11** | *16 published + 5 suppressed counties* | **30** | *16 published + 5 suppressed counties* |

## 5. Scope — where the two sides do not measure the same thing

- **Atlas scope exceeds the denominators' scope.** The QCEW denominators
  cover only establishments whose *primary* NAICS is 326/3252/3259.
  The Atlas's 688 primary-cut PIC-12 sites decompose as: **426** carrying
  a 326/3252/3259 primary NAICS (the only sites that enter §2), **242**
  carrying a primary NAICS outside those families (machinery,
  distribution, testing, services), and **20** carrying no primary
  NAICS at all. By ring, the same 688 are Ring 1: 353, Ring 2: 135,
  Ring 3: 149, Ring 4: 39, Ring 5: 7, ring unassigned: 5. Everything
  outside the 426 has no denominator in this framework and is never
  ratioed.
- **Denominator scope exceeds the Atlas's scope.** QCEW counts every
  UI-covered establishment in the code, including establishments of firms
  the Atlas has not discovered yet, establishments whose polymer activity
  is captive inside another industry's plant (invisible to any
  NAICS-based list, including this one), and establishments that closed
  between 2023 and 2026. A coverage figure below 100% is therefore the
  expected steady state, not a defect to be explained away.
- **Classification is not shared.** Of the 347 primary-cut PIC-12
  NAICS-326 sites, the NAICS provenance is: researcher-inferred 164, directory-assigned 141, government-filing 29, company-disclosed 13.
  QCEW/Census assign primary NAICS independently; the denominators notes
  (§4.3) show the two official systems disagreeing with each other on the
  same rubber shops (e.g., Summit 326299: CBP 20 vs. QCEW 9). Some of the
  per-county gap — in both directions — is classification, not presence
  or absence.

## 6. How to quote this

- ✅ "The Atlas's verified PIC-12 file (sites, operating status
  active/unknown, tiers A–C) covers 347 of the 367 plastics and rubber
  manufacturing establishments QCEW counted in the 12 counties in 2023 —
  94.6%; counting every recorded candidate including unverified Tier U
  rows, 463 (126.2%)."
- ✅ "Rubber (3262) is the best-covered PIC-12 segment at verified tiers:
  83 of 84 (98.8%). Custom compounding (325991) has 30 verified PIC-12
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

1. **Tier U backlog (the largest single gap).** 263 recorded PIC-12 sites
   (operating status active/unknown) sit at Tier U and are excluded from
   the primary cut — the primary cut (688 sites) is 72% of the
   recorded PIC-12 universe (951 sites). Statewide the excluded Tier U
   count is 533 sites. Closing this gap is verification work, not
   discovery work.
2. **Blank NAICS.** 20 of 688 primary-cut PIC-12 sites (2.9%) — and
   87 of 951 recorded PIC-12 sites (9.1%) — carry no `naics_primary`
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
   (World Resource Solutions, Plain City). SITE-001895's county was settled as **Geauga** in pass 9 from the audit-3 address adjudication (16744 West Park Circle Dr is in Bainbridge Township; Chagrin Falls is the mailing city), leaving two. These two are the
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
   expected) and Wayne (12 vs. 18) are discovery gaps; Cuyahoga (103
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
recomputed at the post-pass-7, post-pass-8 and post-pass-9 local states on 2026-10-29; PIC-12
county membership per AGENTS.md §8; denominator aggregates per
`staging/working/denominators_notes.md` §3.3–§3.4 (QCEW 2023, private
ownership, annual averages; Ashtabula and derived totals as corrected
2026-10-29, §3.5) and per-cell values per
`staging/working/denominators_pic12.csv`. Companion reconciliation of the
statewide published figures (890 / 996 / 616) is in
`docs/SOURCE_COUNT_RECONCILIATION.md`.*
