# Ohio fresh faculty review — 2026-11-06

This is a fresh review wave. The original 130 uncertain names were unavailable, so their outcomes cannot be reconstructed from this packet. Discovery supplied names, positions and institutions only. Public people proposals use independently checked institution-own evidence; directory biographies, contact information and rejected/uncertain lead lists are not published.

## Candidate-person accounting

The independent API pagination total was **432 profiles**, with **432 unique objectIds**. A separate assertion found **432 unique normalized `(name, institution)` candidate identities** (case, accents, whitespace and punctuation folded), with zero repeated candidate keys within the frame. Counts use the directory's first listed institution for discovery-frame accounting; that affiliation is not itself proof of current employment.

Same-institution dedupe found **70 held people**: 67 initial matches plus three reviewed name variants. The **362 remaining candidate people** yielded **12 VERIFIED, 8 REJECT and 342 STILL_UNCERTAIN**. These are pre-application frame counts; the 12 verified people subsequently became held records. Cross-institution identity conflicts remain holds.

| Discovery institution | Candidate people | Already held | VERIFIED | REJECT | STILL_UNCERTAIN |
|---|---:|---:|---:|---:|---:|
| Bowling Green State University | 10 | 4 | 1 | 0 | 5 |
| Case Western Reserve University | 112 | 15 | 4 | 1 | 92 |
| Cleveland State University | 11 | 2 | 0 | 0 | 9 |
| Kent State University | 2 | 0 | 0 | 0 | 2 |
| Northeast Ohio Medical University | 3 | 0 | 0 | 0 | 3 |
| Ohio State University | 136 | 19 | 3 | 1 | 113 |
| Ohio University | 22 | 3 | 0 | 0 | 19 |
| University of Akron | 41 | 19 | 0 | 1 | 21 |
| University of Cincinnati | 71 | 5 | 3 | 5 | 58 |
| University of Dayton | 18 | 2 | 0 | 0 | 16 |
| University of Toledo | 1 | 0 | 0 | 0 | 1 |
| Youngstown State University | 5 | 1 | 1 | 0 | 3 |
| **Total** | **432** | **70** | **12** | **8** | **342** |

## Review yield and limits

The continuation accounted for all **308 previously unreviewed candidate inputs**: 199 non-Cincinnati fetched candidates in batches of **50/50/50/49**, 51 Cincinnati fetched candidates reviewed independently by the parent, and 58 source-availability cases. Input and output identities reconcile exactly; no pending-uninspected stage remains.

All 250 fetched inputs were individually examined for candidate identity, professor rank and current polymer scope. One candidate's sole fetched source was binary PDF data, so it received an explicitly uninspectable-route hold, not a completed page gate check. Publication-only records, noncandidate redirects, generic directories and unrelated nearby faculty statements were held on their exact missing facts. The 58 availability cases each retain the failed URLs/statuses and the specific rank/scope facts still needed. Failed retrieval never establishes absence.

The final 342 uncertain candidates comprise 281 reviewed unresolved cases, two requested owner Gate-B holds, one binary-only uninspectable case and 58 availability cases. These are unresolved facts, not rejected people. The eight rejects rest on directly stated excluded university roles, retirement or dated institutional death notices. No reject rests on failed search, missing keyword or inaccessible page.

The source inventory reconciles **686 unique institution-domain URLs**: 552 fetched text responses, 127 unavailable routes and seven raw-PDF-byte responses that the HTML helper cannot extract. A successful response is not automatically a valid person source or gate witness. No new broad searches/fetches were run during the 308-input continuation.

## Public proposals and application

`verified.csv` contains the frozen first eight proposals. `verified_more.csv` contains four later proposals. Each carries institution-own Gate-A and Gate-B URLs and short quotes, exact published title, source-supported specialties and rationale. Current per-person research fields are admissible witnesses; publication titles and generic center/program membership are not.

The parent applied all 12 proposals; this helper made no `data/` edits:

| Person ID | Person | Packet |
|---|---|---|
| PERSON-002005 | Faith Wyzgoski | verified.csv |
| PERSON-002006 | John D. Protasiewicz | verified.csv |
| PERSON-002007 | Burcu Gurkan | verified.csv |
| PERSON-002008 | Huichun (Judy) Zhang | verified.csv |
| PERSON-002009 | John Robert Martin | verified.csv |
| PERSON-002010 | Jonathan David Nickels | verified.csv |
| PERSON-002011 | Junhang Dong | verified.csv |
| PERSON-002012 | Pavel Anzenbacher | verified.csv |
| PERSON-002013 | Allen Yi | verified_more.csv |
| PERSON-002014 | Byung-Wook Park | verified_more.csv |
| PERSON-002015 | Julie Renner | verified_more.csv |
| PERSON-002016 | Aleksander Skardal | verified_more.csv |

The first eight used EVD-280072–EVD-280087 initially; the parent subsequently added required affiliation witnesses. The four later people used EVD-280131–EVD-280142, three must-have claims each. The parent owns complete evidence allocation, integration validation and completion reviews.

Specialty boundaries: John Protasiewicz uses the current profile's literal “Polymers”, replacing the legacy future-tense nanobook witness; polymer synthesis was not inferred. Julie Renner's scope comes from her own current laboratory's explicit polyproline monolayer/antifouling project, with her PI appointment established separately. Skardal's current expertise field names ECM bioinks; the full hydrogel/toolkit paragraph explicitly says the work continues at Ohio State today.

## Owner holds

- **Zheng-Rong Lu:** the [institutional profile](https://case.edu/medicine/ccir/faculty/zheng-rong-lu) states a current professor rank and “Biodegradable macromolecular MRI contrast agents”. Hold until the owner decides whether engineered macromolecular imaging agents meet Gate B, or a direct polymer-material design statement settles it.
- **Carlos Crespo:** the [institutional profile](https://case.edu/artsci/chem/faculty/crespo/) states a current professor rank and “light-induced phenomena in molecules, biopolymers, and cells”. Recommendation: retain hold unless an explicit material-engineering statement or owner ruling accepts this photochemical scope.

Other named holds and all rejected/uncertain identities remain only in the private continuation packet. Existing held identities were not recreated; persistent old institutional pages did not override current-home conflicts.

## Named checks and durable continuation

- `python3 tasks/people-settle-2026-11-06/ohio/check.py` — **PASS**: seven known-answer/boundary checks, including wrong rank, wrong person, injected >40-word surname distance and polymer/depolymerization negatives; 12 unique public proposals; 24 raw quotes; every Gate-A surname within 40 words; exact titles present; institution URLs; no personal contacts/email-bearing URLs; LF CSV. Global held-name guards exempt only PERSON-002005–002016 with the exact expected ID/name mapping and canonical key-field parity.
- `python3 /Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-settle-private/check_accounting.py` — **PASS**: independent 432 total, unique profile IDs and normalized candidate identities, all institution/verdict/stage totals, exactly 308 continuation outputs, privacy field whitelist, archive hashes and injected duplicate failure.
- API rebuild script — **PASS offline fixture**: five pages at offsets 0/100/200/300/400, 432 identities, and injected biography/contact fields discarded. Live API replay was not run during this continuation.

The durable private packet is [people-settle-private](/Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-settle-private/README.md). It contains sanitized names/IDs/institutions/source URLs/verdicts/missing facts, review inputs and notes, source-content hashes, the privacy-preserving API rebuild script and the standalone accounting check. No raw directory response, biography, personal contact field, salary value or raw institutional page is retained there. The source cache remains temporary at `/tmp/atlas-l12-pages`.

| Durable artifact | SHA-256 |
|---|---|
| frame.json | `476dd18432138cf45db2d0237a87bfb8b4b5ca299e41723916b452acbe493597` |
| verdicts.json | `5a7f6bb37c1e838b31bba5f457b6d927d2ee28449b4e91f6d5aa993afc71fb85` |
| summary.json | `a712f7379db1df2094e7b5b7e05b63df29cfab5ee3b5bd27649c2a39a06e642a` |
| source_manifest.json | `be0bcff19cb1b5aed071a33ed6e4d2a2969f6f2d5cb32130454b896ee8140560` |

The packet check requires the temporary source cache; the durable accounting check does not. Quote presence and proximity do not independently establish semantic scope or primary-home currency. Those claims were reviewed against the source context, with uncertain interpretations held. This bounded review pass is fully accounted for; it does not claim that the 342 uncertain people have been settled or admitted. The parent handles independent completion reviews.
