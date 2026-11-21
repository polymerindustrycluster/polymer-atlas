# Evidence backfill, Form 5500 organization lane (2026-11-20)

**Status: built, not reviewed, nothing applied.**
- **Owner instruction (2026-11-20):** "build it, but hold reviews until sunday at least." No review runs before
  2026-11-22, and no row reaches `data/` before a review.
- **Packet:** 780 rows on 270 active organizations that have no evidence rows: 270 `existence`, 266 HQ `address`,
  244 `liveness`.
- **Organizations by tier:** 111 A, 135 B, 20 C, 4 U.

## Why

**The organization gap.** On main `01ef298e`, 1,199 active organizations have no evidence row.
- Earlier lanes don't reach them. A TRI or OSHA filing names a plant, not the HQ, and only 35 of these organizations
  carry an EIN link.

**What a Form 5500 gives.** The filing is made by the employer itself, so it names the legal entity, its address and
the plan's active participants at year end.
- It is a `government_filing`, so it is A-capable for all three claims.
- Liveness follows owner ruling 8 (2026-11-20): a government filing whose covered period ended within 24 months
  witnesses liveness, and the witnessed date is the period's end.

## Method

`build.py` runs with no model.

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
5. **Rows** (`packet_rows.csv`), at supports_A (supports_U on tier U):
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
  Result: 0 witnesses from 270.
- **`build.py plant`, swapped EINs:** each EIN-linked organization was given the next one's EINs. Result: 0 from 35.
- **`check.py` (pre-review):** it fails on each of three injections, and passes once they are restored:
  - a final-filing flag under a liveness row;
  - a phone field in the bundle;
  - a citation without its ACK_ID.
- **`build.py selftest`:** name keys, location-over-mailing, future period ends, the non-final preference, multi-EIN
  and spine-conflict holds, and the ruling-8 liveness gates.

## Next (2026-11-22 or later)

1. **Refresh first.** Merge main, re-run `build.py match` and `plant`, and diff `packet_rows.csv` against this commit.
   `apply.py` does not re-check that an org is still active and still has no evidence row, so a stale packet must not
   be reviewed.
2. Split `review_bundle.json` into briefs (header `review_brief.md`); use 7 parts if Antigravity is used (64 KB cap).
3. Run `council-ask codex --effort deep` on each brief. Have Codex also review `build.py`, `apply.py` and `check.py` in
   the same run; this lane's code has had no review outside its author.
4. If Antigravity's quota is back (about 2026-11-24), run it too; `apply.py` then requires both families. Otherwise
   Codex gates alone under the owner's waiver of 2026-11-20.
5. Run `apply.py . --start EVD-410701 --codex … [--agy …]`, then `check.py`, `validate.py` and `check_row_loss.py`.
6. Open the PR, and ask the owner before merging.

## Reproduce

```
python3 tasks/evidence-form5500-orgs-2026-11-20/build.py selftest
python3 tasks/evidence-form5500-orgs-2026-11-20/build.py match . <form5500 dir>
python3 tasks/evidence-form5500-orgs-2026-11-20/build.py plant . <form5500 dir>     # expect 0 and 0
python3 tasks/evidence-form5500-orgs-2026-11-20/check.py
```
