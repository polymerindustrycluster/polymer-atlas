# Michigan CORROBORATED wave — L11

Scope fixed before application by lane assignment: at most 150 MI CORROBORATED clusters, core polymer NAICS first then score. Input contains the first 150 of 198 Michigan CORROBORATED clusters ordered any explicit 326 token first, descending score, cluster ID. All 150 screened clusters have exactly one legal verdict: 17 VERIFIED creates and 133 STILL_UNCERTAIN holds. Unselected 48 clusters remain unworked. First user: John Swanson / PIC research analyst; assess use by 2026-11-20. Controller owns task status.

## Acceptance and application

Lane acceptance: validator zero errors; unique verdict per selected cluster; before/after strict NAICS326 site count ratio; 17-row full-create blind re-check; two independent family refutes. Delegated integrator per controller BOARD ruling §2.7. Branch history is backup. Only sites_MI and evidence_sites_MI receive appends. IDs SITE-018000–018019; EVD-260000–260139, inside L11 block. No organizations created or modified; 17 site rows tier C, 119 evidence rows supports_C. No inclusion-log decisions or closures.

Banked ITA CY2025 rows are admissible without re-download by controller BOARD ruling, superseding fresh-fetch requirement for this source only. Source: https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv linked by https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data . observed_date remains packet vintage 2026-11-01; reviewed 2026-11-06. Record-level establishment_ID fragments, submission dates and CY retained. All creates have explicit Primary polymer-manufacturing codes and employer names resolved to held operators. Federal-only scope is provisional C per CAMPAIGN convention; no own-site witness, capability, HQ, county or current operating-status inference. operating_status=unknown. No FRS REST calls, registry links or derived qualifier edits.

Dedupe reuses scripts/atlas.py across all shards: normalized names, all cluster name variants/trade names, street+locality; create audit adds held domain and ITA company_name. Distinct explicit addresses under a held operator are separate establishments; ambiguous campus or parent cases are held. The 133 holds are listed individually in verdicts.csv with recommended settling evidence. They are screened leads, not 130 exhausted six-fetch investigations. No owner scope/ring/vocabulary question is self-ruled.

## Runnable checks

`python3 tasks/corroborated-mi-il-2026-11-06/build.py --apply` replays idempotently, preflights conflicting IDs and uses shard_io.append_sorted.

`python3 tasks/corroborated-mi-il-2026-11-06/check.py` PASS: 150 unique verdicts; intentionally duplicated verdict rejected; 3 known-answer held parent checks (Plastipak, ADS, Lacks); 17 allocated sites; 17 blind source rows; existing canonical records unchanged; replay byte-identical. No new fetcher or quote matcher is introduced.

`python3 scripts/validate.py` PASS, zero errors. No shared scripts edited; scripts pytest not applicable.

Strict site filter: physical MI, NAICS primary starts 326, operating_status active/unknown, tier A/B/C. Before 121 site rows / 819 QCEW2023 private establishments = 14.7741%; after 138/819 = 16.8498%. Count ratio, not matched coverage. Historical brief numerator 47 is superseded by measured baseline. check_results.json records result.

## Holds and independent review

| Held cases | Settling evidence / recommendation |
|---|---|
| 133 individual STILL_UNCERTAIN rows in verdicts.csv | Unambiguous operator and distinct manufacturing establishment at recorded address; prefer site-specific operator page, reconcile aliases and existing sites first. |

blind-input.csv is a shuffled source-only 17-row full-create re-check census, excluding lane verdicts and proposed tier. Refute brief asks each reviewer to decide PASS/HOLD separately for each source row before assessing the builder.

Council calls refused by machine-wide deep-call guard: no verdict. Controller 05:55 BOARD clerk route supersedes council-only gate and queue prohibition for clerk requests. Codex and Grok clerk reviews pending; this draft is not approved complete.

Codex/OpenAI PR138 REFUTE (clerk1,6f0109d): Signode Package Design vs Industrial Group and ABC/Undercar variants lack explicit legal-operator linkage. Both creates now held; original source census independently18PASS/2HOLD after JSP banked-EIN resolution. Retired SITE018004/018011 and their original14 EVD slots permanently; remaining IDs unchanged via id_slots.csv. Full18-create census follows controller approval for state creates<20. Check now pins9489b60 baseline instead of mutable HEAD. Revised counts supersede20/140 snapshots and original refute-brief snapshot. Re-review pending.

Grok/xAI REFUTE eeb1960 (clerk1): JSP abbreviated filed name and shared-EIN candidate are not cited proof of the legal operator link. Despite Codex clearing JSP from banked EIN/OSHA comparisons, the parent-claim citation remains insufficient. Conservative cure: hold LF-MI-01241; retire SITE018013/EVD260091–097, keep all surviving IDs unchanged. Final17Csites119EVD133holds; strict121→138/819. Full17-create census; earlier18/126 and20/140 snapshots superseded. Both families requested to re-review.
