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

## Counts (rows)
| Verdict | Rows |
|---|---|
| VERIFIED | 21 (15 distinct sites; 6 are same-address duplicates) |
| REJECT | 25 (4 dated witness rejects + 21 non-manufacturing) |
| STILL_UNCERTAIN | 349 |
| ALREADY_HELD | 29 |

## Judgment calls
- Two witnesses are employer ATS job postings: Latham on Greenhouse and Zenith/Mayzon on Paylocity. I accepted them as own-site witnesses.
- Rows that share an address were collapsed into one site: UT-215/367/371, UT-139/366, UT-219/376, UT-220/378, NV-205/307.
- Three rows have a state mis-key (ID-172, NV-207, NH-188). They stay uncertain and are not rejected.
- UT-138/238 (Convergent) defers to PR #77.
- Fetch failure was treated as availability, not absence. No licensed sources were used.
