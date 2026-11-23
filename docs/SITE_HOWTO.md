# Building and publishing the Atlas site

`scripts/build_site.py` turns the generated SQLite database into a static website for people who do not
use git: chamber staff, economic developers and members. It is stdlib-only Python (developed on 3.13)
and writes to `build/site/`, which is gitignored. The CSVs in `data/` stay canonical; the script reads
the SQLite file, `docs/denominators/qcew_county_polymer_ohio_pa_2023_2024.csv`, its own assets in `scripts/assets/` and the git revision (for the footer), and never edits `data/`.

## Build

```bash
python3 scripts/build_sqlite.py              # only needed when data/ changed (the site builder builds it if the .db is missing)
python3 scripts/build_site.py                # writes build/site/
python3 scripts/build_site.py --rebuild-db   # rebuild the .db first, then the site
python3 scripts/build_pages.py               # the whole public site: build_site.py plus the three graph pages, into build/pages/
python3 -m unittest scripts/test_build_site.py
```

**One shell.** `page()` in `build_site.py` renders every page: skip link, header with the five-item menu (Find companies, Map, Counties, Research & programs, About the data; on a phone the items sit behind a Menu button, `shell.js`), one `<main id="main">`, the footer and the shared stylesheet `style.css` (the street map adds Leaflet's own). The three graph builders (`build_graph.py`, `build_geo_graph.py`, `build_events_3d.py`) import `build_site.page()` and render inside it, so the graph, map + network and trade-show pages have the same header, footer and tokens (their `--root` option says where the site root is, default `../`; they only look right published next to `style.css`, which `build_pages.py` does). Each writes three files side by side: the page (about 8 kB: shell, a plain summary, the stage), its script (`graph.js`, `map-network.js`, `trade-shows.js`) and its data (`graph.json`, `map-network.json`, `trade-shows.json`; the map also copies `us-counties.json`). **Phones (below 720 px) get the summary, not the canvas:** counts that name their unit and filter, the Ring 1-5 colour key, and links to Find companies, the street map and Counties; `explorer.js` then loads none of the libraries, script or data, so a phone transfers the page (6.8 to 9.7 kB), the shell's script, stylesheet and fonts, and no graph library, script or data: 104 to 107 kB in all in the 2026-11-23 Lighthouse phone runs. From 720 px up, `explorer.js` loads the libraries named in `<main data-libs>` in order, then `data-boot`, which fetches the data (so these pages need the folder served over http). The five menu items hold no graph pages: the street map, map + network, industry graph, trade shows and the 3D skyline share a "Views" strip under the header. `test_every_html_page_has_the_shared_stylesheet_skip_link_nav_main_and_footer` fails if any built page, graph pages included, loses one of these.

**Tokens.** Colours (one Ring 1-5 palette, `--r1` to `--r5`, and the explorers' data colours), the Lato type scale (`--t-*`) and spacing (`--s-*`) are declared once, at the top of `CSS` in `build_site.py`; the explorer scripts read them from the page with `getComputedStyle`. The graph pages declare no tokens of their own (`test_graph_pages_carry_no_second_set_of_tokens_or_chrome`). The trade-show stage is dark in both colour schemes (`.viz.dark`).

**Table toolbar.** A table with two or more rows, built by `build_site.py` inside a `.table-wrap`, gets one toolbar above it (`sortable.js`): the row count, a filter box when it has more than 12 rows (`data-nofilter` keeps it off a page that filters its own rows), "Download these rows (CSV)" (client-side: every row left after the filter, and every column of the table, including a column a narrow screen hides; the experts institution table hides City on a phone and still downloads it) and "Copy link". `data-nosort` removes the sort buttons only. `data-nocsv` removes the download (and the toolbar too, unless the table has more than 12 rows and so a filter box). So the toolbar is not on every table: one-row tables, the county and ring summary tables on the directory page, the directory's own list (which has its own count, download and copy-link above it), and the organization-page evidence tables have no download; those have no toolbar at all unless they hold more than 12 rows, when they get the count, a filter box and Copy link. The programs and researchers finder (`experts.html`) draws its tables after load and hands each to the same enhancer (`window.atlasTable` in `sortable.js`): its institution table has sort buttons, count, "Download these rows (CSV)" and "Copy link"; its results list has a "Download these rows (CSV)" bar for every record that matches (not only the ones drawn so far) and "Copy link". The institution table counts the researcher and program records that match the current search and filters, so it and the count above it always describe the same records. The static `directory/<county>.html` pages have it (the download saves the rows on that page). Every page links `directory.csv` and the latest GitHub release in its footer, the graph pages included. **Labels.** Controlled-vocabulary tokens are shown with `vocab()`: a token in `VOCAB_LABELS` (or the research-specialty list `SPEC_LABELS`) gets a readable label ("corporation_public" is "public corporation", "automotive_unspecified" is "automotive (OEM or aftermarket not stated)"), any other token has its underscores turned into spaces. Every `VOCAB_LABELS` key is checked against `docs/SCHEMA.md` (`test_vocab_labels_are_schema_tokens_and_read_as_words`): a label restates a token, it never adds a term. The county Sites tables carry Street address and ZIP columns (and so does the CSV the toolbar downloads). `directory.html` and the home page link `search.html`, the Atlas-wide search, for companies outside the 18 PIC counties. The street-map dots take their Ring colours from the same `--r1`..`--r5` tokens as the key. Evidence and source strings are published only as structured fields and links: claim type, source class, strength, observed date and the public URLs found in the citation (`source_urls` in `build_site.py`). Claim text (`claim_detail`), notes, lane ids and the prose around a source link are never rendered, in the pages or in `directory.csv`; `test_no_evidence_claim_text_on_any_organization_page` checks claim strings of at least 40 characters (leaving out values a page shows for another reason, such as an address), across the evidence rows of each organization and in a sample of two rows per record for the CSV; it is a sample, not proof that no claim text appears.

Options: `--db PATH`, `--out DIR`, `--qcew CSV`, `--repo-url URL`. A full build takes a few seconds.

## What it produces

| Path | Content |
|---|---|
| `index.html` | What the Atlas is, headline counts (each with its unit and filter), ring and tier legends, license, "as of" commit and date |
| `map.html`, `sites.json`, `map.js` | Leaflet 1.9.4 map (vendored at `vendor/leaflet/`) of site rows that have coordinates; filters for ring, tier and state, plus an opt-in for non-active sites. Each popup shows the site's street address, city, state and ZIP as recorded ("Street not recorded" when there is none; a street is never inferred). Below the map, a list of the site rows shown (50 at a time, with address and a "Show on map" button) is the keyboard route to every dot |
| `search.html`, `orgs.json`, `search.js` | Client-side search over organization and ecosystem rows (name, trade names, city, state, ring). Each result shows the site address of an organization with exactly one active site row ("Street not recorded" if it has none) and, for one with several, how many active site rows it has and that their addresses are on its page; the search box does not take focus on load, so the skip link is the first stop |
| `counties/index.html`, `counties/<county>.html` | Ohio county index and one-pagers for every Ohio county with Atlas rows, PIC-18 first (AGENTS.md §8): site rows by ring and by 3-digit NAICS with a tier breakdown, site table, programs, ecosystem organizations, and the BLS QCEW 2023 private NAICS 326 count benchmark |
| `directory.html`, `directory.js`, `directory.json`, `directory.csv` | Northeast Ohio polymer companies (owner ruling 2026-11-23, ATLAS-39). The page opens with two summary tables, counts by county and by ring, each stating its unit (owners with an active tier A-C site row in a PIC-18 county or ring; an owner is an organization record or an ecosystem record, 787 and 7 at 2026-11-23, DECISIONS.md) and an All PIC-18 line; an owner with sites in two counties is counted in each, so the columns can exceed that line. Below: name search, filters (county, ring, site tier, employee band, process, material, market, ownership, and "On the public PIC member list": Yes or No; "or" within one filter, "and" across filters; each lists its unknown count except the member flag, which is yes or no by construction, and every count beside a choice and in the status line is **companies**: distinct organizations, an owner in two counties counts once; the status line also says how many rows, one per owner and county, those companies take; the download stays one row per owner and county) and the list grouped by county, 50 rows at a time (previous/next), one row per owner and county with the street addresses of its site rows in that county ("Street not recorded" when empty). On a phone the two summary tables sit in a block that starts closed (it is open on a larger screen and without JavaScript; a link at the top, "Counts by county and ring", opens it and jumps there) and the filter groups start collapsed, so the list follows the page's own tab order: at 390 x 844 the first company starts at y = 1,571 px, where it started at y = 5,076 px with the summary first and four groups open. The rows are drawn by `directory.js` from `directory.json`, so the HTML holds none; the address bar holds the filters. "Download these rows (CSV)" saves every filtered row, not just the 50 on screen. A "PIC member" badge marks an organization on the public website member list only (AGENTS.md 5.1), and the member filter reads the same public flag (`pic_member`) and nothing else. Its No choice means "not on the public member list", and the page says in a banner that this is not the same as "not a member" (the caveat of the pre-ATLAS-39 prospects page, without its last sentence, which used a word the site bars); organization pages, the CSV and `directory.json` never state absence. An old link such as `prospects.html?member=no` keeps its query through the redirect and applies the filter. Without JavaScript the search and list stay hidden and the page points to `directory/<county>.html` (`<county>-2.html` ...), the same rows 50 a page with street addresses, plus `directory.csv`. `directory.csv` is the whole table (one row per owner and county; `public_member_list` is `yes` or blank; `pic18_site_addresses` last) |
| `prospects.html`, `prospects.csv` | Kept so links shared before the rename work: `prospects.html` redirects to `directory.html`: with JavaScript it keeps the query string and hash (`prospects.js`); without JavaScript a refresh tag sends it to `directory.html` alone, so the filters in the link are lost, `prospects.csv` a byte-identical copy of `directory.csv` (its rows are now per organization and county) |
| `orgs/<record id>.html` | One page per organization and ecosystem organization: fields, sites, the evidence rows (claim type, source class, strength, date, source link; records with no evidence rows yet fall back to their source links), tier, last verified; tombstones are marked, with a link to the successor where the record names one (an acquired record with none recorded is marked and has no link) |
| `skyline.html`, `skyline.js`, `skyline.json`, `vendor/three.min.js` | The 3D skyline of site rows (three.js r128), linked from the home page. The only page that loads `vendor/three.min.js`; the trade-show page's 3d-force-graph bundle carries its own three.js. The home page has a static hero |
| `graph/index.html`, `graph/map.html`, `graph/events.html` and beside them `graph.js`/`graph.json`, `map-network.js`/`map-network.json`/`us-counties.json`, `trade-shows.js`/`trade-shows.json` | Industry graph (Sigma.js), map + network (d3 and Graphology) and trade shows in 3D (3d-force-graph), from `build_graph.py`, `build_geo_graph.py` and `build_events_3d.py` via `build_pages.py`; each renders inside the shared shell, with a plain summary on phones |
| `explorer.js`, `vendor/<lib>/` | The loader for the three pages above, and the vendored libraries (each with `LICENSE` and `SHA256SUMS`) |
| `style.css`, `shell.js`, `sortable.js` | The one shared stylesheet (colour scheme from `prefers-color-scheme`; trade shows stays dark), the phone menu and the table toolbar |

External requests: the only one the site makes is OpenStreetMap tiles on `map.html` (`map.js`). Every JavaScript library is
vendored in `scripts/assets/vendor/<lib>/` and published at `vendor/<lib>/`: graphology 0.25.4, graphology-library 0.8.0,
sigma 2.4.0, d3 7.9.0, topojson-client 3.1.0, 3d-force-graph 1.73.4 (it bundles three.js) and Leaflet 1.9.4, plus three.js r128 at `vendor/three.min.js` for the skyline page, which is copied from `scripts/assets/three/` and is not one of the seven pins below. `python3 scripts/assets/vendor/vendor_libs.py` re-creates the seven packages:
it reads each pin's record from the npm registry, checks the tarball against the registry's published sha512 integrity and sha1
shasum, unpacks it in its own empty directory and copies only the dist files and the LICENSE; each folder's `SHA256SUMS` carries
the integrity line it was checked against and the sha256 of every file kept. `scripts/test_site_vendor.py` re-hashes them
offline (`vendor/three.min.js` is not covered). `test_no_page_or_script_asks_another_host_for_anything_but_osm_tiles` parses every built HTML page for a `src`, `href`, `data`, `poster` or `srcset` that names another host on a script, link, img, iframe, source, video, audio, embed or object tag, and scans our own scripts (not `vendor/`) for `fetch(`, `importScripts(`, `.src =` or `new URL(` with an absolute URL. It does not read CSS `url()`, outbound `<a>` links, or URLs a script builds from parts (the map's tile URL is one: it is passed to Leaflet as a template); that the browser asks only OpenStreetMap was checked with request logs in Chrome. Fonts load from the site (`fonts/`).

## Preview locally

`search.html`, `map.html`, `directory.html`, `experts.html`, `skyline.html` and the three graph pages load JSON with `fetch`, which browsers block for pages opened from disk (`file://`).
Serve the folder instead:

```bash
python3 -m http.server -d build/pages 8000    # then open http://localhost:8000/ (the whole site; build/site, from build_site.py alone, has no graph pages)
```

The pages that do not fetch data (home, counties, organizations) also work when opened directly from disk (`style.css` loads from disk too).

## What is deliberately not published

The generator renders a whitelist of public business fields. It never writes `notes`, `created_by`,
`pic_relevance` (prospecting stages) or any other internal column. It also withholds:

- Source entries that refer to the PIC CRM or to staging/workshop paths (neither their text nor a link inside them), and one-line
  descriptions that mention the CRM or carry build and review wording (the blind audits' leak scan, `INTERNAL_RE`, plus a temporary record id such as `NEW:MJ-07`; it also withholds the odd ordinary description, such as one that names Council Bluffs), on the organization pages and in the graph pages' data (AGENTS.md section 5.1). A source list says how many
  entries were left out; the repository CSV keeps the full text. `test_crm_marked_sources_never_render_and_the_omitted_count_is_stated` fails if one renders. A source entry is withheld when it names the CRM (any capitalisation), a path under `staging/`, `workshop/`, `working/` or `internal/` in the entry's own text (a public URL that happens to contain one of those folder names, and the bare words, stay), or the folder names `crm-export`, `crm-crossref` and `pic-member-list`; a citation of PIC's public member list ("Public PIC member list") is a public source and stays.
- Profile and other links that embed an email address, literally or percent-encoded, including the organization and event links in the graph data (the researcher is still listed, without a link).
- Per-person pages. Professors and federal-lab research staff appear only as name, role as published, research
  specialties and public profile URL, on their institution's page and in the programs and researchers finder, `experts.html`, and its CSV (AGENTS.md section 6).

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
python3 scripts/build_pages.py          # the whole site, graph pages included (build_site.py alone leaves out graph/)
cd build/pages
git init -b gh-pages
git add -A && git commit -m "Atlas site build $(date +%F)"
git push --force https://github.com/polymerindustrycluster/polymer-atlas gh-pages
```

Then, in the repository settings under Pages, choose "Deploy from a branch", branch `gh-pages`, folder `/ (root)`.
The output includes a `.nojekyll` marker. The site will be at
`https://polymerindustrycluster.github.io/polymer-atlas/`. Pages link relative to themselves, so a project sub-path works, except `404.html`, whose links are absolute under `/polymer-atlas/` on purpose: served from another path it is unstyled and its links miss.

**Option 2: Netlify drag-and-drop.** Run `python3 scripts/build_pages.py`, then drag the `build/pages` folder onto
<https://app.netlify.com/drop>. With the Netlify CLI the equivalent is `netlify deploy --dir build/pages --prod`.
For continuous deployment from git instead, set the build command to `python3 scripts/build_pages.py` and the publish directory to
`build/pages` (it builds the database first; the `404.html` caveat above applies at a site root)
(choose a Python 3.12 or newer build image).

Either route serves static files only, so there is no server to maintain. Rebuild and re-publish after data passes land;
the footer shows the commit the site was built from and flags uncommitted local data changes.

## Known limitations

- The street map's dots are not keyboard-navigable (Leaflet draws them on a canvas); the list below the map and every site's county or organization page are the keyboard routes.
- The trade-show page is a 3D canvas with a presentation mode; on a phone it is replaced by its text summary, and its play controls take the keyboard (Space on a focused button presses that button).
- A site row with no recorded ring shows its parent organization's ring, marked with an asterisk.
- County pages count site rows with operating status `active` in all tiers (tier U included, broken out by tier);
  the home-page headline counts use tiers A-C only. The two are labelled differently on purpose.
