# Identifier-URL scrub of historical task files (2026-11-18)

Owner rulings 2026-11-18, items 1 and 1b (`tasks/owner-rulings-2026-11-18/README.md`), treat a profile URL that carries a
personal account (`?u=<id>`, or a home directory `/~<acct>`) as a personal identifier. For task and docs files already on
main, the owner chose **scrub forward**: redact the tip, and do not rewrite history.

## What changed
- **Scope:** every tracked file under `tasks/` and `docs/` at base `099497f`, this folder included. `data/` is out of
  scope: the people rows are remediated by their own lane, with validator V-62.
- **Rewrite rule** (`scrub.py`), applied to every URL that carries an account:
  - `?u=<value>` becomes `?u=<id>`, and `&u=<value>` becomes `&u=<id>`; the separator is kept;
  - `/~<account>` becomes `/~<acct>`;
  - every other bounded occurrence of the same value inside that URL becomes `<acct>` or `<id>` (the 9 cases are
    filenames such as `name-<acct>.html`);
  - text outside the URL is unchanged.
- **No host is exempt.** The two `*.widen.net` PDF links in `tasks/census-geocode-2026-11-16/baseline.csv` are redacted
  too. Codex showed that each PDF is byte-identical without its `u` value, so the value adds nothing.
- `tasks/blind-audit-10-2026-11-14/check.py` now checks that audit's freeze pins at the pre-scrub commit `099497f` and
  the scrubbed tip against `manifest.csv`. Otherwise its pinned `blind_a.csv` and `blind_b.csv` would fail. The pins and
  `freeze.json` are unchanged.

## Counts (unit: URL occurrences in tracked task and docs files)

| | Count |
|---|---|
| Account URLs redacted | 109: `?u=`/`&u=` 48 (2 of them widen.net), `/~` 61 |
| Repeats of an account elsewhere in the same URL | 9 |
| Files changed (not counting this folder or the blind-audit-10 checker) | 44 |
| Lines changed | 87 |

`manifest.csv` lists each file with its sites, its repeats, and its sha256 before and after.

## Checks
- `python3 -I tasks/identifier-url-scrub-2026-11-18/scrub.py` (the dry run) reports 0 sites. `--apply` refuses to run
  again while `manifest.csv` exists.
- Independent check against `099497f`, over every manifest file:
  - the text outside URLs is identical;
  - each JSON file parses, and each CSV keeps its per-record field counts;
  - no account value from a base URL appears in a URL of the tip, apart from one expected match. `/~<acct>` on one host
    and the public lab hostname `qwang.engr.tamu.edu` in `people-titles-3-2026-11-06/expected.json` share a value. A lab
    hostname is a public lab URL and is not an account form under the ruling.
- `python3 tasks/blind-audit-10-2026-11-14/check.py` passes. With a planted byte change in both blind files, it fails with
  "differs from its recorded scrub".

## Not done
- **Git history is not rewritten.** Earlier commits and PR refs still hold the old text; the owner chose this over a
  force-push.
- **Text that names a person without a URL is not touched.**
- **Proposed follow-up:** on main, 2 organization rows and 2 site rows in `data/` still cite widen.net links with
  their `u` values. A data PR could drop them. The 3 evidence rows that cite them are append-only and stay as they are.
