# Economic pulse indicators (reference data)

**Status: context data, not canonical Atlas data.** Nothing here is merged into
`data/`, and nothing here changes a record, tier, status or count in the Atlas.
These series give reports and the static site a dated macro backdrop (prices,
output, employment, earnings, GDP, energy cost) for the polymer / plastics /
rubber industry. **No causal claims are made or implied**: a price moving
alongside employment or output is two published numbers side by side, nothing more.
None of these series measure Atlas organizations or establishments, and none
uses the PIC-12 county definition: they are national or state aggregates
published by other agencies.

Built by `scripts/build_indicators.py` (stdlib only; re-runnable, see "Reproduce").

| File | Content |
|---|---|
| `indicators_series.csv` | Long format, one row per series x observation: `source, series_id, title, units, frequency, geo, date, value` (41 series, 2,658 observations) |
| `catalog.csv` | One row per series: ID, title, units, frequency, geography, request URL (key shown as `<KEY>`), retrieved date, latest date and value, first date, observation count, seasonal adjustment, notes (vintage, preliminary months, gaps) |

`date` is the first day of the month for monthly series. For BEA annual series
`date` is January 1 of the **data year** (2025-01-01 means calendar-year 2025). A
period with no published value has no row; it is never written as zero.

## Retrieval and vintage

- **Retrieved:** 2026-11-01 (UTC) through the session proxy. Window: January 2016 to the latest published period (BEA: 2016-2025, the API's `LAST10`).
- **All of these series are revised.** The values here are what each API served on the retrieval date; a later pull can differ.

| Source | Vintage as served on 2026-11-01 |
|---|---|
| FRED (St. Louis Fed) | Latest period 2026-09 for every series. FRED `last_updated`: PPI series 2026-10-15; industrial production 2026-10-16; CES employment 2026-10-02. PPI figures for recent months and CES figures are revised by the underlying agencies |
| BLS API v2 | Latest period 2026-09. The two most recent months (2026-08, 2026-09) carry BLS footnote P (preliminary) |
| BEA Regional | Annual, latest year **2025**. BEA note: "Last updated: September 30, 2026 -- revised statistics for 2019-2025" (current-dollar table) and "...2018-2025" (real table) |
| EIA API v2 | Electricity and natural gas: latest 2026-08. Propane spot: latest 2026-09. State gas series have unpublished months (see Caveats) |

## Sources, filters and the series verified

Every series ID was confirmed against the source's own metadata endpoint on the
retrieval date before data were kept (the script aborts if an ID is missing or
its title/measure does not match). Units, frequency and titles in `catalog.csv`
are the ones the source served.

### FRED (10 series; `https://api.stlouisfed.org/fred/series` and `/series/observations`)

| Series | Title as served | Units | SA |
|---|---|---|---|
| `PCU325211325211` | PPI by Industry: Plastics Material and Resin Manufacturing | Index Dec 1980=100 | NSA |
| `PCU325212325212` | PPI by Industry: Synthetic Rubber Manufacturing | Index Jun 1981=100 | NSA |
| `PCU32613261` | PPI by Industry: Plastics Product Manufacturing | Index Jun 1993=100 | NSA |
| `PCU326326` | PPI by Industry: Plastics and Rubber Products Manufacturing | Index Dec 1984=100 | NSA |
| `PCU32623262` | PPI by Industry: Rubber Product Manufacturing | Index Dec 2003=100 | NSA |
| `IPG326S` | Industrial Production: Plastics and Rubber Products (NAICS 326) | Index 2017=100 | SA |
| `IPG3261S` | Industrial Production: Plastics Product (NAICS 3261) | Index 2017=100 | SA |
| `IPG3262S` | Industrial Production: Rubber Product (NAICS 3262) | Index 2017=100 | SA |
| `IPG3252S` | Industrial Production: Resin, Synthetic Rubber, and Artificial and Synthetic Fibers and Filaments (NAICS 3252) | Index 2017=100 | SA |
| `CES3232600001` | All Employees, Plastics and Rubber Products Manufacturing | Thousands of persons | SA |

### BLS API v2 (2 published series, 1 cross-check; `POST https://api.bls.gov/publicAPI/v2/timeseries/data/`)

| Series | Title as served | Units |
|---|---|---|
| `CES3232600003` | Average hourly earnings of all employees, plastics and rubber products manufacturing, SA | Dollars per hour |
| `CES3232600008` | Average hourly earnings of production and nonsupervisory employees, plastics and rubber products manufacturing, SA | Dollars per hour |

`CES3232600001` (all employees) was also requested from BLS only as a cross-check
of the FRED copy: 129 months compared, 0 mismatches. It is not duplicated in the
CSV. OEWS is not available through the BLS API and is not included.

### BEA Regional (22 series; `https://apps.bea.gov/api/data`, dataset `Regional`)

- **Tables:** `SAGDP2` (GDP by state, millions of current dollars) and `SAGDP9` (real GDP by state, millions of chained 2017 dollars).
- **Line code 33**, verified through `GetParameterValuesFiltered` on both tables as "Plastics and rubber products manufacturing (326)".
- **Geographies (11):** United States (`00000`), plus the 10 states with the most **private NAICS 326 establishments in 2024** in `docs/denominators/qcew_state_polymer_2023_2024.csv` (QCEW annual averages, `own_code` 5): California 1,284; Texas 971; Ohio 917; Florida 828; Illinois 806; Michigan 780; Pennsylvania 644; Georgia 538; Indiana 514; North Carolina 455. Ohio and Pennsylvania are both in that top 10; the script asserts it.
- BEA's "United States" row is its national total for the industry. The BEA note on the difference between the United States and the sum of states (overseas activity) applies to all-industry and government totals, not to NAICS 326.
- **Series ID convention:** `SAGDP2-33@<state FIPS>000` and `SAGDP9-33@<state FIPS>000` (a project label; BEA has no single series ID).
- **County-level detail for this industry is not available.** BEA's county table `CAGDP2` publishes no NAICS 326 or plastics-and-rubber line: its only manufacturing lines are Manufacturing (31-33), Durable goods manufacturing, Nondurable goods manufacturing (311-316, 322-326) and Manufacturing and information. Verified on the retrieval date; nothing is suppressed or imputed here. County-level polymer context stays with the QCEW county denominators.
- No BEA cell for these 11 geographies x 10 years x 2 tables was non-numeric (no `(D)` suppression), so no BEA row is missing.

### EIA API v2 (7 series; `https://api.eia.gov/v2/`)

| Series ID (project label = route:measure:facet) | What it is | Units |
|---|---|---|
| `electricity/retail-sales:price:IND:OH` / `:PA` / `:US` | Average retail price of electricity, industrial sector, Ohio / Pennsylvania / US total | Cents per kilowatt-hour |
| `natural-gas/pri/sum:N3035OH3` / `N3035PA3` / `N3035US3` | Natural gas industrial price (process `PIN`), Ohio / Pennsylvania / US (EIA series IDs) | Dollars per thousand cubic feet |
| `petroleum/pri/spt:EER_EPLLPA_PF4_Y44MB_DPG` | Mont Belvieu, TX propane spot price FOB (feedstock context) | Dollars per gallon |

**Ethane is not available.** EIA's spot-price route lists 11 series; the only NGL among them
is Mont Belvieu propane. No Mont Belvieu ethane spot series exists in the EIA API
(and a FRED search for ethane returned only PPI plant-condensate/NGL commodity
indexes, not a spot price; those were not pulled). Propane is therefore the only
feedstock-price series, and it is not a proxy for ethane.

## How the summary figures are computed

- **Latest** = the most recent published period in the series (the period is shown).
- **1-yr / 5-yr change** = percent change of the latest value versus the value for the **same month** 12 / 60 months earlier (annual series: same measure 1 / 5 years earlier). If the comparison month has no published value the cell reads `n/a`; nothing is interpolated.
- Percent changes of **index levels, prices and dollar values** are plain ratios; they are not inflation-adjusted unless the series says so (only `SAGDP9` is real).
- **Share of US GDP** = state `SAGDP2` line 33 / US `SAGDP2` line 33, same year, current dollars, in percent. Shares are **not** computed from `SAGDP9`: chained-dollar state values do not sum to the national figure.
- QCEW establishment counts used for ranking are the private-sector 2024 annual averages already in `docs/denominators/`; they are used only to choose the 10 states.

## Dashboard summary

<!-- SUMMARY:BEGIN -->
**Prices (PPI, NSA indexes; FRED / BLS)**

| Series | ID | Units | Latest | Period | 1-yr change | 5-yr change |
|---|---|---|---:|---|---:|---:|
| PPI plastics material and resin mfg (325211) | `PCU325211325211` | Index Dec 1980=100 | 327.535 | 2026-09 | +5.9% | -13.1% |
| PPI synthetic rubber mfg (325212) | `PCU325212325212` | Index Jun 1981=100 | 303.91 | 2026-09 | +10.7% | +11.1% |
| PPI plastics products mfg (3261) | `PCU32613261` | Index Jun 1993=100 | 240.304 | 2026-09 | +6.3% | +19.2% |
| PPI rubber products mfg (3262) | `PCU32623262` | Index Dec 2003=100 | 205.864 | 2026-09 | +3.3% | +24.4% |
| PPI plastics and rubber products mfg (326) | `PCU326326` | Index Dec 1984=100 | 269.793 | 2026-09 | +5.7% | +20.1% |

**Output, employment, earnings (national, SA; FRED / BLS)**

| Series | ID | Units | Latest | Period | 1-yr change | 5-yr change |
|---|---|---|---:|---|---:|---:|
| Industrial production, NAICS 326 | `IPG326S` | Index 2017=100 | 94.1478 | 2026-09 | +0.7% | -6.0% |
| Industrial production, NAICS 3261 | `IPG3261S` | Index 2017=100 | 95.4287 | 2026-09 | -0.1% | -6.8% |
| Industrial production, NAICS 3262 | `IPG3262S` | Index 2017=100 | 88.8689 | 2026-09 | +4.9% | -1.6% |
| Industrial production, NAICS 3252 | `IPG3252S` | Index 2017=100 | 99.7338 | 2026-09 | -0.9% | +14.5% |
| All employees, NAICS 326 | `CES3232600001` | Thousands of Persons | 694.9 | 2026-09 | -0.9% | -4.6% |
| Avg hourly earnings, all employees, NAICS 326 | `CES3232600003` | Dollars per hour | 31.9 | 2026-09 | +4.6% | +21.5% |
| Avg hourly earnings, production and nonsupervisory, NAICS 326 | `CES3232600008` | Dollars per hour | 26.4 | 2026-09 | +3.4% | +19.8% |

**Energy and feedstock cost context (EIA, monthly, NSA)**

| Series | ID | Units | Latest | Period | 1-yr change | 5-yr change |
|---|---|---|---:|---|---:|---:|
| Industrial electricity price, Ohio | `electricity/retail-sales:price:IND:OH` | Cents per kilowatt-hour | 9.75 | 2026-08 | +15.1% | +47.5% |
| Industrial electricity price, Pennsylvania | `electricity/retail-sales:price:IND:PA` | Cents per kilowatt-hour | 10.47 | 2026-08 | +8.4% | +56.5% |
| Industrial electricity price, US | `electricity/retail-sales:price:IND:US` | Cents per kilowatt-hour | 9.64 | 2026-08 | +7.3% | +27.9% |
| Industrial natural gas price, Ohio | `natural-gas/pri/sum:N3035OH3` | Dollars per thousand cubic feet | 9.17 | 2026-07 | n/a | +11.0% |
| Industrial natural gas price, Pennsylvania | `natural-gas/pri/sum:N3035PA3` | Dollars per thousand cubic feet | 12.38 | 2026-08 | n/a | +54.6% |
| Industrial natural gas price, US | `natural-gas/pri/sum:N3035US3` | Dollars per thousand cubic feet | 4.34 | 2026-08 | -2.9% | -12.3% |
| Propane spot price, Mont Belvieu TX | `petroleum/pri/spt:EER_EPLLPA_PF4_Y44MB_DPG` | Dollars per gallon | 0.848 | 2026-09 | +23.3% | -34.3% |

**BEA GDP by state, Plastics and rubber products manufacturing (NAICS 326), current dollars (SAGDP2 line 33), 2025**

| Geography | QCEW 2024 NAICS 326 private establishments (rank) | GDP 2025, $ millions | 1-yr change | 5-yr change | Share of US GDP 2025 | Share 2020 |
|---|---:|---:|---:|---:|---:|---:|
| US | - | 94,074 | -1.5% | +17.5% | 100% | 100% |
| CA | 1,284 (#1) | 5,984 | -3.5% | +17.3% | 6.4% | 6.4% |
| TX | 971 (#2) | 6,883 | +1.2% | +45.1% | 7.3% | 5.9% |
| OH | 917 (#3) | 6,359 | +0.4% | -1.4% | 6.8% | 8.1% |
| FL | 828 (#4) | 2,296 | +0.0% | +59.6% | 2.4% | 1.8% |
| IL | 806 (#5) | 5,450 | -16.8% | -2.5% | 5.8% | 7.0% |
| MI | 780 (#6) | 4,044 | -1.9% | +5.9% | 4.3% | 4.8% |
| PA | 644 (#7) | 5,590 | +0.9% | +26.4% | 5.9% | 5.5% |
| GA | 538 (#8) | 3,838 | -0.5% | +40.0% | 4.1% | 3.4% |
| IN | 514 (#9) | 4,111 | +2.4% | +31.9% | 4.4% | 3.9% |
| NC | 455 (#10) | 4,572 | +1.5% | +12.6% | 4.9% | 5.1% |

**Ohio and Pennsylvania share of US NAICS 326 GDP, by year** (state GDP / US GDP, both SAGDP2 current dollars)

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ohio | 7.4% | 7.3% | 7.8% | 7.6% | 8.1% | 7.4% | 6.9% | 6.7% | 6.6% | 6.8% |
| Pennsylvania | 5.9% | 5.6% | 5.4% | 5.7% | 5.5% | 5.5% | 5.5% | 5.7% | 5.8% | 5.9% |
| OH + PA | 13.3% | 12.9% | 13.2% | 13.3% | 13.6% | 12.8% | 12.3% | 12.4% | 12.4% | 12.7% |

**BEA real GDP by state, NAICS 326 (SAGDP9 line 33, millions of chained 2017 dollars)**

| Geography | 2025 | 1-yr change | 5-yr change |
|---|---:|---:|---:|
| US | 63,211 | +0.4% | -17.8% |
| CA | 4,020 | -1.7% | -17.9% |
| TX | 4,625 | +3.2% | +1.5% |
| OH | 4,273 | +2.4% | -31.0% |
| FL | 1,543 | +1.9% | +11.6% |
| IL | 3,662 | -15.2% | -31.8% |
| MI | 2,717 | +0.0% | -25.9% |
| PA | 3,756 | +2.8% | -11.5% |
| GA | 2,579 | +1.4% | -2.1% |
| IN | 2,762 | +4.4% | -7.7% |
| NC | 3,072 | +3.5% | -21.2% |
<!-- SUMMARY:END -->

Reading notes (units and filters for every number above):

- **National series** (PPI, industrial production, CES) cover the whole US industry named in the series title, not Ohio, PIC-12 or the Atlas.
- **"Ohio share of US plastics and rubber GDP"** = BEA current-dollar GDP of NAICS 326 (Plastics and rubber products manufacturing) located in Ohio / the same measure for the United States, calendar year 2025, BEA vintage of 2026-09-30. It is a value-added share by industry, **not** an establishment count, employment share or PIC-12 figure.
- PPI, industrial production and CES rows are as published as of 2026-11-01; BLS marks the two latest CES months preliminary.

## Caveats

- **Gappy state gas series.** EIA published no value for Ohio natural gas industrial price in 2025-07, 2025-08, 2025-09 and 2026-08, and none for Pennsylvania in 2025-08, 2026-05 and 2026-06 (see `catalog.csv` notes). Where the same-month comparison is missing the summary shows `n/a`, and Ohio's "latest" is therefore 2026-07 while Pennsylvania's and the US are 2026-08. The state gas levels (from 2025-01 through the latest month: Ohio about 8 to 12, Pennsylvania about 9 to 13 and the US about 4 to 8 dollars per thousand cubic feet, over the months each series has published) are shown as EIA publishes them; this set does not investigate or reconcile why state and national levels differ, so do not compare levels across geographies without reading EIA's own methodology notes.
- **Different vintages and periods across sources.** Annual BEA data end in 2025; monthly federal series end in 2026-08 or 2026-09. Mixing them in one chart needs an explicit period label.
- **PPI series are by industry (shipments of that industry), not material-grade prices**; the resin index is the NAICS 325211 industry index, not a price for any particular polymer.
- **Seasonal adjustment differs by series** (`SA` column above); compare 1-yr and 5-yr changes only within a series.
- The 2025 Illinois current-dollar change (-16.8%) and the large real-GDP swings in some states are as BEA publishes them; they are not examined or explained here.

## Request URLs

Every request and its URL template (key replaced by `<KEY>`) is in `catalog.csv`
(`source_url`). Examples:

- FRED: `https://api.stlouisfed.org/fred/series/observations?series_id=PCU325211325211&api_key=<KEY>&file_type=json&observation_start=2016-01-01`
- BEA: `https://apps.bea.gov/api/data?UserID=<KEY>&method=GetData&datasetname=Regional&TableName=SAGDP2&LineCode=33&GeoFips=39000&Year=LAST10&ResultFormat=JSON`
- EIA: `https://api.eia.gov/v2/electricity/retail-sales/data?api_key=<KEY>&frequency=monthly&data[0]=price&start=2016-01&facets[sectorid][]=IND&facets[stateid][]=OH`
- BLS: `POST https://api.bls.gov/publicAPI/v2/timeseries/data/` with JSON body `{"seriesid":["CES3232600003"],"startyear":"2016","endyear":"2026","registrationkey":"<KEY>","catalog":true}`

## Reproduce

```
set -a; . /root/.config/polymer-atlas/api_keys.env; set +a   # FRED_API_KEY, BEA_API_KEY, BLS_API_KEY, EIA_API_KEY
python3 scripts/build_indicators.py --refresh --update-readme
```

- Keys are read from environment variables only. Raw responses are cached in
  `/tmp/claude-0/indicators_raw/` under filenames that are hashes of the request
  with the key removed; BEA echoes the key in its response, so the script blanks
  that field before caching, refuses to cache any body containing a key, and
  checks every file it writes. Without `--refresh` a re-run reads the cache.
- `--update-readme` rewrites only the block between the SUMMARY markers.
- A re-run on a later date will show later vintages; the retrieved date written to
  `catalog.csv` is the constant `RETRIEVED` in the script and should be updated
  with it.
