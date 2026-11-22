# Evidence backfill, Form 5500 organization lane (built 2026-11-20, cut 2026-11-22)

**Status: cut per the owner on 2026-11-22 ("Cut to what's new"); ready for review; nothing applied.**
- **Owner instruction (2026-11-20):** "build it, but hold reviews until sunday at least." The hold ended 2026-11-22.
- **Owner ruling (2026-11-22, multiple choice):** keep the rows for organizations that still have no evidence row, plus
  the lane's liveness rows; drop the rest. Other work had evidenced 194 of the 270 organizations since 2026-11-20.
- **Original packet** (`packet_rows_2026-11-20.csv`, kept as the record): 780 rows on 270 organizations: 270
  `existence`, 266 HQ `address`, 244 `liveness`.

## The cut (computed at merged main `b09b4d47`; this branch's data files equal main's)

`build.py cut` recomputes this at build time from `data/evidence_organizations_*.csv` (rows of other lanes only).
- **Organizations with no evidence row in `data/evidence_organizations_*.csv`: 76** of the 270 (194 have one). Active
  organizations, unit: organization records. Evidence rows on `ecosystem` records are a different table and not counted.
- **Kept: 321 rows** (unit: packet rows): 76 `existence`, 1 `address`, 244 `liveness`. The 76 existence rows are on the 76
  organizations (66 NAME+CITY, 10 EIN+NAME; tiers 34 A, 34 B, 7 C, 1 U). The 244 liveness rows are on 244 organizations,
  68 of them among the 76 and 176 on organizations evidenced elsewhere.
- **Dropped: 386 rows** (194 `existence`, 192 `address`) on the 194 evidenced organizations, each in
  `dropped_rows.csv` with the reason "organization evidenced since 2026-11-20". Liveness rows are never dropped.
- **Held: 73 rows**, all `address` rows on zero-evidence organizations, in `held_rows.csv` with the settling fact:
  - `NO_HQ_STREET` 67: the Atlas holds no active HQ site with a street in the HQ city, so the filing's street cannot be
    compared. Settling fact: an HQ street on the record (an owner or integrator decision), or an address witness.
  - `PO_BOX_OR_NO_NUMBER` 5: the filing's street line is a post-office box or has no street number.
  - `DIFFERENT` 1: ORG-001333, filing '1525 CORPORATE WOODS PARKWAY' vs Atlas '1525 Corporate Wood Parkway, Suite 500'.
    Probably a typo on the Atlas side; settling fact: the correct street, which is a record correction, not this lane's.
- **Balance:** 321 + 386 + 73 = 780 (`check.py` asserts it, every original row exactly once).
- **Provenance of the cut:** the four EFAST2 zips were re-fetched 2026-11-22 from `askebsa.dol.gov` (URL pattern from
  `scripts/build_form5500_spine.py`, outside the repo). Their sha256 prefixes equal those in every row's notes, so the
  files are byte-identical to the 2026-11-20 ones and the rows' notes stay true. All 269 cited ACK_IDs were found with
  sponsor, EIN, plan-year end, active count and final flag unchanged (a change would hold the row).
- **Status guard:** a row on an organization the Atlas no longer calls `active` is dropped (zero-evidence) or held; none
  is kept. ORG-002569 (status `acquired`) was evidenced and is among the dropped.

## What this lane's match requires (shown from `build.py`)

| Claim | Requires | Code |
|---|---|---|
| `existence` | Sponsor name or DBA **equals** the organization's legal or trade name (`name_key`, no containment), plus **either** an Atlas-linked EIN (`EIN+NAME`) **or** a sponsor address in the HQ city and state with exactly one EIN behind that name there (`NAME+CITY`). **No street leg.** | `classify()` |
| `address` | The existence match, **and** the filing's street (location address if given, else mailing) equals, under `atlas.street_key`, the street of an active Atlas HQ site in the HQ city. No HQ street, a PO box or a different street: held. | `in_hq()`, `hq_streets()`, `street_test()` |
| `liveness` | The existence match, plan year ended on or after 2024-11-20, active participants above 0, not a final filing (owner ruling 8). **No street leg.** | `rows_for()` |

- **Where the Atlas HQ street comes from:** organization records carry no street field, so the HQ street is the
  `street_address` of an active site whose `site_type` names HQ or headquarters, in the HQ city and state.
- **A gap on the existence rows, stated plainly:** the 76 kept existence rows rest on name plus EIN link or HQ
  city, with no street. The street test could compare 2 of the 74 filings' addresses (1 same, 1 different); 67 had no
  HQ street on the Atlas side and 5 a PO box. This is the same shape as the defect found in another lane on
  2026-11-22 (name and city, no street), but it bears on an `existence` claim, where one EIN behind an exact name in one
  city is the evidence, not on an address claim. **Owner question, not settled here:** is name plus HQ city (one EIN)
  enough for `existence` when the street cannot be compared?
- **Address-role (SCHEMA v1.19):** the kept `address` row carries `address_role` = `mailing` (the filing gave a mailing
  address); a location address would carry `physical`.
- **Liveness-only organizations (176):** the existence row is not minted, so the liveness verdict stands on identity
  too; a reviewer judging a liveness row SOUND is judging that the sponsor is the organization.

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
  wrote 321 rows `EVD-480100..EVD-480420` in the 12-column header (it first wrote 11 and broke on the v1.19
  `address_role` column; fixed), `check.py` passed, `validate.py` passed, and `prune_baselines.py` shrank V-65 912 -> 844 and
  V-68 346 -> 338 (the 76 organizations).

## Evidence IDs and baselines

- **IDs:** `EVD-480100..480999` is this lane's reserved range (`EVD-480000..480099` belong to another lane; Muse's open
  PR #459 holds everything up to `EVD-475722`). The tree maximum on this branch is `EVD-459524`. `apply.py` asserts the
  start is in range and above the tree maximum, that the packet fits, and that no non-liveness row's organization has
  gained other evidence since the cut.
- **Baselines:** this PR applies no rows, so `scripts/validate_debt_baseline.json` is unchanged. `apply.py` shrinks V-65 and
  V-68 by exactly the organizations it evidences when it runs (see the rehearsal).

## Next

1. Split `review_bundle.json` (252 organizations; 76 with an existence item, 176 liveness-only) into briefs under
   `review_brief.md`; 7 parts if Antigravity is used (64 KB cap).
2. Run `council-ask codex --effort deep` on each brief. Have Codex also review `build.py`, `apply.py` and `check.py`;
   the code has had no review outside its author.
3. If a second family is available, run it; `apply.py` then requires both. Otherwise Codex gates alone under the owner's
   waiver of 2026-11-20.
4. Run `apply.py . --start EVD-480100 --codex … [--agy …]`, then `check.py`, `validate.py`, `check_row_loss.py`.
5. Ask the owner before merging.

## Owner questions (listed, not settled)

1. Is name plus HQ city with one EIN enough for `existence` when no HQ street is on the Atlas record (67 of the 74
   comparable filings)?
2. Should the 67 `NO_HQ_STREET` and 5 PO-box filings' addresses be recorded as `mailing`-role address rows without a street
   test? This lane holds them.

## Reproduce

```
python3 tasks/evidence-form5500-orgs-2026-11-20/build.py selftest
python3 tasks/evidence-form5500-orgs-2026-11-20/build.py cut . <form5500 dir>
python3 tasks/evidence-form5500-orgs-2026-11-20/check.py
python3 tasks/evidence-form5500-orgs-2026-11-20/check.py selftest
```
