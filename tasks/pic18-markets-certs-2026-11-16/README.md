# PIC-18 markets and certifications, 2026-11-16

Claim: atlas-w16-markets-certs / pic18-markets-certs, controller thr_9i2c6byhcz.
First user: the Atlas owner, for member prospecting. This packet awaits integration and review; no issue is closed or adoption claimed.

## Boundary and method

Packet only, under AGENTS §2.7: the controller integrates canonical data. No data file changed. Proposed scope is only blank organization markets_served/certifications cells and matching append-only organization evidence. No sources, notes, last_verified, tier, or qualifier edits. No record creates; dedupe-create is inapplicable. Reserved proposed IDs EVD-370000–370069, within the assigned block; no ID is applied or reused.

Reused round 5's one-value/one-evidence design, ordered normalized word quote check, exact vocabulary guard, full-frame reconciliation, immutable source hash witnesses, and fail-before-application approach. The round 5 builder was read but never replayed: its old frame, IDs, fetch date and current-edition-page certification exception do not apply here. This lane requires dated unexpired certificate identity and site scope for every certification. `build.py` builds only public packet artifacts and is idempotent. It deliberately has no canonical-data application mode.

## Counts (all are recomputed by check.py)

The supplied manifest contains **745 distinct attempted organizations**, of which **419 organizations have retained pages** (the brief's 419 is the retained subset). The eligible frame is **400 distinct manifest organizations with a retained page and blank markets_served or certifications**. Their **1,850 retained pages** were screened; all 1,850 raw SHA256 values reconcile with the manifest. There are **677 blank organization-field cells** in that frame.

The packet proposes **70 market values for 32 organizations / 32 blank market cells**, with **70 matching evidence rows**. Those organizations have unchanged tiers **A 15 / B 13 / C 4**. There are **0 proposed certification values**, **0 canonical cells applied**, and **0 extra fetches**. Organization yield is **32/400 = 8%**, so no new batch is inferred under CAMPAIGN's low-yield convention.

**645 blank field cells remain held**, each with a settling fact in holds.csv. These are field-cell holds, not 645 organizations or negative claims. Every blank field cell is represented exactly once by accepted proposals or a hold. `inputs.csv` marks accepted proposals `held_for_integration`; `holds.csv` marks unresolved proposals `held`. VERIFIED describes the proposed market value only, never the entire organization or a tier upgrade.

## Source judgment and holds

Sources are the public own-company pages retained in the shared 2026-11-16 corpus. `inputs.csv` records URL, exact ordered-word quote, raw SHA256, text SHA256, and corpus paths for every accepted value. These short public quotes are the committed witnesses; raw HTML/text stay in controller persistence. No CRM, licensed data, personal contacts, or full page dumps are included.

Only explicit own-product/own-service narratives were accepted. Automotive stays unspecified unless OEM customers or aftermarket service are explicit. Medical stays general unless equipment/device is explicit. Food processing is supported by those words, never by Food & Beverage alone. Broader packaging, consumer, furniture, energy and communications labels were not forced into narrower tags. Carbon Polymers' furniture is deliberately not mapped; its explicit lawn and garden is. Enduro's own golf tees support sporting goods; no motorsport inference. Delco's own named market sentence supports its own row, not subsidiaries. KOBELCO's machinery statement is corporate at its own named company, not inferred facility capability. Grand River's drinking-water gasket statement supports water_wastewater, not an NSF certification fill.

The remaining market cells are conservative scope/attribution/vocabulary holds, including menu-only signals. All remaining certification cells are held for standard and edition, issuer or certificate number, exact entity/site scope, and unexpired validity. A corpus mention or no screening-term match is just a screening result, never proof of no market/certificate. These holds are unresolved work, not refuted claims. No certificate document follow-up was fetched; this packet does not claim a comprehensive certificate investigation or exhaustive discovery of every possible acceptable market sentence.

## Named checks

- `python3 tasks/pic18-markets-certs-2026-11-16/check.py`: PASS; source hashes, ordered quotes, vocabulary, frame uniqueness, 677-cell coverage, evidence linkage, and every counts.json count. Injected fabricated quote, invalid vocabulary, missing disposition, tampered SHA256 and duplicate proposal all fail (5/5).
- `python3 tasks/pic18-markets-certs-2026-11-16/build.py`: PASS; replay leaves packet bytes identical.
- `python3 scripts/validate.py`: PASS, 0 errors; 41,575 existing evidence rows checked (packet is not applied).
- `python3 scripts/check_row_loss.py --base origin/main`: PASS.
- `python3 scripts/export_vocab.py --check`: PASS.

This is Codex's checked packet, awaiting controller review and integration. Source presence checks do not independently establish semantic mapping; the explicit human-readable selection remains reviewable in selection.tsv and inputs.csv. Shared scripts were untouched; their unittest suite was not run.

## Proposed follow-ups

- Follow company-hosted certificate links, within the assigned three-fetch budget per organization, to settle held identity/currency/site scope.
- Adjudicate remaining own-product market narratives and off-vocabulary markets under B-MARKETS-VOCAB; do not infer absent markets from this conservative packet.
