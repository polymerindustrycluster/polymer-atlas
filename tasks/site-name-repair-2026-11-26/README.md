# Site-name repair, pilot (2026-11-26)

Owner ruling 2026-11-25, "Fix site names, then close". Audit 13 smoke attempt 3 found 2 of 20 PIC-18 records with a contradicted `site_name`: the site is named for a legal entity or its parent, and the operator's own page names the operating division at that street. This folder holds the pilot only; no `data/` row changes yet.

## Frame and yield (unit: PIC-18 sites, `scripts/regions.py`; active, tier A-C, street held)
- 727 sites. 606 (83%) have a retained readable page on their organization's own domain (2026-11-16 corpus and the 2026-11-25 main-fetch run).
- 387 (53% of 727) have their street and city on one of those pages. On 239 of them a held name stands beside the street; 102 print no name beside it.
- 53 candidates (`CANDIDATES.csv`): class A, a different name printed beside the street (46); class B, no held name on any retained page of the site (13); 6 in both.

## Pilot (34 sites read by hand: seeded draw of 25 from class A, plus the 9 class-B sites outside the draw)
VERIFIED rename 3, STILL_UNCERTAIN 2, REJECT 29 (`PILOT.csv`, every quote replayed against the retained page by `pilot.py`). Draw of 25 alone: 2 VERIFIED, 1 STILL_UNCERTAIN, 22 REJECT.

`python3 tasks/site-name-repair-2026-11-26/candidates.py [--raw FILE]` and `python3 tasks/site-name-repair-2026-11-26/pilot.py` reproduce both.
