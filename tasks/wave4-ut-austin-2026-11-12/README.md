# Wave 4 school pass — University of Texas at Austin (ORG-004651)

**Lane type:** research only (packet; no repo data written, no branch, no PR).
**Base:** origin/main `79b1f42b` (post PR #299), re-derived from `data/ecosystem.csv`,
`data/programs.csv`, `data/people.csv` at that head on 2026-11-12.
**Paid calls: zero.** All sources are the institution's own pages (utexas.edu
domains), fetched directly or read via free search extracts.

## Verdict summary

Counts state unit + filter, per AGENTS.md §7.

### 1. PROG-000122 depth fills — VERIFIED for 3 of 5 depth cells

Unit: the one carried program row at ORG-004651 (PROG-000122, Materials Science
and Engineering, degree) × its five depth cells (`research_areas`,
`specialty_processes`, `specialty_materials`, `facilities_note`, `scale_band`).

- `research_areas` — 4 terms proposed, each with its own quote in fills.csv:
  `biomedical_polymers`, `membranes_separations`, `composites_mechanics`,
  `characterization_methods`. All rest on the program's own research-theme
  pages served by the Texas Materials Institute (TMI), the unit that operates
  the MSE Graduate Program ("To operate the graduate degree program in
  Materials Science and Engineering (MS&E)" — TMI About page).
- `specialty_materials` — `composites_unspecified` proposed from the Polymers
  and Biomaterials page's own framing sentence ("…structural composites…");
  the composite type is not stated, so the §3.2 unspecified term is the honest
  tag. No other §3.2 family or resin is named at program level.
- `facilities_note` — proposed from the TMI About page's Facilities section
  (65+ large instruments, three facilities, $40M characterization/processing
  infrastructure, shared user access).
- `specialty_processes` — HELD, no fill proposed. The program's own pages name
  no §3.1 process; "materials synthesis and processing" (TMI Research page) is
  generic and maps to no §3.1 term. Settling fact: a program page naming a
  §3.1 process (e.g. polymerization, fiber formation) as program work.
- `scale_band` — STILL_UNCERTAIN, no fill proposed. The program publishes no
  enrollment figure. Figures that never convert under the S3 rule: "over 100
  affiliated faculty" (faculty count, TMI About), "over 200 active members"
  (facility user base, not students), IPEDS completions 27 in 2024 (completion
  flow, already on the row). Settling fact: a TMI/MSE page publishing the
  graduate program's enrollment or a qualitative size self-characterization.

### 2. People links — 9 LINK, 3 NO_WITNESS (of 12)

Unit: people records with `institution_org_id = ORG-004651` and empty
`program_org_id` on origin/main 79b1f42b. Filter: all 12 such records (the
institution carries exactly 12 people records, all unlinked).

- **LINK → PROG-000122 (MSE Graduate Program), 3:** Dodabalapur
  (PERSON-000675), Marras (PERSON-000674), Page (PERSON-000699). Witness =
  program membership on TMI's own pages: the research-theme rosters style
  their listed faculty "Associated Graduate Program Faculty," and the
  Graduate Studies Committee page — the program's own membership roster —
  states the GSC "is comprised of Texas Materials Institute associated
  faculty who are active participants in the MS&E graduate program."
  Dodabalapur carries a full GSC entry plus the Electronic and Photonic
  Materials roster entry with his polymer statement on the same page. Page
  and Marras appear on the GSC roster; Page is corroborated by the program's
  Prospective Students page, which lists him among "Recruiting Faculty for
  Fall 2027 admissions."
- **LINK → proposed Chemical Engineering department row (packet-local key
  NEW-UTA-CHE), 6:** Lynd (PERSON-000672), Sanoja (PERSON-000676), Ganesan
  (PERSON-000696), Rosales (PERSON-000730), Freeman (PERSON-000742), Peppas
  (PERSON-000761). All are McKetta Chemical Engineering faculty (Gate A) with
  polymer research stated on the institution's own pages (Gate B); under the
  primary-home rule their home department's degree row is the primary
  program once created. Each person's department page or department-hosted
  profile carries the polymer statement quoted in links.csv; Ganesan's
  department-hosted profile ties him to the department's named polymer
  research area verbatim ("Research Areas: Advanced Materials, Polymers &
  Nanotechnology").
- **BANKED-PENDING (M-WET), noted on 2 LINK rows:** Freeman and Sanoja each
  hold a profile on the M-WET center's own site (mwet.utexas.edu/profiles/…);
  Freeman's ChemE page additionally styles him "Center for Materials For
  Water and Energy Systems (MWET), Director." These bank against the M-WET
  EFRC center row a separate integration unit is creating at this
  institution; they are not drafted here. Ganesan and Lynd show only an
  indirect M-WET tie (M-WET student profiles naming them as Ph.D. advisors)
  — flagged in their link notes, not banked.
- **NO_WITNESS, 3:** Anslyn (PERSON-000673, Chemistry), Dortdivanlioglu
  (PERSON-000677, Civil/Architectural/Environmental), Feng Zhang
  (PERSON-000821, Pharmacy). Each has polymer research witnessed on UT pages
  (their records' sources) but no affiliation with any held or forthcoming
  program: all three are absent from the MSE GSC roster and from all five
  TMI research-theme rosters fetched; Anslyn's and Dortdivanlioglu's only
  center witness is the NSF MRSEC (Center for Dynamics and Control of
  Materials), which has no Atlas row. Settling fact for each: a TMI page
  listing them as MSE Graduate Program Faculty, or a held row for a program
  they are witnessed in (e.g. a CDCM row, or a Pharmacy/CAEE department row
  passing the §4.11 test in a future pass).

### 3. Department-row tests (§4.11 prong (b))

Unit: the two departments where the unlinked pool concentrates (Chemical
Engineering, Chemistry).

- **Chemical Engineering — VERIFIED, row drafted** (proposed_rows.csv,
  packet-local key NEW-UTA-CHE). The department's own Graduate Program page
  names the degrees' research areas: "Here are the six main Research Areas
  our faculty and students are investing their energy in: — Advanced
  Materials, Polymers & Nanoengineering — Bioengineering — Energy —
  Environmental Engineering — Theory & Simulation — Process Engineering."
  Polymers are named inside a research area of the department's degrees, so
  prong (b) is met directly (no seam: the naming sits on the degree program
  page itself). The dedicated research-area page corroborates with polymer
  topics (membranes via nanocomposite technology; polymers for
  microelectronics; novel polymers for biomedical applications). Drafted
  `research_areas` are restricted to the polymer slice of that one named
  area; specialty fields and scale held blank (no §3.1/§3.2 term and no
  convertible size figure on the department's pages — $20.5M research
  funding is dollars and never converts).
- **Chemistry — REJECT under prong (b).** Deciding fact: the department's
  own Graduate Handbook (2024/2025, hosted on chemistry.utexas.edu) states
  the graduate program "offers the Ph.D. degree in five major areas of
  chemistry: analytical chemistry, chemical biology, inorganic chemistry,
  organic chemistry, and physical chemistry" — no polymer track,
  concentration, or research area is named for its degrees; the
  undergraduate focus areas name "Materials Chemistry," which is not
  polymer by name. Settling fact that would reopen: a Chemistry page
  naming a polymer research area, track, or concentration of its degrees.
  (Handbook quote read via the search extract of the department's own PDF;
  the integrator may re-verify against the PDF directly.)

### 4. Census — 5 candidates

Unit: current faculty on the rosters used above (TMI research-theme rosters
and the MSE Graduate Studies Committee roster) with no record in
`data/people.csv` at ORG-004651 (filter: Gate A faculty styling + Gate B
polymer statement, both on UT Austin's own pages).

Donglei Emma Fan, Jonathan Yan Chen, Rui Huang, Keith Johnston, Wei Li —
all five are styled Associated Graduate Program Faculty on the Polymers and
Biomaterials roster with polymer-specific research statements, and none has
an Atlas record. Detail in census.csv. Considered and excluded (no
polymer statement on the roster pages): Guihua Yu, Yuebing Zheng, Deji
Akinwande, Nanshu Lu, Huiliang (Evan) Wang; Kenneth Liechti (composites
named without polymer, and styled Professor Emeritus on the GSC roster —
outside Gate A for new records in any case).

## Weakest links (named for the integrator)

1. **Peppas LINK (PERSON-000761)** — no single UT page fetched this pass
   states both his Chemical Engineering membership and the word "polymer."
   The LINK rests on the Dell Med directory (Chemical Engineering first
   among his five department appointments; his degree home) plus his record
   specialty as published on UT pages. If the integrator wants one page
   carrying both, a ChemE faculty-directory fetch is the settling step.
2. **Page and Marras LINKs** rest partly on photo-caption entries in the
   GSC roster sequence (their names appear as roster photo entries, not
   full text blocks). Page is corroborated by the Prospective Students
   recruiting-faculty list; Marras by TMI's own news item styling him
   "affiliated faculty member with the Texas Materials Institute."
3. **`specialty_materials = composites_unspecified`** for PROG-000122 rests
   on one framing sentence ("structural composites") on the Polymers and
   Biomaterials page. It is the only §3.2 value proposed, and the
   unspecified term is used precisely because the type is not stated.
4. **Census Wei Li Gate A** — his professorship is not separately quoted
   this pass; the GSC roster page styles the roster as program faculty and
   carries his entry, and the Polymers and Biomaterials page styles him
   Associated Graduate Program Faculty. Confirm rank from his Mechanical
   Engineering directory page at build time.
5. **Chemistry REJECT** rests on the department's own Graduate Handbook as
   surfaced in search extract (see §3 note) plus the department homepage's
   area list (analytical, inorganic, organic, physical). No fetch failure
   occurred; the handbook PDF itself was not opened.

## Fetch log (summary)

Direct fetches of institution pages (all returned content; no failures):
tmi.utexas.edu — Prospective Students, Polymers and Biomaterials, Electronic
and Photonic Materials, Structural Materials, Computational Materials
Science, Materials Characterization, Graduate Studies Committee roster,
About, Research overview, Marras news item; che.utexas.edu — Research
landing, Graduate Program, Advanced Materials Polymers & Nanoengineering
area page, person pages for Sanoja, Rosales, Freeman, Lynd;
utw10279.utweb.utexas.edu — Ganesan faculty profile (ChemE-hosted);
mwet.utexas.edu — profiles for Freeman and Sanoja-Lopez;
dellmed.utexas.edu — Peppas directory; chemistry.utexas.edu — Page
directory. Free searches (3): TMI faculty/GSC discovery, ChemE research
areas, Chemistry research areas, M-WET profile index, ChemE Lynd page.
Paid calls: **zero** (no Tavily/Exa/Firecrawl).

---

## INTEGRATION RECORD (integrator of record: spaghetti, 2026-11-12)

Built on origin/main `165df3b4be37e54a3a41136466abe3bb58b061ef` (PR #305 head) in worktree `~/workspace/atlas-w4-uta-build-2026-11-12`, branch `agent/spaghetti/wave4-ut-austin-2026-11-12`. The packet files above stand **as authored**; everything below is the integrator's record of application. Pre-pass backups: `~/workspace/atlas-w4-uta-backups-2026-11-12/`. Build script: `~/workspace/atlas-resync-2026-11-10/build_w4_utaustin.py` (packet CSVs read programmatically — quotes, URLs, and notes were never retyped). ID allocation: the Clemson wave-4 unit merges before this unit in sequence but allocated first (PROG-000345/346, PERSON-002155..002162, EVD-334001..334038), so this unit's floors were set by the brief at **PROG-000347 / PERSON-002163 / EVD-334039** regardless of this base's tree maxima (PROG-000344 / PERSON-002154 / EVD-334000, scanned across all shards at build and asserted below the floors). Local build only — nothing pushed, no PR.

**Program CREATE — 1 (integrator ruling 1: CREATE the Chemical Engineering department row):**
- PROG-000347 **Chemical Engineering** (degree, ORG-004651), packet cells verbatim except `program_id` allocated and an allocation marker prepended to `notes` (cell-for-cell audit against proposed_rows.csv: no other diff). EVD-334039 (existence — the McKetta department's own Graduate Program page names "Advanced Materials, Polymers & Nanoengineering" among the six main research areas of its degrees, §4.11 prong (b)) + EVD-334040 (scope — the research-area page's polymer design topics; `research_areas` restricted to the packet's polymer slice `polymer_physics;membranes_separations;biomedical_polymers`). **No seam:** the naming sits on the degree program page itself — stronger than the pilot's seamed rows (PROG-000317 OSU Chemistry, PROG-000319 UTK CEE) — recorded in both evidence rows. `cip_code` blank (no IPEDS pull in the lane; frame candidate CIP 14.0701 is a lead only), `scale_band` blank (research dollars and faculty counts never convert under S3), `specialty_processes`/`specialty_materials` blank (no §3.1/§3.2 term named for the area). Both evidence rows `supports_A` on the row's own tier A.
- **Chemistry department row — REJECT, no row created, no evidence:** the packet's prong-(b) test failed on the department's own Graduate Handbook (the Ph.D. is offered in five major areas — analytical, chemical biology, inorganic, organic, physical — none polymer-named; the undergraduate "Materials Chemistry" focus is not polymer by name). The packet's settling fact stands: a Chemistry page naming a polymer research area, track, or concentration of its degrees reopens it. Anslyn PERSON-000673 and Page PERSON-000699 are Chemistry-home people; Page links to PROG-000122 on his witnessed MSE affiliation (below), Anslyn stands NO_WITNESS.

**Depth fills — 7 packet fill rows applied:** PROG-000122 (Materials Science and Engineering degree, operated by the Texas Materials Institute) 0/5 → **3/5**: `research_areas` = `biomedical_polymers;membranes_separations;composites_mechanics;characterization_methods` (EVD-334041..334044 — one scope row per term, each on its fills.csv witness; `characterization_methods` fills research_areas only, neither specialty field, per standing practice), `specialty_materials` = `composites_unspecified` (EVD-334045 — the Polymers and Biomaterials page's framing sentence names "structural composites" with no type stated, so the §3.2 unspecified term is the honest tag; the packet's weakest-link posture, one framing sentence, is carried in the row's notes), `facilities_note` (EVD-334046 + EVD-334047 — the TMI About page's two witnesses: 65+ large instruments in three facilities, $40M characterization/processing infrastructure, shared user access). `specialty_processes` **held blank** (the program's own pages name no §3.1 process; "materials synthesis and processing" is generic) and `scale_band` **held blank** (STILL_UNCERTAIN per the packet — no published program enrollment; faculty counts, facility user-base counts, and completion flows never convert under S3). All 7 fill rows `supports_B` on the row's own tier B. Changed cells on PROG-000122 are exactly the three fills + `last_verified` → 2026-11-12 (row-level diff vs backups verified); its notes stand unmodified.

**People — 12 packet dispositions applied (links.csv order; one scope evidence row per LINK, `own_site`, tier_effect from the person's own tier — all 12 carried records are tier A → `supports_A`):**
- **LINK 9** (`program_org_id` set + `last_verified` → 2026-11-12; no other cells): → PROG-000122: Marras PERSON-000674 (EVD-334049), Dodabalapur PERSON-000675 (EVD-334050 — the packet's strongest link: one program roster page carries both his Associated Graduate Program Faculty membership and his polymer statement), Page PERSON-000699 (EVD-334054 — Chemistry-home; his home department's row test failed, so his witnessed MSE program affiliation is primary). → PROG-000347 (Chemical Engineering): Lynd PERSON-000672 (EVD-334048), Sanoja PERSON-000676 (EVD-334051), Ganesan PERSON-000696 (EVD-334053), Rosales PERSON-000730 (EVD-334055), Freeman PERSON-000742 (EVD-334056), Peppas PERSON-000761 (EVD-334058 — **weakest link, caveat carried verbatim** in the row's claim_detail: no single UT page fetched in the lane states both his Chemical Engineering membership and the word "polymer"; the LINK rests on the Dell Med directory styling Chemical Engineering first among his five appointments, plus his record specialty as published on UT pages; settling fact named in the row).
- **BANKED-PENDING conversions — 2 (integrator ruling 2):** the M-WET EFRC row the packet awaited now exists as **PROG-000333** (created in the federal round-2 lane B unit, PR #300), so the packet's two BANKED-PENDING dispositions are minted as real banked evidence: Freeman → PROG-000333 (EVD-334057 — styled "Center for Materials For Water and Energy Systems (MWET), Director" on his own ChemE page, and a profile holder on the center's own site) and Sanoja → PROG-000333 (EVD-334052 — profile on the center's own site). Evidence only; both `program_org_id` values stand at PROG-000347.
- **Indirect M-WET ties — flagged only, NOT banked (integrator ruling 2):** Ganesan and Lynd show only indirect M-WET ties (M-WET student profiles naming them as Ph.D. advisors — Lynd as co-advisor, per their links.csv notes, which ride verbatim in EVD-334048/EVD-334053). No banked rows minted for either; the settling witness would be an M-WET faculty/profile page for the person himself.
- **NO_WITNESS 3:** Anslyn PERSON-000673, Dortdivanlioglu PERSON-000677, Feng Zhang PERSON-000821 — **byte-untouched, no evidence** (raw-line identity against backups asserted at build; each has polymer research witnessed on UT pages but no affiliation with any held program — all three absent from the MSE GSC roster and all five TMI theme rosters; Anslyn's home department failed the prong-(b) test, Dortdivanlioglu's CAEE and Zhang's Pharmacy were not department-row tested this pass; the NSF MRSEC/CDCM affiliation has no Atlas row; settling facts stand in links.csv).

**Census mints — 5 (all at ORG-004651, tier A, existence + scope evidence each; `research_specialties` left blank — the packet assigns no §3.1/§3.2 values and none were inferred, per the MatSE/Penn/CMU/Clemson mint practice; the Gate B quotes ride in the scope rows):**
- → PROG-000122 (MSE): Donglei Emma Fan PERSON-002163 (EVD-334059/334060), Jonathan Yan Chen PERSON-002164 (EVD-334061/334062), Rui Huang PERSON-002165 (EVD-334063/334064), Wei Li PERSON-002167 (EVD-334068/334069) — all four styled Associated Graduate Program Faculty on the program's own Polymers and Biomaterials roster, with the Gate A styling from the MSE Graduate Studies Committee roster.
- → PROG-000347 (Chemical Engineering): Keith Johnston PERSON-002166 (EVD-334065/334066) — home department under the primary-home rule, per the packet's disposition; his MSE affiliation is **banked** (EVD-334067, Polymers and Biomaterials roster witness; `program_org_id` stands at PROG-000347).
- **Wei Li flag (integrator ruling 4):** minted exactly on the packet's census evidence; his rank was not separately quoted by the lane. His census note is carried verbatim in EVD-334068/EVD-334069: "His Mechanical Engineering rank (Associate Professor) was not separately quoted this pass — confirm from his ME directory page at build time (weakest census item, see README)." The build-time confirmation fetch was **not** run and the record was not strengthened beyond the packet: `role` = `associate_professor` rests on the packet's own assertion, `role_as_published` carries the roster styling "Associated Graduate Program Faculty (MSE Graduate Program)". Namesake note: a different Wei Li (PERSON-001166, Texas Tech University, Chemical Engineering professor) already stands in people.csv — distinct institution and styling; no dedupe conflict, recorded here so the pair is never merged on name alone.
- The packet's considered-and-excluded names (Yu, Zheng, Akinwande, Lu, Wang — no polymer statement on the roster pages; Liechti — composites without polymer, and emeritus) were **not** minted; reasons stand in the packet README §4.

**Ecosystem rollup — ORG-004651 recomputed (V-16):** recomputation was first verified to reproduce the carried rollup exactly on the pre-build program set (zero drift), with PROG-000333 (M-WET, PR #300) included as carried. `polymer_program_name`: "Materials Science and Engineering; Center for Materials for Water and Energy Systems (M-WET)" → "**Chemical Engineering; Materials Science and Engineering; Center for Materials for Water and Energy Systems (M-WET)**"; `polymer_program_url`: the TMI prospective-students URL → `https://che.utexas.edu/academics/graduate-program/` (first sorted program's URL, mechanically required by V-16). `last_verified` already read 2026-11-12 and stands. No other ecosystem row moved (row-level diff vs backups verified).

**P1 title-refresh rider:** the packet documents no current-page verbatim title conflicting with a carried record — **no title fixes applied in this unit**. Compared and stood: Lynd's record styling differs from his ChemE page only in capitalization; Rosales's carried `role_as_published` ("Associate Professor Adrianne Rosales") is thinner than, but not contradicted by, her ChemE page styling — flagged here for a future people-record pass, not edited (no verbatim conflict documented in the packet).

**Counts (unit + filter):** programs: +1 created (PROG-000347), 1 changed (PROG-000122 — 3 depth cells + `last_verified` only), all other rows byte-identical. People: 9 changed (LINKs; exactly `program_org_id` + `last_verified` per row), +5 created (census mints), 3 of the disposition set byte-untouched (the NO_WITNESS three). Ecosystem: 1 row changed (ORG-004651, rollup fields only). Evidence: 31 rows appended, EVD-334039..EVD-334069 (9 to `evidence_programs.csv`, 22 to `evidence_people.csv`; byte-prefix pure appends verified). Next frees: **PROG-000348 / PERSON-002168 / EVD-334070** (above this unit's floors; tree maxima on the base stood at PROG-000344 / PERSON-002154 / EVD-334000 — the gap to the floors is the Clemson unit's in-sequence allocation).

**QUEUE:** prior claims stand exactly as they are on this base (the NDSU claim still reads `claimed` although PR #305 has merged — left as-is per instruction; no Clemson claim stands on this base — left absent); this unit's claim added directly below the NDSU claim.

**Gates (run on the built tree):** `scripts/validate.py` → "OK — validation passed." (totals: 5,024 organizations, 7,190 sites, 408 ecosystem rows, 1,493 people rows, 212 program rows, 41,094 evidence rows; warnings only the standing classes — V-16 un-decomposed claims, V-38 placement queue, V-44 code assignments, baselined debt — none naming this unit's records). `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base 165df3b4be)". No REMOVALS.csv.
