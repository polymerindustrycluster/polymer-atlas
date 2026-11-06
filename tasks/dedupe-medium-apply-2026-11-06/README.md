# Apply the #254 dedupe-medium verdicts — 2026-11-06

Integrator pass for the merged packet `tasks/dedupe-medium-2026-11-06` (Grok approved; a late FRS name search agreed). Scope is
exactly the packet's `to_apply` rows: org folds, site folds and `repoint_site` actions. The 9 `hold_operator` rows and the two
STILL_UNCERTAIN clusters (Carlisle SND-0014, Jushi SND-0049) are untouched, including Jushi's site fold (see Holds). No record is deleted; no new org or site id.

`python3 tasks/dedupe-medium-apply-2026-11-06/build.py` applies (idempotent); `python3 tasks/dedupe-medium-apply-2026-11-06/check.py
--selftest` is the named check. When main moves: check out main's `data/` files and re-run the builder, never hand-merge.

## What changed (unit: rows of `data/` against merge-base 8b35953)

| Change | Count | Detail |
|---|---:|---|
| Org folds applied | 2 | ORG-005115 -> ORG-004865 (Diamond Plastics); ORG-001792 -> ORG-000937 (Crown Foam Technologies -> Ludlow Composites). `status=merged`, `status_date=2026-11-06`, a source appended, `successor_org_id` = survivor |
| Generated `merged_into` edges | 2 | REL-000470, REL-000471, built from the columns (V-27 parity), `effective_from` empty as in earlier dedupe passes |
| Site folds applied (tombstones) | 10 | the duplicate row is `closed` with a note naming the survivor; the survivor keeps its id and notes the absorbed row |
| Repoints applied | 11 | operator org moves; 12 site rows change org_id in total (SITE-001866 follows its absorbed org) |
| Evidence rows (EVD-333000..333015) | 16 | `parent` rows, one witness set per repointed site |
| Facility-grain registry links re-keyed | 4 | org_id only, because V-6 needs a link to carry its site's org (REMOVALS.csv) |
| Capability rows following their site | 14 | org_id only (V-31) |
| Files in `data/` touched | 12 | 2 org shards, 4 site shards, 3 evidence shards, relationships, registry_links, site_capabilities |

Site folds (retired -> survivor): SITE-000005 -> SITE-002964, SITE-002082 -> SITE-002968, SITE-002301 -> SITE-002302,
SITE-004181 -> SITE-002868, SITE-004182 -> SITE-002870, SITE-000427 -> SITE-003478, SITE-000989 -> SITE-002962,
SITE-002777 -> SITE-004377, SITE-001866 -> SITE-001008, SITE-001800 -> SITE-002965.

Repoints (site: old org -> operator): SITE-002964 and SITE-002968 RPM -> ORG-000005 Day-Glo; SITE-002868 and SITE-002870 Goodyear
Tire -> ORG-003746 Goodyear Chemical (sale effective 2025-10-31); SITE-002962 RPM -> ORG-000919 Key Resin; SITE-002965 RPM ->
ORG-001724 Republic Powdered Metals; SITE-000168 RPM -> ORG-001807 Euclid; SITE-001530 RPM -> ORG-001908 Tremco CPG; SITE-003477 and
SITE-003478 acquired Johnsonite Inc. -> ORG-000131 Tarkett North America; SITE-006423 ORG-005115 -> ORG-004865.

Evidence witnesses: EPA FRS REST row for the registrant at 9 addresses (`raw/frs_<id>.json`, fetched 2026-11-06; quote = the
registrant name and address), the Gemspring completion release and the Goodyear release for the two Goodyear plants, the FloorDaily
Tarkett/Johnsonite release for the two Johnsonite plants, and, for SITE-003478 only, the EPA TRI facility record 44022JHNSN16910
("TARKETT USA INC DBA JOHNSONITE" at 16910 Munn Rd; RY2024 form received 2025-06-27). Cached pages and JSON: sha256 in `sources.csv`.
The TRI JSON carries a public-contact name, phone and email, so it lives in `persist/` and is never committed.

## Holds — not applied

### Jushi site fold (SND-0049): controller carve-out
The scope said 11 site folds and also that the two STILL_UNCERTAIN clusters stay untouched; the Jushi site fold
(SITE-004191 -> SITE-003765) is in both. Resolved conservatively: held. It is the same plant whoever operates it and is ready to apply on the
controller's word: delete the `SND-0049` entry from `HOLD` in `build.py` and `HELD` in `check.py` and re-run (one more site shard, sites_SC.csv).

### US Farathane (SND-0101)

The packet's third org fold (ORG-007061 US Farathane LLC -> ORG-007002 US Farathane Corporation) and its repoint (SITE-010064) are
held, as the controller's rule requires when the registry check does not settle it. Michigan LARA and OpenCorporates are behind a
CAPTCHA/403 from here. The GLEIF golden copy (2026-11-06, `hold_SND-0101_gleif.csv`) lists **two separately registered entities**:
U.S. Farathane Corporation (Auburn Hills MI; LEI issued 2013-03-19, entity-supplied only, registration lapsed) and U.S. Farathane, LLC
(Delaware file 5360808, formed 2013-07-02, fully corroborated, active). That is not a conversion record, and a September 2026 news
item calls the Auburn Hills company "U.S. Farathane LLC". **Settling fact:** the Delaware or Michigan filing history showing whether the
Corporation was converted into, merged into, or still operates beside the LLC. `check.py` fails if the held records change.

## Review round 1 (Codex REFUTE of f9ddb52, two evidence findings; Grok approved)

1. **EVD-333004 / EVD-333006** said the Gemspring affiliate completed the acquisition "on 2025-11-03". The release is dated November 3 and says the
   acquisition has completed; it gives no completion date. Restated as "Gemspring Capital's release dated 2025-11-03 announces that an affiliate has
   completed the acquisition ... (the release does not state the completion date)". The effective date 2025-10-31 stays on the Goodyear rows
   (EVD-333005/333007). `PRESS['gemspring']` in `build.py` carries the new wording,
   and `check.py` fails if a Gemspring row dates completion.
2. **EVD-333008** (SITE-003478) said FRS names Tarkett as operator; FRS 110000385244 says JOHNSONITE. It now records the literal registrant and
   address and states no operator. The 2005 acquisition row (EVD-333009) now says it is an acquisition, not a statement of who operates the plant.
   The operator evidence is a new row, **EVD-333015**: EPA's TRI facility record 44022JHNSN16910 names the facility and its mailing name "TARKETT USA INC DBA
   JOHNSONITE" at 16910 Munn Rd, with a RY2024 form received 2025-06-27, i.e. Tarkett USA Inc is the dated filer at this plant (the Atlas already holds that
   registrant as ORG-000131 at Middlefield: FRS 110009662855 on SITE-001399). The SITE-003478 repoint therefore stands. It was found with 2 fetches
   (the WoodFloorBusiness relocation article returned 403).
   `check.py` now also fails if an FRS row says a registrant "names the operator" while sharing no leading word with the target org's name.

In-place corrections through the builder (the rows are new in this PR): EVD-333004, 333006 (finding 1), EVD-333008, 333009 (finding 2) and EVD-333011
(SITE-003477's copy of the same acquisition-announcement row, same reasoning; no longer asserts "operator is X, no longer Y"). Their ids stay. EVD-333005/333007
(Goodyear release, effective 2025-10-31, accepted by the reviewer) are unchanged. The one new row is EVD-333015, placed last so no id shifts.

## Tier-1 qualifier effect (derive_tier1.py --packet, nothing written)

On the base tree: 0 drifting organizations. After the apply: **1 gain, 0 losses** — ORG-004865 Diamond Plastics Corporation gains
`national_footprint` (active sites now span IN, NE, TX: the Muncie plant moved in). `changes.csv` holds the row. Not written
(derived fields are hands-off); the integrator's next derive run picks it up. The RPM, Goodyear and Tarkett qualifiers do not change.

## Checks

`check.py --selftest` passes (10 site folds, 11 repoints, 2 org folds, held clusters SND-0049 and SND-0101): expected files only; no keyed row disappears; no org/site row added; changed rows change only the allowed
columns to the expected values; every absorbed org has its successor and every retired site names its survivor; new evidence only in
EVD-333000..333999, quotes found in the raw FRS JSON or the cached page; relationships gain exactly the two generated edges; capability and
registry rows only follow moved sites; tier1 columns untouched; the held cluster untouched; the builder is idempotent on a copy of the
applied data. 21 planted defects are caught. `validate.py`: 0 errors (1 new V-29 warning, the Diamond gain above).
`check_row_loss.py --base origin/main`: OK with `REMOVALS.csv` declaring the 4 re-keyed registry links.

**The #254 packet's own `check.py` now fails on the applied tree, by design:** its `to_apply` org folds are merged and its survivors already sit under the
operators it asked for (34 problems, all of that kind). Run each task check at its own pass state with `scripts/run_task_checks.py`.

## Departures from the lane contract, and left alone

- **`data/registry_links.csv` was touched** (4 rows, org_id only). CONTRACT.md lists it as do-not-touch, but V-6 rejects a facility-grain link whose
  org differs from its site's; the Ametek repoint of dedupe-hq-2 did the same. Separable if the controller prefers: hold SITE-002968, SITE-002868,
  SITE-000168 and SITE-001530 instead.
- **REL ids 000470-000471** were not allocated to this lane; they sit above the tree maximum and the backlog sweep's REL-000460..469 block.
- **Not moved (out of scope):** two `event_participation` rows (EVP-000389, EVP-000881) still name merged ORG-001792; capability rows CAP-000025/26
  stay on the retired SITE-000005 (the survivor SITE-002964 has CAP-000199 for the same plant); the retired rows keep their evidence.
- The survivor of a fold gets a note naming the absorbed row's type, tier and status; no survivor field other than notes, org_id (repoints) and
  last_verified changed. ORG-000937 gains the trade name "Crown Foam Technologies".
- Observed, not fixed: SITE-001399 ("Tarkett North America — Middlefield", FRS 110009662855) and SITE-003477 (16035 Industrial Pkwy, same FRS id) are now both under
  ORG-000131 and look like one establishment held twice; they were under different orgs before, so no name cluster found them.
- Not re-verified: plant activity at Muncie and Lake Orion; Johnsonite's acquisition date is the announcement date (EVD-128266 states the same).
