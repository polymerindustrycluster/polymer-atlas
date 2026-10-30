# Blind audit 8 — TRI-era organization and site creations

**Completed: 65/65 sampled records independently researched, frozen, then compared.** Draft packet only: [PR #9](https://github.com/polymerindustrycluster/polymer-atlas/pull/9). No canonical data edits, ID allocation, merges, or main pushes.

## Findings first

- **53/65 agreement on tested claims (81.5%)**, **2/65 confirmed field discrepancies (3.1%)**, **0/65 confirmed creation errors**, **10/65 unresolved (15.4%)**.
- Independent blind outcomes were **55 VERIFIED for existence/polymer scope and 10 STILL_UNCERTAIN**. VERIFIED is not agreement: two verified entities had a positively contradicted stored field.
- Propose correcting **Durable Products' current legal name from Inc. to LLC** and **Carlstar's HQ city from Nashville to Franklin**. These are proposals for the integrator, not applied changes.
- Ten unresolved records remain explicitly held. No failure to fetch was treated as absence. No closure/no-establishment REJECT was made; no Form 5500 gate was invoked or bypassed.

**Important limit:** “agreement” means no confirmed contradiction in the identity, existence, polymer activity, location/operator and other facts actually tested. It does **not** certify every stored field, all must-have claims, NAICS, county, legal continuity, precise current operating status, verification tier, or absence of duplicates. Untested/disputed facts are enumerated per record. Source-contract gaps and owner-only ring/grain proposals are separate from the factual-error numerator. Zero confirmed creation errors is not proof that the population contains none.

## Two positively settled field discrepancies

| Record | Field at pin | Independently observed value and settling source | Proposed handling |
|---|---|---|---|
| ORG-004034 — Durable Products | `legal_name = Durable Products, Inc.` | **Durable Products LLC** — [DQS certificate](https://durableproductsinc.com/wp-content/uploads/2025/11/IATF16949-10000432-DP-LLC.pdf), revision 2025-06-26, corroborated by the [current company footer](https://durableproductsinc.com/), both read 2026-10-30 | Review current name correction; retain historical alias only if continuity is established. Do not infer a successor, merger, conversion date or new organization. Certificate predates the record's 2026-10-30 creation. |
| ORG-004252 — Carlstar | `hq_city = Nashville` | **Franklin, TN** — explicit headquarters/contact address on [Carlstar's own page](https://connect.carlstargroup.com/about), read 2026-10-30 | Review HQ city; independently settle county from the physical address rather than carrying Davidson or guessing a replacement. The 2024 acquisition release's broader “Nashville-based” description does not override the precise HQ address. Exact move date is unknown; this is a current-pin discrepancy, not a dated relocation finding. |

Name-grading consistency: Durable's current own footer and dated exact-operator certificate mutually support LLC. Royale LLC/Inc and Jewell Hudgens Machine Co/Inc differences remain unresolved because the observed witnesses do not settle legal continuity or exact identity. Street suffixes, postal aliases and conflicting ZIP witnesses are likewise **not automatically counted as errors**. See `comparison.json` for all rationales and temporal caveats.

## Population, correction, pins and blindness

- Canonical creation-data pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`.
- Authoritative class-map v2 pin: `bf7857a7826ba62cdcf67af3ba718c3d5a9b32be`, `tasks/f1-class-map/f1_record_tri_class_mapping.csv`.
- Both have identical `data/` tree object `10d3144d9c3527d3ca9d819586af7d3b9197a2e1`. Metadata was read from the new head explicitly; later data was not silently absorbed. AGENTS, SCHEMA and queue instructions are unchanged.
- Full pass-20–25 frame: **2,199 unique creations = 682 organizations + 1,517 sites**. Exclude **227 NOT_TRI records**, all pass 20 (89 SC-wave and 138 Q01/Q02 creations). Eligible frame: **1,972 unique TRI-era creations**.
- Map v1 at `65dc7d4` incorrectly counted five `org_create_watch` markers as extra creations (2,204 rows). The independent duplicate check proved only 2,199 distinct IDs; the owner confirmed the map error and retracted the “sampler five short” statement. Original 2,199 reconstruction was correct. V2 resolves all IDs/classes; no draw used the duplicate-weighted frame. Full chronology: `RESUMPTION.md`.
- **P0 has zero creations by construction**, not a missing stratum. Auditing P0 links requires a separate pre-existing-record/link-row frame and protocol amendment. Eligible classes: P1 417, P2 180, P3 771, P4 604. Class is the creating facility's priority group, not an organization's prior held status; no mixed-class organizations.

An independent sampler reconstructed first-appearance commits and creation tiers, then supplied identity-only names/addresses/domains to five verifier batches. Those keys are unavoidable identity exposure, not independent evidence. Existing evidence, source notes, tiers and wave labels were withheld until **all 65 verdicts froze at 2026-10-30 23:08:00 UTC**. Comparison began **23:08:24 UTC**. Immutable source results are in `blind/`; `VERDICT_FREEZE.json` hashes them. No blind result was rewritten after comparison. All 65 selected IDs are covered exactly once.

### Reproducible stratification

Draw frozen **22:59:07 UTC**, seed `polymer-atlas-audit8-eceead3-2026-10-30-v1`.
Strata: creation tier A/B/C × P1–P4, refined by record table and whether an organization has exactly one held site at the data pin (all statuses included). Allocate one per nonempty refined stratum, then allocate the rest by weighted population / next allocation, with Tier C weight ×3 and P4 single-facility-org weight ×2; deterministic tuple tie-break. Uniform selection without replacement within each stratum. Inclusion probability is `n_h/N_h`.

The sample contains **29 organization records and 36 site records**, tiers **A 9 / B 31 / C 25**, waves **P1 14 / P2 7 / P3 21 / P4 23**. Tier C is 25/65 of the sample versus 406/1,972 of the eligible frame; P4 single-facility organizations are 13/65 versus 289/1,972. Same-organization observations stayed in one verifier batch to share the approximately six-primary-route budget. Five batches each contained 13 records.

`sampler.py`, `SAMPLING_STATUS.md`, `DRAW_MANIFEST.json` and `sample_metadata.json` specify the design and all inclusion probabilities. Two independent reruns reproduced all nine frozen sampler outputs byte-for-byte. There was one first valid draw, no provisional selection and no outcome-driven replacement.

## Measured rates

Raw sample rates reflect deliberate oversampling. Population-weighted **observed-finding point estimates** use `sum(I_grade / inclusion_probability) / 1,972`:

| Grade | Raw count / 65 | Raw rate | Weighted point estimate |
|---|---:|---:|---:|
| Agreement on tested claims | 53 | 81.5% | 82.0% |
| Confirmed field discrepancy | 2 | 3.1% | 3.8% |
| Confirmed creation error | 0 | 0.0% | 0.0% |
| Unresolved | 10 | 15.4% | 14.2% |

Do not read these as whole-record correctness estimates. Seventeen refined strata have only one sampled record; **no design-based confidence interval is claimed**. The weighted field-error point is particularly unstable: Durable's weight is 3 and Carlstar's weight is 71, so one B/P3 multi-facility-organization observation dominates it. Org/site observations can be correlated. On the 55 resolved cases only, field discrepancies are 2/55 = 3.6% (weighted resolved-only 4.4%); that conditional rate excludes unresolved cases and is not the headline rate.

### Creation-tier × wave results

Counts below are unweighted measured outcomes. Rates in parentheses are within the sampled tier × wave group; unequal refined-stratum probabilities mean these are not population-weighted group rates. Full weighted group rates are in `tier_wave_rates.csv`; all 28 uniform-probability refined strata and rates are in `stratum_rates.csv`.

| Tier / wave | Eligible N | Sample n | Agreement | Field error | Creation error | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| A / P1 | 12 | 2 | 2 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| A / P2 | 5 | 1 | 1 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| A / P3 | 88 | 3 | 2 (66.7%) | 0 (0.0%) | 0 (0.0%) | 1 (33.3%) |
| A / P4 | 128 | 3 | 3 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| B / P1 | 324 | 8 | 6 (75.0%) | 1 (12.5%) | 0 (0.0%) | 1 (12.5%) |
| B / P2 | 156 | 4 | 4 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| B / P3 | 502 | 8 | 5 (62.5%) | 1 (12.5%) | 0 (0.0%) | 2 (25.0%) |
| B / P4 | 351 | 11 | 11 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| C / P1 | 81 | 4 | 4 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| C / P2 | 19 | 2 | 1 (50.0%) | 0 (0.0%) | 0 (0.0%) | 1 (50.0%) |
| C / P3 | 181 | 10 | 6 (60.0%) | 0 (0.0%) | 0 (0.0%) | 4 (40.0%) |
| C / P4 | 125 | 9 | 8 (88.9%) | 0 (0.0%) | 0 (0.0%) | 1 (11.1%) |

### Historical audits — descriptive comparison only

| Audit | Supplied result | Rate | Comparability limitation |
|---|---|---:|---|
| Audit 6 | 0/37 creation errors; 12/37 field errors | 0.0%; 32.4% | Different creation population and observation time; supplied baseline, not re-audited here. Its field taxonomy and unresolved-case handling are not established by these two totals. |
| Audit 7 | 58/65 agreement | 89.2% | Different frame/design; the remaining seven cannot be assigned to field/creation/unresolved categories from the supplied aggregate alone. |
| Audit 8 | 53/65 tested-claim agreement; 2/65 field discrepancies; 0/65 creation errors; 10/65 unresolved | 81.5%; 3.1%; 0.0%; 15.4% | Oversampled risk strata, bounded source budget, mixed organization/site unit and explicitly incomplete field coverage. |

These figures do **not** establish improvement or deterioration. The lower observed field-error share cannot be interpreted causally or as an equivalent all-field accuracy measurement.

## Ten unresolved records — named settling facts

| Record / identity | Settling fact required |
|---|---|
| ORG-004047 — Marble Products Co | Existence and Wichita location agree on tested claims; polymer composition and distinct organization grain remained unresolved at blind freeze. Takara association does not positively contradict Koken ultimate-parent field without a complete legal chain. See frozen observations and named witnesses in `blind/`. |
| ORG-004080 — Rahco Rubber, Inc. | Settling fact: current primary confirmation of Rahco legal identity and rubber manufacturing. Six primary routes failed; chamber supports the business but is not a primary signal. Failure is availability only. See frozen observations and named witnesses in `blind/`. |
| ORG-004202 — LACC, LLC | Independent existence/polymer scope remains unresolved on the named frozen settling fact; original evidence does not rewrite blind verdict. See frozen observations and named witnesses in `blind/`. |
| SITE-004762 — Rockmart Fuel Containment - Rockmart Plant | Independent sources confirm operating Rockmart fuel-containment business and historical rubber plant at669GoodyearStreet, but current parent directory says667GoodyearAve. Campus equivalence and current site-specific material/process continuity remain unsettled; not a proven wrong-address or creation error. See frozen observations and named witnesses in `blind/`. |
| SITE-005305 — Weir Minerals Linatex - Salt Lake City | Independent existence/polymer scope remains unresolved on the named frozen settling fact; original evidence does not rewrite blind verdict. See frozen observations and named witnesses in `blind/`. |
| SITE-005406 — Indorama Ventures Oxides - Clear Lake | Exact site address, Harris County, operator affiliation and EO/EG production agree. Whether this precursor-only activity qualifies in polymer scope remains an owner boundary question; neither reject nor ring correction is inferred. See frozen observations and named witnesses in `blind/`. |
| SITE-005513 — Conceptual Creations - Phoenix (38th Ave) | Settling fact: a primary/public establishment-specific witness connecting Conceptual Creations to polymer manufacturing at 3820 N 38th Avenue, Phoenix. No absence or closure inference. See frozen observations and named witnesses in `blind/`. |
| SITE-005582 — Goodrich Interiors / Collins Aerospace Interiors - Phoenix | Blind primary search established Phoenix evacuation-system activity but not the exact sampled address and polymer-material scope within cap. Original mirror/registry claims cannot retroactively settle that blind uncertainty. See frozen observations and named witnesses in `blind/`. |
| SITE-005618 — Toray Performance Materials - 460 Calle San Pablo, Camarillo | Company composite scope agrees but exact 460 Calle San Pablo establishment remains unverified. County listing at 1150 Calle Suerte is a different address and cannot prove duplicate, closure, or wrong address. See frozen observations and named witnesses in `blind/`. |
| SITE-005843 — Terra-Vaults - Fort Worth | Historical exact-address polymer manufacturing verified. Current Fort Worth operating status is unsettled: government file states planned move, while current company site advertises Gainesville manufacturing. No closure REJECT; no Form 5500 check performed. See frozen observations and named witnesses in `blind/`. |

These holds include precursor-only polymer-scope boundaries (Clear Lake EO/EG and LACC ethylene), exact-site/process links, historical/current address continuity and primary-route availability. For Terra-Vaults, a planned move and a current Gainesville manufacturing address do not prove Fort Worth closure. A Form 5500 establishment-address check would be required before any later closure/no-establishment REJECT; none is issued here.

## Owner decisions, enrichment and provenance — not counted as factual errors

- Ring/grain recommendations remain owner-only, including physical foam/composite/solid-surface manufacturing currently coded Ring 2, marketed custom compounding coded Ring 1, and diversified OEM or precursor-only boundaries. `comparison.json` preserves proposed values, sources and caveats; **no ring is changed or self-ruled**.
- Address/legal-name uncertainties include Future Foam Newton Street/Ave, Complete Home Concepts Avenue/Boulevard, Scougal ZIP 89434/89437, Rockmart 667/669, Midwest Chickasha/Ninnekah and Royale LLC/Inc. Missing HQ values that a new source can fill are enrichment opportunities, not false facts. Borger's missing street number and direction conflict require normalization, not a brand-to-legal-operator rewrite.
- LACC's disclosed joint venture warrants ownership-encoding review; the direct partners alone do not settle the ultimate-parent chain. No new dual-parent exception is created.
- Post-freeze inspection found **172 original evidence rows** for the 65 sampled records. Claim-type coverage: scope 65/65 records, existence 31/65, address 37/65, activity 36/65, parent 1/65, code 0/65 and liveness 0/65. These are typed-row coverage counts at the pin, **not proof the facts are false or absent from source prose**. They expose evidence-contract review work; no “missing row = factual error” shortcut was used.
- Original provenance flags include a Titan company release typed `government_filing`, a CompositesWorld URL typed `own_site`, a job mirror typed `own_site` and a Toray corporate homepage typed `government_filing`. They are separately documented per record, not silently repaired or folded into creation-error rates.
- Independent review also caught company-hosted but third-party-issued certificates labelled `own_site` in frozen observations. Frozen research is preserved verbatim. Derivative evidence drafts explicitly normalize certificate authorship to a conservative registry classification, B ceiling for non-address claims and C for address, with an auditable correction log. A hosting domain is not authorship.

## Packet and reproducibility

- `blind/*.json`: immutable 65 independent verdicts, observations, exact public source URLs/names/dates, unresolved facts and successful/failed routes. **321 observations over 137 distinct cited URLs** before derivative normalization; search snippets alone carry no finding.
- `comparison.json`: all 65 post-freeze grades, named field findings, original evidence assessment, owner-review and enrichment proposals. No new primary research was used to rewrite these blind outcomes.
- `evidence_drafts.csv`: **275 ID-free, claim-local drafts over 63 records and 129 frozen URLs**, with 35 held-out observations. Conceptual Creations SITE-005513 and Toray SITE-005618 receive no safe derivative rows because the independent facts did not establish the sampled address-specific site. Excluded/inferred/ambiguous observations and source-class corrections are explicit in the companion method/log. They are **not ready-to-integrate full records** and do not imply all must-have claims or active status are verified.
- `statistics.json`, `tier_wave_rates.csv`, `stratum_rates.csv`, `summarize.py`: reproducible raw/weighted outcome counts and rates.
- `sampler.py`, `sample_metadata.json`, `identity_only.json`, freeze manifests and `reproduction-check.txt`: full sampling/freeze provenance.
- `check_packet.py`: complete-ID, freeze-hash, source-log, comparison and ID-free-draft checks. Run from the repository with `python docs/reviews/f1-audit-8/check_packet.py` and reproduce rates with `python docs/reviews/f1-audit-8/summarize.py`.

Pinned canonical validator and SQLite build pass. No canonical file or schema text changed; only the original F1 queue claim differs outside this review directory. Draft PR remains unmerged, with independent review and integrator recheck required before any proposed correction. **Later policy-only drift flagged:** main advanced to `4a406991c9466b10896f17913f9995b541b39713` by 23:17 UTC, adding AGENTS §2 rule 10 on derived-frame uniqueness/creation-class whitelists/reconciliation. Only AGENTS changed after metadata pin bf7857a; canonical data tree remains byte-identical. The new rule was read and this audit already reconciles git first-appearance IDs/creation passes to the unique v2 map, rather than counting marker rows. The branch did not silently rebase or absorb that snapshot. Final local/upstream checks are recorded in `FINAL_CHECKS.json`; remote readback and published SHA are reported in the PR body/handoff.

## Record-level index

`A` = agreement on tested claims; `F` = confirmed field discrepancy; `U` = unresolved. Full rationales/field limitations are in `comparison.json`; immutable independent evidence is in `blind/`. One row per sampled record, not per organization.

| Record | Identity | Tier / wave at creation | Blind verdict | Grade |
|---|---|---|---|---|
| ORG-004034 | Durable Products, Inc. | B / P1 | VERIFIED | F |
| ORG-004036 | Arlon Graphics, LLC | A / P1 | VERIFIED | A |
| ORG-004039 | SumiRiko Tennessee, Inc. | B / P1 | VERIFIED | A |
| ORG-004047 | Marble Products Co | C / P2 | STILL_UNCERTAIN | U |
| ORG-004053 | SEKISUI Voltek, LLC | A / P2 | VERIFIED | A |
| ORG-004058 | Sinclair & Rush, Inc. | B / P2 | VERIFIED | A |
| ORG-004060 | Monument Chemical LLC | B / P2 | VERIFIED | A |
| ORG-004080 | Rahco Rubber, Inc. | A / P3 | STILL_UNCERTAIN | U |
| ORG-004087 | R&S Processing Co., Inc. | B / P3 | VERIFIED | A |
| ORG-004123 | Sterling Specialty Chemicals LLC | C / P3 | VERIFIED | A |
| ORG-004125 | Premier Foam Inc | C / P3 | VERIFIED | A |
| ORG-004202 | LACC, LLC | C / P3 | STILL_UNCERTAIN | U |
| ORG-004227 | Baxter Healthcare Corporation | C / P3 | VERIFIED | A |
| ORG-004252 | Carlstar Group LLC | B / P3 | VERIFIED | F |
| ORG-004269 | Bullfrog International, L.C. | A / P3 | VERIFIED | A |
| ORG-004332 | ABT Inc. | B / P4 | VERIFIED | A |
| ORG-004346 | American Renolit Corporation | B / P4 | VERIFIED | A |
| ORG-004367 | Central Marble Products Inc | C / P4 | VERIFIED | A |
| ORG-004378 | Coulter LLC | B / P4 | VERIFIED | A |
| ORG-004450 | Midwest Cooling Towers Inc | B / P4 | VERIFIED | A |
| ORG-004485 | The ROHO Group, Inc. | B / P4 | VERIFIED | A |
| ORG-004489 | Royale Comfort Seating LLC | A / P4 | VERIFIED | A |
| ORG-004537 | Electri-Glass, Inc. | B / P4 | VERIFIED | A |
| ORG-004546 | Jewell Hudgens Machine Co | C / P4 | VERIFIED | A |
| ORG-004549 | Mallard Creek Polymers | B / P4 | VERIFIED | A |
| ORG-004586 | Swarco Colorado Paint, LLC | B / P4 | VERIFIED | A |
| ORG-004590 | General Coatings Manufacturing Corp. | C / P4 | VERIFIED | A |
| ORG-004596 | Kempen Paint Co. | C / P4 | VERIFIED | A |
| ORG-004620 | Mississippi Polymers, Inc. | A / P4 | VERIFIED | A |
| SITE-004642 | Future Foam - Mansfield | B / P1 | VERIFIED | A |
| SITE-004651 | Future Foam - Newton | A / P1 | VERIFIED | A |
| SITE-004664 | LyondellBasell Clinton Complex | B / P1 | VERIFIED | A |
| SITE-004746 | Archem America - Sanborn | C / P1 | VERIFIED | A |
| SITE-004756 | Lear - Farwell Plant | B / P1 | VERIFIED | A |
| SITE-004762 | Rockmart Fuel Containment - Rockmart Plant | B / P1 | STILL_UNCERTAIN | U |
| SITE-004771 | AmesburyTruth - Statesville | C / P1 | VERIFIED | A |
| SITE-004828 | Danfoss - Mountain Home | C / P1 | VERIFIED | A |
| SITE-004843 | Solvay Specialty Polymers (Syensqo) - Borger | B / P1 | VERIFIED | A |
| SITE-004878 | DDP Specialty - Channahon | C / P1 | VERIFIED | A |
| SITE-004911 | CSP - Sarepta Plant | B / P1 | VERIFIED | A |
| SITE-004989 | American Excelsior - Sheboygan | C / P2 | VERIFIED | A |
| SITE-004995 | Covation Biomaterials - Kinston Site (Grifton) | B / P2 | VERIFIED | A |
| SITE-005050 | Armacell - Conover | B / P2 | VERIFIED | A |
| SITE-005235 | SMR Technologies - Fenwick | A / P3 | VERIFIED | A |
| SITE-005291 | ACCI Specialty Materials LLC - Harrisonville | C / P3 | VERIFIED | A |
| SITE-005305 | Weir Minerals Linatex - Salt Lake City | C / P3 | STILL_UNCERTAIN | U |
| SITE-005309 | Saint-Gobain Performance Plastics - Bristol | C / P3 | VERIFIED | A |
| SITE-005406 | Indorama Ventures Oxides - Clear Lake | B / P3 | STILL_UNCERTAIN | U |
| SITE-005498 | ITW Polymers Sealants North America (Amrize Building Envelope) - Houston | B / P3 | VERIFIED | A |
| SITE-005510 | Bullfrog International - Bluffdale | C / P3 | VERIFIED | A |
| SITE-005513 | Conceptual Creations - Phoenix (38th Ave) | C / P3 | STILL_UNCERTAIN | U |
| SITE-005567 | Tnemec - Baltimore | B / P3 | VERIFIED | A |
| SITE-005582 | Goodrich Interiors / Collins Aerospace Interiors - Phoenix | B / P3 | STILL_UNCERTAIN | U |
| SITE-005618 | Toray Performance Materials - 460 Calle San Pablo, Camarillo | C / P3 | STILL_UNCERTAIN | U |
| SITE-005635 | Techmer PM - Dalton | B / P3 | VERIFIED | A |
| SITE-005642 | Bakelite Synthetics - Louisville | B / P3 | VERIFIED | A |
| SITE-005695 | Complete Home Concepts - Riverside | A / P4 | VERIFIED | A |
| SITE-005717 | EMCO Williams - Sevierville | C / P4 | VERIFIED | A |
| SITE-005817 | Scougal Rubber - McCarran | C / P4 | VERIFIED | A |
| SITE-005838 | Synmar & Castech - Jonesboro | B / P4 | VERIFIED | A |
| SITE-005843 | Terra-Vaults - Fort Worth | C / P4 | STILL_UNCERTAIN | U |
| SITE-005862 | Chemtrusion - Jeffersonville | C / P4 | VERIFIED | A |
| SITE-005870 | Estron Chemical - Calvert City | B / P4 | VERIFIED | A |
| SITE-005924 | ResinLab / KitPackers - Germantown Plant | B / P4 | VERIFIED | A |
| SITE-005945 | Ryvec - Anaheim | C / P4 | VERIFIED | A |
