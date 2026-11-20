# Show harvest: organizer lists a Muse research pass found (2026-11-20)

**+54 rows** in `data/event_participation.csv` (1,570 → 1,624; EVP-001578 to EVP-001631): 38 organizations at 6 event
series. By role: 43 exhibitor, 4 sponsor, 4 speaker and 3 attendee. All tier A (the organizer's own list), organization
grain only. No organization, event or other row is added or changed.

| Series, edition | Rows |
|-|-|
| EVT-000072 AMPP Annual Conference + Expo, 2025 (Nashville) | 11 exhibitor, 1 sponsor |
| EVT-000072 AMPP Annual Conference + Expo, 2026 (Houston) | 11 exhibitor |
| EVT-000092 RadTech UV+EB Technology Expo & Conference, 2025 (Detroit) | 13 exhibitor |
| EVT-000077 Coatings Trends & Technologies Summit, 2026 | 3 sponsor, 2 speaker, 3 attendee |
| EVT-000085 Meximold, 2026 and 2027 (Querétaro) | 3 + 3 exhibitor |
| EVT-000081 EXPOPLAST, 2026 (ADM Montréal) | 2 exhibitor |
| EVT-000074 Carbon Fiber, 2026 | 2 speaker |

The three attendee rows apply owner ruling 2026-11-20 (`tasks/owner-rulings-2026-11-20/`) to #414's list. Edition
dates and places come from the conferences repo, which added the past editions these rows cite in its PRs #3 and #4.

## Where the lists came from

A Muse research pass (2026-11-19) proposed organizer lists for these shows. **Muse is a lead only.** The controller:
- **Banked** each source in staging (`muse-leads-2026-11-19`: `raw/`, `manifest.json`, never committed): PDFs by
  download, and pages behind bot checks with a real browser. The Meximold and ADM Montréal directories needed headed
  Chrome.
- **Extracted** each list itself (`lists/*.json`).
- **Compared** each list by exact name with Muse's transcription. For every list Muse transcribed in full, the counts
  agree. The names differ only in spacing (Muse wrote "M . C. Miller" where the PDF prints "M. C. Miller") and in one
  bare "PPG" line that matches no Atlas name. Two kinds of list have no full Muse transcription to compare:
  - the ECS 2025 list, which the controller found while checking edition dates;
  - the `_us` lists, which are the Atlas-matching subset of Muse's US-exhibitor lists.

The build re-reads the banked source for every name. A name must be in the source's text: the PDF text layer, or a
page's visible text and real alt/title attributes. Each list's entry count is asserted. For the ECS list this is the
list's own 1,213 entries; the organizer's review page says 1,215 exhibitors.

| List (staging key) | Source | Entries | Atlas matches | Rows |
|-|-|-|-|-|
| `ampp_2025_exhibitor` | AMPP 2025 on-site guide, "Exhibitors as of March 20, 2025" | 367 | 14 | 11 |
| `ampp_2025_sponsor` | the same list's "S Event Sponsor" flags | 36 | 1 | 1 |
| `ampp_2026_exhibitor` | AMPP 2026 advance program, "Exhibitors as of September 15, 2025" | 291 | 12 | 11 |
| `ampp_2026_sponsor` | the same list's "S Event Sponsor" flags | 20 | 0 | 0 |
| `ecs_2025_exhibitor` | ECS "List of Exhibitors" 2025, "As of March 2025", with a country per entry | 1,213 | 20 | 0 |
| `carbonfiber_2026_speaker` | "Carbon Fiber 2026 Agenda" (PDF), employers | 37 | 2 | 2 |
| `ctt_2026_speaker` | Coatings Trends 2026 agenda page, employers | 58 | 19 | 2 |
| `ctt_2026_sponsor` | PCI blog, 2026-08-17: "We are grateful to our 2026 sponsors:" | 19 | 4 | 3 |
| `radtech_2025_exhibitor` | "RadTech 2025 :: Exhibitor List" | 56 | 14 | 13 |
| `meximold_2026_exhibitor_us` | Meximold 2026 directory: exhibitor pages printing "United States of America" | 3 | 3 | 3 |
| `meximold_2027_exhibitor_us` | Meximold 2027 directory (still filling), the same | 3 | 3 | 3 |
| `expoplast_2026_exhibitor_us` | ADM Montréal 2026 directory: "ADM Plastiques 2026", United States of America | 2 | 2 | 2 |

"Atlas matches" counts the entries whose name key belongs to exactly one active/unknown organization. The rest of
the 2,105 entries match none (2,011).

**The `_us` lists.** The Meximold and ADM Montréal lists hold only the US-printed exhibitors that match Atlas names.
Each was checked on its own exhibitor page, which prints the country. The directories hold 128 (Meximold 2026), 87
(Meximold 2027) and 313 (ADM Montréal) exhibitors. Muse found the US-printed ones in three ways:
- by state and province searches checked on each exhibitor page (Meximold 2026; it notes an exhibitor with a blank
  state field could be missed);
- by opening every exhibitor page (Meximold 2027);
- by opening every exhibitor labelled "ADM Plastiques 2026" (ADM Montréal).

**Speaker lists** record only the employer printed beside each speaker.

## Gates (`build.py`)

`python3 tasks/show-harvest-muse-leads-2026-11-20/build.py --data-dir data --staging <muse-leads staging>
--harvest <harvest-2026-11 staging> --conferences ../conferences`

The build imports #411's build and applies its gates:
- **Matching:** a legal-name match to exactly one active/unknown organization. Trade-name hits are held
  (`trade_name_holds.csv`, 6).
- **Review holds:** the wave 2–3 review holds bind.
- **Abroad:** an international series is held abroad. Such a row mints only when the list prints the company's country
  and it equals the organization's HQ country.
- **Existing rows:** no (event, org, year, role) the table already holds.

**Holds (owner ruling 2026-11-20).** The rule (i)/(ii) holds of #404, #411, #414 and this pass bind at their event.
A rule (i) hold binds a bare group name only. A listing that prints the organization's full legal name, suffix
included, names the US entity and mints, and its row carries the ruling's note. Four rows do:
- "Alberdingk Boley, Inc" at RadTech 2025, where #411 holds the bare "Alberdingk Boley";
- the three registration-list names at Coatings Trends 2026.

`held_listings.csv` lists the 10 bare names held here: Armacell at AMPP 2025 and 2026; Evonik (twice), Covestro, Omya,
Sun Chemical and BASF on the Coatings Trends agenda; Evonik on its sponsor list; Arkema at RadTech 2025.

**One new hold (`HOLDS`).** The dated Coatings Trends sponsor list prints a bare "Evonik", and the Atlas record is
Evonik Corporation. This is rule (i), as at SAMPE (#404) and the Waterborne Symposium (#411).

**The bare-name screen (`screen_bare_names.csv`).** The build lists every kept row whose listed name carries no legal
suffix while its organization has a parent on record. The controller read each one:

| Listed name | Organization | Kept because |
|-|-|-|
| Sherwin-Williams (AMPP 2025, exhibitor and sponsor) | The Sherwin-Williams Company | a US group listed by its own name |
| Teijin Carbon America (Carbon Fiber) | Teijin Carbon America, Inc. | the name is the US company's own ("America") |
| PPG Industries (Coatings Trends) | PPG Industries, Inc. | a US group listed by its own name |
| BYK USA (RadTech) | BYK USA LLC | the name names the US entity ("USA") |
| Absolute Robot (EXPOPLAST) | Absolute Robot Incorporated | the company's own name, not a parent's |

**Pre-show lists.** A list that predates its edition says so in each row (29 rows). The build compares the list's own
as-of date with the edition's start:
- the AMPP 2025 list is "as of March 20, 2025", and the show opened April 6;
- the AMPP 2026 list is "as of September 15, 2025", and the show opened March 15, 2026;
- the Coatings Trends sponsor post is dated 2026-08-17, and the show opened September 15;
- the Meximold 2027 directory was read on 2026-11-19, for a September 2027 show.

**Abroad (8 rows).** The 6 Meximold rows and 2 EXPOPLAST rows print "United States of America", which is each
organization's HQ country.
- **EXPOPLAST:** its rows come from the ADM Montréal directory's "ADM Plastiques 2026" pavilion, under owner ruling
  2026-11-19d item 3. The organizer's release of 15 September 2026, which folds EXPOPLAST into ADM Montréal, is banked
  with the sources.
- **ECS 2025 mints nothing new.** Of its 51 US-printed entries, 17 match an Atlas name: 15 are already #411 rows and
  2 are trade-name hits. Three more entries match US organizations but print another country. So #411's partial ECS
  list had already credited every US match.

## Not done here

- **Waterborne Symposium 2025 and 2026:** the Sched pages served a maintenance page (HTTP 503) to every client on
  2026-11-19. Re-fetch, then a short follow-up pass.
- **RubberTech China:** the directory's English header says 2027, but its Chinese title and exhibitor system say 2026.
  The edition year is unresolved, so it mints nothing.
- **Great Lakes speaker pages:** neither the pages nor the site menu date them. Under owner ruling 2026-11-19d item 4
  they mint nothing.
- **A new lead:** the Great Lakes "SPONSORS IN 2025" page (`/our-sponsors/`), which the site menu dates. It is not
  banked here.

## Checks

- `python3 scripts/validate.py`: passes.
- `python3 tasks/show-harvest-muse-leads-2026-11-20/check.py` re-checks every row without the staging sources. It
  covers:
  - each row's list (event, year, role, note);
  - the attendee rows;
  - the cited URL;
  - a unique legal-name match;
  - the wave 2–3 holds;
  - the rule (i)/(ii) holds and the ruling's note;
  - the abroad rule;
  - tier A.
- `python3 tasks/show-harvest-muse-leads-2026-11-20/negative_controls.py`: 15 of 15 planted defects fail `check.py`
  with the expected message. No control writes a person's name.
- The `check.py` of #411 and #414 still pass with these rows in the table.
- **Limit:** `check.py` cannot prove a name is in its source. `build.py`, which reads the banked sources, is the
  guarantee.
