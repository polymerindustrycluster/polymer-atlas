# UT skimpy-state pilot (2026-11-04)
Pilot of the skimpy-state expansion wave: one thin state, two-source federal overlap (ECHO/FRS ∩ OSHA or ITA from tasks/lead-fusion-2026-11-01/clusters.csv).
- Why UT: 20 sites (<25) with the largest clean two-source queue (19). CO had 18 but contains the Cray Valley TRI hold; AZ 16, RI 14, NH 11, NV 11.
- `build.py` appended all rows (IDs from `scripts/atlas.py next-id`); `verdicts.csv` lists all 19 candidates (plus one residue lead found along the way); `frs_fresh_2026-11-04.json` is the FRS REST pull.
- Paid API calls: 0 (FRS REST, Census geocoder, public web only).
