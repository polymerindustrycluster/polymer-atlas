# Wave 4, tranche 2 — Harvard University (ORG-004653) school pass — RESEARCH PACKET

Lane: spaghetti research lane, 2026-11-12. Packet only — no repo writes, no build.
Protocol read: repo `AGENTS.md`, `docs/SCHEMA.md` (§3.1/§3.2/§3.5 vocabularies,
§4.9 people + Gate A rank line, §4.11 program records + prong (b), §4.6/S3
scale-band conversion), `tasks/QUEUE.md`. Base: origin/main `db51af32`
(post PR #310), read via `git show origin/main:` — the local working tree of
the read clone carries unrelated uncommitted edits and was not used.

**Paid calls: zero, all providers.** All verification on Harvard's own pages
(seas.harvard.edu, mrsec.harvard.edu, chemistry.harvard.edu, gsas.harvard.edu,
otd.harvard.edu, and Harvard lab subsites) via free fetch/search routes.
Fetch tally (transparency): 12 primary page fetches + 1 roster fetch (MRSEC
Faculty Participants) + 4 searches. That is above the ~6-fetch guideline on its
face; the pool itself (4 carried people × person page + lab/group page) is 8 of
the fetches, and each remaining fetch settles a named component below.

## Institution facts

- Harvard has no MSE department; the materials unit is SEAS's **Materials
  Science and Mechanical Engineering (MSME)** area — carried as PROG-000124
  (degree, tier B, depth 0/5 at pass start).
- Also carried: **PROG-000312**, Harvard Materials Research Science and
  Engineering Center (MRSEC), center, tier B. Depth at pass start: 1/5
  (research_areas = `polymer_physics;biomedical_polymers`; specialty fields,
  facilities_note, scale_band empty). Per the lane brief it is **noted, not a
  fill target** in this packet.
- The MRSEC's own 2026–2027 pages (crawled 2026-11-08) style **Jennifer Lewis
  as Director** and David Weitz as Industrial Outreach Lead / IRG II Co-Lead.
  This corrects the stale "Director of the MRSEC" styling still shown on the
  Weitz Lab people page (copy crawled 2025-12-05). Nothing in this packet
  rests on the stale styling.
- Unlinked pool at ORG-004653 on current main: exactly **4 people**
  (unit: people records with `institution_org_id=ORG-004653` and empty
  `program_org_id`): PERSON-000682 David A. Weitz, PERSON-000683 Joanna
  Aizenberg, PERSON-000684 Jennifer A. Lewis, PERSON-000862 Zhigang Suo —
  all tier A. All 4 are disposed in `links.csv`; none was a NO_WITNESS.

## Component verdicts

### 1. Depth fills for PROG-000124 — 0 proposed, 5 REFUSED (`fills.csv`)

The MSME degree page (live crawl 2026-11-12,
https://seas.harvard.edu/index%2Ephp/materials-science-mechanical-engineering)
never names a polymer, a §3.1 process, or a §3.2 material family. Its stated
span: "comprehensive undergraduate and graduate programs that span from
fundamental research in solid and fluid mechanics to innovative studies in
materials, metamaterials, mechanical systems, soft materials and
biomechanics"; "Key areas of study include elasticity, plasticity, buckling,
fracture, and wave motion." Every depth cell is therefore refused with its
reason in `fills.csv` — the row honestly stays **0/5**. The program's polymer
content is real but faculty-grain (Suo's polymeric gels, Aizenberg's
hydrogel-actuated polymer structures), which is prong-(c) corroboration and
cannot fill program cells; this matches the Cal Poly posture (PR #292), where
research_areas were held when no §3.5 topic was named at program level.

### 2. Links — 4 LINK, 2 additional BANKED, 0 NO_WITNESS (`links.csv`)

- **Zhigang Suo (PERSON-000862) → LINK PROG-000124; BANKED PROG-000312.**
  Gate A (SEAS person page, live): "Allen E. and Marilyn M. Puckett Professor
  of Mechanics and Materials"; "Primary Teaching Area: Materials Science &
  Mechanical Engineering". Gate B (Suo Group, RESEARCH INTERESTS): "Mechanics
  of soft active materials (SAMs), such as dielectric elastomers and
  polymeric gels." Bank witness: MRSEC 2026–2027 roster lists him in IRG II.
- **Joanna Aizenberg (PERSON-000683) → LINK PROG-000124; BANKED PROG-000312.**
  Gate A (SEAS person page, live): "Amy Smith Berylson Professor of Materials
  Science and Professor of Chemistry & Chemical Biology"; "Primary Teaching
  Area: Materials Science & Mechanical Engineering". Gate B (Aizenberg Lab):
  "HAIRS consist of flexible, high-aspect-ratio polymer or silicon structures
  coupled with a responsive hydrogel, where the hydrogel, upon expansion and
  contraction, acts as a 'muscle' to move or actuate the passive polymer
  'bones'." Bank witness: her SEAS page carries the verbatim line
  "Participant, Materials Research Science and Engineering Center", and the
  MRSEC roster lists her in IRG II. Note for the integrator: the original R2
  adjudication behind PROG-000124 counted Aizenberg as MSME-primary but
  polymer-unstated *on SEAS directory pages*; her own lab's research
  statement states the polymer research explicitly, which is what this LINK
  rests on.
- **David A. Weitz (PERSON-000682) → LINK PROG-000312.** Tie is the MRSEC's
  own current roster: "David A. Weitz (Physics, SEAS)" in IRG I and "(Co-Lead)"
  in IRG II (Faculty Participants 2026–2027); Executive Committee listing
  "David A. Weitz | SEAS & Physics | Industrial Outreach Lead". Gate A (Weitz
  Lab people page): "Mallinckrodt Professor of Physics and Applied Physics".
  Gate B (same page): "The group also investigates the mechanical properties
  of biopolymer networks, both model, reconstituted networks, and those in
  cells…"; his carried tier-A specialty reads "soft matter physics: colloids,
  emulsions, drops, polymers and gels". His home areas hold no row (Applied
  Physics row REJECTED below; Physics STILL_UNCERTAIN), so the MRSEC is his
  only held-program tie.
- **Jennifer A. Lewis (PERSON-000684) → LINK PROG-000312.** Tie: MRSEC About
  page, Executive Committee 2026–2027 — "Jennifer Lewis | SEAS | Director";
  Faculty Participants lists her in IRG II. Center-director linkage follows
  the CMU precedent (Matyjaszewski → the center he directs, PR #304). Gate A
  (SEAS person page, live): "Hansjorg Wyss Professor of Biologically Inspired
  Engineering", "Area Chair, Bioengineering", "Primary Teaching Area:
  Bioengineering" (no held row; REJECTED below). Gate B (Harvard OTD news,
  2026-04-29, on her lab's rotational multimaterial 3D printing): "Their
  active material is a liquid crystal elastomer, a special type of polymer
  that has attracted research interest as a candidate for artificial
  muscle…"; carried tier-A specialty: "liquid crystal elastomer active
  materials".

### 3. Department-row tests, §4.11 prong (b) — 0 drafted, 3 REJECT, 1 STILL_UNCERTAIN (`proposed_rows.csv`)

- **SEAS Bioengineering — REJECT.** Its own degree page's Research Areas
  (live fetch): "Bioinspired Robotics and Computing; Biomechanics and Motor
  Control; Cell and Tissue Engineering, Biomaterials, and Therapeutics;
  Science and Engineering for ClimateTech" — no polymer named.
- **SEAS Applied Physics — REJECT.** The PhD program page's own list of
  research projects: "Quantum Science and Engineering; Photonics; Quantum
  Materials; Soft Matter and Soft Materials; Biomaterials and Biophysics;
  Climate and Sustainability Solutions" — no polymer named. ("Soft Matter"
  is not polymer by name; cf. UTK CBE held in the pilot.)
- **Chemistry and Chemical Biology — REJECT.** CCB's own Faculty & Research
  page enumerates its areas (Analytical, Biophysics, Catalysis, Chemical
  Biology, Energy Related, Inorganic, Materials, Organiometallics/
  Organometallics, Physical/Chemical Physics, Theoretical) and the GSAS
  Areas of Study are "Chemical Biology | Chemical Physics | Inorganic |
  Organic | Physical | Theory" — no polymer area, track, or concentration.
  Individual CCB polymer work (Aizenberg; Shakhnovich's blurb, below) is
  prong-(c) corroboration only.
- **Department of Physics (FAS) — STILL_UNCERTAIN.** Not fetched within
  budget; settling fact named in `proposed_rows.csv` (its own graduate
  research-area enumeration). Expectation is REJECT — the SEAS taxonomy on
  fetched pages never tags Physics faculty with a "polymer" area — but the
  verdict waits on the department's own page.

### 4. Census — 1 VERIFIED, 12 STILL_UNCERTAIN (`census.csv`)

Census frame: the MSME area's faculty plus the MRSEC Faculty Participants
roster for 2026–2027 (the center's own current roster), cross-checked against
`data/people.csv` on current main.

- **VERIFIED: Frans A. Spaepen** (tier B, roster-grade Gate A flag stated in
  `census.csv`). Gate A: SEAS person page styling "John C. and Helen F.
  Franklin Professor of Applied Physics", "Director of Undergraduate
  Studies, Materials Science & Mechanical Engineering", "Primary Teaching
  Area: Materials Science & Mechanical Engineering" — no emeritus styling —
  corroborated as current by the MRSEC 2026–2027 roster (IRG I). Gate B
  (Spaepen Lab, live crawl 2026-11-12): "Amorphous materials (metals,
  semiconductors, polymers): structure, formation, stability, mechanical
  properties, atomic transport…". Primary program PROG-000124 per his
  Primary Teaching Area styling; banked PROG-000312. Notable: Spaepen was
  one of the two faculty whose stated polymer areas carried PROG-000124's
  original R2 promotion, yet he was never himself recorded.
- **STILL_UNCERTAIN (12):** David J. Mooney (Gate A passes verbatim —
  "Robert P. Pinkas Family Professor of Bioengineering", MRSEC IRG II Lead —
  but no person-level polymer statement fetched; settling fact = a Mooney
  Lab research page or his SEAS person page stating polymer/hydrogel
  research in his own description); Eugene Shakhnovich (Gate B blurb present
  verbatim on CCB's own Theoretical Chemistry page — "structural and
  dynamical properties of other complex polymer systems" — but current
  Gate A styling unverified); Vinothan N. Manoharan, Katia Bertoldi,
  Michael P. Brenner, Boris Kozinsky, Jarad A. Mason, Richard Y. Liu,
  Joost J. Vlassak, David R. Nelson, Kevin (Kit) Parker (all MRSEC
  2026–2027 participants; Gate B unwitnessed within this pass's budget,
  settling fact named per person); Samir Mitragotri (named lead outside
  this pass's roster frame; nothing fetched).

## Weakest links in this packet (named, per protocol)

1. **Weitz's Gate B** is the softest link evidence: his person-level polymer
   wording on a live Harvard page is "biopolymer networks" (Weitz Lab people
   page, copy crawled 2025-12-05) plus his carried tier-A specialty string.
   His MRSEC *tie* is current and strong (the center's own 2026–2027
   roster), and his group's microgel IRG work is polymer science in
   substance — but a verifier holding him to a fresh, explicit "polymer"
   statement in his own research description would land him at
   STILL_UNCERTAIN, with the settling fact being exactly that statement
   (e.g. a refreshed Weitz Lab research page or his Salata Institute faculty
   page: https://salatainstitute.harvard.edu/faculty/david-weitz/, already
   among his record's sources, not re-fetched this pass).
2. **Spaepen's Gate A currency**: his SEAS person-page styling reaches this
   packet as an 84-day-old search extract, corroborated by the MRSEC
   2026–2027 roster and his live lab page. If the integrator wants tier A,
   refresh the person page before minting; the packet claims tier B.
3. **Applied Physics / CCB REJECTs rest partly on search extracts** of the
   departments' own pages (crawled 1–12 days before this pass) rather than
   full fetches; the quoted enumerations are the pages' own lists and the
   Bioengineering REJECT — the same test, same school — was confirmed by
   live fetch. A verifier re-fetch of the Applied Physics graduate-program
   page and CCB's Faculty & Research page would harden both.

## What this packet does NOT do

- No fills for PROG-000312 (per brief; noted at 1/5 depth above).
- No people beyond the 4-person pool and the named census frame.
- No §4.21 identifiers (Suo's Suo Group page links a ResearcherID —
  harvesting is opportunistic-only under the mint rule and was not part of
  this lane's charge; noted here so a later §4.21 pass can pick it up from
  his institution-hosted page).
- QUEUE not claimed: research lanes produce packets; the integrator of
  record claims and builds.

---

## Integration record (integrator of record, 2026-11-12 — written from the built tree)

**Unit:** wave-4 tranche-2 Harvard school pass integration. **Worktree:**
`~/workspace/atlas-w4-harvard-build-2026-11-12`; **branch:**
`agent/spaghetti/wave4-tranche2-harvard-2026-11-12`; **base:** origin/main
`db51af320d9c954090a89d2bc729acaca62a8969` (PR #310 head). **Build script:**
`~/workspace/atlas-resync-2026-11-10/build_w4_harvard.py` (packet CSVs read
programmatically). **Pre-pass backups:**
`~/workspace/atlas-w4-harvard-backups-2026-11-12/`. **Paid calls: zero.**
The four packet CSVs in this folder are byte-identical to the staging packet
as authored; this record is appended to the README only.

**ID allocation.** Floors per the integrator brief (parallel tranche-2 units
allocate above their own floors): **PERSON-002173 / EVD-334130**; no new
programs. Tree maxima scanned on the base: PERSON-002167 / EVD-334069 /
PROG-000347 — all below the floors, asserted at build. Used: PERSON-002173
(1 mint); EVD-334130..EVD-334138 (9 evidence rows, contiguous). Next frees:
PERSON-002174 / EVD-334139; programs untouched (next free stands at the
cross-unit floor).

**Fills — none applied.** All five PROG-000124 depth cells stand REFUSED per
`fills.csv` (the MSME degree page names no polymer, §3.1 process, or §3.2
material; its polymer content is faculty-grain prong-(c) corroboration —
Cal Poly PR #292 posture). `data/programs.csv` and
`data/evidence_programs.csv` are **byte-identical to the pre-pass backups**:
PROG-000124 stays 0/5, PROG-000312 (not a fill target in this unit) is
unchanged, no program rows created.

**Links applied** (people rows changed in exactly `program_org_id` +
`last_verified`):
- PERSON-000862 Zhigang Suo → PROG-000124 (EVD-334130 scope); BANKED
  PROG-000312 (EVD-334131).
- PERSON-000683 Joanna Aizenberg → PROG-000124 (EVD-334132 scope); BANKED
  PROG-000312 (EVD-334133, resting on her SEAS page's verbatim "Participant,
  Materials Research Science and Engineering Center" line plus the MRSEC
  2026–2027 roster).
- PERSON-000682 David A. Weitz → PROG-000312 (EVD-334134 scope). **Caveat
  carriage:** the packet's Gate B caveat is carried verbatim in the row —
  his person-level wording is "biopolymer networks" (Weitz Lab people-page
  copy crawled 2025-12-05) plus his carried tier-A specialty string; the
  settling fact (a fresh explicit polymer statement, e.g. his Salata
  Institute page) is named in the row. The stale "Director of the Materials
  Research Science and Engineering Center" styling on the Weitz Lab page is
  used **nowhere** as a claim; its only occurrence in the built evidence is
  inside that caveat sentence, which identifies it as stale. The LINK rests
  on the MRSEC's own current 2026–2027 roster (IRG I; IRG II Co-Lead;
  Industrial Outreach Lead).
- PERSON-000684 Jennifer A. Lewis → PROG-000312 (EVD-334135 scope), as the
  center's Director per the MRSEC's own 2026–2027 Executive Committee page
  (CMU center-director precedent, PR #304).

All four link subjects are tier A; every link/bank evidence row carries
`tier_effect = supports_A` (each subject's own tier, §4.13).

**Census mint (1).** PERSON-002173 **Frans A. Spaepen**, tier B, `role`
professor, `role_as_published` "John C. and Helen F. Franklin Professor of
Applied Physics", linked → PROG-000124, MRSEC affiliation banked. Evidence:
EVD-334136 existence, EVD-334137 scope, EVD-334138 banked (all
`supports_B`, his own tier). **Flag carriage:** the packet's tier-B Gate A
currency caveat (SEAS person-page extract crawled 84 days before the pass;
currency corroborated by the MRSEC 2026–2027 roster and his live lab page;
no emeritus styling anywhere) is carried verbatim in EVD-334136 and
EVD-334137. The 12 STILL_UNCERTAIN census names were **not** minted
(strongest near-miss: David J. Mooney — Gate A passes verbatim, no
person-level polymer statement fetched; settling fact stands in
`census.csv`). Dedupe: no Spaepen record existed anywhere in people.csv;
Mooney/Shakhnovich/Manoharan confirmed absent at ORG-004653 before minting.

**Department rows — none created.** The packet verdicts stand and are
recorded here: SEAS Bioengineering REJECT, SEAS Applied Physics REJECT,
Chemistry and Chemical Biology REJECT (each department's own enumeration
names no polymer area, track, or concentration — §4.11 prong (b) fails;
individual faculty polymer work is prong-(c) corroboration only), FAS
Physics STILL_UNCERTAIN (settling fact: the department's own
graduate-program research-area enumeration).

**Rollup verdict.** The §4.11 V-16 rollup for ORG-004653 was recomputed
from the built program set (PROG-000124 + PROG-000312, both active) and
reproduces the carried `polymer_program_name` / `polymer_program_url`
exactly — no program-set change in this unit. `data/ecosystem.csv` is
byte-identical to the pre-pass backup; the ORG-004653 row is untouched.

**§4.21.** No identifiers minted or harvested in this unit. The packet's
note that Suo's institution-hosted Suo Group page links a ResearcherID is
recorded here as a later §4.21-pass lead only.

**Evidence totals.** `data/evidence_people.csv`: +9 rows
(EVD-334130..EVD-334138), a pure byte-prefix append over the backup
(asserted at build verification). `data/people.csv`: 4 rows changed,
1 row added (1,501 → 1,502 people). QUEUE: +1 line (this unit's claim,
inserted directly after the UT Austin claim; prior claims stand as they
are on this base).

**Gates (run on the built tree, verbatim):**
- `scripts/validate.py` → "OK — validation passed." (5,024 organizations,
  7,190 sites, 408 ecosystem rows, 1,502 people rows, 214 program rows,
  41,141 evidence rows; warnings are the standing classes only.)
- `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK —
  no keyed row removed from data/ since origin/main (merge-base
  db51af320d)". No REMOVALS.csv.
