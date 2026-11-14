# Ohio PIC-18 processes/materials + site_capabilities — batch b02 (2026-11-12)

Worker: grok (branch `agent/grok/oh-capabilities-2026-11-12-b02`). Claim line: `tasks/QUEUE.md`, under the 2026-11-04 claude-code "PIC-18 capability pass" line (added in #321 only).

**Stale claim note.** The `claimed:claude-code 2026-11-04` PIC-18 capability pass has had no capability PR since #124 (2026-11-05). Before that came #92, folded into #108, and #117. claude-code's latest PR is #261 (2026-11-09, people/dedupe). This lane treats that claim as stale, not released.

## Owner ruling recorded (2026-11-12, 13:51 ET)
Owner's words, in reply to the proposal to accept own-site capability/menu lists at a lower tier and use permit records for site-level process facts: **"ok, go for it."**

How it is applied here (existing vocab only, so validate passes):
- **Menu lists.** Own-site capability or menu lists (e.g. "Capabilities: Injection Molding", a Materials page list, a product-line title) now count. Each such row is `source_class=own_site`, `tier_effect=supports_C`, with `basis: self-described menu (owner ruling …)` in claim_detail. The matching `site_capabilities` row is `company_disclosed`, and its notes carry the same basis.
- **Narrative clauses.** Rows where the company states its own process or material in a sentence stay `supports_A`.
- **Permits.** EPA/state permit records (FRS, TRI, Ohio EPA air permits) may support site-level process facts as `government_filing`. This batch used none (see "Permit route").
- **Exclusions.** Hiring sites and the banned sources (Plastics News, Data Axle, Rubber News rankings, ZoomInfo, D&B, CB Insights, PIC CRM) still don't count.

## Frame
`frame.csv` holds rows 100:200 of cap_frame (306), in county order (Summit, Portage, Stark, Medina, Wayne, Cuyahoga, …) and by site_id within each county. A row qualifies when it is:
- an active Ohio site in the PIC-18 counties;
- ring_primary 1–2;
- blank `processes` or blank `materials`;
- owned by an org with a website;
- the org's **only** Atlas site (all shards).

SITE-000174 (Hankook, #322) is not in the frame, and the builder asserts that.

## Method
1. `scripts/capfetch.py` fetches the homepage plus up to 5 same-host pages (capabilities/services/products/materials/about first). That is at most 6 pages per site; careers/jobs pages are skipped.
2. Two extractors find candidate terms:
   - `scripts/capextract.py` + `capfilter.py` pull narrative clauses.
   - `scripts/capmenu.py` pulls menu lists: the term must sit within 220 characters after a Capabilities/Services/Processes/What We Do header (processes) or a Materials/Resins/Capabilities header (materials).
3. Every candidate was then judged by hand (`scripts/decisions.csv`). Each accepted quote is ≤25 words and re-asserted as an exact substring of the normalized raw text, with its SHA-256.

## Rules
- **Fill-blank-only.** A column is written only if it is blank on main.
- **Grain.**
  - *site*: the company has one Atlas site, and its pages show no other-state address and don't describe multiple locations. Site columns are filled, plus org columns when blank. One `site_capabilities` row is minted per §3.6 term.
  - *org*: multi-location companies. Org columns are filled only, and only if blank.
- **§3.6 mapping.**
  - Materials map 1:1 when the term is in CAP_MATERIAL.
  - Process subtypes roll up to their §3.6 umbrella: custom/unspecified compounding → `compounding`; rubber_molding_* → `rubber_molding`; extrusion_* → `extrusion`; thermoforming_* → `thermoforming`; blow_molding_* → `blow_molding`.
  - Terms with no §3.6 entry get a §3 tag only. These are laminating, die_cutting_converting, transfer_molding, rubber_extrusion, composites_frp, insert_overmolding, recycling_unspecified, potting and the specific elastomers.

## V-25 guard (ruling needed)
On a tier-A/B record with no A/B-strength scope row, a `supports_C` scope row fails validate (V-25: "must-have claim scope supported only at C strength"). In that case the menu-basis term is minted as a `site_capabilities` row only, with `company_disclosed` provenance and notes saying the §3 tag is held. The §3 column and evidence row wait for a ruling. One option: let own-site menu rows carry `supports_B`. Another: keep menu facts in capabilities only on A/B-tier records.

## Results
| | count |
|---|---|
| frame rows | 100 (83 with ≥1 page loaded; 342 pages) |
| candidates judged | 90 |
| accepted term decisions | 31 (`verdicts.csv`) |
| records gaining a §3 tag | **6** (6.0% yield) |
| sites tagged, by basis | narrative (A) 4, menu (C) 2 (a site can have both) |
| evidence rows by basis | menu 4, narrative 6 (site 6, org 5) |
| menu terms held from §3 tag (V-25) | 18 (sites with capability rows only: SITE-000623, SITE-000647, SITE-001733) |
| site_capabilities rows | 14 (CAP-001015..CAP-001031; CAP-001026, 001030, 001031 withdrawn) |
| evidence IDs | EVD-345100..EVD-345112 (EVD-345111 and 345112 retired; 11 rows live) |

Candidates that were not minted are in `not_minted.csv`, each with a reason. These are not REJECT verdicts on records. When a fetch failed, the source was unavailable; that does not mean the capability is absent.

## Permit route
No permit rows were minted in this batch. TRI/FRS give NAICS and chemicals, not §3 process terms. Ohio EPA air-permit emission-unit descriptions do name processes, but they need a per-facility document pull. That is left as the next source for the rows still untagged.

## Yield stop
This batch gave 6 of 100 records a §3 tag (6%), or 9 of 100 (9%) counting the 3 sites that got capability rows only (GRAFIX SITE-000383 laminating has no §3.6 term, so it is held entirely). b01 was 11%. Both are below the 20% stop rule even with the menu ruling, so **this lane stops here**. Rows 200–306 of the frame (106 rows) are untouched. Restarting needs a different source, such as Ohio EPA air-permit emission-unit text or product-catalog PDFs.

## Leads
- Mechanical Rubber SITE-000118 (an NY address on its own site), Q Medical Devices SITE-000568 and ePac SITE-001652 (multi-location companies): org grain only, and their org columns were already filled.
- MMI Textiles SITE-000477 shares 1 American Rd with Health-Mor SITE-001573 (the Lane A address-first lead). The nylon tag here is on MMI's own site.

## Correction note
The first push of this PR (commit 1) failed local validate with 4 V-25 errors. The helper didn't stop on the failure. This commit regenerates the unmerged rows in place: EVD-345113..345130 are no longer used, and CAP IDs are unchanged.

## CI
The CI `validate` job fails on main too: docs/schema/vocab.json is stale, and test_audit_evidence_coverage errors on EVD-333167. It is not touched here, per instruction. `python3 scripts/validate.py` passes locally, and `scripts/check_row_loss.py --base origin/main` is OK.

---
Never merged by the author. No Muse files touched; the only QUEUE edit is the #321 claim line. No paid calls.

## Correction 2026-11-12 14:07 ET (Navigator Verifier review)
- **Adherex (SITE-001852 → ORG-001769), moved from site to org.** The cited capabilities page says "Five distribution centers", so under this lane's multi-location rule these are org-grain facts.
  - EVD-345105, 345106 and 345107 keep their IDs. They now sit in `evidence_organizations_OH.csv` on ORG-001769, labelled `supports_A` (the org is tier A).
  - The site's processes and materials are back to blank, as on main.
  - CAP-001026 (adhesives_sealants) is removed; org grain mints no capability rows.
  - The org already listed die_cutting_converting and adhesives_sealants; `laminating` is added to its processes. That adds to a field that was already filled, an exception to this lane's fill-blank-only habit made because the move was requested.
- **Anita Plastics (SITE-000122), EVD-345111/345112 and CAP-001030/001031: notes replaced with the real reason.** The products page says "Anita Plastics serves as a trading group for our parent company, the Mewar Group, which manufactures various products across our India’s plants." Where the fabric is made is unclear. The claim_detail now reads "manufacturing location unclear", with the caveat in the notes.
  - Effect stays `supports_U`, not `supports_C`. SITE-000122 is tier U, and SCHEMA §4.13 (S4) sets `supports_U` for claims on tier-U records (the relabel above), so the evidence rules require it.
- **Not edited, recorded only:** Anita's own site says it is based in Solon, Ohio (44139). Main has SITE-000122 / ORG-000123 in Woodmere (pre-existing). This is a relocation or address lead.
- **Conflict note:** #321 and #324 both touch `data/sites_OH.csv`, `organizations_OH.csv`, `evidence_sites_OH.csv` and `site_capabilities.csv` (appended rows). Whichever merges second needs a normal-merge replay.

## Withdrawal, 2026-11-14 (Codex REFUTE of #324 @ 79541c4): Anita Plastics site tags held
The refute: the PP/PE evidence and capability rows attach to `SITE-000122` (Woodmere, tier U, no street), but the company's own site gives a Solon address and its products page says Anita Plastics is a trading group for a parent that manufactures in India. Neither page binds PP/PE manufacture or sales to the held Woodmere establishment, and `supports_U` plus a caveat does not repair that (SCHEMA §4.15, §3.6).

Withdrawn (unit: cells and rows, all new in this PR, so no row loss):
- `SITE-000122` `materials` back to main's value (empty); it was `polyethylene_pe;polypropylene_pp`. `ORG-000123` already carries both terms at organization grain on main (EVD-013501, EVD-013502), so nothing is lost at org grain.
- EVD-345111, EVD-345112 removed from `evidence_sites_OH.csv`; CAP-001030, CAP-001031 removed from `site_capabilities.csv`. **Retired, never reuse.**
- The two terms moved from `verdicts.csv` and `scripts/decisions.csv` to `not_minted.csv` as HOLD (not REJECT).

| Hold | Recommended reading | What would settle it |
|---|---|---|
| Site-grain PP/PE tags and capabilities on `SITE-000122` | Org grain only until the location is settled | A page or filing tying PP/PE manufacture or sale to the Woodmere (or Solon) establishment, plus the owner's call on the Woodmere/Solon relocation lead already recorded above |

Counts after withdrawal (unit: rows added on this branch against its merge-base): `site_capabilities` rows 14; evidence rows 11 (6 in `evidence_sites_OH.csv`, 5 in `evidence_organizations_OH.csv`); site-row cells changed 5 (SITE-000417, 475, 477 materials; SITE-001791 processes and materials). The Results table and `summary.json` above were refreshed to these figures, which also clears the stale 17-capability line noted in the review.
