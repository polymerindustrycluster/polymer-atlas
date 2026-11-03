# Lane L1 report: PIC-18 new-county discovery, 2026-11-03

Input: 18 lead-fusion clusters (unit: federal lead clusters, Ashland, Columbiana, Erie, Huron, Richland, Tuscarawas counties, OH). 15 are SINGLE ECHO-only clusters, 2 are CORROBORATED ITA+ECHO (Veolia WTS, Dover Chemical), 1 is patent-only.

## Verdict mix (unit: clusters)
- VERIFIED: 0
- DUPLICATE_OF: 3 (LF-OH-00150 -> SITE-000863 / ORG-000798; LF-OH-00295 -> SITE-000813 / ORG-000751; LF-OH-00080 -> SITE-001910 / ORG-001919)
- REJECT: 2 (LF-OH-00089 General Latex: vacant property per EPA 2009-03-05; LF-OH-01404 Minnich: concrete vibrators, out of scope)
- STILL_UNCERTAIN: 13 (settling fact named per row in verdicts.csv)

## Proposed creates
0 new organizations, 0 new sites, 0 evidence rows. The create files hold headers only. registry_link_candidates.csv holds 4 rows (3 FRS with site_id, 1 EIN under R11) for held records, all to be verified at the source before minting.

## Dedupe hits
- Domain hits: doverchem.com (ORG-000798), cooperstandard.com (ORG-000755, ORG-001931), convertapax.com (ORG-000751), kraton.com (ORG-000925), iacgroup.com (ORG-003100), mondigroup.com (ORG-003156, Mondi Jackson LLC, a different entity; not merged).
- Address hits that dedupe-check missed: SITE-000863 and SITE-001910 hold their street only in notes (street_address column blank), so step 3 returned 0. Found by grepping notes of all site shards.
- Cooper Standard: SITE-000818 (ORG-000755) and SITE-001925 (ORG-001931) share street 2228 Reiser Ave SE and coordinates. Possible duplicate org/site pair for the integrator; this lane did not touch it.

## Form 5500 check
Run against tasks/form5500-spine-2026-11-01/sponsors.csv (bulk EFAST2 derived, generated 2026-11-01) by city and name for all 18 leads: no filing whose address is one of the establishments. Veolia WTS EIN 231503731 files from Trevose PA; Kraton files from Jacksonville FL / The Woodlands TX. So nothing blocks the two REJECTs; the closure-flavored leads (Arizona Chemical, IAC Huron, Abbott Plant 3) stay STILL_UNCERTAIN for lack of a dated outcome record, not because of 5500.

## Hygiene and caveats
- WebFetch returns model-processed text, not raw page text, so quotes in verdicts.csv are not script-checked as substrings of raw fetched text. No quote supports a create. The integrator should re-fetch before relying on any quote.
- Availability failures (never evidence): Kraton newsroom (nav only), plasticstoday.com and plasticsnews.com (403), Bloomberg (bot wall), cooperstandard.com ISG page (307), minnich-mfg.com (title only), EPA 2008 CSM PDF (size cap).
- Most SINGLE clusters have no discoverable own site; most are old ECHO-only registrations (latest activity 1993-2019). Operating_status active could not be supported for any of them.
- No new vocabulary gaps (no create rows). ECHO NAICS for Westside Towing (325510) and Abbott Plant 3 (326299) look miscoded.
- Counting: all counts above are clusters unless stated; none are establishments or organizations.
- Dry run: temp copy of data/ validated with ATLAS_DATA_DIR; zero rows appended because there are zero creates; scripts/validate.py exit 0 ("OK - validation passed"). Temp copy deleted.
