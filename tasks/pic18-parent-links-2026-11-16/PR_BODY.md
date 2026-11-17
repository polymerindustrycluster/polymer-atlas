## Summary

Task: controller-assigned PAR, atlas-w16-parents. Draft parent linkage pass for prospecting.

```text
517 PIC-18 organizations with retained corpus pages and blank parents
  → 11 parent fills + 11 evidence rows + 1 generated parent_of edge
  → 506 holds with named settling facts
```

Sources: company-owned retained pages with quotes and SHA256 receipts in proposals.json. Six changed organization rows are tier B; five tier A. Existing tiers unchanged. No creates, deletions, inclusion-log changes or status changes. Only the two authorized parent columns can change. Dedupe name/alias/notes/site-name receipts retained; unavailable domain/street inputs explicitly skipped.

## Evidence

- Before: both parent columns blank on 11 admitted organization rows.
- After: check.py PASS; independent frame/yield and whole-cell delta checks, retained quote/hash checks, repeat builder appends zero rows, 3/3 injected defects rejected.
- python3 scripts/validate.py: 0 errors, validation passed.
- python3 scripts/check_row_loss.py --base origin/main: PASS.
- python3 scripts/export_vocab.py --check: current.

## Merge Danger

**Door:** two-way. **Blast Radius:** parentage.

Held identity cases include Ravago legal-name mismatch, Medco/OEM alias self-links and duplicate SIMONA candidates. Steelastic and Chemionics already have parents and are excluded. No exhaustive live external ownership history or sponsor analysis; no scripts/ change, so full scripts unit suite skipped. Cross-family review remains with controller; not merge-approved.
