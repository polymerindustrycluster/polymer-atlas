# NREL people after the rename: re-verification packet (2026-11-03)

> **RULED 2026-11-03: B-NLR-1 (a) and B-NLR-2 (a), as recommended** (repo owner, in session). Applied by
> `build_nrel.py` → `edits.csv`: 59 cell edits across the 18 people records (all in `data/people.csv`).
> - The 9 VERIFIED records are re-pointed to their NLR profile, with the printed title and `role` kept. The
>   exception is PERSON-000646, which moves to `senior_scientist`.
> - The 9 STILL_UNCERTAIN records go B → U.
> - On all 18, live same-path citations are re-pointed to `nlr.gov`.
> - On the 9 VERIFIED, dead citations are dropped. The 9 U records keep theirs, because they are those records'
>   only sources.

Two owner rulings were needed before the integrator applied anything (AGENTS.md §2 rule 9).

## What changed at the lab
The U.S. Department of Energy renamed the National Renewable Energy Laboratory the **National Laboratory of the
Rockies (NLR)** on 2025-12-01:
- NLR news release, https://www.nlr.gov/news/detail/press/2025/news-release-energy-department-renames-nrel-national-laboratory-of-the-rockies
- DOE release, https://www.energy.gov/cmei/articles/energy-department-renames-nrel-national-lab-rockies

The organization record ORG-002815 already carries the new name and website. `nrel.gov` no longer resolves.

The 18 people records under ORG-002815 cite `nrel.gov` news items and report PDFs (19 URLs, `url_map.csv`):
- 5 still load at the same path on `nlr.gov`;
- 14 are gone at both `nlr.gov` and `docs.nlr.gov`.

## Re-verification (`lane_out.csv`, `raw_check.csv`)
One Sonnet lane looked for each person's current NLR page (`LANE_BRIEF.md`). NLR's staff profiles live on
`research-hub.nlr.gov`. Every title and polymer quote the lane reported was then re-checked on the **raw** page with
the NAS Firecrawl. A full-page fetch was needed for titles, because NLR prints the job title in the page header.

| Lane verdict | People records | Raw check |
|---|---:|---|
| VERIFIED (NLR page styles them as research staff and states polymer work) | 9 | 9 of 9 titles and polymer quotes found verbatim |
| STILL_UNCERTAIN | 9 | see below |
| REJECT | 0 | |

The 9 STILL_UNCERTAIN:
- 4 have no NLR staff profile (unlinked authors only; one only a 2022 news item that says "postdoctoral researcher");
- 3 have a profile that prints a research title but no sentence stating polymer work;
- 2 have a profile that prints a non-research title ("Postdoctoral Liaison Coordinator…", "Laboratory Program
  Manager I-Partnership Development…").

## Owner battery (multiple choice; recommendation first)

**B-NLR-1. NLR prints grade titles that are not the Atlas lab vocabulary**, e.g. "Researcher VI-Chemistry, Materials
Science", "Senior Research Fellow II-Polymer Science…", "Manager & Distinguished Member of Research Staff…". For the 9
VERIFIED records:
- **(a) Recommended:**
  - re-point `public_profile_url` and the dead `sources` to the NLR pages;
  - set `role_as_published` to NLR's printed title, verbatim;
  - **keep** each record's `role`, because a grade title has no rank word. This is the same as the KEEP precedent in
    `tasks/role-rank-recheck-2026-11-03/` for named chairs without a rank word.
  - The one exception is where the printed title is itself a vocabulary rank that differs: PERSON-000646 prints
    "Senior Scientist" against `research_scientist`, so it becomes `senior_scientist`.
- **(b)** Re-point and set titles as in (a), and re-fold every `role` by the documented folds ("researcher" →
  `research_scientist`, and so on). Several records drop a level on a title-format change.
- **(c)** Hold all 18 until a dated vocabulary revision adds NLR's grade titles.

**B-NLR-2. The 9 STILL_UNCERTAIN records**, whose cited pages are gone:
- **(a) Recommended:** set `verification_tier` to U (SCHEMA §4.9: "a vanished/changed profile downgrades the record
  to U"). Keep the records, and list the settling fact for each.
- **(b)** Leave them unchanged until a later re-check.
- **(c)** As (a), and also queue the 2 non-research-title records for removal review under the lab-grain gate.

## Files
- `url_map.csv`: old → `nlr.gov` same-path check
- `people_in.csv`: lane input
- `LANE_BRIEF.md`
- `lane_out.csv`: lane verdicts, NLR title and polymer URLs and quotes
- `raw_check.csv`: raw-page verbatim check
