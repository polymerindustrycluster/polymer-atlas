# Wave 4 school pass — University of Pennsylvania (ORG-002176)

Lane: packet-only research (no repo data written, no branch, no PR). Date: 2026-11-12.
Base state re-derived from origin/main 79b1f42b (PR #299 head): Penn carries exactly two
program rows — PROG-000110 Materials Science and Engineering [degree] and PROG-000034
Polymers and Soft Matter Science and Engineering concentration [course] — both at depth
0/5 (all five depth cells empty), and 16 people records, 0 linked. Paid calls: **zero**
(direct page fetches and free search only; every witness is on upenn.edu pages).

## Verdicts

### Carried rows (unit: 2 carried program rows at ORG-002176; filter: status=active)

| Row | Verdict | Result |
|---|---|---|
| PROG-000110 MSE [degree] | **FILLS PROPOSED** (fills.csv, 5 rows) | research_areas (3 terms, one row each), specialty_materials (1 term), facilities_note. Goes 0/5 → 3/5 honestly filled. specialty_processes and scale_band HELD (below). |
| PROG-000034 Polymers & Soft Matter concentration [course] | **NO FILLS — honest hold** | Its own page (CBE undergraduate concentrations) is a curriculum list. research_areas are for research programs (§4.11) and specialty cells would have to rest on course titles = curriculum inference, dropped per the dept-row pilot's UW–Stout ruling. The row stays 0/5; that is the correct state for a course-grain row, not a gap. |

Held cells on PROG-000110, with reasons:
- `specialty_processes`: the MSE research-areas page names no §3.1 process as the
  program's polymer specialty. Not inferred.
- `scale_band`: the only size figure found on the program's own pages is the MSE
  Graduate Group's "~ 70 members" — a faculty count, which never converts under the
  S3 rule. No program enrollment is published on the pages fetched.

The MSE department itself names "Polymers and Soft Matter" as one of its research-area
taxonomy entries (Graduate Group page, faculty sorted by research topic) — the program's
own research statement for the polymer slice is the dedicated Polymers section of its
Research Areas page, quoted in fills.csv.

### Department-row tests, §4.11 prong (b) (unit: 4 departments where the unlinked pool sits)

| Department | Verdict | Basis |
|---|---|---|
| Chemical & Biomolecular Engineering | **VERIFIED — row drafted** (proposed_rows.csv, NEW-PENN-CBE), **seamed** | The department's own undergraduate concentrations page names a concentration of its B.S. degree: "Students majoring in Chemical and Biomolecular Engineering may elect to follow a concentration in Polymers and Soft Matter Science and Engineering." Seam documented in the row's notes and below. |
| Chemistry | **STILL_UNCERTAIN** — no draft | The Chemistry PhD's own published description enumerates its research fields (bioinorganic, bioorganic, chemical biology, biophysical, bioinformatics, materials science, laser, health-related, …) and names no polymer/macromolecular field; the Master of Chemical Sciences page likewise lists areas without polymers. Against that, Percec's department profile header styles his area "Organic, Supramolecular and Macromolecular Chemistry" — person-grain naming only. Settling fact: a chem.upenn.edu research-areas / faculty-by-area page, or a degree description, naming polymer or macromolecular chemistry as a research area of the department's degrees. |
| Bioengineering | **STILL_UNCERTAIN** — no draft | BE's published research areas (16 categories incl. Biomaterials, Cell Mechanics, Drug/Gene Delivery) name no polymer area; "polymer engineering" appears only as a phrase inside the Cell Mechanics area description — theme-level, prong-(c) posture (the UTK CBE parallel). Settling fact: a BE page naming polymers / polymer science as a named research area, track, or concentration of its degrees. (Area list read on the department's be-dev.seas.upenn.edu mirror — flagged under weakest links.) |
| Mechanical Engineering & Applied Mechanics | **REJECT** — no draft | Deciding fact: MEAM's own graduate-group page enumerates the department's research areas — Advanced Manufacturing; Computational and Data Science and Engineering; Design; Energy Science and Engineering; Fluid Mechanics; Mechanics and Materials; Mechanical Engineering in Biology and Medicine; Micro- and Nano-Scale Science and Engineering — and none is polymer-named. (Same posture as the pilot's UTK MAE reject.) Arratia's polymer work is handled by banking, below. |

**The CBE seam, stated plainly (weakest link #1).** The draft rests on prong (b)'s
letter: a named polymer concentration *of the department's degree*. The counter-reading
is real: the department's named research areas do not include a polymer-named area —
"Soft Matter and Complex Fluids" is the named area and its own page names polymers only
as a member class ("such as polymers, gels, emulsions and suspensions"), which is
exactly the posture the pilot held STILL_UNCERTAIN at UTK CBE. The concentration is
also already carried at course grain (PROG-000034); the drafted degree row represents
the department's degrees, not the concentration, and does not duplicate it. If the
integrator/owner holds CBE to STILL_UNCERTAIN, the packet degrades gracefully: the six
CBE-primary LINKs become BANKED on witnesses already in links.csv (five of the six also
hold MSE Graduate Group memberships witnessed on the grad-group page).

### People (unit: 16 unlinked people records at ORG-002176; filter: program_org_id empty on origin/main)

Dispositions in links.csv: **LINK 9 · BANKED 7 · NO_WITNESS 0.**

- LINK → PROG-000110 (MSE primary home): Winey*, Composto, Shu Yang, Madl (4).
  *Winey is 50:50 CBE/MSE on her own profile; linked to MSE on the MSE Graduate Group
  page's primary-department styling, with the CBE bank recorded in her note.
- LINK → NEW-PENN-CBE (CBE primary home, contingent on the drafted row): Osuji,
  Riggleman, Stebe, Daeyeon Lee, Amish Patel (5).
- BANKED → PROG-000110 on MSE Graduate Group membership: Percec, Saven, Fakhraai
  (Chemistry primaries), Janmey (Physiology primary / BE secondary), Vining (Dental
  primary, MSE assistant-professor appointment — the same witness would support LINK
  if the integrator judges the MSE appointment co-primary) (5).
- BANKED → NEW-PENN-CBE on witnessed secondary appointments: Hammer (BE primary),
  Arratia (MEAM primary) (2).

Gate discipline: every LINK/BANKED carries a person-level polymer witness on a Penn
page (Gate B) and a current-faculty styling (Gate A). Two witnesses deserve note:
Hammer's own CBE-hosted profile never uses the word "polymer" — his Gate B witness is
the department Labs + Facilities page's description of his laboratory (polymersomes,
block copolymers). Stebe's labs-page blurb likewise lacks the word; her witness is the
MSE Graduate Group page's person-level research-area tag ("Polymers and Soft Matter"),
the same directory-tag standard the pilot accepted at Ohio State.

### Census (unit: faculty on the rosters consulted in this pass — MSE departmental
faculty + Graduate Group pages, CBE faculty/labs pages, Chemistry and MEAM pages;
filter: Gate A current-faculty styling + Gate B person-level polymer witness on a Penn
page, primary department in {MSE, CBE, Chemistry, Bioengineering, MEAM}, no Atlas
record tree-wide)

**9 candidates** in census.csv: I-Wei Chen, Vivek B. Shenoy, Eric Detsi, Yuanwen Jiang
(MSE); John C. Crocker, Dennis E. Discher (CBE); Thomas E. Mallouk (Chemistry);
Robert W. Carpick, Kevin T. Turner (MEAM). Name checks ran against the full people
table, not just Penn's rows (the carried Turner and the several Jiangs/Chens elsewhere
are different people).

Out-of-scope sightings (not censused; primary departments outside the tested set):
Cherie Kagan (ESE) and Physics faculty Doug Durian, Randy Kamien, and Andrea Liu all
carry "Polymers and Soft Matter" tags on the MSE Graduate Group page. Also noticed, not
actioned: the Laboratory for Research on the Structure of Matter (LRSM) / Penn MRSEC —
center grain, outside this lane's department-row scope. Wenhao Gao (CBE) was excluded
from census deliberately: his own profile styles him "incoming Assistant Professor"
with a January 2027 start — not current faculty at fetch date.

## Weakest links (ranked)

1. **The CBE drafted row's prong-(b) seam** (above). Everything else in the packet
   survives it being held.
2. **Stale profile copies for the two Chemistry banks**: Fakhraai's chem.upenn.edu
   profile copy was crawled 2025-12-09 and Saven's 2025-11-28. Both are the
   department's own pages and corroborated by fresh grad-group tags, but the
   integrator may re-open them at build.
3. **BE area list read on a dev-subdomain mirror** (be-dev.seas.upenn.edu). It gates
   nothing — BE is STILL_UNCERTAIN either way — but the settling fact should be
   checked against the live be.seas.upenn.edu site.
4. **Discher's Gate A styling** rests partly on a 2006 Penn Today article; his current
   presence is independently established by the department's current Labs + Facilities
   page (named group + facility directorship), but no current page in this lane
   confirms a named-chair styling.
5. **I-Wei Chen's currency** rests on the MSE faculty page's Primary Faculty placement
   (crawled 2026-11-09) as against its separate Emeriti tab — the standard is the
   institution's own styling, but the integrator should re-verify at build.

## Fetch log (summary)

Direct fetches (browser.open): CBE concentrations page; MSE Graduate Group page; MSE
Research Areas page; MSE departmental Faculty page; CBE research-areas index; CBE Soft
Matter and Complex Fluids area page; CBE Labs + Facilities page; CBE profiles for
Hammer; Chemistry profiles for Percec, Fakhraai, Saven; Physiology profile for Janmey;
Penn Engineering directory profiles for Detsi (via grad-group outlink) and Vining.
Searches (free): MSE research areas; CBE research areas (×2); Penn Chemistry research
areas / PhD program; Bioengineering research areas; MEAM research areas + Carpick /
Turner; Mallouk title; Discher title; Yuanwen Jiang title. No fetch failed outright;
no verdict in this packet rests on a failed fetch. Repo data re-derived from
origin/main via git show (ecosystem / programs / people), never from the stale audit
clone.

## INTEGRATION RECORD (integrator of record: spaghetti, 2026-11-12)

Built in worktree `~/workspace/atlas-w4-penn-build-2026-11-12`, branch
`agent/spaghetti/wave4-penn-2026-11-12`, base origin/main `848175b9` (PR #302 head).
Local only at build time — no push, no PR. Build report:
staging `working/wave4-2026-11-12/penn/integration-build-report.md`. Pre-pass backups:
`~/workspace/atlas-w4-penn-backups-2026-11-12/`. Paid calls: zero.

### CBE department-row ruling (integrator, on the owner rule of 2026-11-12)

**CREATE — PROG-000343, Chemical and Biomolecular Engineering (degree, bs;ms;phd).**
Prong (b) is satisfied in the rule's own terms: CBE's own undergraduate concentrations
page names "Polymers and Soft Matter Science and Engineering" as a concentration of
its B.S. — a degree structure, which is stronger than the theme-inside-a-thrust
posture held STILL_UNCERTAIN at UTK CBE. The seam stays documented, here and in the
row's notes: the department's named research areas include no polymer-named area
("Soft Matter and Complex Fluids" is the named area and names polymers only as a
member class), and the concentration is also carried at course grain as PROG-000034
(untouched by this unit; the degree row represents the department's degrees, not the
concentration). research_areas stays restricted to the packet's polymer slice
(polymer_physics;biomedical_polymers;membranes_separations); specialty fields and
scale_band held empty per the packet; cip_code blank (no IPEDS pull ran; frame
candidate 14.0701 is a lead in the row notes only). Existence witness EVD-333906,
scope witness EVD-333907. The packet's graceful-degradation path was NOT taken: no
CBE link converted to banked.

### I-Wei Chen currency re-check (integrator ruling 4)

The live MSE faculty page (https://mse.engineering.upenn.edu/faculty/, read at build
time, 2026-11-12) still lists I-Wei Chen under **Primary Faculty** as "Skirkanich
Professor of Innovation"; the Emeriti Faculty tab does not carry him. **Mint
proceeded** — PERSON-002144, linked to PROG-000110. The same live read corroborated
Shenoy's Primary Faculty styling, Turner's Secondary Faculty styling, and Osuji's
MSE Secondary Faculty styling used for his banked row.

### Program rows

- **PROG-000110 (MSE degree): fills applied exactly per fills.csv** — research_areas
  polymer_physics;membranes_separations;biomedical_polymers, specialty_materials
  coatings, facilities_note per packet (0/5 → 3/5). specialty_processes and
  scale_band stay blank as the packet holds them. Depth evidence EVD-333908..333912
  (one scope row per fills.csv row). last_verified → 2026-11-12. No other cell moved.
- **PROG-000034 (course): untouched, byte-identical** — held at 0/5 by design.
- **PROG-000343 created** (above). Only deviation from the packet draft: the notes'
  packet-local-key prefix was replaced with the allocation statement ("Allocated
  PROG-000343 at integration (packet-local key NEW-PENN-CBE)."); every other cell is
  the packet's verbatim.

### People — dispositions as built (unit: 16 carried people at ORG-002176 with empty
program_org_id on origin/main; filter: links.csv)

LINK 9 (program_org_id set) · BANKED 7 primary dispositions + 3 packet-recorded
secondary banks · NO_WITNESS 0. Banked-only records are byte-untouched apart from
PERSON-001384 (title refresh, below). Evidence: one scope row per disposition plus
one per secondary bank; tier_effect = supports_A throughout (every subject record
is tier A).

| person | name | program_org_id as built | evidence |
|---|---|---|---|
| PERSON-000396 | Karen I. Winey | PROG-000110 (+ bank to PROG-000343) | EVD-333913, EVD-333914 |
| PERSON-000397 | Chinedum O. Osuji | PROG-000343 (+ bank to PROG-000110) | EVD-333915, EVD-333916 |
| PERSON-000398 | Robert A. Riggleman | PROG-000343 | EVD-333917 |
| PERSON-000399 | Virgil Percec | (blank; banked PROG-000110) | EVD-333918 |
| PERSON-000400 | Russell J. Composto | PROG-000110 | EVD-333919 |
| PERSON-000401 | Shu Yang | PROG-000110 (+ bank to PROG-000343) | EVD-333920, EVD-333921 |
| PERSON-000402 | Paul A. Janmey | (blank; banked PROG-000110) | EVD-333922 |
| PERSON-000403 | Jeffery G. Saven | (blank; banked PROG-000110) | EVD-333923 |
| PERSON-000404 | Kathleen J. Stebe | PROG-000343 | EVD-333924 |
| PERSON-000405 | Zahra Fakhraai | (blank; banked PROG-000110) | EVD-333925 |
| PERSON-000406 | Daeyeon Lee | PROG-000343 | EVD-333926 |
| PERSON-000407 | Amish J. Patel | PROG-000343 | EVD-333927 |
| PERSON-000408 | Daniel A. Hammer | (blank; banked PROG-000343) | EVD-333928 |
| PERSON-000409 | Christopher M. Madl | PROG-000110 | EVD-333929 |
| PERSON-000410 | Paulo E. Arratia | (blank; banked PROG-000343) | EVD-333930 |
| PERSON-001384 | Kyle H. Vining | (blank; banked PROG-000110) | EVD-333931, EVD-333932 (title) |

### Census mints (unit: 9 candidates in census.csv; filter: Gate A + Gate B on Penn's
own pages, no Atlas record tree-wide)

All 9 minted, PERSON-002144..002152 in packet order, each with existence + scope
evidence. Wenhao Gao stays excluded (incoming January 2027). No §4.21 identifiers
minted. Discher (PERSON-002149) minted at tier B: his Gate A styling rests partly on
a dated 2006 Penn Today article (packet weakest link #4); his current presence is
established by the department's current Labs + Facilities page. All other mints
tier A. Mallouk, Carpick, and Turner minted unlinked with banked PROG-000110
affiliations (Chemistry / MEAM primaries; no department rows exist for those units —
Chemistry STILL_UNCERTAIN, MEAM REJECT this lane).

| person | name | program_org_id as built | tier | evidence |
|---|---|---|---|---|
| PERSON-002144 | I-Wei Chen | PROG-000110 | A | EVD-333933, EVD-333934 |
| PERSON-002145 | Vivek B. Shenoy | PROG-000110 | A | EVD-333935, EVD-333936 |
| PERSON-002146 | Eric Detsi | PROG-000110 | A | EVD-333937, EVD-333938 |
| PERSON-002147 | Yuanwen Jiang | PROG-000110 | A | EVD-333939, EVD-333940 |
| PERSON-002148 | John C. Crocker | PROG-000343 | A | EVD-333941, EVD-333942 |
| PERSON-002149 | Dennis E. Discher | PROG-000343 | B | EVD-333943, EVD-333944 |
| PERSON-002150 | Thomas E. Mallouk | (blank; banked PROG-000110) | A | EVD-333945, EVD-333946 |
| PERSON-002151 | Robert W. Carpick | (blank; banked PROG-000110) | A | EVD-333947, EVD-333948 |
| PERSON-002152 | Kevin T. Turner | (blank; banked PROG-000110) | A | EVD-333949, EVD-333950 |

### P1 title refresh (owner-approved rider)

- **Applied: PERSON-001384 (Vining)** — role_as_published "Assistant Professor" →
  "Assistant Professor in Preventive and Restorative Sciences (PDM) and Materials
  Science and Engineering (MSE)", verbatim from his Penn Engineering directory page
  as quoted in links.csv; evidence EVD-333932. last_verified → 2026-11-12.
- **Flagged, NOT applied: PERSON-000397 (Osuji)** — the packet note records an MSE
  faculty-page styling "Eduardo D. Glandt Presidential Professor / Department Chair
  of Chemical and Biomolecular Engineering" (corroborated live at build). The record
  carries "Professor and Department Chair of Chemical and Biomolecular Engineering",
  which the styling does not contradict; the packet presents the fuller form as a
  note paraphrase rather than a verbatim title string, so under the rider's
  verbatim-only standard it is flagged here for a future P1 pass, not edited.
- All other Penn stylings in the packet match the records (Winey, Composto, Stebe,
  Lee, Hammer, Madl) or are not documented as differing verbatim titles.

### Ecosystem rollup (ORG-002176, §4.11 V-16, recomputed)

- polymer_program_name: "Materials Science and Engineering; Polymers and Soft Matter
  Science and Engineering concentration" → "Chemical and Biomolecular Engineering;
  Materials Science and Engineering; Polymers and Soft Matter Science and
  Engineering concentration" (degree rows by name, then the course row).
- polymer_program_url: the MSE department page → the CBE concentrations page (the
  first sorted program row, PROG-000343). last_verified → 2026-11-12. No other
  ecosystem cell or row moved.

### IDs and gates

Allocations: PROG-000343 (next free PROG-000344); PERSON-002144..002152 (next free
PERSON-002153); EVD-333906..EVD-333950 — 45 evidence rows (7 programs + 38 people;
next free EVD-333951). Evidence files are pure appends over the backups; the
row-level diff vs backups is exactly the change set above. validate.py: "OK —
validation passed." (1,486 people; 210 programs; 408 ecosystem; 41,013 evidence;
standing warning classes only). check_row_loss.py --base origin/main: "row-loss
guard: OK — no keyed row removed from data/ since origin/main (merge-base
848175b981)".
