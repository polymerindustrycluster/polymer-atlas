# Capability term unions on sites — 2026-11-18

Lane `atlas-w18-backlog` (Claude Sonnet 5.5). One draft PR, no merge. Writes: `data/sites_OH.csv` (`processes`, `materials` cells only) and `data/evidence_sites_OH.csv` (EVD-396500..396510 of the block EVD-396500..396549).
First user: PIC cluster reporting analyst (counts by process and material). Review date: 2026-12-16 (non-use is a finding if those counts are not read).

## Authority
- Owner ruling 2026-11-18 item 8 (`tasks/owner-rulings-2026-11-18/README.md`): a verified term may be appended to a non-blank processes or materials cell, as a union with nothing removed. Ruling 1 of the same item (polymer-concrete casting is not `potting_encapsulation_casting`) is respected: that term is not written.
- Controller decision 2026-11-17 for the 10 CAP2A terms (PR #365; fill-vs-append, "append").

## Result (unit: Ohio sites (establishments), active; one term = one site × field × term)
| Unit | Count |
|---|---|
| Terms proposed (10 CAP2A held terms on 7 sites + 1 CAP2B term on 1 site) | 11 |
| Terms applied (processes 10, materials 1) | 11 |
| Terms held | 0 |
| Site rows changed (tier B 2, tier C 5, tier A 1; processes/materials cells only, 0 values removed) | 8 |
| Evidence rows added (supports_A 9, supports_C 2) | 11 (EVD-396500..396510) |

| Site | Tier | Field | Term appended | Existing value kept | Evidence | Applied/held |
|---|---|---|---|---|---|---|
| SITE-000243 | C | processes | injection_molding | tooling_mold_die | EVD-396500, A | applied |
| SITE-000458 | B | processes | extrusion_profile, extrusion_pipe_tube | machinery_equipment | EVD-396501, -396502, A | applied |
| SITE-000562 | C | processes | compression_molding, transfer_molding | recycling_recovery | EVD-396503, -396504, C (menu line, tier C ok) | applied |
| SITE-000618 | C | processes | recycling_unspecified | recycling_recovery | EVD-396505, A | applied |
| SITE-000707 | C | processes | compression_molding, thermoforming_unspecified | tooling_mold_die | EVD-396506, -396507, A | applied |
| SITE-001109 | C | processes | plastics_machining_cnc | distribution | EVD-396508, A | applied |
| SITE-001125 | A | processes | regrind_pelletizing | recycling_recovery | EVD-396509, A | applied |
| SITE-001986 | B | materials | composites_unspecified | epoxy | EVD-396510, A | applied |

## Rechecks before appending
- **Evidence on main:** none of the 11 terms had an evidence row (CAP2A held the tag, so it minted none; CAP2B held SITE-001986's term), so each gets one here. `build.py` refuses to add a row if one exists for the (site, term).
- **Quote and locality:** `build.py` and `check.py` re-run CAP2A's `validate_decision` per term: raw-page SHA-256 matches, quote words appear in order in the raw page (≤25 words), quote is in the stored text, and the locality witness is on a stored page of the same organization.
- **Tier ceiling (V-25):** nine terms are narrative sentences (supports_A). Two (SITE-000562, tier C) are a "Services" menu line, supports_C on a tier C site; `check.py` fails a C-strength row on a tier A/B site.
- **SITE-001986 (CAP2B hold):** quote "Our CASTINITE ™ epoxy/quartz composites are precision-cast for unparalleled precision." on the organization's home page; witness "4304 Maple Street Perry Village, OH 44081" on the same page. The four stored pages show one address and no other location.
- **SITE-001109 (changed quote):** CAP2A's quote ("fine-machined surface finishes on plastic machined parts") never says CNC and the same company's home page speaks of "automatic screw machines". A stored page of the same organization (`/industries/`) says "Utilizing the latest technologies in CNC machining we are able to meet some of the most stringent tolerances in the industry" and carries the address; this PR cites that sentence instead (the other sentence is not used).

## Self-refute (contract rule 15)
- self-refute: grain — 11 rows checked, 0 changed. Each witness names the site's own address or city. Residual risk carried from CAP2A: SITE-000458 Malish (the directory also lists Mexico, Poland, NY and China entries, and no stored page says those do not extrude); SITE-000562 witness is a "Shipping Address" line (a street address, not a mailing address) with the site's street still blank.
- self-refute: founding — 11 rows checked, 0 changed. No "since" or "years in business" phrase is used as a founding claim; SITE-000243's "Since 1990 … has been custom injection molding" is a process statement.
- self-refute: strength — 11 rows checked, 1 changed (SITE-001109 quote, above). The two menu terms are supports_C on a tier C site only.
- self-refute: truncated quote — 11 rows checked, 1 changed (SITE-001109). Every other quote contains the words that carry its term (`compression molding`, `thermoforming`, `profiles, tube and pipe`, `rubber recycling operation`, `regrind processed by Polynew`, `injection molding`, `epoxy/quartz composites are precision-cast`).
- self-refute: attribution — 11 rows checked, 0 changed. All quotes are on the organization's own site; none is a parent, sister or customer page. SITE-000562 and SITE-000458 `site_type` look inconsistent with the cited processes (CAP2A follow-up, not touched here).

## Checks run
- `python3 tasks/cap-term-unions-2026-11-18/check.py`: recomputes against the pinned base (`base.txt`, 832ea1b); changed sites equal the listed sites; changed columns are processes/materials only; every changed cell keeps its old values in order and gains exactly the decision terms; every term is in the §3.1/§3.2 vocabulary (`docs/schema/vocab.json`); one evidence row per term, ID in the block, strength and tier ceiling right, no other evidence row changed; the decisions equal an independent count (CAP2A `verdicts.csv` "tag held" rows, 10 on 7 sites, plus the CAP2B hold); `build.py` is idempotent. It fails on 6 injected defects: an existing value removed, a term outside §3.1/§3.2, a term without evidence, a write to a non-listed site, a false quote, C-strength evidence on a tier A site.
- `python3 scripts/validate.py`, `scripts/check_row_loss.py --base origin/main`, `scripts/export_vocab.py --check`: see PR body.

## Not checked
- Pages outside the stored corpus. Whether other open lanes touch these cells (rerun `build.py` on the new main; do not hand-merge). `scripts/` untouched, so the unit-test run was skipped. The two-family refute review is the controller's.

## Proposed follow-ups (not in this PR)
- Capability rows (`site_capabilities.csv`) for terms with a §3.6 equivalent that have none yet (e.g. SITE-001986 `composites_unspecified` if §3.6 has one).
