# Wave 3, Lane 6 — Pennsylvania plastics-technology packet: Penn State Behrend + Pennsylvania College of Technology

**Lane:** wave3-batch-plan-2026-11-12, lane 6 (Behrend + Penn College).
**Date:** 2026-11-12. **Mode:** packet-only — no repo data edited, nothing pushed.
**Data read from:** `~/workspace/atlas-p2-2026-11-12/data/` (== main `f2c7c814`).
**Vocabulary:** SCHEMA v1.13.1 §3.1 / §3.2 / §3.5 only; out-of-vocabulary cells held verbatim (§5 below).
**Fetch budget:** 15 primary-source fetches + 3 searches, all on `behrend.psu.edu` / `bulletins.psu.edu` / `pct.edu`. Paid calls: **0**.

## 1. Counts (unit + filter stated)

- **Program rows in scope:** 7 active rows in `data/programs.csv` — 3 at Penn State Behrend (ORG-002779): PROG-000035, PROG-000163, PROG-000164; 4 at Pennsylvania College of Technology (ORG-002780): PROG-000036, PROG-000045, PROG-000165, PROG-000166. All 7 carried **0 of 5 depth cells** filled at lane start (depth cells = `research_areas`, `specialty_processes`, `specialty_materials`, `facilities_note`, `scale_band`).
- **Fill proposals:** 27 rows in `fills.csv` — 13 depth-cell fills + 14 non-cell fills (`admissions_status`, `unit_department`, `employer_custom_training`, `apprenticeship_registered`, `geography_served`, 1 `program_name` correction).
- **People recorded at either institution before this lane:** 0 (filter: `people.csv` rows with `institution_org_id` ∈ {ORG-002779, ORG-002780} — verified by grep, 0 hits each).
- **Census:** 13 rows in `census.csv` — **9 VERIFIED** (admission-ready new people: 5 Behrend, 4 Penn College) and **4 STILL_UNCERTAIN**, each with its settling fact in the CSV's `settling_fact_or_note` column and §4 below.

## 2. Depth outcome per program (proposed)

| Program | Cells before | Cells after (proposed) | Filled | Held |
|---|---|---|---|---|
| PROG-000035 PLET B.S. (Behrend) | 0/5 | 3/5 | specialty_processes, research_areas, facilities_note | specialty_materials, scale_band |
| PROG-000163 PES B.S. (Behrend) | 0/5 | 2/5 | research_areas, specialty_materials | specialty_processes, facilities_note, scale_band |
| PROG-000164 Plastics Training Academy | 0/5 | 2/5 | specialty_processes, facilities_note | scale_band (no enrollment concept published) |
| PROG-000036 Polymer Engineering B.S. (Penn College) | 0/5 | 2/5 | specialty_processes, facilities_note | specialty_materials, research_areas, scale_band |
| PROG-000165 Polymer Technology A.A.S. | 0/5 | 2/5 | specialty_processes, facilities_note | specialty_materials, research_areas, scale_band |
| PROG-000166 Polymer Processing certificate | 0/5 | 1/5 | specialty_processes | research_areas (certificate precedent), facilities_note (shared-lab text already rides the sibling rows), scale_band |
| PROG-000045 Plastics Process Technician Apprenticeship | 0/5 | 1/5 | specialty_processes | research_areas (apprenticeship — non-research by rule), scale_band |

Non-cell fills of note: PROG-000045 `apprenticeship_registered=true` (its own page: "Comprehensive two-year registered program"); PROG-000164 `employer_custom_training=true` (on-site customized cohorts, 8+ participants, per the academy's own About page); PROG-000045 `geography_served=national` (apprenticeship page: "Trains workers in any location via virtual delivery" — integrator adjudication, §4.3).

## 3. Program-by-program basis (condensed; full grounding in fills.csv witnesses)

**PROG-000035 — Plastics Engineering Technology, B.S., Behrend.** ABET-ETAC accredited; the college's own pages claim the largest undergraduate plastics processing lab of its type in the country. The Plastics Training Lab page (Behrend's own lab page for the Burke Center facility the program page calls "our plastics processing lab") names the processes outright: injection molding (ten microprocessor-controlled machines, 17–200 tons), extrusion *and* injection blow molding, extrusion with strand/pipe/sheet dies, a blown film tower, thermoforming machines (type unstated → `thermoforming_unspecified`), and a 75-ton compression molding press — mapped to §3.1 in fills.csv. `research_areas` = `characterization_methods` (program page: "polymer structure and characterization") + `rheology` (bulletin course PLET 330, Advanced Tooling & Rheology). The lab page's testing suite (capillary/torque rheometers, DSC, Flash DSC, TGA, DMA, FTIR) is carried in the facilities note; per §3 discipline it fills **neither** specialty field.

**PROG-000163 — Polymer Engineering and Science, B.S., Behrend.** The bulletin description is a research-flavored degree statement: bulk polymer behavior/manipulation, processing ↔ chemical/micro structure–property development, "comprehensive understanding of bulk, micro and nano polymer characterization techniques," polymer composite formulation incl. polymer/filler interfacial chemistry, failure analysis; courses MATSE 445/447, PES 320/323/340/341/351/365/440/460. Fills: `research_areas` = `characterization_methods;polymer_physics;rheology`; `specialty_materials` = `composites_unspecified` (composite type never stated — the v1.9.1 unspecified slug, never upgraded). **Held:** `specialty_processes` — the degree's own pages name no specific shaping process ("processing" generic throughout); `facilities_note` — no PES-specific facility statement on its own pages (the shared Burke lab is witnessed for PLET/PTA; extending it to PES would be inference).

**PROG-000164 — Plastics Training Academy, Behrend.** Training row: witnessed non-research facts only. Facilities note from the academy's own lab page (10,500 sq ft, equipment as above). Custom/on-site employer training confirmed. `specialty_processes=injection_molding` proposed from the About page's lead topic ("Injection molding principles and scientific molding") — adjudication §4.2.

**PROG-000036 — Polymer Engineering, B.S., Penn College.** The institution styles this degree **"Polymer Engineering Technology"** (its ABET-ETAC accreditation is held "under the Plastics & Polymer Engineering Technology name"); fills.csv proposes the `program_name` correction — integrator adjudication (§4.4). The program page's own "Five Processes" statement (extrusion, injection molding, blow molding, thermoforming, rotational molding) plus its course list (Advanced Extrusion, Advanced Injection Molding, Advanced Blow Molding & Thermoforming, Part Design for Injection Molding & Additive Manufacturing, Recycling/Auxiliary/Automation, Mold & Die Design, Building Molds & Dies, Tooling Maintenance) ground a 9-term `specialty_processes` fill. Subtype discipline: "Extrusion" with no subtype → `extrusion_unspecified`; "blow molding" with no subtype → the §3.1 legacy umbrella `blow_molding`, used only because the subtype is unknown; thermoforming type unstated → `thermoforming_unspecified`; recycling type unstated → `recycling_unspecified`.

**PROG-000165 — Polymer Technology, A.A.S., Penn College.** ABET-ETAC accredited (its own page). Same Five Processes statement; visible courses add Extrusion and Tooling Maintenance → `tooling_repair_maintenance`. Upper-semester course accordions did not render in the fetched text, so the fill rests on the page's own Five Processes statement plus the visible courses — availability limit, not absence (§6).

**PROG-000166 — Polymer Processing certificate, Penn College.** One-year operator certificate. Its own page's skill list ("Decoupled molding processes," "Operating extrusion systems") and career list ("Extrusion machine operator," "Injection mold operator") + the Tooling Maintenance course ground `injection_molding;extrusion_unspecified;tooling_repair_maintenance`. `research_areas` held per the certificate precedent.

**PROG-000045 — Plastics Process Technician Apprenticeship, Penn College (PIRC).** Registered two-year apprenticeship, virtual delivery. The PIRC page states the registered apprenticeships are "in extrusion and injection molding" → the two process fills. Topics on its own page (plastics materials, polymer structures, extrusion fundamentals, injection molder components) are training topics, recorded here, not tagged.

## 4. Adjudications

1. **Shared-lab witness (Behrend).** The equipment page lives under the Plastics Training Academy section of behrend.psu.edu, but it documents the single Burke Center plastics processing laboratory that the PLET program page itself claims ("our plastics processing lab"). It is used as the institution-page witness for PROG-000035 and PROG-000164 facilities/processes. It is **not** extended to PROG-000163 (PES), whose own pages make no facility claim.
2. **Specialty fields on training/apprenticeship rows (PROG-000164, PROG-000045).** Proposed as witnessed non-research facts per the lane brief (what the training *teaches*, from the institutions' own pages). If the integrator's precedent excludes specialty fields on `training`/`apprenticeship` rows, drop those two fill rows; nothing else in the packet depends on them.
3. **PROG-000045 `geography_served` pennsylvania → national.** Grounded verbatim ("Trains workers in any location via virtual delivery"; PIRC: virtual multi-site delivery). Flagged because it changes a carried value rather than filling a blank.
4. **PROG-000036 `program_name` "Polymer Engineering" → "Polymer Engineering Technology".** The carried name came from the IPEDS CIP listing; §4.11 requires the name as the institution styles it, and every Penn College page styles the B.S. "Polymer Engineering Technology." Proposed as a fill for integrator adjudication, not silently assumed.
5. **Census — already-carried Behrend faculty (Rhoades, Zhang).** Both appear in Behrend's current program directory, and both are **already carried in people.csv under ORG-002775** (PERSON-000765 Rhoades, whose recorded role text already says "Penn State Behrend"; PERSON-000777 Zhang). They are census-listed as STILL_UNCERTAIN with an explicit **do-not-mint** note. Per the lane brief and the plan, this packet proposes no re-homing; the settling fact is the owner's campus-grain ruling.
6. **Behrend PES chair conflict (Dillon vs. Rao).** The PES bulletin advising block (crawled 2026-11-06) styles Gregory Dillon "Chair, Polymer Engineering and Science and Professor of Engineering"; the college's Program Chairs page names YuanQiao Rao as PES chair; **neither appears in the current PLET/PES faculty directory** (fetched 2026-11-12). Both are STILL_UNCERTAIN with the settling fact named (a current directory/profile page). The directory's six named faculty govern the VERIFIED set.
7. **Mendis title currency.** The current directory (fetched 2026-11-12) styles Gamini Mendis *Associate Professor*; an older-crawled PLET faculty page styled him *Assistant Professor*. Directory governs; title recorded as published there.
8. **Penn College — Cantor excluded.** Kirk M. Cantor's profile page still styles him "Professor, Plastics & Polymer Technology," but the college's own news item (2025-10-14) records him retired with emeritus status granted 2025-10-09. Emeritus does not count for admission of new people → excluded from census.csv, recorded here. Same rule excluded Behrend's Faculty Emeriti (John Beaumont, Paul Koch).
9. **Penn College — PTA-style instructors excluded (Behrend).** Sean Tucker and Stacey Payne appear on the academy's "Faculty and Instructors" page with industry roles and **no faculty styling** → Gate A fails as published; excluded. Advisory-committee members at Penn College (industry names on the program pages) were likewise never candidates.
10. **Lecturers/instructors counted where the directory presents them as program faculty** (lane brief's Gate A application): Behrend's Nick Vitelli (Lecturer, in the program directory) and Bradley Johnson (Lecturer in Engineering; PTA director), and Penn College's two Instructors (Perez, Sneidman), are VERIFIED. Lab staff/technicians: none were presented as program faculty on any fetched page; none are listed.

## 5. Out-of-vocabulary — held verbatim (no slug invented)

- **"packaging"** — PLET 323 *Packaging Processes*; PLET program page lists "plastics processing and packaging" as a study topic. No §3 slug exists (`packaging_science` is owner battery item B1, undecided). Held verbatim for PROG-000035.
- **"sustainability"** — PLET program page study topic; PES 320 *Polymer Sustainability*. No honest §3/§3.5 mapping (`recycling_circularity` would overclaim a recycling-science specialty neither page states). Held verbatim for PROG-000035 and PROG-000163.
- **"failure analysis"** — PES degree description + PES 440/441; PTA topic "Troubleshooting and failure analysis." No §3.5 slug. Held verbatim for PROG-000163 / PROG-000164.
- **"design of experiments (DOE)"** — PTA topic list. No slug. Held verbatim for PROG-000164.
- **"biomedical polymers" (candidate, not proposed)** — PLET page lists *medical* among industry sectors and a Medical Plastics certificate exists inside the degree; sector mention alone does not state a research area. Held for PROG-000035; see the Medical Plastics Center flag in §7.
- **"Polymer Synthesis & Formulation"** — a Penn College B.S. *course title*. A course title does not state a program research area, and Penn College's pages make no research-area statement for these teaching programs; `research_areas` held for all four Penn College rows.
- **Material families at Penn College** — no resin or family is named on any fetched Penn College program page ("plastics" generic throughout) → `specialty_materials` held for PROG-000036/165/166 rather than inferred.

## 6. Availability notes (failed/partial fetches — signals, not absence)

- Penn College A.A.S. page: course accordions for semesters 3–4 did not render in the fetched text; fills rest on the page's rendered statements (§3).
- Penn College's linked "enrollment/graduation data" page fetched as objectives text only; no enrollment table was captured (see scale_band hold, §8).
- Behrend's directory "Part-Time Faculty" section rendered no names; part-time faculty are therefore unenumerated — an availability limit, recorded, not a zero.
- The apprenticeship page's crawl copy is dated 2025-11-02; its registered-status and topic claims are corroborated by the freshly crawled PIRC page (2026-11-12).

## 7. Discovery flags for the integrator (no rows proposed in this packet)

- **Shell Polymers Rotational Molding Center of Excellence** (Penn College, via PIRC): a named center supporting applied rotomolding R&D — candidate `center` program row under the §4.11 named-program test, for a future discovery decision.
- **Medical Plastics Center of Excellence** (Behrend School of Engineering; Jason Williams is its head): named center, unrowed; likewise the undergraduate **Medical Plastics certificate** inside PLET. Both flagged only.
- **PROG-000163 accreditation currency:** Behrend's PES B.S. is reported (context supplied to this lane) to have gained ABET-EAC accreditation in 2025; no schema field carries accreditation, so no fill is proposed — noted for the integrator's program notes if wanted, to be confirmed against ABET's own listing at application.

## 8. Weakest links (verifier attention, in order)

1. **Mark Sneidman (census, VERIFIED)** — witnessed in the faculty block of all three Penn College polymer program pages, but absent from the Polymer Engineering section of the departmental faculty page (3 names there). Re-check that page at application.
2. **PROG-000035 specialty_processes** — rests on adjudication §4.1 (shared-lab page as the program's witness). The facilities claim itself is multiply witnessed (program page + lab page + academy About page).
3. **`scale_band` — held at both institutions.** No published program-level enrollment was found within budget. Settling sources: Penn College's published Plastics & Polymer enrollment/graduation data (linked from every program page; fetched text carried objectives only) and a Penn State Data Digest / Behrend fact-sheet enrollment figure for PLET/PES. The IPEDS completions already on the rows (27 for PROG-000035, 12 for PROG-000036) are completions, not enrollment, and per ruling S3 never convert.
4. **PROG-000164 `admissions_status=admitting`** — softest fill: grounded on the About page's scheduled-courses statement plus the carried courses page's published schedule; low consequence either way.
5. **Dillon / Rao (§4.6)** — the institution's own pages conflict; both held STILL_UNCERTAIN rather than resolved by preference.

## 9. Deliverables

- `README.md` (this file) — counts, adjudications, holds, weakest links.
- `fills.csv` — 27 rows: program_id, field, proposed_value, witness_url.
- `census.csv` — 13 rows: institution, name, title_as_published, program, verdict, witness_url, settling_fact_or_note (the seventh column extends the brief's six so every STILL_UNCERTAIN row carries its settling fact in machine-readable form, per the verdict grammar).

## Integration record (integrator, 2026-11-12)

**Unit split.** This pass applies the Behrend half of the combined PA
plastics-tech packet (wave-3 lane 6) only. The Penn College half
(ORG-002780: the fills for PROG-000036/165/166/045, including the
PROG-000036 `program_name` correction, and the census-VERIFIED Rice,
Barilla, Perez, and Sneidman) integrates as the next unit and is
untouched here. The packet files are copied into this folder as
authored (they document both institutions); this record states what
was applied.

**Fills applied (12 cell changes from the 13 Behrend fill rows):**
PROG-000035 PLET — `specialty_processes`, `research_areas`,
`facilities_note`, `admissions_status`, `unit_department` all set
from empty, exactly as `fills.csv` adjudicated (depth 0/5 → 3/5).
PROG-000163 PES — `research_areas`, `specialty_materials`,
`admissions_status` set (0/5 → 2/5). PROG-000164 Plastics Training
Academy — `facilities_note`, `specialty_processes`,
`employer_custom_training=true`, `admissions_status` set (0/5 → 2/5).
The thirteenth Behrend fill row (PROG-000164 `unit_department`)
proposes "Community and Workforce Programs", the value the row
already carries — applied as a confirm: no cell change, no evidence
row. Held as adjudicated: `scale_band` on all three rows (no
published program-level enrollment; IPEDS completions never convert
under S3); PROG-000035 `specialty_materials` (the lab's testing suite
fills neither specialty field); PROG-000163 `specialty_processes` and
`facilities_note` (its own pages name no shaping process, and the
shared Burke lab witness is NOT extended to PES — packet §4.1);
PROG-000164 `research_areas` (training row, non-research). The §5
held phrases — "packaging", "sustainability", "failure analysis",
"design of experiments (DOE)" — appear in no applied cell.

**New people (5):** PERSON-002118 Brian Young (associate_professor;
primary PROG-000035), PERSON-002119 Gamini Mendis
(associate_professor; primary PROG-000163), PERSON-002120 Jason
Williams (associate_professor; PROG-000035), PERSON-002121 Nick
Vitelli (PROG-000035), PERSON-002122 Bradley Johnson (PROG-000164) —
IDs allocated in census order above this tree's maximum
PERSON-002116, skipping PERSON-002117 (minted by the Minnesota unit
ahead of this one in merge order). All tier A on the institution's
own directory/faculty pages; `role_as_published` carries each census
title verbatim; `research_specialties` left empty (the witness pages
state no person-level specialty — nothing inferred). Mendis's and
Vitelli's second witnessed programs (PROG-000035 and PROG-000163
respectively) are banked in their link rows' claim text;
`program_org_id` stays single-valued at the census-first program,
and no separate banked rows were minted in this unit (build spec:
one admission row + one link row per person).

**Role folds disclosed (2 kinds):** Williams's "Associate Teaching
Professor" folds to `associate_professor` (rank fold; cf.
PERSON-000259). Vitelli ("Lecturer") and Johnson ("Lecturer in
Engineering") have no exact §4.9 value — the role enum carries no
plain lecturer value; the enum's lecturer-family value
`senior_lecturer` [v1.8.2] is applied with the exact styling
preserved in `role_as_published`. Flagged for the owner schema
battery: add a `lecturer` role value and restate PERSON-002121 and
PERSON-002122. Neither record's published styling is altered.

**Exclusions honored:** Rhoades (PERSON-000765) and Xiaoshi Zhang
(PERSON-000777) — census-listed at Behrend but already carried under
ORG-002775 — were not minted, not moved, and are byte-identical
after the build (campus re-homing stays owner-gated). Dillon and Rao
(the PES chair conflict, STILL_UNCERTAIN) were not minted. No Penn
College rows, fills, or people were touched. No new program rows:
the Medical Plastics Center of Excellence and the undergraduate
Medical Plastics certificate (packet §7) remain discovery flags, and
the reported 2025 ABET-EAC accreditation of PROG-000163 has no schema
field — it is recorded here only.

**Ecosystem rollup (V-16):** no program name or URL changed, so no
recompute was due; the ORG-002779 rollup was independently
recomputed from the built `programs.csv` and matches the carried row
character-for-character (name "Plastics Engineering Technology;
Polymer Engineering and Science, B.S.; Plastics Training Academy";
URL = PROG-000035's URL). `ecosystem.csv` is untouched by this pass.

**Evidence:** EVD-333661..EVD-333682 — 22 rows (12 in
`evidence_programs.csv`, one scope row per applied fill; 10 in
`evidence_people.csv`: 5 existence + 5 scope/link). Allocation opened
at EVD-333661 per the integrator sequence — the preceding wave-3
units consumed EVD-333539..EVD-333660 on their own branches; this
tree's own scan maximum is EVD-333538 and no intervening ID is
backfilled. All rows are `own_site` with `tier_effect` supports_A
(every touched record is tier A). Next free EVD-333683; next free
PERSON-002123. QUEUE: the P2-applications claim is flipped to done
(PR #283, merged) and this pass's claim is added, per the standing
pattern.

**Addendum (integrator ruling, 2026-11-12) — banked second-affiliation
rows:** the two second witnessed program affiliations previously
carried only in link-row text are now minted as separate append-only
evidence rows, symmetric with the Minnesota and Texas A&M follow-ups:
EVD-333683 (PERSON-002119 Mendis → PROG-000035, witnessed on the
Behrend directory page) and EVD-333684 (PERSON-002121 Vitelli →
PROG-000163, witnessed on the Plastics Training Academy faculty page,
which styles his appointment across both PLET and PES programs —
PROG-000164 is the witness page's program, not the affiliation
target). Both rows are `scope` / `own_site` / `supports_A`; neither
changes a `program_org_id` (Mendis stays PROG-000163; Vitelli stays
PROG-000035). Evidence range is now EVD-333661..EVD-333684 — 24 rows
(12 program scope; 12 people: 5 existence + 5 scope/link + 2 banked).
Next free EVD-333685; next free PERSON-002123 unchanged. Post-append
gates: `scripts/validate.py` PASS (exit 0; 40,625 evidence rows);
`scripts/check_row_loss.py --base origin/main` green (exit 0).
