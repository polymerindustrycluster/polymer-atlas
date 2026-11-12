# Wave 3 — Lehigh University (ORG-002776) depth + link packet

Lane date: 2026-11-12. Packet-only: no `data/` edits, no pushes. Data read
from `~/workspace/atlas-p2-2026-11-12/data/` (== main `f2c7c814`).
All witnesses are Lehigh's own pages (lehigh.edu domains), fetched
2026-11-12. Paid API calls: **zero**.

## Counts (unit + filter)

- Programs in lane: **5 carried program rows** at ORG-002776, all at 0/5
  depth cells at lane start (PROG-000038, 000039, 000040, 000070, 000109).
- Fills proposed: **12 rows** in `fills.csv` — PROG-000038 ×3,
  PROG-000039 ×5, PROG-000070 ×1 (non-research only), PROG-000109 ×3,
  PROG-000040 ×0 (held, see currency flag C2).
- People pool: **14 recorded people** at ORG-002776, 0 carrying
  `program_org_id` at lane start. Verdicts: **13 LINK, 1 NO_WITNESS**
  (links.csv). Link distribution: PROG-000038 ×10, PROG-000109 ×2,
  PROG-000039 ×1.
- Fetches: 11 page opens + 4 searches, all free routes; per-program
  fetches ≤3, inside the ~6 cap.

## Program adjudications

Fills follow the wave-2 convention: `proposed_value` is the institution's
own phrase; the integrator maps to §3 slugs. Lane mapping notes:

- **PROG-000038 PSE (degree).** `research_areas` phrase "material
  sustainability" — nearest §3.5 candidates are `sustainable_feedstocks`
  / `recycling_circularity`; neither is an exact fit (the phrase is
  broader than feedstocks), so the integrator may hold. Specialty
  processes/materials **held**: the program's pages state disciplines
  and course topics, not program specialties. `scale_band` **held**: no
  enrollment figure published on the pages checked (and per ruling S3,
  completions/faculty counts never convert). `facilities_note` is the
  program's own generic statement, verbatim — thin but sourced.
- **PROG-000039 EPI (center).** `specialty_processes` "emulsion
  polymerization" maps exactly to §3.1 `polymerization`.
  `research_areas` phrases map to `polymer_synthesis`,
  `characterization_methods`, and `biomedical_polymers` (biocompatible
  particles for diagnostics/therapeutics). `specialty_materials`
  **held verbatim**: the institute's material is "polymer latexes" —
  no §3.2 slug names latex honestly, and `coatings` would be inference.
- **PROG-000070 Online PSE Certificate.** All depth cells **held** per
  the UMass Lowell certificate precedent (research areas are for
  research programs). One non-research fill: `admissions_status =
  admitting` (live admissions requirements + named coordinator on the
  program's own page; 12 credits, matching the recorded credential).
- **PROG-000109 MSE (degree).** `research_areas` phrases map at the
  integrator's discretion: "polymers and composites" →
  `composites_mechanics` is only a partial fit (the department states
  composites as a project area, not mechanics specifically);
  "polymer characterization" → `characterization_methods` is exact.
  Specialty processes/materials **held** (department-wide pages do not
  state polymer-specific specialties for the degree). `scale_band`
  **held**: the row's IPEDS completions (19, 2024, CIP 14.1801) are a
  completion flow, not enrollment, and are institution×CIP-wide in any
  case (per the S3 refinement and the row's own notes).

## People adjudications

The PSE program's own people page (`engineering.lehigh.edu/pse/people`)
carries a RESEARCH FACULTY roster with per-person research statements;
that page is the primary witness for 10 of the 13 LINKs, consistent with
wave-2 practice (program-roster pages at MIT/UCSB). Per-person calls:

- **Dual-witness call — Cheng PERSON-000413 → PROG-000109 (MSE), not
  PSE.** She is on the PSE roster, but her current polymer-research
  witness sits on an MSE page (MSE graduate opening "on sustainable
  polymers" naming her as team leader). Resolved by the MIT wave-2
  precedent: dual-witnessed people take the departmental degree
  primary. The PSE roster witness is banked here: "Cheng has a
  long-standing interest in developing and applying engineering tools…
  Her research emphasis has been on biomaterials, surface modification,
  surface science" (PSE people page). If the integrator prefers
  roster-primary, PROG-000038 is the alternate.
- **Holten-Andersen PERSON-000416 → PROG-000038.** Witnessed only on
  the PSE roster in this pass ("…biomaterials, biomolecular materials,
  biophysics, and polymers"); his MSE appointment is title-level only
  here, so the link follows the witness in hand.
- **Arronche PERSON-000418 → PROG-000038.** She directs the degree
  program and the program page states her polymer research verbatim
  (polymers, polymer processing, polymer characterization,
  fiber-reinforced epoxy composites). Cleanest link in the pool.
- **Ou-Yang PERSON-000422 → PROG-000039 (EPI).** His Lehigh physics
  page styles him current EPI director with "Polymers" among his
  stated research interests; the 2026-27 catalog's EPI entry confirms
  the directorship. Role enum `center_director_professor` already
  matches.
- **Wang PERSON-000475 → NO_WITNESS.** The pool's strongest Gate B and
  its only no-link: Lehigh Chemistry's own announcement states "His
  group develops innovative, sustainable polymers and force-responsive
  materials," and his Lehigh chemistry research page states "design of
  responsive and sustainable polymeric materials." But no carried
  program page or roster names him — his home is the Department of
  Chemistry (no carried row) and he is associated faculty of the
  Institute for Functional Materials and Devices (not a carried row);
  the PSE roster does not list him. **Settling fact:** his appearance
  on the PSE people page / an EPI member list, or a carried program
  row for I-FMD. Expect this to resolve with time — see currency
  flag C4.

## Currency flags (dated witnesses; lane does not adjudicate)

- **C1 — PSE credentials and format (PROG-000038).** The record
  carries `credential_types = ms;phd`, `engagement_modes =
  internships_coops`, `geography_served = pennsylvania`. Lehigh's
  current program page and the 2026-27 catalog both publish only
  "Master of Science" and "Graduate Certificate," and state the
  program "is offered in a completely online distance-learning format"
  (catalog PSE entry; PSE academics page: "offered in a completely
  online distance-learning format with the possibility of completing
  remote research for credit"). No PhD is listed on either current
  source. Integrator call: credential refresh to ms (+ certificate,
  separately rowed as PROG-000070) and engagement/geography review
  for an online program. The PhD route appears to have folded into
  departmental/CPSE routes (EPI catalog entry: degrees "in existing
  science and engineering curricula or in the Center for Polymer
  Science and Engineering") — stated as inference, not adjudicated.
- **C2 — CPSE (PROG-000040) is presence-only on current Lehigh
  pages; all depth held.** CPSE is still named in the 2026-27 catalog
  (EPI entry: a degree route, and an entity EPI has "close ties"
  with) and in the MSE graduate pages' affiliated-centers lists
  (fetched 2026-11-12; pages crawled within the last 8 days). No
  standalone CPSE page, leadership, or research description was found
  on lehigh.edu within budget, and Lehigh's current Interdisciplinary
  Research Institutes are I-FMD, I-CPIE, and I-DISC — CPSE is not
  among them. This is **not** a closure finding: no Lehigh page states
  a rename, merger, or closure, and the catalog presence cuts the
  other way. **Settling fact:** a current Lehigh page presenting
  CPSE's own program/leadership/research (or a Lehigh statement of
  its dissolution). Also a record defect for the integrator: the
  row's `url` points at the *EPI* catalog PDF, not any CPSE page.
- **C3 — Title enrichments (P1 rider; verbatim, integrator applies).**
  - Cheng PERSON-000413: her Lehigh faculty page now styles her
    "Professor and Department Chair" (Bioengineering) — the record
    carries no chair. Source:
    `engineering.lehigh.edu/faculty/xuanhong-cheng`.
  - Reichmanis PERSON-000411: the PSE people page styles her
    "…Carl Robert Anderson Chair in Chemical Engineering… and
    Director of the Institute for Functional Materials and Devices" —
    the record carries the chair but not the I-FMD directorship.
  - Arronche PERSON-000418: the PSE people page adds "Affiliated
    Faculty with the university's Department of Materials Science
    and Engineering" to the recorded title (director + teaching
    assistant professor both confirmed verbatim).
  - Jagota PERSON-000412: Lehigh's NHI page styles him "Robert W.
    Wieseman 1916 Professor and Founding Chair of Bioengineering,
    and Professor of Chemical and Biomolecular Engineering" —
    founding-chair element not in the record (record's Wieseman
    title and Vice Provost for Research both confirmed current on
    the PSE people page).
  - Nied PERSON-000420: his department is now styled "Mechanical
    Engineering and Mechanics" (record: Mechanical Engineering).
  - Gilchrist PERSON-000417: chair title confirmed verbatim on his
    own page ("Ruth H. and Sam Madrid Professor") — no change.
- **C4 — Wang PERSON-000475 arrival.** His lab's own bio and Lehigh
  Chemistry's announcement agree: he joined Lehigh as Associate
  Professor of Chemistry in **January 2026**, from the University of
  Akron (Associate Professor of Polymer Science). The Atlas record
  already sits at Lehigh with the correct title — no record change,
  noted so the NO_WITNESS above isn't misread as a stale-record
  problem. His stated Lehigh research (sustainable polymers,
  force-responsive materials) makes him the pool's most likely
  future PSE link.
- **C5 — MSE polymer minor alive.** The undergraduate Minor in
  Polymer Science and Engineering (15 credits, hosted on MSE's own
  minors pages, incl. "ME 385 Polymer Product Manufacturing" and
  "MAT 386 Polymer Nanocomposites") is current — corroborates the
  `minor` credential already encoded on PROG-000109; no new fill.

## Weakest links (verifier: start here)

1. **Gilchrist PERSON-000417 → PROG-000038.** The only LINK whose
   witness text contains no polymer word: he sits under RESEARCH
   FACULTY on the PSE program's own people page, but his published
   statement is particulate/colloidal/granular systems (his own
   faculty page likewise: suspensions, coatings, rheology — no
   polymer statement). The link rests on program-roster membership
   within a program whose sister institute is polymer colloids. A
   stricter Gate B reading flips him to NO_WITNESS; flagged for the
   verifier/integrator rather than silently resolved.
2. **Jagota PERSON-000412 → PROG-000038.** Roster witness with a
   biomaterials/biomechanics statement; his polymer connection
   (soft-materials adhesion, DNA — a biopolymer — nanomaterial
   hybrids) is one inference step further than the explicit
   statements carried by the other nine PSE links.
3. **Cheng's program choice (000413 → MSE over PSE)** — a precedent
   call, documented above; either target is witnessed, the choice
   is the judgment.
4. **PROG-000038 research_areas phrase** ("material sustainability")
   — the slug mapping is inexact by design; an integrator hold is a
   legitimate outcome.

## Lab witnesses captured

- Gilchrist: "Laboratory for Particle Mixing and Self-Organization"
  (named on the PSE people page and his faculty page; no lab URL in
  the fetched text — no `lab_url` proposed).
- Wang: his lab site `https://junpengwanglab.org` is already the
  record's `public_profile_url`; it is his lab's own site and the
  natural `lab_url` candidate if the integrator wants it duplicated
  there.
- Group names without URLs in fetched text (no `lab_url` proposed):
  Reichmanis Research Group, Gartner group, Holten-Andersen Group,
  Ferguson Research Group.

## Sources (all Lehigh-owned, fetched 2026-11-12)

engineering.lehigh.edu/pse · /pse/academics · /pse/people ·
catalog.lehigh.edu PSE entry (2026-27) · epi.cas.lehigh.edu (home +
research highlight) · lehigh-preview.courseleaf.com EPI catalog entry
(2026-27) · distance.lehigh.edu certificate page ·
engineering.lehigh.edu/mse/graduate/phd · /mse/research/facilities ·
/mse/research/current-research-openings-graduate-students-mse ·
faculty pages: cheng, gilchrist, mcguinness ·
physics.cas.lehigh.edu/faculty-staff/daniel-ou-yang ·
chemistry.cas.lehigh.edu Wang announcement (via search extract).

---

## Integration record (wave-3 unit 3, built 2026-11-12 — matches the final build exactly)

**Branch:** `agent/spaghetti/wave3-lehigh-depth` on base `origin/main`
`f2c7c814dfe88e60b5c337aa9f144754ea14d046`. Build only — NOT pushed,
no PR. Pre-pass backups:
`~/workspace/atlas-wave3-lehigh-backups-2026-11-12/`. Build script:
`~/workspace/atlas-resync-2026-11-10/build_lehigh_wave3.py` (paths
defined locally; per-file EOL preserved — all touched files are LF).

**Programs — 4 rows changed, 0 added** (filter: ORG-002776's 5 carried
program rows):

- PROG-000038 PSE: `description_1line` and `facilities_note` set from
  the program's own catalog/academics pages. **`research_areas` HELD**
  (integrator ruling): the lane's only candidate phrase, "material
  sustainability," maps inexactly to the nearest §3.5 slugs
  (`sustainable_feedstocks` / `recycling_circularity`) — neither is an
  exact fit, so the cell stays empty. Credentials/format fields
  deliberately NOT changed despite flag C1 (see follow-ups).
- PROG-000039 EPI: `description_1line` set; `research_areas` set to
  `biomedical_polymers;characterization_methods;polymer_synthesis`;
  `specialty_processes` set to `polymerization` (§3.1, from the
  institute's own "emulsion polymerization" statement);
  `facilities_note` set. `specialty_materials` stands as the lane's
  adjudicated no-fill ("polymer latexes" has no honest §3.2 slug).
- PROG-000070 certificate: `admissions_status` set to `admitting`
  (non-research fill only; all depth cells held per the UMass Lowell
  certificate precedent).
- PROG-000109 MSE: `research_areas` set to
  `characterization_methods;composites_unspecified` — the lane's
  "polymers and composites" phrase mapped to the generic §3.2 slug,
  NOT `composites_mechanics` (the department states composites as a
  project area, not mechanics specifically); `facilities_note` set
  (Polymer Characterization suite).
- **PROG-000040 CPSE: ZERO change** (presence-only flag C2) — no fill,
  no tombstone, no status motion. Its `url` defect (points at the EPI
  catalog PDF) is documented in C2 and left standing.
- `last_verified` → 2026-11-12 on the 4 changed rows only.
- **V-16 ecosystem rollup (ORG-002776) verified:** no program name or
  URL changed in this pass, so the rollup stands unrecomputed —
  `polymer_program_name` / `polymer_program_url` unchanged, correct
  as carried.

**People — 13 rows changed, 0 added** (filter: ORG-002776's 14 recorded
people): the 13 LINK verdicts applied exactly as `links.csv`
adjudicates — PROG-000038 ×10 (Reichmanis 000411, Jagota 000412,
Gartner 000414, Blocher McTigue 000415, Holten-Andersen 000416,
Gilchrist 000417, Arronche 000418, Ferguson 000419, Nied 000420,
Vavylonis 000421), PROG-000109 ×2 (Cheng 000413 per the degree-primary
precedent; McGuinness 000423), PROG-000039 ×1 (Ou-Yang 000422).
`last_verified` → 2026-11-12 on those 13 rows only. **Wang
PERSON-000475 (NO_WITNESS): untouched in every field; no person
evidence row minted** (wave-2 practice).

**P1 title enrichments (flag C3) — 4 applied, each with its own
evidence row, each tied to a verbatim packet quote:**

- Reichmanis 000411: `role_as_published` += Director of the Institute
  for Functional Materials and Devices.
- Cheng 000413: += Department Chair, Bioengineering.
- Arronche 000418: += Affiliated Faculty, Department of Materials
  Science and Engineering.
- Nied 000420: department styling refreshed to "Mechanical Engineering
  and Mechanics."
- **Jagota 000412 NOT applied:** the packet quotes his "Founding Chair
  of Bioengineering" styling verbatim but attributes it only to
  "Lehigh's NHI page" with no URL, so no `source_ref` can be grounded
  for an evidence row. Settles with the NHI page URL.
- Gilchrist 000417: chair title confirmed verbatim — no change needed,
  none made.

**Lab witnesses:** the packet records no lab URL for any linked person
(Gilchrist's laboratory is named without a URL; group names for four
others carry no URL), so **no `lab_url` values were set and no S6
rows minted**. Wang's lab site (junpengwanglab.org) is already his
`public_profile_url`; he is NO_WITNESS and untouched.

**Evidence — 26 rows appended: EVD-333595..EVD-333620. Next free:
EVD-333621.** Allocation follows the integrator sequence, NOT this
tree's scanned max (EVD-333538, asserted in the build script):
preceding wave-3 units consumed EVD-333539..EVD-333580 (Minnesota) and
EVD-333581..EVD-333594 (Southern Miss) on their own branches; the gap
does not exist on this branch and must not be backfilled here.
Breakdown: EVD-333595..EVD-333603 evidence_programs (9 rows: PSE ×2,
EPI ×4, certificate ×1, MSE ×2; claim_type `scope`, source_class
`own_site`, tier_effect from each record's own tier — A→supports_A,
certificate B→supports_B); EVD-333604..EVD-333616 the 13 LINK rows;
EVD-333617..EVD-333620 the 4 P1 title rows (all `scope` / `own_site` /
`supports_A`; every Lehigh person is tier A).

**QUEUE:** the P2-applications claim is flipped to
`done 2026-11-12 (PR #283, merged)`, and this pass's claim line is
added — mirroring the Minnesota/Southern Miss branches (their own
claim lines live on their branches and are not touched here).

**Gates:** `scripts/validate.py` → "OK — validation passed." (40,627
evidence rows = 40,601 at base + 26 appended; warnings are the standing
V-16/V-38/V-44 classes). `scripts/check_row_loss.py --base
origin/main` → "row-loss guard: OK — no keyed row removed from data/
since origin/main (merge-base f2c7c814df)". No REMOVALS.csv needed or
created.

**Follow-ups carried forward (not adjudicated here):** C1 — PSE's
recorded `credential_types = ms;phd` and its format/geography fields
vs the current catalog's MS + online-certificate-only, fully-online
picture (credential refresh is an integrator/owner call on a later
pass); C2 — CPSE presence-only, settling fact named in the lane
section; C4 — Wang's January 2026 arrival makes him the pool's most
likely future PSE link when a carried roster names him.

**Verifier — look first at Gilchrist PERSON-000417 → PROG-000038**
(EVD-333610): the pool's only LINK whose witness text contains no
polymer word; it rests on RESEARCH FACULTY roster membership on the
PSE program's own people page, exactly as the lane flagged. A stricter
Gate B reading flips him to NO_WITNESS.
