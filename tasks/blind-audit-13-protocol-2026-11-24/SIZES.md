## Decision numbers

Smoke: 40 random PIC-18 records (owners and their sites, published values only). k = records with a source-contradicted core field.
Smoke stop count (owner ruling): stop at the 3rd record with a contradicted core field, 3/40 = 7.5% of the planned sample.
A contradicted descriptive field is reported by field and never stops the smoke (owner ruling).
Unconfirmed claims (u) are reported by field and never stop the smoke; there is no ceiling on the unconfirmed share now (owner ruling). The owner sets any ceiling for a draw after the smoke.
Continue only if the stop count is not reached in all 40, with complete replay accounting and valid controls.
Check each unflagged record independently with probability 15%. Every flagged record gets a second read.
Stress-safe draw: allow 2 records with a contradicted core field in the PIC-18 stratum, fail immediately on 3; no early PASS.
Final PASS also requires the two-sided 95% Wilson upper bound at k ≤ the target.

| Family | Assigned plant calls | Returned | Detected on planted field | Mean miss by plant | 95% interval |
|---|---:|---:|---:|---:|---:|
| Astra | 108 | 108 | 93 | 13.9% | 0.0%–45.9% |
| Hydrogen | 108 | 71 | 65 | 11.3% | 0.0%–43.3% |
| Sonnet | 69 | 54 | 33 | 40.7% | 8.7%–72.8% |

Planning miss probabilities: single 13.89%, single plus checks 12.65%, stress 45.90%.
Stress-safe rule: minimum n satisfying Wilson and ≤2.5% boundary PASS in the stress model. Percentages below are
P(final PASS), conditional on starting the draw in the independent-record model. Each pair is at target / 1.5× target.

| Frame | Target | n | Stop / fail | Perfect reads | Single | Single + checks | Stress, no rescue |
|---|---:|---:|---:|---:|---:|---:|---:|
| PIC-18 | 5% | 265 | 3 | 0.0140% / 0.0000% | 0.0721% / 0.0004% | 0.0624% / 0.0003% | 2.4720% / 0.1278% |

Operating cost of the tight acceptance line: at a true 2% core-field error rate and perfect reads,
the PIC-18 draw passes 9.9% of the time.
Small displayed percentages are rounded; the binomial tail is positive.

### Smoke options (answered 2026-11-24; kept for the record)

smoke-stop: P(smoke reaches the end of its 40 records) at a true share of PIC-18 records with a contradicted core field.
A stop at the m-th k advances with at most m−1 of 40. Perfect reads, then the stress miss.

| Stop at the m-th k | core 2% | core 5% | core 8% | core 2%, stress | core 5%, stress | core 8%, stress |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 81.0% | 39.9% | 15.9% | 93.0% | 70.5% | 47.9% |
| 3 | 95.4% | 67.7% | 36.9% | 99.1% | 90.7% | 75.1% |
| 4 | 99.2% | 86.2% | 60.1% | 99.9% | 97.7% | 90.6% |
| 5 | 99.9% | 95.2% | 78.7% | 100.0% | 99.6% | 97.2% |

descriptive-stop: if a contradicted descriptive field also counted toward the stop at the third. Perfect reads;
core and descriptive errors independent. Columns are true descriptive shares.

| True core share | descriptive 0% | descriptive 5% | descriptive 10% | descriptive 20% |
|---:|---:|---:|---:|---:|
| 2% | 95.4% | 47.2% | 13.4% | 0.4% |
| 5% | 67.7% | 23.8% | 5.7% | 0.2% |

unconfirmed-ceiling: P(more than the ceiling of the 40 records have an unconfirmed core claim), by true share.
The 39.2% column is audit 12's any-field share under the old unit (74 of 189); the core-only share is lower and unmeasured.

| Ceiling (records of 40) | true 10.0% | true 20.0% | true 39.2% |
|---:|---:|---:|---:|
| 8 | 1.5% | 40.7% | 99.2% |
| 12 | 0.0% | 4.3% | 84.9% |
| 16 | 0.0% | 0.1% | 39.1% |

## Input-token budget

Audit 12 long-thread input per record read: Astra ~0.13M, Sonnet ~0.65M, Gemini ~1.0M (unverified).
Audit 12 total ~450M. Fresh-call hypotheses: Astra 0.05M, Hydrogen 0.10M, Sonnet 0.10M.
Scenario: 70/30% primary Astra/Hydrogen. Second reads split 30/45/25% Astra/Hydrogen/Sonnet.
Assume 10% flagged, plus 15% of the remainder. Counts of checks and routing shares are expectations.
Add 3 blind plant calls per provider for smoke and 6 more per provider for the full draw.

| Stage (M input tokens) | Real records | OpenAI | Google | Anthropic | Total |
|---|---:|---:|---:|---:|---:|
| Smoke only | 40 | 1.69 | 1.92 | 0.54 | 4.15 |
| Draw only | 265 | 10.51 | 11.35 | 2.16 | 24.02 |
| Smoke + full stress-safe draw | 305 | 12.20 | 13.28 | 2.69 | 28.17 |

## Decision rule

Power means probability of a PIC-18 PASS conditional on reaching the draw. k counts records with a contradicted core field.
Power triplets are at true record error rates of 1%, 2%, 3%, in that order. Boundary risks use no second-reader rescue.

| Rule | Frame | n | Allow k / fail on | Power, perfect | Power, single + checks | PASS at target, 20% miss | PASS at target, stress | PASS at 1.5× target, 20% miss / stress |
|---|---|---:|---:|---|---|---:|---:|---|
| Stress-safe | PIC-18 | 265 | 2 / 3 | 50.5% / 9.9% / 1.3% | 59.2% / 15.7% / 2.9% | 0.146% | 2.472% | 0.001% / 0.128% |
| Plant-calibrated | PIC-18 | 583 | 14 / 15 | 99.9% / 80.4% / 23.9% | 100.0% / 90.8% / 43.6% | 2.475% | 38.687% | 0.003% / 2.117% |

Select the shortest fixed plant trial giving ≥80% qualification per primary at the worse historical mean miss,
with a one-sided exact 97.5% upper limit ≤20% for each family (Bonferroni simultaneous coverage ≥95%).
Before drawing, score 305 fresh distinct plants per primary family, 610 calls total. Allow ≤47 misses in each;
at that cutoff the upper endpoint is 19.96%. At 13.89% true miss, each family qualifies with probability 80.4%.
Stop on the first excess miss or missing output. A failed calibration returns to the owner without a draw or repeat trial.
Choose the smallest n allowing ≥80% power at true 2% under perfect reads, Wilson within target,
and ≤2.5% boundary PASS at 20% miss. Keep k throughout; the first count above the allowance stops the draw.

| Option (M input tokens) | OpenAI | Google | Anthropic | Total |
|---|---:|---:|---:|---:|
| Extra calibration alone | 15.25 | 30.50 | 0.00 | 45.75 |
| Stress-safe | 12.20 | 13.28 | 2.69 | 28.17 |
| Plant-calibrated | 39.70 | 56.68 | 4.56 | 100.94 |
| Defer rule, smoke only | 1.69 | 1.92 | 0.54 | 4.15 |
Draw-option totals include smoke, routine controls and all planned records. The calibrated total also includes the extra calibration.
