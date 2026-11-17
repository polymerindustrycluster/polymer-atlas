# Archive top-up 2 — 2026-11-16

Claim: atlas-w16-archive, controller thr_9i2c6byhcz, branch agent/codex/archive-topup-2.
First users: Atlas integrator and evidence auditors at draft PR review; non-use is a finding at that review.

Acceptance: first 1,500 distinct source URLs ordered by evidence_id, from unarchived own_site evidence on PIC-18 sites or their organizations. The frozen frame contains 3,948 evidence rows. Six seconds minimum between network requests, serial SPN, exponential 429 backoff honoring numeric Retry-After, three-hour persisted deadline. Only exact readable HTTP-200 Wayback captures containing the canonical preserved quote are admitted; no archive link changes a claim or tier. Existing archive rows remain byte-equivalent by keyed row. No new evidence IDs or tier changes.

The existing top-up 1 method supplies the transport/text extractor, quote extraction and calibrated normalized-token matcher, page and timestamp comparison, and immutable proof restoration. Availability is discovery only. A failed or quote-absent existing capture triggers SPN, followed by CDX and replay. Query-string SPN remains held under the prior method's route restriction. No live semantic support judgment is claimed. Evidence lacking a preserved quote cannot receive a link.

`fetch.py` resumes from URL-keyed JSON results under controller storage `persist/archive-topup-2/`; `state.json` preserves the original deadline and `journal.jsonl` records completed URLs. Proof names are sha256(archive_ref).txt. The journal and proof/result bodies persist outside the worktree. `check.py` reads that directory, independently rebuilds the input frame, reconciles every completed URL and evidence disposition, and checks quote, exact replay, date and proof hashes. `build.py` gates application through that check and appends through shard_io. `restore_proofs.py` reuses top-up 1's hash-identical restoration procedure. Only data/archive_links.csv is an allowed canonical target.

| Proposal | Disposition | Settling fact |
| --- | --- | --- |
| Exact capture with preserved quote and proof | applied by builder | Recorded replay, quote and hash checks pass |
| Missing quote, failed transport, redirected capture or quote absent | held | A freshly readable exact capture with the preserved quote |
| Query-string SPN route | held | Verified encoded submission route |
| URLs unfinished at deadline | held | A later explicitly authorized continuation |

Named checks: `python3 tasks/archive-topup-2-2026-11-16/check.py`; `python3 tasks/archive-topup-2-2026-11-16/mutations.py` (three injected defects must fail); build twice (second run adds zero); repository validation, row-loss guard and vocabulary export check. No scripts/ files changed. Independent family reviews remain controller-owned; draft PR only.

See the terminal result below. Counts distinguish archived URLs / tried URLs from admitted evidence links / worked evidence rows. Machine results: counts.json and outcomes.csv. No complete-coverage inference.

Proposed follow-ups: none outside the held cases above.

## Corrected frame and transport

The source-reference URL parser skips 9 eligible evidence rows as **not a URL** (of 3958 eligible evidence rows before this filter). Every selected reference parses as http or https with a hostname and contains no whitespace. Re-derived frame: 3948 evidence rows, 1,500 distinct URLs. Failed-run artifacts remain in persist/archive-topup-2/failed-run-1/.

All subprocess response bytes are decoded as UTF-8 with errors=replace. Per-item exceptions receive an ITEM_ERROR terminal disposition and do not kill the loop; deadline exhaustion stops the run. The pilot uses ten quote-bearing URLs from the corrected frame, separately from the full-run journal and deadline.

Pilot: 10/10 URLs have terminal journal rows; 25 evidence archive links admitted. Independent proof/quote gate passed for the pilot. URL parser, malformed-byte response and injected item-failure/continuation checks passed. No pilot links applied to data. Full run starts with its own fresh three-hour deadline.

## Controller-authorized parallel resume

2026-11-16: after the pause, 29 terminal URL results were retained. Four subprocess workers own disjoint round-robin slices of the unchanged frame; each has its own transport cache. Shared journal appends use an exclusive file lock. The supervisor rebuilds the journal from durable results before workers start and after all exit. Resume skips all durable results. New captures are requested at least five seconds apart per worker; all HTTP 429 responses trigger at least a minute of backoff (numeric Retry-After honored). New deadline: 2026-11-16 16:36:31 Pacific, 135 minutes after restart setup. Existing capture admission is unchanged. `parallel_fetch.py` is the resumable background entry point; `state.json` retains the authorized deadline. No automatic application or publishing; finalization follows controller wake-up.

## Terminal result

The run attempted 1,251 of 1,500 distinct source URLs for previously unarchived PIC-18 own-site evidence. 716 attempted URLs (57.2%) yielded 711 distinct Wayback snapshots. They support 2,188 archive-link additions across 3,613 evidence rows worked. 249 frame URLs were unfinished at the deadline.

| Terminal journal status | Attempted source URLs |
| --- | ---: |
| `CDX_FETCH_FAILED_000` | 19 |
| `FOUND` | 838 |
| `NO_CAPTURE` | 4 |
| `NO_EXACT_CAPTURE` | 2 |
| `SPN_FETCH_FAILED_000` | 363 |
| `SPN_FETCH_FAILED_520` | 12 |
| `SPN_FETCH_FAILED_523` | 4 |
| `SPN_QUERY_HOLD` | 9 |

| Admission hold | Worked evidence rows |
| --- | ---: |
| `CDX_FETCH_FAILED_000` | 16 |
| `FETCH_FAILED_000` | 735 |
| `FETCH_FAILED_200` | 61 |
| `FETCH_FAILED_404` | 1 |
| `NO_CAPTURE` | 4 |
| `NO_EXACT_CAPTURE` | 5 |
| `NO_PRESERVED_QUOTE` | 342 |
| `QUOTE_ABSENT` | 183 |
| `REPLAY_REDIRECT_HOLD` | 3 |
| `SPN_FETCH_FAILED_000` | 62 |
| `SPN_FETCH_FAILED_520` | 8 |
| `SPN_FETCH_FAILED_523` | 1 |
| `SPN_QUERY_HOLD` | 4 |

Journal statuses describe the final Wayback route outcome and can differ from the evidence admission decision. Failed Save Page Now requests and replay failures describe availability. Admission requires an exact replay and the preserved quote.

The proof and journal check, three injected defects, idempotent rebuild, repository validator, row-loss guard and vocabulary export check passed locally. The frozen frame is rebuilt from `be2e608`. The builder checks each admitted source and quote against the current canonical evidence before application. Independent family reviews and live semantic re-verification are pending or outside this pass.
