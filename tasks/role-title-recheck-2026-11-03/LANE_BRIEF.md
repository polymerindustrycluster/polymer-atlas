# Lane brief — role-title re-check (2026-11-03)

**Problem.** In these people records, `role_as_published` holds narrative or annotation
("promoted to associate professor in 2018…", "a professor in the Department of…",
`Professor" (Bioengineering…`) instead of the institution's **exact title**. SCHEMA §4.9 says
`role_as_published` is the institution's exact words, never normalized or inferred.

**Your job, per row.** Open the record's cited pages, in this order: `public_profile_url` first, then each URL in
`sources` (`;`-separated). Find the person's **title line as the institution prints it**, e.g.
"Associate Professor of Chemical Engineering" or "Professor, Department of Chemistry". Copy it
**verbatim**: no quotes, no commentary, no "per page X". If the page lists several titles, join the
ones the page itself states with "; ". Stop at the first page that gives the title.

- Only university or laboratory pages count (the person's own profile, a department directory or lab page).
  Never use news stories written in prose if a profile/directory title exists; use a news page
  only if it prints a title line for the person and nothing better loads.
- **Never invent, expand, or tidy** a title. If no page shows a clean title line, output
  `CANNOT_CONFIRM` and say why.
- If the page shows a rank different from the record's `role` (e.g. record says
  associate_professor, page says Professor), report it in `rank_note`; do not change `role` yourself.
- Effort cap: about 3 fetches per row. A failed fetch (403/404/timeout) is not evidence of anything.
- Privacy: never record emails, phone numbers or addresses.

## Output
Write ONLY `tasks/role-title-recheck-2026-11-03/lanes/<batchN>_out.csv` (UTF-8, comma, quoted as needed):
`person_id,new_role_as_published,title_url,status,rank_note`
- `status`: `CONFIRMED` (title copied verbatim from `title_url`) or `CANNOT_CONFIRM`.
- One output row per input row, same order.
Do not edit any other file, never touch `data/`, never run git.
