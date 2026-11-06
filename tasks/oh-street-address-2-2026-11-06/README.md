# Ohio streets round 2 — L2, 2026-11-06

Controller's 06:30 BOARD assignment: held PIC-18 Ohio sites, own operator location/contact pages first; A/B need own_site. Branch agent/codex/oh-street-address-2 starts at current main9489b60. Separate from OH PR134 and PA PR147. Prior PR fills are excluded using PR134's frozen holds; their clerk findings remain independently actionable.

First user Atlas integrator/controller, review2026-11-06; non-use finding date2026-11-13. Controller delegated L2 application remains in force. No tracker or task-status writes.

Acceptance before fetch: first60 by immutable site ID of448 still-blank, active, A/B-tier Ohio site rows in PIC-18 with a held operator website; all must have been held by PR134. This leaves388 eligible A/B rows explicitly unworked. Broader prior-hold PIC-18 cohort916 includes other tiers and no-website sites; no statewide saturation claim. Street+sources only; no county/county_source/ZIP/tier/status/registry/qualifier changes. Only raw own-page physical address blocks at the recorded city; known ZIP must agree. Multiple sources/notes disagreements, PO boxes, mailing-only blocks and unresolved source identities held. Full input/output partition and ID uniqueness asserted. Sparse IDs EVD-152000–152447 reserve each eligible frame position; selected first60 use152000–152059, disjoint from prior OH and PA. Own pages only; inherited bulk-extract exception unnecessary.

Known answers: three literal live operator addresses before trusting fetcher; wrong-city/PO-box/phone-prefix mutations. Named checks: write-boundary/idempotence/conflict-rejection self-check, validate.py0errors, seeded30 fresh-source audit or full census if fewer30fills, two-family deep clerk refutes. New reviews use controller06:25 pair R-codex-4/R-grok-4; re-reviews stay with the refuting clerk. Draft-before-review ruling05:55 supersedes council-only order.


Final pass: **20 VERIFIED street fills / 40 STILL_UNCERTAIN holds / 60 selected active PIC-18 A/B site rows**. Other388 eligible frame rows uninvestigated. All20 evidence rows own_site/address/supports_A, sparse immutable frame positions. Record tiers unchanged: {'B': 8, 'A': 12}. Main-only active Ohio coverage **143/1,883 (7.59%) to163/1,883 (8.66%)** excludes pending PR134. Ohio fill-ID sets are disjoint: combined prospective306/1,883 (16.25%), not an already merged result. PA separate.

Transport yield:128 source-page attempts =104 fetched +24 unavailable across60 selected sites;26 sites had raw address blocks,20 passed conflict checks. Unavailable requests never became evidence or negative verdicts. The inherited Windows-only rawcheck_tool.py imports a non-local corpus module; this pass reuses PA147's stdlib HTMLParser/curl block extractor, with explicit URL-host redirect binding and failure logs. Only address blocks and page digests retained, not full pages or personal contacts. Five research fetches per operator maximum reserves a sixth for the accepted-fill audit.

Named checks and outcomes (run from repo root):

- python3 tasks/oh-street-address-2-2026-11-06/fetch.py --known: three known LIVE operator addresses (Chardon373Washington; Freeman1101MooreAvon; Shin-Etsu1150DamarAkron),3/3 PASS before the60-site fetch. Wrong-city,PO-box,phone-prefix defect fixtures pass. known_answers.csv records URLs/digests.
- python3 tasks/oh-street-address-2-2026-11-06/check.py: PASS20fills; only street_address/sources change; second apply byte-identical; pre-existing conflicting street and foreign evidence-shard ID collision both rejected BEFORE canonical writes. Plan-to-quote binding asserted;448frameIDs,60workedIDs unique; source yield exactly60.
- python3 tasks/oh-street-address-2-2026-11-06/audit.py:20/20 accepted fills freshly re-fetched,0missing quotes/errors, full census because20<30. No independent-checkability relaxation.
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

All40holds have per-site reasons;388unworked rows selected=no in frame.csv, never labeled researched. No owner scope/ring/vocabulary calls or inclusion_log changes. Pre-pass hashes and selected/fill/evidence IDs in journal.json; backups local/ignored. On newer main take main data and rerun builder; it refuses changed locality/notes/tier/provenance or populated conflicting street. Global evidence IDs preflighted across every shard.

Review: controller05:55/06:25 clerk route; two-family technical verdicts pending. Draft stays unapproved until Codex4 and Grok4 refute exact output.

Controller integration note,2026-11-06: PA147 merged as reviewed e77dd5e at11:03:46UTC, before its verdict-documentation commit862f67a reached the branch. Controller explicitly authorized that README-only approval record to ride this next PR; no PA data/code changes ride it. Main through bdb8b98 (including PA147 and markets/certs136) merged into this branch before review; merge f9a96a9. All new Ohio data changes remain the20 selected fill rows. My earlier READY message was overtaken by the controller merge; PR147 is MERGED.
