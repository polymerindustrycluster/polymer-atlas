# Michigan / Illinois merged-site quality pass

The frozen frame is 35 Michigan/Illinois establishments created by merged PRs #138 (17 MI sites) and #143 (18 IL sites). Eight sites advance C→B (2 MI, 6 IL); 27 sites remain C. No organizations or sites are created. Forty evidence rows are appended (10 MI, 30 IL): each promoted site receives B-strength existence, address, code, operator linkage and scope observations. All pre-existing evidence, including the original C observations, remains unchanged.

## Acceptance and boundaries

Acceptance was written before application: exactly one verdict per frozen site; all five must-have claims at B; raw own-domain or B-PARENT witness naming the plant city and polymer activity; physical-site binding; no change to operating_status, NAICS, ring, process/material tags, addresses, parent relationships, registry links or derived fields. Site changes are limited to verification_tier, sources, last_verified and appended notes. Only four canonical shards change.

Frame base `97ee6bc2a4475a47d8449ca79db688fb9114ab0f`; PRs #150/#151 were unmerged at freeze and are excluded. Later merges require a separate frozen continuation. EVD IDs use the reserved 277500+ sub-block and immutable input ordinals (six slots/site, five used for a promotion; gaps are never reused). First user: PIC campaign integrator/John Swanson on 2026-11-06; non-use finding date: 2026-11-13.

B-PARENT (OWNER_BATTERY_2026-11-04.md lines12–31) applies only to already recorded parents: Techniplas ultimate_parent_name=Techniplas and Avery Dennison ultimate_parent_name=Avery Dennison Corporation. Their PDFs are on those corporate domains and bind exact plant addresses to activity; no parent is invented. SCHEMA4.13 admits own domain / own issued document. Avery annex page2 was independently rendered: scope explicitly covers all sites on that page, with Mount Prospect in the bottom-middle cell (902 Feehanville Drive). This pass extracts one location, not a general PDF table. Mt. is the unchanged filed abbreviation for Mount.

The 07:20 rule is enforced: every own_site claim_detail contains only a raw-verified page quotation. Filing identifiers, operator normalization, and other federal facts remain in government_filing rows. Banked ITA CY2025 observations retain observed_date2026-11-01 under the controller exception, with submission date and current review in notes. The four government observations per site are re-adjudicated at B with an independent plant witness; scope is carried separately by the own-site row. This is not a current-operation claim: operating_status remains unknown. Dated source vintage is distinct from retrieval2026-11-06. Pella process witness is2023-03-01; Techniplas revision2023-12-19; Avery annex2026-08-18. These support process identity, not current certificate validity.

## Promoted establishments: full census

Fewer than20 creates/promotions: the controller-approved full-census alternative replaces a20-row sample. All8 selected witnesses, all8 banked field sets, and all40 resulting observations are checked; `blind-input.csv` supplies the source-only census for independent clerks.

| Site | Plant | Own witness and binding |
|---|---|---|
| SITE-018006 | The Spiratex Company - Monroe | [Production Operator – Monroe Produce quality parts by operating all ram extrusion equipment and running production jobs.](https://www.spiratex.com/careers/); Monroe ram-extrusion job is paired with own contact page at 1916 Frenchtown Center Dr.; plastic-extrusion context and filed 326199. Contact address independently raw-checked; only one held Spiratex Monroe plant. |
| SITE-018012 | Techniplas US LLC - Jonesville | [PLASTIC INJECTION MOLDING FOR THE AUTOMOTIVE INDUSTRY](https://www.techniplas.com/wp-content/uploads/2024/12/Jonesville-ISO_14001-2015_Jonesville_261220.pdf); Own-domain certificate p1 names the exact operator/address and process. Existing ultimate_parent_name Techniplas qualifies B-PARENT. Process witness at stated 2023-12-19 revision; no certification-validity or current-operation assertion. |
| SITE-019001 | Pella Corporation - Macomb | [producing vinyl windows at Pella’s Macomb plant](https://pressroom.pella.com/women-leaders-at-pella-corporation-recognized-for-excellence-in-manufacturing/); Dated 2023-03-01 own corporate release identifies Macomb vinyl-window manufacturing; CY2025 filing supplies exact address/operator/code, and there is only one held Pella Macomb plant. Historical process corroboration, not a fresh operating-status assertion. |
| SITE-019006 | Owens Corning - Rockford | [The Owens Corning Rockford IL is a premier manufacturing facility that manufactures extruded polystyrene foam board insulation](https://careers.owenscorning.com/job/Rockford-Production-Associate-IL-61109/1446312100/); Own career subdomain names Rockford polystyrene-foam manufacturing; CY2025 filing supplies 2710 Laude Drive/code/operator. Only one held Owens Corning Rockford site; no current-status change. |
| SITE-019007 | Avery Dennison - Mt. Prospect | [The design and manufacture of pressure-sensitive webstock products and printing inks, and the conversion of non-pressure-sensitive webstock products](https://label.averydennison.com/content/dam/averydennison/lpm-responsive/na/doc/technical-bulletins/product/sustainable-solutions/iso-9001-2015-certificate.pdf); Own-domain annex page2 explicitly applies manufacturing scope to all locations on that page, including bottom-middle Avery Dennison 902 Feehanville Drive, Mount Prospect IL60056. Page2 independently rendered and checked; Mt. abbreviates Mount. Recorded ultimate_parent_name Avery Dennison Corporation supplies B-PARENT for corporate subdomain. Process scope only, no current certificate claim. |
| SITE-019015 | Pretium Packaging - Aurora | [With bottle manufacturing plants throughout North America and Europe](https://www.pretiumpkg.com/locations/); Location is explicitly Aurora Illinois Manufacturing Plant in bottle-plant list, distinct from warehouse/office entries. Own page omits Suite140; unchanged suite is supported by CY2025 filing, not attributed to own page. |
| SITE-019016 | Marian, Inc. - West Chicago | [Additional core manufacturing capabilities at Chicago include: Rotary die cutting Steel rule die cutting Matched metal die cutting and more](https://marianinc.com/marian-chicago/); Own facility page binds Chicago capability narrative to 396 Wegner Drive West Chicago. Flexible component fabrication and silicone context plus filed 326299 corroborate polymer converting; no manufacturing techniques added to canonical cells. |
| SITE-019017 | All-State Industries, Inc. - ELK GROVE VILLAGE | [Die Cutting, Water Jet Cutting, Thermal Bending & Assembly.](https://www.all-stateind.com/contact/locations/); Specific Elk Grove section pairs 2651 Carl Blvd with die cutting, water jet cutting, thermal bending and assembly. Page titled plastic/rubber manufacturing solutions, filed 326299, no transfer of another plant’s cast-polyurethane process. |

## Findings for controller correction/status review

These are surfaced findings, not quiet upgrade holds. No classification, address, or operating-status correction is applied here. Gilkey is the only reviewed exact-address page explicitly styling a federal-created manufacturing plant as a showroom/office; other holds are missing/ambiguous witnesses rather than proof of a creation error.

| Site | Finding | Own page |
|---|---|---|
| SITE-019018 | Exact address10160 Virginia Avenue, Chicago Ridge IL60415; own page labels Showroom and Office and describes window replacement. Manufacturing_plant classification needs correction review, not an upgrade. | [Source](https://www.gilkey.com/location/chicago-ridge-il/) |
| SITE-019009 | Own page lists320 Craig Place, Hillside IL60162, versus held320 Craig Road; Packaging label is not plant-specific manufacturing proof. | [Source](https://www.storopack.us/company/about-us/storopack-worldwide/) |
| SITE-018014 | Own page reports substantial fire at South Haven facility and disruption; no closure inference or status edit. | [Source](https://eastjordanplastics.com/blog/statement-regarding-our-south-haven-facility/) |

## Holds

Every hold names the settling evidence; failed routes never imply absence or closure. Discovery-only indexed text and supplier-manual leads were not admitted as evidence. Mauser's two Elk Grove streets and Lacks' several Kentwood plants require street-level activity binding. No global capabilities were silently transferred to all plants. Pactiv has no held parent link, so a presumed parent is not used. Pregis's2018 acquisition witness remains historical and a fresh plant-bound witness is requested; it does not establish present activity. L6 peer notes reinforced these rules: Dart's own distribution-center label over an older manufacturing hit, recorded Avantor parent for NuSil, and source-specific PDF vintages.

| Site | Settling fact |
|---|---|
| SITE-018000 | Kalamazoo address requires own plant-specific activity evidence; global injection-molding capabilities do not bind this street; root timed out. |
| SITE-018001 | Westland named on own survey and corporate news, but no raw-approved Westland-specific polymer-production witness; needs location/activity binding. |
| SITE-018002 | 3505 Kraft is Raleigh East in older supplier-manual lead; needs raw own statement of polymer activity at this street, distinct from nearby Lacks plants. |
| SITE-018003 | Own Gaylord toolmaker job describes tool-room work; old sealing-product release is 2012. Needs current or corroborable plant-specific polymer-production witness. |
| SITE-018005 | Leonard plant award lead does not establish this plant’s polymer process; needs explicit own city/activity witness. |
| SITE-018007 | Own Marysville acquisition article is 2018; current contact page alone does not establish plant activity. Needs fresher location-bound polymer-production evidence. |
| SITE-018008 | Gladwin requires raw own city/activity witness at1191 Wolfson Ct; discovery did not produce an approved plant-specific page. |
| SITE-018009 | Brockton Mold older supplier-manual label alone is not raw-verified polymer production; needs own city/activity binding at4251 Brockton Ct. |
| SITE-018010 | Vicksburg needs own plant-specific activity binding; company-wide molding capabilities and older location-list leads do not establish this plant. |
| SITE-018014 | Own South Haven page reports substantial fire and disruption. Need dated recovery/operations evidence and identity binding; fire is not closure proof. |
| SITE-018015 | 5801 Kraft needs own plant-specific activity evidence; cannot inherit nearby Kraft Plater or other Lacks facilities’ processes. |
| SITE-018016 | ADS locator mixes plants/yards/distribution centers; needs own Clifford-specific polymer-production witness, not company-wide pipe capabilities. |
| SITE-018017 | ADS locator mixes plants/yards/distribution centers; needs own Owosso-specific polymer-production witness, not company-wide pipe capabilities. |
| SITE-018018 | Chesterfield specific page has useful indexed text but fresh curl500/Jina401; needs retrievable primary city/activity evidence, failed fetch is not absence. |
| SITE-018019 | Port Huron page/contact routes failed fresh retrieval; older history is insufficient for selected promotion. Needs raw own plant-city/activity witness. |
| SITE-019000 | Pactiv Bedford Park needs own operator-bound city/activity witness; no held parent relationship permits substituting a presumed parent page. |
| SITE-019002 | Pactiv Manteno needs own operator-bound city/activity witness; no held parent relationship permits substituting a presumed parent page. |
| SITE-019003 | Recorded Amcor parent permits B-PARENT, but Aurora IL raw job page lacks plant-specific polymer-production text; exclude Aurora OH jobs. |
| SITE-019004 | Plasticade Des Plaines address/product-catalog lead alone does not establish polymer manufacturing at100 Howard; needs city/activity bound own witness. |
| SITE-019008 | Trelleborg Streamwood process text is indexed, but all tried specific page routes raw404. Needs retrievable own city/activity witness under recorded parent. |
| SITE-019009 | Own Hillside page says320 Craig Place; held filing says320 Craig Road. Also only Packaging label, no local manufacturing process. Reconcile street and activity. |
| SITE-019010 | Own Addison location lists325 South Lombard Road but global manufacturing wording does not specify polymer work there. Needs local process witness. |
| SITE-019011 | Jacksonville East job route404; needs own location-bound polymer-production witness at2226 East Morton, distinct from any other Jacksonville operation. |
| SITE-019012 | Recorded Amcor parent permits B-PARENT; Alsip job fetch failed and generic packaging language does not establish local polymer process. Needs raw plant witness. |
| SITE-019014 | Own Mauser locator names Arthur and Lively streets in Elk Grove. Small Packaging label/city-only product manufacture cannot allocate process to Arthur; needs street binding. |
| SITE-019018 | Possible creation error: exact own address is styled Showroom/Office and local page describes replacement/installations. Needs direct evidence manufacturing occurs there; controller correction pass. |
| SITE-019019 | Kankakee coating-site and lab leads do not independently bind polymer production to901 North Greenwood. Needs raw own plant city/activity witness. |

## Counts and checks

Counts are establishments with countryUS, statusactive/unknown, tierA/B/C and primaryNAICS326. The QCEW denominator is2023 private establishments in NAICS326; ratios are counts versus a benchmark, not matched coverage.

| State | Strict sites before | After | QCEW | Before/after ratio |
|---|---:|---:|---:|---:|
| MI | 138 | 138 | 819 | 16.8498% → 16.8498% |
| IL | 85 | 85 | 797 | 10.6650% → 10.6650% |

- `python3 tasks/mi-il-site-quality-2026-11-06/check.py` — PASS:35 verdicts=8VERIFIED+27STILL_UNCERTAIN;8 B promotions/40 observations; three known answers (Spiratex Monroe extrusion, Pretium Aurora manufacturing, Gilkey showroom), raw/hash/identity checks, complete original evidence preservation, byte-identical replay. Missing own scope, altered frozen hash, invented city and cross-shard EVD collision all refuse before data writes. The empty evidence_people shard initially exposed a test-fixture header assumption; fixed using the actual CSV header and rerun successfully.
- `python3 scripts/validate.py` —0errors; existing warnings only. No scripts/ changes, so no full scripts pytest.
- Initial application/replay against current mainc267471. Exact fresh-main shard copies plus builder are required on rebase, never hand-merged CSVs.

Raw cache is local at `build/l11-quality-cache/frozen/`; short quotes and hash/route receipts ship, full pages do not. Existing house HTML extractor and calibrated on_page matcher are reused unchanged. `fetches.json` and `extra-fetches.json` preserve route availability separately from judgments; PDF requests/pdftotext receipts are in selected/rawcheck CSVs. Approximate six-route cap per organization respected, no FRS REST or licensed content used.

## Independent refutes

Codex and Grok deep adversarial clerk reviews pending. No Done/merge/approval claim. Limits: no fresh federal bulk download under the explicit packet-vintage exception; no current operating-status adjudication or full scripts test suite. Raw word presence alone is not semantic support, hence the complete source census is requested from both clerks.
