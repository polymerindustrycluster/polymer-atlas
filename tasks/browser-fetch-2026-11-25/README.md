# Headed Chrome retry for bot checks, HTTP/1.1 transport fallback (owner rulings 2026-11-24 and 2026-11-25)

Non-data PR. Changes `scripts/site_corpus.py` (plus its unit tests, `docs/ACQUISITION.md`, `DECISIONS.md`). No file under `data/`.
Follows #560, which shipped robots off, LinkedIn company pages, privacy exclusion and `BOT_CHECK_MANUAL` without a browser (owner ruling 2026-11-25 06:08, "Split it").

**Headed Chrome opens a window on this Mac** for every bot-check retry (and every real-Chrome case of the check). Windows appear and close on their own; do not click in them. Headless Chrome is held by Cloudflare (3 of 3 LinkedIn pages), headed passes without a click, so the browser is headed on purpose.

## What it does

- **One browser retry.** A page the curl path calls a bot check (`challenged()`) is visited once by `Corpus.browser`: local Playwright, real Chrome (`channel='chrome'`), headed, a fresh non-persistent context, no profile. No click and no typing anywhere: the code has no click path. It waits up to 30 s for the page's own check and stops at once if the navigation itself fails (certificate, DNS). Playwright or Chrome missing: the receipt says so in `error`; a bot check stays `BOT_CHECK_MANUAL` on the manual list, a TLS failure stays `FETCH_FAILED`.
- **Every request is checked before it is sent**, redirects included. `Fetch.enable` on the CDP session pauses each request at the request stage, and each HTTP redirect hop is a new paused request (Playwright route handlers do not see them; this was the round-2 finding). For each document: only documents load (scripts, images, XHR, fonts are failed at the request stage); a refused LinkedIn URL (`/in/`, `/pub/`, `/company/<slug>/people`, a hop from an own site), a staff-directory path, or another host reached other than by an HTTP redirect is failed with `BlockedByClient` and the receipt says why (`DOMAIN_BLOCKED`, `SIGNIN_WALL`, `CONTACT_FORM_OR_STAFF_DIRECTORY`, `CROSS_HOST_NAVIGATION`).
- **Robots and pacing for every hop host.** Each allowed document hop reads that host's robots.txt (in memory, as on main), records its state, and waits that host's clock with its own Crawl-delay (`Corpus.wait_host`). The receipt's `robots_disallowed` is yes, unreadable or no across the curl hops and every browser hop and the final URL.
- **No cookie is ever sent.** Set-Cookie is stripped from every response at the response stage, the cookie jar is emptied before every request, and `document.cookie` is a no-op. The check serves a planted fixture that sets cookies in a redirect, a response and JavaScript, and its server never receives a Cookie header; a control run shows an unprotected Chrome does send one.
- **What is stored.** Only an `ok` main document (final HTTP 200, not a bot check) is stored, with the usual hash receipt (`route: browser`). Refused hops, bot-check pages and error pages are never stored at any status (a bot check or error page saves an empty body). Excluded destinations stay excluded by `save()` as on main. A LinkedIn page is reduced to the allowlisted JSON extract before storage, as on main.
- **Transport fallback.** A curl exit 35 (handshake), 60 (certificate chain) or 92 (HTTP/2 stream) on a page or its robots.txt gets one retry over `--http1.1`; certificate verification stays on (the check asserts no `-k`). A handshake or chain failure that survives goes to the browser. 

## Measured on real sites (2026-11-25, this head)

- 3 of 3 LinkedIn company pages (Avient, Day-Glo, Vibrantz) read: curl got Cloudflare's 403, the headed retry returned the page, the receipt is the allowlisted extract (robots.txt says Disallow for that path, so `robots_disallowed` is yes). 3.7 to 5.4 s each.
- The own-site failures counted on main did not mostly yield. `www.may-lin.com` and `premieraerosol.com` (curl 60): Chrome also refuses them (`ERR_CERT_COMMON_NAME_INVALID`), the host name is not on the certificate, so `FETCH_FAILED` is right. `molding-dynamics.net` (curl 35): Chrome fails too (`ERR_SSL_PROTOCOL_ERROR`). `mercurymachine.com` and `www.bmsburns.com` (curl 92 in the main run): with the declared crawler user agent curl now gets exit 52 (empty reply) over HTTP/1.1 as well, while a bare `curl` without that user agent gets 200: those sites drop the declared agent, which no transport retry changes. Count these as results, not as yield of the fallback.

## Named check

`python3 tasks/browser-fetch-2026-11-25/check.py scripts` (mocked transport and browser: every earlier case of #560 plus the browser and fallback cases) and
`uv run --with playwright python3 tasks/browser-fetch-2026-11-25/check.py scripts --real-browser` (real headed Chrome against a local fixture server, sandbox off; windows open),
`python3 -m unittest discover -s scripts -p 'test_site_corpus.py'` (no unit test launches Chrome).
To show the cases fail on the old browser path or on main, export that ref's `scripts/` (`git archive REF scripts | tar -x -C DIR`) and run `check.py DIR/scripts [--real-browser]`: on `5dd966d9` (the refuted browser path) the real-Chrome cases fail on behaviour (a script and an image requested, the staff-directory hop fetched, no Crawl-delay gap, cookies sent, a button clicked); on `4e1cae04` (main, no browser) the browser cases fail.
