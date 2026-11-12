# Carried-institution rows verification lane — 2026-11-12

**Lane:** carried-institution rows (owner-approved 2026-11-12). **Mode:**
packet-only — no repo data edited, nothing pushed. **Data read from:**
`~/workspace/atlas-p2-2026-11-12/data/` (read-only) + `docs/SCHEMA.md`
(v1.13.1) for row shapes. **Flag sources:** the wave-3 PA plastics-tech
packet (`working/wave3-2026-11-12/pa-plastics-tech/`) and the wave-3
ABET/IPEDS cross-check (`working/wave3-abet-ipeds-crosscheck-2026-11-12.md`).
**Fetches:** 7 primary-source page fetches + 7 searches across 4
organizations (cap ~6 per item respected). **Paid calls: zero** (no
Tavily/Exa/Firecrawl; all verification on the institutions' own pages via
direct fetch).

## Counts (unit + filter)

- **Items in scope: 5** — (1a) Penn State MatSE graduate program row,
  (1b) Penn State MRI center row, (1c) campus-grain record for 2 carried
  people, (2) Macomb Community College institution + program, (3) Utah
  Valley University institution + program.
- **Verdicts: VERIFIED 3 items** (1a, 2, and 1b in the reduced
  lab-facility form the evidence supports) · **STILL_UNCERTAIN 1** (1b as
  a center row) · **REJECT 1** (3, program claim) · **record-only
  confirmations 2** (1c: PERSON-000765, PERSON-000777).
- **Rows drafted: 3 program rows** in `proposed_rows.csv` (2 degree/
  facility rows at a carried institution, 1 certificate row at a new
  institution) **+ 1 institution row** in `proposed_institutions.csv`.
  `program_id` is `TBD` throughout (allocated at integration only);
  Macomb's rows join on the packet key `TBD-NEW-MACOMB`.
- **People context (Penn State University Park, ORG-002775):** 18 people
  records in `people.csv` with `institution_org_id = ORG-002775`, **0 of
  18** carrying a `program_org_id`; the only program row at the
  institution today is PROG-000037 (Polymer Science Minor, `course`).

## 1a. Penn State MatSE graduate program (University Park) — VERIFIED, row drafted

Basis, all on Penn State's own pages:

- The Graduate Bulletin's program page styles it the **Intercollege
  Graduate Degree Program in Materials Science and Engineering**,
  "Campus(es): University Park (Ph.D., M.S.)", degrees conferred Ph.D.
  and M.S., and its own program description names the research areas:
  "Faculty have interests in many research areas including biomaterials,
  ceramics, composites and hybrids, computational materials science,
  electronic and photonic materials, materials chemistry and physics,
  metals, nanostructured and nanoscale materials, piezoelectrics and
  ferroelectrics, **polymers and soft materials**."
  (https://bulletins.psu.edu/graduate/programs/majors/materials-science-engineering/)
- The same description makes **MATSE 542 Polymeric Materials: The Solid
  State** a required core course of the M.S.
- The department's own Research Focus Areas page names **Polymers** as a
  focus area in its own right: "Along with metals and ceramics, the
  study of polymers has risen to become a cornerstone of materials
  science and engineering in recent years," and its synthesis area
  covers "synthesis of polymer materials by a range of controlled
  polymerization techniques."
  (https://www.matse.psu.edu/research/about-our-research/research-focus-areas)

Inclusion: §4.11 prong (b) — the degree's own published description
names a polymer research area — and it passes the owner's 2026-11-12
department-row test (the department's own pages name polymers as a
research area of the degree). Drafted as `degree`, `ms;phd`,
`master;doctorate`, tier A. `research_areas` is restricted to the
polymer slice (`polymer_synthesis;polymer_physics`); specialty fields
held (no specific process or material family named beyond polymers
generally).

**Seam, flagged not settled:** the brief scoped this row to the
graduate program; the same department's B.S. is not in it. The
all-levels department row (Minnesota PROG-000104: `bs;ms;phd`) is the
live alternative — the integrator/owner should pick one shape before
people links are minted, because 11 of the 18 people recorded at
ORG-002775 carry MatSE in their role text and a link pass will follow
this row.

## 1b. Penn State Materials Research Institute (MRI) — center row STILL_UNCERTAIN; MCL lab-facility row VERIFIED and drafted instead

MRI's own site (https://www.mri.psu.edu/) presents the institute through
its core facilities and centers (MCL, Nanofab, 2DCC-MIP, MRSEC,
CIMP-3D, …). Within the fetch budget, **no MRI page names polymers as an
institute research focus or thrust**, and MRI is not polymer-named — so
a `center` row fails the named-program test at center grain on current
evidence.

What MRI's own site *does* state is polymer scope at the service level,
through its Materials Characterization Laboratory (MCL):

- MCL sample preparation: "The MCL houses an array of ion mills,
  mounting & polishing equipment and supplies needed to prepare most
  inorganic samples and **many polymer samples** for analysis."
  (https://www.mri.psu.edu/materials-characterization-lab/sample-prep/sample-prep)
- MCL infrared spectroscopy, application examples: "**Temperature
  induced morphology changes in polymers** using in-situ attenuated
  total reflection (ATR)."
  (https://www.mri.psu.edu/materials-characterization-lab/characterization-techniques/infrared-spectroscopy)

That satisfies §4.11 prong (c) — a facility/service stating polymer
characterization as its offer — so the packet drafts MCL as a
`lab_facility` row under ORG-002775 (tier B; `research_areas` =
`characterization_methods` only, per §4.11). **Settling fact for the
MRI center row:** an MRI page (research/focus-area or center listing)
naming polymers or polymer research as an institute-level focus; if one
is produced, the center row can be drafted and the MCL row rides under
it as a second row.

## 1c. Campus-grain record — Rhoades PERSON-000765, Zhang PERSON-000777 (record only, no action)

Confirmed from Penn State's own pages today (Behrend's Plastics
Engineering Technology directory,
https://behrend.psu.edu/directory/school-engineering/plastics-engineering-technology,
live crawl 2026-11-12):

- **Alicyn Rhoades** — "Vice Chancellor and Associate Dean for Research
  and Graduate Studies, **Penn State Behrend**; Distinguished Professor
  of Engineering, Plastics Engineering Technology and Polymer
  Engineering and Science programs" (office: 103 Glenhill Farmhouse,
  Behrend).
- **Xiaoshi Zhang** — "Assistant Professor, **Polymer Engineering and
  Science and Plastics Engineering Technology**" (office: 213G Burke —
  the Burke Center, Behrend).

Both are Behrend-based (Erie) faculty, carried in `people.csv` under
ORG-002775 (University Park). This packet records the confirmation
only; re-homing stays with the owner's separate Penn State campus-grain
item, exactly as the PA packet's census flagged (`STILL_UNCERTAIN`,
do-not-mint).

## 2. Macomb Community College (Warren, MI) — VERIFIED, institution + program rows drafted

Macomb was **MISSING** in the cross-check (no org row; it appeared only
in College Factual's CIP 15.0607 rankings — a discovery lead). On the
college's own pages:

- Macomb's official eCatalog, Applied Technology & Apprenticeship,
  A.A.S. page, states the department's certificate classifications and
  that "Programs currently available include those in the chart on the
  following page"; its **"Areas of Specialty: Apprenticeship,
  Employee-in-Training & General Certificate"** chart lists, among
  others, "**Mold Maker-Plastic and/or Die Cast**" and "**Plastic
  Process Technician**."
  (https://ecatalog.macomb.edu/preview_program.php?catoid=57&poid=6874&returnto=7431%3Futm_source%3Dskillpointe&utm_medium=referral_link)
- A Macomb-hosted program list names the same specialties:
  https://www.macomb.edu/resources/attachments/Survey-Course-Description.pdf
- The department's **Plastic Process Technician Certificate** sheet
  (Applied Technology & Apprenticeship, Warren MI; Rev 5/2019, in a
  sheet series carrying 5/2024 revisions) gives the 32-credit
  curriculum: ATMT 1700 Thermoplastic & Thermosetting Materials,
  ATMT 1750 Plastic Product Design & Tooling, ATMT 2210 Plastic Mold
  & Die Cast Die Theory, et al., stackable into the Manufacturing
  Technology A.A.S.

Inclusion: §4.11 prong (a) — a credential named plastics by name in the
institution's own catalog. Drafted: institution row (ecosystem,
`university_college`, grain `institution`, tier B) + program row
(`certificate`, `certificate`, tier B). `specialty_processes` held —
the certificate's own sheet names no specific shaping process; course
titles ride verbatim in the row instead. **Flag (not drafted):** the
chart's second plastics specialty, **Mold Maker-Plastic and/or Die
Cast** — settling fact is its certificate sheet in the same Applied
Technology series. **Availability note:** ecatalog.macomb.edu returned
403 to this lane's direct fetch; the chart text was read in the
catalog's own indexed extract and corroborated by two Macomb-hosted
documents — hence tier B, and the integrator should re-open the
catalog page at application.

## 3. Utah Valley University (Orem, UT) — program REJECT; no rows drafted

The cross-check's UVU entry rested on IPEDS CIP 15.0607 completions as
derivative-reported (College Factual ranked UVU #4 in the CIP). UVU's
own **2026-2027 Academic Program Inventory** — the university's official
listing of every active program with its CIP code
(https://www.uvu.edu/accreditation-academic-assessment/docs/api-26-27.pdf)
— settles it:

- The strings "Plastic" and "Polymer" occur **nowhere** in the full
  inventory (10,407 extracted lines).
- CIP **15.0607 occurs exactly once**, attached to **Collision Repair
  Technology** (Undergraduate Certificate, 32 credits, Applied
  Automotive Engineering & Transportation Technologies): "The Collision
  Repair Certificate Program at Utah Valley University prepares
  students for entry-level careers in the automotive collision repair
  industry."

**Deciding fact:** UVU's 15.0607 completions are its collision-repair
completions coded to the plastics CIP — the cross-check's own
composites/miscoding caveat, confirmed on the institution's own
inventory. There is no plastics/polymer program to row, and no
institution row is proposed (nothing for it to host). For completeness:
UVU's Mechanical Engineering B.S. carries a single course, ME 3170
Introduction to Plastics and Composites — a single named course does
not pass §4.11's named-program test and is not drafted.

## Weakest links (verifier attention, in order)

1. **Macomb tier-B basis** — the operative catalog chart reached the
   lane via the catalog's indexed extract (direct fetch 403). The
   claim is corroborated by two Macomb-hosted documents and a
   current-revision sheet series, but the integrator should re-open
   the eCatalog page itself at application.
2. **MatSE row grain** — graduate-only (per brief) vs. all-levels
   department row (Minnesota precedent) is an open seam; it must be
   settled before the follow-on people-link pass, not after.
3. **MCL row URL** — points at the witnessed sample-prep page; the MCL
   landing URL should be confirmed at integration.
4. **UVU REJECT scope** — the reject is of the *program attribution*,
   on UVU's current (2026-2027) inventory; it says nothing about
   historical programs, and it is not an organization-closure reject
   (no Form 5500 question arises).

## Deliverables

- `README.md` (this file) — verdicts, witnesses, holds, weakest links.
- `proposed_rows.csv` — 3 rows in `programs.csv` shape plus
  `witness_url` + `verdict` columns (the wave-3 NSF-batch packet
  format): MatSE graduate degree (ORG-002775), MCL lab facility
  (ORG-002775), Plastic Process Technician certificate
  (`TBD-NEW-MACOMB`).
- `proposed_institutions.csv` — 1 row in `ecosystem.csv` shape plus
  `witness_url` + `verdict`: Macomb Community College.

---

## Integration record — carried-institution rows (integrator: spaghetti, 2026-11-12)

Applied from this packet to canonical data on branch
`agent/spaghetti/carried-rows-2026-11-12`, base origin/main
`79b1f42b40` (PRs #284–#299). Build script:
`~/workspace/atlas-resync-2026-11-10/build_carried_rows.py`;
pre-pass backups in `~/workspace/atlas-carried-backups-2026-11-12/`
(programs.csv, ecosystem.csv, evidence_programs.csv,
evidence_ecosystem.csv, QUEUE.md). Packet cells landed verbatim
(the packet-only `witness_url` / `verdict` columns stripped); only
the placeholders (`TBD`, `TBD-NEW-MACOMB`) were replaced by
allocated IDs.

- **Program rows created (3)** — allocation opened at the brief's
  floor **PROG-000340**, in proposed_rows.csv order (the tree maxima
  on this base were PROG-000331 / ORG-013505 / EVD-333850; the
  floors sit above the federal round-2 lane B unit's reserved
  ranges, which merges before this unit in sequence, and governed
  regardless): PROG-000340 Materials Science and Engineering
  (ORG-002775 Penn State University Park, `degree`, `ms;phd`,
  `master;doctorate`, tier A — graduate-only **as drafted**);
  PROG-000341 Materials Characterization Laboratory (MCL)
  (ORG-002775, `lab_facility`, tier B); PROG-000342 Plastic Process
  Technician (ORG-013506 Macomb Community College, `certificate`,
  tier B). **Next free: PROG-000343.**
- **Ecosystem institution row created (1)** — ORG-013506 Macomb
  Community College (`university_college`, grain `institution`,
  tier B), single institution-grain row in the roster-unit shape
  (no organizations-shard row, no site rows), carrying its computed
  rollup (below). `ipeds_unitid` left **blank as drafted**: the
  packet notes the derivatives embed 170790, but the value was not
  confirmed against the IPEDS directory in this pass, and an
  unverified registry identifier is not recorded (AGENTS.md §4).
  **Next free: ORG-013507.**
- **MatSE level seam — HELD OPEN, documented, not settled.** The
  row lands graduate-only (M.S./Ph.D.) exactly as the packet
  drafted it. The live alternative — an all-levels department row
  on the Minnesota PROG-000104 precedent (`bs;ms;phd`) — is an
  owner/integrator call the packet flags must be picked **before**
  the follow-on people-link pass mints links (18 people stand at
  ORG-002775, 0 linked; 11 carry MatSE in their role text). This
  unit made **no people changes**: no links, no re-homing.
  Rhoades (PERSON-000765) and Zhang (PERSON-000777) stand
  confirmed Behrend-based on Behrend's own directory as
  record-only context in the packet; re-homing stays with the
  owner's separate Penn State campus-grain item.
- **MCL posture — as ruled:** `research_areas` carries
  `characterization_methods` only; both specialty fields empty.
  The MRI **center** row was not created (STILL_UNCERTAIN — no
  MRI page names polymers as an institute-level focus; the
  settling fact stands in the packet README §1b). The row's
  url/public_door_url point at the witnessed sample-prep page as
  drafted; the MCL landing-URL confirmation stays flagged in the
  row's notes for a later pass.
- **Macomb evidence posture — the packet's weakest link, landed
  honestly.** ecatalog.macomb.edu returned 403 to the verification
  lane's direct fetch; the lane read the "Areas of Specialty"
  chart in the catalog's own indexed extract, corroborated by two
  Macomb-hosted documents. At integration the catalog page was
  re-read and its chart text confirmed verbatim ("Plastic Process
  Technician" and "Mold Maker-Plastic and/or Die Cast" both
  listed; "Programs currently available include those in the chart
  on the following page"). The minted evidence keeps the posture
  explicit: existence rows rest on the Macomb-hosted program
  document (`own_site`); the two scope rows citing the catalog
  chart are classed `directory` on the indirect access route,
  their claim details state the route, and every Macomb effect is
  capped at `supports_B` — no class was upgraded. The chart's
  second specialty (Mold Maker-Plastic and/or Die Cast) remains
  flagged, not drafted, exactly as the packet left it.
- **Utah Valley University — REJECT stands; nothing created** (no
  program row, no institution row). Deciding fact, from UVU's own
  2026-2027 Academic Program Inventory: "Plastic"/"Polymer" occur
  nowhere in the inventory, and CIP 15.0607 attaches exactly once,
  to Collision Repair Technology.
- **Ecosystem rollups recomputed (V-16, same pass)** — the
  recomputation was first verified to reproduce every carried
  rollup on the pre-build tree (zero drift). Changes: ORG-002775
  Pennsylvania State University (University Park) —
  `polymer_program_name` "Polymer Science Minor (University
  Park)" → "Materials Science and Engineering; Materials
  Characterization Laboratory (MCL); Polymer Science Minor
  (University Park)" (type-precedence order: degree, lab_facility,
  course), `polymer_program_url` → the MatSE graduate bulletin
  URL, `polymer_program` unchanged (true); only the rollup fields
  and `last_verified` moved on that row. The new Macomb row
  carries its computed rollup: name "Plastic Process Technician",
  URL = PROG-000342's catalog URL.
- **Evidence minted (8 rows)** — programs EVD-333874..EVD-333879
  (existence + scope per created row; source_class per the
  witness's actual host and access route: MatSE existence/scope
  `own_site` supports_A ×2; MCL existence/scope `own_site`
  supports_B ×2; Macomb certificate existence `own_site` /
  scope `directory`, supports_B ×2); ecosystem
  EVD-333880..EVD-333881 (Macomb existence `own_site` / scope
  `directory`, supports_B ×2). Allocation opened at the floor
  EVD-333874. **Next free: EVD-333882.**
- **QUEUE** — the federal round-2 lane A claim is flipped to
  `done 2026-11-12 (PR #299, merged)` per the git log (the
  dept-row pilot claim already stood done, PR #298); the lane B
  claim stands absent on this base and is left absent (not
  merged yet); this unit's claim is added below lane A's.
- **Gates** — `scripts/validate.py`: "OK — validation passed."
  (totals: 5,024 organizations, 408 ecosystem rows, 1,472 people,
  201 program rows, 40,921 evidence rows; warnings only the
  standing classes, none naming this unit's records).
  `scripts/check_row_loss.py --base origin/main`: "row-loss
  guard: OK — no keyed row removed from data/ since origin/main
  (merge-base 79b1f42b40)". Row-level diff vs backups: programs
  +3 / 0 changed / 0 removed; ecosystem +1 with exactly
  ORG-002775 changed; evidence pure appends; people files
  unmodified. No REMOVALS.csv.
