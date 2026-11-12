# Cornell University academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 2, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?"). Research lanes run while the owner travels; integration serializes behind
the NC State / Virginia Tech / Georgia Tech PRs; pushes batch for his approval.

## Scope (measured 2026-11-12)

- **3 active program rows** at Cornell University: PROG-000089 Fiber Science (degree), PROG-000090 Polymer Characterization Facility (lab_facility), PROG-000105 Materials Science and Engineering (degree). 12 blank depth cells across the
  five watched fields.
- **24 people** recorded at Cornell University, **0** carrying `program_org_id`.

## School notes

PROG-000090 is a characterization **lab facility**: its fills observe the characterization
discipline (research_areas[characterization_methods]; never specialty_*), and a person
links to it only if the facility's own page names them as its staff or leadership —
ordinary MSE/Fiber Science faculty do NOT link to the facility. Fiber Science sits in the
College of Human Ecology (Fiber Science & Apparel Design).

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

**The Graduate Field Faculty adjudication:** the 9 links stand. The witness is
the MSE department directory's own "Graduate Field Faculty" section — its
heading, placement, and the page's framing name these people as the field's
faculty; the single boilerplate sentence reading "approved for the graduate
field of Applied Physics" is judged a template carry-over from a sibling field
page, not a redefinition of the section. A stray sentence does not outweigh the
directory's own structure. Recorded here so the call is visible and reversible.

**Fills applied:** PROG-000089 research_areas += composites_mechanics;
degradation_biodegradation;biomedical_polymers;polymer_synthesis (mapped from
the field's own topic list) + specialty_processes += fiber_formation (the v1.13
term; the field's "electrostatic technique for fiber spinning"). PROG-000090
research_areas += characterization_methods (the sanctioned facility tag).
PROG-000105 facilities_note as proposed.

**Fills held:** PROG-000089 specialty_materials ("fibrous materials" — no §3.2
slug names the class honestly); PROG-000105 specialty_processes +
specialty_materials (program-general MSE lists; the school's polymer depth
rides on its people links and the Fiber Science row) and scale_band ("some 40
faculty" — a faculty count never converts under S3).

**Links (19 witness rows banked; 17 primaries set; 7 NO_WITNESS stand):**
Fiber Science primaries for its home faculty (Uyar, Shepherd, Joo), MSE banked
for Uyar; Ober → MSE primary (he chairs it), Fiber Science banked. The
facility row PROG-000090 takes no people (its only named staff is not a pool
record).

**Title fixes (P1 rider, first applications):** Yeo PERSON-000325 →
Associate Professor (the MSE directory's current styling, quoted in links.csv);
Ober PERSON-000313 → "Chair of the Department of Materials Science and
Engineering; Francis Norwood Bard Professor of Metallurgical Engineering"
(the record's "Francis Bard Professor of Materials Engineering" had drifted
in both the chair's name and the field's). Each fix carries its own evidence
row from the witnessing directory page.
