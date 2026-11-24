# Owner questions and rulings

**Recorded answers.** “Smoke only” after the remaining repairs land. “Decide after the smoke” on the rule. Bring the unresolved rate and measured per-record cost back to the owner before any draw. The original options follow. [Decision ledger](../../DECISIONS.md)

## Scope of authorization

**How far should the controller proceed after the repairs?**

- **A · Authorize smoke only (recommended).** Read up to 40 random PIC-18 records. Stop on the third confirmed error or unresolved record. Estimate 4.15M input tokens across providers. Bring the unresolved causes, control performance and measured cost back before authorizing a draw.
- **B · Authorize a conditional draw.** Proceed only after a clean-enough smoke and all control and spending gates. Depending on the decision rule chosen below, the combined estimate is 83.83M or 146.40M input tokens. A P1 exit requires all six strata to pass.
- **C · Defer all sampling.** No reader spend. P1 stays open.

## Decision rule

**Which standard should govern a future P1 exit draw?** Choosing a standard sets the design. The scope ruling above determines whether the controller may execute it. A confirmed error or an unresolved record counts once toward the allowance.

- **A · Keep the stress-safe rule.** For 83.83M input tokens including smoke, read 265 PIC-18 records and fail on the third adverse record. With perfect reads, PIC-18 passes only 9.9% of draws when just 2% of records are wrong. At the 5% error boundary, the modeled false-pass risk stays below 2.5% even if readers miss 45.9% of errors.
- **B · Adopt the plant-calibrated rule (recommended for a future draw).** Budget 146.40M including smoke and 45.75M for 305 fresh planted defects per primary family. Each family must miss at most 47, giving a simultaneous 95% upper limit of 19.96% at that cutoff. If either fails, stop before the draw. If both qualify, read 583 PIC-18 records and allow up to 14 adverse. At 2% true error, perfect-read power rises to 80.4%. At the 5% boundary, false-pass risk is 2.475% if real misses stay at 20%, but 38.687% if real misses are 45.9% despite qualification. Choose this only if the challenge mix represents the defects readers must find.
- **C · Defer the rule and run smoke only.** Spend an estimated 4.15M. A favorable smoke establishes readiness to reconsider the draw and gives no exit verdict. This option limits any sampling authorization to smoke.

PIC-18 power below means the probability of passing the draw at the stated true record error rate, conditional on reaching it. The single-reader scenario includes checks by a second family. Its higher pass rate includes undetected errors.

<!-- owner figures -->
| PIC-18 rule | Perfect reads at 1% / 2% / 3% | Single + checks at 1% / 2% / 3% |
|---|---|---|
| Stress-safe | 50.5% / 9.9% / 1.3% | 59.2% / 15.7% / 2.9% |
| Plant-calibrated | 99.9% / 80.4% / 23.9% | 100.0% / 90.8% / 43.6% |

| Option (M input tokens) | OpenAI | Google | Anthropic | Total |
|---|---:|---:|---:|---:|
| Extra calibration alone | 15.25 | 30.50 | 0.00 | 45.75 |
| Stress-safe | 37.43 | 39.85 | 6.54 | 83.83 |
| Plant-calibrated | 60.31 | 78.39 | 7.70 | 146.40 |
| Defer rule, smoke only | 1.69 | 1.92 | 0.54 | 4.15 |
