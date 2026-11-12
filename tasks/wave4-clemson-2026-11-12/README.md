# Wave 4 school pass — Clemson University (ORG-004639) — RESEARCH PACKET

Lane: wave4 clemson (spaghetti subagent), 2026-11-12. **Packet only** — no repo
data written, no branch, no PR. Base state re-derived from `origin/main`
79b1f42b (PR #299 head): Clemson carries exactly one program row
(PROG-000113) and exactly 15 people, all with blank `program_org_id`.
Paid calls: **zero** (direct fetches of clemson.edu / cecas.clemson.edu /
udel.edu pages, the department handbook PDF, and web search only).

## Verdicts by target

### PROG-000113 Materials Science and Engineering [degree] — fills PROPOSED (depth 0/5 → 3/5)

Unit: the one carried degree row at ORG-004639. Filter: the five depth cells.

- **research_areas = `polymer_physics;polymer_synthesis`** — from the
  department's own degree pages. Graduate page: "Graduate students may
  specialize in research areas, including advanced manufacturing,
  biomaterials, energy materials, **polymer design**, and photonics."
  Department homepage: "Research concentrations include advanced
  manufacturing, biomaterials, energy materials, **polymer structure**,
  photonic, and resilient materials." Research Focus page names the focus
  outright: "**Polymer Structure and Design**". Mapping: "polymer design" →
  `polymer_synthesis` (§3.5's own definition covers design of polymer
  architectures); "polymer structure" → `polymer_physics` (structure–property
  relations). Deliberate holds: the same statements name "biomaterials" and
  "advanced manufacturing", which were **not** mapped to
  `biomedical_polymers` / `additive_manufacturing_science` — both are broader
  than polymers on their face (implant metals/ceramics; metal/ceramic AM),
  and the pilot/department-row precedent restricts program research areas to
  the polymer slice as stated.
- **specialty_processes = `additive_manufacturing_polymer`** — the
  department's own Services page lists under Additive
  Manufacturing/Prototyping: "Polymer fused deposition modeling (FDM)".
  The same page's "fiber extrusion" service line was left in
  facilities_note only (a service clause, thinner than a stated specialty).
- **specialty_materials = HELD (blank)** — no §3.2 family is named as the
  program's specialty on its own research pages; "polymers" generically is
  not a family. Settling fact: a department page naming a material family
  (e.g. thermoplastics, composites) as the program's specialty.
- **facilities_note = PROPOSED** — grounded in the department's own Services
  page (Materials Characterization and Processing Center: analytical and
  physical testing, manufacturing, fiber extrusion; rheology and thermal
  analysis suites on its equipment list) and in an MSE faculty page's
  statement of the AMRL: "AMRL is an 111,000 square foot laboratory that
  houses a range of state-of-the-art equipment and is located in the
  Clemson University Advanced Materials Center, an innovative campus and
  technology park located in Anderson, SC"
  (https://www.clemson.edu/cecas/departments/mse/people/faculty/foulger.html).
- **scale_band = HELD (blank)** — no published *program enrollment* figure
  was found on the department's pages. The homepage's "$9.2M Research
  Expenditures" is dollars (never converts under S3); "one of the largest
  academic departments in South Carolina" is a within-state relative claim,
  not a size band; the IPEDS completions already on the row (35, 2024) are a
  completion flow (never converts). Settling fact: a department-published
  program enrollment figure or an unqualified size self-characterization.

### People — 15 unlinked records dispositioned (unit: people rows at ORG-004639 with blank program_org_id; filter: the 15 named targets)

- **LINK ×12** — to PROG-000113 (MSE): Urban PERSON-000288, Kuksenok
  PERSON-000289, Luzinov PERSON-000294, Peresin PERSON-000295 (joint MSE
  appointment stated on her own profile), Foulger PERSON-000297, Kornev
  PERSON-000310 (weakest — see below). To the drafted Chemistry row: Smith
  PERSON-000287, Tennyson PERSON-000290, Perahia PERSON-000291. To the
  drafted ChBE row: Davis PERSON-000292, Thies PERSON-000296, Husson
  PERSON-000311.
- **BANKED ×1** — Urban's witnessed Chemistry (courtesy) appointment,
  banked against the drafted Chemistry row; his `program_org_id` stays
  PROG-000113.
- **BANKED-PENDING ×0** — deliberate. The only target with a witnessed AIM
  for Composites affiliation is Pilla (its founding director), and he has
  left Clemson (below), so no Clemson-program affiliation is banked for
  him. No other target appears on AIM's Clemson roster as published by DOE
  (Gang Li, Zhen Li, Qiong Zhang — none are Atlas records).
- **NO_WITNESS ×3** —
  - **Pilla PERSON-000309 — departed.** University of Delaware's own pages
    style him Professor and Director of UD's Center for Composite
    Materials: "Prior to joining UD-CCM, Pilla held the ExxonMobil
    Employees Chair in Engineering at Clemson University and was the
    founding director of the Clemson Composites Center." Gate A fails at
    Clemson today; his Clemson lab pages no longer resolve. **Flag for the
    integrator (out of lane scope): the carried record's Clemson
    institution is stale — re-home review needed.** DOE's EFRC listing
    still shows AIM's lead institution as Clemson (class 2022–2026); that
    is the AIM row unit's problem, noted here only because it intersects
    this roster.
  - **Sternberg PERSON-000293** — Gates A+B pass on his own profile
    (Assistant Professor of Sustainable Packaging; "Using renewable
    materials for polymers, foams, films, and coatings for packaging
    applications"), but his home unit (Food, Nutrition and Packaging
    Sciences) has no row and drafting one was outside this lane's scope.
    Settling fact: a prong-(b) test + row decision for FNPS / Packaging
    Science — a plausible future department row, flagged as a lead.
  - **Meng PERSON-000298** — Gate A passes; his own profile's stated
    research interests name composites/nanocomposites modeling but not
    polymers (polymer appears only in his publication titles). Settling
    fact in links.csv.

### Department-row tests, §4.11 prong (b) — both DRAFTED (proposed_rows.csv)

- **Chemistry — VERIFIED, row drafted (NEW-CLEMSON-CHEM).** The
  department's own Graduate Studies Overview names **polymer chemistry**
  among the research areas of *both* graduate degrees (M.S. and Ph.D.
  sentences quoted in the row's notes), and its research page maintains a
  named Polymer Chemistry faculty area of eight. `research_areas` held to
  `polymer_synthesis` (the UTK-Chemistry mapping of a "Polymer Chemistry"
  naming). Seam flagged in-row: graduate-overview naming, OSU-Chemistry
  class (PROG-000317), not UTK's catalog-concentration class
  (PROG-000318).
- **Chemical & Biomolecular Engineering — VERIFIED, row drafted
  (NEW-CLEMSON-CHBE).** The department's own Research page names the
  cluster "**Advanced Materials, Polymers and Nanoscience**" (advanced
  polymer membranes, cellulose nanomaterials, nanocomposites) and states
  on the same page: "Graduate students may specialize in any of the
  research areas." `research_areas` held to `membranes_separations` — the
  one cluster topic mapping cleanly to a controlled term; the
  lignin-to-carbon-fiber and cellulose lines were not stretched to
  `sustainable_feedstocks`/`bioplastics_biobased`. Seam flagged in-row
  (research-cluster page, OSU class).

### Census — faculty on the same rosters with no Atlas record (unit: current faculty listings of MSE, Chemistry, ChBE; filter: Gate A styling + Gate B polymer witness on Clemson's own pages)

- **VERIFIED candidates ×8** — Brown, Mefford, Zhu, Weirich (MSE);
  Ogale, Roberts (ChBE); Marcus, Thrasher (Chemistry). Full quotes in
  census.csv. Side finding: Ogale's current profile styles him Director
  of the **Center for Advanced Engineering Fibers and Films (CAEFF)** —
  the center the PROG-000113 wave-B note left unverified as current. A
  prong-(a) CAEFF center row is a plausible future candidate; not drafted
  here (out of scope).
- **STILL_UNCERTAIN ×5** — Larsen (polymersome publications; stated
  interests name no polymer term), Creager, Pennington, Sun (named on
  Chemistry's Polymer Chemistry roster; own profiles silent on polymer),
  Ming Yang (named in ChBE's polymers cluster; own profile catalysis
  only). Settling fact named for each in census.csv.
- **REJECT ×2** — Ashlyn D. Smith and Perla Y. Sauceda-Oloño (both
  lecturer-styled, teaching-only pages; polymer wording reaches only
  training/Ph.D.-era publications). Deciding facts in census.csv.
- Rosters also scanned with no polymer witness and not carried into
  census.csv: the remaining MSE handbook faculty (Aidhy, Ballato,
  Blouin, Bordia, Brinkman, Dive, Hou, Jacobsohn, Johnson, Kennedy, Lu,
  Maksymovych, Peng, Saez, Sun, Tong) and Brian Topper (glasses/fiber
  lasers); the remaining ChBE roster (Alba-Rubio, Birtwistle, Bruce,
  Harcum, Norfolk, Roat).

## Weakest links (named, in order)

1. **Kornev's Gate B (PERSON-000310, LINK).** His current MSE profile and
   the department handbook list his areas without the word "polymer"; his
   lab site did not resolve from this lane (connection closed, twice).
   The link rests on the Clemson University Research Foundation's own
   technology listing naming him inventor of an electrospun-polymer-fiber
   technology. A verifier holding him to NO_WITNESS would be defensible;
   the settling fact is named in links.csv.
2. **The two department rows' prong-(b) form.** Both rest on
   department-published research-area naming (graduate overview /
   research-cluster page), the OSU class of the pilot — not on catalog
   concentrations (the UTK class). If the owner holds Clemson to the
   catalog standard, both rows fall and the six Chemistry/ChBE links fall
   with them (those people then stand NO_WITNESS, like Sternberg).
3. **PROG-000113 specialty_processes.** One service-page line (polymer
   FDM) carries the cell; if the integrator judges services ≠ program
   specialty, the row lands at 2/5 (research_areas + facilities_note)
   instead of 3/5.
4. **Peresin's LINK target.** Her primary chair home is Forestry; the
   link rests on the joint MSE appointment stated on her own profile —
   the standard joint-appointment-to-carried-row treatment, but the
   integrator should confirm it wants joint-home links at primary grain
   (the pilot's Peresin-analogues at UTK took the witnessed center as
   primary on the same logic).

## Fetch log (summary)

≈45 fetches, all direct, zero paid: MSE homepage, graduate page, research
focus page, centers/services pages, people index, and the 2026-2027
Undergraduate Handbook PDF (the department's own faculty list — the
census ground truth for MSE); 8 MSE faculty pages; ChBE homepage,
research page, degrees page, people index and 7 faculty pages; Chemistry
people directory, graduate overview, research page and 9 profile pages;
CAFLS profiles (Sternberg, Peresin); ME profile (Meng); CURF technology
listing 9203 (Kornev); UD college-leadership page (Pilla); 4 web searches
(MSE research/facilities discovery, Kornev, AIM/Pilla, Chemistry).
Failures — all availability, never treated as absence: clemson.edu's new
department pages return JS shells to the plain browser fetch (worked
around by direct fetch of the same URLs); `cecas.clemson.edu/kornevlab/`
connection closed ×2; `cecas.clemson.edu/spilla/...` connection closed
×1 (independently explained by Pilla's departure); CURF page is a JS
shell to direct fetch, read via the browser fetch of the same URL.

Cross-checks: people/program state re-derived from `origin/main`
(79b1f42b) at lane start; the AIM for Composites EFRC row being created
by a parallel unit was not drafted, per instructions; no ID was
allocated anywhere in this packet (packet-local keys NEW-CLEMSON-CHEM /
NEW-CLEMSON-CHBE only).

---

## INTEGRATION RECORD (integrator of record: spaghetti, 2026-11-12)

Built on origin/main `0f3380c9d4322095cf4e1d82dd1aa09fb60ad468` (PR #304 head) in worktree `~/workspace/atlas-w4-clemson-build-2026-11-12`, branch `agent/spaghetti/wave4-clemson-2026-11-12`. The packet files above stand **as authored**; everything below is the integrator's record of application. Pre-pass backups: `~/workspace/atlas-w4-clemson-backups-2026-11-12/`. Build script: `~/workspace/atlas-resync-2026-11-10/build_w4_clemson.py` (packet CSVs read programmatically — quotes, URLs, and notes were never retyped). ID allocation: the NDSU wave-4 unit merges before this unit in sequence but allocates no program/person IDs and evidence only from EVD-333980, so this unit's floors were set by the brief at **PROG-000345 / PERSON-002155 / EVD-334001** regardless of this base's tree maxima (PROG-000344 / PERSON-002154 / EVD-333979, scanned across all shards at build and asserted below the floors). Local build only — nothing pushed, no PR.

**Program CREATEs — 2 (both department rows; integrator ruling 1: CREATE on both):**
- PROG-000345 **Chemistry** (degree, ORG-004639), packet cells verbatim except `program_id` allocated and an allocation marker prepended to `notes` (cell-for-cell audit against proposed_rows.csv: no other diff). EVD-334001 (existence — the department's own Graduate Studies Overview names "polymer chemistry" among the research areas of both the M.S. and the Ph.D., §4.11 prong (b)) + EVD-334002 (scope — the department research page's named Polymer Chemistry faculty area; `research_areas` restricted to the polymer slice `polymer_synthesis` per the UTK Chemistry precedent PROG-000318). **SEAM carried:** the naming sits on the graduate-program overview, not the official catalog — the OSU-Chemistry class (PROG-000317), weaker than UTK's catalog concentration (PROG-000318); stated in the row's notes as drafted and flagged for the owner. `cip_code` blank (no IPEDS pull in the lane; frame candidate CIP 40.0501 is a lead only).
- PROG-000346 **Chemical and Biomolecular Engineering** (degree, ORG-004639), same verbatim discipline. EVD-334003 (existence — the department's own Research page names the "Advanced Materials, Polymers and Nanoscience" cluster and states "Graduate students may specialize in any of the research areas," §4.11 prong (b)) + EVD-334004 (scope — `research_areas` restricted to `membranes_separations`, the one cluster topic mapping cleanly to a controlled term; the lignin-to-carbon-fiber and cellulose lines were NOT stretched to `sustainable_feedstocks`/`bioplastics_biobased`, per the packet). **SEAM carried:** research-cluster page, OSU class (PROG-000316/317), not the UTK catalog class; stated in the row's notes as drafted. `cip_code` blank (frame candidate CIP 14.0701 a lead only). Both evidence rows on each create `supports_A` on the row's own tier A.

**Depth fills — 3 packet fill rows applied:** PROG-000113 (MSE degree) 0/5 → **3/5**: `research_areas` = `polymer_physics;polymer_synthesis` (EVD-334005, EVD-334006 — "polymer design" → `polymer_synthesis` under §3.5's definition; "polymer structure" → `polymer_physics`, witnessed on the department homepage / Research Focus page as quoted in the packet README, with the fills.csv graduate-page witness as source_ref and the posture stated in EVD-334005's notes), `specialty_processes` = `additive_manufacturing_polymer` (EVD-334007 — one Services-page line, "Polymer fused deposition modeling (FDM)"; the packet's weakest-link posture is carried in the row's notes: if services ≠ program specialty the row stands at 2/5), `facilities_note` (EVD-334008 — MCPC services text; AMRL element grounded on the Foulger faculty page per the packet README). `specialty_materials` + `scale_band` **held blank** per the packet (no §3.2 family named as the program's specialty; no published program enrollment — dollars and completion flows never convert under S3). Changed cells on PROG-000113 are exactly the three fills + `last_verified` → 2026-11-12 (row-level diff vs backups verified). The row's notes stand **unmodified**: the packet's CAEFF side finding (below) proposes no note correction, so per integrator ruling 4 it is recorded here only.

**People — 15 dispositions applied (links.csv order; one scope evidence row per LINK/BANK, `own_site`, tier_effect from the person's own tier — all 15 carried records are tier A → `supports_A`):**
- **LINK 12** (`program_org_id` set + `last_verified` → 2026-11-12; no other cells): → PROG-000113: Urban PERSON-000288 (EVD-334010), Kuksenok PERSON-000289 (EVD-334012), Luzinov PERSON-000294 (EVD-334016), Peresin PERSON-000295 (EVD-334017 — joint MSE appointment stated on her own profile; the witnessed-row-as-primary treatment per the packet), Foulger PERSON-000297 (EVD-334019), Kornev PERSON-000310 (EVD-334021 — **Gate B caveat carried verbatim** in the row's claim_detail and notes: his current MSE profile and the department handbook list his areas without the word "polymer," his lab site did not resolve, and the LINK rests on CURF's own technology listing naming him inventor of an electrospun-polymer-fiber technology; settling fact named in the row). → PROG-000345 (Chemistry): Smith PERSON-000287 (EVD-334009), Tennyson PERSON-000290 (EVD-334013 — no banked MSE affiliation: no current Clemson page states the joint appointment his carried record claims; settling fact in the packet note), Perahia PERSON-000291 (EVD-334014). → PROG-000346 (ChBE): Davis PERSON-000292 (EVD-334015), Thies PERSON-000296 (EVD-334018), Husson PERSON-000311 (EVD-334022).
- **BANKED 1**: Urban → PROG-000345 (EVD-334011) — his witnessed Chemistry (courtesy) appointment; evidence only, `program_org_id` stands at PROG-000113.
- **NO_WITNESS 3**: Sternberg PERSON-000293 and Meng PERSON-000298 — **byte-untouched, no evidence** (Sternberg's home unit, Food, Nutrition and Packaging Sciences, has no row; the packet's prong-(b) lead for a future Packaging Science department row is recorded here as future work, **not** drafted in this unit. Meng's own profile states no polymer research area; settling fact in links.csv). Pilla PERSON-000309 — see the staleness ruling below.

**Pilla PERSON-000309 — departed; staleness flag, no re-home (integrator ruling 2):** the packet establishes he has left Clemson — the University of Delaware's own college-leadership page styles him Professor and Director of UD's Center for Composite Materials and states he held the Clemson chair "prior to joining UD-CCM." His `institution_org_id` and `program_org_id` are **not** changed (Delaware institution mechanics are an owner-battery item), he is **not** linked, and his people row stands **byte-identical** (verified against backups, `last_verified` included). The staleness flag rides **EVD-334020**: one evidence row built from the packet's UD witness (quote + URL as the packet gives them), claim_type `existence` per §4.13's people-grain convention (liveness at people grain is carried by the existence row's currency), tier_effect `supports_A` from his record's own tier. Because people.csv carries no notes field (the §4.9 field set is pinned, validator V-11), the flag text lives in EVD-334020's claim_detail + notes and in this record — the Gomez stale-crawl precedent (EVD-333884). **Re-home review (University of Delaware) is referred to the owner battery.** Note the intersection the packet flags: DOE's EFRC listing still shows AIM for Composites (PROG-000334, created PR #300) as Clemson-led with Pilla as director — that is the AIM row's unit problem, untouched here.

**Census mints — 8 (all at ORG-004639, tier A, existence + scope evidence each; `research_specialties` left blank — the packet assigns no §3.1/§3.2 values and none were inferred, per the MatSE/Penn/CMU mint practice; the Gate B quotes ride in the scope rows):**
- → PROG-000113 (MSE): Philip J. Brown PERSON-002155 (EVD-334023/334024), O. Thompson Mefford PERSON-002156 (EVD-334025/334026), Tianyu Zhu PERSON-002157 (EVD-334027/334028), Kimberly Weirich PERSON-002158 (EVD-334029/334030 — packet flag carried: her polymer slice, "Biopolymers"/"Liquid crystals" on her own page, is real but secondary to her soft-matter program; minted as the packet's VERIFIED verdict stands).
- → PROG-000346 (ChBE): Amod A. Ogale PERSON-002159 (EVD-334031/334032; role `center_director_professor` — Dow Chemical Professor plus a publicly stated center directorship), Mark E. Roberts PERSON-002160 (EVD-334033/334034).
- → PROG-000345 (Chemistry): Ken Marcus PERSON-002161 (EVD-334035/334036), Joseph S. Thrasher PERSON-002162 (EVD-334037/334038 — "no longer taking new graduate students" noted on his profile; he remains current Professor, Gate A stands, per the packet).
- The packet's 5 STILL_UNCERTAIN census names (Larsen, Creager, Pennington, Sun, Ming Yang) and 2 REJECTs (Ashlyn D. Smith, Sauceda-Oloño — lecturer-styled) were **not** minted; settling/deciding facts stand in census.csv.
- **CAEFF side finding (integrator ruling 4):** Ogale's current profile styles him Director of the Center for Advanced Engineering Fibers and Films (CAEFF) — verifying as current the center PROG-000113's wave-B note left unverified. The packet proposes **no** note correction on PROG-000113, so the finding is recorded here only; PROG-000113's notes stand unmodified. A prong-(a) CAEFF center row is a plausible future candidate, not drafted here (out of packet scope).

**Ecosystem rollup — ORG-004639 recomputed (V-16):** recomputation was first verified to reproduce the carried rollup exactly on the pre-build program set (zero drift), with PROG-000334 (AIM for Composites, PR #300) included as carried. `polymer_program_name`: "Materials Science and Engineering; Artificially Intelligent Manufacturing Paradigm for Composites (AIM for Composites)" → "**Chemical and Biomolecular Engineering; Chemistry; Materials Science and Engineering; Artificially Intelligent Manufacturing Paradigm for Composites (AIM for Composites)**"; `polymer_program_url`: the legacy MSE URL → `https://www.clemson.edu/cecas/departments/chbe/research/` (first sorted program's URL, mechanically required by V-16). `last_verified` already read 2026-11-12 and stands. No other ecosystem row moved (row-level diff vs backups verified).

**P1 title-refresh rider:** the packet flags no stale titles among the 15 carried records — **no title fixes applied in this unit**.

**Counts (unit + filter):** programs: +2 created (PROG-000345, PROG-000346), 1 changed (PROG-000113 — 3 depth cells + `last_verified` only), all other rows byte-identical. People: 12 changed (LINKs; exactly `program_org_id` + `last_verified` per row), +8 created (census mints), 3 of the disposition set byte-untouched (Pilla — evidence only; Sternberg, Meng — nothing). Ecosystem: 1 row changed (ORG-004639, rollup fields only). Evidence: 38 rows appended, EVD-334001..EVD-334038 (8 to `evidence_programs.csv`, 30 to `evidence_people.csv`; byte-prefix pure appends verified). Next frees: **PROG-000347 / PERSON-002163 / EVD-334039** (above this unit's floors; tree maxima on the base stood at PROG-000344 / PERSON-002154 / EVD-333979 — the gap to the floors is the NDSU unit's in-sequence evidence allocation).

**QUEUE:** prior claims stand exactly as they are on this base (the CMU claim still reads `claimed` although PR #304 has merged — left as-is per instruction; no NDSU claim stands on this base — left absent); this unit's claim added directly below the CMU claim.

**Gates (run on the built tree):** `scripts/validate.py` → "OK — validation passed." (totals: 5,024 organizations, 7,190 sites, 408 ecosystem rows, 1,496 people rows, 213 program rows, 41,080 evidence rows; warnings only the standing classes — V-16 un-decomposed claims, V-38 placement queue, V-44 code assignments, baselined debt — none naming this unit's records). `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base 0f3380c9d4)". No REMOVALS.csv.
