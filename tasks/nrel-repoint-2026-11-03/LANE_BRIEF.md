# Lane brief — NREL people after the rename (2026-11-03)

The U.S. Department of Energy renamed the National Renewable Energy Laboratory (NREL) the **National Laboratory of
the Rockies (NLR)** on 2025-12-01 (https://www.nlr.gov/news/detail/press/2025/news-release-energy-department-renames-nrel-national-laboratory-of-the-rockies).
`nrel.gov` no longer resolves, and most old URLs (news items, report PDFs) were not carried over to the same paths on
`nlr.gov`. The Atlas holds 18 NLR research-staff records (`people_in.csv`) whose cited pages are on `nrel.gov`.

**Standard (SCHEMA §4.9, lab grain).** The laboratory's own public pages must style the person as research staff
**and** state polymer research. Only nlr.gov pages count (the person's NLR staff profile, an NLR program or
research page, an NLR news item that prints their title). A university page, LinkedIn or a paper does not.

## Per person (about 5 fetches max)
1. Find their **current NLR page**: try the NLR staff directory or profile (e.g. `https://www.nlr.gov/research/staff/...`),
   search the web for `"<full name>" site:nlr.gov`, and follow NLR program pages for their group.
2. From that page copy, **verbatim**, the title line as printed (e.g. "Senior Scientist", "Group Manager, ...").
3. Find on an NLR page the sentence that states their **polymer** work (polymers, plastics, composites, resins,
   membranes, polymer recycling, enzymes for plastics, etc.). Copy it verbatim, at most 30 words.
4. Verdict:
   - `VERIFIED`: an NLR page names them as research staff now, with a title line, and an NLR page states polymer work.
   - `STILL_UNCERTAIN`: no NLR page found or none prints a title; name the fact that would settle it.
   - `REJECT`: an NLR page shows they left or are not research staff (e.g. retired, now at another employer); quote it.
5. A failed fetch (404, 403, timeout) is never evidence of anything. Never record emails, phones or addresses.

## Output
Write ONLY `tasks/nrel-repoint-2026-11-03/lane_out.csv` (UTF-8, comma, quoted as needed, LF), one row per input row,
same order:
`person_id,verdict,title_url,role_as_published,polymer_url,polymer_quote,note`
Do not edit any other file, never touch `data/`, never run git.
