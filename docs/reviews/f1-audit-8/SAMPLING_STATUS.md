# Audit 8 sampling preparation — blocked before draw

Pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05` (2026-10-30).

The independently reconstructed population comprises **2,199 organization/site
records first introduced in completed integration passes 20–25: 682 organization
records and 1,517 site records**. Record IDs are differenced between each complete
pass and its predecessor. This agrees with `created_by` but does not rely on it.
All statuses are included. Creation tier comes from the complete creation-pass
snapshot, not the current tier. No evidence rows were inspected.

**No random sample has been drawn.** P0–P4 wave classes are missing from the
repository. P001–P036 labels are packet numbers and cannot substitute for those
classes. Pass 20 also includes SC and Q01/Q02 creations; the requested population
therefore needs an explicit `NOT_TRI` class for these records. These rows remain
in the full creation frame but are excluded from the TRI audit draw. A packet number, site count, parent string, or pass
number is not a lawful surrogate for a missing wave class.

## Required input

A public metadata-only CSV mapping `record_id,wave_class`, with P0/P1/P2/P3/P4
(or explicit NOT_TRI) for every eligible organization/site record. If the available
worklist keys only TRIFIDs, a documented record-ID crosswalk and a policy for
organizations linked to facilities in several classes are needed before sampling.
No source notes or previous verdicts should be sent to the verifier.

## Reproducible implementation

`sampler.py --repo <clone> --output-dir <private-output>` reconstructs the population
at the pin, writes sealed metadata and comparison snapshots, and exits 2 without a
draw when the wave map is absent. Pass `--wave-map <mapping.csv>` only after the
mapping and inclusion definition are complete. It uses git objects, never the
mutable working-tree data. The file manifest hashes every pinned data file; evidence
content is hashed, not parsed or displayed.

The planned draw has 65 records, seed
`polymer-atlas-audit8-eceead3-2026-10-30-v1`, and refines creation-tier × wave strata
by record table and the indicator that an organization has exactly one held site at
the pin. One observation is allocated per nonempty refined stratum, then remaining
allocations maximize weighted population size divided by the next allocation;
Tier C receives 3× weight and P4 single-facility organizations 2× weight. Selection
is uniform without replacement inside each stratum. The output records n/N inclusion
probabilities. The script blocks if the refined design has more than65 strata;
allocation may need review against the actual class frame before the first draw.

## Blindness boundary

The sampler can see creation metadata and notes; the verifier must receive only
`identity_only.json` (ID, table, name, site address/locality, associated organization
name and website). Tier, wave, notes, sources and prior verdicts remain in sealed
files until the verifier freezes every independent verdict. Identity/address facts
are unavoidable exposure and are not independent verification evidence. Do not treat
a source-fetch failure as absence. Corrections and comparison grading occur only
after the blind freeze. No record IDs are allocated and no canonical data is edited.

Preparation checked: population reconstruction succeeds; missing-map gate exits
without creating an identity manifest; Python syntax check succeeds. An end-to-end
65-record audit is **not complete** and this file claims no audit rates.
