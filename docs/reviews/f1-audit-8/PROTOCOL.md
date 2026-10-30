# Audit 8 protocol — frozen before verification

Pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05` (main, 2026-10-30).
Task: F1, passes 20–25 organization and site creations. Packet only; no canonical edits, ID allocation, merges, or main pushes.

## Blindness

An independent sampler examines creation provenance and stratifies the population. The verifier receives only record ID/table, name, address, associated organization identity, and optionally website domain. These are search keys, not independent evidence. Creation tiers, wave labels, source notes, record evidence rows, and prior verdicts remain sealed until all independent verdicts are frozen and hashed. The verifier necessarily knows the candidate identity and candidate location. This is evidence-blind re-verification, not identity-blind research. Schema and task text were read before sampling; they contain historical examples and audit aggregates, not sampled-row evidence.

## Independent verification

Each sampled record receives VERIFIED, REJECT with deciding fact, STILL_UNCERTAIN with the named settling fact, or DUPLICATE_OF terminating at a held record. Approximately six primary-source fetches per organization are available; search results route retrieval but unopened snippets are not evidence. Every substantive witness is named with URL and observation date; dated filings retain their own date. Failed routes are logged as availability failures, never evidence of absence. No closure/no-establishment REJECT is permissible without the Form 5500 establishment-address check. Scope/grain rulings remain owner-only, not decided by this audit.

VERIFIED means the independently observed existence and polymer-scope claim is supported at the stated grain; separately record which identity, address, scope, operator, liveness and code facts are supported or remain unresolved. Do not turn missing optional enrichment into an error. Do not interpret an active company website as proof every historical plant is active.

## Post-freeze grading

Only after frozen verdicts may the comparison examine original record fields/evidence. Grade agreement, field error (named field and settling witness), creation error, or unresolved. Unresolved is essential: inability to independently settle a fact is not agreement and is not an error. A verified in-scope existence can still have a field error. Creation error requires positive evidence that the record should not have been created at its grain/in scope (not simply a dead page). Count one mutually exclusive primary grade per sampled record, with multiple field findings separately enumerated. Field error and creation error grades require a positive settling source; protocol/evidence-contract gaps can be reported separately without inflating factual-error rates.

## Reporting

Report raw per-stratum denominators and outcomes, population coverage, sampling probabilities, and descriptive sample rates. If estimable, population-weighted rates are separate from raw oversampled rates. Unresolved cases remain in the full-sample denominator and their share is shown, with resolved-only rates clearly labeled. Historical comparisons: audit 6 supplied baseline 0/37 creation errors and 12/37 field errors; audit 7 supplied baseline 58/65 agreement. Different populations, sampling methods, evidence availability and observation times prevent a causal trend claim.

## Integrity gates

Pinned validation and SQLite build pass before verification. Final packet must reproduce sample, have one verdict per sample row, ensure all cited files are under docs/reviews (queue claim excepted), and prove zero data diff. Final main SHA recheck flags any drift without absorbing it. Corrections are proposals for the integrator only.
