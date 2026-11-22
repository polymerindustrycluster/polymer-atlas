# last_activity street leg — 2026-11-22

**Owner ruling 2026-11-22 (multiple choice): "Fix script, re-derive."** `scripts/derive_last_activity.py` (SCHEMA §4.5, v1.19)
wrote `sites.last_activity_date` / `last_activity_source` from Muse's OSHA extracts, trusting the extract's `match_tier = A`.
That tier meant name + city + state with no street test, so a date could come from a filing at another street. The script's
docstring and SCHEMA §4.5 already say only name + street matches may feed the pair. This PR makes the script do that.

## What changed

- `scripts/derive_last_activity.py`: an extract row is applied to a site only when `same_street(site.street_address,
  extract.street_as_printed)` holds. That is `atlas.street_key` equality (the repo's one street normaliser, `scripts/atlas.py`;
  nothing new was written), with two guards in the caller: the key must open with a house number and have a second token, and a
  blank street is never equal. A site with a blank `street_address` gets no derived date. Defaults now read the two extracts
  from `inputs/` here, so the derivation replays from the repo.
- `data/sites_*.csv`: the two derived columns only, written by the script. **No other column and no row changed** (`check.py` asserts it).
- `scripts/test_derive_last_activity.py`: 5 tests (6 equal pairs, 11 true mismatches, 6 never-equal, 7 pinned known misses, a fixture derivation).
- **SCHEMA: no text changed.** §4.5 already says "Only tier-A (name + street) matches feed the derivation". The v1.19 revision-history entry still
  reads "3,746 of 7,196 sites"; it is history and is left as written.

## Counts (unit: sites, of 7,196 in `data/sites_*.csv`)

| | osha_inspection | osha_ita | sites with a date |
|---|---|---|---|
| before (origin/main, v1.19) | 1,357 | 2,389 | **3,746** |
| after | 959 | 1,662 | **2,621** |
| cleared | 426 | 699 | **1,125** |

Cleared, by reason (one reason per site, first that applies) and source:

| reason | osha_inspection | osha_ita | sites |
|---|---|---|---|
| blank street (site has no `street_address`) | 120 | 329 | 449 |
| no house number (site street has none, e.g. "Chemical Plant Rd") | 21 | 23 | 44 |
| number only (a tier-A row shares the house number, `street_key` differs) | 144 | 199 | 343 |
| different street (no tier-A row shares the number) | 141 | 148 | 289 |
| **cleared** | 426 | 699 | **1,125** |

Of the 2,621 kept: 2,527 keep the identical date and source; **94** keep a date but from the other source, or a different filing,
because the winning row was at another street and a same-street row remained (osha_ita→osha_inspection 61, osha_inspection→osha_ita 33).
Unit for the row counts below: tier-A extract rows (inspection 2,312 + ITA 2,771 = 5,083): 3,392 applied, 1,691 failed the street test;
tier-B rows (2,264) are excluded as before. `CLEARED_SITES.csv` lists every cleared site with its reason, its old date and source, the
site's street and the tier-A streets printed in the extract.

The 449 blank-street sites match the controller's count. The controller's other figures (340 different street, 52 house number only)
counted sites whose winning row was at another street; this table counts sites left with no same-street row, so the splits differ.

## `street_key` against the looser classes

The looser test is `classify` from the 2026-11-22 address-witness audit, classes `exact` and `number+name` (copied into `report.py`).
Re-deriving with it as the street test dates **2,958** sites; `street_key` dates **2,621**.

- **342 sites** are dated only by the looser test; **5 sites** only by `street_key`; **52 sites** are dated by both with a different winning date or source.
- The 342 are mixed: many are true variants `street_key` misses, many are different streets the looser test lets through. Looser class of the 409
  rows behind them: `number+name` 259 (house number and any one name word, so "1070 Evans Ave" passes against "1070 EVANS ROAD"), `exact` 150.
  `LOOSER_THAN_STREET_KEY.csv` has every one.
- The 5 `street_key`-only sites are ordinal spellings ("13th" / "13", "43rd" / "43") and one "&"/"and" street that the looser test's number rule misses.

Ten examples of rows only the looser test passes (every 40th row of `LOOSER_THAN_STREET_KEY.csv`, from the 4th):

| site | site street | extract street | looser class | reading |
|---|---|---|---|---|
| SITE-000117 | 15242 Foltz Industrial Pkwy | 15242 FOLTZ PARKWAY | number+name | name word dropped |
| SITE-001945 | 527 Ternes Ln | 527 TERNES AVE. | number+name | other street type: different street |
| SITE-002655 | 150 Dominion Dr. | 150 SOUTH DOMINION DRIVE | number+name | direction on one side only |
| SITE-003225 | 5414 Us-42 | 5414 US Highway 42 East | number+name | route spelling |
| SITE-004087 | 110 Badger Pkwy | 110 BADGER PARKWAY BDG 5 | exact | "bdg" is not a unit word in the key |
| SITE-004833 | 1230 INDEPENDENCE PARKWAY, SOUTH | 1230 INDEPENDENCE PARKWAY SOUTH NEW UNIT CONSTRUCTION | exact | trailing text |
| SITE-005283 | 250 CHEESEQUAKE RD | Inside DuPont Parlin Site, 250 Cheesequake Road | exact | text before the number |
| SITE-005630 | 3900 DAYTON ST | 3900 WEST DAYTON STREET | number+name | direction on one side only |
| SITE-006072 | 55 W L Runnels Industrial Dr | 55 W.LL. RUNNELS INDUSTRIAL DR. | number+name | initials punctuation |
| SITE-008309 | 222W 33Rd St | 222W 33RD st | exact | `street_key` returns "222w 33 st"; the guard rejects it: no leading digits-only house number |

The last row: the key opens with `222w`, so the "house number first" guard rejects an address that is in fact equal. A guard on the leading
digits (`222`) would keep it. Listed under follow-ups.

## Variants `street_key` misses (proposed follow-ups; street_key is not widened in this PR)

Each pinned in `test_known_misses_stay_rejected`; if the key is widened they flip and the test says so.
number words ("One Plastics Dr" / "1 Plastics Drive"); a number inside a recorded range or list ("1025-1055 W 8th St", "2251/2450/2451 Dix Rd");
a dotted direction pair ("N.E." / "NE"); a `US` prefix on a highway ("US HWY 72"); a direction or street type present on one side only;
state-route spellings ("AL-186" / "SR 186", "OHIO 21" / "State Route 21"); compound words ("Air Park" / "Airpark"); "bdg"/"bld" and a glued
"Suite" / "P.O. Box" after the street type; a house number with a letter ("222W", "61A", "500-A"); one-letter misspellings ("STANDWOOD").
A prototype comparator (not committed) that handled these dated about 300 more sites than `street_key`. Whether to widen the key is a
controller decision; nothing in this PR depends on it.
One finding the other way: `street_key` over-accepts when the unit regex eats the street ("1604 Building" and "1604 Building Barth Street" both key to "1604",
"3206 #6 Road" to "3206"); the caller's second-token guard rejects those.

## Inputs and checksums

`inputs/` holds the two extracts the derivation reads. Original files (controller storage, `persist/osha-extracts-2026-11-22/`):

```
c059aee6da3a163c51aec7112481bdac76f900bc362019a233917e7ef3b987ee  witness_extract_sites_inspection.csv
c58012fbdaaa525a9211c250cc67ac864cb02909b95f736e237749d92e343c08  witness_extract_sites_ita.csv
```

**The committed copies are not byte-identical.** The originals use CRLF; the repo's `.gitattributes` stores every CSV with LF, so the copies are LF. Three `street_as_printed` cells held an individual's contact detail or name (AGENTS §6):
two email addresses (ITA extract lines 400 and 3926) and one "ATTENTION: <person>" line (inspection extract line 2704). They are replaced by
`[REDACTED: email address in the street field]` and `[REDACTED NAME]`; every other byte is unchanged apart from the line endings. The derivation is identical on original
and redacted (checked: same 2,621 sites, same dates, same rejected rows; the email cells are unreadable streets either way). Checksums of the
committed copies are in `inputs/SHA256SUMS`, and `check.py` verifies them.

## Check

`python3 tasks/last-activity-street-leg-2026-11-22/check.py` asserts: inputs match `SHA256SUMS`; re-running the derivation from `inputs/`
gives exactly the data columns; no other column and no row of any sites shard differs from `origin/main`; every dated site has a tier-A extract
row at its street by an independent test (house number found in the quote plus a shared name word, not `street_key`); and the check **fails on a
planted site** that keeps a date with a different street (run: planted SITE-000001 caught). I also ran it against a copy with one other column
edited (`site_name`): caught. `report.py` regenerates `CLEARED_SITES.csv`, `LOOSER_THAN_STREET_KEY.csv` and the counts above.

## Not checked

- No sample of the 1,125 cleared sites was read against the live OSHA record: a cleared site means "no extract row at this street by `street_key`", not "no activity".
  Some are true same-street filings the key misses (see follow-ups), so the cleared list overstates absence; absence asserts nothing (§4.5).
- Muse's own join fix (which uses `street_key` for OSHA matches) is not in this tree; this PR does not depend on it.
- ECHO and FMCSA sources named in the §4.5 vocabulary (`echo`, `fmcsa_mcs150`) are not wired into this script and are untouched.
