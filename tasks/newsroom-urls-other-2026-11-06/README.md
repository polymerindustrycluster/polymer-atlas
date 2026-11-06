# L9 newsroom round 3 — other organizations, 2026-11-06

Controller approved third class as a separate branch/PR under original priority ruling. Branch agent/codex/newsroom-urls-other starts from current main af3f87e (#147 merged). PR145 tier1 and PR152 PIC18 are separate, unchanged drafts. Integrator delegation limited to newsroom_url/newsroom_feed_url. First user is the existing news-monitor operator (L8/controller), after merge; no new operator system.

## Scope and acceptance before application

Full frame2258 distinct **active organizations** with website, tier1_qualifier empty and no physical OH site in PIC18. inputs.csv freezes scope; regions.py supplies counties. The earlier2256 census was correct at bd57a08; independent ref-by-ref recomputation reconciled current2258 = old2256 + ORG-002487 + ORG-002729, no losses. No silent count discrepancy. Unit/filter: tier1=0, PIC18 non-tier1=0, other=2258 attempted in this pass.

Use only own-domain news/press/announcements indexes found from canonical website navigation. Hold home redirects, broader parent/division/brand mismatches, template/tag/post uncertainty and unreachable routes; failed fetches assert no absence/closure. <=6 discovery requests per org, all input IDs reconciled to dispositions. No full website/sitemap crawl; explicit residual holds. Every retained URL HTTP200, final path/domain unchanged; feed parses RSS/Atom with >=1 article entry, at least one article permalink linked from selected newsroom; no channel/feed metadata or comments-feed acceptance. Conservative gates inherit PR145 Codex/Grok refute fixes before work starts.

SCHEMA4.4/v1.11 and V-58 make these navigation aids, never evidence themselves. No EVD rows/quotes, lane block unused. No record creates/dedupe/ID allocation/inclusion decisions; no status/tier/liveness/registry/derived/LinkedIn changes. Sources are held own websites and linked indexes, no licensed/private/personal-contact sources. Exact routes/date samples/verdicts will be in task artifacts. Builder is idempotent, preflights scope/website/value conflicts before writes, and replays from exact current-main organization shards on main changes. Branch history is pre-pass backup, README pass journal.

## Named checks

```
python3 tasks/newsroom-urls-other-2026-11-06/self_check.py --live
python3 tasks/newsroom-urls-other-2026-11-06/build.py
python3 tasks/newsroom-urls-other-2026-11-06/check.py
python3 scripts/validate.py
```

Self-check:3 fresh known answers (Avient/RPM/GEON), injected HTTP403/off-domain/emptyfeed/channel-home/comments/same-domain-home failure cases; independent full frozen9d69978-frame reconciliation. Check every accepted data cell equals reviewed packet, then re-fetch all filled URLs and inspect article-item feed overlap. Repeat builder must write0 cells; compare every data field and rowset against main. Final deep Codex/Grok clerk reviews required before completion; no Done claim while pending.

## Application and checks

Refreshed to main9d69978 before application (includes #147, #136 markets/certs, #129 registry restore). Independent frame recheck remained2258, no gains/losses. No hand CSV merges; exact current data preserved, only packet cells added.

**171 active other non-tier1 organizations:171 newsroom pages+93 feeds=264 empty cells,33 organization shards.** Priority fill counts: tier1=0,PIC18 non-tier1=0,other=171. Existing tiers unchanged: A=15,B=99,C=56,U=1. 2,087 organization holds:1,701 no bounded-nav candidate,386 candidate identity/purpose/accessibility/re-fetch holds. Fifteen overlapping feed-only holds (14 no article-item overlap,1 comments feed). Technetics's index re-fetch failed; held as route unavailable, no absence assertion. IC3D's page retained but its comments feed rejected. All2,258 input IDs reconcile to explicit verdicts.

Actual-source purpose review held A.M.Toolbox's single press release (not an index) and Avian USA's multi-item page because it states Shanghai as publisher; no claim that its article-shaped URL is itself a single article. ETI/Starwin joint publisher held for entity-specific confirmation. Crayola,Plustech,Formed Plastics,Elinor media centers were read raw and show organization news/press announcements, not merely contacts or galleries. No body/contact text retained. Regional/global parent and technical-division pages remain held, including names/links in verdicts.csv. No scope/identity ruling self-applied.

| Hold group | Active organizations | Settling fact/recommendation |
|---|---:|---|
| No bounded-nav candidate |1701|Reachable own-domain newsroom index confirmed; absence never asserted|
| Candidate purpose/identity/accessibility |386|Organization-specific maintained index confirmed, including listed parent/region/single-post/identity questions|
| Feed-only, overlapping accepted orgs |15|Dedicated article feed confirmed; pages retained|

- `build.py`:264 cells/171 organizations; second run0cells/0shards.
- `self_check.py --live`:PASS,3 fresh known answers; injected defects rejected; independent complete2258-ID frame and <=6 discovery requests reconciled.
- `check.py`: **PASS:171 active organizations;264 URLs, all HTTP200 and feeds nonempty**. Same stored path/domain; feed article-item overlap; current canonical data equals packet. refetch.json records every result.
- `python3 scripts/validate.py`: **0 errors,V-58 clean**.
- Field-boundary comparison against current main:264 previously empty cells in171 existing organization IDs, only two named columns; no rowset changes. No scripts/ code change or dependency added.

Final deep Codex/Grok clerk reviews pending; draft until resolved. No completion/Done claim.

## Potential staleness leads

Only pre-2024 fully parsed dates occur in these saved index samples (up to12 dates, nonstandard dates may be missed). Candidate liveness signals only, not assertions of newest release or operating status. Old newsrooms still count under B-NEWS. Posted to BOARD for L8; no liveness/status fields changed.

| Active organization | Date sample |
|---|---|

| ORG-000726 Century Label | November 9, 2021;October 21, 2021;October 8, 2021;September 28, 2021;September 21, 2021;September 17 |
| ORG-000801 Haviland Drainage Products | October 19, 2018 |
| ORG-001118 Southeastern Container, Inc. | 2021-10-20;2023-03-16;2021-05-28;2020-07-31;2020-06-01;2020-05-01;2020-03-31;2019-10-22 |
| ORG-001177 Univenture Inc. | 3/07/2023;9/29/2022;8/29/2022;8/12/2022;7/12/2022;9/09/2021;8/30/2021 |
| ORG-001181 Veelo Technologies | November 1, 2018;April 13, 2016 |
| ORG-001487 UGN, Inc. | May 12, 2023;March 03, 2022;May 14, 2021;August 25, 2020;August 23, 2019;May 07, 2019;October 29, 20 |
| ORG-001536 N8 Medical LLC | August 25, 2023;July 31, 2023;January 6, 2023;July 5, 2022;August 11, 2020;April 2, 2020 |
| ORG-002971 Endeavor Composites, Inc. | October 5, 2022;June 16, 2022;November 16, 2021;February 25, 2020 |
| ORG-003243 Kerotest Manufacturing Corp. | November 1, 2019 |
| ORG-003281 Wisconsin Tubing, LLC | 7/20/2020;2/11/2020;4/15/2019;1/2/2019 |
| ORG-003346 Revchem Composites, Inc. | May 30, 2023;Mar 2, 2023;Aug 29, 2022;Jul 12, 2022;Mar 9, 2022;Feb 11, 2022;February 11, 2022;Dec 30 |
| ORG-003428 Extreme Coatings, Inc. | August 3, 2022;April 27, 2022 |
| ORG-003451 MonTech USA | August 8, 2022;April 12, 2021;March 18, 2021;December 23, 2020;December 15, 2020;December 10, 2020;O |
| ORG-003461 beyondGREEN biotech, Inc. | August 13, 2019 |
| ORG-003470 D&W Fine Pack, LLC | December 6, 2022;Oct. 24, 2018;July 25, 2018 |
| ORG-003566 Reed City Group | February 1, 2023;september 21, 2022;August 15, 2022;February 28, 2022;September 30, 2021;July 30, 20 |
| ORG-003618 Ryan Herco Flow Solutions | March 31, 2015;December 29, 2006 |
| ORG-003645 Gregstrom Corporation | November 26, 2019;June 14, 2019 |
| ORG-003658 The Metal Ware Corporation | September 4, 2020;June 4, 2020 |
| ORG-003667 PlayPower Inc. | March 1, 2022;2022-03-01;November 16, 2021;2021-11-16;2021-11-24;September 21, 2021;2021-09-21;2023- |
| ORG-003702 INOAC USA, Inc. | Mar 15, 2023;March 13, 2023;Feb 17, 2023;Feb 10, 2021;December 15, 2020;January 1, 2021 |
| ORG-003739 Concordia Manufacturing, LLC | April 14, 2023;November 3, 2022;June 15, 2022;April 14, 2022;March 14, 2022;December 30, 2021;Decemb |
| ORG-003874 Legacy Precision Molds Inc. | January 22, 2016 |
| ORG-004830 Microspec Corporation | August 3, 2022;August 27, 2021;April 28, 2021;April 11, 2021;February 3, 2021;June 24, 2019;Septembe |
| ORG-004866 Snyder Industries, Inc. | Jan 8, 2018;Mar 06, 2017 |
| ORG-005058 Induron Coatings Inc. | Jan. 1, 2023;February 22, 2022 |
| ORG-007007 Diversified Engineering & Plastics, LLC | May 22, 2018 |
| ORG-007021 KAM Plastics Corp. | February 26, 2020;December 16, 2019;November 23, 2016;May 21, 2018;November 14, 2016;December 28, 20 |
| ORG-007717 7-Sigma Incorporated | Aug 2 2019 |
| ORG-007721 Avon Plastics, Inc. | April 18, 2017 |
| ORG-008004 R&D Plastics of Hickory, Ltd. | October 15, 2015;January 1, 2015 |

The input manifest was fixed before application at2258 IDs (source snapshot9d69978, same class as af3f87e). Later parallel main creates are outside this pass, not silently added. Self_check independently recomputes the manifest from immutable9d69978 tables; builder/check revalidate current eligibility and values for accepted records. Incoming main changes are retained by merge/replay. No claim of whole-current-tree coverage beyond the named snapshot.
