# Illinois CORROBORATED wave — L11

Scope fixed before application by lane assignment: at most 150 IL CORROBORATED clusters, core polymer NAICS first then score. Input contains the first 150 of 195 Illinois CORROBORATED clusters ordered any explicit 326 token first, descending score, cluster ID. All 150 screened clusters have exactly one legal verdict: 18 VERIFIED creates and 132 STILL_UNCERTAIN holds. Unselected 45 clusters remain unworked. First user: John Swanson / PIC research analyst; assess use by 2026-11-20. Controller owns task status.

## Acceptance and application

Lane acceptance: validator zero errors; unique verdict per selected cluster; before/after strict NAICS326 site count ratio; 18-row full-create blind re-check; two independent family refutes. Delegated integrator per controller BOARD ruling §2.7. Branch history is backup. Only sites_IL and evidence_sites_IL receive appends. IDs SITE-019000–019019; EVD-270000–270139, inside L11 block. No organizations created or modified; 18 site rows tier C, 126 evidence rows supports_C. No inclusion-log decisions or closures.

Banked ITA CY2025 rows are admissible without re-download by controller BOARD ruling, superseding fresh-fetch requirement for this source only. Source: https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv linked by https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data . observed_date remains packet vintage 2026-11-01; reviewed 2026-11-06. Record-level establishment_ID fragments, submission dates and CY retained. All creates have explicit Primary polymer-manufacturing codes and employer names resolved to held operators. Federal-only scope is provisional C per CAMPAIGN convention; no own-site witness, capability, HQ, county or current operating-status inference. operating_status=unknown. No FRS REST calls, registry links or derived qualifier edits.

Dedupe reuses scripts/atlas.py across all shards: normalized names, all cluster name variants/trade names, street+locality; create audit adds held domain and ITA company_name. Distinct explicit addresses under a held operator are separate establishments; ambiguous campus or parent cases are held. The 132 holds are listed individually in verdicts.csv with recommended settling evidence. They are screened leads, not 130 exhausted six-fetch investigations. No owner scope/ring/vocabulary question is self-ruled.

## Runnable checks

`python3 tasks/corroborated-il-2026-11-06/build.py --apply` replays idempotently, preflights conflicting IDs and uses shard_io.append_sorted.

`python3 tasks/corroborated-il-2026-11-06/check.py` PASS: 150 unique verdicts; intentionally duplicated verdict rejected; 3 known-answer held parent checks (Plastipak, ADS, Lacks); 18 allocated sites; 18 blind source rows; existing canonical records unchanged; replay byte-identical. No new fetcher or quote matcher is introduced.

`python3 scripts/validate.py` PASS, zero errors. No shared scripts edited; scripts pytest not applicable.

Strict site filter: physical IL, NAICS primary starts 326, operating_status active/unknown, tier A/B/C. Before 68 site rows / 797 QCEW2023 private establishments = 8.5320%; after 85/797 = 10.6650%. Count ratio, not matched coverage. Historical brief numerator 42 is superseded by measured baseline. check_results.json records result.

## Holds and independent review

| Held cases | Settling evidence / recommendation |
|---|---|
| 132 individual STILL_UNCERTAIN rows in verdicts.csv | Unambiguous operator and distinct manufacturing establishment at recorded address; prefer site-specific operator page, reconcile aliases and existing sites first. |

blind-input.csv is a shuffled source-only 18-row full-create re-check census, excluding lane verdicts and proposed tier. Refute brief asks each reviewer to decide PASS/HOLD separately for each source row before assessing the builder.

Council calls refused by machine-wide deep-call guard: no verdict. Controller 05:55 BOARD clerk route supersedes council-only gate and queue prohibition for clerk requests. Codex and Grok clerk reviews pending; this draft is not approved complete.

BWAY resolution: held ORG-006250 is tombstoned merged with successor_org_id ORG-000717 (Mauser), so LF-IL-01154 follows that terminal held chain. The builder rejects tombstoned operators. No new ownership adjudication or organization edit. 19 new NAICS326 sites and one 325510 coatings site.

Codex/OpenAI clerk1 final APPROVE/0 findings on2c5cfe0: full20/20 blind census PASS after independent Liquibox alias resolution from banked OSHAE-cd3fa515e0 (2026-01-15,1201WindhamParkway) and exact LIQUI BOX CORP alias toORG000934. Verified20ITA transcriptions, BWAY successor/Trelleborg alias, global street/source-ID checks, unchanged original197sites/721evidence,validate0/replay and68→87/797 ratio. Report: controller reviews/143-clerk-codex-1.md. This supersedes clerk's provisional Liquibox REFUTE. Grok final approval still pending; no Done claim or current-operation assertion.

Grok/xAI final REFUTE of2c5cfe0 supersedes technical completion despite prior Codex APPROVE: Liquibox/Sealedair has competing held-EIN/operator signals; American Flange vsGreif legal-operator alias unproven. Both now held; retire SITE019005/EVD270035–041 andSITE019013/EVD270091–097 permanently. All surviving IDs unchanged usingid_slots.csv. Final18Csites126EVD132holds;strict68→85/797. Full18-create census followscontroller small-state approval. Prior20/140 snapshots superseded; bothfamily re-reviews pending.

Final technical approvals: Codex/OpenAI clerk1 APPROVE25b9314,0findings (18retainedsourcecensus,stableunchangedfields,retired2slots,old197sites/721EVDpreserved,validate0,rowloss,replay,68→85/797); Grok/xAI clerk1 APPROVE same25b9314,0findings (bothoperatorholdsverified). Both approve final18Csites126EVD132holds,notoriginal20snapshot. Controller alreadymerged25b9314 when this documentation paragraph was recorded; data/builder unchanged. Reports incontroller reviews/143-clerk-{codex,grok}-1.md;taskstatus/merge remainscontroller-owned.
