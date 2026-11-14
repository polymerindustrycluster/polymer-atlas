# Wave 4, tranche 2 — University of Chicago (ORG-004660) school pass — RESEARCH PACKET

Lane: wave4-2026-11-12 tranche2-uchicago (spaghetti subagent), 2026-11-12. RESEARCH ONLY —
no repo writes, no build. Every fact below is verified on the institution's own pages
(uchicago.edu domains); award and registry records were never used as verification.
Base tree: origin/main db51af32 (PR #310). Paid calls: **zero, all providers** — direct
page fetches and web search only. Two fetches failed on a fetch-service 429 (the PME
directory profile pages for Patel and Wang); per protocol they were **not retried**, and
the affected Gate A/B cells rest on other UChicago pages, flagged where that happens.
A failed fetch is an availability signal, never evidence of absence.

## Institution facts

- University of Chicago, Chicago, IL (Cook County). Ecosystem ORG-004660, tier A;
  IPEDS UNITID 144050; ROR 024mw5h28 (both as carried).
- Carried program rows (2): **PROG-000157** "Polymer Science and Engineering (Master of
  Engineering track)", degree, tier B, depth **0/5** — this pass's fills target; and
  **PROG-000311** UChicago MRSEC, center, tier B (created PR #293; already carries
  specialty_materials, research_areas, engagement_modes, facilities_note — not a fills
  target here, but it is the bank target for two affiliations).
- People at the institution: 10 records in data/people.csv, **all 10 unlinked**
  (program_org_id empty) — the pool is the whole institutional roster: 7 Pritzker School
  of Molecular Engineering (PME), 3 Chemistry. All 10 are tier A as carried.
- The load-bearing discovery of this pass: PME's own research-areas hierarchy carries a
  page titled **"Polymeric Materials & Soft Matter"**
  (pme.uchicago.edu/institute-materials-and-sustainability/research-areas/polymeric-materials-soft-matter)
  — "Polymeric materials research at UChicago PME bridges soft matter chemistry and
  physics with macro-scale solutions to global challenges." — with a named Faculty
  roster for the area. That page is the prong-(b) witness for the drafted PME degree row
  (§3) and a roster witness for six of the seven PME links (§2).

## Component verdicts

### 1. Depth fills for PROG-000157 — 3 PROPOSED, 4 REFUSED (`fills.csv`)

PROG-000157 lands at an honest **2/5** (research_areas + facilities_note).

- **research_areas = polymer_physics; characterization_methods PROPOSED**, each from the
  track page's own description paragraph: "you will develop conceptions of the structure,
  physics, and macroscale properties of polymers, understand how these properties emerge
  from molecular-level interactions…" and "In the soft matter characterization lab,
  you'll develop the hands-on skills you'll need to study the structure, properties, and
  dynamics of soft materials."
- **research_areas / polymer_synthesis REFUSED** — it rests only on the curriculum line
  "Polymer Synthesis (MENG 35110)". Program research areas rest on research statements,
  not curriculum lines (UW–Stout ruling, PR #294). The refused quote is carried in
  fills.csv so the integrator sees exactly what was refused.
- **specialty_processes REFUSED** — the track's own page names no §3.1 process; specialty
  values are never inferred beyond the program's own page (§4.11).
- **specialty_materials REFUSED** — the only §3.2-adjacent word ("coatings") sits in a
  candidate-interests list: "This track suits candidates interested in: soft materials,
  polymers, packaging and coatings, consumer products, biomedicine, pharmaceuticals, and
  energy." A career-interest list is not a statement of the program's material focus.
- **facilities_note PROPOSED** at the grain the page states it: the soft matter
  characterization lab named in the track description (track core course MENG 35130).
  Explicitly NOT the MRSEC Soft Matter Characterization Facility on PROG-000311 — a
  different unit's statement; do not merge them.
- **scale_band REFUSED** — neither the track page nor the MEng overview publishes
  program enrollment; the S3 conversion has nothing to convert, and an MEng-wide figure
  would not be the track's enrollment anyway.

### 2. Links — 7 LINK, 2 BANKED, 3 NO_WITNESS (`links.csv`, 12 rows over 10 people)

All seven PME links target the drafted PME degree row (**NEW-UCHICAGO-PME**, §3),
contingent on its creation. **Integrator fallback, stated once here and in each row:** if
the row is declined, the seven fall back to LINK → PROG-000157 — PME's carried polymer
program row, but a weaker grain (a master's track is not these professors' program home;
the department row is the honest target, which is why it is drafted). Recommendation:
create the row.

- **LINK → NEW-UCHICAGO-PME (7):** Jie Xu (PERSON-000597), Stuart J Rowan
  (PERSON-000737), Aaron Esser-Kahn (PERSON-000738), Shrayesh N. Patel (PERSON-000757),
  Andrew Ferguson (PERSON-000813), Paul Nealey (PERSON-001368), Sihong Wang
  (PERSON-001369). Every one passes Gate A (current PME faculty styling on PME's own
  pages) and Gate B (person-level polymer witness on PME's own pages — profile or
  lab-group page quotes in links.csv). Six of the seven also sit on the Polymeric
  Materials & Soft Matter faculty roster; Ferguson does not (see weakest links).
- **BANKED → PROG-000311 (2 additional rows):** Rowan and Esser-Kahn. The MRSEC's own
  IRG 1 page: "our group brings together expertise in polymer synthesis/characterization
  (Esser-Kahn, Rowan), nano-to-macro experiments (Driscoll, Jaeger, Nagel, Tian),
  soft-materials modeling (Olvera de la Cruz, Witten), bio-soft matter theory (Dinner,
  Murugan), and learning in neural networks (Palmer)." Evidence only; program_org_id
  stays at the PME row. Nealey is NOT banked to the MRSEC on this packet: no fetched
  MRSEC page names him (his block-copolymer work is adjacent to the center's IRGs, but
  adjacency is not a witness).
- **NO_WITNESS (3):** John Stuart Anderson (PERSON-000773), S. J. Sibener
  (PERSON-000819), Ka Yee Christina Lee (PERSON-001390) — all Chemistry. All three pass
  both person gates on UChicago pages (quotes in links.csv); the blocker is uniformly
  the **program tie**: the Chemistry row test REJECTED (§3), and neither the James
  Franck Institute (Sibener, Lee) nor M-STAR (Anderson) holds an Atlas row or is
  polymer-named. BANKED is unavailable for all three — no witnessed tie to a held row
  exists to bank. Settling fact for each: a held program row styling them a member
  (named per-row in links.csv).

### 3. Department-row tests, §4.11 prong (b) — 1 drafted, 1 REJECT (`proposed_rows.csv`)

- **PME (Pritzker School of Molecular Engineering) — VERIFIED, drafted as
  NEW-UCHICAGO-PME** (degree; phd;ms). PME's own research-areas page names "Polymeric
  Materials & Soft Matter" as a research area of the school, in so many words, with a
  faculty roster: "Polymeric materials research at UChicago PME bridges soft matter
  chemistry and physics with macro-scale solutions to global challenges. PME researchers
  are developing functional and active polymers that process like traditional plastics
  while exhibiting advanced electronic, ionic, responsive, and responsive/adaptive
  properties, with impact across energy, water, sustainability, and human health."
  **Seam, stated plainly:** this is the OSU-Chemistry-class seam (dept-row pilot,
  PR #298) — the polymer naming sits on the school's own research-area page, not inside
  a degree-description page or a catalog concentration list. It is materially stronger
  than UTK CBE's posture (polymers appearing only as themes inside other thrusts — held
  STILL_UNCERTAIN in the pilot): PME names the polymer area itself, as an area, and
  rosters its faculty. If the owner holds UChicago to the UTK-catalog standard, this row
  and its nine links (7 carried + 2 census) fall together — the packet is built so that
  consequence is visible, not buried. research_areas on the draft are restricted to the
  polymer slice of the named area, from the area page's own text (polymer_physics;
  recycling_circularity — "circular-by-design plastics, the repurposing of existing
  plastic feedstocks into new functional materials"); specialty fields, facilities_note,
  scale_band, and cip_code are held blank with reasons in the row's notes. The draft is
  NOT a duplicate of PROG-000157: that row is the named MEng track credential; this is
  the unit's graduate degree program at department grain (the Penn two-grain pattern:
  PROG-000034 concentration alongside PROG-000343 CBE).
- **Chemistry — REJECT.** Deciding fact: the department's own research page
  (chemistry.uchicago.edu/research) enumerates its research areas as Catalysis,
  Materials Chemistry, Biophysics, Physical Chemistry, Chemical Biology, Organic
  Chemistry, Inorganic Chemistry, and Theoretical Chemistry — **none names polymers**,
  and "Materials Chemistry" is not polymer by name (the UT Austin Chemistry precedent,
  PR #310). Faculty polymer work (Sibener, Lee, Anderson) is prong-(c) corroboration,
  which never suffices alone. Settling fact that would reopen: a Chemistry page naming
  a polymer research area, track, or concentration for its degrees. Consequence, stated
  openly: the three Chemistry people in §2 stay unlinked on this pass — the rule
  refused their row, and the packet does not route around the refusal.

### 4. Census — 2 VERIFIED, 1 REJECT, 10 STILL_UNCERTAIN (`census.csv`)

Thirteen unrecorded names surfaced by the pages read this pass were dispositioned;
**none of the 13 has a record anywhere in data/people.csv** (checked 2026-11-12).

- **VERIFIED (2):**
  - **Chibueze Amanchukwu** (PME) — tier A. Gate A: "Neubauer Family Assistant
    Professor of Molecular Engineering, UChicago Pritzker School of Molecular
    Engineering" (PME research-area roster; matches his directory profile). Gate B,
    PME's own news page: "Amanchukwu's proposal is to design, synthesize, and
    characterize novel polymer electrolytes that can be used in solid-state lithium
    batteries." Mint; LINK → NEW-UCHICAGO-PME.
  - **Margaret L. Gardel** (PME / Physics / MGCD) — tier B, **roster-grade Gate B**:
    her keyword line on PME's Polymeric Materials & Soft Matter faculty roster reads
    "Cell and Tissue Mechanics; Polymer Physics; Cell Adhesion and Migration" — the
    school files her Polymer Physics under its polymer research area, but no
    profile-grade research statement was captured, so the mint rides at tier B with
    the flag on the record (PR #302 precedent). Her polymer strand is biopolymer
    (cytoskeletal) physics. Mint; LINK → NEW-UCHICAGO-PME.
- **REJECT (1): Matthew Tirrell** (PME) — Gate A fails on the deciding fact that
  UChicago's own pages style him **Professor Emeritus**: PME's research-area roster
  ("D. Gale Johnson Distinguished Service Professor Emeritus") and UChicago News
  (2026-10-20). Emeritus is outside Gate A in every rank (§4.9) even though his Gate B
  ("pioneering the design and synthesis of self-assembling polymers…") is the strongest
  in this census.
- **STILL_UNCERTAIN (10):** Po-Chun Hsu (area-roster seat, but his own keyword line
  names no polymer term — Gate B short at person level); **Juan J. de Pablo** (Gate B
  strong via Nealey's profile — "collaborative projects with Prof. Juan de Pablo have
  focused on block copolymer films" — but Gate A *currency* is unsettled: PME pages
  still carry his group while no fetched page styles him with a current title, and his
  primary-institution status is publicly in question — do not mint on this packet);
  Dmitri V. Talapin (Gate A passes as Chemistry DSP / M-STAR director; Gate B fails on
  every page consulted — quantum dots, nanoparticle assemblies, MXenes, no polymer
  statement); Heinrich Jaeger, Sidney Nagel, Aaron Dinner, Arvind Murugan, Bozhi Tian,
  Thomas Witten (MRSEC IRG-roster names whose expertise lines name soft matter, never
  polymers — Gate B unmet; Witten also carries unverified emeritus risk); Paul
  Alivisatos (Gate B unmet — nanomaterials only, on the pages consulted). Each row in
  census.csv names its settling fact.

## Weakest links in this packet (named, per protocol)

1. **Andrew Ferguson's LINK** — the only PME link not corroborated by the Polymeric
   Materials & Soft Matter faculty roster (he is absent from it as fetched). It rests on
   his own profile's polymer-simulation statement ("simulations of polymers, peptides,
   and colloids") plus his role as Director of Graduate Studies for the PhD in Molecular
   Engineering (Materials Track). A verifier holding him to roster corroboration would
   demote him to NO_WITNESS; the packet judges the profile-grade witness sufficient.
2. **The drafted row's polymer_physics cell** — rests on the area page's framing
   sentence ("bridges soft matter chemistry and physics"), the softest cell in
   proposed_rows.csv. recycling_circularity, by contrast, is quoted nearly verbatim
   ("circular-by-design plastics, the repurposing of existing plastic feedstocks").
3. **Patel's and Wang's Gate A** — their PME directory profile pages could not be
   re-fetched this pass (fetch-service 429; not retried per protocol). Gate A rests on
   PME's own research-area roster styling (fetched) plus the directory stylings already
   carried in their records; Gate B rests on PME's Patel Group page and Wang's
   uchicago.edu lab site respectively. One clean directory fetch at integration
   refreshes both.
4. **Anderson's Gate B grain** — "redox-active coordination polymers" is polymer at the
   scope edge (polymeric assemblies of inorganic clusters). It changes nothing here (he
   is NO_WITNESS on the program tie), but the integrator should carry the flag if a
   future row ever receives him.
5. **The two MRSEC banked rows** rest on a crawl of the IRG 1 page dated 2026-02-08 —
   the center's own page, but not same-day. A live re-read at integration would firm
   them; nothing in the packet contradicts them.
6. **Lee's Gate B** — genuine but thin: "cell-protective and cell-permeable polymers" is
   one strand inside a membrane-biophysics program. Recorded honestly as the pool's
   thinnest person-level witness (she is NO_WITNESS regardless, on the program tie).

## What this packet does NOT do

- No repo writes, no QUEUE claim, no IDs allocated (NEW-UCHICAGO-PME is a packet-local
  key; allocation is the integrator's).
- PROG-000311 (MRSEC) depth was not a fills target — it already carries 4 of 5 depth
  fields from its creation packet; only the two banked evidence rows in links.csv touch
  it.
- No §4.21 identifiers are proposed for anyone.
- The PME lab-groups page extract available to this lane truncated after the E
  surnames; census coverage is every name surfaced by the pages actually read (track,
  MEng, and PhD pages; lab groups A–E; the Polymeric Materials & Soft Matter roster;
  MRSEC IRG 1; M-STAR directory; Chemistry research page) plus targeted checks
  (Tirrell, Amanchukwu). A PME group page in the F–Z range with a polymer statement
  for an unrostered PI would be census residue for a later pass, not a gap this packet
  conceals.

---

## Integration record (integrator, 2026-11-12 — written from the built tree)

Unit: wave-4 tranche-2 University of Chicago school pass. Worktree `~/workspace/atlas-w4-uchicago-build-2026-11-12`,
branch `agent/spaghetti/wave4-tranche2-uchicago-2026-11-12`, base origin/main `db1184a`
(PR #327 head, verified by `git ls-remote` before the build). ID floors per the integration
brief, recomputed from the base tree before allocating (all 103 evidence shards scanned —
evidence IDs are global under V-22): tree maxima were PROG-000348 / PERSON-002181 /
EVD-334163, so this unit allocates PROG-000349 / PERSON-002182..002183 / EVD-334164..334181.
Paid calls: zero — no fetches were needed; the packet carries the witnesses.

**Landed, exactly per packet:**
- **PROG-000349 Molecular Engineering created** (degree, phd;ms, tier A, §4.11 prong (b)).
  Packet cells verbatim; only the allocated ID and the notes allocation marker differ from
  the draft. Existence evidence EVD-334164, scope EVD-334165.
- **PROG-000157 depth fills 0/5 → honest 2/5:** research_areas gains polymer_physics +
  characterization_methods and facilities_note set, each from the track page's own prose
  (scope evidence EVD-334166..334168, supports_B — the subject row is tier B). Refused cells
  stay blank: polymer_synthesis (curriculum line only, UW–Stout PR #294 ruling),
  specialty_processes, specialty_materials (candidate-interests list), scale_band (nothing
  published converts under S3). Only research_areas, facilities_note, and last_verified moved.
- **7 primary LINKs → PROG-000349** (program_org_id + last_verified only): Xu PERSON-000597
  (EVD-334169), Rowan PERSON-000737 (EVD-334170), Esser-Kahn PERSON-000738 (EVD-334172),
  Patel PERSON-000757 (EVD-334174), Ferguson PERSON-000813 (EVD-334175), Nealey
  PERSON-001368 (EVD-334176), Wang PERSON-001369 (EVD-334177).
- **2 BANKED affiliations → PROG-000311** (evidence only; program_org_id stands at
  PROG-000349): Rowan (EVD-334171) and Esser-Kahn (EVD-334173) on the MRSEC's own IRG 1
  page. Nealey deliberately NOT banked (no fetched MRSEC page names him).
- **3 NO_WITNESS byte-untouched:** Anderson PERSON-000773, Sibener PERSON-000819, Lee
  PERSON-001390 — raw lines byte-identical to the pre-pass backup; no evidence minted for
  them. Chemistry department row NOT created (packet REJECT under prong (b) stands: its own
  research page names eight areas, none polymer).
- **2 census mints:** PERSON-002182 Chibueze Amanchukwu (assistant_professor, tier A,
  linked → PROG-000349; EVD-334178/334179), PERSON-002183 Margaret L. Gardel (professor,
  tier B — roster-grade Gate B, the packet's flag carried verbatim in EVD-334181 — linked
  → PROG-000349; EVD-334180/334181). Tirrell REJECT (emeritus, Gate A) and the 10
  STILL_UNCERTAIN names (incl. de Pablo on appointment currency) not minted. No §4.21
  identifiers.
- **Rollup:** ORG-004660 recomputed — polymer_program_name "Polymer Science and Engineering
  (Master of Engineering track); University of Chicago Materials Research Science and
  Engineering Center (MRSEC)" → "Molecular Engineering; Polymer Science and Engineering
  (Master of Engineering track); University of Chicago Materials Research Science and
  Engineering Center (MRSEC)" (degree precedes center in V-16 order; "Molecular
  Engineering" sorts first among the degrees), polymer_program_url changes to the new
  row's URL (https://pme.uchicago.edu/academics/phd-program); last_verified already read
  2026-11-12, unchanged. Pre-build recompute reproduced the carried rollup exactly
  (zero drift).

**Integrator judgments / deviations from the packet draft (documented per protocol):**
1. **PME row CREATE (brief adjudication):** the packet's open call is settled CREATE. PME's
   own research-areas hierarchy carries a "Polymeric Materials & Soft Matter" page naming
   the polymer area in so many words, with a faculty roster — §4.11 prong (b) is satisfied
   at the OSU-Chemistry seam class (PR #298), materially stronger than UTK CBE's held
   thrust-theme posture. The seam is documented in the row's notes and in EVD-334164. The
   packet's fallback (link all 7 to PROG-000157) was NOT taken; per the packet's own terms,
   the row and its nine links (7 carried + 2 census) stand or fall together.
2. **Ferguson LINK stands** on his profile-grade witness (his own directory page's
   polymer-simulation statement + his Director of Graduate Studies role for the PhD the new
   row covers); the packet's weakest-link caveat — he is absent from the Polymeric
   Materials & Soft Matter faculty roster as fetched — is carried verbatim in EVD-334175's
   claim_detail and notes. A verifier holding him to roster corroboration would demote him
   to NO_WITNESS; the packet judges the profile-grade witness sufficient.
3. **Patel + Wang Gate A stand as the packet built them** (research-area roster styling +
   carried directory styling; their directory profile pages 429'd in the lane and were not
   retried — the packet flags one clean directory fetch as the refresh). Recorded in
   EVD-334174 / EVD-334177 notes.
4. **Mint cells the packet left to the integrator:** Amanchukwu's role_as_published records
   the roster/directory styling ("Neubauer Family Assistant Professor of Molecular
   Engineering, UChicago Pritzker School of Molecular Engineering"); Gardel's
   role_as_published carries her roster styling verbatim and her `role` folds to
   `professor` (Distinguished Service Professor). research_specialties on both mints are
   drawn from the packet's witnessed text only (Amanchukwu: the ECS news statement;
   Gardel: her roster keyword line, with the biopolymer grain named).
5. **Weakest cells, carried openly:** PROG-000349's polymer_physics cell rests on the area
   page's framing sentence (recycling_circularity is quoted nearly verbatim); the two
   MRSEC banked rows rest on a crawl of the IRG 1 page dated 2026-02-08 (the center's own
   page, not same-day) — both caveats ride in the evidence rows.

**Gates on the built tree:** `scripts/validate.py` → "OK — validation passed."
(1,513 people, 216 programs, 408 ecosystem, 41,227 evidence rows; warnings are the
standing classes only). `scripts/check_row_loss.py --base origin/main` →
"row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base
db1184a8f6)". Cross-shard evidence-ID uniqueness verified explicitly: all 41,227 evidence
IDs across the 103 shards occur exactly once. Row-level diff vs pre-pass backups = exactly
the adjudicated change set: programs +1 created / 1 changed, people +2 minted / 7 changed,
ecosystem 1 changed, evidence +18 pure appends (both evidence files byte-prefix pure),
QUEUE +1 claim line. Next frees: PROG-000350 / PERSON-002184 / EVD-334182.
