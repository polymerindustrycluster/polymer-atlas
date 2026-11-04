# L2 notes (NJ STRONG wave, 2026-11-04)

Input: 16 clusters. Output: `verdicts.csv` (16 rows, one per cluster, 22 columns in brief order).
Every non-empty `own_quote` was re-fetched from `own_url` after the file was written and found verbatim
(whitespace and curly quotes normalized); the Datwyler quote is from a PDF read with pdftotext.

## Counts
| Verdict | n | Clusters |
|-|-|-|
| VERIFIED_NEW_SITE | 3 | 00191 Datwyler (B), 00261 Amcor Millville (C), 00051 Saint-Gobain Wayne (C) |
| VERIFIED_NEW_ORG | 7 | 00460 Pan Technology, 00437 Innovative Resin Systems, 00471 Rotuba, 00615 Merlin, 00381 Keystone Plastics, 00535 Minor Rubber, 00568 Infra Pipes (Endot) |
| REJECT | 4 | 00127 Spex, 00520 Firmenich, 00073 American Flux, 00013 Spectra Colors |
| STILL_UNCERTAIN | 2 | 00091 Avantor, 00844 Cases By Source |
| DUPLICATE_OF | 0 | |

Totals: 3 + 7 + 4 + 2 = 16.

## Integrator flags
1. **Saint-Gobain Wayne (00051) and Amcor Millville (00261) are federal-only C sites** with no own-site witness.
   Saint-Gobain's sites bot-block every route (403, Jina challenge, TinyFish bot_blocked); I found no amcor.com page
   naming Millville. Both sit under held orgs whose scope is already proven. Same treatment as held SITE-006421
   (Franklin IN). If you want a stricter reading of "page must show in-scope work", hold both at STILL_UNCERTAIN.
2. **HQ left blank (rule: own site must state it)** for Pan Technology (00460) and Minor Rubber (00535): each own site
   prints one company address but never labels it headquarters. Carlstadt NJ / Bergen and Bloomfield NJ / Essex are the
   obvious fills if you accept the sole-address reading.
3. **Foreign HQ:** Infra Pipes (00568) HQ is Mississauga, Ontario, Canada (own Locations page). Entered Canada in
   `org_hq_state`. Needs the INTL placement rule. Held ORG-003210 United Poly Systems (SC) has `ultimate_parent_name`
   Infra Pipes; this new org is the parent target. Federal registrant is Endot Industries, Inc.
4. **Scope questions (owner rulings, not self-ruled):**
   - Pan Technology (00460): inks and coatings are Ring 2, but the core line is pigment dispersions for coatings and inks.
   - Merlin Industries (00615): vinyl pool liners and mesh safety covers fabricated from purchased film and fabric; own
     site does not state the process. Tier C, processes `fabrication_unspecified`.
5. **Datwyler (00191):** new site 9012 Pennsauken Hwy under held ORG-004822 (HQ Middletown DE). The same certificate lists
   a second building at 9009 Pennsauken Hwy with rubber closure mixing, molding and finishing; decide whether it is a
   separate site. The certificate expires 2026-09-18, so no certification is recorded.
6. **Brand checks (addendum item 3):** searched the org shards by domain and name for each new org and for brands Pen
   Company of America (Rotuba), PanTINT, Rez-Cure, EndoPure/EndoPoly, kpbrush; no held org or site matched.
7. **Counties filled from public geography** where the federal row was blank: Hamilton (Mercer), Rockaway (Morris),
   Bloomfield (Essex), Mahwah (Bergen), Plainsboro (Middlesex). Rotuba's 'Union County' is normalized to Union.
8. **Closures:** none found. No row was rejected for closure.
9. **Still open:** Avantor Phillipsburg (00091) needs an Avantor page naming what the plant makes (ITA NAICS 325211 is
   unexplained; lean REJECT). Cases By Source Mahwah (00844) needs a page saying molding, thermoforming or foam cutting
   happens at 40 Whitney Road (lean Ring 3/4 design-and-sourcing, not a Ring 1 site).
10. **Spex (00127)** reject rests on the company's own submitted profile on spectroscopyonline.com because spex.com is
    behind a Cloudflare wall; `own_url` is blank for that row.

## Method notes
- Dedupe: `atlas.py dedupe-check` run per row; hits only for Datwyler (step 2), Amcor (step 1/4), Saint-Gobain (step 2/4).
  All other rows had zero hits at steps 1-4.
- Fetch route: direct request, then Jina fallback per the addendum; `own_url` is always the company's own URL.
- Search snippets were used to find pages, never as quotes. Page text addressed to an AI: none seen.
- naics_primary filled only where the set holds one 6-digit code (Pan 325510, Datwyler 326299, Merlin 326199,
  Saint-Gobain 326121, Infra Pipes 326122, Spex/American Flux 325998 as given).
