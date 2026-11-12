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

---

## Integration record — Penn College half (wave-3 unit 7, applied 2026-11-12)

**Split:** this packet covers two institutions. The Behrend half (ORG-002779: PROG-000035/163/164 + 5 people) integrated as unit 6 (`tasks/behrend-academic-depth-2026-11-12/`). This record covers **only the Penn College half**; the packet files are copied as authored (both institutions documented) and this record states the split. Behrend rows were not touched by this pass.

**Institution ID note:** the unit brief named the org ORG-002781; the packet and the data carry Pennsylvania College of Technology as **ORG-002780** (ORG-002781 is Drexel University). ORG-002780 governs and was used.

**Applied from `origin/main` `f2c7c814` on branch `agent/spaghetti/wave3-penn-college-depth`:**

- `data/programs.csv` — 4 rows changed, 0 added (filter: ORG-002780's 4 active rows), 14 cell fills from fills.csv, `last_verified` → 2026-11-12 on exactly those 4 rows:
  - PROG-000036: `program_name` **"Polymer Engineering" → "Polymer Engineering Technology"** (name correction, packet adjudication 4.4), `specialty_processes` (9 §3.1 slugs), `facilities_note`, `admissions_status`=admitting, `unit_department`. Depth 0/5 → **2/5**.
  - PROG-000165: `specialty_processes` (6 slugs), `facilities_note`, `unit_department`. Depth 0/5 → **2/5**.
  - PROG-000166: `specialty_processes` (3 slugs), `unit_department`. Depth 0/5 → **1/5**.
  - PROG-000045: `apprenticeship_registered`=true, `specialty_processes` (2 slugs), `geography_served` **pennsylvania → national** (a change to a carried value, packet adjudication 4.3 — the page states "Trains workers in any location via virtual delivery"), `unit_department`. Depth 0/5 → **1/5**.
  - Holds honored: `research_areas` unfilled on all four rows (packet §5 — a course title states no research area; teaching programs make no research statement); `specialty_materials` unfilled (no resin/family named on any fetched page); `scale_band` unset on all four (no published program-level enrollment within budget; completions never convert, ruling S3).
- `data/ecosystem.csv` — 1 row changed: ORG-002780's V-16 rollup recomputed in this same pass, as the PROG-000036 name change requires. Before: name "Polymer Engineering; Polymer Technology; Polymer Processing; Plastics Process Technician Apprenticeship", URL https://www.pct.edu/academics/et/polymer-engineering, `last_verified` 2026-10-29. After: name **"Polymer Engineering Technology; Polymer Technology; Polymer Processing; Plastics Process Technician Apprenticeship"** (type precedence degree → certificate → apprenticeship, then name), URL **unchanged** (the first row in rollup order, PROG-000036, keeps the same `url`), `last_verified` 2026-11-12. No other ecosystem field or row changed; the rollup is a generated field and carries no evidence row (Texas A&M unit-5 precedent).
- `data/people.csv` — 4 rows added, 0 changed (filter: institution ORG-002780, 0 recorded at base). Census order; `role_as_published` = census title verbatim; `research_specialties` empty on all four (no person-level specialty stated — nothing inferred):
  - PERSON-002123 Vii Rice — `assistant_professor`, tier A, program_org_id PROG-000036 (PROG-000165 banked in link-row text).
  - PERSON-002124 Adam Barilla — `assistant_professor`, tier A, program_org_id PROG-000036 (PROG-000165 banked).
  - PERSON-002125 Jose Perez — `senior_lecturer` (**fold**, below), tier A, program_org_id PROG-000036 (PROG-000165 banked).
  - PERSON-002126 Mark Sneidman — `senior_lecturer` (**fold**, below), **tier B**, program_org_id PROG-000036 (PROG-000165/166 banked). Weakest mint: witnessed in the faculty blocks of all three polymer program pages but absent from the departmental faculty page's Polymer Engineering section; tier B prices the missing roster corroboration (packet §8.1). Settling re-check: that departmental page at a future pass.
  - **Role folds (Perez, Sneidman — styled "Instructor, Plastics & Polymer Technology"):** the §4.9 role enum carries **no `instructor` value** (nor a plain `lecturer` value — the Behrend unit-6 gap). The enum's instructional-faculty value `senior_lecturer` [v1.8.2] is applied with the exact styling preserved in `role_as_published`; the fold is disclosed in both admission evidence rows (EVD-333703, EVD-333705) and flagged for the owner schema battery: add `lecturer`/`instructor` values and restate PERSON-002121, PERSON-002122, PERSON-002125, PERSON-002126.
  - ID allocation: this tree's people maximum is PERSON-002116; PERSON-002117..002122 were taken by the Minnesota and Behrend units ahead of this one in merge order, so allocation opened at PERSON-002123. **Next free PERSON-002127.**
- Evidence — 22 rows appended, all `own_site`: `data/evidence_programs.csv` +14 (EVD-333685..EVD-333698, one `scope` row per applied fill, tier_effect from each program's own tier — all A → supports_A); `data/evidence_people.csv` +8 (EVD-333699..EVD-333706: per minted person one `existence` admission row + one `scope` link row; tier_effect supports_A ×6, supports_B ×2 for Sneidman). Allocation opened at EVD-333685 per the integrator sequence (units 1–6 consumed EVD-333539..EVD-333684 on their own branches); this tree's scan maximum is EVD-333538 — asserted, no intervening ID backfilled. **Next free EVD-333707.**
- `tasks/QUEUE.md` — the P2 claim flipped to `done 2026-11-12 (PR #283, merged)`; this unit's claim added after it.

**Exclusions honored:** no Behrend content; no new program rows (the Shell Polymers Rotational Molding Center of Excellence is named inside the PROG-000036/165 `facilities_note` text only, exactly as the fills state — packet §7 discovery flag, no row); Kirk M. Cantor not minted (emeritus 2025-10-09, packet adjudication 4.8); no one else minted.

**Validators (run on the built tree):** see the staging build report for the verbatim verdicts (`scripts/validate.py`; `scripts/check_row_loss.py --base origin/main`).

**Addendum — banked second-affiliation rows (follow-up append, 2026-11-12):** per the integrator ruling (symmetry with the Behrend follow-up), the four minted people's second-program affiliations were minted as separate banked evidence rows, append-only: **EVD-333707** (PERSON-002123 Rice → PROG-000165, supports_A), **EVD-333708** (PERSON-002124 Barilla → PROG-000165, supports_A), **EVD-333709** (PERSON-002125 Perez → PROG-000165, supports_A), **EVD-333710** (PERSON-002126 Sneidman → PROG-000165, supports_B — his tier B; witness = the Polymer Technology A.A.S. program page whose faculty block styles him in that program). PROG-000165 is the second program census.csv records for each of the four; no person was skipped. Each row states plainly it is a banked second affiliation; all four `program_org_id` values remain PROG-000036 (verified post-append). No PROG-000166 row was minted for Sneidman (mentioned in build prose only; census.csv records PROG-000165 as his second program, and the ruling specified one row per person). **Final unit evidence range: EVD-333685..EVD-333710 (26 rows). Next free EVD-333711.** Validators re-run after the append: `scripts/validate.py` → "OK — validation passed." (40,627 evidence rows); `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base f2c7c814df)".
