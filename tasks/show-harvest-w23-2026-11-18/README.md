# Show harvest, waves 2 and 3 (2026-11-18)

**+52 exhibitor rows** in `data/event_participation.csv` (1,296 → 1,348), for 5 event series already held in
`data/events.csv`. All tier A (the organizer's own published list, SCHEMA §4.12.2). No organization, event or other
row is added or changed.

| Event | List year | Rows | Source |
|-|-|-|-|
| EVT-000001 NPE: The Plastics Show | 2027 | 24 | Map Your Show list: the A–B entries plus NPE's featured exhibitors, 200 of 1,749 (partial; pre-show) |
| EVT-000017 SPE Annual Blow Molding Conference | 2026 | 17 | blowmoldingdivision.org ABC 2026 exhibitors |
| EVT-000069 Plastic Pipes Conference (PP XXIII, The Woodlands TX) | 2027 | 4 | ppxxiii.com exhibition map (pre-show) |
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
  active/unknown organization. A hit on a trade name is held in `trade_name_holds.csv` for review, because
  `trade_names` carries brands, parents and subsidiaries (#252 credited Coperion to Hillenbrand that way). Of the 8
  trade-name hits, the review added 2 (below) and 6 stay held.
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
| Trade-name hit, held (`trade_name_holds.csv`) | 6 |
| Legal-name hit held by the cross-family review (`review_decisions.csv`, `hold`) | 5 |
| Already held | 59 |

**Attendees.** SPE International Polyolefins 2026 publishes a delegate workbook (first name, last name, title,
organization): a delegate list naming people never mints (owner ruling 2026-11-09). SAMPE 2026's company-only list
("Industry leaders were here", 800 organizations) is printed in a sponsorship brochure; whether that counts as an
organizer-published attendee list or a brochure line is an owner question, so nothing is minted from it.

## Cross-family review (2026-11-18)

Codex (deep) and agy (Gemini 4 Hydrogen, XHigh) each reviewed all 55 first-build rows and the 8 trade-name holds
from an evidence packet: the org record and a page excerpt for every row. Both returned SHIP-WITH-FIXES.

- **Held, both families (5):** "Trelleborg" and "iNOEX" at PP XXIII (bare group or brand names; NPE's "iNOEX, LLC"
  stays), "Aaron Industries, Inc." at NPE (the company calls itself a Corporation), "ACS Group" at NPE (a family of
  brands), "Hultec" at PP XXIII (a brand over four companies). Recorded as `hold` in `review_decisions.csv`.
- **Added, both families SAME (2):** "Baystar" at NPE and at PP XXIII → Bayport Polymers LLC (the brand's privacy
  policy names the LLC; NPE's profile gives Pasadena TX). Recorded as `accept` in `review_decisions.csv`, valid
  only for that event, year, listed name and organization; the notes say so.
- **Fix confirmation (codex, deep):** the data delta was exactly the five holds and two adds. It refuted the first
  enforcement: the overrides were not keyed by edition year or organization, and `check.py` trusted a phrase in the
  notes (a held Blueshift row with "NOT adjudicated …" in its notes passed). Both now read `review_decisions.csv`
  keyed by event (or show), role, year, name and org; that Blueshift row, a held row and an accepted name in the wrong
  year all fail `check.py`. The rebuilt rows are byte-identical to the reviewed fix.
- **Second confirmation (agy and codex, both REFUTE):** the decision file itself was not validated. A malformed or
  duplicate row could be overwritten by a later one, empty fields passed, `event_id` and `show_key` were never
  cross-checked, holds ignored the organization, and `check.py` compared held names raw instead of normalized.
  Fixed as one rule, not case by case: `decisions.py`, shared by `build.py` and `check.py`, refuses the whole file on
  any bad row (8 non-empty fields; hold/accept; role; 4-digit year; show_key's series = event_id; a held org; a unique
  key; a hold names the org whose legal name it is, an accept the org whose trade name it is), and every decision binds
  only its organization. The data is unchanged.
- **Third confirmation (agy REFUTE; codex's run was stopped by the machine's low-memory guard):** show keys were not
  validated (a trailing space or a missing year passed), the year accepted non-ASCII digits, `check.py` ignored the
  show key and read inactive organizations. Fixed by the controller directly (same defect class three rounds
  running): ASCII-only fields, no surrounding spaces, `show_key` of the form `<slug>:<year>`, uniqueness at show and
  at event grain, active/unknown organizations in both scripts, and `check.py` reads each row's show key from its
  notes. A hold binds the event whatever show listed the name; an accept binds only its exact show.
  `negative_controls.py` now runs 22 reviewer counterexamples, and each fails `check.py`. The data is unchanged
  (rebuilt rows byte-identical to the reviewed fix).
- **Still held (6):** Blueshift and Cambium (codex: same, citing their legal pages; agy: unsure), Alpek Polyester,
  3A Composites Core Materials, Airtech Advanced Materials Group, Brighton Science (both unsure or split).
- **Split, kept (2):** agy would also drop "Atomic Industries" and "Fiber Dynamics" for lack of profile text. Codex
  checked Atomic Industries' own site, which matches the Warren MI record, and found no other company of that name.
  Fiber Dynamics is named outright in the joint entry "NIAR | Fiber Dynamics | FILL USA INC", which the row's notes
  now quote.
- **For the integrator, not this PR:** codex noted Brighton Science's terms name Brighton Technologies, LLC, while
  the record says Brighton Technologies Group, Inc. agy noted record gaps: ORG-007105 has no HQ, ORG-003769 has no
  city, and ORG-003278 has `hq_country` "United States" rather than "US".

## Follow-ups (not in this PR)

- The 107 untracked series: most fail the named-subject test (material-agnostic shows such as Formnext, Compamed, IMTS,
  Pack Expo). The ones that pass are added in their own PR, then backfilled from the banked harvest.
- SAMPE 2026 attendee list: after the owner rules.
- 146 wave-3 editions were not harvested (owner decision).
