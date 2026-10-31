# F5 coverage-reconciliation source packet

Published by the campaign orchestrator on 2026-10-30, at the request of the
F5 lane (PR #10), so the coverage reconciliation can be finished against
primary inputs instead of campaign-reported figures. Published from main
`4a406991c9466b10896f17913f9995b541b39713`; this packet is documentation and
build metadata only — **no canonical data files are touched**.

## Contents and provenance

### QCEW denominators
- `qcew_denominators_by_state_2023.csv` — QCEW establishment counts for all
  51 jurisdictions × the Atlas NAICS set. Source: **BLS QCEW via the CEW
  data API**, annual state area files
  (`https://data.bls.gov/cew/data/api/{year}/a/area/{area_fips}.csv`),
  filter `own_code=5` (private), `qtr=A`, `size_code=0`, value
  `annual_avg_estabs`. **2023 is the denominator of record**; 2024 columns
  are a sensitivity pull, never mixed into a 2023 ratio. Pennsylvania 2023
  NAICS 326 = **642** (3261 = 551, 3262 = 91); Ohio 2023 NAICS 326 = **890**
  (the standing control anchors 3261 = 706, 3262 = 184 reproduce exactly).
  Blank cells are not-published / no-row — **unknown, never zero**. State
  totals come from the state area file, never a county sum; geography was
  asserted against BLS's own area-titles file.
- `qcew_denominators_pic12_county_2023.csv` — the PIC-12 county × NAICS
  extract (12 counties × 20 codes, 240 rows). Sources: **Census CBP 2023**
  county file and **BLS QCEW 2023** (same filters as above), merged
  per-cell with the source named on each row; suppressed cells are marked,
  never zero-filled. PIC-12 NAICS 326 denominator of record = **367**.
  This file carries the 2026-10-29 FIPS correction inline: the original
  build read Ashtabula County from BLS area 39005 (Ashland County);
  Ashtabula is **39007** (QCEW 2023 NAICS 326 = 21), and the corrected
  367 supersedes the original 353.

### TRI worklist / verdict ledger
- `tri_worklist_verdict_ledger.csv` — all **1,797 facilities** of the
  national TRI reverse-yield worklist, one row per facility, keyed by
  TRIFID (the stable facility ID), with FRS ID, facility identity/address
  as filed, worklist classification and priority class (P0–P4), packet,
  the lane verdict and tier, the registry-link outcome (org/site), and the
  creation outcome (org/site IDs created, per the F1 class map v2).
  Source: **EPA Toxics Release Inventory, reporting year 2024** national
  extract (77,295 form rows → 21,482 facilities → screen → 1,797-row
  worklist after excluding OH/PA/SC, which were built in earlier phases).
  TRI parent names are as filed in the public TRI data (a lead, never an
  Atlas parent determination). Final accounting: **1,657 VERIFIED /
  84 REJECT / 56 STILL_UNCERTAIN** — every worklist facility verdicted
  exactly once.

### Creation-frame reproduction kit (passes 20–25)
- `frame_allocations_pass20.csv` … `frame_allocations_pass25.csv` — the
  passes' allocation records, restricted to the frame-relevant columns
  (`allocated_id`, `id_type`, `class`, `source_key`, `target_file`,
  `resolves_to`). The free-text `notes` column is **withheld under
  AGENTS.md §5 hygiene**: it is integrator working prose and in places
  discusses licensed-source conformance; nothing in it is needed to
  reproduce the frame. Marker/annotation classes (e.g. `org_create_watch`)
  are present in these files and are **not** creations — see AGENTS.md
  §2 rule 10.
- `frame_design_key_index.csv` — every packet design key (TRI waves,
  SC wave 1, candidate queue Q01–Q02) with its kind, org reference, and
  creating-facility TRIFID where the design carries one. Pass 21's PR #6
  packet produced no creations (flips/repoints/edits only), so it has no
  design keys here.
- `build_f1_mapping.py` — the exact builder that produced the F1 class
  map v2 (`tasks/f1-class-map/`) from these inputs plus the worklist;
  paths inside are the orchestrator's staging paths — map them onto this
  packet's files (worklist columns are carried in the ledger above).

## Count clarifications (agreed with the F1/F5 lanes)
- Unique creation frame, passes 20–25: **2,199 records** (682 orgs +
  1,517 sites).
- The 1,517 site creations split **1,383 TRI-origin + 134 NOT_TRI**
  (NOT_TRI = SC wave 1: 61 sites, candidate queue Q01–Q02: 73 sites;
  NOT_TRI orgs = 93, for 227 NOT_TRI records in total).
- Class distribution of the frame: P0 0 · P1 417 · P2 180 · P3 771 ·
  P4 604 · NOT_TRI 227.
