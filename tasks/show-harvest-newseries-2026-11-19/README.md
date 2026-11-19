# Show harvest: participation rows for the 27 new series (2026-11-19)

**+128 rows** in `data/event_participation.csv` (1,440 → 1,568; EVP-001448 to EVP-001575): 95 organizations at
13 of the 27 series PR #409 seeded (EVT-000072 to EVT-000098). By role: 78 attendee, 38 exhibitor, 6 sponsor and
6 speaker. All tier A (the organizer's own list), organization grain only. No organization, event or other row is
added or changed.

| Series | Rows |
|-|-|
| EVT-000077 Coatings Trends & Technologies Summit, 2026 | 48 attendee, 6 speaker, 1 sponsor |
| EVT-000082 Great Lakes Coatings Conference, 2025 | 30 attendee |
| EVT-000080 European Coatings Show, 2025 (Nuremberg) | 15 exhibitor |
| EVT-000072 AMPP Annual Conference + Expo, 2027 | 11 exhibitor |
| EVT-000074 Carbon Fiber, 2026 | 4 exhibitor, 3 sponsor |
| EVT-000092 RadTech UV+EB Technology Expo & Conference, 2027 | 4 exhibitor |
| EVT-000076 CHINACOAT, 2026 | 3 exhibitor |
| EVT-000073 ArabPlast, 2025 | 1 exhibitor |
| EVT-000079 Eastern Coatings Show, 2027 | 1 sponsor |
| EVT-000098 Waterborne Symposium, 2027 | 1 sponsor |

The other 14 series mint nothing. Their lists are abroad and give no country (China Composites Expo, Meximold,
Plástico Brasil, PRS Europe and India, ICERP), match no Atlas organization, or are held.

## Method (`build.py`)

`python3 tasks/show-harvest-newseries-2026-11-19/build.py --data-dir data --harvest <staging> --conferences ../conferences`

These lists were never read by an earlier pass, so every name on them is judged here. The gates are those of
waves 1 and 2–3 and of `tasks/show-harvest-rulings-2026-11-19/`, applied unchanged:
- a name counts when it is in the page's visible text or a real `alt`/`title` attribute (owner ruling
  2026-11-18c); a name rebuilt from a link URL or file name does not;
- a legal-name match to exactly one active/unknown organization; trade-name hits are held (`trade_name_holds.csv`,
  20);
- an edition abroad mints only when the list gives the company's country, and it equals the organization's
  `hq_country`;
- the controller drop lists of waves 1 and 2–3, and the wave 2–3 review holds; the media-partner, not-an-event and
  combined co-located list exclusions;
- the list's own edition year, with pre-show and partial notes.

**Attendee lists.** Two lists are admitted (`ATTENDEE_LISTS`), each bound to its own event. Both were checked on the
banked page. Both list companies only and name no people:
- Coatings Trends & Technologies: the organizer's "final list of registered companies" for the 2026 edition
  (pcimag.com, PCI Magazine's own page);
- Great Lakes Coatings Conference: the organizer's list "Companies attended in 2025".

**Which editions are abroad.** The conferences repo's editions of these new series mostly carry no country. One,
ICERP 2026 (Mumbai), is keyed `country: US, region: IN`. Waves 2–3 defaulted a missing country to US, and on these
series that default minted 31 wrong rows in the dry run, such as US companies exhibiting in São Paulo or Querétaro,
and Scott Bader Company Ltd matched to Scott Bader, Inc. So here an international series (its `home_region`, set
from the organizer in #409) is always abroad. Its edition city and state come only from a conferences edition that
has a country; otherwise they are left empty.

**Held by the controller (`CONTROLLER_HOLDS`, 20).** As #404 held "Arkema" and "Sun Chemical" at SAMPE, a bare group
name does not pin the group's US entity. Each hold binds that listed form at its event in every role and year:
- (i) Armacell, Henkel, Evonik, Covestro, BASF, Omya, Arkema, Sun Chemical, Lanxess, Synthomer and Alberdingk Boley,
  at the events where they are listed bare;
- (ii) generic names: Resin Solutions (Great Lakes); and PolyFil (The Tire Cologne). Nothing on the list ties the
  tire-trade exhibitor to the Rockaway NJ masterbatch maker.

A listed form that names the US entity itself ("Evonik Corporation", "BASF Corporation", "Covestro LLC", "Omya,
Inc.") pins it, and is not held. Every hold must match a listing, or the build fails, so a mistyped hold cannot
silently do nothing.

**Skipped in the build:**

| Reason | Names |
|-|-|
| no Atlas organization | 7,438 |
| combined co-located list (EXPOPLAST, PUTECH, TyreXpo 2026, PRS India) | 362 |
| abroad, no listed country or not the org's HQ country | 50 |
| trade-name hit, held | 20 |
| `CONTROLLER_HOLDS` | 20 |
| name not on the page | 6 |
| labelled for a co-located show | 5 |
| controller drop | 4 |
| media-partner or not-an-event list | 4 |
| ambiguous name key | 1 |
| already held | 1 |

## Checks

- `python3 scripts/validate.py`: passes.
- `python3 tasks/show-harvest-newseries-2026-11-19/check.py`: re-checks every row against every rule repo data can
  show, without the staging harvest. That includes the abroad rule: a row of an international series must name its
  listed country, equal to the org's HQ country, with no USPS `edition_state`.
- `python3 tasks/show-harvest-newseries-2026-11-19/negative_controls.py`: 17 of 17 planted defects fail
  `check.py` with the expected message, each for that one reason, except the controller-drop control.
- Limit: `check.py` cannot prove a row came from its list. `build.py`, which reads the banked pages, is the
  provenance guarantee.

## Proposed follow-ups (not done here)

- Conferences repo: most editions of these 27 series have no `country`, and ICERP 2026 is keyed `country: US,
  region: IN` (Mumbai). Fill the countries, so a later pass need not rely on `home_region`. (Fakuma's market-visit
  mis-key, noted earlier, is the same kind of defect.)
- The 14 series that mint nothing: country-bearing directories for the abroad shows would admit their US
  exhibitors.
