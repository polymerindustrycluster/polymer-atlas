# L3 STRONG wave — Missouri, South Carolina, Louisiana

Scope: 36 lead-fusion STRONG establishment clusters, MO 15 / SC 14 / LA 7. `verdicts.csv` is exhaustive, not a sampling frame.
The original recipe is `../mi-strong-wave-2026-11-04/`; the binding lane acceptance criteria are in `LANE_BRIEF.md`.

Sources: public operator pages selected in `research.py`, re-fetched in `rawcheck.csv`; OSHA ITA CY2025 establishments,
OSHA inspection records and DOL EFAST2 sponsor packets already held under tasks/. ECHO/FRS identifiers are notes only;
no FRS REST requests were made (shared-IP restriction from controller 2026-11-06, recorded on BOARD).

`dedupe.json` records atlas.py's four steps, including domain, normalized legal/trade names, street and successor chains.
Street matching additionally ignores mailing-city and ZIP variations. JM Eagle ORG-002260 is tombstoned: Columbia attaches
to survivor ORG-002261. Insulfab uses held ORG-006173; Nike uses ORG-003555; Yokohama TWS uses ORG-001336.
The Aurora substring in Polyply notes is a lead, not proof of common legal identity; the Aurora cases remain held.
No organizations were merged, no ownership/status changes were applied, and no inclusion-log borderline create was made.

## Build and checks

Before applying: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py`, then `adjudicate.py` in that directory.
The three known published witnesses (TG Missouri, Manchester Packaging, Insulfab) passed 3/3; appending a nonexistent token
to each quote failed 3/3. Script/style content is excluded. Failed routes are not evidence of absence.

Apply each state: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/build.py --state MO --apply` (then SC, LA).
IDs are deterministic input-index offsets in the reserved block. `append_sorted` is used for every append. Reapplication
asserts exact equality for held IDs instead of overwriting evidence. On fresh main, re-run adjudication and inspect new
dedupe hits before re-running the builder; do not merge CSV conflicts by hand.

Named checks: `python3 scripts/validate.py`; `python3 tasks/strong-waves-mo-sc-la-2026-11-06/check.py`.
`check.py` injects three missing/duplicate census defects and requires all three to fail. It also checks exact creates,
unique IDs and the per-state NAICS 326 strict-site/QCEW rise using `scripts/build_qcew_denominators.py::atlas_numerators`.
Denominator = QCEW 2023 private establishments, NAICS 326: MO 368, SC 406, LA 117; held official-source denominator file.
A ratio is not matched establishment coverage. No QCEW downloads or denominator changes are needed.

## Holds

`holds.csv` is the holds table: one cluster and named settling fact per row. Fetch availability holds remain explicit.
Agfa is held pending dated closure outcome + address-matched EFAST2, never rejected solely on a closure headline.
PIDC is excluded under owner B-SCOPE (2026-11-04), inorganic alumina output; deciding regulator source is in its verdict.
County/HQ are not inferred from postal city or plant location. Blank fields remain honest unknowns.

## Pass journal and reviews

Application counts, before/after ratios and independent review verdicts are appended below before PR publication.

- Missouri application: 7 new organizations (tier C), 9 new establishments {'C': 1, 'B': 8}; 98 evidence observations. `validate.py`: zero errors. Builder replay: passed.
- South Carolina application: 4 new organizations (tier C), 6 new establishments (tier B); 64 evidence observations; 2 held-parent alias updates. `validate.py`: zero errors. Builder replay: passed.
- Louisiana application: 4 new organizations (tier C), 4 new establishments (tier B); 48 evidence observations. `validate.py`: zero errors. Builder replay: passed.

Final census: {'STILL_UNCERTAIN': 16, 'VERIFIED': 19, 'REJECT': 1} across the 36 STRONG establishment clusters. Creates: 15 organizations (C), 19 establishments (18 B / 1 C), 210 evidence rows; 4 held-parent alias additions.

| State | QCEW 2023 NAICS 326 private establishments | Atlas strict before | Atlas strict after | Strict/QCEW before → after |
|---|---:|---:|---:|---:|
| MO | 368 | 37 | 43 | 10.05% → 11.68% |
| SC | 406 | 49 | 52 | 12.07% → 12.81% |
| LA | 117 | 6 | 7 | 5.13% → 5.98% |

`check.py`: PASS, exact 36/36 verdict census, 3/3 injected census defects caught, 19 applied sites, unique IDs, T3 rises in all states. Prior-row comparison against pre-pass commit: every old evidence row preserved; only four old organization trade_names fields gained aliases. All three builder replays are byte-identical across 16 changed data files.

### Held clusters and settling facts

| Cluster | Settling fact |
|---|---|
| LF-MO-00006 | Need a polymer formulation or captive shaping witness; contract filling alone does not settle scope. |
| LF-MO-00018 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00053 | Need polymer-binder formulation at Clifton Avenue; broad chemical blending and distribution does not settle site scope. |
| LF-MO-00120 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00165 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00289 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00047 | Need polymer-specific production or qualifying polymer value-chain focus at Rock Hill; metal finishing alone is insufficient. |
| LF-SC-00129 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00198 | Closure reporting found; need dated primary outcome and address-matched EFAST2 check before any closure REJECT. No active create. |
| LF-SC-00206 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00302 | Need Laurens foam-control product binder/composition; silicone/polymer formulation versus nonpolymer defoamer not settled. |
| LF-SC-00326 | Need primary operator identity linking Curd Enterprises to Multiplastics and current manufacturing at 476 Long Point Road. |
| LF-SC-00358 | Need captive polymer processing or site-grain Ring 4 two-of-three test; chlorination equipment alone is insufficient. |
| LF-LA-00029 | Need dedicated polymer line or polymer-specific value-chain witness; sulfuric acid regeneration alone is insufficient. |
| LF-LA-00183 | Need current operator/site identity after Berry/Amcor transaction, and plant-specific polymer scope at 4611 Central Avenue. |
| LF-LA-00234 | Precursor-only Ring 3 precedent applies, but dated current operating outcome and operator after restructuring must be settled before active create. |

Controller 2026-11-06 authorized merge of origin/main instead of rebase to preserve the two pre-existing CRLF-dirty federal-frame files; this supersedes the lane rebase-only route for this integration. Controller also authorized publishing draft for queued refute-clerk review while saturated council calls remain pending; two-family approval is still required. Reviews pending at this checkpoint.
