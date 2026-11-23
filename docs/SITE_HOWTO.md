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
python3 scripts/build_pages.py               # the whole public site: build_site.py plus the three graph pages, into build/pages/
python3 -m unittest scripts/test_build_site.py
```

**One shell.** `page()` in `build_site.py` renders every page: skip link, header with the five-item menu (Find companies, Map, Counties, Research & programs, About the data; on a phone the items sit behind a Menu button, `shell.js`), one `<main id="main">`, the footer and the single stylesheet `style.css`. The three graph builders (`build_graph.py`, `build_geo_graph.py`, `build_events_3d.py`) import `build_site.page()` and render inside it, so the graph, map + network and trade-show pages have the same header, footer and tokens (their `--root` option says where the site root is, default `../`; they only look right published next to `style.css`, which `build_pages.py` does). The five menu items hold no graph pages: the street map, map + network, industry graph, trade shows and the 3D skyline share a "Views" strip under the header. `test_every_html_page_has_the_shared_stylesheet_skip_link_nav_main_and_footer` fails if any built page, graph pages included, loses one of these.

**Tokens.** Colours (one Ring 1-5 palette, `--r1` to `--r5`, and the explorers' data colours), the Lato type scale (`--t-*`) and spacing (`--s-*`) are declared once, at the top of `CSS` in `build_site.py`; the explorer scripts read them from the page with `getComputedStyle`. The graph pages declare no tokens of their own (`test_graph_pages_carry_no_second_set_of_tokens_or_chrome`). The trade-show stage is dark in both colour schemes (`.viz.dark`).

**Table toolbar.** A table with two or more rows, built by `build_site.py` inside a `.table-wrap`, gets one toolbar above it (`sortable.js`): the row count, a filter box when it has more than 12 rows (`data-nofilter` keeps it off a page that filters its own rows), "Download these rows (CSV)" (client-side: the rows and columns on screen) and "Copy link". `data-nosort` removes the sort buttons only. `data-nocsv` removes the download (and the toolbar too, unless the table has more than 12 rows and so a filter box). So the toolbar is not on every table: one-row tables, the county and ring summary tables on the directory page, the directory's own list (which has its own count, download and copy-link above it), the organization-page evidence tables, and the programs and researchers finder (`experts.html`, which draws its own table) have none. The static `directory/<county>.html` pages have it (the download saves the rows on that page). Every page links `directory.csv` and the latest GitHub release in its footer, the graph pages included. `directory.html` and the home page link `search.html`, the Atlas-wide search, for companies outside the 18 PIC counties. The street-map dots take their Ring colours from the same `--r1`..`--r5` tokens as the key. Evidence and source strings are published only as structured fields and links: claim type, source class, strength, observed date and the public URLs found in the citation (`source_urls` in `build_site.py`). Claim text (`claim_detail`), notes, lane ids and the prose around a source link are never rendered, in the pages or in `directory.csv`; `test_no_evidence_claim_text_on_any_organization_page` fails if any appears.

Options: `--db PATH`, `--out DIR`, `--qcew CSV`, `--repo-url URL`. A full build takes a few seconds.

## What it produces

| Path | Content |
|---|---|
| `index.html` | What the Atlas is, headline counts (each with its unit and filter), ring and tier legends, license, "as of" commit and date |
| `map.html`, `sites.json`, `map.js` | Leaflet 1.9.4 map (version pinned, with SRI hashes) of site rows that have coordinates; filters for ring, tier and state, plus an opt-in for non-active sites |
| `search.html`, `orgs.json`, `search.js` | Client-side search over organization and ecosystem rows (name, trade names, city, state, ring) |
| `counties/index.html`, `counties/<county>.html` | Ohio county index and one-pagers for every Ohio county with Atlas rows, PIC-18 first (AGENTS.md §8): site rows by ring and by 3-digit NAICS with a tier breakdown, site table, programs, ecosystem organizations, and the BLS QCEW 2023 private NAICS 326 count benchmark |
| `directory.html`, `directory.js`, `directory.json`, `directory.csv` | Northeast Ohio polymer companies (owner ruling 2026-11-23, ATLAS-39). The page opens with two summary tables, counts by county and by ring, each stating its unit (owners with an active tier A-C site row in a PIC-18 county or ring; an owner is an organization record or an ecosystem record, 787 and 7 at 2026-11-23, DECISIONS.md) and an All PIC-18 line; an owner with sites in two counties is counted in each, so the columns can exceed that line. Below: name search, filters (county, ring, site tier, employee band, process, material, market, ownership; "or" within one filter, "and" across filters; each lists its unknown count) and the list grouped by county, 50 rows at a time (previous/next), one row per owner and county with the street addresses of its site rows in that county ("Street not recorded" when empty). The rows are drawn by `directory.js` from `directory.json`, so the HTML holds none; the address bar holds the filters. "Download these rows (CSV)" saves every filtered row, not just the 50 on screen. A "PIC member" badge marks an organization on the public website member list only (AGENTS.md 5.1); the page never says an organization is not on it. Without JavaScript the search and list stay hidden and the page points to `directory/<county>.html` (`<county>-2.html` ...), the same rows 50 a page with street addresses, plus `directory.csv`. `directory.csv` is the whole table (one row per owner and county; `public_member_list` is `yes` or blank; `pic18_site_addresses` last) |
| `prospects.html`, `prospects.csv` | Kept so links shared before the rename work: `prospects.html` redirects to `directory.html` keeping the query string and hash (`prospects.js`, with a refresh tag for no-JavaScript), `prospects.csv` a byte-identical copy of `directory.csv` (its rows are now per organization and county) |
| `orgs/<record id>.html` | One page per organization and ecosystem organization: fields, sites, the evidence rows (claim type, source class, strength, date, source link; records with no evidence rows yet fall back to their source links), tier, last verified; tombstones are marked, with a successor link |
| `skyline.html`, `skyline.js`, `skyline.json`, `vendor/three.min.js` | The 3D skyline of site rows (three.js r128), linked from the home page. The only page that loads three.js; the home page has a static hero |
| `graph/index.html`, `graph/map.html`, `graph/events.html` | Industry graph (Sigma.js), map + network (d3 and Graphology) and trade shows in 3D (3d-force-graph), from `build_graph.py`, `build_geo_graph.py` and `build_events_3d.py` via `build_pages.py`; each renders inside the shared shell |
| `style.css`, `shell.js`, `sortable.js` | The one shared stylesheet (colour scheme from `prefers-color-scheme`; trade shows stays dark), the phone menu and the table toolbar |

External requests: `map.html` loads Leaflet (unpkg, version 1.9.4) and OpenStreetMap tiles. The three graph pages still load
their libraries from cdnjs.cloudflare.com and cdn.jsdelivr.net (graphology, graphology-library, sigma, d3, topojson-client,
3d-force-graph with its three.js); vendoring them is the next ATLAS-40 pull request. Every other page is self-contained, and
fonts load from the site (`fonts/`).

## Preview locally

`search.html` and `map.html` load JSON with `fetch`, which browsers block for pages opened from disk (`file://`).
Serve the folder instead:

```bash
python3 -m http.server -d build/site 8000     # then open http://localhost:8000/
python3 -m http.server -d build/pages 8000    # the whole site, graph pages included
```

The other pages (home, counties, organizations) also work when opened directly from disk, except for the graph pages,
which need the folder served so that they find `style.css`.

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
