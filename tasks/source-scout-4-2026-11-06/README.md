# L5 source scout4 — atlas-L5-scout-3, 2026-11-06

Controller06:30 continuation, NEW branch agent/codex/source-scout-4 from origin/main9489b60. Packet only: no data/ writes, IDs, membership edges, scope/ring/vocabulary decisions or tracker status changes. PR131 remains separate. First user: Atlas controller/PIC researcher, source prioritization by2026-11-13; non-use then is a controller review finding, not a new commitment.

Acceptance: route and terms checked for all5 sources; terms/auth/raw-access gates stop extraction and remain explicitly unmeasured. For usable ACMA/CDR routes: precise discovery-frame units/filter,20 unique seeded sample units, all-shard dedupe with unknown fields disclosed, legal row verdicts/settling facts, verified-new yield with Wilson interval from CSV, independent count checks and executable negative controls. Keep vs corroboration vs closed is a source-route verdict, never an organization operating-status decision. No closure REJECTs or Form5500 closure decisions.

| Source | Source-route verdict | Frame/sample and measured new yield | Hold |
|---|---|---|---|
| Association of Plastic Recyclers | CLOSED automated extraction | NOT MEASURED, terms stop | Prior written permission |
| Vinyl Institute | CLOSED public roster extraction | NOT MEASURED, raw-verified publication restriction | Reuse right |
| ACMA composites public directory | CORROBORATION_ONLY |98 US/nonoptout Manufacturer listings;0/20 new organization leads, Wilson95%0–16.11% |4 identity/scope uncertainties, publication rights |
| EPA2024 CDR | CORROBORATION_ONLY |290 core-NAICS TSCA site IDs;0/20 new sites established current, Wilson95%0–16.11% |15 site/operator/current-process uncertainties; report vintage2023 |
| SAM.gov PUBLIC entity extract | CORROBORATION_ONLY, credential/route held | NOT MEASURED; terms/route only as assigned | Read Public key and successful authenticated extract |

CDR20:5DUPLICATE_OF held sites /15STILL_UNCERTAIN. ACMA20:16DUPLICATE_OF held organizations /4STILL_UNCERTAIN. No REJECT, no VERIFIED-new. Zero current verified-new under the documented bulk-evidence/one-homepage budget does not mean source absence or ultimate discovery yield zero. Association directory category and CDR NAICS/import records do not establish current polymer operations. Sample CIs are descriptive at their different listing/site-ID grains and must not be pooled into a parent-level estimate.

## Checks and reproducibility

`python3 tasks/source-scout-4-2026-11-06/check.py` is the named offline check: recomputes every yield/CI from the40 committed sample rows; verifies duplicate endpoints, unknown metrics for gates, unique source IDs, CDR290 IDs/2924row yield, ACMA98 slice, known matcher/NAICS/optout answers and intentional duplicate/boundary defects. `--write` refreshes metrics.json, default rejects drift.

`python3 tasks/source-scout-4-2026-11-06/fetch_routes.py` re-probes9 bounded public URLs and writes routes.csv status/hash metadata. Non200 is a recorded route observation, never an empty dataset. Expected usable APR terms/ACMA/EPA routes must succeed for the offline gate; Vinyl uses a full Chrome UA after generic Mozilla406; SAM anonymous404 remains explicit. Raw pages/JSON/downloads remain under /tmp; no full directory/contact payload is committed.

`epa-cdr/build.py` re-builds frame/sample from the strict source CSV. `acma/scout.py` re-fetches company homepages from a locally downloaded public directory JSON and reproduces seeded sample20; raw directory acquisition URL is in its README. All script output targets stay in this packet; canonical tables are read-only. A changed upstream roster/release must be investigated before changing pinned counts. No dependencies added or scripts/ changed, so no unrelated full-suite rerun required.

Checks: named offline check PASS; source count reconciliation PASS; six raw terms excerpts PASS (terms_checks.csv, house evidence-repair word normalizer); `python3 scripts/validate.py` PASS0errors. Current-main row-loss guard PASS; CDR builder second run byte-identical; ACMA live252/98/seeded20 check with three real category known answers PASS. Grok/xAI APPROVE39849c0,0findings; Codex3 review pending. Clerk pairs06:25: new request Codex3 thr_jukpm97t9c + Grok3 thr_4g4uwqjxjv. Clerk-only --mode queue exception supersedes the general never-queue contract.

## Ledger / holds

Controller notified of assignment/source gates; no peer ownership agreements. Estate search was partial because the Windows Documents inventory and corpus are absent on this Mac; no private source copied. Proposed source-ledger/IDEAS changes are in docs_proposals.md, keeping this main-based continuation independent of PR131's edits to those shared files.

PR131 review correction is separate: Codex exposed51 as a hidden location intersection; that PR now reports79 broad held-PIC18 footprint patent candidates and51 explicitly flagged intersection, with current-main row-loss guard passing. No PR131 files or old results are bundled into this continuation.

## Independent refutation

Grok/xAI APPROVE,0findings,39849c0: independent oracle, validator, row-loss, live ACMA252/98/seed20, CDRbyte-identical replay and independent SQL counts, all21 held duplicate endpoints and source terms/gates checked. Report: controller review ledger reviews/162-clerk-grok-3.md. Following that report the lane independently raw-fetched Vinyl terms with the working full Chrome UA and replaced the raw-access hold with the publication-permission hold; counts, samples and source standings unchanged. Codex/OpenAI review pending; PR remains draft.

## Codex review correction

Codex/OpenAI REFUTE598d910 identified one ACMA RL Industries discovery snippet containing generic business phone/fax/email text, outside an appropriate schema field. Removed that entire non-evidentiary excerpt, and the generator now omits excerpts containing contact text. The oracle tests clean materials text plus email/PH/FX/bare-phone fixtures, checks every committed ACMA snippet, and detects the original defect. All40sample identities/verdicts, counts, source standings and metrics remain unchanged. Targeted Codex re-review pending; Grok APPROVE39849c0 remains recorded.

Correction checks: named oracle PASS; restoring the original RL excerpt makes it fail with "contact data in discovery excerpt" (expected negative control); clean snapshot passes. Fresh RL homepage HTTP200 passed the updated generator contact-omission check. CSV comparison to reviewed packet shows exactly one scope_quote changed, with every identity/verdict/count unchanged. Merged current main2742438c3c; validator0errors and row-loss guard --base origin/main PASS; data/scripts/docs net diff0.

Codex/OpenAI APPROVE644f32b, targeted re-review,0outstanding findings (supersedes598d910 REFUTE). Independent CSV comparison confirms only the RL scope_quote changed210characters to empty; all40identities/verdicts/other fields and metrics/counts/routes/terms unchanged. Fresh RL HTTP200 reproduces contact omission; seven contact fixtures omitted and clean materials preserved. Reinjecting the original excerpt into an isolated archive makes the actual oracle fail; clean restoration, validator0 and row-loss pass. Review report: controller ledger reviews/162-clerk-codex-1.md. Full source/terms/CDR research and full pytest not repeated. Grok targeted correction review remains pending; previous39849c0 approval retained historically, PR draft/noDone.

Grok/xAI APPROVE420bf3bd660e, targeted correction re-review,0findings (supersedes historical39849c09b348 approval). Independently confirmed the correction changes only one sample cell, all other sample identities/verdicts and metrics unchanged; named oracle and original-excerpt reinjection control pass; fresh RL source reproduces contact omission and clean materials fixture survives. Report: controller review ledger reviews/162-clerk-grok-1.md. Grok did not repeat validator/row-loss, bulk extraction or full-source research. Together with Codex APPROVE644f32b, both families approve the contact correction; earlier pending-review statements above are historical. Remains draft per reviewer instruction; controller owns integration/status.
