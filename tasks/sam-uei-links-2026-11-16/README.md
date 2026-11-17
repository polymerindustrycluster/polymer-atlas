# SAM UEI links — acceptance before application, 2026-11-16

Controller-assigned integrator scope: data/registry_links.csv only; separate from scout PR #335. First user: Atlas controller/researcher; non-use review 2026-11-23.

Acceptance: recover three existing organization UEIs using exact normalized legal/trade/registrant name plus held site street key, state and city before writing data. Query current all-shard Atlas, not the scout's stale frame. Require one distinct UEI per organization and one organization per UEI across all matching pairs; hold any existing UEI, multiple registration, ambiguous location or partial name. No site-grain UEI rows (none exist). New rows contain only org_id, UEI, registry UEI, sam_exact_uei, extract date 2026-11-01 and blank site_id, per controller instruction. No source attributes copied. Retained non-D&B source row required. Preserve registry file as exact byte prefix; pre-pass backup private. Check all additions, one-to-one mapping, existing-link exclusion, counts by organization shard and three injected defects before draft PR. No issue closure; independent data review belongs to controller.

## Result and provenance

Applied locally for PR review: **472 organization-grain UEI rows**, each on an organization previously without a UEI. **595 matching organization/UEI pairs across 557 organizations** were found after requiring exact normalized SAM legal name (not SAM DBA alone), organization legal/trade/recorded alias, site street key, city and state. One-to-one checks cover all such matching pairs, not merely the proposals. A UEI must occur exactly once in the retained extract; multiple registrations/identities are held. No site UEI links are authored. Multiple sites supporting the same organization/UEI are witnesses, not additional proposals.

This is narrower than the scout's 685 site/UEI name+street pairs: this pass uses current main, requires city equality and org legal/alias-to-SAM-legal-name equality, then collapses by organization and applies ambiguity/existing-link gates. It does not claim all 685 pairs were eligible. No fields were inherited from SAM into organization/site records.

| Proposal disposition | Applied/held | Count of organization/UEI pairs | Settling fact |
|---|---|---:|---|
| Exact unique pair; organization has no prior UEI | Applied locally | 472 | Exact UEI in retained source index; review/CI pending |
| Organization already has UEI | Held | 87 | Separate authorization if any existing mapping is to be revised; none changed here |
| Multiple UEIs match one organization | Held | 35 | Exact legal registrant/site binding resolving the ambiguity |
| Multiple source registrations/identities for UEI | Held | 1 | Unique current source registration identity |

Three known answers recovered BEFORE data mutation, with the same UEIs as the pre-pass registry table: ORG-000194 / RQJGN2NZMNC4; ORG-000317 / VD1NLZGAJ2L4; ORG-000402 / GM5MMNB6DGB8. All three use the same strict candidate matcher as the proposals; existing links remain untouched.

Source: [SAM PUBLIC extract documentation](https://open.gsa.gov/api/sam-entity-extracts-api/), `SAM_PUBLIC_MONTHLY_V2_20261101.ZIP`, SHA256 `2db04ae10f237f048b28b6354884431c7b8d61d122b437647b29d23a6cdb5e4d`; acquired 2026-11-16, extract dated 2026-11-01. `as_of` carries **extract date**, as this pass's controller explicitly instructed; this differs from SCHEMA §4.8's usual retrieval-date wording and is disclosed for review. `match_basis=sam_exact_uei` follows §4.8. The identifier itself is checked verbatim against a retained non-D&B source row. The owner's filtered-leads/UEI-only ruling applies; no new API calls or credentials used. No SAM names, addresses or codes are copied into task outputs or canonical data. Registry identity is the reference-link table (§4.8); no activity, scope, tier, name or address claim is authored, and no evidence IDs are minted.

`summary.json` carries counts by the organization's current shard (the registry itself remains a single file), all known answers and baseline hash. `holds.csv` has only Atlas IDs, source-issued UEIs, held witness site IDs, shard and reasons. `additions.csv` is the exact append payload. Pre-pass backup: controller persistence `persist/sam-uei-links/registry_links.before.csv`. Initial baseline is pinned there; builder refuses any registry file differing from that baseline or this exact append. The private source index remains `persist/sam-entity-scout/sam.sqlite`. It contains 911,352 retained source rows, with non-D&B and date gates checked for every proposed UEI. Raw ZIPs were deleted in the scout.

## Verification and limits

`python3 tasks/sam-uei-links-2026-11-16/build.py` idempotently reproduces the append from the baseline; `check.py` recomputes current candidates, reconciles every proposal/hold/count and shard count, verifies exact retained source rows, proves the canonical file is the baseline plus only the append, and rejects three injected defects: phantom UEI, second UEI for an organization, same UEI assigned twice. Missing source/backup fails closed. No changes under scripts/, no dependencies or generated database committed.

Remaining holds: no name+city address lead or unmatched NAICS lead applied; no identity beyond this exact matcher asserted. Independent family reviews/CI are pending with controller; this task does not close an issue. Proposed follow-ups: adjudicate ambiguous registrant pairs separately, retaining current links until explicit authorization.

Recorded checks: builder rerun PASS (same append); packet check PASS (3 known answers, 472 new links, 123 holds, 3 injected defects); `python3 scripts/validate.py` PASS (0 errors); `python3 scripts/check_row_loss.py --base origin/main` PASS; `python3 scripts/export_vocab.py --check` PASS. Full scripts test suite not run (scripts/ untouched). No task/issue closed and no merge performed.
