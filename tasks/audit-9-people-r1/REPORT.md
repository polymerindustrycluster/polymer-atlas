# Blind Audit 9 — pass-34 people creations (R1)

## Headline: 50 random people creations

**41/50 AGREE (82%); 3/50 FIELD_ERROR (6%); 0/50 confirmed CREATION_ERROR (0%); 6/50 UNRESOLVED (12%).**

Unit: unique people records drawn randomly without replacement from the **403 pass-34 creations PERSON-000074–PERSON-000476** at main **`604fea8ef1d9fe3f17049aeb053d157345a61de5`**. These are raw sample rates for the specified checks, with unresolved records retained in the denominator, not population-wide accuracy claims. Zero confirmed creation errors does **not** prove that all 403 creations are correct. No weighting, and no blending of purposive/held frames into random rates.

Independent observations were frozen at **2026-10-31 20:08:49 UTC**. The frozen initial random count was 42 agreements / 3 field errors / 5 unresolved. Independent review found that Almenar's vendor-hosted MSU-branded profile lacked an authenticated institutional-ownership bridge; its derivative grade was conservatively changed to UNRESOLVED. **The headline above includes that correction.** Original frozen observations remain byte-identical in the audit workspace; one published batch copy redacts an email-shaped URL as documented below; `DERIVATIVE_CORRECTIONS.json` records the changes and reasons.

| Frame | Unit and filter | AGREE | FIELD_ERROR | CREATION_ERROR | UNRESOLVED |
|---|---|---:|---:|---:|---:|
| Stratum 1 | 50 random pass-34 new people rows | 41 (82%) | 3 (6%) | 0 (0%) | 6 (12%) |
| Stratum 2 | 4 owner-declared judgment cases | 4 (100%) | 0 (0%) | 0 (0%) | 0 (0%) |
| Mini-frame | 7 named changes to held people rows; grade the specified correction | 6 (85.7%) | 0 (0%) | 0 (0%) | 1 (14.3%) |

PERSON-000448 (Zimmerman) appears in both strata. There are **61 frame memberships but 60 distinct audited people**. Zimmerman was researched once and included in each frame's own denominator. No replacement draw was made. The four judgment cases cannot be used as a random accuracy estimate.

## Scope and record-level deliverable

`worksheet.csv` contains one row per distinct audited person, with frame membership, the permitted claim fields, separate Gate A / Gate B / affiliation / role / duplication grades, each substantive witness URL and observed fact, a short exact operative Gate B quotation, overall grade, error fields and unresolved settling facts. Sources were independently located on current institutional sites, not copied from Atlas citations. Dates of access are 2026-10-31; source publication dates are retained in observations where relevant.

A positive Gate B finding is person-level research, not institution/department membership. The Palmer precedent is applied only after finding his own OSU laboratory's polymerized-hemoglobin research statement. Current real joint appointments are flagged rather than failed. Name normalization and held-name comparison are screens, not proof against every undiscovered alias. The source-owning institution and currentness tests remain explicit, especially for alternate hosted profiles and historical announcements.

No canonical fields are changed. Suggested fixes are for the integrator, who must recheck the then-current record and source before application.

## Confirmed random-sample field errors

| Person | Held claim | Independently observed current institutional styling | Proposed finding and witness |
|---|---|---|---|
| PERSON-000162 — Sanket A. Deshmukh | associate_professor | Full Professor and Associate Department Head | FIELD_ERROR: `role` and `role_as_published`. [Virginia Tech faculty profile](https://che.vt.edu/People/faculty/Deshmukh.html). Opened body, not stale associate-rank search snippet, governs. Polymer research and faculty gates pass. |
| PERSON-000173 — Paul Deck | professor | Associate Professor | FIELD_ERROR: `role` and `role_as_published`. [Virginia Tech faculty profile](https://chem.vt.edu/people/faculty/teaching-and-research/pdeck.html). Person-level polymer synthesis research and faculty eligibility pass. |
| PERSON-000225 — Reika Katsumata | assistant_professor | Associate Professor | FIELD_ERROR: `role` and `role_as_published`. [UMass CNS faculty profile](https://www.umass.edu/natural-sciences/about/directory/reika-katsumata). Person-level polymer research is corroborated by the current faculty body independently reopened during review and by her [May 2026 institutional research profile](https://www.umass.edu/natural-sciences/news/pse-reika-katsumata-young-scientists-award). |

The three records remain eligible people on the checked evidence; these are rank/styling discrepancies, not creation errors. Differences in university search snippets were not treated as authoritative when the opened body settled the rank.

## Random-sample unresolved cases — not errors or passes

| Person | Unsettled check | Specific fact needed |
|---|---|---|
| PERSON-000092 — Judit E. Puskas | Current faculty/profile access and current Gate B witness | An accessible current institution-owned person profile/lab body confirming the asserted professor styling and her polymer research. Historical 2024 institutional recognition supports the identity/research history, but current profile routes were JavaScript-only or blocked. |
| PERSON-000095 — Christo S. Sevov | Exact coded rank | An unambiguous current OSU rank statement resolving the lab's associate-through-2025 chronology versus distinguished-title wording and a 2025 trustee record retaining associate rank. Faculty eligibility and polymer work are supported; a distinction/award title is not automatically a promotion. |
| PERSON-000236 — John Klier | Claimed UMass affiliation and role | A current UMass appointment/leave record confirming whether UMass remains a real current affiliation alongside his positively established OU deanship/professorship. An old/currently indexed leave snippet and blocked UMass body do not settle this. OU's person-level polymer research is real but does not itself prove UMass affiliation. |
| PERSON-000318 — Alireza Abbaspourrad | Current person-level Gate B witness | An accessible current Cornell faculty/lab/profile statement explicitly tying him to polymer research. Current food/soft-materials profile and historic 2018 polymer work are not silently combined into a current polymer-work verdict. |
| PERSON-000392 — Eva Almenar | Institutional ownership of alternate profile source | An accessible institution-owned faculty/lab body, or authenticated MSU routing/crosslink establishing the vendor-hosted production profile. MSU branding and a self-declared canonical URL are corroborative, not sufficient ownership proof. No claim that its content is false. |
| PERSON-000442 — Anthony M. Waas | Current Michigan appointment / emeritus-only conflict | A current Michigan appointment record resolving an emeritus heading versus retained active/joint-role wording. Current ASU professorship and polymer-composite work do not alone prove that every Michigan appointment ended. |

All settling URLs, failed routes and positive corroboration are in the worksheet/frozen source logs. Fetch failures are availability observations, not evidence of departure, nonexistence or absence of polymer research. No CREATION_ERROR was manufactured from missing pages.

## Stratum 2 — declared judgment cases (separate n=4)

| ID / person | Overall | Gate reasoning and borderline calls |
|---|---|---|
| PERSON-000476 — Andre Francis Palmer | AGREE | OSU current faculty/lab evidence supports professor eligibility and engineering polymerized hemoglobin as the research object. Applies the 2026-10-31 Palmer class ruling, not an automatic person exemption. |
| PERSON-000448 — Paul Martin Zimmerman | AGREE | Michigan faculty styling plus his institution-hosted laboratory's authored polymer-research publications. This is a person/lab research witness, not a macromolecular center-roster inference. Also sampled randomly; overlap retained explicitly. |
| PERSON-000409 — Christopher M. Madl | AGREE | Penn faculty/appointment evidence and a substantial person-focused current research profile embedded in its July 2026 Almanac article establish hydrogel/protein-engineering work. **Borderline source format:** news-hosted profile, accepted for its explicit person-level research content, not merely an award or roster. External lab page was opened as a lead/corroboration but was not used to settle the verdict. Penn primary MSE / secondary CBE appointment is a real internal joint appointment, flagged not failed. |
| PERSON-000084 — Laura S. Bruckman | AGREE | Current CWRU faculty research and 2026–27 institutional bulletin support professor + center-director styling and person-authored polymer degradation work. |

## Mini-frame — held corrections (separate n=7)

| Person | Correction grade | Scope of agreement / remaining limit |
|---|---|---|
| PERSON-000003 — Joseph C. Furgal | AGREE | Current BGSU profile supports associate-professor styling and person-level polymer work. |
| PERSON-000041 — Maria R. Coleman | AGREE | Toledo faculty body supports professor and graduate-director styling; polymer nanocomposite research explicit. |
| PERSON-000042 — Yakov Lapitsky | AGREE | Current Toledo department page supports professor/chair styling and polyelectrolyte research. |
| PERSON-000052 — Mesfin Tsige | AGREE | Akron person profile supports professor/director styling and computational polymer research. |
| PERSON-000054 — Sadhan C. Jana | AGREE | Akron person profile supports professor/endowed-chair/research leadership styling and polymer work. |
| PERSON-000056 — Shing-Chung Josh Wong | AGREE, **downgrade only** | Opened Akron board material records resignation effective 2022-08-31, supporting the U downgrade. This is not agreement that the retained affiliation is current or that current Gates A/B were re-established. These components remain explicitly unresolved/historical in the worksheet. |
| PERSON-000060 — Xiong Gong | UNRESOLVED | UTA's institutional 2025 hiring booklet establishes a new professorship, but does not settle whether all Akron appointments ended or a joint appointment persists. Need an institutional departure or current joint-appointment record. The audit does not reverse U or promote the record; it cannot independently confirm the stated departure basis. |

## Borderline calls and limitations, separately enumerated

1. **Palmer:** binding polymerized-protein class precedent applied to an independently located OSU lab witness.
2. **Madl:** current person-specific research profile embedded in Penn Almanac accepted by content/grain; URL section alone is not the test. A residual sentence in frozen `results_batch5.json` sources[0].facts says the strict gate remained unsettled; it is superseded draft wording inconsistent with that worker's final Gate B verdict and source[1]. The final decision and basis above govern; raw text is preserved, not silently rewritten.
3. **Cheng:** August 2026 Lehigh chair article has a person-focused current appointment/research profile explicitly identifying polymer biodegradation. Accepted as an institutional person profile, not as generic departmental news.
4. **Katsumata:** May 2026 UMass person-focused research profile supported B during blind verification; independent review also opened the canonical CNS faculty body's current polymer research. Rank discrepancy remains positive.
5. **Dufresne:** Cornell LASSP research catalogue is explicitly keyed to him as author/group and contains polymer research abstracts. Accepted as person-level lab research output, not a roster. Publication dates are research evidence dates, not an inferred tenure or employment start date.
6. **Zimmerman:** authored research on his institution-hosted lab page, including polymer subjects, witnesses his work; center membership alone would not.
7. **Almenar:** post-freeze conservative UNRESOLVED on vendor-host ownership; official-route access failures and a search-index-only possible domain bridge were not promoted to verified evidence.
8. **Klier and Waas:** alternative current institutional homes do not automatically negate a genuine joint/leave affiliation at the recorded home. Conflicting evidence remains held.
9. **Sevov:** distinguished styling does not by itself prove a change in controlled academic rank; exact rank remains unresolved.
10. **Research faculty and internal joint appointments:** Jinde Zhang's institution-styled Assistant Research Professor maps to `research_professor`; Sodano/Zhang/Madl cross-department appointments are not affiliation failures. An additional center-director duty does not require every otherwise valid professor code to become `center_director_professor` without an owner rule imposing that precedence.
11. **Duplication:** all creation identities were screened against all 73 pre-pass held names/institution identities and observed name forms; mini-frame rows exclude their own ID. No positive duplicate was found. Eleven frozen batch-4 duplicate notes accidentally copied Tsige's self-exclusion wording into new-person rows; derivative wording is corrected transparently in `DERIVATIVE_CORRECTIONS.json`, with no grade change.
12. **Effort and availability:** approximately six primary pages per person was the target; some alternate failed routes pushed fetch-log entry counts higher without adding substantive witnesses. Page body, not HTTP 200, is required: challenge pages and scripts are not evidence. No currentness claim is based solely on a successful response code.
13. **Privacy:** outputs contain public professional identity/appointment/research facts and source URLs only; no individual contact field, phone or address is published. One original MIT faculty URL contained an email-shaped routing identifier. It is replaced by a non-contact placeholder in the published batch-4 copy, with original/published hashes in `PRIVACY_REDACTIONS.json`; original frozen bytes stay private. The worksheet instead cites independently reopened privacy-safe MIT J-WAFS and ISN profiles. This changes source routing/quote only, not the verdict.

## Methods and exact read order

1. Fetched Git main and resolved requested `604fea8e` to `604fea8ef1d9fe3f17049aeb053d157345a61de5`; current main matched. Read AGENTS first, then SCHEMA academic-layer §1 rulings and §4.9, then QUEUE. AGENTS people text is actually §6, not a §4.9 heading; SCHEMA supplies §4.9. The user-specific audit grammar is distinguished from AGENTS integration-lane grammar.
2. Created isolated branch/worktree and appended/committed a new queue claim, preserving every existing entry. The worktree operation printed the pass-34 commit title mentioning the Gong/Wong downgrades; this is disclosed metadata exposure, not a source witness. The user's brief already specified the held-downgrade purpose.
3. Fixed seed `2026103109` before viewing claim values. Parsed CSV in memory, selected exact new-ID range and asserted uniqueness/count. Whitelisted only name, institution identifier, role, role styling and tier; resolved institution names using legal_name only. Original cited sources, public_profile_url, research_specialties, source notes and evidence columns were never displayed or exported. The parser necessarily reads CSV bytes, but prohibited column values are discarded without agent inspection.
4. Drew 50 ascending-ID frame entries using Python `random.Random(seed).sample`; published seed, method and full ID list in `sample_manifest.json`. Appended four judgment and seven mini-frame IDs as separate memberships; did not redraw overlap. Exported held PERSON-000001–000073 names/IDs/institution identities only for duplication screening.
5. Five fresh verifier contexts each received 12 disjoint identity/claim records, the held-name list and this gate doctrine, not the wider conversation or previous evidence. They independently searched and opened current institution-owned pages. Source discovery can lead to the same URL the Atlas originally cited, but no verifier was given or read that original citation. A few external leads were opened; no verdict rests on those rather than the identified institutional witness. Short Gate B quotations and paraphrased facts were recorded with access dates/fetch failures.
6. All 60 verifier outputs were declared final and SHA-256 frozen before aggregation/review. **No Atlas row citations, R1 packet, staging material, pass-34 journal or existing evidence row was opened at any stage of this audit, including review.** No original-evidence comparison was needed.
7. Independent review reopened the three rank witnesses and selected borderline sources, reproduced the sample and counts, and inspected all frame/check completeness. It corrected Almenar's derivative source-ownership grade and the copied duplicate-screen wording through an explicit log; original raw observations and freeze hashes remain unchanged; the published privacy-redacted batch-4 copy has its own separately checked hash. Headline results use the reviewed derivative worksheet, not the preliminary freeze counts.
8. Re-ran packet checks, canonical validation, SQLite build and 37 regression tests. Confirmed no canonical data diff; changes are confined to this audit packet and its appended queue claim. Final main drift/read-back information appears below.

This audit is **evidence-blind**, not identity-, claim-, tier-, judgment-status- or correction-purpose-blind. Gate B conclusions are limited to the directly checked research claims; neither 82% agreement nor 0% confirmed creation errors should be advertised as complete record or population accuracy.

## Reproduction and source inventory

Run `python3 tasks/audit-9-people-r1/check_packet.py` on the pinned tree plus this packet. The script reproduces the seed draw, asserts 403 unique frame IDs / 50 random IDs / 60 audited identities, validates raw SHA-256 freezes, checks derivative corrections, worksheet parity and every denominator/rate. `sample.py --output-dir <scratch-directory>` regenerates only claim-whitelisted inputs and the manifest; it writes no canonical files. The final worksheet itself is the actionable findings packet.

Every source used is named with its URL, title, observed date, paraphrased witness and fetch status in the five `results_batchN.json` files. These preserve source/observation inventories (batch 4 is a documented privacy-redacted copy); unsuccessful routes are labeled. `held_names.json` is the exact 73-ID duplicate-screen input. `statistics.json` contains the reviewed raw per-frame counts/rates. `VERDICT_FREEZE.json` records the pre-review freeze; `DERIVATIVE_CORRECTIONS.json` states every worksheet deviation from frozen observations. All are public-professional facts only.

## Validation, publication and drift

- Pinned canonical validator: PASS; existing warnings retained, no new data errors.
- SQLite build: PASS.
- Regression tests: 37 passed.
- Packet/reproduction checks: PASS.
- Canonical edits, ID allocations, merges and main pushes: zero.
- Starting/audited main: `604fea8ef1d9fe3f17049aeb053d157345a61de5`.
- Final live-main check and exact remote-byte parity: recorded in `PUBLICATION.json` at publication. Any later drift is flagged, never silently absorbed into this snapshot.
