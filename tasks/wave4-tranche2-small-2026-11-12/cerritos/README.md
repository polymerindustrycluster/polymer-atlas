# Wave 4 tranche 2 — Cerritos College (ORG-004630)

Lane: research only, 2026-11-12. Paid calls: zero.
Carried targets: PROG-000083 Plastics/Composites Manufacturing Technology (degree-type
row aggregating the program family's certificate + associate credentials, tier A,
depth 0/5) and PROG-000120 Chemical Technology - Polymer (certificate, tier A,
depth 0/5).
Unlinked pool at this institution: 0 people — no pool; links.csv/census.csv not
delivered per brief.

## Currency check — VERIFIED for both rows

Both programs are carried in the college's current catalog (cerritos-public.courseleaf.com,
fetched this pass):
- PROG-000083: "The Plastic Manufacturing Technology Program provides the diverse
  student body in the surrounding regional community with advanced education in plastic
  manufacturing technology…" — Associate program, 21 units of major requirements.
  https://cerritos-public.courseleaf.com/degrees-certificates-courses/degrees-certificates-programs-majors/plastics-manufacturing-aa/
- PROG-000120: "The Chemical Technology - Polymer program from Cerritos College is
  designed to bridge the technical training in process controls and plastic with the
  academic theoretical and practical laboratory skills of chemistry." — Certificate of
  Achievement, 19 units, as carried.
  https://cerritos-public.courseleaf.com/degrees-certificates-courses/degrees-certificates-programs-majors/chemical-technology-polymer/
The department page is also live: "Since 1974, the Cerritos College Plastics
Manufacturing Department (PMT) has been a leader in state-of-the-art technical
education." https://www.cerritos.edu/plastics/

## Depth fills (see fills.csv)

PROG-000083: 2 proposed, both flagged curriculum/description-grain; 3 refused.
- specialty_processes `injection_molding` (FLAGGED): the program's own published
  requirements include the required major course "ENGT 209 — Plastics Injection
  Molding I" (3.0 units). This is a required-course witness, not a program research
  statement; the integrator rules on whether required-curriculum process content
  codes at this grain. The weaker elective witness ("ENGT 251 Composites Fabrication
  and Tooling", recommended elective) was NOT coded — no §3.1 term honestly maps to
  it (fabrication/tooling composites subtypes are not stated).
- specialty_materials `composites_unspecified` (FLAGGED): the program's own catalog
  description states students "learn specific techniques related to composite and
  plastic manufacturing" — composites are named as program content with the type not
  stated, which is exactly the B-VOC `composites_unspecified` posture.
- REFUSED: research_areas (workforce program; no research statements; SLOs are
  skills statements); facilities_note (no publicly stated labs/equipment on the
  fetched program/department pages — the department Pathways page was not read this
  pass and is the named place to look); scale_band (no published enrollment; the
  IPEDS completions figure of 11 already on the row is a completion flow, which never
  converts).

PROG-000120: all five cells REFUSED. The certificate's own page is curriculum-only
(CHEM 110/111/112 + ENGT 111 Plastics Technology + ET 103 Industrial Process Control);
research areas are refused per the certificate rule (research statements, not
curriculum lines), and no specialty, facility, or enrollment statement exists on its
own page. It honestly stays 0/5.

## Weakest links

1. Both PROG-000083 proposals rest on catalog description/requirements text rather
   than a program research or capability statement — flagged in fills.csv for the
   integrator's call. If held to research-statement grain, PROG-000083 also stays 0/5
   and nothing in this packet is lost.
2. facilities_note for PROG-000083 was refused on the pages fetched; the department's
   Pathways page (linked from https://www.cerritos.edu/plastics/) is the unsettled
   place a facilities statement might exist.
