# L9 newsroom navigation — 2026-11-06

Claim: atlas-L9-newsroom; branch agent/codex/newsroom-urls; PR145. Controller delegated application of two navigation columns. First user: existing news-monitor operator (L8/controller), usable after merge. No new operator system.

## Scope and provenance

Controller ruling supersedes proposed 100-org cap: first PR attempts every active organization with tier1_qualifier nonempty and website, column as-is despite pending derivation. Frozen inputs.csv: 1,043 distinct active organizations; 218 of 1,261 active tier1 organizations have no website and are outside fetch frame. PIC-18 non-tier1 and other organizations are subsequent PR scopes. Primary sources: each canonical own website and directly linked newsroom indexes; routes in discovery.json, dates in audit.json, dispositions in verdicts.csv.

SCHEMA §4.4/v1.11 and V-58: navigation aids, never evidence by themselves; no evidence rows or quotes added. EVD-230000–239999 unused. No creates (dedupe/ID allocation/append_sorted inapplicable), no status, tier, liveness, registry, derived, LinkedIn or inclusion_log changes.

## Reproduce and acceptance

```
python3 tasks/newsroom-urls-2026-11-06/self_check.py --live
python3 tasks/newsroom-urls-2026-11-06/build.py
python3 tasks/newsroom-urls-2026-11-06/check.py
python3 scripts/validate.py
```

Accept reachable same-domain organization-specific news/press/announcements indexes. Hold home redirects, parent/division mismatch, ambiguous purpose, unavailable routes. Final URL must remain the stored path (trailing slash tolerated). Every feed must parse RSS/Atom with >=1 item and have an article-item permalink linked from its selected newsroom; channel/feed metadata never establishes overlap; comments feeds barred. Build refuses conflicting nonempty cells, website or eligibility changes, off-domain URLs and comments routes before any writes. Current data values must equal reviewed packet before re-fetch. Branch history is the pre-pass backup; README is the pass journal.

`discover.py` uses exact navigation labels, up to three candidates, advertised alternate feeds or /feed/ and /rss.xml, <=6 discovery requests/org. It retains prior attempts rather than silently retrying. Known-answer live probes Avient /company/news-events, RPM /news/, GEON /news PASS; initial matcher missed Avient “News + Events”, fixed before acceptance. --live freshly repeats these probes; default self_check only checks saved calibration outputs. Injected defects cover HTTP403, off-domain redirects, empty feeds, channel-home false overlap, comments feeds (even overlapping), same-domain homepage redirects. All caught. Date years include copyright; only parsed text date samples are recorded, not liveness evidence. Whole website/sitemap crawling was not done; no matching link never asserts absence.

## Final results

Unit/filter: **active organizations**, mutually exclusive priority buckets, tier1 before PIC-18 non-tier1 before other. Attempted: tier1=1,043; PIC-18 non-tier1=0; other=0. Filled: **tier1=114 organizations with 114 newsroom URLs and 41 feeds (155 empty cells, 27 organization shards); other buckets=0**. Changed organization tiers unchanged: A=37, B=70, C=6, U=1. 929 organization holds, each with settling fact in verdicts.csv. 344 candidate indexes examined. No records created or inclusion decisions changed.

| Hold class | Active organizations | Settling fact |
|---|---:|---|
| No bounded-navigation candidate | 699 | Reachable own-domain newsroom index confirmed |
| Candidate purpose/identity/accessibility | 230 | Organization-specific news-index purpose and reachable final URL confirmed |
| Feed-only holds, overlapping accepted orgs | 19 | Same newsroom article feed confirmed; pages still accepted |

Specific final refute holds (included above):

| Record | Uncertainty / recommendation |
|---|---|
| ORG-004556 Oregon Rubber Mills | Placeholder title [FOCUS AREA 2/3]; confirm this is maintained company news before filling |
| ORG-004418 Duraco | Blog tag archive; confirm scope as company announcements or obtain owner ruling before filling |
| ORG-004620 Mississippi Polymers | Post-shaped slug; confirm multi-item news index, not an individual post |
| ORG-004287 Thorpe Plant Services | Site title Thorpe Specialty Services; confirm canonical identity/alias before filling |
| ORG-004605 Proviron feed | Regional index with global root stream; confirm dedicated regional feed before filling |

## Checks and reviews

- Baseline and final `python3 scripts/validate.py`: **0 errors / OK — validation passed**, V-58 clean, existing warnings only.
- Final `check.py`: **PASS: 114 active organizations; 155 URLs, all HTTP 200 and feeds nonempty**. Final report refetch.json includes article-item overlap counts for every feed.
- `build.py` immediate second run: **0 cells /0 shards written**.
- `self_check.py --live`: full1,043 IDs uniquely reconciled across input/discovery/verdict; <=6 discovery fetches; three fresh known answers; injected defects rejected.
- Existing script suite: **221 tests OK (1 skipped)**. Existing build_site.py SyntaxWarning observed; scripts/ unchanged.
- Final field-boundary check against origin/main: only newsroom_url/newsroom_feed_url, every prior cell empty; row IDs unchanged. No generated exports.

Codex deep v1 **REFUTE**: Synray comments feed and false channel/feed metadata overlap. Substantiated and fixed. Restricted to item/entry article links, explicitly rejected comments, injected regression tests. Removed15 extra feeds (including Synray); initial177 URLs became162.

Grok deep v1 **REFUTE**: same feed defects; same-domain home redirects; Oregon template, Duraco tag, Mississippi index purpose, Thorpe identity, Proviron regional/global feed; static calibration could be mistaken for fresh. Held four organization pages plus their two feeds and Proviron feed; strict same-path check; --live calibration added. Final155 URLs supersedes both earlier figures. No scope/vocabulary/identity ruling self-applied. All findings fixed or held pending confirmation; final two-family rereviews pending, no completion approval claimed.

Controller integration ruling (BOARD06:12) explicitly superseded the hands-off constraint narrowly: take main's exact LF federal-frame files (#139), commit, then merge. Net diff of those files vs main is zero. Merged origin/main9489b60; took all organization shards from main and replayed builder, preserving #128 ownership/evidence changes. No CSV conflict hand-merged. Latest narrowed packet also replayed from main. Catalogue search was incomplete on this Mac (Windows Documents sources absent), not a finding of source absence; canonical held websites supplied the source frame.

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

