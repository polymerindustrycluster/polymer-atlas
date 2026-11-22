# Street from government filings, 25-site trial, 2026-11-22 (lane atlas-w22-size-sprint)

Packet only (owner approval 2026-11-22, "Government files as a street source", as a 25-site trial). Nothing under `data/` changes. Frame: the 121 no-street sites of `tasks/pic18-size-sprint-2026-11-22/no_street_sites.csv`; first 25 of a shuffle of the sorted site ids, seed 20261122 (`frame.csv`). Not extended beyond 25.

## Rule as built (`build.py`)
A street is PROPOSED for a site only when all hold: (a) the organization has exactly one active site in that city and state in the whole Atlas; (b) in each source family, exactly one establishment (one `street_key`, civic number, no PO box) in that city and state carries a held name (exact, or the corporate-words rule of ruling B); (c) the filing is dated on or after 2021-11-22; (d) a SECOND independent source family gives the same `street_key` under a held name. One family alone is a lead. Two families that each name one establishment but different streets are reported as DISAGREEING.
Choices the controller's text left open (each is this lane's reading; the owner may differ):
- **Families:** `osha` = ITA 300A + OSHA inspection (one family: same agency, one pull); `epa` = RCRA, ICIS-AIR, NPDES (FRS is a mirror of the same programs, so also `epa`). Form 5500 is not used. The streets-lane branch (`origin/agent/claude-code/pic18-streets-2026-11-22`) is not pushed yet, so a third family was not available.
- **Dates:** ITA = 31 December of the filing year; inspection = open date; EPA = the facility's latest dated compliance event in the raw files (RCRA evaluation start, ICIS-AIR FCE/PCE end, NPDES inspection end), with its row locator in `date_locator`. **A bare EPA registry row with no dated event, and every FRS row (FRS has no date column), is undated and cannot support a proposal.** This is the reading that decides SITE-000297 (below).
- **Held names:** the site's own names (site name, legal name, trade names). A match on a named parent only is held (`parent_name_only`); the packet's held-name set is the size sprint's `name_class` with exact / corporate_suffix_only.
- **Extras:** a candidate ZIP that conflicts with a recorded site ZIP holds the site (none fired); an organization with a second active site in the same city holds it (none fired).
Sources read: `raw/osha/.../ita/*` (CY2016-2025), `OSHA_inspection.zip`, `raw/echo/.../{rcra,ICIS-AIR,npdes,frs}_downloads.zip`; `extract_epa.py` streams EPA to an Ohio-only cache (OSHA uses the size sprint's `extract_oh.py` cache). No earlier match file or Muse index is used.

## Numbers (unit: the 25 frame sites)
| outcome | sites |
|---|---|
| **proposal: two source families agree on one street** | **1** (SITE-000519) |
| **two families DISAGREE** (each one establishment, different streets) | **1** (SITE-003983) |
| one family only (OSHA ITA; lead) | 3 (SITE-000008, SITE-000524, SITE-000297) |
| no dated held-name source at all | 20: no row in the city 10; only filings before 2021-11-22 7; only an undated FRS row 2; only a named parent's name 1 |
Pre-set threshold: any proposal not stakeable, or disagreement in more than 2 of 25, drops the route. Disagreements: 1 of 25. Stakeable: see the reading below. Yield: 1 proposal of 25 (4%).

All 25:
| site | name | outcome |
|---|---|---|
| SITE-002067 | Aropha Inc. | no_candidate |
| SITE-000148 | WV International — Strongsville | no_candidate |
| SITE-001483 | Meese (MODRoto) — Ashtabula | parent_name_only |
| SITE-001795 | Pyramid Plastics, Inc. | stale_only |
| SITE-002035 | May Lin Silicone Products Inc. | no_candidate |
| SITE-000158 | Cleveland State University — Cleveland | stale_only |
| SITE-000008 | Myers Industries — Akron HQ | one_source_lead |
| SITE-000123 | Prime Conduit — Beachwood | no_candidate |
| SITE-000562 | Profile Rubber Corp., Inc. — Wadsworth | stale_only |
| SITE-002100 | AXILEA LLC | no_candidate |
| SITE-001575 | Beacon Biosignals — Cleveland | no_candidate |
| SITE-000524 | Philpott Rubber Extrusions — Mogadore | one_source_lead |
| SITE-001572 | ICHOR VASCULAR INC — Brecksville | no_candidate |
| SITE-001868 | Dal-Little Fabricating Inc | stale_only |
| SITE-001150 | R & S Technologies, Inc. — Bellevue | stale_only |
| SITE-000292 | ChemSpec — Canton | undated_only |
| SITE-001665 | Amros Industries Inc — Cleveland | stale_only |
| SITE-002063 | Poly Tech Plastics | no_candidate |
| SITE-000456 | Mac Divitt Rubber Co., LLC — North Perry | no_candidate |
| SITE-001818 | Global Waste and Recycling LLC | undated_only |
| SITE-003983 | G-3 Chickadee Akron R&D Facility | SOURCES_DISAGREE |
| SITE-000106 | T&M Plastics Co. — Cleveland | stale_only |
| SITE-000297 | Cobra Plastics, Inc. — Macedonia | one_source_lead |
| SITE-000056 | CF Extrusion Technologies — Cuyahoga Falls | no_candidate |
(`proposals.csv` holds SITE-000519; every other site is in `holds.csv`.) `candidates.csv` lists every held-name row in the site's city with file path, sha256, row locator, name, street, date, name_match and whether it counts.

## Reading of the proposal against the raw rows
**SITE-000519 Perry Fiberglass OH — Elyria (ORG-000485) -> 611 Lowell St, Elyria 44035.** Raw rows agreeing: ITA CY2025 "Perry Fiberglass OH" / "Perry Fiberglass Products, Inc." at "611 Lowell St" (2025_partial.csv row 286545); ITA CY2024 at "611 Lowell St." (row 279840); two OSHA inspections of 2023-01-27 at "611 LOWELL STREET" (OSHA_inspection chunk_5 rows 274161 and 299629); ICIS-AIR facility OH0000000247042017 "PERRY FIBERGLASS PRODUCTS, INC." at "611 LOWELL ST", FCE/PCE dated 2025-09-15. Undated and not counted but agreeing: FRS (two rows), RCRA "PERRY FIBERGLASS INC" 611 LOWELL ST (evaluation 2025-06-25; the name is a contained, not corporate-words, match so it is not counted). ITA CY2017-2019 also say 611 Lowell Street. The only contrary street is in the site's own notes, "Street (per Grok): 377 Woodland Avenue", a discovery-list value: the OSHA files put Stanadyne/Moen, then Leggett & Platt, at 377 Woodland Avenue, Elyria (1973-2014), and Perry Fiberglass inspections before 2016 at 33660 Pin Oak Parkway, Avon Lake. I would stake the record on 611 Lowell St. Flag for the integrator: the organization has a second site record, SITE-000520 "Perry Fiberglass Products" (status unknown, same city, no street), a likely duplicate; condition (a) counts active sites only.

## The disagreement (the batch-5 failure showing itself)
**SITE-003983 G-3 Chickadee Akron R&D Facility (ORG-003545):** OSHA ITA CY2025 (partial file row 299440) "Archwood" / "G-3 Chickadee Purchaser, LLC" says **1484** E. Archwood Ave.; EPA RCRA OHD982068488 (evaluation 2023-05-25) and ICIS-AIR OH0000001677010196 (2026-08-31), both "G-3 CHICKADEE PURCHASER LLC", say **1485** E Archwood Ave. The OSHA files carry the same plant under Goodyear ("Archwood Chemical" / "Archwood Plant 3", CY2016-2024) at 1485 E Archwood Avenue every year, so the CY2025 "1484" is most likely a one-digit slip in the newest filing, but the raw files do not settle it. A one-source OSHA match would have proposed the wrong number; the second family caught it. Held, settling fact: the facility's own page or a county parcel record.

## Leads (one family) and the undated reading
SITE-000008 Myers Industries (ITA 1293 South Main Street, 2022 and 2025), SITE-000524 Philpott Rubber Extrusions (ITA CY2025 330 Gilchrist Rd), SITE-000297 Cobra Plastics (ITA "Silgan Dispensing" CY2022-2025 at 1244 E. Highland Rd). Sensitivity, not in the packet: if an undated EPA registry row counted as current, SITE-000297 would become a second proposal (RCRA and FRS both say 1244 E HIGHLAND RD) and SITE-000008 would fall into `multiple_establishments` (EPA names both 1293 S Main St and 104 Gregory St for Myers); proposals 2, disagreements still 1. If a named parent's name counted, SITE-001483 Meese (ITA 4920 State Road, RCRA 4920 STATE RD) becomes a one-family lead, still no proposal. Re-run with `build.py --epa-undated-counts` / `--parents`. 14 of the 20 sites with no dated held-name source were spot-checked against the caches by a distinctive name token across Ohio (no missed plant found: the hits were other businesses or other cities); the other 6 have no distinctive token (WV International, May Lin, Dal-Little, R&S Technologies, T&M Plastics, CF Extrusion) and were not.

## Files
`frame.csv`, `candidates.csv`, `proposals.csv`, `holds.csv`, `extract_epa.py`, `build.py`, `check.py`. `check.py --dir . --raw <store>/raw --selftest` replays every `candidates.csv` row from the raw files by path, sha256 and locator (id, name, street, city equal to the raw row; EPA date from the dated event row), re-derives every site's disposition from the replayed rows and requires proposals + holds to partition the 25 sites; the selftest plants a different street on a candidate (replay must fail) and a disagreeing second source (the proposal must disappear).

## Not checked
No web page, no live street lookup. City spelling variants (e.g. a "North Perry" site filed under "Perry") are not tried: a city the files spell differently is a miss reported as no candidate. ITA `ein` and Form 5500 are not used. The EPA date proxy is this lane's reading.

## Named check
`python3 -I tasks/pic18-street-from-filings-2026-11-22/check.py --dir tasks/pic18-street-from-filings-2026-11-22 --raw /Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/raw --selftest` -> `replayed 70 candidate rows, re-derived 25 sites: 0 failures`; `selftest planted wrong street caught on replay: True | a disagreeing second source stops a proposal: True` (2026-11-22; sha256 of every cited file checked against `raw/MANIFEST.sha256` and the files on disk). `check.py` shares the name and street functions with `build.py` (replay, not an independent matcher).
