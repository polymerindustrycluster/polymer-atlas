# Robots off, bot checks, LinkedIn company pages: fetcher change (2026-11-24 owner rulings)

Non-data PR. Changes `scripts/site_corpus.py` only (plus its unit tests, `docs/ACQUISITION.md`, `DECISIONS.md`, `tasks/QUEUE.md`). No file under `data/`.

## What changed

- **robots.txt is read, not obeyed.** Crawl-delay and the per-host clock stay. Each receipt gets `robots_disallowed`: `yes` if any redirect hop's URL was disallowed, else `unreadable` if any hop's robots.txt could not be read, else `no`. Receipts of robots.txt itself carry an empty value. Receipts cached before the change read back as `not_recorded`. An unreadable robots.txt is no longer Disallow all.
- **Stale receipts.** A cached `ROBOTS_BLOCKED` or `DOMAIN_BLOCKED` receipt is a cache miss and is refetched. A cached `FETCH_FAILED` receipt that was really a bot-check page is not refetched: it keeps answering until its cache entry is removed.
- **Bot checks.** A 200, 403, 503 or 999 response that `challenged()` calls a bot-check page (title or wall text, or a widget marker on a refusal code or a nearly empty page) is retried once in `Corpus.browser`: a fresh Chrome (`channel='chrome'`, headless, new context, no profile, no cookies), under the same host clock and slot as `request()`. It waits up to 30 s for the page's own check, and from the 4th second clicks one plain "verify you are human" button, checkbox or label (in a frame too, and a Turnstile frame by position). It never solves a puzzle. Bytes the browser renders get the same hash receipt (`route: browser`). If the page is still a bot check, the receipt is `BOT_CHECK_MANUAL` and the URL joins `manual-bot-check.csv` in the cache folder. If Playwright or Chrome is missing, the old path runs and the receipt's `error` says `PLAYWRIGHT_UNAVAILABLE` or `CHROME_UNAVAILABLE`; nothing passes silently. 429 and robots.txt never go to the browser.
- **LinkedIn.** `/company/<slug>` and `/showcase/<slug>`, optionally `/about`, are fetched logged out. Everything else on LinkedIn (`/in/`, `/pub/`, `/company/<slug>/people`, jobs, `lnkd.in`, a Jina-wrapped URL) is refused as `DOMAIN_BLOCKED`. A redirect to `/authwall`, `/login`, `/uas/` or `/checkpoint` is `SIGNIN_WALL`. A non-LinkedIn URL that redirects to LinkedIn is still refused. LinkedIn is never read through the Jina proxy. `linkedin_url()` keeps its meaning (any LinkedIn host); `scripts/check_evidence_binding.py` still refuses LinkedIn as an evidence source, which is the separate evidence-route PR.

## Named check

`python3 tasks/robots-off-fetch-2026-11-25/check.py scripts` (mocked transport), then
`uv run --with playwright python3 tasks/robots-off-fetch-2026-11-25/check.py scripts --real-browser` (real Chrome against a local fixture server; run with the sandbox off).
`python3 -m unittest discover -s scripts -p 'test_site_corpus.py'` is the unit suite (no test launches Chrome).

To show the cases fail on the old rule, export `origin/main`'s `scripts/` (`git archive origin/main scripts | tar -x -C DIR`) and run `check.py DIR/scripts`.
The kept-line case (profiles still refuse) cannot fail on old code, which refused all of LinkedIn; a mutation case removes the guard from the new code and shows that case fail.
