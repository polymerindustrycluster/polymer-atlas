# L3 CORROBORATED continuation — MO/SC

All143 CORROBORATED establishment clusters in Missouri63 and South Carolina80 are screened. Final verdicts:10 VERIFIED
(4MO/6SC),132 STILL_UNCERTAIN (58MO/74SC),1 DUPLICATE_OF (MO). This is an exhaustive two-state census, not a sample.
No organizations are created. LA42 clusters are the next separate PR under the controller's ≤150-cluster cap.

Every create is provisional tier C, current operating_status unknown. The witness is the employer's OSHA ITA CY2025
establishment filing (public raw extract already banked under tasks/osha-ita-2026-11-01), packet observed2026-11-01,
reviewed2026-11-06. We do not claim a fresh government download, own-site witness, or present-day operation. Sources resolve
to the official CY2025 URL plus establishment_ID. No ECHO/FRS identifiers enter registry links. County stays unset.

Reuses the L11 MI/IL CORROBORATED prep/build/check pattern from PR138 and the house atlas/shard_io functions. Acceptance,
first user/use date and ID allocations are in LANE_BRIEF.md. Controller06:40 assigned EVD300000–309999; no old gaps reused.
Sites are allocated by frozen input index in SITE012100+, evidence300000+20*index. The20-row spacing is a fixed allocation,
not permission to fill the unused gaps. All IDs are checked across every shard before writes.

## Identity and scope gates

A filed company_name must independently normalize to one active, surviving held organization legal/trade name. A plant
label or parent-group variant alone is insufficient. Exact street/state and every linked ITA NAICS must agree. All ITA
records must be reliable. Explicit polymer manufacturing descriptions and primary scope codes are required; paint-remover
and distribution-only records do not become plants. Names/notes/street dedupe is recorded in dedupe.json, against all shards.
Existing street/state sites and same-parent/locality blank-street sites block creates.

Known-answer operator tests passed for Plastipak Packaging, Nike IHM and Hydrite Chemical. Injecting an ambiguous alias
produced two operators and was rejected. These tests preceded use of the name matcher; no new network fetcher is involved.

Four held organization trade_names fields gain actual filed company_name variants. City/unit establishment labels remain
in site notes, not parent aliases. Each registrant identity observation cites its actual government filing (supports_A:
primary employer-reported registrant identity under SCHEMA4.13). That strength is identity-local; it changes no held tier
or operating claim. All70 site observations remain supports_C;10 new plants remain C/unknown.

## Holds

The full holds table is verdicts.csv:132 STILL_UNCERTAIN rows with a named settling fact. In particular:

| Cluster | Settling fact |
|---|---|
| LF-MO-00442 | Legal/operator continuity between Festus lamp-shade filing and held Ohio Crown Plastics UHMW maker |
| LF-SC-00014 | Actual function of Duncan Innovation: production plant versus R&D/innovation center |
| LF-SC-00285 | Polymer-binder activity witness; paint and varnish remover alone does not establish polymer formulation |
| LF-SC-00267 | Polymer warehouse/site function witness; wholesale NAICS does not establish a manufacturing plant |
| Alltrista/Jadex, CCP/American Plastics and other name-only variant cases | Primary confirmation of filed company versus held operator, rather than inheriting parent/division identity |

No scope or ownership ruling is self-made; no closure/status change or merge is applied. Source absence is not closure.
No borderline inclusion-log create; unsettled cases are held. DUPLICATE_OF terminates at a held site.

## Checks

`python3 tasks/corroborated-mo-sc-2026-11-06/prep.py` reproduces input/verdict/dedupe/known answers from canonical data.
`python3 tasks/corroborated-mo-sc-2026-11-06/build.py --state MO --apply` (then SC) applies via append_sorted.
`python3 tasks/corroborated-mo-sc-2026-11-06/check.py --negative-controls` binds all10 sites and70 site evidence rows to
actual ITA values, exact143 census, reserved/global IDs, and a wrong-shard ID collision that must fail before any writes.
`python3 scripts/validate.py` must have0errors. All existing canonical rows are preserved except the four alias additions.
Source-class/tier gates do not require weakening any held organization.

T3 uses scripts/build_qcew_denominators.py::atlas_numerators, unit NAICS326 US establishments with active/unknown status and
A/B/C tier; denominator QCEW2023 private NAICS326 establishments. Baseline bdb8b98: MO37/368, SC49/406. Ratios are counts,
not matched coverage. Final deltas must equal the actual created-site NAICS326 subset (ring1 is not identical to NAICS326).

On moving main, take main's data, replay the builder and recompute before/after; do not hand-merge CSV conflicts.
No shared scripts changed, so scripts pytest is not required. Final checks and independent two-family refutes below.

- Missouri application:4 new C/unknown establishments,31 evidence observations(28 site +3 registrant identity),0 new organizations. validate.py0errors.

- South Carolina application:6 C/unknown establishments,43 evidence observations(42 site+1 registrant identity),0 organizations. Final74 evidence observations;4 aliases on held organizations, all prior canonical rows otherwise unchanged.
- Final checks: validator0errors; check.py PASS143/143 exact census,3 census mutations caught,10 C sites/74 evidence source-bound; wrong-shard SITE collision rejected before writes; both-state replay byte-identical. Full10-create census supplied for independent review in blind-full-census.csv (fewer than20 creates).

| State | Strict NAICS326 establishments before | After | QCEW2023 private326 establishments | Count ratio before → after |
|---|---:|---:|---:|---:|
| MO | 37 | 41 | 368 | 10.05% → 11.14% |
| SC | 49 | 54 | 406 | 12.07% → 13.30% |

LA reuse exposed an order-dependent global-ID dictionary-collapse defect. The builder now asserts SITE and EVD input-ID uniqueness before constructing either lookup; both wrong-shard duplicate types are injected and must fail before any data write. This supersedes the earlier SITE-only negative-control coverage. No duplicate was applied to canonical data.

Updated-main integration: conflicts resolved with main data then both-state builder replay, no hand CSV merges. Baseline is now recorded in baseline.json (includes mergedSTRONG PR141); original bdb8b98 ratios above are the earlier checkpoint, superseded for this PR's final integration.
- MO: strict326 43→47/368, 11.68%→12.77%; this batch still adds 4 NAICS326 sites.
- SC: strict326 52→57/406, 12.81%→14.04%; this batch still adds 5 NAICS326 sites.
Updated main boundary comparison PASS: every original record/evidence retained; only four registrant alias fields gain values. Replay byte-identical. validate0errors, source/census/T3 checks PASS, both SITE and EVD cross-shard defect injections fail before writes.
