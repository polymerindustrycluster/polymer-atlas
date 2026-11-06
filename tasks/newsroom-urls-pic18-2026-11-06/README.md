# L9 newsroom round2 — PIC18, 2026-11-06

Controller BOARD06:30 continuation, branch agent/codex/newsroom-urls-pic18,PR152. NEW separate pass from PR145/169; integrator delegation only newsroom_url/newsroom_feed_url. First user:existing news-monitor operator(L8/controller),usable after merge;no new operator system.

## Scope and sources

Named source snapshot9d69978:772 distinct active organizations with website,tier1_qualifier empty,>=1 physical OH site in PIC18. County suffix normalized;regions.py controls region. Frozen inputs/discovery/verdicts all772;independent snapshot frame recomputed from canonical tables. Current builder/check revalidate each accepted record's website,active status and packet values; frozen source census governs membership. Later parallel creates outside manifest. Priority counts:attempt tier1=0,PIC18 non-tier1=772,other=0.

Primary sources are held own websites and linked news/press indexes. discovery.json records <=6 initial discovery requests/org and115 candidates;audit.json raw visible-text date samples;verdicts.csv one disposition/input. No full website/sitemap crawl;route failure never absence/closure. No private/licensed/contact data. SCHEMA4.4/V-58 navigation aids need no EVD;block unused. No records created,dedupe/ID allocation/inclusion decisions;no tiers,status,liveness,registry,derived,LinkedIn or evidence fields authored.

## Gates and results

Accept own organization-specific news/press/announcements indexes;hold home redirects,parent/publisher/brand mismatches,template/tag/post/changelog uncertainty and unavailable routes. Exact parsed URL components required except path trailing slash;query and fragment preserved. Feeds RSS/Atom>=1 article,item permalink also linked from selected index;channel/feed metadata/comments excluded. Builder preflights all affected shards/conflicting cells before writes. Branch history is pre-pass backup,this README pass journal. No CSV conflict hand-merged;latest main c2674712c0c9f8aeefac9179597b8a4c6e5eda5f integrated by exact-main organization files plus builder.

```
python3 tasks/newsroom-urls-pic18-2026-11-06/self_check.py --live
python3 tasks/newsroom-urls-pic18-2026-11-06/build.py
python3 tasks/newsroom-urls-pic18-2026-11-06/check.py
python3 scripts/validate.py
```

**38 active organizations in the frozen PIC18 cohort:38 pages+11 feeds=49 empty cells/4 shards.** Other priority classes0. Unchanged source tiers:A=15,B=17,C=6,U=0.734 organization holds:657 no bounded-nav candidate,77 candidate identity/purpose/accessibility.5 overlapping feed-only holds:Vertex,BaseTek,Flambeau,Godfrey&Wing,iCHOR(no article overlap). No inclusion_log changes.

| Hold group | Active organizations | Still needed before fill |
|---|---:|---|
| No bounded-nav candidate |657|Still need reachable own-domain newsroom index;none confirmed by bounded route|
| Candidate purpose/identity/accessibility |77|Still need organization-specific maintained news index/publisher confirmation|
| Feed-only,overlaps accepted orgs |5|Still need dedicated article-feed overlap confirmation;page retained,feed empty|

Parent/home/purpose exclusions include broad SealedAir/DuPont/Röchling/Honeywell/Datwyler pages,Kenda/Nexen technical-center versus tire-company indexes,ProspectGroup versusProspectMold,Terry versusTederic,Beacon versusCleveMed,RubberMoldDesign versusDalin and ambiguous blogs. No scope/identity ruling self-applied. Filled regional sources include Spazzolplastica /us/,Yokohamaiaohio andBoleAmerica. **Hankook000204 remains held**,both cells empty;its candidate was not filled.

Checks:build49cells/38orgs,immediate repeat0cells/0shards;self_check --live3 fresh known answers plus immutable772frame reconciliation and defect injections PASS;check.py **PASS38 active organizations;49URLs,allHTTP200 and feeds nonempty**;validate.py0errors,V-58clean. Immutable-main boundary only49 previously empty cells/38 existing IDs/two named columns. scripts/ unchanged,no new dependencies.

## Refute responses

Codex3 REFUTE on c71bb0f:full-URL rstrip erased a slash inside query values. Exact actual-Plastipak reproduction run before fix and showed false acceptance;after fix it raises the specific redirect assertion. All URL comparisons now use urlsplit keys,normalizing only path trailing slash,including feed article overlap. Negative tests reject query52→52/ redirects and different article query values;benign path-only slash still accepted. Applied same root fix to allthree checkers,not a Plastipak-specific exception.

Grok3 REFUTE on c71bb0f:Keener000405 is website maintenance history,not confirmed organization-news index;held andcellcleared. This is purpose uncertainty,not old dates or closure. Hankook prose corrected to held. Known valid Pretium feed took32.3s in reviewer fetch:fetch cap raised18→45s(connect8s unchanged),bounded final49URL gate passes. Initial discovery attempts used18s;timeout is never evidence of absence.

All original findings fixed or held. Final corrected two-family rereviews pending;draft/no Done claim. Previous39page/50cell/733hold figures superseded. All772 source IDs still attempted;holds unresolved,not silently skipped.

## Potential staleness leads

Only current VERIFIED indexes listed;Keener removed. Samples have only pre-2024 fully parsed dates(up to12 dates,nonstandard dates may be missed). Candidate liveness signals only,not newest-release/operating-status claims. B-NEWS allows old newsrooms;BOARD/L8 informed,no status fields changed.

| Active organization | Date sample |
|---|---|
| ORG-000156 Swagelok | July 31, 2022 |
| ORG-000174 Vertex, Inc. | October 26, 2018;June 3, 2021;June 5, 2017 |
| ORG-000251 Bole Machinery Inc. | Sep 22, 2023;Aug 18, 2023;May 15, 2023;May 12, 2023;April 17, 2023;April 15, 2023;April 14, 2023;Mar |
| ORG-000340 Flambeau, Inc. | July 23, 2023;February 20, 2023;February 2, 2023;May 16, 2022;March 7, 2022;January 6, 2022;December |
| ORG-001327 AltraSet Composite Technologies | Feb 18, 2019 |
| ORG-001717 FlexLink, LLC | March 28, 2016 |
| ORG-001830 Impact Sleeve | May 10, 2017 |
| ORG-001937 Smetzer's Tire Center, Inc. | March 28, 2014 |

Controller frame instruction: frozen9d69978 membership governs; rank was ordering only. Runtime rank/region guards removed; frozen772 census, current active status, exact canonical website, own publisher/domain and value-conflict preflight retained. Pretium ORG-000523 gained national_footprint tier1 on later main, but stays in this frozen PIC18 cohort under that instruction. No tier1 edits by L9. Current-main542629e replay originally stopped on that runtime guard before writing; after the controller-directed guard removal it applies the same38-page/11-feed packet.

Latest integration replay pinned d1e618b06ae71588e80d117b042cf5c0308e0d50:all main organization shards restored+builder replayed;49 previously empty cells/38existing IDs/4shards,only2navigation fields,no row loss. Builder0,selfcheckPASS,validator0;researchpacket unchanged.

Grok3 **APPROVEc347c2519afc27c1ecb7b477f5646e9fe203a697,0 findings**, superseding its c71bb0f REFUTE: Keener held/empty and removed from staleness, Hankook held, query redirect and article-link mutations rejected while path-only slash passes. Reviewer independently confirmed772 frozen IDs,38pages+11feeds49emptycells/734holds,self_check --live,full49URL check,builder0,validator0,row-loss guard. Report: controller ledger reviews/152-clerk-grok-3-rereview.md. This approval covers the corrected research packet and query fix at c347c25; the later controller-directed frozen-frame guard change at f36fdbd remains under focused two-family re-review already queued. No final approval of that code change is inferred from this older-head verdict.
