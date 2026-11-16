# PIC-18 capabilities from the corpus, slice 2A — 2026-11-16

Lane CAP2A (`atlas-w16-cap2a`, Claude Sonnet 5.5), designated integrator for this slice only. One draft PR, no merge. Output: `data/sites_OH.csv` (processes, materials only), `data/site_capabilities.csv` (CAP-001200+), `data/evidence_sites_OH.csv` (EVD-387000+).
First user: PIC cluster reporting analyst (counts by process). Review date: 2026-12-16 (non-use is a finding if process counts are not being read).

## Slice
PR #351 (`tasks/pic18-capabilities-corpus-2026-11-16`, still open) built a frame of 224 active tier A–C PIC-18 Ohio sites with one active Atlas site per organization and a blank process or material cell, and adjudicated 4 of them. The other 220 are listed in `pr351_unadjudicated_sites.txt` (from its `verdicts.csv` at head 19c0120). **This slice is the first 110 of those 220 by site_id** (`slice.csv`; SITE-000014 to SITE-001468). Unit: Ohio sites (establishments), active, PIC-18 counties, tier A 17 / B 22 / C 71. `check.py` recomputes the #351 frame criteria at the pinned base (`base.txt`, origin/main 4abc9eb) and asserts every slice site is still in it. The second half (110 sites, SITE-001479 onward) is not in this PR.

## Result (units named)
| Unit | Count |
|---|---|
| Sites in slice | 110 |
| Sites with at least one applied term | 19 (tier A 2, B 5, C 12) |
| Sites whose §3 cell gained a tag | 18 (A 2, B 4, C 12) |
| Site rows changed (processes/materials cells only; appended, nothing removed) | 18 |
| Term decisions (site × field × term) | 64 (processes 26, materials 38); narrative 57, menu/list 7 |
| Evidence rows, `evidence_sites_OH.csv` | 63 (supports_A 57; supports_C 6, all on tier C sites) |
| Capability rows, `site_capabilities.csv` | 46 (materials 32, processes 14) on 16 sites, all `company_disclosed` |
| Capability-only (owner ruling 2026-11-14) | 1 site: SITE-000667 Vinylume (tier B, "vinyl extrusion projects" is a C-strength line) |
| Sites held with no applied term | 91 (one more, SITE-000591, has one applied term and held menu terms) |

Yield: 19 of 110 slice sites (17%) gained data. PR #351 gained 3 of 224 sites. IDs used: EVD-387000..387062 and CAP-001200..001245 of the reserved blocks.

## Applied (every row also in `verdicts.csv`, disposition `applied` or `capability row only`)
| Site | Tier | Terms applied |
|---|---|---|
| SITE-000198 Ohio Elastomers | B | mold_tool_making, transfer_molding |
| SITE-000239 Allpass | C | polyethylene_pe, polypropylene_pp (product list, supports_C) |
| SITE-000243 American Molded Plastic | C | injection_molding, thermoplastics |
| SITE-000287 Chardon Rubber | B | rubber_mixing_compounding, elastomers_rubber |
| SITE-000402 Industrial Technologies | C | silicones, polyurethane_pu |
| SITE-000438 Keyland Polymer UV Powder | C | epoxy |
| SITE-000458 Malish Plastic Div. | B | extrusion_profile, extrusion_pipe_tube; thermoplastics, PP, PE, ABS, ASA, PVC, PS, TPE, PC |
| SITE-000490 Neff-Perkins | C | compression/transfer/injection molding; rubber, silicones, thermoplastics, thermosets |
| SITE-000546 PolyStamp | A | recycling_unspecified |
| SITE-000562 Profile Rubber | C | compression_molding, transfer_molding (menu, supports_C); elastomers_rubber |
| SITE-000591 Royal Plastics | B | injection_molding |
| SITE-000618 Sparton Enterprises | C | recycling_unspecified; elastomers_rubber, epdm, sbr |
| SITE-000651 Treemen Industries | C | injection_molding; thermoplastics, PC, ABS, acrylic_pmma, ASA, nylon_pa, PP |
| SITE-000667 Vinylume | B | capability row `extrusion` only |
| SITE-000707 Alliance Innovations | C | compression_molding, thermoforming_unspecified |
| SITE-000909 Flex Technologies | C | custom_compounding, extrusion_pipe_tube, extrusion_profile, injection_molding, plastics_fabrication_welding; thermoplastics, pvc |
| SITE-000987 Kar-Del Plastics | C | fabrication_unspecified, polypropylene_pp (list, supports_C); composites_frp, pvc, thermoplastics |
| SITE-001109 Paramont Machine | C | plastics_machining_cnc |
| SITE-001125 Polynew | A | regrind_pelletizing, thermoplastics |

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
| SITE-000487 MUM / Integra Enclosures | Atlas site_type hq_only; page says Integra "offers" CNC machining | A page placing machining at 8989 Tyler Blvd, or a site_type correction |

## Method and how far it got
1. Read #351's frame and verdicts; took the unadjudicated sites in site_id order (first 110).
2. For each site, ran a term finder over its stored non-news pages (term list reused from b02 `capextract.py`, plus broader words), read the hit context for every site, and opened the surrounding sentences and locality for all candidates (about 45 sites in detail). Sites whose pages are distributor catalogues, equipment makers, testing labs or empty shells were judged from the hit list and the page descriptions, not read page by page. **Not every stored page of the 110 sites was read in full.**
3. Rules reused from b01/b02 and the 2026-11-14 owner ruling: tags only from the PROCESSES and MATERIALS vocabularies and never broader than the page's words; narrative sentence = supports_A; capability or product list = supports_C; a C-strength term on a tier A/B site is a capability row only; on a tier C site it may tag the site with its evidence row. Every decision carries a quote (≤25 words, words in order in the stored raw page, raw SHA-256) and a locality witness (the site's own address or city on a stored page) before it counts; the check re-verifies both.
4. Section 3.6 mapping as in b02: custom/unspecified compounding → `compounding`; `extrusion_*` → `extrusion`; `thermoforming_*` → `thermoforming`; exact matches otherwise; terms with no §3.6 entry get a §3 tag only.
5. Appending vs fill-blank: terms are appended to cells that already hold other values (for example `processes=distribution`, `machinery_equipment`, `tooling_mold_die`, which are subtype-style values, not §3.1 terms). b02 wrote blank cells only; #351 appended. Tell me if you want blank-only.

## Checks run
- `python3 tasks/pic18-capabilities-corpus-2a-2026-11-16/check.py`: recomputes counts, replays every added cell and row against the pinned base, checks the column boundary and ID blocks, the V-25 rule, and idempotence; it fails on 5 injected defects (false quote, off-vocabulary term, false locality witness, tier A/B menu term promoted to a tag, a dropped decision).
- `python3 scripts/validate.py`: 0 errors. `check_row_loss.py --base origin/main` and `export_vocab.py --check`: see PR body.

## Not checked
- Pages not in the stored corpus; failed or robots-blocked fetches count as availability, not absence.
- Form 5500 and permit routes (no REJECT was issued, so the Form 5500 gate did not apply).
- Org-level columns, tiers and notes are untouched (contract rule 13). The required two-family refute review is the controller's; this lane did not call other threads.
- Overlap with #351 is none by site (its 4 adjudicated sites are outside the slice); both PRs append to the same three data files, so the second to merge needs a normal-merge replay of `build.py`.

## Proposed follow-ups (not in this PR)
- Second half of the unadjudicated list (110 sites, SITE-001479 onward).
- site_type `hq_only` on SITE-000198 Ohio Elastomers and SITE-000458 Malish Plastic Div., which each describe manufacturing at their one address: site_type review.
- SITE-000562 Profile Rubber: existing `processes=recycling_recovery` and site_type `recycling_facility` look inconsistent with a molded-rubber maker; street address blank.
- Gnadenhutten, Ohio (Progressive Foam, 220,000 sq ft) and Minerva, Ohio (Jerico logistics site) have no Atlas site: discovery leads.
