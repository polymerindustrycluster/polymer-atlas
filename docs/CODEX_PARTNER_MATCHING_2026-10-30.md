# Read-only site / program topical-fit pilot

**Draft PR:** https://github.com/polymerindustrycluster/polymer-atlas/pull/5  
**Source snapshot:** main `b67b1924368d60b45a0cb49134ae81ce6b1b0d8c`, 2026-10-30 at 16:37 UTC (repaired main).  
**Scope:** current committed canonical data only. No dependency on unmerged enrichment PRs #2 or #3. No canonical CSV, status, tier, vocabulary or relationship changes; no new IDs. This is a read-only analytical view, not a research verdict packet or an introduction authorization.

## What this can answer

“Which held Ohio sites and Ohio programs share a structured, evidenced process or material term, and what source should a researcher check before proposing an introduction?”

A result is **a potential topical fit only**. It does not establish demand, service availability, commercial suitability, an existing partnership, a supplier/customer relationship, or that anybody wants an introduction. Broad material matches are especially weak discovery signals. No external contact was made. Sources here are carried from the Atlas, not newly reverified by this script.

## Reproduce

From the repository root, using the standard library only:

```sh
python3 scripts/validate.py
python3 scripts/match_program_capabilities.py > /tmp/atlas-partner-matches.json
python3 -m unittest discover -s scripts -p test_match_program_capabilities.py -v
```

The script only reads files and prints JSON to stdout. Redirection chooses an output outside canonical data. `--site-state PA --program-state OH` changes the two explicit state filters; `ALL` disables a state filter. `--root` selects another complete checkout. The output includes each input file's SHA-256 and an aggregate input-manifest digest, so future runs can distinguish data changes from branch metadata.

Snapshot input-manifest SHA-256: `193b6781f344c05a909bbf6a7d4f3cdd56e71d8bb8b9eb31abdbd5e040581c0c`.

## Rules and deliberate limits

- The unit is a **site × program candidate pair**, never a company count or a confirmed relationship.
- Site, operator, program and institution must all have tier A/B/C and status `active`. Unknown, idled, acquired, merged, closed and unverified records are not included. This conservative report filter does not change any record or establish that excluded records are unusable.
- Only unwithdrawn, sourced, dated `company_disclosed` / `government_filing` capability rows tied to the site's held operator are used. Existing capability IDs and source references travel with every result. An operator mismatch is ignored and reported, not repaired.
- Program `specialty_processes` and `specialty_materials` are matched on **axis plus exact token** against site capabilities. Allowed tokens are the intersection of the existing §3.1/§3.2 and §3.6 vocabularies, read as literal declarations from the validator without executing it.
- No fuzzy matching, inferred aliases, family expansion, cross-axis matching or new schema vocabulary. `extrusion` does **not** match `extrusion_film_blown`, and `compounding` does **not** match `compounding_extrusion`. The schema defines rollups, but this pilot intentionally does not apply even those; this loses recall transparently rather than hiding an expansion. Product-form capabilities have no counterpart in program specialties and are excluded.
- Multiple evidence rows for one matching token still produce one site/program pair, with all supporting rows retained. Duplicate record IDs fail fast rather than being arbitrarily collapsed. Separate held sites are never merged by matching. No legal-entity resolution is attempted.
- Degree, certificate, apprenticeship, training and course records use an education/training route. `not_admitting` rows are excluded; blank/unknown admissions remain visibly `admissions_unverified`, never actionable enrollment suggestions. Centers and labs use a research/facility route, with their actual engagement modes shown; the classification does not assert that every mode is available.
- Same county requires the **same recorded state and nonblank county**. Otherwise the label is same state, different state or unknown. No coordinates, geocoding, distance estimates or mailing-city county inference. Geographic proximity is context, not a requirement for research collaboration.
- Program URLs, public doors, source strings, verification dates and record tiers remain visible. A legacy source string that is not a precise link remains a limitation, not silently upgraded evidence.
- Absence of a match means absent compatible structured data, not absent expertise. This pilot ignores research-area-only characterization expertise, so many useful labs intentionally produce no match.

This snapshot is pinned to the observed pass-18 main commit above. Later main changes require a rerun; these counts do not claim to track a moving branch.

## Snapshot result

Under the Ohio-site / Ohio-program defaults and filters above:

- 1,483 eligible site rows and 22 eligible program rows.
- **89 candidate pairs**, involving **43 distinct site rows** and **4 distinct program rows**.
- 18 pairs share a recorded county; 71 are same-state pairs in different or incompletely recorded counties.
- The four programs are National Polymer Innovation Center, MDS-Rely, NFM Welding Engineers Process Development Lab and Steer America Application Development Center. Two carry tier C, exposed in every corresponding result. They are not promoted by being matched.
- This snapshot produces no education/training pairs. It is not evidence that Ohio lacks training options: sparse program specialties and strict vocabulary intersection are major constraints.

Illustrative matches from existing data, not freshly validated recommendations:

| Held site | Held program | Exact shared token | Geography |
|---|---|---|---|
| Ferriot, Inc. — Akron (`SITE-000061`) | National Polymer Innovation Center (`PROG-000022`) | process: `injection_molding` | Same recorded county (Summit, OH) |
| MRP Solutions — Twinsburg (`SITE-000074`) | National Polymer Innovation Center (`PROG-000022`) | process: `injection_molding` | Same recorded county (Summit, OH) |
| Qualiform — Wadsworth (`SITE-000202`) | National Polymer Innovation Center (`PROG-000022`) | material: `elastomers_rubber`; process: `compression_molding` | Same state (OH) |

Each JSON result includes exact capability IDs and witnesses (for example Ferriot's carried source `https://ferriot.com/`) and the program's `https://www.uakron.edu/npic/request` page. The matcher does not validate the precision, current availability, or taxonomy correctness of those inherited facts. A reviewer must re-open the sources and confirm the actual technical requirement before outreach.

## How to use safely

1. Select a real PIC question, such as a process need, training need or research problem.
2. Filter this report to the exact technical term and desired region; inspect tiers and evidence dates.
3. Confirm the site's specific need and the program's current offer through public evidence or separately authorized contact.
4. Keep a proposed introduction separate from the canonical relationship graph. Matching alone never mints an edge.

No new source crawling or monitoring is activated. After upstream enrichment merges, rerun against the merged tree and compare input hashes. Do not copy the counts above into new releases without recomputation.

## Verification and coordination

- Twenty focused tests cover positive/no-match cases, absent capabilities, tombstones, unknown status, tier U, withdrawn evidence, operator mismatch, source omissions, wrong axis, unsupported tokens, no fuzzy rollups, duplicate IDs, pair deduplication, admissions handling, geography, deterministic output and nonmutation.
- Full repository validator passes on repaired main `b67b192`; twenty focused tests and a byte-identical repeated report pass. Independent typed-reference resolution checks 14,237 nonblank entity references against 8,018 held IDs (3,495 organizations, 206 ecosystem records, 73 programs, 4,244 sites), with zero unresolved references. Evidence references resolve within their declared table, not merely the union. These are local results, not remote CI.
- Historical correction: the earlier `f928257` snapshot had 49 unresolved references because the Oregon organization shard was absent. Upstream repair `b67b192` resolves those failures; the failure claim is historical, not current. The Ohio matching counts remain reproducible unchanged. No repair was authored or applied by this lane.
- Task was claimed in `tasks/QUEUE.md` before implementation and published as draft PR #5. Only this report, its script/test and the five existing PR queue claims are proposed. All five claim blocks are preserved verbatim from their observed PR heads. All other PR claims must be preserved if queue appends conflict at merge.
- Reviewer checks should use the final PR head and rerun the commands, rather than relying only on this static snapshot.
