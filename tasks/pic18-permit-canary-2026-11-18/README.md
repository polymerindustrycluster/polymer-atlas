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

## Decision (round 2): GO under the registered thresholds, as held packets only, and fragile

Registered thresholds (above): specific ≥ 5/10 **and** ≥ 25 of 58 retrievable → GO. Under the registered rule the canary gives **6/10** and 33/58 retrieve, so the threshold is met, narrowly. Two things keep this from being a fill campaign:

1. **Nothing is applied.** Every proposal is `held` for owner ruling **B-PERMIT**: may a regulator's emissions-unit description carry a process claim, and at what strength? (SCHEMA §4.13: `government_filing` class ceiling `supports_A`, not an awarded tier; a table row or heading is a list item and is proposed at `supports_C` by contract rule 5c; on a tier-A/B record a C-strength term is a `site_capabilities` row only, owner ruling 2026-11-14.)
2. **The result is sensitive.** Excluding sites whose only term is `coating_applying` gives 4/10, below the threshold; counting only narrative-strength unit witnesses gives 1/10. Reach is capped at 58 sites (17.5% of the 331) and measured at 33.

Round 1 reported 8/10 with 10/10 bound. Codex round 1 refuted that: it used two ECHO-street fallbacks and a one-token holder match that the registered bind rule did not allow, and scored facility summaries as unit witnesses. Round 2 re-scores under the rule registered at `d0a43b46` and reports the broadened reading separately.

| Measure (unit, filter) | Value |
|---|---|
| Pool: PIC-18 organizations, process unknown (331), exactly one active PIC-18 site, FRS link on the site or organization → sites | **58** (17.5% of 331) |
| Pool sites whose linked FRS record has an ECHO air-program flag (`AIR_FLAG = Y`) | **41** |
| Pool sites with a retrievable final permit document (Ohio EPA eDocument, newest-6 rule) | **33** (Wilson 95% of 58: 44.1%–68.8%) |
| Not retrievable | **25**: 17 no air flag; 6 flagged but the Facility-ID search returned 0 documents; 2 documents listed but none of the newest 6 non-draft ones is a final permit (SITE-000517, SITE-000676) |
| Canary: 10 of the 33, `random.Random(20261118).sample(sorted(ids), 10)`; bound under the registered rule (printed Facility ID, holder = Atlas legal/trade name, street and city = Atlas site row) | **7/10** (broadened bind, with ECHO-street fallback and one-token holder match: 10/10) |

Specific hit = at least one §3.1 term that is not `_unspecified` and not ancillary, on a **bound** site, from an emissions-unit **heading or equipment description** (registered rule). Broadened = also unit-level terms and permit/facility descriptions, with the broadened bind. Projection = 33 retrievable × hit rate, over the 331 organizations.

| Reading | Specific hits | Wilson 95% | Projected sites of the 58 (range) | Share of the 331 (range) |
|---|---|---|---|---|
| **Registered rule** | 6/10 | 31.3%–83.2% | 19.8 (10.3–27.4) | 6.0% (3.1%–8.3%) |
| Registered, any-term (adds `_unspecified`) | 6/10 | 31.3%–83.2% | 19.8 (10.3–27.4) | 6.0% (3.1%–8.3%) |
| Registered, excluding sites whose only term is `coating_applying` | 4/10 | 16.8%–68.7% | 13.2 (5.6–22.7) | 4.0% (1.7%–6.9%) |
| Registered, narrative-strength witnesses only | 1/10 | 1.8%–40.4% | 3.3 (0.6–13.3) | 1.0% (0.2%–4.0%) |
| Broadened specific | 9/10 | 59.6%–98.2% | 29.7 (19.7–32.4) | 9.0% (5.9%–9.8%) |
| Broadened any-term | 10/10 | 72.2%–100.0% | 33.0 (23.8–33.0) | 10.0% (7.2%–10.0%) |

Context: the NEI SCC scout confirmed 2/20 (10%) with coarse terms only. A ratio over the 33 retrievable sites is not a rate over the 331.

## Screen: how many of the 58, and why not the others

`screen.csv` (one row per pool site, with the reason). Route: (1) Atlas FRS link → ECHO exporter `AIR_FLAG`/`AIR_IDS` for that FRS ID; (2) Ohio EPA's public eDocument search, document type Permit, secondary-ID field = the 10-digit Facility ID; (3) newest-first, up to 6 non-draft documents per site fetched and classified (final permit = `RE: FINAL AIR ...` line, printed Facility ID, ≥ 15,000 characters, unit terms). A zero-hit search, a missing flag and a failed fetch are availability signals about this route, never evidence that no permit exists (AGENTS §2.8).

Name-route check (exact-match only; outside the draw): for the 23 sites with no ID hit, searching the ECHO and Atlas names with the county found Air Permit documents for one site only, **SITE-001651 Chemical Solvents** (17 Air Permit documents under Facility ID `1318007651`), whose ECHO air ID suffix is `1318005609`: a different printed ID, so **held, not bound** (settling fact: a street address in a permit under `1318007651`, or an ECHO/FRS correction). Others returned water permits (NPDES) only.

## Canary: permits, terms, binding (every row held)

| Site | Name (Atlas) | Tier | Permits | Newest effective → face expiry | Registered bind | §3.1 term(s) in the quotes | Registered result |
|---|---|---|---|---|---|---|---|
| SITE-000814 | Cook Composites & Polymers Co. | C | P0133722 | 2023-09-22 → 2028-09-22 | BOUND | `coating_formulation` | miss (broadened hit) |
| SITE-001530 | Tremco CPG | B | P0130251, P0134097 | 2023-08-29 → 2026-09-13 (face-expired) | BOUND | `adhesive_sealant_formulation`, `coating_formulation` | **hit** |
| SITE-000248 | Architectural Fiberglass | C | P0131830, P0131913, P0133197 | 2023-05-16 → 2027-11-29 | BOUND | `coating_applying` | **hit** |
| SITE-000238 | Alliance Equipment Company, Inc. | C | P0105759, P0127661 | 2019-12-27 → 2024-04-08 (face-expired) | BOUND | `composites_hand_layup` | **hit** |
| SITE-001833 | ACO Polymer Products, Inc. | B | P0136498, P0137654 | 2025-03-28 → 2030-02-04 | NOT BOUND | `extrusion_unspecified` | miss |
| SITE-000140 | Cleveland Specialty Products | C | P0140000 | 2026-06-10 → 2031-06-10 | NOT BOUND | `foam_extrusion` | miss (broadened hit) |
| SITE-000535 | PLASTPRO INC | B | P0134435 | 2024-03-26 → 2029-03-26 | NOT BOUND | `composites_compression_smc_bmc`, `compression_molding` | miss (broadened hit) |
| SITE-000664 | Uniwall Mfg | C | P0131116 | 2025-09-10 → 2035-09-10 | BOUND | `laminating` | **hit** |
| SITE-000601 | Schneller LLC | A | P0127863, P0140443 | 2026-08-20 → 2031-08-20 | BOUND | `coating_applying`, `compounding_unspecified` | **hit** |
| SITE-000997 | Kurz-Kasch Inc. | C | P0135320 | 2024-07-15 → 2034-07-15 | BOUND | `coating_applying` | **hit** |

Per quote: `canary_quotes.csv` (19 rows over 10 sites: quote verbatim, document id, permit number, `witness` (unit_heading / unit_equipment count under the registered rule; unit_term and permit_description are broadened only), mapped term and `term_class`, note, class `government_filing`, ceiling `supports_A`, proposed strength, held route, settling fact). Per site: `canary_sites.csv` (printed bind fields, Atlas fields, both bind results, `location_evidence_note`). `doc_hashes.json` pins the PDF and extracted-text SHA-256 of every cited document; PDFs and text stay in controller storage `persist/pic18-permit-canary-2026-11-18/docs/` because cover letters name individuals.

**Round-2 adjudications (Codex round 1, findings 1–5).**
- *SITE-000248 (finding 1):* scored `coating_applying` from the gel-coat spray unit rows and the "resin/gel coat spray gun operation" term, the same mapping as SITE-000601 (coaters) and SITE-000997 (epoxy dip stations). The spray-up shaping step still has no §3.1 term (vocabulary gap held; `composites_hand_layup` would be inexact because the regulator lists Hand Lay-Up and spray-up as separate units at SITE-000238). Result: hit, and one of the two `coating_applying`-only sites.
- *SITE-000601 (finding 2):* the permit has a "Compounding" unit group (P002 mixers for "blending of pigments into raw compounds"): `compounding_unspecified` stands (unspecified); `pigment_colorant_dispersion` is **not** used (the words say blending, not dispersion). The unit-level witness for the coating term is now the "Coaters" group (reverse roll coaters) in the 2020 permit. Because compounding stands, the site is not coating-only in the sensitivity.
- *SITE-000535 (finding 3):* the work-practice term names the SMC slitter and mold charge loader at each press, so `composites_compression_smc_bmc` is supported in addition to `compression_molding` (a unit term: broadened reading). The site is not bound under the registered rule, so it is a miss there.
- *Binds (finding 4):* under the registered rule SITE-000140 (Atlas street blank), SITE-000535 (Atlas street blank; printed municipality Saybrook Twp. vs Atlas Ashtabula) and SITE-001833 (printed holder "ACO, Inc" vs Atlas legal name "ACO Polymer Products, Inc.", no trade name) are **not bound**: bound **7/10**. The stronger location evidence (ECHO exporter street equals the permit street, same ZIP, FRS link) is in each `location_evidence_note`; it is a lead for a later bind, not a registered bind.
- *SITE-000814 (finding 5):* the scored quote was a facility summary. No emissions-unit heading or equipment description names a §3.1 process (units are "Process 1 - 20X Area" with mixers). The unit-level recordkeeping term "the company name of each paint batch manufactured" is added as a unit_term witness. Registered rule: **miss**; broadened: hit.

**Currency.** Two canary permits are face-expired at 2026-11-18 (SITE-001530 expired 2026-09-13, SITE-000238 2024-04-08) with no later non-draft document in the portal listing; a timely renewal continues under Ohio rules, so this is a currency flag, not a status finding. Permit text is a statement as of its issue date, not proof of present operation. SITE-000601's coaters are listed in the 2020 permit (face expiry 2025-04-01).

## Self-refute (contract rule 15)

- self-refute: Grain — 19 quotes over 10 sites re-checked, 0 changed. Every permit is issued to a Facility ID; the issuance block street and municipality are compared with the Atlas site; Polynt's Illinois cover-letter address is not used. Round 1 had accepted ECHO-street fallbacks as binds; those are now not-bound.
- self-refute: Founding — 0 rows checked, 0 changed (no founding claim).
- self-refute: Strength — 19 quotes checked, 10 held at `supports_C` as list items (table rows and headings); the registered-rule yield is also reported at narrative strength only (1/10).
- self-refute: Truncated quote — 19 quotes checked, 0 changed: each contains the words that carry its term; `check.py` verifies each in order against the stored text.
- self-refute: Attribution — 19 quotes checked, 2 changed in round 2: the SITE-000814 facility summary no longer counts under the registered rule, and SITE-001833's holder match no longer counts as a bind. No quote is from a parent, customer or explainer page.

## Disclosures for the controller and owner

- **Facility-number derivation (rule 14).** The Ohio EPA Facility ID used as a search value is the last 10 characters of the ECHO `AIR_IDS` value (`OH` + 16 digits). It is a search term, not a fetched URL; tested on one facility first. Every ViewDocument URL fetched is a document id returned by a search this scout ran. The portal URL came from a web search and from links on Ohio EPA pages; its search form fields were read from the fetched page. No URL was guessed or constructed.
- **Retrieval unit.** `fetch_journal_v2.jsonl` holds **177 distinct document IDs** (the newest 6 non-draft documents per site across the 58-site screen, each downloaded once), all HTTP 200 with extractable text. Searches: 42 Facility-ID searches and 44 name searches (about 20 s each). An earlier scratch pass fetched 38 of the same documents under a looser classifier; its journal is not used. The 122 in round 1 was a mid-run count of journal lines and is withdrawn.
- **Order of work.** The screen and two permit excerpts were read before the criteria were committed (`d0a43b46`); the git record shows pre-draw registration, not pre-fetch registration.
- Local air agencies may hold some of the 8 no-document sites (unverified).

## Owner battery proposal B-PERMIT (held)

**Question:** May an Ohio EPA air permit's emissions-unit heading or equipment description be a `government_filing` witness for a §3.1 process at facility grain, and at what strength? Also: a §3.1 term for spray-up open molding (SITE-000248, SITE-000238's chopper booths)?
**Recommendation:** Admit unit descriptions that name the process in the permit's own words as `government_filing` corroboration (class ceiling for narrative descriptions, `supports_C` for table rows and headings); require printed Facility ID + holder (legal or trade name) + street + city binding against the Atlas site; carry issue and expiry dates; use `_unspecified` terms when the type is not stated; ancillary units (boilers, tanks, finishing paint booths) name no process; a vocabulary addition is a separate ruling.

## Reproduction and checks

- `python3 tasks/pic18-permit-canary-2026-11-18/build.py --canary` rebuilds `screen.csv`, `canary_*.csv`, `doc_hashes.json`, `metrics.json` from caches; Atlas rows are read at the pinned ref `832ea1b3` so later merges do not move the inputs. `build.py --regen-pool` rebuilds `pool.csv` from the controller's frame code at that ref. `fetch_permits.py search|docs` rebuilds the caches under `persist/pic18-permit-canary-2026-11-18/` (the original ID search ran from equivalent scratch scripts, ported verbatim; the name search is `ohio_epa_name_hits.json` there). `canary_verdicts.json` is hand-authored and never regenerated.
- Named check: `python3 tasks/pic18-permit-canary-2026-11-18/check.py`. It recomputes the air-flag count from the pinned ECHO exporter, the screen from the caches, the fetched-document set from the selection rule, the draw, every quote in order against its stored document, each quote's establishment (site → verdict document → printed Facility ID equals the site's ECHO-linked ID), every printed bind field and both bind results from the stored text and the Atlas rows at the pinned ref, every term against §3.1, pdf/text hashes, **every published metric** from the rows, and that nothing outside this folder (and nothing under `data/`) differs from the merge-base with `origin/main`. It then rejects **9/9** injected defects (fabricated quote, term not in §3.1, site outside the pool, frame site without verdict, change under `data/`, tampered count, real quotes swapped between two sites, fabricated bind fields, zeroed bound total and projection). Missing caches or `pdftotext` fail the run.

## Proposed follow-ups (not in this PR)

- Owner ruling B-PERMIT, then a packet lane over the **23 remaining retrievable sites** (integrator applies after the ruling).
- Settle SITE-001651's two Facility IDs; look up the 6 air-flag/no-document sites and 2 no-final-permit sites by a second route (ECHO detailed facility report, local air agency).
- Widen the pool: an FRS-linking lane over the other 273 process-unknown organizations raises the ceiling; blank Atlas site streets (SITE-000140, SITE-000535) block a registered bind that the ECHO street would otherwise support.
- `coating_applying` seeding question (SCHEMA §3.6) and the spray-up vocabulary gap.

Not checked: the 273 process-unknown organizations outside the 58; the 23 retrievable sites outside the canary; permits older than the newest 6 documents per site; local-agency permits; whether any plant still runs the permitted equipment; OCR accuracy beyond the quoted words (quotes verified against the extracted text of the stored PDFs).
Risk: unit text is a regulator's restatement of the applicant's description, dated at issue; a bound permit is not proof of present operation or of polymer relevance for coating-only plants.
