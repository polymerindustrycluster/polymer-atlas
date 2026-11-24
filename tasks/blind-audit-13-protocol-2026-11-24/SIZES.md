## Decision numbers

Smoke: 40 random PIC-18 records. Stop on the third k+u (3/40 = 7.5% of the planned sample).
Continue only after all 40 with k+u ≤ 2, complete replay accounting and valid controls.
Check each unflagged record independently with probability 15%. Every flagged record gets a second read.
Full draw: allow 2 adverse records per stratum, fail immediately on 3; no early PASS.
Final PASS also requires the two-sided 95% Wilson upper bound at k+u ≤ the target.

| Family | Assigned plant calls | Returned | Detected on planted field | Mean miss by plant | 95% interval |
|---|---:|---:|---:|---:|---:|
| Astra | 108 | 108 | 93 | 13.9% | 0.0%–45.9% |
| Hydrogen | 108 | 71 | 65 | 11.3% | 0.0%–43.3% |
| Sonnet | 69 | 54 | 33 | 40.7% | 8.7%–72.8% |

Planning miss probabilities: single 13.89%, single plus checks 12.65%, stress 45.90%.
Minimum n satisfying Wilson and ≤2.5% boundary PASS in the stress model. Percentages below are
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
| Smoke + full draw | 960 | 37.43 | 39.85 | 6.54 | 83.83 |
