# Identifier-URL scrub of historical task files (2026-11-18)

Owner rulings 2026-11-18, items 1 and 1b (`tasks/owner-rulings-2026-11-18/README.md`) treat a university profile URL that
carries a personal account (`?u=<id>`, or a home directory `/~<acct>`) as a personal identifier. For task and docs files
already on main, the owner chose **scrub forward**: redact the tip, and do not rewrite history.

## What changed
- Scope: every tracked file under `tasks/` and `docs/` at base `099497f`. `data/` is out of scope: the people rows are
  remediated by their own lane, with validator V-62.
- Rewrite rule (`scrub.py`):
  - `?u=<value>` and `&u=<value>` become `?u=<id>`;
  - `/~<account>` becomes `/~<acct>`;
  - the rest of the line is unchanged.
- Kept on purpose: 2 `?u=` occurrences on `*.widen.net`, a document-sharing host whose `u=` is a share token, not a
  person (in `tasks/census-geocode-2026-11-16/baseline.csv`).

## Counts (unit: URL occurrences in tracked task and docs files)

| | Count |
|---|---|
| Occurrences matched (excluding widen.net) | 107: `?u=` 46, `/~` 61 |
| Occurrences redacted | 107 |
| Files changed | 43 |
| Lines changed | 85 |

Each file, with its sha256 before and after, is listed in `manifest.csv`.

## Check
`python3 -I tasks/identifier-url-scrub-2026-11-18/scrub.py` (the dry run) must report `0 sites` once this lands.

Independent recount, a `git grep` with the pre-push scan's pattern over `tasks/` and `docs/`:
- 2 hits remain, both widen.net;
- the added lines carry 107 placeholders (46 `?u=<id>`, 61 `/~<acct>`).

## Frozen hashes
`tasks/blind-audit-10-2026-11-14/freeze.json` pins the sha256 of `blind_a.csv` and `blind_b.csv`.
- Before this scrub, both files hashed to the pinned value (`3d7a3a12…`; see `manifest.csv`, column `sha256_before`).
- After it, they do not.
- `freeze.json` is a historical record and is left as it is. The frozen bytes can still be checked with
  `git show 099497f:<path> | shasum -a 256`.

## Not done
- **Git history is not rewritten.** Earlier commits and PR refs still hold the old text; the owner chose this over a
  force-push.
- **Text that names a person without a URL is not touched.**
