# Polymer Atlas v2026.11.14

A dated snapshot of the Polymer Industry Atlas: the SQLite database, merged CSV exports, every single-file table and a
Frictionless `datapackage.json`, zipped with a SHA-256 checksum manifest. Everything is generated from the canonical
CSVs in `data/`.

- Git commit: COMMIT
- Date: 2026-11-14 (America/New_York)
- License: the compiled data is CC BY 4.0 (root `LICENSE`); scripts are MIT. Licensed discovery sources (Plastics
  News, Rubber News, D&B and similar) and PIC CRM content are not republished in this bundle.

## Counts (unit named on every line; all statuses and all verification tiers)

- 5,026 parent-organization rows (all HQ states and statuses)
- 7,196 site/establishment rows; headline cut (operating status active, tiers A–C): 6,482 site rows, 1,488 of them
  in Ohio and 881 in the 18 PIC counties
- 41,575 evidence rows (one claim-source observation each)
- 408 Ring 5 ecosystem-entity rows; 216 education/training program rows
- 1,513 people rows (professors and federal-lab research staff; public professional facts only) and 816 person
  external-identifier rows (ORCID)
- 5,448 external registry-link rows; 360 relationship edge rows; 526 site-capability rows; 88 equipment rows
- 71 event-series rows and 1,296 organization-level event-participation rows

These are row counts, not counts of active companies or unique ultimate parents. Full per-table counts with units are
in `COUNTS.md` inside the bundle.

## Quality

A blind sample audit of the records changed in the 2026-11-09 to 2026-11-12 work (`docs/reviews/BLIND_AUDIT_10_2026-11-14.md`):
of 50 sampled records, 45 agreed with their public sources, 2 had field errors (both corrected), 0 should not have
existed, and 3 remain unresolved. The design-weighted confirmed-error rate is 4.6% (95% interval about 1.3% to 15.5%).

## Verify the download

Unzip, then inside the folder run `sha256sum -c MANIFEST.sha256` (or `shasum -a 256 -c MANIFEST.sha256` on macOS);
every file should report OK.
