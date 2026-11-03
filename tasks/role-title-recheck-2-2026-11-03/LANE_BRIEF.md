# Lane brief — role-title re-check, wave 2 (2026-11-03)

Wave 1 (`tasks/role-title-recheck-2026-11-03/`) could not confirm these people's titles, mostly because hosts were
blocked or rate-limited from the cloud. This wave runs from the owner's laptop.

**Problem.** In these people records, `role_as_published` holds narrative or annotation instead of the institution's
**exact title**. SCHEMA §4.9 says `role_as_published` is the institution's exact words, never normalized or inferred.

**Your job, per row.** Open the record's cited pages, in this order: `public_profile_url` first, then each URL in
`sources` (`;`-separated). Find the person's **title line as the institution prints it**, e.g.
"Associate Professor of Chemical Engineering" or "Professor, Department of Chemistry". Copy it **verbatim**: no
quotes, no commentary, no "per page X", and not the person's name. If the page lists several titles, join the ones
the page itself states with "; ". Stop at the first page that gives the title.

- Only university or laboratory pages count (the person's own profile, a department directory or lab page). Use a
  news page only if it prints a title line for the person and nothing better loads.
- **Only the record's own cited pages count.** A title found on any other page cannot be applied; if the cited
  pages fail, output `CANNOT_CONFIRM` and name the page that would settle it in `rank_note`.
- **jhu.edu and columbia.edu** block ordinary fetches (403). For a cited page on those domains, read it with the
  Tavily extract tool (`mcp__tavily__tavily_extract`, one URL per call), then copy the title from that page text.
  Use Tavily for nothing else.
- Skip cited URLs on **nrel.gov**: the domain no longer resolves (a separate packet re-points them).
- **Never invent, expand, or tidy** a title. If no cited page shows a clean title line, output `CANNOT_CONFIRM` and
  say why.
- If the page shows a rank different from the record's `role` (e.g. the record says associate_professor, the page
  says Professor), report it in `rank_note`; do not change `role` yourself.
- Effort cap: about 3 fetches per row. A failed fetch (403/404/timeout) is not evidence of anything.
- Privacy: never record emails, phone numbers or addresses.

## Output
Write ONLY `tasks/role-title-recheck-2-2026-11-03/lanes/<batchN>_out.csv` (UTF-8, comma, quoted as needed, LF
line endings):
`person_id,new_role_as_published,title_url,status,rank_note`
- `status`: `CONFIRMED` (title copied verbatim from `title_url`) or `CANNOT_CONFIRM`.
- One output row per input row, same order. Read the whole input file first; there are 25 rows (fewer in the last
  batch).
Do not edit any other file, never touch `data/`, never run git.
