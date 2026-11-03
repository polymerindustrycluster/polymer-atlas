# Site discovery: the 6 counties PIC-18 added (2026-11-03)

When PIC-18 replaced PIC-12 (AGENTS.md §8), six counties joined the reporting region: Ashland, Columbiana, Erie, Huron, Richland and Tuscarawas. This pass checked whether the Atlas was missing polymer sites in them.

**Result: no creates and no data changes.** The six counties were already covered: most leads were sites the Atlas already holds.

## Lanes
Each count is a federal-spine or web lead, judged once.

| Lane | Scope | Leads | Duplicate of an Atlas site | Rejected | Still uncertain |
|---|---|---|---|---|---|
| L1 | Federal leads (TRI, OSHA, FRS) across the 6 counties | 18 | 3 | 2 | 13 |
| L2 | Tuscarawas, Columbiana | 14 | 7 | 2 | 5 |
| L3 | Richland, Ashland | 16 | 8 | 4 | 4 |
| L4 | Erie, Huron | 8 | 3 | 1 | 4 |
| **All** | | **56** | **21** | **9** | **26** |

- Of the 9 rejects:
  - one is a vacant lot in Ashland, per an EPA Region 5 release;
  - 8 are firms whose own sites state no polymer process (glass, copper, wood, packaging distribution, metal stamping, carbon brushes, construction equipment).
- Each lane's `verdicts.csv` gives the reason for every row.
- STILL_UNCERTAIN rows name the fact that would settle them. Most need the company's own page to confirm a polymer process at that address.
- L1 also found 4 registry-link candidates for existing records (`L1/registry_link_candidates.csv`). They are unapplied and go through the usual registry-link ruling.

## Flags for the integrator
- **The dedupe check misses some sites.** `atlas.py dedupe-check` does not match a site whose street address is only in `notes`. Examples: SITE-000863 and SITE-001910.
- **Possible duplicate pair.** SITE-000818 (ORG-000755) and SITE-001925 (ORG-001931) share 2228 Reiser Ave SE.

## Files
- `LANE_BRIEF.md`: the brief each lane ran.
- `L1_assignment.csv`: the federal lead list for L1.
- `L*/verdicts.csv` and `L*/REPORT.md`: each lane's verdicts and report.
- `L*/creates_*.csv`, `L*/evidence_rows.csv`: header-only, because no lane created anything.
