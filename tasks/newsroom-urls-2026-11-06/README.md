# L9 newsroom navigation — 2026-11-06

Claim: atlas-L9-newsroom; branch agent/codex/newsroom-urls. Controller delegated application of these two columns.
First user: existing news-monitor operator (L8/controller); URLs usable when this PR lands. This task adds navigation data, not a new user-operated system.

## Scope and acceptance

Controller ruling 2026-11-06 supersedes the proposed 100-org cap: attempt every active organization with a nonempty tier1_qualifier and website, using the column as-is (pending derivation gains excluded). First PR only; PIC-18 non-tier1 and other organizations belong to subsequent PRs. inputs.csv freezes 1,043 distinct active organizations from the 1,261 active tier1 organizations; 218 without a website are outside the fetch frame.

Acceptance: fill only reachable own-domain news/press/announcements indexes; hold redirects to home pages, ambiguous purpose, parent/division mismatches and inaccessible pages. Feeds must parse as RSS/Atom with >=1 item. No status, verification tier, evidence, liveness, derived field, registry or LinkedIn changes. §4.4 explicitly makes these navigation aids, never evidence by themselves; EVD-230000–239999 remains unused. No factual evidence claims or quotes are added. Primary sources are the organization websites and the linked indexes in verdicts.csv.

## Reproduce

- `python3 tasks/newsroom-urls-2026-11-06/self_check.py`
- `python3 tasks/newsroom-urls-2026-11-06/build.py` (idempotent; fail on conflicting nonempty cells, website changes or eligibility changes; fresh-main rebase re-runs this)
- `python3 tasks/newsroom-urls-2026-11-06/check.py` (every accepted page and feed, HTTP 200, final domain check, nonempty RSS/Atom)
- `python3 scripts/validate.py` (0 errors, V-58 clean)

Branch history is the pre-pass backup. The builder preflights all edited shards before any write. No rows are created, so ID allocation, dedupe and append_sorted do not apply. Only two cells per accepted organization can change; generated exports are untouched. Known CRLF-dirty federal-frame files are excluded.

## Discovery and calibration

`discover.py` extracts exact newsroom navigation labels, fetches up to three candidates, then advertised RSS/Atom feeds or /feed/ and /rss.xml. Up to six discovery fetches per organization; prior attempts are retained, not silently retried. No third-party wire service or social platform is accepted. Ambiguous or unavailable routes remain STILL_UNCERTAIN, never evidence of absence.

Three known-answer records: Avient /company/news-events, RPM /news/, GEON /news all PASS (known_answers.json). Initial matcher missed Avient's “News + Events”; fixed before accepting output. Goodyear had no matching link and Lubrizol/Parker returned 403; these are route failures, not negative findings. self_check.py injects 403, an off-domain redirect and empty RSS and confirms each fails. Domain matching mirrors V-58's documented short two-level-suffix heuristic; no new dependency.

## Results and holds

Final verification passed. verdicts.csv contains one disposition per input, with a named settling fact for every STILL_UNCERTAIN row. Discovery is not complete website crawling: pages without a matching nav link are held even if a newsroom may exist elsewhere. Date years in discovery.json include footer years and are not liveness evidence. Staleness is recorded only after actual dated-item review; no status motion follows.

Baseline `python3 scripts/validate.py`: PASS (4,945 organization rows; existing warnings only). `council-doctor --json`: healthy, all four configured providers pass. No third-party API bulk sources used. Catalogue search was incomplete because the Mac lacks the Windows Documents catalogues; this is not a finding of absence, and discovery uses the already-held canonical website column.

### Potential staleness leads

These indexes have only pre-2024 dates in the parsed date sample (up to 12 distinct dates; nonstandard dates may be missed). This is a **candidate signal**, not a claim about the newest release or operating status. MFG alone was manually confirmed latest 2023-10-26. All remain valid navigation pages.

| Active organization | Date sample |
|---|---|
| ORG-000138 Permatex | February 14, 2020;December 21, 2018 |
| ORG-000430 Mar-Bal Inc. | August 9, 2021;February 24, 2020;February 8, 2021 |
| ORG-000451 Molded Fiber Glass Companies | October 26, 2023;October 5, 2023;August 21, 2023;August 7, 2023;November 17, 2022;October 7, 2022;January 24,  |
| ORG-000835 Fiber-Tech Industries, Inc. | July 30, 2019 |
| ORG-000868 Guardian Manufacturing Company | June 22, 2018;April 5, 2018;September 27, 2018 |
| ORG-001080 Ridge Corporation | September 30, 2021;September 28, 2019;July 26, 2019;January 29, 2018;July 26, 2017;February 29, 2016 |
| ORG-002174 Parker Rust-Proof of Cleveland | 07/08/2022;3/19/2020;2/26/2020 |
| ORG-002401 Mi Windows & Doors Inc. | November 10, 2022;November 02, 2022;October 17, 2022;September 13, 2022;September 07, 2022;August 22, 2022;Jul |
| ORG-002497 The Murus Company | March 15, 2013 |
| ORG-003132 Seasafe, Inc. | Apr 20 2021;April 20, 2021;Jan 25 2021;January 25, 2021;Mar 19 2020;March 19, 2020;Apr 30 2018;April 30, 2018; |
| ORG-003183 AmFine Chemical Corporation | November 12, 2015;June 4, 2014;April 11, 2014 |
| ORG-003194 REXtac, LLC | June 7, 2022;January 1, 2022;December 16, 2021;June 22, 2021;August 20, 2020;April 11, 2019;December 12, 2018; |
| ORG-003219 Covation Biomaterials LLC | May 11, 2023 |
| ORG-003952 Augusta Fiberglass Coatings, Inc. | October 20, 2016;September 6, 2016;July 22, 2016;January 6, 2016;December 10, 2015 |
| ORG-003989 General Plastics Manufacturing Company | May 15, 2019;Oct 20, 2015;September 8, 2015;Oct 6, 2014;October 07, 2014;October 2, 2014;September 23, 2014;Oc |
| ORG-004137 R3 Composites Corp | Feb 11, 2021 |
| ORG-004287 Thorpe Plant Services, Inc. | September 13, 2022;January 18, 2022;June 13, 2016 |
| ORG-004291 Viskase Companies, Inc. | May 31, 2022;February 8, 2022;January 4, 2022;October 6, 2021;April 16, 2021;April 15, 2021;November 24, 2020; |
| ORG-004386 Dicar Inc | May 31, 2022;Mar 23, 2020;March 22, 2020;Mar 20, 2020;Feb 22, 2019;Sep 28, 2018;Jul 18, 2018;Apr 19, 2018 |
| ORG-004533 Bomar Specialties, LLC | January 31, 2023;May 4, 2022;January 31, 2022;June 8, 2021;April 5, 2021;November 2, 2020 |
| ORG-004556 Oregon Rubber Mills Co | 6/3/2016 |
| ORG-004620 Mississippi Polymers, Inc. | 06/01/2017;12/05/2016;11/22/2016;11/01/2016 |

### Final application and checks

Unit/filter: **active organizations**, mutually exclusive priority buckets (tier1 first, then PIC-18 non-tier1, then other). This PR attempts tier1=1,043; PIC-18 non-tier1=0; other=0. Fills: **tier1=118 organizations with 118 newsroom URLs and 44 feeds; PIC-18 non-tier1=0; other=0**. 162 empty cells filled in 118 existing organization rows, across 28 organization shards. No records created. Verification tiers of changed organizations: A=39, B=71, C=7, U=1 (unchanged). 925 STILL_UNCERTAIN organization holds, individually listed in verdicts.csv. No borderline inclusion decisions and no inclusion_log rows.

344 candidate indexes were found. Accepted indexes have an own-domain nav label, matching organization brand in title, and actual text dates in audit.json. Human exclusions include home redirects, parent/group indexes for subsidiary records, investor-only indexes, product-division indexes and page-purpose ambiguity. Identity/page-purpose holds require a confirmed organization-specific index. Route holds require a reachable own-domain index; failed routes make no negative entity assertion. 18 candidate feeds were omitted because no item was also linked from the selected index. No external feed hosts filled.

- `self_check.py`: PASS; 3 live known-answer results; injected failure cases caught; full 1,043-ID reconciliation and <=6 discovery requests per organization.
- `build.py`: 118 organizations, 162 cells; immediate second run **0 cells, 0 shards written**.
- `check.py`: **PASS: 118 active organizations; 162 URLs, all HTTP 200 and feeds nonempty**. Every feed additionally has >=1 item linked from its selected newsroom. `refetch.json` records every result.
- `python3 scripts/validate.py`: **0 errors / OK — validation passed**, V-58 clean, existing warnings unchanged.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: **221 tests, OK (skipped=1)**. Existing build_site.py SyntaxWarning observed; no scripts/ files changed.
- Independent before/after comparison against branch HEAD: **162 changed cells, 118 existing organization IDs, only newsroom_url/newsroom_feed_url, every prior value empty**. No other fields or row sets changed.

### Refute reviews

Pending Codex and Grok deep refute verdicts. No completion claim until both resolved.

### Holds table

| Hold class | Active organizations | Settling fact |
|---|---:|---|
| No newsroom candidate from bounded nav discovery | 699 | Reachable own-domain newsroom index confirmed from navigation, sitemap or direct route |
| Candidate page held | 226 | Confirm organization-specific news-index purpose, identity and accessibility (each candidate URL in verdicts.csv) |
| Feed only, within accepted organizations | 18 | Feed item linked from the selected index; pages still accepted, feeds omitted |

The 925 organization holds are the first two rows, not plus the 18 overlapping feed-only holds.

Feed-gate correction before publication: the initial overlap implementation counted channel-level links, so a shared homepage could give a false match. Restricted overlap to RSS item / Atom entry article links, ignoring channel/self metadata; added injected channel-home fixture. This caught 15 additional feeds, now omitted (18 total feed-only holds including initial three). Final fill = 118 pages +44 feeds. This supersedes the initial 177-URL/59-feed figures sent to the controller and v1 review packet.

Codex deep v1 review **REFUTE**: identified Synray comments feed and channel/feed metadata producing false item overlap. Both findings substantiated. The corrected gate already omitted Synray among the 15 removed feeds; added explicit comments-feed rejection and injected test (even an overlapping comments item fails). Rerunning final checks and requesting a focused final refute. No other data fields changed.
