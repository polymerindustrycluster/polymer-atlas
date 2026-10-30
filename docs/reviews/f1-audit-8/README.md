# Blind audit 8 — TRI-era creations

**Status: authoritative map v2 validated; 65-record sample frozen 2026-10-30 22:59:07 UTC. Five blind verification batches are in progress. No audit error rates are claimed yet.**

Draft PR: https://github.com/polymerindustrycluster/polymer-atlas/pull/9

## Frozen baseline

- Main pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`, 2026-10-30.
- Task F1 only. Independent clone and branch `agent/codex/tri-blind-audit-8`.
- Canonical data changes: **0**. Allocated IDs: **0**. No merge or main push.
- Pinned `scripts/validate.py`: **PASS**. Pinned SQLite build: **PASS** (logs alongside this report).
- Main rechecked 2026-10-30 21:37 UTC: unchanged.

## Resolved preparation blockers and frozen design

See `RESUMPTION.md` for the explicit metadata-pin transition and map-duplicate diagnostic, and `SAMPLING_STATUS.md` for the complete sampling method. Original data pin remains unchanged. Corrected metadata pin is `bf7857a7826ba62cdcf67af3ba718c3d5a9b32be`; no canonical data changed.

The creation frame is **2,199 unique records: 682 organizations + 1,517 sites**. The author's original reconstruction was correct. Map v1 counted five watch-marker rows twice; the owner confirmed the error and published v2. Excluding 227 NOT_TRI records yields **1,972 TRI-eligible creations**. P0 has no creations and no synthetic stratum.

The fixed-seed stratified draw selected **65 distinct records**, now assigned to five organization-grouped batches of 13 for independent public-source verification. `DRAW_MANIFEST.json` freezes input/output hashes. Existing evidence/notes, creation tiers and wave classes remain sealed from verifiers until every independent verdict is frozen. Findings, comparison grades and rates will be added only afterward.

## Historical comparison reserved until measured

User/task supplied baselines: audit 6, **0/37 creation errors** and **12/37 field errors**; audit 7, **58/65 agreement**. These are different audit populations/designs and are not evidence about the audit-8 sample. No trend or quality-improvement conclusion is possible yet.
