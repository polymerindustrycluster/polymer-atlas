# IPEDS completions layer: where polymer and materials degrees are taught

The layer shows where polymer, plastics and materials degrees are taught in the United States, and how that has
changed since 1991. It comes from the federal IPEDS completions survey. The schema is in SCHEMA §4.23; this page is the
reading guide.

| Table | Rows | What it holds |
|-|-|-|
| `data/ipeds_institutions.csv` | 343 | US institutions that conferred an award under one of the six CIP codes below in any year from 1991 to 2023 |
| `data/ipeds_programs.csv` | 825 | One row per institution, CIP code and award level ever observed |
| `data/ipeds_completions.csv` | 10,486 | Completions per program per year |

The three tables are generated from `data/ipeds/raw_ipeds_national.json` and are never edited by hand. Validator V-63
refuses any table that differs from a fresh derivation. To join a program to an Atlas institution, match `unitid` to
`ecosystem.ipeds_unitid`.

| CIP | Title | Programs | Active in 2023 | Awards 1991–2023 |
|-|-|-|-|-|
| 14.3201 | Polymer/Plastics Engineering | 59 | 26 | 7,529 |
| 40.0507 | Polymer Chemistry | 39 | 11 | 2,406 |
| 15.0607 | Plastics and Polymer Engineering Technology/Technician | 193 | 31 | 10,807 |
| 14.1801 | Materials Engineering | 413 | 236 | 71,599 |
| 40.1001 | Materials Science | 112 | 79 | 7,791 |
| 40.1002 | Materials Chemistry | 9 | 6 | 309 |

## What the polymer series shows, and how to quote it

Completions under the three polymer codes (14.3201, 40.0507 and 15.0607), labelled by the fall of the academic year:

```
1991: 476   2007: 379 (trough)   2016: 970 (peak)   2019: 807   2020: 763   2021: 673   2022: 690   2023: 617
```

2023 is 36% below the 2016 peak. The series fell through the 2000s, recovered strongly to 2016, and has declined in five
of the last seven years.

**Institutions that sustained a polymer program:** 35. That is institutions with one program of at least 50
completions whose first and last completion years are at least 10 apart. 27 of the 35 had completions in 2023.
`scripts/ipeds_build.py` prints this figure on every build. Quote it together with its rule.

**Do not quote "148 institutions ever, 41 still active".** The two halves have different denominators: one is a union
of 33 years, the other a one-year snapshot. The union is also full of tiny programs: 46 of the 148 institutions
conferred five polymer awards or fewer in total.

**The caveat that goes with any of these numbers:**

> These counts cover only programs that institutions chose to file under these CIP codes in IPEDS. Rubber and coatings
> have no CIP code and cannot be separated. Programs filed under chemistry, chemical engineering or general engineering
> codes are invisible; the University of Chicago's Pritzker School of Molecular Engineering and Dartmouth's Thayer
> School are confirmed cases. Non-degree training is out of scope for IPEDS, and 2024 is missing. Treat the figures as
> a floor, not a census.

Don't use this layer for an attrition claim about any one state. A state with zero programs here may just file under
other codes; that is not confirmed closure. It can't support a talent-pipeline argument either, because there is no
denominator here.

**"Ended" does not mean closed.** A 2026 check of nine Ohio programs against current catalogs found three still
running. Check a program's catalog before calling it closed.

## How the build handles the traps

1. **IPEDS counts completions, not programs.** A program that conferred nothing in a year is absent from that year, so
   programs are enumerated from the union of all years.
2. **`majornum` does not exist before 2000.** The fetcher applies that filter only from 2000 onward.
3. **There is no rubber CIP code.**
4. **40.0510 is forensic chemistry**, not materials chemistry, and is excluded.
5. **Certificate levels were re-coded in 2020.** Both codings map onto one level (`CERT_CANON`).
6. **The year labels.** The Urban Institute mirror filed 2021 and 2022 a year late, republished 2019's data as 2020,
   and never served 2022-23. The build re-files those years, takes 2022-23 from NCES, and refuses to build on a hole or
   a label clash.

## Refreshing

```
python3 scripts/ipeds_fetch.py        # IPEDS completions via the Urban Institute API (free, no key); rewrites the raw file
python3 scripts/ipeds_fetch_nces.py   # adds the years the mirror never served, from NCES complete data files
python3 scripts/ipeds_build.py        # regenerates the three tables and prints the summary above
python3 -m unittest discover -s scripts -p 'test_ipeds*.py'   # every wrong year map must be refused
```

## Corrections

Append-only: an entry is never edited, and a later entry corrects an earlier one. These were found before the layer
moved into the Atlas. They are listed because the internal copy circulated the wrong figures.

- **2026-08-21: a 2018-19 "closure spike" was a coding artifact.** The 2020 certificate re-coding split continuous
  programs in two, which made 19 programs appear to close in 2018-19. None had stopped teaching. The tell: every
  program in the spike was a certificate.
- **2026-08-21: the trough is 2007 (379), not 2006 (380).**
- **2026-08-21: the series peaked in 2016 (970), not in 2019 (807).** The earlier reading sampled every fourth year.
- **2026-10-14: the year labels for 2021-2022 were off by one, and 2022-23 was missing.** The endpoints stand; the
  middle years changed to 2020: 763, 2021: 673 and 2022: 690.
- **2026-10-14: "31 institutions sustained a polymer program, 22 active" is retracted.** It could not be reproduced. The
  stated rule gives 35 and 27.
- **2026-11-18: "77 institutions carry a polymer program of five awards or fewer" was stale.** The figure predates the
  certificate fix, which had split programs into small pieces. Recomputed from these tables: 74 institutions have at
  least one such program, and 46 of the 148 conferred five polymer awards or fewer in total.
- **2026-08-21: three Ohio programs recorded as ended are still running.** Northwest State's plastics AAS runs in full.
  At Shawnee State the certificate and minor are active and the AAS lapsed. Terra State narrowed to one certificate.
