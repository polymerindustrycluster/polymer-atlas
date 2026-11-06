# Site-name dedupe — 2026-11-06

**Finding (PR #170 worker):** lane dedupe never searched `sites.site_name`, so "IFS Coatings - Ardmore" (SITE-006097, under
ORG-002633 "Ifs Industries Inc.") went unnoticed. Two deliverables: (1) close the gap in `scripts/atlas.py dedupe-check`;
(2) a **leads-only** sweep of the existing tree. No `data/` edit, no merge, no verdict (AGENTS §3: when in doubt, do not merge).

## 1. `dedupe-check` step 5 (site names)

- `atlas.site_name_key(site_name, city)` = the existing `name_key` (the organization-name normalizer) applied after removing a
  trailing `" - <city>"`, `" — <city>"` (the SCHEMA default form) or `" (<city>)"` suffix. A suffix is locality only when it
  starts with the site's own city, so `IFS Coatings - Annex` keeps its suffix. No city given means nothing is stripped.
- `dedupe()` gains **step 5**, after the four AGENTS §3 steps (existing step numbers and `stop_at_step` semantics unchanged). It
  matches the query name (and the query with `--city` removed) against each site's full-name key and stripped key, and reports
  site id, site name, operator org, street, city. `--name` is the only input.
- Known answer: `python3 scripts/atlas.py dedupe-check --name "IFS Coatings"` now stops at step 5 with SITE-006097
  (operator ORG-002633, 3430 Cypert Way). Before the change it reported "No hits".
- Tests in `scripts/test_atlas_cli.py`: `site_name_key` cases, a three-form hit (hyphen / em dash / parenthesis) with operator and
  street asserted, near-misses that must not match (`IFS Coatings Group`, `IFS Coatings - Annex`, `Ifs Holdings`), and the
  `--city` query form, and a real-data known answer in `RealDataSmoke` (IFS Coatings finds exactly SITE-006097). Run:
  `python3 -m unittest discover -s scripts -p "test_*.py"` (276 tests, OK; pytest is not installed here).
- **Behavior change:** a query that used to end "No hits" (exit 0) can now stop at step 5 (exit 1). That is the gap being closed.
  Consumers: `build_form5500_spine.py` and `build_lead_fusion.py` compare steps 2 and 3 only, so they are unaffected. The ten
  `tasks/corroborated-*/check.py` files that read `dedupe()['steps']` already fail on current `main` (data moved since their PRs);
  they fail identically before and after this change, so none is newly broken. Re-run them on their own PR's data, not here.
- `docs/AGENT_QUICKSTART.md` mentions step 5. `AGENTS.md` §3 is **not** edited (binding protocol; suggest the owner add
  "site names" to its list if wanted).

## 2. Sweep: `leads.csv`

`python3 tasks/site-name-dedupe-2026-11-06/build.py` rewrites `leads.csv` and `counts.json`; `check.py` is the named check.

**Rule.** Key every name with `site_name_key`: each `site_name`, each organization `legal_name` and `trade_names` entry (a
trailing annotation such as `(former name)` dropped), each ecosystem `legal_name`. A **cluster** is one key with at least one
site name and members under **2+ different organizations**. A plant named after its own parent is the normal case and is never
a cluster. The key `headquarters` (a kind of place, not a company) is dropped and listed in `counts.json`.

**Columns** (one row per cluster; `;`-separated lists are positional, one entry per record, same order in all five):
`cluster_id`, `name_key`, `strength`, `orgs_linked`, `n_sites`, `n_orgs`, `record_ids`, `names` (the matched text), `org_ids`,
`orgs` (legal name of the record's org), `streets` (`-` = no street on record; organization names never carry one), `why`.

- `strength`: **strong** = two sites of different orgs share a normalized street; **medium** = members of different orgs share
  city + state (site city, or org HQ city); **weak** = name only.
- `orgs_linked`: **all** / **some** / **none** of the cluster's orgs are joined by a direct `parent_org_id` or `successor_org_id`
  (`all` means the relationship is already recorded, so these are lowest priority).

## Counts (input: 7,188 sites rows; 5,023 organizations rows; 402 ecosystem rows)

| Unit | Count |
|---|---|
| Clusters (name keys spanning 2+ orgs, ≥1 site name) | **107** |
| …site names under 2+ orgs (site vs site) | 40 |
| …site names under one org, matched by another org's name | 67 |
| Clusters by strength: strong / medium / weak | 0 / 34 / 73 |
| Clusters by orgs_linked: all / some / none | 35 / 2 / 70 |
| Highest-priority cell (medium + none or some) | 14 |
| Distinct sites in clusters | 248 |
| Distinct organizations in clusters | 200 |

Zero strong clusters is consistent with an independent count: 33 normalized-street + city + state groups hold sites of 2+ orgs
in the tree, and none of their cross-org site pairs share a name key (0 pairs, checked directly). That is a separate lead class (AGENTS §3 step 3, not swept here).

## Checks (`python3 tasks/site-name-dedupe-2026-11-06/check.py`)

- Known answers on the real tree: step 5 returns exactly SITE-006097 for "IFS Coatings"; the Snyder Industries and Latham Pool
  Products clusters contain the expected records and orgs.
- Planted fixture: a cross-org pair on one street is found (strong); a parent-linked pair is found (`orgs_linked=all`); a
  same-org control, a near-miss name and generic "Headquarters" sites are **not**. With the locality-stripping defect injected the
  check fails (verified by monkeypatch).
- `leads.csv` equals a fresh sweep (idempotent) and `data/` has no change. `validate.py`: 0 errors. `check_row_loss.py --base
  origin/main`: OK.

## Holds and limits

- Nothing here is a verdict. A cluster is a name coincidence to be adjudicated against sources; many are chains or group
  structures (e.g. Amcor, orgs linked) or genuinely different companies sharing a short name (TMI, PTI, TCI).
- Locality stripping matches the city text word-for-word ("St." vs "Saint" is not folded). `orgs_linked` uses direct
  `parent_org_id` / `successor_org_id` edges only; `relationships.csv` is not consulted.
- Existing steps 2 and 4 still key trade names without dropping `(former name)`-style annotations; not changed here
  (outside this task), noted for the owner.
- No refute run: this worker is barred from `council-ask` (CONTRACT-CLAUDE); the controller routes review.
