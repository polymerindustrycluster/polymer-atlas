# Release preparation (2026-11-12) — do not publish

This is preparation only. Cutting a GitHub Release is an owner action (`docs/RELEASE_HOWTO.md`). No tag was created and nothing was uploaded.

## Already in place
- `docs/RELEASE_HOWTO.md` describes the owner steps: clean `main`, `python3 scripts/validate.py`, `python3 scripts/build_sqlite.py`, `python3 scripts/export_release.py`, then tag `vYYYY.MM.DD` and `gh release create` with the zip. Agents do not tag, publish, or upload.
- A root `LICENSE` file is already in the repository (the how-to still says "the repository has no LICENSE file at the time of writing"; that sentence is stale). The README licensing section already states CC BY 4.0 for the compiled data and MIT for the scripts.
- Optional Zenodo and Hugging Face mirrors remain owner decisions and were not enabled.

## Suggested owner steps when cutting the first release
1. Checkout a clean commit of `main` (not a dirty or mid-PR tree).
2. Recompute inventory counts from the CSVs (or copy the README inventory paragraph, which this pass refreshes) and confirm `python3 scripts/validate.py` passes.
3. Run `python3 scripts/export_release.py`. Confirm the zip name is `polymer-atlas-release-<date>-<sha>.zip` and does not end in `-dirty`. Check `build/release/COUNTS.md` units and `sha256sum -c MANIFEST.sha256`.
4. Tag `v2026.11.12` (or the calendar date of the cut). If two releases land on one day, add a suffix rather than moving the tag.
5. Publish with notes that state the git commit, the date, the counts-with-units from COUNTS.md, and the license (CC BY 4.0 data / MIT scripts). Nothing from Plastics News, D&B, Data Axle, ZoomInfo, CB Insights, Rubber News rankings, or the PIC CRM may ride in the bundle.

## Draft release-notes skeleton (fill counts from COUNTS.md at cut time)

Title: Polymer Atlas vYYYY.MM.DD

This is a dated snapshot of the Polymer Industry Atlas: the SQLite database, merged CSV exports, single-file tables, and a Frictionless datapackage.json, with a checksum manifest.

- Git commit: <sha>
- Date: <America/New_York date>
- Counts (copy units from build/release/COUNTS.md; do not quote bare "companies")
- License: compiled data CC BY 4.0; scripts MIT
- Licensed discovery sources and PIC CRM content are not republished in this bundle

Inventory counts recomputed from the canonical CSVs on 2026-11-12 at head 4eba6f4968429e4387da6872aecae1b5b355ffac, before this pass's own data PRs, were: 5,024 organization rows, 7,190 site rows, 408 ecosystem rows, 1,496 people rows, 213 program rows, 5,444 registry-link rows, 41,101 evidence rows. Headline cut (operating status active, tiers A–C): 6,476 site rows — 1,488 in Ohio, 881 in the PIC-18 counties. Recompute at the tagged commit; Muse academic merges can move people, programs, and evidence counts.
