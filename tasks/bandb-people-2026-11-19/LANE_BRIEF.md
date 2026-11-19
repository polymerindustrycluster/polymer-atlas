# Lane brief: band-B faculty leads (2026-11-19)

You are a packet lane for the Polymer Atlas, a public dataset. You verify whether each lead is a current
polymer professor at the named US university. You write ONE CSV and edit nothing else.

## Input
`laneNN.json`: leads with `lead_id`, `name`, `school`, `institution_org_id`, `census_rank` and `roster_page` (a
department roster URL where the name was found). The leads come from a private faculty census. They are discovery
leads only: never cite the census, and take no fact from it. Every fact comes from the university's own pages.

## Reading pages
Read pages ONLY through the helper, which prints the raw visible text:

`python -I C:/Users/JohnSwanson/Documents/pic-github/_atlas-corpus/bandb-2026-11-19/fetch.py <url>`

Do not use WebFetch: it paraphrases, and your quotes are machine-checked word for word against the raw page. Start
from `roster_page`, then the person's own profile or lab page on the university's domain. You have about 5 fetches
per person. A failed or blocked fetch is availability, never absence: the verdict is STILL_UNCERTAIN, naming the
missing page.

## Both gates must pass, on the university's own domain
- **Gate A, current faculty rank.** The university's own page styles the person, now, as a professor:
  - `professor`, `associate_professor` or `assistant_professor`;
  - `research_professor`, for an assistant, associate or full research professor;
  - `center_director_professor`, for a director who also holds a stated professor title;
  - `senior_lecturer`.

  These fail Gate A: emeriti, adjuncts, lecturers other than senior lecturers, professors of practice, teaching
  professors, research or staff scientists, postdocs, students, and visiting titles. Copy the exact styling into
  `role_as_published`. The quote must contain the person's surname, or sit on a page that is plainly that person's
  own profile.
- **Gate B, polymer research.** The person's own profile or lab page states polymer-specific research: polymers,
  macromolecules, plastics, rubber or elastomers, polymer-matrix composites, polymer membranes, hydrogels or polymer
  networks, polymer coatings or adhesives, or polymer processing. These fail Gate B:
  - generic "soft matter", "materials", "nanomaterials" or "biomaterials" with no polymer named;
  - a department blurb, or another person's work.

  A paper title in the person's own publication list passes only if the profile states no research at all; say so in
  `verdict_note`.

## Quotes
Each quote is ONE contiguous passage copied exactly from the helper's output, 25 words or fewer, with no ellipsis.

## Privacy, a hard line
No emails, phone numbers, office or home addresses, CVs or photos anywhere. If the only profile URL contains an
`@`, use the department page.

## Output
Write `C:/Users/JohnSwanson/Documents/pic-github/_atlas-corpus/bandb-2026-11-19/out/laneNN.csv` with the Python csv
module, from a script file you create in `.../bandb-2026-11-19/workNN/`. Append one row per lead as you finish it;
every input lead gets exactly one row. The header is exactly:

`lead_id,full_name,institution_org_id,role,role_as_published,public_profile_url,gate_a_url,gate_a_quote,gate_b_url,gate_b_quote,verdict,verdict_note,observed_date`

- `full_name`: as the university's page writes it.
- `verdict`: exactly one of:
  - `VERIFIED`;
  - `REJECT`, with the deciding fact in `verdict_note` (for example "styled Professor Emeritus", "now at another
    university", "no polymer research stated");
  - `STILL_UNCERTAIN`, with the fact that would settle it.
- `observed_date`: 2026-11-19.

Before finishing, check that every input lead_id appears exactly once, and that every VERIFIED row has both URLs and
both quotes of 25 words or fewer.

Final response under 2000 characters: counts by verdict, and the rows a reviewer should look at.
