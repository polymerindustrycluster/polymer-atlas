# Wave 3 — Southern Miss lane packet (2026-11-12)

Packet only. No repo data edited, nothing pushed. Data read from
`~/workspace/atlas-p2-2026-11-12/data/` (== main `f2c7c814`).
Institution: University of Southern Mississippi, ORG-002848.
Program in scope: PROG-000060, School of Polymer Science and Engineering
(degree; bs;ms;phd; CIP 14.3201) — the institution's only carried program row.

## Counts (unit + filter)

- **Programs treated:** 1 program row (PROG-000060, active, at ORG-002848).
- **Depth cells** (the 5-cell convention: research_areas, specialty_processes,
  specialty_materials, facilities_note, scale_band): **0/5 filled before →
  2/5 proposed filled** (research_areas, facilities_note); 1 held
  (scale_band); 2 adjudicated no-fill (specialty_processes,
  specialty_materials — see adjudications).
- **People in scope:** 11 people records at ORG-002848 with `program_org_id`
  empty at f2c7c814 (PERSON-000459…PERSON-000469). **Verdicts: LINK 11,
  NO_WITNESS 0** — all to PROG-000060 (the school's degree program; the
  degree-primary rule is automatic, it is the only row at the institution).
- **Stale-title flags:** 0 of 11. Every recorded role matches the rank USM
  currently publishes for that person, verbatim in rank (directory read
  2026-11-12; Ma via the Provost page below).
- **Proposed new program rows:** 0 (`proposed_rows.csv` omitted per brief).
- **Fetches:** 5 primary usm.edu pages (school page, faculty directory,
  Provost 2026 Award Winners, Graduate Programs page, Nazarenko profile)
  + 2 web searches used for discovery only. **Paid calls: 0.**

## Fills (fills.csv)

### research_areas — 11 terms, term-by-term witnesses

All terms are §3.5 supplement or §3.2 materials, which `research_areas`
accepts; no §3.1 process term honestly fits a stated school research area
(Stevens' "Controlled Radical Polymerization" is carried as
`polymer_synthesis`, the §3.5 term designed for it — not double-tagged as
`polymerization`).

| Term | Witness (usm.edu) |
|---|---|
| `polymer_physics` | Directory: Gu "Polymer physics", Qiang "Polymer Engineering and Physics"; Graduate page: "polymer physical chemistry" |
| `polymer_synthesis` | Directory: Patton "Polymer synthesis", Stevens "Controlled Radical Polymerization", Collier/Clemons "Polymer Chemistry"; Graduate page: "polymer synthetic chemistry" |
| `characterization_methods` | Directory: Gu "X-ray scattering, Neutron scattering" |
| `thermosets` (§3.2) | Directory: Patton "polymer thermosets" |
| `sustainable_feedstocks` | Directory: Patton "biobased polymers"; McNair "High performance polymer systems from sustainable resources"; Rawlins "Biomass" |
| `recycling_circularity` | Directory: Qiang "Sustainability and Circular Economy"; Rawlins "Polymer Circularity"; Stevens "Depolymerization" |
| `biomedical_polymers` | Directory: Clemons "Biomaterials"; Stevens "Nucleic Acid Delivery" (corroborated by unrecorded faculty Broadhead, "Polymers with biomedical and personal care applications") |
| `composites_carbon` (§3.2) | Directory: Wiggins "Polymer Matrix Carbon Fiber Reinforced Composite Science and Engineering"; McNair "carbon-carbon composites" |
| `composites_mechanics` | Directory: McNair "Tuning thermal and mechanical performance of carbon-carbon composites"; Wiggins composite science |
| `coatings` (§3.2) | Directory: Rawlins "Surface Coatings, Corrosion Control" |
| `membranes_separations` | Nazarenko profile: "a broad range of transport related phenomena, gas diffusion and permeation, probing of free volume" |

Considered and **not** tagged: `coating_formulation` (the directory states
"Surface Coatings," not formulation — never inferred); `elastomer_science`,
`rheology`, `additive_manufacturing_science`, `liquid_crystals` (not stated
on any usm.edu page fetched); `degradation_biodegradation` (Stevens'
depolymerization is recycling-directed, carried under
`recycling_circularity`). Boran Ma's "multiscale modelling and
machine-learning design of polymeric materials" has **no §3 term** —
out-of-vocabulary, noted here, not tagged.

### facilities_note — PSRC only

"Housed in the Thames Polymer Science Research Center (202 Thames PSRC),
Hattiesburg campus." — the school's own contact block (school page; the
same block closes the Graduate Programs page). The detailed instrumentation
list is HELD (below), so this cell carries only what usm.edu states.

## Holds (out-of-evidence, with verbatim quotes)

1. **scale_band — HELD.** USM's own job-posting boilerplate states:
   "SPSE is home to ~90 undergraduate and ~70 graduate students; it offers
   polymer science and engineering degrees at the B.S. (ABET accredited),
   M.S., and Ph.D. levels." (~160 total enrollment would convert to
   `large` under the v1.13 S3 rule.) But every copy of that text found this
   pass sits on third-party job-board mirrors (scholarshipdb.net,
   jobs.world.edu), not on a usm.edu page, so it cannot witness a fill.
   The 2026 postings' "SPSE comprises 13 faculty members" is a faculty
   count and never converts; "one of the largest polymer-focused graduate
   programs in the country" is a comparative claim, likewise mirror-only.
   **Settling witness:** the enrollment figure or an equivalent size
   self-characterization on a usm.edu page (the live posting in USM's own
   careers portal, or an SPSE fact sheet).
2. **facilities instrumentation detail — HELD.** Same boilerplate:
   "The Thames Polymer Science Research Center provides state-of-the-art
   facilities for polymer research, including NMR (400/600 MHz), TEM,
   SAXS/WAXS, XPS/UPS, polymer processing (extrusion/injection molding),
   composite fabrication, and advanced thermal, rheological, and
   mechanical characterization tools." Mirror-only provenance, as above.
   **Settling witness:** the same statement on a usm.edu page. If it lands,
   it also supplies the school's only stated processing processes
   (extrusion / injection molding) — as facilities, not specialties.

## Adjudications — no-fill cells

- **specialty_processes — no fill.** No §3.1 process is claimed as a
  program specialty on the school's own pages; the Graduate Programs page's
  "polymer engineering" is program-general and is held, per the
  generic-phrase rule. The only process nouns on usm.edu pages fetched are
  research-area statements (carried in research_areas).
- **specialty_materials — no fill.** SPSE is a generalist polymer school;
  its own pages single out no material family as the program's specialty.
  Faculty-level materials (thermosets, carbon composites, coatings) are
  carried in research_areas instead of being promoted to program
  specialties.
- **No new program rows proposed.** Two candidates were tested against
  §4.11 and rejected at lane level:
  - *EPSCoR Graduate Fellowship Program in Polymer Research (EGFP)* —
    named on the school page and given its own page, and already named in
    PROG-000060's integration note. But it is a fellowship (a funding
    mechanism for the school's graduate students), grants no credential,
    and no §4.11 `program_type` fits it. Not proposed.
  - *Thames Polymer Science Research Center as `lab_facility`* — on the
    usm.edu pages fetched, the PSRC is presented as the school's home
    building, with no separate public characterization-service offer
    stated; it fails §4.11 prong (c) on this evidence. Re-test if a
    usm.edu facilities/services page surfaces (same settling witness as
    Hold 2).
- The single-row structure stands: the B.S./M.S./Ph.D. are one named
  school with one row, matching the degree grain in programs.csv (contrast
  a school that names distinct centers — none are presented here).

## Links (links.csv) — notes per person

Witness for 9 of 11 is the USM faculty directory's SPSE listing (read
2026-11-12), which styles each person with current rank, school, and
Areas of Expertise — Gate A (current faculty styling) and Gate B
(person-level polymer-research witness) on one institution page.

- **PERSON-000462 Nazarenko** — witnessed on his individual profile page
  instead (stronger): "Full Professor" at SPSE; research stated verbatim
  (transport phenomena, gas diffusion and permeation, free volume,
  flammability). His directory expertise line is generic ("Polymer Science
  and Engineering"), which is why the profile is the cited witness.
- **PERSON-000465 Wiggins** — directory styles him "Jeff Wiggins,"
  Professor; the record's "Jeffrey S. Wiggins" is the same person (the
  directory's own contact line is Jeffrey.Wiggins@usm.edu).
- **PERSON-000460 Qiang** — directory witness, corroborated twice more on
  usm.edu: Provost page ("Graduate Mentor of the Year… Associate
  Professor, School of Polymer Science and Engineering") and the Graduate
  Programs page (named Graduate Recruiting Contact).

### Weakest link

- **PERSON-000464 Boran Ma — LINK, flagged.** He does **not** appear in
  the faculty-directory keyword listing for the school as fetched this
  pass. He is instead witnessed on the Provost's 2026 Award Winners page
  (usm.edu): "Boran Ma, Ph.D. — Assistant Professor, School of Polymer
  Science and Engineering," as a Nina Bell Suggs Endowed Professorship
  recipient — current-faculty styling (Gate A) dated 2026, matching his
  recorded `role_as_published` verbatim. Gate B rests on his recorded
  research specialties, whose source (his lab site) is already in the
  record. The directory absence is treated as a listing artifact, **not**
  departure evidence; it is flagged here as a currency item for a future
  pass, and this is the link a verifier should check first.

## Census flags (outside lane scope — integrator awareness only)

- The current directory lists two SPSE faculty with **no people record**:
  Heather Broadhead (Associate Teaching Professor; biomedical/personal-care
  polymers, surface modification) and Brian Olson (Assistant Teaching
  Professor; no expertise stated). Both are teaching-track; whether
  teaching professors pass Gate A is an integrator/owner call — flagged,
  not proposed.
- Five emeritus faculty (Mathias, McCormick, Morgan, Otaigbe, Storey) are
  listed and correctly unrecorded under the emeritus rule.
- The school is actively hiring (tenure-track Assistant Professor and a
  Professor of Practice, both for August 2027, per the mirrored postings) —
  expect the census to move.

## lab_url

No new lab_url was verified inside this pass's fetch cap, with one
exception already latent in the data: PERSON-000464 Ma's existing
`public_profile_url` **is** his lab site (maresearchlab.com, already in his
record's sources) — the integrator may copy it to `lab_url` on that
witness. Other SPSE group sites (Gu, Patton, Qiang, Collier…) were not
fetched; a lab_url sweep for this school remains undone, stated plainly
rather than papered over.

## Sources fetched (all 2026-11-12)

1. https://www.usm.edu/polymer-science-engineering/ — ABET-accredited
   B.S. stated; EGFP home; PSRC address block.
2. https://www.usm.edu/faculty-directory/?keyword=School+of+Polymer+Science+and+Engineering
   — 17 people listed (12 current-rank faculty incl. 2 teaching-track,
   5 emeritus); ranks + Areas of Expertise per person.
3. https://www.usm.edu/provost/2026-award-winners.php — Ma and Qiang
   stylings.
4. https://www.usm.edu/graduate-programs/polymer-science-engineering.php
   — M.S./Ph.D. at Hattiesburg; three primary areas (synthetic chemistry,
   physical chemistry, polymer engineering); EGFP.
5. https://www.usm.edu/faculty-directory/profile.php?id=1936549 —
   Nazarenko profile.

## Integration record (integrator, 2026-11-12)

**Applied** (branch `agent/spaghetti/wave3-southern-miss-depth`, base
`f2c7c814`):

**Depth fills (PROG-000060, 0/5 → 2/5):** `research_areas` set to the 11
adjudicated terms (biomedical_polymers;characterization_methods;coatings;
composites_carbon;composites_mechanics;membranes_separations;
polymer_physics;polymer_synthesis;recycling_circularity;
sustainable_feedstocks;thermosets); `facilities_note` set to the Thames
PSRC housing statement exactly as fills.csv adjudicates.
`specialty_processes` and `specialty_materials` stand as adjudicated
no-fills; `scale_band` stands HELD — not set (mirror-only enrollment
witness; settling fact in Holds §1 above). `last_verified` → 2026-11-12
on PROG-000060 only.

**Links (11):** PERSON-000459…PERSON-000469 each took
`program_org_id = PROG-000060` as PRIMARY, one evidence row each, and
`last_verified` → 2026-11-12. No other people row changed. Weakest link
stands as flagged in the packet: Ma PERSON-000464, witnessed on the
Provost's 2026 Award Winners page; his directory absence is recorded as
a listing artifact, not departure evidence.

**lab_url applied (1 value):** PERSON-000464 Ma's `lab_url` set to his
already-recorded `public_profile_url`
(https://www.maresearchlab.com/team-boranma-usm) on the packet's stated
witness, with its own S6 evidence row.

**Not applied:** the two unrecorded teaching-track faculty (Broadhead,
Olson) were NOT minted — Gate A treatment of teaching-track faculty is
an owner/integrator call the packet flags but does not propose; the five
emeriti stand unrecorded under the emeritus rule. No new program rows
(the EGFP and Thames-PSRC-as-lab_facility lane rejections stand).

**Evidence:** EVD-333581..EVD-333594 — 14 rows (2 in
evidence_programs.csv: the two fills; 12 in evidence_people.csv: 11
links + 1 lab_url). Allocation note: this unit's range starts at
EVD-333581 because the preceding wave-3 unit (Minnesota, built on its
own branch) consumed EVD-333539..EVD-333580; this tree's own scan max is
EVD-333538. Next free EVD-333595. QUEUE: the P2-applications claim is
flipped to done (PR #283, merged) and this pass's claim is added, per
the standing pattern.
