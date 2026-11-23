# Ohio organization navigation links

First user is John, for company profile lookups. Non-use review is 2026-12-23.

The batch must reconcile to 748 active organizations with an HTTP(S) website and an Ohio HQ or active Ohio site at `87ba8847`, outside the prior PIC-18 input list. At most eight pages per organization may be requested, with robots checks, the declared Atlas user agent and one transport retry. A refused route stays held. Admission requires a same-entity header/footer company link, an own-domain newsroom index, or a feed whose item link appears on the selected newsroom. Existing values are protected. A11-047 is the one named repair and requires the same overlap check. No evidence rows are added.

The draft requires a 30-cell stratified witness sample for another-family reading, a replay that rejects all three planted defects and a byte-identical second apply, Atlas validation, and a row-loss check against `origin/main`.

The task uses #350's company-link and newsroom candidate rules. It uses the article-item intersection from `tasks/newsroom-urls-other-2026-11-06/check.py` (the adjacent `audit.py` checks dates). The robots policy and direct transport are from the November 16 crawler. One crawl pass uses `Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)` and reserves the eighth page slot for a uniquely advertised feed. The #350 feed path requires a newsroom page in the retained corpus.

The manifest records SHA-256 and byte length for the original response. The pinned HTML and XML retain the navigation anchors and hashes of item URLs needed to replay the decision. Page text, contact details and feed descriptions are discarded before writing receipts. Replay checks the pinned witness bytes against their own digest. The original response bytes are unavailable for a second hash calculation. The witnesses stay in the controller's `persist/ohio-corpus-2026-11-23/` directory.

Run `python3 tasks/ohio-links-corpus-2026-11-23/build.py --freeze --apply` from the assigned worktree. Run `python3 tasks/ohio-links-corpus-2026-11-23/check.py` to replay the packet and sample, verify the cell delta, and prove a byte-identical second build and apply.

The seed for `sample.csv` is `20261123`. It allocates 30 observations across the three fields by the filled cell shares, distributes remaining slots by largest fractional remainder, then draws without replacement within each field. Each sampled cell carries its page URL and pinned witness digest. The controller assigns the independent sample reading.

Round 1 review identified a parent-company newsroom on a domain held by a single Atlas record. The builder now holds all three navigation fields when the Atlas record cites a parent site or several records share the domain. `parent_site_holds.csv` records additional entity ambiguities found by reading the previously applied rows against their held names, operator notes and corporate domains. The same pinned corpus replays this narrower set of fills and regenerates the sample at the original seed.

## National-arm scan

The scan screened 132 organizations with at least one fill at `433fe056`. The initial flag rule matched `US`, `USA`, `U.S.`, `America`, `Americas` or `North America` as whole words in the legal or trade names, or `US arm`, `North American arm` or `subsidiary of` in the notes. It flagged four organizations. The reviewer nominated ORG-003002, whose description identifies the US arm. A second screen across notes and descriptions also recognized `subsidiary/division of`, `US subsidiary` and `Americas arm` and flagged three more organizations. Eight distinct organizations were flagged and all eight were read against the proposed links and held records.

| Organization | Disposition |
| --- | --- |
| ORG-000670 | Kept the newsroom on the exact entity's own site, which uses its acronym. |
| ORG-000791 | Kept the LinkedIn slug matching the subsidiary's own name, linked from its own site. |
| ORG-000912 | Kept the newsroom published on the subsidiary's distinct brand domain. |
| ORG-000992 | Kept the newsroom and feed on the US arm's explicitly US-branded domain. |
| ORG-001076 | Kept the newsroom and feed published on the subsidiary's own brand domain. |
| ORG-001815 | Kept the LinkedIn slug that explicitly names the US arm, linked from its own site. |
| ORG-001910 | Kept the newsroom and feed on the domain documented as the North American operator's own site. |
| ORG-003002 | Withdrew the LinkedIn page for the global group from the US arm's record. |

The withdrawn cell was outside the released sample, whose bytes were preserved.
