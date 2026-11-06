# L6 CA CORROBORATED, 2026-11-06

Authorized by controller thr_9i2c6byhcz, lane atlas-L6-corr-ca-tx. CA first; TX requires a separate PR. First user: campaign integrator reviewing this PR on 2026-11-06; non-use finding date 2026-11-13. Controller owns status.

Acceptance: `python3 scripts/validate.py` passes with zero errors; exactly one verdict for every selected cluster; builder rerun is byte-identical; 20 randomized blind federal-source rechecks; before/after strict NAICS 326 establishment share of QCEW, using `scripts/build_qcew_denominators.py` definitions. Two independent deep refutes must approve before submission.

Selection: explicit core prefixes 3252/3261/3262/325991 first, score descending, cluster_id ascending. Initial 30 extended to 40 contiguous ranked clusters to furnish 20 create candidates for the required blind check after source/identity holds. This changes batch size, not the criteria or any rejected interpretation. Universe: 262 CA CORROBORATED clusters; this pass works 40, below the 150 maximum. `input.csv` freezes the selection; `verdicts.csv` contains 20 VERIFIED and 20 STILL_UNCERTAIN establishment verdicts. No closure or no-establishment REJECTs.

Proposed application: 11 new parent organizations at C in the residual US shard (HQ unestablished, not copied from a plant); 20 CA establishments, 16 C and 4 B; 161 appended evidence rows. No existing canonical record is changed. IDs use the controller-reserved ORG-010000+, SITE-014000+, EVD-180000+ blocks, superseding general sequential allocation for this lane. `allocations.csv` is the ID journal. Branch history is the pre-pass backup. The builder refuses collisions and reapplies an identical packet as a no-op.

Sources: local government OSHA ITA CY2025 and OSHA inspection extracts. A resolvable core manufacturing classification supports provisional C under the STRONG-wave convention; it populates no inferred capability. B additionally requires a raw own-page witness. Raw quotes are checked with curl browser UA and Jina fallback using the house `W` matcher from evidence-repair-2/prep.py; `rawcheck.csv` records short quotes and content hashes. The task's ownership-status-2 rawcheck path does not exist in this checkout. No FRS REST or licensed/private sources used. ECHO/FRS and additional same-address `QUEUE_MULTISOURCE.csv` federal identifiers are notes only, never registry evidence or registry links. No parent-level Form5500 employee count is assigned to a site.

Dedupe: `atlas.py dedupe-check` domain, normalized name, street/locality, trade names and notes across all shards; results in `dedupe.json`. Known-answer records: ADS domain -> ORG-000651; Graham -> ORG-001403; CA Mercury -> ORG-007413, not OH Mercury ORG-000431. House matcher has 3 positive and 2 injected negative checks in research.py. Trelleborg multiple domain hits are held. Generic Madera/Modesto/Corona aliases are resolved with ITA company_name, not guessed from the plant name.

Source discrepancy: Dart cluster includes an older OSHA witness at 150 **North** Maple; excluded explicitly. Only the matching **South** Maple witness supports the create. Cytec's latest inspection carries peripheral 325998; held pending polymer-specific scope rather than choosing its older core code. Current status remains unknown; a historic inspection is not an affirmative operating-status finding. County remains empty because the cluster county is orientation-only. No process/material tags are inferred from a code.

## Holds

The authoritative settling facts are the 20 STILL_UNCERTAIN rows in verdicts.csv. Holds include Cepheid/Hi-Temp site scope; ECHO+employer-Form5500-only establishments without a resolvable plant source; Trelleborg operator; Parco ZIP/Datwyler operator; Providien/Amphenol and Kruger/Alentra parent identity; Cytec's peripheral latest code; Oroville WARN outcome; and current polymer-specific operators at the remaining unverified candidates. No scope, vocabulary, parent correction, closure or ring exception is self-ruled. Failed routes mean availability only. The two pre-existing CRLF-dirty federal-frame files remain untouched.

## Checks and reviews

Pending final run and independent refute. The 20-row shuffled blind input omits lane verdict/tier/link decisions. Reviewers must independently check source identity, physical address, manufacturing scope, and parent linkage, then reconcile against allocations.

Inherited government packet authority was relayed by L7 (thr_88ej2yjjna) from controller: ITA/OSHA/ECHO packet vintage 2026-11-01 is admissible without a fresh bulk download. ITA citations include establishment_ID, submission date and the CY2025 bulk URL, whose `/sites/default/largefiles/` path was verified from the live OSHA download page on 2026-11-06. Thirteen ITA site employee bands are carried with size_band evidence; no employer-plan counts are used.

Named check results (2026-11-06): `python3 scripts/validate.py` zero errors / OK; `python3 tasks/corroborated-ca-tx-2026-11-06/check.py` PASS (40 unique verdicts,20 source rows, replay bytes unchanged, strict32675→94/1306); `python3 scripts/shard_io.py` PASS. Duplicate-verdict injection41rows/40IDs failed as intended. Existing canonical rows preserved by ID comparison to HEAD; two pre-existing unsorted CA evidence rows move in sorted output without value changes.

Controller 05:55 BOARD instruction supersedes original council-only/push-after-refute sequence: draft PR may be pushed before reviews, then dedicated Codex/Grok clerks review it. A first council Codex call is still live; Grok did not launch because shared HARD40deep/600s refused it. Refusal is not approval. Assigned clerks are thr_mdr3gn2xmm and thr_f2fcbx6tq8.
