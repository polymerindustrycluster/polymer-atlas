# Blind audit after repairs

**Only the smoke stage is authorized, after the remaining repairs land.** Return the results, including the unresolved rate and measured cost per record by provider, to the owner. Both full-draw decision rules below are proposals. Even a clean smoke requires a fresh owner ruling before calibration or a draw. [Owner rulings](../../DECISIONS.md)

## Population and custody

Use the [preceding protocol’s approved frames, footprint precedence, placement exceptions, published-field classes, child scope and grade definitions](../blind-audit-12-protocol-2026-11-23/PROTOCOL.md), amended as follows. **The frame is the PIC-18 stratum only** (owner step-back ruling): organizations and ecosystem entities with an active tier A–C site in the PIC-18 counties, and their sites. The preceding protocol’s other strata are not audited; national records stay as they are, labeled unaudited. **The audit counts only published values.** A blank (unknown) value is not a claim: it is never an error and never an unconfirmed claim. The grade table of the preceding protocol is amended in the next section. At a fresh repaired main commit, reconcile unique records and all exclusions to the pinned tables and site/export surfaces. Update the field inventory for current published facts, including process and material other-notes. Use the vocabulary and ring restrictions at that commit. A missing field classification or unexplained population change blocks sampling. The [owner’s lean-design, review-routing and vocabulary rulings](../../DECISIONS.md) govern this revision.

After the remaining repairs land, the controller seals the commit, protocol, sizes, packet/replay code, frame digest, randomization method and fresh secret commitment before seeing outcomes. For smoke, take an equal-probability sample without replacement from the cluster stratum. Keep that selection private. Only if the owner subsequently authorizes a full draw, sample uniformly without replacement within the PIC-18 stratum, excluding smoke IDs. Use independent keyed orderings for smoke, draw, plants, check coins and display order. Assert no duplicate or overlapping units, sufficient remaining population and equal inclusion probability within each eligible frame. If the stratum is too small, return for a revised calculation. No repairs between smoke and draw, substitutions, or retries on the same snapshot. On repair, start a new sealed attempt. Privately link the audit receipts; publish only aggregate results.

## What counts as wrong, unconfirmed or descriptive

Owner look-back ruling: a published value is wrong only when a source contradicts it. A value that cannot be confirmed is reported as unconfirmed, by field, next to the error rate; it is not counted as an error. The bar gates on the core fields. [Ruling text](../../DECISIONS.md)

- **Core fields (gate):** organization or site name (`legal_name`, `site_name`), operating status (`status`, `operating_status`), street (`street_address`), county (`county`, `hq_county`) and polymer relevance. Polymer relevance is judged in or out of scope at the record’s grain (organization or site), under the [SCHEMA ring tests and exclusions](../../docs/SCHEMA.md), from the entity’s own site or filing. It is contradicted only when a source shows no polymer, rubber, coating or comparable on-site activity at that grain (polymer only as packaging or a purchased part, retail only, a different entity). A different ring number is not an error; it is reported as a descriptive note.
- **Contradicted** means a replayed public source states a different value, states the fact at another grain, or shows that the row is a different entity or a duplicate of a held record. A wrong-entity or duplicate row contradicts the name. An out-of-scope row follows the polymer-relevance choice. A failed fetch, a silent page, an unreachable source or a spent fetch budget is never a contradiction.
- **Unconfirmed** means the reader could not settle a claim and no source contradicts it. The reader names the fact that would settle it. This is the inherited UNRESOLVED grade; FIELD_ERROR and CREATION_ERROR now require the contradicting source. Unconfirmed claims are reported per field with the count of published values audited in that field as denominator. They never count toward a stop or a gate. There is no ceiling on the unconfirmed share now; the owner sets any ceiling for a draw after the smoke.
- **Gate count k** is the number of audited records (owner, with its scoped children) that have at least one contradicted core field. A record counts once, however many core fields it contradicts.
- **Descriptive fields** are process, market, size (employee bands) and every other published field that is not core. For each, report the error rate and the unconfirmed share. They do not gate. A contradicted descriptive field is reported and never stops the smoke.

## What goes to a reader

Before sampling, inventory the dependencies of every judged field and child. Test the final serialized packet against that inventory. In particular, NAICS attribution needs the actual public source name, source type, code, grain and supporting document. Never mask a value needed to judge another field. Use the [blind-packet addendum](../blind-audit-12-tooling-2026-11-23/PROTOCOL_ADDENDUM_2026-11-23.md) for leak scanning, privacy and exact public-cell approvals. Where a dependency collides with metadata or privacy, supply a clean, independently replayed public witness preserving the full deciding fact. If neither safe literal nor equivalent witness is possible, block packet release and record the dependency. Exercise the gate with a removed source name. Suppress builder family, history, order, control labels and prior verdicts. Report withheld judged literals separately; a placeholder earns no credit.

Fetch once per distinct source/version by script, cache the raw bytes, time, canonical URL, digest and availability status. Both readers receive the same sanitized excerpt and may request further admissible sources through the shared cache within the inherited fetch budget. Replay quoted words in order against main text and check operator, street, date, qualifier and claim grain. Binding alone cannot establish a filing fact.

For every populated filing-backed band, filing NAICS or registry ID, run the [raw-snapshot replay pattern](../pic18-size-10yr-2026-11-23/check.py) before issuing the packet. Verify the store checksum, locate the original filing row, bind identifier and operator to establishment or parent as claimed, and emit the source name, filing period, relevant public values, comparison and replay status. For bands apply the schema’s filing-age cutoff, newer contradictory evidence, establishment headcount, single-site eligibility and source-specific restrictions. Plan participants cannot establish employee count. For NAICS compare the raw code and attribution at that grain. For registry IDs check the issuing registry’s extract and conflicting owners. Test wrong operator, wrong vintage and conflicting identifiers as well as a matched control. Deliver replay receipts and deciding facts to the reader. A failed download or ambiguous match leaves an unresolved claim. A reproduced contrary fact can establish an error. Reconcile the replay inventory to every expected field and child. A missing receipt blocks packet issuance.

## Reading and stopping

Determine builder families privately from record and child provenance plus repair history. Route primary to Astra when independent and to Hydrogen otherwise. Unknown provenance or no eligible primary blocks the run; never drop such records. Keep the Gemini watchdog. Give each reader a fresh short call containing one record and its scoped children; require a complete field/child checklist. Privately mix realistic, separately sourced field swaps into each participating family's queue, exercise the actual reader/replay interface and keep all controls outside the real samples. Stage plant calls ahead of any PASS and interleave with real calls, without announcing their positions. Every control must identify the planted field as erroneous or specifically unsettled on its merits. A missed or missing control invalidates that stage; suspend and diagnose. No replacement draws.

Lock first verdicts before releasing cases to a different family. Flag any error, uncertainty, missing assessment or adverse replay. Bernoulli-check each remaining AGREE independently using the precommitted check coin. Route second reads to another eligible family (prefer Hydrogen for Astra, Astra for Hydrogen, Sonnet when needed). With only the builder available as second family, mark the exception and give its objection evidentiary review; its agreement cannot clear a flag. Require the independent primary plus objective source replay to settle each disputed field. If those cannot settle it, retain UNRESOLVED. The new rule replaces the prior lead sweep. The second reader sees neither flag nor initial verdict. Log a missing required read and hold the decision until delivered or terminate incomplete.

Count each real record exactly once. A contradicted core field on the record or any scoped child puts the record in k. Contradicted descriptive fields and unconfirmed claims are tallied by field and never enter k. An upheld flag cannot be erased by a vote. Verified contradictions take precedence over uncertainty. Missing values are omissions under the inherited rule and are not claims. A clean record requires all applicable checks. Both gates use k. Process completed decisions in sealed order; as soon as the smoke reaches its stop count or the draw exceeds its allowance, cancel the remaining calls and label the unfinished work incomplete. Report the audited denominator, k, contradicted core fields by field, unconfirmed claims by field for core and descriptive fields, the error rate and unconfirmed share of each descriptive field, reason classes, omissions, replay coverage, routing exceptions, check-only discoveries and plant performance. A stopped sample establishes a decision, not an exact population rate.

Under the calibrated option, the controller also seals a separate pre-draw calibration after the owner adopts that option. Sample independent, distinct challenge records from a preregistered mix of repair and error classes at the audited grains. Include hard attribution, filing, field-dependency and child-binding defects. Use a held-out challenge bank independent of the current eligible frame and exclude historical plants. Never remove eligible Atlas rows to assemble the bank. If representative distinct challenges cannot be sourced, return to the owner before calibration. Lock packets, answer keys, scoring and family assignments before releasing calls. Use the production packet and grading path, with blind fresh calls and no disclosure of membership. Score a miss unless the actual planted field is identified under the same criteria as routine controls. The calibrated allowance applies only to these extra trials. Routine smoke and draw controls retain their all-detected gate. Both primary families must qualify before the calibrated draw. A favorable pooled result cannot qualify a failing family.

<!-- sizes begin -->
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
<!-- sizes end -->

## Interpreting the risks and budget

The risk table models independent real-record errors with a common stratum rate and independent detections across records. Each entry is the lower binomial tail at the allowed count with observed adverse probability equal to true error probability times detection probability. Unconfirmed claims are not adverse, so the table does not move with the unconfirmed share. Early failure has the same PASS event as reading the whole planned sample. Smoke can veto the audit but cannot certify the population. The table models the full draw; it gives no finite-population guarantee conditional on a favorable smoke from a fixed population. There is no multiplication of stratum probabilities to claim a joint confidence level.

Calibration uses the frozen prior reader outputs. Within each family join assigned blind packets to the private plant key and returned field verdicts. Credit a returned FIELD_ERROR or UNRESOLVED on the exact altered field, excluding withheld-only explanations. That historical credit accepted UNRESOLVED; under the current unit an unconfirmed plant is not a contradicted error, so those miss rates measure detection of a changed field and may overstate detection of source-contradicted errors. Average miss fractions equally over distinct plants with returns. Repeated calls on one plant are replicates, so the interval uses a two-sided Hoeffding radius over distinct plants. It is a sensitivity interval under independent representative plant clusters, conditional on returns. Plants are purposive field swaps, families share plants and unfinished calls may differ. These intervals cannot validate sensitivity to subtle real errors. The stress column uses the worse primary upper endpoint and gives the second family no rescue credit. The check-share scenario uses the worse primary mean and the worst second-family mean, with independent misses conditional on error. Shared source failures could erase that gain; systematic defects invisible to all readers could evade even the stress model. The stress-safe option often fails a relatively clean Atlas. The calibrated option uses its own pre-draw sensitivity gate and a larger allowance for adverse records. Its confidence limits apply to the challenge distribution; extending them to real defects in every stratum assumes equally good detection there. Neither the old purposive plants nor the new qualification test establish that transfer. If the real-record miss rate stays at the stress value despite qualification, use the stress column for the calibrated draw. Higher apparent power with imperfect reads partly reflects undetected errors.

In the smoke, record k and the per-field unconfirmed counts separately, including filing-replay and missing-dependency reasons. Log tokens from provider request records, including cache reads and retries exactly once, divided by completed real and control calls by provider; charge unsuccessful work to the same ledger. Compare measured mean input, flag share, provider eligibility and projected spend to the scenario before scaling. Short-call savings assume each request carries a bounded packet without prior conversation history. No-output or unmetered work stops. If a provider exceeds its stage budget or measured rates project an overrun, halt for repricing before further calls. Retain the owner’s fan-out controls. Smoke-only spends the first budget and gives no publication decision.
