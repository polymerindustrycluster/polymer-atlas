# PIC-18 own-site quote re-verification and archive links, 2026-11-06

L1, claimed by controller thr_9i2c6byhcz for atlas-L1-reverify-archive. Source tree: bd57a08.
First users: Atlas integrator and evidence auditors, beginning with this PR on 2026-11-06; no operational UI is added.

Frame: every OH site whose physical county, after stripping a trailing ` County`, is in `scripts/regions.py` PIC18;
plus the organizations operating those sites, regardless of HQ. No status/tier filter. The union contributes
**3,683 own_site evidence rows / 1,120 distinct cited references**, exactly the controller's baseline. Four references
(8 rows) are not bare URLs. Organization HQ-only selection would instead yield 3,540 rows / 1,073 references;
including all PIC18 HQ organizations plus site parents would yield 3,765 / 1,149. Neither alternative is used.

## What the judgments mean

This pass tests **preserved quote presence**, using the unchanged `words`, `on_page`, and `wilson` implementations
loaded from the calibrated 2026-11-03 audit's `analyze.py` via AST (without executing its CLI). Contiguous normalized
words must match; punctuation and accents follow the original matcher. Quote extraction uses `notes`' `Quote: "..."`
format, then quoted `claim_detail`. No inference from a match to the underlying claim's truth is made.

Live URLs were fetched once per exact reference and cached (curl/browser UA, Jina raw fallback). Script/style/noscript
content is excluded; visible HTML text is used, Jina's response metadata is excluded. Raw responses and full page
text stay in ignored `build/l1-cache/`, never in the PR. No truncation. Fetch errors, unsupported PDF extraction,
challenge walls, non-URL references and insufficient readable content are availability failures, never evidence of absence.
A failed cached fetch is not silently retried. `fetched_at` and route metadata live in the local cache; verdicts carry checked_at.

**3,344 SUPPORTED** means the preserved quote's words occur in order. **76 NOT_SUPPORTED** means that exact quote is
absent from the readable cited page, not that the claim is false. **35 PARTIAL** rows are holds: readable page but no
preserved quote to test; no semantic partial-support assertion is intended. **228 FETCH_FAILED** rows are availability
holds. `repair_leads.csv` includes all 339 non-supported rows, including availability holds, and names the settling claim/page.
Lane-level posture for every unresolved row is STILL_UNCERTAIN; none is an organization rejection or status change.

The prior audit judged **claim semantics**, then verified its newly chosen quotes. Its 74% support rate (142/191
readable sampled pages; 68–80% Wilson CI) is a different estimand, geography, and sampling design. The comparison
below is context, **not evidence that semantic support improved**. This pass does not independently validate that
site-level claims are locally attributable, or that a quoted capability maps to the claimed vocabulary term.
All-frame denominators count fetch/no-quote holds against support; readable denominators exclude FETCH_FAILED only.
Wilson intervals are descriptive binomial reference intervals on this full frame, not uncertainty from random sampling.
PIC18 evidence rows: 3683 distinct cited refs: 1120
Judgments: {'SUPPORTED': 3344, 'PARTIAL': 35, 'NOT_SUPPORTED': 76, 'FETCH_FAILED': 228}
Repair/availability leads: 339 / 3683
| Claim | Quote supported / all rows | Rate (Wilson 95% CI) | Supported / readable | Rate (Wilson 95% CI) | 2026-11-03 semantic audit |
|-|-:|-|-:|-|-|
| activity | 0/3 | 0.0% (0–56%) | 0/1 | 0.0% (0–79%) | not sampled |
| address | 19/37 | 51.4% (36–67%) | 19/28 | 67.9% (49–82%) | 7/13 (54%; 29–77%) |
| existence | 32/59 | 54.2% (42–66%) | 32/46 | 69.6% (55–81%) | 12/24 (50%; 31–69%) |
| liveness | 0/2 | 0.0% (0–66%) | 0/1 | 0.0% (0–79%) | not sampled |
| parent | 5/7 | 71.4% (36–92%) | 5/5 | 100.0% (57–100%) | 0/2 (0%; 0–66%) |
| scope | 3288/3575 | 92.0% (91–93%) | 3288/3374 | 97.5% (97–98%) | 122/151 (81%; 74–86%) |

## Archive snapshot and continuation

The snapshot currently applies **34 archive links / 11 captures**, each citing the same page under V-59's exact
normalization. All 34 referenced evidence rows already have `tier_effect=supports_A`; zero evidence rows, organizations,
sites, or verification tiers are created/changed. No replacement EVD IDs were minted. No inclusion decisions or
inclusion-log entries. No dedupe/create procedure is triggered. Existing evidence and links are immutable.
The controller designated L1 as sole archive-file writer under AGENTS §2.7; git bd57a08 is the pre-pass backup.
`build.py` uses `shard_io.append_sorted`, skips byte-equivalent existing rows and refuses conflicting links.

Discovery through `/wayback/available` hit sustained 429s after roughly 100 successful responses. The initial parallel
batch lacked shared backoff; it was stopped and replaced by a global API stop, then the controller's paced CDX worker.
Normal replay URLs work where `id_` replay was rate-limited. Every candidate requires readable normal replay, exact
capture/page binding (replay redirects held), and the same quote match before it is eligible. An initial 101-row packet
was reduced after fresh transport failures; exclusions are explicit, not claims of quote contradiction. Raw request
metadata are local. The full-frame yield check failed while the archive snapshot was incomplete, as intended.

`discovery.py` is a resumable local worker: CDX at most one call per five seconds, Save Page Now at most one per 20 seconds
when CDX returns no exact capture, exponential 429 backoff from 60 seconds. No link is added because SPN accepted a request:
it must appear in CDX, be readable, and contain the quote. A worker run has an 11-hour ceiling and resumes per-URL JSON
receipts from `build/l1-discovery/`. It writes only local `build/l1-cdx-links.csv`, never canonical or committed packet files.
A later top-up must apply the same strict re-fetch and review gates. Receipt files with transport errors are holds,
not absence findings. To retry those URLs on another run, move their receipts aside in the local cache first.

| Hold | Count (evidence rows) | Settling fact/action |
|-|-:|-|
| Preserved quote absent | 76 | Own-site page with the claimed words, or a separately reviewed fresher evidence row |
| No preserved quote on readable page | 35 | Manual semantic review and selection of a supporting quote |
| Live fetch failed | 228 | Readable cited primary page; no absence inference |
| Archive not in this snapshot | 3,310 | Exact readable capture with matching quote; includes rate-limit, pending, missing and failed re-fetch cases |

Rest-of-Ohio and PA continuation belongs to a second PR; this first snapshot does not include them. Semantic claim
re-judgment, replacements, owner/ring/vocabulary changes, PDF text extraction and site-attribution repair are not claimed.
The read-only data-estate lookup had Mac platform gaps in the Windows-only Documents catalogues; repository sources
and the live cited web pages suffice for this pass. No CRM, private vault, licensed sources or personal data were used.

## Reproduce and gates

Run from repository root (Python 3.15, curl 8.7.1; standard library only):

```sh
python3 tasks/evidence-reverify-archive-2026-11-06/run.py
python3 tasks/evidence-reverify-archive-2026-11-06/known_answers.py
python3 tasks/evidence-reverify-archive-2026-11-06/archive.py --cached-only
python3 tasks/evidence-reverify-archive-2026-11-06/build.py
python3 tasks/evidence-reverify-archive-2026-11-06/check_archives.py
python3 tasks/evidence-reverify-archive-2026-11-06/report.py
python3 scripts/validate.py
```

The archive command regenerates from local discovery cache; a fresh machine must populate it using `archive.py` or
`discovery.py` first. It will not silently claim zero archives as a pass. `check_archives.py` independently refreshes
all distinct captures and fails on any unreadable or unmatched row, including an empty packet. It retries transient
failures at most twice and backs off on 429. Live cache reuse is intentional; remove only the relevant local cache
receipt to request a new live observation. Never commit raw caches.

Known-answer gate: EVD-013356, EVD-013357, EVD-013360 and EVD-013379 were inspected in raw fetched page text. All four
matched; inserting a unique absent token or reversing their word order failed. Empty quote returned None. V-59 binding
mutations reject a different path, path case, and query string; permitted scheme/www/host-case/trailing-slash changes pass.
`known_answers.py`: PASS. `build.py` rerun: zero additions, PASS. `report.py`: full frame/lead/archive counts reconcile,
PASS. Baseline `python3 scripts/validate.py`: zero errors, PASS. No `scripts/` files changed, so the scripts pytest gate
is not triggered. Fresh capture gate and two-family review results are recorded below when terminal.

Fresh archive gate: `python3 tasks/evidence-reverify-archive-2026-11-06/check_archives.py` —
**34 rows / 11 distinct captures / 0 failures**, PASS after bounded retry of transport failures. Earlier failed
101-row and 34-row checks were retained locally as diagnostics; this result follows exclusion of the first failing
candidates and retrying connection failures. No quote-match threshold was changed. Every row now included was freshly
re-fetched and its quote found. Validation after application: zero errors; builder idempotence: zero additions.

Controller 05:55 ruling supersedes the council-only ordering: draft PR publication may precede refutes; reviewer
threads are an approved alternative while council is saturated. Required families remain Codex + Grok. The original
deep council calls are still pending. Clerk reviews will be requested after branch publication; no Done claim.
Additional known-answer fixtures check CDX exact-page binding, another page, no captures, transport HTTP error and
invalid JSON, all PASS. Worker deadline handling and exponential replay backoff were tightened before restarting
from saved progress. The restarted worker uses the same local receipts and does not mutate the 34-row snapshot.
