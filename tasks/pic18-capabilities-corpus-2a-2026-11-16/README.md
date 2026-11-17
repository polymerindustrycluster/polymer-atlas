# PIC-18 capabilities from the corpus, slice 2A — 2026-11-16

Lane CAP2A (`atlas-w16-cap2a`, Claude Sonnet 5.5), designated integrator for this slice only. One draft PR, no merge. Output: `data/sites_OH.csv` (processes, materials only), `data/site_capabilities.csv` (CAP-001200+), `data/evidence_sites_OH.csv` (EVD-387000+).
First user: PIC cluster reporting analyst (counts by process). Review date: 2026-12-16 (non-use is a finding if process counts are not being read).

## Slice
PR #351 (`tasks/pic18-capabilities-corpus-2026-11-16`, merged by the time of this PR) built a frame of 224 active tier A–C PIC-18 Ohio sites with one active Atlas site per organization and a blank process or material cell, and adjudicated 4 of them. The other 220 are listed in `pr351_unadjudicated_sites.txt` (from its `verdicts.csv` at head 19c0120). **This slice is the first 110 of those 220 by site_id** (`slice.csv`; SITE-000014 to SITE-001468). Unit: Ohio sites (establishments), active, PIC-18 counties, tier A 17 / B 22 / C 71. `check.py` recomputes the #351 frame criteria at the pinned base (`base.txt`, origin/main 19bd1aa, after #351 and later merges; the build was first run on 4abc9eb and replayed on 19bd1aa with identical output) and asserts every slice site is still in it. The second half (110 sites, SITE-001479 onward) is not in this PR.

## Result (units named; `summary.json` is the source)
| Unit | Count |
|---|---|
| Sites in slice (active Ohio PIC-18 sites; tier A 17, B 22, C 71) | 110 |
| Sites with at least one verified term | 19 |
| Sites whose §3 cell gained a tag (tier A 1, B 4, C 10) | 15 |
| Site rows changed (processes/materials cells only, blank cells filled) | 15 |
| Term decisions (site × field × term): processes 26, materials 37; narrative 56, menu/list 7 | 63 |
| …of which applied as §3 tags with evidence | 52 |
| …of which tag held because the cell was not blank at base (b02 fill-blank rule) | 10 on 7 sites |
| …of which capability row only (tier B, C-strength, owner ruling 2026-11-14) | 1 (SITE-000667 Vinylume) |
| Evidence rows, `evidence_sites_OH.csv` (supports_A 48; supports_C 4, all on tier C sites) | 52 (EVD-387000..387051) |
| Capability rows, `site_capabilities.csv` (materials 31, processes 14; all `company_disclosed`) | 45 on 15 sites (CAP-001200..001244) |
| Sites held with no verified term (STILL_UNCERTAIN) | 91 (SITE-000591 also carries one term-level hold) |

Yield: 15 of 110 slice sites (14%) gained a §3 tag and 19 of 110 (17%) have a verified term. PR #351 gained 3 of 224 (1.3%).
**Fill-blank vs append (needs a controller call).** 10 verified terms on 7 sites were not tagged because the cell already held other values (`distribution`, `machinery_equipment`, `tooling_mold_die`, `recycling_recovery`; none is a §3.1 process term): SITE-000243, 000458, 000562, 000618, 000707, 001109, 001125. Their capability rows are minted where §3.6 has a term. Recommendation: append the 10 terms (rerun `build.py` after changing one line); each already has its quote and locality witness in `decisions.csv`.

## Verified terms by site (every row also in `verdicts.csv`)
| Site | Tier | Applied as §3 tag | Tag held / capability-only |
|---|---|---|---|
| SITE-000198 Ohio Elastomers | B | mold_tool_making, transfer_molding | — |
| SITE-000239 Allpass Corporation | C | polyethylene_pe, polypropylene_pp | — |
| SITE-000243 American Molded Plastic, Inc. | C | thermoplastics | injection_molding |
| SITE-000287 Chardon Rubber Company | B | rubber_mixing_compounding, elastomers_rubber | — |
| SITE-000402 Industrial Technologies, Inc. | C | silicones, polyurethane_pu | — |
| SITE-000438 Keyland Polymer UV Powder, LLC | C | epoxy | — |
| SITE-000458 Malish Corp., Plastic Div. | B | thermoplastics, polypropylene_pp, polyethylene_pe, abs, asa, pvc, polystyrene_ps_hips, thermoplastic_elastomers_tpe_tpu, polycarbonate_pc | extrusion_profile, extrusion_pipe_tube |
| SITE-000490 Neff-Perkins Company | C | compression_molding, transfer_molding, injection_molding, elastomers_rubber, silicones, thermoplastics, thermosets | — |
| SITE-000546 PolyStamp, LLC. | A | recycling_unspecified | — |
| SITE-000562 Profile Rubber Corp., Inc. | C | elastomers_rubber | compression_molding, transfer_molding |
| SITE-000591 Royal Plastics, Inc. | B | injection_molding | — |
| SITE-000618 Sparton Enterprises, Inc. | C | elastomers_rubber, epdm, sbr | recycling_unspecified |
| SITE-000651 Treemen Industries | C | injection_molding, thermoplastics, polycarbonate_pc, abs, acrylic_pmma, asa, nylon_pa, polypropylene_pp | — |
| SITE-000667 Vinylume Products, Inc. | B | — | (cap only) extrusion_unspecified |
| SITE-000707 Alliance Innovations | C | — | compression_molding, thermoforming_unspecified |
| SITE-000909 Flex Technologies, Inc. | C | custom_compounding, thermoplastics, pvc, extrusion_pipe_tube, extrusion_profile, injection_molding, plastics_fabrication_welding | — |
| SITE-000987 Kar-Del Plastics, Inc. | C | fabrication_unspecified, polypropylene_pp, composites_frp, pvc, thermoplastics | — |
| SITE-001109 Plastics Family Holdings Inc (Para | C | — | plastics_machining_cnc |
| SITE-001125 Polynew | A | — | regrind_pelletizing |

## Held (every site; reason and settling fact in `verdicts.csv`, STILL_UNCERTAIN, never REJECT)
By hold class (unit: sites): nothing found 32; equipment or supply firm 16; distributor or dealer 15; multi-location, not bound to the site 6; locality not witnessed on stored pages 5; plant allocation 4; off-vocabulary 3; testing lab 3; menu-only with no §3.6 term 2; one each for plant elsewhere, site_type hq_only, partner processing, not in-house, not a processor, and the SITE-000591 term hold. A hold says the stored pages did not prove the term for that establishment; it does not say the capability is absent.
Holds an owner or a later fetch can settle:
| Site | Hold | Settling fact |
|---|---|---|
| SITE-000229 Aetna Plastics | The page labels Mantua (4466 Orchard St) "Fabrication & Production" and Cleveland sales/distribution | A page placing fabrication at the Cleveland address |
| SITE-000423 Jerico Plastic | "plants in Ohio and Georgia"; Wadsworth is the corporate office | A page placing compounding or toll pulverizing at Wadsworth |
| SITE-000453 LMT Mercer | New Jersey and Hartville both manufacture | Which plant runs the 33 injection molding machines |
| SITE-000563 Progressive Foam | Beach City and Gnadenhutten plants (Gnadenhutten has no Atlas site) | Which plant makes foam insulation |
| SITE-000670 Walton Plastics | "Located in Northeast Ohio" only; site is a Walton Hills warehouse_distribution row | A page with the Hannan Pkwy address and production there |
| SITE-000014 Diamond America | "forming dies, sheet dies, film dies and other custom tooling" fits no governed term | Owner vocabulary ruling: map die/tooling manufacture to mold_tool_making? Recommendation: no, add it by dated revision if wanted |
| SITE-000487 MUM / Integra Enclosures | Page says Integra "offers" CNC machining and gives 8989 Tyler Blvd only as the company address; site_type hq_only | A page placing machining at that address, or a site_type correction |

## Method and how far it got
1. Read #351's frame and verdicts; took the unadjudicated sites in site_id order (first 110).
2. For each site, ran a term finder over its stored non-news pages (term list reused from b02 `capextract.py`, plus broader words), read the hit context for every site, and opened the surrounding sentences and locality for all candidates (about 45 sites in detail). Sites whose pages are distributor catalogues, equipment makers, testing labs or empty shells were judged from the hit list and the page descriptions, not read page by page. **Not every stored page of the 110 sites was read in full.**
3. Rules reused from b01/b02 and the 2026-11-14 owner ruling: tags only from the PROCESSES and MATERIALS vocabularies and never broader than the page's words; narrative sentence = supports_A; capability or product list = supports_C; a C-strength term on a tier A/B site is a capability row only; on a tier C site it may tag the site with its evidence row. Every decision carries a quote (≤25 words, words in order in the stored raw page, raw SHA-256) and a locality witness (the site's own address or city on a stored page) before it counts; the check re-verifies both.
4. Section 3.6 mapping as in b02: custom/unspecified compounding → `compounding`; `extrusion_*` → `extrusion`; `thermoforming_*` → `thermoforming`; exact matches otherwise; terms with no §3.6 entry get a §3 tag only.
5. Fill-blank only, as b02: a §3 cell is written only if blank at base; otherwise the tag is held and the capability row (if §3.6 has a term) is still minted. See the Result section for the 10 held terms and the recommendation.
6. Locality and plant: a quote counts only with a witness that names this establishment's address or city on a stored page. Royal Plastics uses the about page line "RPI – Mentor, OH USA Custom Injection Molder and Contract Manufacturer", because the company also runs RPI-China. Malish is applied, unlike Venture Plastics (held), because Venture's own page says "in Ohio & Texas"; Malish's page names only its Mentor address for the plastics division and its history page says the 160,000 sq ft Mentor facility is where the company moved. Residual risk: Malish's directory also lists Mexico, Poland, China and an NY brush company, and the page does not say those do not extrude.

## Checks run
- `python3 tasks/pic18-capabilities-corpus-2a-2026-11-16/check.py`: recomputes counts, replays every added cell and row against the pinned base, checks the column boundary and ID blocks, the V-25 rule, and idempotence; it fails on 5 injected defects (false quote, off-vocabulary term, false locality witness, tier A/B menu term promoted to a tag, a dropped decision).
- `python3 scripts/validate.py`: 0 errors. `check_row_loss.py --base origin/main` and `export_vocab.py --check`: see PR body.

## Not checked
- Pages not in the stored corpus; failed or robots-blocked fetches count as availability, not absence.
- Form 5500 and permit routes (no REJECT was issued, so the Form 5500 gate did not apply).
- Org-level columns, tiers and notes are untouched (contract rule 13). The required two-family refute review is the controller's; this lane did not call other threads.
- Overlap with #351 is none by site (its 4 adjudicated sites are outside the slice). Other open lanes append to the same three data files; the second PR to merge needs a replay of `build.py` against the new main, not a hand merge.

## Proposed follow-ups (not in this PR)
- Second half of the unadjudicated list (110 sites, SITE-001479 onward).
- site_type `hq_only` on SITE-000198 Ohio Elastomers, SITE-000438 Keyland and SITE-000458 Malish Plastic Div., which each describe making product at their one address: site_type review (the MUM hold above is the same question).
- SITE-000562 Profile Rubber: existing `processes=recycling_recovery` and site_type `recycling_facility` look inconsistent with a molded-rubber maker; street address blank.
- Gnadenhutten, Ohio (Progressive Foam, 220,000 sq ft) and Minerva, Ohio (Jerico logistics site) have no Atlas site: discovery leads.
