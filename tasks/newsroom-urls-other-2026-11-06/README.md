# L9 newsroom round 3 — other organizations, 2026-11-06

Controller approved third class as a separate branch/PR under original priority ruling. Branch agent/codex/newsroom-urls-other starts from current main af3f87e (#147 merged). PR145 tier1 and PR152 PIC18 are separate, unchanged drafts. Integrator delegation limited to newsroom_url/newsroom_feed_url. First user is the existing news-monitor operator (L8/controller), after merge; no new operator system.

## Scope and acceptance before application

Frozen9d69978 frame:2258 distinct **active organizations** with website, tier1_qualifier empty and no physical OH site in PIC18 at that snapshot. inputs.csv freezes scope; regions.py supplies counties. The earlier2256 census was correct at bd57a08; independent ref-by-ref recomputation reconciled current2258 = old2256 + ORG-002487 + ORG-002729, no losses. No silent count discrepancy. Unit/filter: tier1=0, PIC18 non-tier1=0, other=2258 attempted in this pass.

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

## Final application and checks

Source manifest is frozen at9d69978 (2258 IDs, same class as af3f87e). Latest integration replay pinned main09df9e9d7ff09858b5ff02c9637de517242e4230; exact main organization files restored, builder applied only reviewed cells. Later parallel main creates are outside this pass. Current eligibility/value assertions still run on every accepted row; no CSV conflict hand-merged.

**165 active organizations in the frozen other cohort:165 newsroom pages+89 feeds=254 empty cells,33 organization shards.** Frozen-cohort fills:tier1=0,PIC18 non-tier1=0,other=165. Tiers unchanged:A=15,B=96,C=53,U=1.2093 organization holds:1701 no bounded-nav candidate,392 candidate purpose/identity/accessibility/re-fetch holds.15 overlapping feed-only holds (14 no article-item overlap,IC3D comments). Technetics re-fetch failed; route hold, never absence. All2258 IDs reconcile to explicit verdicts.

Purpose review held A.M.Toolbox's single release. Avian USA's page is a multi-item index, but it identifies Shanghai as publisher: identity hold, not a false claim that article-shaped URL means single post. ETI/Starwin joint publisher held pending entity-specific confirmation. Crayola,Plustech,Formed Plastics,Elinor media centers read raw and show company announcements, not just contacts/galleries. No body/contact text retained. Parent/regional,division,tag,template and brand ambiguities remain held, no self-ruling.

Related-case fix from PR145 Codex Kaneka finding: also held ORG-003396 Kongskilde Industries USA,003692 Aplix Inc.,003725 Zotefoams Inc.,003766 Roctool Inc. Canonical records name same-brand parents; global news pages need organization-specific publisher/region confirmation. Four pages+their four feeds removed before completion review. Initial171+93=264 was reduced to167+89=256 before review, then165+89=254 after the publisher corrections below.

| Hold group | Active organizations | Settling fact/recommendation |
|---|---:|---|
| No bounded-nav candidate |1701|Need a reachable own-domain index; no absence asserted|
| Candidate identity/purpose/accessibility |392|Need organization-specific publisher/index confirmation, including listed parent/single-post/identity questions|
| Feed-only, overlaps accepted orgs |15|Need dedicated article feed/overlap confirmation; pages retained|

- `build.py`:254 cells/165orgs; immediate second run0cells/0shards.
- `self_check.py --live`:PASS,3 fresh known answers; all injected defects caught; immutable9d69978 frame2258 independently recomputed; allinput/discovery/verdictIDs match,<=6 current discovery requests/org.
- `check.py`: **PASS:165 active organizations;254 URLs,all HTTP200 and feeds nonempty**; exact stored path/domain,article-item overlap,currentdata=packet and current eligibility.
- `python3 scripts/validate.py`: **0 errors,V-58 clean**.
- Immutable-main comparison:254 previously empty cells/165 existing IDs/two named columns only; no rowset changes. No scripts/ code/dependency changes.

Codex1 APPROVE08ce3fe (0 findings) covered the previous167-page packet. Grok1 REFUTE08ce3fe: Stockhausen ORG-008010 and Wickert ORG-002942 now held for organization-specific publisher confirmation; no status/ownership repair. Dunn-Edwards ORG-004896's mentions archive was replaced with its own [announcements index](https://www.dunnedwards.com/press-releases/), fetched200, with dated company releases; feed remained held after failing the same gate. Hold-table prose now states the missing facts.

The igus finding is disputed on primary publisher evidence: the portal's own [Contact page](https://press.igus.com/contact/) identifies **igus, Inc., Rumford, RI**, matching ORG-004835; it does not identify igus GmbH as publisher. The portal's “global leader” wording does not negate that explicit identity. SCHEMA4.4 own-company rule governs; no parent-site exception is claimed. Minimal nonpersonal receipt is publisher-recheck.json. Final two-family review of these corrections remains pending.

Controller frame clarification: frozen9d69978 membership governs; tier1 rank was ordering only. Runtime rank/region guards were removed, while frozen census, current active status, exact canonical website, own-domain/publisher and value-conflict checks remain. INOAC USA ORG-003702 moved to tier1 on later main (national_footprint), as did WL Plastics ORG-003282 and Inteplast ORG-003476; they remain in this frozen cohort, with no tier1 edits by L9. This controller frame instruction supersedes the earlier runtime rank/region exclusion. Query-value redirect and article-link mutations now fail; only path trailing slashes normalize. Fetch timeout45s accommodates slow valid feeds; failure never establishes absence.

Cross-PR union:1049 tier1+772 PIC18+2258 other=4079 distinct active-with-website source-snapshot organizations; all attempted. No claim covers later-main creates or website gains outside that frozen census.

## Potential staleness leads

Only pre-2024 fully parsed dates in saved samples below (up to12 dates; nonstandard dates may be missed). These are candidate liveness leads, never newest-release or operating-status assertions. Old newsrooms still qualify B-NEWS; BOARD/L8 notified. No liveness/status fields changed.

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
