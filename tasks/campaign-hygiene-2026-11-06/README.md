# Campaign hygiene — 2026-11-06

Controller-assigned docs/tasks-only pass on agent/codex/campaign-hygiene-2026-11-06. No canonical records/evidence rows added or changed at any tier; no data/, scripts/, AGENTS.md, SCHEMA.md or CAMPAIGN.md edits. The queue edits are explicitly authorized by the controller's final hygiene assignment, superseding the original lane prohibition on editing QUEUE. Only its2026-11-06 campaign section changes; older sections remain byte-identical.

The frozen GitHub snapshots merged-prs.json/open-prs.json were fetched with gh pr list --state merged --search 'merged:>=2026-11-06' and the open-PR list. They contain36 merged PR claims and50 open PR claims (unit: PRs at snapshot), plus2 unopened continuation claims. Every PR line retains its actual branch. User-requested in-pr:codex tokens include controller-authored branches; branch text preserves authorship. Combined original families are split into their bounded PRs, including CA/TX, FL/GA, MI/IL and program lead/completion continuations. BOARD continuation cohorts06:30/09:15/11:05 and later are represented, including the final88Ohio rows now inPR211 and TX qualityPR212. Two task continuations had no PR at the snapshot; this hygiene pass was the third, now represented as open PR213. Later merges/openings require a refreshed snapshot, not an invented status.

The restore wording now correctly says805528a merged throughPR68. PR129 restored3,348 registry-link rows; PR130 is the keyed row-loss guard and PR163 the separate tier1 derivation. A done token means its bounded PR merged, not that every follow-up research hold is settled.

## Postmerge receipts

receipts.json audits11 source commits:9 missing receipt patches carried,2 already-main skips. Requested source commits57c77f7(#131),d9dd945(#134),c2c4729(#138),661a9b6(#143 after25b9314),2f5639c(#150),80123b1(#174) are represented. Additional BOARD receipts862f67a(#147),87d2fb0(#171) and newly postmerged03359c3(#137) are carried.30fb413(#140) ande39f6af's GA README(#142) were already on main and are not duplicated.

Each source path list and installed SHA256 is recorded. The exact source patch is preserved in a separate commit for each carried receipt. The mixed #150 commit's check.py baseline change and mixed #171 commit's new-round data/code are excluded; only their README portions travel. #134 includes its approved-replay.json receipt. One whitespace-only line copied by #134 is normalized in the hygiene pass. No federal-frame normalization or other source-branch changes are carried. Historical producer checks remain observations at their pinned source revision; this PR does not assert every old builder can replay against today's main.

## Follow-up counts and limits

Six open lines represent the five requested families (Tier1 is split owner/scope and human outreach). counts.json records immutable public Git source revisions/hashes; its public aggregate counts are reproduced by check.py. No private worksheet/list was opened or copied.

- Tombstone: corrected PR201 has14candidate site rows,10VERIFIED/4STILL_UNCERTAIN. Four holds are distinct from two valid sourced keeps.
- Tier1: merged PR205's final remainder is155unique unhealthy organization rows/197overlapping gap memberships. Disjoint classes50owner-only/93human-only/11scope-only/1mixed. The93human-only rows have130gaps:73capability/37tier/20website. This is a disposition count, not a new target, impact or permission to contact anyone.
- Archive: two disjoint outcomes files contain3,227+2,975=6,202unique supported evidence rows without an admitted archive witness. The34links merged byPR137 are excluded; no new URL/capture/source validation is performed here.
- ResidualHQ: the three pending packets contain249unique organization candidates:28HQ_FOUND/221STILL_UNKNOWN (8/92,12/88,8/41). Latest #189 withdraws both HB&G and IDEX, superseding earlier10/90 and9/91 reports. Two ownership exclusions remain among the holds. No new HQ research or canonical relocation is performed here.
- Ohio streets: pinned baseline a90d8e3 has1,883active Ohio site rows/1,559blankstreet_address. Pending fills are excluded; this broader universe is not the original448-row A/B frame. Final88frame rows are already claimed inPR211. Main coverage will change when pending fills merge.

## Named checks and review

Run python3 tasks/campaign-hygiene-2026-11-06/build.py, then python3 tasks/campaign-hygiene-2026-11-06/check.py. Builder is idempotent and only renders the campaign section. Check matches every frozen PR state/branch/date, unchanged earlier queue prefix, all receipt source patches/path scopes/content hashes, disjoint/unique count sources and protected-path boundaries. Deliberately wrong PR state and non-receipt code paths must be refused. check.py and build.py are task-local audit tooling; production scripts/ is untouched.

Validator: python3 scripts/validate.py, zero errors (pre-existing warnings); log validate.txt. Byte-identical builder replay and git diff --check pass. No production-code tests were needed for receipt/queue documentation; two-family deep short-queue clerk refutes are pending. First user: campaign controller reviewing this PR immediately2026-11-06. No source availability, historical producer checks, hosted deployment or private outreach was rechecked.
