# Show harvest, waves 2 and 3 (2026-11-18)

**+55 exhibitor rows** in `data/event_participation.csv` (1,296 → 1,351), for 5 event series already held in
`data/events.csv`. All tier A (the organizer's own published list, SCHEMA §4.12.2). No organization, event or other
row is added or changed.

| Event | List year | Rows | Source |
|-|-|-|-|
| EVT-000001 NPE: The Plastics Show | 2027 | 25 | Map Your Show alpha list, read A–B only (partial; pre-show) |
| EVT-000017 SPE Annual Blow Molding Conference | 2026 | 17 | blowmoldingdivision.org ABC 2026 exhibitors |
| EVT-000069 Plastic Pipes Conference (PP XXIII, The Woodlands TX) | 2027 | 6 | ppxxiii.com exhibition map (pre-show) |
| EVT-000047 Fakuma | 2026 | 4 | fakuma-messe.de exhibitor list (edition abroad; see below) |
| EVT-000035 SAMPE Conference & Exhibition | 2027 | 3 | Map Your Show alpha list (pre-show); 37 more matches already held |

## Source

Waves 2 and 3 of the full participation harvest (owner decision 2026-11-06; QUEUE "Full participation harvest"):
69 wave-2 editions and 27 of 173 wave-3 editions (the owner stopped wave 3 after a homepage scan), harvested into
local staging (`_internal/atlas-staging/harvest-2026-11/`, never committed). Retrieved 2026-11-06 to 2026-11-09.
The controller re-checked the files independently before building: file, list and company counts match the lane's
handoff note. Public lists were read under the owner's 2026-11-06 robots/terms ruling (tasks/exhibitor-links-2026-11-06).

## Method (`build.py`)

`python3 tasks/show-harvest-w23-2026-11-18/build.py --data-dir data --harvest <staging> --conferences ../conferences`
(dry run; `--apply --i-am-the-integrator` appends). Same method as tasks/show-harvest-w1-2026-11-06, with the lessons
of that PR's 2026-11-09 review built in:

- **Event** from `events.csv` `pic_events_slug` (schema v1.12).
- **Organization: legal names only.** A name mints only when its `atlas.name_key` is the legal name of exactly one
  active/unknown organization. A hit on a trade name is held in `trade_name_holds.csv` (8 names) for review, because
  `trade_names` carries brands, parents and subsidiaries (#252 credited Coperion to Hillenbrand that way).
- **Edition abroad:** mints only when the list gives the company's country and it equals the organization's
  `hq_country` (74 matched names held). Fakuma's 4 rows are three US-listed US companies and one German-listed
  organization whose record is German-headquartered.
- **Evidence gate:** the name must appear in the visible text of its banked raw page. No held-event list in these
  waves has a logo-only name.
- **Edition year** is the list's own year; notes say when it differs from the staging key's year, and when a list is
  pre-show or partial.

## Not minted, and why

| Reason | Names |
|-|-|
| Series not held in `events.csv` (71 series in these waves, 107 across all three; scope test pending, §4.12.1) | 18,333 |
| Attendee lists (below) | 3,009 |
| No Atlas organization matches (leads, kept in staging) | 3,420 |
| Media-partner lists filed as sponsors (NPE 2027 media partners; K "Cooperating Media") | 60 |
| Not a list for this event (SPE Blow Molding Division 2025 scholarship sponsors, not ABC sponsors) | 10 |
| Edition abroad, listed country missing or not the org's HQ country | 74 |
| Trade-name hit, held for review | 8 |
| Already held | 59 |

**Attendees.** SPE International Polyolefins 2026 publishes a delegate workbook (first name, last name, title,
organization): a delegate list naming people never mints (owner ruling 2026-11-09). SAMPE 2026's company-only list
("Industry leaders were here", 800 organizations) is printed in a sponsorship brochure; whether that counts as an
organizer-published attendee list or a brochure line is an owner question, so nothing is minted from it.

**For reviewers:** bare "Trelleborg" (→ Trelleborg Corp, Pawling NY) and bare "iNOEX" (→ iNOEX LLC) at PP XXIII are
legal-name hits on a group name; say if either should be held.

## Follow-ups (not in this PR)

- The 107 untracked series: most fail the named-subject test (material-agnostic shows such as Formnext, Compamed, IMTS,
  Pack Expo). The ones that pass are added in their own PR, then backfilled from the banked harvest.
- SAMPE 2026 attendee list: after the owner rules.
- 146 wave-3 editions were not harvested (owner decision).
