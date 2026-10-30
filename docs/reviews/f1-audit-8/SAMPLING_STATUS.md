# Audit 8 — sampling method and frozen draw

**Draw frozen:** 2026-10-30 22:59:07 UTC. **65 distinct records**, distributed to
five verifier batches of 13 records each. Organizations are not split across batches,
so their shared ~6-primary-fetch budget can be enforced. This is sampling preparation,
not an audit result; no agreement/error rates are asserted here.

## Pins and population

Creation-data pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`.
Authoritative class-map v2 pin: `bf7857a7826ba62cdcf67af3ba718c3d5a9b32be`,
`tasks/f1-class-map/f1_record_tri_class_mapping.csv`. Later map publication changes
metadata only; canonical data remained unchanged. The sampler does not absorb later
main data silently. Map SHA-256:
`86e78616b3c4aac23ceb143fd724acc3e287a64ce9b9071b08088249ec0b8fd7`.

The full frame comprises **2,199 distinct organization/site records first introduced
in integration passes 20–25: 682 organizations and 1,517 sites**. Git ID-set first
appearances reconstruct this frame independently of allocation-file row counts.
Creation tier is read at the actual first-appearance commit, not the current tier;
these tiers also matched all complete-pass snapshots. All statuses are included.
The authoritative map's IDs and creation passes must match this reconstruction.

The TRI-only eligible frame contains **1,972 distinct records**. Explicit NOT_TRI
rows (227, all pass 20 SC/Q01/Q02 creations) are excluded, not assigned a synthetic
TRI class. Eligible class counts: P1=417, P2=180, P3=771, P4=604. **P0=0** because
P0 created links on already-held records, not records; it has no creation stratum.
An audit of those links would need a separately authorized frame.

## Deterministic allocation and draw

Frozen seed: `polymer-atlas-audit8-eceead3-2026-10-30-v1`.

Strata are creation tier × TRI wave class, refined by record table and whether an
organization has exactly one held site at the creation-data pin. This last indicator
uses all held sites at the pin, without a status exclusion; it is not inferred from
the organization's name. The P4 class itself is the creating facility's worklist
priority class, as supplied by the orchestrator, not a guessed site-count proxy.

Allocate one observation to each nonempty refined stratum. Allocate the remaining
observations until n=65 by maximizing weighted population size divided by the next
allocation, with deterministic tuple-order tie breaking. Tier C receives 3× weight;
P4 single-facility organizations receive 2× weight (multiplicative when both apply).
Population-size caps prevent allocating more records than a stratum contains.
Select uniformly without replacement from record-ID-sorted members of each stratum,
then shuffle the selected records using the same Python `random.Random` instance.
Every selected record has inclusion probability n_h/N_h, recorded in sealed output.

The sample was drawn **once**, after valid v2 metadata arrived. No provisional sample
was drawn while wave metadata was missing or while duplicate-map correction awaited
approval. An unchanged deterministic reproduction is not a new sample selection.

## Reproduction and blindness

From this branch, materialize the map at its exact pin, then run:

```sh
git show bf7857a7826ba62cdcf67af3ba718c3d5a9b32be:tasks/f1-class-map/f1_record_tri_class_mapping.csv > /tmp/f1-map-v2.csv
python docs/reviews/f1-audit-8/sampler.py --repo . --wave-map /tmp/f1-map-v2.csv --output-dir /tmp/f1-reproduction
```

The sampler reads git objects, never mutable working-tree data. It records SHA-256
hashes of pinned data files; evidence content is hashed, not parsed or displayed.
The sampler can see creation metadata/notes. Verifiers receive only
`identity_only.json` or their `identity_batch_N.json`: ID, table, name, physical
site address/locality, associated organization name and website. These identity
facts are unavoidable exposure and are not independent verification evidence.
Sources, notes, tiers and the per-record class manifest were withheld until every independent
verdict was frozen. A post-freeze transparency note in `BLINDNESS_LIMITATION.md` records
possible Carlstar P3 exposure through inherited owner instructions, not through the sampler. `DRAW_MANIFEST.json` publishes hashes without revealing those
values. No record IDs are allocated; no canonical data is edited.

## Map correction before sampling

Map v1 (`65dc7d4f2810b144d6fdc6e377c6bc07b7e6cf89`) contained 2,204 rows but only
2,199 distinct IDs. Five `org_create_watch` marker rows duplicated ordinary creations
(ORG-004131, ORG-004218, ORG-004229, ORG-004252, ORG-004288). The independent
sampler's original 2,199 frame already included all five. The owner confirmed the
error, retracted the claim that the sampler omitted them, and supplied corrected v2.
All duplicate pairs were identical; P3 dropped from 776 CSV rows to 771 records.
No draw used the faulty duplicate-weighted frame.

## Checks

- Full frame 2,199 unique IDs; organization 682/site 1,517.
- Exact map/frame ID sets and per-record creation-pass correspondence.
- Eligible stratum populations sum to 1,972; selected IDs 65 unique.
- Five batches of 13; union equals the sample; no associated organization overlaps
  batches.
- Missing-map gate produces no identities; conflicting/unauthorized duplicate map
  rows fail before sampling.
