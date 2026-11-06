# PatentsView / USPTO PVGPATDIS — CORROBORATION_ONLY, 2026-11-06

Route: legacy PatentsView has migrated; authenticated ODP bulk metadata and four grant tables worked. `download.py` reads USPTO_API_KEY from environment, sends it only to api.uspto.gov, follows the signed redirect without the key, and verifies advertised sizes. No API key or signed URL is committed. Bulk manifest pins four public file descriptors; raw files remain /tmp/l5-patents. Data end 2025-12-31, latest grants 2025-12-30: **2026 grants are not covered**.

Terms: [USPTO terms, Use of USPTO databases](https://www.uspto.gov/terms-use-uspto-websites):
> Bulk data products may be separately obtained from the USPTO, either for free or at the cost of dissemination.

Use is via the designated bulk route, not high-volume search scraping. Attribution: patent data from PatentsView / USPTO. No unverified CC license assertion is substituted for the live USPTO terms.

Filter: g_patent grant date >=2020-01-01, withdrawn !=1; g_cpc_current subclass starts C08 or B29, or equals C09J/B60C; any sequence/type, distinct patent IDs. **C09D alone is excluded** (unlike the earlier Nov 1 pilot). Only organization assignees exported; no inventor/individual assignee names or personal contacts. `extract.sql` runs with DuckDB, 2GB memory cap. LEFT JOIN locations retains missing locations: an initial INNER JOIN lost 173 distinct assignees and was discarded. Counts refer to disambiguated organization identities, never establishments.

- **79,016 qualifying grants worldwide** including patents without an organization assignee.
- **76,311 qualifying grants with an organization assignee**; **12,939 disambiguated organization assignees**, worldwide.
- **525/12,939 exact normalized-name Atlas candidates = 4.0575%** (all organization shards plus ecosystem, legal/trade names); unknown domain/street fields were not inferred. This is a conservative candidate match rate, not resolved ownership coverage.
- **4,507 US-located assignees** (at least one US assignee location).
- **133 assignees with a PIC-18 OH county location** on qualifying grants, joined by county_fips rather than county spelling.
- **51 distinct held organizations with a PIC-18 HQ/site footprint are exact-name patent candidates** (`pic18_matches.csv`). This is a **candidate count, not a confirmed count of PIC-18 organizations owning patents**. Names, subsidiaries and successors need identity adjudication; a location on a patent is not a current plant address. The actual confirmed total is held pending that work. Patent counts deduplicate patent_id within each disambiguated assignee then union per held candidate; co-assigned patents may count for more than one organization.

Twenty uniformly seeded US-located assignee samples (seed 20261106, sorted assignee_id frame): **0 VERIFIED new, 3 DUPLICATE_OF, 17 STILL_UNCERTAIN**; **0/20 = 0%, 95% Wilson CI 0–16.11%**. Each sample has a primary grant number/date/CPC from the bulk tables, then all-shard name/alias matching. No separate own-site operation verification was performed for these 20: this yield measures what this bulk-evidence scout alone establishes, not a maximal six-fetch verification campaign or the source's ultimate discovery potential. Name-match candidates cannot establish current polymer scope; the named settling facts are in sample.csv. No closure REJECTs. Domain/street dedupe is explicitly unavailable in these tables.

Known answers: named held matcher cases in ../build.py; date/CPC inclusion and exclusion checked by the extraction filter and independent count queries. Grant count 79,016 is not 76,311: the latter requires an organization assignee. Original pilot was not reused as a 2020+ count.

| Hold | Settling fact | Recommendation |
|---|---|---|
| Confirmed PIC-18 patent total | Entity/successor adjudication of 51 exact-name organization candidates and nonexact assignee aliases | Publish candidates only; no patent-count column added |
| D-05 schema | Owner ruling on innovation storage and count semantics | Packet only, no scope/vocabulary self-ruling |
| 17 sample uncertainties | Own-site current polymer operation and identity / multiple-candidate linkage | CORROBORATION_ONLY |
