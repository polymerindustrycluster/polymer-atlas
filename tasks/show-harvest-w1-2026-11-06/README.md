# Show harvest, wave 1 (2026-11-06)

> **Review, 2026-11-09:** 7 of the 161 rows are dropped, leaving **154** (1,142 → 1,296). Codex and grok each
> reviewed a 60-row sample, and the integrator then checked all 161 for the pattern they found: a parent or brand name
> credited as a different entity through `trade_names`.
>
> | Dropped | Why |
> |-|-|
> | 4 | A different entity: Coperion → Hillenbrand, Cimatron → SigmaTEK, Barnes Molding Solutions → Synventive, and a bare "Continental" |
> | 2 | The Adhesives & Bonding sponsor page is undated, so the edition year is unresolved |
> | 1 | Amcor Flexibles credited to a rigid-PET plant record |
>
> The other 22 trade-name matches are the same company, for example Nouryon, Magris Talc and Wittmann USA. On 102
> rows the staging key names a later edition. Their notes now say the row year follows the year printed in the source,
> which is what both reviewers checked. Details are in `review_fixes.py` and `review_drops.csv`. The per-event table
> below is from before the drops.

**+161 participation rows** in `data/event_participation.csv` (1,142 → 1,303): 87 exhibitor, 36 sponsor, 38 speaker
rows, for 12 event series already held in `data/events.csv`. All tier A (the organizer's own published list,
SCHEMA §4.12.2). No organization, event or other row is added or changed.

| Event | Role | List year | Rows |
|-|-|-|-|
| EVT-000007 AMI Plastics World Expos North America | speaker / sponsor | 2026 | 34 / 4 |
| EVT-000011 PTXPO | exhibitor | 2028 | 46 |
| EVT-000057 SPE International Polyolefins Conference | exhibitor / sponsor | 2026 | 23 / 4 |
| EVT-000046 SPE TPO Global Automotive Engineered Polyolefins | exhibitor / sponsor | 2026 | 10 / 11 |
| EVT-000067 Tire Recycling Conference | exhibitor / sponsor | 2026 | 6 / 6 |
| EVT-000021 Adhesives & Bonding Expo | sponsor | 2026 | 4 |
| EVT-000056 Stretch & Shrink Film North America | exhibitor / speaker | 2026 | 2 / 3 |
| EVT-000069 Plastic Pipes Conference | sponsor | 2027 | 3 |
| EVT-000020 Foam Expo North America | sponsor | 2026 | 2 |
| EVT-000032 PINO | sponsor / speaker | 2026 | 1 / 1 |
| EVT-000031 GRC Polymers | sponsor | 2027 | 1 |

## Source

Wave 1 of the full participation harvest (owner decision 2026-11-06; QUEUE "Full participation harvest"): 102 show
editions from the PIC conferences list, harvested by a Grok Build packet lane into local staging
(`_internal/atlas-staging/harvest-2026-11/`, never committed). One JSON file per edition; the raw page behind every
list is banked under `out/raw/`. Retrieved 2026-11-06. Public lists were read under the owner's 2026-11-06 ruling that
robots.txt and platform terms do not bar publicly viewable rosters (tasks/exhibitor-links-2026-11-06).

The controller re-checked the lane's output independently before building (not the lane's own checker): 102/102
files, list and company counts matched the lane's report, and a person/junk screen produced `controller_drops.csv`
(person names in company slots, page labels).

## Method (`build.py`)

`python3 tasks/show-harvest-w1-2026-11-06/build.py --data-dir data --harvest <staging> --conferences ../conferences`
(dry run; `--apply --i-am-the-integrator` appends). An (event, org, year, role) key already held is skipped.

- **Event.** Show slug → event via `event_map.csv`, which is the schema v1.12 crosswalk (PR #250) unpacked one slug
  per line. The AMI component expos map to the umbrella EVT-000007, as in the earlier exhibitor passes.
- **Organization.** Exact `atlas.name_key` on legal and trade names of active/unknown organizations; a key held by two
  organizations is held (17 names). No organization is created; 1,090 unmatched names stay in staging as leads.
- **Evidence gate.** A name mints only if it appears verbatim in its list's banked raw file (3 sponsor names
  reconstructed from logo file names were held).
- **Edition year** is the list's own year, never the show file's year: a 2027 page carrying the 2026 list mints 2026
  rows, and one list copied onto several show files collapses to one row per (event, org, year, role).
- **Edition dates and city** come from the conferences repo's series YAML for that year; empty when the YAML has no
  such edition (Foam Expo 2026, SPE Polyolefins 2026).
- **role_detail** is the list's own booth number, sponsor level or session title, verbatim, blanked if it contains a
  personal pattern. No person's name is transcribed anywhere.
- **Notes** say when a roster was pre-show (still filling) or partial (`complete: false`).

## Not minted, and why

| Reason | Names |
|-|-|
| Series not held in `events.csv` | 8,998 |
| Attendee lists: wait for v1.12 (`attendee` role) and a terms check (§4.12.2 rule 4) | 1,657 |
| Combined co-located list with no per-company show label (below) | 257 |
| Edition abroad, list gives no company country (Tire Technology Expo speakers, European Bioplastics Conference sponsors) | 95 |
| Media-partner ("supporters") lists: not sponsors | 10 |

Combined lists skipped: Global Polymer Summit / International Rubber Conference shared sponsor page (also hosted off
the organizer's domain); GPS 2028 exhibitor list (GPS + ITEC); Materials Week USA sponsors (seven co-located expos;
the crosswalk maps the slug to Silicone Expo USA, EVT-000023, so these cannot be assigned); Adhesives & Bonding Expo
speaker lists; Foam Expo speaker list (the shared Foam Expo + A&B conference, though the lane did not flag it).

## Follow-ups (not in this PR)

- Series in the harvest that `events.csv` does not hold are added only when they pass the §4.12.1 scope test, in
  their own PR; their rows are backfilled from the banked harvest.
- Attendee rows (SOCMA Show, SPE Polyolefins, Coatings Trends & Technologies, Great Lakes Coatings): after v1.12.
- Waves 2 and 3 (242 editions) have not run.
