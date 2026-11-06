# L10 round 2 — Tier-1-qualified organizations

Controller 06:30 BOARD assignment; new branch agent/codex/markets-certs-tier1 off current main. Scope: markets_served and certifications only, plus append-only own_site evidence. First user PIC supplier-matching staff; use review due 2026-12-15. IDs EVD-240100 onward inside original L10 block (prior PR136 reserves through240063; never reuse).

Acceptance before application: own-site corporate markets using exact SCHEMA vocabulary; automotive unspecified stays unspecified, medical without devices stays medical_healthcare_general. No generic material uses treated as served markets. Current edition + current dates for certifications; identity and expiry quotes checked, no ISO9001:2015 until owner transition ruling. Every added value has its own evidence row; no other organization columns changed, no tier changes. validate0errors, known answers and defect rejection, fresh30-value sample with error count, replay identical, two-family clerks required. PR136 was reviewed separately, approved by both families, and merged by the controller (not this lane).

Frozen frame: frame.csv selected30 from1261 active organizations with nonempty stored tier1_qualifier (no rederivation). First30 blank markets + HTTP website, PIC18 first then org_id; excludes two prior holds ORG62/101 without resolving evidence. frame.json records census and filters. Lower-priority unselected rows are unworked, never held or verified by implication.

Research underway; not completion-approved.

## Results and provenance

Unit/filter: all active organization rows, integration baseline mainbdb8b98 (includes PR136 and PR147), 4,884. markets_served populated404→416 (+12 organizations); certifications52→54 (+2). Tier-1-filtered active organizations1,261: markets162→174, certifications15→17. These are incremental round2 counts on main after PR136; frame.json preserves the earlier main9489b60 selection census (cert13 before the two Tier1 cert fills in PR136).

30 frozen-frame organizations =12 VERIFIED and18 STILL_UNCERTAIN; verdicts.csv covers all30 exactly once. The12 changed organizations retain tiers A8/B3/C1. inputs.csv contains60 VERIFIED value fills:58 market values and2 certifications, EVD240100–240159. Evidence shards OH42/US18. No organizations/sites created or status/tier/website/parent/newsroom/notes/source columns changed. No inclusion-log entries or dedupe/create needed.

Sources are corporate own-site markets/about/industry pages of LyondellBasell, Novagard, Goldsmith&Eggleton, Addipel, Advanced Polymer Coatings, American Wire&Cable, Architectural Fiberglass, Barentz North America, Blair Rubber, Duracote, Forest City Technologies and Garland. Every URL and exact quote is in inputs.csv. Broad branded-material application possibilities are not corporate market evidence. Provider-specific product applications are used only where they explicitly state that provider's own market or business (e.g. American Wire's core appliance-wire business and named automotive-wire manufacturing).

Certificates: Novagard Smithers04.293.1 / IATF0520614, IATF16949:2016 with Product Design, current2024-05-31 through2027-05-30, main Cleveland site plus named warehousing support only. Duracote Smithers19.018.1, AS9100:2016 with Design, current2024-04-20 through2027-04-19, Ravenna single-site laminates/coatings scope. Duracote home also states AS9100RevD. Original company-hosted PDFs quote identity/edition/expiry, date bounds checked; no ISO9001 component filled.

Normative context, never organization evidence: [IATF current standard page](https://www.iatfglobaloversight.org/iatf-169492016/about/), [IAQG9100:2016 resources](https://iaqg.org/standard/9100-qms-requirements-for-aviation-space-and-defense-organizations/) and [IAQG/SAE standards register](https://brx-content.fullsight.org/site/binaries/content/assets/sae-org/content/landing-page/iaqg/2025-12-05-standards-register-for-publication.pdf) identify the accepted editions (register lists AS9100RevD2016-09-20). [ISO14001 current edition](https://www.iso.org/standard/14001) is2026, so Goldsmith's2015 claim stays held under R3c, alongside ISO9001:2015 candidates. The owner transition-window question remains the PR136 battery; no exception self-ruled.

## Holds and limits

holds.csv has25 claim/organization cases:18 organizations without a fill plus7 partial-field cases on filled organizations. Every row is STILL_UNCERTAIN with its settling fact. Availability failures prove nothing about operating status or absence of a market/certification. Ashtabularubber.com served ASC Engineered Solutions; attribution is held. Global Huntsman and LG Chem pages are not attributed to the named subsidiaries. Other holds include explicit end-market gaps, edition-less or superseded certifications, uninspected image certificate, and ambiguous/off-vocabulary categories. No markets_other_note org column exists, so no off-vocabulary tag is inserted. Unselected qualifying organizations remain unworked; no full Tier1 completion claim.

## Named checks

- `python3 tasks/markets-certs-tier1-2026-11-06/check.py`: four live known answers4/4, fabricated-quote defects refused4/4; all60 input quotes passed with no unavailable sources, including both certificate identity and expiry quotes. Fresh random30 VERIFIED value rows (seed20361106):0 quote errors. audit30.csv records values, retrieval routes and parsed-text hashes. This is a raw quote-support audit, not30 distinct organizations or an independent human semantic audit. fetched HTML has scripts/styles excluded; CSS visibility is not evaluated. Pages may change later.
- `python3 tasks/markets-certs-tier1-2026-11-06/build.py`: first run60 appends, second run byte-identical across affected shards. Tree-wide duplicate-ID defect was injected into read() before application: AssertionError before writes, all canonical CSV byte hashes unchanged. Vocabulary, active/storedTier1/frame membership, domain, unique values/recordIDs, certificate dates and immutable evidence collision conditions asserted. Existing observation equality checked.
- Parsed CSV before/after scope check:12 organizations,12 market fields,2 certification fields,60 evidence rows; zero missing keys, changed unrelated columns or edited existing evidence observations.
- `python3 scripts/validate.py`: OK validation passed,0errors,35,512 total evidence rows on this main baseline. Existing warnings remain. No scripts/ shared files changed, so shared-script pytest gate is not triggered.

Reuse: fetch.py/check.py/build.py carry forward the reviewed PR136 helper and guard fixes. Token normalization and contiguous-order matching are imported from the house tasks/evidence-repair-2-2026-11-04/prep.py. No dependency added. Research primary-page budget≤5 distinct own-site pages per organization; required live verification re-fetches are additional checks. Raw bodies lived temporarily under /tmp; only public quotes are committed.

Replay on newer main: restore main's organizations_OH.csv, organizations_US.csv, evidence_organizations_OH.csv and evidence_organizations_US.csv, rerun build.py and validate; never hand-merge CSVs. Preserve inputs order to preserve reserved evidence IDs. Branch base is the pre-pass backup; this README is the pass journal.

## Coordination and review

Controller06:30 assignment supersedes initial lane's lack of continuation. Branch/ID allocation/frame recorded in BOARD before application. Controller06:25 route supersedes old clerk pair for new requests: Codex4 thr_x5xruuutxp and Grok4 thr_95ffgh3rxy; queue exception applies to requests only. PR136 received Codex/Grok APPROVE0blocking, both recorded in its README, and controller merged it. This round's final two-family reviews are pending; no Done claim.

Additional controls: check.py reconciles30unique frame IDs against30unique verdict IDs; injected29/30 extraction fails before network or writes. Independent DuckDB1.5.6 SQL recount (`duckdb :memory: < tasks/markets-certs-tier1-2026-11-06/counts.sql`) confirms the active and storedTier1 filled counts above.

Integration: main advanced to bdb8b98 with controller merges PR136/147. Took main versions of the four affected OH/US shards and reran builder; no hand CSV merges. Original round2 proposal on9489b60 was394→406market/47→49cert; on current main the same60fills give404→416/52→54. No first-PR changes are bundled as round2 changes. Both earlier frame and current counts reconcile by the merged first-PR additions.
