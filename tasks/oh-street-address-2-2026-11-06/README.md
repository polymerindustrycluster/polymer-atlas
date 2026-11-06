# Ohio streets round 2 — L2, 2026-11-06

Controller's 06:30 BOARD assignment: held PIC-18 Ohio sites, own operator location/contact pages first; A/B need own_site. Branch agent/codex/oh-street-address-2 starts at current main9489b60. Separate from OH PR134 and PA PR147. Prior PR fills are excluded using PR134's frozen holds; their clerk findings remain independently actionable.

First user Atlas integrator/controller, review2026-11-06; non-use finding date2026-11-13. Controller delegated L2 application remains in force. No tracker or task-status writes.

Acceptance before fetch: first60 by immutable site ID of448 still-blank, active, A/B-tier Ohio site rows in PIC-18 with a held operator website; all must have been held by PR134. This leaves388 eligible A/B rows explicitly unworked. Broader prior-hold PIC-18 cohort916 includes other tiers and no-website sites; no statewide saturation claim. Street+sources only; no county/county_source/ZIP/tier/status/registry/qualifier changes. Only raw own-page physical address blocks at the recorded city; known ZIP must agree. Multiple sources/notes disagreements, PO boxes, mailing-only blocks and unresolved source identities held. Full input/output partition and ID uniqueness asserted. Sparse IDs EVD-152000–152447 reserve each eligible frame position; selected first60 use152000–152059, disjoint from prior OH and PA. Own pages only; inherited bulk-extract exception unnecessary.

Known answers: three literal live operator addresses before trusting fetcher; wrong-city/PO-box/phone-prefix mutations. Named checks: write-boundary/idempotence/conflict-rejection self-check, validate.py0errors, seeded30 fresh-source audit or full census if fewer30fills, two-family deep clerk refutes. New reviews use controller06:25 pair R-codex-4/R-grok-4; re-reviews stay with the refuting clerk. Draft-before-review ruling05:55 supersedes council-only order.


Final pass: **19 VERIFIED street fills / 41 STILL_UNCERTAIN holds / 60 selected active PIC-18 A/B site rows**. Other388 eligible frame rows uninvestigated. All19 evidence rows own_site/address/supports_A, sparse immutable frame positions. Record tiers unchanged: {'B': 8, 'A': 12}. After controller merge of PR134, active Ohio coverage for THIS PR is **286/1,883 (15.19%) to305/1,883 (16.20%)**. The round2planning snapshot was143to163 before PR134 merged; that denominator is historical and superseded for the current PR diff. The19round2fillIDs remain disjoint from the143first-pass IDs. PA separate.

Transport yield:128 source-page attempts =104 fetched +24 unavailable across60 selected sites;26 sites had raw address blocks,19 pass the final conflict/postal gate. Unavailable requests never became evidence or negative verdicts. The inherited Windows-only rawcheck_tool.py imports a non-local corpus module; this pass reuses PA147's stdlib HTMLParser/curl block extractor, with explicit URL-host redirect binding and failure logs. Only address blocks and page digests retained, not full pages or personal contacts. Five research fetches per operator maximum reserves a sixth for the accepted-fill audit.

Named checks and outcomes (run from repo root):

- python3 tasks/oh-street-address-2-2026-11-06/fetch.py --known: three known LIVE operator addresses (Chardon373Washington; Freeman1101MooreAvon; Shin-Etsu1150DamarAkron),3/3 PASS before the60-site fetch. Wrong-city,PO-box,phone-prefix defect fixtures pass. known_answers.csv records URLs/digests.
- python3 tasks/oh-street-address-2-2026-11-06/check.py: PASS19fills; only street_address/sources change; second apply byte-identical; pre-existing conflicting street and foreign evidence-shard ID collision both rejected BEFORE canonical writes. Plan-to-quote binding asserted;448frameIDs,60workedIDs unique; source yield exactly60.
- python3 tasks/oh-street-address-2-2026-11-06/audit.py:20/20 accepted fills freshly re-fetched,0missing quotes/errors, full census because19<30. No independent-checkability relaxation.
- python3 scripts/validate.py: OK — validation passed,0errors. No scripts/ files changed.
- git diff --check: PASS.

Holds (unit:selected active PIC-18 A/B blank site rows; reasons overlap):

| Filter | Rows | Settling fact |
|---|---:|---|
| No raw address block at recorded city |34| Operator physical address page; failed/ambiguous pages do not show absence |
| Current ZIP conflicts with own-page ZIP |3| Separate dated geography adjudication; no ZIP correction |
| Notes street conflicts with fresh own page |3| Dated address reconciliation; do not choose convenient witness |
| Own-page street blocks disagree |2| Exact establishment among multiple addresses |
| Own-page ZIPs disagree |2| Exact establishment/locality |

All41holds have per-site reasons;388unworked rows selected=no in frame.csv, never labeled researched. No owner scope/ring/vocabulary calls or inclusion_log changes. Pre-pass hashes and selected/fill/evidence IDs in journal.json; backups local/ignored. On newer main take main data and rerun builder; it refuses changed locality/notes/tier/provenance or populated conflicting street. Global evidence IDs preflighted across every shard.

Review: controller05:55/06:25 clerk route; two-family technical verdicts pending. Draft stays unapproved until Codex4 and Grok4 refute exact output.

Controller integration note,2026-11-06: PA147 merged as reviewed e77dd5e at11:03:46UTC, before its verdict-documentation commit862f67a reached the branch. Controller explicitly authorized that README-only approval record to ride this next PR; no PA data/code changes ride it. Main through bdb8b98 (including PA147 and markets/certs136) merged into this branch before review; merge f9a96a9. All new Ohio data changes remain the20 selected fill rows. My earlier READY message was overtaken by the controller merge; PR147 is MERGED.


PR134 integration update: controller merged its reviewed50ac7a2 as1afa5f5 before the worker's verdict/replay documentation commitd9dd945 landed. This PR carries only its README approval record and approved-replay.json; no first-pass code or unmerged first-pass data is bundled. Both original independent verdicts already live on PR134 and BOARD. Main OH evidence-file conflict resolved exclusively by taking main's BOTH Ohio data files and re-running this unchanged20-fill builder. Fresh-main pre-pass copies retained locally. All20 street/evidence values and source quotes remain identical to reviewed-request head0cc6fa0; coverage286to306 now reflects PR134 already on main. Check20fills/boundary/idempotence/mutation-before-write and validator0errors re-pass.


Postal-context refute correction (supersedes20-fill snapshots and original Grok approval): Codex4 REFUTE correctly identified SITE-000008/EVD-152005 Myers contact page explicitly introduces its only new witness with "You can reach us by mail at this address:". Old gate recognized mailing-address/postal-address but missed by-mail. Reproduced BEFORE editing: empty posture, VERIFIED and expected failing assertion; preserved in mailing-regression-before.txt.

The proposal is now HOLD; EVD-152005 permanently retired in retired_ids.csv (never reused). The physical street is not declared false; its sole own-site witness does not settle physical-location use. The shared classifier now catches actual by-mail wording and is tested with that exact phrase plus mailing/postal labels and an email/physical-address negative. Production fetch and monotonic recheck both use it. Re-fetched37 unique witness URLs for original20 positives, checking EVERY qualifying raw block: only Myers flagged. Remaining19 site/evidence values are identical to9ef7eb1 after removing the one proposal; no favorable unit/source substitution.

Took current main's two Ohio data files and replayed19fills, preserving all main keys/legacy evidence. Check19/boundary/idempotence/street+foreign-ID-before-write mutations PASS. Complete19/19 quote audit passes0errors; first re-audit had four temporary TLS/timeout failures (audit_transport_attempt1.csv), a second full run recovered all four; no failed request became evidence or a status inference. Final validator0errors. Coverage286→305/1883(15.19→16.20%), tiersA11/B8. The40 prior holds plus Myers make41. OriginalGrok APPROVE20 is superseded for completion; corrected19/strictmail gate sent to both families.

Nonblocking lead from Codex: Day-Glo SITE-000005's pre-existing notes address overlaps active SITE-002964 under RPM. No new entity created, and no merge/dedupe ruling is made; controller can adjudicate separately. This pass exposes the matching key, not a dedupe decision.

Corrected-head re-review: **Grok(xAI), clerk5, APPROVE511a5af,0findings**, independently reviewing the current19fills. Fresh19quotes and mailing contexts pass; Myersstreet remains blank/EVD152005 absent(retiredonly). check19,validator0,native row-loss andID/federal-frame boundaries independently pass. This receipt carries no earlier20-fill approval forward. Codex corrected-head re-review is still pending; draft retained. This README-only receipt changes no canonical value, builder, source or adjudication input.
