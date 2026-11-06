# Medium possible-duplicate clusters: adjudication packet — 2026-11-06

**Packet only.** No `data/` edit, no merge, no tombstone. Applying the folds, repoints and holds below is a separate
integrator PR after review. Frame: `tasks/site-name-dedupe-2026-11-06/leads.csv` (PR #244, merged at 14f134d), rows with
`strength == medium` — clusters where records of different organizations share a normalized name and a city and state.
Verdict grammar is AGENTS §2 rule 8. Federal registrant names are used as dedupe aliases (owner ruling B-ALIAS).

## Deliverable

| File | Content |
|---|---|
| `verdicts.csv` | one row per cluster: `verdict`, `survivor`, `org_state`, deciding or settling fact, sources, site folds to apply, operator actions, lookups |
| `pairs.csv` | the record-level decisions behind each verdict (org pairs and site pairs), each with state, basis, fact, sources |
| `operator_actions.csv` | `repoint_site` (operator is not the current parent) and `hold_operator` (settling fact named) |
| `decisions.py` | the packet as written by hand; `build.py` renders it to the CSVs, `check.py` verifies them |
| `evidence.csv`, `frs_excerpt.csv` | 12 quotes from 9 cached web pages (sha256, quote) and the EPA ECHO registrant rows cited |
| `counts.json` | counts recomputed by `check.py` |

How a cluster verdict is derived (re-derived by `check.py`): from the cluster's **org-level pairs**. If any org pair is still
open (`to_apply` or DISTINCT/STILL_UNCERTAIN) the open pairs decide (DUPLICATE_OF over STILL_UNCERTAIN over DISTINCT); if every
org pair is already recorded in the tree the cluster is DUPLICATE_OF with `org_state=recorded`. Site-level folds are listed
separately so that a DISTINCT org verdict never hides a site duplicate.

## Counts

Unit: **clusters** in `leads.csv` with `strength == medium` (shared normalized name plus shared city and state across
different organizations), 34 of the 107 swept. Verdicts are per cluster; pairs are record-level decisions inside clusters.

Clusters by verdict:
- 34 medium clusters
- 15 DUPLICATE_OF (already recorded in the tree)
- 3 DUPLICATE_OF (org fold to apply)
- 14 DISTINCT
- 2 STILL_UNCERTAIN

Work for the integrator PR, by unit:
- 3 org folds to apply (SND-0022 Diamond Plastics, SND-0055 Ludlow/Crown Foam, SND-0101 US Farathane)
- 11 site folds to apply (record-level `DUPLICATE_OF` site pairs, 9 clusters)
- 12 repoint_site (a site moves to the operator org; 7 are survivors of site folds)
- 9 hold_operator (operator not settled; each names a settling fact)

Already recorded, no action: 17 org folds and 6 site folds that the tree already carries (`status=merged`/`acquired` plus
`successor_org_id`, or a tombstone note). The 17 org folds sit in 17 clusters, two of which (Carlisle SND-0014, Ultra Poly SND-0100) also hold
an open pair that decides their verdict (STILL_UNCERTAIN and DISTINCT).

Pairs: 15 DISTINCT, 2 STILL_UNCERTAIN, 3 org + 11 site DUPLICATE_OF to apply, 17 org + 6 site recorded (`counts.json`).

## Clusters

| Cluster | Name key | Verdict | Survivor / outcome |
|---|---|---|---|
| SND-0009 | barentz | DUPLICATE_OF (recorded) | ORG-000242 |
| SND-0010 | berry global | DUPLICATE_OF (recorded) | ORG-002544 (ORG-002149 consolidated; successor field empty by design) |
| SND-0014 | carlisle polyurethane systems | STILL_UNCERTAIN | is CPS (ORG-000262) a legal entity or a unit of Carlisle Construction Materials LLC (ORG-002251)? 4 plants held on the same fact |
| SND-0015 | carpenter | DUPLICATE_OF (recorded) | ORG-002348 |
| SND-0016 | charter plastics | DISTINCT | acquired 2021-12-31 by WL Plastics, successor recorded |
| SND-0020 | creative composites group | DISTINCT | group vs member company Composite Advantage; SITE-000831 held for operator |
| SND-0021 | day glo color | DISTINCT | subsidiary of RPM; 2 site folds, survivors repointed to ORG-000005 |
| SND-0022 | diamond plastics | DUPLICATE_OF (to apply) | ORG-004865 |
| SND-0028 | esstech division of esschem | DUPLICATE_OF (recorded) | ORG-002324; + 1 site fold (Powhatten/Powhattan typo) |
| SND-0029 | euclid chemical | DISTINCT | SITE-000168 repoint RPM -> ORG-001807 |
| SND-0030 | ferro polymer additives div | DUPLICATE_OF (recorded) | ORG-000135 |
| SND-0037 | goodyear chemical | DISTINCT | divestiture effective 2025-10-31; 2 site folds (Houston, Beaumont), survivors repointed to ORG-003746 |
| SND-0038 | harrison paint | DUPLICATE_OF (recorded) | ORG-001678 |
| SND-0039 | hexpol compounding ... | DUPLICATE_OF (recorded) | ORG-000103 |
| SND-0040 | house of plastics | DUPLICATE_OF (recorded) | ORG-000108 |
| SND-0043 | ier fujikura | DUPLICATE_OF (recorded) | ORG-000373 |
| SND-0048 | johnsonite | DISTINCT | acquired 2005; 1 site fold + 2 repoints |
| SND-0049 | jushi usa | STILL_UNCERTAIN | org identity unsettled; 1 site fold (same plant), operator held |
| SND-0050 | key resin | DISTINCT | subsidiary of RPM; 1 site fold, survivor repointed to ORG-000919 |
| SND-0051 | lanxess | DISTINCT | Rhein Chemie is a recorded child; 1 site fold (RIDC Park West) |
| SND-0055 | ludlow composites | DUPLICATE_OF (to apply) | ORG-000937 (Crown Foam is a brand division) |
| SND-0061 | murdock industrial | DUPLICATE_OF (recorded) | ORG-000028 |
| SND-0064 | newko polymers | DUPLICATE_OF (recorded) | ORG-000460 |
| SND-0065 | nfm welding engineers | DUPLICATE_OF (recorded) | ORG-000456 |
| SND-0069 | performance elastomers | DISTINCT | acquired 2021-12-01 by Pexco, successor recorded |
| SND-0072 | pilot plastics | DISTINCT | acquired 2023-02-02 by Preformed Line Products, successor recorded |
| SND-0074 | polymer and steel technologies | DUPLICATE_OF (recorded) | ORG-001806 |
| SND-0077 | premere enterprises | DUPLICATE_OF (recorded) | ORG-000902 |
| SND-0082 | quikey manufacturing | DUPLICATE_OF (recorded) | ORG-001997 |
| SND-0083 | republic powdered metals | DISTINCT | subsidiary of RPM; 1 site fold, survivor repointed to ORG-001724 |
| SND-0084 | royal building products | DISTINCT | two Columbus plants (1550 vs 1441 Universal Rd), different registrant entities |
| SND-0099 | tremco cpg | DISTINCT | 1 repoint, 3 holds |
| SND-0100 | ultra poly | DISTINCT | Tacoma "Ultra Poly Inc." is not the PA corporation; Berwick fold recorded |
| SND-0101 | us farathane | DUPLICATE_OF (to apply) | ORG-007002 |

Full facts and sources are in `verdicts.csv` and `pairs.csv`.

**Survivor rule (enforced by `check.py`).** The record holding more registry links plus relationships survives, then the one with more
evidence rows; ties keep the stated survivor. Evidence is append-only and keyed by record id, so the folded row's evidence rows stay
with the retired id; the rule minimises how much history that strands. A survivor under a non-operator org is repointed to the
operator (`operator_org` in `pairs.csv`; blank means the operator is unsettled and a `hold_operator` is required). The integrator
copies street, type and tier basis from the folded row into the survivor's fields and notes; it does not re-create evidence rows.

### What each fold strands (rows referencing the folded record: evidence / registry links / relationships)

| Cluster | Level | Folded | Folded side | Survivor | Survivor side |
|---|---|---|---|---|---|
| SND-0021 | site | SITE-000005 | 1 / 0 / 0 | SITE-002964 | 6 / 0 / 0 |
| SND-0021 | site | SITE-002082 | 0 / 0 / 0 | SITE-002968 | 6 / 1 / 0 |
| SND-0022 | org | ORG-005115 | 6 / 0 / 0 | ORG-004865 | 6 / 1 / 0 |
| SND-0028 | site | SITE-002301 | 3 / 0 / 0 | SITE-002302 | 1 / 1 / 0 |
| SND-0037 | site | SITE-004181 | 0 / 0 / 0 | SITE-002868 | 9 / 1 / 0 |
| SND-0037 | site | SITE-004182 | 0 / 0 / 0 | SITE-002870 | 8 / 0 / 0 |
| SND-0048 | site | SITE-000427 | 1 / 0 / 0 | SITE-003478 | 2 / 0 / 0 |
| SND-0049 | site | SITE-004191 | 0 / 0 / 0 | SITE-003765 | 1 / 0 / 0 |
| SND-0050 | site | SITE-000989 | 0 / 0 / 0 | SITE-002962 | 7 / 0 / 0 |
| SND-0051 | site | SITE-002777 | 0 / 0 / 0 | SITE-004377 | 1 / 0 / 0 |
| SND-0055 | org | ORG-001792 | 0 / 0 / 0 | ORG-000937 | 0 / 0 / 0 |
| SND-0055 | site | SITE-001866 | 0 / 0 / 0 | SITE-001008 | 4 / 0 / 0 |
| SND-0083 | site | SITE-001800 | 0 / 0 / 0 | SITE-002965 | 7 / 0 / 0 |
| SND-0101 | org | ORG-007061 | 6 / 0 / 0 | ORG-007002 | 6 / 0 / 0 |

Only three folds strand anything: SITE-002301 (3 evidence rows), ORG-005115 and ORG-007061 (6 each; the survivors hold the same
number). A reviewer who prefers the other direction for any pair can swap `survivor`; `check.py` will then fail on the survivor rule,
which is deliberate.

## Patterns worth knowing

- **RPM family (SND-0021, -0029, -0050, -0083, -0099).** Sites named for a subsidiary (Day-Glo, Euclid, Key Resin, Republic,
  Tremco) were created under parent RPM (ORG-000006) from the EDGAR/TRI parent-filer packet. The orgs are DISTINCT
  (RPM's own note says classify subsidiaries individually). The EPA registrant at each address names the subsidiary, so the
  operator is the subsidiary (AGENTS §3: operator, never brand owner). All five hold a site duplicate, a repoint or a hold.
- **Goodyear Chemical (SND-0037).** The Gemspring sale closed effective 2025-10-31 and covered the Houston and Beaumont plants
  and the Akron R&D facility; Goodyear kept Niagara Falls NY and Bayport TX. So Niagara Falls stays with ORG-000003, and the
  Houston and Beaumont rows that hold the TRI/OSHA evidence survive, repointed to the new operator ORG-003746.
- **Why Royal (SND-0084) is DISTINCT while Diamond and Farathane are folds.** Diamond and Farathane share one operator name, one HQ
  address and one site between their two org rows. The two Royal rows share only the brand name and the Westlake Royal website: their
  establishments are at different addresses (1550 vs 1441 Universal Rd) under different EPA registrant legal entities, and the
  2026-10-28 audit ruled 'do not merge'. ORG-000764's `legal_name` is a brand name; its operator is Crane Performance Siding LLC North.
- **Why Carlisle (SND-0014) is STILL_UNCERTAIN and Euclid/Tremco are repoints.** 'Euclid Chemical Company' and 'Tremco CPG Inc.' are
  legal-entity names with their own HQs and registrants. 'Carlisle Polyurethane Systems' is a unit name (ORG-000262's whole
  legal_name, its trade name, and the EPA registrant text), so the tree does not show a filing entity distinct from Carlisle
  Construction Materials LLC. If it is a unit, ORG-000262 is a division record (the Ludlow/Crown Foam precedent) and the four plants
  stay with ORG-002251; the registrant at Chattanooga equals ORG-000262's name and is still held, not repointed.
- **Already-folded orgs (15 clusters).** The lead sweep matches names, and a merged duplicate keeps its name, so a settled merge
  still looks like a cluster. For those, the packet confirms that the tree shows the fold and that nothing remains.

## Checks

`python3 tasks/dedupe-medium-2026-11-06/check.py` (add `--selftest` to plant defects, `--offline` to skip only the FRS-cache
comparison). It proves: exactly the 34 medium clusters of `leads.csv`, one verdict each, `records` equal to `leads.csv`;
verdict and survivor re-derived from the pairs; every DUPLICATE_OF survivor exists, is an active org (or a held site), is
never folded, and is the survivor of one cluster only; no record is folded twice; recorded folds are visible in the tree and
each to-apply site fold is re-derived from `data/` (shared FRS id, same street, street variant, or same city with one
streetless row plus a cited witness); every source token resolves; every quote is on its cached page with the stated sha256;
every FRS row equals the ECHO cache; no file under `data/` differs from `origin/main`.

Planted defects (`--selftest`, all caught): a merged org as survivor; a record folded in two clusters; a survivor that is
itself folded; a site fold across cities; a basis that does not hold; a dropped cluster; a verdict not derivable from the pairs;
STILL_UNCERTAIN without a settling fact; a recorded fold the tree does not show; a quote not on the page; an unknown source
token; a survivor in two clusters; a survivor holding less history than the folded record; an unsettled operator with no hold; a
survivor under a non-operator org with no repoint.

Known answers before trusting the matchers: Key Resin's registrant row (110070207889) is the FRS id that SITE-000989's own
notes cite, and its street equals SITE-002962's; Day-Glo's two rows cite the same FRS id 110000386494; the street key treats
"1570 E Highland Rd" and "1570 Highland Rd" as one street, "Powhatten"/"Powhattan" as a variant, and "111 RIDC Park West" as
"111 Park West"; Royal's 1550 and 1441 Universal Rd keys differ (`known_answers()` in `check.py`).

Lookups used (`lookups` column in `verdicts.csv`): 44 distinct EPA ECHO registrant rows from the local cache and 9 web pages
(12 quotes). No cluster cites more than 2 web quotes and 5 EPA rows. Web pages are cached under
`thread-storage/.../persist/dedupe-medium-2026-11-06/` (some contain business phone lines, so they are not committed).
Discovery searches (Tavily, five queries) pointed to the pages; only raw-fetched pages are cited.

## Holds and what this does not settle

- **SND-0049 Jushi: STILL_UNCERTAIN.** Three names for one plant: "Jushi USA", "Jushi USA Fiberglass Co., Ltd." and the EPA
  registrant CHINA JUSHI USA CORPORATION at 2971 Shop Rd. Settling fact: the SC Secretary of State or SCDES record naming the
  plant's owner. The two plant rows are the same establishment and are listed as a site fold; the surviving row SITE-003765 sits
  under ORG-003321 only by default, so it carries a `hold_operator`: one plant, operator open.
- **SND-0101 US Farathane.** The fold rests on website, HQ address and EPA registrants (all "Corporation"; the LLC form comes
  from OSHA inspection names). The Michigan LARA record would show whether the LLC is a conversion (then the survivor's `legal_name` becomes
  the LLC: survivor ID is not survivor name) or a separate entity (then the fold is reversed; nothing is deleted, ORG-007061 is only
  tombstoned).
- **SND-0100 Ultra Poly (Tacoma).** DISTINCT rests on different legal-form suffix, state and registrants and on the PA company's
  own page naming no Washington plant. That page also lists three unnamed embedded plants at customers, so absence is not proof;
  if a link is found later, treat it as a new lead.
- **9 hold_operator** (SND-0014 four Carlisle plants, SND-0020 SITE-000831, SND-0049 SITE-003765, SND-0099 three Tremco rows): each
  names the legal entity that files the EPA/TRI report (or the SOS record) as the settling fact.
- **Not done:** no AGENTS §3 dedupe-check on the three org folds (the integrator does it); no check that `relationships.csv`
  parity (V-27) holds after the folds; Muncie (SITE-006423) and Lake Orion (SITE-010064) activity not re-verified.

Observed and left alone (separate issues, not fixed here):
- SITE-019012 (Berry, Alsip IL) is "12900 S. Pulaski Avenue"; EPA lists BERRY GLOBAL GROUP INC at 12900 S CRAWFORD AVE, Alsip.
- ORG-002619's `legal_name` "Ultra Poly Corp. - Portland" is a site name; the EPA registrant is ULTRA-POLY CORPORATION.
- SITE-004180 (Goodyear Chemical, Akron HQ and R&D) is `closed`, but the 2025 sale included the Akron R&D facility and EPA
  lists G-3 CHICKADEE PURCHASER LLC at 1485 E Archwood Ave. A status change needs dated evidence.
- ORG-001790's `trade_names` carries the group name "Creative Composites Group"; ORG-000768's HQ is Dayton OH although the
  group's main-office line is not Composite Advantage's.
- EPA also lists ESSTECH SITE B (48 W Powhattan Ave) and a second Ludlow address (2260 Cedar St, Fremont); neither examined.

## Review

No `council-ask` run (barred for Claude workers by `CONTRACT-CLAUDE.md`); the controller routes review. A reviewer should try
first: the three org folds to apply, the Goodyear Houston/Beaumont folds (street-less survivors), and the Jushi site fold.
