# Capability terms from companies' own sites: national pilot (2026-11-04)

The repo owner chose this pass in session on 2026-11-04, as a pilot of about 100 organizations before scaling. It
repeats `tasks/capability-pass-2026-11-04/` (66 NE Ohio organizations) at national scale.

**Stacked on #123, which is stacked on #122.** Merge #122, then #123, then this PR. All three append to the same
evidence shards, so stacking avoids end-of-file conflicts.

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
| `processes` cells filled with SCHEMA terms | 61 |
| `materials` cells filled with SCHEMA terms | 63 |
| `scope` evidence rows carrying each term's quote (`own_site`, `supports_A`) | 264 |
| `last_verified` → 2026-11-04 | 73 |

Evidence ids are EVD-128001 to EVD-128264, above every open PR. There are no tier moves.

## Review
Grok tried to refute a random 60 of the first build's 292 terms (deep effort, read-only). It marked 48 OK. Checked
against the quotes, 9 of its flags held. In each, the quote mentions a process or material without saying the company
does it:
- the company uses extrusions as inputs;
- a float has a rotomolded shell;
- a material is being developed for others to extrude;
- a product is compared against thermoformed blisters;
- a quote states only a property of nylon;
- the other four are in `build.py`.

Those 8 terms are held (`COUNCIL_HELD`), and the bare-word "Foam" falls under the next rule. Every term whose quote is
three words or fewer is now held as too thin: 20 more terms. Two of grok's flags were rejected. Kracor's own domain is
the record's website, so it is this company. Replex is a thermoformer describing its own process.

A codex pass was stopped by the machine for low memory before it returned. The sampled error rate was about 15% before
these rules. Scaling this pass needs a stricter lane brief, requiring a quote that says the company itself does the
process, and a second-family check.

The commonest terms are `polyethylene_pe` (19), `injection_molding` (14), `assembly_secondary_ops` (12),
`elastomers_rubber` (8) and `polypropylene_pp` (8).

## Held (`holds.csv`, 63 terms)
- 31 failed the raw check.
- 20 had a quote of three words or fewer.
- 8 were held after review.
- 2 were quoted from another domain: Olin's olinepoxy.com and Polytex's parent group site.
- 2 were `pvc` terms inferred from "vinyl".

## Findings for other passes (not applied)
- **Websites that now serve unrelated content.** W.B. Wagner's domain redirects to a gambling spam site. HPE
  Extrusion's serves an unrelated sports-news page. Federal Process's serves a blank ad page. Paddington Group's is for
  sale. These are leads for the website hygiene and ownership passes.
- **HQ disagreements.** Clearly Clean's site gives Frackville, PA, where the record has Orwigsburg. Ronald Mark's names
  a Pitman, NJ plant, where the record has Hillside.
- **Yield.** 74 of 100 sampled organizations gained at least one term (80 had terms before the raw check). Scaling to
  the full pool of about 2,100 would fill roughly 1,500 records at this rate, after the brief is tightened (see Review).

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0 on the committed tree.
