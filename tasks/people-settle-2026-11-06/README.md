# L12 people settlement — 2026-11-06

Claim atlas-L12-people-settle; branch agent/codex/people-settle; PR149.
Only people.csv/evidence_people.csv are canonical outputs. Controller retains merge/status authority.
base_commit.txt is the pre-pass backup; reviewed.csv,expected.json,rawcheck.csv,evidence_append.csv form the replay journal.

## Applied packet

46 reviewed people:31 existing(28A/3B),15 newC.18 printed titles and5 controlled roles change.
140 own_site observations:existence/scope/affiliation for each46person(138),plus two explicit correction witnesses.
New people require all3 claims prospectively. Unchanged legacy affiliations did not require backfill; this packet
retains the fresh own-profile observations it checked. No pre-pass held people/evidence/institutions are deleted.

- Yavitt PERSON000063:professor→assistant_professor; current UC roster/research entry prints Asst Professor(F2).
- Maiti PERSON000621:research_scientist→group_leader from Deputy Group Leader,Multiscale Modeling.
- Scott PERSON000920 and Ayzner PERSON001139:associate_professor→professor.
- Fernandez-Ballester PERSON001238:assistant_professor→associate_professor.
- Four census creates:PERSON002000 Sletten,002002 Lee,002003 VanTassel,002004 Heilshorn.
- Eleven fresh-Ohio creates:PERSON002005–002014 and002016.
- EVD280000–280144,excluding280046–47 and280137–139. IDs are frozen; gaps permanent.

Every quote was independently re-fetched through browser-UA curl/Jina. rawcheck.csv records exact-token
matches, Gate-A surname proximity, date and processed-text hashes. Raw pages stay outside the public tree.
The matcher reuses the house word-window rule; it rejects partial words and noncontiguous phrases.
Institution-domain checks cover both primary gates and supplemental witnesses.

## Source-list accounting

Unit:candidate people within each named source/filter. Title lists overlap; never sum them as unique people.

| Source/filter | Candidates | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---:|---:|---:|---:|---:|
| census-gap-2 uncertain.csv,all rows |79|4|4|45|26|
| atlas-cleanup holds.csv,role-title rows |214|30|0|184|0|
| role-title-recheck-2 holds.csv,all rows |149|14|0|135|0|
| fresh Ohio frame,after final-refute corrections |432|11|8|343|70|

The title outcomes represent30 unique candidates,plus the separate Yavitt correction.18 title values change;
other printed wording is rechecked alongside source/date updates. Every unresolved source candidate has a named
settling fact. Duplicate chains terminate at held records; none are merged/deleted. Current primary-home conflicts
block creates. atlas.py dedupe-check resolves institutions; people-specific checks additionally compare normalized
full names and first/surname variants against all people.csv rows.

The original130 Ohio uncertain names were unavailable in another harness staging area on this Mac
(IDEAS F-10 bus-factor risk,confirmed by controller). Windows Documents catalogs were absent,so the estate
search was incomplete,not proof of absence. Controller explicitly substituted a fresh public-directory rebuild.
The API returned432 unique objectIds AND432 normalized(name,institution) candidate identities across5pages.
Three additional name variants beyond initial67matches yielded70 pre-application held identities.

All250 formerly uninspected fetched inputs received gate/source-inspectability review(199helper+51parent);
one binary-only source remains explicitly uninspectable.58 cases have individual unavailable-route/missing-fact
verdicts. Failed fetches do not establish absence. No unaccounted input is hidden as passing.
The original fixed archive reported12VERIFIED/342UNCERTAIN; review withdrew one unmerged proposal,so the
append-only after_refute revision reports11VERIFIED/343UNCERTAIN. The original archive/hash and the second-pass
342-person input remain immutable. Julie's new hold is outside that frozen second-pass frame.

## Holds and corrected interpretations

| Candidate/issue | Evidence/recommendation | Settling action |
|---|---|---|
| Zheng-Rong Lu | [Own profile](https://case.edu/medicine/ccir/faculty/zheng-rong-lu):biodegradable macromolecular MRI contrast agents. Recommend admission if owner accepts this engineered-material reading. |Owner Gate-B ruling;HOLD.|
| Carlos Crespo | [Own profile](https://case.edu/artsci/chem/faculty/crespo/):photochemistry of molecules,biopolymers,cells. Recommend retain hold pending explicit material engineering. |Owner Gate-B ruling;HOLD.|
| Julie Renner | [Own PI profile](https://case.edu/engineering/labs/renner/group-members/julie-renner) and [lab group](https://case.edu/engineering/labs/renner/group-members) describe a student's polyproline project. Codex accepted own-lab attribution;Grok refuted person-level scope and polymer_physics mapping. Recommend owner decide whether this explicit own-lab project meets the required grain;no self-ruling. |Unmerged create withdrawn;PERSON002015/EVD280137–139 permanently unused.|
| Byung-Wook Park | Profile header Associate Professor conflicts with present-tense Assistant Professor bio. [Official Fall2026 syllabus](https://catalog.ysu.edu/syllabi/2026-fall/chen-6990-04-41034/) explicitly names Park and Instructor Title:Associate Professor. |Current dated instructor styling supports associate_professor;EVD280144 appends that witness.|
| Huichun(Judy)Zhang | Own page states polymeric sorbents,not membranes. |Specialty corrected to exact published Polymeric sorbents;EVD280143 explicitly supports it.|
| Sara Molinari | UMD page now describes engineering cells and biopolymer matrix;earlier B-CG-2 explicitly did not admit her. |Hold for owner review rather than silently reverse that ruling.|
| Qiang Wang title lead | A surname-proximate rank at /people/david-wang/ does not settle full identity. |Own-institution identity confirmation before editing.|
| Teaching/practice titles | Governed by B-CG-1;senior_lecturer exception is distinct. |No inferred eligible research rank.|
| Remaining candidates | Named facts in source verdict files/private revision. |Current own rank/current polymer statement or primary-home resolution.|

Wong's unmerged create repeated its original held example list and was withdrawn earlier;
PERSON002001/EVD280046–47 remain permanently unused. Heilshorn instead has a freshly fetched Stanford
lab statement engineering protein hydrogels(B-CG-2). Lee now has current primary Chemistry rank2013-present
and explicit conductive-polymer nanostructure work. VanTassel has his own lab nanofilm-material construction project.
These withdrawals revise unmerged proposals only; all pre-pass held rows remain intact.

## Durable continuation and privacy

The complete discovery worklist stays outside the public tree:
 /Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-settle-private/
It preserves the original immutable frame/verdicts and a separate after_refute_revision.json/check_after_refute.py.
Only sanitized identities,sourceURLs/hashes,verdicts/missing facts and accounting/rebuild scripts persist.
No directory biographies,contacts,salary values or raw institutional bodies are retained there.
The public ohio/README.md records source filters,institution counts,hashes and limitations.
Only institution-supported professional facts publish;no CRM/private census/band-B leads were accessed.

## Named checks

- python3 tasks/people-settle-2026-11-06/check.py — PASS:79/79 census,214/214+149/149 title-source rows;
  46 reviewed people,15 creates,140 evidence;unchanged non-owned cells;no pre-pass loss;byte-identical replay.
- Known answers:Yavitt assistant rank,Sletten professor rank,Mai assistant rank.7 injected negatives include
  wrong rank/person,empty-token surname,polymer inside depolymerization/polymers,materials inside biomaterials,
  and noncontiguous words. Missing-parent mutation on a NEW create fails. Fall2026 Park styling is independently checked.
- python3 tasks/people-settle-2026-11-06/ohio/check.py — PASS:11 proposals/22 raw quotes,exact ID/name parity.
- Durable check_accounting.py — PASS:original432/308 yield/hash/privacy/duplicate controls.
- Durable check_after_refute.py — PASS:432=70DUP+11VERIFIED+8REJECT+343UNCERTAIN;original archive unchanged.
- python3 scripts/validate.py — PASS,0 errors(V22/V51 included). scripts/unchanged;pytest not required.
- Replay:fresh main owned data files,then build.py;expected-cell/ID guards stop conflicts. Update base_commit.txt
  to that pre-pass base for the diff oracle. No hand-merged CSV conflicts.

## Independent refutes

- c1528f0 Codex REFUTE:Wong repeated a held example list,new creates missed parent observations,matcher accepted
  partial words. All fixed. Grok APPROVE was bounded to that initial35-person commit and is not final approval.
- 066c448 Codex APPROVE:all16 then-proposed creates/all12 then-Ohio admissions independently checked,
  plus new-parent mutation and deterministic checks. Remaining25legacy sources not independently re-fetched.
- 066c448 Grok REFUTE:Julie lab-student attribution/tag,Zhang membrane inference,Park conflicting rank.
  Julie is held/withdrawn;Zhang literal specialty corrected;Park now has a current dated official syllabus witness.
  These fixes await re-review by both families.
- Legacy-parent correction:SCHEMA4.13 tier-restatement3 does not independently require unchanged legacy
  affiliation backfill. No new repository-wide rule was introduced.
- Controller's clerk route supersedes council-only dispatch;final Grok runs xhigh. No completion approval
  is claimed until both families approve the revised artifact.
