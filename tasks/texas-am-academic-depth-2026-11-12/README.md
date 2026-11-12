# Wave 3 — Texas A&M lane packet (2026-11-12)

**Lane type:** PACKET ONLY. No repo data edited, nothing pushed. Integrator
applies from `proposed_rows.csv` + `links.csv` in this folder.
**Basis data:** Atlas main `f2c7c814`, read from
`~/workspace/atlas-p2-2026-11-12/data/` — Texas A&M University is
ORG-004656 (ecosystem `university_college`, College Station, Brazos County,
TX; `polymer_program=false`, no program rows at basis).
**Plan:** `working/wave3-batch-plan-2026-11-12.md`, lane 1 — program
discovery first (21 recorded people, 0 program rows), then depth + links.
**Vocabulary law:** SCHEMA v1.13.1 §3.1/§3.2/§3.5, §4.11 inclusion prongs,
§1 R2 materials-candidate legs, S3 scale-band conversion. Out-of-vocabulary
material is HELD verbatim below, never slug-invented.
**Fetch accounting:** primary-source pages read — PTC 4 (faculty roster,
home, consortia, research), MSEN 3 (facts, catalog department page,
academics), SoMF 1 (home; iLab/research pages read via search extract),
people spot-checks 2 (Wang lab page, M. Grunlan BME profile). All free
routes. **Paid calls: zero, all providers.**

## Counts (unit + filter)

- Program units tested at Texas A&M (tamu.edu pages): **5** — Polymer
  Technology Center, MSEN degrees, Soft Matter Facility, PTC Polymer
  Specialty Certificate, departmental degree programs (ChE/ME/Chem/BME/
  AERO) as a class. **3 proposed rows, 2 held** (below).
- Depth cells filled across the 3 proposed rows (of the 5 tracked cells —
  specialty_processes, specialty_materials, research_areas, facilities_note,
  scale_band): **6** — MSEN 3 (research_areas, facilities_note, scale_band),
  PTC 2 (research_areas, facilities_note), SoMF 2 (research_areas,
  facilities_note). Specialty cells are empty on all three, by the rules
  stated per row — not by omission.
- Link pass: **21 recorded people** at ORG-004656 (the full recorded pool,
  all with empty `program_org_id` at basis) → **18 LINK** (5 to the
  proposed MSEN degree row, 13 to the proposed PTC center row),
  **3 NO_WITNESS**. No person was linked on anything but an A&M page.

## Program discovery — adjudications

### PROPOSED TAMU-W3-1 — Materials Science and Engineering (degree)
Settled by the university catalog's department page and the department's
own facts/academics pages.

- Inclusion, two independent legs: **§4.11 prong (b)** — the degree's own
  published description names a polymer research area: the catalog MS page
  and the department facts page both list **"Polymers, Soft Matter and
  Composites"** among the department's research areas; and **R2 leg (c)** —
  at least two of the unit's own faculty state polymer-specific research
  areas on institution pages; the count is **4** among the catalog's own
  faculty list (Hung-Jue Sue — fracture/toughening of polymers and blends;
  Svetlana A. Sukhishvili — polymer and polymer-nanocomposite assemblies;
  Michael S. Dimitriyev — self-assembling/disassembling polymer networks;
  Pavan V. Kolluru — mechanical behavior of polymers, 3D-printed polymers).
- Credentials as the institution publishes them: BS, MS (thesis and
  non-thesis), MEng, PhD, plus an undergraduate minor → row carries
  `bs;ms;phd;minor` (MEng rides `ms`; no `meng` value exists in the enum).
- Depth draft: `research_areas=polymer_physics` (the §3.5 honest fit for
  the published "Polymers, Soft Matter and Composites" area — structure–
  property of polymer systems). Specialty cells **empty**: a general
  materials department states no polymer-specific process/material
  specialty on its own pages (matches the Michigan/CWRU/Lehigh MSE-row
  precedent). `scale_band=large`: the department publishes total
  enrollment **507 students (Fall 2026**, facts page, THECB-sourced) —
  published program enrollment converts under S3 (>120 → large); the
  academics page's rounded figures (~300 undergrad + ~190 graduate) land
  in the same band. `facilities_note` from the catalog's facility list.
- Held from this row: CIP 14.1801 (seen only via a third-party aggregator
  quoting TAMU) — `cip_code` left empty for the integrator's IPEDS
  completions pull, per §4.11 (CIP is data, never evidence).

### PROPOSED TAMU-W3-2 — Polymer Technology Center (center)
Settled by ptc.tamu.edu (faculty roster, consortia and research pages,
all read 2026-11-12).

- Inclusion: **§4.11 prong (a)** — a center named for polymers on the
  institution's own pages. PTC is a Texas A&M Engineering Experiment
  Station (TEES) research organization directed by Hung-Jue Sue, with
  **36 faculty rostered** across chemical, materials, mechanical,
  biomedical and aerospace engineering, chemistry, and allied units.
  It operates two current industrial consortia — **PTIC** (Polymer
  Technology Industrial Consortium, est. 1986) and **SCRATCH** (Scratch
  Behavior of Polymers Consortium, est. 2001) — whose members sponsor
  research individually and jointly.
- Depth draft: `research_areas=polymer_physics` — the center's own
  research page states its efforts are "largely concerned with
  establishing structure-property relationships for polymeric materials
  and composites," and SCRATCH's stated aim is "a generic
  structure-property relationship on scratch behaviors in polymers."
  `engagement_modes=research_collaboration` (consortia pages publish
  industry-sponsored collaboration; no current page publishes a testing
  or facility-access offer to non-members, so no further modes).
  `facilities_note` carries the consortia-laboratory list from the
  center's own brochure — **flagged dated (2019)** in the row notes for
  integrator re-verification.
- **Held verbatim** from the research page (research topics, not the
  center's stated specialties — specialty cells stay empty, the wave-2
  discipline): "high performance functional polymers for nanotechnology,
  biotechnology and micro-/nano-electronics packaging applications";
  "structure-property relationship in polymers, blends, **polyolefin
  films, fiber-reinforced composites, adhesives and nanocomposites**";
  "strengthening and toughening of polymers". None of these is a §3.2
  slug as stated (`nanocomposites` is not one — cf. the UConn wave-2
  correction); mapping them onto `composites_unspecified` etc. is the
  integrator's call, not the lane's.
- APPEAL (Consortium for Advancing Performance Polymers in Energy
  Applications, est. 2011) appears in the center's 2018–2019 materials
  but the **current consortia page lists exactly two** affiliated
  consortia (PTIC, SCRATCH) — APPEAL is treated as no longer current,
  and no consortium is proposed as a row in any case (they are the
  center's engagement surface, not program-grain units).

### PROPOSED TAMU-W3-3 — Soft Matter Facility (SoMF) (lab_facility)
Settled by somf.engr.tamu.edu and the facility's iLab service page.

- Inclusion: **§4.11 prong (c)** — a facility whose own offer states
  polymer characterization services: "the only user facility in Texas
  dedicated to state-of-art characterization of multifunctional soft
  materials"; its iLab page opens on "Multifunctional **polymer-based**
  and soft materials." Directed by Svetlana A. Sukhishvili (MSEN);
  multi-college (Engineering, Arts & Sciences, Agriculture & Life
  Sciences); sustainable core facility since September 2021.
- Depth draft: `research_areas=characterization_methods` and **both
  specialty cells empty**, exactly per §4.11's characterization-facility
  rule. `engagement_modes=testing_characterization_access;
  lab_facility_access` (the AMLCI Characterization Facility precedent).
  `facilities_note` from the home page: 3,100 sq. ft., TCF building,
  1313 Research Parkway; suites for molecular characterization,
  nanostructure analysis, thin-film/interfacial studies, and
  thermomechanical evaluation. Square footage never converts to
  scale_band (S3) — the cell stays empty.

### HELD — PTC Polymer Specialty Certificate
A 2017 PTC newsletter states the center "offers a Polymer Specialty
Certificate Program, the first professional development program of its
kind in the state of Texas, for undergraduate and graduate students."
No current ptc.tamu.edu or catalog page for the certificate was found
in this lane's fetches. **No row proposed.** Settling fact: a current
institution page (catalog or ptc.tamu.edu) carrying the certificate —
if found, it is a `certificate` row under PTC and the natural primary
link for no one (certificates do not outrank degrees under the
degree-primary rule).

### HELD — departmental degree rows (ChE, ME, Chemistry, BME, AERO)
Tested as a class and **not proposed**. None of these degrees' own
published descriptions names a polymer track, concentration, or
research area (§4.11 prong (b) fails), and none houses a polymer-named
unit (prong (a) fails — PTC sits above the departments, in TEES).
The college's degree index says chemical engineering students explore
products "such as fuels, pharmaceuticals and polymers" — a generic
phrase, held under the wave-2 rule, not a named polymer area.
Consequence, intended: the recorded polymer faculty of these
departments link to PTC (their witnessed polymer home) or stand
NO_WITNESS — the department degrees are not minted to catch them.
Settling fact for any future row: that department's own catalog or
program page naming a polymer track/concentration/research area.

### NOTED, no row — a future M.S. in Polymer Science and Engineering
SoMF's iLab page says the facility will "facilitate the establishment
of a M.S. degree program in polymer science and engineering." That is
an intention, not a program: no catalog listing exists. Recorded here
so a future lane checks for it; minting a row now would fabricate one.

## Link pass — adjudications (21 people)

Rule applied: Gate A (current faculty styling on an A&M page) + Gate B
(person-level polymer-research witness on an A&M page) + a program
witness tying the person to a proposed row; `program_org_id`
single-valued — **degree program primary** where the person is the
degree unit's own faculty, else the witnessed center (PTC).

**To TAMU-W3-1 (MSEN degree) — 5.** The current graduate catalog's
MSEN faculty list styles all five as Materials Science & Engr faculty:
Sue (PERSON-000750), Sukhishvili (PERSON-000760), Dimitriyev
(PERSON-000829), Kolluru (PERSON-001366), and **Ware (PERSON-000729)**
— Ware is also on the PTC roster, but the degree-primary rule puts
him here; his PTC membership is banked in this note, not in a second
value. Sukhishvili's SoMF directorship is likewise banked here; her
`program_org_id` is the degree row.

**To TAMU-W3-2 (PTC) — 13.** Each is named on the current PTC faculty
roster (read 2026-11-12), with Gate B from their recorded institution
profiles: Lutkenhaus (000710), Darensbourg (000712), Wooley (000716),
Michaudel (000736), M. Green (000766), Naraghi (000787), Pentzer
(000804), M. A. Grunlan (000975), Q. Wang (001000), Elabd (001091 —
he also carries a dedicated PTC profile page, the roster's strongest
form of witness), Bergbreiter (001365), Xie (001367), Muliana (001383).

**NO_WITNESS — 3.**
- **Jaime C. Grunlan (PERSON-000713, Mechanical Engineering).** His
  personal gates are met on his ME profile (polymer nanocomposites) —
  what is missing is purely a program witness: he is **not on the
  current PTC roster** (his BME counterpart M. A. Grunlan is), and ME
  carries no proposed row (held, above). The Atlas's strongest
  unlinked A&M polymer person; a PTC roster addition settles him
  instantly.
- **Hong-Cai "Joe" Zhou (PERSON-000752, Chemistry).** Not on the PTC
  roster and not in the current MSEN catalog faculty list. Gate B is
  also borderline on its own terms — his stated program is
  metal-organic frameworks; "porous polymer networks" is the
  secondary line. NO_WITNESS on both counts; do not force.
- **Daniel L. Alge (PERSON-000808, Biomedical Engineering).** Hydrogel
  Gate B is met on his BME profile, but he is not on the PTC roster
  and BME carries no proposed row. Same shape as J. Grunlan.

## Weakest links (flagged for the verifier)

1. **Qingsheng Wang → PTC (PERSON-001000) — the weakest LINK.** The
   roster witness is solid, but his research center of gravity is
   process safety; Gate B rests on one line of his own lab page
   ("Flame retardant polymers," alongside "Soft matter for safety and
   sustainability"). The link stands — PTC itself styles him faculty
   and polymer work is stated — but if any link in this packet is
   re-checked first, it is this one.
2. **Emily Pentzer → PTC, not MSEN (PERSON-000804).** A styling
   conflict, documented rather than resolved: the current PTC roster
   styles her "Associate Professor — Chemistry and Materials Science
   & Engineering," and the 2023–24 catalog archive listed her as MSEN
   faculty, but the **current graduate catalog's MSEN faculty list
   omits her**. The lane applied the degree-primary rule strictly —
   degree linkage requires the degree unit's *current* own styling —
   so she takes the center. If the integrator finds a current MSEN
   page styling her as faculty, she moves to TAMU-W3-1.
3. **PTC facilities_note** rests on the center's 2019 brochure; the
   laboratory list may have turned over. Dated in the row's notes.

## Title-refresh flags (P1 rider — lane flags, integrator applies)

- **Pentzer (PERSON-000804):** Atlas carries "Professor in the
  Department of Chemistry"; the current PTC roster styles her
  *Associate* Professor. One of the two is stale — her Chemistry
  profile page settles it; the lane did not spend the fetch.
- **Ware (PERSON-000729):** PTC roster styles him *Associate*
  Professor, but the current MSEN catalog list styles him **Professor**
  — the Atlas styling stands on the fresher witness; no change
  recommended, noted so the discrepancy is not re-litigated.

## Integrator notes

- Allocate PROG ids above the tree-wide maximum at application;
  TAMU-W3-1/2/3 are packet placeholders only.
- Ecosystem rollup (V-16): on application, ORG-004656's
  `polymer_program` flips to true and `polymer_program_name` becomes
  the generated rollup — by type precedence (degree, center,
  lab_facility): "Materials Science and Engineering; Polymer
  Technology Center; Soft Matter Facility (SoMF)", with
  `polymer_program_url` = the MSEN row's URL.
- Evidence rows to mint at application: one `scope`/`own_site` row per
  proposed program (tier_effect supports_A — all three rows rest on
  the institution's own pages) and one per LINK (18), each citing the
  witness URL in `links.csv`.
- **Discovery residue (not this packet's scope):** the current PTC
  roster names 18 further faculty with no Atlas record — Akbulut,
  Asadi, Balbuena, Bluemel, Borazjani, Cagin, Castaneda, Hsiao, Hung,
  Jin, Liang, Monroe, Patterson, Pharr, Tu, Ufodike, S. Wang,
  Whitcomb. Several state polymer research on their own pages (Cagin,
  Asadi, Bluemel at minimum). They are the candidate pool for a future
  scoped professor pass at A&M; this lane created no people records.

---

## Integration record (integrator of record, 2026-11-12)

**Applied** on branch `agent/spaghetti/wave3-texas-am-depth` from
origin/main `f2c7c814dfe88e60b5c337aa9f144754ea14d046` (build only —
not pushed; PR follows the standing batched-approval pattern).
Build script: `~/workspace/atlas-resync-2026-11-10/build_texasam_wave3.py`;
pre-pass backups: `~/workspace/atlas-wave3-texasam-backups-2026-11-12/`.

- **Program rows created (3)** — the packet's `proposed_rows.csv`
  applied verbatim with allocated IDs, in packet order:
  **PROG-000306** Materials Science and Engineering (degree;
  `scale_band=large` as drafted; `cip_code` left blank — the packet
  held CIP 14.1801 for an IPEDS pull that has not run, and no CIP is
  asserted); **PROG-000307** Polymer Technology Center (center);
  **PROG-000308** Soft Matter Facility (SoMF) (lab_facility).
  Allocation note: this tree's own scan shows max PROG-000304 on main;
  PROG-000305 was taken by the Minnesota unit ahead of this one in
  merge order, so this unit allocates 306–308.
- **Links applied (18 of 21)** — 5 to PROG-000306 (Sue 000750,
  Sukhishvili 000760, Dimitriyev 000829, Kolluru 001366, Ware 000729)
  and 13 to PROG-000307 (Lutkenhaus 000710, Darensbourg 000712,
  Wooley 000716, Michaudel 000736, M. Green 000766, Naraghi 000787,
  Pentzer 000804, M. A. Grunlan 000975, Q. Wang 001000, Elabd 001091,
  Bergbreiter 001365, Xie 001367, Muliana 001383). Changed fields per
  person: `program_org_id` + `last_verified` (2026-11-12) only.
  Ware's PTC roster membership is banked as evidence row EVD-333645
  only — his `program_org_id` is the degree row (single-valued rule).
  NO_WITNESS (J. Grunlan 000713, Zhou 000752, Alge 000808): no link,
  no person evidence row; their records are byte-untouched.
- **Evidence minted (25 rows)** — programs EVD-333635..EVD-333640
  (existence + scope per created row, `own_site`, `supports_A` from
  the rows' drafted tier A); people EVD-333641..EVD-333659 (18 LINK
  rows + Ware's banked row). Allocation starts at EVD-333635 per the
  serial sequence — preceding wave-3 units consumed EVD-333539..
  EVD-333634 on their own branches (this tree's scan max is
  EVD-333538; the gap does not exist on this branch and was not
  backfilled). **Next free: PROG-000309 / EVD-333660.**
- **Ecosystem rollup (V-16) recomputed for ORG-004656** in the same
  pass: `polymer_program` false → true; `polymer_program_name`
  (blank) → "Materials Science and Engineering; Polymer Technology
  Center; Soft Matter Facility (SoMF)" — sort working: program-type
  precedence degree < center < lab_facility, name order within type
  (one row per type here); `polymer_program_url` (blank) →
  https://engineering.tamu.edu/materials/academics/ (the first sorted
  row's URL); `last_verified` → 2026-11-12. Matches the packet's
  predicted rollup exactly.
- **Title flags: NO changes applied** (integrator ruling). Pentzer
  PERSON-000804's rank conflict is carried verbatim: the record reads
  "Professor in the Department of Chemistry"; the current PTC roster
  styles her "Associate Professor — Chemistry and Materials Science
  & Engineering"; the current graduate catalog's MSEN faculty list
  omits her (the 2023–24 catalog listed her). Unsettled — her
  `program_org_id` is PROG-000307 as adjudicated, and the conflict is
  quoted in her link evidence row EVD-333651. Ware PERSON-000729
  needs no change: the current catalog styles him Professor, backing
  the record; the PTC roster's "Associate Professor" styling is noted
  in the packet.
- **Not created:** the PTC Polymer Specialty Certificate row and all
  departmental degree rows (held at lane level; settling facts stand
  in the packet); no new people records — the 18 unrecorded
  PTC-roster faculty named in the packet remain future-pass residue,
  in the packet only.
- **Gates:** `scripts/validate.py` — "OK — validation passed" (174
  program rows = 171 + 3 created; 40,626 evidence rows = 40,601 + 25
  minted; 1,450 people rows, count unchanged; no warning names
  ORG-004656 or PROG-000306..308). `scripts/check_row_loss.py --base
  origin/main` — "row-loss guard: OK — no keyed row removed from
  data/ since origin/main (merge-base f2c7c814df)". No REMOVALS.csv.
- **Push allowlist (9 paths, exact):** data/programs.csv,
  data/people.csv, data/ecosystem.csv, data/evidence_programs.csv,
  data/evidence_people.csv, tasks/QUEUE.md,
  tasks/texas-am-academic-depth-2026-11-12/README.md,
  tasks/texas-am-academic-depth-2026-11-12/proposed_rows.csv,
  tasks/texas-am-academic-depth-2026-11-12/links.csv. Excluded EOL
  phantoms (CRLF→LF noise only; empty diff under
  `git diff --ignore-cr-at-eol`, never to ride the push):
  tasks/michigan-state-academic-depth-2026-11-12/fills.csv,
  tasks/michigan-state-academic-depth-2026-11-12/links.csv,
  tasks/nc-state-academic-depth-2026-11-11/fills.csv,
  tasks/nc-state-academic-depth-2026-11-11/links.csv.

---

## Addendum — Sukhishvili banked SoMF row (integrator ruling, 2026-11-12)

Append-only follow-up to close the asymmetry flagged in item 8 above:
exactly one row appended to `data/evidence_people.csv` — **EVD-333660**,
PERSON-000760 (Svetlana A. Sukhishvili) → PROG-000308 (Soft Matter
Facility), claim_type `scope`, source_class `own_site`, witness
https://somf.engr.tamu.edu/ (the SoMF page the packet cites; it carries
her directorship of the facility), tier_effect `supports_A` (her
record's tier A), mirroring the column shape and banked-witness form of
Ware's EVD-333645. The row is a **banked affiliation only**: her
`program_org_id` stays PROG-000306 (single-valued primary stands); no
other file or field changed.

- **Evidence range for this build is now EVD-333635..EVD-333660
  (26 rows)** — the original 25 plus this addendum row.
- **Next free evidence ID: EVD-333661.**
- **Gates re-run after the append:** `scripts/validate.py` — "OK —
  validation passed" (40,627 evidence rows = 40,601 base + 26 minted).
  `scripts/check_row_loss.py --base origin/main` — "row-loss guard:
  OK — no keyed row removed from data/ since origin/main (merge-base
  f2c7c814df)".
