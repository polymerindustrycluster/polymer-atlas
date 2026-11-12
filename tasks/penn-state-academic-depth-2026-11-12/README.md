# Pennsylvania State University (University Park) academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 3, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?" / burn remaining capacity on verified data before his limit reset).
Research lanes run while the owner travels; integration serializes behind waves 1-2;
pushes batch for his approval.

## Scope (measured 2026-11-12)

- **1 active program row(s)** at Pennsylvania State University (University Park): PROG-000037 Polymer Science Minor (course-type record). 5 blank depth cells across
  the five watched fields.
- **18 people** recorded at Pennsylvania State University (University Park), **0** carrying `program_org_id`.

## School notes

The Atlas carries exactly one Penn State program row — an undergraduate **minor**. Most of
the 18 recorded people are research faculty whose program tie, if published, runs through
the Materials Research Institute (MRI) or the Huck Institutes rather than a degree
program the Atlas carries. A witness to MRI/Huck membership alone is NOT a link to the
minor; return NO_WITNESS and name the actual affiliation in notes.md. Do not create
program rows — discovery is out of scope for this pass; flag the gap in notes.md so the
integrator can queue it.

## Discipline (same as the Ohio, NC State, VT, GT and wave-2 passes)

- The institution's own pages are the citation of record (department, program, and center
  pages; catalog pages where they carry program-grain rosters — check the catalog and
  program faculty listings FIRST: in the NC State and UMass Amherst passes a single
  published roster carried most links).
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

**Fill applied (1):** PROG-000037 research_areas += polymer_synthesis;
polymer_physics, from the minor's own bulletin description ("the synthesis,
processing, structure, and properties of polymer materials").

**Held:** specialty_processes and specialty_materials — the packet's
proposals are course titles inside the minor's curriculum ("Rheology and
Processing of Polymers"; "Sustainable & Recyclable Polymers"), not program
specialty statements; the same posture as Michigan State's MSE 370 course
title. scale_band — "20 credits" is a curriculum fact and never converts
under S3.

**Links: 0 of 18 — the honest gap measurement.** The Polymer Science Minor
publishes no faculty roster; its only named person (advising contact R.
Allen Kimel) is not a pool record. No pool person was forced into a program
the institution does not tie them to. The lane's discovery inventory
(MatSE ~10, ChemE 3, Chemistry 1, with the MRI directory page-verifiably
listing three of them) is banked in notes.md as the worklist for the
program-row candidates below.

**Not created here (owner ruling required):** the lane names three
program-row candidates — the MatSE Intercollege Graduate Degree Program,
an MRI center row, and Behrend's Polymer Engineering and Science B.S.
Creating program rows is discovery work beyond this pass's claim.

**Campus-grain defect — recorded, not repaired:** Rhoades (PERSON-000765)
and Xiaoshi Zhang (PERSON-000777) are Penn State Behrend (Erie) faculty;
Mathers is New Kensington. All three are recorded under the University Park
institution row. There is no Behrend institution/program row to re-home
them to, and creating one is the same owner ruling as the Behrend
candidate above — the repair rides that decision rather than stranding
three people on an institution row invented inside a depth pass.
