## Decision numbers

Smoke: 40 random PIC-18 records. Stop on the third k+u (3/40 = 7.5% of the planned sample).
Continue only after all 40 with k+u ≤ 2, complete replay accounting and valid controls.
Check each unflagged record independently with probability 15%. Every flagged record gets a second read.
Stress-safe draw: allow 2 adverse records per stratum, fail immediately on 3; no early PASS.
Final PASS also requires the two-sided 95% Wilson upper bound at k+u ≤ the target.

| Family | Assigned plant calls | Returned | Detected on planted field | Mean miss by plant | 95% interval |
|---|---:|---:|---:|---:|---:|
| Astra | 108 | 108 | 93 | 13.9% | 0.0%–45.9% |
| Hydrogen | 108 | 71 | 65 | 11.3% | 0.0%–43.3% |
| Sonnet | 69 | 54 | 33 | 40.7% | 8.7%–72.8% |

Planning miss probabilities: single 13.89%, single plus checks 12.65%, stress 45.90%.
Stress-safe rule: minimum n satisfying Wilson and ≤2.5% boundary PASS in the stress model. Percentages below are
P(final PASS), conditional on starting the draw in the independent-record model. Each pair is at target / 1.5× target.

| Stratum | Target | n | Stop / fail | Perfect reads | Single | Single + checks | Stress, no rescue |
|---|---:|---:|---:|---:|---:|---:|---:|
| PIC-18 | 5% | 265 | 3 | 0.0140% / 0.0000% | 0.0721% / 0.0004% | 0.0624% / 0.0003% | 2.4720% / 0.1278% |
| Rest of Ohio | 10% | 131 | 3 | 0.0122% / 0.0000% | 0.0670% / 0.0003% | 0.0578% / 0.0002% | 2.4898% / 0.1209% |
| Rest of country | 10% | 131 | 3 | 0.0122% / 0.0000% | 0.0670% / 0.0003% | 0.0578% / 0.0002% | 2.4898% / 0.1209% |
| Researchers | 10% | 131 | 3 | 0.0122% / 0.0000% | 0.0670% / 0.0003% | 0.0578% / 0.0002% | 2.4898% / 0.1209% |
| Programs | 10% | 131 | 3 | 0.0122% / 0.0000% | 0.0670% / 0.0003% | 0.0578% / 0.0002% | 2.4898% / 0.1209% |
| Events and participation | 10% | 131 | 3 | 0.0122% / 0.0000% | 0.0670% / 0.0003% | 0.0578% / 0.0002% | 2.4898% / 0.1209% |

Operating cost of the tight acceptance line: at a true 2% error rate and perfect reads,
PIC-18 passes 9.9% of draws and each other stratum passes 51.2%;
at a 5% true adverse rate the smoke gate alone advances 67.7% of the time (perfect reads).
Small displayed percentages are rounded; the binomial tail is positive.

## Input-token budget

Audit 12 long-thread input per record read: Astra ~0.13M, Sonnet ~0.65M, Gemini ~1.0M (unverified).
Audit 12 total ~450M. Fresh-call hypotheses: Astra 0.05M, Hydrogen 0.10M, Sonnet 0.10M.
Scenario: 70/30% primary Astra/Hydrogen. Second reads split 30/45/25% Astra/Hydrogen/Sonnet.
Assume 10% flagged, plus 15% of the remainder. Counts of checks and routing shares are expectations.
Add 3 blind plant calls per provider for smoke and 6 more per provider for the full draw.

| Stage (M input tokens) | Real records | OpenAI | Google | Anthropic | Total |
|---|---:|---:|---:|---:|---:|
| Smoke only | 40 | 1.69 | 1.92 | 0.54 | 4.15 |
| Draw only | 920 | 35.74 | 37.93 | 6.01 | 79.68 |
| Smoke + full stress-safe draw | 960 | 37.43 | 39.85 | 6.54 | 83.83 |

## Decision rule

Power means probability of a stratum PASS conditional on reaching the draw, with no additional unresolved records.
Power triplets are at true record error rates of 1%, 2%, 3%, in that order. Boundary risks use no second-reader rescue.

| Rule | Stratum | n | Allow k+u / fail on | Power, perfect | Power, single + checks | PASS at target, 20% miss | PASS at target, stress | PASS at 1.5× target, 20% miss / stress |
|---|---|---:|---:|---|---|---:|---:|---|
| Stress-safe | PIC-18 | 265 | 2 / 3 | 50.5% / 9.9% / 1.3% | 59.2% / 15.7% / 2.9% | 0.146% | 2.472% | 0.001% / 0.128% |
| Stress-safe | Each other stratum | 131 | 2 / 3 | 85.6% / 51.2% / 24.4% | 89.2% / 59.8% / 33.0% | 0.138% | 2.490% | 0.001% / 0.121% |
| Plant-calibrated | PIC-18 | 583 | 14 / 15 | 99.9% / 80.4% / 23.9% | 100.0% / 90.8% / 43.6% | 2.475% | 38.687% | 0.003% / 2.117% |
| Plant-calibrated | Each other stratum | 107 | 3 / 4 | 97.7% / 83.3% / 60.0% | 98.5% / 88.2% / 69.2% | 2.451% | 16.347% | 0.072% / 2.234% |

Select the shortest fixed plant trial giving ≥80% qualification per primary at the worse historical mean miss,
with a one-sided exact 97.5% upper limit ≤20% for each family (Bonferroni simultaneous coverage ≥95%).
Before drawing, score 305 fresh distinct plants per primary family, 610 calls total. Allow ≤47 misses in each;
at that cutoff the upper endpoint is 19.96%. At 13.89% true miss, each family qualifies with probability 80.4%.
Stop on the first excess miss or missing output. A failed calibration returns to the owner without a draw or repeat trial.
For each stratum choose the smallest n allowing ≥80% power at true 2% under perfect reads, Wilson within target,
and ≤2.5% boundary PASS at 20% miss. Keep k+u throughout; the first count above the allowance stops the stratum.

| Option (M input tokens) | OpenAI | Google | Anthropic | Total |
|---|---:|---:|---:|---:|
| Extra calibration alone | 15.25 | 30.50 | 0.00 | 45.75 |
| Stress-safe | 37.43 | 39.85 | 6.54 | 83.83 |
| Plant-calibrated | 60.31 | 78.39 | 7.70 | 146.40 |
| Defer rule, smoke only | 1.69 | 1.92 | 0.54 | 4.15 |
Draw-option totals include smoke, routine controls and all planned records. The calibrated total also includes the extra calibration.
