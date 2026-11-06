FINAL PACKET L10 PR136: supersedes earlier57/60/49 claim snapshots as described in README. Current is57 VERIFIED value fills (52 markets +5 certs),13 active PIC18 organizations,394→404 markets populated and47→52 certs populated out of4884 active orgs. Seven held input cases:4 ISO9001 and3 Rainbow;21 holds overall. Authoritative ISO2015 superseded:controller holds transition ruling. Cert identities/expiry quotes and bounds now machine-checked; duplicate evidence ID lookup assertion fixed. Scope diff:13 org rows,10 marketfields,5certificatefields,57 evidence appends;historical observations unchanged (WI17 sorted). validate0errors. Raw64quotes +fresh seeded30 VERIFIED sample0errors; sample is quote presence, not independent semantic audit. Re-run commands and review sources/diff from branch. Initial council Codex/Sonnet refuted Rainbow and duplicate-ID guarantee;fixed/held. Clerk final APPROVE/REFUTE requested.

FILE README.md
# L10 markets and certifications — PIC-18 batch, 2026-11-06

Claim: atlas-L10-markets-certs (IDEAS B-01/B-07), delegated integrator scope: only organization markets_served and certifications plus their evidence. Branch `agent/codex/markets-certs`; baseline `bd57a08`. First user: PIC supplier-matching staff; use review due 2026-12-15 (campaign T1 date; controller owns follow-up).

## Acceptance and result

Own-site statements only; corporate claims, no inferred ISO-to-market mapping. Markets use SCHEMA §3.3 / vocab.json exactly, automotive without OEM stays automotive_unspecified, medical without device stays medical_healthcare_general. Certifications follow owner 2026-11-01 R3c/R12: current edition named on current page, or current certificate; no expired/future certificate, edition-less claim or product-compliance claim. Four ISO9001:2015 candidates are held after the edition check (battery below). No other org column or existing evidence row changes; no tier change, record create, inclusion ruling, or registry link.

Unit/filter: all active organization rows on baseline, 4,884 (the brief's 4,893 denominator does not match this checked-out tree). Filled markets_served 394 → 404 (+10 organizations); certifications 47 → 52 (+5 organizations). 13 active organizations changed, all with a PIC-18 site; 52 market value fills and 5 certification fills, each with one evidence row: 57 appended, EVD-240000–240063 (four ISO9001 and three Rainbow candidate IDs reserved and unused), OH (56) and WI (1) evidence shards. Changed organizations by unchanged verification tier: A 5 / B 8. counts.json records the initial before/after.

This is a bounded first PIC-18 batch, not completion of the 900+ PIC-18 backlog or the national gap. Lower-priority Tier-1/other Ohio/Pennsylvania phases were not reached. 24 active organizations were screened or followed up at own-site pages/certificates; 13 enriched, 11 without fills. One extra attempted cyplas.com address was a failed route, not attributed to an Atlas organization.

## Sources and holds

inputs.csv is the reviewed verdict packet: organization, field, exact value, public own-site URL, raw quote, verdict, certification expiry when shown. No private/CRM/licensed material. The held company quality page links Design Molded Products LLC's Intertek CERT-0145662, at the matching two Bavaria Drive addresses; valid 2025-05-29 to 2028-06-01. This is certificate attribution, not an entity-name correction.

holds.csv is the holds table (21 claim/organization cases, STILL_UNCERTAIN, each naming the settling fact). Main holds: Ferriot certificate current cycle starts 2026-11-20 (future at observation; expiry 2029-09-30), CIMA ISO 9001:2000 obsolete and aspirational, retail/security/material-handling/communication/transportation markets ambiguous or off vocabulary, unavailable sites, and Ohio Precision Molding domain serving Design Molded content. Recommended reading for vocabulary holds: owner 2026-11-01 R2/R8, SCHEMA §3.3; retain holds until an explicit mapping or narrower evidence exists. No organization markets_other_note column exists, so no off-vocabulary notes written. Missing certifications on other worked organizations mean unfilled, never uncertified.

## Reproduction and checks

- `python3 tasks/markets-certs-2026-11-06/check.py`: 4/4 live known answers (CIMA markets, ESTERLE ISO, Hudson ISO, CIMA negative ISO2015); fabricated quote defect rejected 4/4. All 64 candidate quotes pass (57 VERIFIED, four ISO9001 and three Rainbow holds); unavailable source fails loudly. Then fresh network retrieval of seeded random 30 **value rows**, seed 20261106: **0 raw quote errors**. audit30.csv records every sampled value. The sample is at value-row grain, not 30 distinct organizations, and measures quote support, not an independent human semantic audit.
- `python3 tasks/markets-certs-2026-11-06/build.py`: 57 evidence appends first run, zero second run; field union preserves existing tags. Evidence ID collision or altered pre-existing observation fails. All active/input/PIC-18/vocabulary/own-domain/unique-value conditions asserted. Only markets_served/certifications differ on 13 org rows; historical evidence unchanged. No new dependency.
- `python3 scripts/validate.py`: **OK — validation passed; 0 errors** (35,410 evidence rows total). Initial run caught B-strength activity evidence against five tier-A records (V-25); regenerated unpublished lane evidence with own_site's allowed supports_A strength. Existing evidence and org tiers untouched.

The named ownership-status-2 raw checker was absent. fetch.py reuses the existing evidence-repair-2 prep.W token normalization/contiguous-order matcher, with curl browser UA (compressed responses supported), Jina fallback and pdftotext for PDF. HTML text (script/style excluded; hidden content not evaluated) is matched, never a model summary. Known answers caught a gzip response issue before inputs were trusted. Fallback failure is availability only. Source snapshots were temporary; only public claim excerpts are committed. Network re-checks can later fail if a witness changes.

Rebase: restore fresh main's data/organizations_OH.csv and data/evidence_organizations_OH.csv, then rerun build.py and validate; never hand-merge CSV. Preserve this inputs.csv ordering because IDs derive from it. The branch base is the pre-pass backup.

## Coordination and review

Controller notified via bb thread tell and shared BOARD: ownership-status-2 checker absent, repair-2 matcher reused; two-column scope and ID block unchanged. Controller confirmed the ISO transition hold and requested battery recommendation (a); recorded below. No files owned by L4/L9 beyond the two explicitly delegated columns were changed. Controller alone merges/statuses tasks.

Reviews pending on the final packet via controller-designated Codex/Grok refute clerks (05:55 BOARD direction supersedes council-only/before-PR gate; draft PR may precede review). Initial council reviews targeted an earlier packet and are not final approval.


Accepted certification details: Denney NSF-ISR C0588169-AS2 AS9100D expires 2027-09-09; Paramont Amtivo264532 AS9100D expires 2027-01-16; STERIS BSI FM75837 ISO13485:2016 expires 2027-12-18; US Endoscopy BSI FM75888 expires 2027-12-21; Flambeau Sharon Center ABS38565.E/IATF0555367 IATF16949:2016 expires 2027-11-17. Each quote comes from the company-hosted original PDF. Certificate coverage is limited to its named entity/sites/scope, as recorded in evidence notes. ISO9001 components on joint certificates are not filled. ISO13485:2016 current status confirmed at https://www.iso.org/standard/59752.html.

## Owner battery item B-L10-ISO-TRANSITION — HOLD

Question: does R3c's bar on a superseded edition also bar an otherwise current, unexpired certificate during the official accreditation transition window?

Facts checked 2026-11-06: [ISO's standard record](https://www.iso.org/standard/62085.html) marks ISO9001:2015 withdrawn 2026-09-16, replaced by ISO9001:2026. [ISO's transition explainer](https://www.iso.org/quality-management/iso-9001-2026) states a three-year transition for existing certificate holders. The [Dutch national accreditation body's 2026-10-27 notice](https://www.rva.nl/en/nieuws/transistion-iso-9001/) attributes the policy to GLOBAL ACI (the IAF successor), specifies 36 months, final certificate-holder deadline 2029-09-30 and last initial/recertification audits against 2015/AMD1 on 2028-03-31. The original Global ACI/IAF policy PDF was not directly retrieved; this is the accreditation body's first-party published implementation, not an inferred deadline. These normative sources are battery context, never own-site evidence for any organization's certification.

Recommendation (a), requested by controller: a certificate of a superseded edition stays recordable while unexpired and within the published IAF/Global ACI transition window, with edition and expiry in its evidence note; use the earlier of printed expiry and transition deadline. An undated logo/current page alone would not establish certificate validity within that exception. Keep four ISO9001:2015 candidate fills held until the owner rules; no existing certifications changed. Ferriot additionally has a future cycle start; that requires a currently effective certificate irrespective of the transition ruling. Controller message explicitly confirmed this interpretation is an owner ruling (AGENTS §2 rule 9), not a lane decision.

shard_io.append_sorted also restores ascending order of 17 existing Wisconsin evidence rows; their field values are byte-for-byte equivalent after CSV parsing. No historical evidence observation is edited.

Initial review findings resolved: Codex and Sonnet both REFUTED the superseded packet's three Rainbow material-application mappings; all three moved to STILL_UNCERTAIN and their reserved IDs remain unused. Codex identified dictionary construction could hide duplicate existing evidence IDs; builder now asserts tree-wide evidence ID uniqueness before use. Sonnet requested certificate identity/expiry checks; verified certificate input rows now carry identity/expiry quote checks and start/expiry date bounds in builder. Raw audit now records retrieval route and parsed-text SHA256, and is described as quote-presence checking, never independent semantic verification. Other Sonnet uncertainties (truck OEM, EV charging, military/defense and water/plumbing) follow explicit source labels and existing vocabulary; no new terms/rulings adopted. Four ISO9001 candidates had already moved to holds after authoritative edition check.

FILE inputs.csv
org_id,field,value,source_url,quote,verdict,note,cert_identity_quote,cert_start,cert_expiry,cert_expiry_quote
ORG-000061,markets_served,medical_device,https://www.ferriot.com/,"Enclosures and components for critical devices such as analyzers, infusion systems, and patient equipment",VERIFIED,,,,,
ORG-000061,markets_served,industrial_machinery,https://www.ferriot.com/,"Machine control housings, automation components, and rugged industrial enclosures",VERIFIED,,,,,
ORG-000061,markets_served,electronics_electrical,https://www.ferriot.com/,"EMI shielded enclosures, cable and connector housings, and electronic device components",VERIFIED,,,,,
ORG-000061,markets_served,appliances,https://www.ferriot.com/,"Kiosk enclosures, terminals, and appliance housings for high-use environments",VERIFIED,,,,,
ORG-000061,markets_served,energy_renewables_battery,https://www.ferriot.com/,EV Charging and Electrical Infrastructure,VERIFIED,,,,,
ORG-000069,markets_served,automotive_unspecified,https://www.designmolded.com/markets-served/,Automotive Industry Precision and durability are paramount in the automotive sector.,VERIFIED,,,,,
ORG-000069,markets_served,medical_healthcare_general,https://www.designmolded.com/markets-served/,Healthcare Sector Reliability and precision are crucial in the healthcare industry for patient care.,VERIFIED,,,,,
ORG-000069,markets_served,toys_sporting_goods,https://www.designmolded.com/markets-served/,"Our injection-molded parts are utilized in athletic gear, outdoor equipment, and sporting goods accessories",VERIFIED,,,,,
ORG-000069,markets_served,appliances,https://www.designmolded.com/markets-served/,"From refrigerators to washing machines, we provide components that meet the highest quality and performance standards.",VERIFIED,,,,,
ORG-000113,markets_served,industrial_machinery,https://customrubbercorp.com/industries,Industrial Machinery Learn More,VERIFIED,,,,,
ORG-000113,markets_served,consumer_goods_housewares,https://customrubbercorp.com/industries,Consumer Products Read more,VERIFIED,,,,,
ORG-000113,markets_served,automotive_unspecified,https://customrubbercorp.com/industries,Automotive Read more,VERIFIED,,,,,
ORG-000113,markets_served,electronics_electrical,https://customrubbercorp.com/industries,Electronics Read more,VERIFIED,,,,,
ORG-000113,markets_served,aerospace_defense,https://customrubbercorp.com/industries,Military/Firearms Read more,VERIFIED,,,,,
ORG-000113,markets_served,appliances,https://customrubbercorp.com/industries,Appliances Read more,VERIFIED,,,,,
ORG-000113,markets_served,lawn_garden_recreation,https://customrubbercorp.com/industries,Lawn and Garden Read more,VERIFIED,,,,,
ORG-000113,markets_served,medical_healthcare_general,https://customrubbercorp.com/industries,Medical Read more,VERIFIED,,,,,
ORG-000113,markets_served,marine,https://customrubbercorp.com/industries,Marine Read more,VERIFIED,,,,,
ORG-000113,markets_served,energy_oil_gas,https://customrubbercorp.com/industries,Oil & Gas Read more,VERIFIED,,,,,
ORG-000113,markets_served,water_wastewater,https://customrubbercorp.com/industries,Wastewater Treatment Aeration,VERIFIED,,,,,
ORG-000072,markets_served,lawn_garden_recreation,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000072,markets_served,medical_healthcare_general,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000072,markets_served,construction_building_products,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000072,markets_served,marine,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000072,markets_served,furniture_office,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000072,markets_served,cosmetics_personal_care,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000072,markets_served,electronics_electrical,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000072,markets_served,rv_powersports_trailers,https://cimaplastics.com/markets.shtml,Markets Served Outdoor Power Equipment Medical Construction Retail Security Marine Office furniture Commercial Skin Care Retail Products Electronics Recreational Vehicles,VERIFIED,,,,,
ORG-000086,markets_served,general_industrial,https://rubberassociates.com/,Industries we serve We serve a wide variety of industries. Below are some of the ones we work with the most. industrial automotive aerospace farming & agriculture water & plumbing consumer products chemical,VERIFIED,,,,,
ORG-000086,markets_served,automotive_unspecified,https://rubberassociates.com/,Industries we serve We serve a wide variety of industries. Below are some of the ones we work with the most. industrial automotive aerospace farming & agriculture water & plumbing consumer products chemical,VERIFIED,,,,,
ORG-000086,markets_served,aerospace_defense,https://rubberassociates.com/,Industries we serve We serve a wide variety of industries. Below are some of the ones we work with the most. industrial automotive aerospace farming & agriculture water & plumbing consumer products chemical,VERIFIED,,,,,
ORG-000086,markets_served,agriculture,https://rubberassociates.com/,Industries we serve We serve a wide variety of industries. Below are some of the ones we work with the most. industrial automotive aerospace farming & agriculture water & plumbing consumer products chemical,VERIFIED,,,,,
ORG-000086,markets_served,water_wastewater,https://rubberassociates.com/,Industries we serve We serve a wide variety of industries. Below are some of the ones we work with the most. industrial automotive aerospace farming & agriculture water & plumbing consumer products chemical,VERIFIED,,,,,
ORG-000086,markets_served,consumer_goods_housewares,https://rubberassociates.com/,Industries we serve We serve a wide variety of industries. Below are some of the ones we work with the most. industrial automotive aerospace farming & agriculture water & plumbing consumer products chemical,VERIFIED,,,,,
ORG-000086,markets_served,chemical_mining_metals_processing,https://rubberassociates.com/,Industries we serve We serve a wide variety of industries. Below are some of the ones we work with the most. industrial automotive aerospace farming & agriculture water & plumbing consumer products chemical,VERIFIED,,,,,
ORG-000031,markets_served,energy_oil_gas,https://www.akronporcelain.com/akron-plastics/,Akron Porcelain & Plastics Company has specialized in molding Thermoset material and processing technologies to satisfy the Oil & Gas Industry since 1957.,VERIFIED,,,,,
ORG-000031,certifications,iso_9001,https://www.akronporcelain.com/akron-plastics/plastic-quality/,AKRON Porcelain & Plastics Company is ISO-9001:2015 certified,STILL_UNCERTAIN, Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates.,,,,
ORG-000065,certifications,iso_9001,https://www.hudsonextrusions.com/,iso 9001:2015 Without Design Certificate number 95:160,STILL_UNCERTAIN, Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates.,,,,
ORG-000060,certifications,iso_9001,https://esterle.com/,"Our forged tooling capacity and expertise, as well as all of our services, boasts ISO 9001:2015 certification.",STILL_UNCERTAIN, Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates.,,,,
ORG-000110,markets_served,general_industrial,https://teamplasticsinc.com/,"Team Plastics supplies, machines, and fabricates plastic products for industrial, retail, museum, display, and specialty applications.",VERIFIED,,,,,
ORG-000110,markets_served,food_processing_foodservice,https://teamplasticsinc.com/,Food Service & Hospitality Custom cutting boards,VERIFIED,,,,,
ORG-000071,markets_served,aerospace_defense,https://milesrubber.com/,"When duty calls, the military turns to Miles Rubber.",VERIFIED,,,,,
ORG-000071,markets_served,automotive_oem,https://milesrubber.com/,We are a trusted Tier 1 supplier to major heavy truck manufacturers,VERIFIED,,,,,
ORG-000071,markets_served,rv_powersports_trailers,https://milesrubber.com/,Recreational Vehicle,VERIFIED,,,,,
ORG-000071,markets_served,industrial_machinery,https://milesrubber.com/,"Miles Rubber provides specialized, heat-resistant seals, gaskets, and protective boots that maintain their integrity under the most demanding conditions. Trust our materials to safeguard your welding equipment",VERIFIED,,,,,
ORG-000087,markets_served,appliances,https://rainbowrubber.com/,"Viton ™ offers a wide range of fluid and chemical resistance, and can be used in applications for: - Appliances - Chemical Processing - Down-Hole Applications - Fuel and Oil Lines",STILL_UNCERTAIN,Codex/Sonnet refute: generic Viton applications do not establish Rainbow corporate served markets; need company-specific market statement.,,,,
ORG-000087,markets_served,chemical_mining_metals_processing,https://rainbowrubber.com/,Chemical Processing - Down-Hole Applications,STILL_UNCERTAIN,Codex/Sonnet refute: generic Viton applications do not establish Rainbow corporate served markets; need company-specific market statement.,,,,
ORG-000087,markets_served,energy_oil_gas,https://rainbowrubber.com/,Down-Hole Applications - Fuel and Oil Lines,STILL_UNCERTAIN,Codex/Sonnet refute: generic Viton applications do not establish Rainbow corporate served markets; need company-specific market statement.,,,,
ORG-000069,certifications,iso_9001,https://www.designmolded.com/wp-content/uploads/2025/05/CERT-0145662_ENG_Design-Molded-Products-LLC.pdf,ISO 9001:2015,STILL_UNCERTAIN,"Intertek CERT-0145662; issued 2025-05-29, valid until 2028-06-01; issued to Design Molded Products LLC, both Bavaria Drive sites match linked company quality page. Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates.",,,,
ORG-000790,certifications,as9100,https://www.denneyplastics.com/wp-content/uploads/2024/08/AS9100D-Certificate.pdf,AS9100D with ISO 9001:2015,VERIFIED,"NSF-ISR C0588169-AS2; AS9100D only; issued 2024-09-10, expires 2027-09-09. ISO9001 component not filled pending transition ruling.","Denney Plastics Machining, Ltd.",2024-09-10,2027-09-09,09-SEP-2027
ORG-001027,certifications,as9100,https://paramontmachinecompany.com/wp-content/uploads/2026/05/Paramont-Machine-Co-AS9100D-ISO9001-Certificate.pdf,AS9100D / ISO 9001: 2015,VERIFIED,"Amtivo 264532; AS9100D only; cycle starts 2024-06-11, latest issue 2024-10-31, expires 2027-01-16. ISO9001 component not filled pending transition ruling.",Paramont Machine Company,2024-06-11,2027-01-16,"January 16, 2027"
ORG-001549,certifications,iso_13485,https://www.steris.com/-/media/documents/pdfs/quality-system-certificates/mentor-oh/6-10-2026/iso-13485-fm-75837.pdf,QUALITY MANAGEMENT SYSTEM - ISO 13485:2016,VERIFIED,"BSI FM75837, STERIS Corporation at 5960 Heisley Rd Mentor; effective 2024-12-19, revision 2026-06-03, expires 2027-12-18. Coverage limited to named certificate sites/scope.",STERIS Corporation,2024-12-19,2027-12-18,2027-12-18
ORG-001550,certifications,iso_13485,https://www.steris.com/-/media/documents/pdfs/quality-system-certificates/steris-endoscopy/9-5-2025/iso-13485-2016-fm75888.pdf,QUALITY MANAGEMENT SYSTEM - ISO 13485:2016,VERIFIED,"BSI FM75888 United States Endoscopy Group Inc trading as US Endoscopy; effective 2024-12-22, revision 2025-09-04, expires 2027-12-21. Coverage limited to named certificate sites/scope.","United States Endoscopy Group, Inc.",2024-12-22,2027-12-21,2027-12-21
ORG-000340,certifications,iatf_16949,https://www.flambeau.com/wp-content/uploads/2025/01/IATF16949-Sharon-Center-Exp17Nov2027.pdf,"IATF 16949:2016, First Edition",VERIFIED,"ABS38565.E/IATF0555367; Flambeau Sharon Center OH facility, blow-molded components; effective 2024-11-18, expires 2027-11-17. Not every Flambeau location certified; linked by corporate quality page.","Flambeau Inc. – Sharon Center, OH.",2024-11-18,2027-11-17,17 NOV 2027
ORG-000790,markets_served,aerospace_defense,https://www.denneyplastics.com/,"We manufacture ball valve seats for many industries. Aerospace, Pharmapsutical, Medical, Oil & Gas, Naval Nuclear, Naval Seawater, Chemical and Cryogenic industries.",VERIFIED,,,,,
ORG-000790,markets_served,pharmaceutical_biotech,https://www.denneyplastics.com/,"We manufacture ball valve seats for many industries. Aerospace, Pharmapsutical, Medical, Oil & Gas, Naval Nuclear, Naval Seawater, Chemical and Cryogenic industries.",VERIFIED,,,,,
ORG-000790,markets_served,medical_healthcare_general,https://www.denneyplastics.com/,"We manufacture ball valve seats for many industries. Aerospace, Pharmapsutical, Medical, Oil & Gas, Naval Nuclear, Naval Seawater, Chemical and Cryogenic industries.",VERIFIED,,,,,
ORG-000790,markets_served,energy_oil_gas,https://www.denneyplastics.com/,"We manufacture ball valve seats for many industries. Aerospace, Pharmapsutical, Medical, Oil & Gas, Naval Nuclear, Naval Seawater, Chemical and Cryogenic industries.",VERIFIED,,,,,
ORG-000790,markets_served,marine,https://www.denneyplastics.com/,"We manufacture ball valve seats for many industries. Aerospace, Pharmapsutical, Medical, Oil & Gas, Naval Nuclear, Naval Seawater, Chemical and Cryogenic industries.",VERIFIED,,,,,
ORG-000790,markets_served,chemical_mining_metals_processing,https://www.denneyplastics.com/,"We manufacture ball valve seats for many industries. Aerospace, Pharmapsutical, Medical, Oil & Gas, Naval Nuclear, Naval Seawater, Chemical and Cryogenic industries.",VERIFIED,,,,,
ORG-001027,markets_served,aerospace_defense,https://paramontmachinecompany.com/expertise/,"Aerospace & Defense: High-temperature, lightweight, and flight-ready solutions",VERIFIED,,,,,
ORG-001027,markets_served,energy_oil_gas,https://paramontmachinecompany.com/expertise/,"Oil & Gas: Severe-duty, corrosion-resistant seals and fluid transfer sub-components",VERIFIED,,,,,
ORG-001027,markets_served,medical_healthcare_general,https://paramontmachinecompany.com/expertise/,Medical & Life Sciences: Strict biocompatible plastic parts machined for critical healthcare and surgical applications,VERIFIED,,,,,
ORG-001027,markets_served,electronics_electrical,https://paramontmachinecompany.com/expertise/,"Semiconductor & High-Tech: Ultra-pure, precision components constructed for advanced technology manufacturing environments",VERIFIED,,,,,

FILE holds.csv
org_id,field,source_url,verdict,settling_fact
ORG-000061,certifications,https://www.ferriot.com/wp-content/uploads/2026/10/Ferriot__Inc._ISO_9001_Cert_Nov_2026.pdf,STILL_UNCERTAIN,"Certificate 526008 issued 2026-10-06; current cycle starts 2026-11-20, expires 2029-09-30. Need prior current certificate or a current dated-edition claim; do not assume future cycle is active."
ORG-000072,certifications,https://cimaplastics.com/quality.shtml,STILL_UNCERTAIN,Page says currently evaluating moving to ISO 9001:2000. Need current certificate/current edition claim (R3c).
ORG-000069,markets_served,https://www.designmolded.com/markets-served/,STILL_UNCERTAIN,Safety components has no precise markets vocabulary term or organization markets_other_note. Recommend hold until owner approves vocabulary; no general-industrial inference.
ORG-000072,markets_served,https://cimaplastics.com/markets.shtml,STILL_UNCERTAIN,Retail and Security have no exact vocabulary mapping or organization markets_other_note. Recommend hold pending owner vocabulary ruling.
ORG-000113,markets_served,https://customrubbercorp.com/industries,STILL_UNCERTAIN,"Material Handling, Communication, Transportation, Smart Grid Technology ambiguous against current vocabulary. Need narrower own-site statement or owner ruling."
ORG-000110,markets_served,https://teamplasticsinc.com/,STILL_UNCERTAIN,Retail and museum markets lack precise vocabulary mapping; hold pending owner ruling.
ORG-000040,both,https://splastics.com/,STILL_UNCERTAIN,Direct and Jina fetch unavailable; need retrievable own-site industries/quality page. No absence inference.
ORG-000062,both,https://www.chemionics.com/,STILL_UNCERTAIN,Direct and Jina fetch unavailable; need retrievable own-site industries/quality page. No absence inference.
ORG-000116,both,https://www.amdplastics.com/,STILL_UNCERTAIN,Direct and Jina fetch unavailable; need retrievable own-site industries/quality page. No absence inference.
ORG-000115,both,https://cuyahogaplastics.com/,STILL_UNCERTAIN,Direct and Jina fetch unavailable; need retrievable own-site industries/quality page. No absence inference.
ORG-000085,both,https://ohioprecisionmolding.com/,STILL_UNCERTAIN,URL serves Design Molded Plastics content. Hold attribution to Ohio Precision Molding; need entity linkage before copying claims.
ORG-001905,both,https://thermoprene.com/,STILL_UNCERTAIN,Homepage lacks explicit corporate markets/edition-qualified certification claim in reviewed text; need own-site industries/quality page.
ORG-000101,markets_served,https://www.polymericsinc.com/,STILL_UNCERTAIN,Homepage supports mixing but no explicit end markets; need own-site market page. Existing iso_9001 is unchanged.
ORG-000117,both,https://www.noramcobag.com/,STILL_UNCERTAIN,Homepage navigation gives leads but not sufficiently specific market/certificate evidence; need substantive industry/quality page.
ORG-000031,certifications,https://www.akronporcelain.com/akron-plastics/plastic-quality/,STILL_UNCERTAIN, Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates.
ORG-000065,certifications,https://www.hudsonextrusions.com/,STILL_UNCERTAIN, Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates.
ORG-000060,certifications,https://esterle.com/,STILL_UNCERTAIN, Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates.
ORG-000069,certifications,https://www.designmolded.com/wp-content/uploads/2025/05/CERT-0145662_ENG_Design-Molded-Products-LLC.pdf,STILL_UNCERTAIN,"Intertek CERT-0145662; issued 2025-05-29, valid until 2028-06-01; issued to Design Molded Products LLC, both Bavaria Drive sites match linked company quality page. Held under R3c: ISO official 62085 page marks ISO9001:2015 withdrawn 2026-09-16 and replaced by 2026. Need current-edition evidence or owner ruling for transition-period certificates."
ORG-000087,markets_served,https://rainbowrubber.com/,STILL_UNCERTAIN,Codex/Sonnet refute: generic Viton applications do not establish Rainbow corporate served markets; need company-specific market statement.
ORG-000087,markets_served,https://rainbowrubber.com/,STILL_UNCERTAIN,Codex/Sonnet refute: generic Viton applications do not establish Rainbow corporate served markets; need company-specific market statement.
ORG-000087,markets_served,https://rainbowrubber.com/,STILL_UNCERTAIN,Codex/Sonnet refute: generic Viton applications do not establish Rainbow corporate served markets; need company-specific market statement.

FILE build.py
"""Idempotently union the reviewed L10 values and append one immutable evidence row per value."""
import csv, json, sys
from datetime import date
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
from regions import PIC18

def read(path):
    with path.open(newline='') as f: return list(csv.DictReader(f))

def main():
    data = ROOT / 'data'
    shards = {p: read(p) for p in sorted(data.glob('organizations_*.csv')) if p.stem != 'organizations_all'}
    orgs = {r['org_id']: (p, r) for p, rows in shards.items() for r in rows}
    assert len(orgs) == sum(map(len, shards.values()))
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']
    allowed = {'markets_served': set(vocab['MARKETS']['values']), 'certifications': set(vocab['CERTS']['values'])}
    inputs = read(HERE / 'inputs.csv')
    assert len({(r['org_id'], r['field'], r['value']) for r in inputs}) == len(inputs)
    pic18 = {r['org_id'] for r in read(data / 'sites_OH.csv') if r['county'] in PIC18}
    old_evidence = [r for p in data.glob('evidence_*.csv') for r in read(p)]
    evidence = {r['evidence_id']: r for r in old_evidence}
    assert len(evidence) == len(old_evidence), 'duplicate evidence IDs in current tree'
    append, touched = defaultdict(list), set()
    def counts():
        active = [r for _, r in orgs.values() if r['status'] == 'active']
        return {'active_organizations': len(active), **{f: sum(bool(r[f]) for r in active) for f in allowed}}
    before = counts()
    for i, v in enumerate(inputs):
        if v['verdict'] == 'STILL_UNCERTAIN': continue
        assert v['verdict'] == 'VERIFIED'
        field = v['field']; assert field in allowed and v['value'] in allowed[field]
        if field == 'certifications':
            assert v['cert_identity_quote'] and v['cert_expiry_quote']
            assert date.fromisoformat(v['cert_start']) <= date(2026, 11, 6) <= date.fromisoformat(v['cert_expiry'])
        path, row = orgs[v['org_id']]
        assert row['status'] == 'active' and row['org_id'] in pic18
        host = lambda u: urlparse(u if '://' in u else 'https://' + u).hostname.removeprefix('www.')
        assert host(v['source_url']) == host(row['website']), v
        values = row[field].split(';') if row[field] else []
        if v['value'] not in values:
            row[field] = ';'.join(sorted(values + [v['value']])); touched.add(path)
        eid = f'EVD-{240000+i:06d}'; assert int(eid[4:]) <= 259999
        ev = dict(evidence_id=eid, record_table='organizations', record_id=v['org_id'], claim_type='activity',
                  claim_detail=f'{field} {v["value"]}: "{v["quote"]}"', source_class='own_site',
                  source_ref=v['source_url'], observed_date='2026-11-06', tier_effect='supports_A',
                  created_by='codex atlas-L10-markets-certs', notes=v['note'] or 'Own-site corporate claim; raw quote checked 2026-11-06; record tier unchanged.')
        if eid in evidence: assert evidence[eid] == ev, ('ID collision or changed observation', eid)
        else: append[data / path.name.replace('organizations_', 'evidence_organizations_')].append(ev)
    for path in touched:
        with path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(shards[path][0]), lineterminator='\n'); w.writeheader(); w.writerows(shards[path])
    for path, rows in append.items(): append_sorted(path, rows, 'evidence_id')
    print(json.dumps({'before': before, 'after': counts(), 'packet_value_rows': len(inputs),
                      'packet_organizations': len({r['org_id'] for r in inputs if r['verdict'] == 'VERIFIED'}),
                      'tiers': dict(Counter(orgs[oid][1]['verification_tier'] for oid in {r['org_id'] for r in inputs if r['verdict'] == 'VERIFIED'})),
                      'new_evidence_rows': sum(map(len, append.values()))}, indent=2))

if __name__ == '__main__': main()

FILE fetch.py
"""Raw HTML fetch via curl; token matcher reused from the house evidence-repair prep."""
import importlib.util
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('repair_prep', ROOT / 'tasks/evidence-repair-2-2026-11-04/prep.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)
W = prep.W

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.links = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'a': self.links.extend(v for k, v in attrs if k == 'href')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, text):
        if not self.skip: self.parts.append(text)

def fetch(url):
    for route in (url, 'https://r.jina.ai/' + url):
        r = subprocess.run(['curl', '--compressed', '-fLsS', '--max-time', '35', '-A', 'Mozilla/5.0', route], capture_output=True)
        if r.returncode: continue
        if r.stdout.startswith(b'%PDF'):
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / 'certificate.pdf'; path.write_bytes(r.stdout)
                pdf = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, check=True)
                return pdf.stdout.decode('utf-8'), [], route
        raw = r.stdout.decode('utf-8', 'replace')
        p = Page(); p.feed(raw)
        text = ' '.join(' '.join(p.parts).split()) if route == url else raw
        if len(text) > 100 and 'Just a moment...' not in text[:500]: return text, p.links, route
    raise RuntimeError('unfetchable: ' + url)

def found(text, quote):
    p, q = W(text), W(quote)
    return bool(q) and any(p[i:i+len(q)] == q for i in range(len(p)-len(q)+1))

if __name__ == '__main__':
    import sys
    text, links, route = fetch(sys.argv[1]); print(route); print(text); print('\nLINKS', '\n'.join(links))

FILE check.py
"""Fetch known answers, check every packet quote, then independently re-fetch a seeded 30-value sample."""
import csv, random, hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fetch import fetch, found
HERE = Path(__file__).resolve().parent

def main():
    cases = [
        ('https://cimaplastics.com/markets.shtml', 'Markets Served Outdoor Power Equipment Medical', True),
        ('https://esterle.com/', 'ISO 9001:2015 certification', True),
        ('https://www.hudsonextrusions.com/', 'iso 9001:2015 Without Design', True),
        ('https://cimaplastics.com/quality.shtml', 'ISO 9001:2015 certified', False),
    ]
    for url, quote, expected in cases:
        text, _, _ = fetch(url)
        assert found(text, quote) == expected, (url, quote)
        assert not found(text, 'L10 deliberately fabricated defect phrase'), url
    print('known answers: 4/4; injected fabricated quotes refused: 4/4')
    rows = list(csv.DictReader((HERE / 'inputs.csv').open()))
    routes = {}
    def retrieve(url):
        text, _, route = fetch(url); routes[url] = route
        return url, text
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in rows})))
    for r in rows:
        assert found(pages[r['source_url']], r['quote']), r
        if r['verdict'] == 'VERIFIED' and r['field'] == 'certifications':
            assert found(pages[r['source_url']], r['cert_identity_quote']), r
            assert found(pages[r['source_url']], r['cert_expiry_quote']), r
    print('packet quotes:', len(rows), 'passed; zero unavailable pages')
    sample = random.Random(20261106).sample([r for r in rows if r['verdict'] == 'VERIFIED'], 30)
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in sample})))
    out = [{**r, 'raw': 'yes' if found(pages[r['source_url']], r['quote']) else 'no',
            'route': routes[r['source_url']], 'text_sha256': hashlib.sha256(pages[r['source_url']].encode()).hexdigest()} for r in sample]
    with (HERE / 'audit30.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator='\n'); w.writeheader(); w.writerows(out)
    assert all(r['raw'] == 'yes' for r in out)
    print('random fresh raw re-check: 30 value rows; 0 errors; seed 20261106')

if __name__ == '__main__': main()

FILE counts.json
{
  "before": {
    "active_organizations": 4884,
    "markets_served": 394,
    "certifications": 47
  },
  "after": {
    "active_organizations": 4884,
    "markets_served": 404,
    "certifications": 52
  },
  "packet_value_rows": 64,
  "packet_organizations": 13,
  "tiers": {
    "B": 8,
    "A": 5
  },
  "new_evidence_rows": 57
}
