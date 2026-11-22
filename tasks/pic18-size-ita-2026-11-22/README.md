# PIC-18 site size bands from OSHA ITA, 2026-11-22 (lane atlas-w22-size-ita)

Owner pick 2026-11-22, "PIC-18 unknowns pilot". Fill blank `employee_band_site` from OSHA ITA Form 300A CY2025 annual average employees (SCHEMA §1 R13, source 1) on a fixed frame of 23 site/establishment pairs (`frame.csv`, copied from the controller's brief, byte-identical). Claim: `tasks/QUEUE.md` (`claimed:claude-code 2026-11-22`, EVD-470000..470099). First user: the Atlas owner, for prospecting by size; non-use is a finding if no prospecting list uses the band by 2026-12-20.

## Result (unit: site records in the 23-pair frame; organizations counted as PIC-18 organization rows)
- **Applied: 12 site records** (blank-only; band only), across **11 organizations** (ORG-000035 owns two). Bands: 10-49 x5, 100-249 x4, 50-99 x1, 250-499 x1, 500-999 x1. Evidence: 12 `size_band` rows, `government_filing` / `supports_B`, EVD-470000..470011. Site tiers are unchanged (A/B/C as before; a size band is not a tier input).
- **Held: 11 site records**, all STILL_UNCERTAIN with the settling fact (table below).
- **Outcome** (`python3 S/harness/pic18_unknown.py "$PWD" <ref>`; unit: PIC-18 organization rows = 794; S = controller storage): `origin/main` 17834918 **band_unknown = 443 (55.8%)**; HEAD **band_unknown = 431 (54.3%)**: a fall of exactly 12... see the PR body for the final run (the harness reads committed trees).
- Controller disposition vs mine: I disagree on **5** rows, all toward hold: SITE-000250 and SITE-002114 (R13, the OSHA inspection `nr_in_estab` band is 4 and 5 bands away: 1000-4999 and 5000+; 2026-11-02 `band_updates.csv` already statused both REVIEW, `inspection_differs_by_5_bands`), SITE-000639 (a second ITA establishment, "Technoform TGI" id 1458057, 30 avg, files at the same suite; the site's true band could be 100-249 if the record covers both), SITE-002965 (the same establishment id is also bound to closed SITE-001800, same organization, blank street: a dedupe lead), and SITE-000138 was already a hold but I add that its name is tied (the hold is reliability only). The judgment-eligible rows 000264, 000383, 000620, 001109 are applied (see Judgment calls).

## Verdicts (AGENTS 2.8 grammar: applied = VERIFIED; everything else STILL_UNCERTAIN). Machine-readable: `verdicts.csv`
`street/name` = how the record's street and the operator name matched the ITA row (`key_equal` = equal after normalisation; `judged` = a named exception below; `no` = failed).

| site | ITA establishment_id | disposition | band | evidence | street/name | held: settling fact |
|---|---|---|---|---|---|---|
| SITE-000035 | 656015 | applied | 100-249 | EVD-470000 | key_equal/key_equal | - |
| SITE-000043 | 1500985 | applied | 10-49 | EVD-470001 | key_equal/key_equal | - |
| SITE-000062 | 941625 | applied | 10-49 | EVD-470002 | key_equal/key_equal | - |
| SITE-000138 | 1454209 | held | - | - | key_equal/key_equal | ITA reliability='review', size_code_vs_avg='inconsistent' (settles: an amended filing or a second source for the count) |
| SITE-000250 | 1433741 | held | - | - | key_equal/key_equal | R13: OSHA inspection nr_in_estab bands ['1000-4999'] are more than one band from ITA 10-49 (settles: review of which count is the establishment's) |
| SITE-000264 | 1477377 | applied | 50-99 | EVD-470003 | judged/key_equal | - |
| SITE-000297 | 920442 | held | - | - | no/key_equal | no recorded street_address (settles: an address pass that records the street, then re-test) ; ITA reliability='review', size_code_vs_avg='inconsistent' (settles: an amended filing or a second source for the count) |
| SITE-000383 | 902411 | applied | 10-49 | EVD-470004 | key_equal/judged | - |
| SITE-000450 | 1403938 | applied | 250-499 | EVD-470005 | key_equal/key_equal | - |
| SITE-000517 | 1401244 | held | - | - | no/key_equal | different street: record '200 INDUSTRIAL PARKWAY', ITA '220 Park Drive' (settles: which address is the establishment's) |
| SITE-000519 | 1448582 | held | - | - | no/key_equal | no recorded street_address (settles: an address pass that records the street, then re-test) ; ITA reliability='review', size_code_vs_avg='inconsistent' (settles: an amended filing or a second source for the count) ; establishment bound to 2 site records ['SITE-000519', 'SITE-000520']: dedupe lead, never merged here (settles: an integrator dedupe ruling) |
| SITE-000522 | 69522 | applied | 10-49 | EVD-470006 | key_equal/key_equal | - |
| SITE-000620 | 1067222 | applied | 100-249 | EVD-470007 | judged/key_equal | - |
| SITE-000639 | 1451043 | held | - | - | key_equal/key_equal | more than one ITA establishment at the address |
| SITE-000683 | 922771 | held | - | - | key_equal/key_equal | ITA reliability='review', size_code_vs_avg='inconsistent' (settles: an amended filing or a second source for the count) ; establishment bound to 2 site records ['SITE-000683', 'SITE-001725']: dedupe lead, never merged here (settles: an integrator dedupe ruling) |
| SITE-000863 | 260187 | applied | 100-249 | EVD-470008 | key_equal/key_equal | - |
| SITE-001109 | 1154717 | applied | 10-49 | EVD-470009 | judged/key_equal | - |
| SITE-001137 | 281495 | applied | 500-999 | EVD-470010 | key_equal/key_equal | - |
| SITE-001397 | 1113070 | applied | 100-249 | EVD-470011 | key_equal/key_equal | - |
| SITE-001725 | 922771 | held | - | - | key_equal/key_equal | ITA reliability='review', size_code_vs_avg='inconsistent' (settles: an amended filing or a second source for the count) ; establishment bound to 2 site records ['SITE-000683', 'SITE-001725']: dedupe lead, never merged here (settles: an integrator dedupe ruling) |
| SITE-002110 | 498112 | held | - | - | no/key_equal | no recorded street_address (settles: an address pass that records the street, then re-test) |
| SITE-002114 | 1079717 | held | - | - | key_equal/key_equal | R13: OSHA inspection nr_in_estab bands ['5000+'] are more than one band from ITA 50-99 (settles: review of which count is the establishment's) |
| SITE-002965 | 1450510 | held | - | - | key_equal/key_equal | establishment bound to 2 site records ['SITE-001800', 'SITE-002965']: dedupe lead, never merged here (settles: an integrator dedupe ruling) |

## Method
`build.py` re-derives each disposition from the site row, its organization row, the CY2025 ITA row (`tasks/osha-ita-2026-11-01/establishments.csv`) and the 2026-11-01 OSHA-inspection spine (`tasks/osha-spine-2026-11-01/band_proposals.csv`, the R13 cross-source), then writes `verdicts.csv`, `fills.csv`, `evidence_rows.csv`, `counts.json`; `--apply` edits `data/` and is idempotent. Batch 5's binding is not trusted: the street and the name are re-tested from the recorded `street_address` and names, and every establishment is counted against all site records carrying a witness for it, tree-wide. The band is the SCHEMA §4.4 band of `annual_average_employees`; the file's own `band_from_avg_employees` column is asserted equal.

Per fill, on the site row: `employee_band_site` and a `BAND-SOURCE: ... filed <date>` note suffix (the 2026-11-02 pass's convention). Per fill, one `size_band` evidence row in the format of the 413 rows by "claude-code size-band-evidence-2026-11-03", appended to the shard's tail (the shard already has 30 out-of-order spots; a re-sort would have rewritten other waves' rows). `observed_date` 2026-11-01 = the date the CY2025 file was extracted; nothing was re-read from OSHA today. `source_ref` is the named-source form with a parenthesised URL, so V-66 (archive at capture) does not apply and no archive link is owed; `validate.py` passes.

## Judgment calls (each is named in `build.py` and re-tested in `check.py`)
- SITE-000264 Blair Rubber: record "5020 Enterprise Parkway", filing "5020 Enterprises pkwy": plural in the filing; same number, same city, one ITA establishment at the address.
- SITE-000620 Speed North America: record "1700A Old Mansfield Road", filing "1700 Old Mansfield Rd": a unit letter on the record's number; same operator, same city, one ITA establishment at the address, no other Speed site on that street. The settling fact if a reviewer disagrees: a record or filing showing 1700A is a different premises.
- SITE-001109 Paramont Machine Company: "Commercial" / filing typo "Commerical"; same number, same city, same operator.
- SITE-000383 GRAFIX: filing name "Graphic Arts Systems Inc"; the organization's own trade name on the record is "Graphic Art Systems Inc" (one letter), same street. Applied on that tie.
- Quadrant suffixes (SE, S.E., NW, N.W.) and "Suite" tails are ignored when trailing; a leading N/S/E/W is kept.

## Deviations and limits
- **No headcount anywhere.** The 413 existing size-band rows put "annual average employees 79" in `claim_detail`; these rows say only "annual average employees in <band>". The existing rows are never edited (proposed follow-up below).
- **`employee_count_source_date` has no column on sites** (SCHEMA §4.4 names it for organizations' bands; §4.5 sites carry none). The filing date goes in the `BAND-SOURCE` note and the evidence row, as on 2026-11-02.
- R13 cross-source check covered: the 2026-11-01 OSHA inspection spine, Form 5500 spine, PPP packet (none of the 23 sites holds a PPP band; SITE-000620 is a PPP hold), existing site and organization bands (all 23 sites and their organizations were blank), and existing `size_band` evidence rows (none).

## What was not checked
- Batch 5 bound later OSHA inspections to some of these sites; the raw inspection bulk file is not in the repo or the controller storage, so their `nr_in_estab` was not compared (only the 2026-11-01 spine was). An unseen disagreement of more than one band would have been held.
- No live re-read of any ITA filing; CY2025 only (no earlier year to test stability).
- The ITA count is an annual average for the filing establishment; whether the Atlas site record covers exactly that establishment is the premise of rule 1, tested by street and operator name only.

## Proposed follow-ups (not commitments; owner rulings are not settled here)
1. Dedupe leads for the integrator: SITE-000683/SITE-001725 (one establishment, 922771, two active A/B records, same organization and street); SITE-002965/SITE-001800 (establishment 1450510; SITE-001800 is closed with a blank street); SITE-000519/SITE-000520 (establishment 1448582; blank streets). Never merged here.
2. Street fill candidates that would unlock holds: SITE-000297, SITE-000519, SITE-002110 (batch-5 witnesses quote the street; the record's `street_address` is blank). SITE-000519 also needs a clean ITA reliability.
3. SITE-000517: record street 200 Industrial Parkway vs ITA 220 Park Drive (Chardon): which address is the establishment's.
4. Technoform: the Atlas site may need to say whether it covers "Technoform TGI" (second ITA establishment at the same suite).
5. Owner/schema: an `employee_count_source_date` column for sites; and whether the 413 existing `size_band` rows should drop the headcount from `claim_detail` (append-only §4.13 means a superseding practice, not an edit).

## Named check (commands and results are in the PR body)
`python3 tasks/pic18-size-ita-2026-11-22/check.py [base-ref]` (own matcher and band table, independent of `build.py`): recomputes each band from `establishments.csv`, re-tests the street and name rule from the data rows, asserts held rows are untouched, applied + held = 23, diffs the whole `data/` tree against the base (only 12 band cells with note suffixes and 12 appended evidence rows may differ), asserts the evidence block is above the base maximum, and plants 8 defects (a band on a held site, a wrong band, a band on the different-street site, a band on a shared-establishment site, a missing evidence row, a headcount in an evidence row, an out-of-block evidence ID, a held verdict flipped) and requires each to fail.
