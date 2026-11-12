# University of Massachusetts Amherst academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 2, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?"). Research lanes run while the owner travels; integration serializes behind
the NC State / Virginia Tech / Georgia Tech PRs; pushes batch for his approval.

## Scope (measured 2026-11-12)

- **2 active program rows** at University of Massachusetts Amherst: PROG-000059 Polymer Science and Engineering (degree), PROG-000100 Materials Science and Engineering (degree). 10 blank depth cells across the
  five watched fields.
- **26 people** recorded at University of Massachusetts Amherst, **0** carrying `program_org_id`.

## School notes

Polymer Science and Engineering (PROG-000059) is a standalone department — one of the
oldest dedicated polymer programs in the US — and its faculty directory is the program tie
for its people. MSE (PROG-000100) is an interdisciplinary program spanning departments;
its published program faculty / affiliate listings are the tie there. A person witnessed
on both returns both rows.

## Discipline (same as the Ohio, NC State, VT and GT passes)

- The institution's own pages are the citation of record (department, program, and center
  pages; catalog pages where they carry program-grain rosters).
- People→program links require a **person-level witness** tying the named person to the
  specific program (a program faculty listing, a department page grouping faculty by
  program, a profile naming the program). Employment at the institution or in a home
  department alone is NOT a link.
- Vocabulary fills return the institution's verbatim phrase; the integrator maps to
  §3.1/§3.2/§3.5. Characterization facilities tag `research_areas[characterization_methods]`,
  never specialty_*. `scale_band` needs a published band or self-characterizing statement,
  not a raw headcount or dollar figure.
- A failed fetch is an availability signal, never evidence of absence. Effort cap ~6 fetches
  per program, ~3 per person.

## Deliverables (lane produces the packet; the integrator writes `data/`)

In this folder: `fills.csv` (program_id, field, proposed_value, source_url, verbatim_quote
≤25 words, source_kind), `links.csv` (person_id, program_id, verdict LINK|NO_WITNESS,
witness_quote, witness_url, source_kind), `notes.md` (borderline calls, failed fetches,
suspected defects).

---

## Integration record (integrator, 2026-11-12)

**Fills applied:** PROG-000059 research_areas += polymer_physics;polymer_synthesis;
biomedical_polymers;sustainable_feedstocks, mapped from the department's own theme
names (Polymer and Soft Matter Physics; Macromolecular Synthesis & Materials
Chemistry; Materials for Life & Lifelike Systems; Materials for Sustainable
Resources & Energy — "Materials for Next-Generation Manufacturing" and "Polymer
Materials Engineering" carry no honest slug and stay unmapped); facilities_note as
proposed; scale_band = large (the department's own "one of the largest academic
centers for polymer research in the world" — qualitative self-characterization,
S3). PROG-000100 research_areas += polymer_physics (the program's soft-matter
field; the remaining fields are program-general) + facilities_note as proposed
(an honest structural note: the interdisciplinary program has no dedicated
facility). Specialty fields for both programs stand blank as the packet left
them — the pages publish themes, not process/material taxonomies.

**Links (26 witness rows banked; 24 primaries set; 2 NO_WITNESS stand):** Perry →
MSE primary (her PSE tie is an adjunct listing; the MSE IDGP roster is a core
program roster; her tenure home, Chemical Engineering, is not a carried program),
PSE banked. Granick → PSE primary (full PSE faculty), MSE banked. Hu's PSE link
stands (Research Professors and Lecturers section of the department's own Faculty
Listing; the packet's weakest, flagged, not overruled). Winter and Klier stand
NO_WITNESS.
