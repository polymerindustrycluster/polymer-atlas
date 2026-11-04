# Lane L1 notes (STRONG wave, NC, 2026-11-04)

18 input rows, 18 verdict rows in `verdicts.csv`. Every own_quote was re-fetched through Jina Reader and matched after whitespace and markdown normalization (script check, 12 of 12 quotes found).

## Counts
- VERIFIED_NEW_ORG 7: LF-NC-00148 Bonset, 00245 Darnel, 00113 Modern Polymers, 00204 R&D Plastics of Hickory, 00255 Premiere Fibers, 00775 Urethane Innovators, 00408 Thunderbird (parent Thunderbird LLC).
- VERIFIED_NEW_SITE 6: 00037 Plastek -> ORG-002315 (B), 00021 Sonoco -> ORG-003930 (B), 00109 Carpenter -> ORG-002348 (B), 00102 Surteco -> ORG-002199 (C), 00055 Amcor Asheville -> ORG-000665 (C), 00011 Sherwin-Williams Howard St -> ORG-000132 (C).
- DUPLICATE_OF 1: 00417 FXI -> SITE-004720.
- STILL_UNCERTAIN 3: 00018 Sherwin-Williams Stage Coach Trail, 00238 Berry/Amcor Monroe, 00185 Hayward Clemmons.
- REJECT 1: 00024 Goulston (scope).
- No closures found.

## Flags for the integrator
1. **FXI dupe missed by tool.** Held SITE-004720 stores the street as `2222 SURRET T DR` (typo), so dedupe step 3 returned nothing. County conflict: held RANDOLPH vs federal Guilford.
2. **Scope question (owner ruling, not self-ruled).** Premiere Fibers (LF-NC-00255) makes melt-spun synthetic filament yarn (NAICS 325220, a supporting-signal code in SCHEMA 2.2; `fiber_filament` exists as a product form). Written as VERIFIED_NEW_ORG tier C on the strength of the existing map; hold it if the owner does not admit fibre producers. Goulston (LF-NC-00024) is the opposite case: fiber-lubricant chemicals sold to synthetic-fibre spinners, no polymer made, so REJECT on scope. If the owner treats synthetic-fibre suppliers as Ring 3, reopen it.
3. **Plastek duplicate orgs.** ORG-002314 (Plastek Grp-Spectrum Molding) and ORG-002315 (Plastek Industries, Erie) look like two rows for one company. Hamlet was attached to ORG-002315 (federal registrant name and HQ site).
4. **Sonoco held-org choice.** Fusion pointed to ORG-001117 (TOPPAN Packaging Americas) by trade name 'Sonoco'. The Forest City plastics plant is current on sonoco.com, so it goes under ORG-003930 Sonoco Products Company.
5. **Surteco entity.** ORG-002199 `Surteco North Amer Inc.` (Auburn PA) is a notes-only step-4 match; same group but entity confirmation is the integrator's. Own site also lists a Monroe NC SURTECO site (2011 N Rocky River Rd) not in this lane. Own site does not say which location extrudes; site rests on federal rows (C).
6. **Darnel.** Own site names a 'Charlotte, NC' production site, never Monroe or 1809 Airport Rd, so the site stands on federal rows (C). HQ left blank because the pages do not state one; choose between Darnel, Inc. and the group as the org.
7. **Thunderbird.** HQ Oak Brook IL from thunderbirdllc.com; county not stated. Sibling molding sites (Elkhart IN, Shelbyville IN, Elgin IL) are follow-up leads.
8. **Berry Monroe (STILL_UNCERTAIN).** Berry merged into Amcor 2025-04-30; the fusion step-4 ref ORG-004278 (Magnera) matches by notes only. Needs an own-site page naming Monroe plus the operating entity.
9. **Hayward (STILL_UNCERTAIN).** Large site (500-999). Only syndicated Hayward job posts describe a Clemmons injection molding operation; the own-site Clemmons text is JS-state and was not in the fetched text. One own-site or careers page settles it.
10. **Sherwin-Williams.** Howard St is federal-only plus an NC DOL page (Paint and coating Manufacturing). Stage Coach Trail: the only own-site page for that street is a design center, hence STILL_UNCERTAIN.

## Method
- Dedupe: `atlas.py dedupe-check` by name, street, domain for all 18; brand and common-name rg over all org and site shards (Darnel, Goulston, Modern Polymers, R&D/R-D Plastics, Surteco/Canplast, Premiere Fibers, Hayward, Urethane Innovators, Thunderbird, Bright/Williams/Indiana Plastics, Bonset, Magnera). Held-org site lists checked for ORG-000132, -000665, -000853, -001117, -002348, -003930.
- Fetches: TinyFish fetch_content for own pages; Jina Reader for body text of the JS-shell Bonset pages and for quote verification. Search snippets were never used as quotes.
- No Form 5500 check was needed: no REJECT for closure or no-establishment was written.
- Page instructions: none seen addressed to an AI.
- `processes`/`materials` only where a fetched page states them; Sherwin-Williams Howard St, Amcor, Bonset (process) and Premiere Fibers (process) left blank on purpose.
