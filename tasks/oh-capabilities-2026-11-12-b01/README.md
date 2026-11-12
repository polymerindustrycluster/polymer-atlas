# Ohio PIC-18 processes/materials + site_capabilities — batch b01 (2026-11-12)

Worker: grok (branch `agent/grok/oh-capabilities-2026-11-12-b01`). Claim line: `tasks/QUEUE.md`, under the 2026-11-04 claude-code "PIC-18 capability pass" line (added in #321 only).

**Stale claim note.** The `claimed:claude-code 2026-11-04` PIC-18 capability pass has had no capability PR since #124 (2026-11-05). Before that came #92, folded into #108, and #117. claude-code's latest PR is #261 (2026-11-09, people/dedupe). This lane treats that claim as stale, not released.

## Owner ruling recorded (2026-11-12, 13:51 ET)
Owner's words, in reply to the proposal to accept own-site capability/menu lists at a lower tier and use permit records for site-level process facts: **"ok, go for it."**

How it is applied here (existing vocab only, so validate passes):
- **Menu lists.** Own-site capability or menu lists (e.g. "Capabilities: Injection Molding", a Materials page list, a product-line title) now count. Each such row is `source_class=own_site`, `tier_effect=supports_C`, with `basis: self-described menu (owner ruling …)` in claim_detail. The matching `site_capabilities` row is `company_disclosed`, and its notes carry the same basis.
- **Narrative clauses.** Rows where the company states its own process or material in a sentence stay `supports_A`.
- **Permits.** EPA/state permit records (FRS, TRI, Ohio EPA air permits) may support site-level process facts as `government_filing`. This batch used none (see "Permit route").
- **Exclusions.** Hiring sites and the banned sources (Plastics News, Data Axle, Rubber News rankings, ZoomInfo, D&B, CB Insights, PIC CRM) still don't count.

## Frame
`frame.csv` holds rows 0:100 of cap_frame (306), in county order (Summit, Portage, Stark, Medina, Wayne, Cuyahoga, …) and by site_id within each county. A row qualifies when it is:
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

## Results
| | count |
|---|---|
| frame rows | 100 (86 with ≥1 page loaded; 394 pages) |
| candidates judged | 110 |
| accepted term decisions | 31 (`verdicts.csv`) |
| records gaining a §3 tag | **11** (11.0% yield) |
| sites tagged, by basis | narrative (A) 11, menu (C) 2 (a site can have both) |
| evidence rows by basis | narrative 18, menu 2 (site 20, org 5) |
| site_capabilities rows | 15 (CAP-001000..CAP-001014) |
| evidence IDs | EVD-345000..EVD-345024 |

Candidates that were not minted are in `not_minted.csv`, each with a reason. These are not REJECT verdicts on records. When a fetch failed, the source was unavailable; that does not mean the capability is absent.

## Permit route
No permit rows were minted in this batch. TRI/FRS give NAICS and chemicals, not §3 process terms. Ohio EPA air-permit emission-unit descriptions do name processes, but they need a per-facility document pull. That is left as the next source for the rows still untagged.

## Leads
- Ohio Precision Molding SITE-000085: the website on file is designmolded.com (Design Molded Plastics SITE-000069), the same as the Lane A address-first lead. Nothing was minted.
- ACE Cryogenic SITE-001695 ("two locations") and Impact Sleeves SITE-001883 (Locations page) have one Atlas site each but disclose more locations, so they are org grain only. Possible missing sites.

## CI
The CI `validate` job fails on main too: docs/schema/vocab.json is stale, and test_audit_evidence_coverage errors on EVD-333167. It is not touched here, per instruction. `python3 scripts/validate.py` passes locally, and `scripts/check_row_loss.py --base origin/main` is OK.

---
Never merged by the author. No Muse files touched; the only QUEUE edit is the #321 claim line. No paid calls.
