# Site-name repair, pilot (2026-11-26)

Owner ruling 2026-11-25, "Fix site names, then close". Audit 13 smoke attempt 3 found 2 of 20 PIC-18 records with a contradicted `site_name`. This folder holds the pilot only; no `data/` row changes yet. Reproduce: `candidates.py [--raw FILE]`, then `pilot.py` (replays every quote against the retained page).

## Frame and yield (unit: PIC-18 sites, `scripts/regions.py`; active, tier A-C, street held)
- 727 sites. 606 (83%) have a retained readable page on their organization's own domain (2026-11-16 corpus plus the 2026-11-25 main-fetch run).
- 387 (53% of 727) have their street and city on one of those pages. For 239 of them a held name (site_name part, legal name or trade name) falls in a 350-character window around the street (a window match, not read); 102 print no name beside it; 46 print another name beside it.
- 79 candidates in `CANDIDATES.csv`: A, another name printed beside the street, no held name there (46); B, no held name on any retained page of the site (13); C, the page prints a legal or trade name beside the street but never the site_name's own part (26). Classes overlap.

## Pilot reads (44 sites; verdict grammar of AGENTS.md section 2 rule 8; `PILOT.csv`)
| Read | VERIFIED | STILL_UNCERTAIN | REJECT |
|---|---:|---:|---:|
| Class A, seeded draw of 25 (plus the 9 class-B sites outside it: B census 13, all read) | 3 | 2 | 29 |
| Class C, 10 of 26 read, chosen by me from a snippet triage (not a draw) | 5 | 3 | 1 |
| Found by hand, not by the finder | 1 | 0 | 0 |

Only one VERIFIED page (NextStep Arthropedix) states that the printed name is a division of the held operator. The other 8 are a brand, trade name or legal name printed beside the one street on the organization's own held website while the held `site_name` is a different one: the evidence is clean, but whether that is a rename is an owner question (AGENTS.md section 2 rule 9).

## Limits
- Recall is unmeasured. The finder reads a printed name by text pattern only; a page that prints the division where a held name also stands in the window is invisible to class A. The two smoke records were not available as known answers.
- Class C cut the held site_name to its distinctive words, so a one-word match hides a case (SITE-001843, found by hand).
- 23 of the 26 class C sites were judged from a snippet, not read in full; none of those 23 is in `PILOT.csv`.
- NextStep and HAR pages are pass-2 files: the corpus report says pass-2 direct hashes describe stored redacted HTML, so a binding proof may need a fresh capture.
- Token spend is not measured from provider logs. My context grew to about 280K tokens over roughly 60 calls; the cost sits in building and iterating the finder, not in the per-record reads (a few thousand tokens each).
