# People dedupe — Miguel Modestino (2026-11-11)

**Verdict: DUPLICATE_OF.** PERSON-001260 is the same person as PERSON-001187; it is merged into the
older record and its id retired, never reused (owner decision 2026-11-03; AGENTS §3). Declared in this
folder's `REMOVALS.csv`; logged in `data/inclusion_log.csv`; executed by this folder's `build.py` on the
PR #260 pattern.

**Lead:** the ORCID pass 2 dedupe screen (`tasks/people-orcid-2-2026-11-11/`): same normalized name,
same institution. Neither record carries an ORCID iD, and no identifier, engagement, or evidence row
references either id — the merge touches `people.csv` plus one appended evidence row and one
inclusion_log row.

## The two records

| field | PERSON-001187 (kept) | PERSON-001260 (removed) |
| --- | --- | --- |
| full_name | Miguel Antonio Modestino | Miguel Modestino |
| institution | ORG-004705 (NYU) | ORG-004705 (NYU) |
| role_as_published | "professor of chemical and biomolecular engineering at NYU Tandon" (news style) | "Director, Sustainable Engineering Initiative; Donald F. Othmer Professor of Chemical Engineering" |
| public_profile_url | an NYU news article | his NYU Tandon faculty page |
| research_specialties | *(empty)* | polymers; electrochemistry; energy storage |
| verification_tier / last_verified | A / 2026-11-02 | A / 2026-11-03 |

## Merge

- Survivor PERSON-001187 stays at ORG-004705 (no re-homing) and keeps the fuller name form; the faculty
  page styles him "Miguel A. Modestino", consistent with it.
- Survivor takes the faculty page as `public_profile_url`, the specialties from 001260, and the union of
  both records' `sources` (faculty page first).
- Title refreshed from the faculty page as read 2026-11-11: the page now styles him "Sustainable
  Engineering Initiative Director and **Associate Professor** of Chemical and Biomolecular Engineering"
  (001260's recorded Othmer-chair styling is stale), so `role` becomes `associate_professor` and
  `role_as_published` the page's current words. `last_verified` 2026-11-11; tier stays A.
- One evidence row (EVD-333029, parent claim, own_site, supports_A) records the merge on the survivor.
