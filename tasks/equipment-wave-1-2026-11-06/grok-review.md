# PR #140 clerk-grok-2 (Grok) — APPROVE

Reviewed branch tip `29c62fe`. `scripts/build_site.py`, `scripts/test_build_site.py`, `scripts/test_validate.py`, and `data/equipment.csv` are identical to named head `b398365`. The two later commits only refresh the README, `render-checks.txt`, and `review-packet-v2.json`. Merge-base with current `origin/main` is `bdb8b98`.

## Scripts and patches

`fixture.patch` and `render.patch` match the branch diff against `bdb8b98` and touch only the authorized lines. No other production change.

- `equipment_block` was an f-string immediately followed by a parenthesized conditional. Calling that old expression on a real row raises `TypeError: 'str' object is not callable`. With the added `+`, `equipment_block` on all 34 rows returns a section titled `34 equipment rows` and 34 host-page links. Empty `source_ref` renders `<td></td></tr>`; a URL renders the host link.
- `test_v52_equipment_row_accepted` allocates `max(existing EQP)+1` instead of hard-coding `EQP-000001`.
- `unittest` of those two tests: OK. Full `python3 -m unittest discover -s scripts -p 'test_*.py'`: 222 run, 221 pass, 1 skip, exit 0.

## Data

34 rows, `EQP-000001`–`EQP-000034`, six held ecosystem hosts: Akron 7, CWRU 4, Kent 7, Ohio State 8, Dayton 2, YSU 6. Classes are all in SCHEMA §3.7. Access is `fee_for_service` on the 7 NPIC rows and `not_stated` on the other 27. Program FKs are NPIC `PROG-000022` (Akron) and AMLCI Characterization Facility `PROG-000014` (Kent) only. No site FKs, no withdrawn dates, no evidence rows. `inputs.csv` matches `equipment.csv` on every canonical field. `build.py` replay: 0 new rows, known answers 3/3, fabricated-name matcher rejected. `validate.py` exit 0 (34 equipment rows). Row-loss vs `origin/main` exit 0.

## Live pages, 2026-11-06

All 34 names and quotes, and all 7 `Request a Quote` access quotes, are words-in-order on the cited page. 0 misses. Checked class context: MORE microindenter text states Vickers hardness (`hardness_tester`); MORE Agilent 5500 AFM; Kent one TT-AFM line that says the lab has 5, kept as one named row; OSU thermoplastics, twin-screw, and the host spelling Bencthop; BAMS Instron text says polymers and elastomers; YSU Lulzbot sits under Polymer AM. `https://udayton.edu/engineering/research/labs/index.php` links `https://sites.google.com/udayton.edu/bams-lab/home`, the same university Google Site as the facilities source.

## Render

`python3 scripts/build_site.py --rebuild-db --out /tmp/l14/site` built 5432 HTML pages. The six host pages' `<th scope="row">` sets equal the 34 names, with host-link counts 7, 4, 7, 8, 2, and 6.
