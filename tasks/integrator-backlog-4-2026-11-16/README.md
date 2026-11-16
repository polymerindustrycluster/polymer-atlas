# Integrator backlog 4 — 2026-11-16

Fixed owner manifest; researcher/integrator `atlas-w16-fixes`. Acceptance: no new organization/site IDs, no unrelated edits, append-only evidence, plant-specific scope, no inferred parent, preserved tombstones; local validator and row-loss check pass. First operator: controller for this integration pass, 2026-11-16. No tracker or queue change.

9 manifest cases: 4 VERIFIED-applied; 5 STILL_UNCERTAIN with settling facts. Of the held cases, 3 have a partial application. `dispositions.csv` lists every applied/held item and settling fact. Baseline differed from brief: HEXPOL was already merged, Reiser already tombstoned, AltraSet already parented, Pittsburgh already had its website, and PPG/Sherwin-Williams were already tier A. No further tier promotion, status change, parent change, or generated relationship change is needed or made.

15 evidence rows added on 9 existing records (5 organizations and 4 sites): 10 organization-grain observations and 5 site-grain observations, within EVD-369000–369014; 12 supports_A and 3 supports_C. Two existing tier-C sites gain materials: Silgan Thomaston recycled_content_pcr_pir, NOV Wichita epoxy. No processes filled; no organization/site created or removed. No inclusion-log borderline changes.

Sources: own AltraSet about page; SEC fiscal-2025 10-Ks and Exhibit 21/21.1 for PPG and Sherwin-Williams; Pittsburgh Paints home page; Silgan 2021 Thomaston announcement; NOV STAR Anhydride pipe data sheet (Wichita manufacturing-location code); Oklahoma DEQ draft 2025 construction permit; Cooper Standard-hosted 2023 operator/address certificate. Exact URLs and short quotes are in evidence.json and selected witness files. Full fetched raw sources, hashes and pre-pass backups live in controller storage `persist/integrator-backlog-4/`. fetch.py is resumable; raw content is not committed, preventing personal-contact spill from source pages. No more than 6 primary fetch URLs per entity. Cache needs controller storage to rerun the quote check.

The Reiser certificate establishes historical operator/address; expired certification does not imply a plant closure or current certification. The Kingspan draft permit is prospective and filed under Kingspan USA, not recast as the exact corporate legal name. Its evidence explicitly banks planned scope with supports_C; current tags remain blank. NOV fittings language is not used to invent a plant-wide process. Silgan PCR is directly tied to Thomaston. Exhibit 21 lists downstream subsidiaries; it cannot establish an upstream parent of either public registrant, and no parent claim is fabricated. Item 2 establishes PPG headquarters; Sherwin cover establishes Cleveland principal offices. No subsidiary rows or relationships added.

Named checks:
- `python3 tasks/integrator-backlog-4-2026-11-16/check.py`: verifies all 15 input proposals against 15 persisted evidence rows; exact raw quote presence; unique reserved IDs; 9 case dispositions; existing resolutions; material cells. Rejects three injected defects (input loss, duplicate ID, fabricated quote).
- `python3 tasks/integrator-backlog-4-2026-11-16/build.py --apply`: second run reports 0 changed operations.
- `python3 scripts/validate.py`: 0 errors, existing warnings.
- `python3 scripts/check_row_loss.py --base origin/main`: PASS, no keyed row removed.
- `python3 scripts/export_vocab.py --check`: PASS, vocab current.

Proposed follow-ups: none outside fixed manifest. H-TARKETT excluded. No council call or cross-family completion claim: contract routes review through controller. No issue closed. Not checked: legal identity underlying existing HEXPOL fold; current Huron street; actual Kingspan commissioning; Silgan/NOV plant processes; unrelated records. Local estate catalogue is incomplete on Mac (Windows Documents inventory absent); this is a platform gap, not evidence of absence.
