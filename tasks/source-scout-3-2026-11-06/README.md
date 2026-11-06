# L5 source scout 3 — atlas-L5-scout-3, 2026-11-06

Scope fixed before work: packet/docs only; no data edits, no IDs, no membership edges. Branch agent/codex/source-scout-3. First user: Atlas controller/PIC researcher, for next source-prioritization decision by 2026-11-13; non-use then is a finding for controller review, not an automatically opened commitment.

| Source | Source verdict | Sample result (new organization leads) | Open hold |
|---|---|---|---|
| IAF CertSearch | CLOSED public extraction | Not sampled: terms gate; yield/CI unavailable | Written redistribution authorization |
| PMA Processor Members | CORROBORATION_ONLY | 3/20 VERIFIED new; 15%, Wilson 95% 5.24–36.04% | Publication rights; 10 uncertain entries |
| PatentsView / USPTO bulk | CORROBORATION_ONLY | 0/20 VERIFIED new; 0%, Wilson 95% 0–16.11% | Current operation/identity; confirmed PIC-18 patent count |

See each source subfolder for route, terms clause or explicit inability to obtain one, count units, sampling frame, dedupe limitations and holds. No automated-use right was inferred from public accessibility. PatentsView sample is a bulk-evidence sufficiency scout, not an own-site verification campaign; zero does not mean no opportunity. 51 PIC-18 held organization candidates are not 51 confirmed patent-owning organizations.

CBP request resolved: CSV already contains all six counties (160 rows; 16 totals reconciled to fresh Census API). Fresh bulk rebuild is byte-identical. Updated stale reporting selection from PIC-12 to regions.PIC18; PIC-18 NAICS 326 total 401 establishments.

## Named runnable checks

- `python3 tasks/source-scout-3-2026-11-06/build.py`: PASS. Recomputes every yield/CI from sample CSVs and compares metrics.json; requires 20 unique sample rows per sampled source, legal verdicts and singleton held duplicate endpoints. Known Wilson endpoints, three named held matcher answers and a deliberate duplicate-sample defect all exercised; malformed input must fail. Reconciles all 16 county/NAICS API totals and asserts row and assignee-ID uniqueness.
- `python3 scripts/validate.py`: PASS, 0 errors, OK — validation passed.
- `uv run --with pytest python -m pytest -q scripts/`: PASS, 220 passed, 1 skipped, 1 warning, 43 subtests passed (67.55s). Bare python3 has no pytest; ephemeral uv dependency, no repo dependency added.

No canonical data rows added/changed at any verification tier; three VERIFIED packet leads only. No inclusion_log writes or closure/rejection decisions. Two pre-existing CRLF-dirty federal-frame files are excluded.

## Cross-thread ledger

Controller thr_9i2c6byhcz owns integration and status. No sibling agreements or ownership transfers. Estate catalog search found the prior patent pilot and migrated bulk route; Windows Documents inventory is unavailable on this Mac, so search coverage is partial. No private holdings were copied into the packet.

## Independent refutation

Council deep calls were refused by shared-host burst limits (no verdict). Controller 05:55 ruling supersedes council-only routing: assigned independent Codex/Grok refute clerks will review PR #131. Results appended after inspection. No claim of Done while a required gate remains open.

Additional checks: `python3 tasks/source-scout-3-2026-11-06/association/check_frame.py` PASS: live95-element processor frame, seeded20 identities equal committed sample, three-item parser known answer and missing-boundary negative check. `python3 -m unittest discover -s scripts -p test_*.py` PASS:221 tests,1 skipped.
