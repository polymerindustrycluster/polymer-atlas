# Nine-case PA adjudication packet

Snapshot: 2026-10-30 16:44 UTC. Pinned main: `b67b1924368d60b45a0cb49134ae81ce6b1b0d8c`. Rechecked unchanged at16:47:20UTC.

**Packet only. Draft PR6. No data edits, merges, ID allocation or main pushes.** All motions are recommendations for owner/integrator adjudication, not authorization to apply. Conditional folds must not run until settling facts are obtained. Status/tier/date changes are not implied by evidence rows.

Counts (filter: PR1 PA01–08 and PA10 only): 9 cases; 40 distinct referenced canonical records; 29 draft evidence rows; 0 canonical rows changed; verdict counts: {'STILL_UNCERTAIN': 7, 'VERIFIED': 1, 'DUPLICATE_OF': 1}.

## Reproduction and protocol
- Read pinned AGENTS.md §2 rules7–9, SCHEMA.md and QUEUE.md. Claimed sixth task before research; preserved five existing PR queue blocks byte-for-byte. Historical blocker text in those entries is not a current finding.
- Re-ran `python3 scripts/validate.py`: PASS on repaired main (organizations_OR.csv present). Counts are validator rows, all statuses:3495 organizations,4244 sites,206 ecosystem,634 registry links,60 members,73 people,73 programs,71 events,6640 evidence,331 relationships,461 capabilities,782 participations.
- `python3 scripts/check_pa_packet.py` checks full-row SHA256 fingerprints, named-table/union FK resolution, source-backed evidence drafts and ceilings, verdict grammar and terminating successor chains. No final evidence IDs allocated. Fingerprint input is full CSV row canonical JSON, including empty values.
- No REJECT verdicts or closure actions. No Form5500 check completed; it remains mandatory before any later closure/no-establishment rejection. Failed routes are availability observations only. Research stayed approximately six unique primary-source pages per organization; repeated retrieval of same URL is not independent corroboration.
- PA09/JM Eagle is **resolved by upstream pass18** at f928257aa92ce7b91f781183d00035c752663349: ORG002260→ORG002261, duplicate site2229→2230. Already recorded in PR1; no renewed dedupe motion.
- `packet.json` contains full pinned records/fingerprints and machine-readable motions. `evidence_rows.csv` uses exact Atlas columns, blank evidence_id. `source_ledger.json` names every used source and failed route. Sources support only the narrow claim described, not whole-record tier upgrades.

## Cases

### PA-01 — STILL_UNCERTAIN


Affected records: `ORG-002472`, `ORG-002473`, `SITE-002457`, `SITE-002458`, `SITE-002459`.
- **annotate**: Annotate historical industrial cooling-discharge context and current Lenni manufacturer identity. Hold organization fold and all site consolidation pending exact IWTP source-system crosswalk. [owner/integrator review]
- **stand separate**: Preserve Mayfield as a distinct plant, unaffected by Lenni wastewater identity question. [owner/integrator review]
- Settling fact: A source-system FRS/DEP record crosswalk linking the exact Westlake Plastics IWTP harvested record to permitPA0051438 and its legal operator; and establishment boundary for the treatment asset versus Lenni plant.
- Reproduction/correction: Privacy address reproduces. Existing assertion IWTP is merely a permit is directionally corroborated by historicalNPDES evidence but exact harvested IWTP crosswalk still does not reproduce.
- Source: [Westlake Plastics privacy policy](https://www.westlakeplastics.com/privacy-policy/) — Company postal contact is Westlake Plastics Company, 490 W. Lenni Road, Lenni PA19052.
- Source: [Westlake Plastics quality systems](https://www.westlakeplastics.com/capabilities/quality-systems/) — Quality page retrieved; no exact IWTP registry crosswalk found in examined page.
- Source: [Pennsylvania Bulletin March7 1998, p1252](https://pacodeandbulletin.gov/secure/pabulletin/data/vol28/28-10/28_10_not.pdf) — PA0051438 renewal describes Westlake Plastics Company cooling-water discharge from thermoplastic extrusion manufacturing in Chester Heights Borough, Delaware County. Historical permit purpose, not current status.
- Source: [Pennsylvania Bulletin July1 2023 application E2301223-002](https://www.pacodeandbulletin.gov/secure/pabulletin/data/vol53/53-26/847a.html) — Westlake Plastics Co application at490 Lenni Road proposes main manufacturing building addition; Chester Heights Borough Delaware County.
- Source: [Westlake Plastics contact route](https://www.westlakeplastics.com/contact-us/) — Fetch timed out; no negative company inference.
- Source: [Westlake Plastics about route](https://www.westlakeplastics.com/about-us/) — Fetch timed out; no negative company inference.

Borderline calls (not self-ruled):
- Owner/integrator decides whether treatment asset warrants separate establishment if same operator; no scope ruling made.

### PA-02 — STILL_UNCERTAIN


Affected records: `ORG-002358`, `ORG-002359`, `SITE-002336`, `SITE-002337`.
- **stand separate**: Provisional hold, not a final duplicate rejection: corporation parent and Graphics division have distinct trade identity, websites and locations satisfying evidence for separate-unit consideration. Existing parent row describes Graphics, so rectify identity mapping before final keep/fold. [owner/integrator review]
- **annotate**: Annotate verified corporate division relationship; cite Graphics345 OakRoad and parent PittsburghHQ separately. Do not replace1239 street or fold site solely because homepage gives345. [owner/integrator review]
- **re-point**: Conditional proposal to assign345 OakRoad manufacturing site to Graphics operator row if integrator confirms separate-unit identity; do not allocate new site IDs for parent addresses in this packet. [owner/integrator review]
- Settling fact: Resolve what ORG-002358 represents: actual Pannier Corporation parent versus a second mislabeled Graphics operator; obtain primary historic address evidence linking1239 OakRoad to345 OakRoad before treating site rows as duplicate.
- Reproduction/correction: Homepage345 OakRoad reproduces. Prior ai-info route does not reproduce (cache miss). Earlier implication common website alone settles corporate identity is not supported: parent owns different site/domain and explicitly calls Graphics a division.
- Source: [Pannier Corporation company history](https://www.pannier.com/about-us/history/) — Corporation explicitly identifies acquired fiberglass-signage business as Pannier Graphics division in Gibsonia; corporation HQ remains Sandusky Street Pittsburgh.
- Source: [Pannier Corporation locations](https://www.pannier.com/contact-us/locations/) — HQ207 Sandusky Street Pittsburgh PA15212; factory1130 Old Butler Plank Road Glenshaw PA15116. These are not345 Oak Road.
- Source: [Pannier Graphics homepage](https://www.panniergraphics.com/) — Outdoor-sign manufacturer; footer345 Oak Road Gibsonia PA15044; fiberglass embedment and gel-coat laminate offerings.
- Source: [Pannier Graphics fiberglass embedment](https://www.panniergraphics.com/fiberglass-embedment) — Dedicated manufacturer product page retrieved; evidence of distinct Graphics trade identity, not legal independence.
- Source: [Pannier Graphics contact](https://www.panniergraphics.com/contact-us) — Own contact page retrieved; supports branded division route.
- Source: [Pannier Graphics AI information route](https://www.panniergraphics.com/ai-info) — Cache-miss failure, including direct link from homepage; cannot reproduce prior packet reliance on AI-info text via present tool.
- Source: [Pannier contact guessed route](https://www.pannier.com/contact/) — Unavailable; superseded for research by linked /contact-us/locations/.

Borderline calls (not self-ruled):
- Graphics distinct trade name/site/domain support separate-unit test, but authoritative entity mapping needs integrator adjudication.
- Ring1 versus ring4 and326112 versus339943 discrepancies require owner scope/ring ruling and sourced code review; no automatic harmonization.

### PA-03 — STILL_UNCERTAIN


Affected records: `ORG-002367`, `ORG-002401`, `SITE-002345`, `SITE-002381`.
- **stand separate**: Keep both establishments:760 WMarketStreet Gratz and79 ParkLane Hegins; not site duplicates. [owner/integrator review]
- **annotate**: Record primary evidence that current Hegins permit holder is LLC, not Inc; retain unresolved historical alias/legal conversion, do not manufacture conversion date. [owner/integrator review]
- **fold**: Conditional only: once Inc-to-LLC identity history verified, fold legacy Inc organization into held LLC organizationORG-002367 and remove plant-specific qualifier from survivor name through integrator, not data deletion. [owner/integrator review]
  - Successor chain: ORG-002401 → ORG-002367 (held terminal; conditional where stated).
- **re-point**: Conditional on accepted organizational fold; retain Hegins site and activity/address separate from Gratz. [owner/integrator review]
- Settling fact: A corporate conversion/name-history filing or equivalent company legal statement links legacy MI Windows & Doors Inc record to current MI Windows & Doors LLC; without it legal succession date and tombstone treatment are not established.
- Reproduction/correction: Both own location pages reproduce. Earlier unresolved Hegins operator can now be narrowed: issued2024 permit and currentOSHA roster explicitly sayLLC; Inc spelling no longer supports an inference of separate current operator.
- Source: [MI Windows Gratz location](https://miwindows.com/gratz-location) — Separate vinyl-window/sliding-door manufacturing establishment760 W Market Street Gratz PA17030; company says opened1995.
- Source: [MI Windows Hegins location](https://miwindows.com/hegins-location) — Separate manufacturing establishment79 Park Lane Hegins PA17938; two buildings on same grounds about12 miles east of Gratz.
- Source: [PADEP issued permit54-00098](https://files.dep.state.pa.us/air/AirQuality/AQPortalFiles/Permits/PermitDocuments/1435271%5B54-00098%5D_Issued_v1.pdf) — Cover names owner MI Windows & Doors LLC and Hegins plant79 Park Lane; issued/effective2024-01-16, expires2029-01-16. Confirms LLC operator, not legal Inc-to-LLC conversion.
- Source: [OSHA current VPP sites](https://www.osha.gov/vpp/bylocation) — Lists MI Windows and Doors LLC Gratz and Hegins as separate Pennsylvania Star site-based entries, each NAICS326199.
- Source: [OSHA recent VPP approvals](https://www.osha.gov/vpp/approvals) — May2026 Gratz LLC recertification; site activity corroboration, not proof of corporate conversion date.
- Source: [Pennsylvania Bulletin November25 2023](https://www.pacodeandbulletin.gov/secure/pabulletin/data/vol53/53-47/53-47.pdf) — Notice54-00098 identifies MI Windows & Doors LLC Hegins79 Park Lane; application receivedMarch20 2023.

Borderline calls (not self-ruled):
- Current same-operator evidence is strong; historical legal conversion still unsettled. Do not infer M&A date from permit effective date.
- OSHA historical600 WMarketStreet material appeared in discovery; not substituted for current company760 WMarketStreet and not treated as another plant.

### PA-04 — STILL_UNCERTAIN


Affected records: `ORG-002652`, `ORG-002752`, `SITE-002642`, `SITE-002829`.
- **stand separate**: Hold organizational consolidation: transaction counsel distinguishes PlasticProducts seller from PackagingCorp operating affiliate; current LLC ownsite names M&QHoldings, not PlasticProducts, as group context. [owner/integrator review]
- **annotate**: Annotate historical parent/affiliate sale and current LLC manufacturing identity; flag malformed SITE-002642 street P.O.Box1803 EarlSt. Do not interpret POBox180 as street180 or invent3 EarlStreet from concatenation. [owner/integrator review]
- **re-point**: Conditional only after physical establishment and ownership chain verified; avoid duplicate counting but retain both IDs pending integrator adjudication. [owner/integrator review]
- Settling fact: Corporate transaction/name-history record identifies whether ORG-002652 is historical seller/parent or the same continuing operating LLC, and identifies the Corp-to-LLC successor. A primary permit/parcel/certificate must establish physical street number and whether both site rows represent one EarlStreet establishment.
- Reproduction/correction: Ownsite LLC and POBox180/EarlStreet reproduces. Any earlier direct same-domain duplicate implication is weakened by fresh primary transaction-participant distinction; physical3 EarlStreet cannot be reproduced from own contact alone.
- Source: [M&Q Packaging homepage](https://mqplastics.com/) — Current company footer identifies M&Q Packaging LLC; manufacturing-address block combines POBox180 and EarlStreet, not an independently verified street number.
- Source: [M&Q Why M&Q](https://mqplastics.com/why/) — Packaging LLC is part of Engineered Materials division M&Q Holdings; Pennsylvania manufacturing spans film extrusion to finished products. This is not evidence that Plastic Products Corporation equals LLC.
- Source: [M&Q quality](https://mqplastics.com/why/quality/) — Own quality policy; footer identifies LLC and POBox180 EarlStreet.
- Source: [M&Q contact](https://mqplastics.com/contact-us/) — Own contact route retrieved; does not establish legal conversion chain.
- Source: [Fox Rothschild transaction experience](https://www.foxrothschild.com/mergers-acquisitions/transaction-experience) — Transaction participant says it represented M&Q Plastic Products in sale of operating affiliate M&Q Packaging Corp to affiliate of Capital Partners. Rebuttal to same-domain automatic fold; undated transaction summary.
- Source: [US Third Circuit Mandel v M&Q Packaging Corp Jan14 2013](https://www.govinfo.gov/content/pkg/USCOURTS-ca3-11-03193/pdf/USCOURTS-ca3-11-03193-0.pdf) — Historical caption names Packaging Corp subsidiary of M&Q Plastic Productions Inc. Caption differs from Atlas Products Corporation; do not silently equate spelling/legal entities.

Borderline calls (not self-ruled):
- Historical legalcaption says Plastic Productions Inc, Atlas says Plastic Products Corporation; not an automatic alias match.
- A public supplier platform and401k aggregator surfaced3 EarlStreet, but neither used as canonical primary-address evidence. Form5500 bulk not checked; no closure or no-establishment rejection proposed.

### PA-05 — VERIFIED
Retain Bostik ORG-000683 and Arkema Inc ORG-002224 as distinct organizations. Shared Arkema domain is not duplicate identity. Preserve all five establishments and current organization pointers.

Affected records: `ORG-000683`, `ORG-002224`, `SITE-000734`, `SITE-001532`, `SITE-002189`, `SITE-002190`, `SITE-002688`.
- **stand separate**: Retain Bostik ORG-000683 and Arkema Inc ORG-002224 as distinct organizations. Shared Arkema domain is not duplicate identity. Preserve all five establishments and current organization pointers. [ready for integrator review]
- **annotate**: Correct HQ city King of Prussia -> Wauwatosa; state PA -> WI; propose integrator-only move organizations_PA.csv -> organizations_WI.csv. Preserve org ID and all Ohio site rows. Keep hq_county blank pending physical-address county resolution. Propose own Bostik website rather than shared parent URL. [VERIFIED]
- **annotate**: Correct HQ city Birdsboro -> Radnor, retain PA. Birdsboro is a production establishment, not HQ. Clear stale HQ county Berks pending independently sourced county of 155 King of Prussia Road. Preserve Birdsboro and West Chester site addresses and counties. [VERIFIED]
- **annotate**: HQ counties held; do not guess from postal city. Obtain municipal parcel/physical-address county evidence for 11320 W Watertown Plank Road and 155 King of Prussia Road. [STILL_UNCERTAIN]
- Reproduction/correction: Prior distinct-HQ finding reproduces. A complete county correction does not reproduce from these primary pages; leave county unresolved, never retain Birdsboro/Berks as HQ by inertia.
- Source: [Arkema in the U.S. at a glance](https://www.arkema.com/usa/en/united-states/arkema-united-states/at-a-glance/) — Separately identifies Arkema Inc North American HQ at Radnor PA and Bostik Inc HQ at Wauwatosa WI.
- Source: [Bostik US Locations and Certifications](https://www.bostik.com/us/en_US/customer-support/locations-certifications/) — Own Bostik page identifies US headquarters / Smart Technology & Business Center at 11320 W Watertown Plank Road, Wauwatosa WI 53226.
- Source: [Arkema Radnor headquarters](https://www.arkema.com/usa/en/united-states/headquarters/radnor-pa-hq-1/) — Own page reports 2024 headquarters move to Radnor and 155 King of Prussia Road address; page updated March 2025.
- Source: [Arkema Wauwatosa headquarters](https://www.arkema.com/usa/en/united-states/headquarters/wauwatosa-wi-hq/) — 11320 W Watertown Plank Road address; page updated September 2024.

Borderline calls (not self-ruled):
- Owner/integrator must rule exact parent relationship: shared group and distinct operating organization do not prove Bostik Inc immediate legal parent is held Arkema Inc. Do not set parent_org_id on this evidence.
- County and shard corrections are HQ-only; no relocation of establishments.

### PA-06 — STILL_UNCERTAIN
Retain both org IDs pending exact historical Hazleton-operator/current Archbald entity continuity proof. Annotate historical relocation witness and current warehouse-versus-former-plant mismatch. No fold/re-point/status change yet.

Affected records: `ORG-002193`, `ORG-002399`, `SITE-002155`, `SITE-002379`.
- **annotate**: Retain both org IDs pending exact historical Hazleton-operator/current Archbald entity continuity proof. Annotate historical relocation witness and current warehouse-versus-former-plant mismatch. No fold/re-point/status change yet. [held pending settling fact]
- **annotate**: Set monitor_watch=true as queue-only liveness flag with named reason: 2014 former Hazleton plant/relocation announcement conflicts with active Hazleton warehouse representation. Keep liveness_signal empty: closure_signature requirements were NOT established. Preserve status, status_date, last_verified, last_activity_evidence_date and tier. [VERIFIED]
- **annotate**: Preserve warehouse classification and active status until current address-specific evidence adjudicates them; do not manufacture closure date or convert plant announcement into warehouse closure. [STILL_UNCERTAIN]
- Settling fact: Dated primary company or public filing identifying the legal operator and current activity at 64 N Conahan Drive, Hazleton, and explicitly linking that establishment to the held Archbald organization. If closure is proposed, obtain address-matched Form5500 check plus affirmative closure/status witness; announcement alone cannot settle current warehouse liveness.
- Reproduction/correction: 2014 historical movement finding reproduces, but neither actual completion date nor current Hazleton warehouse closure is reproduced. Any earlier unconditional closure interpretation must be withdrawn.
- Source: [SIMONA and Boltaron unite North American operations, SIMONA AMERICA release](https://www.simona.de/fileadmin/user_upload/Medien/Mediacenter/Presse/2014/2014-10-22-SIMONA-and-Boltaron-unite-North-American-operations.pdf) — Calls Hazleton a former plant and expects equipment/personnel integration into Archbald by end2014. Establishes dated plan and historical linkage, not completed move or 2026 warehouse closure.
- Source: [SIMONA America About](https://simona-america.com/about/) — SIMONA AMERICA Industries described as SIMONA AG subsidiary manufacturing sheet products in Archbald; footer SIMONA AMERICA Inc at101PowerBoulevard.
- Source: [SIMONA America home](https://simona-america.com/) — Current company footer supplies101PowerBoulevard ArchbaldPA18403.
- Source: [SIMONA America legal notice](https://simona-america.com/legal-notice/) — Reviewed; no address-specific Hazleton continuity or current liveness fact found.

Borderline calls (not self-ruled):
- Legal/operating identity versus historical corporate umbrella: do not collapse SIMONA Boltaron ORG-000823 or SIMONA PMC ORG-001046.
- No Form5500 check completed; no REJECT or closure recommendation made.
- 2014 plant relocation does not resolve a later warehouse claim at same locality.
- Historical SIMONA planned-move source retained only as monitor rationale, not affirmative liveness evidence for unresolved Hazleton identity.

### PA-07 — DUPLICATE_OF
Fold ORG-002218 into held ORG-002619; re-point SITE-002182.org_id from ORG-002218 to ORG-002619. Preserve Berwick and Portland as distinct establishments, statuses, dates and provenance. Optional annotate street from malformed string to BIDA Complex Building 350, 3rd and Oak St., supported by OSHA and county-hosted directory; not a relocation.

Affected records: `ORG-002218`, `ORG-002619`, `SITE-002182`, `SITE-002609`.
- **fold**: Fold ORG-002218 into held ORG-002619; re-point SITE-002182.org_id from ORG-002218 to ORG-002619. Preserve Berwick and Portland as distinct establishments, statuses, dates and provenance. Optional annotate street from malformed string to BIDA Complex Building 350, 3rd and Oak St., supported by OSHA and county-hosted directory; not a relocation. [ready for integrator review]
  - Successor chain: ORG-002218 → ORG-002619 (held terminal; conditional where stated).
- Settling fact: Entity/address linkage settled by OSHA inspection showing Berwick site and Portland mailing address under Ultra-Poly Corporation. Any separate current-liveness motion still needs dated current operating or closure evidence at Berwick; this fold does not assert either.
- Reproduction/correction: Berwick2012/PortlandHQ reproduce. Initial research hold for exactBIDA linkage was resolved during same pass by historical OSHA site+mailing-address witness. Current Berwick liveness still not reproduced.
- Source: [Ultra-Poly About: Plastic Recycling at Scale](https://ultrapoly.com/about/) — Own history records a Berwick compounding plant constructed2012; own facilities section names Portland HQ102DemiRd. Historical plant existence is not fresh Berwick liveness.
- Source: [Ultra-Poly Contact Us](https://ultrapoly.com/contactus/) — Names Ultra-Poly Corporation at102DemiRd POBox330 PortlandPA18351.
- Source: [U.S. Department of Labor OSHA inspection1336727.015](https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1336727.015) — Ultra-Poly Corporation site at BIDA Complex#3503rd&OakStreet Berwick with mailing address102DemiRoad Portland. Inspection opened2018-08-08, case closed2019-09-09.
- Source: [Pennsylvania companies accepting agriculture plastics, county-hosted directory](https://www.berkspa.gov/getmedia/cdbf2324-8f01-41ca-a6fa-39daa1c88a37/Ag-Plastics-Recyclers-Oct-2018.pdf) — Lists Ultra-Poly Corporation at BIDA Building3503rdandOakBerwick and102DemiRdPortland with same phone.

Borderline calls (not self-ruled):
- Survivor choice ORG-002619 favors primary-backedHQ over lower-numbered plant-derivedORG-002218; owner/integrator approval required.
- Present Berwick liveness remains separate and unresolved; do not treat inspection-case CLOSED or absence from website current facility list as plant closure.
- County-hosted2016directory is directory evidence, not government-filing evidence; no tier elevation on hosting domain.

### PA-08 — STILL_UNCERTAIN
Issued permit39-00025 distinguishes the owner mailing address in Boyertown from its Macungie plant. It supports one operator but not Boyertown manufacturing or the Macungie street number.

Affected records: `ORG-002232`, `ORG-002489`, `SITE-002200`, `SITE-002476`.
- **annotate**: Correct source interpretation: 230 E Philadelphia Ave is owner mailing address, not a manufacturing establishment proven by this permit. Preserve site pending separate establishment evidence. [ready for integrator review]
- **fold**: Conditional organization-only consolidation after exact legal crosswalk; retain both site records pending establishment adjudication. [held pending settling fact]
  - Successor chain: ORG-002489 → ORG-002232 (held terminal; conditional where stated).
- **re-point**: Only if the conditional fold is approved: org_id ORG-002489 -> ORG-002232. Do not collapse SITE-002476 into SITE-002200. [conditional on fold]
- Settling fact: An exact registry/name crosswalk tying ORG-002232 legal name to permit owner Luicana Ind Inc, plus establishment evidence for Boyertown and the Macungie street address. Permit is sufficient to correct the mailing/plant conflation now.
- Reproduction/correction: Earlier permit-based Boyertown manufacturing attribution does not reproduce. The opened permit identifies Macungie Borough, Lehigh County as plant location, Boyertown only as owner mailing address.
- Source: [Pennsylvania DEP issued permit39-00025, authorization1509250, PF527016](https://files.dep.state.pa.us/Air/AirQuality/AQPortalFiles/Permits/PermitDocuments/1509250%5B39-00025%5D_Issued_v1.pdf) — Owner Luicana Ind Inc; owner mailing230 E Philadelphia Ave Boyertown; plant Macungie Borough Lehigh County; SIC3088; gelcoat spraying/marble casting; effective2025-08-05, expiry2030-08-05. Permit not proof of present-day operating status.

Borderline calls (not self-ruled):
- Boyertown mailing address cannot establish HQ or manufacturing.
- Permit municipality does not validate 111 Lehigh St.

### PA-10 — STILL_UNCERTAIN
Fresh OSHA canonical /ords route opens and identifies Rehrig Pacific Company at1738 W20thStreet in2015. It does not identify building2 or1739. Own locations page opens but rendered text provides no Erie street detail.

Affected records: `ORG-002318`, `ORG-002319`, `SITE-002296`, `SITE-002297`.
- **annotate**: Mark building2/1739 inference unverified; cited OSHA inspection supports1738 only. Preserve statuses and both sites. [ready for integrator review]
- **fold**: Conditional organization-only fold if exact operator crosswalk is obtained; no site collapse or closure authorized. [held pending settling fact]
  - Successor chain: ORG-002319 → ORG-002318 (held terminal; conditional where stated).
- **re-point**: Only after approved organization fold, point building2 site at held ORG-002318; retain distinct site pending establishment review. [conditional on fold]
- Settling fact: A current company facility plan, county parcel/building record or permit explicitly linking building2/1739 to Rehrig and distinguishing independent establishment from ancillary building.
- Reproduction/correction: Earlier claim that OSHA could not be opened is route-specific, not reproducible generally: /ords/imis route now opens. It still does not support1739/building2 or2026liveness.
- Source: [OSHA inspection1073421.015](https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1073421.015) — Company site1738 W20thStreet Erie; NAICS326199; no building2/1739 identity.
- Source: [Rehrig Pacific company locations](https://www.rehrigpacific.com/about/locations) — Network overview; map addresses not present in extracted text; no street-level support.
- Source: [Rehrig Pacific company history](https://www.rehrigpacific.com/about/history) — Company history; not building2 identity evidence.
- Source: [Rehrig legacy location route](https://www.rehrigpacific.com/locations/) — Route failed; no negative inference.
- Source: [OSHA legacy inspection route](https://www.osha.gov/pls/imis/establishment.inspection_detail?id=1073421.015) — Legacy route failed; canonical /ords opened.

Borderline calls (not self-ruled):
- 1738 versus1739 may be different buildings; names and proximity do not settle establishment grain.
- OSHA case CLOSED means enforcement case closed, not plant closed.

## Independent review corrections
Independent reviewer reproduced PA05 HQ witnesses and PA07 OSHA link. Removed two premature affirmative drafts: PA02 parent address awaiting identity mapping; PA06 historical plan as Hazleton liveness support. Sources remain in ledger and motion rationale, not ingestible support. Final evidence count is29 rows. Added uncertain-submotion settling facts and guard checks for exact JSON/CSV equality,40 unique fingerprints and successfully retrieved witness URLs.
