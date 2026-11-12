# Wave 4 school pass — North Dakota State University (ORG-002841)

Packet-only research lane, 2026-11-12. Base state re-derived from origin/main
`79b1f42b` (PR #299 head). No repo data written; this packet is the authority
for the integrator's build. All witnesses are the institution's own pages
(ndsu.edu, catalog.ndsu.edu) or the center's own site (cb2center.org).
**Paid calls: zero** (direct fetch + web search only).

## Verdicts per target

| Target | Verdict | Result |
|---|---|---|
| PROG-000064 Coatings and Polymeric Materials (degree) | VERIFIED, depth fillable 3/5 | 5 fill rows in fills.csv: research_areas (two grounded rows), specialty_materials, facilities_note. specialty_processes and scale_band honestly unfilled (see below). |
| PROG-000047 Center for Bioplastics and Biocomposites (CB2) (center) | VERIFIED, depth fillable 3/5 + currency VERIFIED active | 3 fill rows in fills.csv: research_areas, specialty_processes, specialty_materials. facilities_note and scale_band honestly unfilled. |
| 15 unlinked people (PERSON-000424..000438) | 6 LINK / 7 BANKED / 2 NO_WITNESS | One row per person in links.csv. |
| Mechanical Engineering department row (prong b) | STILL_UNCERTAIN | No row drafted — see proposed_rows.csv. |
| Physics department row (prong b) | STILL_UNCERTAIN | No row drafted — see proposed_rows.csv. |
| Census (unrecorded CPM/CB2 faculty) | none proposed | census.csv itemizes the evaluated near-misses. |

Counts state unit + filter: fills = proposed cell fills for the 2 carried
program rows at ORG-002841 that stand at depth 0/5 on current main; links =
dispositions over the 15 people at ORG-002841 with empty program_org_id on
current main.

## Depth fills — what was proposed and what was refused

**PROG-000064 (CPM)** goes 0/5 → 3/5:
- `research_areas` = `polymer_synthesis;rheology;characterization_methods`
  from the Graduate School program page's own research statement ("specialized
  training in areas such as colloidal and interfacial chemistry, polymer
  synthesis, adhesion, spectroscopy, rheology, nanomaterials design and
  synthesis, and surface chemistry"), plus `biomedical_polymers` from the
  department's own SURE research-areas list ("Polymers/Polymeric Materials
  for Biomedical Applications"). Mapping notes: "spectroscopy" →
  `characterization_methods` per the §3.5 definition (expert application of
  analytical methods for polymer structure/properties). Colloidal/interfacial
  chemistry, adhesion, nanomaterials design, and surface chemistry have no
  honest §3/§3.5 term and were left unmapped rather than forced.
- `specialty_materials` = `coatings` (the program's own homepage: "expertise
  in the realms of paints, coatings, and polymers").
- `facilities_note` from the program page's facilities statement (nearly
  40,000 sq ft, Research and Technology Park; spectrometers, thermal
  analysis, electrochemical corrosion equipment, AFM, paint making/testing).
  Integrator may also append the Bioactive Materials Research Laboratory —
  CPM's own page (ndsu.edu/bioactive-materials-lab) states the BMRL "occupies
  1,000 square feet of space in the Research and Technology Park at NDSU
  under the auspices of the Coatings and Polymeric Materials Department"
  with BSL-2 capability and high-throughput screening of coatings — but it is
  not in fills.csv, so the built note stays exactly the fills.csv value
  unless the integrator rules otherwise.
- `specialty_processes`: NO FILL. CPM's program-level pages state research
  areas and instrumentation, never a named §3.1 process. `coating_formulation`
  appears only at person grain (Qi's profile: "coating design and
  formulation") and §4.11 bars carrying a person-level statement up to the
  program row.
- `scale_band`: NO FILL. No program enrollment or qualitative program-size
  self-characterization is published on CPM's pages; §4.6 S3 conversions do
  not run on anything else.

**PROG-000047 (CB2)** goes 0/5 → 3/5, all from the center's own research
page (cb2center.org/research, five thrust areas):
- `research_areas` = `polymer_synthesis;sustainable_feedstocks` (Synthesis
  and Compounding thrust: "bioplastic synthesis and compounding, including
  fermentation and polymerization … polymer additives and feedstock
  production"). `degradation_biodegradation` was considered for the Biobased
  Products thrust's "composting" and refused — the thrust frames composting
  as a commercialization topic, not a breakdown-science statement.
- `specialty_processes` = `polymerization;compounding_unspecified;
  extrusion_unspecified;injection_molding;molding_unspecified` — subtypes
  carried only where the center names them ("injection molding" in the
  Modeling thrust); generic "extrusion" / "molding" / "compounding" take the
  `_unspecified` terms per §3.1, never upgraded.
- `specialty_materials` = `bioplastics_biobased;composites_unspecified;
  elastomers_rubber` (Biocomposites thrust names biobased resin/fiber
  systems without a composite class, hence `composites_unspecified`).
- `facilities_note` / `scale_band`: NO FILL — the center's own pages state
  neither facilities nor a convertible size figure (industry-partner counts
  never convert under S3).

## CB2 currency check — VERIFIED active (center's own site only)

The Atlas row records CB2 as an NSF I/UCRC Phase II center (award 2113804)
with status active. Checked against cb2center.org alone, fetched 2026-11-12:

- Homepage (cb2center.org/home): "Save the Date — The 2026 IAB Fall Meeting
  will be hosted by Iowa State University in Ames, IA … October 28-29,
  2026."
- Call for proposals (cb2center.org/research/call-for-proposals): "The
  Center for Bioplastics and Biocomposites (CB2) has announced a call for
  proposals for research projects to begin in 2027. Proposal topics from
  Industry Advisory Board will be released to faculty on July 6, 2026.
  Proposal applications due August 9, 2026."

Verdict: **the center is operating now** — an IAB, a dated future meeting,
and a live funding call for 2027 projects, all on its own site. This
confirms the carried `status=active`. Posture update vs the earlier lane:
the center's current own pages do not restate an NSF phase label in the
pages fetched; the Phase II framing on the record stands as historical
fact (NDSU's own news page documents award 2113804), and nothing on the
center's site contradicts continued post-award industry-consortium
operation — the same posture the Lane A build landed for WBC and CDP. No
status or description change is proposed by this packet. Grain note: the
row stays anchored at NDSU per the decided IUCRC rule; NDSU's own news
page styles NDSU the lead site ("co-located at North Dakota State
University (NDSU) (lead), Iowa State University (ISU), Washington State
University (WSU), and the University of Georgia (UGA)"), with Webster as
NDSU site director — consistent with the carried row.

## Links — reasoning highlights (full rows in links.csv)

- **LINK → PROG-000064 (6):** the six current CPM core faculty — Webster,
  Caldona, Voronov, Rasulev, Hevus, Qi. Each is styled with a CPM faculty
  rank on CPM's own faculty page (current) and carries a polymer-research
  witness on an institutional page. Webster, Caldona, Rasulev and Qi also
  sit on CB2's roster; that is noted in their rows for the integrator, but
  their program home is CPM.
- **BANKED → PROG-000047 (5):** Ulven, Wu, Jiang, Amiri, Vold — Mechanical
  Engineering faculty on CB2's own NDSU roster with polymer/composites
  research stated on the roster and/or ME's own people page. Their primary
  home (ME) has no program row, so program_org_id stays unchanged.
- **BANKED → PROG-000064 (2):** Hobbie (CPM's own faculty page lists the
  Physics professor as CPM faculty) and Quadir (see restyle flag below).
- **NO_WITNESS (2):**
  - Croll (Physics) — Gate B is strong ("Experimental Studies of Polymers,
    Diblock Copolymers, Thin Films…" on Physics' own page) but no CPM/CB2
    affiliation is witnessed anywhere on the institution's pages, and
    Physics has no row. Affiliation gap only.
  - Narayanan (IME) — CB2's roster lists him by name/contact with no
    research statement, and no NDSU page found states his research; his
    polymer-AM publications are not an institutional witness.

## Flags for the integrator (P1 title-refresh rider)

1. **PERSON-000433 Quadir — restyled.** CPM's current faculty page: "Adjunct
   Professor — Coatings and Polymeric Materials". His Atlas role text reads
   "Associate Professor, Coatings and Polymeric Materials". The page states
   the new title verbatim; apply the refresh in the same PR if the banked
   row is minted. This is also why he is BANKED, not LINKED.
2. **PERSON-000432 Narayanan — promoted.** Current catalog Graduate Faculty
   listing: "Narayanan, Lokesh Karthik — Associate Professor, Industrial
   and Manufacturing Eng". His Atlas role text reads Assistant Professor.
   (He is NO_WITNESS for linking in this pass; the title fact is recorded
   here so it is not lost.)

## Gate A call the brief asked for — Amiri

Ali Amiri (PERSON-000437) styles as "Associate Professor of Practice" in
ME's own directory, which lists him under "Directory - Faculty" with
polymer-nanocomposite research interests. A professor-of-practice rank is
a professorial faculty styling — not a staff-scientist or
research-associate styling — and his Atlas record already stands.
**Call: Gate A satisfied** for the banked CB2 affiliation.

## Weakest links (named, per protocol)

1. **Hevus's Gate B** (PERSON-000431): his NDSU profile page carries no
   research statement; the polymer witness is his 2012 CPM dissertation
   abstract on NDSU's own repository plus his CPM publication record.
   Gate A is current and unambiguous, and CPM is plainly his program home,
   so he is LINKED — but this is the thinnest person witness in the unit.
2. **Quadir's disposition** turns on a styling change (Associate →
   Adjunct Professor) read from CPM's current faculty page; if the
   integrator reads adjunct affiliation as still linkable, the packet's
   evidence supports either build — the packet recommends BANKED.
3. **CB2 specialty_processes** rest on thrust-area statements ("will focus
   on…") from the center's own research page — program-grain and honest,
   but prospective in tense.
4. **CPM `characterization_methods`** is a mapping step (spectroscopy →
   the §3.5 analytical-methods term), flagged here rather than hidden.

## Fetch log (summary)

19 fetches/searches, all zero-paid: CPM homepage, CPM faculty page, CPM
SURE research-areas page, Graduate School CPM program page, current
catalog doctorate page, catalog CPM program/facilities text (2024-25) and
faculty text (2021-22), current catalog Graduate Faculty listing, Physics
faculty-interests page, ME people page, WRRI affiliate-faculty page,
NDSU people pages (Hevus, Voronov; Caldona via search extract), Hevus
dissertation record (NDSU Digital Commons), CB2 homepage, CB2 research
page, CB2 call-for-proposals page, CB2 NDSU faculty-and-staff roster.
No fetch failed outright; the CPM homepage's extracted text was thin, and
its substance was recovered from the Graduate School and catalog pages —
an availability note, not an absence finding.

## INTEGRATION RECORD (integrator of record: spaghetti, 2026-11-12)

Built in worktree `~/workspace/atlas-w4-ndsu-build-2026-11-12`, branch
`agent/spaghetti/wave4-ndsu-2026-11-12`, base origin/main `3cade2c9` (PR #303 head).
Local only at build time — no push, no PR. Build report:
staging `working/wave4-2026-11-12/ndsu/integration-build-report.md`. Pre-pass backups:
`~/workspace/atlas-w4-ndsu-backups-2026-11-12/`. Paid calls: zero.
Allocation: evidence opened at the **EVD-333980** floor (the CMU unit is sequenced
before this one and allocated first; this base's tree maximum is EVD-333950) and the
PERSON-002155 people floor went unused (no mints). The packet governed every cell;
no integrator brief deviation arose.

### Program rows (unit: the 2 carried active program rows at ORG-002841; filter: the packet's depth-0 targets)

- **PROG-000064 (Coatings and Polymeric Materials, degree): fills applied exactly per
  fills.csv** — research_areas `polymer_synthesis;rheology;characterization_methods;
  biomedical_polymers` (two grounded fills.csv rows joined in packet order),
  specialty_materials `coatings`, facilities_note as drafted (0/5 → 3/5).
  specialty_processes and scale_band stay blank — the packet's refusals landed as
  refusals (no program-level §3.1 process on CPM's own pages; no convertible size
  figure under S3). Depth evidence EVD-333980..333983, supports_B per the record's
  own tier B (§4.13). last_verified → 2026-11-12. No other cell moved.
- **PROG-000047 (Center for Bioplastics and Biocomposites (CB2), center): fills
  applied exactly per fills.csv** — research_areas
  `polymer_synthesis;sustainable_feedstocks`, specialty_processes
  `polymerization;compounding_unspecified;extrusion_unspecified;injection_molding;
  molding_unspecified`, specialty_materials
  `bioplastics_biobased;composites_unspecified;elastomers_rubber` (0/5 → 3/5).
  facilities_note and scale_band stay blank per the packet's refusals, and
  `degradation_biodegradation` was NOT carried for the Biobased Products thrust
  (composting framed as a commercialization topic, not a breakdown-science
  statement). Depth evidence EVD-333984..333986, supports_A per the record's own
  tier A. **Currency: the lane VERIFIED CB2 active on the center's own site
  (2026 IAB Fall Meeting announced; live call for 2027 projects) — the carried
  status=active stands; the packet proposes no status or description wording and
  none was made.** last_verified → 2026-11-12. No other cell moved.
- **No program rows created.** The packet's two prong-(b) verdicts stand as
  STILL_UNCERTAIN with their settling facts recorded in proposed_rows.csv:
  Mechanical Engineering (person-grain polymer statements are prong-(c)
  corroboration only) and Physics (faculty-interests directory does not tie
  polymers to its degrees).

### People (unit: the 15 people at ORG-002841 with empty program_org_id on the base; filter: links.csv dispositions)

- **6 LINKs → PROG-000064** (program_org_id set, last_verified → 2026-11-12):
  Webster PERSON-000424 (EVD-333987), Caldona PERSON-000425 (EVD-333988),
  Voronov PERSON-000426 (EVD-333989), Rasulev PERSON-000427 (EVD-333990),
  Hevus PERSON-000431 (EVD-333993), Qi PERSON-000434 (EVD-333995). All
  supports_A (each record's own tier is A).
- **Hevus Gate B disclosure, carried verbatim:** the packet names his the unit's
  weakest link witness — his NDSU profile carries no research statement, so the
  polymer witness is his 2012 CPM dissertation abstract on NDSU's own repository
  plus his CPM publication record (Gate A current and unambiguous; CPM plainly
  his program home). The disclosure stands verbatim in EVD-333993's notes,
  carried from links.csv untruncated.
- **7 BANKED affiliations** (evidence only; program_org_id unchanged):
  Ulven PERSON-000428 → PROG-000047 (EVD-333991), Wu PERSON-000429 → PROG-000047
  (EVD-333992), Quadir PERSON-000433 → PROG-000064 (EVD-333994),
  Hobbie PERSON-000435 → PROG-000064 (EVD-333996), Jiang PERSON-000436 →
  PROG-000047 (EVD-333997), Amiri PERSON-000437 → PROG-000047 (EVD-333998; Gate A
  call per the packet: professor-of-practice is a professorial faculty styling),
  Vold PERSON-000438 → PROG-000047 (EVD-333999).
- **2 NO_WITNESS records byte-untouched:** Croll PERSON-000430 (Gate B strong,
  no witnessed CPM/CB2 affiliation) and Narayanan PERSON-000432 (no institutional
  research witness). Verified byte-identical against the pre-pass backups.
- **Census: none minted** — census.csv's none-proposed stands (Kallmeyer fails
  Gate B; Sibi unwitnessed on the center's pages; CPM adjuncts as a class fail
  Gate A for new records).
- **Not taken:** links.csv notes Webster (and the README notes Caldona, Rasulev,
  Qi) also sit on CB2's roster. No banked CB2 rows were minted for the four
  CPM-linked faculty in this unit — the packet's dispositions govern (their
  program home is CPM), and the integrator brief enumerates exactly the 7 banked
  rows above. Flagged here so a later pass can bank them if wanted.

### P1 title-refresh flags (owner-approved rider, 2026-11-12)

- **Quadir PERSON-000433 — APPLIED.** links.csv directs the refresh verbatim and
  his banked row is minted in this pass: role_as_published "Associate Professor,
  Coatings and Polymeric Materials" → "Adjunct Professor, Coatings and Polymeric
  Materials" (CPM's current faculty page styling, EVD-334000, claim_type
  existence, supports_A); the controlled `role` value moves associate_professor
  → professor per the standing adjunct convention (the §4.9 enum carries no
  adjunct value; cf. PERSON-000387 and PERSON-000457, both styled "Adjunct
  Professor" at role=professor); the CPM faculty-page URL was appended to his
  `sources` (it was not among them); last_verified → 2026-11-12.
- **Narayanan PERSON-000432 — RECORDED, NOT APPLIED.** The packet records his
  promotion (current catalog Graduate Faculty listing: "Associate Professor,
  Industrial and Manufacturing Eng") so the fact is not lost, but it supplies no
  citable URL for that listing and no restyle directive, and it dispositions him
  NO_WITNESS — so his record stands byte-untouched in this unit, per the rider's
  verbatim-page rule. Settling fact for a later pass: the current catalog
  Graduate Faculty listing read at a citable URL.

### Ecosystem rollup — ORG-002841

No program-set change (no rows created), so the V-16 rollup was recomputed and
verified to reproduce the carried values exactly — `polymer_program_name`
"Coatings and Polymeric Materials; Center for Bioplastics and Biocomposites
(CB2)", `polymer_program_url` = PROG-000064's URL. **The ecosystem row is
untouched (ecosystem.csv byte-identical to the pre-pass backup).**

### Evidence minted (21 rows)

Programs EVD-333980..EVD-333986 (7 scope rows, one per fills.csv row; supports_B
×4 for PROG-000064, supports_A ×3 for PROG-000047); people EVD-333987..EVD-334000
(14 rows: 6 LINK scope + 7 BANKED scope + 1 P1 existence, all supports_A).
Contiguous, each ID exactly once. **Next free: EVD-334001** (people floor
PERSON-002155 unused; next free people on the built tree remains PERSON-002153).

### QUEUE

This unit's claim added directly after the wave-4 Penn claim. Prior claims stand
exactly as they are on this base: the Penn claim still reads `claimed` here
(PR #303 merged with its own claim standing; its flip belongs to the CMU unit,
which is sequenced before this one), and no CMU claim exists on this base — both
left untouched per the build brief.

### Gates

`scripts/validate.py`: "OK — validation passed." (totals on the built tree:
5,024 organizations, 408 ecosystem rows, 1,486 people, 210 program rows, 41,034
evidence rows; warnings only the standing classes, none naming this unit's
records). `scripts/check_row_loss.py --base origin/main`: "row-loss guard: OK —
no keyed row removed from data/ since origin/main (merge-base 3cade2c9c3)".
Row-level diff vs the pre-pass backups: programs 2 rows changed (fill cells +
last_verified only), people 7 rows changed (6 LINKs' program_org_id +
last_verified; Quadir's role / role_as_published / sources / last_verified),
evidence +21 pure appends, ecosystem byte-identical. No REMOVALS.csv.
