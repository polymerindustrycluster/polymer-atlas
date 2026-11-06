# OSU second-pass follow-up — 2026-11-06

Bounded deeper review of **15 reassigned, previously unresolved Ohio State candidate people**: **0 VERIFIED proposals, 2 REJECT, 13 STILL_UNCERTAIN, 0 DUPLICATE_OF**. These are part of the parent's original frame, not additional candidates. The integrator merges these dispositions into its original 53-candidate accounting.

The two exclusions rest on one explicitly published professional-practice rank (B-CG-1) and one emeritus rank (nonemeritus Gate A). Full own-department pages were inspected through `web.open` after browser-UA curl and house Jina failed; one NAS fallback also failed. These are full institutional pages retrieved through the web engine (directory crawl last week, latest person-page crawl today), not search snippets or raw HTTP confirmation. The latest person page styles Emeritus and supersedes an earlier retrieved professional-practice styling; both are excluded. That availability/freshness limit is recorded with their tool-response hashes.

The 13 holds name the facts needed to settle them in the private dispositions. New department, lab, and catalog sources identified current professor entries and more specific research programs, but did not establish the required current institution-hosted polymer-material object. Department-wide polymer bullets, neighboring PI paragraphs, generic biomaterials/coatings, historical projects, external-lab-only text, publication titles, and natural cellular protein polymers do not carry Gate B. Unavailable routes never establish absence. No scope exception was self-ruled.

New source observations cover **35 unique associated URLs**: 21 usable HTTP responses with SHA256 hashes, 2 cached full institutional pages with explicitly labeled tool-response hashes, and 12 unavailable routes. A current dentistry graduate handbook yielded **55 of 55 physical PDF pages**, with the candidate-specific research entry inspected on printed page 45. Contact information is omitted from retained extracted text; raw cache stays under `/tmp`. Full URL/hash/scope observations and all 15 exact input IDs remain in the private runtime, so uncertain/rejected discovery names are not published. `verified.csv` intentionally contains only its header.

Run from the second-pass checkout:

```sh
python3 tasks/people-settle-2-2026-11-06/lanes/root15/check.py
```

PASS: exact 15 IDs in input order; complete 0/2/13/0 accounting; five actual-source known answers; four token-boundary/wrong-identity controls; target-entry-bound excluded ranks; PDF page yield; maximum six associated source URLs per candidate; explicit raw-versus-tool hash basis and failed routes; main and the current pending first-pass snapshot (12 candidate people at this rerun; checker reports its row count dynamically) dedupe; empty public proposals; privacy and discovery-name exclusion. Global first/surname variants were inspected privately as distinct names/institutions without forced merges. The check's count gates were mutation-tested with an injected duplicate candidate ID and correctly failed.

No data edits, IDs, branch changes, commits, PRs, task-status changes, or faculty census expansion. Independent inspection, integration, and completion refutes remain with the parent. Checks require the parent-owned private input/runtime and temporary source cache.
