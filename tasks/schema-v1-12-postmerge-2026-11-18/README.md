# Schema v1.12: post-merge review fixes (2026-11-18)

PR #250 (schema v1.12) merged on 2026-11-09 after a claude-code + grok review, with no codex pass. A codex deep
review of the merged change (`git diff 1fe26374^1 1fe26374`) ran on 2026-11-18 and returned SHIP-WITH-FIXES with four
findings. This folder applies all four.

| # | Finding (codex) | Fix |
|-|-|-|
| 1 | Medium. EVT-000023 Silicone Expo USA carried `materials-week-usa`. Materials Week USA is the umbrella of several co-located expos (Silicone Expo, Specialty Polymers World, Gaskets & Seals and others), and §4.12.1 keeps co-located series distinct, so the umbrella slug cannot identify one component. The crosswalk row itself said "reviewer to confirm umbrella vs series". | `fix.py` clears the slug in `data/events.csv` and in the crosswalk input (`tasks/schema-v1-12/crosswalk.csv`), so a re-run of `add_crosswalk.py` cannot bring it back. The conferences repo has no Silicone Expo slug yet. No participation row used the mapping. |
| 2 | Low. A row missing the whole last column passed V-61: `DictReader` gives `None`, read as empty. | `validate.py` V-61 rejects a row with fewer or more fields than the header; an explicitly empty last cell still passes. agy's review added the wide case: `DictReader` files surplus cells under a `None` key, so a row one field too wide (even with a malformed slug in it) had passed. New test `test_v61_row_width_must_match_header` (short by 1, short by 2, wide by 1), which fails on the pre-fix validator. |
| 3 | Low. `tasks/schema-v1-12/BRIEF.md` still allowed brochure "companies attending" lines as attendee evidence, against the 2026-11-09 ruling. | The brief carries a superseded-in-part note pointing at §4.12.2. |
| 4 | Low. SCHEMA §4.12.1 said V-60 for the slug rule (V-60 is the licensed-source rule). | Reads V-61, and lists every V-61 condition. |

Codex also ran 46 targeted and 24,621 generated slug cases with no V-61 mismatch, and found all 69 mapped slugs in
the conferences repo. It noted that the validator cannot see person data in `role_detail` or brochure provenance for
any role; that is not new in v1.12 and is not changed here.

**Second family (agy, Gemini 4 Hydrogen XHigh, 2026-11-18): SHIP-WITH-FIXES.** It agreed clearing the slug is right
(the column is nullable; an inner join on it drops EVT-000023 until the conferences repo has a Silicone Expo series).
Applied: the wide-row hole (above); the test now edits rows with the csv module, not by splitting on newlines; `fix.py`
reports "already applied" on a re-run instead of failing; the QUEUE line uses the `in-pr:<link>` form.

Checks: `python3 scripts/validate.py` exits 0. `python3 -m unittest scripts.test_validate -k v61` passes 5 tests.
`python3 -m unittest discover -s tasks/schema-v1-12 -p "test_*.py"` passes. A truncated `events.csv` row now
fails with exactly one error, the new V-61 message.
