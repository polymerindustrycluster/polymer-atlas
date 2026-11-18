# PIC-18 market scale, batch 2 of 2, 2026-11-18: 30 of 100 organizations' `markets_served` filled (54 values), 70 held

Claim: atlas-w18-mktscale (controller thr_9i2c6byhcz). First user: the Atlas owner, for prospecting by market; non-use is a finding if no prospecting list uses `markets_served` by 2026-12-16. No issue closed. Family review is pending. Batch 1 merged as #390 (dd07afc9).

## Frame, unit and filter

Unit: PIC-18 organization rows. The 191-organization market-scale frame (`frame.py`, the canary's pool definition recomputed from git at `e1df30e4`, minus the canary's 10; asserted and recomputed a second way by `check.py`) is split by organization ID: batch 1 the first 96, batch 2 the other **95** (ORG-001514 to ORG-004022: tiers A 32, B 47, C 16, U 0). Plus **5 batch-1 `list_item_only` holds re-screened** under the controller ruling that a content-page markets-served list on the organization's own page is supports_A (the merged MKT3 precedent). Frame = 100 organizations. `check.py` fails on any frame count or identity change.

Reading basis (`read_basis`): every stored text page of every organization was run through a sentence screen (lines re-joined), a keyword-window pass over the section 3.3 vocabulary and customer words, a plastics/rubber/molder window, and a second pass for the batch-1 review rules (customer lists, "for the X industries" sentences, own products marketed to a market); the matched passages were read. `page_read` (39) means the candidate page itself was opened and read; `text_screened` (61) means matched passages were read, not every page in full. A hold is "no claim found by the screen", never a finding of absence.

Batch-1 review rules carried over: no `furniture_office` from a bare "furniture" (JB Jewitt's value was dropped for it); `check.py` derives every applied evidence row (all 11 fields, SHA256 recomputed from the stored page) from `inputs.csv` and the stored page, never from the editable packet; an own "industries" sentence counts (C4 Polymers, Covia); the full sentence is read past its first clause; a company's own product marketed to a market counts; a named customer on the company's own customer list counts; consecutive evidence ID groups are listed separately; organizations, URLs, passages and values are counted separately.

## Result

**30 of 100 filled (30%); 95% Wilson interval 22% to 40%.** Counts, separately: **30 organizations, 30 distinct witness URLs, 32 distinct quoted passages, 54 values** (one controlled tag and one evidence row each). Tiers applied: A 8, B 17, C 5. 28 organizations from stored pages, 2 (ICS Laboratories, Comdess) only after a live fetch of an own-site page linked from a stored page (rule 14). Batch 1 was 25 of 96 (26%).

## Verdicts and terms (every quote a narrative sentence or a content-page markets list, supports_A; no tier U record applied)

| Organization (tier) | `markets_served` | Evidence (EVD- numbers) | Source and quote |
|---|---|---|---|
| ORG-000075 Industrial Mold & Machine (B) (re-screened) | consumer_goods_housewares; medical_healthcare_general; appliances; general_industrial; toys_sporting_goods; automotive_unspecified; electronics_electrical | 396750-396756 | industrialmold.com/capabilities.html: "Serving Many Markets •Medical •Household Appliance •Industrial •Toys •Automotive •Electronics •Packaging •Beverage •Consumer Products •Transportation •Electrical •Housewares" |
| ORG-001514 Julius Zorn, Inc. (Juzo USA) (B) | medical_healthcare_general | 396757 | juzousa.com/: "Juzo designs all our medical compression garments to improve your life, not inhibit it." |
| ORG-001524 Kapp Surgical, Inc. (B) | medical_device | 396758 | kappsurgical.com/about-us/: "Kapp Surgical, Inc. is a world leading manufacturer of custom designed stainless steel surgical instruments and implants." |
| ORG-001546 Earthwalk Orthotics Acquisition Company LLC (Earthwalk Orthotics) (A) | medical_device | 396759 | www.earthwalkorthotics.com/about-us: "Our staff of experienced craftsmen combine high-tech digital software, high-quality materials, and decades of experience to create a premium medical device for your patients." |
| ORG-001548 Frantz Medical Development Ltd. (Frantz Medical Group) (B) | medical_device | 396760 | frantzgroup.com/: "We have developed a broad range of unique, patented medical devices in the fields of:" |
| ORG-001557 MatPLUS, LTD (B) | medical_healthcare_general | 396761 | matplusinc.com/: "MP Foam™️ materials are widely used in orthotics and prosthetics and a variety of medical and health care applications." |
| ORG-001570 GHSP (B) | automotive_unspecified | 396762 | www.ghsp.com/about/: "GHSP is an experienced supplier for the automotive and vehicle industry that provides advanced electronic controls and mechatronic systems." |
| ORG-001598 J B Jewitt Co Inc (B) | aerospace_defense | 396763 | homesteadfinishingproducts.com/about-us/: "We are the originator of TransTint® Dyes, which are sold world-wide for furniture applications as well as other diverse applications such as musical instruments, aerospace, and flooring." |
| ORG-001655 C4 Polymers Inc (B) | plastics_rubber_processors | 396764 | c4poly.com/about-us: "Founded in 1996 by Eric Smith, C4 Polymers has delivered world-class services to the plastics industry," |
| ORG-001657 Comdess Company Inc (B) | agriculture; general_industrial; medical_healthcare_general; marine; aerospace_defense; food_processing_foodservice | 396798-396803 | comdess.com/index.php/content/application-areas: "Application Areas Recreational Industrial Agriculture Safety Food Service Storage Containers Medical Marine Material Handling Tanks Military Insulation Metal Conversion" |
| ORG-001671 FastForming.com LLC (A) | aerospace_defense; automotive_unspecified; marine; medical_healthcare_general | 396765-396768 | fastforming.com/: "Fast Forming is known for precision die-cutting and producing high-quality die-cut plastic materials for the aerospace, automotive, marine, robotic, tool, and healthcare industries." |
| ORG-001691 Mike Cindia Sales Inc (C) | plastics_rubber_processors | 396769 | mcsiengineering.com/: "In 1982, Mike Cindia decided to apply his experience as a Plastic Process Engineer and Plant Manager to sell manufacturing equipment to the plastics industry." |
| ORG-001701 Cru Performance Coatings LLC (B) | automotive_unspecified; lawn_garden_recreation | 396770-396771 | www.continentalpaints.com/industrialcoatings: "INDUSTRIES SERVED Tier 1 Automotive Suppliers Truck, Bus & Equipment OEM OEM Compressor Manufacturers Radiator Manufacturers Machine Manufacturers Metal Cabinetry Lawn & Garden Equipment ..." |
| ORG-001702 J T Adams Company (C) | aerospace_defense; automotive_unspecified; medical_healthcare_general | 396772-396774 | tensiletestinginc.com/: "Industries Served: Aerospace, Automotive, and Nuclear are the main industries we serve but there are many more Forgings, Foundries, Heat Treat, Medical, Plating, Steel Warehouses, Tubes /..." |
| ORG-001720 Sun Art Decals, Inc. (A) | agriculture | 396775 | sunartdecals.com/industrial-equipment-decals.html: "Agricultural Equipment Weather-resistant decals for tractors, combines, sprayers, and agricultural machinery operating in extreme outdoor conditions." |
| ORG-001728 Buckeye Medical Technologies LLC (B) | dental | 396776 | www.anatotemp.com/: "By using the AnatotempSC system, implant surgeons are able to create an effortless restorative process for their restorative dentists and lab technicians." |
| ORG-001730 3D Dental Designs and Development LLC (B) | dental | 396777 | 3d-dent.com/: "3D Dental Designs & Development was launched with the vision and determination to bring a unique value proposition to the dental industry." |
| ORG-001739 API II, Inc. (A) | automotive_unspecified; consumer_goods_housewares; medical_healthcare_general | 396778-396780 | www.api2.net/: "API II is a reliable supplier of plastic resin used in the manufacturing of industrial and automotive parts, containers for housewares, medical, and the general consumer needs." |
| ORG-001740 Auto Technology Company (C) | automotive_unspecified; aerospace_defense; electronics_electrical | 396781-396783 | autotechnology.com/: "Automotive & Transportation OEM corrosion qualification and supplier testing for components, fasteners, coated parts, and assemblies" (+2 more quoted passages) |
| ORG-001749 Standards Testing Laboratories, Inc. (C) | tire_rubber_goods | 396784 | www.stllabs.com/: "STL can accommodate almost any tire or wheel test requirement" |
| ORG-001755 Medina Recycling Inc. (A) | plastics_rubber_processors | 396785 | www.medinarecycling.com/: "From printers and box shops, to plastic molders and manufacturers, Medina Recycling specializes in custom recycling programs of all sizes." |
| ORG-001783 Beacon Gasket & Seals Co (A) | marine | 396786 | www.beacongasket.com/sealing-products/: "With a wide variety of high temperature products and custom fabrications for Industrial and Marine applications," |
| ORG-001869 Pro-Line Automation Systems Ltd. (A) | construction_building_products | 396787 | www.prolineautomation.com/about-us/: "Focused on vinyl and aluminum building products, our machines help window and door manufacturers around the world to streamline production, improve quality, and stay competitive." |
| ORG-001908 Tremco CPG Inc. (B) | construction_building_products | 396788 | tremcocpg.com/markets-we-serve: "For commercial architects, contractors, buildings owners and facility managers, Tremco CPG companies offer a wide range of building materials for the in-field or off-site construction of ..." |
| ORG-001928 Green Processing Company Inc (A) | automotive_unspecified | 396789 | green-processing.com/: "GPC maintains a substantial inventory of bulk containers (both plastic and metal), as well as plastic totes, trays, and lids used in the automotive industry." |
| ORG-001958 ICS Laboratories Inc (B) | toys_sporting_goods | 396797 | www.icslabs.com/industriesserved/sporting-goods/: "ICS Laboratories tests a variety of sporting goods, including protective eyewear, athletic helmets and headgear, body padding and gloves." |
| ORG-002068 Chemstress Consultant Company (B) | chemical_mining_metals_processing | 396790 | www.chemstress.com/about/: "Chemstress can provide engineering, design, and construction solutions across various markets, serving some of the world’s largest chemical and other manufacturing companies across the co..." |
| ORG-002948 Covia Holdings LLC (B) | general_industrial | 396791 | www.coviacorp.com/about-us/: "Our main role in that partnership is to provide a broad array of high-quality minerals and material solutions for the industrial markets" |
| ORG-003545 G-3 Chickadee Purchaser, LLC (C) | tire_rubber_goods; toys_sporting_goods; medical_healthcare_general | 396792-396794 | www.g-3chickadee.com/about-us: "Today, the company possesses an industry-leading polymer technology and engineered solution portfolio that serves Goodyear and the world’s other top tire manufacturers, as well as preemin..." |
| ORG-003576 Micro-Poise Measurement Systems, LLC (B) | tire_rubber_goods; automotive_unspecified | 396795-396796 | www.micropoise.com/about-us/about-us: "Markets include all final finish test and measurement solutions for tire manufactures, tire & wheel assembly solutions and drivetrain balancing solutions for automotive manufacturers." |

Term notes. Each tag needs its own wording in its quote (`WORDS` in `check.py`). `medical_device` is by the page's own words ("medical device", "implants", "medical devices"). `dental` for Anatotemp's "restorative dentists" and 3D Dental's "dental industry". Industrial Mold & Machine's list ("Serving Many Markets" bullets) is applied under the content-page-list ruling for the seven terms its words name (Medical, Household Appliance, Industrial, Toys, Automotive, Electronics/Electrical, Housewares); "Packaging", "Beverage", "Transportation" and "Consumer Products" are not tagged (no single section 3.3 term matches). CPC's "Industries Served" list yields automotive and lawn and garden only.

Live-sourced: ICS Laboratories' Sporting Goods page ("tests a variety of sporting goods, including ...") and Comdess' Application Areas page, a content-page list (Industrial, Agriculture, Food Service, Medical, Marine, Military) applied under the same ruling; ICS' Defense & Tactical page was not tagged (the sentence names the Armed Forces but not the words defense or military), nor were Recreation & Leisure or Emergency Response (no matching term).

## Re-screen of batch 1 list holds

| Organization | Outcome under the content-page-list precedent |
|---|---|
| ORG-000075 Industrial Mold & Machine | applied |
| ORG-000229 American Molded Plastic, Inc. | held (list_item_only) |
| ORG-000322 ECP Corp dba Polycase | held (list_item_only) |
| ORG-000378 Infinity Composites Inc. | held (list_item_only) |
| ORG-001065 R & S Technologies, Inc. | held (list_item_only) |

The other four stay held: their text is a product list or a product-link list, not a markets-served list (settling facts in `verdicts.csv`).

## Holds (70 organizations, `STILL_UNCERTAIN`; settling facts in `verdicts.csv`; none is a finding of absence)

| Reason | Organizations | IDs |
|---|---|---|
| no_market_claim | 38 | ORG-001525, ORG-001579, ORG-001580, ORG-001591, ORG-001592, ORG-001596, ORG-001624, ORG-001635, ORG-001639, ORG-001641, ORG-001642, ORG-001656, ORG-001670, ORG-001708, ORG-001709, ORG-001742, ORG-001776, ORG-001787, ORG-001788, ORG-001793, ORG-001829, ORG-001836, ORG-001911, ORG-001916, ORG-001936, ORG-001956, ORG-001963, ORG-001986, ORG-001999, ORG-002010, ORG-002018, ORG-002030, ORG-002053, ORG-002056, ORG-002067, ORG-002134, ORG-002137, ORG-002922 |
| off_vocabulary_or_ambiguous_market | 11 | ORG-001523, ORG-001551, ORG-001555, ORG-001573, ORG-001603, ORG-001700, ORG-001714, ORG-001745, ORG-001780, ORG-001922, ORG-001959 |
| group_or_redirect_attribution | 7 | ORG-001534, ORG-001949, ORG-002038, ORG-002047, ORG-003196, ORG-003771, ORG-004022 |
| list_item_only | 7 | ORG-001682, ORG-001779, ORG-001784, ORG-000229, ORG-000322, ORG-000378, ORG-001065 |
| no_vocab_market | 4 | ORG-001538, ORG-001595, ORG-001636, ORG-001927 |
| menu_or_nav_only | 2 | ORG-001607, ORG-001883 |
| scope_owner_ruling | 1 | ORG-001558 |

`group_or_redirect_attribution`: subsidiary or division records whose only website is the group site stay held (controller is taking the question to the owner). `scope_owner_ruling`: Myrava (ORG-001558), whose record note says "do not promote above C without own-site check"; the own site does say "FDA-cleared, patient-specific medical devices". Two records (Raydar, Sherwood) have a domain-parking or for-sale page as their website.

## Writes (rule 13) and outcome check

- Only `markets_served` changes, on 30 organization rows, each blank at base: `data/organizations_OH.csv` and `data/organizations_TX.csv`. 54 evidence rows appended to the matching `evidence_organizations_*.csv`, IDs EVD-396750 to EVD-396803 of the block 396750-396899 (consecutive, none retired), pinned in `selection.tsv` and allocated with `scripts/shard_io.py` `append_sorted`. `check.py` compares every data file with base: nothing else changes.
- Outcome: `python3 S/harness/pic18_unknown.py "$PWD" <ref>` (unit: PIC-18 organization rows, 794). At merge-base `dd07afc9`: `mkt_unknown=354`. At HEAD: `mkt_unknown=326`. **It fell by exactly 28, the number of organizations applied.** `proc_unknown` (331) and `band_unknown` (445) unchanged.

## Self-refute (rule 15)

- self-refute: grain — 30 organizations checked, 0 changed. The 30 organizations, 30 distinct witness URLs, 32 distinct quoted passages and 54 values all sit on the organization's own site and are organization-grain. Group-site records (Zimmer Surgical, Eckart, ST BlowMoulding, VMI, Wayne-Dalton, Akron Steel Fabricators, Pinnacle Recycling) were held. Micro-Poise is an AMETEK business unit but micropoise.com is its own site and the record's website (its witness is a reader-route page, so the DOM nav check cannot run; the sentence is body prose).
- self-refute: founding — 0 rows checked (no founding or age value written), 0 changed. Kapp Surgical's "since 1927", Juzo's "since 1912" and Tremco's history were not used.
- self-refute: strength — 30 organizations checked, 6 changed. Held rather than written: Covia's Building & Construction text (the DOM check marks it all menu chrome), Rezkem's hero-slider sentence, Speedline's H1 tagline, Frantz's hero-block sentence (replaced by its body sentence "We have developed ... patented medical devices"), Kinetico's navigation card, ICS Laboratories' menu. Rule used once: a complete sentence in a list element, card or sub-heading is supports_A; a bare label, link text or tile heading is supports_C; a content-page markets-served list is supports_A (controller ruling, applied to Industrial Mold & Machine, CPC and Auto Technology's industry cards). `check.py` runs `witness_class.nav_only` on every witness.
- self-refute: truncated quote — 54 values checked, 2 changed. Sun Art Decals' quote was extended from "...operating in" to the sentence end; Frantz's quote moved to the body sentence and ends at "in the fields of:" (the claim words "patented medical devices" are inside); GHSP, Kapp and Earthwalk quotes were checked to end at sentence ends.
- self-refute: attribution — 100 organizations checked, 5 changed. Eagle Plastics' "partnered with top medical, automotive, and household brands" is the founders' earlier employment, not the company's customers (held); Synapse Biomedical's "medical devices" sentence is about NOCI, a separate Canadian distributor (held); ELC's named customers (Blockbuster, Dunkin') are its printers' customers, not its own (held); API II's resin sentence was read under the Alterra rule (written only for the industries its sentence names); Poling's page names Akron Steel Fabricators only in a merger notice (held); Pinnacle Recycling's stored pages are Rumpke's (held).

## Live fetches (rule 14)

6 fetches, all of URLs linked from a stored page (`fetches.csv` records the linking page), through the shared `scripts/site_corpus.py` (robots-aware), cached under `S/persist/pic18-market-scale-2026-11-18/` with sha256: ICS Laboratories 5 (one failed: the Construction, Manufacturing and General Industry page returned FETCH_FAILED, an availability signal, not absence), Comdess 1. Result: 2 applies. The link discovery ran over every `no_market_claim`, `menu_or_nav_only`, `list_item_only` and ambiguous hold; the other candidates (Kinetico consumer pages, Certon's adhesive-application pages, catalog categories, application-for-employment pages) were not fetched because their link text named products or forms, not markets.

## Named checks

- `python3 tasks/pic18-market-scale-2-2026-11-18/check.py`: PASS with the boundary check; fails on every batch-1 injection (the canary's 17, frame count and identity changes, group-domain witness, source-domain mismatch, do-not-promote and carbon records, tier effect, read basis, falsified evidence provenance in the shard and the packet) plus the batch-2 frame rule (the 5 re-screened organizations must be batch-1 frame organizations). `withdrawn.csv` is empty (no retired IDs in this batch; the retired-ID injection runs only when a withdrawal exists).
- `build.py` is idempotent (`--packet-only` builds the CSVs without writing `data/`). `scripts/validate.py` 0 errors; `check_row_loss.py --base origin/main`, `export_vocab.py --check` and `python3 -m unittest discover -s scripts -p 'test_*.py'`: see the PR description.
- Reuse: batch 1's `build.py`, `check.py`, `fetch.py`, `frame.py` (final #390 versions) with the batch parameters changed.

## Not checked

Family review. Holds were screened, not read page by page. `mkt3_reach` stays dropped for the reason given in batch 1's README. Linked-page discovery was applied to holds only (see live fetches). No site-level markets.

## Proposed follow-ups (not in this PR)

- Subsidiary and division records on a group site (Zimmer Surgical, Eckart, ST BlowMoulding, VMI Holland, Wayne-Dalton, Akron Steel Fabricators) stay held; the controller takes the question to the owner.
- Myrava (ORG-001558): a ruling that a tier-cap note ("do not promote above C") does not bar a markets cell written from an own-site sentence.
- Centerline Biomedical, Synapse Biomedical, PRC-Saltillo and Volk Optical describe devices without the word "medical device"; a ruling on by-meaning device terms would decide four holds.
- Raydar of Ohio and Sherwood Advanced Composite Technologies: the record website serves a parked or for-sale page; a website correction is another lane's.
