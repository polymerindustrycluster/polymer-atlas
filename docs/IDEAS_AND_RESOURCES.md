# Ideas & resources register

A standing list of improvements, future data layers, and public sources nobody has
worked yet. The point is that a good idea doesn't vanish when the session that had
it ends. **This is not a task queue.** To work an item:

1. Copy it into `tasks/QUEUE.md` as a task and claim it (AGENTS.md §2 rule 1).
2. Change its **Status** here to `queued → <QUEUE line>`.

Items tagged **OWNER** gate on an owner ruling (AGENTS.md §2 rule 9). Write those
up as battery items with a recommendation. Never self-rule them.

Sources already documented in `docs/SOURCES.md` are not repeated below. This file
lists only sources that are not there yet, or that are there but have never been
worked for the purpose named here.

Status values: `idea` · `scoped` (route and terms checked) · `queued → …` · `done → …` · `rejected (reason)`.
Started 2026-11-01 from a whole-repo review (`docs/reviews/FIELD_FILL_PROFILE_2026-11-01.md`,
`docs/denominators/README.md`). Add new items at the end of their section with the
next free number. Never renumber.

---

## A. Coverage — the national gap

QCEW 2023 counts **14,200** private NAICS 326 establishments in the US. The Atlas
holds **2,201** site rows coded NAICS 326 under the strict filter: active or
unknown status, tier A/B/C, with Ohio at 815 of 890 and Pennsylvania at 396 of
642. Outside those two states, coverage is mostly large TRI reporters. The biggest
gaps by count are CA (1,267), TX (869), FL (775), MI (772), IL (755), GA, IN, WI,
NY, NC. Figures and caveats are in `docs/denominators/README.md`. A count ratio is
not matched coverage.

| ID | Idea | Why | Status |
|---|---|---|---|
| A-01 | **OSHA Injury Tracking Application (ITA) establishment files.** Annual CSV per establishment: name, street address, NAICS, annual average employees, total hours. https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data | It covers establishments with 20+ employees in manufacturing, the small and mid-size processors TRI misses. It also gives a **site employee count**, so it fixes the employee-band gap (1.8% filled). Unlike TRI, it's a size source. The page returns 403 to plain curl, so download it by hand or through a browser route. Check how SCHEMA's banding rule treats a stated count. | idea |
| A-02 | **SAM.gov public entity extract.** UEI, CAGE code, physical address, self-reported NAICS. https://sam.gov/data-services | It covers every federal-contract-eligible firm, and UEI is already in the `REGISTRIES` enum but unused. Self-reported NAICS = `company_disclosed`. | idea |
| A-03 | **Census ZIP Business Patterns + CBP employment-size classes.** https://www.census.gov/programs-surveys/cbp.html | It gives the *shape* of the gap: how many missing establishments are 1–19 employees versus 100+. That says which source can close it, since TRI only reaches the large end. | idea |
| A-04 | **EPA ECHO / FRS bulk by NAICS 325211/3252/326xx for all states** (FRS is in SOURCES.md but was worked as a TRI sideways pull for PA/OH only). https://echo.epa.gov/tools/data-downloads | Air, water and RCRA permittees include small molders with a regenerative oxidizer or stormwater permit. | idea |
| A-05 | **State manufacturer directories** published free by state EDOs or MEPs (e.g. Michigan, Indiana, Wisconsin, Texas). | One state at a time, matching the spine order in QUEUE Phase 4. These are directory-class sources (tier ceiling B, SCHEMA §4.13). | idea |
| A-06 | **Association member directories not yet harvested:** PLASTICS Industry Association, Plastics Pipe Institute, Vinyl Institute, EPS Industry Alliance, Flexible Packaging Association, Foodservice Packaging Institute, American Composites Manufacturers Association, Polyurethane Manufacturers Association, Adhesive & Sealant Council, American Mold Builders Association, Association of Plastic Recyclers, Recycled Materials Association (ReMA). | `member_of` edges are authored and sourced to a public snapshot (AGENTS.md §4), so each directory both discovers firms and creates edges. | PMA scouted 2026-11-06: CORROBORATION_ONLY; 3/20 verified-new leads; publication rights held. [packet](../tasks/source-scout-3-2026-11-06/association/README.md) |
| A-07 | **Operation Clean Sweep (OCS Blue) public participant list** (pellet-loss program, PLASTICS/ACC). | A resin-handler roster, and a circularity/environment signal (see E-04). | idea |
| A-08 | **USPTO PatentsView assignees by CPC C08** (polymers), **B29** (plastics shaping), **C09J** (adhesives), **B60C** (tires). https://patentsview.org | Finds R&D-active firms and gives an innovation layer (see D-05). Assignee address = HQ-grade lead only. | scouted 2026-11-06: CORROBORATION_ONLY via USPTO bulk; 79 PIC-18 held organization candidates, ownership total held. [packet](../tasks/source-scout-3-2026-11-06/patentsview/README.md) |
| A-09 | **IAF CertSearch** (accredited ISO certificates). https://www.iafcertsearch.org | Verifies ISO 9001 / 13485 / IATF 16949 per site, which fills the `certifications` column (enum exists, see current fill profile), and is also a discovery route. Check terms. | CLOSED public extraction 2026-11-06: copying/redistribution restricted; no certificate sample. [terms gate](../tasks/source-scout-3-2026-11-06/iaf/README.md) |
| A-10 | **UL Product iQ** "Recognized Component — plastics" listings, and **NSF/ANSI 61** listings (pipe, potable-water parts). | Certification facts per manufacturer and plant. Terms check first, since these may be licensed. | idea |
| A-11 | **Census Nonemployer Statistics** for 326. | Shows how much of the universe is one-person shops. It sets an honest floor for "complete". | idea |
| A-12 | **OWNER — North America scope.** Canada/Mexico plants of held parents (there are already 4 ON, 2 QC, 1 BC rows in `sites_INTL`). | Supply chains are continental, and USMCA reshoring is a PIC talking point. Needs a scope ruling plus a dated schema revision for shards. | idea |

## B. Fill the empty high-value fields

All counts are site rows or organization rows, all tiers and statuses, from
`docs/reviews/FIELD_FILL_PROFILE_2026-11-01.md`.

| ID | Idea | Gap today | Status |
|---|---|---|---|
| B-01 | **`markets_served` pass** from each company's own "industries we serve" page. Own-site class, supports A. | 7 of 5,773 sites; 24 of 4,180 orgs | idea |
| B-02 | **Employee bands** via A-01 (OSHA ITA), Form 5500 participant counts (**OWNER**: is a plan participant count admissible as a size band input?), and own-site statements. | 105 sites / 251 orgs informative | idea |
| B-03 | **Ohio capabilities backfill.** Ohio site rows have `processes` at 21% and `materials` at 8%, versus about 74% and 72% elsewhere. The home turf is the thinnest. | 2,009 Ohio sites | idea |
| B-04 | **Ohio street addresses.** 144 of 2,009 Ohio sites (7.2%) have `street_address`, versus about 90% elsewhere. That blocks address-first dedupe (AGENTS.md §3 step 3) in the state that matters most. | 1,865 Ohio sites | idea |
| B-05 | **Evidence backfill for pre-v1.6 records.** Tier A first, because 79.6% of Tier A orgs have no evidence row. | 2,381 orgs, 3,491 sites | idea |
| B-06 | **`entity_type` / `ownership_type`** from Secretary of State filings and own-site "about" pages. A private-equity ownership layer is a major industry story. | Ohio-HQ orgs 2.2% / 0.7% | idea |
| B-07 | **Certifications** via A-09 and own-site quality pages. ISO 13485 marks medical, IATF 16949 marks automotive, AS9100 marks aerospace. That's the supplier-matching core. | 0 rows | idea |
| B-08 | **Machinery and capacity facts** (press count / tonnage range, extrusion lines, cleanroom class, sq ft). SCHEMA §4.5 lists them as "Nice … collect systematically in v2". **OWNER**: schedule v2 columns. | no columns yet | idea |
| B-09 | **Validator debt** (V-45..V-48, 890 grandfathered rows): see `tasks/validator-debt-2026-11-01/`. | 175 site_type, 383 ring, 312 NAICS provenance, 20 bands | queued → QUEUE "Validator debt" |
| B-10 | **`hq_country` normalization** (`US` 4,037, `USA` 53, `United States` 45, plus spelled-out country names) and a validator rule for ISO alpha-2. | 98+ org rows | idea |
| B-11 | **OWNER — `members.member_since` year-only.** AGENTS.md §4 bans year-only dates, but `validate.py` *requires* a 4-digit year for `member_since`. The two rules contradict, so one needs a ruling. | 1 row | idea |
| B-12 | **Registry crosswalk expansion:** EIN (from the Form 5500 hits already worked), SAM UEI, EPA FRS registry ID, OSHA establishment ID, SEC CIK for every public parent. Stable joins are the Atlas's lasting value. | LEI 132, SEC 15, Wikidata 19 | idea |

## C. Freshness and liveness

| ID | Idea | Why | Status |
|---|---|---|---|
| C-01 | **Staggered re-verification rotation.** Every `last_verified` falls in 2026-10, so the whole Atlas ages at once. Rotate about 1/12 of records per month, oldest and Tier A first. | Prevents a cliff | idea |
| C-02 | **Automated liveness sweep** (packet lane): website resolves, SOS status, newest Form 5500 year, newest TRI year. A hit queues re-verification and never changes status (AGENTS.md §3). | Only 5 orgs are closed out of 4,180. Small manufacturers close at several percent a year, so dead records are almost certainly present. | idea |
| C-03 | **OWNER — activate the news / WARN monitor** (built and dry-run validated, per QUEUE "Weekly signals sweep"). | Turns the Atlas from a snapshot into a living record | idea |
| C-04 | **Change feed:** a generated `CHANGELOG`/RSS of record creations and status changes per pass, built from git diffs of `data/`. | Lets PIC staff and EDOs follow changes without git | idea |
| C-05 | **Per-edition event roster snapshots** (already queued). Extend to state EDO announcement pages and tax-credit minutes as a dated investment-signal stream. | Expansion and closure timeline | idea |

## D. New data layers (most need OWNER scope rulings)

| ID | Idea | Notes | Status |
|---|---|---|---|
| D-01 | **Supply-chain edges:** supplier→customer, toll processor, distributor carries resin line X. `relationships.csv` holds only ownership and membership today. | Distributor **line cards** are public pages. Needs new `REL_TYPES` (**OWNER**). | idea |
| D-02 | **Investment and closure timeline table:** dated announcements (capex $, jobs, sq ft), grants, closures, each with a source. | SCHEMA addition (**OWNER**). Feeds C-03/C-05. | idea |
| D-03 | **Resin and compound capacity** (tonnes/yr) per Ring 1–2 plant, from 10-Ks, press releases and permit applications. | Public-source only. Never copied from licensed capacity databases (AGENTS.md §5). | idea |
| D-04 | **Circularity layer:** mechanical recyclers, MRFs and plastics recovery facilities, advanced/chemical recycling plants, PCR compounders. Also state packaging-law (EPR) producer registrations (OR, CO, CA SB 54, …) and the EPA Recycling Infrastructure map. | Only about 62 recycling site rows exist. Strong policy tailwind. | idea |
| D-05 | **Innovation layer:** patents (A-08), SBIR/STTR awards (scout in progress), federal grants to firms and labs, university–industry partnerships (`match_program_capabilities.py` is a start). | | Patent candidate packet available 2026-11-06 (A-08); confirmed organization ownership count and storage schema held for adjudication/owner ruling. |
| D-06 | **Regulatory exposure:** TSCA §8(a)(7) PFAS reporting (fluoropolymer firms); Minnesota and Maine PFAS-in-products reporting; TRI chemical profile per site. | Facts about firms, not judgments. Evidence rows only. | idea |
| D-07 | **Foreign direct investment view:** ultimate parent country for every site. Japanese, German and Korean ownership of Ohio plants is a standard EDO question. | Needs `ultimate_parent_org_id` records for foreign parents (only 32 INTL org rows today). | idea |
| D-08 | **Workforce layer:** BLS OEWS wages for plastics occupations (51-4072, 51-4021, 51-9197…), QCEW average pay per county × NAICS (now in `docs/denominators/`), IPEDS completions by CIP (programs table), registered apprenticeships (DOL RAPIDS). | Talent supply vs demand by county | idea |
| D-09 | **Products/brands:** a light table of consumer brands → manufacturing site, for public storytelling ("made in NE Ohio"). | **OWNER** scope | idea |
| D-11 | **Economic pulse context data:** FRED producer-price and production indexes, BLS NAICS 326 employment and earnings, BEA state GDP for NAICS 326, EIA industrial energy prices (`docs/indicators/`, `scripts/build_indicators.py`; keys from env). Ohio was 6.8% of US NAICS 326 GDP in 2025, down from 8.1% in 2020. | Context only, with vintages; never evidence for a record | done → `docs/indicators/` |
| D-10 | **Federal programs anchoring the cluster:** EDA Tech Hubs (the NE Ohio Sustainable Polymers Tech Hub), NIST MEP centers per state (MAGNET in NE Ohio), Manufacturing USA institutes with polymer work (IACMI composites, America Makes, LIFT, REMADE). | Ecosystem rows. Check which are held. | idea |

## E. Product — make it usable by people, not just agents

| ID | Idea | Notes | Status |
|---|---|---|---|
| E-01 | **Cut releases** (`scripts/export_release.py`, `docs/RELEASE_HOWTO.md`). No GitHub Release exists yet, though the README says SQLite is attached to releases. | Owner pushes the button | scoped |
| E-02 | **Public explorer:** Datasette (or datasette-lite on GitHub Pages / Netlify) over the release DB, with saved queries such as "Ring 1 sites in PIC-12 by county" and "processors with ISO 13485 within 50 mi". | Static, no server to maintain | idea |
| E-03 | **Map:** sites by ring and county with a filter panel. 72% of site rows have coordinates. | Coordinates are reference data, never evidence (AGENTS.md §1) | idea |
| E-04 | **County one-pagers** (PIC-12 first): establishments by ring, top employers (where bands are known), programs, a QCEW benchmark, generated from the DB. | The artifact a chamber actually hands out | idea |
| E-05 | **Supplier / partner finder:** process × material × certification × geography query, plus the program-capability matcher. | Depends on B-01/B-03/B-07 | idea |
| E-06 | **Member-recruitment view for PIC:** in-scope NE Ohio establishments without the public member flag. Only 35 orgs carry it. | Internal use. The publish line is §5.1. | idea |
| E-07 | **"Claim / correct my record" GitHub issue forms** for companies, plus a **removal request** form for people records (836 people rows). | It's a privacy obligation, and corrections from companies are the cheapest way to keep records fresh | idea |
| E-08 | **Citable dataset:** Zenodo DOI via the GitHub integration; mirror on Hugging Face Datasets. | **OWNER** | idea |
| E-09 | **Annual "State of the Polymer Cluster" report** generated from the DB plus QCEW (counts always with unit + filter). | | idea |
| E-10 | **Semantic search** over `description_1line` and capability text (embeddings in the release, not in canonical data). | Helps both agents and humans | idea |
| E-11 | **Graph explorer (Obsidian-style):** `scripts/build_graph.py` → `build/graph/index.html`, one self-contained page using Sigma.js + Graphology (WebGL, ForceAtlas2 layout, Louvain clusters). Nodes are organizations, institutions, vocabulary tags (processes/materials/markets) and event series; edges are tags, ownership, association membership, program specialties and event participation; scope PIC-12 / Ohio / all. Public fields only (tested). Free-text capability values show as marked "free-text tags": about 79% of site `processes` values are off-vocabulary, the main reason Ohio looks sparse. | Publishing is an owner decision (e.g. GitHub Pages next to E-02) | built 2026-11-02 |
| E-12 | **Map/graph hybrid + 3D show presentation:** `scripts/build_geo_graph.py` → `build/graph/map.html` puts sites at their coordinates on an Albers USA map, with PIC-12 counties outlined and company-network arcs from each parent's HQ site. A Geography ↔ Network toggle morphs the same dots into a ForceAtlas2 layout around capability tags (d3 + topojson + Graphology; vendored us-atlas geometry, ISC). `scripts/build_events_3d.py` → `build/graph/events.html` is a 3D network of event series and participants (3d-force-graph). "Present" auto-tours the shows, largest first, with captions (Ohio and PIC-12 counts) and a PIC-12 spotlight. Cosmograph was not used: the Atlas is about 5k nodes, below where it pays off. | Coordinates exist for 4,113 of 5,716 non-closed sites (the rest have none or fall outside the US frame) | built 2026-11-02 |

## F. Multi-agent operations (Grok, Muse, Dot, Duet, Claude…)

| ID | Idea | Notes | Status |
|---|---|---|---|
| F-01 | **Agent quickstart** (`docs/AGENT_QUICKSTART.md`): a short brief so an agent need not read 290 KB before its first edit. | | done → this PR |
| F-02 | **Machine-readable vocabularies** (`docs/schema/vocab.json`, derived from the validator, parity-tested). | | done → this PR |
| F-03 | **Rules as tools:** `scripts/atlas.py` (`next-id`, `dedupe-check`, `show`, `shard-of`). | | done → this PR |
| F-04 | **Read-only MCP server** (`scripts/atlas_mcp_server.py`) so any harness can query the Atlas. | | done → this PR |
| F-05 | **CI:** `docs/ci/validate.yml`, which the owner commits to `.github/workflows/` (the App lacks Workflows permission). Then revisit campaign mode by dated revision. | **OWNER** action | scoped |
| F-06 | **One file per task** (`tasks/open/T-####.md`, claimed by PR) instead of one 52 KB `QUEUE.md` that every harness edits. Archive done items. | Removes the biggest merge-conflict hotspot. **OWNER** process change. | idea |
| F-07 | **SCHEMA v2 consolidation:** fold dated rulings into the rules, move history to `docs/SCHEMA_CHANGELOG.md`, target under 60 KB. | Agents currently read precedent soup | idea |
| F-08 | **Packet JSON schema + `atlas lint-packet`**, so lane packets from any harness are machine-checkable before the integrator reads them. | | idea |
| F-09 | **Harness scorecard:** blind-audit agreement and field-error rates per `created_by` harness, published per pass. | Shows which harness to trust for which lane. Audit 6 measured 12/37 field errors. | idea |
| F-10 | **Get local staging into version control** (a private repo is fine): pass journals, the snapshot sync log, banked raw snapshots, requeue lists, decision memos. | The F5 audit was already blocked by inputs "not in the public tree". This is the largest bus-factor risk. **OWNER** | idea |
| F-11 | **Close or refresh stale draft PRs** whose packets QUEUE records as applied (e.g. #7, #11). Agents told to check open PRs for claims are misled by them. | Owner or PR authors | idea |
| F-12 | **Normalize `created_by`** to a harness/agent registry (e.g. `docs/HARNESSES.md`: id, operator, model family, lanes allowed). | Enables F-09 | idea |
| F-13 | **Cost and yield ledger per pass** (agent-hours or tokens per verified row), so the owner can price waves. The "Q03–Q15 ~29% yield" doctrine already reasons this way. | | idea |

## G. Governance and continuity

| ID | Idea | Notes | Status |
|---|---|---|---|
| G-01 | **LICENSE file.** The README states CC BY 4.0 (data) + MIT (scripts), but the repo has no LICENSE file. Root files are outside the "only data/docs/scripts/tasks travel" rule, so the owner adds it. | **OWNER** | idea |
| G-02 | **Delegate for rulings:** a named deputy who can rule on routine battery items when the owner is unavailable. Scope, ring and vocab rulings currently queue on one person. | **OWNER** | idea |
| G-03 | **Data-sharing MOUs** (JobsOhio / Shale Crescent 616-company list, Team NEO, MEPs). The JobsOhio email draft is already written and awaiting send approval. | **OWNER** | idea |
| G-04 | **Sustainability plan:** who maintains the Atlas after the campaign, what cadence, what budget. | | idea |
| G-05 | **Usage telemetry** (release downloads, explorer queries) to learn which fields people actually use and prioritize B-items. | | idea |
