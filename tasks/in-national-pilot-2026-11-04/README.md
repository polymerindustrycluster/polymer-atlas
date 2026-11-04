# National-spine pilot: Indiana (2026-11-04)

The repo owner requested this pass in session on 2026-11-04. It tests whether the federal lead-fusion spine
(`tasks/lead-fusion-2026-11-01/`) turns into verified Atlas records in a state with a large QCEW gap. Indiana had 512
QCEW 2023 NAICS 326 private establishments and 82 Atlas strict sites. The pass follows the UT skimpy-state pilot's
conventions (#41).

**Input:** the 53 Indiana clusters classed STRONG, meaning three or more independent federal families among OSHA ITA,
OSHA inspections, EPA ECHO/FRS and Form 5500. They were re-deduped against today's Atlas with `scripts/atlas.py`
dedupe; 15 had a name or street hit for the lanes to settle. Three packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments)

| Verdict | Count |
|-|-:|
| VERIFIED, a new site under a held organization | 15 |
| VERIFIED, a new organization plus its site | 23 |
| DUPLICATE_OF a held site | 1 |
| REJECT: scope, i.e. no polymer production (aerosol filler, magnesia, chemical distribution, metal salts) | 4 |
| STILL_UNCERTAIN, each with its settling fact | 10 |

**Yield:** 38 of 53 (72%) verified. That is much higher than the census people leads (about 25%). STRONG federal
overlap is a good predictor.

## Applied (`build.py`)
- **`organizations_*.csv`:** +21 organizations (ORG-005101 onward), all tier C.
  - Shards: IN 13, US residual 6 (no HQ stated), NE 1, INTL 1 (a Québec HQ).
  - Two verdict rows share one new organization.
- **`sites_IN.csv`:** +37 sites (SITE-006401 onward). 4 are tier B, with a federal source plus an own-site witness;
  33 are tier C. Indiana goes from 171 to 208 site rows.
- **Evidence:** +413 rows (EVD-077010 to 026913). The federal rows are OSHA ITA and inspection extracts, cited as
  `government_filing`. ECHO/FRS ids sit in `notes` only, because a registry row needs a fresh dated fetch (§4.13 grep
  rule).
- **Raw check:** the integrator re-fetched every own-site quote (`rawcheck.csv`), and 29 of 38 were found verbatim.
  Where the quote was not found, the site falls back to federal-only tier C, and processes and materials are left
  blank, so nothing is inferred.
- **Ids:** all allocated above every id used by open PRs at build time.

## Held
- `holds.csv`: 1, a cluster whose ITA and OSHA rows did not resolve in the packets.
- **Lane flags for the integrator** (`lanes/*/NOTES.md`):
  - ACS Technical Products (bio-based plasticizers), American Window & Glass and Marian are owner scope or ring
    questions.
  - Exo-s has a Québec HQ.
  - MonoSol's held HQ (Lebanon) differs from its current site (Portage).
  - Tenneco Angola's parent choice.
  - Futurex's federal address is a finance office.
  - The Triangle Rubber domain trap: trianglerubberco.com is the Goshen company.

## Next
The same pass can run on Indiana's 145 CORROBORATED clusters, then on Michigan (106 STRONG). Michigan has the largest
gap after CA, TX and FL.
