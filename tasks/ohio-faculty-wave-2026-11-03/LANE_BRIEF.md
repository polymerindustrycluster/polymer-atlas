# Lane brief — Ohio faculty wave (2026-11-03)

**What this is.** Packet lanes (AGENTS.md section 2 rule 7) that check a list of Ohio university people whose names
came from a public expert directory used **only as a discovery lead**. That directory is never cited. Your input CSV
gives `name`, a `title_hint` and `institution`. These are hints only. Every fact you record comes from the
university's own public pages. Many candidates matched only on a publication title, so expect many REJECTs:
that is fine and correct.

**You never edit `data/`.** You write only under `/tmp/claude-0/-home-user/bb4f739a-dbf8-595a-877b-096d27d4d6d9/scratchpad/ohwave/lanes/ (your file names are given in your prompt)`.
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
About 3 page fetches per person: their own faculty profile on the university domain first, then their lab page.
Work through every input row. There is no per-school cap. A failed fetch (403, timeout, bot wall) is an
availability signal, never evidence: mark STILL_UNCERTAIN with the fact that would settle it.

## Privacy — hard line
No email addresses, phone numbers, office/home addresses, photos, CVs or personal data
anywhere in your output. If the only profile URL embeds an `@`, use the department people page instead.

## Output files (CSV, UTF-8, comma, quoted as needed)

`people.csv` — one row per person examined:
`institution,full_name,role,role_as_published,unit,research_specialties,public_profile_url,gate_a_url,gate_a_quote,gate_b_url,gate_b_quote,verdict,verdict_note,already_in_atlas,observed_date`
- `verdict`: exactly `VERIFIED` | `REJECT` (with the deciding fact in `verdict_note`) | `STILL_UNCERTAIN` (with the fact that would settle it).
- `research_specialties`: `;`-separated. Use §3.1/§3.2/§3.5 terms where they honestly fit
  (e.g. `polymer_synthesis;rheology;biomedical_polymers`), otherwise short phrases as the
  page states them. As stated on the page — never inferred.
- `observed_date`: today, ISO (2026-11-03).
- Quotes: ≤ 25 words, verbatim.

`NOTES.md` — 5–15 lines: pages used per school, counts (examined / VERIFIED / REJECT / STILL_UNCERTAIN), anything odd.

## Done when
Every input row has exactly one output row (VERIFIED, REJECT or STILL_UNCERTAIN). Every VERIFIED row has both gate URLs
and quotes. NOTES.md has the counts.
