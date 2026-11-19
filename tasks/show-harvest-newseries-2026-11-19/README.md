# Show harvest: participation rows for the 27 new series (2026-11-19)

**+79 rows** in `data/event_participation.csv` (1,440 → 1,519; EVP-001448 to EVP-001526): 66 organizations at
12 of the 27 series PR #409 seeded (EVT-000072 to EVT-000098). By role: 38 exhibitor, 29 attendee, 6 sponsor and
6 speaker. All tier A (the organizer's own list), organization grain only. No organization, event or other row is
added or changed.

| Series | Rows |
|-|-|
| EVT-000082 Great Lakes Coatings Conference, 2025 | 29 attendee |
| EVT-000080 European Coatings Show, 2025 (Nuremberg) | 15 exhibitor |
| EVT-000072 AMPP Annual Conference + Expo, 2027 | 11 exhibitor |
| EVT-000074 Carbon Fiber, 2026 | 4 exhibitor, 3 sponsor |
| EVT-000077 Coatings Trends & Technologies Summit, 2026 | 6 speaker, 1 sponsor |
| EVT-000092 RadTech UV+EB Technology Expo & Conference, 2027 | 4 exhibitor |
| EVT-000076 CHINACOAT, 2026 | 3 exhibitor |
| EVT-000073 ArabPlast, 2025 | 1 exhibitor |
| EVT-000079 Eastern Coatings Show, 2027 | 1 sponsor |
| EVT-000098 Waterborne Symposium, 2027 | 1 sponsor |

The other 15 series mint nothing. Their lists fall into three groups:
- abroad with no country given: China Composites Expo, Meximold, Plástico Brasil, PRS Europe and India, ICERP;
- no name matches an Atlas organization;
- every match is held.

## Owner question (held, not ruled here)

**Coatings Trends & Technologies 2026 registration list (224 companies).** PCI Magazine, the organizer, publishes
the "final list of registered companies for Coatings Trends & Technologies Summit 2026. This list does not denote the
total number of registered attendees." SCHEMA §4.12.2 admits "a list of attending companies that the organizer
itself published". Whether a final registration list shows attendance is a new seam. AGENTS rule 9 makes it an
owner ruling, so the list is in `OWNER_PENDING` and mints nothing.

- **Recommendation:** count it. It is the organizer's own complete company list for a named, past edition, published
  as final after the event, and it names no people.
- **If ruled in:** about 48 attendee rows would follow in a short PR, under the same gates and holds.

## Method (`build.py`)

`python3 tasks/show-harvest-newseries-2026-11-19/build.py --data-dir data --harvest <staging> --conferences ../conferences`

No earlier pass read these lists, so this pass judges every name on them. It applies the gates of waves 1 and 2–3
and of `tasks/show-harvest-rulings-2026-11-19/` unchanged:
- **On the list:** a name counts when it is in the page's visible text or a real `alt`/`title` attribute (owner
  ruling 2026-11-18c). A name rebuilt from a link URL or file name does not.
- **Matching:** a legal-name match to exactly one active/unknown organization. Trade-name hits are held
  (`trade_name_holds.csv`, 13).
- **Abroad:** an edition abroad mints only when the list gives the company's country, and it equals the
  organization's `hq_country`.
- **Exclusions:** the controller drop lists of waves 1 and 2–3, and the wave 2–3 review holds; the media-partner,
  not-an-event and combined co-located list exclusions.
- **Year:** the list's own edition year, with pre-show and partial notes. An edition with no dates on record is
  pre-show when its year is later than the read.

**Attendee list.** One list is admitted (`ATTENDEE_LISTS`), bound to its own event: the Great Lakes Coatings
Conference page titled "Companies Attending". The organizer's site menu links it as "Companies attended in 2025".
The page lists companies only and names no people.

**Which editions are abroad.** Most conferences-repo editions of these new series carry no country, and ICERP 2026
(Mumbai) is keyed `country: US, region: IN`. Waves 2–3 defaulted a missing country to US. On these series, that
default minted 31 rows in the dry run that the abroad rule cannot support. Examples:
- US companies listed at Plástico Brasil and Meximold, with no country given;
- Scott Bader Company Ltd at ICERP, matched to Scott Bader, Inc.

So here an international series (its `home_region`, set from the organizer in #409) is always abroad. Its edition
city and state come only from a conferences edition that gives a country; otherwise they stay empty.

**Held by the controller (`CONTROLLER_HOLDS`, 19).** As #404 held "Arkema" and "Sun Chemical" at SAMPE, a bare group
name does not pin the group's US entity. Each hold is keyed on the name key, as in #404, so it binds every listed
form of the name at its event, in every role and year. There are two kinds:
- (i) a bare group name whose Atlas record is the group's US entity: Armacell, Henkel, Evonik, Covestro, BASF, Omya,
  Lanxess, Orion Engineered Carbons (its parent, Orion S.A., is registered in Luxembourg), Sun Chemical, Synthomer,
  Alberdingk Boley and Arkema;
- (ii) a generic name with nothing to pick the Atlas organization: Resin Solutions (Great Lakes), and PolyFil (The
  Tire Cologne; nothing ties a tire-trade exhibitor to the Rockaway NJ masterbatch maker).

The build fails if a hold matches no listing, so a mistyped hold cannot silently do nothing.

**Not held, and why.** Every kept row whose listed name has no legal or geographic suffix falls into one of two
groups:
- a US-parented group listed by its own name: Cargill, Chemours, Hexcel, Ingevity, Lubrizol, Michelman,
  Sherwin-Williams, Stepan and others;
- a company listed by its own name, not a parent's: FlexSteel Pipeline Technologies, Schneller, Engineered Polymer
  Solutions, Anderson Development.

A name that names the US entity ("Hauschild SpeedMixer Inc", "Hempel USA") pins it. At SAMPE, #404 held the bare
"Hauschild SpeedMixer". Two suffixes differ from the Atlas legal form and are kept, since the name key matches one
organization: Chem-Materials Inc. (Chem-Materials Co.) and IMCD LLC US (IMCD US).

**Skipped in the build:**

| Reason | Names |
|-|-|
| no Atlas organization | 7,274 |
| combined co-located list (EXPOPLAST, PUTECH, TyreXpo 2026, PRS India) | 362 |
| attendee list awaiting an owner ruling (Coatings Trends) | 224 |
| abroad, no listed country or not the org's HQ country | 50 |
| `CONTROLLER_HOLDS` | 19 |
| trade-name hit, held | 13 |
| name not on the page | 6 |
| labelled for a co-located show | 5 |
| media-partner or not-an-event list | 4 |
| controller drop | 2 |
| ambiguous name key | 1 |

## Checks

- `python3 scripts/validate.py`: passes.
- `python3 tasks/show-harvest-newseries-2026-11-19/check.py`: re-checks every row against every rule that repo data
  can show, without the staging harvest. That includes the abroad rule: a row of an international series must name
  its listed country, which must equal the org's HQ country, and must not have a USPS `edition_state`.
- `python3 tasks/show-harvest-newseries-2026-11-19/negative_controls.py`: 19 of 19 planted defects fail
  `check.py` with the expected message. Three of the controls plant a variant form of a held name, such as
  "Evonik Corporation" where "Evonik" is held.
- **Limit:** `check.py` cannot prove a row came from its list. `build.py`, which reads the banked pages, is the
  provenance guarantee.

## Proposed follow-ups (not done here)

- **Conferences repo:** most editions of these 27 series have no `country`, and ICERP 2026 is keyed `country: US,
  region: IN` (Mumbai). Filling in the countries would let a later pass stop relying on `home_region`. Fakuma's
  market-visit mis-key, noted earlier, is the same kind of defect.
- **The 15 series that mint nothing:** country-bearing directories for the abroad shows would admit their US
  exhibitors.
