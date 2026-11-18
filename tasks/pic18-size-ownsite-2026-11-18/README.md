# PIC-18 own-site Ohio size bands, 2026-11-18 (lane atlas-w18-size)

Fill blank `employee_band_ohio` on organization rows from the company's own published headcount (source class `own_site`, SCHEMA §4.4, §4.13 ceiling supports_B). Organization rows only; no site `employee_band_site` is written (SCHEMA §4.4: a company headcount is never allocated to a site).

## Result (units and filters named)
- **Frame:** 37 PIC-18 organization rows with a blank Ohio band whose stored corpus text matched an "<N> employees" screen (controller frame, `frame.csv`; a screen, not a claim). 20 are Ohio-only (HQ in Ohio, every held site of any status in Ohio); 17 are not.
- **Applied: 2 organization rows**, blank-only: Scott Molders, Inc. 10-49 (record tier A), S. Slesnick Company 50-99 (tier B). Evidence: 2 `size_band` rows, `own_site` / supports_B, EVD-396300 and EVD-396301 (block 396300-396399).
- **Held: 10 Ohio-only rows:** 5 on grain or limit (GrafTech, Technoform and Kinetico say worldwide/global; H.B. Chemical sits on the 50 band edge; GLI Pool Products says "over 340", which is open-ended and fits 250-499 and also 500-999 and above, and is scoped to its Youngstown facility), 1 on department-only wording (Alpha Tool and Mold), 4 on attribution (the page is another entity's: Seco Machine, Team Wendy, Youngstown Rubber Products, Pinnacle Recycling).
- **No claim: 8 Ohio-only rows** (parent/group count, history only, animated 0-counter, or no count on the pages).
- **Non-Ohio-only: 17 rows recorded, none applied:** 9 carry a company-wide statement (held leads), 8 have no usable statement for that record (4 are parent/group pages or a different entity than the record; 4 have nothing).
- **Outcome check** (`python3 S/harness/pic18_unknown.py "$PWD" <ref>`; unit: PIC-18 organization rows = 794; S = the controller storage dir): at merge-base `origin/main` dd07afc9 **band_unknown = 445 (56.0%)**; at HEAD with the 2 fills applied **band_unknown = 443 (55.8%)**: a fall of exactly 2 = the organizations filled. proc_unknown 331 and mkt_unknown 354 unchanged. `validate.py` passes on the applied tree.
- **Yield is small by design:** 2 of 445 unknown-band rows closed here (0.4%). The other 443 need a different source (owner ruling 2026-11-18b item 4: company-wide counts never set `employee_band_ohio`).

## Method
Read the stored pages (S/persist/pic18-corpus-2026-11-16); `check.py` re-verifies each page's sha256 against the manifest (pass-2 pages are reader text with no raw file, so only holds may rest on them), that every quote is a contiguous substring of its stored page, and that the stated count is the headcount in the quote (not a shift count or other number). Five live fetches, each of a URL linked from a stored page (rule 14), raw bytes and journal in S/persist/pic18-size-ownsite-2026-11-18/ (`fetch.py`): Alpha Tool and Mold /employment/, Juzo USA The-Juzo-Family and Juzo-International, Swagelok /about/global and /about/legacy. None added a count. A count qualifies only if the company's own page gives its own current count, or a range inside one band; "about N" and "~N" are banded at N. An open-ended count ("over", "more than", "at least", "N+") does not qualify unless an upper bound is also stated (GLI "over 340"); `build.py` and `check.py` both refuse it. `observed_date` is the stored fetch date (2026-11-16). Page dates, where shown, are in each evidence row's notes: Scott Molders footer copyright 2026, no publication date; Slesnick none.

## Verdicts (all 37 frame IDs; AGENTS 2.8 grammar: applied = VERIFIED, everything else STILL_UNCERTAIN with the settling fact)
Machine-readable: `verdicts.csv` (disposition, quote, URL, sha256, page date).

### Ohio-only (20)
| org | disposition | stated | band if it counted | quote (stored page) | settling fact / note |
|---|---|---|---|---|---|
| ORG-000564 | applied | 30 | 10-49 | We employ ~30 people that work 2 shifts/5 days per week. | Single Kent plant. |
| ORG-001776 | applied | 60 | 50-99 | Slesnick Recycling has enjoyed growth, with two recycling facilities in Canton and Alliance, Ohio. They currently employ about 60 people that process  | Two Ohio facilities (Canton, Alliance); Slesnick Recycling is the S. Slesnick Company brand. |
| ORG-000157 | held | 1000 | 1000-4999 | We employ more than 1,000 people around the world | Page itself says worldwide (plants in Europe and the Americas); the Atlas Ohio-only site list cannot make it an Ohio count. Settles: an Ohio-grain count (owner ruling 2026-11-18b item 4: a company-wide count never sets employee_band_ohio). |
| ORG-000360 | held | 50 | 50-99 | We now employ just over 50 people with almost everyone working out of our main office in Twinsburg, OH. | Grain, band edge: "just over 50" sits at the 50-99 floor and "almost everyone" works at the Twinsburg office, so the Ohio count may be 49 or fewer. Settles: an Ohio-grain count (OSHA ITA, Form 5500) or a page stating the Twinsburg headcount. |
| ORG-000416 | held | 340 | 250-499 | GLI has grown nearly 400% since our inception and currently employs over 340 people on three shifts within our Youngstown facility. | Round 2: "over 340" is open-ended: it fits 250-499 and also 500-999 and above, so no band is settled; the page also scopes it to the Youngstown facility. Settles: an Ohio count within one band. |
| ORG-000567 | held | 800 | 500-999 | 800+ Employees Worldwide | Attribution: record is Seco Machine (a brand of Stucki); the count is the Stucki group worldwide, 23 facilities. Settles: a Seco Machine page with its own count. |
| ORG-000598 | held | 900 | 500-999 | We are an organization of over 900 people | Attribution: Team Wendy states it is an Avon Technologies plc company; "we" may be Team Wendy or the Avon group. Settles: a page giving a Team Wendy headcount. |
| ORG-000600 | held | 1400 | 1000-4999 | More than 55 sites with 1,400 employees | Grain: Technoform group worldwide, 55 sites; Atlas holds one Twinsburg site. Settles: a Technoform North America count. |
| ORG-001592 | held | 20 | 10-49 | have 20 employees with 3,000 man-hours/month working capacity | Grain: sentence sits in the INJECTION MOLDING paragraph and may be that department only. The live /employment/ page has no count. Settles: a company-wide count. |
| ORG-001607 | held | 2130 | 1000-4999 | Our global organization is represented by 2,130 associates | Grain: the page says global organization; Atlas holds one Newbury site. Settles: an Ohio-grain count (owner ruling 2026-11-18b item 4: a company-wide count never sets employee_band_ohio). |
| ORG-001649 | held | 60 | 50-99 | our talented staff of nearly 60 associates operate out of more than 75,000 square feet in our four inventory and operations facilities in the Midwest | Attribution: record is Youngstown Rubber Products; the page is Midstate Sales (four facilities, Midwest). Settles: a Youngstown Rubber Products count. |
| ORG-002038 | held | 4000 | 1000-4999 | team of nearly 4,000 employees provide safe and reliable waste and recycling solutions | Attribution and grain: record is Pinnacle Recycling; the page is Rumpke, five states. Settles: a Pinnacle count. |
| ORG-000138 | no_claim | - | - | employ 50,000+ people | Only the parent ITW group count (49 countries); the Permatex pages give none. |
| ORG-000156 | no_claim | - | - | - | No Swagelok headcount on 6 stored pages or 2 live about pages (global, legacy); "50 people" is a training-room capacity. |
| ORG-000196 | no_claim | - | - | - | No employee count on stored pages. |
| ORG-000540 | no_claim | - | - | Nearly 3,000 people who would be dead | Screen hit is a 9/11 essay, not a headcount; no company count on stored pages. |
| ORG-001514 | no_claim | - | - | Juzo Group, which to date employs 1,000 staff around the world | Group count (Juzo Group), not Juzo USA; 2 further live Juzo pages carry none. |
| ORG-001549 | no_claim | - | - | STERIS grows to more than 4,500 Associates | Historical (2000) and global; no current count. |
| ORG-001550 | no_claim | - | - | STERIS grows to more than 4,500 Associates | Same STERIS history page; historical, parent, global. |
| ORG-001643 | no_claim | - | - | 0 Employees 0 Happy Clients | Animated counters render as 0 in stored text; no usable count. |

### Non-Ohio-only (17): leads, none applied
Owner ruling 2026-11-18b item 4 (tasks/owner-rulings-2026-11-18b/README.md §4): a company-wide or worldwide count on an organization's own page never sets `employee_band_ohio`; these stay held leads and need an Ohio-grain source (OSHA ITA, Form 5500, a plant page).

| org | disposition | stated | band if it counted | quote (stored page) | settling fact / note |
|---|---|---|---|---|---|
| ORG-000050 | no_claim | 3500 | 1000-4999 | we employ 3,500 people around the world | Page is Synthomer plc (London group); the record is Synthomer, Inc.; parent count is not the record's claim; not Ohio-only. |
| ORG-000202 | no_claim | - | - | responsible for a team of 5 employees | A branch manager's team, not the company; not Ohio-only. |
| ORG-001197 | no_claim | - | - | 0 Employees in North America | Animated page counter renders as 0 in stored text; no usable count; not Ohio-only. |
| ORG-001577 | no_claim | 2000 | 1000-4999 | Headcount ca. 2,000 employees worldwide | Page is the global Master Builders Solutions group; the record is Master Builders Solutions US LLC; not the record's claim; not Ohio-only. |
| ORG-001619 | no_claim | 11200 | 5000+ | More than 11,200 employees worldwide | SOPREMA group-wide count (parent of SOPREMA Inc); not the record's claim; not Ohio-only. |
| ORG-001757 | no_claim | - | - | - | No employee count of the company on stored pages; not Ohio-only. |
| ORG-002136 | no_claim | - | - | - | Only "Employees buy the Automotive Division" (1987 history); not Ohio-only. |
| ORG-003196 | no_claim | 1800 | 1000-4999 | Employees: approx. 1.800 worldwide | Group page (ECKART GmbH, Germany), not Eckart America Corporation; parent count is not the record's claim; not Ohio-only. |
| ORG-000007 | held_lead | 4500 | 1000-4999 | ~4,500 employees | Vibrantz global group count; org not Ohio-only. Held: owner ruling 2026-11-18b item 4 (a company-wide count never sets employee_band_ohio); needs an Ohio-grain source. |
| ORG-000009 | held_lead | 1700 | 1000-4999 | talented workforce of 1,700 employees worldwide | Worldwide count; not Ohio-only. |
| ORG-000030 | held_lead | 600 | 500-999 | Our growing company now employs over 600 people | North America-wide distributor; not Ohio-only. |
| ORG-000073 | held_lead | 500 | 500-999 | now employ more than 500 people in 23 locations worldwide | Two Professional Plastics pages give 500+ and 450+ across 23 locations in four countries; not Ohio-only. |
| ORG-000236 | held_lead | 3500 | 1000-4999 | 3,500+ TEAM MEMBERS | Two-country footprint count; not Ohio-only. |
| ORG-000278 | held_lead | 10000 | 5000+ | team of approximately 10,000 associates across the globe | Global count; not Ohio-only. |
| ORG-000651 | held_lead | 5000 | 5000+ | Advanced Drainage Systems has over 5000+ employees | National count; not Ohio-only. |
| ORG-001007 | held_lead | 25000 | 5000+ | 25,000 people working together | Global count; not Ohio-only. |
| ORG-004022 | held_lead | 1800 | 1000-4999 | About 1800 VMI people around the world | Entity: the page is VMI Group (about 1800 worldwide); the record is VMI Holland B.V. The same page gives about 1000 at the Epe headquarters. Group-wide count, not the exact entity's; not Ohio-only. |

## Self-refute (rule 15)
- self-refute: grain — 20 Ohio-only rows checked (+17 non-Ohio-only recorded, none written), 6 changed: GrafTech, Technoform and Kinetico moved from candidate to hold because the page itself says worldwide/global; H.B. Chemical moved to hold because "just over 50" sits on the 50 band edge and "almost everyone" is at one office, so its Ohio count could read 49; Alpha Tool and Mold moved to hold because the "20 employees" sentence sits in the injection-molding paragraph; GLI moved to hold in round 2 because "over 340" is open-ended (it fits 250-499 and also 500-999 and above) and is scoped to one facility.
- self-refute: founding — 2 rows checked, 0 changed (no founding or "since" year is used).
- self-refute: strength — 2 rows checked, 0 changed (each is a narrative own-site sentence, no menu, tab or list item; supports_B ceiling).
- self-refute: truncated quote — 2 rows checked, 1 changed: the Slesnick quote was extended back to the sentence that names the company and facilities, so the claim and its subject are both in the quote.
- self-refute: attribution — 37 frame rows checked, 8 changed: Seco Machine (Stucki group page), Team Wendy (page says an Avon Technologies plc company; "we" may be the group), Youngstown Rubber Products (Midstate Sales page) and Pinnacle Recycling (Rumpke page) held; Eckart America (ECKART group page), SOPREMA Inc (group count), Synthomer, Inc. (Synthomer plc page) and Master Builders Solutions US LLC (global group page) reclassified from lead to no-claim. VMI Holland B.V.'s lead is corrected in round 2: the page is VMI Group (about 1800 worldwide; the 1000 is the Epe headquarters). The two applied rows are each on the organization's own recorded website; "Slesnick Recycling" is the S. Slesnick Company's trade name on its own site (nav "About S. Slesnick").

## What was not checked
- No live re-fetch of the 2 applied rows: each rests on the stored 2026-11-16 page, which may have changed since.
- No second source for any applied count: a company statement is a band-level `supports_B` claim, not corroborated by OSHA or Form 5500 here (the government sources were spent on this frame). The earlier Youngstown ITA match for GLI (100-249, site measure) is a different band and was not used.
- I did not look for Ohio-grain counts for the 17 non-Ohio-only rows.

## Check commands
`python3 tasks/pic18-size-ownsite-2026-11-18/build.py` (writes fills.csv, evidence_rows.csv, counts.json; `--apply [--base REF]` edits data/, idempotent) then `cd tasks/pic18-size-ownsite-2026-11-18 && python3 check.py [base-ref]` (default base = merge-base with origin/main). `--apply` stages every shard as a temp sibling, asserts each staged row count equals its count at base (plus this packet's evidence rows), then replaces evidence first and organizations last, so a failure between writes leaves no cell without its evidence and a retry works. `check.py` diffs the whole `data/` tree against base (only the 2 band cells and 2 appended evidence rows may differ), recomputes counts against the controller frame and the stored corpus, then rejects 11 injected defects: band not containing the quoted count, verdict and fill both moved off the count, write to a non-Ohio-only organization, write to an organization with a non-Ohio site, write to a non-blank cell, write to a site row, a count with the wrong role (Scott Molders' "2 shifts" read as 2 employees), an open-ended "over 340" taken as a band (GLI switched back to applied), quote not in its stored page, frame ID with no verdict, plus two builder faults run through the real `apply()` in a temp tree (truncated input shard rejected; failure between writes leaves no cell without evidence and the retry succeeds). Last output: `PASS (applied): 2 fills, 2 evidence rows, 37 frame verdicts, 11 injected defects rejected`.

## Apply status
Applied 2026-11-18 on main dd07afc9 (after market batch 1, #390, merged): 2 organization cells in `data/organizations_OH.csv` (ORG-000564 Scott Molders 10-49, ORG-001776 S. Slesnick Company 50-99) and 2 appended rows in `data/evidence_organizations_OH.csv` (EVD-396300, EVD-396301); no other file or row changed (`check.py` diffs the whole `data/` tree against the merge-base). Outcome check at merge-base dd07afc9 vs HEAD: band_unknown 445 (56.0%) -> 443 (55.8%).

## Proposed follow-ups
- Settled, no ruling pending: owner ruling 2026-11-18b item 4 says a company-wide count never sets `employee_band_ohio`, so the 12 held leads (9 non-Ohio-only statements plus GrafTech, Technoform, Kinetico) need an Ohio-grain source.
- Seven holds each need a page of the record's own giving its own count, or an Ohio-grain count: Seco Machine, Team Wendy, Youngstown Rubber Products, Pinnacle Recycling, Alpha Tool and Mold (company-wide); H.B. Chemical and GLI Pool Products (an Ohio count within one band).
