# programs-db crosswalk: IPEDS check, ROR links, Texas A&M fix, leads (2026-11-03)

**Integrator for this pass:** claude-code. The repo owner requested this pass in session
on 2026-11-03, and it goes in as a PR. **Inputs:** NCES IPEDS HD2024 (fetched
2026-11-03), the live ROR API (api.ror.org v2, fetched 2026-11-03), and the
UNITID→ROR crosswalk and hand-research layers of the PIC repo `polymer-programs-db`
(private). Crosswalk and layers are **leads**: nothing is minted on them alone.

## Applied (data/ecosystem.csv, data/evidence.csv)

| Change | Rows | Rule |
|---|---:|---|
| `ror_id` added | 69 | Institution-grain `university_college` rows with a UNITID and no ROR. Crosswalk candidate verified at api.ror.org: active, US, in the row's state, and domain or name agree . The ROR URL is appended to `sources`. Sub-units are skipped: V-14 keeps ROR unique. |
| Texas A&M identity fix (`ORG-004656`) | 1 | `ipeds_unitid` 228732 → **228723** and `website` tamus.edu → **www.tamu.edu**. Deciding fact, IPEDS HD2024: 228732 is "Texas A & M University-System Office" (tamus.edu). The record anchors 14 College Station faculty. Dated note, sources, and evidence row EVD-019902 (registry, supports_B). |

Edits are hash-checked (`edits.csv`, applied with `scripts/apply_p1_crm_scrub.py --packet-dir`).
141 cell edits across 69 rows; the evidence row goes to `data/evidence_ecosystem.csv` (SCHEMA v1.8 shard). Rebuilt against main after passes 41–46. `python3 scripts/validate.py` passes.

## Held (`holds.csv`, 10 rows)

- Penn State Behrend: its ROR record is **withdrawn**.
- Pennsylvania College of Technology, The Landing School, Purdue Indianapolis and the three Rutgers campuses (Camden, New Brunswick, Newark): no crosswalk candidate.
- Wichita State Tech (ROR = WATC), Edmonds College (ROR = Edmonds Community College) and CT State (ROR = Capital Community College): the name or domain disagrees. Each is a likely rename or merger, so each needs a human check.

## UNITID check (`unitid_check.csv`)

All 243 held `ipeds_unitid` values were checked against HD2024. One real error was found and fixed (Texas A&M). Three
domain differences are benign: web.mit.edu vs mit.edu, ucsb.edu, and twin-cities.umn.edu vs umn.edu.

## Leads (`leads.csv`, 224 rows): discovery only, never evidence

| Layer | Leads |
|---|---:|
| ABET-accredited programs | 80 |
| Polymer-specific society chapters (SPE, ACS Rubber, POLY/PMSE) | 61 |
| US non-degree credentials | 29 |
| Ohio program history | 19 |
| TAACCCT grant checks | 15 |
| Closure checks | 9 |
| Active polymer-CIP IPEDS programs at UNITIDs with no Atlas record | 7 |
| Programs invisible to a CIP census | 4 |

`atlas_org_id` shows whether the institution is already held. The match is by UNITID or exact name, or by name with
generic words ignored, which is flagged `(check)`. Each lead needs the named-program
test on the institution's own pages (SCHEMA §4.11, the Lakeland rule).

**Not used:** the programs-db layers drawn from PIC's internal vault or the faculty census. Internal material never
enters this public repo.

## Not done, and why

- **Completion years.** The Atlas already has its own NCES-direct pull,
  `tasks/ipeds-completions-2026-11-01/`, which labels by file year (C2024_A = 2024).
  Its proposals await application. programs-db labels by the fall of the academic year (2023 = AY2023-24) and takes
  pre-2022 years from the Urban mirror, so it is used here only as a cross-check, not a source.

## Rebuild

```bash
python3 tasks/programs-db-crosswalk-2026-11-03/build_crosswalk.py --data-dir <pre-pass data> --hd HD2024.csv --ipeds-ror <polymer-programs-db>/incoming/ipeds_ror.tsv --cache <ror cache dir>
python3 tasks/programs-db-crosswalk-2026-11-03/build_leads.py --data-dir data --programs-db <polymer-programs-db> --hd HD2024.csv
```
