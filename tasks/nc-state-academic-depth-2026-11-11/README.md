# NC State academic depth pass (2026-11-11)

Owner instruction 2026-11-11: "Could we try another school next?" — the by-school scaling trial
that follows the Ohio academic depth pass (PR #269). School chosen by measured yield, not
familiarity: among universities (federal-lab pools excluded — their staff have no program grain),
NC State holds the largest unlinked people pool in the Atlas (38 people, 0 linked) and three
polymer-true program rows that are nearly empty.

## Scope (measured 2026-11-11, unit: active program rows / recorded people)

- **3 active program rows** at North Carolina State University (ORG-002851):
  PROG-000065 Polymer and Color Chemistry (Wilson College of Textiles), PROG-000118 Fiber and
  Polymer Science (Wilson College of Textiles), PROG-000147 Materials Science and Engineering
  (College of Engineering). Gap cells: 11 of 12 across the four depth fields (PCC and FPS are
  blank on all four; MSE lacks processes/materials/facilities).
- **38 people** recorded at NC State, **0** carrying `program_org_id`.

## Discipline (same as the Ohio pass)

- NC State's own pages are the citation of record (textiles.ncsu.edu, mse.ncsu.edu, and the
  university's program/catalog pages). No lead source is needed at single-school scale.
- People→program links require a **person-level witness** tying the named person to the specific
  program (a program faculty listing, a department page grouping faculty by program, a profile
  naming the program). The three programs are distinct: Textiles faculty may belong to PCC, FPS,
  or another Wilson College program (e.g. Textile Engineering, Chemistry & Science; Fashion and
  Textile Management) that the Atlas does not carry — witness to a non-Atlas program is
  NO_WITNESS for this pass, noted, never forced into the nearest row. Employment at NC State
  alone is NOT a link.
- Vocabulary fills return the institution's verbatim phrase; the integrator maps to §3.1/§3.2/§3.5.
  Characterization facilities tag `research_areas[characterization_methods]`, never specialty_*.
  `scale_band` needs a published band or a self-characterizing statement, not a raw headcount.
- A failed fetch is an availability signal, never evidence of absence. Effort cap ~6 fetches per
  program, ~3 per person.

## Deliverables (lane produces the packet; the integrator writes `data/`)

In this folder: `fills.csv` (program_id, field, proposed_value, source_url, verbatim_quote ≤25
words, source_kind), `links.csv` (person_id, program_id, verdict LINK|NO_WITNESS, witness_quote,
witness_url, source_kind), `notes.md` (borderline calls, failed fetches, suspected defects).

## Integration

One branch, one PR. Integrator applies mapped fills as cell edits with append-only evidence
rows, sets `program_org_id` on LINK-verdict people (degree program primary where a person has
several witnesses; additional witnessed programs carried as evidence rows), refreshes
`last_verified` only on changed rows, flips the Ohio QUEUE claim to done in the same PR (the
standing next-packet pattern), and lands with validate + row-loss guard green.

## Integration record (2026-11-11)

The lane returned 13 fills and 47 link rows (30 LINK verdicts covering 21 of 38 people; 17
NO_WITNESS), all resting on NC State pages, no paid calls. Applied after integrator mapping:

- **All 3 program rows changed**: PCC gained research_areas (inks_colorants_masterbatch,
  polymer_synthesis, polymer_physics) + specialty_materials (inks_colorants_masterbatch) +
  facilities_note; FPS gained research_areas (polymer_synthesis, polymer_physics,
  inks_colorants_masterbatch, biomedical_polymers) + facilities_note; MSE gained a
  facilities_note. 6 append-only evidence rows (EVD-333192..EVD-333197).
- **21 people gained `program_org_id`** (FPS 10 primary, MSE 6, PCC 5); all 30 LINK witnesses
  banked as evidence_people rows (EVD-333198..EVD-333227). Dual-witness primaries follow the
  home program (e.g. Salmon/Krause/Budhathoki-Uprety/Schroeder → PCC on the college's own
  program-grouped directory; Spontak → MSE on his department profile); the second program
  rides as an evidence row.
- Witness architecture worth noting: the FPS and MSE graduate-faculty rosters in NC State's
  own catalog did most of the linking — the catalog is the program-grain witness the Ohio
  pass usually had to find on department pages.

### Held fills (proposed, NOT applied — with reason)

- **Both scale_band facts** — FPS "close to 90 students enrolled" and MSE "$17M in research
  expenditures (2025)" are a headcount and a dollar figure, not bands; the conversion question
  is already the owner's from the Ohio pass. PCC published no size fact at all.
- **Textile wet-processing processes** (PCC and FPS specialty_processes: fiber formation,
  dyeing, finishing, chemical modification) — §3.1 has no honest slug for textile dyeing /
  finishing / fiber formation; minting one is an owner vocabulary question, proposed here —
  the same shape as the Ohio pass's liquid-crystals gap, and likely the recurring gap for
  any textiles-carrying school.
- **Generic materials phrases** — FPS specialty_materials ("polymer, fiber and materials
  science") and MSE specialty_materials ("metals, ceramics, polymers and nanomaterials"):
  program self-names and out-of-scope classes, per the Ohio pass's identical calls.
- **MSE specialty_processes** ("discovery, design, characterization and manufacturing") —
  a mission list; characterization belongs to research_areas, which MSE already carries.

### Currency flags from the lane (records not edited by this pass)

- Gorman (PERSON-000282) and Shen (PERSON-000306) appear on the 2024-2025 FPS roster and not
  the 2025-2026 one — Shen's PCC link stands on the current college directory; Gorman returned
  NO_WITNESS and his record may be going stale (emeritus/departure not asserted).
- Budhathoki-Uprety (PERSON-000305) is now styled Associate Professor on her college profile
  (recorded as Assistant); Salmon's rank differs between the college page (Professor) and the
  FPS roster (Associate Professors); Pasquinelli's profile now also appears under the College
  of Natural Resources. Title/college-home refresh is a separate look.
