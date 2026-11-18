# PIC-18 Ohio EPA air-permit process scout — packet only (0 data rows)

Claim: atlas-w18-permit, controller-assigned, 2026-11-18. Packet only: no data file, queue, validator or `tier1_qualifier*` change.

First user: the Atlas integrator, deciding at the W18 review whether to open a full permit lane. Non-use is a finding if that lane has not been opened or declined by the next wave review.

## Pre-registered criteria (written and committed before the canary draw)

Disclosure of order: the 58-site screen (ECHO air flag, Ohio EPA eDocument search) and two permit excerpts (one single-unit PTIO, one Banbury/calender PTIO) were read while designing the loop, before these criteria were committed. No canary site was drawn and no unit text was mapped before this commit.

**Question.** Do Ohio EPA air-permit documents, issued to PIC-18 plants whose Atlas `processes` is unknown, name a process in words that a §3.1 term matches without being broader than the words, and do they bind it to that establishment?

**Would show it (GO case).** A canary site counts as a **specific hit** when its permit text (a) is bound to the establishment (printed Facility ID, holder name and street/city all match the Atlas site; one AIR ID per site, else hold), and (b) has at least one emissions-unit heading or equipment description whose words are matched exactly by a §3.1 term that is *not* an `_unspecified` term and *not* ancillary equipment (boilers, generators, tanks, baghouses, paint booths and cleaning are ancillary and name no §3.1 process). An **any-term hit** also admits `_unspecified` terms (the NEI scout already reached those from SCCs, so the added value of permits is in specific-subtype terms).

**Would refute it (NO-GO case).** Most retrievable permits list only ancillary units, generic "process"/"line" headings with no equipment noun, or cannot be bound to the establishment.

**Thresholds, fixed now.**
- GO for a full permit lane: specific yield ≥ 5/10 **and** ≥ 25 of the 58 pool sites with a retrievable permit.
- NO-GO: specific yield ≤ 2/10 **or** < 15 of 58 retrievable.
- Otherwise GO-as-leads (held packets for integrator triage, no fill campaign).
- Projection over the 331 = (retrievable permit sites of 58) × (specific yield) with its Wilson 95% interval; sites outside the 58 (no FRS link, multi-site organizations) are unreachable by this route as built.

**Definitions.**
- *Air-program record*: ECHO exporter `AIR_FLAG = Y` for an FRS ID that is on the Atlas record for that site/organization, from the pinned exporter extract (`persist/oh-federal-rematch`, retrieved 2026-11-16).
- *Retrievable permit document*: a stored PDF fetched from Ohio EPA's eDocument public portal, with a text layer containing the printed Facility ID, classed as a final permit-to-install / PTIO / Title V permit (not a cover letter, correspondence or draft), with at least one emissions-unit term.
- *Per-site document rule*: newest-first, up to 6 non-draft documents, no stop at first hit; units are the union across final permits, newest permit wins per unit ID.
- *Current*: no later non-draft permit document for that facility is listed in the portal search at retrieval date; permit effective/issue date is recorded.

**Draw rule, added before the draw (2026-11-18).** The canary pool is the sites whose `status` is `retrievable_permit` in `screen.csv` by the printed-Facility-ID route only. The exact-name searches for sites with no ECHO air flag or zero ID hits (the portal's name field is exact-match only) are reported as leads that would each need an address match, and are outside the draw. Draw: `random.Random(20261118).sample(sorted(ids), 10)`. No substitution for a site whose permit fails to bind: it counts as a miss.

## Decision: GO as a bounded packet lane (held packets only), not a fill campaign

Applied against the thresholds fixed above: specific yield **8/10** (≥ 5) and **33 of 58** retrievable (≥ 25) → **GO** for a permit lane. Three conditions travel with it, and they are why this is not "GO to fill":

1. **No row is applied.** Every proposal below is `held` for owner ruling **B-PERMIT**: may a regulator's emissions-unit description carry a process claim, and at what strength? (SCHEMA §4.13: `government_filing` has class ceiling `supports_A`; that ceiling is not an awarded tier. Registry address alone caps at `supports_C`. A narrative permit or unit description is proposed at the ceiling; a unit table row or heading is a list item and proposed at `supports_C` by contract rule 5c. On a tier-A/B record a C-strength term is a `site_capabilities` row only, owner ruling 2026-11-14.)
2. **Reach is capped at 58 sites** (17.5% of the 331) and measured at 33: this route cannot touch organizations without an FRS link, with several active sites, or whose plant has no Ohio EPA permit document the portal returns.
3. **A conservative reading still clears the bar:** counting only narrative-strength quotes, **6/10**.

| Measure (unit, filter) | Value |
|---|---|
| Pool: PIC-18 organizations, process unknown (331), exactly one active PIC-18 site, FRS link on the site or organization → sites | **58** (17.5% of 331) |
| Pool sites whose linked FRS record has an ECHO air-program flag (`AIR_FLAG = Y`) | **41** |
| Pool sites with a retrievable final permit document (Ohio EPA eDocument, newest-6 rule) | **33** (Wilson 95% of 58: 44.1%–68.8%) |
| Not retrievable | **25**: 17 no ECHO air flag; 6 air flag but the Facility-ID search returned 0 documents; 2 documents listed but none of the newest 6 non-draft ones is a final permit (SITE-000517, SITE-000676) |
| Canary: 10 sites drawn from the 33, `random.Random(20261118).sample(sorted(ids), 10)` | bound to the establishment: **10/10** |
| **Specific hit** (≥ 1 §3.1 term bound, not `_unspecified`, not ancillary) | **8/10, Wilson 95% 49.0%–94.3%** |
| Specific hit at narrative strength only | 6/10 (31.3%–83.2%) |
| Any-term hit (adds `_unspecified`) | 9/10 (59.6%–98.2%) |
| Projected specific-term sites among the 58 = 33 × 8/10 | **26.4** (16.2–31.1) = **8.0%** of the 331 (4.9%–9.4%) |

Context: the NEI SCC scout confirmed 2/20 (10%) and could only produce coarse terms. The permit route reaches 6–8 of 10 canary sites with specific terms, but only over the sites that have a retrievable permit. A ratio drawn from the 33 retrievable sites is not a rate over the 331.

## Screen: how many of the 58, and why not the others

`screen.csv` (one row per pool site, with the reason). Route order: (1) Atlas FRS link → ECHO exporter `AIR_FLAG`/`AIR_IDS` for that FRS ID; (2) Ohio EPA's public eDocument search, document type Permit, secondary-ID field = the 10-digit Facility ID; (3) newest-first, up to 6 non-draft documents per site fetched and classified. A zero-hit search, a missing flag and a failed fetch are availability signals about this route, never evidence that no permit exists (AGENTS §2.8).

Name-route check (exact-match only; outside the draw): for the 23 sites with no ID hit, searching the ECHO and Atlas names with the county found Air Permit documents for one site only, **SITE-001651 Chemical Solvents** (17 Air Permit documents under Facility ID `1318007651`), whose ECHO air ID suffix is `1318005609`: a different printed ID, so **held, not bound** (settling fact: street address in a permit under `1318007651`, or an ECHO/FRS correction). Others returned water permits (NPDES) only. The portal's name field is exact-match, so these zeros are weak.

## Canary: permits, terms, binding (every row held)

| Site | Name (Atlas) | Tier | Permits | Newest effective → face expiry | Bind | §3.1 term(s) | Proposed strength | Applied |
|---|---|---|---|---|---|---|---|---|
| SITE-000814 | Cook Composites & Polymers Co. | C | P0133722 | 2023-09-22 → 2028-09-22 | BOUND | `coating_formulation` | supports_A | held |
| SITE-001530 | Tremco CPG | B | P0130251, P0134097 | 2023-08-29 → 2026-09-13 (face-expired) | BOUND | `adhesive_sealant_formulation`, `coating_formulation` | supports_A, supports_C | held |
| SITE-000248 | Architectural Fiberglass | C | P0131830, P0131913, P0133197 | 2023-05-16 → 2027-11-29 | BOUND | `— (no §3.1 term)` | — | held |
| SITE-000238 | Alliance Equipment Company, Inc. | C | P0105759, P0127661 | 2019-12-27 → 2024-04-08 (face-expired) | BOUND | `composites_hand_layup` | supports_C | held |
| SITE-001833 | ACO Polymer Products, Inc. | B | P0136498, P0137654 | 2025-03-28 → 2030-02-04 | BOUND | `extrusion_unspecified` | supports_C | held |
| SITE-000140 | Cleveland Specialty Products | C | P0140000 | 2026-06-10 → 2031-06-10 | BOUND | `foam_extrusion` | supports_A | held |
| SITE-000535 | PLASTPRO INC | B | P0134435 | 2024-03-26 → 2029-03-26 | BOUND | `compression_molding` | supports_C | held |
| SITE-000664 | Uniwall Mfg | C | P0131116 | 2025-09-10 → 2035-09-10 | BOUND | `laminating` | supports_A | held |
| SITE-000601 | Schneller LLC | A | P0127863, P0140443 | 2026-08-20 → 2031-08-20 | BOUND | `coating_applying` | supports_A | held |
| SITE-000997 | Kurz-Kasch Inc. | C | P0135320 | 2024-07-15 → 2034-07-15 | BOUND | `coating_applying` | supports_A | held |

Per quote: `canary_quotes.csv` (12 rows over 10 sites: quote verbatim in document order, document id and permit number, mapped term and `term_class`, mapping note, class `government_filing`, ceiling `supports_A`, proposed strength, held route, settling fact). Per site: `canary_sites.csv`. Documents: `doc_hashes.json` pins the PDF and the extracted-text SHA-256 of every cited document (PDFs and text stay in controller storage `persist/pic18-permit-canary-2026-11-18/docs/`, because cover letters name individuals; the quotes here are permit-description and unit text only).

**Binding rule (every row).** A permit is bound to the establishment only if (a) the printed Facility ID equals the ID in the ECHO exporter row of the Atlas-linked FRS record, (b) the holder name equals the organization legal name or a recorded trade name, and (c) the permit's issuance-block street equals the Atlas site street, or the ECHO exporter street where the Atlas site row has none (SITE-000140, SITE-000535). A cover-letter mailing address is never used; Polynt's cover letter is addressed to Illinois, its issuance block to Sandusky. Result: 10/10 bound. SITE-001530's holder changed name between permits (recorded in its note).

**Process notes.** (1) SITE-000248: the regulator's units are "spray up booth[s]" for polyester gelcoat and FRP; in SITE-000238's tables Hand Lay-Up and spray-up Chopper Booths are separate units, so no §3.1 term states spray-up open molding and `composites_hand_layup` would be inexact. This is a **vocabulary gap held for owner ruling**, not a miss to be papered over. (2) SITE-001833: "Polymer Concrete Extruder Line" maps only to `extrusion_unspecified`; counted as any-term, not specific. (3) The two `coating_applying` sites (SITE-000601, SITE-000997) match the §3.1 words but the permits say metal parts or decorative laminates; polymer relevance rests on the Atlas NAICS and ring. Excluding them, specific yield is 6/10. (4) §3.6 notes that `coating_applying` is not a seeded capability at plant grain.
**Currency.** Two canary permits are face-expired at 2026-11-18 (SITE-001530 expired 2026-09-13, SITE-000238 2024-04-08) with no later non-draft document in the portal listing; Ohio EPA rules let a timely renewal continue, so this is a currency flag, not a status finding. Permit text is a statement as of its issue date, not proof of present operation.

## Self-refute (contract rule 15)

- self-refute: Grain — 12 quotes over 10 sites checked, 0 changed. Every permit is issued to a Facility ID whose issuance block street equals the site; Polynt's cover letter (Illinois) was not used; no company-wide or sister-plant page is used.
- self-refute: Founding — 0 rows checked, 0 changed (no founding or date-of-establishment claim made).
- self-refute: Strength — 12 quotes checked, 4 downgraded from the class ceiling: table rows and headings (CQ-02, CQ-05, CQ-06, CQ-08) are held at `supports_C`, not `supports_A`; CQ-04 maps no term. Yield reported both ways (8/10 all, 6/10 narrative-only).
- self-refute: Truncated quote — 12 quotes checked, 0 changed: each quote contains the words that carry its term (for example "production of coatings and adhesives", "coating lines", "foam extrusion line"); `check.py` also verifies each in order against the stored text.
- self-refute: Attribution — 12 quotes / 10 sites checked, 0 changed: every quote is the permit's own text about the permitted facility, not a parent, customer or explainer page. Holder-name bind rechecked for SITE-001530 (rename) and SITE-000997 (trade name of a parent organization, Atlas `trade_names`).

## Disclosures for the controller and owner

- **Facility-number derivation (rule 14).** The Ohio EPA Facility ID used as a search value is the last 10 characters of the ECHO `AIR_IDS` value (`OH` + 16 digits). It is a search term, not a fetched URL; it was tested on one facility first. Every ViewDocument URL fetched is a document id returned by a search this scout ran. The eDocument portal URL came from a web search and from links on the Ohio EPA pages fetched; its search form fields were read from the fetched page. No URL was guessed or constructed.
- **Source terms.** Ohio EPA eDocument is a public-records portal (ORC 149.43 notice on its search page). Retrieval was about 150 searches (each about 20 s) and 122 document downloads; no access barrier was met.
- **Order of work.** The screen and two permit excerpts were read before the criteria were committed; see the top section.
- Local air agencies may hold some of the 8 no-document sites (unverified).

## Owner battery proposal B-PERMIT (held)

**Question:** May an Ohio EPA air permit's emissions-unit description or permit description be a `government_filing` witness for a §3.1 process at facility grain, and at what strength? Also: add a §3.1 term for spray-up open molding (SITE-000248, SITE-000238's chopper booths)?
**Recommendation:** Admit permit and unit descriptions that name the process in the permit's own words as `government_filing` corroboration at the class ceiling for narrative descriptions and `supports_C` for table rows and headings; require printed Facility ID + holder + street binding as above and carry issue and expiry dates; use `_unspecified` terms when the type is not stated; treat ancillary units (boilers, tanks, paint booths for finishing) as naming no process; a vocabulary addition (spray-up) is a separate ruling.

## Reproduction and checks

- `python3 tasks/pic18-permit-canary-2026-11-18/build.py --canary` rebuilds `screen.csv`, `canary_*.csv`, `doc_hashes.json`, `metrics.json` from caches. `build.py --regen-pool` rebuilds `pool.csv` from the controller's frame code at the pinned ref (`832ea1b3`). `fetch_permits.py search|docs` rebuilds the caches under `persist/pic18-permit-canary-2026-11-18/` (the original search ran from equivalent scratch scripts, ported verbatim; the name-route search is `ohio_epa_name_hits.json` there). `canary_verdicts.json` is hand-authored and never regenerated.
- Named check: `python3 tasks/pic18-permit-canary-2026-11-18/check.py` — recomputes the air-flag count from the pinned ECHO exporter, the screen from the caches, the fetched-document set from the selection rule, the draw, every quote in order against its stored document, every term against §3.1 (validator `PROCESSES` and the SCHEMA section), pdf/text hashes, the hit counts, Wilson intervals and projections, and that nothing outside this folder (and nothing under `data/`) changed; it then rejects **6/6** injected defects (fabricated quote, term not in §3.1, site outside the pool, frame site without verdict, change under `data/`, tampered count). Missing caches or `pdftotext` fail the run.

## Proposed follow-ups (not in this PR)

- Owner ruling B-PERMIT (above), then a packet lane over the **23 remaining retrievable sites**, integrator of record applies after the ruling.
- Settle SITE-001651's two Facility IDs; look up the 6 air-flag/no-document sites and 2 no-final-permit sites by a second route (ECHO detailed facility report, local air agency) before calling them unreachable.
- Widen the pool: the route only reaches sites with an FRS link; an FRS-linking lane over the other 273 process-unknown organizations raises the ceiling.
- `coating_applying` seeding question (SCHEMA §3.6) and the spray-up vocabulary gap.

Not checked: the 273 process-unknown organizations outside the 58; the 23 retrievable sites outside the canary; permits older than the newest 6 documents per site; local-agency permits; whether any plant still runs the permitted equipment; OCR accuracy of scanned permits beyond the quoted words (quotes were verified against the extracted text of the stored PDFs).
Risk: unit text is a regulator's restatement of the applicant's description, dated at issue; a bound permit is not proof of present operation or of polymer relevance for coating-only plants.
