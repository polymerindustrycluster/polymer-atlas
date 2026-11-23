# Building and publishing the Atlas site

`scripts/build_site.py` turns the generated SQLite database into a static website for people who do not
use git: chamber staff, economic developers and members. It is stdlib-only Python (developed on 3.13)
and writes to `build/site/`, which is gitignored. The CSVs in `data/` stay canonical; the script only reads
the SQLite file and `docs/denominators/qcew_county_polymer_ohio_pa_2023_2024.csv`, and never edits `data/`.

## Build

```bash
python3 scripts/build_sqlite.py              # only needed when data/ changed (the site builder builds it if the .db is missing)
python3 scripts/build_site.py                # writes build/site/
python3 scripts/build_site.py --rebuild-db   # rebuild the .db first, then the site
python3 -m unittest scripts/test_build_site.py
```

Every table page has a "Download these rows (CSV)" button (client-side, the rows and columns on screen); `data-nocsv` on a table opts out and `data-nofilter` keeps the shared text filter off a page that filters its own rows. Every page links `directory.csv` and the latest GitHub release. Evidence and source strings are published only as structured fields and links: claim type, source class, strength, observed date and the public URLs found in the citation (`source_urls` in `build_site.py`). Claim text (`claim_detail`), notes, lane ids and the prose around a source link are never rendered, in the pages or in `directory.csv`; `test_no_evidence_claim_text_on_any_organization_page` fails if any appears.

Options: `--db PATH`, `--out DIR`, `--qcew CSV`, `--repo-url URL`. A full build takes a few seconds.

## What it produces

| Path | Content |
|---|---|
| `index.html` | What the Atlas is, headline counts (each with its unit and filter), ring and tier legends, license, "as of" commit and date |
| `map.html`, `sites.json`, `map.js` | Leaflet 1.9.4 map (version pinned, with SRI hashes) of site rows that have coordinates; filters for ring, tier and state, plus an opt-in for non-active sites |
| `search.html`, `orgs.json`, `search.js` | Client-side search over organization and ecosystem rows (name, trade names, city, state, ring) |
| `counties/index.html`, `counties/<county>.html` | Ohio county index and one-pagers for every Ohio county with Atlas rows, PIC-18 first (AGENTS.md §8): site rows by ring and by 3-digit NAICS with a tier breakdown, site table, programs, ecosystem organizations, and the BLS QCEW 2023 private NAICS 326 count benchmark |
| `directory.html`, `directory.js`, `directory.json`, `directory.csv` | Northeast Ohio polymer companies (owner ruling 2026-11-23, ATLAS-39). The page opens with two summary tables, counts by county and by ring, each stating its unit (organization rows with an active tier A-C site row in a PIC-18 county or ring) and an All PIC-18 line; an organization row with sites in two counties is counted in each, so the columns can exceed that line. Below: name search, filters (county, ring, site tier, employee band, process, material, market, ownership; "or" within one filter, "and" across filters; each lists its unknown count) and the list grouped by county, 50 rows at a time (previous/next), one row per organization and county with the street addresses of its site rows in that county ("Street not recorded" when empty). The rows are drawn by `directory.js` from `directory.json`, so the HTML holds none; the address bar holds the filters. "Download these rows (CSV)" saves every filtered row, not just the 50 on screen. A "PIC member" badge marks an organization on the public website member list only (AGENTS.md 5.1); the page never says an organization is not on it. Without JavaScript the page shows the summary, links to the county pages and `directory.csv`. `directory.csv` is the whole table (one row per organization and county; `public_member_list` is `yes` or blank; `pic18_site_addresses` last) |
| `prospects.html`, `prospects.csv` | Kept so links shared before the rename work: `prospects.html` is a redirect page to `directory.html`, `prospects.csv` a byte-identical copy of `directory.csv` (its rows are now per organization and county) |
| `orgs/<record id>.html` | One page per organization and ecosystem organization: fields, sites, the evidence rows (claim type, source class, strength, date, source link; records with no evidence rows yet fall back to their source links), tier, last verified; tombstones are marked, with a successor link |
| `style.css` | The one shared stylesheet (light/dark via `prefers-color-scheme`, mobile friendly) |

The only external requests the site makes are Leaflet (unpkg, version 1.9.4) and OpenStreetMap tiles, both on
`map.html`. Every other page is self-contained.

## Preview locally

`search.html` and `map.html` load JSON with `fetch`, which browsers block for pages opened from disk (`file://`).
Serve the folder instead:

```bash
python3 -m http.server -d build/site 8000     # then open http://localhost:8000/
```

The other pages (home, counties, organizations) also work when opened directly from disk.

## What is deliberately not published

The generator renders a whitelist of public business fields. It never writes `notes`, `created_by`,
`pic_relevance` (prospecting stages) or any other internal column. It also withholds:

- Source entries that refer to the PIC CRM or to staging/workshop paths, and one-line descriptions that mention the CRM
  (AGENTS.md section 5.1). Each page says how many source entries were left out; the repository CSV keeps the full text.
- Profile URLs that embed an email address (the researcher is still listed, without a link).
- Per-person pages. Professors and federal-lab research staff appear only as name, role as published, research
  specialties and public profile URL, on their institution's page (AGENTS.md section 6).

Coordinates are reference data and never evidence; the map and county pages say so. County benchmarks are labelled
count benchmarks, not matched coverage.

## Publishing (owner decision)

**Current setup:** the `pages` workflow (`.github/workflows/pages.yml`, live since 2026-11-02) builds the site with
`scripts/build_pages.py` and deploys it to GitHub Pages on every push to `main`, with the Pages source set to GitHub
Actions (docs/ci/README.md). The two options below are alternatives. Choosing one changes the hosting configuration,
which is the repository owner's decision.
`AGENTS.md` lets only `data/`, `docs/`, `scripts/` and `tasks/` travel in commits, so the generated site must
not be committed to `main`. Review a build locally first, especially the "not published" list above.

**Option 1: GitHub Pages from a `gh-pages` branch** (the owner runs this; it overwrites that branch each time, and
switching the Pages source to a branch turns off the workflow deployment above):

```bash
python3 scripts/build_site.py
cd build/site
git init -b gh-pages
git add -A && git commit -m "Atlas site build $(date +%F)"
git push --force https://github.com/polymerindustrycluster/polymer-atlas gh-pages
```

Then, in the repository settings under Pages, choose "Deploy from a branch", branch `gh-pages`, folder `/ (root)`.
The output includes a `.nojekyll` marker. The site will be at
`https://polymerindustrycluster.github.io/polymer-atlas/`; all links are relative, so a project sub-path works.

**Option 2: Netlify drag-and-drop.** Run the build, then drag the `build/site` folder onto
<https://app.netlify.com/drop>. With the Netlify CLI the equivalent is `netlify deploy --dir build/site --prod`.
For continuous deployment from git instead, set the build command to
`python3 scripts/build_sqlite.py && python3 scripts/build_site.py` and the publish directory to `build/site`
(choose a Python 3.12 or newer build image).

Either route serves static files only, so there is no server to maintain. Rebuild and re-publish after data passes land;
the footer shows the commit the site was built from and flags uncommitted local data changes.

## Known limitations

- The map's dots are not keyboard-navigable; every site is also reachable from its county page (PIC-18) or its
  organization page.
- A site row with no recorded ring shows its parent organization's ring, marked with an asterisk.
- County pages count site rows with operating status `active` in all tiers (tier U included, broken out by tier);
  the home-page headline counts use tiers A-C only. The two are labelled differently on purpose.
