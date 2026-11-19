# Identifier-URL scrub 2 and a CI guard for tasks/ and docs/ (2026-11-19)

Owner rulings 2026-11-18 items 1 and 1b, and 2026-11-18b item 3, treat four URL forms as personal account identifiers:

- `?u=<id>`;
- `/~<account>`;
- `?unid=<id>`;
- `researchdirectory.uc.edu/p/<shortname>`.

V-62 enforces this on people rows. PR #378 scrubbed task and docs files forward, but only for the first two forms,
because the 2026-11-18b forms were ruled after its frame was built.

The 2026-11-19 repo audit found two gaps:
- 71 occurrences of the 2026-11-18b forms were still in tasks/;
- 3 new `/~` URLs had reached main in `tasks/bandb-people-2026-11-19/verified.csv` (PR #407, merged 2026-11-19). The
  harness that pushed it does not run this clone's pre-push disclosure scan, and CI had no such check.

The owner chose (2026-11-19, repo-audit question) to scrub forward as #378 did, and to add a CI check that fails if
tasks/ holds any such URL. docs/ is guarded too, matching #378's scope.

## What changed
- **Scrub** (`scrub.py`, extending `tasks/identifier-url-scrub-2026-11-18/scrub.py` to the 2026-11-18b forms):
  - every tracked file under `tasks/` and `docs/` at base `63ebeb66`;
  - `?unid=<value>` becomes `?unid=<id>`, `researchdirectory.uc.edu/p/<value>` becomes
    `researchdirectory.uc.edu/p/<shortname>`, and `?u=` / `/~` get #378's placeholders;
  - text outside the URL is unchanged;
  - `data/` is out of scope: V-62 covers people rows, and the 21 identifier-bearing `evidence_people` rows are
    append-only by ruling.
- **Guard** (`scripts/check_account_urls.py`, a new step in `.github/workflows/validate.yml`):
  - it fails on any line under `tasks/` or `docs/` holding one of the four forms;
  - each candidate token is judged by `scripts/people_url.url_has_account`, the V-62 test;
  - tokens are split on quotes, backticks, brackets and pipes as well, so a URL in a Python string or a Markdown link
    is still read;
  - placeholders pass;
  - it prints path:line only. Unit test: `scripts/test_check_account_urls.py`.
- **`tasks/people-identifier-urls-2026-11-18/check.py`:**
  - two of its committed `manifest.csv` URLs are scrubbed, so it now compares them with its private persist
    manifest after the same redaction;
  - with a deliberately wrong redaction it fails, as before.

## Counts (unit: URL occurrences in tracked task and docs files)

| Form | Redacted |
|---|---|
| UC `/p/<shortname>` | 51 |
| `?unid=` / `&unid=` | 21 |
| `/~<account>` (the 3 from PR #407) | 3 |
| `?u=` | 0 |
| **Total** | **75 in 24 files** (`manifest.csv`: per-file sites and sha256 before and after) |

One of the 51 is a single-quoted URL in `tasks/people-settle-2-2026-11-06/lanes/uc58/check.py`. V-62's tokenizer does
not split on quotes, so the guard uses a wider one.

## Checks
- `python3 -I tasks/identifier-url-scrub-2026-11-19/scrub.py --selftest`: 6 cases, including placeholders, `fisid_`
  and SCHEMA prose that must stay.
- `python3 -I tasks/identifier-url-scrub-2026-11-19/scrub.py`: the dry run now reports 0 sites. `--apply` refuses to
  run again while `manifest.csv` exists.
- `python3 scripts/check_account_urls.py`: 0 lines across 4,720 files. With one URL planted in a tracked task file, it
  reports the line and exits 1.
- `python3 -m unittest scripts.test_check_account_urls`: OK.
- The controller's pre-push disclosure scan on this branch: 0 findings.
- `python3 scripts/run_task_checks.py --ref HEAD` for the four affected tasks that have a `check.py`:
  - `people-identifier-urls-2026-11-18` passes;
  - `people-settle-2-2026-11-06`, `people-settle-2026-11-06` and `people-titles-3-2026-11-06` fail with the same
    assertions as on main before this change. They depend on local fetch caches and quotes, so the failures predate
    this change.

## Not done
- **Git history is not rewritten**, as for #378. Earlier commits and PR refs keep the old text.
- **Bare account values outside a URL are not touched**, as for #378. Against the controller's private denylist, the
  only remaining matches are the 13 append-only `data/evidence_people.csv` rows.
- **`scripts/` is not guarded.** Test fixtures there use synthetic accounts on non-`.edu` hosts.
- **`tasks/people-settle-2-2026-11-06/lanes/uc58/check.py`**, a lane checker that `run_task_checks.py` does not run,
  builds a local-cache key from the URL on its line 73. That URL is now redacted, so the lane check can no longer find
  its cache entry. It already needed the private fetch cache to run at all.
