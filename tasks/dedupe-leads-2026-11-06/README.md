# Dedupe leads adjudication — 2026-11-06

Twelve frozen candidate pairs were adjudicated: **two VERIFIED / DISTINCT and ten STILL_UNCERTAIN / LINK_FLAG**. No dated witness establishes both same legal entity and same establishment for any site fold. No organization merge or registry re-key is admitted. `flags.csv` contains 24 reciprocal held-record links with settling facts; `verdicts.json` contains the evidence and reasoning.

The controller explicitly approved a packet-only PR: no canonical notes, status changes, merges, deletions, registry edits or new evidence rows. The two supported distinct-entity findings also stay in the packet. EVD-318000–318999 remains unused. `REMOVALS.csv` is header-only because no composite key is removed. This supersedes the provisional data-application plan in acceptance.md; the builder writes task outputs only. Source-backed notes may be applied in a later authorized pass, but no source is stretched to support an unproved identity join here.

## Pair results

| Pair | Held records | Verdict | Deciding or settling fact |
|---|---|---|---|
| D01 Cooper/Lauren | SITE-000818 ↔ SITE-001925 | STILL_UNCERTAIN | 2018 acquisition **agreement**, not dated same-operator/same-2228-Reiser establishment proof. Preserve the old tombstone; do not interpret it as physical closure evidence. |
| D02 Iten/TDM | ORG-000386 ↔ ORG-002079 | STILL_UNCERTAIN | 2008 emissions inventory names Iten Plant3 at West38th; independently verified dated TDM legal/operator succession is missing. |
| D03 Roppe | ORG-001088 ↔ ORG-001087 | VERIFIED DISTINCT | Own2018 release states RHC parent; own2024 EPD explicitly names Roppe Corporation as wholly owned division. Parent/operator records are not equated. |
| D04 Bridgestone/Firestone | ORG-000011 ↔ ORG-001716 | VERIFIED DISTINCT | FY2025 company report lists separate Americas and Firestone Polymers entities and activities; own subsidiary page corroborates. Shared TRIFID attribution remains a separate source-system question. |
| D05 Royal | ORG-000764 ↔ ORG-001091 | STILL_UNCERTAIN | Dated regulator lists Exterior Portfolio North1550Universal and South1441Universal; this does not settle held organization identity or sharedTRIFID re-key. |
| D06 American Sign/Thermoprene | SITE-001858 ↔ SITE-001904 | STILL_UNCERTAIN | Shared address/group subsidiaries are not dated legal-entity and establishment equivalence. Innoplast unrecorded-parent context classified as press, not own-site admission. |
| D07 Horsemen/Tusco | SITE-001882 ↔ SITE-001721 | STILL_UNCERTAIN | Need dated legal/DBA and unit/establishment boundary proof; four fresh address/terms pages were independently unconfirmed. |
| D08 IT Plastics/Overmold | SITE-001924 ↔ SITE-001717 | STILL_UNCERTAIN | Same Jenther street on own pages does not prove same legal operator or process establishment. |
| D09 Esstech | SITE-002301 ↔ SITE-002302 | STILL_UNCERTAIN | Existing merged parent record and current address do not supply a dated site identity/establishment bridge. Esschem affiliate page is contextual press. |
| D10 APT | SITE-002364 ↔ SITE-002304 | STILL_UNCERTAIN | Need inspectable dated legal record resolving Harmony/Evans City109Conica continuity versus relocation/separate premises. No admitted witness; no rescue fetch. |
| D11 Middlefield | SITE-003477 ↔ SITE-001399 | STILL_UNCERTAIN | EPA permit styling Tarkett USA Inc does not equate held Tarkett North America/Johnsonite entities. |
| D12 Chagrin Falls | SITE-003478 ↔ SITE-000427 | STILL_UNCERTAIN | Historical Johnsonite permit and address do not establish dated legal operator continuity for a fold. |

The original SITE-001399 ↔ SITE-000427 assignment was corrected by the controller: those are distinct locations, Middlefield and Chagrin Falls. They are retained in `distinct-location-control.json`, not a thirteenth merge candidate. The corrected D11/D12 endpoints are authoritative.

## Evidence and honest coverage

Helper A: exact5 pairs,20 requests/20 raw hashes, three real-source known answers and actual address-only/parent-only/undated/different-site/fabricated/reversed quote and coverage controls. Helper B: exact7 pairs,36 attempts/35 surviving raw captures, one overwritten APT empty-200 response **UNINSPECTABLE**, three source/identity seams and six negative controls. Both helper checks pass their bounded assertions; the missing capture is explicitly an audit gap, never a verified response.

Independent integration checks cover **20 quoted observations over19 source URLs**: 15 source URLs confirmed (including the two dated distinct-entity decisions), four unconfirmed, zero skipped. The four unconfirmed Horsemen/Tusco routes are retained as limitations on D07, not admitted new facts or absence/closure findings. All retained raw hashes and quote statuses are checked. Roppe2018 calibration was fetched once and reused. No new APT request was made. Raw full pages stay in `/tmp/dedupe-leads-*`; public URLs, quotes, dates and SHA256 receipts are committed.

Research total:20 A +36 B +19 independent-source requests =75 route attempts. APT used6 helper attempts rather than its5 allocation because parallel attempt3 cache names collided; one empty body was overwritten. It stays held and the gap is not hidden by a successful check. Tusco used5 helper plus2 independent address/terms requests =7 direct-subject requests, above the approximate six-fetch effort cap; both fresh routes were unconfirmed and no retry followed. These are disclosed effort/audit exceptions, not relaxed identity criteria. Source failure is availability only.

Source dates are document/period facts. FY2025 financial report states December31,2025; it is not a fresh operating-status census. Iten2008 inventory has year-only coverage and no invented full date. EPA permit dates are permit facts, never corporate rename/closure dates. No shared TRIFID was verified as a new link; all existing registry rows remain untouched.

## Checks

- `python3 tasks/dedupe-leads-2026-11-06/build.py`: reproducible12 adjudications/24 flags, zero canonical writes.
- `python3 tasks/dedupe-leads-2026-11-06/check.py`: exact endpoints, reciprocal coverage/settling facts, two dated distinct findings, all19 raw hashes/statuses, 15confirmed+4unconfirmed yield, every canonical CSV byte equal integration base, output idempotency; three fresh real-source known answers and six admission faults. Missing/duplicate pair, wrong endpoint and forced merge all fail before output writes; missing date or fabricated quote cannot retain VERIFIED admission. Canonical bytes remain unchanged after all faults.
- Both helper check commands are in lanes/a/check.py and lanes/b/check_packet.py, with explicit APT audit exception.
- `python3 scripts/validate.py` and `python3 scripts/check_row_loss.py --base origin/main`: required before PR. No scripts/ changes; full scripts pytest not run.

## Baselines, ownership and agreements

Frozen research snapshots:542629e (`frame-base.txt`, pairs.json). The earlier620c2ec brief pin was superseded because main advanced before checkout; reflog/base confirmed542629e. Current integration base is in base.txt. Latest main snapshot comparison in main-snapshot-drift.json reports no changed endpoint fields. All main canonical bytes are untouched.

L5b thr_ii6ybubss4 is sole integrator. Helpers thr_cbqmb8vyh7(A5 pairs) and thr_niknbt9gc4(B7 corrected pairs) wrote only owned packet folders. L2 confirmed #211 addresses and six notes are co-location leads only, not legal identity;208 must precede211 due frozen notes. L5b does not treat pending208/211 as main facts or edit L2 files. L6 supplied already-captured201 sources: Esstech operator/address does not authorize site fold/Justi parent change; APT has no integrated operator evidence; Tarkett USA/North America legal gap remains. L5b owns D09–D12 adjudication; L6 retains201 operator packet/one-cell registry exception. No sibling proposal authorizes editing another's files. Agreements are also on controller BOARD.

Catalogue search was partial; the Mac lacks the configured Documents entity index. No absence inference was made. No private/CRM/licensed information enters this packet. Controller owns tracker/status/merge. First user: Atlas controller/PIC researcher; non-use finding2026-11-13. Both independent-family deep refutes are pending until requested on the draft PR; no Done or merge claim.

## Final verification receipt

Integration base5574d48f40, frozen research frame542629e. `main-snapshot-drift.json` is empty: all24 endpoint snapshots remain unchanged on the refreshed main. `check.py` PASS exact12/24,2dateddistinct/10holds,19sources15confirmed4unconfirmed,allcanonicalCSVbytesunchanged,rebuildidempotent,3knownanswers+6admissionfaults. `validate.py` PASS zeroerrors:4985organizationrows/7096siterows/37641evidenceobservations. `check_row_loss.py --base origin/main` PASS no keyed row removed,merge-base5574d48f40. No canonical changes or EVD/REL allocations. Fullscripts pytest notrun because scripts/unchanged. Deepindependentfamilyreviewsrequestedondraft;noDone/mergeclaim.

## Codex review receipt — APPROVE

Codex/OpenAI clerk7 thr_4a74hsbtsd APPROVE with zero blocking findings, bound to356bebd7c89a. Independently verified validator0, native row-loss guard (merge-base5574d48), task checks/replay/three known answers/six faults and both helper checks. All220 canonical CSV files are byte-identical to5574d48; diff confined to29 task paths; no data/scripts/QUEUE/federal-frame edits or IDs minted. Counts recompute12pairs=2distinct+10holds/24reciprocalflags/20observations over19URLs=15confirmed+4unconfirmed;REMOVALS has zero body rows.

Independent seed22207 sample10/19URLs:8HTTP200 with ordered quotes confirmed,2HTTP403 matching recorded D07 unconfirmed holds. Sample includes all four D03/D04 witnesses; context supports parent/operator distinction and no-merge result. All12 settling facts inspected; legal/operator/TRI uncertainties stay held. APT overwritten capture remains explicitly UNINSPECTABLE; APT6/Tusco7 effort exceptions remain disclosed. Limits: nine remaining fresh URLs, missing APT body, legal/TRI source-system adjudication, hosted output/fullscripts pytest not inspected. Packet-only scope grants no canonical merge/note/rekey authority. Report: controllerstorage2026-11-06-atlas/reviews/222-clerk-codex-7.md.

This receipt changes README only. Reviewed packet inputs, adjudications, flags and code remain unchanged. Grok verdict is pending; no two-family completion or merge claim. Earlier statements that both family reviews are pending are superseded for Codex only.

## Grok review receipt — APPROVE; both families recorded

Grok clerk6 thr_3b6qu2kt8w APPROVE/zero findings bound a823ebb (packet356bebd, later README-only Codex receipt), report reviews/222-clerk-grok-6.md. Independently passed task12/24/2distinct10holds/19sources15PASS4UNCONFIRMED/canonical-byte-equality/rebuild/knownanswer/fault checks, both helper checks, validator0 and native row-loss. Diff29 task paths only; REMOVALS header-only; no canonical edits/EVD318/merge. Endpoint snapshots have0mismatches; Middlefield/Chagrin control not a thirteenth pair. Contextual Innoplast/Esschem press classification and D10 zero admitted evidence confirmed.

Fresh Roppe2018 parent statement, RoppeEPDvalid2024-05-09, Bridgestoneperiodended2025-12-31 separate entity rows/subsidiarypage, and Cooper2018 acquisition agreement context inspected. No legal-identity or establishment fold inferred. Limits: nine other admitted URLs not freshly fetched, stored hashes checked; D07 integrator captures remain unconfirmed despite live pages now containing words; no new quotes admitted. APT walls/missing capture remain limitations, Tusco7 effort count retained. SITE000818 old duplicate note untouched.

Codex7 and Grok6 both approve unchanged packet356bebd. This README-only receipt leaves all adjudications, flags, inputs, code and canonical data unchanged. Controller owns the merge gate and tracker status; this receipt performs neither merge nor issue closure. Earlier statements that Grok is pending are superseded by this receipt.
