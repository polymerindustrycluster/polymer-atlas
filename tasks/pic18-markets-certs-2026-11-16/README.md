# PIC-18 markets and certifications, 2026-11-16 — applied

Claim: atlas-w16-markets-certs / pic18-markets-certs, controller thr_9i2c6byhcz.
First user: the Atlas owner, for member prospecting. Applied under the controller’s explicit delegation on PR #344; family review remains pending. No issue is closed or adoption claimed.

## Boundary and method

The controller, integrator of record under AGENTS §2.7, explicitly delegated application of this fixed packet to this lane. Applied scope is 32 previously blank organization markets_served cells and 70 matching append-only organization evidence rows in the OH shard pair. No sources, notes, last_verified, tier, or qualifier edits. No record creates; dedupe-create is inapplicable. Reserved proposed IDs EVD-370000–370069, within the assigned block; all 70 IDs are applied once; no pre-existing ID is reused.

Reused round 5's one-value/one-evidence design, ordered normalized word quote check, exact vocabulary guard, full-frame reconciliation, immutable source hash witnesses, and fail-before-application approach. The round 5 builder was read but never replayed: its old frame, IDs, fetch date and current-edition-page certification exception do not apply here. This lane requires dated unexpired certificate identity and site scope for every certification. `build.py` uses pinned pre-application commit `0c7bacc1840741fbf130e39c9bb11fd5c39abdc0` for the frozen frame and applies the fixed packet idempotently. It preserves all other current row fields, accepts only blank or exact-replay market cells, and checks global evidence-ID uniqueness plus exact shard/payload parity before any write. `scripts/shard_io.py append_sorted` appends new evidence. Pre-pass copies of both edited shards are retained at controller persistence `persist/pic18-markets-certs/pre-application/`. `application.json` is the fixed-scope application journal.

## Counts (all are recomputed by check.py)

The supplied manifest contains **745 distinct attempted organizations**, of which **419 organizations have retained pages** (the brief's 419 is the retained subset). The eligible frame is **400 distinct manifest organizations with a retained page and blank markets_served or certifications**. Their **1,850 retained pages** were screened; all 1,850 raw SHA256 values reconcile with the manifest. There are **677 blank organization-field cells** in that frame.

The packet proposes **70 market values for 32 organizations / 32 blank market cells**, with **70 matching evidence rows**. Those organizations have unchanged tiers **A 15 / B 13 / C 4**. There are **0 proposed certification values**, **32 canonical market cells applied**, and **0 extra fetches**. Organization yield is **32/400 = 8%**, so no new batch is inferred under CAMPAIGN's low-yield convention.

**645 blank field cells remain held**, each with a settling fact in holds.csv. These are field-cell holds, not 645 organizations or negative claims. Every blank field cell is represented exactly once by accepted proposals or a hold. `inputs.csv` marks accepted proposals `applied`; `holds.csv` marks unresolved proposals `held`. VERIFIED describes the proposed market value only, never the entire organization or a tier upgrade.

## Source judgment and holds

Sources are the public own-company pages retained in the shared 2026-11-16 corpus. `inputs.csv` records URL, exact ordered-word quote, raw SHA256, text SHA256, and corpus paths for every accepted value. These short public quotes are the committed witnesses; raw HTML/text stay in controller persistence. No CRM, licensed data, personal contacts, or full page dumps are included.

Only explicit own-product/own-service narratives were accepted. Automotive stays unspecified unless OEM customers or aftermarket service are explicit. Medical stays general unless equipment/device is explicit. Food processing is supported by those words, never by Food & Beverage alone. Broader packaging, consumer, furniture, energy and communications labels were not forced into narrower tags. Carbon Polymers' furniture is deliberately not mapped; its explicit lawn and garden is. Enduro's own golf tees support sporting goods; no motorsport inference. Delco's own named market sentence supports its own row, not subsidiaries. KOBELCO's machinery statement is corporate at its own named company, not inferred facility capability. Grand River's drinking-water gasket statement supports water_wastewater, not an NSF certification fill.

The remaining market cells are conservative scope/attribution/vocabulary holds, including menu-only signals. All remaining certification cells are held for standard and edition, issuer or certificate number, exact entity/site scope, and unexpired validity. A corpus mention or no screening-term match is just a screening result, never proof of no market/certificate. These holds are unresolved work, not refuted claims. No certificate document follow-up was fetched; this packet does not claim a comprehensive certificate investigation or exhaustive discovery of every possible acceptable market sentence.

## Named checks

- `python3 tasks/pic18-markets-certs-2026-11-16/check.py`: PASS; source hashes, ordered quotes, vocabulary, frame uniqueness, 677-cell coverage, evidence linkage, and every counts.json count. Injected fabricated quote, invalid vocabulary, missing disposition, tampered SHA256 and duplicate proposal all fail (5/5).
- `python3 tasks/pic18-markets-certs-2026-11-16/build.py`: PASS; replay leaves canonical data and task artifacts byte-identical.
- `python3 tasks/pic18-markets-certs-2026-11-16/guardcheck.py`: PASS; duplicate ID, identical evidence in foreign shard, changed evidence payload and conflicting market cell rejected before any data write.
- Applied boundary in `check.py`: all canonical tables compared with the pinned pre-application commit; exactly 32 market-cell fills and 70 evidence appends, zero unrelated field changes, old-row loss or old-evidence edits. The 645 holds remain byte-identical at CSV row level.
- `python3 scripts/validate.py`: PASS, 0 errors; 41,645 evidence rows checked, including the 70 appended rows.
- `python3 scripts/check_row_loss.py --base origin/main`: PASS.
- `python3 scripts/export_vocab.py --check`: PASS.

This is Codex's checked application, awaiting the required two-family review before merge. Source presence checks do not independently establish semantic mapping; the explicit human-readable selection remains reviewable in selection.tsv and inputs.csv. Shared scripts were untouched; their unittest suite was not run.

## Proposed follow-ups

- Follow company-hosted certificate links, within the assigned three-fetch budget per organization, to settle held identity/currency/site scope.
- Adjudicate remaining own-product market narratives and off-vocabulary markets under B-MARKETS-VOCAB; do not infer absent markets from this conservative packet.

## Applied counts by shard

| Organization shard | Market cells / organizations | Market values | Matching evidence shard | Appended evidence rows |
|---|---:|---:|---|---:|
| organizations_OH.csv | 32 | 70 | evidence_organizations_OH.csv | 70 |

No other canonical shard changed. All 645 holds remain as originally submitted.

Review repair: batch 1 now reads immutable corpus `manifest-pass1.csv` (through build.source in both builder and checker), so later corpus passes do not change its frozen frame. No data payload changed. Named check rerun from a clean local clone of the repair commit.
