# University of Massachusetts Lowell academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 2, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?"). Research lanes run while the owner travels; integration serializes behind
the NC State / Virginia Tech / Georgia Tech PRs; pushes batch for his approval.

## Scope (measured 2026-11-12)

- **3 active program rows** at University of Massachusetts Lowell: PROG-000057 Plastics Engineering (degree), PROG-000058 Graduate Certificate in Plastics Processing (certificate), PROG-000300 Plastics Engineering Seminars (training). 15 blank depth cells across the
  five watched fields.
- **22 people** recorded at University of Massachusetts Lowell, **0** carrying `program_org_id`.

## School notes

Plastics Engineering (PROG-000057) is the flagship plastics program in the US and the
main yield here; its department faculty pages are the program tie. The certificate
(PROG-000058) and seminar series (PROG-000300) rarely publish per-person faculty ties —
absence is NO_WITNESS, never forced.

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

**Fills applied (11):** PROG-000057 research_areas += elastomer_science;
characterization_methods;recycling_circularity;biomedical_polymers (design,
mold/die, and CAE topics unmapped); specialty_processes = the five process
families from the program's own pages (bare "extrusion"/"thermoforming" at
the unspecified slugs); specialty_materials += elastomers_rubber;
polymer_additives; facilities_note; scale_band = large ("first and largest
ABET-accredited Plastics Engineering program in the U.S." — qualitative
self-characterization, S3). PROG-000058 specialty_processes (same five),
specialty_materials += elastomers_rubber, facilities_note (100% online).
PROG-000300 specialty_processes += injection_molding;
injection_molding_lsr_silicone;compounding_extrusion;extrusion_unspecified;
specialty_materials += thermoplastic_elastomers_tpe_tpu;silicones;
facilities_note.

**Held:** PROG-000058 scale_band (4 courses / 12 credits — credit hours never
convert under S3) and PROG-000300 scale_band (30+ years offered — longevity,
not size). Research areas for the certificate and the seminar program stand
blank per §4.11 (research programs only), as the packet left them.

**Links (22 witness rows banked; 14 primaries set, all PROG-000057; 8
NO_WITNESS stand):** the 8 seminar-program rows are second-program evidence
for people whose primary is the degree. Zhang's degree link stands — he is in
the department Faculty page's core Faculty list, the brief's named standard;
his Nanomanufacturing Center title line makes it the packet's weakest link,
flagged, not overruled. The certificate takes no people, as predicted.

**Carried defect, deliberately not repaired in this pass:** Hansen
(PERSON-000252) is Mechanical & Industrial Engineering faculty with no
Plastics tie (NO_WITNESS stands), and his recorded profile URL returns HTTP
410 Gone. No live Plastics-side target exists to repoint to; the defect is
recorded here for a future currency pass. Kokil's title inconsistency is
internal to UML's own pages (Associate vs Assistant Teaching Professor) — no
winner to pick; Sobkowicz's name styling ("Sobkowicz Kline") is flagged in
the packet likewise. Records untouched on both.
