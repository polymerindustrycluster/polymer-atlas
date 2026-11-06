# L9 newsroom navigation — Tier-1, 2026-11-06

Claim atlas-L9-newsroom; branch agent/codex/newsroom-urls, PR145. Controller delegated application of newsroom_url/newsroom_feed_url. First user: existing news-monitor operator (L8/controller), usable after merge; no new operator system.

## Scope and provenance

Controller ruling superseded initial100-org proposal: first pass attempts all active organizations with tier1_qualifier nonempty and website, column as-is despite pending derivation. **Named canonical source snapshot9d69978:1261 active tier1 organizations,1049 with website,212 without.** All1049 IDs and canonical website values exactly equal inputs.csv. Nine existing canonical routes changed and six previously website-blank tier1 records gained websites after initial snapshot: all15 routes re-fetched; superseded-route-attempts.json preserves the9 old route histories. Each current canonical-route discovery <=6 requests; new canonical evidence justified reopening those route holds. No six-record omission remains.

Six added input IDs: ORG-004065,004069,004079,004083,004084,004085. Each attempted and STILL_UNCERTAIN; no absence or closure asserted. No website supplied for212 source-snapshot tier1 organizations, outside fetch frame. PIC18 non-tier1 and other classes are separate PR152/169, not part of this pass. Source manifest is frozen at9d69978; later parallel creates are outside it. Current accepted-row eligibility and website assertions still run on fresh main.

Primary sources: each canonical own website and directly linked news/press/announcements index; exact routes/statuses in discovery.json, text date samples in audit.json, one disposition/input in verdicts.csv. Navigation aids under SCHEMA4.4/v1.11/V-58 require no EVD, never evidence themselves; EVD230000–239999 unused. No new records/dedupe/ID allocation/inclusion decisions. No status,tier,liveness,registry,derived,LinkedIn or evidence fields authored.

## Acceptance and repeatable checks

Hold homepage redirects,parent/division/publisher mismatches,tag/template/post uncertainty and unavailable routes. Accept reachable own-domain organization-specific news indexes; final URL must remain stored path (trailing slash tolerated). Feed must parse RSS/Atom with >=1 article entry and link an article also linked from selected index. Channel/feed metadata and comments never establish overlap. Builder preflights all shards and refuses conflicting cells,website/scope changes,off-domain/comment URLs before writes. Re-fetch first asserts current canonical data equals packet and eligibility remains active/tier1.

```
python3 tasks/newsroom-urls-2026-11-06/self_check.py --live
python3 tasks/newsroom-urls-2026-11-06/build.py
python3 tasks/newsroom-urls-2026-11-06/check.py
python3 scripts/validate.py
```

Calibration:3 fresh known-answer discoveries (Avient/RPM/GEON) PASS. Default self_check checks saved calibration; --live actually re-fetches. Injected403,off-domain,emptyfeed,channel-home false match,comments and same-domain homepage redirects all rejected. **New coverage gate recomputes all4945 canonical organization rows at immutable9d69978,1261/1049/212 counts,exact eligible IDs and canonical website values; injected historical six-ID omission fails this gate.** Packet reconciliation alone is not claimed as canonical coverage.

## Final counts and holds

Unit/filter: active organizations in frozen priority cohort. Attempted tier1=1049,PIC18 non-tier1=0,other=0. **115 tier1 organizations:115 newsroom pages+41 feeds=156 previously empty cells,28 organization shards.** Other class fills0. Existing tiers unchanged:A=36,B=72,C=6,U=1.934 organization holds:701 no bounded-nav candidate,233 candidate identity/purpose/accessibility.20 overlapping feed-only holds. No inclusion_log changes.

| Hold class | Active organizations | Still needed before a fill |
|---|---:|---|
| No bounded-nav candidate |701|Still need a reachable own-domain newsroom index; none confirmed by this bounded route|
| Candidate identity/purpose/accessibility |233|Still need organization-specific maintained index/publisher confirmation; held candidate URL is in verdicts.csv|
| Feed-only, overlaps accepted orgs |20|Still need dedicated article feed/overlap confirmation; page retained, feed empty|

Specific holds: Oregon Rubber Mills004556 template placeholder; Duraco004418 tag archive; Mississippi004620 index purpose; Thorpe004287 canonical identity; Proviron004605 global feed for regional index; Kaneka003079 holding-company newsroom; BOGE004161 global German index and AP Nonweiler004606 platform publisher. None is self-ruled as a scope/identity change.

Kaneka own /kaneka-americas/our-company/ explicitly distinguishes North America as a subsidiary of Americas Holding. Holding-company /kaneka-americas/newsroom/ is therefore held under SCHEMA4.4 parent bar; no ownership repair made. PCI004274's own home page explicitly identifies Petroleum Containment Inc (PCI); its index accepted,root feed held for no article overlap. Shintech003186's corrected own-site index accepted. These are the only two additions after v3; Kaneka removed.

## Checks and review response

Final re-fetch: **PASS115 active organizations;156 URLs,all HTTP200 and feeds nonempty**,same path/domain and article-item overlap; refetch.json lists all outcomes. Build repeat0cells/0shards. Validator0errors,V-58 clean. Current-main field-boundary proof156 emptycells/115 existing IDs/only two target columns. Core suite earlier221 tests OK(1 skipped),scripts/ untouched. Branch history is pre-pass backup; README pass journal.

Codex and Grok original deep v1 REFUTE: channel/feed metadata falsely counted as article overlap,Synray comments feed; fixed and defect-injected. Additional Grok same-domain redirect and four ambiguous index/identity holds applied. v3 was114pages+41feeds=155cells and1043 stale input IDs; superseded by this packet.

Codex clerk1 FINALv3 REFUTE: Kaneka parent publisher and missing six source-snapshot IDs. Both substantiated independently; Kaneka held,six fetched,all9 changed routes refreshed,immutable canonical census plus historical-defect injection added.

Grok clerks1/3 FINALv3 REFUTE: same frame gap,Kaneka parent (clerk1),hold-table ambiguity and stale-table contradiction. Fixed: hold table now explicitly states what is still needed,not that held indexes were confirmed; staleness table below lists **only current VERIFIED indexes**,all held rows removed. Final corrected two-family rereviews pending; no Done claim.

Latest integration replay pinned 85b85600c77e72c91fde772b0cf3c25e51c321ab; exact main organization shards restored and builder replayed,preserving all upstream state-wave,ownership,markets,registry changes. No CSV conflict hand-merged; no net federal-frame diff vs main. Source snapshot stays9d69978 while current eligibility/value checks use integrated data.

## Potential staleness leads

Only currently VERIFIED navigation indexes appear below. Saved samples contain only pre-2024 fully parsed dates (up to12 dates; nonstandard dates can be missed). They are candidate liveness leads,not newest-release or operating-status assertions. MFG004451 alone had latest listed item manually confirmed2023-10-26. BOARD/L8 informed; no liveness/status fields changed. Held Oregon,Mississippi,Thorpe pages are absent.

| Active organization | Date sample |
|---|---|
| ORG-000138 Permatex | February 14, 2020;December 21, 2018 |
| ORG-000430 Mar-Bal Inc. | August 9, 2021;February 24, 2020;February 8, 2021 |
| ORG-000451 Molded Fiber Glass Companies | October 26, 2023;October 5, 2023;August 21, 2023;August 7, 2023;November 17, 2022;October 7, 2022;Ja |
| ORG-000835 Fiber-Tech Industries, Inc. | July 30, 2019 |
| ORG-000868 Guardian Manufacturing Company | June 22, 2018;April 5, 2018;September 27, 2018 |
| ORG-001080 Ridge Corporation | September 30, 2021;September 28, 2019;July 26, 2019;January 29, 2018;July 26, 2017;February 29, 2016 |
| ORG-002174 Parker Rust-Proof of Cleveland | 07/08/2022;3/19/2020;2/26/2020 |
| ORG-002401 Mi Windows & Doors Inc. | November 10, 2022;November 02, 2022;October 17, 2022;September 13, 2022;September 07, 2022;August 22 |
| ORG-002497 The Murus Company | March 15, 2013 |
| ORG-003132 Seasafe, Inc. | Apr 20 2021;April 20, 2021;Jan 25 2021;January 25, 2021;Mar 19 2020;March 19, 2020;Apr 30 2018;April |
| ORG-003183 AmFine Chemical Corporation | November 12, 2015;June 4, 2014;April 11, 2014 |
| ORG-003194 REXtac, LLC | June 7, 2022;January 1, 2022;December 16, 2021;June 22, 2021;August 20, 2020;April 11, 2019;December |
| ORG-003219 Covation Biomaterials LLC | May 11, 2023 |
| ORG-003952 Augusta Fiberglass Coatings, Inc. | October 20, 2016;September 6, 2016;July 22, 2016;January 6, 2016;December 10, 2015 |
| ORG-003989 General Plastics Manufacturing Company | May 15, 2019;Oct 20, 2015;September 8, 2015;Oct 6, 2014;October 07, 2014;October 2, 2014;September 2 |
| ORG-004137 R3 Composites Corp | Feb 11, 2021 |
| ORG-004291 Viskase Companies, Inc. | May 31, 2022;February 8, 2022;January 4, 2022;October 6, 2021;April 16, 2021;April 15, 2021;November |
| ORG-004386 Dicar Inc | May 31, 2022;Mar 23, 2020;March 22, 2020;Mar 20, 2020;Feb 22, 2019;Sep 28, 2018;Jul 18, 2018;Apr 19, |
| ORG-004533 Bomar Specialties, LLC | January 31, 2023;May 4, 2022;January 31, 2022;June 8, 2021;April 5, 2021;November 2, 2020 |

Cross-PR coverage gate now PASS against named source9d69978:1049+772+2258=4079 disjoint IDs,exactly all active organizations with website at that snapshot. No missing/extra IDs. Later-main creates excluded by frozen manifests,not claimed as attempted. Current proposals across PR145/152/169:321 newsroom pages+141 feeds=462 URLs in321 active organizations;3758 explicit organization holds.
