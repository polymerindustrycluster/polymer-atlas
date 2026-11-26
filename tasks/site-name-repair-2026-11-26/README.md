# Site-name repair, finder and pilot (2026-11-26)

Owner ruling 2026-11-25, "Fix site names, then close". Audit 13 smoke attempt 3 found 2 of 20 PIC-18 records with a contradicted `site_name`. This folder holds the finder and the pilot only; no `data/` row changes yet. Reproduce: `candidates.py [--raw FILE]`, then `pilot.py` (replays every quote against the retained page). Check: `candidates.py --selftest` (10 planted cases and the two known answers; exit 1 on any miss).

## Frame and yield (unit: PIC-18 sites, `scripts/regions.py`; active, tier A-C, street held)
- 727 sites. 617 (85%) have a retained readable page on their organization's own domain (2026-11-16 corpus plus the 2026-11-25 main-fetch run), counting the host the held website redirects to.
- 391 (54% of 727) have their street and city on one of those pages. For 240 of them a held name (site_name part, legal name or trade name) falls in a 350-character window around the street (a window match, not read).
- 115 candidates in `CANDIDATES.csv`. Classes overlap: A, the run before the street differs from every held name and no held name is in the window (35); B, no held name on any retained own page (14); C, a legal or trade name beside the street, never the site_name's own part (27); D, a held name plus a following word, such as "<name> Division" (19); E, as A with a held name also in the window (37).

## Known answers (controller, audit 13 smoke: site_name CONTRADICTED, confirmed by hand)
The first finder had 0 of 2: SITE-000646 and SITE-001778. Causes, found from stage flags and URLs without reading either page: the page prints the held name plus "Division" and the finder dropped "division" as a generic word (now class D); the held website redirects to another host and the own-domain test discarded every page (now counted as own). Both are now candidates (000646: D; 001778: A and B). `--selftest --against <old CANDIDATES.csv>` fails on the first finder's output and the selftest passes on this one. Two known answers are a smoke test, not a recall estimate.

## Old 79 against new 115
68 stay, 11 drop, 47 are new. All 14 pilot reads that were VERIFIED or STILL_UNCERTAIN are still candidates. The 11 that dropped are noise in their printed text (a footer, a navigation line, a section label); none was a pilot VERIFIED or STILL_UNCERTAIN.

## Pilot reads (44 sites, from the first finder; verdict grammar of AGENTS.md section 2 rule 8; `PILOT.csv`)
| Read | VERIFIED | STILL_UNCERTAIN | REJECT |
|---|---:|---:|---:|
| Class A, seeded draw of 25 (plus the 9 class-B sites outside it) | 3 | 2 | 29 |
| Class C, 10 of 26 read, chosen from a snippet triage (not a draw) | 5 | 3 | 1 |
| Found by hand, not by the first finder | 1 | 0 | 0 |

Only one VERIFIED page (NextStep Arthropedix) states that the printed name is a division of the held operator. The other 8 print a brand, trade name or legal name beside the one street on the organization's own held website while the held `site_name` is a different one: the evidence is clean, but whether that is a rename waits for the owner's scope ruling. Nothing in classes D and E (new) and nothing new in A to C has been read.

## Limits
- Recall is unmeasured beyond the two known answers. Class E and D are untested for precision; E is the noisiest.
- 23 of the 26 first-pass class C sites were judged from a snippet, not read; none is in `PILOT.csv`.
- A held website that redirects counts as own; the binding gate's own-domain test (`own_domain(source, record website)`) may not, so a rename row for such a site (SITE-001778) may need the held website updated first.
- NextStep and HAR pages are pass-2 files: the corpus report says pass-2 direct hashes describe stored redacted HTML, so a binding proof may need a fresh capture.
- Token spend is not measured from provider logs.
