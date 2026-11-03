# Lane brief: rank re-check (2026-11-03)

For each person, an earlier lane read a page whose printed rank disagrees with the record's `role`.
Example: the record says `associate_professor` and the page says "Professor".
Your job is to settle the rank from the person's **current official pages**.

## Per row
1. **Open the pages, about 4 fetches max.**
   - Start with `earlier_lane_url`, `public_profile_url` and `sources`.
   - Then try the department's current faculty directory on the same university or lab domain.
2. **Find the current title line as printed.** Note anything that dates the page: "updated 2025", a news date, a CV year.
3. **Decide:**
   - `UPDATE`: two current official pages agree on a rank that differs from `record_role`. One page is enough only if it is the person's own current directory profile and shows no sign of being stale. Give `new_role` from the vocabulary below and `new_role_as_published`, the verbatim title line.
   - `KEEP`: the record's rank is right. For example, the disagreeing page is stale or is a news item about an earlier rank, while a current page agrees with the record.
   - `CANNOT_CONFIRM`: pages conflict or will not load. Say which fact would settle it.
4. **Rank vocabulary (SCHEMA §4.9):**
   - University ranks: `professor` | `associate_professor` | `assistant_professor` | `research_professor` (assistant, associate or full research professor) | `center_director_professor` | `senior_lecturer`.
   - Lab staff: keep the lab's own value family, such as `research_scientist`, `staff_scientist` or `senior_scientist`.
   - "Professor of Practice", "Industry … Professor", adjunct and emeritus titles are **not** a professor rank. Report them as `CANNOT_CONFIRM` with a note; do not map them.
5. **Rules:** copy titles verbatim; never invent. A failed fetch is not evidence. Record no emails, phones or addresses.

## Output
Write only `tasks/role-rank-recheck-2026-11-03/lanes/batch<N>_out.csv` with these columns:
`person_id,verdict,new_role,new_role_as_published,url_1,url_2,note`
Include one row per input row. Do not edit anything else, do not touch `data/`, and do not run git.
