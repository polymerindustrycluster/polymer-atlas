# University of Michigan academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 2, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?"). Research lanes run while the owner travels; integration serializes behind
the NC State / Virginia Tech / Georgia Tech PRs; pushes batch for his approval.

## Scope (measured 2026-11-12)

- **2 active program rows** at University of Michigan: PROG-000062 Macromolecular Science and Engineering (degree), PROG-000102 Materials Science and Engineering (degree). 9 blank depth cells across the
  five watched fields.
- **21 people** recorded at University of Michigan, **0** carrying `program_org_id`.

## School notes

Macromolecular Science and Engineering (PROG-000062) is an interdisciplinary graduate
program; its published participating / affiliated faculty listings are the program tie.
The MSE department roster ties to PROG-000102. A person witnessed on both returns both
rows.

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

**Fills applied (6):** PROG-000062 research_areas += polymer_synthesis;
polymer_physics;biomedical_polymers (the master's-page topic list; "polymer
mechanics" and "plastic and organic electronics" unmapped);
specialty_processes += polymerization only (the core-course sentence's
"synthesis" mapped; characterization/rheology are methods, "processing"
generic); facilities_note; scale_band = medium (50 graduate students, S3 —
the 37 affiliated faculty in the same sentence never convert). PROG-000102
facilities_note; scale_band = large (138 students pursuing MSE degrees, S3;
the "oldest and largest" self-characterization agrees).

**Held:** PROG-000062 specialty_materials ("synthetic and natural
macromolecules" — program-general) and PROG-000102 specialty_processes /
specialty_materials (the bulletin sentence is the department's generic
self-description across all materials classes). Held fills stay banked in
fills.csv.

**Links (25 witness rows banked; 17 primaries set; 4 NO_WITNESS stand):**
eight people are dual-witnessed — the Macro roster's appointment strings
name both carried programs, or a person's own Michigan page does. For duals,
the primary is the FIRST of the two carried programs named in the
appointment string: MSE primary for Sodano, Glotzer, Kotov, Pena-Francesch,
Laine; Macro primary for Lahann, Gong, Ma. (Verifier correction, 2026-11-12:
the first draft of this sentence transposed Laine and Ma; the built data
followed the first-named rule correctly in both cases — Laine's string names
Materials Science and Engineering first, Ma's names Macromolecular Science
and Engineering before the exact MSE string.) Larson's Macro link stands on his
ChE profile's Experience block (the packet's weakest; a person-level witness
on the institution's own pages). The packet's restraint calls stand: Tuteja
takes no Macro row (title claim without a roster witness), Kim takes no
Macro row (a staging-domain claim is not a citation).

**P1 title fix:** Loebel (PERSON-000457) — the record's "Assistant Professor
of Materials Science and Engineering" is stale; MSE's Adjunct Faculty page
styles her "Adjunct Professor". role set to professor (the published rank;
the controlled vocabulary has no adjunct value) and role_as_published to the
verbatim styling, with its own evidence row.
