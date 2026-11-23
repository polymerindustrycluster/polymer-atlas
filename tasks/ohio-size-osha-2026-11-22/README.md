# Ohio outside PIC-18 OSHA size bands

The 2026-11-22 owner request extends the #468 size route to sites in named Ohio counties outside PIC-18. The comparator includes organization rows with an active tier A–C site in this region. An organization is size-unknown when all its active tier A–C sites in the region lack a known `employee_band_site` and its `employee_band_ohio` is blank or unknown. The packet frame is those organizations' active tier A–C sites in the region.

## Yield

- Canary, reported before the full pass. Seed `20261122` sampled 25 of the frame's 34 civic-street sites. **0 of 25 sites filled.**
- Full frame. **1 of 367 sites filled, 366 held.** Of the 366 held sites, 332 have no street and one address lacks a civic street. The other 33 holds include 12 with no eligible-location filing, 6 with an unheld operator name, 5 with stale filings, 3 with multiple ITA establishments, 3 individual-looking filers, 2 with a later filing under another name, 1 parent-only name and 1 near-street or locality difference.
- One existing tier-C site and one `government_filing` evidence row with `supports_B`. Ohio-outside-PIC-18 size-unknown organization rows went from **356 to 355 of 564**. Organization data, site tier, and inclusion-log rows are unchanged. PIC-18 unknowns are unchanged.

## Admission and provenance

The #468 extractor reads the 11 OSHA files in `INPUTS.sha256` from the 2026-11-22 archive snapshot. `build.py` calls the #468 matcher with an Ohio-outside-PIC-18 frame, preserves substantive site-name parts, and restricts the name key to case, punctuation and the designated corporate suffixes. The match requires a held operator name on an Ohio filing, an equal civic `street_key`, compatible suites, and corroborating city or ZIP. Holds disclose source paths and row ordinals only. Ambiguous personal names and sole proprietors stay held. The filing window is 2021-11-22 through 2026-11-22.

The controller confirmed that R13 ranks ITA ahead of inspection and chooses the newest filing within each source series. SITE-001083 uses the ITA 2025-12-31 band of **100–249**. Its exact-match inspection on 2026-05-05 gives the adjacent **250–499** band. The packet and site note record that disagreement, and a difference of more than one band would hold the site. I read both raw rows. The ITA filing separately names the held legal operator, which identifies the establishment with its city-labelled branch.

Evidence ID `EVD-481200` was allocated after #468 merged at `8547aed3f93da98fd9b6b7aefa877c8058e30873`. At application, `scripts/atlas.py next-id EVD` reported the tree maximum `EVD-481095`. The next ID above #468's complete reserved range preserves its withdrawn IDs. Pre-pass backups are the Git blobs `9c4edd8e92929227f5cb15a0bb1148b9ec9f276d` (Ohio sites) and `a44949fbdbb16bb15cbed6a47e5b34513710561a` (Ohio site evidence). The hash-checked site apply wrote one band and one notes append. Evidence was appended as one row.

## Replay

From the repository root, set `ATLAS_RAW` to the shared store's `raw/` directory and run

```sh
python3 -B tasks/ohio-size-osha-2026-11-22/check.py --raw "$ATLAS_RAW" --selftest --base 8547aed3f93da98fd9b6b7aefa877c8058e30873
python3 scripts/validate.py
python3 scripts/check_row_loss.py --base 8547aed3f93da98fd9b6b7aefa877c8058e30873
```

The replay enumerates the frame independently from the Ohio shard, verifies all 11 raw SHA-256 digests, checks both raw witness rows by member and ordinal, then rebuilds every decision from the raw extract in memory. Its controls plant a wrong band, a different street, a suite conflict, a stale raw date, a parent-only name, and a conflict beyond one band. Review of live websites and unrelated Atlas records was outside this pass.
