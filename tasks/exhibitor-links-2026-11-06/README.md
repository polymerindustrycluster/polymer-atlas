# Exhibitor links, pass 2 (2026-11-06)

The repo owner asked for this pass on 2026-11-06, to sync the conferences list with the Atlas events layer. It records
**organizations only**: no person is named (AGENTS §6), and no attendee list was used.

## Owner ruling, 2026-11-06
Publicly viewable exhibitor rosters may be read even where robots.txt or a platform's terms say otherwise. That
covers Map Your Show (terms section 9), Informa and Deutsche Messe. In the owner's words: "THey are publically viewable
and findable." This pass relies on that ruling for AMI, CAMX, the Battery Show, Ceramics Expo, Foam Expo and Hannover.

## Method
1. **Ten rosters were read in full on 2026-11-06.**
   - **Plain fetch:** six rosters.
   - **Real Chrome (local Playwright):** four Map Your Show and Informa directories. The script kept one name per
     detail page and dropped booth codes and description blurbs.
   - **Snapshots:** banked in staging, as `raw/tradeshows/MANIFEST.md` and `raw/tradeshows/2026-11-06/`, before
     matching.
2. **`names.csv`:** 4,493 names, in the same format as the 2026-11-04 task.
3. **Matching:** `../exhibitor-links-2026-11-04/match.py`, unchanged. It uses an exact `name_key` on legal and trade
   names, and a key held by two organizations is not matched. That gave 338 matches.
4. **`build.py`:** it mints only for series held in `events.csv`. Edition city and dates come from the conferences
   repo's series YAML (organizer-checked), never from the series' home city.

## Applied: `event_participation.csv` +258 rows (organization × event edition)

| Event | Edition | Rows |
|-|-|-:|
| EVT-000020 Foam Expo (includes co-located Adhesives & Bonding names) | 2027 | 80 |
| EVT-000003 Global Polymer Summit | 2027, Cleveland | 62 |
| EVT-000007 AMI Plastics World Expos (umbrella) | 2026, Cleveland | 58 |
| EVT-000014 CAMX | 2027, Anaheim | 52 |
| EVT-000030 Tire Technology Expo | 2027, Hannover | 6 |

- **Skipped as already held:** 42 rows from the 2026-11-04 pass, which read only the first page of each Map Your
  Show gallery.
- **Skipped, no Atlas series:** 38 matches from Hannover Messe, Materials Week, RAPID + TCT, the Battery Show and
  Ceramics Expo.
  - Owner ruling 2026-11-04: RAPID + TCT fails the named-subject test.
  - The others need an `events.csv` row through the normal gate first.
- **Pre-show rosters:** upcoming editions were read while their rosters were still filling (§4.12.2), so later
  re-reads diff against these.
- **Foam Expo:** its 2027 list includes the co-located Adhesives & Bonding Expo exhibitors under one page. They are
  recorded under Foam Expo because that is the roster that names them. A reviewer should decide whether the adhesives
  names belong to EVT-000021.

## Leads, not records: `leads.csv` (4,155 names)
These are exhibitor names with no single exact Atlas match. They are discovery leads for the dedupe and scope test.
Most are out-of-scope suppliers or international companies, and Hannover alone accounts for 2,905 names.
