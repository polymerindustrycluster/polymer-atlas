# Owner rulings 2026-11-18c applied to held series (2026-11-19)

**+92 attendee rows** in `data/event_participation.csv` (1,348 → 1,440): EVT-000035 SAMPE Conference &
Exhibition, 2026 edition (Seattle WA, April 27–30, 2026), one row per organization. All tier A (the organizer's own
list). No organization, event or other row is added or changed. The rulings (`tasks/owner-rulings-2026-11-18c/`)
are written into SCHEMA v1.16.1 §4.12.2 in this PR.

## What the rulings admit, and what this pass reads

1. **SAMPE 2026's company list.** SAMPE's sponsorship brochure for the 2027 show prints "SAMPE 2026 | April 27-30,
   2026. INDUSTRY LEADERS WERE HERE. Attendees represented the organizations advancing aerospace, defense, ...",
   then the organization list: 800 extracted entries, a few of them heading fragments or names split across lines,
   and no people. Under the ruling, an organizer's complete company list for a named edition counts even in its own
   brochure. It is the only list in `ATTENDEE_LISTS`, bound there to EVT-000035. SPE International Polyolefins 2026
   stays out: its workbook names delegates (first name, last name, title, organization), and delegate lists never
   mint.
2. **Logo alt text.** A name the organizer wrote as a logo's alt or title text is on the list; a name rebuilt from a
   link URL or image file name is not. `build.py` reads real `alt` and `title` attributes with Python's HTML parser,
   never `src`, `href` or `data-*` text. Across every list of a held series in waves 1–3, 7 names appear only as alt
   text and match one organization by legal name. 6 are already held (C4 Polymers, Nanoxplore and JEG Plastics at
   AMI 2026, under both staging keys), and 1 is on NPE's media-partner page, which never mints sponsors. So this
   ruling adds no row on held series; it matters for the new-series pass.

**Narrow by design.** The pass reads only the evidence these rulings newly admit: alt-text-only names, plus the one
attendee list. Every visible name on every other list was already judged by waves 1 and 2–3 and their reviews, so
no row those reviews removed (Continental, Coperion, Trelleborg and others) can come back.

## Method (`build.py`)

`python3 tasks/show-harvest-rulings-2026-11-19/build.py --data-dir data --harvest <staging> --conferences ../conferences`
(dry run; `--apply --i-am-the-integrator` appends). It reuses the wave 2–3 gates (`tasks/show-harvest-w23-2026-11-18/`):
- legal-name match to exactly one active/unknown organization; trade-name hits are held (`trade_name_holds.csv`, 21);
- the abroad country rule;
- the controller drop lists of waves 1 and 2–3, and that pass's review holds;
- the media-partner, not-event-list and combined-list exclusions, and wave 1's AMI umbrella mapping;
- the list's own edition year (2026; SAMPE 2026 is past, so there's no pre-show note).

**Held by the controller (`CONTROLLER_HOLDS`).** As the wave 2–3 review held "Trelleborg" and "ACS Group", these
listed names don't pin one legal entity. Each hold binds its name at the event in every role, year and organization.
- **Bare group or brand names whose Atlas record is one national entity of a group with others:**
  - Arkema, Evonik, Henkel (held before review);
  - United Initiators, Microtex Composites, Hauschild SpeedMixer, Sun Chemical (after review).
- **Names several unrelated companies use:**
  - Alpha Technologies (held before review);
  - Advanced Composites, Specialty Materials (after review). Codex found a second Advanced Composites, Inc., in
    Salt Lake City, which works with SAMPE; the Atlas record is a Sidney OH compounder.

| Not minted | Names |
|-|-|
| No Atlas organization (kept in staging) | 690 |
| Trade-name hit, held | 21 |
| Held by the controller | 10 |
| Already held | 7 |

## Cross-family review (2026-11-19)

Codex (deep) returned DO-NOT-SHIP and agy (Gemini 4 Hydrogen, XHigh) SHIP-WITH-FIXES on the 98-row first build.
Both confirmed that the SCHEMA additions express rulings 1 and 2, and found no person among the rows.

**Applied:**
- 6 more holds (above).
- Alt text is read from real attributes only; a name inside an `href` query or a `data-alt` value no longer counts.
- `check.py` now also enforces:
  - the combined-list exclusion, and the controller drop lists;
  - the SAMPE list bound to its own event;
  - no duplicate (event, org, year, role) anywhere in the table;
  - an empty `role_detail` on attendee rows, and no personal pattern in any `role_detail`.
- Holds bind their name at the event in every role.
- A None-safe `role_detail`.
- SCHEMA wording: "or prospectus" dropped (the ruling says brochure), the earlier blanket sentence now reads "lines
  that name only some companies", and the row-note requirement is stated.
- "800 organization names" corrected to 800 extracted entries.

**Recorded for the integrator, not this PR:**
- TA Instruments (a Waters division) and Collins Aerospace (an RTX business) are business-unit records.
- SMR Technologies' trade names show a different current legal form.
- Four matched records have no HQ: Copps Industries, Mosites Rubber, Professional Plastics and Toray Advanced
  Composites.

## Checks

- `python3 scripts/validate.py` exits 0 (1,440 participation rows).
- `python3 tasks/show-harvest-rulings-2026-11-19/check.py` exits 0. It enforces every `build.py` rule that repo data
  can show (listed in its docstring).
- `python3 tasks/show-harvest-rulings-2026-11-19/negative_controls.py`: 14 of 14 planted defects fail `check.py`.
  Each must fail with its expected message, and each planted row must fail for that one reason only. The one
  exception is the drop-list control: a dropped page label is never an organization's legal name, so the name
  checks fire too.
