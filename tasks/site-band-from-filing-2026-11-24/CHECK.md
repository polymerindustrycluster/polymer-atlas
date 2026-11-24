# Verification

Run from the repository root with the Atlas store mounted. The shared lock serializes full builds and checks.

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 tasks/site-band-from-filing-2026-11-24/build.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 tasks/site-band-from-filing-2026-11-24/check.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py
```

The builder was run twice with identical data diffs. The independent checker recomputed the candidate frame and decisions at the pinned base, checked source hashes, compared every site cell and allowed evidence append, and reconciled the claims list. Wrong value, omission, overwrite, truncated record, and duplicate on-disk claim plants were rejected. Atlas validation passed.

The new evidence passed `scripts/check_evidence_binding.py --new-since HEAD` and `--provenance-since HEAD` before commit.
