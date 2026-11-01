# Lane brief: new-plant discovery wave (2026-11-01)

**Packet lanes.** A lane never edits `data/`, never allocates IDs, and never
commits or pushes (AGENTS.md §2 rules 7–8). It produces **create packets** for
the integrator of record.

## Population

- **Input:** `<STATE>_assignment.csv`, the top 40 STRONG clusters per state from
  `tasks/lead-fusion-2026-11-01/top_leads_by_state.csv` (pin `9b2e3b9`). A
  STRONG cluster is a polymer-NAICS establishment confirmed by 3 or more federal
  source families (OSHA ITA, OSHA inspections, EPA ECHO, Form 5500,
  USAspending).
- **What the cluster is:** a lead only, never existence or scope evidence for a
  record.
- **What it already carries:** the federal source records, with IDs in
  `sources_with_ids`. Their facts can become `government_filing` evidence
  **only** for the fact the record states (address, NAICS, activity date),
  citing the source system and record ID.

## Per lead, in order (AGENTS.md §3, with a ~6 primary fetch cap per lead)

1. **Find the operator's own website.** WebSearch is allowed as a discovery step
   only, and is never cited. Record the domain.
2. **Dedupe** with `python3 scripts/atlas.py dedupe-check --domain <d> --name
   "<name>" --street "<street>" --city <c> --state <ST>`. Check both the org
   shards and the site shards.
   - **The same domain or org is held:** propose a site under that org (or
     `DUPLICATE_OF` if this exact site is already held).
   - **Nothing is held:** propose a new org plus a site.
3. **Verify from the own site.**
   - **Existence:** the company exists and operates at, or names, this location.
   - **Scope:** a polymer process or material at this plant, under SCHEMA §1
     ring tests.
   - **Quotes:** ≤ 25 words each, checked by script as a substring of the
     fetched text.
   - **Values:** use vocab v1.7.6 (`docs/schema/vocab.json`) for processes,
     materials, markets and certifications (R3c), one value per row.
4. **Verdict:** exactly **VERIFIED** (create proposed), **DUPLICATE_OF** (give
   the held ID and the chain), **REJECT** (the deciding fact, e.g. out of scope:
   distributor, non-polymer), or **STILL_UNCERTAIN** (the settling fact).
   - A failed fetch is never evidence. Use no bot-wall workarounds and curl's
     default user agent only.
   - A closure REJECT requires dated evidence plus the Form 5500 check. A
     cluster with a recent Form 5500 filing at the same address blocks a
     closure REJECT.

## Output per lane (in `<STATE>/`)

- **`creates_orgs.csv`:** new orgs only, in the exact column order of the
  `data/organizations_<TAG>.csv` header.
  - `org_id` = `<ALLOC>`; the shard comes from `atlas.py shard-of --hq-state`.
  - `verification_tier` = C at most (AGENTS.md §3 step 5).
  - `naics_primary` with `naics_primary_source_type` + confidence. A
    government-filing NAICS is the facility's code; never copy it to the org
    without a basis (SCHEMA §2.1).
  - `sources` are public URLs and source-system record IDs only, with no local
    paths (P3).
- **`creates_sites.csv`:** in the exact `data/sites_<ST>.csv` header order.
  - `site_id` = `<ALLOC>`; `org_id` is a held ID or `<ALLOC:new-org-row-n>`.
  - Ring from site facts (§1).
  - `operating_status` = active only with dated activity in the cluster or on
    the own site.
  - County from the physical address. ECHO county is orientation only (Ohio
    rule: never from the mailing city).
  - Tier C at most.
- **`evidence_rows.csv`:** in the `data/evidence.csv` header order.
  `evidence_id` = `<ALLOC>`. Cover existence, address and scope at minimum
  (§4.13). Use claim types and source-class ceilings exactly as in
  `scripts/validate.py`.
- **`registry_link_candidates.csv`:** FRS, TRI, FDA_FEI, UEI and EIN IDs taken
  verbatim from the cluster's source records. Add `site_id` per SCHEMA v1.7.7
  R10 for facility-grain IDs. EIN only under the R11 mint rule.
- **`verdicts.csv`:** cluster_id, verdict, deciding_or_settling_fact,
  own_domain, fetches_used, availability_failures.
- **`REPORT.md`:** counts with units; dedupe hits; verdict mix; vocabulary gaps;
  hygiene notes. If your tool refuses to write the report, return it as text.

## Dry-run requirement

Before finishing:
1. Copy `data/` to a temp directory.
2. Fill the `<ALLOC>` IDs there from `python3 scripts/atlas.py next-id ORG|SITE|EVD
   --data-dir <tmp>` (temp copy only), then append your rows.
3. Run `ATLAS_DATA_DIR=<tmp> python3 scripts/validate.py`. It must exit 0. Report
   the result.
4. Delete the temp directory.

**Never touch the real `data/`.**

**Privacy:** no personal emails, direct phones or individual names (AGENTS.md §6).
Form 5500 sponsors flagged as possibly individuals are never created as orgs
from the 5500 record alone.

**Scratch directory:** `/tmp/claude-0/discovery/<ST>/` only, with per-lead
locked files.
