# Department-row pilot — Ohio State + UT Knoxville (2026-11-12)

Packet-only research lane. **No canonical files were edited, no repo files
were touched, nothing was pushed.** Data read from
`~/workspace/atlas-p2-2026-11-12/data/` (read-only). All fetches were free
routes (browser text fetch + web search). **Paid calls: zero, all
providers.**

**Owner rule under test (John, 2026-11-12):** a department-level degree
row is created ONLY when the department's own pages name polymers as a
research area, track, or concentration of its degrees (SCHEMA §4.11
prong (b)); faculty polymer work is corroboration (prong (c)), never
sufficient alone. A created row's `research_areas` stay restricted to
the polymer slice.

**Input:** the wave-3 residual-pools packet
(`working/wave3-2026-11-12/residual-pools/`), which attempted 42 people
against the rows then carried and returned 1 LINK / 41 NO_WITNESS,
diagnosing a program-row gap, not a witness gap. This pilot tests
whether creating the missing department rows — under the rule above —
closes that gap, and measures the yield before the class generalizes.

## Verdict table (unit + filter: 9 candidate units named in the brief)

| # | Institution | Candidate unit | Verdict | Basis in one line |
|---|---|---|---|---|
| 1 | Ohio State (ORG-001284) | Chemical & Biomolecular Engineering | **VERIFIED** | Department's own page names "polymers" among its research areas; its directory taxonomy carries a "Polymers, Nanomaterials" research area |
| 2 | Ohio State | Chemistry & Biochemistry | **VERIFIED** (seam flagged) | Department's Organic Chemistry research-areas page names "Polymer synthesis" as a research area |
| 3 | Ohio State | Materials Science & Engineering | **ALREADY CARRIED** | Degree row **PROG-000108** already exists — no new row (see correction note) |
| 4 | UT Knoxville (ORG-004681) | Chemistry | **VERIFIED** | Official catalog names a required **Polymer Chemistry** concentration of the Chemistry PhD |
| 5 | UT Knoxville | Chemical & Biomolecular Engineering | **STILL_UNCERTAIN** | Department names three research areas (Advanced Materials, Biomolecular Engineering, Sustainable Energy); polymers appear only as themes inside them |
| 6 | UT Knoxville | Civil & Environmental Engineering | **VERIFIED** (seam flagged) | Geotechnical & Materials research page names "Polymers, geomaterials, and composites" among its research areas |
| 7 | UT Knoxville | Mechanical / Aerospace / Biomedical Eng. | **REJECT** | Department's own research-areas page names five areas, none polymer; polymers are one of three material classes inside Manufacturing |
| 8 | UT Knoxville | SMaRT Center (center grain) | **STILL_UNCERTAIN** | Existence witnessed 2014–2018 only; no current center-owned page stating scope or roster found |
| 9 | UT Knoxville | IAMM (center grain) | **VERIFIED** | Institute's own site names **Polymer Science** as one of its five key research areas, with a dedicated page and roster |

## Prong-(b) quotes (verbatim, with source)

**1. OSU CBE — VERIFIED.** Department's own page (Dietz Chair posting,
cbe.osu.edu/endowed-dietz-chair-chemical-engineering, fetched 2026-11-12):

> "The William G. Lowrie Department of Chemical and Biomolecular
> Engineering (CBE) is home to 30 faculty working in diverse research
> areas including bioengineering, reaction engineering and catalysis,
> separations, systems engineering, particulates and multiphase flows,
> colloids, molecular simulation, **polymers**, nanomaterials, and
> sustainability."

Corroboration on the same domain: the faculty directory's research-area
view (cbe.osu.edu/directory/faculty-research-area, fetched 2026-11-12)
tags current faculty to the area "**Polymers, Nanomaterials**" (Cooper,
Hall, Kimmel entries read verbatim), and the department's facilities
page names a "**Polymer and Composite Processing**" laboratory. The
posting also states the credential set ("CBE offers undergraduate (B.S.)
and graduate (M.S. and Ph.D.) programs, with total enrollment around 900
students") — the enrollment figure grounds `scale_band=large` under the
§4.11/S3 conversion.

**2. OSU Chemistry & Biochemistry — VERIFIED, seam flagged.** The
department's own research-areas page for Organic Chemistry
(chemistry.osu.edu/research/research-areas/organic, fetched 2026-11-12)
carries a "Research Areas" list naming "**Polymer synthesis**", and tags
Davita Watkins "**Organic & Polymer Synthesis**" on the same page.
**Seam:** the naming sits on a division page inside the department's
research-areas tree, not on a department-wide index — the pilot's
second-weakest VERIFIED. Corroboration: the department operates the
Polymer Synthesis Research Facility (PROG-000018, already carried —
polymer by name at facility grain).

**3. OSU MSE — ALREADY CARRIED, and a correction to the brief.** The
brief described "the carried Polymer Engineering graduate certificate
PROG-000063" as living in OSU MSE. The data say otherwise: **PROG-000063
is the Macromolecules Innovation Institute at Virginia Tech
(ORG-002845)**. Ohio State MSE's degree row is **PROG-000108** (BS/MS/PhD,
CIP 14.1801), already admitted on this same basis — its notes record "a
named Polymers research area (biomaterials and polymers joining) and a
Polymers undergraduate focus area". No new MSE row is proposed, and no
pool person links to it: the residual packet read MSE's full directory
and none of the 27 appears (Ho is the documented near-miss; he stays
NO_WITNESS — see links.csv).

**4. UTK Chemistry — VERIFIED (strongest form).** The institution's
official catalog (2025-2026 Graduate Catalog, "Chemistry Major, PhD",
catalog.utk.edu/preview_program.php?catoid=55&poid=35066, fetched
2026-11-12) lists "**Concentrations (Required)**" including "**Polymer
Chemistry**", and the concentration's own section states:

> "Polymer chemistry is the study of the synthesis and properties of
> macromolecules composed of repeating chemical subunits."

with a required sequence of CHEM 590 Polymer Chemistry, CHEM 594
Organic Chemistry of Polymers, CHEM 595 Physical Chemistry of Polymers,
CHEM 596 Advanced Techniques in Polymer Synthesis and Characterization.
A named concentration in the degree's own catalog description is
prong (b) verbatim.

**5. UTK CBE — STILL_UNCERTAIN (the pilot's controlling judgment
call).** The department's Research Overview (cbe.utk.edu/research/,
fetched 2026-11-12) states:

> "we have targeted three fundamental research areas for emphasis in
> the next five years: **Advanced Materials, Biomolecular Engineering,
> and Sustainable Energy**."

Polymers appear only *inside* those areas — e.g., the Engineering of
Soft Materials thrust page (fetched 2026-11-12): "Key research themes
include **polymeric and polymer matrix composite materials**, nanoscale
self-assembly and organization, nano- and mesoscale-interfacial
engineering, **polymer synthesis and functionalization**, patterning
semiconductors, organic/inorganic elastomers, and rheology." That is
prong-(c)-grade corroboration — strong faculty polymer work inside a
differently-named area — and under the owner's rule it is not
sufficient alone. **Settling fact:** a CBE page that names polymers (or
a polymer/soft-materials area) in its research-area list itself, or a
catalog degree description naming a polymer track/concentration. Five
pool people ride on this call (Stein, Doxastakis, Khomami link via IAMM
meanwhile; Edwards and Corder remain unlinked — see links.csv).

**6. UTK CEE — VERIFIED, seam flagged (weakest VERIFIED).** The
department's Geotechnical & Materials Engineering page
(cee.utk.edu/research/geotechnical-and-materials-engineering/, fetched
2026-11-12):

> "The Geotechnical and Materials Engineering faculty members are
> active in a broad range of research areas, including: …
> **Polymers, geomaterials, and composites** …"

plus "Creating new soil materials –'tunable' clay-polymer composites".
**Seam:** "Polymers" is one item in a compound bullet on a research-
group page — named in a research-areas list on the department's own
site, which meets the letter of prong (b), but it is not a standalone
area or a degree concentration. The strengthening fact is a CEE
degree/concentration description naming polymers. The same page's
faculty list names the pool's one CEE person (Penumadu) verbatim.

**7. UTK MAE — REJECT.** Deciding fact: the department's own
Research Areas page (tickle.utk.edu/mae/research/areas/, fetched
2026-11-12) states "our faculty and students drive progress in **five
key research areas including computational science, energy storage,
manufacturing, robotics, and of thermal, fluid, and structural
systems**" — no polymer area, track, or concentration. What it *does*
name, inside Manufacturing, is "additive manufacturing of **polymers,
metals, and ceramics**" — polymers as one of three material classes,
which is not a named polymer research area. (The department now styles
itself Mechanical and Aerospace Engineering; IAMM's roster still uses
the older "Mechanical, Aerospace & Biomedical Engineering" styling.)
Compton and Duty are not lost: both are rostered on IAMM's Polymer
Science page and link there.

**8. SMaRT Center — STILL_UNCERTAIN.** SMaRT = Soft Materials Research
in Tennessee, developed by Kilbey with Dadmun ("we have developed the
Soft Materials Research in Tennessee (SMaRT) Center" — UTK CBE faculty
feature, published 2014); Dadmun is styled "Founding Director of the
Soft Materials Research in Tennessee (SMART) Center" in a 2015 UTK
Chemistry news item, and SMaRT appears as a funder in 2018 papers. No
current center-owned page stating scope or membership was found in
this lane's searches, and the center's own name is soft-materials
grain, not polymer. **Settling fact:** a current UT page for the SMaRT
Center stating its scope/roster — or confirmation that it was folded
into IAMM, whose Polymer Science area now rosters both founders.

**9. IAMM — VERIFIED (center grain).** The institute's own
research-areas page (research.utk.edu/iamm/research-areas/, fetched
2026-11-12) names "**Polymer Science** — Designing and creating new
advanced materials to improve industrial processes for an increasingly
circular economy" as one of its areas; the Tickle College labs page
states "IAMM focuses on five key research areas: advanced manufacturing,
advanced materials, materials for extremes, **polymer science**, and
quantum materials." The dedicated Polymer Science page
(research.utk.edu/iamm/research-areas/polymer-science/, fetched
2026-11-12) opens "Investigating polymers through a variety of
fundamental scientific problems with real-world impact" and rosters 26
named researchers. Center rows rest on prong (a) (a center named with
polymer scope) under the BioPACIFIC/MRSEC precedent — a different,
already-settled grain from the department rule.

## Measured yield (unit + filter stated)

Filter: the residual packet's 41 unlinked people (Ohio State ORG-001284:
27 people; UT Knoxville ORG-004681: 14 people), each given exactly one
primary disposition in `links.csv`, against the rows this pilot
proposes. People already carrying `program_org_id` were not re-examined.

| Measure | Count |
|---|---|
| Candidate units examined | 9 |
| VERIFIED units | 5 (OSU CBE, OSU Chemistry, UTK Chemistry, UTK CEE, IAMM) |
| STILL_UNCERTAIN units | 2 (UTK CBE, SMaRT) |
| REJECT units | 1 (UTK MAE) |
| Already-carried units | 1 (OSU MSE = PROG-000108) |
| **Program rows proposed** (`proposed_rows.csv`) | **5** |
| **New primary links** | **22 of 41 people** (Ohio State 11 of 27; UTK 11 of 14) |
| Banked second-program affiliations (witnessed, evidence-row only) | 7 |
| People remaining unlinked | 19 of 41 |

Primary links per proposed row:

| Proposed row | Primary LINKs | People |
|---|---|---|
| NEW-OSU-CBE (degree) | 5 | Cooper, Hall, Sangoro, Wang, Palmer |
| NEW-OSU-CHEM (degree) | 6 | Watkins, Bong, McGrier, Sevov, Olesik, Wyzgoski |
| NEW-UTK-CHEM (degree) | 5 | Dadmun, Zhao, Long, Brantley, Kilbey |
| NEW-UTK-CEE (degree) | 1 | Penumadu |
| NEW-UTK-IAMM (center) | 5 | Stein, Doxastakis, Khomami, Compton, Duty |
| **Total** | **22** | |

Banked affiliations (7): Watkins → OSU CBE (joint; primary Chemistry);
Dadmun, Zhao, Long, Brantley, Kilbey → IAMM (primary Chemistry);
Penumadu → IAMM (primary CEE; he holds its Chair of Excellence). The
five IAMM primaries are people whose degree home has no row (CBE
STILL_UNCERTAIN, MAE REJECT) — per the standing rule, `program_org_id`
takes the degree program where a person has one, otherwise the
witnessed center.

Why the remaining 19 stay unlinked (people, by reason):

- **Home department not a pilot candidate** (13): OSU — Castro and Park
  (ISE), Polyák (FABE), Vodovotz and Pascall (Food Science), Berger
  (ECE), Yi (ISE/optical science), Skardal and Y. Zhao (Biomedical
  Engineering), Dupaix and Dapino (MAE), Schricker (Dentistry);
  UTK — Popov (UTORII).
- **Membership itself contested** (2): Ho and Han — legacy CBE profile
  surfaces conflict with absence from CBE's current research-faculty
  directory (residual packet flags; settling facts in links.csv).
- **Emeritus** (1): Lee — directory-witnessed CBE membership, but
  emeritus styling never admits a link.
- **Joint, not primary** (1): Swindle-Reilly — primary home is
  Biomedical Engineering; CBE is one of three appointments.
- **Gated on the UTK CBE call** (2): Edwards and Corder — CBE's Soft
  Materials roster names them, but no CBE row exists and IAMM's
  Polymer Science roster does not.

## Judgment calls and flags (for the integrator / owner battery)

1. **UTK CBE is the pilot's controlling judgment call.** The rule as
   stated produces STILL_UNCERTAIN; a looser reading of the Soft
   Materials themes sentence would produce VERIFIED + 2 more links
   (Edwards, Corder primaries). The lane held the rule's letter —
   that is what the pilot is for — and the call is surfaced here
   rather than settled in the packet.
2. **Two VERIFIED rows carry flagged seams** (OSU Chemistry:
   division-page naming; UTK CEE: compound-bullet naming). Both are
   logged in their `proposed_rows.csv` notes with the strengthening
   fact named. If the owner holds department rows to the UTK Chemistry
   catalog standard, these two rows (and their 7 links) are the ones
   that fall.
3. **Brief-vs-data correction:** PROG-000063 is Virginia Tech's
   Macromolecules Innovation Institute, not an OSU MSE certificate
   (see unit 3 above). No OSU MSE work was needed.
4. **All five proposed rows carry `cip_code` blank.** No IPEDS
   completions pull ran in this lane; frame-candidate CIPs are named
   in the row notes as leads only (a CIP never satisfies prong (b) —
   Lakeland rule). The integration pass owes the completions pull.
5. **Minor roster staleness:** IAMM's Polymer Science page styles
   Brantley "Assistant Professor"; his record says Associate
   Professor. Membership is unaffected; no person record was touched.
6. **Popov (PERSON-001196) record-hygiene defect** (Cyrillic
   `full_name`, quote debris in `role_as_published`) is carried from
   the residual packet as flag-only; this lane did not adjudicate it.

## Fetch log (cap ~6 primary-source fetches per unit; all under)

| Unit | Fetches | Pages |
|---|---|---|
| OSU CBE | 2 | faculty directory (research-area view); Dietz Chair posting (department information section) |
| OSU Chemistry | 1 | Organic Chemistry research-areas page |
| OSU MSE | 0 | Carried row PROG-000108 read from data; directory reading relied on from the residual packet / Ohio lane B |
| UTK Chemistry | 1 | 2025-2026 Graduate Catalog, Chemistry Major PhD (two views of one page) |
| UTK CBE | 2 | Research Overview; Engineering of Soft Materials thrust page |
| UTK CEE | 1 | Geotechnical & Materials Engineering page |
| UTK MAE | 1 | Research Areas page |
| SMaRT | 0 | Searches only (2); no center-owned page surfaced |
| IAMM | 2 | Research Areas index; Polymer Science page |

Plus 8 web searches total for discovery. Availability: no fetch failed;
no bot walls encountered. The UTK catalog copy carries a 2026-01-23
crawl stamp (2025-2026 catalog, current at reading); all other pages
were crawled live on 2026-11-12.

## Files in this packet

- `README.md` — this file: verdicts, verbatim prong-(b) quotes,
  measured yield, judgment calls.
- `proposed_rows.csv` — 5 proposed program rows (all 36 `programs.csv`
  columns; `program_id` values are packet-local keys NEW-* — real IDs
  are allocated by the integrator at integration, above the tree-wide
  maximum).
- `links.csv` — 48 rows: the 41 pool people's primary dispositions
  (22 LINK / 19 NO_WITNESS) plus 7 LINK_BANKED second-program
  affiliations, each with its witness URL and quote.

## Integration record (integrator of record, 2026-11-12)

**Applied** on branch `agent/spaghetti/dept-row-pilot-2026-11-12` from
origin/main `8aecf0ca7a` (head after PR #297; build only — not pushed;
PR follows the standing batched-approval pattern). Build script:
`~/workspace/atlas-resync-2026-11-10/build_deptrow_pilot.py`; pre-pass
backups: `~/workspace/atlas-pilot-backups-2026-11-12/`. The packet
governed every cell; the only substitutions are the allocated
`program_id` values below.

**The pilot's measured result.** Creating the five rows the rule
admits converts 22 of the 41 residual-pool people from unlinked to
linked (Ohio State 11 of 27; UT Knoxville 11 of 14) — against the
residual pass's 1-of-42 yield against the previously carried rows.
Atlas-wide linked people: 353 → 375 of 1,472. Ohio State: 6 → 17 of 33
recorded people linked; UT Knoxville: 5 → 16 of 19.

- **Program rows created (5)** — packet cells verbatim, `cip_code`
  blank throughout (no IPEDS pull ran; the packet's frame candidates
  stand as leads in the row notes only):
  - **PROG-000316** — Ohio State, Chemical and Biomolecular
    Engineering (degree). Prong-(b) witness quoted in EVD-333785.
  - **PROG-000317** — Ohio State, Chemistry and Biochemistry (degree).
    Seam carried in the row notes and in EVD-333787 (division-page
    naming; second-weakest VERIFIED).
  - **PROG-000318** — UT Knoxville, Chemistry (degree). Prong (b) in
    its strongest form: the official catalog's required Polymer
    Chemistry concentration (EVD-333789).
  - **PROG-000319** — UT Knoxville, Civil and Environmental
    Engineering (degree). Seam carried in the row notes and in
    EVD-333791 (compound-bullet naming; weakest VERIFIED).
  - **PROG-000320** — UT Knoxville, Institute for Advanced Materials
    and Manufacturing (IAMM) (center, prong (a) on the BioPACIFIC/MRSEC
    grain).
- **Primary links applied (22)** — `program_org_id` + `last_verified`
  changed, nothing else: PROG-000316 ← Cooper PERSON-001324, Hall
  PERSON-000094, Sangoro PERSON-000093, Wang PERSON-001325, Palmer
  PERSON-000476; PROG-000317 ← Watkins PERSON-000033, Bong
  PERSON-000103, McGrier PERSON-000102, Sevov PERSON-000095, Olesik
  PERSON-001329, Wyzgoski PERSON-002005; PROG-000318 ← Dadmun
  PERSON-000962, Zhao PERSON-000965, Long PERSON-000991, Brantley
  PERSON-001171, Kilbey PERSON-000998; PROG-000319 ← Penumadu
  PERSON-001309; PROG-000320 ← Stein PERSON-000981, Doxastakis
  PERSON-001051, Khomami PERSON-001087, Compton PERSON-001310, Duty
  PERSON-001311 (the five whose degree homes are unrowed — UTK CBE
  STILL_UNCERTAIN, UTK MAE REJECT — so the witnessed center takes the
  primary link under the standing rule). One transparency note:
  Watkins's `last_verified` already read 2026-11-12 (refreshed earlier
  today by the residuals unit, EVD-333745), so her only cell change in
  this unit is `program_org_id`; her Professor title cells stand as
  merged and were not touched.
- **Banked affiliations (7)** — evidence rows only, `program_org_id`
  unchanged: Watkins → PROG-000316 (CBE; primary Chemistry);
  Dadmun, Zhao, Long, Brantley, Kilbey → PROG-000320 (IAMM; primary
  Chemistry); Penumadu → PROG-000320 (IAMM; primary CEE). Kilbey's CBE
  affiliation cannot bank — no CBE row exists.
- **Unlinked, byte-untouched (19)** — no link, no evidence row,
  asserted by row-level diff against the pre-pass backups: the 13
  whose home departments were not pilot candidates (Castro, Polyák,
  Park, Vodovotz, Berger, Yi, Skardal, Dupaix, Schricker, Pascall,
  Y. Zhao, Dapino at OSU; Popov PERSON-001196 at UTK — his
  record-hygiene defect stays flag-only, unadjudicated here), Ho
  PERSON-000037 and Han PERSON-000038 (membership contested; settling
  facts in the packet), Lee PERSON-000036 (emeritus styling never
  admits a link), Swindle-Reilly PERSON-001333 (joint; primary home
  Biomedical Engineering), and Edwards PERSON-001165 + Corder
  PERSON-001244 (gated on the UTK CBE call).
- **No rows, no evidence** — UTK CBE (STILL_UNCERTAIN: polymers appear
  only as themes inside its three named research areas; the packet
  names the settling fact, and the call is the pilot's controlling
  judgment item for the owner battery), UTK MAE (REJECT on its own
  research-areas page), SMaRT (existence witnessed 2014–2018 only).
  OSU MSE needed no work: its degree row PROG-000108 is already
  carried, and no pool person links to it.
- **Ecosystem rollups recomputed (V-16, same pass)** — ORG-001284:
  name "Materials Science and Engineering; Center for Electron
  Microscopy and Analysis (CEMAS); Polymer Synthesis Research Facility
  (PSRF); Program of Excellence in Natural Rubber Alternatives
  (PENRA)" → "Chemical and Biomolecular Engineering; Chemistry and
  Biochemistry; Materials Science and Engineering; Center for Electron
  Microscopy and Analysis (CEMAS); Polymer Synthesis Research Facility
  (PSRF); Program of Excellence in Natural Rubber Alternatives
  (PENRA)"; URL → https://cbe.osu.edu/directory/faculty-research-area.
  ORG-004681: name "Materials Science and Engineering" → "Chemistry;
  Civil and Environmental Engineering; Materials Science and
  Engineering; Institute for Advanced Materials and Manufacturing
  (IAMM)"; URL → the UTK Chemistry catalog page
  (catalog.utk.edu, catoid=55&poid=35066). Only the two rollup fields +
  `last_verified` changed on each row; the recomputation was first
  verified to reproduce both carried rollups from the pre-build tree.
- **Evidence minted (39 rows)** — programs EVD-333784..EVD-333793
  (existence + scope per created row, `own_site`, `supports_A` from
  the new records' tier A; each scope row quotes its prong witness,
  with the two flagged seams recorded in the OSU Chemistry and UTK CEE
  rows); people EVD-333794..EVD-333822 (22 LINK + 7 banked,
  claim_type `scope`, source_class `own_site`, in links.csv order;
  tier_effect from each subject person's own tier per §4.13 —
  `supports_A` ×28, `supports_C` ×1 for Wyzgoski, tier C). Allocation
  opens at EVD-333784: this tree's scan max was EVD-333783 and the
  range is contiguous. **Next free: EVD-333823 / PROG-000321.**
- **QUEUE** — the roster claim, the one straggler still standing
  `claimed` on current main, is flipped to `done 2026-11-12
  (PR #297, merged)` per the git log; this unit's claim is added
  below it.
- **Gates** — `scripts/validate.py`: "OK — validation passed."
  (totals: 1,472 people, 187 programs, 40,885 evidence rows; warnings
  only the standing classes, none naming this unit's records).
  `scripts/check_row_loss.py --base origin/main`: "row-loss guard:
  OK — no keyed row removed from data/ since origin/main (merge-base
  8aecf0ca7a)". No REMOVALS.csv.
