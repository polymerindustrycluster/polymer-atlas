# SBA PPP employee bands, re-run on current main, 2026-11-26

Built by: Claude Sonnet 5.5 (Claude Code), thread thr_rqdexkkube

Owner rulings 2026-11-26 07:20 (multiple choice): **"PPP now, street route next"** and **"Same ten-year rule"**; 07:36: **"Gate PR for PPP first"** (the gate route merged as #572). The census (`size-ceiling-census-2026-11-26`, outside the repo) found 38 size-unknown PIC-18 owners that the 2026-11-16 PPP rule binds today; 37 of them bind because their site street was blank at the 2026-11-16 pass and has been filled since.

## Rule (unchanged logic, SCHEMA §1 R13 source 4 as extended by v1.21.1)

`build.py` reuses `tasks/ppp-size-bands-2026-11-16/build.py`'s matching without rebuilding it: blank bands only (never overwrites a non-empty band); a single-site, Ohio-only organization (exactly one active site, every held site in Ohio, the active site in PIC-18); the borrower name equals a name the organization holds (`atlas.name_key` over `atlas.org_name_fields`); the borrower city equals the site's city and the street keys are equal and non-empty; positive integral JobsReported mapped to the schema bands; the latest qualifying loan per organization, ties by loan number; a loan dated on or after **2016-11-26**, and R13 v1.19.7 precedence (below) (write date 2026-11-26 minus ten years; the ten-year limit now applies to PPP, SCHEMA v1.21.1). Privacy whitelist kept: named corporations, S corporations, LLCs, partnerships and LLPs only; no sole proprietor, self-employed or individual name enters a file. All 1,953 input loans are 2020 or 2021 today, so the age limit excludes none.

Base: `8be53fd74ab624734cb24843b7cbc7a825499cc0` (origin/main after #572). Data is unchanged since `e4fd6585` (#572 changed only the gate, its tests, SCHEMA and DECISIONS). Evidence ids EVD-483200 to EVD-483295 (93 rows; three ids retired, see Precedence), label `claude-code ppp-size-bands-rerun-2026-11-26`.

## Applied (unit: Ohio organization records and their active PIC-18 site records, tiers A to C and U as held)

| Change | Applied |
|---|---:|
| `organizations_OH.employee_band_ohio`, previously empty | 48 |
| `sites_OH.employee_band_site`, previously empty | 45 |
| `size_band` evidence rows (new quote format, SCHEMA §4.13 v1.21.1) | 93 (92 supports_B, 1 supports_U) |
| Owners (organizations) with at least one fill | 56 |

By held tier: organizations A 17, B 27, C 3, U 1; sites A 14, B 17, C 14. By loan year: 36 dated 2020, 57 dated 2021. 246 organizations meet the strict rule; 391 candidate cells were skipped because the record already holds a band (this includes the 248 bands applied on 2026-11-16). Existing evidence and every other field are untouched, except the two follow-on changes below: `check.py` compares every touched table with the base as a whole-row multiset.

## Precedence under SCHEMA §1 R13 v1.19.7 (Codex round 1 finding, applied generally)

R13: "When admissible dated sources for the same establishment give different bands, use the newer one regardless of the distance between the bands ... Hold the older conflicting filing, with reason `newer_contradicting_filing` when the newer source is also a filing"; lead-only sources have no precedence. For a single-site, Ohio-only owner, the organization's Ohio band and its sole active site's band describe the same establishment. `build.py` therefore compares **every** candidate fill with the band already held on that establishment (an organization fill against its sole active site's band; a site fill against its owner's Ohio band). A differing held band whose source is an admissible dated source (an OSHA ITA or inspection filing, an SBA PPP loan, or a dated own-site page; the date is the filing's own: ITA 31 December of its year, inspection its open date) newer than the loan holds the loan with reason `newer_contradicting_filing` (`newer_contradicting_own_site` if the newer source were an own-site page); Form 5500 is lead-only. Every comparison with a differing held band is recorded in `precedence.csv` with its class.

| Class (fills whose establishment already holds a different band) | Fills | Treatment |
|---|---:|---|
| `newer_contradicting_filing`: held band from an OSHA ITA CY2025 filing dated 2025-12-31, loan older | 3 | **held, loan dropped**: ORG-000322 (loan 2020-04-13, PPP 50-99; sole site SITE-000343 holds 100-249, EVD-020312), ORG-001394 (2021-01-20, 50-99; SITE-001437 holds 10-49, EVD-481055), ORG-001710 (2021-03-16, 50-99; SITE-001786 holds 10-49, EVD-483015). Their three evidence ids, EVD-483215, EVD-483238 and EVD-483271, are retired and not reused; no surviving id moved. Listed in `holds.csv` with the retired id. |
| `older_differs`: held band from a dated admissible source older than the loan | 0 | none to list |
| `lead_only`: held band rests on a Form 5500 count | 1 | fill stands, listed: SITE-001651 (ORG-001580; loan 2020-04-28, 50-99; the organization's band 100-249 traces to a Form 5500 count, EVD-022238) |
| `undated_or_other`: held band with no admissible dated evidence row | 1 | fill stands, listed: SITE-001632 (ORG-001565; loan 2020-04-13, 100-249; the organization's band 50-99 has no `size_band` evidence row, and its base notes trace it to a Form 5500 count) |

The held band is never changed. **Follow-ups (surfaced, not committed, per Codex):** SITE-001632 and SITE-001651 may stand; the legacy Form 5500 organization bands of ORG-001565 and ORG-001580 go to the weekly repair batch for separate review.

## Follow-on changes the fills cause (CI found them on the first push)

- **V-65 debt baseline.** Two filled organizations, ORG-001433 and ORG-001493, had been grandfathered in `scripts/validate_debt_baseline.json` under V-65 (no supporting evidence row at tier strength). Their new `size_band` rows cure that, so the validator says to remove them: both IDs are removed from the V-65 list (1,324 to 1,322 entries). The unit test `test_v65_baseline_still_warns_only` reads its count from that file, so it needs no edit.
- **tier1_qualifier (derived, V-29).** Three organization bands are 250 or more employees, so the derived `employees_250plus` qualifier now applies: ORG-000362 (H-P Products, band 250-499), ORG-000637 (Xaloy, 250-499) and ORG-000955 (Meteor Sealing Systems, 250-499). The column was not hand-edited: I ran the repository's derivation tool, `python3 scripts/derive_tier1.py --write --i-am-the-integrator --packet <dir>`, over the post-pass tree, as SCHEMA §4.4 asks for each integration pass ("changed rows are listed in the pass journal"), and the same way `tasks/bands-apply-2026-11-02` did when its bands created drift. `tier1_changes.csv` is the tool's own change list (3 rows: old and new qualifier and basis, and its inputs). The 2026-11-16 PPP pass had no 250+ band, so it had no drift to handle. The tool also reports one organization with a stale canonical basis clause only; it is not rewritten here (no `--refresh-basis`), as before this PR. `check.py` allows a derived-column change only on a filled organization whose new band is 250 or more and only to the pinned values, and requires `derive_tier1.py` to report no qualifier drift.

## Binding gate

All 93 rows PASS `python3 scripts/check_evidence_binding.py --new-since origin/main` (93 PASS, 0 FAIL, 0 HELD). Of 101 candidate cells the gate did not pass 5 (and the precedence rule then held 3 more, above), which are dropped and listed in `gate_holds.csv`:

| Record | Gate verdict | Reason |
|---|---|---|
| ORG-001525 (organization) and SITE-001590 | FAIL `unit_differs` | the record's street is "22901 Millcreek Blvd, Suite 500", the borrower's is "...Ste 110": another unit, not a street match. The controller ruled both held. No suite rule was added to the copied logic; the gate's own rule held them. |
| ORG-001590 (organization) and SITE-001662 | HELD `designator_not_on_both_sides` | a suite on one side only |
| SITE-001694 (ORG-001623) | HELD `designator_not_on_both_sides` | a suite on one side only |

`holds.csv` also lists the 183 loan and organization pairs that meet the name, city and single-site screen but fail street equality or lack a held street (loan and organization pairs, not rejected companies, and never closure verdicts), and the three `newer_contradicting_filing` holds above (with the cell and the retired evidence id).

## Reconciliation with the census (AGENTS.md §2 rule 10c)

Unit: owners (org_id). The census counts 38 owners with a PPP-strict binding row; this pass fills 56 owners. **In both: 37. In the pass only: 19. In the census only: 1.** `reconciliation.csv` lists each owner not in both, with its reason; `build.py` stops if any has none, and `check.py` re-derives the file.

- **Census only (1): ORG-001590**, held by the gate for a suite on one side only (above). It is the 38th owner.
- **Pass only (19):** none is in the census's 372-owner frame, because the owner's other record already holds a band, so the owner was not size-unknown: 11 organization-only fills where the site holds a band and 8 site-only fills where the organization holds a band. The PPP band equals the held band on 17 of the 19 and differs from it by one band on two (ORG-001565 and ORG-001580, the Form 5500 cases above); the held band is not changed. Each fill is on the blank record only. The three owners that held a newer contradicting ITA band (ORG-000322, ORG-001394, ORG-001710) were in the earlier 22 and are now held; none is in the census 38.
- Not an owner in either list: ORG-001525 (census PPP state N, held by the gate) and ORG-001623 (its only fill, SITE-001694, is held).
- The census flagged one of its 38 as unexplained (street present at the 2026-11-16 base, not in that pass's `holds.csv`): **ORG-001709**, whose legal name carries a dba and a parenthetical. The 2026-11-16 base's `atlas.org_name_fields` yields only the full string as a name key; the current one also yields the alias `goodlevel enterprises`, which equals the borrower name. The 2026-11-16 pass could not match it; the matcher now can. The census records that the other 37 had a blank site street at that base. Two of the census's other owners were not in that pass's `holds.csv`: ORG-001709 (above) and ORG-000041, whose site city was Akron with a blank street then and is Fairlawn with a street now.

Size-unknown count (unit: PIC-18 owners, organizations and ecosystem entities, of active tier A to C sites with no band on any such site and none on the owner record): **372 of 792 at `e4fd658`; 335 of 792 after this PR** (37 of the 56 owners filled were size-unknown; the 19 others already held a band). Re-derived with the controller's `pic18_unknown.py` harness: `band_unknown=372 (47.0%)` on `origin/main` (8be53fd7), `band_unknown=335 (42.3%)` at this PR's head; process and market unknown counts are unchanged.

## Inputs

`INPUTS.sha256` names the two privacy-filtered PPP caches in the shared store (`provenance/ppp-loan-scout-2026-11-16/`, copied add-only by the controller): `public_150k_plus_240930.csv.filtered.csv` (951 rows, sha256 `431808599c…`) and `public_up_to_150k_9_240930.csv.filtered.csv` (1,002 rows, `188afe48a6…`). They are the named-corporation Ohio loan rows of two of the 13 national SBA PPP FOIA files (release 2024-09-30; original file hashes in `source_manifest.json`). A PPP miss means not in this cache, not no loan. The national files were never stored. I verified both hashes against the store and against `source_manifest.json`; the controller checks them against the store as rule 6 requires.

## Checks

`python3 tasks/ppp-size-bands-rerun-2026-11-26/check.py` (named check): compares the four touched data tables with the base as whole-row multisets, so a deleted or edited existing row, or an overwritten non-empty band, fails; compares each evidence shard's own delta with the planned rows of its record table (a row in the other shard, missing or extra fails); pins every addition to the rule's output and to `evidence_rows.csv`; re-applies the R13 v1.19.7 precedence rule to every fill; allows the retired evidence ids only for the three held loans; ties each fill to its dated evidence row and to `CLAIMS_CHECKED.csv` (verdict `corrected`, one per changed cell, equal to the changed cells); replays each evidence row through the binding gate (93 PASS); checks the input hashes; and plants thirteen defects, each rejected by the rule it exists to trip: deleted existing row, edited existing row (two fields), a hand-edited `tier1_qualifier` on an unfilled organization, a `tier1_qualifier` that differs from the pinned derivation, overwritten non-empty band, a loan older than ten years, an individual borrower type, a fill with no evidence row, an organization fill against a newer, different ITA band on its sole site (ORG-000322 put back), an evidence row moved to the wrong shard (EVD-483295 moved to the organization shard, a Codex round-1 finding), a 2019 ITA filing with a retrieval `observed_date`, which must read as older and not hold a 2020 loan (Codex round 2), and a changed cell missing from `CLAIMS_CHECKED.csv`. `scripts/run_tests.py` (the CI unit and mutation tests) was run on this head; only `scripts/validate_debt_baseline.json` changed under `scripts/`.

This is a dated borrower statement, not a current employment assertion; each band is labelled by its evidence row's 2020 or 2021 loan date (`observed_date`). No verification tier is changed.

## Also carried in this PR (owner-directed, no new data)

- `tasks/linkedin-market-ownsite-2026-11-26/AUDIT.md` copied unchanged from the controller's persist copy; sha256 `1a8f2b6eda5df2b15e2b6eb14831e9df4041270fce4d90411eb6a2d728060a1d`, checked on the copy.
- DECISIONS entries "2026-11-26 · Owner rulings 04:04 and 04:26" and "2026-11-26 · Owner rulings: PPP re-run and PPP age".
- The census experiments row in `docs/ACQUISITION.md` and the packet name in `tasks/acquisition-record-2026-11-24/check.py`.
- SCHEMA is not changed: v1.21.1 landed in #572.

Not done: no fresh PPP download (the 13 national files remain unstored), no reader opened a loan row beyond the scripted match and the gate, and the 183 street holds were not re-examined. Proposed follow-up (surfaced, not committed): a street-fill route for the PPP street holds ("street route next").
