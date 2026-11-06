# L1 archive top-up 1 — 2026-11-06

Controller-authorized sole archive_links.csv writer; branch agent/codex/archive-topup-1 from main49ddb5d.
First users: Atlas integrator and evidence auditors, at this PR review on2026-11-06. This is a provenance top-up,
not claim re-verification, a tier upgrade or evidence replacement. L11 owns all frozen weak-row repairs.

Acceptance: ≤500 new archive links; every included capture freshly readable, exact14digit timestamp and structural
original-page binding per V-59 (stricter on query values); canonical preserved quote occurs in order; zero failed
or skipped rows silently pass; pre-existing34 links immutable; receipt/proof hashes and full500-candidate dispositions
reconcile; builder idempotent; validate0 and two-family refute. No data write before fresh receipt/proof gate.

## Frozen inputs and method

Snapshot of the running local CDX stream: bank_sha256.txt identifies the exact bank bytes. candidates.csv freezes500
previously unarchived evidence IDs in43 distinct captures, ordered by capture groups with most eligible IDs first.
No inference from that convenience frame to support rates or archive completeness. All candidates reference
SUPPORTED rows of the immutable PIC18 audit; the binder cross-checks inputs/verdicts/quotes against current canonical
evidence. The34 archived IDs on main are excluded. before.csv is the pre-pass backup and this README is the pass journal.

Fresh requests use the already reviewed curl/browser-UA fetcher and calibrated contiguous normalized-token matcher.
Separate cache build/l1-topup-1-cache and copied page proofs build/l1-topup-1-proof prevent the continuing discovery
worker from overwriting this batch's witnesses. Replays use no Jina fallback. At least5seconds between distinct
captures; bounded transport retries and exponential429 backoff honoring numeric Retry-After. Every failed, redirected
or quote-absent candidate stays in outcomes.csv. Successful receipts are written only after the candidate file is
confirmed unchanged, and bind the final successful packet hash plus canonical quote hash. capture_checks.csv records
HTTP status, effective capture URL, fresh observation date, immutable proof path and text hash for every distinct capture.
Cached discovery alone never qualifies a row. Raw/proof bodies remain outside the shipped tree in ignored build/.

The normalized matcher is quote presence, not semantic claim support or rendered visibility. Existing evidence/tiers,
orgs/sites, registry links, derived fields and original frozen audit frames are unchanged. No EVD IDs minted, no creates,
dedupe/inclusion decisions or inclusion_log edits. No CRM, private, licensed or personal sources. Only existing cited
public own-site URLs and exact Wayback captures are used. Continuing bank candidates are not auto-applied.

## Named checks

~~~
python3 tasks/archive-topup-1-2026-11-06/selfcheck.py
python3 tasks/archive-topup-1-2026-11-06/check_archives.py
python3 tasks/archive-topup-1-2026-11-06/mutations.py
python3 tasks/archive-topup-1-2026-11-06/build.py
python3 tasks/archive-topup-1-2026-11-06/check.py
python3 scripts/validate.py
~~~

selfcheck.py: exact success and redirected query/timestamp, absent quote, transport-failure gate fixtures PASS.
check.py verifies the frozen500-ID universe, unique exact success/hold sets, all43 capture observations, canonical
quote binding, packet/receipt/proof hashes, prior-link preservation and current-table equality. build.py runs that
preflight before the existing shard_io/receipt-gated builder; unchanged re-runs add zero. mutations.py proves missing
receipt, forged packet URL and substituted proof hash fail before any canonical write. No scripts/ edits; scripts
pytest gate not triggered. No full archive completeness or new semantic support claim.

Results, fresh gate and independent verdicts are recorded below when terminal. No Done claim before both reviews.

## Fresh gate results

Topup: 486 new links / 42 captures; 14 held / 500 frozen candidates
Outcomes: {'VERIFIED': 486, 'FETCH_FAILED': 14}
Prior 34 links preserved; canonical 520 links; canonical quote/proof hashes PASS

Known-answer positive+4negatives PASS; 3real-builder no-write mutations PASS; builder second run0 additions; validate.py0 errors; native row-loss guard49ddb5d PASS.

Codex/OpenAI and Grok/xAI fresh top-up refutes pending. This remains draft until both approve.
