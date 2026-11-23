# PIC-18 evidence queue (V-65 / V-68) from the NAS lake, 2026-11-22

Lane `atlas-w22-pic18-evidence`. **Applied in this PR:** `apply.py` appended the 123 `packet.csv` rows to `data/evidence_sites_OH.csv` (10) and `data/evidence_organizations_OH.csv` (113) as EVD-482000..482122 (`applied_ids.csv`; lane reserve EVD-482000..482999). `build.py` and `check.py` rebuild the frame as it was before the apply (they leave out the IDs in `applied_ids.csv`).

## Unit and filter
- **Frame (419 records):** the PIC-18 records the validator grandfathers in `scripts/validate_debt_baseline.json`. Sites: `state = OH` and `county` in `scripts/regions.py` PIC18. Organizations: `hq_state = OH` and `hq_county` in PIC18 (the HQ county, not "has a PIC-18 site"; 198 of the 214 organizations also have one). Reconciled by id against `validate.py --debt-details`: every id is in its V-65 / V-68 lines, none missing.
- **V-65** (tier A or B, no supporting row at the tier's strength): 249 = 86 sites + 163 organizations. **V-68** (tier C/U, no evidence row at all): 170 = 119 sites + 51 organizations (2 of the 51 are merged-organization tombstones, which V-68 keeps; 168 without them).
- Region is a parameter (`build.py --region pic18|oh_rest`); nothing else changes between frames.

## Result: records cured of records attempted
"Cured" = the record gets at least one packet row, which clears its V-65 or V-68 line (V-65: any claim at the tier's strength; V-68: any row). Tier `supports_A` rows clear both tiers.

| Rule | Unit | Attempted | Cured |
|---|---|---|---|
| V-65 | sites | 86 | 5 |
| V-65 | organizations | 163 | 62 |
| V-68 | sites | 119 | 0 |
| V-68 | organizations | 51 | 11 |
| **Total** | records | **419** | **78** |

**341 of 419 are not curable by this route.** Reasons (a record can carry several): 189 sites have no civic street (see `sites_without_civic_street.csv`; 74 of them have a held-name record in the same city, a lead for a street route); 106 organizations have no held-name record at their HQ city or an own-site street in OSHA or Form 5500; 28 have only filings older than five years; 26 have only establishment addresses (not an entity's own address); 7 only SAM rows (held). Cure per record: 123 rows for 78 records (1.6 rows per record; the two reverted batches added about 127 per record). 350 candidate rows were **discarded** as a second witness to a claim already witnessed.

## Rows by source and claim (`packet.csv`, 123 rows)
| Source | existence | address |
|---|---|---|
| DOL Form 5500-SF, sponsor mailing address (city and state only) | 51 | 34 |
| DOL Form 5500, sponsor mailing address (city and state only) | 6 | 5 |
| DOL Form 5500-SF, sponsor location address | 1 | 1 |
| OSHA ITA 300A establishment filing | 17 | 4 |
| OSHA establishment inspection | 3 | 1 |

All rows: `source_class = government_filing`, `tier_effect = supports_A` (the class ceiling, controller ruling Q2: the effect describes the witness, not the record). SAM: 25 organization-side matches held; 0 site-side.

## Owner ruling on Q1 (applied)
Owner ruling 2026-11-22 (multiple choice): a Form 5500 mailing address proves **existence and city only**; it never proves a street or a plant location, and the street line is not published. In this packet: `existence` rows from mailing-role filings stand (held legal name, quoted city and state equal the recorded HQ); an organization `address` row from a mailing-role filing claims `hq_city` and `hq_state` only and its quote carries no street line (a location-role filing or an OSHA own-site street still quotes its street); nothing from a mailing address is attached to a site. The 19 street-level mailing candidates the first run held back are **not applied and not in this directory** (they stay in controller storage). Records cured: 78 either way; records with both claims witnessed: 45. 57 of the 78 cured records (46 V-65, 11 V-68, all organizations) rest only on a mailing-role filing.

## Holds and leads
- `held_filer_not_the_record.csv`: **6 organizations** where the filer matches only a trade name of the record, so it may be a different legal entity (an operating subsidiary): ORG-000383, ORG-000391, ORG-000460, ORG-000482 (ParkOhio Holdings, 18 source rows), ORG-001433, ORG-001461. Reason `different_entity_trade_name` (controller ruling Q5). Record-quality lead: a subsidiary's or affiliate's name in a parent's `trade_names`. Natural-person guard (`source_name_looks_like_a_natural_person`: 2-3 name words with no business word, and the record has no website) fired for 0 records on this frame; its text would never be written.
- `leads.csv`: ids, reason and raw locator only (path, row, key). **No third-party name or address is in the repo.** The same leads with filer names (never a natural person's) are in controller storage: `S/persist/pic18-evidence-2026-11-22/leads_with_source_names.csv`.
- `sites_without_civic_street.csv`: the 189 PIC-18 queue sites with no civic street, for a later street route.
- `discards.csv`: the 350 surplus candidates (record, claim, source locator only).

## Binding rules (code: `binding.py`; replayed by `check.py`)
Site: `scripts/derive_last_activity.py same_street` (equal non-empty street keys, civic number, no suite conflict, no PO box), state OH, city or ZIP5 equal (Atlas city's parenthetical second locality accepted), and the source's operator name a held name: exact or held name plus corporate-form words only. A site-name part counts as a held name unless every word is generic (plant, facility, warehouse, main, a number, a compass word, a state, the site's city or county). A recorded parent's name never binds, on any path. A mailing-role source never witnesses a site. Organization: held **legal** name (or its marked alias); quoted city and state equal the recorded HQ, or the street is an own site's street. SCHEMA 4.8 S-5: OSHA establishment addresses, state filings and FMCSA never witness an HQ address. Freshness: `observed_date` is the source record's own date (OSHA inspection open date; ITA `created_timestamp`, else `date_submitted`; Form 5500 `DATE_RECEIVED`); a filing older than five years is never the sole witness (28 records).
**Quote** = the source record's own establishment or entity name plus address line, built by `build.make_row`, never written by a model. No person, phone or e-mail field is read. `notes` carries the raw file path under `raw/`, its sha256 and the 1-based CSV row.

## Checks
- `python3 -I tasks/pic18-evidence-queue-2026-11-22/check.py --file packet.csv --selftest --rehash` (stdlib only, from the repo root): replays every row from `raw/` by path, requires the sha256 equal `raw/MANIFEST.sha256` (`--rehash` re-reads the files), re-derives binding, date, claim-still-missing against current `data/`, one witness per claim, and every shipped text column, and refuses an e-mail or phone-like string. `--selftest` plants six defects and requires each rejected: a row at a different street; a parent-name row (site-name part and organization); a surplus second witness; a claim already witnessed in `data/`; a wrong sha256.
- Result (2026-11-22, `--rehash` of all 11 raw files, after the apply and the mailing ruling): `packet.csv` 123 rows replayed, 0 failures, selftest 6/6 rejected. It replays with the builder's own matcher: that shows the rows can be rebuilt from the raw files, not that the matcher is right.
- `build.py` rebuilds the files (`uv run --with duckdb --with numpy python tasks/pic18-evidence-queue-2026-11-22/build.py`); `inputs.py` writes `INPUTS.sha256` (repo files as at the merge-base with main, before this packet's rows; lake manifest; the raw files cited); `apply.py` is the one-shot apply.

## SCHEMA 4.13 notes
1. A mailing-role address row is a city-and-state claim at the class ceiling `supports_A`: 4.13 has no rule on address role except for ADDRESS_DIFF; the packet sets `address_role` to `mailing`/`physical`.
2. Evidence for an organization's HQ address does not state the county; the row says so (`county ... not stated by the source`).
3. 4.13 has no rule for a filing by a different legal entity named in a record's trade names (Q5; held).

## Outcome line
This work is **not expected to move** the outcome line (PIC-18 unknown shares for process 322 / market 316 / size 443 at 393c389): it adds existence and address evidence, not process, market or size. Before and after: unchanged.

## Rest of Ohio (second frame, not built)
Ohio outside PIC-18, same filter and count (sites by `county` not in PIC-18; organizations by HQ county): **478 records = V-65 330 (116 sites, 214 organizations), V-68 148 (127 sites, 21 organizations).** Only **15 of its 243 sites have a civic street**, so on this route the site side is about as thin as in PIC-18; the organization side (235) is where rows would land. Build only on the controller's word after the PIC-18 PR merges.
