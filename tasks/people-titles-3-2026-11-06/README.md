# Remaining people titles — 2026-11-06

L12 continuation `agent/codex/people-titles-3`; controller owns merge/status. Only people.csv and evidence_people.csv are canonical outputs. The fixed pre-application scope is the union of two published title-hold lists, less people already covered by merged PR149. No new discovery frame or subsequent batch is included.

## Result and source filters

Unit: existing candidate people, with overlapping source-list filters. **184 unique people = 91 VERIFIED rechecks, 7 REJECT dispositions and 86 STILL_UNCERTAIN; no duplicates or creates.** All184 have an ordered disposition with a deciding/settling fact. The seven excluded people remain canonically untouched; this title pass neither deletes people nor changes tiers.

| Source/filter | Raw candidate people | Covered by PR149 | This pass | VERIFIED | REJECT | STILL_UNCERTAIN |
|---|---:|---:|---:|---:|---:|---:|
| atlas-cleanup holds, people title rows |214|30|184|91|7|86|
| role-title-recheck-2 holds, people rows |149|14|135|67|6|62|

Do not sum these source rows as unique people. `source_counts.csv` is recomputed against original source IDs; `verdicts.csv` accounts each of184 once. The original lists contain214 unique people;30 are covered by PR149, leaving184. Title shape alone did not determine a verdict: all184 were checked, including44 that already looked title-shaped under the earlier heuristic.

Applied: **91 existing people (83 tierA,8 tierB),77 printed-title changes,13 controlled-role changes,14 already-exact title/role observations;189 append-only own_site evidence rows**. Each person gets current role/title and polymer-scope witnesses; seven supplemental rank observations resolve/corroborate dated appointments. No affiliation, program, name, specialty, profile URL or tier changes. All pre-pass people/evidence and all unowned cells remain intact. Evidence IDs EVD283000–283188; no person IDs allocated.

The source packets are lane1 56→27V29U; lane2 56→31V6R19U; lane3 56→28V1R27U; NLR16→5V11U. Their READMEs distinguish target-body review from availability-only inspection, PDF conversion from inspected pages, shared pages and person-level fetch budgets. Failed routes never prove absence. The controller clarified approximately6 distinct primary routes per person; shared directories count once for all covered people.

## Acceptance and evidence

Acceptance was fixed before application: re-read current institution-owned pages, settle the exact printed title and §4.9 role together, bind the correct person entry/surname within40words, require current person/lab polymer-material research, preserve every other claim, append evidence, and pass deterministic conservation/replay checks plus two-family refute. The builder uses scripts/shard_io.py append_sorted; expected.json and base_commit.txt are the pre-pass backup/journal.

Titles come from formal headings, fields, catalog entries or explicit title attributions; biography noun phrases are not copied as titles. Case/punctuation remain exact, whitespace alone normalizes. Literal pipes are retained when actually printed in a formal field. Kramer has an eligible primary Associate appointment plus a separately printed secondary Adjunct appointment; solely adjunct ranks remain excluded. University Research Assistant/Associate/Professor maps to research_professor under §4.9.

GateB uses current person-specific research statements or explicitly named own institutional lab programs, not menus, roster categories, fingerprints, publications, prior degrees or ordinary natural biology. Bharti explicitly investigates manufactured microplastics transport. Salas-de-laCruz explicitly engineers functional natural-polymer biomaterials. Njardarson's named ongoing sulfur-material collaboration supplies context beyond a generic example list. Peresin's `/experts/` witness is an institutional expert profile. Chipara's8-page faculty catalog was extracted8/8 and page2 visually inspected to bind his own column. No new specialty mapping is attempted.

All189 quote keys pass exact-token raw matching and the25word quote ceiling. Core GateA retains surname/own-published alias proximity. Cook's current LLNL profile explicitly bridges Krikorian(Cook); the held name remains unchanged. Jäkle/Jaekle are own-published spellings. Long's supplemental promotion sentence is bound to the same individually named current profile as the core surname-proximate title witness. Source dates stay full ISO or empty; Nangia's source gives only promotion year2023, so no day is invented.

Long's live NAS maxAge0 response200 prints Graduate Programs, modified2026-11-05T17:45:38Z; this supersedes the older indexed Graduate Education wording. Hallinan2025, Stache2026 and Lu2025 own dated promotions resolve prior rank disagreements. HuYang's joint Marquette/MedicalCollegeWisconsin own lab is linked from the primary departmental profile; affiliation remains Marquette. NLR grade-only titles keep prior enums under B-NLR-1(a); no tier upgrades or novel folds.

Kroonblawd's proposed Deputy Group Leader→group_leader follows the identical Maiti pair already merged in PR149, with fresh independent own identity/title/polymer research. This is L12's precedent interpretation for family refute, not a new owner ruling. The owner-addendum curator flagged the precedent but did not authorize or approve this case.

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

- `python3 tasks/people-titles-3-2026-11-06/check.py` PASS:184 exact IDs/source filters,91 existing/0creates/189evidence,rawquotes,role/title pairs,own domains,pre-pass preservation,7matcher negatives,8production mutations and byte-identical replay.
- Four lane checks PASS, with3/5/4 actual university calibrations and3NLR known answers; wrong quote/person/rank-affix fixtures fail. Production fake-quote tests include a forged matching certificate; actual source matching rejects it. A late foreign-shard evidence collision fails before writes.
- Private account.py PASS184 unique inputs/outputs/facts/proposal parity; missing/duplicate/wrong-identity/unknown-verdict mutations fail.
- `python3 scripts/validate.py` PASS0errors, including people-grain/email checks. `python3 scripts/check_row_loss.py --base origin/main` PASS at49ddb5d. No shared scripts changed; shared-script pytest was not required.
- Codex and Grok completion refutes pending on the committed artifact. No completion/status claim until the required review basis is recorded. In conservation mode, disputed observations will be withdrawn/held as a strict subset, with no new frame/batch.

## Prior-pass receipt and integration base

PR149 merged by controller as2845288, head263f35a:31legacy updates+11newC/127EVD; census3V4R46U26D, Ohio70D8V8R346U. Lee was withdrawn as a strict subset of73cd5ee; Codex approval, Grok-only-Lee finding and the controller's explicit subset/no-fifth-review ruling are recorded there. Clean7d526c8 main replay, validator0, row-loss and hostedvalidateSUCCESS preceded merge. The present title branch refreshed to49ddb5ddd636e6023b4cc381678dd3629717ffb4 before application; all184 candidate baseline cells were unchanged. Merged people/evidence are preserved. Initial discovery basee008ab9 and intervening refresh receipts remain in the private/BOARD journal.

Not checked: live discovery API replay, an exhaustive faculty census, or factual re-adjudication of people outside the fixed184. Availability-only cases and original-hash loss are limitations, not passing gates.
