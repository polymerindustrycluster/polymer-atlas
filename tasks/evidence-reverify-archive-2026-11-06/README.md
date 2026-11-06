# PIC-18 preserved-quote re-verification and archive links — 2026-11-06

L1 (`atlas-L1-reverify-archive`), controller-claimed; draft PR #137. Frame pinned to bd57a08: every OH site whose
physical county, stripping a trailing ` County`, is in `scripts/regions.py` PIC18, plus those sites' parent organizations,
regardless of HQ. No status/tier filter. Exactly 3,683 own_site evidence rows / 1,120 distinct cited references;
4 references (8 rows) are not bare URLs. This matches the controller's baseline. HQ-only and HQ-plus-footprint
alternatives are excluded. First users: Atlas integrator and evidence auditors, from PR review on 2026-11-06.

## Results (unit: evidence rows)

This measures **preserved quote presence**, not the semantic truth of a claim or site attribution. SUPPORTED requires
contiguous normalized words, using the unchanged `words`, `on_page`, and `wilson` functions from the calibrated
2026-11-03 audit. NOT_SUPPORTED means the preserved quote is absent from the readable returned text, not that the
underlying claim is false. PARTIAL is a no-preserved-quote/ambiguous-quote hold; it does not assert semantic partial
support. WRONG_PAGE holds a redirect to another host/path/query, even if the destination might be a valid successor.
FETCH_FAILED is transport, recognized wall, uncertain decoding, or unavailable source identity; never evidence of absence.
All unresolved records have lane posture STILL_UNCERTAIN; there are no organization REJECT/status decisions.

The 2026-11-03 audit's 142/191 (74%, Wilson 68–80%) assessed claim semantics on a different sampled frame, then checked
its selected quotes. The table below puts it beside the new quote-presence rates for context. These different
estimands do **not** demonstrate an improvement in semantic support. All-row denominators count availability/no-quote
holds against support. Readable denominators exclude FETCH_FAILED; redirect holds still count against support.
Wilson intervals are descriptive binomial reference intervals on a full frame, not sampling uncertainty.

<!-- RESULTS BEGIN -->
PIC18 evidence rows: 3683 distinct cited refs: 1120
Judgments: {'SUPPORTED': 3261, 'PARTIAL': 34, 'NOT_SUPPORTED': 75, 'FETCH_FAILED': 264, 'WRONG_PAGE': 49}
Repair/availability leads: 422 / 3683
| Claim | Quote supported / all rows | Rate (Wilson 95% CI) | Supported / readable | Rate (Wilson 95% CI) | 2026-11-03 semantic audit |
|-|-:|-|-:|-|-|
| activity | 0/3 | 0.0% (0–56%) | 0/1 | 0.0% (0–79%) | not sampled |
| address | 19/37 | 51.4% (36–67%) | 19/28 | 67.9% (49–82%) | 7/13 (54%; 29–77%) |
| existence | 30/59 | 50.8% (38–63%) | 30/46 | 65.2% (51–77%) | 12/24 (50%; 31–69%) |
| liveness | 0/2 | 0.0% (0–66%) | 0/1 | 0.0% (0–79%) | not sampled |
| parent | 5/7 | 71.4% (36–92%) | 5/5 | 100.0% (57–100%) | 0/2 (0%; 0–66%) |
| scope | 3207/3575 | 89.7% (89–91%) | 3207/3338 | 96.1% (95–97%) | 122/151 (81%; 74–86%) |
Archive packet: 34 rows / 11 captures
Archive holds: {'CAPTURE_FETCH_FAILED': 82, 'NO_CAPTURE': 25, 'CAPTURE_REDIRECT_HOLD': 5, 'FRESH_RECHECK_FAILED': 50, 'CAPTURE_PENDING': 106, 'RATE_LIMIT_HOLD': 2959}
<!-- RESULTS END -->

## Method and artifact boundary

Fetch once per exact cited reference, curl/browser UA with Jina raw fallback, local cache in ignored `build/l1-cache/`.
HTML text nodes exclude script/style/noscript; this is **not** a browser visibility/rendering audit (hidden/template
nodes may remain). No truncation; undecodable cached text is held if replacement characters occur. Recognized
challenge walls are held; no fixed phrase list can identify every interstitial. Source-ref redirects are compared
structurally, preserving query values; Jina must supply a matching URL Source header. Unverifiable response identity
is held. Raw bodies, headers, effective URLs, hashes and timestamps are local; verdicts retain observation timestamps.
No private, licensed, CRM, vault or personal information is used. Data-estate lookup reported missing Windows-only
Documents catalogues on this Mac; repository references and the live public pages suffice for this pass.

Quote extraction uses the house `Quote: "..." | ...` notes format, then an unambiguous single quoted claim_detail span.
Multiple quoted fragments and punctuation-only quotes are held. Inputs, verdicts, and quotes are bound field-for-field
to the canonical evidence; a forged verdict quote fails. No evidence row, tier, org/site, inclusion decision or registry
link changes. No new EVD IDs are allocated. No dedupe/create procedure is triggered. All 34 archive links reference
existing supports_A evidence rows; the archive has no tier effect.

The controller delegated sole archive_links.csv application to L1 under AGENTS §2.7. Git bd57a08 is the pre-pass backup;
this README is the pass journal. An initially verified 101-row capture packet was reduced to 34 after fresh transport
failures. These are availability exclusions, not quote contradictions. The revised conservative live classification
changed the preliminary 3,344 matches to 3,261 (redirect/decoding/ambiguous-quote holds); no matching threshold changed.
Existing evidence and published archive facts remain append-only. All 34 included rows still pass the revised live posture.

## Archive discovery and holds

Legacy availability discovery hit sustained 429s after approximately 100 successful responses; the parallel batch
lacked shared backoff and was stopped. The snapshot collector now uses a shared global stop and labels rate-limit holds.
No unavailable capture ever becomes an archive link. Normal replay is required; a replay redirect is held. URL binding
is stricter than V-59 on query values: scheme/www/host case and a trailing **path** slash may differ; query case and
slashes must not. Raw metadata stay local. `archive_outcomes.csv` supplies exactly one outcome for every supported
row without a link. `repair_leads.csv` supplies exactly one settling-fact lead for every non-supported live row.

The controller authorized a resumable `discovery.py` worker (11-hour run window): CDX at most once per five seconds,
Save Page Now at most once per 20 seconds when no exact capture is returned, 429 exponential backoff from 60 seconds.
Numeric Retry-After is honored. Accepted SPN is not evidence of a capture: CDX must expose a readable exact capture
containing the quote. Query-string SPN submissions are held until the encoded submit route is verified;
existing query-string captures can still qualify. Per-URL receipts under `build/l1-discovery/` support resume; the aggregate is rebuilt on restart.
The worker writes only local `build/l1-cdx-links.csv`, never canonical or frozen PR files. Restart errors are explicit
holds; move aside failed URL receipts locally to retry. The worker's deadline cannot reuse a preceding URL's replay.
No archive completeness is claimed. A later top-up requires fresh checks and review. Rest-OH then PA are a separate PR.

## Named checks and reproduction

```sh
python3 tasks/evidence-reverify-archive-2026-11-06/run.py
python3 tasks/evidence-reverify-archive-2026-11-06/known_answers.py
python3 tasks/evidence-reverify-archive-2026-11-06/check_mutations.py
# Discovery may regenerate a candidate packet; do not change the frozen packet during checking.
python3 tasks/evidence-reverify-archive-2026-11-06/check_archives.py --packet-only
python3 tasks/evidence-reverify-archive-2026-11-06/build.py
python3 tasks/evidence-reverify-archive-2026-11-06/report.py
python3 scripts/validate.py
```

Fresh `check_archives.py --packet-only`: **34 rows / 11 captures / 0 failures**, PASS. It binds canonical quotes,
re-fetches every capture, rejects any packet mutation, and writes per-row receipts bound to the packet/quote hashes.
Failures clear the receipts and fail closed. `build.py` refuses any row without that successful receipt; application
therefore follows the content gate. The default check also requires the whole canonical archive table to equal the
checked packet, so an earlier applied row cannot disappear from verification. Builder rerun: zero additions, PASS.
`report.py`: exact canonical/input/verdict binding, unique leads, exact disposition sets and README-result equality,
PASS. `validate.py`: zero errors after application, PASS. No scripts/ edits, so its pytest gate is not triggered.

Known answers: four inspected real records EVD-013356/013357/013360/013379; inserted words and reversed order fail,
empty quote returns None. URL mutations reject another path, path case, query value case and query trailing slash.
Controlled redirect, ASCII challenge-wall and decoding-error fixtures hold. CDX known answers cover exact/other/empty/
HTTP error/invalid JSON. All PASS. `check_mutations.py` injects forged verdict quote, duplicate repair lead and unknown
archive-outcome ID, plus a missing fresh-check receipt before application; every defect fails the named report check and all originals restore byte-for-byte.

## Independent refute record

Initial council Codex (gpt-6-astra/max, `--effort deep`): REFUTE. Valid findings: structural query URL binding;
canonical quote binding; missing exact disposition/lead uniqueness assertions; overclaim of visible text; packet freeze;
worker aggregate recovery. Fixed with structural URL parsing, canonical cross-checks, exact set/uniqueness checks,
narrowed text-extraction description, packet hash checks and restart aggregate regeneration. Ambiguous spans now hold.

Initial council Grok (grok-4.7/xhigh, `--effort deep`): REFUTE. Valid findings: unflagged final-page redirects, wall/
decoding ambiguity, quote extraction ambiguity, apply-before-fresh-check and canonical rows outside packet. Fixed with
conservative response posture, guarded quotes, mandatory fresh receipts and whole-table default archive check. Settling
page wording describes a future readable source, not an assertion that failed pages loaded. Sticky legacy cache is
explicit; the controller's paced CDX/SPN worker is the continuation route. Some review findings concerned the earlier
in-flight code and were already fixed before publication (429 label/backoff, terminal gates, deadline handling).

Controller 05:55 ruling supersedes council-only ordering and permits draft publication before refutes. Both independent families approve the corrected snapshot: Codex3 reviewed7484791 (code8533b8e), Grok3 approved8533b8e. Full archive completeness is not claimed. The original refute outputs are local, with the
verdicts and responses recorded here. No semantic claim re-verification, replacement evidence, scope/ring/vocabulary
ruling, rendered visibility audit or PDF text extraction is claimed.

Codex3 clerk @4ef764e: REFUTE one remaining replay-query gate defect. Reproduced before editing with the clerk's
controlled fixture: a requested query value key=a/ redirected to key=a passed and wrote a receipt. Current 34 rows
have no queries; no bad current row was demonstrated. Fixed all three replay-effective-response comparisons via
same_capture: exact capture timestamp plus structural original-page comparison, preserving query case/slashes.
check_replay_binding.py exercises the actual receipt gate: exact replay passes; changed query and capture timestamp
fail and leave no successful receipt. PASS. The continuation cache collector receives the same shared guard.
Existing frame, judgments, quotes and canonical archive rows do not change. The targeted cure subsequently passed both clerk re-reviews.


Grok3 clerk @8533b8e7e5bc8eeaeadb897c970f661cfd34d12a: **APPROVE, zero findings**. Targeted replay-cure review
confirms exact timestamp and preserved inner query across collector/checker/worker. Actual receipt-gate regression
passes; extra probes reject another query value and id_ modifier, and preserve permitted scheme/www/path-slash
normalization. validate.py zero errors; keyed row-loss guard PASS against merge-base bd57a08dfe. No data differs from
4ef764e: same34 archive rows, none with queries, frozen judgments unchanged. The prior Grok review independently
re-fetched7captures covering10rows with matching quotes; network captures were not re-fetched again for this code-only
cure. Codex3 subsequently approved the same code cure, as recorded below.


Codex3/OpenAI clerk: **APPROVE, zero remaining findings**, code cure8533b8e reviewed at7484791 (documentation-only
receipt afterward). Original redirected-query reproducer now fails at the actual gate; permanent replay-binding
regression passes. Eight additional controlled query/timestamp/modifier/host/path/encoded-slash mutations reject
and clear a pre-seeded stale receipt; allowed scheme/www/path-slash normalization passes. validate.py zero errors,
row-loss guard PASS against pinned origin/main (merge-base bd57a08), report exact3261/422/34/3227 PASS. Canonical
data and frozen quote/judgment/ID packets unchanged from4ef764e, no forbidden federal-frame files in committed diff.
The unchanged34links/11captures and1120live references were not re-fetched for this targeted code cure. Both-family
approval is for the scoped quote audit and verified34-link snapshot; the3227 archive holds and long worker remain open.
