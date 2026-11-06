# L1 continuation: rest of Ohio, then Pennsylvania — 2026-11-06

Separate branch/PR continuation of PIC18 PR #137; stacked on its corrected commit 4ef764e. Merge #137 first.
First users: the Atlas integrator and evidence auditors, beginning at PR review on 2026-11-06. Acceptance is the
original lane gate: canonical quote binding, complete row/lead yields, fresh readable exact capture containing the
quote before any archive application, idempotent builder, validate zero errors, two-family refute approval.

Frame: own_site evidence on OH sites and their parents, excluding every PIC18 evidence ID already audited; then PA
sites and their parents excluding all prior Ohio/PIC18 evidence IDs. No HQ/status/tier filter. State membership
comes from physical site rows. One evidence row is counted once even if its parent operates in both states. The two
phases have 745/567 cited references, with 1 shared exact reference; 1,311 distinct references in their union.

Judgments are preserved-quote presence with the corrected PIC18 matcher/response posture, not semantic claim truth:
NOT_SUPPORTED = quote absent; PARTIAL = missing/ambiguous quote; WRONG_PAGE = different host/path/query redirect
hold; FETCH_FAILED = availability/decoding/recognized-wall/response-identity hold. No rejection/status inference.
All unresolved lane records are STILL_UNCERTAIN. The 2026-11-03 audit's semantic support estimand is different.

<!-- RESULTS BEGIN -->
OH: 1947 evidence rows / 745 cited references; {'PARTIAL': 35, 'FETCH_FAILED': 146, 'SUPPORTED': 1658, 'NOT_SUPPORTED': 79, 'WRONG_PAGE': 29}
- OH activity: 0/6 quote-supported (0.0%; Wilson 95% 0–39%)
- OH address: 8/19 quote-supported (42.1%; Wilson 95% 23–64%)
- OH existence: 1/23 quote-supported (4.3%; Wilson 95% 1–21%)
- OH liveness: 0/4 quote-supported (0.0%; Wilson 95% 0–49%)
- OH parent: 0/5 quote-supported (0.0%; Wilson 95% 0–43%)
- OH scope: 1649/1890 quote-supported (87.2%; Wilson 95% 86–89%)
PA: 1639 evidence rows / 567 cited references; {'FETCH_FAILED': 196, 'PARTIAL': 67, 'SUPPORTED': 1317, 'WRONG_PAGE': 29, 'NOT_SUPPORTED': 30}
- PA activity: 0/2 quote-supported (0.0%; Wilson 95% 0–66%)
- PA address: 3/14 quote-supported (21.4%; Wilson 95% 8–48%)
- PA existence: 36/84 quote-supported (42.9%; Wilson 95% 33–54%)
- PA liveness: 0/1 quote-supported (0.0%; Wilson 95% 0–79%)
- PA parent: 1/7 quote-supported (14.3%; Wilson 95% 3–51%)
- PA scope: 1277/1531 quote-supported (83.4%; Wilson 95% 81–85%)
Continuation total: 3586 rows / 1311 distinct references; 611 repair/availability leads; 0 new archive links; 2975 archive holds. Inherited links: 34.
<!-- RESULTS END -->

## Current archive hold — no Done claim

No new continuation capture has yet been verified. `check_archives.py` and `build.py` deliberately refuse a zero-new-link
packet: 34 inherited PIC18 links are not counted as continuation impact. This PR is a live-audit packet pending its
archive stream and two-family review. It makes **zero new data edits**. No EVD IDs or verification tiers change.
`archive_links.csv` includes the inherited links solely so the eventual shared fresh check covers the whole canonical
table, including inherited rows. `new_archive_links.csv` separates actual continuation additions.

The continuation CDX/SPN worker is queued behind the existing PIC18 worker; the two must never run concurrently.
It reuses the exact paced worker (CDX ≥5 seconds, SPN ≥20 seconds, exponential 429 backoff, readable exact capture and
quote required). Separate resumable outputs: build/l1-discovery-OH, build/l1-discovery-PA and build/l1-cdx-links-OH.csv,
build/l1-cdx-links-PA.csv. It writes no canonical or frozen task files. `candidate_packet.py` imports matching witnesses
from these local streams only after checking their cached replay/quote; a fresh check must still pass before application.
Raw caches stay in ignored build/. This does not claim archive discovery complete or treat absent captures as false claims.

The first PR's scripts are reused for fetching, matching, canonical binding, capture checks and receipt-gated appends.
The only shared extensions are optional output paths for the serialized worker and an explicit directory argument for
canonical binding. Defaults preserve PIC18 behavior. No new matcher/fetcher, dependency, vocabulary or field exists.
No private/CRM/licensed/personal content is used. Source witnesses are the existing public cited own-site pages and
Wayback exact captures. No org/site creates, inclusion-log entries, registry links, derived fields or QUEUE edits.

L1/L11 agreement: fresher-evidence repairs are reserved to L11, including PR137's frozen 158 weak rows at4ef764e
(75 NOT_SUPPORTED,49 redirect holds,34 quote holds). L1 adds no replacements; its EVD140000–149999 block is unused.
L11 independently checks claim semantics, and L1 will notify it if clerk review changes the frozen weak set.

## Reproduce

```sh
python3 tasks/evidence-reverify-archive-oh-pa-2026-11-06/run.py
python3 tasks/evidence-reverify-archive-oh-pa-2026-11-06/archive_cached.py
python3 tasks/evidence-reverify-archive-oh-pa-2026-11-06/candidate_packet.py
python3 tasks/evidence-reverify-archive-oh-pa-2026-11-06/report.py
# Once the serialized discovery has produced at least one matching continuation capture:
python3 tasks/evidence-reverify-archive-oh-pa-2026-11-06/check_archives.py --packet-only
python3 tasks/evidence-reverify-archive-oh-pa-2026-11-06/build.py
python3 scripts/validate.py
```

Known-answer coverage reuses the four inspected raw-page examples and adversarial quote, URL, CDX, response-posture,
canonical binding and yield mutations from PR137. `report.py` independently reconstructs each state membership against
canonical data, checks disjoint IDs, exact repair/disposition yields, and exact README result text. These pass.
The zero-new-capture archive gate intentionally fails, leaving the work pending. Two-family continuation refute is
pending, as is archive application; no script/validator code changed so scripts/ pytest is not triggered.

L11 also owns round4 replacements for PR155 a012caa: OH143weak +PA126weak =269, excluding342FETCH_FAILED. No L1 replacements. The replay-query guard correction changes code only, not either frozen evidence frame, judgments or quotes. All four replay-response comparison callers (including this continuation cache collector) now use the shared timestamp/query-preserving guard.
