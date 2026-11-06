# Florida CORROBORATED screening (L7), 2026-11-06

Acceptance: FL first, <=150 clusters; exact one-verdict census; no new parent when ownership unresolved; provisional federal-only C sites only under resolved held parents; ordered lane IDs; evidence append-only; idempotent fail-closed builder; validate 0 errors; source-first blind re-check of 20 creates; strict NAICS 326 numerator before/after. First user: campaign integrator reviewing this PR on 2026-11-06; non-use finding date 2026-11-13 (controller review).

103 FL CORROBORATED candidate establishment clusters screened: 20 VERIFIED new sites under 19 held parents; 83 STILL_UNCERTAIN holds; 0 REJECT, 0 DUPLICATE_OF, 0 new organizations. All 20 sites are tier C. 141 evidence rows appended (140 site, 1 organization); one held organization gets a federal registrant alias (MAPEI, B-ALIAS). No ring/scope vocabulary rulings. No inclusion_log entries: unresolved cases remain holds.

Sources: banked OSHA ITA CY2025 establishment rows, source URL https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv. Controller thr_9i2c6byhcz explicitly granted use without fresh download at packet vintage 2026-11-01; notes preserve establishment_ID, date_submitted and review date. This supersedes brief section 4 only for the enumerated inherited federal packets. ECHO and Form5500 are discovery/corroboration only here. No own-page quotations or tier B claims. Source scope is provisional federal NAICS per CAMPAIGN's C convention, not independently established current product mix. No current operating-status claim beyond the federal vintage is warranted; active is provisional as documented on each new row.

Dedupe: `create_dedupe.json` records atlas.py CLI domain (when held), normalized-name, address, trade_names/notes searches. `dedupe.json` screens all 103 original clusters and variants. Generic Lakeland resolved from ITA company_name to Graham Packaging. Dart and WinCup known-answer hits prove the B-ALIAS examples remain held, not new parents. MAPEI registrant alias is explicitly marked. No missing county is guessed from city; counties remain blank. No blank HQ inferred for new parents because none are created. The 83 holds were screened for identity/site evidence, not exhaustively investigated or fetched six times. They remain uncompleted research, not negative findings.

Named checks (2026-11-06):
- `python3 scripts/validate.py`: PASS, zero errors.
- `python3 tasks/corroborated-fl-ga-2026-11-06/check.py`: PASS. 103/103 exact verdict census, 3 known answers, 20/20 shuffled source-first blind re-checks against the banked ITA records; exact rerun produces byte-identical data. Deliberate occupied-ID corruption fails before any write.
- `python3 tasks/corroborated-fl-ga-2026-11-06/build.py --apply`: idempotent, second run pending rows 0.
- No scripts/ edits, so scripts pytest gate does not apply.

Florida NAICS 326 strict sites (active/unknown, A/B/C, US) / QCEW 2023 private establishments: 37/798 = 4.6366% before, 53/798 = 6.6416% after. 16 of 20 creates carry 326; four carry 3255. This is a count ratio, not matched QCEW coverage. Baseline bd57a08. GA unchanged by this PR; continuation requires separate branch and PR.

Pre-pass backup: branch base bd57a08. Builder touches sites_FL, evidence_sites_FL, organizations_FL (alias only), evidence_organizations_FL. IDs SITE-016000–016019; EVD-200000–200140. No ORG IDs minted. No registry_links or derived qualifiers touched. Rebase by restoring current main data then re-running build.py (never hand-merge CSVs).

Cross-thread: L6 confirmed ECHO+F5500-only holds, ITA plant labels and missing ownership-status-2 rawcheck path; no shared scripts edited. L2 owns paced FRS REST; L7 made no FRS requests. DATA-ESTATE Documents/RAG layers unavailable on Mac (platform gaps), so no claim of exhaustive estate search; repository extracts suffice for this scoped pass.

## Refutes
Pending Codex + Grok deep refutes. Not completion-approved until both approve.

## Holds (unit: candidate establishment clusters)
| Cluster | Settling fact / recommendation |
|---|---|
| LF-FL-00109 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00450 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00343 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00370 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00381 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00544 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00425 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00385 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00403 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00092 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00338 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00485 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00487 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00526 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00250 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00060 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00435 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00520 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00098 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00047 | HOLD: TSE campus at 5260 vs held 5180 113th Ave N and 4370 112th Terrace; settle distinct establishment vs campus address. |
| LF-FL-00006 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00358 | HOLD: Dart ORG-002441 is held (B-ALIAS); 1605 Turkey Creek Rd must be reconciled against held SITE-010912 at 4610 Airport Rd before treating it as a distinct establishment. |
| LF-FL-00022 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00081 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00155 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00392 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00529 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00115 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00151 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00196 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00070 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00404 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00345 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00363 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00815 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00176 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00087 | HOLD: Carpenter 5100 vs held SITE-005317 at 5150 Frontage Rd S; settle same-campus identity before creating. |
| LF-FL-00225 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00549 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00369 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00437 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00278 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00454 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00333 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00867 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00378 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00334 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00290 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00812 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00277 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00118 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00299 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00248 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00311 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00234 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00052 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00041 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00597 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00832 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00436 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00386 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00284 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00845 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00102 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00270 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00495 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00050 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00552 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00265 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00181 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00362 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00527 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00648 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00630 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00030 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00319 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00523 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00374 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00059 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00101 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00787 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00224 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
| LF-FL-00831 | HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation. |
