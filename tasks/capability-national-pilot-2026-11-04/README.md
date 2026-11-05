# Capability terms from companies' own sites: national pilot (2026-11-04)

The repo owner chose this pass in session on 2026-11-04, as a pilot of about 100 organizations before scaling. It
repeats `tasks/capability-pass-2026-11-04/` (66 NE Ohio organizations) at national scale.

## Sample
The pool is the active Ring 1–2 organizations with a website and **no** `processes` or `materials`: 2,110 of them, after
excluding the 137 organizations touched by open PRs #122 and #123. 100 were drawn at random (seed 1104), across 28
states, and split into four packet lanes (`lanes/F1`–`F4`, brief in `LANE_BRIEF.md`).

The lanes read each company's own site. They recorded every SCHEMA §3.1 / §3.2 term the site explicitly states, with
one verbatim quote per term. Nothing was inferred.

## Lane outcomes (unit: sampled organizations; 100)
| Status | Orgs |
|-|-:|
| TERMS_FOUND | 80 |
| NO_TERMS (the site states no vocabulary term) | 10 |
| SITE_DOWN | 5 |
| WRONG_SITE (the domain no longer serves the company) | 5 |

## Raw check and build
- **`rawcheck_tool.py`** re-fetched every page (Firecrawl, then Jina Reader) and matched each quote as a word sequence.
  296 of 327 term quotes passed; 13 were not on the page, and 18 pages could not be fetched.
- **`build.py`** is reused from the earlier capability pass, with two guards added:
  - a term counts only when its page is on the record's own website domain;
  - `pvc` needs the quote to say PVC (a lane had mapped "vinyl" windows to `pvc`).

## Applied (74 organizations)
| Change | Rows |
|-|-:|
| `processes` cells filled with SCHEMA terms | 64 |
| `materials` cells filled with SCHEMA terms | 64 |
| `scope` evidence rows carrying each term's quote (`own_site`, `supports_A`) | 292 |
| `last_verified` → 2026-11-04 | 73 |

Evidence ids are EVD-128001 to EVD-128292, above every open PR. There are no tier moves.

The commonest terms are `polyethylene_pe` (19), `injection_molding` (14), `assembly_secondary_ops` (12),
`elastomers_rubber` (8) and `polypropylene_pp` (8).

## Held (`holds.csv`, 35 terms)
- 31 failed the raw check.
- 2 were quoted from another domain: Olin's olinepoxy.com and Polytex's parent group site.
- 2 were `pvc` terms inferred from "vinyl".

## Findings for other passes (not applied)
- **Websites that now serve unrelated content.** W.B. Wagner's domain redirects to a gambling spam site. HPE
  Extrusion's serves an unrelated sports-news page. Federal Process's serves a blank ad page. Paddington Group's is for
  sale. These are leads for the website hygiene and ownership passes.
- **HQ disagreements.** Clearly Clean's site gives Frackville, PA, where the record has Orwigsburg. Ronald Mark's names
  a Pitman, NJ plant, where the record has Hillside.
- **Yield.** 74 of 100 sampled organizations gained at least one term (80 had terms before the raw check). Scaling to
  the full pool of about 2,100 would fill roughly 1,500 records at this rate.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0 on the committed tree.
