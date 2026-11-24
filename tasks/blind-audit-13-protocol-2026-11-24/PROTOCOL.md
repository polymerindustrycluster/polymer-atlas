# Proposed blind audit after repairs

**Owner ruling required before sampling.** The first decision is whether the post-repair Atlas merits a full audit. A clean smoke permits the draw only under the full-audit option. Publication requires a PASS in every stratum.

## Population and custody

Use the [preceding protocol’s approved frames, footprint precedence, placement exceptions, published-field classes, child scope and grade definitions](../blind-audit-12-protocol-2026-11-23/PROTOCOL.md). At a fresh repaired main commit, reconcile unique records and all exclusions to the pinned tables and site/export surfaces. Update the field inventory for current published facts, including process and material other-notes. Use the vocabulary and ring restrictions at that commit. A missing field classification or unexplained population change blocks sampling. The [owner’s lean-design, review-routing and vocabulary rulings](../../DECISIONS.md) govern this revision.

After approval, the controller seals the commit, protocol, sizes, packet/replay code, frame digest, randomization method and fresh secret commitment before seeing outcomes. For smoke, take an equal-probability sample without replacement from the cluster stratum. Keep that selection private. On a go decision only, sample uniformly without replacement within each remaining stratum, excluding smoke IDs. Use independent keyed orderings for smoke, draw, plants, check coins and display order. Assert no duplicate or overlapping units, sufficient remaining population and equal inclusion probability within each eligible frame. If a stratum is too small, return for a revised calculation. No repairs between smoke and draw, substitutions, or retries on the same snapshot. On repair, start a new sealed attempt. Privately link the audit receipts; publish only aggregate results.

## What goes to a reader

Before sampling, inventory the dependencies of every judged field and child. Test the final serialized packet against that inventory. In particular, NAICS attribution needs the actual public source name, source type, code, grain and supporting document. Never mask a value needed to judge another field. Use the [blind-packet addendum](../blind-audit-12-tooling-2026-11-23/PROTOCOL_ADDENDUM_2026-11-23.md) for leak scanning, privacy and exact public-cell approvals. Where a dependency collides with metadata or privacy, supply a clean, independently replayed public witness preserving the full deciding fact. If neither safe literal nor equivalent witness is possible, block packet release and record the dependency. Exercise the gate with a removed source name. Suppress builder family, history, order, control labels and prior verdicts. Report withheld judged literals separately; a placeholder earns no credit.

Fetch once per distinct source/version by script, cache the raw bytes, time, canonical URL, digest and availability status. Both readers receive the same sanitized excerpt and may request further admissible sources through the shared cache within the inherited fetch budget. Replay quoted words in order against main text and check operator, street, date, qualifier and claim grain. Binding alone cannot establish a filing fact.

For every populated filing-backed band, filing NAICS or registry ID, run the [raw-snapshot replay pattern](../pic18-size-10yr-2026-11-23/check.py) before issuing the packet. Verify the store checksum, locate the original filing row, bind identifier and operator to establishment or parent as claimed, and emit the source name, filing period, relevant public values, comparison and replay status. For bands apply the schema’s filing-age cutoff, newer contradictory evidence, establishment headcount, single-site eligibility and source-specific restrictions. Plan participants cannot establish employee count. For NAICS compare the raw code and attribution at that grain. For registry IDs check the issuing registry’s extract and conflicting owners. Test wrong operator, wrong vintage and conflicting identifiers as well as a matched control. Deliver replay receipts and deciding facts to the reader. A failed download or ambiguous match leaves an unresolved claim. A reproduced contrary fact can establish an error. Reconcile the replay inventory to every expected field and child. A missing receipt blocks packet issuance.

## Reading and stopping

Determine builder families privately from record and child provenance plus repair history. Route primary to Astra when independent and to Hydrogen otherwise. Unknown provenance or no eligible primary blocks the run; never drop such records. Keep the Gemini watchdog. Give each reader a fresh short call containing one record and its scoped children; require a complete field/child checklist. Privately mix realistic, separately sourced field swaps into each participating family's queue, exercise the actual reader/replay interface and keep all controls outside the real samples. Stage plant calls ahead of any PASS and interleave with real calls, without announcing their positions. Every control must identify the planted field as erroneous or specifically unsettled on its merits. A missed or missing control invalidates that stage; suspend and diagnose. No replacement draws.

Lock first verdicts before releasing cases to a different family. Flag any error, uncertainty, missing assessment or adverse replay. Bernoulli-check each remaining AGREE independently using the precommitted check coin. Route second reads to another eligible family (prefer Hydrogen for Astra, Astra for Hydrogen, Sonnet when needed). With only the builder available as second family, mark the exception and give its objection evidentiary review; its agreement cannot clear a flag. Require the independent primary plus objective source replay to settle each disputed field. If those cannot settle it, retain UNRESOLVED. The new rule replaces the prior lead sweep. The second reader sees neither flag nor initial verdict. Log a missing required read and hold the decision until delivered or terminate incomplete.

Count each real record exactly once. A demonstrated error on any in-scope field or child goes in k; absent a demonstrated error, any unsettled claim goes in u. An upheld flag cannot be erased by a vote. Verified contradictions take precedence over uncertainty. Missing values are omissions under the inherited rule. A clean record requires all applicable checks. Use k+u at both gates. Process completed decisions in sealed order; as soon as a stratum fails, cancel its remaining calls. Since one failed stratum precludes exit, cancel the remaining draw at the first decisive failure and label unfinished strata incomplete. Report audited denominator, k, u, reason classes, omissions, replay coverage, routing exceptions, check-only discoveries and plant performance. A stopped sample establishes a decision, not an exact population rate.

<!-- sizes begin -->
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
<!-- sizes end -->

## Interpreting the risks and budget

The risk table models independent real-record errors with a common stratum rate and independent detections across records. Each entry is the lower binomial tail at the allowed count with observed adverse probability equal to true error probability times detection probability. Taking unsettled records as adverse can only lower PASS relative to the table if real flags are retained. Early failure has the same PASS event as reading the whole planned sample. Smoke can veto the audit but cannot certify the population. The table models the full draw; it gives no finite-population guarantee conditional on a favorable smoke from a fixed population. There is no multiplication of stratum probabilities to claim a joint confidence level.

Calibration uses the frozen prior reader outputs. Within each family join assigned blind packets to the private plant key and returned field verdicts. Credit a returned FIELD_ERROR or UNRESOLVED on the exact altered field, excluding withheld-only explanations. Average miss fractions equally over distinct plants with returns. Repeated calls on one plant are replicates, so the interval uses a two-sided Hoeffding radius over distinct plants. It is a sensitivity interval under independent representative plant clusters, conditional on returns. Plants are purposive field swaps, families share plants and unfinished calls may differ. These intervals cannot validate sensitivity to subtle real errors. The stress column uses the worse primary upper endpoint and gives the second family no rescue credit. The check-share scenario uses the worse primary mean and the worst second-family mean, with independent misses conditional on error. Shared source failures could erase that gain; systematic defects invisible to all readers could evade even the stress model. Full sample sizes deliberately trade a high chance of failing a relatively clean Atlas for low modeled false-pass risk.

In the smoke, record k and u separately, including filing-replay and missing-dependency reasons. Log tokens from provider request records, including cache reads and retries exactly once, divided by completed real and control calls by provider; charge unsuccessful work to the same ledger. Compare measured mean input, flag share, provider eligibility and projected spend to the scenario before scaling. Short-call savings assume each request carries a bounded packet without prior conversation history. No-output or unmetered work stops. If a provider exceeds its stage budget or measured rates project an overrun, halt for repricing before further calls. Retain the owner’s fan-out controls. Smoke-only spends the first budget and gives no publication decision.
