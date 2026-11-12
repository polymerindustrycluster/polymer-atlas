# Federal Round-2 Verification — Lane A: NSF I/UCRC + Manufacturing USA

Packet-only verification lane. **No canonical data was edited.** Owner-approved
2026-11-12; grain rules applied as decided: I/UCRC rows anchor at the LEAD
institution with partner sites recorded as affiliations; Manufacturing USA
institutes are their own institution of record (institute-as-institution,
BioPACIFIC MIP precedent, PROG-000071). Input packet:
`working/wave3-2026-11-12/federal-round2-iucrc-musa.md`. Atlas state read from
`~/workspace/atlas-p2-2026-11-12/data/` (main snapshot). All verification on the
candidates' **own pages** (center/institute sites and lead-institution pages);
NSF award records were never used as verification. Verification date:
**2026-11-12**. Paid calls: **0** (all sources via free browser search/fetch).

## Counts (unit + filter)

Unit: one candidate from the round-2 lane A packet. Filter: the 14 candidates
the packet screened in as MISSING or institution-only (5 I/UCRC missing;
4 Manufacturing USA carried ecosystem orgs with no program row;
5 Manufacturing USA missing entirely).

- **VERIFIED: 12** (5 I/UCRC + 4 carried-org program rows + 3 new institutes)
- **STILL_UNCERTAIN: 2** (RAPID, LIFT)
- **REJECT: 0**
- Rows drafted in `proposed_rows.csv`: **12 program rows**.
- Rows drafted in `proposed_institutions.csv`: **4 ecosystem institution rows**
  (AFFOA, NextFlex, FutureTEX — new institutes of record; University of Denver —
  anchor institution for the concluded HVT row, no Atlas record exists).

## Verdict table — NSF I/UCRC (5)

### 1. SHAP3D — VERIFIED · status: ACTIVE · anchor UMass Lowell (ORG-002846)
Center's own page at the lead institution: "SHAP3D is a collaboration between
the University of Massachusetts Lowell (UML), Arizona State University (ASU)
and Georgia Institute of Technology to create a National Science Foundation
Industry-University Cooperative Research Center (Industry-University Research
Partnerships (I/UCRC)) focused on 3D printing… developing new 3D printing
methods for novel materials and composites" — and a current Fall Industrial
Advisory Board meeting, October 20–21, 2026 (Georgia Tech).
- https://www.uml.edu/research/shap3d/
- Affiliations: Arizona State University (ORG-004661), Georgia Institute of
  Technology (ORG-002844); University of Connecticut (ORG-004664) is a founding
  site per its own Tech Park page ("Co-founded by UConn, UMass Lowell and
  Georgia Tech", est. July 2018) — https://techpark.uconn.edu/institutes-centers_old/
- Polymer basis: multi-material polymer additive printing; center research
  described as "with a focus on polymer based materials" (center authors,
  TechConnect 2019). Tier **A**.

### 2. Wood-Based Composites Center (WBC) — VERIFIED · status finding: ACTIVE AS INDUSTRY CENTER (NSF award concluded) · anchor Virginia Tech (ORG-002845)
Center's own About page: "The Wood-Based Composites Center (WBC) is
Cooperative Research Center driven by an industry-scientific community that
develops research related to composites and renewable materials… Advance the
science and technology of wood-based composite materials." On status, the same
page: "The Phase II Award supported the WBC as an NSF center through 2022" —
and the center demonstrably continues: present-tense mission/objectives,
IAB Fall Meeting 2022 (Blacksburg), site imagery dated 2023, and a leadership
transition in 2022 ("Dr. Arijit Sinha from OSU assumed the role of director of
the WBC"). **Finding: the NSF I/UCRC award period ended in 2022; the
consortium continues operating on industry funding — row drafted `active`,
with the post-award basis stated in the row notes.**
- https://www.wbc.center/center/about/
- Affiliations (per the center's own history): Oregon State University
  (ORG-004773, current director's site), Michigan State University, University
  of Minnesota, University of Maine, University of British Columbia;
  Mississippi State University as affiliate. Tier **A**.

### 3. Center for Dielectrics and Piezoelectrics (CDP) — VERIFIED (marginal, as screened) · status finding: ACTIVE AS INDUSTRY CENTER (former I/UCRC) · anchor NC State (ORG-002851)
Center's own homepage header styles it "The Center for Dielectrics and
Piezoelectrics – a National Science Foundation Industry University
Collaborative Research Center – **a former NSF Industry/University
Collaborative Research Center (I/UCRC)**", and the same homepage announces
"The CDP Fall Meeting will be held on November 11-13, 2026" — i.e., operating
now. The Phase II period (03/01/19–2/28/25) has ended; CDP Core Projects run
through 2026-06-30 (NC State MSE pages). **Finding: former I/UCRC continuing
as an industry consortium — row drafted `active` with the basis in notes.**
Polymer slice, from the center's own research page: Research Thrust Areas
include "**Polymer Nanocomposite Dielectrics**" and "Dielectrics for low-T
and flexible substrates"; funded projects include "Dielectric Response of
Polymers at High Electric Field".
- https://cdp.ncsu.edu/ · https://cdp.ncsu.edu/research-2/
- Affiliations: Pennsylvania State University (ORG-002775, co-lead site);
  University of Sheffield (international affiliate). Tier **A**. Marginal
  flag retained: the polymer line is one thrust among several in a
  ceramics-led center — the row's coded specialty fields are deliberately
  left empty and the polymer basis is carried in the description/notes.

### 4. HVT Center — VERIFIED · status finding: CONCLUDED (Phase I ended 2024-09-30; no Phase II established) · anchor University of Denver (NEW institution row drafted, ORG-NEW-A04)
The center's own domain is lapsed: hvtcenter.org resolves to a GoDaddy
for-sale page (fetched 2026-11-12). The center director's own record
(University of Denver–hosted CV, updated through January 2026): "The first
Phase of the center was completed on September 30, 2024, after five no-cost
extensions… it is presently ready to move to Phase II in a new structure and
location" — a proposal posture, not an operating center; the director
retired from DU in July 2024. No current meetings, members, or activity were
found on any site. **Finding: concluded — row drafted with `status=closed`
and the 2024-09-30 completion date recorded in notes (programs.csv carries
no status_date column).** Polymer basis (historical, from the NSF center
page and the director's DU-hosted record): "HV HTLS Polymer Core Composite
Conductors", "In-Situ Sensing of Manufacturing and Aging of HVT Polymer
Matrix Composites", silicone-rubber aging for HV applications, nanodielectrics.
- https://iucrc.nsf.gov/centers/novel-high-voltage-temperature-materials-and-structures/
- https://ritchieschool.du.edu/sites/default/files/2021-04/MKumosa Major Accomplishments February 2021.pdf
- Affiliations: Michigan Technological University (ORG-004668), University of
  Illinois Urbana-Champaign (ORG-004657), University of Connecticut
  (ORG-004664). Tier **B**. Integrator note: if the owner prefers not to mint
  rows for centers that concluded before ever being recorded, this is the
  one row to drop; the University of Denver institution draft exists only to
  anchor it.

### 5. WindSTAR — VERIFIED · status: ACTIVE · anchor UMass Lowell (ORG-002846)
Center's own About page at the lead institution: "WindSTAR is an NSF-funded
Industry/University Cooperative Research Center for Wind Energy, Science,
Technology and Research. A collaboration between UMass Lowell and the
University of Texas at Dallas (UTD)…" Research areas listed first:
"**Composites and Blade Manufacturing**". Current project list (2025) includes
"Recycling Epoxy Composites through Vitrimerization – Phase II" and
"Integration of Machine-Learning Based Approach for Curing Cycle Process
Optimization of Vacuum Assisted Resin Infusion Process (VARIM)"; member
companies listed for 2026–2027.
- https://www.Uml.edu/research/windstar/about/ · https://www.uml.edu/Research/WindSTAR/research/
- Affiliation: The University of Texas at Dallas (ORG-004698). Tier **A**.

## Verdict table — Manufacturing USA, program rows on carried orgs (4)

### 6. IACMI — The Composites Institute (ORG-002099) — VERIFIED · ACTIVE
Institute's own About page: "IACMI is one of 17 Manufacturing USA institutes…
our industry needs composites manufacturing that is more cost-, material- and
energy-efficient." Lead institution's own page (UT Knoxville) states the
scope verbatim: "accelerating development and adoption of innovative
manufacturing technologies for **low-cost, energy-efficient manufacturing of
advanced polymer composites for vehicles, wind turbines, compressed gas
storage**, aerospace, and industrial applications", and "the University of
Tennessee, Knoxville, would be the lead institution" with Oak Ridge National
Laboratory a founding partner.
- https://www.iacmi.org/about-us/ · https://tickle.utk.edu/mae/news/iacmi-what-it-means-for-ut-ornl-and-east-tennessee/
- Tier **B** (own About page read via an older crawl; lead-institution quote
  current). Program row keys to ORG-002099 (institute as its own institution
  of record); HQ Knoxville, TN.

### 7. REMADE Institute (ORG-002100) — VERIFIED · ACTIVE
Institute's own homepage (live, current — 2026 summit announced): "REMADE
Institute – Increasing the Reuse, Remanufacturing, Recycling and Recovery of
Energy-Intensive Materials"; featured R&D project "**Reinforced Recycled
Polymer Composites**". Anchor facts from its CEO's own abstract: "Founded in
2017 and **headquartered in Rochester, NY**, the REMADE Institute is the only
national institute dedicated to accelerating the transition to a Circular
Economy in the United States… established in partnership with the U.S.
Department of Energy"; DOE's own announcement language for the institute:
technologies to "reuse, recycle and remanufacture materials such as metals,
**fibers, polymers** and electronic waste". Led by Rochester Institute of
Technology (Golisano Institute for Sustainability).
- https://remadeinstitute.org
- Tier **A**. Locality note: HQ is stated as Rochester, NY on the institute's
  own materials; the RIT campus sits in Henrietta (Monroe County either way) —
  the row drafts Rochester/Monroe per the institute's own statement.

### 8. BioMADE (ORG-002097) — VERIFIED · ACTIVE
Institute's own About page: "BioMADE's mission is to enable domestic
bioindustrial manufacturing at all scales…" Its own bioindustrial-manufacturing
page states the polymer scope verbatim: "Bioindustrial manufacturing uses
biological systems to convert agricultural feedstocks and waste streams to
high-value chemicals, materials, textiles, fuels, **bioplastics**, and other
products", with consumer applications including "Biodegradable plastics and
compostable packaging materials" and "Plant-based nylon"; its own April 2026
project announcement names "plastics for 3D printing" and PHA bioplastic for
"films, fibers, and 3D printing".
- https://www.biomade.org/about · https://www.biomade.org/bioindustrial-manufacturing
- Tier **B**. HQ St. Paul, MN (already on the ecosystem record).

### 9. America Makes (ORG-001217) — VERIFIED · ACTIVE
Institute's own site: "America Makes is the nation's leading public-private
partnership for additive manufacturing (AM) technology and education…
**based in Youngstown, Ohio, and managed by the not-for-profit National
Center for Defense Manufacturing and Machining (NCDMM)**." Polymer scope on
its own pages: its February 2026 AACAMS project call defines the work as
"any process capable of depositing **an unbroken fiber and polymer matrix**
into a 3D part", and its project records carry a "DEVELOPMENT CATEGORY:
**Polymer**" classification.
- https://www.americamakes.us/america-makes-awards-udri-450k-for-aacams-project-call/
- Tier **B**.

## Verdict table — Manufacturing USA, missing institutes (5)

### 10. AFFOA (Advanced Functional Fabrics of America) — VERIFIED · ACTIVE · new institution row drafted (ORG-NEW-A01)
Institute's own homepage: "As a non-profit, public-private partnership and a
**Manufacturing USA Innovation Institute headquartered in Bedford, MA**, we
accelerate textile technology and manufacturing breakthroughs… We are
revolutionizing the textile industry by **transforming traditional fibers,
yarns and textiles into highly sophisticated, integrated, and networked
devices and systems**." **Correction to the round-2 packet: HQ is now
Bedford, MA** (own homepage: "AFFOA Celebrates Opening of New Headquarters
with Ribbon-Cutting Ceremony in Bedford, Massachusetts"), not Cambridge.
Bedford is in Middlesex County, MA.
- https://affoa.org/ — Tier **A**.

### 11. NextFlex — VERIFIED · ACTIVE · new institution row drafted (ORG-NEW-A02)
Institute's own homepage: "We're working to create a strong U.S. industrial
base for **hybrid electronics manufacturing**", through its manufacturing
consortium, Technology Hub, and workforce programs. Polymer-medium basis on
its own pages: its flexible-Arduino project page states "NextFlex replaced
the traditional circuit board with **a thin, flexible plastic sheet** and used
digital printing processes for circuit elements", and its own 2026 REARM call
materials span "Printed electronics, metals, ceramics, glass, and **polymer
manufacturing technologies**". Technology Hub location, from its own
materials: San Jose, California. Operated by FlexTech Alliance under a DoD
(AFRL) cooperative agreement.
- https://nextflex.us/ · https://www.nextflex.us/technology-hub/
- Tier **B**. Screened-in basis retained: the electronics mission is the
  headline; polymer films/substrates are the manufacturing medium — the row's
  notes say so.

### 12. FutureTEX — Textiles Futures Institute — VERIFIED · ACTIVE (in formation) · new institution row drafted (ORG-NEW-A03)
The institute's independent nonprofit is still being established (announced
August 2026), so verification rests on the lead institution's and the HQ
host's own pages — flagged here and in the row (tier **C**; re-verify when
the institute's own site launches). NC State Wilson College of Textiles (lead
institution): "FutureTEX is a 10-year Department of War initiative aimed at
modernizing textile manufacturing in the United States to support the defense
industry **currently led by NC State**. While **FutureTEX headquarters will
ultimately be located on Gaston College's Kimbrell Campus**, FutureTEX will
forever have a node in the Wilson College." Gaston College's own news page:
"Gaston's Kimbrell Campus will serve as the **headquarters of FutureTEX, a
new Manufacturing Innovation Institute focused on strengthening America's
fibers, textiles, and advanced materials manufacturing capabilities**."
$36M first year, $480M ceiling over 10 years; Gaston College's president is
the inaugural CEO. **Lead settled: NC State University; HQ settled: Gaston
College Kimbrell Campus, Belmont, NC (Gaston County)** — the packet's open
question is closed. Core partners: Gaston College, NC State (ORG-002851),
Drexel University, Georgia Tech (ORG-002844), UMass Lowell (ORG-002846),
ISAIC.
- https://www.gaston.edu/category/campus-news/ · https://engr.ncsu.edu/news/2026/09/15/flex-factory-ready-to-foster-entrepreneurship/
- Row `url` gap flagged for the integrator: no institute-owned site exists
  yet; the draft points at the HQ host's news page pending the institute's
  own site.

### 13. RAPID Institute — STILL_UNCERTAIN
What its own pages establish: AIChE's RAPID site states the institute "is
focused on addressing the modular chemical process intensification barriers
to enable the development of breakthrough technologies to boost energy
productivity and energy efficiency through manufacturing processes in
industries such oil and gas, pulp and paper and various domestic chemical
manufacturers", with focus areas Chemical & Commodity Processing, Natural
Gas Upgrading, Renewable Bioproducts, Modeling and Simulation, Intensified
Process Fundamentals, and Module Manufacturing. Polymer content on its own
pages is **project-level only** (e.g., an announced project to "develop a
furan-based polymer membrane for energy-efficient separation of hydrogen");
no own page states polymer production or polymer separations as an
institute scope line. **Settling fact: a RAPID own page (focus-area,
technology, or portfolio page) stating polymer processing — polymerization,
polymer separations, or polymer production — as a named scope area of the
institute, not a single project.**
- https://rapid.aiche.org/about · https://rapid.aiche.org/news/04-22-2020/rapid-manufacturing-institute-announces-new-project-selections
- (rapidinstitute.org itself failed to fetch — network error; availability,
  not absence. The institute's live own site is the AIChE-hosted one above.)

### 14. LIFT — STILL_UNCERTAIN
What its own pages establish: LIFT's own homepage describes "an accelerator
connecting advanced materials, manufacturing processes, systems engineering
and talent development", a Detroit High Bay "advanced materials facility",
and a new AMPP Center "redefining how the U.S. develops and produces
**advanced metals**"; its own published About language is "committed to the
development and deployment of **advanced lightweight metal manufacturing
technologies**". Its current flagship federal program is ceramics / ceramic
matrix composites (CMC — not polymer-matrix). Polymer-matrix composites
appear only via co-location with IACMI at the Corktown facility and a joint
LIFT–IACMI education hub — not as a LIFT portfolio line on its own pages.
**Settling fact: a LIFT own page (active-programs or technology page)
stating polymer-matrix composites as a program area in LIFT's own
portfolio.**
- https://lift.technology/

## Drafting conventions (for the integrator)

- `program_id` / new `org_id` values are placeholders (`PROG-NEW-A##`,
  `ORG-NEW-A##`) — allocate above tree-wide maxima at integration, per
  AGENTS.md §3 (this snapshot's maxima: PROG-000304, ORG-013001).
- Program rows follow SCHEMA §4.11: `program_type=center`, `level=none`,
  `engagement_modes` employer-facing (`research_collaboration` minimum),
  `geography_served=national`, `pic_relevance=research_partner`,
  `last_verified=2026-11-12`. Coded specialty/research fields are filled
  only where the candidate's own pages state the term (§3-first rule);
  several are deliberately empty — see each row's notes.
- Ecosystem `polymer_program_name` rollups (§4.11) are generated at
  integration; the drafted institution rows for AFFOA/NextFlex/FutureTEX
  carry `polymer_program=true` with the program name pre-stated, and the
  integrator regenerates the rollup when the program rows land. The four
  carried MUSA orgs and the anchor universities need their rollups
  regenerated in the same pass — not drafted here.
- Evidence rows (existence + scope per §4.13) are the integrator's to mint;
  the quoted witnesses above are the scope/existence basis for each row.
- Status discipline: WBC and CDP are drafted `active` on the strength of
  their own current pages (meetings/activity in 2026), with the concluded
  NSF award periods stated in their notes — not silently assumed. HVT is
  drafted `closed` (see verdict 4).

---

## Integration record — federal round-2 lane A (integrator: spaghetti, 2026-11-12)

Applied from this packet to canonical data on branch
`agent/spaghetti/federal-round2-lane-a-2026-11-12`, base origin/main
`1f4a26c2f0` (PRs #284–#298). Build script:
`~/workspace/atlas-resync-2026-11-10/build_lanea_fedround2.py`;
pre-pass backups in `~/workspace/atlas-lanea-backups-2026-11-12/`
(programs.csv, ecosystem.csv, evidence_programs.csv,
evidence_ecosystem.csv, QUEUE.md). Packet cells landed verbatim;
only the lane placeholders were replaced by allocated IDs.

- **Program rows created (11)** — allocation opened at PROG-000321
  (tree scan max PROG-000320), in proposed_rows.csv order among the
  created rows: PROG-000321 SHAP3D (ORG-002846 UMass Lowell, tier A);
  PROG-000322 Wood-Based Composites Center (ORG-002845 Virginia Tech,
  tier A, `active` as a post-award industry consortium per the
  packet's status finding); PROG-000323 CDP (ORG-002851 NC State,
  tier A, `active` as a former-I/UCRC industry consortium);
  PROG-000324 WindSTAR (ORG-002846, tier A); PROG-000325 IACMI
  (ORG-002099, tier B); PROG-000326 REMADE Institute (ORG-002100,
  tier A); PROG-000327 BioMADE (ORG-002097, tier B); PROG-000328
  America Makes (ORG-001217, tier B); PROG-000329 AFFOA
  (ORG-013503, tier A); PROG-000330 NextFlex (ORG-013504, tier B);
  PROG-000331 FutureTEX (ORG-013505, tier C). I/UCRC partner
  affiliations are recorded in the program rows' notes exactly as
  the packet drafts them; no partner institution rows were created.
  **Next free: PROG-000332.**
- **Ecosystem institution rows created (3)** — allocation opened at
  ORG-013503 (tree-wide scan max ORG-013502 across ecosystem +
  organization shards): ORG-013503 AFFOA, ORG-013504 NextFlex,
  ORG-013505 FutureTEX — single institution-grain rows in the roster
  unit's shape (no organizations-shard row, no site rows), each with
  existence + scope evidence. **Next free: ORG-013506.**
- **HELD — HVT Center (packet row PROG-NEW-A04) and its University
  of Denver anchor draft (ORG-NEW-A04) were NOT created.** The
  packet's status finding, quoted: "The first Phase of the center
  was completed on September 30, 2024, after five no-cost
  extensions… it is presently ready to move to Phase II in a new
  structure and location" — a proposal posture, not an operating
  center; the center's own domain (hvtcenter.org) is lapsed and
  parked for sale, and the director retired from DU in July 2024.
  Whether to mint rows for centers that concluded before ever being
  recorded is an open owner-battery item; the packet supplies the
  pair as drop-together, and both drafts remain preserved verbatim
  in this folder's `proposed_rows.csv` / `proposed_institutions.csv`.
  No IDs were allocated to either draft. RAPID and LIFT
  (STILL_UNCERTAIN) were likewise left untouched — no rows, no
  evidence.
- **Ecosystem rollups recomputed (V-16, same pass)** — the
  recomputation was first verified to reproduce every carried
  rollup on the pre-build tree (zero drift). Changes: ORG-002846
  UMass Lowell name gains the two center rows (SHAP3D, WindSTAR) in
  type-precedence order, URL unchanged; ORG-002845 Virginia Tech
  name gains "Wood-Based Composites Center (WBC)", URL unchanged;
  ORG-002851 NC State name gains "Center for Dielectrics and
  Piezoelectrics (CDP)", URL unchanged; ORG-002099 IACMI name →
  "Institute for Advanced Composites Manufacturing Innovation
  (IACMI)", URL → https://www.iacmi.org/about-us/ (the un-decomposed
  claim is now decomposed by PROG-000325); ORG-002100 REMADE name
  unchanged, URL → https://remadeinstitute.org; ORG-002097 BioMADE
  `polymer_program` false → true, name → "BioMADE", URL →
  https://www.biomade.org/about; ORG-001217 America Makes name →
  "America Makes", URL → https://www.americamakes.us (the
  EARTH/AACAMS claim text is replaced by the rollup of
  PROG-000328). Only the rollup fields (+ `polymer_program` on
  BioMADE) and `last_verified` changed on each carried row. The
  three new institution rows carry their computed rollups
  (FutureTEX's rollup URL is the HQ host's news page, pending the
  institute's own site, as its row notes state).
- **Evidence minted (28 rows)** — programs EVD-333823..EVD-333844
  (existence + scope per created row; source_class per the witness's
  actual host: `own_site` throughout except the IACMI scope row,
  whose verbatim scope witness is the lead institution's dated news
  page, classed `press`; tier_effect from each new record's own
  tier: supports_A ×12, supports_B ×8, supports_C ×2); ecosystem
  EVD-333845..EVD-333850 (existence + scope per new institution;
  supports_A ×2, supports_B ×2, supports_C ×2). Allocation opened
  at EVD-333823 (tree scan max EVD-333822), contiguous. **Next
  free: EVD-333851.**
- **QUEUE** — the dept-row pilot claim, the one straggler still
  standing `claimed` on current main, is flipped to `done
  2026-11-12 (PR #298, merged)` per the git log; this unit's claim
  is added below it.
- **Gates** — `scripts/validate.py`: "OK — validation passed."
  (totals: 5,024 organizations, 407 ecosystem rows, 1,472 people,
  198 program rows, 40,913 evidence rows; warnings only the
  standing classes, none naming this unit's records).
  `scripts/check_row_loss.py --base origin/main`: "row-loss guard:
  OK — no keyed row removed from data/ since origin/main
  (merge-base 1f4a26c2f0)". No REMOVALS.csv.
