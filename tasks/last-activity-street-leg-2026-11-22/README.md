# last_activity street leg — 2026-11-22

**Owner ruling 2026-11-22 (multiple choice): "Fix script, re-derive."** `scripts/derive_last_activity.py` (SCHEMA §4.5, v1.19)
wrote `sites.last_activity_date` / `last_activity_source` from Muse's OSHA extracts, trusting the extract's `match_tier = A`.
That tier meant name + city + state with no street test, so a date could come from a filing at another street. The script's
docstring and SCHEMA §4.5 already say only name + street matches may feed the pair. This PR makes the script do that.

## What changed

- `scripts/derive_last_activity.py`: an extract row is applied to a site only when `same_street(site.street_address,
  extract.street_as_printed)` holds: both `atlas.street_key` values (the repo's one street normaliser, `scripts/atlas.py`; nothing new
  was written) are equal and non-empty, the key has a **civic number** (a token containing a digit, or a leading number word one to ten; not a
  PO box) and at least one more token, and **no suite or unit conflict**: `street_key` discards suites, so where the record and the extract
  both state a suite/unit (`Suite`, `Ste`, `Unit`, `Apt`, `Room`, `Rm`, a non-leading `#`) and they differ, the row is not applied. A site with a
  blank `street_address` gets no derived date. Defaults read the two extracts from `inputs/`, so the derivation replays from the repo.
- `data/sites_*.csv`: the two derived columns only, written by the script. **No other column and no row changed** (`check.py` asserts it).
- `scripts/test_derive_last_activity.py`: 5 tests: equal pairs (incl. SITE-011463, SITE-004620, SITE-004431 and same-suite pairs), true mismatches (incl.
  SITE-000514 and SITE-019015 suite conflicts), never-equal pairs, 7 pinned known misses, and a fixture derivation in which the suite-140 inspection wins over a
  suite-120 ITA row.
- **SCHEMA: no text changed.** §4.5 already says "Only tier-A (name + street) matches feed the derivation". The v1.19 revision-history entry still
  reads "3,746 of 7,196 sites"; it is history and is left as written.

Review round 1 (Codex, 2026-11-22) changed three things against the first head 3b4ac079: the digits-only-first-token rule was replaced by the civic-number
rule (12 sites gain a date, e.g. SITE-011463, SITE-004620, SITE-004431: 2,621 -> 2,633); the suite conflict
rule was added (SITE-000514 loses its date; SITE-019015 takes its suite-140 inspection date: 2,633 -> 2,632); the street cells of two inspection lines holding personal address text were blanked (below).

## Counts (unit: sites, of 7,196 in `data/sites_*.csv`)

| | osha_inspection | osha_ita | sites with a date |
|---|---|---|---|
| before (origin/main, v1.19) | 1,357 | 2,389 | **3,746** |
| after | 966 | 1,666 | **2,632** |
| cleared | 421 | 693 | **1,114** |

Cleared, by reason (one reason per site, first that applies) and source:

| reason | osha_inspection | osha_ita | sites |
|---|---|---|---|
| blank street (site has no `street_address`) | 120 | 329 | 449 |
| suite/unit conflict (equal key, different suites) | 0 | 1 | 1 |
| equal key held: no civic number | 2 | 0 | 2 |
| equal key held: bare number only | 1 | 2 | 3 |
| no house number (site street has none, e.g. "Chemical Plant Rd") | 15 | 19 | 34 |
| number only (a tier-A row shares the house number, `street_key` differs) | 142 | 194 | 336 |
| different street (no tier-A row shares the number) | 141 | 148 | 289 |
| **cleared** | 421 | 693 | **1,114** |

Of the 2,632 kept: 2,536 keep the identical date and source; **96** keep a date but from the other source, or a different filing,
because the winning row was at another street (or another suite) and a same-street row remained (osha_ita→osha_inspection 63, osha_inspection→osha_ita 33).
Unit for the row counts: tier-A extract rows (inspection 2,312 + ITA 2,771 = 5,083): 3,403 applied, 1,680 failed the street test;
tier-B rows (2,264) are excluded as before. `CLEARED_SITES.csv` lists every cleared site with its reason, its old date and source, the site's street and the
tier-A streets printed in the extract. `HELD_EQUAL_KEYS.csv` lists the 9 tier-A rows (8 sites) with equal, non-empty keys that are held: 3 suite conflicts (SITE-000514, SITE-004585, SITE-019015; only
SITE-000514 loses its date; the other two keep or take a same-suite row) and 6 rows on 5 sites that have no civic number to witness a street: four building or park names
(SITE-002182 "BIDA Complex Building 350…", SITE-002988 "1604 Building", SITE-003187 "1790 Building", SITE-005976 "Freeport Center Bldg Z-13") and SITE-003780 ("3206 #6 Road"):
a **`street_key` limit**, since its unit regex strips "#6 Road" and leaves the key "3206", so equality there does not witness a street. `street_key` is not patched here.
The other 12 equal-key sites that review round 1 found dated no longer (Wisconsin grid addresses such as N44 W33341 and W188 N11707, alphanumeric numbers such as 1700A
and 94A, number words such as "One Centro Way", "Spur 119 East") keep their dates under the civic-number rule; each is a test case.

The 449 blank-street sites match the controller's count. The controller's other figures counted sites whose winning row was at another street; this table counts
sites left with no same-street row, so the splits differ.

## `street_key` against the looser classes

The looser test is `classify` from the 2026-11-22 address-witness audit, classes `exact` and `number+name` (copied into `report.py`).
Re-deriving with it as the street test dates **2,958** sites; this rule dates **2,632**.

- **331 sites** are dated only by the looser test; **5 sites** only by this rule; **54 sites** are dated by both with a different winning date or source.
- The 331 are mixed: many are true variants `street_key` misses, many are different streets the looser test lets through. Looser class of the 395
  rows behind them: `number+name` 259 (house number and any one name word, so "527 Ternes Ln" passes against "527 TERNES AVE."), `exact` 136. `LOOSER_THAN_STREET_KEY.csv` has every one.
- The 5 key-only sites are ordinal spellings ("13th" / "13", "43rd" / "43") and one "&"/"and" street that the looser test's number rule misses.

Ten examples of rows only the looser test passes (every 39th row of `LOOSER_THAN_STREET_KEY.csv`, from the 4th):

| site | site street | extract street | looser class | reading |
|---|---|---|---|---|
| SITE-000117 | 15242 Foltz Industrial Pkwy | 15242 FOLTZ PARKWAY | number+name | name word dropped |
| SITE-001945 | 527 Ternes Ln | 527 TERNES AVE. | number+name | other street type: different street |
| SITE-002655 | 150 Dominion Dr. | 150 SOUTH DOMINION DRIVE | number+name | direction on one side only |
| SITE-003225 | 5414 Us-42 | 5414 US Highway 42 East | number+name | route spelling |
| SITE-004161 | 1140 West Grand River | 1140 W GRAND RIVER AVE | exact | street type on one side only |
| SITE-004896 | 4400 VANDALIA RD | Spartech 4400 vandalia Rd pleasant Hill, IA | exact | company name before and city after |
| SITE-005295 | 2200 BAYOU D'INDE | 2200 Bayou D'Inde Pass | exact | "Pass" not in the key's suffix list |
| SITE-005632 | 7015 W PUEBLO | 7015 W. PUEBLO DRIVE | exact | street type on one side only |
| SITE-006072 | 55 W L Runnels Industrial Dr | 55 W.LL. RUNNELS INDUSTRIAL DR. | number+name | initials punctuation |
| SITE-008220 | 1 Chestnut Strear | 1 Chestnut Street | number+name | misspelled street type |

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

**The committed copies are not byte-identical.** The originals use CRLF; the repo's `.gitattributes` stores every CSV with LF. Individual contact detail and
personal address text is removed (AGENTS §6). Redactions, by path:line in the committed copies:
- `inputs/witness_extract_sites_ita.csv` lines 400 and 3926: street cell was an individual's email address; replaced by `[REDACTED: email address in the street field]`.
- `inputs/witness_extract_sites_inspection.csv` line 2702 (SITE-005544): street cell held an individual-associated mailing route; **blanked** (review round 1).
- `inputs/witness_extract_sites_inspection.csv` line 314 (SITE-005449): street cell held residential-address text; **blanked** (review round 1).
- The earlier "ATTENTION: <person>" redaction on an inspection row was reviewed and is superseded by the same treatment; it is `[REDACTED NAME]` in place.

Every other byte is unchanged apart from the line endings. The derivation on the committed copies is **not** identical to the originals: the two blanked rows no
longer match their sites, so those sites carry no date from that row (the re-derived counts above include this). `CLEARED_SITES.csv` line 905 (the same SITE-005544 row)
now carries a blank printed street. Scan of every CSV in this folder (`check.py`): **0 email addresses, 0 phone-number patterns** (formatted 3-3-4 or ten consecutive digits).
Checksums of the committed copies are in `inputs/SHA256SUMS`.

## Check

`python3 tasks/last-activity-street-leg-2026-11-22/check.py` asserts: inputs match `SHA256SUMS`; re-running the derivation from `inputs/`
gives exactly the data columns; no other column and no row of any sites shard differs from `origin/main`; every dated site has a tier-A extract
row at its street by an independent test (civic number found in the quote plus a shared name word, not `street_key`); and the check **fails on a
planted site** that keeps a date with a different street (planted SITE-000001 caught), and that no CSV here holds an email or phone pattern. A copy with one other column edited (`site_name`) is also caught. `report.py` regenerates `CLEARED_SITES.csv`, `LOOSER_THAN_STREET_KEY.csv` and the counts above.

## Not checked

- No sample of the 1,125 cleared sites was read against the live OSHA record: a cleared site means "no extract row at this street by `street_key`", not "no activity".
  Some are true same-street filings the key misses (see follow-ups), so the cleared list overstates absence; absence asserts nothing (§4.5).
- Muse's own join fix (which uses `street_key` for OSHA matches) is not in this tree; this PR does not depend on it.
- ECHO and FMCSA sources named in the §4.5 vocabulary (`echo`, `fmcsa_mcs150`) are not wired into this script and are untouched.
