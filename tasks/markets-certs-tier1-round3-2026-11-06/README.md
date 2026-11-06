# L10 Tier-1 markets/certifications round 3

Branch `agent/codex/markets-certs-tier1-round3`. First user: PIC supplier-matching staff; non-use review date 2026-12-15. Acceptance and frame were recorded before research/application. PR157 remains separately reviewed.

## Acceptance and frame

Controller assigned next 100 active organizations with nonempty stored `tier1_qualifier` and blank markets, PIC-18 site first then org_id. Frozen main bdb8b98 frame excludes prior 30 and unresolved ORG-000062/ORG-000101. `frame.csv` has 100 unique IDs; `frame.json` records 1261 active stored-Tier-1 organizations and 1067 eligible after exclusions. No website filter: 12 organizations lack websites; 88 have websites sharing 85 distinct URLs. Unselected organizations remain unworked.

Only markets_served/certifications and matching append-only evidence may change. Exact SCHEMA vocabulary; explicit served-market claims, never generic material possibilities or parent-wide unions copied to subsidiaries. Bare medical/automotive stay unspecified unless the source is specific. No tier/website/status/notes/sources/parent/registry/derived-field edits. The two tier-U organizations remain U.

Certifications follow R3c/R12: current certificate OR current own page naming a non-superseded edition. Dated certificates require identity/effective/expiry witnesses. Current-edition pages assert no invented dates. Superseded ISO9001/14001 and edition-less claims remain held; PR136's transition-window owner battery is unresolved. Failed fetches prove no absence/closure.

Named gates: validator zero errors; known-answer/defect checks; every candidate quote freshly fetched; random30 raw-value audit with error count; complete unique frame/verdict coverage; no-write mutation failures; two-column/append-only boundary; byte-identical replay; Codex and Grok approval before ready.

## Outcomes and provenance

100 organization-enrichment verdicts = **48 VERIFIED / 52 STILL_UNCERTAIN**. VERIFIED means at least one accepted value, not a tier upgrade or every field verified. 159 candidate value rows = **158 VERIFIED (155 markets + 3 certs) / 1 held**. `holds.csv` records **66 claim/organization cases**: all 52 without fills and 14 partial cases. `attempts.csv`: 68 FETCHED / 20 UNFETCHABLE / 12 NO_WEBSITE organization routes; FETCHED means availability, not acceptance.

**50 changed cells on 48 active stored-Tier-1 organizations**: 47 market cells + 3 certification cells; unchanged tiers A22/B24/U2. **158 new evidence rows**, one per accepted value: MN16/NC1/NJ2/OH128/TN1/TX10. Input-index IDs EVD-240160–240318; **240254 is an unused permanent hold slot**. No organization/site creates. Public own-site industries/products/quality pages and original PDFs only; each evidence row retains quote, URL and 2026-11-06 observation date. No private/licensed content.

Initial bdb8b98 baseline, unit = active canonical organizations (4884): markets **404→451**, certs **52→55**. Active stored-Tier-1 subset (1261 organizations): markets **162→209**, certs **15→18**. These count populated organizations, not tags. `counts.json` records latest first application after main replay; `counts.sql` independently recounts canonical shards, excludes generated exports and reports frame/candidate yield.

Accepted certifications (full own-site URLs and exact quotes in inputs):

| Organization | Witness | Currency/scope |
|---|---|---|
| ORG-000823 SIMONA Boltaron | AS9100:D; Intertek 0146420-01 PDF | 2026-04-09 to 2029-04-08; named Newcomerstown entity, specialty thermoplastic sheet/fabricated parts. ISO9001 portion held. |
| ORG-000612 Trelleborg Sealing Profiles US | IATF16949:2016; Smithers 21.197.2 / IATF0528128 PDF | 2024-07-03 to 2027-07-02; named US entity, Aurora extrusions. No market inferred from cert. |
| ORG-000987 Nifco America | Current own homepage names QMS IATF16949:2016 | R3c current-edition-page basis; expiry unknown, date fields empty. Linked normative IATF page is not registrar evidence. No expired PDF overruled. |

Scope-sensitive mappings: STERIS Corp/US Endoscopy medical_device use named-entity certificate product scopes (surgical lights/tables; biopsy devices), not ISO-label inference. Freudenberg-NOK OEM/aftermarket uses explicitly attributed TransTec claims. Spartech OEM uses light-truck OEM flooring. H.B. Fuller food packaging uses packaging_food_beverage. Emery textile/leather→apparel stays held. Generic energy→battery and nuclear→oil/gas are not asserted.

Holds name settling facts and source routes. They include unavailable/challenge-only pages; parent/subsidiary attribution (Roechling, United Initiators, Polynt, Covestro, DuPont, Altivia, INEOS, IPL); Kasai's expired 2024 certificate; edition-less MPC/SECO claims; Superior Trim certificates naming different legal entities; off-vocabulary markets. Core Molding/2020 JS challenges are availability holds: fetch.py now rejects that body despite HTTP200. No operating-status conclusion follows.

## Checks and replay

Run from repo root:

```sh
python3 tasks/markets-certs-tier1-round3-2026-11-06/check.py
python3 tasks/markets-certs-tier1-round3-2026-11-06/build.py
python3 tasks/markets-certs-tier1-round3-2026-11-06/guardcheck.py
python3 tasks/markets-certs-tier1-round3-2026-11-06/boundary.py <integration-main-sha>
duckdb :memory: < tasks/markets-certs-tier1-round3-2026-11-06/counts.sql
python3 scripts/validate.py
```

Before trusting the copied house fetch/matcher, four live known answers passed: CIMA markets positive, ESTERLE ISO2015 positive, Hudson ISO2015 positive, CIMA quality ISO2015 negative. Four fabricated quotes rejected. Raw matching reuses W from `tasks/evidence-repair-2-2026-11-04/prep.py` (requested ownership rawcheck tool absent). Curl browser UA, Jina fallback, pdftotext; ordered normalized tokens, not visual layout. New JS-challenge negative control rejects both routes. **159/159 candidate quotes**, accepted certificate identity/expiry quotes pass; zero unavailable candidate pages. Fresh random sample seed20361107: **30 VERIFIED value rows, 0 raw errors**, routes and parsed-text hashes in audit30.csv. Thirty values, not distinct organizations or semantic-review substitute.

Runnable `guardcheck.py` repeats the following in a temporary copy with canonical-file hashes. Pre-application mutations: duplicate existing evidence ID; IATF page edition2016→2015; dated-cert expiry→2025. Each rejected before writes, canonical hashes unchanged. Dropping a verdict failed 99/100 coverage. boundary.py checks existing keys, old evidence immutability, allowed fields and monotone tag additions, then byte-identical replay. Initial base bdb8b98: 48 orgs/47+3 cells/158 evidence; zero row loss/unrelated fields/old evidence edits. Validator **zero errors**, 35610 evidence rows on initial base. Existing warning queues remain warnings. Shared scripts unchanged; scripts pytest gate not triggered.

On main movement, keep branch history as pre-pass backup. Merge current main per controller-authorized recipe; replace **ALL organization AND evidence shards MN/NC/NJ/OH/TN/TX with main versions**, replay builder, rerun checks. Never retain hand-merged CSV. boundary.json records latest base; refresh counts after replay. Frozen frame/input-index IDs stay unchanged.

Latest integration: merged pinned main **fd55c1049a3aa317e3bef9f4112b739be3500001**, restored all 12 owned data files from that exact base, replayed builder. Active canonical organizations now **4899**, markets **404→451**, certs **52→55**; stored-Tier-1 counts remain **1261 / 162→209 / 15→18**. Same 48 organizations/50 cells/158 evidence, zero old-row loss/unrelated changes, byte-identical replay. Fresh raw159 + random30/0, all four no-write/yield guard checks and validator zero errors (**36563 evidence rows**) pass. Origin/main is moving in parallel; this receipt pins the actual merge parent.

## Refutes and limits

Codex4/Grok4 final deep reviews pending; no completion approval claimed. Refute brief highlights Nifco current-page basis, entity scope and specific market mappings.

Unselected organizations, blocked routes, private-corpus completeness, hosted CI, owner ISO-transition ruling, and status/parent/dedupe settlements are unchecked. Current own-page certificate expiry remains unknown where stated; dated PDFs are point-in-time observations.
