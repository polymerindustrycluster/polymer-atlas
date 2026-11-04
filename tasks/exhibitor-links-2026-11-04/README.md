# Exhibitor links from organizer rosters (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("scrape the conferences pages in order to link the
companies listed as exhibitors"). It records **organizations only**: `event_participation.csv` never names a person
(AGENTS §6), and attendee lists were not used.

## Method
1. The exhibitor-list URLs came from the conferences refresh lanes: 30 rosters for 2026–2027 editions.
2. Each roster page was fetched rendered, full page, through the NAS Firecrawl (`fetch_rosters.py`).
3. Exhibitor names were taken mechanically from the link text of exhibitor or booth detail links. That gave 1,720
   names from 14 rosters. The other 16 rosters render names without detail links, or behind search or maps (ACHEMA,
   JEC, IPF Japan, Hannover and others), and need a different extraction.
4. Names were matched to organizations by exact `scripts/atlas.py name_key` on legal and trade names. A key held by
   two organizations was not matched (`match.py`). That gave 316 exact matches.

## Applied: `event_participation.csv` +146 (unit: exhibitor rows, organization × event edition)

| Event | Edition | Rows |
|-|-|-:|
| EVT-000021 Adhesives & Bonding Expo | 2027, Atlanta | 79 |
| EVT-000010 Plastics Recycling Conference | 2027, National Harbor | 27 |
| EVT-000007 AMI Plastics World Expos (umbrella) | 2026, Cleveland | 21 |
| EVT-000014 CAMX | 2027, Anaheim | 19 |

- **Edition city and dates** come from the conferences refresh, which read organizer pages and raw-checked every
  quote. They do not come from the series' home city.
- **AMI:** the five co-located AMI expos share one MapYourShow gallery, so those names go to the umbrella event once.
- **Tier A:** the organizer's own published roster is A-equivalent for the fact of participation (SCHEMA §4.12).
- **Partial rosters:** MapYourShow galleries returned only their first page.
- **Skipped:** 84 rows already held, and 86 matches whose series has no Atlas event row: SAMPE, MD&M West and Midwest,
  RAPID + TCT, Chemspec and Automotive Testing Expo. Those series need `events.csv` rows first.

## Leads, not records: `unmatched_exhibitors.csv` (1,404 names)
These are exhibitor names with no single exact Atlas match. Each is a discovery lead for the dedupe and scope test,
never a record on its own. Many are suppliers outside polymer scope (machinery, software), and some are Atlas
organizations under a different styling.

## Next
- Add `events.csv` rows for the five unheld series.
- Paginate the MapYourShow galleries.
- Write per-site extractors for the 16 rosters that yielded no names.
- Run the unmatched names through the dedupe and scope test, PIC-18 first.
