# Show harvest: participation rows for the 27 new series (2026-11-19)

**+86 rows** in `data/event_participation.csv` (1,440 → 1,526; EVP-001448 to EVP-001533): 70 organizations at
10 of the 27 series PR #409 seeded (EVT-000072 to EVT-000098). By role: 43 exhibitor, 29 attendee, 9 speaker and
5 sponsor. All tier A (the organizer's own list), organization grain only. No organization, event or other row is
added or changed.

| Series | Rows |
|-|-|
| EVT-000082 Great Lakes Coatings Conference, 2025 | 29 attendee |
| EVT-000080 European Coatings Show, 2025 (Nuremberg) | 15 exhibitor |
| EVT-000074 Carbon Fiber, 2026 | 9 exhibitor, 3 sponsor |
| EVT-000072 AMPP Annual Conference + Expo, 2027 | 11 exhibitor |
| EVT-000077 Coatings Trends & Technologies Summit, 2026 | 9 speaker |
| EVT-000092 RadTech UV+EB Technology Expo & Conference, 2027 | 4 exhibitor |
| EVT-000076 CHINACOAT, 2026 | 3 exhibitor |
| EVT-000073 ArabPlast, 2025 | 1 exhibitor |
| EVT-000079 Eastern Coatings Show, 2027 | 1 sponsor |
| EVT-000098 Waterborne Symposium, 2027 | 1 sponsor |

The other 17 series mint nothing. Their lists fall into three groups:
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
and of `tasks/show-harvest-rulings-2026-11-19/`:
- **On the list:** a name counts when it is in the page's visible text or a real `alt`/`title` attribute (owner
  ruling 2026-11-18c). A name rebuilt from a link URL or file name does not.
- **Matching:** a legal-name match to exactly one active/unknown organization. Trade-name hits are held
  (`trade_name_holds.csv`, 12).
- **Abroad:** an edition abroad mints only when the list gives the company's country, and it equals the
  organization's `hq_country`.
- **Exclusions:** the controller drop lists of waves 1 and 2–3, and the wave 2–3 review holds; the media-partner and
  not-an-event list exclusions.
- **Combined lists:** a list covering several co-located shows mints only entries labelled for this show. An empty
  `shows_covered` on such a list counts as several. This is stricter than waves 2–3, where an unlabelled entry on a
  partly labelled list passed.
- **Year:** the list's own edition year, with pre-show and partial notes. An edition with no dates on record is
  pre-show when its year is later than the read. When its year is the read's year, the row says the dates are not
  on record (9 Coatings Trends 2026 speaker rows).

**Attendee list.** One list is admitted (`ATTENDEE_LISTS`), bound to its event and its edition year (2025): the Great
Lakes Coatings Conference page titled "Companies Attending". The organizer's site menu links it as "Companies
attended in 2025".
- **Completeness:** the page's table has 178 cells, and the harvest holds all 178.
- **Not all companies:** three cells name no organization: one personal name, "Retired" and "University of Michigan
  Student". Four more are organizations but not companies: Bowling Green State University, University of Akron,
  Chicago Paint & Coatings Association and Zinc Association. None of these seven matches an Atlas organization, so
  none mints. The rest are organization names, mostly companies, with some acronyms (for example "ACA", the American
  Coatings Association); they were not classified one by one.
- **Not a delegate list:** each cell is a single name, and no cell gives a person's title or employer.

**Undated list (`UNDATED_LISTS`).** The Coatings Trends sponsor block on the organizer's home page names no year,
and the page announces the 2027 edition. One logo's alt text also names the wrong company ("BYK" on Elinor's logo).
It cannot support a row for any one edition, so its 20 names mint nothing.

**Names the harvest omitted (`SUPPLEMENT`).** Two lists came back short of their banked pages:
- **Carbon Fiber exhibitors:** "All Carbon Fiber 2026 Exhibiting Companies" has 29 names, and the harvest kept 16;
- **Coatings Trends speakers:** "2026 Speakers" has 57 live speaker cards (a 58th is commented out in the page
  source), and the harvest omitted 11 of the employers.

The controller copied the omitted names verbatim from each banked page. They pass every gate like harvested names,
and their rows say so in `notes`.
- **Result:** 5 more Carbon Fiber exhibitor rows (Hexcel, A&P Technology, Park Aerospace, Composites One, Fives
  Machining Systems) and 3 more speaker rows (Vibrantz Technologies, Vinavil Americas, Evonik Corporation).
- **Build asserts:** a supplement name must be on its page, and must not repeat a harvested name.

**Yield audit of the other lists.** The controller searched every banked page of these series for Atlas legal names
(cores of 8 characters or more) that are missing from the list's JSON. Every other hit is a substring of a longer
listed name, or the listed company's own national entity:
- substrings: "Owens Corning Foamglas", "Americhem Sales Company";
- national entities on the European Coatings Show list: Eastman Chemical B.V., Huntsman Belgium BV and others.

The audit cannot see shorter names. The European Coatings Show list is marked partial in the harvest, and its rows
say so.

**Which editions are abroad.** Most conferences-repo editions of these new series carry no country, and ICERP 2026
(Mumbai) is keyed `country: US, region: IN`. Waves 2–3 defaulted a missing country to US. On these series, that
default minted 31 rows in the first dry run that the abroad rule cannot support. Examples:
- US companies listed at Plástico Brasil and Meximold, with no country given;
- Scott Bader Company Ltd at ICERP, matched to Scott Bader, Inc.

So here an international series (its `home_region`, set from the organizer in #409) is always abroad. Its edition
city and state come only from a conferences edition that gives a country; otherwise they stay empty.

**Held by the controller (`CONTROLLER_HOLDS`, 19).** As #404 held "Arkema" and "Sun Chemical" at SAMPE, a bare group
name does not pin the group's US entity. Each hold is keyed on the name key, as in #404, so it binds every listed
form of the name at its event, in every role and year. There are two kinds:
- (i) a bare group name whose Atlas record is the group's US entity: Armacell, Henkel, Covestro, BASF, Omya, Sun
  Chemical, Lanxess, Orion Engineered Carbons (its parent, Orion S.A., is registered in Luxembourg), Synthomer,
  Alberdingk Boley, Arkema and Evonik (Waterborne);
- (ii) a generic name with nothing to pick the Atlas organization: Resin Solutions (Great Lakes), and PolyFil (The
  Tire Cologne; nothing ties a tire-trade exhibitor to the Rockaway NJ masterbatch maker).

The build fails if a hold matches no listing, so a mistyped hold cannot silently do nothing.

**Not held, and why.** At Coatings Trends, the bare "Evonik" occurs only on the undated sponsor block. The dated
speaker list names "Evonik Corporation", which mints, and "Evonik Industries", which matches no Atlas organization.
So Evonik is not held there. Every kept row
whose listed name has no legal or geographic suffix falls into one of two groups:
- a US-parented group listed by its own name: Cargill, Chemours, Hexcel, Ingevity, Lubrizol, Michelman,
  Sherwin-Williams, Stepan and others;
- a company listed by its own name, not a parent's: FlexSteel Pipeline Technologies, Schneller, Engineered Polymer
  Solutions, Anderson Development, Composites One.

A name that names the US entity ("Hauschild SpeedMixer Inc", "Hempel USA") pins it. At SAMPE, #404 held the bare
"Hauschild SpeedMixer". Two suffixes differ from the Atlas legal form and are kept, since the name key matches one
organization: Chem-Materials Inc. (Chem-Materials Co.) and IMCD LLC US (IMCD US).

**Skipped in the build:**

| Reason | Names |
|-|-|
| no Atlas organization | 7,277 |
| combined co-located list (EXPOPLAST, PUTECH, PRS India) | 362 |
| attendee list awaiting an owner ruling (Coatings Trends) | 224 |
| abroad, no listed country or not the org's HQ country | 50 |
| undated list (Coatings Trends sponsors) | 20 |
| `CONTROLLER_HOLDS` | 19 |
| trade-name hit, held | 12 |
| labelled for a co-located show | 5 |
| media-partner or not-an-event list | 4 |
| controller drop | 2 |
| name not on the page | 1 |
| ambiguous name key | 1 |

## Checks

- `python3 scripts/validate.py`: passes.
- `python3 tasks/show-harvest-newseries-2026-11-19/check.py`: re-checks every row against every rule that repo data
  can show, without the staging harvest. That includes:
  - the attendee list's event and year;
  - the undated and owner-pending lists;
  - the supplement notes;
  - the abroad rule: an international series, an abroad note or a non-US `edition_state` each require a listed
    country equal to the org's HQ country.
- `python3 tasks/show-harvest-newseries-2026-11-19/negative_controls.py`: 25 of 25 planted defects fail
  `check.py` with the expected message.
- **Limit:** `check.py` cannot prove a row came from its list, or that no unlabelled combined-list entry minted.
  `build.py`, which reads the banked pages, is the guarantee for both.

## Review (PR #411)

The first round, on `bbc6d531`, had 79 rows. Codex (deep) and agy (Gemini 4 Hydrogen, XHigh) each returned
SHIP-WITH-FIXES. Applied:
- **Undated sponsor list (codex):** the Coatings Trends sponsor block names no year, so R.E. Carroll's sponsor row
  is gone.
- **Under-extraction (codex):** the harvest omitted 13 of 29 Carbon Fiber exhibitors. The controller's speaker check
  found 11 omitted Coatings Trends employers as well. Both lists are now supplemented, and a yield audit covers the
  rest.
- **Great Lakes provenance (codex):** the README claimed the list names no people. It has one personal name, and
  this README now says so.
- **Count corrected (codex):** the README, PR and QUEUE said the 79 rows covered 12 series. They covered 10. The
  figure was wrong; it is corrected here, not silently.
- **Combined lists (agy):** an unlabelled entry on a combined list no longer passes. An empty `shows_covered` counts
  as several shows.
- **Attendee year pinned (agy).**
- **Abroad edges (agy):** the checker applies the abroad rule to any row with an abroad note or a non-US state. An
  empty country string is treated as missing. The country pattern tolerates parentheses.
- **Pre-show note (agy):** an edition in the read's year with no dates says so.

## Proposed follow-ups (not done here)

- **Conferences repo:** most editions of these 27 series have no `country`, and ICERP 2026 is keyed `country: US,
  region: IN` (Mumbai). Filling in the countries would let a later pass stop relying on `home_region`. Fakuma's
  market-visit mis-key, noted earlier, is the same kind of defect.
- **The 17 series that mint nothing:** country-bearing directories for the abroad shows would admit their US
  exhibitors.
- **Waves 2–3 (merged):** their combined-list gate let an unlabelled entry through on a partly labelled list. A
  re-check of the merged rows against that case is worth one pass.
