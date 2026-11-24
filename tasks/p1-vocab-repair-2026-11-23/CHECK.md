# Named checks

Run from the repository root. The pre-pass Git ref is
`d69c4099dd08ecf7a14f762e3328718438bb0fe9`.

## a. V-55 and validator

`lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py --debt-details`

- Pre-pass: `WARN  V-55: 2884 baselined rows still violate` and
  `OK — validation passed.`
- Post-pass: `OK — validation passed.` with no V-55 entries. The independent
  census matched the pre-pass baseline record IDs and found zero residuals.
- `python3 scripts/export_vocab.py --check` reports the export is current.

## b–c. Conservation, mutation and scope

`python3 tasks/p1-vocab-repair-2026-11-23/check.py`

```text
organizations: 5026 rows in 50 shards; 114 rows with capability or other-note value changes
  processes: 3 kept, 0 exact re-encoded, 118 moved verbatim, 145 Ring 3 admitted
  materials: 12 kept, 0 exact re-encoded, 26 moved verbatim, 0 Ring 3 admitted
sites: 7196 rows in 50 shards; 2415 rows with capability or other-note value changes
  processes: 360 kept, 0 exact re-encoded, 2799 moved verbatim, 243 Ring 3 admitted
  materials: 669 kept, 0 exact re-encoded, 2492 moved verbatim, 0 Ring 3 admitted
V-55 records: 2884 before, 0 after; 2529 repaired, 355 cleared by Ring 3 admission alone
PASS: all changed rows accounted for, shard IDs/counts stable, unrelated cells unchanged
```

Kept counts are original token occurrences in changed cells. Ring 3
admissions count previously out-of-vocabulary tokens retained across
all records with primary Ring 3, including records with no cell edit.
The replay covers all 2,529 value-edited records and checks both fields
on all organization and site records. It checks synthetic exact
re-encoding (comma and “and” splits, case, separators and secondary
suffixes) because none of the pre-pass off-vocabulary values in either
field had a complete exact match under the two rulings. Mixed wording
was preserved in full.

`python3 tasks/p1-vocab-repair-2026-11-23/check.py --inject-drop` exits 1.

```text
Injected loss in data/organizations_NJ.csv ORG-001489 processes_other_note
data/organizations_NJ.csv ORG-001489: processes_other_note lost or added verbatim wording
```

`python3 tasks/p1-vocab-repair-2026-11-23/build.py` on the repaired tree
reports `0 organization or site shard files rewritten`.

## d. PIC-18 process unknown

```sh
env -u GH_TOKEN -u GITHUB_TOKEN python3 /Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/harness/pic18_unknown.py "$PWD" HEAD
```

PIC-18 parent organizations with active tier A–C Ohio sites: 305 of 792
process unknown at the base, 332 of 792 (41.9%) after the repair. Market
and employee-band unknowns are 303 and 372 of 792 on both trees.

The expected 330 is reproduced if the Ring 3 tokens are accepted on
all rings. The exact two additional unknowns are Ring 1
`ORG-000211` (`tooling_mold_die (secondary)` on the parent and
`SITE-000224`) and Ring 1 `ORG-000214` (`machinery_equipment (secondary)`
on the parent). Both values are preserved verbatim in their corresponding
other-notes under the Ring 3-only ruling. All other parent classifications
agree between the two computations.

## e. Site and release

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -m unittest \
  scripts/test_build_site.py scripts/test_site_release.py \
  scripts.test_validate.ValidatorMutationTests.test_v55_process_token_out_of_vocab \
  scripts.test_validate.ValidatorMutationTests.test_v55_ring3_subtype_process_scope
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/build_pages.py
lockf -k /tmp/polymer-atlas-heavy.lock env -u GH_TOKEN -u GITHUB_TOKEN python3 scripts/export_release.py
```

- All 128 tests passed, including the Ring 3 validator mutation and the
  planted build-wording combinations for both release note columns.
- The page build wrote 5,554 HTML files. The release export produced the
  ZIP and passed its consistency guard.
- The four capability-note columns matched release CSV to SQLite per
  record ID, across 5,026 organizations and 7,196 sites. The build-prose
  lexicon found zero hits in the release note columns. The wider watch
  list flagged the word “carried” in `fluorescent pigments (resin-carried
  colorants)`, which describes the material on `SITE-003847`.
