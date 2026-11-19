# New event series from the show harvest (2026-11-19)

**+27 event series** in `data/events.csv` (71 → 98 series; EVT-000072 to EVT-000098) and **+13 inclusion-log rows**
in `data/inclusion_log.csv`. No organization, site or participation row is added or changed: participation rows
for these series come from the banked harvest in a separate pull request. SCHEMA v1.16.2 records the owner's
borderline rulings as §4.12.1 worked seams 4–7 (`tasks/owner-rulings-2026-11-19b/README.md`).

| Home | Series |
|-|-|
| United States (7) | AMPP Annual Conference + Expo, Carbon Fiber, Coatings Trends & Technologies Summit, Eastern Coatings Show, Great Lakes Coatings Conference, RadTech UV+EB Technology Expo & Conference, Waterborne Symposium |
| International (20) | ArabPlast, China Composites Expo, CHINACOAT, Composites Meetings, European Coatings Show, EXPOPLAST, ICERP, India Rubber Expo, Meximold, Plástico Brasil, Plastics Recycling Show Brazil, Plastics Recycling Show Europe, Plastics Recycling Show India, Plastindia, PUTECH Eurasia, RubberTech China, SAMPE Japan Exhibition, THE TIRE COLOGNE, TyreXpo Asia, UTECH Europe |

By subject (a series can carry more than one): coatings 8, composites 6, rubber 5, recycling 5, plastics general 4,
adhesives 2, plastics processing 2, polyurethanes 2, tooling 1.

## How the 107 untracked series were sorted

The waves 1–3 harvest (staging `harvest-2026-11`, not committed) holds lists for 107 series that `events.csv` did
not hold. The test is SCHEMA §4.12.1's named-subject prong: the organizer's own statement must name polymers,
plastics or rubber (or a listed subfield, or coatings) as the primary subject. Material-agnostic shows fail however
polymer-heavy their exhibitors are (the Pack Expo seam).

1. **72 not researched (name-level OUT).** Their own names state a material-agnostic subject:
   - general manufacturing: Hannover Messe, IMTS, the SME series, the Assembly Show;
   - packaging: Pack Expo, Expo Pack, Pharmapack;
   - medical: Compamed, MD&M, MEDevice;
   - additive manufacturing: Formnext, TCT, AMUG;
   - chemicals: SOCMA, Chemspec, ACHEMA, AIChE, ACS Spring;
   - wire and cable, general materials, textiles, general recycling, batteries and vehicles;
   - innovation, economic development and education events.

   Also here: `fakuma-european-market-visit-s`, a mis-key in the conferences repo for the held Fakuma series,
   which that repo should fold into `fakuma`.
2. **35 researched** (`verdicts.csv`).
   - **The research lane:** codex read each organizer's own site on 2026-11-19 and quoted its subject statement,
     with the URL. It proposed the series fields from that page and the PIC conferences repo's organizer-checked
     edition facts.
   - **The cross-check:** agy (Gemini 4 Hydrogen, XHigh), the second family, checked every verdict and field
     against the quotes and returned SHIP-WITH-FIXES. Applied:
     - subject scopes trimmed to what the quotes state (ArabPlast, Plastindia, RubberTech China, EXPOPLAST);
     - recycling added to The Tire Cologne, and composites to RadTech;
     - prongs settled on the owner-ruled rows.
   - **Stronger quotes:** the controller replaced three that named no polymer subject, from the organizers' own
     pages (SAMPE Japan, China Composites Expo, Composites Meetings).
   - **Result:** 20 IN on the lane's verdict, 7 IN by owner ruling, and 8 OUT: ACS POLY Fall Show (a polymer track
     inside ACS national meetings), the Kent State AMLCI Materials Day (a general materials series whose theme
     rotates), AMI's two textile-recycling expos, Moulding Expo (material-agnostic toolmaking), the Packaging
     Conference, FiltXPO, and the Geosynthetics Conference (owner ruling).

## Field rules applied (`build.py`)

`python3 tasks/new-series-2026-11-19/build.py --data-dir data` (dry run; `--apply --i-am-the-integrator` appends).
- **Name** as the organizer styles it, without edition year or city: "EXPOPLAST" (with "EXPOPLAST Montréal" as a
  trade name), and "Plastics Recycling Show Brazil" (trade name "PRS Brazil").
- **Home:** an international series leaves `home_state` empty and names its country in `geography_note`. A rotating
  series leaves the home city empty and names only editions that ran or are announced.
- **Cadence:** `cadence_note` is kept only for an irregular cadence (V-17); for a regular one the lane's cadence
  source moves to `notes`.
- **Organizer:** `organizer_org_id` links the one organizer the Atlas holds, Gardner Business Media (ORG-001502):
  Meximold, and Carbon Fiber through its CompositesWorld brand.
- **Backbone:** tier A (the organizer's own site); `last_verified` 2026-11-19; `pic_events_slug` is the
  conferences-repo slug.
- **Inclusion log:** one row for each owner-ruled call, plus each OUT that names a polymer subject.

## Checks

- `python3 scripts/validate.py` exits 0 (98 event series).
- `build.py` asserts that no candidate is already an Atlas series (by `pic_events_slug`) and that no new name
  duplicates an existing series name.
