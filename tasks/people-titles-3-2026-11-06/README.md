# Remaining people titles — 2026-11-06

L12 continuation `agent/codex/people-titles-3`; controller owns merge/status. Only people.csv and evidence_people.csv are canonical outputs. The fixed pre-application scope is the union of two published title-hold lists, less people already covered by merged PR149. No new discovery frame or subsequent batch is included.

## Result and source filters

Unit: existing candidate people, with overlapping source-list filters. **184 unique people = 88 VERIFIED rechecks, 7 REJECT dispositions and 89 STILL_UNCERTAIN; no duplicates or creates.** The lanes proposed 91; after the 75cdeb5 refutes the integrator withdrew 3 (see "Refute fix pass"). All184 have an ordered disposition with a deciding/settling fact. The seven excluded people remain canonically untouched; this title pass neither deletes people nor changes tiers.

| Source/filter | Raw candidate people | Covered by PR149 | This pass | VERIFIED | REJECT | STILL_UNCERTAIN |
|---|---:|---:|---:|---:|---:|---:|
| atlas-cleanup holds, people title rows |214|30|184|88|7|89|
| role-title-recheck-2 holds, people rows |149|14|135|65|6|64|

Do not sum these source rows as unique people. `source_counts.csv` is recomputed against original source IDs; `verdicts.csv` accounts each of184 once. The original lists contain214 unique people;30 are covered by PR149, leaving184. Title shape alone did not determine a verdict: all184 were checked, including44 that already looked title-shaped under the earlier heuristic.

Applied: **88 existing people (83 tierA,5 tierB),75 printed-title changes,12 controlled-role changes,13 already-exact title/role observations;183 append-only own_site evidence rows**. Each person gets current role/title and polymer-scope witnesses; seven supplemental rank observations resolve/corroborate dated appointments. No affiliation, program, name, specialty, profile URL or tier changes. All pre-pass people/evidence and all unowned cells remain intact. Evidence IDs EVD283000–283188, less 6 retired IDs (withdrawn.csv) that are never reused; no person IDs allocated.

The source packets are lane1 56→27V29U; lane2 56→31V6R19U; lane3 56→28V1R27U; NLR16→5V11U. Their READMEs distinguish target-body review from availability-only inspection, PDF conversion from inspected pages, shared pages and person-level fetch budgets. Failed routes never prove absence. The controller clarified approximately6 distinct primary routes per person; shared directories count once for all covered people.

## Acceptance and evidence

Acceptance was fixed before application: re-read current institution-owned pages, settle the exact printed title and §4.9 role together, bind the correct person entry/surname within40words, require current person/lab polymer-material research, preserve every other claim, append evidence, and pass deterministic conservation/replay checks plus two-family refute. The builder uses scripts/shard_io.py append_sorted; expected.json and base_commit.txt are the pre-pass backup/journal.

Titles come from formal headings, fields, catalog entries or explicit title attributions; biography noun phrases are not copied as titles. Case/punctuation remain exact, whitespace alone normalizes. Literal pipes are retained when actually printed in a formal field. Kramer has an eligible primary Associate appointment plus a separately printed secondary Adjunct appointment; solely adjunct ranks remain excluded. University Research Assistant/Associate/Professor maps to research_professor under §4.9.

GateB uses current person-specific research statements or explicitly named own institutional lab programs, not menus, roster categories, fingerprints, publications, prior degrees or ordinary natural biology. Bharti explicitly investigates manufactured microplastics transport. Salas-de-laCruz explicitly engineers functional natural-polymer biomaterials. Njardarson's named ongoing sulfur-material collaboration supplies context beyond a generic example list. Peresin's `/experts/` witness is an institutional expert profile. Chipara's8-page faculty catalog was extracted8/8 and page2 visually inspected to bind his own column. No new specialty mapping is attempted.

All189 quote keys pass exact-token raw matching and the25word quote ceiling. Core GateA retains surname/own-published alias proximity. Cook's current LLNL profile explicitly bridges Krikorian(Cook); the held name remains unchanged. Jäkle/Jaekle are own-published spellings. Long's supplemental promotion sentence is bound to the same individually named current profile as the core surname-proximate title witness. Source dates stay full ISO or empty; Nangia's source gives only promotion year2023, so no day is invented.

Long's live NAS maxAge0 response200 prints Graduate Programs, modified2026-11-05T17:45:38Z; this supersedes the older indexed Graduate Education wording. Hallinan2025, Stache2026 and Lu2025 own dated promotions resolve prior rank disagreements. HuYang's joint Marquette/MedicalCollegeWisconsin own lab is linked from the primary departmental profile; affiliation remains Marquette. NLR grade-only titles keep prior enums under B-NLR-1(a); no tier upgrades or novel folds.

Kroonblawd's proposed Deputy Group Leader→group_leader fold is WITHDRAWN (Refute fix pass): the merged Maiti example is not an owner ruling.

## Holds and exclusions

| Case | Settling fact / recommendation |
|---|---|
| Knauer | Hub Coordinator vs dated own program Senior Researcher; held enum is senior_scientist. Owner interpretation of title precedence/gradeKEEP for a formerly uncertain NLR record; no new term or self-refold, retain prior tier. |
| Killgore | Current NIST Project Leader; Materials Research Engineer is explicitly2011–15. Owner mapping or current explicit eligible research-staff title; no invented ProjectLeader fold. |
| Conflicting current university ranks | Dated own appointment/promotion resolving both current observations; otherwise hold. |
| Bhat held-name typo | Own source prints Gajanan; held Ganjanan preserved. Name correction is outside this title pass. |
| Popov identity | Own institution bridge between held Cyrillic name and proposed Latin styling; no inferred match. |
| Other holds | Named current title/research/identity or available primary page in verdicts.csv; no missing-keyword rejection. |

Positive exclusions: Huelskamp practice; Pilla current Clemson Adjunct; Alamo emerita; GangSun emeritus; Schieber emeritus; Egap adjunct; Ryu own dated2021 death notice. Parent independently checked all seven. No canonical deletion/status/tier action is bundled.

## Privacy and source integrity

No CRM, licensed/private census, contact fields or directory biographies. Only public professional facts, short quotes and sanitized metadata publish. Full source bodies and PDF images remain temporary under/tmp. The sanitized durable184-person accounting is under people-titles-3-private; runtime_manifest.json pins its frame/disposition hashes. No claim is made that unavailable held candidates passed either gate.

A lane1 cleanup exceeded owned URLs and changed222 shared sanitized cache texts; original traversal size was not retained. Its125 original own hash attestations were overwritten before pre/post pairs were saved. This provenance limitation is explicit. Other owners preserved original attestations separately from current redacted-cache hashes. The regex also removed standalone10digit strings, so every retained professional quote and full title was rechecked. Five lane2 hash mismatches correctly failed the parent's first final check; they were reconciled without changing any proposal and now pass against shared and isolated frozen observations. Current hashes certify exact sanitized text, never original HTTP bytes. First/second-pass caches are separate and unaffected.

## Checks and review

- Superseded by the Refute fix pass checks below. Original: `python3 tasks/people-titles-3-2026-11-06/check.py` PASS:184 exact IDs/source filters,91 existing/0creates/189evidence,rawquotes,role/title pairs,own domains,pre-pass preservation,7matcher negatives,8production mutations and byte-identical replay.
- (Superseded: lane3 failed on the applied tree; see the Refute fix pass.) Four lane checks, with3/5/4 actual university calibrations and3NLR known answers; wrong quote/person/rank-affix fixtures fail. Production fake-quote tests include a forged matching certificate; actual source matching rejects it. A late foreign-shard evidence collision fails before writes.
- Private account.py PASS184 unique inputs/outputs/facts/proposal parity; missing/duplicate/wrong-identity/unknown-verdict mutations fail.
- `python3 scripts/validate.py` PASS0errors, including people-grain/email checks. `python3 scripts/check_row_loss.py --base origin/main` PASS at49ddb5d. No shared scripts changed; shared-script pytest was not required.
- Codex and Grok completion refutes pending on the committed artifact. No completion/status claim until the required review basis is recorded. In conservation mode, disputed observations will be withdrawn/held as a strict subset, with no new frame/batch.

## Prior-pass receipt and integration base

PR149 merged by controller as2845288, head263f35a:31legacy updates+11newC/127EVD; census3V4R46U26D, Ohio70D8V8R346U. Lee was withdrawn as a strict subset of73cd5ee; Codex approval, Grok-only-Lee finding and the controller's explicit subset/no-fifth-review ruling are recorded there. Clean7d526c8 main replay, validator0, row-loss and hostedvalidateSUCCESS preceded merge. The present title branch refreshed to49ddb5ddd636e6023b4cc381678dd3629717ffb4 before application; all184 candidate baseline cells were unchanged. Merged people/evidence are preserved. Initial discovery basee008ab9 and intervening refresh receipts remain in the private/BOARD journal.

Not checked: live discovery API replay, an exhaustive faculty census, or factual re-adjudication of people outside the fixed184. Availability-only cases and original-hash loss are limitations, not passing gates.

## Refute fix pass 2026-11-06 (Claude, controller thr_9i2c6byhcz)

This pass handles Codex2 REFUTE (2 findings) and Grok2 REFUTE (4 findings) of 75cdeb5. The fix is a pure withdrawal: a strict subset of 75cdeb5, with no new or rewritten values. The integrator withdraws three people at application time (`withdrawn.csv`). The lanes' own packets (`lanes/*/verified.csv`) and their private dispositions stay as the lanes' record, so they still show 91 proposals. check.py now asserts that the 91 lane proposals minus the 3 withdrawn equal the 88 applied people.

| Finding | Disposition |
|---|---|
| Codex2 #1 / Grok2 #1, PERSON-000624 Kroonblawd, Deputy Group Leader→group_leader | **Withdrawn, held STILL_UNCERTAIN.** SCHEMA §4.9 has no Deputy Group Leader fold, and the merged PR149 Maiti example is not an owner ruling (AGENTS §2 rule 9). Settles on a dated §4.9 owner ruling. The baseline research_scientist pair is restored. EVD-283018/283019 are retired. In lane3's check, the `group_leader` pattern is now anchored `^Group Leader\b`, so "Deputy Group Leader" no longer passes and "Group Leader / Polymer Engineer" (Cook) still does. |
| Codex2 #2 / Grok2 #2, lane3 check fails on the applied tree | **Fixed.** The live pair must equal either the exact baseline pair or the exact applied proposal. New in-check fixtures: the baseline pair passes, the applied pair passes, and a mixed pair (baseline role with a different title) fails. For a parent-withdrawn person, the live row must be at baseline and the lane proposal must fail `validate`. Injection: lane3 run against 75cdeb5's people.csv fails with `withdrawn person not at baseline`. |
| Grok2 #3, PERSON-000635 Addison, scope witness is a news feature about assisting a paper | **Withdrawn, held STILL_UNCERTAIN.** Settles on a lab staff-directory or program page stating his polymer research (SCHEMA §4.9). The printed grade title may be re-proposed with that witness. Baseline restored. EVD-283024/283025 are retired. |
| Grok2 #4, PERSON-000636 Roy, polymer sentence is the program's and his name is 74 words away | **Withdrawn, held STILL_UNCERTAIN.** Settles on a polymer-research statement that binds Roy within 40 words. Baseline sources and last_verified restored. EVD-283026/283027 are retired. |

Rows for the three in rawcheck.csv are kept. They certify only that each quote appears on its page; nothing applies them. root16, lane1 and lane2 check lane proposals, not live data, so they are unedited and still pass with Addison and Roy in root16's packet. A gap they expose, surfaced and not fixed here: the root `near()` check runs only when `surname_witness` is set, and neither root16 nor the root checker requires the polymer witness to fall within 40 words of the person. That is how Roy's row passed.

**Counts after withdrawal** (unit: existing candidate people). 88 VERIFIED, 7 REJECT, 89 STILL_UNCERTAIN. Applied to 88 people (83 tier A, 5 tier B): 75 printed-title changes, 12 role changes and 13 already-exact pairs; 68 people gain sources and all 88 get a new last_verified. That is 183 evidence rows: EVD-283000 to EVD-283188, less the 6 retired IDs, which are never reused. By source list: atlas-cleanup 88/7/89, and role-title-recheck-2 65/6/64 (Kroonblawd and Addison are on both lists; Roy is on atlas-cleanup only).

**Strict subset proof.** `delta_compare.py 75cdeb5 <head>` reports only-in-75cdeb5 = 15, with 0 cells only in the new head, 0 value differences and 0 new-row differences. The full list of 15 is: EVD-283018, 283019, 283024, 283025, 283026 and 283027 (6 new rows); PERSON-000624 role, role_as_published, sources and last_verified; PERSON-000635 role_as_published, sources and last_verified; PERSON-000636 sources and last_verified.

**Merge and persistence.** Merged origin/main 0dd6c53 with a normal merge (no conflicts). Restored main's people.csv and evidence_people.csv, then re-ran build.py. A second run is a no-op. The sanitized page cache (477 files) is copied to `thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/people-titles-3-2026-11-06/pages/`. `fetch.py` and the lane3 `--cache-root` default read that copy when it exists and fall back to /tmp. The private `tools/fetch.py` used by root16 still reads /tmp. The private `account.py` was not re-run, because it writes into the lane thread's storage and reads that lane's own checkout.

**Checks on this head:**
- `python3 tasks/people-titles-3-2026-11-06/check.py`: PASS, 88 people / 183 evidence, including the withdrawal reconciliation and an injected reuse of a retired ID, which fails.
- `python3 tasks/people-titles-3-2026-11-06/lanes/lane1/check.py`: PASS.
- `python3 tasks/people-titles-3-2026-11-06/lanes/lane2/check.py <private>/lane2 <persist pages>`: PASS.
- `python3 tasks/people-titles-3-2026-11-06/lanes/lane3/check.py --private-root <private>/lane3`: PASS.
- `python3 tasks/people-titles-3-2026-11-06/lanes/root16/check.py`: PASS.
- `python3 scripts/validate.py`: OK, 0 errors.
- `python3 scripts/check_row_loss.py --base origin/main`: OK.

**Surfaced for the owner, not changed here.** Merged PERSON-000621 Maiti (PR149) carries the same unruled "Deputy Group Leader"→group_leader fold.
