# Ohio C/U streets — L2 optional round 4, 2026-11-06

Controller explicitly assigned C/U-tier blank Ohio streets after round3, using ITA/FRS and inherited ITA exception. New branch agent/codex/oh-street-address-cu off currentmain; exact commit in BASE_COMMIT. Acceptance frozen BEFORE fetch:819 active C/U Ohio blank-street site rows;108have site-keyed FRS link and nonblank ZIP. Work first40 of108 by immutable siteID, retaining all their source links;779broad-cohort rows and68otherFRS-knownZIP candidates explicitly unworked. IDs153000–153818 reserved by819-cohort position, within lane OH150000–154999, disjoint originalOH/448A/Bframe/PA. Only these40rows may receive a fill.

Sources in priority: usable already-held address evidence (inspect, no street inferred from city-only row), freshly fetched exact site-keyed FRS record at12-second spacing, then exact/strong inherited CY2025 ITA source if necessary. FRS city+ZIP5+county+state must agree; links must keep Atlas operator ID. PO-box/nonphysical/contradictory FRS/ITA/notes/ZIP/county cases held, never geocorrected. Registry address supports_C; ITA government_filing supports_A; both allowed on unchanged C/U record tiers. Existing notes are LEADS only. No entity/status/ring/tier/county/county_source/ZIP/registry/qualifier changes; street_address/sources plus append-only address evidence only.

Inherited ITA rule explicitly granted by controller earlier: original2026-11-01 observation, officialCY2025CSV URL, establishment_ID/date_submitted/full supplied-extract SHA-256 in notes; no claim of fresh bulk CSV download. Direct download403/Jina401 availability never negative evidence. No current entity creates/dedupe merges; no tracker edits. First user Atlas integrator, review2026-11-06, non-use finding2026-11-13.

Known gate BEFORE fetching40: reuse committed first-pass FRS helper, with three live literal known answers and wrong-city/ZIP/county/PO-box mutations. Fresh JSON retained in raw/, metadata/failures every request; no concurrent FRS fetches. New nontrivial builder must pass exact-field/write-boundary/idempotence and fail-before-write cross-shardID/changed-geography/street injections; validate0errors; seeded30freshrefetch-or-census audit; inherited ITA transcription vs extract plus separate independent freshcorroboration rates per controller ruling. Independent Codex4/Grok4 refutes before readiness.


Final bounded pass: **40selected active Ohio C/U blank-site rows =24VERIFIED fills +16STILL_UNCERTAIN holds**. Other779 of819 broadcohort unworked;68 of108 knownZIP+FRS eligible candidates unworked.41site-keyed registry requests (one selected site has two): **40OK +1UNAVAILABLE**. Existing address evidence on these40rows:0, so no reusable witness.6exact/strong inherited ITA matching rows transcribed/checked against banked extract,0transcription drift; their city/ZIP conflicts block fills where present. **All24 admitted evidence rows are fresh FRS registry/address/supports_C**, no government_filing observation added. Record tiers unchanged **C22/U2**. Sparse evidence IDsEVD-153120–153334; full819-cohort positions reserved153000–153818. No ID reuse.

Active Ohio coverage on this main baseline **286/1883(15.19%)→310/1883(16.46%)**; excludes pending independentA/Bpasses156(19) and171(38). Their targets are disjoint by original record tier; no prospective combined figure is claimed as already merged. Only street_address/sources change plus24append-only evidence rows; no entity creates/deletes/merges, no inclusion_log calls, no county/county_source/ZIP/status/tier/ring/registry/qualifier changes. Every source ID resolves in kept raw JSON; county/state/city/ZIP agreement explicitly checked, coordinates unused.

Fresh cited-source audit: **24/24 accepted fills,0address/transcription errors,0uncheckable** after two bounded retries. Initial census had22matches and2HTTP22unavailable; strict registry gate correctly FAILED (audit_transport_attempt1.csv). retry_audit.py re-fetched onlythose2 at12secspacing, bothmatch (audit_retry_log.csv), then full24-row gatePASS. No failed request supplies evidence/absence/status. A preliminary controller update overstated completion before the finalassert was read; corrected immediately in BOARD and before any canonicalCUwrite. Audit columns now say fresh_source_match: this repeats each cited FRS witness; it does not add an independent second source or promote a tier. Original failure-history header retained as observed.

Named checks (repo root):

- python3 tasks/oh-street-address-cu-2026-11-06/fetch.py --known:3live literal answers PASS; city/ZIP/county/PO-box mutations rejected, before41source requests.
- python3 tasks/oh-street-address-cu-2026-11-06/check.py: **PASS24fills**, all24auditedIDs bound to24admitted witnesses, field-boundary and byte-idempotent replay; street/ZIP/tier/status/foreign-shardID mutation cases reject BEFORE canonical writes. Legacy street-vs-county-annotation boundary fixture passes; annotations are not street components. Written ordinals/dotted diagonals deliberately remain distinct and are held pending adjudication.
- python3 tasks/oh-street-address-cu-2026-11-06/audit.py: full24census (under30); first run availability gatefailed; bounded retry_audit.py final gatePASS24/24,0errors. Kept every successful audit JSON in audit_raw/.
- python3 scripts/validate.py: **OK — validation passed,0errors**.
- Fresh-main keyed comparison: every site/evidence key preserved, every legacy evidence row unchanged; exactly24site street/source edits+24EVDappends.
- git diff --check: PASS. No scripts/ files changed.

Holds (unit:selected active Ohio C/U blank site rows, reasons overlap):

| Filter | Rows | Settling fact |
|---|---:|---|
| No admissible witness after unavailable FRS | 1 | Successful site-keyed source with physical street/locality |
| Notes street disagreement/unresolved spelling | 5 | Dated street/suite/direction adjudication |
| ITA city/ZIP conflict or missing | 5 | Reconcile primary establishment locality without changing it here |
| FRS county conflict/missing | 4 | Address-exact county/source linkage adjudication |
| FRS ZIP conflict/missing | 2 | Confirm source linkage and recorded ZIP |
| FRS city conflict | 1 | Confirm physical locality/source linkage |

All16hold reasons and all40outcomes in holds.csv/verdicts.csv; unworked779frame rows selected=no, not described as investigated. Pre-pass/current hashes and exactIDs in journal.json; backups local/ignored. Controller originaldelegation andoptionalR4claim authorize application. Codex4/Grok4 refutes pending before readiness; neither correctsourceclassnorpassingvalidator establishes physical use without the stated source gate.

Independent review receipt: **Codex(OpenAI), clerk1, APPROVEa9af228,0findings.** Independently reconstructed819broad/108eligible/first40cohort and24fills16holds, all24 literal FRS streets/registry/locality/counties and held aliases, global IDs/exactslots, current source-class ceiling and unchangedC22/U2tiers. Fresh3known plus negative cases pass; independently repeated full24-source paced census24/24PASS,0errors0uncheckable,no retries. Verified original22+2transport failures and bounded two-retry cure; same-source verification is not independent corroboration. Native validator/rowloss/namedcheck and all220CSV exact-base/second replay pass; exact lateEVD153334 wrong-shard and rawRegistryID mutations reject before writes. Report: controller reviews/192-clerk-codex-1.md and reviews/192-clerk-codex-1/. Limits: no fullpytest, second-source/current-operation/postal-deliverability claim;16holds/779unworked unresolved. This README-only receipt changes no data/code/input/source. Grok remains pending; draft retained.
