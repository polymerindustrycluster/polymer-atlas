# P2 single-source federal candidates: UT/DE/ID/NH/RI/NV (packet-only)

Base: main 9708c3a. No data files are edited. All evidence was fetched on 2026-11-04.

## Method
1. Rebuilt the federal frame with `tasks/federal-frame-2026-11-04/build_frame.py`. The patched copy is `build_frame_patched.py`, with only the MAIN/OUT paths changed. Inputs are the 2026-11-01 echo-frs-spine, osha-ita and osha-spine packets.
2. Kept the single-source classes C_ECHO, C_ITA and C_INSP for the 6 states, restricted to polymer NAICS (326*, 325211/212/510/520/910/991). That gives 424 rows (pid `P2-ST-nnn`).
3. Ran a name+city hint check against main because the frame dedupe misses held sites. 29 rows are ALREADY_HELD; see `held_map.txt` for the pid → SITE mapping.
4. Triage:
   - X_nonmfg (21): stores, distribution centres, banks.
   - U_stale (98): latest activity before 2019, or undated.
   - U_small (81): INSP-only rows with fewer than 20 employees.
   - CHECK: everything else.
5. Witness-checked the own sites of the largest CHECK rows, ordered by employees then recency, plus their address-duplicates. That covered 36 rows. The other CHECK rows are STILL_UNCERTAIN, each with a settling fact.

## Counts (rows), pass 2
| Verdict | Rows |
|---|---|
| VERIFIED | 26 (20 distinct sites) |
| REJECT | 27 (6 dated witness rejects + 21 non-manufacturing) |
| STILL_UNCERTAIN | 342 |
| ALREADY_HELD | 29 |

52 rows have been witness-checked so far, largest employers first. The rest carry settling facts.

## Rulings applied (integrator, 2026-11-04)
- Hiring-site postings are not witnesses. Latham (UT-378/220), Zenith/Mayzon (DE-243), Cornerstone (NH-180) and Corning (UT-217) moved back to STILL_UNCERTAIN.
- Address-first dedupe is accepted. Each merge is flagged in the `address_merge_group` column.
- Wrong-state rows carry `correct_state`: ID-172→IA, NV-207→AZ, NH-188→MA.

## Other judgment calls
- UT-138/238 (Convergent) defers to PR #77.
- Autajon Nashua (NH-258) is rejected as out of polymer scope, based on its own site's product description.
- Chem-Tainer Cranston (RI-260) is rejected on its RI Secretary of State revocation dated 2020-12-30.
- Fetch failure was treated as availability, not absence. No licensed sources were used.
