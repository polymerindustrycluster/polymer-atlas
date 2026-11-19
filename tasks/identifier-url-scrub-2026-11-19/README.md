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
  - each line is decoded first: JSON `\/` and `\uXXXX` escapes, and HTML entities;
  - every URL-shaped substring is then taken wherever it sits: with a scheme, scheme-relative, or a bare `host.tld/...`,
    and inside quotes, a Markdown link, `url=...`, braces or bold;
  - each substring is judged by `scripts/people_url.url_has_account`, the V-62 test, which also reads
    percent-encoding and ports. It is only judged when its percent-decoded text shows `u=`, `unid`, `~` or the UC host;
  - placeholders, fragments, sibling hosts and prose pass;
  - it prints path:line only. Unit test: `scripts/test_check_account_urls.py`.
- **`tasks/people-identifier-urls-2026-11-18/check.py`:**
  - its committed `manifest.csv` held 2 of these URLs, and `build.py` wrote it as a byte copy of the private persist
    manifest;
  - `common.redact` now applies the scrub-forward placeholders. `build.py` writes `redact(persist)`, so a replay
    restores no account URL, and its output equals the committed file byte for byte;
  - `check.py` requires the committed manifest to equal `redact(persist)` row for row. That is stricter than the old
    subset test: dropping a row or a wrong redaction now fails.

## Counts (unit: URL occurrences in tracked task and docs files)

| Form | Redacted |
|---|---|
| UC `/p/<shortname>` | 51 |
| `?unid=` / `&unid=` | 21 |
| `/~<account>` (the 3 from PR #407) | 3 |
| `?u=` | 0 |
| **Total** | **75 in 24 files** (`manifest.csv`: per-file sites and sha256 before and after) |

One of the 51 is a single-quoted URL in `tasks/people-settle-2-2026-11-06/lanes/uc58/check.py`. V-62's tokenizer does
not split on quotes, so the guard extracts URLs itself.

## Checks
- `python3 -I tasks/identifier-url-scrub-2026-11-19/scrub.py --selftest`: 9 cases. They include placeholders, `fisid_`
  and SCHEMA prose that must stay, and since review r1 a table pipe, a fragment, and a UC host inside another site's
  path.
- `python3 -I tasks/identifier-url-scrub-2026-11-19/scrub.py`: the dry run now reports 0 sites. `--apply` refuses to
  run again while `manifest.csv` exists.
- `python3 scripts/check_account_urls.py`: 0 lines across 4,720 files. With one URL planted in a tracked task file, it
  reports the line and exits 1.
- `python3 -m unittest discover -s scripts -p test_check_account_urls.py`: OK. It covers the four forms in plain,
  quoted, Markdown, percent-encoded, port, JSON-escaped, scheme-relative, `url=` and HTML-entity representations
  (review r1, both families), and the allowed forms.
- The controller's pre-push disclosure scan on this branch: 0 findings.
- `python3 scripts/run_task_checks.py --ref HEAD` for the four affected tasks that have a `check.py`:
  - `people-identifier-urls-2026-11-18` passes, and fails when one manifest row is deleted;
  - `people-settle-2-2026-11-06`, `people-settle-2026-11-06` and `people-titles-3-2026-11-06` fail with the same
    assertions as on main before this change. They depend on local fetch caches and quotes, so the failures predate
    this change.

## Not done
- **Git history is not rewritten**, as for #378. Earlier commits and PR refs keep the old text.
- **Bare account values outside a URL are not touched**, as for #378. Against the controller's private denylist, the
  only remaining matches are the 13 append-only `data/evidence_people.csv` rows.
- **`scripts/` is not guarded.** Its fixtures use synthetic accounts: `example.org` hosts, and UC-host strings split
  across two literals so that no line holds the form.
- **The scrub rewrites literal forms only.** An encoded account URL, for example percent-encoded, is caught by the
  guard and must be redacted by hand.
- **`tasks/people-settle-2-2026-11-06/lanes/uc58/check.py`**, a lane checker that `run_task_checks.py` does not run,
  builds a local-cache key from the URL on its line 73. That URL is now redacted, so the lane check can no longer find
  its cache entry. It already needed the private fetch cache to run at all.
