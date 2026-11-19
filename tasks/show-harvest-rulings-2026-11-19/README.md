# Owner rulings 2026-11-18c applied to held series (2026-11-19)

**+98 attendee rows** in `data/event_participation.csv` (1,348 → 1,446): EVT-000035 SAMPE Conference &
Exhibition, 2026 edition (Seattle WA, April 27–30, 2026), one row per organization. All tier A (the organizer's own
list). No organization, event or other row is added or changed. The rulings (`tasks/owner-rulings-2026-11-18c/`)
are written into SCHEMA v1.16.1 §4.12.2 in this PR.

## What the rulings admit, and what this pass reads

1. **SAMPE 2026's company list.** SAMPE's sponsorship brochure for the 2027 show prints "SAMPE 2026 | April 27-30,
   2026. INDUSTRY LEADERS WERE HERE. Attendees represented the organizations advancing aerospace, defense, ...",
   then 800 organization names and no people. Under the ruling, an organizer's complete company list for a named
   edition counts wherever the organizer prints it. It is the only list in `ATTENDEE_LISTS`. SPE International
   Polyolefins 2026 stays out: its workbook names delegates (first name, last name, title, organization), and
   delegate lists never mint.
2. **Logo alt text.** A name the organizer wrote as a logo's alt or title text is on the list; a name rebuilt from a
   link URL or image file name is not. Across every list of a held series in waves 1–3, 7 names appear only as alt
   text and match one organization by legal name. 6 are already held (C4 Polymers, Nanoxplore and JEG Plastics at
   AMI 2026, under both staging keys), and 1 is on NPE's media-partner page, which never mints sponsors. So this
   ruling adds no row on held series; it matters for the new-series pass.

**Narrow by design.** The pass reads only the evidence these rulings newly admit: alt-text-only names, plus the one
attendee list. Every visible name on every other list was already judged by waves 1 and 2–3 and their reviews, so
no row those reviews removed (Continental, Coperion, Trelleborg and others) can come back.

## Method (`build.py`)

`python3 tasks/show-harvest-rulings-2026-11-19/build.py --data-dir data --harvest <staging> --conferences ../conferences`
(dry run; `--apply --i-am-the-integrator` appends). It reuses the wave 2–3 gates (`tasks/show-harvest-w23-2026-11-18/`):

- a legal-name match to exactly one active/unknown organization; trade-name hits are held (`trade_name_holds.csv`, 21);
- the abroad country rule; the controller drop lists of waves 1 and 2–3; that pass's review holds;
- the media-partner, not-event-list and combined-list exclusions, plus wave 1's AMI umbrella mapping;
- the list's own edition year (2026 here; SAMPE 2026 is past, so there's no pre-show note).

**Held by the controller before review** (`CONTROLLER_HOLDS`), the way the wave 2–3 review held "Trelleborg" and
"ACS Group":
- "Arkema", "Evonik" and "Henkel" are bare group names whose Atlas records are US subsidiaries;
- "Alpha Technologies" is a name several unrelated companies use.

| Not minted | Names |
|-|-|
| No Atlas organization (kept in staging) | 690 |
| Trade-name hit, held | 21 |
| Held by the controller | 4 |
| Already held | 7 |

## Checks

- `python3 scripts/validate.py` exits 0 (1,446 participation rows).
- `python3 tasks/show-harvest-rulings-2026-11-19/check.py` exits 0. It confirms:
  - the table matches the packet;
  - `sources` cites `evidence_source_url`;
  - each listed name is the legal name of exactly the row's organization;
  - attendee rows come only from `ATTENDEE_LISTS` and carry its note;
  - other rows must be alt-text names;
  - no held name appears;
  - each row's show is a series of its event.
- `python3 tasks/show-harvest-rulings-2026-11-19/negative_controls.py`: 7 of 7 planted defects fail `check.py` with
  their expected message.
