# PIC-18 size-sprint packet, 2026-11-22 (lane atlas-w22-size-sprint)

Packet only: nothing under `data/` changes. Owner pick 2026-11-22, "Size sprint from pulled files". SCHEMA §1 R13 sources 1-3, matched from the raw store by this lane itself (no earlier match file, no Muse index, no `registry_links.csv` EIN, no PPP). Counts name their unit.

## Owner rulings applied (2026-11-22, multiple choice; recorded in `DECISIONS.md` and SCHEMA §1 R13 v1.19.1 on this branch)
- **A. Headcount age: 5 years.** A filing sets a band only if its source date (ITA: 31 December of the filing year; inspection: open date; Form 5500: plan-year end, the tax-period end in the file) is on or after **2021-11-22**. Older filings are held as leads, reason `stale_over_5_years`.
- **B. Name match when the street already matches: corporate words only.** The held name may be a leading run of the filing name when every extra token is in the ruled list (Inc, Incorporated, LLC, L.L.C., Corp, Corporation, Co, Company, Ltd, Limited, LP, LLP, Holdings, Holding, Group, US, USA, U.S., North America, Americas). Containment is not accepted.
`packet.csv` = street equal under `street_key` + `same_street` AND name `exact` or `corporate_suffix_only` AND source date on or after 2021-11-22 AND no later filing at that street under an unheld name AND the ambiguity holds below do not fire.

## Frame (computed on origin/main 393c3895)
- PIC-18 organization rows 794; **size-unknown 443** (`pic18_unknown.py` definition).
- Frame = their active tier A-C PIC-18 sites: **465 sites**, **344 with a street_address, 121 without** (`no_street_sites.csv`; both columns say whether the organization has another site with a street, any status and active only: 15 of 121 do).

## Result (unit: site records filled / organizations with >=1 filled site)
- **98 site bands in 95 organizations**: OSHA ITA 55, Form 5500 40, OSHA inspection 3. Bands: 10-49 x45, 50-99 x18, 100-249 x16, 1-9 x13, 250-499 x4, 500-999 x1, 1000-4999 x1. Name match: 95 exact, 3 corporate_suffix_only (SITE-000157 GrafTech International Holdings, SITE-001719 RTS Companies US, SITE-001856 Anchor Industries Holdings). Minimum source date 2021-12-31.
- **367 sites held** (`holds.csv`, each with its settling fact): no_street 121; name_not_held 96; no_filing_at_street 69; stale_over_5_years 26; later_filing_other_name 16; ita_multiple_establishments_at_street 9; street_near_differs 7; filing_binds_two_sites 4; sources_disagree 4; near_cutoff_source_disagrees 4; f5500_no_active_participants 4; f5500_plans_disagree 3; near_street_filing_differs_from_fill 2; f5500_not_single_establishment 1; ita_years_disagree 1. `stale_over_5_years` = 26 sites whose only held-name filings at the street are older than the cutoff: leads. `near_cutoff_source_disagrees` = 4 sites held pending the owner (below).
- **Expected fall in size-unknown organizations (794 PIC-18 org rows):** against main (393c3895) 443 -> 348 (a fall of 95, 12.0 points). PR #461 (12 site bands, 11 organizations) is not on main and its 23 pilot sites are in this frame: 5 packet sites in 4 organizations carry the same band as #461's applied rows (none conflict). Net of #461 this packet adds 91 organizations; #461 alone 443 -> 432; both 443 -> 341 (union 102 organizations; 7 are #461-only because this packet holds them).
- Alternatives, for the record (organizations filled; `candidates_all.csv`, 2,778 street-equal candidate rows): with the 5-year limit, exact only 92, **+ corporate words 95 (ruled)**, + containment 115; with no age limit (reference only, without the window and near-street tests) 115 / 118 / 139.

## Assumption for the reviewers and the owner: stale filings are ignored as sources and as conflicts
Ruling A says a filing older than the cutoff "sets" no band. This packet reads that as: **a filing older than 2021-11-22 is ignored both as a band source and as a conflicting source** (it cannot fill, and it cannot make a fill a `sources_disagree` hold). The ruling does not say this; it is this lane's reading. One exception is held pending the owner: where a source dated in the year before the cutoff (2020-11-22 to 2021-11-21) disagrees with the fill by more than one band, the site is held (`near_cutoff_source_disagrees`). Four sites:
| site | org | fill held | window filing | window band | fill band |
|---|---|---|---|---|---|
| SITE-000450 Little Tikes — Hudson | ORG-000421 | ITA CY2025 | inspection 2021-11-03 | 1000-4999 | 250-499 |
| SITE-000454 LT Molding Solutions — Hudson (same street, second active site) | ORG-000424 | ITA CY2025 | inspection 2021-11-03 | 1000-4999 | 250-499 |
| SITE-000530 Plastic Platers — Brooklyn | ORG-000495 | ITA CY2025 | ITA CY2020 (2020-12-31) | 100-249 | 10-49 |
| SITE-001680 Kinetico Incorporated — Newbury | ORG-001607 | ITA CY2025 | ITA CY2020 (2020-12-31) | 50-99 | 250-499 |
Owner question: should a filing in that window count as a conflicting source, or should all pre-cutoff filings be ignored? If ignored, these 4 sites return to the packet (SITE-000450 and SITE-000454 would still be held by `filing_binds_two_sites`), a rise of at most 2 organizations. SITE-000450 is also #461's applied row (250-499): this packet and #461 therefore disagree on it.

## Reconciliation: 87 organizations (earlier filter table) -> 97 (first rebuild) -> 95 (final)
The earlier table (README of the first full run, "+ corporate suffix, <=5 y": 87 organizations, 90 sites) applied the age cutoff after selection: the matcher chose the best fill by precedence over all filings of any age, then dropped fills with filing year before 2021. `reconcile_87_to_97.py` re-runs `build.py`'s own `evaluate()` under those pre-ruling rules and reproduces **87 organizations / 90 sites** exactly; `reconcile_87_to_95.csv` is the site-by-site difference to the final packet:
- **Entered, 7: precedence falling through** from an old ITA or inspection fill (dropped after selection, so nothing filled) to a recent Form 5500: SITE-000068, 000079, 000275, 000310, 000488, 001834, 001856 (all `form5500`).
- **Entered, 2: a stale source no longer counted as a disagreement** (pre-ruling `sources_disagree` against an old inspection or ITA): SITE-000339, SITE-001599 (both `form5500`).
- **Left, 1: the window rule:** SITE-001680 (in the 87 as ITA CY2025 250-499; now held, `near_cutoff_source_disagrees`).
- 87 + 9 - 1 = **95** organizations, 98 sites (the 87 organizations had 90 sites). Nothing else: the changed corporate-word list (Holding, Limited, LLP, Americas added; `north`/`america` only as the phrase) moved no site.
- The first rebuild's 97 organizations (100 sites) were the 87 plus those 9 entered plus SITE-000530 (a third stale-conflict case: pre-ruling `sources_disagree` against an inspection of 2011); the window rule then held SITE-000530 and SITE-001680, which is the 97 -> 95 step.

## Rules the matcher applies (beyond the brief), each found against the raw rows
- ITA: most recent year in the window with a positive count; >1 ITA establishment of the same company (same company name, same EIN, or a shared first name token) at the street that year -> HELD; rows that disagree by a band, or years within two years that differ by >1 band -> HELD; ITA `size` code more than one band from the annual average -> HELD (none fired).
- Inspection: latest `open_date` in the window with positive `nr_in_estab`; same-date rows that disagree -> HELD. `nr_in_estab` can be company-wide (SITE-002114: 14,000 in 2024 against ITA 80); R13's >1-band disagreement test catches it.
- Form 5500: organization with exactly one active site in the Atlas; sponsor location or mailing street equal; most recent plan year (files cover 2023-2025); top plan of that year; plans across years more than one band apart -> HELD; a sponsor that matches only a named parent -> HELD (`f5500_sponsor_is_parent`, none fired). A plan-count hold does not block an ITA/inspection fill.
- Any ambiguity hold in a higher source blocks a lower source's fill. If a higher-precedence source has a near-identical street (suffix, directional or unit letter differs) under a held name and would give a different band, the site is HELD. A later filing (any source, later calendar year than the fill) at the same street under a name the packet does not accept holds the fill (`later_filing_other_name`). One filing cannot size two active site records (`filing_binds_two_sites`).
- Band only; no headcount in any cell. Row locators: `<zip member>|row=<1-based data-row ordinal>|id=<ITA id / OSHA activity_nr / ACK_ID>`.

## Read against raw rows
The canary (25 sites, seed 20261122) and all uncorroborated fills of the first full run were read against the raw rows; the 6 fills added by rulings A and B (SITE-000157, 000339, 000530, 001599, 001719, 001856) were read after. No wrong plant found. 4 ITA fills match only a named parent's name with an establishment label the record does not hold (SITE-000051 Continental AG, SITE-001421 Simon Roofing & Sheet Metal, SITE-001513 Tenneco, SITE-001792 Bridgestone Americas; `matched_name` starts `parent:`): a reviewer may want to see these four.

## Files
`frame.csv`, `packet.csv`, `holds.csv`, `candidates_all.csv`, `no_street_sites.csv`, `counts.json`, `INPUTS.sha256` (17 raw files, from `raw/MANIFEST.sha256`), `extract_oh.py` (stage 1: stream the store to an Ohio-only cache; never writes into the store), `build.py` (stage 2), `check.py`, `pilot23_comparison.csv`, `canary-25/` (re-run with the final matcher), `reconcile_87_to_97.py` and `reconcile_87_to_95.csv`.
Rebuild: `python3 -I extract_oh.py <store>/raw <cache> ita|insp|f5500`, then `python3 -I build.py --cache <cache> --out .`.

## Sibling pilot (PR #461, lane atlas-w22-size-ita): re-derivation of its 23 pairs (`pilot23_comparison.csv`), final matcher
Agreement 14 of 23 (its 12 applied: same band on 5; its 11 held: held here on 9). The 9 disagreements, against raw rows:
- SITE-000138 (it held on a Muse-index flag; here filled 100-249, ITA CY2025 with 2025 inspections agreeing): raw ITA size code 3 against average 238 is adjacent bands, not a conflict. SITE-002965 (it held on a dedupe lead with a closed record; here filled 10-49): the closed record is not an active second site.
- SITE-000450 Little Tikes (it applied 250-499): held here, pending the owner: the inspection of 2021-11-03 (2000 employees, 1000-4999) is 19 days before the cutoff and more than one band from the fill (`near_cutoff_source_disagrees`); a second active site, SITE-000454, sits at the same street. Without the window rule it would be a stale lead and the held reason would be `filing_binds_two_sites`.
- SITE-000522 and SITE-000863 (applied there on ITA CY2016 and an inspection of 2014 respectively): held here `stale_over_5_years` / `f5500_plans_disagree` after ruling A. SITE-000383 (trade-name tie, later other-name filing), SITE-000620, SITE-001109, SITE-001137 (street spelled differently): held here under the `street_key` rule.

## Owner rulings still open
Whether a near-identical street (suffix, directional, unit letter) may count as the same street (SITE-001109, 001137, 000620, 000522, Castek and others: `street_near_differs`, 7 sites, each with the would-be band in `holds.csv`).

## What was not checked
No live page, registry or street lookup (a failed street is a hold, not a miss). `check.py` replays each packet row from the raw file but shares the street, name and band functions with `build.py`, so it is a replay, not an independent matcher. It does not re-prove that no later qualifying row exists. ITA `ein` was used only for the multi-establishment test. 121 frame sites without a street cannot be filled until a street lane records one.

## Named check
`python3 -I tasks/pic18-size-sprint-2026-11-22/check.py --packet tasks/pic18-size-sprint-2026-11-22/packet.csv --raw /Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/raw --selftest` -> `replayed 98 packet rows: 0 failures`; `selftest wrong band caught: True | row from a different street caught: True | stale source date caught: True` (2026-11-22, file hashing on; the 17 inputs were verified against `raw/MANIFEST.sha256` earlier today and are unchanged). It re-tests street, name class (must be exact or corporate_suffix_only and equal the packet's), source date on or after 2021-11-22, count, band, year, frame membership and the single-site condition for Form 5500.
