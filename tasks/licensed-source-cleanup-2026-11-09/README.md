# Licensed-source cleanup (2026-11-09)

The repo owner asked for this in session on 2026-11-09. AGENTS.md §5 allows Plastics News, Rubber News, D&B, Data
Axle and ZoomInfo as **discovery leads only**: every fact must be cited to a primary or public source. 36 evidence
rows cited plasticsnews.com. None copied that publication's text; each cited it for a paraphrased fact.

## What this PR does
1. **Answers each of the 36 rows** with a new row citing a public source for the same claim. Evidence is
   append-only (SCHEMA §4.13): the old row stays and is answered by a later row, never edited away.
   - Two packet lanes found the public sources (`LANE_BRIEF.md`, `lanes/L1`, `lanes/L2`). They were company pages and
     releases, state and federal records, and free trade or local press.
   - Every quote was re-fetched through Firecrawl, then Jina Reader, and matched as a word sequence (`rawcheck.csv`):
     30 of 36 passed.
   - **`build.py`** mints a new row only for a raw-verified quote from a non-licensed host. The new row's tier effect
     is never stronger than the old row's, nor than its source class allows. A partial match says which part it
     states.
2. **Adds validator V-60:** an evidence row may not cite a licensed publication. The 36 existing rows are
   grandfathered in `scripts/validate_debt_baseline.json` (`add_baseline.py`), so the debt can shrink but never grow.
   It comes with a test: a new licensed citation fails.

## Outcomes (unit: licensed-source evidence rows; 36)
| Result | Rows |
|-|-:|
| Answered by a public source stating the claim | 7 |
| Answered by a public source stating part of the claim | 5 |
| Held: quote not raw-verified | 6 |
| Held by the integrator: the quote does not bear on the claim (OMG Thermoforming parent link) | 1 |
| Held after the codex review: the quote does not support the claim, or names another entity or level | 10 |
| Held after the grok review: the quote never names the record's own entity | 7 |

12 new evidence rows, EVD-333016..EVD-333027, all at `supports_B` or below, plus one `supports_C` on a site address.
Each new row claims **only what its quote states** (its claim text is the quote), and it names the row it answers.
No record row changes. The 24 held rows stay answered by nothing; they remain in V-60's baseline as known debt.

## Review
Codex and grok each tried to refute the new rows (deep effort, read-only).
- The first build copied the old row's full claim text, so a quote had to back every detail. Codex flagged 19 of 29.
  New rows now claim only what the quote states, and 10 rows whose quote did not support the claim type at all are
  held. Examples: "joined forces" is not an acquisition, and a distributor listing is not ownership.
- Grok then flagged rows whose quote never names the record's own entity, for example a facility named without
  Newlight, and caps described without Mauer USA. Seven are held.
- Every hold and its reason is in `build.py` (`HOLD`) and `journal.txt`.

## Findings from the lanes (not applied)
- **Dakota Molding → Nott:** Nott's own release is dated 2023-05-05, not August 2023 as the old row says.
- **Mauer USA:** a Kentucky state record says "established 2008"; the old row says 2007.
- **Gregstrom:** its own 2025 post says rotomolding is moving from Woburn, MA to Bedford, NH. The record's location may
  be stale.
- **OMG Thermoforming, Arlington TX:** the parent's site lists Arlington only as an agent or distributor address, so
  the record may be stale.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0. The V-60 test and the pristine-tree test pass.
