# L8 liveness sweep — 2026-11-06

Owner: atlas-L8-liveness. Branch: agent/codex/liveness-sweep-2. Claimed by controller; QUEUE untouched.
First user: Atlas campaign integrator, on delivery of this PR; non-use finding date: 2026-11-13.

Acceptance criteria: full eligible-domain sweep; ranked organization queue with exact EIN/TRIFID joins and explicit missing/failed coverage; compare November 1 sweep on both full and common-domain frames; no status mutation without dated primary/near-primary evidence and raw-checked quote; validate.py zero errors. Acquirer identity/grain questions stay held. No registry or derived-field edits.

Registry input pinned to restore branch commit d26438057e4e0199a2407d2a9508238494f31deb (PR #129). Snapshot is an input only, never applied to data/.

Methods and decisions (append-only journal):
- Sweep uses the existing script unchanged: active/unknown organizations plus ecosystem, excludes missing/invalid/shared-platform websites and groups shared normalized domains. It does not inspect acquired/closed rows.
- Rank score is triage only: NXDOMAIN 30, parked 25, cross-domain redirect 20; all matched EIN years older than 2024 adds 10; any latest-year all-final/short sponsor flag adds 10; all matched TRI years older than 2024 adds 5. Missing keys contribute zero, not a negative activity inference. Ties sort by org_id. Every active/unknown row remains in signals.csv, even score zero or NOT_SWEPT.
- EIN years are newest plan years in the held November 1 spine, not fresh DOL searches. No sponsor-address equivalence is assumed. All EIN links, including unmatched ones, remain in federal_link_signals.csv.
- TRI years fetched 2026-11-06 through EPA DMAP, grouped by exact held TRIFID, max(reporting_year) across historical reporting forms. Query selects no personal fields. 2,153 restored TRI link rows represent 2,150 distinct facility keys; repeated keys are not dropped at link grain. No TRI parent name is used.
- Source documentation: https://www.epa.gov/enviro/dmap-graphql-api ; https://www.epa.gov/toxics-release-inventory-tri-program/reporting-tri-facilities . TRI reporting depends on activity and thresholds; ceasing reporting does not establish closure.
- Known answers: independent legacy REST COUNT + complete forms reconciled 99, 8, 180 input forms for TRIFIDs 44224STRKT201ES, 4430WLTRRN12EWA, 44305RPBLC60SOU; all newest years = 2024. Only counts/year retained, no contact fields. EIN known keys 631127539=2024, 881282156=2025, 341352998=2023 checked in held spine. Exact-key matcher does not perform name inference.
- Estate search on Mac returned partial coverage (Documents inventory / wiki / RAG missing); this does not establish absence. TRI registry route was held and successfully queried; no missing estate source was needed.
- pytest is absent from base Python; scripts/ is unchanged. Existing sweep unittest suite passed 26 tests. No dependency added.
- Cross-thread lead from L9 (thr_t3bqpsncvw): ORG-000451 Molded Fiber Glass Companies newsroom https://moldedfiberglass.com/category/company-news/ reportedly HTTP 200, latest listed actual item 2023-10-26. This is L9's observation, not independently verified here, and not closure evidence (AGENTS §3). Keep as supplemental re-verification lead; do not change queue rank from a sibling-only observation.

## Results

- Input: 4,945 organization rows plus 400 ecosystem rows. Ranked frame: 5,288 active/unknown organization+ecosystem rows, exactly one per org_id; 154 have score > 0. No row is silently discarded for missing website/federal link.
- Full eligible-domain sweep: 4,327 unique normalized domains; 31 NXDOMAIN + 3 parked = 34 dead/parked **domain observations**, not closures. November 1: 3,629 domains; 24 NXDOMAIN + 3 parked = 27. Shared frame: 3,594 domains; prior 27 vs current 32 combined observations (24→29 NXDOMAIN, 3→3 parked). There are 733 newly eligible domains and 35 no longer eligible; route and website corrections can change observations. `comparison.csv` exposes every transition.
- All 2,150 distinct TRI keys returned 2024, so no TRI-staleness score was added. All 320 EIN links matched the held spine. Federal link output: 2,473 rows (2,153 TRI + 320 EIN).
- Applied data rows: **0**, evidence rows: **0**, status changes: **0**; verification tiers unchanged (A/B/C/U: 0 each). No EVD ids consumed. No inclusion-log entries or relationships required.

## Initial top-down review and holds

This pass investigates the first **10 ranked organization rows**. The remaining **144 positive-priority rows** are uninvestigated, explicitly held for the next dated-evidence pass. No claim of a completed queue-wide closure census is made. `verdicts.csv` names the settling facts; raw observations are in `rawcheck.csv`. Search snippets are discovery only. No dated closure witness was found for these ten; no organization is rejected for closure. Every domain failure stays a signal under AGENTS §3.

| Rank / organization | Verdict | Hold / recommended reading and settling fact |
|---|---|---|
| 1 ORG-002133 Vinyl Tool & Die | STILL_UNCERTAIN | EIN 341570514 newest PY2024, latest all-final/short flag. This is plan wind-down only. Need dated company/outcome record at Youngstown establishment; directory “closed now” is business hours, not closure. |
| 2 ORG-002712 Fay L Wagner | STILL_UNCERTAIN | EIN 251290948 newest PY2025, final/short flag. TIPS public dealer list is a counter-lead, not operating proof; need dated establishment outcome or current company statement. |
| 3 ORG-000422 Littlern | STILL_UNCERTAIN | Historical own-site description cannot establish current activity when domain fails. Need dated operating or cessation witness at Barberton. |
| 4 ORG-000443 Midlands Technologies | STILL_UNCERTAIN | Read own contact page at midlands-technologies.com; stored midlandstech.com was already flagged as wrong in record notes. Need identity/address confirmation before website correction; the 2026 court case being “Closed” does not mean company closure. No scope self-ruling. |
| 5 ORG-000654 Advanced Technology Products | STILL_UNCERTAIN | Own about page indexed at www.atp4pneumatics.com; domain-level DNS observation differs from indexed route. Need raw accessible current operating witness; no closure inference. |
| 6 ORG-000960 Midwest Plastics | STILL_UNCERTAIN | Lima domain fails; similarly named midwestplastics.com is not established to be same entity. Need dated Lima establishment witness. |
| 7 ORG-001427 KN Rubber | STILL_UNCERTAIN | Indexed about/fact sheet describe Koneta/National Rubber combination but no dated transaction/outcome is established. Need current operator and dated ownership chain; HOLD grain question, do not infer successor. |
| 8 ORG-001685 Kittyhawk Molding | STILL_UNCERTAIN | Chemstar's own about page names Kittyhawk as parent manufacturer, a counter-lead to dead domain. Need independently current operator/identity witness; no closure. |
| 9 ORG-001719 Pyramid Plastics | STILL_UNCERTAIN | Atlas row is Cleveland; pyramidplastics.com describes Rockford IL. HOLD identity; never apply Rockford acquisition/parent facts to Cleveland from name alone. Need Cleveland primary witness. |
| 10 ORG-001729 ICU Medical | STILL_UNCERTAIN | ICU announcement dated 2022-01-06 covers acquisition of Smiths Medical; held record already named ICU Medical, but old Smiths domain. HOLD record grain/identity before any acquisition tombstone. Acquirer buying a business does not mean acquirer was acquired. |

## Reproduce and checks

```sh
python3 scripts/liveness_sweep.py --out tasks/liveness-2026-11-06/sweep  # new network observation
python3 tasks/liveness-2026-11-06/federal_signals.py  # cached TRI batches; remove/review cache only for a new dated run
python3 tasks/liveness-2026-11-06/build.py
python3 tasks/liveness-2026-11-06/compare.py
python3 tasks/liveness-2026-11-06/check.py
python3 scripts/validate.py
python3 -m unittest scripts/test_liveness_sweep.py
```

`build.py` is idempotent and writes task packets only; on rebase rerun it against fresh main. Historical sweep/registry/federal inputs remain frozen for this dated comparison. Base data is branch history (bd57a08); there is no data application. No new abstraction or dependency, no status inference, no website repair outside lane scope.

Raw follow-up outcome: 2 of 10 business snippets passed direct curl word checks (Midlands contact; Chemstar about). The other 8 failed both direct and fallback availability or could not return a usable page. No snippet from those eight is used as evidence; search-indexed descriptions above are explicitly counter-leads/identity cautions. No acquisition or closure is applied. The top two Form 5500 sponsor addresses were checked in the held spine: 1144 Meadowbrook Avenue, Youngstown and 500 North Main Street, Yeagertown. They do not resolve cessation. Each case used at most two primary raw fetch attempts plus indexed discovery.

Offline checks run: `check.py` PASS (2,150 TRI keys, 3 independent TRI known answers, 3 EIN known answers, 5,288 unique ranked rows, score boundaries, zero data mutation); `validate.py` PASS 0 errors; existing sweep unittest PASS 26 tests. Scripts/ unchanged; full scripts pytest not required.

Additional deterministic checks: queue coverage equals the independent set of active/unknown input IDs; an injected duplicate was rejected by the uniqueness gate. Queue/federal/comparison rebuilds were SHA-256 byte-identical. `test_research.py`: 5 tests passed (known-good words, absent quote, curl failure with body, HTTP failure, empty quote). Data mutation remains forbidden by `check.py` for this signal-only packet.

Lead check refinement during review: zero-data-change assertion now compares the entire PR against `merge-base(HEAD, origin/main)`, including committed edits, rather than only the working tree against HEAD. It passes; this strengthens the signal-only packet gate without changing any output or data.
Whole-PR mutation-gate known defect test: in an isolated temporary git repository, committed an injected `active`→`closed` CSV change after the simulated origin/main base; the identical merge-base/diff command returned 1 and rejected it. The Atlas data tree was never edited.

## Cross-family refute

Grok, grok-4.7 xhigh (`--effort deep`): **APPROVE** for the explicitly bounded packet. Useful hardening adopted: check all 2,150 TRI keys are found/year 2024, all 320 EIN link hits and 2,473 link rows, recompute every queue score, pin registry snapshot SHA-256 (b830d047d4bedc576b7628cf0bbdebf685a6288cb2ed4d2ddbf1700d9e741953; separately byte-compared to d264380), and reject duplicate sponsor EIN input rows. The whole-PR data gate was already strengthened during the review. These checks pass. Grok inspected inline code/journal/rawcheck/verdicts, not the full CSVs or live sources; the deterministic checks supply population ground truth.

Other observations held as limits, not hidden: error/empty TRI query batches are explicitly marked and cached, but the frozen-run check now rejects them; a new dated fetch must refresh/review its caches. No empirical pre-aggregation truncation was demonstrated: documented query selects grouped maxima with 10,000 output limit for 100 keys, all 100 keys per batch reconciled, with three independent full-form max-year comparisons. The legacy REST row counts (99/8/180) are observation receipts, not an offline re-fetch. HTTP-200 interstitials without the requested quote return no match and may need manual alternate routes; no data change is supported by that checker. Business sponsor addresses and public reseller RecordID are public business data, not private identifiers or personal contact data.

Codex round 1, GPT-6 Astra max (`--effort deep`): **REFUTE** — reproduced committed status changes escaping HEAD-only comparison, all-zero scores passing, missing federal/comparison outputs passing, and a failed non-control TRI key passing. All addressed: merge-base + untracked-data check, full source/link-multiset/field reconciliation, explicit all-key year/coverage assertions, every comparison transition checked, researched top-ten alignment checked. Injected all-zero scores, dropped federal/comparison rows, and a TimeoutError TRI key now each fail `check.py`; original files restored after each test. No CSV output content was repaired silently by the checker.

Codex also identified a rerun risk after website edits: builder now records current_website and sweep_domain separately; a changed normalized hostname yields WEBSITE_CHANGED_SINCE_SWEEP (no old-domain liveness points, no stale redirect URL). The raw historical observation remains in sweep/. `test_build.py` passes two cases (same domain retains NXDOMAIN score; changed domain clears it). Queue population and priority counts are unchanged on this tree. This is a task-local signal label, never a schema value or data mutation. A rebase that changes the researched top ten fails the gate and requires renewed research.

Final round 2 verdicts: Grok **APPROVE**; Codex **REFUTE** on a masking variant of the data gate (committed/staged mutation hidden by restoring the working file). Corrected directly, with no third council redispatch under the council recurrence rule: `git_gate.py` separately checks base→HEAD, HEAD→index, index→working tree, plus untracked data. `test_git_gate.py` passes five isolated cases: clean, masked commit, masked stage, working mutation, untracked data. Also added checker assertions for duplicate sponsor/domain inputs and equal-score tie ordering. All checks pass on this packet, with zero data changes. **Draft PR; independent Codex approval of this final correction remains for the controller. No Done claim.**

Codex round 2 independently fetched the legacy REST counts 99/8/180 and all 287 ungrouped DMAP forms, with each maximum 2024. A grouped `limit:3` query still counted all 287 forms, supporting aggregation-before-limit for those controls. It reproduced the four round-1 input/output defects being rejected by the revised checker and found no demonstrated false-key, closure, privacy or ownership error. Full CSV population and repo validation remain grounded by local runnable checks rather than reviewer filesystem access.

Post-main integration (controller's 06:12 / 07:45 rulings): merged origin/main 9d69978 using the explicitly authorized LF federal-frame recipe; those two files have zero net PR diff. No data file was hand-merged or authored here. Main's ownership/website repairs make 24 original positive-priority rows WEBSITE_CHANGED_SINCE_SWEEP, clearing their old-domain points. Final rebuilt queue remains 5,288 rows, now **130 positive-priority rows**. The dated raw domain sweep (4,327 / 34 dead+parked) and common-domain comparison are unchanged. Earlier 154 priority count is the original pre-integration frame; controller explicitly assigned its remaining 144 rows to the separate continuation, which keeps that frozen original frame (including repaired rows for confirmation). Initial first ten researched IDs remain identical and all checks pass. The registry restore #129 is now merged; this first packet preserves its dated snapshot receipt, continuation reads registry links from main.
