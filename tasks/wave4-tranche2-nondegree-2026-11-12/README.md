# Wave 4 Tranche 2 — Non-Degree Light Sweep Packet

**Lane:** research only (no repo writes, no build). Date: 2026-11-12.
**Base:** origin/main `db51af32` (PR #310 head). Targets pulled from
`data/programs.csv` on that main: every `program_type != degree` row with
all five depth fields (`research_areas`, `specialty_processes`,
`specialty_materials`, `facilities_note`, `scale_band`) blank — **33 rows**.
**Paid calls: zero** (direct page fetches + two web searches only).
**Fetch budget:** ≤3 primary-source fetches per row; most rows took 1–2.

## Headline counts

| Outcome | Rows |
|---|---|
| Addressed | **33** |
| Fillable (≥1 depth cell proposed) | **9** |
| Fully REFUSED (all five cells) | **24** |
| Currency flags (STILL_UNCERTAIN currency) | **5** |

`scale_band` is REFUSED on **all 33 rows**: no row's own page publishes a
program enrollment or a qualitative size self-characterization that
converts under the S3 rule (2026-11-12). Headcounts seen en route were
member counts (AFFOA "over 125 members"), credit hours, and course hours —
none convert.

## Per-type summary

| Type | Rows | Fillable | Refused | Notes |
|---|---|---|---|---|
| center | 11 | 7 | 4 | Fillable: CICI, MAST, iCOUP, NIST ×3 groups, CDP. Refused: CPSE (URL mismatch), AFFOA, NextFlex, FutureTEX (all three #299-new; mission-level homepages only) |
| lab_facility | 3 | 2 | 1 | PCML is the sweep's fullest fill (4 of 5 cells); MDF takes research_areas only; ACAPP refused (ARL profile names it, states nothing about it) |
| certificate | 11 | 0 | 11 | Every certificate page is curriculum/admissions grain; research areas held per the certificate rule (curriculum is not research); none states facilities or enrollment |
| training | 3 | 0 | 3 | AGPA (K-12 outreach), PT&E and Paulson (course-catalog copy) |
| course | 3 | 0 | 3 | Penn concentration, Pitt concentration, CMU CPS minor — course grain by design, as expected |
| apprenticeship | 2 | 0 | 2 | GACC Polymer Process Technician (state feature article), WCTC Injection Mold Setup (catalog occupation page) |

## The 9 fillable rows

- **PROG-000051 PNNL Polymer and Composite Materials Laboratory** — 4 cells:
  research_areas (characterization_methods; composites_mechanics;
  degradation_biodegradation; recycling_circularity), specialty_processes
  (7 terms incl. composites_pultrusion, composites_filament_winding,
  composites_rtm_infusion, rubber_mixing_compounding), specialty_materials
  (composites_carbon; composites_frp; elastomers_rubber), facilities_note
  from the lab's own "Full Spectrum of Capabilities and Equipment" table.
- **PROG-000048 CICI** — research_areas (4 terms from the NSF IUCRC center
  page's research-focus list) + specialty_materials composites_frp.
- **PROG-000323 CDP** — research_areas characterization_methods
  (cross-cutting areas) + specialty_materials composites_unspecified
  ("Polymer Nanocomposite Dielectrics" thrust). Restraint: most CDP
  thrusts are ceramic dielectrics; only the polymer-named thrust carried.
- **PROG-000016 ORNL MDF** — research_areas only
  (additive_manufacturing_science; recycling_circularity), grounded on the
  facility page itself (polymer AM machine caption + thermoplastic
  circularity demonstration).
- **PROG-000049 MAST** — research_areas membranes_separations only;
  facilities_note refused (page's facilities language is generic, names
  no lab or equipment).
- **PROG-000052 iCOUP** — research_areas (characterization_methods;
  recycling_circularity); no §3.1 recycling process carried (pathway not
  specified as pyrolysis/solvolysis).
- **PROG-000053 NIST Polymers and Complex Fluids Group** — research_areas
  (characterization_methods; polymer_physics).
- **PROG-000054 NIST Functional Polymers Group** — research_areas
  (characterization_methods; membranes_separations; polymer_physics).
- **PROG-000055 NIST Polymer Processing Group** — research_areas
  characterization_methods only (rheology not carried — the rheo-Raman
  capability sits on the NIST-wide tools page, not this group's scope).

## Currency flags (5) — for the integrator; no status changes proposed

1. **PROG-000044 CCAC Polymer Technology Certificate** — STILL_UNCERTAIN.
   Only witness is the **archived 2024-2025 catalog** (crawled 2026-02-03).
   Settling fact: a current CCAC catalog/program page listing it as offered.
2. **PROG-000067 EMU Graduate Certificate in Polymers and Coatings** —
   STILL_UNCERTAIN. The stored URL resolves to EMU's generic online-programs
   landing page; the fetched text **does not name the certificate at all**.
   Settling fact: an EMU page/catalog entry naming it as currently offered.
3. **PROG-000149 Shawnee State Plastics Manufacturing Certificate** —
   STILL_UNCERTAIN. Catalog page returned **HTTP 403** (Acalog bot wall —
   availability signal, not evidence of absence).
4. **PROG-000151 Northwest State Plastics Manufacturing** — STILL_UNCERTAIN.
   Same 403 basis.
5. **PROG-000159 Central Community College (NE) Plastics Engineering
   Technology Certificate** — STILL_UNCERTAIN. Same 403 basis.

The other 28 rows are currency VERIFIED active on their own pages
(dated quotes in fills.csv), including CDP (projects funded Jul 2026–
Jun 2028 listed; Fall Meeting Nov 11–13, 2026 announced; now a former
NSF I/UCRC operating as an industry center) and FutureTEX (newly
launched; Gaston Kimbrell Campus named HQ of a 10-year initiative).

## Integrator flags (record hygiene, no action taken by this lane)

- **PROG-000040 CPSE URL/name mismatch:** the row is named "Center for
  Polymer Science and Engineering (CPSE)" but its stored URL is Lehigh's
  **Emulsion Polymers Institute** catalog PDF. CPSE appears in that text
  only as an affiliated center. Fills refused rather than taking EPI's
  research statement as CPSE's.
- **PROG-000054 / PROG-000055 shared stored URL:** both NIST group rows
  point at NIST's circular-economy tools page. Fills are grounded on each
  group's own NIST page, reached via that page's group links (URLs in
  fills.csv). **PROG-000055 name form:** data says "Polymer Processing
  Group"; NIST styles it "Polymers Processing Group".
- **PROG-000301 Davis Tech:** the row's `url` is a curriculum-evaluation
  PDF that failed to load from this lane; verdicts are grounded on the
  program's own page at the row's `public_door_url`.
- **PROG-000323 CDP** already carries the PR #299 posture (active industry
  center post-NSF); this sweep's currency check concurs.

## Weakest links

- **CICI currency** rests on a live center site (WVU Statler) + the current
  NSF IUCRC page; no dated 2025–26 activity quote found within the light
  fetch budget.
- **ACAPP currency** rests on a single facilities-list mention on ARL's
  tech-transfer page (crawled 2026-09-08) — name only, no dated activity.
- **MDF fills** are the thinnest of the fillable set: the facility's own
  page is marketing-level; ORNL's own news pages describe BAAM and
  additively reinforced thermoforming at MDF and would support a deeper
  facilities_note/process pass, but news copy was not treated as the
  facility page's equipment statement.
- Three Acalog catalogs (Shawnee, Northwest State, Central CC) were
  unreachable (403); those rows are REFUSED/STILL_UNCERTAIN on
  availability grounds only and should be re-run through any route that
  reads Acalog before being treated as settled.

## Federal-lab lead (no people work done, per lane rules)

The NIST Polymers and Complex Fluids Group page and the PNNL PCML page
name individual researchers (e.g., Vivek Prabhu at NIST; Wenbin Kuang and
Kevin Simmons as PCML contacts). Recorded here as a lead only for the
owner-gated federal-lab class; this lane made no links and no census.

## Files

- `fills.csv` — one row per target program (33): cell-by-cell proposals
  or REFUSED, verbatim witness quote(s) + URL, currency verdict + quote,
  and per-row notes.

## INTEGRATION RECORD (integrator of record: spaghetti, 2026-11-12)

Built on origin/main `db51af320d9c954090a89d2bc729acaca62a8969` (PR #310
head) in worktree `~/workspace/atlas-w4-nondegree-build-2026-11-12`,
branch `agent/spaghetti/wave4-tranche2-nondegree-2026-11-12`. The packet
files above stand **as authored**; everything below is the integrator's
record of application. Pre-pass backups:
`~/workspace/atlas-w4-nondegree-backups-2026-11-12/`. Build script:
`~/workspace/atlas-resync-2026-11-10/build_w4_nondegree.py` (packet
fills.csv read programmatically — applied values and witness quotes were
never retyped; every quoted fragment in the minted evidence was asserted
verbatim against the packet's witness text at build). ID allocation:
sibling tranche-2 units merge around this unit, so evidence IDs were
allocated from the brief's floor **EVD-334100** regardless of this base's
tree-wide maximum (EVD-334069, scanned at build); the gap
EVD-334070..EVD-334099 is those units' headroom, not this unit's
allocation. Local build only — nothing pushed, no PR.

**Depth fills — 9 rows filled, 33 evidence rows appended
(EVD-334100..EVD-334132; all `claim_type=scope`, `source_class=own_site`,
`tier_effect` from each subject row's own tier — all nine subjects are
tier A → `supports_A`; byte-prefix pure appends to
`data/evidence_programs.csv` verified):**

- **PROG-000051 PNNL Polymer and Composite Materials Laboratory 0/5 →
  4/5** (EVD-334108..EVD-334122, 15 rows): `research_areas` =
  `characterization_methods;composites_mechanics;degradation_biodegradation;recycling_circularity`,
  `specialty_processes` = `additive_manufacturing_polymer;composites_filament_winding;composites_pultrusion;composites_rtm_infusion;injection_molding;polymerization;rubber_mixing_compounding`,
  `specialty_materials` = `composites_carbon;composites_frp;elastomers_rubber`,
  `facilities_note` from the lab's own "Full Spectrum of Capabilities
  and Equipment" table. `scale_band` held (no enrollment published; lab
  facility). `thermoforming_vacuum` not carried — the table's "Vacuum
  forming" is ambiguous against §3.1 thermoforming, per the packet.
- **PROG-000048 CICI 0/5 → 2/5** (EVD-334102..EVD-334106):
  `research_areas` =
  `characterization_methods;composites_mechanics;degradation_biodegradation;recycling_circularity`,
  `specialty_materials` = `composites_frp`. Witness posture: the NSF
  I/UCRC center page is this row's own `url` and carries the
  center-authored overview (corroborated by the center's WVU Statler
  site); classed `own_site` on that basis — stated here for the
  verifier. Packet weakest link carried in the evidence notes: CICI
  currency rests on the live center site plus the current NSF page; no
  dated 2025-26 activity quote was found within the light fetch budget.
- **PROG-000323 CDP 0/5 → 2/5** (EVD-334131..EVD-334132):
  `research_areas` = `characterization_methods`, `specialty_materials` =
  `composites_unspecified`. Restraint per the packet: most CDP thrusts
  are ceramic dielectrics/piezoelectrics — only the polymer-named thrust
  ("Polymer Nanocomposite Dielectrics") and the characterization
  cross-cutting areas are carried. `specialty_processes` +
  `facilities_note` held (the research page names neither). The sweep's
  currency check concurs with the PR #299 posture.
- **PROG-000016 ORNL Manufacturing Demonstration Facility 0/5 → 1/5**
  (EVD-334100..EVD-334101): `research_areas` =
  `additive_manufacturing_science;recycling_circularity`, grounded on
  the facility page itself. `specialty_processes` held (no §3.1 process
  at cell grain; polymer AM appears as a photo caption, carried in
  research_areas only); `facilities_note` held (the page enumerates no
  equipment; ORNL news copy was not treated as the facility page's
  equipment statement — deeper-pass lead stands in the packet).
- **PROG-000049 MAST 0/5 → 1/5** (EVD-334107): `research_areas` =
  `membranes_separations`. `facilities_note` refused — the page's
  facilities language is generic and names no lab or equipment.
- **PROG-000052 iCOUP 0/5 → 1/5** (EVD-334123..EVD-334124):
  `research_areas` = `characterization_methods;recycling_circularity`.
  No §3.1 recycling process carried — the pathway is not specified as
  pyrolysis/solvolysis at cell grain.
- **PROG-000053 NIST Polymers and Complex Fluids Group 0/5 → 1/5**
  (EVD-334125..EVD-334126): `research_areas` =
  `characterization_methods;polymer_physics`.
- **PROG-000054 NIST Functional Polymers Group 0/5 → 1/5**
  (EVD-334127..EVD-334129): `research_areas` =
  `characterization_methods;membranes_separations;polymer_physics`.
- **PROG-000055 NIST Polymer Processing Group 0/5 → 1/5** (EVD-334130):
  `research_areas` = `characterization_methods` only — rheology not
  carried (the rheo-Raman capability sits on the NIST-wide tools page,
  not this group's own scope statement).

Changed program rows carry exactly the packet's filled cells plus
`last_verified` → 2026-11-12 and no other cell changes (row-level and
raw-line diffs vs backups verified) — with one precision: PROG-000323's
`last_verified` already read 2026-11-12 from its PR #299 creation, so
its only changed cells are the two depth fields. `scale_band` stays
blank on all 33 rows (packet refused it 33/33 under S3).

**REFUSED — 24 rows byte-identical, no `last_verified` movement**
(raw-line identity vs backups verified): PROG-000021 (AGPA training),
PROG-000034 (Penn concentration, course), PROG-000040 (CPSE, center),
PROG-000041 (Pitt concentration, course), PROG-000042 (CMU CPS minor,
course), PROG-000044 (CCAC certificate), PROG-000046 (GACC
apprenticeship), PROG-000056 (ACAPP, lab_facility), PROG-000067 (EMU
certificate), PROG-000068 (Westmoreland certificate), PROG-000070
(Lehigh Online PSE certificate), PROG-000120 (Cerritos certificate),
PROG-000149 (Shawnee certificate), PROG-000151 (Northwest State
certificate), PROG-000158 (AIM PT&E, training), PROG-000159 (Central CC
certificate), PROG-000161 (WCTC apprenticeship), PROG-000301 (Davis
Tech certificate), PROG-000302 (Paulson, training), PROG-000303 (UWM
certificate), PROG-000329 (AFFOA), PROG-000330 (NextFlex), PROG-000331
(FutureTEX), PROG-000342 (Macomb certificate). The three #299-new
centers' homepages are mission-level only — their depth fields stay
honestly empty.

**Currency flags — 5, recorded here only; NO status changes:**
PROG-000044 CCAC Polymer Technology Certificate — STILL_UNCERTAIN, only
witness the archived 2024-2025 catalog (settling fact: a current CCAC
catalog/program page listing it as offered). PROG-000067 EMU Graduate
Certificate in Polymers and Coatings — STILL_UNCERTAIN, the stored URL
resolves to EMU's generic online-programs landing page and the fetched
text does not name the certificate (settling fact: an EMU page/catalog
entry naming it as currently offered). PROG-000149 Shawnee State,
PROG-000151 Northwest State, PROG-000159 Central Community College —
STILL_UNCERTAIN on HTTP 403 (Acalog bot wall): an availability signal,
explicitly **not** evidence of absence; the packet recommends a re-run
through any route that reads Acalog before these are treated as
settled. The other 28 target rows are currency VERIFIED active on their
own pages per the packet.

**Integrator flags — record-only, no cell changes beyond the packet's
fills:** PROG-000040's stored `url` is Lehigh's **Emulsion Polymers
Institute** catalog PDF, not a CPSE page — CPSE's fills were refused
rather than taking EPI's research statement as CPSE's, and no EPI
statement was substituted at integration. PROG-000054 / PROG-000055
share one stored `url` (NIST's circular-economy tools page); their
fills are grounded on each group's own NIST page (the evidence
`source_ref`s carry those pages), reached via that page's group links.
PROG-000055's carried name is "Polymer Processing Group"; NIST styles
it "Polymers Processing Group" — no rename in this unit. PROG-000301's
`url` (a curriculum-evaluation PDF) failed to load for the lane; its
verdicts rest on the program's own page at the row's `public_door_url`.

**Federal-lab lead — record-only:** the NIST Polymers and Complex
Fluids Group page and the PNNL PCML page name individual researchers
(e.g. Vivek Prabhu at NIST; Wenbin Kuang and Kevin Simmons as PCML
contacts). Recorded for the owner-gated federal-lab class; this unit
made **no people changes** — no links, no census, no people evidence.

**Ecosystem rollups:** fills change no program name or `url`, so no
rollup movement is expected; the §4.11 V-16 rollups for the seven
affected institutions (ORG-002814 ORNL, ORG-002817 PNNL, ORG-002818
Ames/iCOUP, ORG-002819 NIST, ORG-002842 WVU/CICI, ORG-002843 MAST,
ORG-002851 NC State/CDP) were recomputed from the built tree and match
the carried `polymer_program_name` / `polymer_program_url` exactly —
no drift found, `data/ecosystem.csv` untouched.

**Counts (unit + filter):** programs: 9 changed (depth cells +
`last_verified` discipline above), 24 target rows and all other 181
rows byte-identical, 0 created, 0 removed. People: 0 changed, 0
created. Ecosystem: 0 rows changed. Evidence: 33 rows appended, all to
`data/evidence_programs.csv` (EVD-334100..EVD-334132). Next frees:
**PROG-000348 / PERSON-002168 / EVD-334133** (tree maxima on the base
stood at PROG-000347 / PERSON-002167 / EVD-334069; this unit consumed
no program or person IDs).

**ADDENDUM — verifier ruling + fix (2026-11-12):** independent
verification (report:
`~/workspace/polymer-atlas-staging/working/wave4-2026-11-12/tranche2-nondegree/nondegree-verification-2026-11-12.md`)
passed checks 1–4, 6, 7 and ruled check 5 **against the build**: the
six CICI/MAST evidence rows EVD-334102..EVD-334107 were classed
`own_site` with `tier_effect=supports_A`, but their cited pages sit on
NSF's domain (`iucrc.nsf.gov`) — a funder directory witness, not the
centers' own sites (§4.13; PR #293 precedent: NSF-directory-sourced
scope evidence classed `directory`). Directory evidence caps at
`supports_B`. The builder's ground (the IUCRC page is each row's
carried `url` and the overview is center-authored) does not carry:
authorship of text inside a third party's listing does not make the
listing the entity's own site. **Fix applied in this unit, exactly as
specified:** EVD-334102..EVD-334107 now read `source_class=directory`,
`tier_effect=supports_B`; no other cell of those rows changed, no
program cells changed, no other evidence rows changed (raw-line diff
vs the pre-fix build state = exactly the six lines, two cells each).
The fills themselves stand on the directory evidence — evidence rows
do not set record tiers. The depth-fill summary above ("all
`source_class=own_site` … `supports_A`") describes the pre-fix build
and is superseded by this addendum for the six CICI/MAST rows.
**Gate consequence (found at the fix pass, 2026-11-12):**
`scripts/validate.py` re-run on the fixed tree FAILS with 2 errors —
`V-25: programs PROG-000048 must-have claim scope supported only at B
strength but tier is A` and the same for PROG-000049. PROG-000048 and
PROG-000049 are tier-A records whose must-have scope claim, after this
reclass, is supported only at B strength; no other supports_A scope
evidence for these two records exists in the tree. The six-row fix
stands as specified, but the unit does NOT pass the validator until
one of these lands (integrator/owner adjudication, NOT applied here):
(a) supports_A `own_site` scope evidence for each center from its own
site (CICI: WVU Statler `compositescici.statler.wvu.edu`; MAST:
`mastcenter.org` — the strengthening route the verifier named), or
(b) a ruling on the two records' tiers. The unit was therefore NOT
committed or rebased at this pass; the worktree holds the build + fix
+ this addendum, uncommitted, on base `db51af32`.

**ADDENDUM 2 — own-site strengthening applied (2026-11-12):**
integrator adjudication took route (a) above — strengthen from the
centers' own sites; neither record's tier was touched. Both own sites
were fetched directly on 2026-11-12 and each carries a usable scope
statement, minted as one `scope` / `own_site` / `supports_A` row per
center, appended after this unit's block: **EVD-334133**
(PROG-000048, CICI) cites the center's WVU Statler site
(`https://compositescici.statler.wvu.edu/`), quoting its mission
statement verbatim: "The mission of CICI is to accelerate the
adoption of polymer composites and innovated construction material
into infrastructure and transportation applications through
collaborative research." **EVD-334134** (PROG-000049, MAST) cites
the center's own site (`https://mastcenter.org/`), quoting verbatim:
"Our Center focuses on new membrane materials and processes and
their industrial applications. Membranes are made of polymers,
inorganic materials, or hybrids of the two. They are used for the
separation and purification of chemical compounds, biological
molecules, and other process streams." The six directory rows
EVD-334102..EVD-334107 stand as reclassed; the fills are unchanged.
Re-run after strengthening: `scripts/validate.py` → "OK —
validation passed." (the two V-25 errors are cured) and
`scripts/check_row_loss.py --base origin/main` → green. The unit
then proceeded to commit + rebase onto current main for its PR.

---

## Renumber addendum (2026-11-12, post-proof-pass)

The first proof pass against merged main failed validator V-22 only:
this unit's five programs-shard evidence rows EVD-334130..EVD-334134
collided with the Harvard unit's people-shard rows of the same IDs
already on main (PR #325) — evidence IDs are global across shards, and
the two units' allocation floors overlapped. The five rows were
renumbered in place, order preserved, only the evidence_id cell
changed:

- EVD-334130 → EVD-334139
- EVD-334131 → EVD-334140
- EVD-334132 → EVD-334141
- EVD-334133 → EVD-334142 (CICI own-site strengthening row; content unchanged)
- EVD-334134 → EVD-334143 (MAST own-site strengthening row; content unchanged)

The unit's evidence block on the final tree is therefore
EVD-334100..EVD-334129 + EVD-334139..EVD-334143 (35 rows). References
inside the strengthening rows' notes to EVD-334102..EVD-334107 point
at this unit's reclassed depth-fill rows, which were not renumbered
and remain accurate.
