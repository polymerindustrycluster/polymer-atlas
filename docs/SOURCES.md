# Sources & Method

> **Snapshot notice — F5 audit, 2026-10-30:** Counts and source claims below are historical to their stated pass/date, not current inventory or newly verified external statistics. See the [pinned count audit](reviews/F5_PUBLIC_COUNTS_2026-10-30.md) for current units/filters, corrections, reproducible results and missing-denominator limitations. Historical dates and observations are retained.
> **Attribution correction:** Numerically reproducing 996 from a CBP definition does not prove the strategic framework used that definition. The banked CBP extract and author methodology are absent here; historical firm/establishment ranges are not verified current statistics.

How this database is built: which sources feed it, what each source is actually
good for, and the data-quality failure modes we have learned to defend against.
The methodology is part of the contribution — another region building the same
kind of database should be able to reuse this page wholesale.

## Principles

1. **Licensed sources are discovery leads only.** Commercial directories and
   trade-press databases may point us at a company, but no fact enters this
   database from them. Every fact is verified against a primary or public
   source — the company's own website, a government filing or dataset, an
   association directory, or trade-press reporting of a specific event — and
   cited to that source.
2. **Existence is not activity.** Registries and directories keep listing
   facilities after they close. A record is only as current as its most recent
   dated evidence of operation.
3. **County comes from the physical address**, never from the mailing city.
   Postal cities and ZIP codes straddle county lines constantly.
4. **Counts name their unit and filter.** Establishments, companies, and
   directory location records are different things; any total stated without
   its unit is a category error.
5. **When in doubt, don't merge.** A false merge destroys data; a false split
   is cheap to fix. Records are never deleted — closed, acquired, and merged
   entities are tombstoned with a successor pointer.

## Source classes at a glance

| Source | Class | Public access pattern | What it is good for here | Standing |
|---|---|---|---|---|
| US EPA Facility Registry Service (FRS) | Government dataset | Free bulk state files | Facility addresses, ZIPs, counties, and government-filed industry codes for the regulated subset; a second source for existence | Core pipeline |
| EPA FRS — SIC-code sideways pull | Government dataset | Free bulk state files | Re-querying the registry by legacy SIC codes catches facilities whose modern industry code files them outside the sector (a rubber-products plant coded as apparel). Leads only: measured verification rate under 8% — the SIC witness is noisy in both directions | Leads only |
| US EPA Toxics Release Inventory (TRI) | Government dataset | Free per-state annual files | **Dated** evidence a facility operated in a reporting year; facility-reported parent companies | Core pipeline |
| US EPA ECHO | Government dataset | Free web exports | Dated compliance, inspection, and permit activity — the currency cross-check on registry matches | Planned complement |
| Ohio WARN notices (ODJFS) | Government dataset | Free compiled files + per-notice PDFs | Closure/layoff status evidence for larger employers; notices queue adjudication, they never auto-close a record | Core pipeline |
| OSHA establishment & inspection data (DOL) | Government dataset | Public data portal (free API key) | An inspection is dated proof an establishment operated at that address on that date | Awaiting API key |
| openFDA device registration & listing | Government dataset | Free public API | Medical-device establishment discovery and registration currency (annual expiry) for the downstream-OEM ring | Core pipeline |
| SEC EDGAR | Registry | Free, public | Subsidiary lists (Exhibit 21), closure/acquisition monitoring for public parents — primary-source status evidence | Core pipeline |
| GLEIF (LEI) | Registry | Free public API | Legal-name history (including previous names — prime dedupe evidence) and published parent/child relationships where issuers report them | Core pipeline |
| ProPublica Nonprofit Explorer | Registry | Free public API | Existence, filing currency, and scale for nonprofit ecosystem organizations (IRS Form 990 data) | Core pipeline |
| USAspending | Government dataset | Free public API + bulk archives | Federally active firms in testing, R&D, and defense-adjacent codes | Bulk route only (live search is unreliable at scale) |
| NSF Award Search / SBIR award files | Government dataset | Free public API / free award files | University program corroboration; small-firm R&D discovery | Core pipeline |
| Internet Archive Wayback Machine (CDX) | Archive | Free public API | Website-liveness evidence — with strict interpretation rules (below) | Core pipeline |
| Census County Business Patterns + BLS QCEW | Government statistics | Free published files | The denominators: official establishment counts by county × industry that every coverage claim is measured against | Denominators |
| Census batch geocoder + TIGERweb | Government geospatial | Free batch + point services | Coordinates for every site; authoritative county resolution for disputed addresses | Core pipeline |
| County auditor / parcel records | Government dataset | Free per-county GIS | Settling county disputes — parcel and tax-district evidence outranks geocode centroids | Targeted use |
| County parcel fabrics + statewide parcel layer (OGRIP) | Government dataset | Free per-county GIS services + one statewide layer | Systematic discovery and county settlement: industrial land-use parcels joined on physical address surface plants directories miss, and parcel records settle a site's county from its land, not its mailing city. Parcel owners are leads only (often a realty LLC, never assumed to be the operator); the statewide layer publishes no owner field and its coverage is uneven, so its misses settle nothing | Core pipeline |
| State Secretary of State business search | Registry | Free per-entity lookup | Legal existence and entity status — the settling fact for "does this entity legally exist" (not whether it operates) | Core pipeline |
| Economic-development announcements (state jobs agency, tax-credit authority minutes) | Government announcements | Free public releases + minutes | New-plant and expansion discovery; tax-credit amendments uniquely record cancellations and moves — negative evidence most sources never publish | Monitoring |
| Trade & business press monitoring (news aggregation, wire RSS feeds) | News | Free RSS / public APIs | Event monitoring: openings, expansions, closures, renames — regional and trade press carry the private-company events the wires miss | Monitoring |
| Job postings (state job board) | Jobs | Free public search | A production-role posting by the direct employer, in the plant's locality, is a dated operating signal | Liveness evidence |
| SBA Paycheck Protection Program (PPP) loan data | Government dataset | Free bulk FOIA release | Small-shop discovery where directories are thinnest: a loan is dated existence evidence at a stated address under a borrower-reported industry code. Vintage 2020–21 — a loan proves a firm existed then, not that it operates now, so every candidate still needs a current witness. Sole-proprietor rows are excluded by rule (they carry personal names); demographic fields are never carried. Measured verification rate ~38% in the core plastics/rubber/resin codes; distribution and testing codes verified at 0% and are corroboration-only | Discovery (core codes) |
| Ohio Tax Credit Authority — Jobs Creation Tax Credit meeting minutes | Government announcements | Free public minutes (some scanned, OCR'd) | Project approvals name the company, the locality, and the job commitments behind expansions and new plants — the highest-precision discovery list we have measured (~41% verified). Coverage has gaps: not every meeting's minutes are retrievable | Discovery |
| Ohio EPA industrial stormwater general-permit coverage list | Government dataset | Free public permit records | Facilities holding industrial stormwater coverage are operating industrial sites by definition; the permittee list is a discovery floor for regulated plants (measured verification rate ~20%). The sector screen is partial — an unscreened residue remains, so the list understates rather than overstates | Discovery |
| US DOL Form 5500 / 5500-SF filings (EFAST2) | Government filings | Free public database | An employer's benefit-plan filing proves an employer address with active plan participants as of the filing date — dated operating evidence for exactly the small private firms the web misses. It proves an employer address, not a plant, and absence is weak (small employers may file the short form or be exempt). Run as the standing check before any record is rejected for closure or no-establishment | Core pipeline |
| US bills of lading (import records) | Trade data | Free-tier web service | Importer/distributor discovery and shipment-recency activity evidence for import-dependent firms | Planned |
| Association member directories (rubber, adhesives, composites, mold builders, processors) | Association | Public lists/PDFs where published; member-gated elsewhere | Discovery of small and mid-size firms other sources under-cover, and an independent second source family for corroboration. Membership proves membership — never activity by itself | Core pipeline where public |
| Trade-show exhibitor lists | Trade shows | Public rosters/directories, snapshotted per edition | Exhibiting is a dated, market-facing activity attestation with the exhibitor's own-words description — strong ring-classification evidence. Rosters are perishable: snapshot the current edition or lose it | Core pipeline |
| Commercial directories (licensed) | Directory | Licensed directory data via public-library access, discovery leads only | Gap-filling leads and capability tags — every lead re-verified publicly before use (Principle 1) | Leads only |
| Trade-press rankings & databases (licensed) | Directory | Subscription, discovery leads only | Processor rankings as a discovery spine for the plastics segment — leads only, per Principle 1 | Leads only |
| Self-hosted search & scrape infrastructure | Tooling | Project-operated instances of open-source metasearch and scraping tools | Paced, serialized lookups and JavaScript-rendered directory harvests without hammering public services | Tooling |

## What we evaluated and do not use

- **Business Wire RSS and Yahoo Finance tooling** — unreachable from our
  automation environment (edge blocks, handshake failures); their content
  reaches us through news aggregation and primary filings instead.
- **Low-tier pay-to-publish wires** — no usable machine feed, and anything
  material surfaces through aggregation.
- **Used-equipment marketplace listings as a closure signal** — a reseller's
  warehouse location is not the seller's plant; the provenance fails.
- **Building permits as company discovery** — a permit names an applicant or
  a contractor, never the operator of the finished plant. Measured directly:
  57 permit-derived candidates produced zero verifications. Permits remain
  useful as corroboration for a record another source produced, and for
  nothing else.
- **OpenStreetMap name queries for company discovery** — structurally blind:
  a name-keyword query can only find firms whose names contain sector words,
  which excludes most large employers by construction.
- **Certificate-lookup services** — human, one-record-at-a-time tools with no
  bulk or state-level access; not pipelines.
- **A certain international trade-promotion directory** — investigated
  thoroughly for a company-level state directory; none exists publicly (its
  published product is aggregate survey statistics). A regional investment
  map published by a binational business society covers part of the same
  ground and is used instead, with its vintage caveats attached.

## Denominators (why our counts differ from the headlines)

The widely quoted figures for this industry in Ohio are all real — and all
measure different things:

- **890 establishments** — NAICS 326 (plastics & rubber products), Ohio,
  BLS QCEW 2023, private ownership. This is the source of the "~900" rumor;
  it is an establishment count for one sector code, not a company count for
  "the polymer industry."
- **996 companies** — a regional cluster strategic-framework figure.
  Reproduced exactly as Census CBP 2016 Ohio establishments under NAICS
  326 + 325211 + 325212 + 325991 — an establishment count under a wider
  code set, at 2016 vintage, relabeled "companies." Derivation in
  `docs/SOURCE_COUNT_RECONCILIATION.md`.
- **616 companies** — a 2022 onshoring study's hand-cleaned count, screened
  from 1,100+ raw commercial-database records for a single sub-code. The
  cleaning ratio is the lesson: a raw pull for one sub-code returned more
  records than the official establishment total for the entire sector.
- Our county × industry denominators are built cell-by-cell from Census CBP
  and BLS QCEW; where both sources suppress a cell (disclosure rules), we
  record it as *suppressed*, never as zero, and we never sum across the two
  measurement systems.

## Failure modes we defend against

1. **The mailing-city county trap.** County inferred from a postal city is
   wrong wherever a city or ZIP straddles a line — and the error is
   one-directional, toward the well-known side of the straddle, so
   city-derived county data systematically over-counts large counties and
   under-counts their neighbors. County is stored from the physical address
   and settled, when disputed, by parcel records or authoritative boundary
   geography — never by a geocode centroid.
2. **Registry ≠ activity.** Listings persist after closure. Every
   single-source registry record gets an activity check (the company's own
   site, or dated evidence such as a toxics-release filing, a closure
   notice, or an inspection) before it is treated as operating. A legal
   entity can be in good standing for a decade after its last operation.
3. **Exclusions decay.** "Not found" and "defunct" dispositions are
   perishable in both directions — most subtly for young companies, which
   get excluded before they exist and then exist. Exclusions carry dates and
   the fact that would settle them, and are annotated as superseded when
   newer evidence arrives rather than silently deleted.
4. **Name magnets.** Matching on a single generic token ("Continental,"
   "Medical," "Products") manufactures false identities. Containment matches
   require multiple distinctive tokens; address matching runs before name
   research, because the hardest duplicates are address-exact and
   name-invisible (legacy names, brands, predecessors, third-party
   operators).
5. **Staffing registrations inherit the host plant.** A staffing agency
   registered at a plant's address, with the plant's industry code, is not
   the plant and not a second company. The same trap appears in job
   postings: agency postings are no signal.
6. **Government industry codes are evidence, not truth.** Federal datasets
   disagree with each other and with reality at a meaningful rate, and
   company-reported parent names lag mergers by a reporting cycle.
   Conflicts are kept as adjudication queues with both values recorded —
   never auto-merged.
7. **Absence of evidence, three ways.** A rate-limited search returning zero
   results is an availability signal, not a finding. An archived-website
   index with zero captures for a domain is no signal at all — operating
   companies can be entirely absent from it. A facility missing from a
   threshold-gated dataset (toxics reporting, closure notices, device
   registration) may simply fall below the threshold.
8. **Announcement bias.** Incentive announcements, accelerator cohorts, and
   portfolio pages see projects that sought support or publicity. Cohort
   eligibility (state registration, key personnel in-state) is weaker than
   an in-state establishment, and alumni-inclusive portfolios list closed
   companies as current.
9. **Membership proves membership; exhibiting proves exhibiting.** Both are
   dated activity attestations for the member or exhibitor entity — often a
   parent or sales organization — so site records still need plant-level
   verification.
10. **Co-location is not identity.** Shared buildings, industrial parks, and
    adjacent addresses on one campus are adjudication items, not merges.
11. **Denominator geography errors masquerade as findings.** A county code
    misread in a denominators file (one county's FIPS code read as its
    neighbor's) manufactured a phantom 157–214% "over-coverage" county and
    understated the whole region's coverage until the denominators were
    re-derived against the statistical agencies' own area titles. Coverage
    ratios are only as trustworthy as the geography underneath them; verify
    the codes before publishing the percentages.

## How records are built from these sources

Incoming lists are de-duplicated deterministically before any research is
spent (website domain → normalized name → street address → trade names and
successors). Research proceeds in bounded packets with a strict verdict
grammar — verified, rejected with the fact, or uncertain with the specific
fact that would settle it. Changes are applied by a single writer per file,
validated by the repository's validation script, and published with a
byte-level read-back check. Personal contact data is never collected into
this database; sources that carry it are stripped at ingest.
