# L9 newsroom round 2 — PIC-18, 2026-11-06

Claim: atlas-L9-newsroom continuation, controller BOARD06:30; branch agent/codex/newsroom-urls-pic18, NEW branch off main9489b60. Integrator delegation remains limited to newsroom_url/newsroom_feed_url. PR145 tier1 work is separate and unchanged. First user: existing news-monitor operator (L8/controller), usable after merge; no new operator system.

## Acceptance and provenance

Full772 distinct active organizations with website, empty tier1_qualifier, and >=1 physical OH site in PIC18 (county suffix normalized). inputs.csv freezes scope; independent self_check recomputes it from canonical org/site shards using scripts/regions.py. Priority counts are mutually exclusive: this pass tier1=0, PIC18 non-tier1=772, other=0. No region tags written to data.

Primary sources are the held canonical own websites and directly linked news/press/announcements indexes. discovery.json records <=6 discovery fetches/org and115 candidate indexes; audit.json records title and parsed visible-text date samples; verdicts.csv has exactly772 dispositions, no silent skips. No full website/sitemap crawl; no matching nav link is a route hold, never absence/closure. No licensed, private or contact data. SCHEMA4.4/V-58 navigation aids need no EVD; lane EVD block unused. No creates (dedupe/ID allocation/append_sorted inapplicable), no tier/status/derived/evidence/registry/LinkedIn/inclusion_log changes.

Accept own-domain organization-specific newsroom indexes. Hold homepage redirects, parent/division/brand mismatches, template/tag/post ambiguity and unreachable routes. Final URL must stay on stored path, trailing slash tolerated. Feeds must parse RSS/Atom with >=1 article entry and link at least one article also linked from the selected index; exclude channel/feed metadata and comments feeds. Builder preflights conflicting populated cells, website/eligibility/PIC18 changes and off-domain/comment URLs before writes. Re-fetch also checks current data matches packet and PIC18 eligibility.

## Reproduce and current results

```
python3 tasks/newsroom-urls-pic18-2026-11-06/self_check.py --live
python3 tasks/newsroom-urls-pic18-2026-11-06/build.py
python3 tasks/newsroom-urls-pic18-2026-11-06/check.py
python3 scripts/validate.py
```

**39 active PIC18 non-tier1 organizations:39 newsroom pages+11 feeds=50 empty cells,4 organization shards.** Filled tier1=0; PIC18 non-tier1=39;other=0. Tiers unchanged: A=15, B=18, C=6, U=0. 733 organization holds:657 no candidate,76 candidate identity/purpose/accessibility holds. Five overlapping feed-only holds (Vertex,BaseTek,Flambeau,Godfrey & Wing,iCHOR) because no article item also linked from selected index. Only two named fields change. Branch history is pre-pass backup; this README is pass journal. No borderline inclusion decisions or record creation.

| Hold group | Active organizations | Settling fact/recommendation |
|---|---:|---|
| No bounded-navigation candidate |657|Reachable own-domain index confirmed; no absence asserted|
| Candidate purpose/identity/accessibility |76|Organization-specific reachable index confirmed; candidates individually named in verdicts.csv|
| Feed-only (overlaps accepted organizations) |5|Dedicated feed/article-item overlap confirmed; pages retained|

Manual identity/purpose exclusions include broad Sealed Air/DuPont/Röchling/Honeywell/Datwyler parent pages, Kenda/Nexen technical-center versus tire-company indexes, Prospect Group versus Prospect Mold, Terry versus Tederic, Beacon versus CleveMed, Rubber Mold Design versus Dalin, broad product divisions, homepage redirects and blog-purpose ambiguity. No identity/scope/vocabulary ruling self-applied. Regional routes Spazzolplastica /us/, Hankook /us/, Yokohamaiaohio own domain and BoleAmerica own domain distinguish their own regional indexes.

Calibration inherited the same standard-library fetcher already tested on Avient,RPM,GEON; --live freshly repeats all3 expected URL discoveries for this pass. Default self_check verifies saved results, not fresh fetching. Prior PR145 Codex/Grok v1 REFUTE lessons are built in before this pass: RSS item/Atom entry-only overlap, comments-feed rejection, same-domain home-redirect rejection, conservative parent/tag/template holds. Defect injections prove each rejection, plus403/off-domain/emptyfeed. No new scripts/ change or dependency.

Checks: build applied50 cells/39 orgs; immediate second run0cells/0shards. Fresh3knownanswers,self_check full772-frame reconciliation, final50-URL refetch and validate0 must pass before push; results in refetch.json. Review status: final Codex/Grok clerk refutes pending; no Done claim.

## Potential staleness leads

Only pre-2024 fully parsed dates occur in the following saved index samples (up to12 distinct dates; nonstandard dates may be missed). Candidate liveness signals only, not newest-release/closure assertions. Old newsrooms still qualify under B-NEWS. Posted to BOARD for L8, no liveness/status fields changed.

| Active organization | Parsed date sample |
|---|---|
| ORG-000156 Swagelok | July 31, 2022 |
| ORG-000174 Vertex, Inc. | October 26, 2018;June 3, 2021;June 5, 2017 |
| ORG-000251 Bole Machinery Inc. | Sep 22, 2023;Aug 18, 2023;May 15, 2023;May 12, 2023;April 17, 2023;April 15, 2023;April 14, 2023;Mar |
| ORG-000340 Flambeau, Inc. | July 23, 2023;February 20, 2023;February 2, 2023;May 16, 2022;March 7, 2022;January 6, 2022;December |
| ORG-000405 Keener Rubber Company | 6/15/2000;7/25/2000;11/15/2000;1/18/2001;1/25/2001;10/2/2001;2/19/2002;5/15/2002;7/23/2002;July 23,  |
| ORG-001327 AltraSet Composite Technologies | Feb 18, 2019 |
| ORG-001717 FlexLink, LLC | March 28, 2016 |
| ORG-001830 Impact Sleeve | May 10, 2017 |
| ORG-001937 Smetzer's Tire Center, Inc. | March 28, 2014 |
