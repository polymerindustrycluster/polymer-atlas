# PIC-18 market scale, batch 2 of 2, 2026-11-18: 35 of 100 organizations' `markets_served` filled (66 values), 65 held

Claim: atlas-w18-mktscale (controller thr_9i2c6byhcz). First user: the Atlas owner, for prospecting by market; non-use is a finding if no prospecting list uses `markets_served` by 2026-12-16. No issue closed. Family review is pending. Batch 1 merged as #390 (dd07afc9).

## Frame, unit and filter

Unit: PIC-18 organization rows. The 191-organization market-scale frame (`frame.py`, the canary's pool definition recomputed from git at `e1df30e4`, minus the canary's 10; asserted and recomputed a second way by `check.py`) is split by organization ID: batch 1 the first 96, batch 2 the other **95** (ORG-001514 to ORG-004022: tiers A 32, B 47, C 16, U 0). Plus **5 batch-1 `list_item_only` holds re-screened** under the controller ruling that a content-page markets-served list on the organization's own page is supports_A (the merged MKT3 precedent). Frame = 100 organizations. `check.py` fails on any frame count or identity change.

Reading basis (`read_basis`): every stored text page of every organization was run through a sentence screen (lines re-joined), a keyword-window pass over the section 3.3 vocabulary and customer words, a plastics/rubber/molder window, and a second pass for the batch-1 review rules (customer lists, "for the X industries" sentences, own products marketed to a market); the matched passages were read. `page_read` (44) means the candidate page itself was opened and read; `text_screened` (56) means matched passages were read, not every page in full. A hold is "no claim found by the screen", never a finding of absence.

Batch-1 review rules carried over: no `furniture_office` from a bare "furniture" (JB Jewitt's value was dropped for it); `check.py` derives every applied evidence row (all 11 fields, SHA256 recomputed from the stored page) from `inputs.csv` and the stored page, never from the editable packet; an own "industries" sentence counts (C4 Polymers, Covia); the full sentence is read past its first clause; a company's own product marketed to a market counts; a named customer on the company's own customer list counts; consecutive evidence ID groups are listed separately; organizations, URLs, passages and values are counted separately.

## Result

**35 of 100 filled (35%); 95% Wilson interval 26% to 45%.** Counts, separately: **35 organizations, 37 distinct witness URLs, 41 distinct quoted passages, 66 values** (one controlled tag and one evidence row each). Tiers applied: A 9, B 21, C 5. 33 organizations from stored pages, 2 (ICS Laboratories, Comdess) only after a live fetch of an own-site page linked from a stored page (rule 14). Batch 1 was 25 of 96 (26%).

## Verdicts and terms (every quote a narrative sentence or a content-page markets list, supports_A; no tier U record applied)

| Organization (tier) | `markets_served` | Evidence (EVD- numbers) | Source and quote |
|---|---|---|---|
| ORG-000075 Industrial Mold & Machine (B) (re-screened) | consumer_goods_housewares; medical_healthcare_general; appliances; general_industrial; toys_sporting_goods; automotive_unspecified; electronics_electrical | 397300-397306 | industrialmold.com/capabilities.html: "Serving Many Markets •Medical •Household Appliance •Industrial •Toys •Automotive •Electronics •Packaging •Beverage •Consumer Products •Transportation •Electrical •Housewares" |
| ORG-001514 Julius Zorn, Inc. (Juzo USA) (B) | medical_healthcare_general | 397307 | juzousa.com/: "Juzo designs all our medical compression garments to improve your life, not inhibit it." |
| ORG-001523 Centerline Biomedical, Inc. (B) | medical_device | 397366 | centerlinebiomedical.com/about.html: "The company’s commercially available IOPS® (Intra-Operative Positioning System) technology platform is designed to enhance visualization and provide three-dimensional navigation to suppor..." |
| ORG-001524 Kapp Surgical, Inc. (B) | medical_device | 397308 | kappsurgical.com/about-us/: "Kapp Surgical, Inc. is a world leading manufacturer of custom designed stainless steel surgical instruments and implants." |
| ORG-001538 Perma Laboratories LLC (B) | dental | 397364 | perma-laboratories.com/: "Since 1986, we have offered our long-lasting Perma Soft Denture Reline Kit that's available for Denture Wearers in need of a Denture Reliner." |
| ORG-001546 Earthwalk Orthotics Acquisition Company LLC (Earthwalk Orthotics) (A) | medical_device | 397309 | www.earthwalkorthotics.com/about-us: "Our staff of experienced craftsmen combine high-tech digital software, high-quality materials, and decades of experience to create a premium medical device for your patients." |
| ORG-001548 Frantz Medical Development Ltd. (Frantz Medical Group) (B) | medical_device | 397354 | frantzgroup.com/fmd-product-design/: "Frantz Medical Development Product Design Research, Engineering and Manufacturing FMG’s manufacturing capabilities include high-volume injection molding, assembly, inspection, and packagi..." |
| ORG-001551 Volk Optical Inc. (A) | medical_healthcare_general | 397368 | www.volk.com/pages/about-us-1: "Our products are designed to enhance visualization and imaging, enabling doctors to effectively screen, diagnose, and treat eye disease, ultimately making quality eye care accessible to e..." |
| ORG-001555 Synapse Biomedical Inc. (B) | medical_device | 397367 | synapsebiomedical.com/: "Our FDA approved NeuRx DPS ® is specifically designed to decrease the reliance on mechanical ventilators for patients with spinal cord injuries." |
| ORG-001557 MatPLUS, LTD (B) | medical_healthcare_general | 397311 | matplusinc.com/: "MP Foam™️ materials are widely used in orthotics and prosthetics and a variety of medical and health care applications." |
| ORG-001570 GHSP (B) | automotive_unspecified | 397312 | www.ghsp.com/about/: "GHSP is an experienced supplier for the automotive and vehicle industry that provides advanced electronic controls and mechatronic systems." |
| ORG-001598 J B Jewitt Co Inc (B) | aerospace_defense | 397313 | homesteadfinishingproducts.com/about-us/: "We are the originator of TransTint® Dyes, which are sold world-wide for furniture applications as well as other diverse applications such as musical instruments, aerospace, and flooring." |
| ORG-001655 C4 Polymers Inc (B) | plastics_rubber_processors | 397314 | c4poly.com/about-us: "Founded in 1996 by Eric Smith, C4 Polymers has delivered world-class services to the plastics industry," |
| ORG-001657 Comdess Company Inc (B) | agriculture; general_industrial; medical_healthcare_general; marine; aerospace_defense; food_processing_foodservice | 397348-397353 | comdess.com/index.php/content/application-areas: "Application Areas Recreational Industrial Agriculture Safety Food Service Storage Containers Medical Marine Material Handling Tanks Military Insulation Metal Conversion" |
| ORG-001671 FastForming.com LLC (A) | aerospace_defense; automotive_unspecified; marine; medical_healthcare_general | 397315-397318 | fastforming.com/: "Fast Forming is known for precision die-cutting and producing high-quality die-cut plastic materials for the aerospace, automotive, marine, robotic, tool, and healthcare industries." |
| ORG-001691 Mike Cindia Sales Inc (C) | plastics_rubber_processors | 397319 | mcsiengineering.com/: "In 1982, Mike Cindia decided to apply his experience as a Plastic Process Engineer and Plant Manager to sell manufacturing equipment to the plastics industry." |
| ORG-001701 Cru Performance Coatings LLC (B) | automotive_oem; lawn_garden_recreation; industrial_machinery | 397321 and 397356-397357 | www.continentalpaints.com/industrialcoatings: "INDUSTRIES SERVED Tier 1 Automotive Suppliers Truck, Bus & Equipment OEM OEM Compressor Manufacturers Radiator Manufacturers Machine Manufacturers Metal Cabinetry Lawn & Garden Equipment ..." |
| ORG-001702 J T Adams Company (C) | aerospace_defense; automotive_unspecified; medical_healthcare_general | 397322-397324 | tensiletestinginc.com/: "Industries Served: Aerospace, Automotive, and Nuclear are the main industries we serve but there are many more Forgings, Foundries, Heat Treat, Medical, Plating, Steel Warehouses, Tubes /..." |
| ORG-001714 AML Industries, Inc. (B) | chemical_mining_metals_processing | 397365 | amlube.com/about-us/: "we supply our proprietary AMLUBE products to customers engaged in metal forging, extrusion, piercing and other metalforming activities throughout the world." |
| ORG-001720 Sun Art Decals, Inc. (A) | agriculture; industrial_machinery | 397325 and 397363 | sunartdecals.com/industrial-equipment-decals.html: "Agricultural Equipment Weather-resistant decals for tractors, combines, sprayers, and agricultural machinery operating in extreme outdoor conditions." (+1 more quoted passage) |
| ORG-001728 Buckeye Medical Technologies LLC (B) | dental | 397326 | www.anatotemp.com/: "By using the AnatotempSC system, implant surgeons are able to create an effortless restorative process for their restorative dentists and lab technicians." |
| ORG-001730 3D Dental Designs and Development LLC (B) | dental | 397327 | 3d-dent.com/: "3D Dental Designs & Development was launched with the vision and determination to bring a unique value proposition to the dental industry." |
| ORG-001739 API II, Inc. (A) | automotive_unspecified; consumer_goods_housewares; medical_healthcare_general; general_industrial | 397328-397330 and 397361 | www.api2.net/: "API II is a reliable supplier of plastic resin used in the manufacturing of industrial and automotive parts, containers for housewares, medical, and the general consumer needs." |
| ORG-001740 Auto Technology Company (C) | automotive_oem; aerospace_defense; electronics_electrical; water_wastewater | 397332-397333 and 397355 and 397358 | autotechnology.com/: "Automotive & Transportation OEM corrosion qualification and supplier testing for components, fasteners, coated parts, and assemblies" (+3 more quoted passages) |
| ORG-001749 Standards Testing Laboratories, Inc. (C) | tire_rubber_goods | 397334 | www.stllabs.com/: "STL can accommodate almost any tire or wheel test requirement" |
| ORG-001755 Medina Recycling Inc. (A) | plastics_rubber_processors | 397335 | www.medinarecycling.com/: "From printers and box shops, to plastic molders and manufacturers, Medina Recycling specializes in custom recycling programs of all sizes." |
| ORG-001783 Beacon Gasket & Seals Co (A) | marine; general_industrial | 397336 and 397362 | www.beacongasket.com/sealing-products/: "With a wide variety of high temperature products and custom fabrications for Industrial and Marine applications," |
| ORG-001869 Pro-Line Automation Systems Ltd. (A) | construction_building_products | 397337 | www.prolineautomation.com/about-us/: "Focused on vinyl and aluminum building products, our machines help window and door manufacturers around the world to streamline production, improve quality, and stay competitive." |
| ORG-001908 Tremco CPG Inc. (B) | construction_building_products | 397338 | tremcocpg.com/markets-we-serve: "For commercial architects, contractors, buildings owners and facility managers, Tremco CPG companies offer a wide range of building materials for the in-field or off-site construction of ..." |
| ORG-001928 Green Processing Company Inc (A) | automotive_unspecified | 397339 | green-processing.com/: "GPC maintains a substantial inventory of bulk containers (both plastic and metal), as well as plastic totes, trays, and lids used in the automotive industry." |
| ORG-001958 ICS Laboratories Inc (B) | toys_sporting_goods; aerospace_defense; medical_healthcare_general | 397347 and 397359-397360 | www.icslabs.com/industriesserved/sporting-goods/: "ICS Laboratories tests a variety of sporting goods, including protective eyewear, athletic helmets and headgear, body padding and gloves." (+2 more quoted passages) |
| ORG-002068 Chemstress Consultant Company (B) | chemical_mining_metals_processing | 397340 | www.chemstress.com/about/: "Chemstress can provide engineering, design, and construction solutions across various markets, serving some of the world’s largest chemical and other manufacturing companies across the co..." |
| ORG-002948 Covia Holdings LLC (B) | general_industrial | 397341 | www.coviacorp.com/about-us/: "Our main role in that partnership is to provide a broad array of high-quality minerals and material solutions for the industrial markets" |
| ORG-003545 G-3 Chickadee Purchaser, LLC (C) | tire_rubber_goods; toys_sporting_goods; medical_healthcare_general | 397342-397344 | www.g-3chickadee.com/about-us: "Today, the company possesses an industry-leading polymer technology and engineered solution portfolio that serves Goodyear and the world’s other top tire manufacturers, as well as preemin..." |
| ORG-003576 Micro-Poise Measurement Systems, LLC (B) | tire_rubber_goods; automotive_unspecified | 397345-397346 | www.micropoise.com/about-us/about-us: "Markets include all final finish test and measurement solutions for tire manufactures, tire & wheel assembly solutions and drivetrain balancing solutions for automotive manufacturers." |

Term notes. Each tag needs its own wording in its quote (`WORDS` in `check.py`). `medical_device` is by the page's own words ("medical device", "implants", "medical devices"). `dental` for Anatotemp's "restorative dentists" and 3D Dental's "dental industry". Industrial Mold & Machine's list ("Serving Many Markets" bullets) is applied under the content-page-list ruling for the seven terms its words name (Medical, Household Appliance, Industrial, Toys, Automotive, Electronics/Electrical, Housewares); "Packaging", "Beverage", "Transportation" and "Consumer Products" are not tagged (no single section 3.3 term matches). CPC's "Industries Served" list yields `automotive_oem` ("Tier 1 Automotive Suppliers"), `lawn_garden_recreation` and `industrial_machinery` ("Machine Manufacturers").

Live-sourced: ICS Laboratories' Sporting Goods page ("tests a variety of sporting goods, including ...") and Comdess' Application Areas page, a content-page list (Industrial, Agriculture, Food Service, Medical, Marine, Military) applied under the same ruling; ICS' Defense & Tactical page ("United States Armed Forces") yields `aerospace_defense` and its Emergency Response page ("frontline medical staff") yields `medical_healthcare_general` after Codex round 2; Recreation & Leisure has no matching term.

## Review rounds on #396 (12 findings: Gemini 1, Codex 11; each fixed or rebutted)

Evidence IDs were re-allocated by the controller's decision (the decision recorded EVD-397103 as main's maximum at that time and open PRs up to 397200; the maximum at this PR's merge-base `c8ce2d4a` is EVD-397200, recomputed by `check.py`, and every new ID is above it): commit A renumbered the 54 existing rows to EVD-397300 to 397353 with `build.py --renumber` (never sed; for the five data and packet files, the two evidence shards and the three packet tables, a diff against 11b63972 with the IDs masked is empty; 54 renumbered of 54 matched; no old ID remains in the task folder. Commit A also changed `build.py` (the `renumber` function, its CLI and the new block constants) and this README, which are not covered by the masked-diff claim). Commit B holds the content and tooling fixes, with new rows from EVD-397354.

| # | Finding | Call |
|---|---|---|
| G1 | `automotive_unspecified` where the words say OEM or Tier 1 (Auto Technology, Cru) | Fixed: both values re-allocated as `automotive_oem` (EVD-397331 and EVD-397320 retired); `automotive_oem` added to `WORDS`; `check.py` now fails an `automotive_unspecified` row whose quote says OEM or Tier 1 (injection added). Re-check of the other seven `automotive_unspecified` rows (IMM, GHSP, Tensile Testing, API II, Green Processing, FastForming, Micro-Poise): none says OEM or Tier 1; Micro-Poise's "automotive manufacturers" does not say OEM or aftermarket either, so it stays `automotive_unspecified` (rebutted as a words call: a maker of automobiles or of automotive parts is not stated) |
| C1 | Frantz cites the group page | Fixed: re-sourced to the FMD Product Design page, which places the claim under Frantz Medical Development Product Design; EVD-397310 retired |
| C2 | ICS omits two markets | Fixed: `aerospace_defense` (Defense & Tactical page: "contributes to the United States Armed Forces' Soldier Protective Equipment Process", `armed forces` added to the wording map) and `medical_healthcare_general` (Emergency Response page: "PPE products used by frontline medical staff") |
| C3 | Auto Technology omits water_wastewater | Fixed: "Water & Wastewater Infrastructure ... drinking-water and wastewater systems" card |
| C4 | API II and Beacon omit `general_industrial` | Fixed: same sentences, "industrial and automotive parts" and "Industrial and Marine applications" |
| C5 | Cru and Sun Art omit `industrial_machinery` | Fixed: Cru's "Machine Manufacturers" and Sun Art's "Manufacturing Machinery ... production equipment" |
| C6 | Perma Laboratories false hold for dental | Fixed: "we have offered our long-lasting Perma Soft Denture Reline Kit that's available for Denture Wearers"; own product marketed to a market (rule 5) |
| C7 | AML omits metals processing | Fixed: "customers engaged in metal forging, extrusion, piercing and other metalforming activities" |
| C8 | Centerline, Synapse, Volk false holds | Fixed: Centerline and Synapse `medical_device` by meaning (commercially available IOPS system "to support physicians during procedures"; "Our FDA approved NeuRx DPS ... for patients with spinal cord injuries"); Volk `medical_healthcare_general` ("enabling doctors to effectively screen, diagnose, and treat eye disease"). Myrava stays held (record note) |
| C9 | Pre-application backups are batch 1's | Fixed: backups are per batch (`pre-application-batch2`), taken at this batch's own base |
| C10 | A cell can publish without its evidence | Fixed: evidence shards are replaced before organization shards; the check interrupts at every replacement position and asserts that no filled cell lacks its rows and that a retry reproduces the shards |
| C11 | Frame verifier ignores each re-screen's prior class | Fixed: the re-screen set must equal batch 1's `list_item_only` holds exactly (batch 1's `verdicts.csv`); the substitution injection is refused |

Also new in `check.py`: the lowest new evidence ID must exceed the maximum evidence ID at the merge-base.

Report-only (no change in this PR): merged batch-1 (#390) rows with `automotive_unspecified` on words that say OEM or Tier 1: none. Its three `automotive_unspecified` rows are EVD-396604 (Laird, "automotive" in an industries list), EVD-396630 (Silicone Solutions, "automotive" in a market-areas sentence) and EVD-396636 (ABC Technologies, "for the global automotive industry"); none of the three quotes says OEM or Tier 1 (ABC's page names a Tier 1 supplier in a different sentence about the combined business).

## Re-screen of batch 1 list holds

| Organization | Outcome under the content-page-list precedent |
|---|---|
| ORG-000075 Industrial Mold & Machine | applied |
| ORG-000229 American Molded Plastic, Inc. | held (list_item_only) |
| ORG-000322 ECP Corp dba Polycase | held (list_item_only) |
| ORG-000378 Infinity Composites Inc. | held (list_item_only) |
| ORG-001065 R & S Technologies, Inc. | held (list_item_only) |

The other four stay held: their text is a product list or a product-link list, not a markets-served list (settling facts in `verdicts.csv`).

## Holds (65 organizations, `STILL_UNCERTAIN`; settling facts in `verdicts.csv`; none is a finding of absence)

| Reason | Organizations | IDs |
|---|---|---|
| no_market_claim | 38 | ORG-001525, ORG-001579, ORG-001580, ORG-001591, ORG-001592, ORG-001596, ORG-001624, ORG-001635, ORG-001639, ORG-001641, ORG-001642, ORG-001656, ORG-001670, ORG-001708, ORG-001709, ORG-001742, ORG-001776, ORG-001787, ORG-001788, ORG-001793, ORG-001829, ORG-001836, ORG-001911, ORG-001916, ORG-001936, ORG-001956, ORG-001963, ORG-001986, ORG-001999, ORG-002010, ORG-002018, ORG-002030, ORG-002053, ORG-002056, ORG-002067, ORG-002134, ORG-002137, ORG-002922 |
| group_or_redirect_attribution | 7 | ORG-001534, ORG-001949, ORG-002038, ORG-002047, ORG-003196, ORG-003771, ORG-004022 |
| off_vocabulary_or_ambiguous_market | 7 | ORG-001573, ORG-001603, ORG-001700, ORG-001745, ORG-001780, ORG-001922, ORG-001959 |
| list_item_only | 7 | ORG-001682, ORG-001779, ORG-001784, ORG-000229, ORG-000322, ORG-000378, ORG-001065 |
| no_vocab_market | 3 | ORG-001595, ORG-001636, ORG-001927 |
| menu_or_nav_only | 2 | ORG-001607, ORG-001883 |
| scope_owner_ruling | 1 | ORG-001558 |

`group_or_redirect_attribution`: subsidiary or division records whose only website is the group site stay held (controller is taking the question to the owner). `scope_owner_ruling`: Myrava (ORG-001558), whose record note says "do not promote above C without own-site check"; the own site does say "FDA-cleared, patient-specific medical devices". Two records (Raydar, Sherwood) have a domain-parking or for-sale page as their website.

## Writes (rule 13) and outcome check

- Only `markets_served` changes, on 35 organization rows, each blank at base: `data/organizations_OH.csv` and `data/organizations_TX.csv`. 66 evidence rows appended to the matching `evidence_organizations_*.csv`, IDs EVD-397300 to EVD-397368 of the block 397300-397449 (controller re-allocation 2026-11-18; the decision recorded main's maximum as EVD-397103 and open PRs up to 397200; the maximum at the merge-base `c8ce2d4a` is EVD-397200) (66 IDs in use; 3 retired: EVD-397310, EVD-397320, EVD-397331; `withdrawn.csv`), pinned in `selection.tsv` and allocated with `scripts/shard_io.py` `append_sorted`. `check.py` compares every data file with base: nothing else changes.
- Outcome: `python3 S/harness/pic18_unknown.py "$PWD" <ref>` (unit: PIC-18 organization rows, 794). At merge-base `c8ce2d4a`: `mkt_unknown=354`. At HEAD: `mkt_unknown=319`. **It fell by exactly 35, the number of organizations applied.** `proc_unknown` (331) and `band_unknown` (443) unchanged.

## Self-refute (rule 15)

- self-refute: grain — 35 organizations checked, 0 changed. The 35 organizations, 37 distinct witness URLs, 41 distinct quoted passages and 66 values all sit on the organization's own site and are organization-grain. Group-site records (Zimmer Surgical, Eckart, ST BlowMoulding, VMI, Wayne-Dalton, Akron Steel Fabricators, Pinnacle Recycling) were held. Micro-Poise is an AMETEK business unit but micropoise.com is its own site and the record's website (its witness is a reader-route page, so the DOM nav check cannot run; the sentence is body prose).
- self-refute: founding — 0 rows checked (no founding or age value written), 0 changed. Kapp Surgical's "since 1927", Juzo's "since 1912" and Tremco's history were not used.
- self-refute: strength — 35 organizations checked, 6 changed. Held rather than written: Covia's Building & Construction text (the DOM check marks it all menu chrome), Rezkem's hero-slider sentence, Speedline's H1 tagline, Frantz's hero-block sentence (replaced by its body sentence "We have developed ... patented medical devices"), Kinetico's navigation card, ICS Laboratories' home-page menu (the organization was later applied from its fetched content pages). Rule used once: a complete sentence in a list element, card or sub-heading is supports_A; a bare label, link text or tile heading is supports_C; a content-page markets-served list is supports_A (controller ruling, applied to Industrial Mold & Machine, CPC and Auto Technology's industry cards). `check.py` runs `witness_class.nav_only` on every witness.
- self-refute: truncated quote — 66 values checked, 2 changed. Sun Art Decals' quote was extended from "...operating in" to the sentence end; Frantz's quote moved to the body sentence and ends at "in the fields of:" (the claim words "patented medical devices" are inside); GHSP, Kapp and Earthwalk quotes were checked to end at sentence ends.
- self-refute: attribution — 100 organizations checked, 5 changed. Eagle Plastics' "partnered with top medical, automotive, and household brands" is the founders' earlier employment, not the company's customers (held); Synapse Biomedical's "medical devices" sentence is about NOCI, a separate Canadian distributor (held); ELC's named customers (Blockbuster, Dunkin') are its printers' customers, not its own (held); API II's resin sentence was read under the Alterra rule (written only for the industries its sentence names); Poling's page names Akron Steel Fabricators only in a merger notice (held); Pinnacle Recycling's stored pages are Rumpke's (held).

## Live fetches (rule 14)

6 fetches, all of URLs linked from a stored page (`fetches.csv` records the linking page), through the shared `scripts/site_corpus.py` (robots-aware), cached under `S/persist/pic18-market-scale-2026-11-18/` with sha256: ICS Laboratories 5 (one failed: the Construction, Manufacturing and General Industry page returned FETCH_FAILED, an availability signal, not absence), Comdess 1. Result: 2 applies. The link discovery ran over every `no_market_claim`, `menu_or_nav_only`, `list_item_only` and ambiguous hold; the other candidates (Kinetico consumer pages, Certon's adhesive-application pages, catalog categories, application-for-employment pages) were not fetched because their link text named products or forms, not markets.

## Named checks

- `python3 tasks/pic18-market-scale-2-2026-11-18/check.py`: PASS with the boundary check; fails on every batch-1 injection (the canary's 17, frame count and identity changes, group-domain witness, source-domain mismatch, do-not-promote and carbon records, tier effect, read basis, falsified evidence provenance in the shard and the packet) plus the batch-2 frame rule (the 5 re-screened organizations must be batch-1 frame organizations). `withdrawn.csv` lists the 3 retired IDs (EVD-397310, EVD-397320, EVD-397331), so the retired-ID injection runs. Round 3 adds: backups are written from `git show <merge-base>:<file>` into a directory named for the merge-base SHA (`pre-application-batch2-c8ce2d4a`), each file's sha256 is recorded against the git blob in `SHA256SUMS.json` and verified before an existing backup is trusted (a stale-base backup or a 128-byte truncated backup is rewritten; both probes are tests), and they are taken only after every input check has passed; the interruption test counts canonical destination writes only and a write-order injection (an organization shard before its own evidence shard) must be detected; `build.py --renumber` is idempotent by refusal (a replay, whose source IDs are already inside the allocated block, is refused and the file is unchanged, tested).
- `build.py` is idempotent (`--packet-only` builds the CSVs without writing `data/`). `scripts/validate.py` 0 errors; `check_row_loss.py --base origin/main`, `export_vocab.py --check` and `python3 -m unittest discover -s scripts -p 'test_*.py'`: see the PR description.
- Reuse: batch 1's `build.py`, `check.py`, `fetch.py`, `frame.py` (final #390 versions) with the batch parameters changed.

## Not checked

Family review. Holds were screened, not read page by page. `mkt3_reach` stays dropped for the reason given in batch 1's README. Linked-page discovery was applied to holds only (see live fetches). No site-level markets.

## Proposed follow-ups (not in this PR)

- Subsidiary and division records on a group site (Zimmer Surgical, Eckart, ST BlowMoulding, VMI Holland, Wayne-Dalton, Akron Steel Fabricators) stay held; the controller takes the question to the owner.
- Myrava (ORG-001558): a ruling that a tier-cap note ("do not promote above C") does not bar a markets cell written from an own-site sentence.
- Centerline Biomedical and Synapse Biomedical (`medical_device`) and Volk Optical (`medical_healthcare_general`) were applied in commit cbb32cb3 (round 2) by the meaning of their own product-and-user sentences; only PRC-Saltillo (speech-generating AAC devices; "medical device" is never stated) remains held. A ruling on by-meaning device terms would decide that one hold and confirm the three applies.
- Raydar of Ohio and Sherwood Advanced Composite Technologies: the record website serves a parked or for-sale page; a website correction is another lane's.
