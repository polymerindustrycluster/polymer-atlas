# Lane brief — census-gap researcher wave (2026-11-03)

**What this is.** Packet lanes (AGENTS.md §2 rule 7) that find polymer faculty at major US
research universities the Atlas does not yet cover. The school list comes from the PIC
faculty census's target-school list (`polymer-faculty-census/rosters/targets.json`, private).
That list is a **discovery lead only**: it is never cited, and no name, count or fact
comes from it. Every fact in your packet comes from the university's own public pages.

**You never edit `data/`.** You write only under `tasks/census-gap-people-2026-11-03/lanes/<your lane>/`.
The integrator allocates IDs and writes data files.

## Read first (5 minutes)
- `docs/SCHEMA.md` §4.9 (people records) and the "Faculty-rank line [v1.7.5]".
- `docs/SCHEMA.md` §3.5 (research-area supplement) and §3-first rule.
- `data/people.csv` — check every name against it (same person already held → mark `already_in_atlas`).

## The two gates (both must pass, both on the university's own domain)
- **Gate A — faculty styling.** The university's own page styles the person as faculty in a
  professor rank: `professor`, `associate_professor`, `assistant_professor`,
  `research_professor` (assistant/associate/full research professor), or
  `center_director_professor` (a director who also holds a stated professor title).
  Lecturers, adjuncts, emeriti, research scientists, staff scientists, research associates,
  postdocs and students **fail** Gate A at a university. Record the exact styling verbatim in
  `role_as_published`.
- **Gate B — polymer work.** The person's own profile (or their own lab/group page on the
  university domain) states polymer-specific research: polymers, macromolecules, plastics,
  rubber/elastomers, composites with polymer matrices, polymer membranes, hydrogels/polymer
  networks, polymer coatings/adhesives, polymer processing, etc. Generic "soft matter",
  "materials", "nanomaterials" or "biomaterials" without a stated polymer object **fails**.
  Polymerized-protein therapeutics pass (Palmer precedent). Quote the deciding phrase.

## Effort cap
~6 page fetches per person, ~60 per school. Prioritise the departments where polymer work
concentrates (chemical engineering, materials science, chemistry, macromolecular/polymer
programs, mechanical engineering composites groups). **Cap: 15 VERIFIED people per school**;
take the clearest polymer researchers first. A failed fetch (403, timeout, bot wall) is an
availability signal, never evidence: mark STILL_UNCERTAIN with the fact that would settle it.

## Privacy — hard line
No email addresses, phone numbers, office/home addresses, photos, CVs or personal data
anywhere in your output. If the only profile URL embeds an `@`, use the department people page instead.

## Output files (CSV, UTF-8, comma, quoted as needed)

`institutions.csv` — one row per school:
`school_key,legal_name_as_published,city,state,website,polymer_unit_name,polymer_unit_url,unit_evidence_quote,observed_date`
(`polymer_unit_*`: a **named** polymer center, institute, program or concentration on the
university's own pages, if one exists; blank if none. "Has a chemistry department" is not one.)

`people.csv` — one row per person examined:
`school_key,full_name,role,role_as_published,unit,research_specialties,public_profile_url,gate_a_url,gate_a_quote,gate_b_url,gate_b_quote,verdict,verdict_note,already_in_atlas,observed_date`
- `verdict`: exactly `VERIFIED` | `REJECT` (with the deciding fact in `verdict_note`) | `STILL_UNCERTAIN` (with the fact that would settle it).
- `research_specialties`: `;`-separated. Use §3.1/§3.2/§3.5 terms where they honestly fit
  (e.g. `polymer_synthesis;rheology;biomedical_polymers`), otherwise short phrases as the
  page states them. As stated on the page — never inferred.
- `observed_date`: today, ISO (2026-11-03).
- Quotes: ≤ 25 words, verbatim.

`NOTES.md` — 5–15 lines: pages used per school, counts (examined / VERIFIED / REJECT / STILL_UNCERTAIN), anything odd.

## Done when
Each assigned school has an `institutions.csv` row and up to 15 VERIFIED people (fewer is fine
if the school genuinely has fewer), every row has both gate URLs + quotes, and NOTES.md has counts.
