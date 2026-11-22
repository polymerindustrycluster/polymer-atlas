# Evidence backfill, Form 5500 organization lane (built 2026-11-20, cut 2026-11-22)

**Status: cut per the owner on 2026-11-22 ("Cut to what's new"); ready for review; nothing applied.**
- **Owner instruction (2026-11-20):** "build it, but hold reviews until sunday at least." The hold ended 2026-11-22.
- **Owner ruling (2026-11-22, multiple choice):** keep the rows for organizations that still have no evidence row, plus
  the lane's liveness rows; drop the rest. Other work had evidenced 194 of the 270 organizations since 2026-11-20.
- **Original packet** (`packet_rows_2026-11-20.csv`, kept as the record): 780 rows on 270 organizations: 270
  `existence`, 266 HQ `address`, 244 `liveness`.

## The cut (computed on this branch after merging origin/main `8f30ce0f`; the data files equal main's)

`build.py cut` recomputes this at build time from every `data/evidence_*.csv` row (any `record_table`) that is not this
lane's own.
- **Organizations with no evidence row at all: 76** of the 270 (194 have one); the same 76 whether the filter is
  `evidence_organizations_*.csv` alone or every evidence table. Active organizations, unit: organization records. The
  controller's count on main `17834918` was also 76.
- **Kept: 319 rows** (unit: packet rows): 75 `existence`, 1 `address`, 243 `liveness`. The 75 existence rows are on 75 of the
  76 organizations (65 NAME+CITY, 10 EIN+NAME; tiers 34 A, 33 B, 7 C, 1 U). The 243 liveness rows are on 243 organizations:
  67 of the 76 and 176 evidenced elsewhere. Kept rows sit on 251 organizations.
- **Dropped: 386 rows** (194 `existence`, 192 `address`) on the 194 evidenced organizations, each in `dropped_rows.csv`
  with the reason "organization evidenced since 2026-11-20". Liveness rows are never dropped.
- **Held: 75 rows** in `held_rows.csv`, each with its settling fact:
  - `NO_HQ_STREET` 66 (address): the Atlas has no usable HQ street, so the filing's street cannot be compared. Breakdown of
    the organizations: 30 have only a non-HQ site in the HQ city, 28 have sites only elsewhere, 5 have no site record,
    3 have an active HQ-type site with no street. Whether a plant street in the HQ city counts as the HQ street is an owner
    question (below).
  - `PO_BOX_OR_NO_NUMBER` 5 (address): the filing's street line is a PO box or has no street number (not quoted).
  - `DIFFERENT` 1 (address): ORG-001333, filing '1525 CORPORATE WOODS PARKWAY' vs Atlas '1525 Corporate Wood Parkway, Suite
    500'. Probably a typo on the Atlas side; settling fact: the correct street, a record correction, not this lane's.
  - `SHARED_FILING` 3 (existence, address, liveness on **ORG-001440**, Spectra Group Ltd., Inc.): its ACK_ID is the same one
    cited for **ORG-001552** (Formlabs Ohio, Inc.), the exact legal-name match. ORG-001440 matches only through the Atlas trade
    name 'Formlabs Ohio, Inc.'. A sponsor that is a different legal entity (an acquirer) is the UNSOUND class in the brief.
    Settling fact: whether 'Formlabs Ohio, Inc.' is a trade name of this legal entity or of its acquirer. ORG-001552's rows stay.
- **Balance:** 319 + 386 + 75 = 780 (`check.py` asserts every original row exactly once, and that no ACK_ID is cited for two kept
  organizations).
- **Street test over all 251 kept organizations** (informational for liveness rows, which it does not gate; recorded per item in
  the bundle as `street_check`): 6 SAME, 4 DIFFERENT, 14 PO_BOX_OR_NO_NUMBER, 4 NOT_IN_HQ_CITY, 223 NO_HQ_STREET. The 4 DIFFERENT:
  ORG-001333 (typo above); ORG-000445 ('4220 ALABAMA AVENUE SW' vs '4220 Alabama Ave', a direction suffix); ORG-002691 ('618
  FOURTH AVENUE' vs '618 4th Ave.', the same street); ORG-002315 ('2425 WEST 23RD STREET' vs '2315 W 23rd St.', a different
  number). Three are normalizer or typo limits; ORG-002315 may be a real difference. Whether a different street defeats a
  liveness row is an owner question; the reviewers see the result.
- **Provenance of the cut:** the four EFAST2 zips were **re-fetched 2026-11-22** (the owner's brief expected the files to be at
  hand; they were not on this machine) from `askebsa.dol.gov`, by the URL pattern in `scripts/build_form5500_spine.py`, into
  `/Users/johnswanson/f5500_raw_2026-11-22`, outside the repo. Their sha256 prefixes equal those in every row's notes, so the
  files are byte-identical to the 2026-11-20 ones and the rows' notes stay true. All 269 distinct cited ACK_IDs (270 organizations,
  one shared pair) were found with sponsor, EIN, plan-year end, active count and final flag unchanged (a change would hold the row).
- **Status guard:** a row on an organization the Atlas no longer calls `active` is dropped (no evidence) or held; none is kept.
  ORG-002569 (status `acquired`) was evidenced and is among the dropped.
- **Street text:** only the street lines of business filings appear, and only when clean: any line with `@`, `c/o`, `attn`, `care
  of`, a leading `%` or no digit is blanked in the bundle and not quoted in a reason; `check.py` scans the bundle, reasons and
  kept text for those markers.
- **No rows are applied in this PR.** It is packet-only: review comes first. Evidence IDs are asserted by `apply.py`, not
  allocated, and `scripts/validate_debt_baseline.json` is unchanged.

## What this lane's match requires (shown from `build.py`)

| Claim | Requires | Code |
|---|---|---|
| `existence` | Sponsor name or DBA **equals** the organization's legal or trade name (`name_key`, no containment), plus **either** an Atlas-linked EIN (`EIN+NAME`) **or** a sponsor address in the HQ city and state with exactly one EIN behind that name there (`NAME+CITY`). **No street leg.** | `classify()` |
| `address` | The existence match, **and** the filing's street (location address if given, else mailing) equals, under `atlas.street_key`, the street of an active Atlas HQ site in the HQ city. No HQ street, a PO box or a different street: held. | `in_hq()`, `hq_streets()`, `street_test()` |
| `liveness` | The existence match, plan year ended on or after 2024-11-20, active participants above 0, not a final filing (owner ruling 8). **No street leg.** | `rows_for()` |

- **Where the Atlas HQ street comes from:** organization records carry no street field, so the HQ street is the
  `street_address` of an active site whose `site_type` names HQ or headquarters, in the HQ city and state.
- **A gap on the existence rows, stated plainly:** the 75 kept existence rows rest on name plus EIN link or HQ
  city, with no street. Of the 74 zero-evidence filings with an in-HQ-city address, the street test could compare 2 (1 same, 1
  different); 66 had no HQ street on the Atlas side, 5 a PO box, and 1 was the shared-filing hold. This is the same shape as the defect found in another lane on
  2026-11-22 (name and city, no street), but it bears on an `existence` claim, where one EIN behind an exact name in one
  city is the evidence, not on an address claim. **Owner question, not settled here:** is name plus HQ city (one EIN)
  enough for `existence` when the street cannot be compared?
- **Address-role (SCHEMA v1.19):** the kept `address` row carries `address_role` = `mailing` (the filing gave a mailing
  address); a location address would carry `physical`.
- **Liveness-only organizations (176):** the existence row is not minted, so the liveness verdict stands on identity
  too; a reviewer judging a liveness row SOUND is judging that the sponsor is the organization. The street test does not gate
  these rows; it is shown to the reviewer.

## Why (as of 2026-11-20)

**The organization gap.** On main `01ef298e`, 1,199 active organizations have no evidence row.
- Earlier lanes don't reach them. A TRI or OSHA filing names a plant, not the HQ, and only 35 of these organizations
  carry an EIN link.

**What a Form 5500 gives.** The filing is made by the employer itself, so it names the legal entity, its address and
the plan's active participants at year end.
- It is a `government_filing`, so it is A-capable for all three claims.
- Liveness follows owner ruling 8 (2026-11-20): a government filing whose covered period ended within 24 months
  witnesses liveness, and the witnessed date is the period's end.

## Method of the 2026-11-20 build (the cut applies it, then the street test)

`build.py` runs with no model. The `match` step below ran once on tree `01ef298e`; it is not re-run (its frame is "no evidence
now"), and `cut` reads its output as the record.

1. **Source:** DOL EBSA EFAST2 bulk "Latest" datasets, Form 5500 and 5500-SF, plan years 2024 and 2025.
   - Fetched 2026-11-20 from `askebsa.dol.gov`. Hashes are in the corpus MANIFEST and each row's notes.
   - The files stay outside the repo.
   - Readers reuse `scripts/build_form5500_spine.py` (`SPECS`, `num`) and the house name normalizer
     (`scripts/atlas.py` `name_key`).
   - Signer names, phones and care-of fields are never read; `check.py` whitelists ledger columns and scans the bundle.
2. **Match** (`ledger.csv`): the sponsor name or DBA must **equal** the organization's legal or trade name (no
   containment), plus one of:
   - **`EIN+NAME`**: an EIN the Atlas links to the organization (34).
   - **`NAME+CITY`**: a sponsor address in the HQ city and state, with exactly one EIN behind that name there (236).
3. **Held as leads:**
   - `MULTI_EIN` (3): a name in the HQ city spans several EINs (Honeywell, ArmorSource, Health Care Logistics).
   - `NAME_STATE_ONLY` (40): the name files in the HQ state but in another city, an HQ-city lead.
   - `SPINE_OTHER_EIN` (1): the 2026-11-01 spine (`tasks/form5500-spine-2026-11-01`) gave the org a different EIN.
     This is Hankook Tire America (ORG-000204).
   - Two further classes, `EIN_NAME_DIFF` and `SPINE_CONFLICT`, catch an EIN filing under another name and an EIN the
     spine gave to another org; both are 0.
   - **The spine check runs both ways:** every EIN behind the match is tested.
   - **Spine agreement:** the spine independently gives the cited EIN to the same org for 70 of the 270. It covers only
     polymer-coded sponsors, so the other 200 are unchecked by it, not contradicted.
4. **Filing choice:** one filing is cited per organization. It is the latest plan-year end on or before 2026-11-20,
   preferring a non-final filing with active participants, then the most participants, then the ACK_ID.
5. **Rows** (`packet_rows_2026-11-20.csv`), at supports_A (supports_U on tier U):
   - **`existence`:** the filing, naming the matched Atlas name. Ten rows match through an Atlas trade name, and the
     claim text says so.
   - **`address`:** HQ city and state, only when the sponsor's address is there. The location address governs when one
     is given; otherwise the mailing address is used.
   - **`liveness`:** only for a plan year that ended on or after 2024-11-20, with active participants above 0 and no
     final filing. A final filing is a plan fact, never a status change (AGENTS.md §3). `observed_date` is the plan-year
     end (SCHEMA §4.13).
6. **Citation:** rows cite "DOL EBSA Form 5500[-SF], plan year ending …, ACK_ID … (EFAST2 dataset …)". That is a named
   source, so V-66 does not apply.

## Defect injections, all caught

- **`build.py plant`, rotated HQs:** each witnessed organization was given another organization's HQ city and state.
  Result: 0 witnesses from 270. **Swapped EINs:** 0 from 35. (2026-11-20, on tree `01ef298e`.)
- **`check.py selftest` (2026-11-22):** plants, on a copy of the real cut, (a) an `existence` row for an already-evidenced
  organization among the kept rows, (b) a lost row, (c) a kept `address` row whose HQ site street differs. Each is
  caught, and the unplanted cut passes.
- **`check.py`:** it also fails on a final-filing flag under a liveness row, a phone field in the bundle, and a
  citation without its ACK_ID (checked 2026-11-20).
- **`build.py selftest`:** name keys, location-over-mailing, future period ends, the non-final preference, multi-EIN
  and spine-conflict holds, and the ruling-8 liveness gates.
- **Apply rehearsal (2026-11-22, throwaway worktree, not committed):** with every kept row marked SOUND, `apply.py`
  wrote 319 rows `EVD-480100..EVD-480418` in the 12-column header (it first wrote 11 and broke on the v1.19
  `address_role` column; fixed), `check.py` passed, `validate.py` passed, and `prune_baselines.py` shrank V-65 912 -> 845 and
  V-68 346 -> 338 (the 75 organizations).

## Evidence IDs and baselines

- **IDs:** `EVD-480100..480999` is this lane's reserved range (`EVD-480000..480099` belong to another lane; Muse's open
  PR #459 holds everything up to `EVD-475722`). The tree maximum on this branch is `EVD-459524`. `apply.py` asserts the
  start is in range and above the tree maximum, that the packet fits, and that no non-liveness row's organization has
  gained other evidence since the cut.
- **Baselines:** this PR applies no rows, so `scripts/validate_debt_baseline.json` is unchanged. `apply.py` shrinks V-65 and
  V-68 by exactly the organizations it evidences when it runs (see the rehearsal).

## Next

1. Split `review_bundle.json` (251 organizations; 75 with an existence item, 176 liveness-only) into briefs under
   `review_brief.md`; 7 parts if Antigravity is used (64 KB cap).
2. Run `council-ask codex --effort deep` on each brief. Have Codex also review `build.py`, `apply.py` and `check.py`;
   the code has had no review outside its author.
3. If a second family is available, run it; `apply.py` then requires both. Otherwise Codex gates alone under the owner's
   waiver of 2026-11-20.
4. Run `apply.py . --start EVD-480100 --codex … [--agy …]`, then `check.py`, `validate.py`, `check_row_loss.py`.
5. Ask the owner before merging.

## Owner questions (listed, not settled)

1. Is name plus HQ city with one EIN enough for `existence` when no HQ street is on the Atlas record (66 of the 74 comparable
   filings)?
2. Does the street of a non-HQ site in the HQ city (30 organizations) count as the HQ street, so those address rows could be
   street-tested? This lane does not count it.
3. Should the 66 `NO_HQ_STREET` and 5 PO-box filings' addresses be recorded as `mailing`-role address rows without a street
   test? This lane holds them.
4. Does a DIFFERENT street defeat a liveness row (4 organizations, one a real number difference)? This lane does not gate on it.

## Reproduce

```
python3 tasks/evidence-form5500-orgs-2026-11-20/build.py selftest
python3 tasks/evidence-form5500-orgs-2026-11-20/build.py cut . <form5500 dir>
python3 tasks/evidence-form5500-orgs-2026-11-20/check.py
python3 tasks/evidence-form5500-orgs-2026-11-20/check.py selftest
```
