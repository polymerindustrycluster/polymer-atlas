# PIC-18 ownership and founding, 2026-11-16

Claim: atlas-w16-ownership, controller-assigned lane OWN. First user: PIC member-prospecting owner; review at handoff on 2026-11-16.

Frame: **419 organizations** present in the shared PIC-18 corpus manifest with at least one `status=ok` retained page and a blank target field at the merge-base. They have **830 blank organization fields**. This is a corpus-conditioned frame, not all PIC-18 organizations. IDs are unique at organization-field grain.

Applied: **58 field fills across 54 organizations**, comprising **30 ownership_type** and **28 year_founded** values, with **58 evidence rows** (EVD-373000–373057). No organization or site was created, deleted, moved or re-tiered. **772 fields held**. The table below gives every blank-field proposal an applied/held disposition; a held field asserts no absence of a fact.

Sources: retained own-site home/about/history pages from the controller's `pic18-corpus-2026-11-16/manifest.csv`. `proposals.json` is the small public witness packet: exact selected quotes, source URLs, raw and text file hashes and paths. No full pages containing contact data are copied into this task. `frame.json` freezes the independent input denominator. Both files are checked against the pinned git merge-base and the external corpus. No new fetching routes or dependencies added.

Method: manually select explicit self-statements, then reuse the normalized contiguous word-sequence method of `tasks/ownership-status-2-2026-11-05/rawcheck_tool.py` (its Windows-only fetch import prevents importing the old module here). The current pass reads the explicitly assigned shared corpus rather than re-fetching. Founding years require an explicit company statement; predecessor, brand, facility and parent dates are held. Ownership never follows from surname, legal form or size. No demographic ownership was populated. As in the earlier ownership passes, evidence uses `parent` for ownership and `existence` for founding/identity; own-site ceiling supports_A, supports_U on U records. No parent linkage is asserted. Organization sources, notes and last_verified are untouched.

Build: `python3 tasks/pic18-ownership-founded-2026-11-16/build.py` (idempotent). Check: `python3 tasks/pic18-ownership-founded-2026-11-16/check.py` (PASS; 3/3 injected defects rejected: fabricated quote, changed text hash, forbidden field). It independently recomputes the frame, checks the complete organization-cell delta, quote and witness hashes, evidence linkage and yield. All selected founding-year candidates were also scanned across retained pages for competing founding/established/formed/since dates; other-company and activity dates were excluded.

## Proposed follow-ups

- Laird Plastics ORG-000059: retained pages say since 1944, 1950 and 1970; hold pending an exact legal-entity founding statement resolving those dates.
- PolyMet Recovery ORG-001868: formation in 2015 versus predecessor dates 1959/1971; recommend owner review of lineage convention before adopting a year.
- Diamond America ORG-000015: 1941 history belongs to Akron Tool & Die; require Diamond America's own formation year.
- Pinnacle Recycling ORG-002038 pages name Rumpke; M. Argueso ORG-002039 pages name Paramelt. Parent/identity leads only; settle exact entity and immediate parent in a separately scoped pass. No inherited ownership or founding year.
- Struktol ORG-000008 pages discuss parent Schill + Seilacher's 1877 history; IML Containers ORG-001389 describes family-owned Lacroix. Parent leads only.
- Remaining blanks need exact-company primary ownership/founding statements. This pass did not exhaust external sources, establish historical ownership changes, or review SEC filings. Independent cross-family review is deferred to the controller; this draft is not merge-approved.

## Field dispositions

| Organization | Field | Applied/held | Value or settling fact |
|---|---|---|---|
| ORG-000005 Day-Glo Color Corp | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000005 Day-Glo Color Corp | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000006 RPM International Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000007 Vibrantz Technologies Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000007 Vibrantz Technologies Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000008 Struktol Company of America LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000008 Struktol Company of America LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000009 Myers Industries Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000009 Myers Industries Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000010 GEON Performance Solutions | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000010 GEON Performance Solutions | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000015 Diamond America Corporation | ownership_type | applied | family_owned |
| ORG-000015 Diamond America Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000025 Musson Rubber Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000025 Musson Rubber Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000026 Enterprise Rubber, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000026 Enterprise Rubber, Inc. | year_founded | applied | 1974 |
| ORG-000030 Piedmont Plastics, Inc. | ownership_type | applied | private_company |
| ORG-000030 Piedmont Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000031 Akron Porcelain & Plastics Co. | ownership_type | applied | family_owned |
| ORG-000031 Akron Porcelain & Plastics Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000033 LyondellBasell | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000033 LyondellBasell | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000034 Akron Polymer Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000034 Akron Polymer Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000036 Win Plastic Extrusions LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000036 Win Plastic Extrusions LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000038 Pioneer Plastics Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000038 Pioneer Plastics Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000041 Next Generation Plastics | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000041 Next Generation Plastics | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000043 Alterra Energy | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000043 Alterra Energy | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000048 Akrochem Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000048 Akrochem Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000051 Continental ContiTech USA | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000051 Continental ContiTech USA | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000052 Harwick Standard Distribution Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000052 Harwick Standard Distribution Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000054 Americhem, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000054 Americhem, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000056 CF Extrusion Technologies | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000056 CF Extrusion Technologies | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000057 Smithers-Oasis Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000057 Smithers-Oasis Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000059 Laird Plastics | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000059 Laird Plastics | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000060 Esterle Mold & Machine Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000060 Esterle Mold & Machine Co., Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000063 Akron Gasket | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000063 Akron Gasket | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000064 Green Technologies of Ohio, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000064 Green Technologies of Ohio, LLC | year_founded | applied | 2010 |
| ORG-000065 Hudson Extrusions, Inc. | ownership_type | applied | family_owned |
| ORG-000065 Hudson Extrusions, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000069 Design Molded Plastics | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000069 Design Molded Plastics | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000072 Cima Plastics Group | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000072 Cima Plastics Group | year_founded | applied | 1976 |
| ORG-000075 Industrial Mold & Machine | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000075 Industrial Mold & Machine | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000077 Mantaline Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000077 Mantaline Corp. | year_founded | applied | 1964 |
| ORG-000078 Giesecke+Devrient America | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000078 Giesecke+Devrient America | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000082 Merryweather Foam, Inc. | ownership_type | applied | family_owned |
| ORG-000082 Merryweather Foam, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000087 Rainbow Rubber Extrusions, Inc. | ownership_type | applied | private_company |
| ORG-000087 Rainbow Rubber Extrusions, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000088 PPG Industries, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000088 PPG Industries, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000098 Spazzolplastica North America LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000098 Spazzolplastica North America LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000101 Polymerics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000101 Polymerics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000105 Transcendia Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000105 Transcendia Inc. | year_founded | applied | 1931 |
| ORG-000106 PharoPLAST | ownership_type | applied | family_owned |
| ORG-000106 PharoPLAST | year_founded | applied | 1972 |
| ORG-000108 HP Manufacturing | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000108 HP Manufacturing | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000113 Custom Rubber Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000113 Custom Rubber Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000115 Cuyahoga Plastics | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000115 Cuyahoga Plastics | year_founded | applied | 1960 |
| ORG-000118 GSH Industries | ownership_type | applied | private_company |
| ORG-000118 GSH Industries | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000119 Mechanical Rubber Ohio LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000119 Mechanical Rubber Ohio LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000124 Prime Conduit Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000124 Prime Conduit Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000132 The Sherwin-Williams Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000133 Oatey Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000133 Oatey Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000135 Valtris Specialty Chemicals | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000135 Valtris Specialty Chemicals | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000138 Permatex | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000138 Permatex | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000140 Cleveland Specialty Products, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000140 Cleveland Specialty Products, Inc. | year_founded | applied | 2009 |
| ORG-000145 Plastics Machinery Group | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000145 Plastics Machinery Group | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000148 WV International | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000148 WV International | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000152 Seglian Manufacturing Group | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000152 Seglian Manufacturing Group | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000169 Zatkoff Seals & Packings | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000169 Zatkoff Seals & Packings | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000174 Vertex, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000174 Vertex, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000176 Kent Elastomer Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000176 Kent Elastomer Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000177 Seal Master Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000177 Seal Master Corp. | year_founded | applied | 1974 |
| ORG-000178 Elbex Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000178 Elbex Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000179 Jet Rubber Company | ownership_type | applied | employee_owned |
| ORG-000179 Jet Rubber Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000180 Enduro Rubber Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000180 Enduro Rubber Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000183 Die-Cut Products Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000183 Die-Cut Products Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000185 anyseals, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000185 anyseals, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000186 SKF USA Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000186 SKF USA Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000188 Universal Polymer & Rubber | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000188 Universal Polymer & Rubber | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000189 GBSA Inc. | ownership_type | applied | family_owned |
| ORG-000189 GBSA Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000194 Salem-Republic Rubber Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000194 Salem-Republic Rubber Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000195 Qualiform Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000195 Qualiform Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000196 Goldsmith & Eggleton | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000196 Goldsmith & Eggleton | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000197 Kenda American Technology Center | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000197 Kenda American Technology Center | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000199 Seaman Corporation | ownership_type | applied | family_owned |
| ORG-000199 Seaman Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000202 Quality Belt Maintenance Ltd. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000202 Quality Belt Maintenance Ltd. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000208 A-ROO Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000208 A-ROO Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000210 Addipel | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000210 Addipel | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000211 Additive Engineering Solutions, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000211 Additive Engineering Solutions, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000216 Aetna Plastics Fabrication | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000216 Aetna Plastics Fabrication | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000223 All Foam Products Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000223 All Foam Products Co., Inc. | year_founded | applied | 1977 |
| ORG-000224 Alliance Equipment Company, Inc. | ownership_type | applied | family_owned |
| ORG-000224 Alliance Equipment Company, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000226 ALTTRAN | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000226 ALTTRAN | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000227 American Foam Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000227 American Foam Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000231 Apollo Plastics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000231 Apollo Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000233 Arc Rubber, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000233 Arc Rubber, Inc. | year_founded | applied | 1965 |
| ORG-000234 Architectural Fiberglass, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000234 Architectural Fiberglass, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000236 Associated Materials, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000236 Associated Materials, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000237 Sealed Air - Automated Packaging Systems | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000237 Sealed Air - Automated Packaging Systems | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000238 Avery Dennison | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000240 Baker Plastics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000240 Baker Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000246 BioThane Coated Webbing | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000246 BioThane Coated Webbing | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000248 Blair Rubber Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000248 Blair Rubber Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000251 Bole Machinery Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000251 Bole Machinery Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000252 The Bonnot Company | ownership_type | applied | private_company |
| ORG-000252 The Bonnot Company | year_founded | applied | 1891 |
| ORG-000258 C.A. Litzler Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000258 C.A. Litzler Co., Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000261 Carbon Polymers Company | ownership_type | applied | private_company |
| ORG-000261 Carbon Polymers Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000262 Carlisle Polyurethane Systems | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000262 Carlisle Polyurethane Systems | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000267 CG Thermal, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000267 CG Thermal, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000268 Chapin Manufacturing, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000268 Chapin Manufacturing, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000273 ChemSpec, Ltd. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000273 ChemSpec, Ltd. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000289 Corrosion Resistant Technologies, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000289 Corrosion Resistant Technologies, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000293 Creative Millwork of Ohio, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000293 Creative Millwork of Ohio, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000299 DCA Construction Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000299 DCA Construction Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000308 Dott Products | ownership_type | applied | family_owned |
| ORG-000308 Dott Products | year_founded | applied | 1989 |
| ORG-000310 Dreco | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000310 Dreco | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000312 Duo-Corp | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000312 Duo-Corp | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000313 DuPont — Valley View (Vespel) plant | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000313 DuPont — Valley View (Vespel) plant | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000315 Dura-Line | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000315 Dura-Line | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000316 Duracote Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000316 Duracote Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000317 Duramax Marine, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000317 Duramax Marine, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000325 Huntsman Advanced Materials Americas LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000325 Huntsman Advanced Materials Americas LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000330 ESI-Extrusion Services, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000330 ESI-Extrusion Services, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000333 Evans Industries | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000333 Evans Industries | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000336 Extrudex | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000336 Extrudex | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000339 Ferry Industries Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000339 Ferry Industries Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000340 Flambeau, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000340 Flambeau, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000341 Flavorseal, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000341 Flavorseal, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000343 Flexsys America L.P. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000343 Flexsys America L.P. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000344 Fomo Products, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000344 Fomo Products, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000360 H.B. Chemical | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000360 H.B. Chemical | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000361 H & B Machine & Tool Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000361 H & B Machine & Tool Co., Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000362 H-P Products, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000362 H-P Products, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000365 Harrison Machine & Plastic Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000365 Harrison Machine & Plastic Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000373 IER Fujikura | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000373 IER Fujikura | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000376 IMS Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000376 IMS Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000378 Infinity Composites Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000378 Infinity Composites Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000379 Infinity Engineered Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000379 Infinity Engineered Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000380 Ingalls Process Equipment Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000380 Ingalls Process Equipment Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000384 Intralox, L.L.C. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000384 Intralox, L.L.C. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000391 JACO Manufacturing Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000391 JACO Manufacturing Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000397 Johnson Brothers Rubber Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000397 Johnson Brothers Rubber Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000399 Joslyn Manufacturing Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000399 Joslyn Manufacturing Co., Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000400 JRM Chemical | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000400 JRM Chemical | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000403 Karman Rubber Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000403 Karman Rubber Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000406 Kent Pultrusion | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000406 Kent Pultrusion | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000407 American Marble Industries | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000407 American Marble Industries | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000409 Keyland Polymer UV Powder, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000409 Keyland Polymer UV Powder, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000410 Killian Latex, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000410 Killian Latex, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000412 Kobelco Stewart Bolling | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000412 Kobelco Stewart Bolling | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000414 Koroseal Interior Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000414 Koroseal Interior Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000416 GLI Pool Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000416 GLI Pool Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000421 The Little Tikes Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000421 The Little Tikes Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000423 LMT Mercer Group | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000423 LMT Mercer Group | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000428 The Malish Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000428 The Malish Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000430 Mar-Bal Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000430 Mar-Bal Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000431 Mercury Plastics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000431 Mercury Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000433 McCann Plastics | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000433 McCann Plastics | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000434 MCI Technologies, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000434 MCI Technologies, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000435 Medco Coated Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000435 Medco Coated Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000438 Mexichem Specialty Resins Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000438 Mexichem Specialty Resins Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000441 Mid-west Poly Pak | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000441 Mid-west Poly Pak | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000442 Middlefield Plastics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000442 Middlefield Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000449 Aptyx | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000449 Aptyx | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000453 Momentous Mold & Machine LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000453 Momentous Mold & Machine LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000454 Montville Plastics & Rubber, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000454 Montville Plastics & Rubber, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000456 NFM / Welding Engineers, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000456 NFM / Welding Engineers, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000457 National Polymer | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000457 National Polymer | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000458 Neff-Perkins Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000458 Neff-Perkins Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000462 Next Dimension Components (current trade name unresolved | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000462 Next Dimension Components (current trade name unresolved | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000468 North American Seal & Supply, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000468 North American Seal & Supply, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000469 Northeastern Plastics International, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000469 Northeastern Plastics International, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000474 ORBIS Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000474 ORBIS Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000480 Palmer Holland, Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000480 Palmer Holland, Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000483 Pentair | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000483 Pentair | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000486 PET Processors LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000486 PET Processors LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000487 The Plastic Forming Company, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000487 The Plastic Forming Company, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000495 MPC Plating, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000495 MPC Plating, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000499 Plastore, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000499 Plastore, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000500 Plastpro 2000 Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000500 Plastpro 2000 Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000506 Greenbridge | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000506 Greenbridge | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000511 Polymer Packaging, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000511 Polymer Packaging, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000512 PolyStamp, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000512 PolyStamp, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000513 Polystar Containment | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000513 Polystar Containment | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000515 Precision Foam Fabrication, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000515 Precision Foam Fabrication, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000520 Premier Equipment | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000520 Premier Equipment | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000522 Premix-Hadlock Composites, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000522 Premix-Hadlock Composites, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000523 Pretium Packaging | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000523 Pretium Packaging | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000525 Profile Plastics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000525 Profile Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000526 Profile Rubber Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000526 Profile Rubber Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000527 Progressive Foam Technologies | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000527 Progressive Foam Technologies | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000528 Promerus | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000528 Promerus | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000529 Prospect Mold, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000529 Prospect Mold, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000530 Protectoplas Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000530 Protectoplas Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000531 Q-Lab Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000531 Q-Lab Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000534 Quality Synthetic Rubber | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000534 Quality Synthetic Rubber | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000537 Rainbow Printing | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000537 Rainbow Printing | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000538 Rapid Molding | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000538 Rapid Molding | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000540 Raven Concealment Systems | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000540 Raven Concealment Systems | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000541 R.D. Abbott Company, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000541 R.D. Abbott Company, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000544 Foundation Wellness | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000544 Foundation Wellness | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000550 Röchling Automotive USA LLP | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000550 Röchling Automotive USA LLP | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000551 Roechling Industrial Cleveland, LP | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000551 Roechling Industrial Cleveland, LP | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000552 Rogers Industrial Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000552 Rogers Industrial Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000553 Royal Plastics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000553 Royal Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000554 RP+M | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000554 RP+M | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000555 Rubbermaid | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000555 Rubbermaid | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000562 Schneller LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000562 Schneller LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000567 Seco Machine | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000567 Seco Machine | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000569 Shin-Etsu Silicones of America, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000569 Shin-Etsu Silicones of America, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000576 Soft-Lite, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000576 Soft-Lite, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000579 Sparton Enterprises, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000579 Sparton Enterprises, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000580 Specialty Hose Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000580 Specialty Hose Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000581 Speed North America | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000581 Speed North America | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000582 Spencer Industries Incorporated | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000582 Spencer Industries Incorporated | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000584 Sprosty Bag Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000584 Sprosty Bag Co., Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000586 Spunfab, Ltd. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000586 Spunfab, Ltd. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000587 Squire, T. L. & Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000587 Squire, T. L. & Co., Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000598 Team Wendy | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000598 Team Wendy | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000600 Technoform | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000600 Technoform | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000601 The Technology House | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000601 The Technology House | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000606 Third Dimension Division | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000606 Third Dimension Division | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000607 Timco Rubber Products, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000607 Timco Rubber Products, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000608 Tomlinson Industries | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000608 Tomlinson Industries | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000610 Tower Industries, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000610 Tower Industries, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000611 Treemen Industries | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000611 Treemen Industries | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000612 Trelleborg Sealing Profiles U.S. Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000612 Trelleborg Sealing Profiles U.S. Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000613 The Trexler Rubber Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000613 The Trexler Rubber Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000614 Tri-Craft, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000614 Tri-Craft, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000616 Tribotech Composites | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000616 Tribotech Composites | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000620 Universal Plastics Group, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000620 Universal Plastics Group, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000623 Uniwall Mfg | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000623 Uniwall Mfg | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000625 Venture Plastics, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000625 Venture Plastics, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000626 Vinylume Products, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000626 Vinylume Products, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000628 Wacker Chemical Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000628 Wacker Chemical Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000629 Walton Plastics | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000629 Walton Plastics | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000631 Wooster Elastomers, LLC | ownership_type | applied | private_company |
| ORG-000631 Wooster Elastomers, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000632 West & Barker | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000632 West & Barker | year_founded | applied | 1971 |
| ORG-000637 Xaloy LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000637 Xaloy LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000638 Yokohama Industries Americas Ohio Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000638 Yokohama Industries Americas Ohio Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000641 Zeiger Industries, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000641 Zeiger Industries, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000660 Alliance Innovations LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000660 Alliance Innovations LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000683 Bostik, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000683 Bostik, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000684 ASK Chemicals LP | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000684 ASK Chemicals LP | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000697 Ball, Bounce and Sport, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000697 Ball, Bounce and Sport, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000698 BASF Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000698 BASF Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000706 Bob Sumerel Tire Co | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000706 Bob Sumerel Tire Co | year_founded | applied | 1968 |
| ORG-000728 Charter Next Generation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000728 Charter Next Generation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000735 LyondellBasell Advanced Polymers Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000735 LyondellBasell Advanced Polymers Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000751 Convertapax | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000751 Convertapax | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000752 Polynt Composites USA, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000752 Polynt Composites USA, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000790 Denney Plastics Machining | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000790 Denney Plastics Machining | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000798 Dover Chemical Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000798 Dover Chemical Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000830 Extol of Ohio, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000830 Extol of Ohio, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000832 FabOhio, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000832 FabOhio, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000868 Guardian Manufacturing Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000868 Guardian Manufacturing Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000870 H.B. Fuller Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000870 H.B. Fuller Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000902 Premere Enterprises, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000902 Premere Enterprises, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000909 Jerico Plastic Industries, Inc. | ownership_type | applied | family_owned |
| ORG-000909 Jerico Plastic Industries, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000911 Johns Manville | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000911 Johns Manville | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000913 JP Industrial Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000913 JP Industrial Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000917 Kar-Del Plastics Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000917 Kar-Del Plastics Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000951 Md Plastics Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000951 Md Plastics Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000955 Meteor Sealing Systems | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000955 Meteor Sealing Systems | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000968 MPS Manufacturing Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000968 MPS Manufacturing Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000997 Ohio Foam Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000997 Ohio Foam Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-000999 Okamoto Sandusky Manufacturing | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-000999 Okamoto Sandusky Manufacturing | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001007 Owens Corning | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001007 Owens Corning | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001033 Plastipak Packaging, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001033 Plastipak Packaging, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001042 Polynew | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001042 Polynew | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001053 ProVia LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001053 ProVia LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001065 R & S Technologies, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001065 R & S Technologies, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001116 Snyder Manufacturing, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001116 Snyder Manufacturing, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001147 CSP | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001147 CSP | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001183 Ventra (Flex-N-Gate) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001183 Ventra (Flex-N-Gate) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001335 Polychem Dispersions, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001335 Polychem Dispersions, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001379 Elyria Plastic Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001379 Elyria Plastic Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001380 Bauer Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001380 Bauer Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001382 SR Products | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001382 SR Products | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001383 Delco, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001383 Delco, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001384 Sterilite Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001384 Sterilite Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001385 Aexcel Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001385 Aexcel Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001386 Ergomat Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001386 Ergomat Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001388 Hy-Ko Products Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001388 Hy-Ko Products Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001389 IML Containers Ohio, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001389 IML Containers Ohio, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001391 KONG Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001391 KONG Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001395 CREO Greenhouse | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001395 CREO Greenhouse | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001396 Sure-foot Industries Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001396 Sure-foot Industries Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001397 PolyKinetix | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001397 PolyKinetix | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001398 Smithers Medical Products, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001398 Smithers Medical Products, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001404 Deflecto, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001404 Deflecto, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001409 American Bath Group | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001409 American Bath Group | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001423 ABC Technologies Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001423 ABC Technologies Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001438 Thogus Products Company | ownership_type | applied | family_owned |
| ORG-001438 Thogus Products Company | year_founded | applied | 1950 |
| ORG-001447 Axalta Coating Systems USA LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001447 Axalta Coating Systems USA LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001454 IMCD US | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001454 IMCD US | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001459 RFD Beaufort Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001459 RFD Beaufort Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001462 Clevite Elastomers Technical Center (Tenneco) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001462 Clevite Elastomers Technical Center (Tenneco) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001465 Chalfant Sewing Fabricators Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001465 Chalfant Sewing Fabricators Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001466 Henkel Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001466 Henkel Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001470 The Pittsburgh Paint Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001470 The Pittsburgh Paint Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001472 ChemMasters Inc. | ownership_type | applied | family_owned |
| ORG-001472 ChemMasters Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001475 ChromaScape, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001475 ChromaScape, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001477 Aurora Material Solutions | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001477 Aurora Material Solutions | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001490 Chardon Custom Polymers | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001490 Chardon Custom Polymers | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001501 Polymer Valley Chemicals Inc. | ownership_type | applied | private_company |
| ORG-001501 Polymer Valley Chemicals Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001506 ValenSil Technologies, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001506 ValenSil Technologies, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001507 HOYA VISION CARE - CLEVELAND | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001507 HOYA VISION CARE - CLEVELAND | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001508 ICHOR VASCULAR INC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001508 ICHOR VASCULAR INC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001514 Julius Zorn, Inc. (Juzo USA) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001514 Julius Zorn, Inc. (Juzo USA) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001515 S4 Medical Corp | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001515 S4 Medical Corp | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001523 Centerline Biomedical, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001523 Centerline Biomedical, Inc. | year_founded | applied | 2015 |
| ORG-001525 SPR Therapeutics, Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001525 SPR Therapeutics, Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001538 Perma Laboratories LLC | ownership_type | applied | family_owned |
| ORG-001538 Perma Laboratories LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001541 AlphaMicron Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001541 AlphaMicron Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001548 Frantz Medical Development Ltd. (Frantz Medical Group) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001548 Frantz Medical Development Ltd. (Frantz Medical Group) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001549 STERIS Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001549 STERIS Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001550 United States Endoscopy Group, Inc. (STERIS Endoscopy) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001550 United States Endoscopy Group, Inc. (STERIS Endoscopy) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001555 Synapse Biomedical Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001555 Synapse Biomedical Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001557 MatPLUS, LTD | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001557 MatPLUS, LTD | year_founded | applied | 2004 |
| ORG-001570 GHSP | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001570 GHSP | year_founded | applied | 1924 |
| ORG-001573 Prentke Romich Company | ownership_type | applied | employee_owned |
| ORG-001573 Prentke Romich Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001577 Master Builders Solutions US LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001577 Master Builders Solutions US LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001578 Bright Idea Shops LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001578 Bright Idea Shops LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001580 Chemical Solvents Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001580 Chemical Solvents Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001583 Grand River Rubber & Plastics Company | ownership_type | applied | employee_owned |
| ORG-001583 Grand River Rubber & Plastics Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001585 High Tech Extrusions Ltd | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001585 High Tech Extrusions Ltd | year_founded | applied | 1997 |
| ORG-001588 The Kent Mold & Manufacturing Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001588 The Kent Mold & Manufacturing Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001589 The Ruscoe Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001589 The Ruscoe Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001590 Therm-O-Link Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001590 Therm-O-Link Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001591 Winsell Incorporated | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001591 Winsell Incorporated | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001592 Alpha Tool & Mold Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001592 Alpha Tool & Mold Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001595 Eleven 10 LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001595 Eleven 10 LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001596 Gateway Products Recycling Inc | ownership_type | applied | family_owned |
| ORG-001596 Gateway Products Recycling Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001598 J B Jewitt Co Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001598 J B Jewitt Co Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001603 Speedline Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001603 Speedline Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001607 Kinetico Incorporated | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001607 Kinetico Incorporated | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001609 Morgan Adhesives Company, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001609 Morgan Adhesives Company, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001622 ABSOLUTE POLYMERS INC | ownership_type | applied | family_owned |
| ORG-001622 ABSOLUTE POLYMERS INC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001630 AKRON BELTING & SUPPLY CO | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001630 AKRON BELTING & SUPPLY CO | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001636 ENGINEERED LAMINATES & COATINGS | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001636 ENGINEERED LAMINATES & COATINGS | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001639 PLASTIC ENTERPRISES | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001639 PLASTIC ENTERPRISES | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001642 MOTIVO DISPLAY SOLUTIONS | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001642 MOTIVO DISPLAY SOLUTIONS | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001643 OVERMOLD EXPRESS | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001643 OVERMOLD EXPRESS | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001644 RPM INDUSTRIES | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001644 RPM INDUSTRIES | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001647 V&A PROCESS | ownership_type | applied | family_owned |
| ORG-001647 V&A PROCESS | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001648 WORTHINGTON PRODUCTS | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001648 WORTHINGTON PRODUCTS | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001653 Bruns Brush Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001653 Bruns Brush Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001656 ClearSonic Manufacturing Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001656 ClearSonic Manufacturing Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001657 Comdess Company Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001657 Comdess Company Inc | year_founded | applied | 1981 |
| ORG-001665 Dischem International Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001665 Dischem International Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001666 Drossbach Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001666 Drossbach Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001667 Dudick Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001667 Dudick Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001670 Enpac LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001670 Enpac LLC | year_founded | applied | 1988 |
| ORG-001679 Hollo Plastics Equipment Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001679 Hollo Plastics Equipment Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001681 Inter-Ion Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001681 Inter-Ion Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001702 J T Adams Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001702 J T Adams Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001717 FlexLink, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001717 FlexLink, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001725 Thorworks Industries Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001725 Thorworks Industries Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001728 Buckeye Medical Technologies LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001728 Buckeye Medical Technologies LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001739 API II, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001739 API II, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001740 Auto Technology Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001740 Auto Technology Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001742 Global Waste and Recycling LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001742 Global Waste and Recycling LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001744 Jet Di, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001744 Jet Di, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001745 J.G. Sales Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001745 J.G. Sales Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001747 P3 Infrastructure Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001747 P3 Infrastructure Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001748 PKG, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001748 PKG, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001749 Standards Testing Laboratories, Inc. | ownership_type | applied | family_owned |
| ORG-001749 Standards Testing Laboratories, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001753 Foundation Industries Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001753 Foundation Industries Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001755 Medina Recycling Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001755 Medina Recycling Inc. | year_founded | applied | 1973 |
| ORG-001757 ACO Polymer Products, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001757 ACO Polymer Products, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001758 Niles Building Products Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001758 Niles Building Products Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001760 Pioneer Manufacturing Company, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001760 Pioneer Manufacturing Company, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001768 Action Super Abrasive Products, Inc. | ownership_type | applied | private_company |
| ORG-001768 Action Super Abrasive Products, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001769 Adherex Packaging | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001769 Adherex Packaging | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001774 Alcon Tool Co | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001774 Alcon Tool Co | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001776 S. Slesnick Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001776 S. Slesnick Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001777 American Consolidated Industries Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001777 American Consolidated Industries Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001781 Astro Manufacturing & Design Corp | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001781 Astro Manufacturing & Design Corp | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001783 Beacon Gasket & Seals Co | ownership_type | applied | family_owned |
| ORG-001783 Beacon Gasket & Seals Co | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001784 BF Plastics Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001784 BF Plastics Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001787 Circle Mold & Machine Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001787 Circle Mold & Machine Inc | year_founded | applied | 1966 |
| ORG-001791 Cosar Mold Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001791 Cosar Mold Inc | year_founded | applied | 1985 |
| ORG-001806 ENPRESS LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001806 ENPRESS LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001807 The Euclid Chemical Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001807 The Euclid Chemical Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001810 Expert Gasket & Seal LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001810 Expert Gasket & Seal LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001826 Hapco Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001826 Hapco Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001855 NewKor Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001855 NewKor Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001856 Novation Solutions LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001856 Novation Solutions LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001859 OEM/Miller | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001859 OEM/Miller | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001868 PolyMet Recovery LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001868 PolyMet Recovery LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001869 Pro-Line Automation Systems Ltd. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001869 Pro-Line Automation Systems Ltd. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001879 Rainbow Master Mixing LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001879 Rainbow Master Mixing LLC | year_founded | applied | 1983 |
| ORG-001883 Rezkem Chemicals | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001883 Rezkem Chemicals | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001892 Schibley Solvents and Chemicals Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001892 Schibley Solvents and Chemicals Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001905 Thermoprene Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001905 Thermoprene Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001908 Tremco CPG Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001908 Tremco CPG Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001916 Zero D Products Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001916 Zero D Products Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001922 Faull and Son | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001922 Faull and Son | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001927 GlueTread LLC | ownership_type | applied | family_owned |
| ORG-001927 GlueTread LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001928 Green Processing Company Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001928 Green Processing Company Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001930 Industrial Thermoset Plastics (IT Plastics) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001930 Industrial Thermoset Plastics (IT Plastics) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001936 Rotocast Technologies, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001936 Rotocast Technologies, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001937 Smetzer's Tire Center, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001937 Smetzer's Tire Center, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001947 AAM Mold and Machine LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001947 AAM Mold and Machine LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001949 Akron Steel Fabricators Co. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001949 Akron Steel Fabricators Co. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001957 Friess Equipment Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001957 Friess Equipment Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001958 ICS Laboratories Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001958 ICS Laboratories Inc | year_founded | applied | 1995 |
| ORG-001959 Jax Mold and Machine Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001959 Jax Mold and Machine Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001978 Sprayworks Equipment Group, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001978 Sprayworks Equipment Group, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001986 Optimax Plastic LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001986 Optimax Plastic LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001992 Precision Polymer Casting LLC (dba Castinite) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001992 Precision Polymer Casting LLC (dba Castinite) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-001998 R A M Plastics Co Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-001998 R A M Plastics Co Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002007 S&A Industries Corporation | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002007 S&A Industries Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002014 Stroup & Son Ltd | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002014 Stroup & Son Ltd | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002018 Telar Corp. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002018 Telar Corp. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002034 Whip Guide Company | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002034 Whip Guide Company | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002038 Pinnacle Recycling, LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002038 Pinnacle Recycling, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002039 M. Argueso & Co., Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002039 M. Argueso & Co., Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002043 Mitsubishi Chemical America, Inc. (Bellevue Plant) | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002043 Mitsubishi Chemical America, Inc. (Bellevue Plant) | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002053 STUCK LLC | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002053 STUCK LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002056 P & E Sales Ltd. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002056 P & E Sales Ltd. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002067 Aropha Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002067 Aropha Inc. | year_founded | applied | 2021 |
| ORG-002069 Summit Glove, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002069 Summit Glove, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002135 Applied Specialties Inc | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002135 Applied Specialties Inc | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002136 Kongsberg Automotive | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002136 Kongsberg Automotive | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002153 Checkpoint Systems | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-002153 Checkpoint Systems | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-002922 Absolute Haitian Corporation | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-003030 Budenheim USA, Inc. | ownership_type | held | Explicit current statement of this company’s control; distinguish parent/customer statements. |
| ORG-003030 Budenheim USA, Inc. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-003545 G-3 Chickadee Purchaser, LLC | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-003746 Goodyear Chemical | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-004022 VMI Holland B.V. | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
| ORG-004026 Anderson International Corp | year_founded | held | Explicit founding/formation year for this company, resolving any lineage or conflicting dates. |
