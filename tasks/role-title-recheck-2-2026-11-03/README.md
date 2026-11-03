# Role-title re-check, wave 2 (2026-11-03)

**Integrator for this pass:** claude-code, on the owner's laptop. It follows up wave 1
(`tasks/atlas-cleanup-2026-11-03/`), which left 214 people with a narrative `role_as_published`.

**Who (`build_batches.py`):** the 214 holds minus the 45 rank disagreements, plus the 27 KEEP rows of
`tasks/role-rank-recheck-2026-11-03/` (rank stands, title still narrative). That makes 196 people. 12 whose cited
pages are all on nrel.gov are listed in `nrel_held.csv` instead: nrel.gov stopped resolving after the lab was
renamed the National Laboratory of the Rockies (2025-12-01), and their URLs are re-pointed in a separate packet.
The other 184 people went to 8 Sonnet lanes (`LANE_BRIEF.md`, `lanes/`).

**Gates (`build_titles.py`):** a title applies only when every one of these holds.
1. The lane CONFIRMED it.
2. It reads as a title line (wave 1's `bad_title` filter, imported).
3. Its page is one the record already cites.
4. The lane reported no rank disagreement.
5. **New in wave 2:** its words appear in order on the **raw** page. WebFetch hands lanes a model's quotation, not
   the page, so each page was re-fetched with the NAS Firecrawl (`raw_check.csv`).
6. It passes integrator review (`TITLE_HOLD` in `build_titles.py`).

## Result (people records)

| | People |
|---|---:|
| `role_as_published` set to the printed title | 35 |
| Held: lane could not confirm (403s, no title line on a cited page, news prose only) | 86 |
| Held: lane line is not a clean title line | 25 |
| Held: page rank differs from the record's `role` | 25 |
| Held: title not found verbatim on the raw page | 7 |
| Held: integrator review (prose, not a title line) | 6 |
| Not sent to lanes: NREL-only pages | 12 |

`holds.csv` gives each held row's reason and, where a lane named it, the page that would settle it.

## Raw-page check (`raw_check.csv`, CONFIRMED lane rows)

84 found verbatim, 9 not found, 5 unfetchable (Johns Hopkins, Northeastern and Wisconsin pages answered errors to
the NAS fetcher). Only "found" rows can apply.

## Verification

- Every edit is hash-checked against the current cell. It was rehearsed on a temp copy of `data/`, then applied with
  `scripts/apply_p1_crm_scrub.py`.
- `python3 scripts/validate.py` passes.
