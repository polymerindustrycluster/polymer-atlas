# Robots off, LinkedIn company pages, privacy exclusion: fetcher change (owner rulings 2026-11-24 and 2026-11-25)

Non-data PR. Changes `scripts/site_corpus.py` (plus its unit tests, `docs/ACQUISITION.md`, `DECISIONS.md`, `tasks/QUEUE.md`). No file under `data/`.
The Chrome retry for bot checks was built, refuted twice, and taken out by the owner's "Split it" (2026-11-25 06:08). It waits for its own PR.

## What this PR does

- **robots.txt is read, not obeyed.** Crawl-delay and the per-host clock stay. Each receipt gets `robots_disallowed`: `yes` if any redirect hop's URL was disallowed, else `unreadable` if any hop's robots.txt could not be read, else `no`. robots.txt receipts carry an empty value; receipts cached before the change read back as `not_recorded`. An unreadable robots.txt is no longer Disallow all.
- **Stale receipts.** A cached `ROBOTS_BLOCKED` or `DOMAIN_BLOCKED` receipt is a cache miss and is refetched.
- **Bot checks go to a person.** A 200, 403, 503 or 999 response that `challenged()` calls a bot-check page (title or wall text, or a widget marker on a refusal code or a nearly empty page) is receipted `BOT_CHECK_MANUAL`, never `ok`, and its URL goes to `manual-bot-check.csv` in the cache folder. Nothing goes to Jina after a bot check.
- **Privacy exclusion before any body is stored.** `save()` drops the body of a staff-directory path (`/team`, `/staff`, `/our-team` ...) or a form-only page (fewer than 80 words outside forms), at every status. An `ok` page becomes `CONTACT_FORM_OR_STAFF_DIRECTORY`; other statuses keep theirs with an empty body. An excluded page is never retried through Jina. Same tests as the 2026-11-16 crawl. Side effect: `rawcheck` on such a page returns `unfetchable`.
- **LinkedIn.** `/company/<slug>` and `/showcase/<slug>`, optionally `/about`, are fetched logged out (curl with `-q`, no cookie jar, no header). Everything else on LinkedIn (`/in/`, `/pub/`, `/company/<slug>/people`, jobs, `lnkd.in`, a Jina-wrapped URL) is refused as `DOMAIN_BLOCKED` at the first URL and at every redirect hop, including a hop from an own site. A redirect to `/authwall`, `/login`, `/uas/` or `/checkpoint` is `SIGNIN_WALL`. LinkedIn never goes through Jina. `linkedin_url()` keeps its meaning, so `check_evidence_binding.py` still refuses LinkedIn as an evidence source (the evidence route is a separate PR).

## Named check

`python3 tasks/robots-off-fetch-2026-11-25/check.py scripts` (mocked transport; every case asserts behaviour) and
`python3 -m unittest discover -s scripts -p 'test_site_corpus.py'`.
To show the cases fail on an older rule, export its `scripts/` (`git archive REF scripts | tar -x -C DIR`) and run `check.py DIR/scripts`.
The kept-line case (profiles refuse at every hop) cannot fail on `origin/main`, which refused all of LinkedIn at the first URL only; a mutation case removes the guard and shows it fail.

## Evidence for the follow-up browser PR (not built here)

Measured 2026-11-25 on PR #560 head 5dd966d9 (`Corpus.browser`, since removed), outside the repo, owner-ruled "click through bot checks":

- **Headless real Chrome (Playwright `channel='chrome'`, `headless=True`) does not clear the check.** 3 of 3 LinkedIn company pages tried (Avient, Day-Glo, Vibrantz) came back as Cloudflare's interactive "Just a moment..." challenge (`__cf_chl_rt_tk` in the URL), 403, about 40 s each, all `BOT_CHECK_MANUAL`. curl got the same Cloudflare 403.
- **Headed real Chrome passes with no click.** The same Avient URL, headed: HTTP 200, title "Avient Corporation | LinkedIn", 400 KB, "Company size" shown. All 127 LinkedIn company pages (PIC-18 owners with `linkedin_url`) were then fetched headed: 122 page, 1 sign-in wall, 4 failed, 0 bot checks. So `headless=True` was the yield limit, not the click logic. (Unreviewed captures kept in `persist/pic18-linkedin-2026-11-25-headed-unreviewed/` and `persist/pic18-robots-off-2026-11-25-headed-unreviewed/`; to be rerun on main.)
- A logged-out company page carries named employees and post authors (`data-test-id` blocks `employees-at`, `updates`, plus JSON-LD graph items); a LinkedIn capture must strip them before storage.
- Round-2 findings the browser PR must meet: Playwright routes only the first URL of an HTTP redirect, so hops inside Chrome escape destination, pacing and robots checks; cookies must be prevented, not detected; no coordinate click.
