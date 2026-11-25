# HTTP/1.1 transport fallback; rows for the two bare-curl runs (2026-11-25)

Non-data PR. Changes `scripts/site_corpus.py` only (plus `docs/ACQUISITION.md`, `DECISIONS.md`, `tasks/QUEUE.md`). No file under `data/`. Split out of the browser PR (#564) by the owner's 09:33 ruling; it contains no browser code.

- **Fallback.** `Corpus.hop` is one transport step: curl, and if curl exits 35 (TLS handshake), 60 (certificate chain) or 92 (HTTP/2 stream), whatever HTTP status it had read, one more request over `--http1.1`. The retry's response, redirects included, is processed normally. It is used for every page hop and for robots.txt. Certificate verification stays on (the check asserts no `-k`). A timeout or any other exit is not retried.
- **Docs.** Two experiment rows in `docs/ACQUISITION.md` name `persist/pic18-robots-off-main-2026-11-25` (12 of 117 organizations readable) and `persist/pic18-linkedin-main-2026-11-25` (0 of 127), with units, and say LinkedIn now runs through Muse with raw evidence on the NAS (owner, 2026-11-25). A DECISIONS entry records the fallback and the two runs.

Named check: `python3 tasks/fetch-fallback-2026-11-25/check.py scripts` (6 cases, mocked curl) and `python3 -m unittest discover -s scripts -p 'test_site_corpus.py'`. On a copy of `origin/main` (`git archive origin/main scripts`) all 6 cases fail.
