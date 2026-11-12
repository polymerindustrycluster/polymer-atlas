# Wave 3 — Minnesota lane packet (University of Minnesota, ORG-002855)

**Lane:** wave 3 lane 2 (Minnesota), per `working/wave3-batch-plan-2026-11-12.md`.
**Date:** 2026-11-12. **Basis:** Atlas data at main `f2c7c814` (read from
`~/workspace/atlas-p2-2026-11-12/data/`). **Packet-only:** no repo data edited,
nothing pushed. All witnesses are University of Minnesota pages fetched
2026-11-12. **Paid calls: 0** (free browser fetches + built-in search only).

## Counts (unit + filter)

| Count | Value |
|---|---|
| Carried program rows treated (UMN, active) | 2 — PROG-000072 IPRIME, PROG-000104 MSE |
| Proposed new program rows | 1 — UMN MRSEC (center-page witness; `proposed_rows.csv`) |
| Program fill cells proposed (`fills.csv` rows) | 6 — IPRIME 4 (research_areas, specialty_processes, specialty_materials, facilities_note), MSE 2 (research_areas, scale_band) |
| Depth after fills (of the 5 depth cells) | IPRIME 0/5 → 4/5 (scale_band held); MSE 3/5 → 4/5 (specialty_processes held) |
| Recorded UMN people adjudicated | 16 of 16 carried at ORG-002855 |
| LINK verdicts | 12 — 8 to PROG-000104 (MSE), 4 to PROG-000072 (IPRIME) |
| NO_WITNESS verdicts | 4 — PERSON-000113, 000115, 000118, 000121 |
| New-person candidates evaluated | 1 — C. Daniel Frisbie: **VERIFIED**, proposed primary PROG-000104 |
| lab_url witnesses captured | 13 people (11 on UMN subdomains; 2 UMN-linked but off-domain, flagged) |
| Title-refresh flags (rider: flag only) | 2 — PERSON-000105 Bates, PERSON-000108 Dorfman |
| Held out-of-vocabulary items | 2 verbatim quotes (below) |

## 1. PROG-000072 IPRIME — depth adjudication

Witnesses are IPRIME's own program pages on cse.umn.edu: Functional and
Sustainable Polymers (FSP), Coating Process Fundamentals (CPF), and
Biomaterials and Pharmaceutical Materials (BPM). (The cse.umn.edu/iprime
landing page itself returned only a news snippet on extraction — an
availability artifact of the fetch route, not absence; the program subpages
carried the substance.)

- **research_areas** (union of §3.1/§3.2/§3.5, §3-first):
  `polymer_synthesis;polymer_physics;rheology;characterization_methods;membranes_separations;sustainable_feedstocks;biomedical_polymers`
  — FSP: "Design and synthesis of novel polymers, characterization of their
  structural and mechanical properties, and investigation of their
  rheological and processing behavior"; applications include "Ionic
  membranes", "Nanoporous materials and templates", "Biorenewable
  materials"; BPM header states the biomedical/pharmaceutical-applications
  scope that carries `biomedical_polymers`.
- **specialty_processes** (§3.1 only): `coating_applying` (CPF: coatings
  "made by depositing layers of polymer solution, liquid monomer or
  particulate suspension that are then solidified by drying or curing");
  `extrusion_unspecified` (FSP project "Multilayer coextrusion and
  adhesion" — subtype never stated, so the unspecified term, never
  upgraded); `fiber_formation` (FSP PI expertise "fibers");
  `polymerization` (FSP synthesis scope).
- **specialty_materials** (§3.2 only): `fluoropolymers` (FSP project "New
  fluorinated polymers and copolymers"); `bioplastics_biobased` ("Improved
  biorenewable polymers"); `composites_unspecified` ("Inorganic/organic
  nanocomposites"; BPM "materials and composites" — type unstated);
  `films_flexible_packaging` (FSP application "Multilayer and barrier
  films").
- **facilities_note**: Polymer Characterization Facility (FSP "Key
  Facilities"); CPFP Labs; Characterization Facility + Biomedical Image
  Processing Laboratory (BPM facilities paragraph).
- **scale_band — HELD.** IPRIME is an industry consortium; it publishes
  member-company and faculty counts and dollar contributions (47 faculty /
  9 departments / 7 program areas per the ERC Association directory), and
  the S3 conversion rule bars faculty counts and dollars. A consortium has
  no enrollment to convert. Nothing else on its own pages states a
  qualitative size self-characterization in enrollment terms.
- **Out-of-vocabulary HOLD (verbatim):** FSP PI table, Ellison expertise:
  "Composites, thin films, lithography, fibers, **photopolymerization**,
  and processing" — no §3.1 slug covers photopolymerization or lithography;
  held for the vocabulary queue, not improvised. (`fiber_formation` covers
  "fibers"; the rest of the line is covered by other fills.)

## 2. PROG-000104 Materials Science and Engineering — depth adjudication

- **research_areas**: proposed value adds one term to the carried four —
  `biomedical_polymers` — from the program's own PhD page, whose research
  clusters are named as "Biological Engineering and Biomaterials,
  Catalysis and Reaction Engineering, Soft Matter and Fluid Mechanics,
  **Polymer Science**, Electronic, Photonic, and Structural Materials…"
  (https://cse.umn.edu/cems/materials-science-phd).
- **scale_band: `medium`** — borderline call, logged. Basis: the UMN
  Graduate School's published program statistics (apps.grad.umn.edu) give
  Materials Science and Engineering (Twin Cities) **enrolled 80 in Fall
  2022**, the latest year of the published series (72–87 across Fall
  2013–2022); 80 converts to medium (30–120) under the v1.13 S3 rule.
  Caveat for the integrator: that series counts the program's *graduate*
  enrollment (M/ MS/ PhD) only; BMatSE undergraduate enrollment is not in
  it, so a whole-program figure could in principle cross into large. The
  row's carried completions (45, IPEDS CIP 14.1801) were *not* used —
  completions are not enrollment under S3.
- **specialty_processes — HELD.** The program pages state research
  clusters, not §3.1 process specialties at program grain; individual
  faculty processes are people-grain facts and were not promoted to the
  program row.
- **specialty_materials / facilities_note:** no change proposed; the
  carried values stand (the PhD page's "state-of-the-art experimental and
  computational resources" is generic and fills nothing).

## 3. UMN MRSEC — proposed program row: SETTLED (VERIFIED for creation)

Settling witness is the center's own site on the UMN domain
(https://www.mrsec.umn.edu/), which states verbatim: "University of
Minnesota MRSEC… Funded by the National Science Foundation through the
University of Minnesota MRSEC under **Award Number DMR-2011401**" —
matching the NSF scan's candidate (award 2011401, 09/2020–08/2027; UMN
Experts gives the period as 9/1/20 → 8/31/27). Research page names IRG-1
(Ionic Control of Materials) and IRG-2, "Mesoscale Network Materials",
whose senior-investigator expertise lines are polymer-verbatim
("Amphiphile/polymer synthesis, thermodynamics, scattering" —
Mahanthappa, Leader; "Polymer synthesis, thermodynamics, mechanics" —
Bates; "Polymer characterization, scattering, dynamics" — Lodge), and a
center highlight is "Sub-1 V, Flexible, **All-Polymer** Complementary
Logic Circuits" (PI: Dan Frisbie, IRG-1). Director: Chris Leighton (CEMS
core-faculty page: "Director, MRSEC"). Draft row in `proposed_rows.csv`
(center type, research_areas
`polymer_synthesis;polymer_physics;rheology;characterization_methods`,
tier A basis = center's own site). Held cells on the draft row, with
reasons recorded in its notes: specialty_processes / specialty_materials
/ facilities_note / scale_band — fetched center pages state no §3.1
process or §3.2 material family at program grain, name no facility, and a
center has no enrollment.

Not conflated: the **Center for Sustainable Polymers** (CSP, NSF CCI) is
a separate UMN center and belongs to the NSF-centers batch-1 lane; this
packet proposes the MRSEC row only.

## 4. Link pass — adjudications (16 recorded + Frisbie)

Rule applied: person-level witness on UMN pages (Gate A current-faculty
styling + Gate B polymer-research witness); `program_org_id`
single-valued, degree program primary where the person holds one,
otherwise the witnessed center. CEMS core faculty are the faculty of the
department that houses PROG-000104; Chemistry/Pharmaceutics faculty take
the witnessed center (IPRIME) instead.

**LINK → PROG-000104 (MSE degree, primary):** Bates 000105, Lodge 000107,
Dorfman 000108, Ellison 000109, Mahanthappa 000111, Calabrese 000112,
Morse 000117, Dutcher 000119. Witnesses: FSP PI table (Bates, Lodge,
Dorfman, Ellison, Mahanthappa, Morse), MRSEC IRG-2 investigator list
(Lodge, Mahanthappa, Calabrese — "Rheology/mechanics, in situ scattering,
dynamics"), CPF PI table (Dutcher), CEMS Core & Emeritus Faculty page
(all eight styled as current CEMS faculty).

**LINK → PROG-000072 (IPRIME, witnessed center):** Hillmyer 000106 (FSP
Program Leader; his own UMN profile's Affiliations list names IPRIME),
Reineke 000110 (FSP PI), Lamb 000114 (FSP PI — "Catalysis and physical
organic techniques to the synthesis of new polymers and small
molecules"), Siegel 000116 (BPM PI — "Drug and hormone delivery,
biosensing, hydrogels, microfabrication, **drug/polymer dynamics**").

**NO_WITNESS (4), with the settling fact for each:**
- **Walker 000113** — Gate A is certain (CEMS core faculty, "Professor";
  MRSEC senior investigator, Seed focus; UMN Experts lists L. M. Walker
  as a PI on award DMR-2011401). But no fetched UMN program page states
  her research area or names her on a polymer-program roster, so no
  program tie settles within this lane's budget. Settling fact: a UMN
  page stating her soft-matter/polymer-rheology research area (e.g., her
  CEMS research-area profile) or naming her on an FSP/CPF/IRG roster.
  Near-miss; her lab witness was still captured (below).
- **Hoye 000115** — appears on no current IPRIME program PI table
  (FSP/CPF/BPM/4D all fetched). A dated IPRIME deck once listed him as a
  BPM affiliated investigator; the current BPM page does not. Settling
  fact: a current UMN program page naming him (a CSP roster, if the CSP
  row lands via NSF batch 1, is the likely one).
- **Tonks 000118** — no fetched UMN program page names him; his
  polymer-center tie runs through CSP, which is not a carried row in
  this packet. Settling fact: the CSP row landing (NSF-centers batch-1
  lane) with its roster naming him, or another carried-program page.
- **Boehnke 000121** — named PI on IPRIME's Data Driven Discovery and
  Design (4D) page ("Nanotechnology / drug delivery"), but 4D is not
  polymer-scoped on its face, so the listing does not carry a polymer
  program tie. Settling fact: naming on an IPRIME polymer program page
  (FSP/BPM/CPF) or a UMN page stating polymer research by her. (The 4D
  page also styles her "(CEMS)" — affiliation drift from her recorded
  DSI profile URL; noted for the integrator, no rank stated there.)

**Weakest links (named, per packet practice):** Dutcher 000119 → MSE
(her polymer witness is the CPF PI listing; her stated expertise —
"Rheology, Emulsions, Surfactants, Microfluidics" — is not
polymer-verbatim, though CPF's own scope is polymer-solution coatings)
and Morse 000117 → MSE (FSP expertise line reads only "Theory of complex
fluids"; the witness is his PI listing inside FSP's polymer-explicit
program scope). Both stand on program-scope + named-PI, the roster
standard used in waves 1–2; flagged so the verifier can spend its
attention there.

**Banked witnesses (evidence only; primaries unchanged):** MRSEC
senior-investigator ties for Bates, Calabrese, Dorfman, Ellison, Lodge,
Mahanthappa, Reineke (IRG-2) and Frisbie (IRG-1) — if the MRSEC row
lands, these bank as evidence rows behind the degree/IPRIME primaries.
Hillmyer's own profile also lists the Center for Sustainable Polymers
affiliation (CSP lane's witness, banked here).

## 5. New-person candidate — C. Daniel Frisbie: VERIFIED

- **Gate A:** CEMS Core & Emeritus Faculty page styles him
  "Distinguished McKnight University Professor" (CEMS); MRSEC People page:
  "C. Daniel Frisbie, **Professor, CEMS**… focus: IRG-1". (He was CEMS
  Head 2014–2024 per UMN-hosted bios — past role, not proposed.)
- **Gate B:** his CEMS profile (https://cse.umn.edu/cems/c-daniel-frisbie)
  states research on organic semiconductors / molecular electronics; the
  CPFP people page (cpfp.cems.umn.edu/people) gives "Research areas:
  Organic and molecular electronics, printed and flexible electronics";
  the UMN MRSEC site names him PI of the all-polymer complementary
  logic-circuits highlight — polymer-semiconductor research stated on
  UMN's own pages.
- **Proposed record sketch** (integrator creates; ID allocated there):
  full_name "C. Daniel Frisbie"; institution ORG-002855; role
  `professor`; role_as_published "Distinguished McKnight University
  Professor"; program_org_id **PROG-000104** (degree primary — CEMS core
  faculty); public_profile_url https://cse.umn.edu/cems/c-daniel-frisbie;
  lab_url https://frisbie.cems.umn.edu (his link in the CPF PI table);
  banked affiliations: IPRIME CPF PI ("Printing Processes, Printed
  Electronics"), MRSEC IRG-1 senior investigator. Tier A basis.

## 6. lab_url witnesses captured (people.csv `lab_url` field; flag-only packet)

All are the person's group-site link as published on a UMN page.

| Person | lab_url | Witness page |
|---|---|---|
| Bates 000105 | https://bates.cems.umn.edu | FSP PI table |
| Hillmyer 000106 | https://hillmyer.chem.umn.edu | FSP PI table; his profile ("Research Website") |
| Lodge 000107 | https://lodge.cems.umn.edu | FSP PI table |
| Dorfman 000108 | https://dorfman.cems.umn.edu | FSP PI table; MRSEC People |
| Ellison 000109 | https://ellison.cems.umn.edu | FSP PI table; MRSEC People |
| Reineke 000110 | https://www.reinekegroup.org | FSP PI table; MRSEC People — **off-domain** (group site linked from UMN pages but not hosted on umn.edu; §4.9 describes lab_url as published on an institutional domain — integrator's call) |
| Mahanthappa 000111 | https://softmatter.cems.umn.edu | FSP PI table; MRSEC People |
| Calabrese 000112 | https://calabrese.cems.umn.edu | FSP PI table; MRSEC People |
| Morse 000117 | https://morse.cems.umn.edu | FSP PI table |
| Dutcher 000119 | https://cfmf.umn.edu | CPF PI table; MRSEC People ("group site") |
| Walker 000113 | https://walker.cems.umn.edu | MRSEC People ("group site") — captured although her link verdict is NO_WITNESS |
| Frisbie (new) | https://frisbie.cems.umn.edu | CPF PI table |
| Lamb 000114 | (sites.google.com group page, linked from FSP PI table) | **weak** — Google Sites, not an institutional domain; recorded here as a witness only, not proposed as a clean lab_url |

No lab witness found on fetched pages for Hoye 000115, Siegel 000116
(BPM links him to the generic pharmacy.umn.edu), Tonks 000118,
Boehnke 000121.

## 7. Title-refresh flags (rider: flag only — integrator applies)

- **PERSON-000105 Frank S. Bates** — recorded role_as_published
  "Professor". Current CEMS Core & Emeritus Faculty page and MRSEC
  People page both style him "**Regents Professor**". Proposed refresh:
  role_as_published → "Regents Professor" (role stays `professor`).
- **PERSON-000108 Kevin D. Dorfman** — recorded "Professor". Current
  CEMS core-faculty page styles him "**Distinguished McKnight University
  Professor, Department Head**"; an MRSEC news item likewise calls him
  "CEMS Department Head Kevin Dorfman". Proposed refresh:
  role_as_published → "Distinguished McKnight University Professor;
  Department Head" (verbatim components as published; role stays
  `professor`).
- Checked, **no flag**: Hillmyer 000106 (current profile styling matches
  the recorded role_as_published verbatim); Lodge 000107 ("Regents
  Professor" matches); Calabrese 000112 ("Associate Professor" matches,
  MRSEC People verbatim); Mahanthappa 000111, Morse 000117, Walker 000113,
  Dutcher 000119 ("Professor" stylings consistent). Ellison 000109: core
  page adds "Faculty Director, IPRIME" — an addition, not a
  contradiction of the recorded styling; no flag, but the IPRIME
  directorship is banked corroboration in §4 above.

## 8. Census observations (out of scope for this lane; noted once)

IPRIME's program pages name further UMN polymer faculty not among the 16
recorded people — e.g., FSP/CPF co-leads Lorraine Francis and Satish
Kumar, Xiang Cheng (CPF PI: "Colloids, Polymers, Rheology"), MRSEC
Director Chris Leighton, BPM leader Chun Wang. No verdicts offered;
they belong to a people-census lane if the owner wants one.

## Fetch log (all umn.edu unless noted; ~6-per-program budget respected)

IPRIME: cse.umn.edu/iprime (thin extraction — see §1), /iprime/fsp,
/iprime/coating-process-fundamentals-cpf-1,
/iprime/biomaterials-and-pharmaceutical-materials-bpm,
/iprime/data-driven-discovery-and-design-4d. MSE/CEMS:
cse.umn.edu/cems/materials-science-phd,
cse.umn.edu/cems/cems-core-emeritus-faculty, apps.grad.umn.edu program
statistics (via search result). MRSEC: mrsec.umn.edu/, /research/,
/people/investigators/. People: cse.umn.edu/chem/marc-hillmyer;
cse.umn.edu/cems/c-daniel-frisbie (via search-result text). Discovery
corroboration read, not re-derived: NSF scan (UMN MRSEC + CSP entries)
and rosters scan (Frisbie row) in staging/working. No failed fetches; no
paid calls.

---

## Integration record (integrator, 2026-11-12)

**Fills applied (6):** PROG-000072 IPRIME — research_areas,
specialty_processes, specialty_materials, facilities_note all set from
empty, exactly as `fills.csv` adjudicated (scale_band stays held: a
consortium publishes no enrollment, and S3 bars faculty counts and
dollars). PROG-000104 MSE — research_areas += biomedical_polymers;
scale_band = medium, the borderline call as adjudicated in §2 above
(published graduate enrollment of 80 in Fall 2022 converts under S3;
the series carries no undergraduate enrollment — the caveat stands as
logged, not re-litigated).

**New program row:** PROG-000305 Materials Research Science and
Engineering Center (MRSEC), as drafted in `proposed_rows.csv`
(program_id allocated at integration, above the tree-wide maximum
PROG-000304). The ORG-002855 ecosystem rollup was recomputed per V-16
in the same pass: polymer_program_name is now "Materials Science and
Engineering; IPRIME; Materials Research Science and Engineering Center
(MRSEC)"; polymer_program_url is unchanged (the MSE degree row still
sorts first). The Center for Sustainable Polymers row is NOT part of
this pass — it integrates with the NSF-centers unit.

**Links (12 primaries; 4 NO_WITNESS stand):** 8 to PROG-000104,
4 to PROG-000072, one scope evidence row each. NO_WITNESS stands —
Walker 000113, Hoye 000115, Tonks 000118, Boehnke 000121: no record
motion and no evidence row, per wave-2 practice; the verdicts and
their settling facts stand in §4 above. Weakest links stand as
flagged there: Dutcher 000119 and Morse 000117, both to PROG-000104.

**New person:** PERSON-002117 C. Daniel Frisbie minted (VERIFIED in
this packet and in the wave-3 roster-verification packet; program
PROG-000104 agreed by both). Title applied as this packet styles it:
role_as_published "Distinguished McKnight University Professor" —
the roster packet's longer form ("Distinguished McKnight University
Professor of Chemical Engineering and Materials Science") is flagged
here, not applied. His lab_url (https://frisbie.cems.umn.edu) rides
the record creation; his evidence is the admission row plus the link
row, per the build spec.

**lab_url applied (11 values):** the 10 recorded people Bates,
Hillmyer, Lodge, Dorfman, Ellison, Mahanthappa, Calabrese, Morse,
Dutcher, and Walker — each with its own S6 evidence row — plus
Frisbie's new record. HELD, as flagged in §6: Reineke
(www.reinekegroup.org, off-domain) and Lamb (Google Sites) were not
applied.

**Title refreshes (P1 rider, 2):** Bates 000105 → "Regents
Professor"; Dorfman 000108 → "Distinguished McKnight University
Professor; Department Head" (the page's verbatim components, joined
with the field's semicolon per §7), each with its own evidence row.

**Banked witnesses:** the MRSEC senior-investigator ties banked in
§4 (Bates, Calabrese, Dorfman, Ellison, Lodge, Mahanthappa, Reineke;
Frisbie IRG-1) were minted as banked evidence rows in an append-only
follow-up build under the integrator's ruling (EVD-333573..EVD-333580;
they claim the PROG-000305 affiliation only and change no
program_org_id). Hillmyer's CSP affiliation remains unminted — no CSP
program row exists yet; it integrates with the centers unit.

**Evidence:** EVD-333539..EVD-333580 — 42 rows (8 in
evidence_programs.csv: 6 fills + MRSEC existence/scope; 34 in
evidence_people.csv: 12 links, Frisbie admission + link, 10 lab_url,
2 title refreshes, 8 banked MRSEC affiliations). Next free
EVD-333581. QUEUE: the P2-applications
claim is flipped to done (PR #283, merged) and this pass's claim is
added, per the standing pattern.
