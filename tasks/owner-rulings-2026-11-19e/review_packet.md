# Review: 3 `year_founded` fills from GLEIF (owner ruling 2026-11-19e)

**Your job: try to REFUTE each fill.** Answer per row `SOUND`, `DOUBT` or `WRONG` with one line of reason, then an overall verdict. Judge only from the facts below.

**Rules in force.**
- SCHEMA `year_founded`: "Legal-entity formation year where a source states it". Owner ruling 2026-11-19: the formation year of the legal entity the record describes, even when the business is older or the entity was later renamed (older business year goes in the note). Not covered: a conversion, a re-incorporation into a new entity, a predecessor's charter, or a placeholder date.
- #406 used GLEIF `entity.creationDate` only when GLEIF's legal or HQ address named the organization's HQ city and state. These three failed that gate. Owner ruling 2026-11-19e: a second source's SAME verdict (Muse, 2026-11-19) plus a re-read quote from the company's own page may stand in for the address gate.
- Registry evidence caps at `supports_B`; none of these organizations is tier A.

## ALPLA Inc. (ORG-000664) → year_founded 2001

- **Our record:** legal name "ALPLA Inc."; HQ field Lima, OH; tier B; website https://www.alpla.com/.
- **GLEIF 549300GL8XWPNYKSXX74:** legal name "ALPLA INC."; jurisdiction US-GA; registeredAs 0112452; entity status ACTIVE; LEI registration LAPSED; creationDate 2001-03-14; previous legal names: none.
- **GLEIF addresses:** legal C/O CORPORATION SERVICE COMPANY, 2 SUN COURT, SUITE 400, PEACHTREE CORNERS, US-GA; HQ 289 Highway 155 South, McDonough, US-GA.
- **GLEIF field-modification history:** the creation date was never changed to a different value (the history starts at LEI issuance and cannot see earlier corporate history).
- **tie quote** (2026-11-20 tinyfish fetch): "ALPLA INC. Regional HQ | 289 Highway 155 South 30253 MC Donough GA" — https://www.alpla.com/en/company/global-presence?country=United%20States%20of%20America
- **tie quote** (2026-11-20 tinyfish fetch (Muse quote; re-read 2026-11-19 by check_part2.py)): "ALPLA INC. Base Plant | 3320 Fort Shawnee Industrial Drive 45806 Lima Ohio" — https://www.alpla.com/en/company/global-presence?country=United%20States%20of%20America
- **year quote** (2026-11-20 tinyfish fetch): "ALPLA North America was established and headquartered in McDonough Georgia in 2001." — https://www.alpla.com/en/north-america

## Molten North America Corporation (ORG-000965) → year_founded 1990

- **Our record:** legal name "Molten North America Corporation"; HQ field Findlay, OH; tier C; website https://www.molten.co.jp/.
- **GLEIF 549300RM25BXTF73R043:** legal name "Molten (North America) Corporation"; jurisdiction US-OH; registeredAs 783787; entity status ACTIVE; LEI registration LAPSED; creationDate 1990-11-01; previous legal names: none.
- **GLEIF addresses:** legal C/O CT CORPORATION SYSTEM, 4400 EASTON COMMONS WAY, SUITE 125, COLUMBUS, US-OH; HQ 1300 East 9th Street, Cleveland, US-OH.
- **GLEIF field-modification history:** the creation date was never changed to a different value (the history starts at LEI issuance and cannot see earlier corporate history).
- **tie quote** (2026-11-20 tinyfish fetch (Muse quote; re-read 2026-11-19 by check_part2.py)): "Molten (North America) Corporation | | 1) | Company Outline ... 2) | Location | | | (1) | Findlay, Ohio, U.S.A." — https://www.molten.co.jp/english/autoparts/plant/index.html
- **year quote** (2026-11-20 tinyfish fetch): "Molten (North America) Corporation extended its business to the largest automobile market in the world, the United States, in December 1991." — https://www.molten.co.jp/english/autoparts/plant/index.html

## Storopack, Inc. (ORG-001128) → year_founded 1978

- **Our record:** legal name "Storopack, Inc."; HQ field Cincinnati, OH; tier B; website https://www.storopack.us/.
- **GLEIF 549300UCYIXHJ7CBMB49:** legal name "Storopack, Inc."; jurisdiction US-DE; registeredAs 849492; entity status ACTIVE; LEI registration ISSUED; creationDate 1978-02-08; previous legal names: none.
- **GLEIF addresses:** legal C/O The Corporation Trust Company, Corporation Trust Center, 1209 Orange Street, Wilmington, US-DE; HQ Corporation Trust Center, 1209 Orange Street, Wilmington, US-DE.
- **GLEIF field-modification history:** the creation date was never changed to a different value (the history starts at LEI issuance and cannot see earlier corporate history).
- **tie quote** (2026-11-20 tinyfish fetch (Muse quote; re-read 2026-11-19 by check_part2.py)): "Storopack Inc. 4758 Devitt Drive Cincinnati" — https://www.storopack.us/imprint/
- **year quote** (2026-11-20 curl + pdftotext): "1978 Start of business activities in the USA." — https://www.storopack.com/fileadmin/user_upload/DI_EN-US_Fact_Sheet_web.pdf

## Held before review (for context; tell us if any hold is wrong)

- Sealed Air Corporation (ORG-000566), GLEIF 1996-01-29: HELD: Sealed Air's own 10-K says it 'was incorporated in Delaware in 1960'; GLEIF dates Delaware file 2586601 to 1996-01-29. A possible successor or reorganization, which the formation-year ruling does not cover
- Plastipak Packaging, Inc. (ORG-001033), GLEIF 1982-05-24: HELD: owner ruling 2026-11-19e: Plastipak's only web quote is a third-party page (ndt.org)
- Ridge Corporation (ORG-001080), GLEIF 1994-02-14: HELD: Ridge's own site says it 'was incorporated in 2004'; GLEIF gives 1994-02-14 under the former name Techna Composites Incorporated (Ohio charter 864734). Ohio SOS was in maintenance on 2026-11-20, so the charter could not be read
- MSI Express Inc (ORG-001471), GLEIF 1998-12-31: HELD: MSI Express's FAQ says it was 'formed through the merger of Express Packaging (founded in 1988) and Manufacturing Solutions International (founded in 2008)'; GLEIF's 1998-12-31 is a year-end date (the Struktol placeholder pattern) and Ohio SOS (charter 1054053) was unreachable

**Known limits.** Muse's SAME verdicts and notes are leads, not evidence; only the quotes above were re-read. ALPLA's record names the legal entity ALPLA Inc. but carries its Lima, Ohio plant in the HQ field (the entity's HQ is McDonough, GA); fixing HQ fields is a separate follow-up and not part of this change.

Reply format: one line per fill `ORG-xxxxxx: SOUND|DOUBT|WRONG — reason`, then `OVERALL: SOUND|UNSOUND`.
