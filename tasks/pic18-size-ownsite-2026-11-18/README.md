# PIC-18 own-site Ohio size bands, 2026-11-18 (lane atlas-w18-size)

Fill blank `employee_band_ohio` on organization rows from the company's own published headcount (source class `own_site`, SCHEMA §4.13, ceiling supports_B). Organization rows only; no site `employee_band_site` is written (SCHEMA §4.4: a company headcount is never allocated to a site).

## Result (units and filters named)
- **Frame:** 37 PIC-18 organization rows with a blank Ohio band whose stored corpus text matched an "<N> employees" screen (controller frame, `frame.csv`; a screen, not a claim). 20 are Ohio-only (HQ in Ohio, every held site of any status in Ohio); 17 are not.
- **Applied: 3 organization rows**, blank-only: GLI Pool Products 250-499, Scott Molders 10-49, S. Slesnick Company 50-99. Evidence: 3 `size_band` rows, `own_site` / `supports_B`, EVD-396300 to EVD-396302 (block 396300-396399). Record tiers A, B, B (none U).
- **Held: 9 Ohio-only rows:** 4 on grain (GrafTech, Technoform and Kinetico say worldwide/global; H.B. Chemical sits on the 50 band edge), 1 on department-only wording (Alpha Tool and Mold), 4 on attribution (the page is another entity's: Seco Machine, Team Wendy, Youngstown Rubber Products, Pinnacle Recycling).
- **No claim: 8 Ohio-only rows** (parent/group count, history only, animated 0-counter, or no count on the pages).
- **Non-Ohio-only: 17 rows recorded, none applied:** 9 carry the record's own company-wide statement (held leads), 8 have no usable statement for that record (4 are parent/group pages or a different entity than the record; 4 have nothing).
- **Outcome check** (`python3 S/harness/pic18_unknown.py "$PWD" <ref>`; unit: PIC-18 organization rows = 794; S = the controller storage dir): merge-base `origin/main` e1df30e4 **band_unknown = 445 (56.0%)**; with the 3 fills applied **band_unknown = 442 (55.7%)**: a fall of exactly 3 = the organizations applied. proc_unknown 331 and mkt_unknown 383 unchanged. `validate.py` passes on the applied tree.
- **Yield is small by design:** 3 of 445 unknown-band rows closed here (0.7%). The other 442 need a different source or an owner ruling on company-wide counts.

## Method
Read the stored pages (S/persist/pic18-corpus-2026-11-16); `check.py` re-verifies each page's sha256 against the manifest (pass-2 pages are reader text with no raw file, so only holds may rest on them) and that every quote is a contiguous substring of its stored page. Five live fetches, each of a URL linked from a stored page (rule 14), raw bytes and journal in S/persist/pic18-size-ownsite-2026-11-18/ (`fetch.py`): Alpha Tool and Mold /employment/, Juzo USA The-Juzo-Family and Juzo-International, Swagelok /about/global and /about/legacy. None added a count. A count qualifies only if the company's own page gives its own current count, or a range inside one band; "over N", "nearly N", "about N" and "~N" are banded at N. `observed_date` is the stored fetch date (2026-11-16). Page dates, where shown, are in each evidence row's notes: GLI page metadata dateModified 2025-09-22 (datePublished 2022-12-16); Scott Molders footer copyright 2026, no publication date; Slesnick none.

## Verdicts (all 37 frame IDs; AGENTS 2.8 grammar: applied = VERIFIED, everything else STILL_UNCERTAIN with the settling fact)
Machine-readable: `verdicts.csv` (disposition, quote, URL, sha256, page date).

### Ohio-only (20)
| org | disposition | stated | band if it counted | quote (stored page) | settling fact / note |
|---|---|---|---|---|---|
| ORG-000416 | applied | 340 | 250-499 | GLI has grown nearly 400% since our inception and currently employs over 340 people on three shifts within our Youngstown facility. | Single Youngstown facility; "over 340". |
| ORG-000564 | applied | 30 | 10-49 | We employ ~30 people that work 2 shifts/5 days per week. | Single Kent plant. |
| ORG-001776 | applied | 60 | 50-99 | Slesnick Recycling has enjoyed growth, with two recycling facilities in Canton and Alliance, Ohio. They currently employ about 60 people that process  | Two Ohio facilities (Canton, Alliance); Slesnick Recycling is the S. Slesnick Company brand. |
| ORG-000157 | held | 1000 | 1000-4999 | We employ more than 1,000 people around the world | Page itself says worldwide (plants in Europe and the Americas); the Atlas Ohio-only site list cannot make it an Ohio count. Settles: an Ohio headcount, or an owner ruling. |
| ORG-000360 | held | 50 | 50-99 | We now employ just over 50 people with almost everyone working out of our main office in Twinsburg, OH. | Grain, band edge: "just over 50" sits at the 50-99 floor and "almost everyone" works at the Twinsburg office, so the Ohio count may be 49 or fewer. Settles: an Ohio-grain count (OSHA ITA, Form 5500) or a page stating the Twinsburg headcount. |
| ORG-000567 | held | 800 | 500-999 | 800+ Employees Worldwide | Attribution: record is Seco Machine (a brand of Stucki); the count is the Stucki group worldwide, 23 facilities. Settles: a Seco Machine page with its own count. |
| ORG-000598 | held | 900 | 500-999 | We are an organization of over 900 people | Attribution: Team Wendy states it is an Avon Technologies plc company; "we" may be Team Wendy or the Avon group. Settles: a page giving a Team Wendy headcount. |
| ORG-000600 | held | 1400 | 1000-4999 | More than 55 sites with 1,400 employees | Grain: Technoform group worldwide, 55 sites; Atlas holds one Twinsburg site. Settles: a Technoform North America count. |
| ORG-001592 | held | 20 | 10-49 | have 20 employees with 3,000 man-hours/month working capacity | Grain: sentence sits in the INJECTION MOLDING paragraph and may be that department only. The live /employment/ page has no count. Settles: a company-wide count. |
| ORG-001607 | held | 2130 | 1000-4999 | Our global organization is represented by 2,130 associates | Grain: the page says global organization; Atlas holds one Newbury site. Settles: an Ohio count or an owner ruling that a global count may stand for an Ohio-only record. |
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
A company-wide count needs an owner ruling before it can stand for an organization with sites outside Ohio. **Recommendation: do not count them; an Ohio count needs an Ohio-grain source (OSHA ITA, Form 5500, a plant page).**

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
| ORG-000007 | held_lead | 4500 | 1000-4999 | ~4,500 employees | Vibrantz global group count; org not Ohio-only. Needs owner ruling that a company-wide count may stand for a multi-state organization. |
| ORG-000009 | held_lead | 1700 | 1000-4999 | talented workforce of 1,700 employees worldwide | Worldwide count; not Ohio-only. |
| ORG-000030 | held_lead | 600 | 500-999 | Our growing company now employs over 600 people | North America-wide distributor; not Ohio-only. |
| ORG-000073 | held_lead | 500 | 500-999 | now employ more than 500 people in 23 locations worldwide | Two Professional Plastics pages give 500+ and 450+ across 23 locations in four countries; not Ohio-only. |
| ORG-000236 | held_lead | 3500 | 1000-4999 | 3,500+ TEAM MEMBERS | Two-country footprint count; not Ohio-only. |
| ORG-000278 | held_lead | 10000 | 5000+ | team of approximately 10,000 associates across the globe | Global count; not Ohio-only. |
| ORG-000651 | held_lead | 5000 | 5000+ | Advanced Drainage Systems has over 5000+ employees | National count; not Ohio-only. |
| ORG-001007 | held_lead | 25000 | 5000+ | 25,000 people working together | Global count; not Ohio-only. |
| ORG-004022 | held_lead | 1000 | 1000-4999 | headquarters based in Epe, the Netherlands, employs about 1000 people | Dutch headquarters count; not Ohio-only. |

## Self-refute (rule 15)
- self-refute: grain — 20 Ohio-only rows checked (+17 non-Ohio-only recorded, none written), 5 changed: GrafTech, Technoform and Kinetico moved from candidate to hold because the page itself says worldwide/global (an Atlas Ohio-only site list does not make a worldwide headcount an Ohio count); H.B. Chemical moved to hold because "just over 50" sits on the 50 band edge and "almost everyone" is at one office, so its Ohio count could read 49; Alpha Tool and Mold moved to hold because the "20 employees" sentence sits in the injection-molding paragraph.
- self-refute: founding — 3 rows checked, 0 changed (no founding or "since" year is used; GLI's "grown nearly 400% since our inception" is not read as a date).
- self-refute: strength — 3 rows checked, 0 changed (each is a narrative own-site sentence, no menu, tab or list item; all at the §4.13 ceiling supports_B, none higher).
- self-refute: truncated quote — 3 rows checked, 2 changed: the GLI and Slesnick quotes were extended back to the sentence that names the company and facility, so the claim and its subject are both in the quote.
- self-refute: attribution — 37 frame rows checked, 8 changed: Seco Machine (Stucki group page), Team Wendy (page says an Avon Technologies plc company; "we" may be the group), Youngstown Rubber Products (Midstate Sales page) and Pinnacle Recycling (Rumpke page) held; Eckart America (ECKART group page), SOPREMA Inc (group count), Synthomer, Inc. (Synthomer plc page) and Master Builders Solutions US LLC (global group page) reclassified from lead to no-claim. The three applied rows are each on the organization's own recorded website; "Slesnick Recycling" is the S. Slesnick Company's trade name on its own site (nav "About S. Slesnick").

## What was not checked
- No live re-fetch of the 3 applied rows: each rests on the stored 2026-11-16 page, which may have changed since.
- No second source for any applied count: a company statement is a band-level `supports_B` claim, not corroborated by OSHA or Form 5500 here (the government sources were spent on this frame).
- I did not look for Ohio-grain counts for the 17 non-Ohio-only rows.

## Check commands
`python3 tasks/pic18-size-ownsite-2026-11-18/build.py` (writes fills.csv, evidence_rows.csv, counts.json; `--apply` edits data/, idempotent) then `cd tasks/pic18-size-ownsite-2026-11-18 && python3 check.py [base-ref]` (default base = merge-base with origin/main). `check.py` diffs the whole `data/` tree against base (only the 3 band cells and 3 appended evidence rows may differ), recomputes counts against the controller frame and the stored corpus, then rejects 8 injected defects: band not containing the quoted count, verdict and fill both moved off the count, write to a non-Ohio-only organization, write to an organization with a non-Ohio site, write to a non-blank cell, write to a site row, quote not in its stored page, frame ID with no verdict. Last output: `PASS (applied): 3 fills, 3 evidence rows, 37 frame verdicts, 8 injected defects rejected`.

## Apply status
Applied 2026-11-18 on main e1df30e4 (after the market canary #385 merged): 3 organization cells in `data/organizations_OH.csv` and 3 appended rows in `data/evidence_organizations_OH.csv`; no other file or row changed (`check.py` diffs the whole `data/` tree). Outcome check at merge-base e1df30e4 vs HEAD: band_unknown 445 (56.0%) -> 442 (55.7%), exactly the 3 organizations filled; proc_unknown 331 and mkt_unknown 379 unchanged.

## Proposed follow-ups
- Owner ruling (the owner battery will carry company-wide counts as existing precedent, since `employee_band_ohio` is Ohio-grain; these 12 stay held leads meanwhile): may a company-wide own-site count stand for an organization whose page says it has sites or staff outside Ohio? (9 leads waiting, plus GrafTech, Technoform, Kinetico.)
- Five holds each need a page of the record's own giving its own count: Seco Machine, Team Wendy, Youngstown Rubber Products, Pinnacle Recycling, Alpha Tool and Mold (company-wide); H.B. Chemical needs an Ohio-grain count.
