# Keyed CSV merge driver

Scope: local Git merge driver for Atlas CSVs; no data rows changed and no verification tiers affected. Uses the row-loss guard's key definitions. Known answers: disjoint appends and edits merge; conflicting edits, deletions and header changes fail; the actual #190 merge onto #172 reproduces its committed Ohio evidence shard.

Checks: `uv run --with pytest python -m pytest -q scripts/test_csv_merge_driver.py` passed (2 tests); `python3 scripts/validate.py` passed with 0 errors. `uv run --with pytest python -m pytest -q scripts/` passed (233 passed, 1 skipped, 45 subtests). A temporary Git repository merged divergent appends through the installed driver successfully. Git can bypass the driver for one-sided changes; the row-loss guard remains necessary. Independent refutations pending.

Codex clerk REFUTE: shared Git config referenced a removable linked worktree, and pipe-joined keys could collide. Fixed by resolving the active checkout at merge time and using tuple keys; regression tests cover linked-worktree removal, literal pipes and repeated inclusion rows. Re-review pending. The separate row-loss guard still uses ambiguous pipe-joined keys; reported to the controller.

Codex clerk re-review: APPROVE at 71128a7; independent reproductions confirm both fixes. Grok clerk review pending.

After fixes: `uv run --with pytest python -m pytest -q scripts/` passed (235 passed, 1 skipped, 45 subtests); `python3 scripts/validate.py` passed with 0 errors.

Grok clerk review: APPROVE at 907b290, no findings; independently verified the focused tests, key handling, worktree setup and historical replay.
