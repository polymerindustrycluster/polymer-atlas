# L12 people settlement — 2026-11-06

Claim: atlas-L12-people-settle, delegated application in branch agent/codex/people-settle.
Only people.csv and evidence_people.csv are canonical data outputs. Controller retains merge/status authority.
Branch history (base_commit.txt) is the pre-pass backup; reviewed.csv, expected.json and rawcheck.csv are the pass journal.

## Applied packet

47 reviewed people: 31 existing records (28 tier A, 3 tier B) and 16 new tier C people.
18 printed-title values change; five controlled roles change. Remaining cells refresh public sources/verification dates.
141 append-only own_site evidence observations: existence, scope and affiliation/parent for every reviewed person. New records require all three prospectively; unchanged legacy affiliations need not have been backfilled, but this packet records the fresh own-profile observations it checked.
No existing evidence, people, institutions or relationship records are deleted.

- PERSON-000063 Yavitt: professor → assistant_professor. UC's live roster and research page print Asst Professor (F2)
  beside Ben Merkel Yavitt; the research page names rheology, polymer processing and polymer physics.
- PERSON-000621 Maiti: research_scientist → group_leader, from LLNL's Deputy Group Leader, Multiscale Modeling.
- PERSON-000920 Scott and PERSON-001139 Ayzner: associate_professor → professor.
- PERSON-001238 Fernandez-Ballester: assistant_professor → associate_professor.
- PERSON-002000, PERSON-002002–002004: Ellen M. Sletten, Sang Bok Lee, Paul Van Tassel and Sarah Heilshorn.
  Institution-owned profiles state both current professor styling and person-level polymer research.
- EVD-280000–280142 excluding 280046–280047: reserved L12 allocation; three rows per reviewed person.
  Append-only observations retain existing verification tiers; new people remain C.

Sources are the university/laboratory URLs in reviewed.csv. Every quote was re-fetched with a browser-UA curl route,
with the house Jina fallback. rawcheck.csv records exact word-sequence checks, surname proximity for Gate A,
observation date and fetched-text hashes. Raw pages stay outside the repository to avoid exporting contact data.
The previous Windows-only raw checker was inspected; fetch.py reuses its word-sequence matching method with stdlib/curl.

## Source-list accounting

Unit: candidate people within each named source list. The title lists overlap: never sum them as unique people.

| Source list / filter | Candidates | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---:|---:|---:|---:|---:|
| census-gap-2 uncertain.csv, all rows | 79 | 4 | 4 | 45 | 26 |
| atlas-cleanup holds.csv, role-title rows | 214 | 30 | 0 | 184 | 0 |
| role-title-recheck-2 holds.csv, all rows | 149 | 14 | 0 | 135 | 0 |

The 30 and 14 title verdicts overlap and represent 30 unique title candidates, plus the separate Yavitt correction.
Some previously applied titles are rechecked without changing their printed wording.
Every unresolved candidate has a named settling fact in census_verdicts.csv or title_verdicts.csv.
A failed fetch is availability only. Neither publication titles nor institution-wide menus are Gate B evidence.
Same-institution duplicates are reported as DUPLICATE_OF terminating at held IDs; no duplicate records are merged/deleted.
Possible cross-institution matches require resolving the current primary home before creating anything.

## Holds requiring judgment

| Candidate / issue | Evidence and recommended reading | Settling action |
|---|---|---|
| Zheng-Rong Lu | [CWRU profile](https://case.edu/medicine/ccir/faculty/zheng-rong-lu) states biodegradable macromolecular MRI contrast agents. Recommend admission if owner confirms this materials-engineering reading satisfies Gate B. | Owner Gate B ruling; HOLD. |
| Carlos Crespo | [CWRU profile](https://case.edu/artsci/chem/faculty/crespo/) studies light-induced phenomena in molecules, biopolymers and cells; current applications center on small-molecule photomedicines. Recommend retain hold pending a stated engineered-polymer-material research object. | Owner Gate B ruling; HOLD. |
| Sara Molinari | Live UMD profile now describes engineering both cells and biopolymer matrix. Earlier B-CG-2 explicitly did not admit her. | Hold for owner review against B-CG-2 rather than silently reverse it. |
| Qiang Wang title lead | A surname-proximate rank on a page at /people/david-wang/ is insufficient identity resolution. | Institution-own identity confirmation before editing. |
| Teaching/practice titles | Teaching Professor / Professor of Practice are held against the dated B-CG-1 styling decision. | Do not infer an eligible rank from a prior biographical professorship. |
| 45 remaining census candidates | Individual missing facts, failed routes or primary-home conflicts in census_verdicts.csv. | Current institution-own rank plus current person-level polymer research. |

## Ohio fresh wave

The original 130 STILL_UNCERTAIN names/full outputs are local-only in another harness's staging, absent on this Mac.
This is the IDEAS F-10 bus-factor risk, confirmed by controller thread thr_9i2c6byhcz.
The estate search was incomplete because the Windows Documents catalogs are absent on this Mac; a miss is not absence.
Controller explicitly replaced waiting for that list with a fresh public-directory rebuild, followed by institution-own checks.
The live API returns 432 unique object IDs, reconciled against independent total432 across five pages.
Directory lead content and the full candidate/reject list remain local-only. The initial normalized name+institution dedupe found 67 held people; three additional variants were resolved on review. Final pre-application accounting is70 held people,362 remaining candidate people. This is NOT a claim that the exact original130 have been recovered.
The packet helper owns ohio/ only, never canonical data. Twelve fresh-wave candidates were independently checked and admitted by this lane as PERSON-002005–002016 (all C). See ohio/README.md for final fresh-frame accounting and holds. Original130 have not been individually recovered.

## Named checks and replay

- python3 tasks/people-settle-2026-11-06/check.py — PASS:
  79/79 census rows, 214/214 +149/149 title-source rows;47 reviewed people;16 creates;141 evidence rows;
  unchanged non-owned cells;append-only evidence;byte-identical builder replay.
- Known answers before accepting the matcher: Yavitt assistant rank, Sletten professor rank, Mai assistant rank
  on freshly fetched institution pages. Injected nonexistent rank, wrong surname and empty-token Cyrillic surname fail.
  This also catches silently accepting an empty surname. Matcher output alone never admits research scope.
- python3 scripts/validate.py — PASS,0 errors, including V-22 people grain and V-51 email checks.
- scripts/ is unchanged; scripts/pytest was not required.
- Replay: check out fresh main's two owned data files, then python3 tasks/people-settle-2026-11-06/build.py.
  Expected-cell and evidence-ID checks stop conflicting rebases; resolve the packet explicitly rather than hand-merge CSVs.
  Update base_commit.txt to that pre-pass base before running the diff oracle.

## Independent refutes

Initial Codex review REFUTE (c1528f0): Wong repeated the original held example list; prospective creates lacked affiliation evidence; the quote matcher accepted partial words. Wong was withdrawn before integration; all47 current records now have source-backed affiliation observations; matching now compares complete token sequences. The oracle injects a missing parent row and confirms rejection for creates, and rejects polymer inside depolymerization/polymers plus materials inside biomaterials.

Reviewer correction: missing parent rows were not independently blocking on the31 legacy edits under tier-restatement clause3. That legacy exception is preserved; the extra affiliation observations are scoped fresh evidence, not a schema/vocabulary change.

Final Codex/Grok re-review pending. Controller's 05:55 BOARD directive supersedes council-only routing:
Codex clerk thr_mdr3gn2xmm and Grok clerk thr_f2fcbx6tq8, two independent families still required.
No completion approval claimed while either independent review remains pending.

Dedupe cross-check: atlas.py dedupe-check was run with the four new names and UCLA/UMD/Yale domains.
It resolves existing institutions (organization/site grain only); people-grain admission additionally checks all
people.csv names with initials removed and first-name/surname matches within the same institution. Both checks are required.

Unmerged draft correction: Wong's quoted example list did not settle the source's named polymer-project fact.
His proposed create was withdrawn before integration; PERSON-002001 and EVD-280046–280047 are permanently reserved,
never reused. Sarah Heilshorn is admitted on a newly fetched Stanford lab materials-engineering statement
(B-CG-2); Lee and Van Tassel use explicit conductive-polymer work / nanofilm material-construction witnesses.
These changes withdraw draft proposals only; all pre-pass held people/evidence remain unchanged.


## Final fresh Ohio coverage

Unit: candidate people within the freshly rebuilt432-profile source frame, with unique normalized(name,institution) identities.
Final outcomes:70DUPLICATE_OF +12VERIFIED +8REJECT +342STILL_UNCERTAIN =432.
All250 previously fetched-but-uninspected candidates received explicit gate/source-inspectability review (199helper +51parent). One binary-only source remains uninspectable; it is held rather than passed.
The58 cases without a usable own-institution page received individual route/missing-fact verdicts; they remain uncertain,
not negative evidence. There are0 unaccounted input candidates. Of342uncertain candidates,283 have reviewed sources
that do not settle both gates (including2owner holds),1has only uninspectable binary data, and58 lack a usable institutional source. Owner holds Lu/Crespo remain unapplied.

The full discovery worklist stays outside the public tree, but is now durable:
 /Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-settle-private/
This sanitized packet preserves candidate identities, source URLs/hashes, by-candidate verdicts, bounded-review notes,
a privacy-filtered API rebuild script, and an independent accounting checker. No directory biographies, contact details,
salary values, or raw page bodies are retained there. The public ohio/README.md records hashes and checks.
Only institution-supported VERIFIED professional facts travel in this PR.

Additional Ohio admissions after the first8: Allen Yi (polymer-optics injection molding), Byung-Wook Park
(current engineered living-material hydrogels), Julie Renner (her own laboratory's current polyproline
monolayer assembly/antifouling research), Aleksander Skardal (current ECM bioinks expertise with continuing
ECM-derived hydrogel/biofabrication work). The Julie own-lab attribution and Skardal history/current bridge are
explicit final-refute targets; neither rests on publication titles alone.
