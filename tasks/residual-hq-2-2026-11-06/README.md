# Residual HQ determination, pass 2 — L5b

Acceptance is frozen in acceptance.md; cohort.csv holds the first 100 eligible ID-sorted organizations from the 247-row residual shard at base.txt. Excludes ORG-009017/009026. First user: Atlas controller/PIC researcher; non-use finding date 2026-11-13. Controller owns tracker/status/merge. This lane is the delegated single data writer.

Sources: each verdict names its public primary URL; rawcheck.json records independent integrator curl/browser-UA checks and hashes. PDF witnesses use pdftotext -layout. Source text caches remain outside the repository in /tmp, not public artifacts. Parser and token matching reuse lane A's HTML reader and the house evidence-repair prep.W normalizer. Ordered `||` excerpts are checked separately, in page order, never treated as adjacent source words.

The packet verdicts in lanes/a and lanes/b are proposals. Final verdicts.csv governs integration. LEI discovery addresses are held because the pass calls for own-site, state registry or dated public records; the West Virginia state principal-office proposal caps address evidence at supports_C and is held because its organization remains B tier. Parent/group HQ, mailing-only contacts, unsupported county, and tombstone moves are not inferred. No tiers, statuses, qualifiers, relationships, sites or registry links change. A move is not re-verification; last_verified remains unchanged. Historical evidence moves intact with its organization. Append-only new address observations use EVD-315000–319999.

## Holds

All STILL_UNKNOWN rows in verdicts.csv form the holds table, one organization per row, with settling_fact and note. In particular LyondellBasell's own page lists three HQ cities; recommendation: owner select the intended canonical HQ before applying a single placement. Subsidiaries retain unknown HQ when only the parent HQ is stated. Tombstones remain in their old shard under Appendix C §2. Registry-only Professional Plastics/Jacuzzi/Armorock/DiversiTech discoveries remain proposals, not applied facts.

## Checks

- Baseline `python3 scripts/validate.py`: PASS, zero errors.
- House reader/parser: three known primary-page quote answers (Dura Bloomington, RESRG Troy, Synthomer group London) PASS. Synthomer's parser answer is deliberately not an entity-grain acceptance. Mailing/HQ and wrong-city substitutions fail. Lane A check: 30 exact IDs, six proposed positives, 52 receipts, maximum three attempts/entity; missing/duplicate/fabricated quote mutations fail as expected. Lane B supplies its own checks/receipts.
- `python3 tasks/residual-hq-2-2026-11-06/check.py`: full organization ID/content and old evidence ID/content union proof against base.txt, exact 100 final verdicts, raw hashes, byte-idempotent builder replay, missing ID/header/evidence-collision no-write fault checks.
- `python3 scripts/validate.py`: final result recorded below after application.

Builders preflight all before writes and preserve unrelated main rows. Rebase by replacing canonical files with fresh main, updating base.txt, and rerunning builder/check; stop on any cohort preimage conflict rather than hand-merging CSVs.

## Review

BOARD 05:55 and 06:25 explicitly supersede the original council-only gate. Request independent deep refutation from R-codex-3 and R-grok-3 using a draft PR and refute.md. Approvals remain pending until received; no Done/merge/issue closure claimed.

## Handoff ledger

2026-11-06: L5b thr_ii6ybubss4 took over thr_3mzpqc9u48's existing checkout/branch, acceptance and frozen cohort. Existing helpers A thr_cbqmb8vyh7 and B thr_niknbt9gc4 continue packet-only, no shared data edits. Helper A delivered 30 rows/6 proposals/24 holds; integrator independently qualifies and re-fetches every proposed source. Same agreement and facts appended to the controller BOARD. Review clerk messages use queue mode only under explicit BOARD exception.

## Applied result and validation

Final unit/filter: 100 frozen residual organizations reviewed = 10 HQ_FOUND placements + 90 STILL_UNKNOWN holds. Ten existing organizations moved from US to AL 1, CA 2, CT 1, IN 2, ME 1, MI 1, MO 1, NV 1. Residual shard 247 → 237 organizations. No organizations or sites created. Held organization tiers unchanged: A 2, B 6, C 2, U 0. Twenty old evidence rows moved with those ten organizations, byte-equivalent at row-content grain; ten new address evidence rows appended (EVD-315000–315007 and EVD-315009–315010). EVD-315008 retired after a local validation rejection, never published.

`python3 tasks/residual-hq-2-2026-11-06/check.py`: PASS — exact100 coverage, full organization and old evidence union/content preservation, ten permitted HQ edits, receipts, byte-idempotency, three no-write faults, two quote substitutions. `python3 scripts/validate.py`: PASS, zero errors, 4,970 organizations / 7,007 sites / 36,556 evidence observations checked. Existing repository-wide warnings remain; none waived here. No scripts/ changes, so full pytest not required/run.

The first local application exposed WV SOS APG's address-only registry ceiling C versus held B (V-25). APG is now held rather than downgraded; its proposed evidence ID is retired. American Renolit's certificate quote did not reproduce in the independent integrator extraction and is held, not treated as an absence finding. Three LEI-only proposals are held by the source restriction. Fresh corrected build replay and validation both pass.

Helper B delivered 30 unique verdicts, seven proposals, 23 holds; 87 raw route attempts, max six per organization, 3 real parser cases and 3 negative controls. Lead reran both helper checks successfully. Raw caches in /tmp are needed for receipt rechecks; canonical preservation and replay checks use committed inputs and git base. Cross-thread receipt facts recorded here and on BOARD; no helper is an integration writer.

## Original-session collision reconciliation

Controller confirmed sole-writer L5b after original L5 resumed. Its only uncommitted lead/verdicts.csv overwrite was restored from committed HEAD, then the three independent findings were compared deliberately: RESRG Troy and Dura Bloomington agree with the applied observations; Professional Plastics GLEIF Fullerton is retained as a fourth registry-only discovery hold, without changing canonical data. Its 16 independent positive receipts (15 raw PASS, Renolit split-layout FAIL) are preserved in original-l5-rawcheck.json; all 16 hashes independently reproduced. Renolit remains held. No helper results or data were overwritten during this reconciliation.

Fetch-budget exception: Wabash helper used six routes; original L5 then independently fetched once, and L5b independently fetched twice (the second replay followed the APG V-25 correction): nine total source fetches, exceeding the approximate six-route effort cap. No further Wabash fetch is needed. This collision/redundant replay is disclosed rather than hidden. All fetched affirmative content agrees; it does not change acceptance criteria.
