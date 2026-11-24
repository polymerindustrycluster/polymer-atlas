# Blind audit after repairs

**Only the smoke stage is authorized, after the remaining repairs land.** Return the results, including the unresolved rate and measured cost per record by provider, to the owner. Both full-draw decision rules below are proposals. Even a clean smoke requires a fresh owner ruling before calibration or a draw. [Owner rulings](../../DECISIONS.md)

## Population and custody

Use the [preceding protocol’s approved frames, footprint precedence, placement exceptions, published-field classes, child scope and grade definitions](../blind-audit-12-protocol-2026-11-23/PROTOCOL.md). At a fresh repaired main commit, reconcile unique records and all exclusions to the pinned tables and site/export surfaces. Update the field inventory for current published facts, including process and material other-notes. Use the vocabulary and ring restrictions at that commit. A missing field classification or unexplained population change blocks sampling. The [owner’s lean-design, review-routing and vocabulary rulings](../../DECISIONS.md) govern this revision.

After the remaining repairs land, the controller seals the commit, protocol, sizes, packet/replay code, frame digest, randomization method and fresh secret commitment before seeing outcomes. For smoke, take an equal-probability sample without replacement from the cluster stratum. Keep that selection private. Only if the owner subsequently authorizes a full draw, sample uniformly without replacement within each remaining stratum, excluding smoke IDs. Use independent keyed orderings for smoke, draw, plants, check coins and display order. Assert no duplicate or overlapping units, sufficient remaining population and equal inclusion probability within each eligible frame. If a stratum is too small, return for a revised calculation. No repairs between smoke and draw, substitutions, or retries on the same snapshot. On repair, start a new sealed attempt. Privately link the audit receipts; publish only aggregate results.

## What goes to a reader

Before sampling, inventory the dependencies of every judged field and child. Test the final serialized packet against that inventory. In particular, NAICS attribution needs the actual public source name, source type, code, grain and supporting document. Never mask a value needed to judge another field. Use the [blind-packet addendum](../blind-audit-12-tooling-2026-11-23/PROTOCOL_ADDENDUM_2026-11-23.md) for leak scanning, privacy and exact public-cell approvals. Where a dependency collides with metadata or privacy, supply a clean, independently replayed public witness preserving the full deciding fact. If neither safe literal nor equivalent witness is possible, block packet release and record the dependency. Exercise the gate with a removed source name. Suppress builder family, history, order, control labels and prior verdicts. Report withheld judged literals separately; a placeholder earns no credit.

Fetch once per distinct source/version by script, cache the raw bytes, time, canonical URL, digest and availability status. Both readers receive the same sanitized excerpt and may request further admissible sources through the shared cache within the inherited fetch budget. Replay quoted words in order against main text and check operator, street, date, qualifier and claim grain. Binding alone cannot establish a filing fact.

For every populated filing-backed band, filing NAICS or registry ID, run the [raw-snapshot replay pattern](../pic18-size-10yr-2026-11-23/check.py) before issuing the packet. Verify the store checksum, locate the original filing row, bind identifier and operator to establishment or parent as claimed, and emit the source name, filing period, relevant public values, comparison and replay status. For bands apply the schema’s filing-age cutoff, newer contradictory evidence, establishment headcount, single-site eligibility and source-specific restrictions. Plan participants cannot establish employee count. For NAICS compare the raw code and attribution at that grain. For registry IDs check the issuing registry’s extract and conflicting owners. Test wrong operator, wrong vintage and conflicting identifiers as well as a matched control. Deliver replay receipts and deciding facts to the reader. A failed download or ambiguous match leaves an unresolved claim. A reproduced contrary fact can establish an error. Reconcile the replay inventory to every expected field and child. A missing receipt blocks packet issuance.

## Reading and stopping

Determine builder families privately from record and child provenance plus repair history. Route primary to Astra when independent and to Hydrogen otherwise. Unknown provenance or no eligible primary blocks the run; never drop such records. Keep the Gemini watchdog. Give each reader a fresh short call containing one record and its scoped children; require a complete field/child checklist. Privately mix realistic, separately sourced field swaps into each participating family's queue, exercise the actual reader/replay interface and keep all controls outside the real samples. Stage plant calls ahead of any PASS and interleave with real calls, without announcing their positions. Every control must identify the planted field as erroneous or specifically unsettled on its merits. A missed or missing control invalidates that stage; suspend and diagnose. No replacement draws.

Lock first verdicts before releasing cases to a different family. Flag any error, uncertainty, missing assessment or adverse replay. Bernoulli-check each remaining AGREE independently using the precommitted check coin. Route second reads to another eligible family (prefer Hydrogen for Astra, Astra for Hydrogen, Sonnet when needed). With only the builder available as second family, mark the exception and give its objection evidentiary review; its agreement cannot clear a flag. Require the independent primary plus objective source replay to settle each disputed field. If those cannot settle it, retain UNRESOLVED. The new rule replaces the prior lead sweep. The second reader sees neither flag nor initial verdict. Log a missing required read and hold the decision until delivered or terminate incomplete.

Count each real record exactly once. A demonstrated error on any in-scope field or child goes in k; absent a demonstrated error, any unsettled claim goes in u. An upheld flag cannot be erased by a vote. Verified contradictions take precedence over uncertainty. Missing values are omissions under the inherited rule. A clean record requires all applicable checks. Use k+u at both gates. Process completed decisions in sealed order; as soon as a stratum fails, cancel its remaining calls. Since one failed stratum precludes exit, cancel the remaining draw at the first decisive failure and label unfinished strata incomplete. Report audited denominator, k, u, reason classes, omissions, replay coverage, routing exceptions, check-only discoveries and plant performance. A stopped sample establishes a decision, not an exact population rate.

Under the calibrated option, the controller also seals a separate pre-draw calibration after the owner adopts that option. Sample independent, distinct challenge records from a preregistered mix of repair and error classes at the audited grains. Include hard attribution, filing, field-dependency and child-binding defects. Use a held-out challenge bank independent of the current eligible frame and exclude historical plants. Never remove eligible Atlas rows to assemble the bank. If representative distinct challenges cannot be sourced, return to the owner before calibration. Lock packets, answer keys, scoring and family assignments before releasing calls. Use the production packet and grading path, with blind fresh calls and no disclosure of membership. Score a miss unless the actual planted field is identified under the same criteria as routine controls. The calibrated allowance applies only to these extra trials. Routine smoke and draw controls retain their all-detected gate. Both primary families must qualify before the calibrated draw. A favorable pooled result cannot qualify a failing family.

<!-- sizes begin -->
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
<!-- sizes end -->

## Interpreting the risks and budget

The risk table models independent real-record errors with a common stratum rate and independent detections across records. Each entry is the lower binomial tail at the allowed count with observed adverse probability equal to true error probability times detection probability. Taking unsettled records as adverse can only lower PASS relative to the table if real flags are retained. Early failure has the same PASS event as reading the whole planned sample. Smoke can veto the audit but cannot certify the population. The table models the full draw; it gives no finite-population guarantee conditional on a favorable smoke from a fixed population. There is no multiplication of stratum probabilities to claim a joint confidence level.

Calibration uses the frozen prior reader outputs. Within each family join assigned blind packets to the private plant key and returned field verdicts. Credit a returned FIELD_ERROR or UNRESOLVED on the exact altered field, excluding withheld-only explanations. Average miss fractions equally over distinct plants with returns. Repeated calls on one plant are replicates, so the interval uses a two-sided Hoeffding radius over distinct plants. It is a sensitivity interval under independent representative plant clusters, conditional on returns. Plants are purposive field swaps, families share plants and unfinished calls may differ. These intervals cannot validate sensitivity to subtle real errors. The stress column uses the worse primary upper endpoint and gives the second family no rescue credit. The check-share scenario uses the worse primary mean and the worst second-family mean, with independent misses conditional on error. Shared source failures could erase that gain; systematic defects invisible to all readers could evade even the stress model. The stress-safe option often fails a relatively clean Atlas. The calibrated option uses its own pre-draw sensitivity gate and a larger allowance for adverse records. Its confidence limits apply to the challenge distribution; extending them to real defects in every stratum assumes equally good detection there. Neither the old purposive plants nor the new qualification test establish that transfer. If the real-record miss rate stays at the stress value despite qualification, use the stress column for the calibrated draw. Higher apparent power with imperfect reads partly reflects undetected errors.

In the smoke, record k and u separately, including filing-replay and missing-dependency reasons. Log tokens from provider request records, including cache reads and retries exactly once, divided by completed real and control calls by provider; charge unsuccessful work to the same ledger. Compare measured mean input, flag share, provider eligibility and projected spend to the scenario before scaling. Short-call savings assume each request carries a bounded packet without prior conversation history. No-output or unmetered work stops. If a provider exceeds its stage budget or measured rates project an overrun, halt for repricing before further calls. Retain the owner’s fan-out controls. Smoke-only spends the first budget and gives no publication decision.
