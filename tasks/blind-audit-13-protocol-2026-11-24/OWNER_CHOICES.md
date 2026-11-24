# Owner choices the 2026-11-24 rulings do not settle

The look-back ruling fixed the unit (a value is wrong only when a source contradicts it; unconfirmed is reported by field, not counted) and the gate (core fields: name, operating status, street, county, polymer relevance; process, market and size report and do not gate). The step-back ruling fixed the frame (PIC-18 only, published values only, an unknown value is not an error). [Rulings](../../DECISIONS.md) · [PROTOCOL.md](PROTOCOL.md) carries one marked placeholder per choice below. The controller seals the protocol only after the owner answers (AGENTS §2 rule 9). Numbers come from `sizes.py` and are checked by its selftest: binomial, independent records, **perfect reads unless the stress column says otherwise**. They measure the choice, not the Atlas: no record was read for this document, and the true core-field error share is unmeasured. The only anchor is audit 12's all-field, old-unit result: 12 of 189 PIC-18 records with a confirmed error (6.3%), 74 of 189 with only an unresolved claim (39.2%).

## 1 · smoke-stop: how many core-field contradictions stop the smoke?

- **A · Stop at the third record with a contradicted core field (recommended).** Same count as sealed in the earlier protocol, now counting only contradictions. At a true core share of 2% / 5% / 8% the smoke reaches its end 95.4% / 67.7% / 36.9% of the time (90.7% at 5% if readers miss 45.9% of errors).
- **B · Stop at the second.** 81.0% / 39.9% / 15.9%. A clean Atlas (2% core) is stopped one time in five.
- **C · Stop at the fourth.** 99.2% / 86.2% / 60.1%. Passes an Atlas at the 8% core share six times in ten.

Why A: the smoke can veto but cannot certify, and the owner asked for it to run once. B stops a good Atlas too often; C lets a clearly failing Atlas through. Token cost does not differ materially (smoke ceiling 4.15M input tokens in all three).

## 2 · descriptive-stop: does a contradicted descriptive field stop the smoke, or is it only reported?

- **A · Only reported, by field, with its error rate and unconfirmed share (recommended).** Matches "process, market and size … do not gate". The smoke's stop count sees core contradictions only.
- **B · Also counts toward the stop.** Under stop-at-third, an Atlas with a 2% core share and a 10% descriptive share reaches the end 13.4% of the time (5% descriptive: 47.2%; 20%: 0.4%). At audit 12's all-field share of 6.3% (core plus descriptive), 52.9%.

Why A: B turns the stop into a descriptive-field gate by another route, and descriptive error shares are the larger and less measured ones. Descriptive results still come back to the owner by field.

## 3 · unconfirmed-ceiling: is there a ceiling on the unconfirmed share?

- **A · No ceiling; report u per field with the smoke and let the owner decide the draw's ceiling afterwards (recommended).** Consistent with "decide after the smoke" and "not counted as an error".
- **B · Ceiling of 12 of 40 records with an unconfirmed core claim (30%).** More than 12 means the smoke returns "inconclusive". At a true 20% unconfirmed share this fires 4.3% of the time; at 39.2% (the old-unit any-field figure, an overstatement for core fields) 84.9%.
- **C · Ceiling of 8 of 40 (20%).** Fires 40.7% at a true 20% and 99.2% at 39.2%.

Why A: audit 12's 39.2% was mostly facts that no page states, which is why the unit changed; a ceiling set now would stop the smoke for the reason the owner removed. The core-only unconfirmed share is unmeasured until the smoke reads. A ceiling changes no token cost.

## 4 · polymer-relevance: how does a reader judge it?

Audit 12 classes: `ring_primary` and `hq_in_scope` were judged (J); `pic_relevance` was withheld builder metadata (W). The owner's term "polymer relevance" maps to the ring and scope test in SCHEMA §3, not to `pic_relevance`.

- **A · Judge `ring_primary` against the SCHEMA ring tests; contradicted when a source shows another ring.** Ring-boundary calls (Ring 1 versus 2 by the PIC rulings, resin production, diversified parents) become reader judgments that count as errors.
- **B · Judge in or out of scope only (recommended).** The reader uses the entity's own site or filing at the record's grain (organization or site) and the SCHEMA §3 exclusions. Contradicted only when a source shows no polymer, rubber, coating or comparable on-site activity at that grain (polymer only as packaging or a purchased part, retail only, a different entity). A different ring number is not a contradiction; it is reported as a descriptive note.
- **C · No reader judgment.** Relevance is checked by script from NAICS, process and material fields. Contradicted only when the script's rule fails. Fast, but it tests the Atlas's own fields against each other, not a source.

Why B: it tests the claim the PIC-18 bar cares about (is this a polymer entity at all) without converting classification nuance into errors, the same failure the unit change targets. No sizes.py number exists for this choice: the contradiction rate is unmeasured, and the smoke is what measures it.

## Not asked now

- **Plant credit.** The historical miss rates counted an UNRESOLVED return on the planted field as detected. Under the new unit that is not a source-contradicted error, so detection of real contradictions may be lower than modeled. Routine smoke controls still need the planted field flagged as erroneous or specifically unsettled. Revisit before any draw.
- **Draw rules** (stress-safe 265 records or plant-calibrated 583) are unchanged except that they now gate on core-field k for PIC-18 only. Totals fell because the other strata left the frame. The owner decides after the smoke.
- **Second reads** still go to every flagged record, including one flagged only for an unconfirmed claim. That is cost, not a gate; say if a descriptive-only flag should skip the second read.

<!-- choice figures -->
### Smoke options (owner choices smoke-stop, descriptive-stop, unconfirmed-ceiling)

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
