# PIC-18 streets from dated physical government filings

Acceptance criteria for the controller's 2026-11-22 instruction. Screen the 121 original no-street sites. Apply a physical street only when every qualifying dated witness under a held operator name agrees by the current matching functions and no other Atlas site holds the street key. Require binding PASS and raw replay for every address and OSHA band row. Use the original R13 OSHA order and window. Report the before and after PIC-18 organization outcome and reconcile the prior 25-site trial.

## Outcome

The street route qualifies **8 of the 121 missing-street PIC-18 site rows**. Five of those sites also qualify for an OSHA size band. The five bands affect five distinct organization IDs, of which four were size-unknown under the PIC-18 outcome definition. The before and after size count is **396 to 392 of 794 organization rows**. The outcome counts distinct organizations with an active tier A–C PIC-18 site. A known site band at any such site, or a known organization Ohio band, settles size for that outcome.

| Site decision | Sites out of 121 |
|---|---:|
| Street qualified | 8 |
| Newer filing at a held name in another city | 3 |
| No in-window witness with held name and locality | 92 |
| Dated physical witnesses disagree | 9 |
| Unanimous street without a quote the binding gate can pass | 7 |
| EPA registry address evidence below the existing site tier | 2 |
| Otherwise eligible street key already held by another site | 0 |

Six of the eight qualifying streets have one witness family (OSHA). The other two have two families (one OSHA and SAM, one EPA and OSHA). The seven unbindable site addresses consist of six SAM-only sites, for which the gate has no source parser, and one OSHA-only site. `frame.csv` lists the source families and locators per site. Street fills affect one tier-A, four tier-B and three tier-C sites. The five band fills affect one tier-A, three tier-B and one tier-C site. The three addressed sites without a band held for later operator mismatch (two sites) or conflicting latest inspection counts (one).

The packet adds eight address evidence rows and five size evidence rows. Seven OSHA ITA address rows and one OSHA inspection address row carry `supports_A`. The five OSHA ITA `size_band` rows carry `supports_B`. The two EPA-only sites have a tier-A or tier-B record and registry address evidence capped at `supports_C`. Validator V-25 requires support at the existing tier, so those sites stay held. No inclusion-log rows or verification tiers change.

## Earlier trial comparison

The earlier [25-site trial source](https://github.com/polymerindustrycluster/polymer-atlas/tree/db44edb68781fb433d9f22624595c7e4f33bd6aa/tasks/pic18-street-from-filings-2026-11-22) proposed **one of 25 sites** using a two-family rule and OSHA plus EPA extracts. On those same 25 sites, this pass qualifies **three**. It preserves SITE-000519's agreed OSHA/EPA address, admits SITE-000524 with one dated OSHA family under the new instruction, and admits SITE-000008 with the broader in-hand source set, which supplies a dated SAM address agreeing with OSHA. The comparison preserves the date requirement and holds the trial's conflicting street. The full frame adds five qualifying street fills among the other 96 sites. `trial_comparison.csv` records the paired results.

## Witness rules and application record

The exact street and locality tests come from `scripts/matching.py`. The binding gate supplies the held names, excludes parent-only matches and checks the emitted quote. Every dated qualifying physical witness participates in the street agreement decision. The earliest date is 2021-11-22. After a local witness qualifies, a newer dated physical witness at a held name and a different street puts the site on hold, including when the witness is outside the recorded locality. Later filings within each OSHA series take precedence under R13, with ITA ranked ahead of inspection and Form 5500 counts kept as leads. Street keys are checked against all Atlas site rows, including inactive sites, and against the other proposed streets in the batch.

ITA uses calendar year-end. Inspections use the open date. ECHO dates come from the linked compliance event under the earlier trial's convention, with a separately replayed event locator and the same facility ID. A bare undated FRS row cannot carry a street. Ohio air permits use only explicit facility locations and the issuance date. SAM uses the permitted public extract's last update date. Form 5500 contributes only a location-role address, dated by receipt. Mailing blocks and undated or stale rows cannot supply street evidence. SAM and Form 5500 rows participate in agreement, while a selected address evidence row must use a family the binding gate can pass.

The pre-pass Git blobs at `a8119ad1` are `4a1d0456efaed165be1c21beaa6e687895c44725` for Ohio sites and `5a10d88016ce21e47746e40ce0bf3f19f8ce9885` for Ohio site evidence. `scripts/atlas.py next-id EVD` returned `EVD-483002` above the tree-wide maximum `EVD-483001`. The range is `EVD-483002` through `EVD-483019`. Review withdrew `EVD-483004`, `EVD-483005`, `EVD-483007`, `EVD-483008`, and `EVD-483013`. Those IDs remain gaps. The 13 retained evidence rows keep their original IDs and content.

The new check held three of the 11 original fills. For SITE-000014 the 2024 and 2025 OSHA ITA filings place Diamond America at a different Mogadore street from the 2023 Akron filing. The relocation and locality repair remain open. SITE-000155 has a later conflicting SAM physical-address record. SITE-001676 has a later conflicting dated EPA facility record. The frame and witness files carry the exact locators. The other eight street fills and five band fills reproduced as before.

## Named checks

```sh
python3.12 -B tasks/pic18-street-fill-2026-11-22/check.py --base 454dc9f5
python3.12 -B scripts/check_evidence_binding.py --new-since origin/main
python3.12 -B scripts/check_evidence_binding.py --provenance-since origin/main
python3.12 -B scripts/validate.py
python3.12 -B scripts/check_row_loss.py --base origin/main
```

The replay regenerates the frame, reads the located records and any linked date events from the raw store, verifies the input hashes and evidence text, and checks the exact canonical delta. It plants a wrong street, competing units, stale date, occupied key, parent-only name, and a newer filing under a held name at another city’s street. The 9 hashed raw inputs and 122 dated raw witnesses cover both fills and current holds in the 121-site frame. Live sources were outside this pass.

The pre-application replay passed for 122 dated witnesses, 9 raw-file digests and 13 evidence rows. The post-application byte comparison, binding gate (13 PASS), provenance, canonical validator and row-loss guard passed. The matching and binding unit suites passed 105 tests.

The cross-city control returned `eligible` before the guard was added. It now returns `newer_filing_other_city`.
