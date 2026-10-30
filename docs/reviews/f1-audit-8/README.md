# Blind audit 8 — TRI-era creations

**Status: sample not drawn; required wave-class mapping unavailable. No audit verdicts or error rates are claimed.**

Draft PR: https://github.com/polymerindustrycluster/polymer-atlas/pull/9

## Frozen baseline

- Main pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`, 2026-10-30.
- Task F1 only. Independent clone and branch `agent/codex/tri-blind-audit-8`.
- Canonical data changes: **0**. Allocated IDs: **0**. No merge or main push.
- Pinned `scripts/validate.py`: **PASS**. Pinned SQLite build: **PASS** (logs alongside this report).
- Main rechecked 2026-10-30 21:37 UTC: unchanged.

## Sampling blocker (not an audit finding)

Independent creation-history extraction establishes 2,199 organization/site records first created across integration passes 20–25: **682 organization records and 1,517 site records**. This is the broad pass-era frame, not yet the final TRI-origin audit population: pass 20 also includes SC and Q01/Q02 work. The public repository does not supply the authoritative P0–P4 wave-class mapping required by F1. P001–P036 packet numbers must not be substituted for P0–P4 wave classes. Neither pass number nor present-day record tier is a valid undocumented substitute for creation wave/tier.

The requested design is a reproducible stratified random sample of approximately 65 records, stratified by **creation tier × P0–P4 wave class**, with extra selection probability for Tier C and P4 single-facility organizations. Drawing against a pass-only proxy would not satisfy that design. The sample therefore remains unselected; source notes and record evidence remain unseen by the verifier. An independent sampler owns the sealed metadata. The verifier's protocol was frozen before any draw in `PROTOCOL.md`.

**Required input:** an accessible authoritative worklist/export mapping the relevant pass 20–25 creations (or resolvable facility/organization identities) to P0, P1, P2, P3, P4, including the TRI-origin eligibility needed to separate mixed pass-20 records. The parent task requested this input on 2026-10-30 at approximately 21:35 UTC. A supplied backup exceeded the connector's 256 MiB limit; that refusal is not bypassed by this lane.

Once supplied, the independent sampler will seal a population manifest and draw, release only identity search keys, and the verifier will complete/freeze the entire sample before inspecting recorded evidence. This draft will then be updated with per-record verdicts, named field/creation errors, unresolved cases, per-stratum denominators and rates, and corrections proposed to the integrator.

## Historical comparison reserved until measured

User/task supplied baselines: audit 6, **0/37 creation errors** and **12/37 field errors**; audit 7, **58/65 agreement**. These are different audit populations/designs and are not evidence about the undrawn audit-8 sample. No trend or quality-improvement conclusion is possible yet.
