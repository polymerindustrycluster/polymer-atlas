# L14 — equipment first wave, 2026-11-06

Integrator application delegated by controller thr_9i2c6byhcz under AGENTS §2.7. Branch history at c71c0413 is the pre-pass backup. This folder is the packet and pass journal. No other canonical file is changed.

Acceptance: host-owned equipment pages only; held host FKs; §3.7 classes and §4.19 grain/access; allocated EQP block only; raw name/quote checks with no skipped sources; three hand-confirmed known answers; validate.py zero errors; two independent family refutes before ready status.
First user: PIC industry staff seeking characterization facilities. Non-use review date: 2026-12-06 (controller to assess use; no usage is claimed here).

## Published scope

34 equipment rows, all observed 2026-11-06, no withdrawals. Equipment has no verification_tier column; tiers A/B/C/U are not assigned. Zero evidence rows: §4.13 record_table excludes equipment, and §4.19 uses source_ref directly. The lane's conditional EVD allocation remains unused. No owner vocabulary/ring ruling is made.

Unit for both tables: equipment rows in this wave, host in Ohio, not physical instrument inventory counts. A plural equipment listing remains one named instrument line, never an inferred number of machines.

| Institution | Equipment rows |
|---|---:|
| University of Akron | 7 |
| Case Western Reserve University | 4 |
| Kent State University | 7 |
| The Ohio State University | 8 |
| University of Dayton | 2 |
| Youngstown State University | 6 |

| equipment_class | Equipment rows |
|---|---:|
| additive_manufacturing_polymer | 7 |
| afm | 2 |
| compression_press | 1 |
| dma | 1 |
| dsc | 3 |
| ftir | 1 |
| gpc_sec | 1 |
| hardness_tester | 2 |
| impact_tester | 1 |
| melt_flow_indexer | 1 |
| nmr | 1 |
| optical_microscopy | 2 |
| rheometer_rotational | 2 |
| sem | 3 |
| tga | 2 |
| twin_screw_compounder | 1 |
| universal_tester | 3 |

## Provenance and limits

`inputs.csv` records every output field and the checked words from the source. `verdicts.csv` has exactly 34 VERIFIED equipment rows; it reconciles one-to-one by EQP ID to inputs and data. Six source URLs (one per institution) supply the admitted rows. Booking details/contact data are not copied. Seven NPIC equipment/testing-service rows have fee_for_service from its Request a Quote route; the other 27 use not_stated. Kent's public user access does not by itself determine an access_mode enum. Room reservation fees at YSU are not equipment fees.

Dedupe: ran atlas.py dedupe-check by domain and institution name for all six hosts. All hosts are held ecosystem records; no organization/site is created, so address/trade-name creation checks do not apply. Existing equipment.csv had zero rows; builder checks unique host/name against all existing equipment rows before append. Optional site FKs are blank because no physical site mapping was verified. Program FKs link NPIC and AMLCI Characterization Facility only; no institution-wide degree-program link is inferred.

Dayton's university-managed Google Sites BAMS page is an own lab page, independently linked as BAMS Lab by https://udayton.edu/engineering/research/labs/index.php (raw fetched 2026-11-06). It explicitly names the load frame and polymers/elastomers. Dayton is represented by BAMS, not by an inferred UDRI instrument model.

## Holds and unworked candidates

These are source-level holds, not counted in the 34 instrument verdicts.

| Institution / candidate | Verdict | Settling fact / recommendation |
|---|---|---|
| Akron NPIC generic Rheometer | STILL_UNCERTAIN | Rotational vs capillary subtype not stated; need an own-page model or subtype. Other out-of-vocabulary tools deferred without using escape class. |
| CWRU Swagelok expansion | STILL_UNCERTAIN | https://engineering.case.edu/research/centers/swagelok-surface-analysis-materials/image-analysis reached; instrument detail pages not checked this wave. Follow named instruments on own detail pages, do not infer a model from general microscopy prose. |
| Kent AMLCI TEM | STILL_UNCERTAIN | Published name is truncated `Transmission Electron Microscope (TEM`; obtain clean instrument naming before create. Remaining tools deferred; escape vocabulary would need flagging. |
| Ohio State Dynamic Vapor Sorption | STILL_UNCERTAIN | Page describes water-vapor permeability; verify the actual named instrument and method before classifying. |
| UDRI generic capabilities | STILL_UNCERTAIN | https://udri.udayton.edu/expertise/materials/material-and-manufacturing-research/polymer-and-composite-materials.php reached but groups techniques and processing capabilities; need specific instrument or named service pages to avoid splitting a generic capability list. |
| YSU Filabot Filament Extruder | STILL_UNCERTAIN | Need source-supported screw configuration before assigning single_screw_extruder. |

Institutions whose attempted pages were unreachable: **none** (6/6 institutions reached). The Swagelok legacy equipment URL redirected to a general center page, so it was not treated as an equipment list. No failed fetch is used as negative evidence. Local data-estate catalogue search was incomplete because Windows Documents indexes are unavailable on this Mac; fresh university sources govern this wave.

Fetch budget: ≤6 primary page fetches per institution, counting initial discovery fetches and builder raw re-fetch; Dayton used six (generic UDRI, BAMS, Green Labs, engineering labs, BAMS re-fetch plus search retrieval as a conservative extra). Full raw HTML stays uncommitted in build/ because pages contain contacts. Only equipment quotes and citation URLs travel.

## Checks

- `python3 tasks/equipment-wave-1-2026-11-06/build.py --raw-check --apply`: PASS 34/34 names/quotes, six sources, zero skipped sources. Matcher uses the house ownership-status-2 word normalization, with standard HTML parsing and curl browser UA. No fallback needed.
- Hand-confirmed known answers: Akron NPIC Differential Scanning Calorimetry → dsc; MORE Atomic Force Microscope (Agilent 5500 SPM) → afm; YSU Lulzbot Taz 6 under Polymer AM → additive_manufacturing_polymer. All 3/3 returned correctly. Fabricated instrument negative control rejected.
- `python3 tasks/equipment-wave-1-2026-11-06/build.py`: PASS rerun, zero new rows; existing output compared field-for-field before skip.
- `python3 scripts/validate.py`: PASS, zero errors (baseline warnings retained); captured in validate.txt.
- No scripts/ changes; scripts pytest not applicable.

Rebase: take fresh main equipment.csv and rerun `build.py --apply`; never hand-merge CSV. A conflicting EQP ID or duplicate host/name fails rather than silently changing/duplicating data.

## Review

Pending independent Codex and Grok refute clerks, controller 05:55 directive supersedes council-only invocation requirement for this campaign.
