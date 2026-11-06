# Apply the #254 dedupe-medium verdicts — 2026-11-06

Integrator pass for the merged packet `tasks/dedupe-medium-2026-11-06` (Grok approved; a late FRS name search agreed). Scope is
exactly the packet's `to_apply` rows: org folds, site folds and `repoint_site` actions. The 9 `hold_operator` rows and the two
STILL_UNCERTAIN org questions (Carlisle SND-0014, Jushi SND-0049) are untouched. No record is deleted; no new org or site id.

`python3 tasks/dedupe-medium-apply-2026-11-06/build.py` applies (idempotent); `python3 tasks/dedupe-medium-apply-2026-11-06/check.py
--selftest` is the named check. When main moves: check out main's `data/` files and re-run the builder, never hand-merge.

## What changed (unit: rows of `data/` against merge-base 8b35953)

| Change | Count | Detail |
|---|---:|---|
| Org folds applied | 2 | ORG-005115 -> ORG-004865 (Diamond Plastics); ORG-001792 -> ORG-000937 (Crown Foam Technologies -> Ludlow Composites). `status=merged`, `status_date=2026-11-06`, a source appended, `successor_org_id` = survivor |
| Generated `merged_into` edges | 2 | REL-000470, REL-000471, built from the columns (V-27 parity), `effective_from` empty as in earlier dedupe passes |
| Site folds applied (tombstones) | 11 | the duplicate row is `closed` with a note naming the survivor; the survivor keeps its id and notes the absorbed row |
| Repoints applied | 11 | operator org moves; 12 site rows change org_id in total (SITE-001866 follows its absorbed org) |
| Evidence rows (EVD-333000..333014) | 15 | `parent` rows, one witness set per repointed site |
| Facility-grain registry links re-keyed | 4 | org_id only, because V-6 needs a link to carry its site's org (REMOVALS.csv) |
| Capability rows following their site | 14 | org_id only (V-31) |
| Files in `data/` touched | 13 | 2 org shards, 5 site shards, 3 evidence shards, relationships, registry_links, site_capabilities |

Site folds (retired -> survivor): SITE-000005 -> SITE-002964, SITE-002082 -> SITE-002968, SITE-002301 -> SITE-002302,
SITE-004181 -> SITE-002868, SITE-004182 -> SITE-002870, SITE-000427 -> SITE-003478, SITE-004191 -> SITE-003765,
SITE-000989 -> SITE-002962, SITE-002777 -> SITE-004377, SITE-001866 -> SITE-001008, SITE-001800 -> SITE-002965.
(SITE-004191 -> SITE-003765 sits in the Jushi cluster, whose org question stays open: the two rows are the same plant whoever
operates it, and the survivor's `hold_operator` is untouched.)

Repoints (site: old org -> operator): SITE-002964 and SITE-002968 RPM -> ORG-000005 Day-Glo; SITE-002868 and SITE-002870 Goodyear
Tire -> ORG-003746 Goodyear Chemical (sale effective 2025-10-31); SITE-002962 RPM -> ORG-000919 Key Resin; SITE-002965 RPM ->
ORG-001724 Republic Powdered Metals; SITE-000168 RPM -> ORG-001807 Euclid; SITE-001530 RPM -> ORG-001908 Tremco CPG; SITE-003477 and
SITE-003478 acquired Johnsonite Inc. -> ORG-000131 Tarkett North America; SITE-006423 ORG-005115 -> ORG-004865.

Evidence witnesses: EPA FRS REST row for the registrant at 9 addresses (`raw/frs_<id>.json`, fetched 2026-11-06; quote = the
registrant name and address), the Gemspring completion release and the Goodyear release for the two Goodyear plants, and the
FloorDaily Tarkett/Johnsonite release for the two Johnsonite plants (cached pages, sha256 in `sources.csv`).

## Hold: US Farathane (SND-0101) — not applied

The packet's third org fold (ORG-007061 US Farathane LLC -> ORG-007002 US Farathane Corporation) and its repoint (SITE-010064) are
held, as the controller's rule requires when the registry check does not settle it. Michigan LARA and OpenCorporates are behind a
CAPTCHA/403 from here. The GLEIF golden copy (2026-11-06, `hold_SND-0101_gleif.csv`) lists **two separately registered entities**:
U.S. Farathane Corporation (Auburn Hills MI; LEI issued 2013-03-19, entity-supplied only, registration lapsed) and U.S. Farathane, LLC
(Delaware file 5360808, formed 2013-07-02, fully corroborated, active). That is not a conversion record, and a September 2026 news
item calls the Auburn Hills company "U.S. Farathane LLC". **Settling fact:** the Delaware or Michigan filing history showing whether the
Corporation was converted into, merged into, or still operates beside the LLC. `check.py` fails if the held records change.

## Tier-1 qualifier effect (derive_tier1.py --packet, nothing written)

On the base tree: 0 drifting organizations. After the apply: **1 gain, 0 losses** — ORG-004865 Diamond Plastics Corporation gains
`national_footprint` (active sites now span IN, NE, TX: the Muncie plant moved in). `changes.csv` holds the row. Not written
(derived fields are hands-off); the integrator's next derive run picks it up. The RPM, Goodyear and Tarkett qualifiers do not change.

## Checks

`check.py --selftest` passes: expected files only; no keyed row disappears; no org/site row added; changed rows change only the allowed
columns to the expected values; every absorbed org has its successor and every retired site names its survivor; new evidence only in
EVD-333000..333999, quotes found in the raw FRS JSON or the cached page; relationships gain exactly the two generated edges; capability and
registry rows only follow moved sites; tier1 columns untouched; the held cluster untouched; the builder is idempotent on a copy of the
applied data. 18 planted defects are caught. `validate.py`: 0 errors (1 new V-29 warning, the Diamond gain above).
`check_row_loss.py --base origin/main`: OK with `REMOVALS.csv` declaring the 4 re-keyed registry links.

## Departures from the lane contract, and left alone

- **`data/registry_links.csv` was touched** (4 rows, org_id only). CONTRACT.md lists it as do-not-touch, but V-6 rejects a facility-grain link whose
  org differs from its site's; the Ametek repoint of dedupe-hq-2 did the same. Separable if the controller prefers: hold SITE-002968, SITE-002868,
  SITE-000168 and SITE-001530 instead.
- **REL ids 000470-000471** were not allocated to this lane; they sit above the tree maximum and the backlog sweep's REL-000460..469 block.
- **Not moved (out of scope):** two `event_participation` rows (EVP-000389, EVP-000881) still name merged ORG-001792; capability rows CAP-000025/26
  stay on the retired SITE-000005 (the survivor SITE-002964 has CAP-000199 for the same plant); the retired rows keep their evidence.
- The survivor of a fold gets a note naming the absorbed row's type, tier and status; no survivor field other than notes, org_id (repoints) and
  last_verified changed. ORG-000937 gains the trade name "Crown Foam Technologies".
- Not re-verified: plant activity at Muncie and Lake Orion; Johnsonite's acquisition date is the announcement date (EVD-128266 states the same).
