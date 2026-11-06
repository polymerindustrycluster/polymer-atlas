# L14 equipment wave 2 — 2026-11-06

Controller-delegated application under AGENTS §2.7, new branch agent/codex/equipment-wave-2 from main 85b8560, fast-forwarded to ce4e22e before application. Branch history is the pre-pass backup; this folder is the packet and pass journal. The only canonical change is data/equipment.csv. SPEC.md records acceptance before application.

## Scope and counts

53 new equipment rows, EQP-000100–EQP-000152, observed 2026-11-06; 34 existing equipment rows preserved, total 87. All 53 use access_mode=not_stated; no operating availability or commercial booking right is inferred. Equipment has no verification tier: A/B/C/U counts are not applicable. No EVD rows: §4.13 record_table excludes equipment; §4.19 carries source_ref directly. No organization/site creation, status change, registry link, or owner ruling.

Unit/filter for both tables: equipment rows admitted in this wave, not a physical machine inventory or a complete institutional census. Five Ohio hosts contribute 41 equipment rows; three Pennsylvania hosts contribute 12 equipment rows. Plural/model-family listings remain one published line.

| Institution | Equipment rows |
|---|---:|
| Carnegie Mellon University | 3 |
| Cleveland State University | 12 |
| Lehigh University | 5 |
| NASA Glenn Research Center | 4 |
| Ohio University | 6 |
| Pennsylvania State University (University Park) | 4 |
| The University of Toledo | 12 |
| University of Cincinnati | 7 |

| equipment_class | Equipment rows |
|---|---:|
| additive_manufacturing_polymer | 3 |
| afm | 1 |
| dma | 1 |
| dsc | 5 |
| fatigue_tester | 1 |
| ftir | 3 |
| hardness_tester | 4 |
| mass_spectrometry | 3 |
| optical_microscopy | 5 |
| permeation_tester | 1 |
| raman | 1 |
| rheometer_rotational | 6 |
| saxs_waxs | 1 |
| sem | 8 |
| tem | 2 |
| tga | 4 |
| universal_tester | 2 |
| xrd | 2 |

## Provenance, grain and FKs

inputs.csv supplies the exact canonical projection and per-row raw quote. verdicts.csv has 53 VERIFIED instrument/line verdicts and reconciles one-to-one by equipment_id. Eight own-page URLs supply all admitted rows. Quotes and names were freshly fetched using curl with a browser UA; the reused wave1 Text/has matcher (house word-sequence normalization) checks all rows with no skips. Full downloaded pages remain uncommitted under build/ because they contain personal contacts; no contacts are copied into this packet.

Host dedupe: atlas.py dedupe-check domain and normalized name across all organization shards and ecosystem (dedupe-*.txt); its exit 1 means a hit, not a failure. NASA's shared nasa.gov domain returns other NASA and technology-transfer records: ORG-001264 is specifically Glenn. Toledo, Cincinnati and CSU technology-transfer offices are not used. Penn State University Park ORG-002775 and Behrend ORG-002779 are distinct. Address/trade-name creation dedupe is not applicable because no host/site is created. Existing equipment host/name pairs are checked before append.

Six Ohio University rows link held CAMP program PROG-000020, whose host is ORG-002088; all other program FKs are blank. CMSC is not assumed to be Toledo's Polymer Institute, and AMCC is not assumed to be Cincinnati's Polymer Research Center. Site FKs are blank because a physical site mapping was not verified.

NASA's Environmental Effects and Coatings page lists both spacecraft-polymer exposure work and materials characterization; four admitted rows preserve its listed analysis/instrument lines without a service-access assertion. Toledo's combined SEM/FIB and XRD/SAXS each remain one row; the latter uses xrd, with its SAXS capability in the published name. Its Varian instrument family remains one line. Cincinnati's HR-20 DMA attachment is not separately counted. Penn State's DSC + FSC remains one published line under dsc. Ohio's published spellings “LBPF Polymer Printer” and “Micro-Hardness Intender” are retained. No unlisted models or counts are invented.

## Holds and source availability

holds.csv contains 10 STILL_UNCERTAIN cases: six host/source cases and four instrument-listing cases. They are separate from the 53 instrument verdicts. No REJECT for absence or closure.

| Institution / candidate | Settling fact |
|---|---|
| Wright State — host | A held institutional operator record is needed before an equipment FK can be applied. Recommend its own Materials Characterization Facility list after host integration. |
| Lorain County Community College — host | A held institutional operator record is needed. Recommend own Fab Lab or Campana Center equipment list after host integration. |
| Stark State — Fortus 450 MC lead | The own mechanical engineering page is reachable but does not list this printer. Need an own-host instrument list; Ohio TechNet is only a lead. |
| Penn State Behrend — Knowledge Park list | Direct and house fallback both returned 403. Need a fresh reachable own-page listing; Behrend ORG-002779 is distinct from University Park. |
| University of Michigan — own equipment pages | Scott lab direct/fallback, battery lab and chemical engineering facilities returned 403. Need reachable own listing with raw words. |
| Michigan State — own testing/equipment pages | CANR and dotCMS routes returned Incapsula bot responses; rheology site timed out. Need reachable own listing; no absence inference. |
| The University of Toledo — Polymer Institute generic extruders | Need a named instrument line with screw subtype to select a governed processing class; do not infer from auxiliary equipment. |
| Ohio University — DIW Printer | Need polymer feedstock stated for this direct-ink-writing printer before polymer AM classification. |
| Ohio University — MTS / Instron / Psylotech | Material Loading System list gives manufacturer names only; need instrument identity/testing configuration to settle grain/class. |
| Cleveland State — BioX / Lumen X bioprinters | Need stated polymer or hydrogel feedstock rather than infer it from bioprinter branding. |

Pages unavailable on attempted routes: Penn State Behrend/Knowledge Park (403 direct and house fallback), University of Michigan (403 on Scott lab, fallback, battery and chemical-engineering pages), Michigan State (Incapsula bot walls on CANR/dotCMS; rheology timeout). These observations describe routes, not entire institutions or absent instruments. Stark's page was reachable but supplied no named printer. Wright State and Lorain County CC equipment pages were not raw-fetched because no held host FK resolves. Other admitted institutions' source pages were reachable. Research stayed below ~6 primary discovery fetches per host; raw verification re-fetches repeat admitted URLs.

The estate search was partial on this Mac (missing Windows Documents catalogues, exit 2); that is a platform coverage gap, not absence. No CRM, vault or licensed-source content is used. This is a selected governed-class subset, not every apparatus on the cited pages.

## Named checks

- Three hand-confirmed answers before relying on this packet: Toledo TA Instruments Q50 Thermogravimetric Analyzer (TGA) → tga / ORG-001316; CSU Asylum MFP-3D-BIO Atomic Force Microscope → afm / ORG-000158; CMU Zeiss Crossbeam 550 Ga FIB-SEM → sem / ORG-002778. Their exact names were read on the raw host lists, then all three passed the live name matcher. The reused matcher rejects “Fabricated instrument XYZ”.
- python3 tasks/equipment-wave-2-2026-11-06/build.py --raw-check --apply: 53/53 names and quotes across 8/8 sources, known answers 3/3. raw-checks.txt and application.txt record the pre-application checks/application; replay adds zero rows. append_sorted is reused.
- python3 tasks/equipment-wave-2-2026-11-06/check.py --pages: exact projection, all main equipment unchanged, 53/53 verdict census; temporary main-based application matches canonical output and byte-identical replay. Existing-ID mutation, duplicate host/name under a new ID, and an unheld host each fail before any CSV write. Actual 8 host HTML sections reconcile all 53 names/classes/access/source links.
- python3 scripts/validate.py: zero errors, 87 equipment rows; existing V-29/V-38/V-44 warnings. validate.txt is the full output.
- python3 scripts/build_pages.py: exit 0, 5,460 HTML files / 43.1 MB; generated output stays uncommitted in build/pages. No scripts/ change, so script pytest was not repeated.

## Refute status and limits

Independent Codex + Grok clerk reviews are pending. Not ready for controller merge until both approve and findings are fixed or held.

First user: PIC industry staff seeking testing/fabrication facilities. Non-use review date: 2026-12-06, for controller follow-up; no usage is claimed. No hosted deployment, physical instrument inspection, booking test or full institutional inventory was checked.
