# Local binding gate verification

## Census on main

Both gate versions ran `python3 scripts/check_evidence_binding.py --all --head 0b191fe604f8e3e6691ea7f7fadb2e4b36d6ce9b --out <verdicts.csv>` and exited 0. Both judged exactly 47,610 evidence rows against the same pinned main tree. The gate reconciled its CSV row count to an independent raw-line count. Comparing the two exports found the same 47,610 unique evidence IDs and identical output rows outside the two tables below.

The unit is an evidence row whose `record_table` is the named table, including every claim and source class.

| Record table | Gate version | PASS | FAIL | HELD | READ_REQUIRED | UNINSPECTABLE | Total evidence rows |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| programs | Main | 0 | 0 | 0 | 0 | 794 | 794 |
| programs | Patched | 0 | 0 | 0 | 0 | 794 | 794 |
| ecosystem | Main | 0 | 0 | 0 | 6 | 427 | 433 |
| ecosystem | Patched | 0 | 0 | 0 | 4 | 429 | 433 |

All 794 program evidence rows move from `other_table` to `no_quote`. Main already processed ecosystem rows. Two legacy ecosystem address quotes now report `locality_not_matched` because their prose does not isolate a city for the parser (EVD-405003 and EVD-405014).

`--all` runs the mechanical checks without capture replay. The regression tests exercise proof replay against synthetic HTML bytes through the gate CLI. No live S4 Medical capture was fetched.

## Planted regressions

```sh
python3 scripts/test_check_evidence_binding.py ProgramAndEcosystemVerdicts \
  WebProofs.test_divi_body_and_empty_main_replay \
  WebProofs.test_empty_capture_cannot_replay \
  WebProofs.test_program_and_ecosystem_web_rows_require_proof_replay
```

The final test file against main's original gate exited 1 (four tests, 31 failing assertions including subtests). Against the patched gate the same command exited 0 (four tests). The fixtures plant another record, a parent-only quote, another city, another state, an unsupported claim, a same-campus sibling URL, an absent proof line, a Divi body wrapper and an empty main element. A chrome-only capture is blocked in both versions.

The authoritative PR binding job loads the gate from main. The local census and regression command above exercise the patch before that job picks it up.

## Validation and full suite

```sh
lockf -k /tmp/polymer-atlas-heavy.lock sh -c 'python3 scripts/validate.py && python3 scripts/run_tests.py'
```

Validation passed. The suite completed all ten shards with 620 passing tests and one skip because the optional `mcp` package was unavailable.
