# Cincinnati second-pass people packet — 2026-11-06

Bounded review of the **58 assigned University of Cincinnati candidate people**, in supplied order. This is a research packet for integrator inspection, with no data edits or allocated IDs. The private frame and full rejected/uncertain discovery identities are not published.

| Assigned input positions | Candidate people reviewed | VERIFIED proposals | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---:|---:|---:|---:|---:|
| 1–25 | 25 | 1 | 2 | 22 | 0 |
| 26–50 | 25 | 1 | 1 | 23 | 0 |
| 51–58 | 8 | 0 | 1 | 7 | 0 |
| Total assigned UC frame | 58 | 2 | 4 | 52 | 0 |

The external corroborating CV previously yielded 9 of 9 physical pages, but is not required for dated rank resolution.

`verified.csv` contains two proposals that were previously unresolved:

- **Jianbing Jiang:** the current own chemistry directory target entry gives `Jianbing Jiang Assoc Professor`. A dated UC article from October 2, 2023 styles Associate Professor Jimmy Jiang, while the own department biography explicitly bridges Jianbing/Jimmy and dates his assistant start to August 2018. The institution-owned 2023 rank witness plus current header resolves the stale assistant biography; `rank_resolution.csv` records its quote, date, and sanitized extracted-text hash (no HTTP-byte hash claimed). The external dated CV is optional corroboration only. The UC research profile attributes active grant CHE-2347912 to Jiang as PI, May 1, 2024–April 30, 2027, explicitly for PVC upgrading. That direct institution-hosted current research object carries Gate B; the news article never carries scope.
- **Yoonjee Park:** the current own chemical-engineering directory gives `Professor (F2)`; the own profile dates promotion to 2026. A direct UC project narrative describes developing biodegradable-polymer implant capsules, carrying Gate B.

Research specialties use existing controlled tokens under SCHEMA §4.9: Jiang → `pvc` (§3.2), directly from the active grant’s explicit Polyvinyl Chloride (PVC); Park → `biomedical_polymers` (§3.5), directly from the polymer drug-delivery capsule project. These replace the earlier unsupported literal specialties; no vocabulary or scope extension is proposed.

New sources include current department directories, named institutional research/project pages, institution-linked lab statements, and a dated linked CV. Across the **106 unique URL routes associated with this assigned frame**, 89 returned usable text and 17 remained unavailable. Raw HTTP response hashes exist for 88 successful routes; the additional dated UC rank article has a sanitized extracted-text hash, explicitly labeled without an HTTP-byte hash. Explicit availability states are retained privately. The public manifest lists only sources supporting the two public proposals. Raw responses and extracted source text stay under `/tmp`.

Four exclusions rest on positive current rank evidence: two educator appointments, one emeritus appointment, and one university research-associate/staff appointment. Holds require specific missing facts in the private dispositions. They include current-rank conflicts, identity/primary-home questions, polymer research appearing only in publications or historical projects, generic materials statements, external-lab-only scope, and unavailable own pages. Failed fetches and missing keywords never establish absence. Search-index snippets never carry either gate. Biological molecules alone do not establish engineered polymer materials under B-CG-2.

The parent clarified that required scope evidence must be institution-hosted; external named labs alone cannot carry `own_site` scope. This supersedes any external-lab-alone interpretation of the initial batch report. An attributed current institutional PI project with explicit research object and verified dates can qualify; the Jiang grant was checked on that basis.

## Checks

Run from the shared second-pass checkout:

```sh
python3 tasks/people-settle-2-2026-11-06/lanes/uc58/check.py
```

PASS: existing controlled specialty tokens and direct source mappings; exactly 58 unique candidate IDs in input order; 2 public proposals agree with private VERIFIED dispositions; five actual-source known answers; six token-boundary/wrong-identity matcher checks; quote presence and 25-word ceilings; exact title/surname within 40 words; UC-domain gate sources; current Jiang PI/date object; institution-owned dated rank witness and nickname bridge; privacy; LF CSV; maximum six associated source URLs per candidate; normalized-name/institution and global first/surname checks against main and the current pending first-pass snapshot (12 candidate people at this rerun; checker reports its row count dynamically). Broader first-or-surname hits were inspected as different published identities/institutions, never forcibly merged. No duplicate endpoint was assigned. A fabricated Gate B quote was injected into the check in memory and correctly failed with `quote absent`.

Checks depend on the parent-owned private runtime and temporary source cache. This is a bounded candidate review, not a faculty census. No band-B census expansion, canonical data application, repository-wide validation, independent integrator inspection, completion refutes, commits, or PRs were performed by this lane; those remain with the parent.
