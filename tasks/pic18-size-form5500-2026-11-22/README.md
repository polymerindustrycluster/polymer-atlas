# PIC-18 size bands from Form 5500: follow-up packet for the 28 fills withdrawn from PR #468 (2026-11-22)

**Packet only. No PR, no change under `data/`.** Branch `agent/claude-code/pic18-size-form5500-2026-11-22` is cut from the head of PR #468 (cc65f3a4) so it can reuse that PR's builder and checker; against that head it adds only this folder (`git diff cc65f3a4 --stat -- data` is empty). It waits for the owner's ruling on whole-company plans (below), and for PR #468 to merge.

## Why these 28 were withdrawn
Review round 2 of #468 (Codex and Gemini) found, on the 28 Form 5500 fills only: five sponsors with a second plan number under the same EIN; three selected returns with a later return of the same plan at another mailing address; and the public packet printed the sponsor mailing street, which the owner's round-12 ruling bars publishing. The 50 OSHA fills carry no finding and stay in #468. The 28 sites, their bands and their first-head evidence ids are in `inputs_28.csv` (those ids are gaps in #468 and must not be reused: applying these fills needs a new reserved id range).

## The two tests (Codex round 2), applied to every filing under the sponsor EIN before any address filter
`sponsor_plan_inventory.csv` lists all **87 filings under the 28 EINs** in the six national Form 5500 and 5500-SF files (plan years 2023-2025, every state, every address). Fields used: plan number (`SPONS_DFE_PN` / `SF_PLAN_NUM`), plan year begin and end (`FORM_PLAN_YEAR_BEGIN_DATE`, `FORM_TAX_PRD` / `SF_...`), active participants (`TOT_ACTIVE_PARTCP_CNT` / `SF_TOT_ACT_PARTCP_EOY_CNT`, published as a band only), pension and welfare benefit codes.
1. **One plan number with positive participants in the window.** The sponsor EIN may report only one plan number with at least one active participant in the window (source date on or after 2021-11-22). Zero-participant filings are not counted; a stricter reading that counts any other plan number is reported beside it.
2. **The selected return is the latest return of that plan** (same EIN and plan number). A later return is tested for equality with the recorded street on both the mailing and the location line; if it binds, it, not the older filing, would be the one to use; if it does not bind, the older filing is held, never an automatic fall-back (`newer_return_of_same_plan`).
Also the partial-plan tests of #468's builder on the selected filing: plan name (union, bargaining, collective, steelworker, teamster, hourly, salaried, retiree, numbered local), **the collective-bargaining field of both forms (`COLLECTIVE_BARGAIN_IND` on the 5500 and `COLLECTIVELY_BARGAINED` on the 5500-SF; an earlier README wrongly said the 5500-SF has none)**, and the pension/welfare codes (welfare-only = partial). Street equality, name class (exact), source date, the single-active-site condition and the band are replayed by `check.py` as in #468.

## Result (unit: site records, one per organization)
| of the 28 | sites |
|---|---:|
| **survive both tests (positive-participants reading)** | **22** |
| survive if any other plan number also counts (Codex's reading) | **21** |
| fail test 1: two plan numbers with positive participants | 3 (SITE-000145, 000293, 001897; plan 501 each) |
| fail test 2: a later return of the same plan exists, none binds to the recorded street | 3 (SITE-000285, 001972, 002113) |
| fail the partial-plan tests (name, either collective-bargaining field, welfare-only) | 0 |
| bind a later return to the recorded street | 0 |
Under the stricter reading SITE-001834 also drops: a second plan number (501, welfare) with zero participants in the available years (SITE-001972, also in test 2, has a zero-participant plan 502). The 22 survivors are in `packet.csv` (band 10-49 x15, 1-9 x5, 100-249 x1, 50-99 x1; no street, no headcount, no sponsor name); the 6 holds are in `holds.csv`. The 22 organizations are not among #468's 47, so applying them after #468 would take PIC-18 size-unknown from 396 to **374** (unit: 794 PIC-18 organization rows).

## Owner question this packet waits on
**May a single whole-company plan's active participants set a site band?** Participation is not employment: an eligibility rule, a union carve-out or an employee who declines can make a plan count smaller (or, with a multi-employer plan, larger) than the workforce. What this packet establishes: one plan number with participants, the latest return, a pension feature code on every survivor, no bargaining indication, and exactly one active site for the organization in the Atlas. None of that proves that every employee is eligible or participates. Codex counted 21 of 28 meeting both tests; the difference to 22 is the zero-participant welfare plan of SITE-001834.

## Files
`inputs_28.csv` (the 28 withdrawn fills: site, band, raw file path, sha256, row locator, dates; no street), `sponsor_plan_inventory.csv`, `packet.csv` (22), `holds.csv` (6), `counts.json`, `INPUTS.sha256` (the six national files, store-relative paths and manifest digests), `extract_ein.py` (stage 1: stream the national files for a list of EINs; never writes into the store; the EIN list and the mailing/location lines it reads stay in controller storage, not in the repo), `build.py`, `check.py`.
Rebuild: `python3 -I extract_ein.py <store>/raw eins.csv f5500_ein28.csv`, then `python3 -I build.py --cache <dir> --eins eins.csv --data-dir <base>/data --out .`.

## Personal data and addresses
No Form 5500 mailing or location street, sponsor name, plan name, EIN, headcount, email or phone is written to any file here (scan of this folder: 0 emails, 0 phone numbers, 0 street lines). Plan names were read to test for partial plans and are not published.

## What was not checked
Whether any survivor's plan covers every employee (above); plan types beyond the pension and welfare feature codes; filing years outside the six national files; no employer contact. `check.py` shares the street, name and band functions with #468's builder, so it proves reproducibility from the raw files, not that those functions are correct.

## Named check
`python3 -I tasks/pic18-size-form5500-2026-11-22/check.py --raw <store>/raw --selftest --base-data <base>/data` (2026-11-22, file hashing on) -> `replayed 28 selected rows; national scan found 87 filings under 28 EINs; survivors 22 of 28: 0 failures`; `selftest wrong band caught: True | a second positive plan number holds the sponsor: True | a newer return of the same plan holds the older filing: True`. It replays each selected row from the raw file by path and sha256 (street equality, name, band, date, single active site), reads the sponsor EIN from that raw row, scans all six national files for the EIN with no address filter (the scan must equal `sponsor_plan_inventory.csv`), and re-derives every verdict.
