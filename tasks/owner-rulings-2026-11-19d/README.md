# Owner rulings, 2026-11-19d (the #411 owner question and the Muse lead lists)

The repo owner ruled four items in session on 2026-11-19, as multiple choice, each time choosing the recommended
option. This file records each item. The ruling text is separate from how each is applied. Counts are at main 146982b5
unless stated.

## 1. A final registration list as an attendee list (#411's `OWNER_PENDING`)

PCI Magazine, the organizer of the Coatings Trends & Technologies Summit (EVT-000077), publishes "the final list of
registered companies for Coatings Trends & Tecnologies Summit 2026" (sic). The page adds: "This list does not denote the
total number of registered attendees." SCHEMA §4.12.2 admits "a list of attending companies that the organizer itself
published", so #411 held the list for a ruling.

- **Ruled:** it counts. The organizer's final list of registered companies for a named, past edition is a list of
  attending companies. Each row quotes the list's own heading in `notes`.
- Not chosen: registration is not attendance, so the list stays excluded.

## 2. Past editions in the conferences repo

The conferences repo holds no 2024 or 2025 edition of any series, and few past editions of the 27 new series (none for
Coatings Trends 2026). SCHEMA §4.12.2 notes that "the linked conferences repo holds edition dates and place", and the
harvest builds (#384, #411 and this one) fill a row's edition dates, city and state from that repo's edition. Without
the edition, those fields stay empty.

- **Ruled:** add a past edition to the conferences repo only when an Atlas participation row cites it. Each edition's
  quote is re-checked on the organizer's page.
- Not chosen: every past edition the Muse lead lists found (about 22); none, keeping the repo upcoming-only.
- Applied in the conferences repo, not here.

## 3. EXPOPLAST (EVT-000081) after it folded into ADM Montréal

The organizer's release of 15 September 2026, as Muse reported it, says EXPOPLAST no longer runs on its own: it is part
of ADM Montréal. The shared ADM Montréal directory labels the plastics exhibitors "ADM Plastiques 2026" and never
prints "EXPOPLAST".

- **Ruled:** EVT-000081 continues. From 2026, entries the directory labels "ADM Plastiques" count for it. Each row
  cites the organizer's release in `notes`.
- Not chosen: the series ended with its last standalone edition; a new series for ADM Montréal.
- Applied in a later pass, after the release and the directory are banked and read.

## 4. Undated Great Lakes speaker pages

The Great Lakes Coatings Conference's "Technical Presentations" and "Short Course Speakers" pages print no year. #411
admitted the same site's "Companies Attending" page as 2025 because the site menu links it as "Companies attended in
2025".

- **Ruled:** admit the speaker pages as 2025 only if the organizer's own page or menu ties them to 2025. Otherwise
  they are undated lists and mint nothing.
- Not chosen: exclude them whatever the menu says; admit them as 2025 without further evidence.
- Applied in a later pass.

## How item 1 is applied (`build.py`)

`python3 tasks/owner-rulings-2026-11-19d/build.py --data-dir data --harvest <staging> [--apply --i-am-the-integrator]`

**+44 rows** in `data/event_participation.csv` (1,526 → 1,570; EVP-001534 to EVP-001577): 44 organizations as
attendees of the 2026 edition (EVT-000077), all tier A, organization grain only. No other row or file under `data/`
changes.

**The list.** The build reads it from the same banked staging JSON #411 used (read 2026-11-06) and asserts the page's
"final list" heading. The page source still carries the earlier version, commented out: "the list of registered
companies ... as of 9/9/26". The visible text names it final, so no row carries a pre-show note.
- **Completeness:** the build parses the page's list itself, one entry per printed line: 224 lines. The harvest's 224
  names are not the same 224: it omits "E2C", which matches no Atlas organization, and adds the page label
  "More Videos", a controller drop. The build asserts exactly this difference, so any other gap fails it.
- **A name split across two lines:** the page prints "Lintech International" on one line and "LP" on the next. The
  build reads them as one name, "Lintech International LP", which matches no Atlas organization; the shortened form
  would have matched Lintech International LLC. A line that holds only a legal suffix is joined to the line above,
  and the build asserts this is the only such line.
- **Edition fields:** the conferences repo has no 2026 edition of this series yet (item 2 adds it), so
  `edition_dates`, `edition_city` and `edition_state` stay empty, as on #411's nine Coatings Trends 2026 speaker
  rows.

**Gates.** The build applies #411's gates by importing its build:
- the name is on the banked page;
- it is not on a controller drop list and not held by the wave 2–3 review;
- it is not held by #411's `CONTROLLER_HOLDS` at EVT-000077. Those holds are keyed on the name key, so they bind
  every listed form: "BASF Corporation", "Covestro LLC", "Omya, Inc." and "Sun Chemical" stay held;
- it is a legal-name match to exactly one active/unknown organization. Trade-name hits are held
  (`trade_name_holds.csv`, 7).

**One new hold (`HOLDS`).** The list prints a bare "Arkema", and the Atlas record for that name key is Arkema Inc., the
group's US entity. This is rule (i) of #411, and #404 held "Arkema" at SAMPE the same way. The build fails if a hold
matches no listing.

**Kept names.** Many listed names name the US entity itself: "Evonik Corporation", "BYK, USA", "ECKART America LLC",
"Hauschild SpeedMixer Inc.", "IMCD US LLC", "Kaneka North America LLC", "MAPEI CORP", "Nagase America LLC",
"NOF AMERICA CORPORATION", "Synthomer Inc.", "Tosoh USA Inc." and others. Each pins its US entity, since no bare form of
these names is held at EVT-000077. Several listed suffixes differ from the Atlas legal form, for example
"Chem-Materials, Inc." (Chem-Materials Co.), "ECKART America LLC" (Eckart America Corporation) and "MFG Chemical, LLC"
(MFG Chemical Inc.). As in #411, each is kept because its name key, which drops legal suffixes, matches exactly one
organization's legal name.

**Every harvested name accounted for:**

| Outcome | Names |
|-|-|
| row minted | 44 |
| no Atlas organization (including the fragment "LP") | 164 |
| printed name continues on the next line ("Lintech International" + "LP") | 1 |
| trade-name hit, held | 7 |
| held by #411's `CONTROLLER_HOLDS` | 4 |
| held by `HOLDS` (Arkema) | 1 |
| second listing of the same organization ("Brilliant Group" and "Brilliant Group Inc") | 1 |
| controller drop (a person's name in the company slot; the page label "More Videos") | 2 |
| **total** | **224** |

The "no Atlas organization" entries include universities and associations ("AUBURN UNIVERSITY", "Cal Poly SLO",
"Canadian Coatings Association"). The build matches only the organization shards, as every harvest pass so far does;
#411's follow-ups record the `ecosystem.csv` gap.

## Checks

- `python3 scripts/validate.py`: passes.
- `python3 tasks/owner-rulings-2026-11-19d/check.py` re-checks every row without the staging harvest:
  - event, year, role and list;
  - the ruling's note and the staging key;
  - tier A, an empty `role_detail` and empty edition fields;
  - a unique legal-name match;
  - no drop or hold;
  - no duplicate in the table.
- `python3 tasks/owner-rulings-2026-11-19d/negative_controls.py`: 14 of 14 planted defects fail `check.py` with the
  expected message. No control writes a person's name: the drop lists store hashes so that none enters this public
  repo.
- #411's `check.py` and its 25 negative controls still pass with these rows in the table.
- **Limit:** `check.py` cannot prove a name is on the page. `build.py`, which reads the banked page, is the guarantee.

## Review (PR #414)

The first round, on `49761cfd`, had 45 rows. Codex (deep) and agy (Gemini 4 Hydrogen, XHigh) each returned
SHIP-WITH-FIXES, and both found the rule (i) screening clean. Applied:
- **Lintech International (codex, agy):** the page splits "Lintech International LP" across two lines, and the harvest
  kept only the first. The row is gone (45 → 44), and the build now joins a suffix-only line to the line above.
- **Completeness claim (agy, then the controller's exact comparison):** the README said the harvest holds all 224
  entries. It does not: it omits "E2C" and adds "More Videos". The claim was wrong; it is corrected above, not
  silently, and the build asserts the difference.
- **A person's name in a negative control (codex):** the control for a dropped name wrote that person's name into the
  repo. It now uses the page label "More Videos".
- **Edition fields (agy):** item 2 now says what the builds do and quotes SCHEMA §4.12.2's own wording.
- **More asserts (agy):** the build asserts the page's list block and its earlier dated version, and `check.py`
  checks tier A and empty edition fields.
