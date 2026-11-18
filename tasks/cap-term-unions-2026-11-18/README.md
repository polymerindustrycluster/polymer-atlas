# Capability term unions on sites — 2026-11-18

Lane `atlas-w18-backlog` (Claude Sonnet 5.5). One draft PR, no merge. Writes: `data/sites_OH.csv` (`processes`, `materials` cells only) and `data/evidence_sites_OH.csv` (EVD-396500..396506 of the block EVD-396500..396549).
First user: PIC cluster reporting analyst (counts by process and material). Review date: 2026-12-16 (non-use is a finding if those counts are not read).

## Authority
- Owner ruling 2026-11-18 item 8 (`tasks/owner-rulings-2026-11-18/README.md`): a verified term may be appended to a non-blank processes or materials cell, as a union with nothing removed. Ruling 1 of the same item (polymer-concrete casting is not `potting_encapsulation_casting`) is respected: that term is not written.
- Controller decision 2026-11-17 for the CAP2A terms (PR #365; fill-vs-append, "append"), corrected on 2026-11-18 after review: four holds and one remap, below.

## Result (unit: Ohio sites (establishments), active; one term = one site × field × term)
| Unit | Count |
|---|---|
| Terms proposed (10 CAP2A held terms on 7 sites + 1 CAP2B term on 1 site) | 11 |
| Terms applied (processes 6, materials 1) | 7 |
| Terms held (SITE-001109 ×1, SITE-000707 ×2, SITE-000562 ×1) | 4 |
| Site rows changed (tier A 1, B 2, C 3; processes/materials cells only, 0 values removed) | 6 |
| Evidence rows added (supports_A 6, supports_C 1) | 7 (EVD-396500..396506; IDs closed up after each hold, none of the earlier numbering was merged) |

| Site | Tier | Field | Term appended | Existing value kept | Evidence | Applied/held |
|---|---|---|---|---|---|---|
| SITE-000243 | C | processes | injection_molding | tooling_mold_die | EVD-396500, A | applied |
| SITE-000458 | B | processes | extrusion_profile, extrusion_pipe_tube | machinery_equipment | EVD-396501, -396502, A | applied |
| SITE-000562 | C | processes | rubber_molding_compression (remapped, see below) | recycling_recovery | EVD-396503, C (menu line, tier C ok) | applied; `transfer_molding` **held** |
| SITE-000618 | C | processes | recycling_unspecified | recycling_recovery | EVD-396504, A | applied |
| SITE-000707 | C | processes | compression_molding, thermoforming_unspecified | tooling_mold_die | none | **held** |
| SITE-001109 | C | processes | plastics_machining_cnc | distribution | none | **held** |
| SITE-001125 | A | processes | regrind_pelletizing | recycling_recovery | EVD-396505, A | applied |
| SITE-001986 | B | materials | composites_unspecified | epoxy | EVD-396506, A | applied |

## Corrections after review (controller decisions 2026-11-18)
- **SITE-000562 remap.** The services-menu item "Compression Molding" is mapped to `rubber_molding_compression`, not the plastics term `compression_molding` (SCHEMA §3.1 puts them in separate groups; §3.6 draws the plastics/rubber boundary). It stays supports_C on tier C.
- **SITE-000562 `transfer_molding` held** (controller decision 2026-11-18, Codex round 2). §3.1 lists it under "Primary shaping — plastics" and has no rubber counterpart; whether a plastics-section term may describe a rubber process is an owner question, now on the battery list. Its evidence row is not minted.
- **SITE-000707 held.** A tool shop (NAICS 333511, existing `tooling_mold_die`); its pages describe making molds for compression molding and thermoforming, not running those processes.
- **SITE-001109 held.** See Holds.

## Rechecks before appending
- **Evidence on main:** none of the 7 applied terms had an evidence row (CAP2A held the tag, so it minted none; CAP2B held SITE-001986's term), so each gets one here. `build.py` refuses to add a row if one exists for the (site, term).
- **Quote and locality:** `build.py` and `check.py` re-run CAP2A's `validate_decision` per term: raw-page SHA-256 matches, quote words appear in order in the raw page (≤25 words), quote is in the stored text, and the locality witness is on a stored page of the same organization.
- **Tier ceiling (V-25):** six terms are narrative sentences (supports_A). One (SITE-000562, tier C) is a "Services" menu line, supports_C on a tier C site; `check.py` fails a C-strength row on a tier A/B site.
- **SITE-001986 (CAP2B hold):** quote "Our CASTINITE ™ epoxy/quartz composites are precision-cast for unparalleled precision." on the organization's home page; witness "4304 Maple Street Perry Village, OH 44081" on the same page. The four stored pages show one address and no other location.

## Holds
| Site | Term | Why held | Settling fact |
|---|---|---|---|
| SITE-001109 | plastics_machining_cnc | CAP2A's quote ("fine-machined surface finishes on plastic machined parts") says plastic machining but never CNC; the stored `/industries/` page says "Utilizing the latest technologies in CNC machining…" about 30 words after "plastic components". Joining two sentences is an inference (controller decision 2026-11-18). | One own-page sentence stating that the company CNC-machines plastic |
| SITE-000707 | compression_molding, thermoforming_unspecified | Tool shop; the cited sentence ("excels in compression molding, thermoforming, tooling…") sits among pages that describe building compression and thermoforming molds ("Compression Molding & Thermoforming Tooling", "Tooling Supplier of the Year"). The pages do not say the company runs the processes (Gemini review h16; controller decision 2026-11-18). | An own-page sentence stating that the company produces parts by compression molding or thermoforming |
| SITE-000562 | transfer_molding | A plastics-section §3.1 term on a rubber molder's services menu; §3.1 has no rubber counterpart, so applying it to rubber is a vocabulary scope question (AGENTS.md §2 rule 9). | An owner ruling on `transfer_molding`'s scope for rubber, or a rubber-specific term |

## Self-refute (contract rule 15)
- self-refute: grain — 11 rows checked, 0 changed (7 applied, 4 held). Each witness names the site's own address or city. Residual risk carried from CAP2A: SITE-000458 Malish (the directory also lists Mexico, Poland, NY and China entries, and no stored page says those do not extrude); SITE-000562's witness is a "Shipping Address" line (a street address, not a mailing address) with the site's street still blank.
- self-refute: founding — 11 rows checked, 0 changed. No "since" or "years in business" phrase is used as a founding claim; SITE-000243's "Since 1990 … has been custom injection molding" is a process statement.
- self-refute: strength — 11 rows checked, 1 changed (SITE-001109 held: the quote does not carry "CNC"). The two menu terms are supports_C on a tier C site only.
- self-refute: truncated quote — 11 rows checked, 1 changed (SITE-001109 held: the words that carry the claim are in two sentences). Every other applied quote contains the words that carry its term (`injection molding`, `profiles, tube and pipe`, `rubber recycling operation`, `regrind processed by Polynew`, `epoxy/quartz composites are precision-cast`; the menu line "Compression Molding").
- self-refute: attribution — 11 rows checked, 3 changed (SITE-000707 held: a tooling page is not a molding claim; SITE-000562 compression term remapped, its transfer term held: a rubber menu is not a plastics claim). All quotes are on the organization's own site; none is a parent, sister or customer page. SITE-000562 and SITE-000458 `site_type` look inconsistent with the cited processes (CAP2A follow-up, not touched here).

## Checks run
- `python3 tasks/cap-term-unions-2026-11-18/check.py`: recomputes against the pinned base (`base.txt`, 832ea1b). Changed sites equal the listed sites; changed columns are processes/materials only; the sites row count equals the base; evidence rows equal the base plus one per term; every changed cell keeps its old values in order and gains exactly the decision terms; every term is in the §3.1/§3.2 vocabulary (`docs/schema/vocab.json`); no held term is written; one evidence row per term, ID in the block, strength and tier ceiling right, and the published tier split (A 1, B 2, C 3) and strength split (supports_A 6, supports_C 1); the decisions equal an independent count (CAP2A `verdicts.csv` "tag held" rows, 10 on 7 sites, minus the four holds, with the SITE-000562 remap, plus the CAP2B term); `build.py` is idempotent.
- **Source binding.** Each decision's cited URL, raw-file digest and text file must equal the corpus manifest entry (`manifest.csv`) of the raw file whose bytes and quote were checked, its locality-witness URL must equal the manifest entry of the witness page, both pages must belong to the site's organization, and the evidence row must cite the same URL, digest and witness page.
- Injected defects, each caught (11): an existing value removed, a term outside §3.1/§3.2, a term without evidence, a write to a non-listed site, a false quote, C-strength evidence on a tier A site, a held term written (the plastics term on the rubber molder), an extra evidence row, a dropped sites row, a source swap (SITE-001986 citing another stored page while its quote and digest belong to the home page), and a cited page that does not contain the quote.
- **Atomic writes.** `build.py` writes each data file to a temp file in the same directory, flushes and fsyncs, then `os.replace`s it, and asserts the row counts first (sites unchanged from the base; evidence = base + one per term); a target that is not the base or the base plus this PR is refused. `check.py` replays Codex's cut-short-write reproduction from the #382 review on temp copies: a write that dies after 100 rows leaves both targets intact with no temp file, the retry reproduces the committed bytes, and a target truncated to 100 rows is refused instead of reported as success.
- `python3 scripts/validate.py`, `scripts/check_row_loss.py --base origin/main`, `scripts/export_vocab.py --check`: see PR body.

## Not checked
- Pages outside the stored corpus. Whether other open lanes touch these cells (rerun `build.py` on the new main after updating `base.txt`; do not hand-merge). `scripts/` untouched, so the unit-test run was skipped. The two-family refute review is the controller's.

## Proposed follow-ups (not in this PR)
- Owner battery item: is `transfer_molding` plastics-only or process-generic for rubber (no rubber counterpart exists in §3.1)? Settles the SITE-000562 hold.
- Capability rows (`site_capabilities.csv`) for terms with a §3.6 equivalent that have none yet.
