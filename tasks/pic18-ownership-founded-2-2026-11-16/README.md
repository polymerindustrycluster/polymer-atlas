# PIC-18 ownership and founding, batch 2 — 2026-11-16

Claim: atlas-w16-ownership, controller-assigned second OWN batch. Separate from PR #343, based on current origin/main. First user: PIC member-prospecting owner; review at handoff on 2026-11-16.

Frame: **209 organizations**, whose retained (`status=ok`) pages are **all pass 2**, with a blank ownership_type or year_founded at the git merge-base. The frame has **954 retained pages** and **411 blank organization fields**. It excludes every organization with any retained pass-1 page, regardless of later failures. This is a corpus-conditioned frame, not all PIC-18 organizations.

Applied: **63 field fills across 55 organization rows**: **27 ownership_type** and **36 year_founded** values, with **63 evidence rows** within EVD-373058–373133 (13 withdrawn IDs retired). Existing organization tiers: **25 A, 29 B, 1 C**. **348 fields held**. No organization or site records created/deleted/moved/re-tiered. Organization sources, notes, last_verified and all other cells remain unchanged. The disposition table covers each of the 411 blank organization fields; applied and held are disjoint at that grain.

Sources: the shared retained own-site corpus in controller storage `persist/pic18-corpus-2026-11-16/manifest.csv`. `proposals.json` holds small public witness quotes, URLs, route and hashes; full contact-bearing pages are not committed. **58 field witnesses use direct fetches; 5 use the reader route.** Reader receipts have retained text only (no HTML), and are checked against that text's hash; direct receipts check both raw HTML and text hashes. These routes are distinguished in the packet. A route failure is never absence evidence.

Method: reuse batch 1's builder, evidence pattern and normalized contiguous ordered-word check, itself taken from `tasks/ownership-status-2-2026-11-05/rawcheck_tool.py`. No new dependencies or fetching tools. Explicit own-company statements only: private, family or employee control, or a founding/established/since date referring to the company. No demographic ownership, parent ownership inheritance, or parent/product/facility founding dates. `parent` evidence records ownership control, `existence` records founding identity, following earlier ownership evidence precedent; no parent link is authored. Evidence is append-only via scripts/shard_io.py. Selected years were scanned across all retained pages for competing dates; other-company, certification and staff-tenure dates were excluded.

Checks: `python3 tasks/pic18-ownership-founded-2-2026-11-16/check.py` independently reconstructs frame and page count from the manifest and merge-base, verifies every packet quote/hash and evidence linkage, compares the entire organization-cell delta, and rejects 3/3 injected defects (fabricated quote, altered text hash, forbidden field). `python3 tasks/pic18-ownership-founded-2-2026-11-16/build.py` is idempotent; repeat appends zero evidence rows. Pre-pass byte backups were saved before application in controller `persist/pic18-ownership-founded-2/preimages`; journal pins pre-pass HEAD.

## Review correction

Codex clerk refuted 12 founding-year inferences at dea97f4. Exactly those fills and their new evidence rows are withdrawn; `withdrawn.json` preserves reasons and permanently retired evidence IDs. A further review at 8aa8b3a withdrew Eagle Elastomer ORG-000321 year_founded=1983 and retired EVD-373089. The remaining 63 assignments and their evidence IDs are unchanged. All 36 retained batch-2 founding witnesses and all 28 batch-1 founding witnesses were reread in context: each explicitly states founded/established and refers to the held company. Batch 1 has no same-defect finding and remains unchanged. The builder now rejects year_founded quotes lacking founded/established, with a bare-since injected-defect check. Word presence does not prove founding semantics.

## Proposed follow-ups

- ITEN Industries ORG-000386: retained pages say since 1921 and founded/since 1922. Hold pending explicit reconciliation of the company’s formation date.
- Plastics-R-Unique ORG-000496: innovation since 1979 versus company in Wadsworth since 1991. Ownership applied; founding held until exact formation year is stated.
- Steelastic ORG-000058: ownership by Heico since 1998 is a parent lead, not an ownership_type. Heico's privately held statement is about Heico. Founding 1970 is independently explicit for Steelastic.
- Hygenic ORG-000027: historical 2000 transition to private equity does not settle present control or name a current sponsor; hold.
- Chemionics ORG-000062: explicit privately held statement supports private_company; Chessco subsidiary statement is a separate parent lead, no parent columns changed.
- Nippon Paint Automotive Americas ORG-000464: explicit 2019 entity establishment used; Nippon Paint Group’s 1881 history excluded.
- Youngstown Rubber ORG-001649 pages describe Mid-State Sales; Cru Performance Coatings ORG-001701 describes CPC. Hold inherited ownership/founding facts pending exact-entity confirmation.
- Stuchell ORG-001461 shares CPI page wording; no shared 1994 date applied without an exact-entity statement.
- Micro-Poise ORG-003576: began as family-owned in 1928 is historical ownership, not evidence of current family control.
- All remaining held fields need explicit exact-company primary statements resolving lineage/conflicts. Sources outside the shared corpus, live SEC filings, ownership event histories and exhaustive recovery of held values were not checked. No scripts/ changes: full scripts unit suite not run. Cross-family refutation and merge approval remain with the controller; this is a draft handoff.

## Field dispositions

| Organization | Field | Applied/held | Value or settling fact |
|---|---|---|---|
| ORG-000001 Avient Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000002 The Lubrizol Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000003 The Goodyear Tire & Rubber Company | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000004 Parker-Hannifin Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000004 Parker-Hannifin Corporation | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000011 Bridgestone Americas, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000013 E & T Plastics Mfg. Co., Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000013 E & T Plastics Mfg. Co., Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000018 Ace Rubber Products | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000018 Ace Rubber Products | year_founded | held | The standalone Since 1950 / 75+ years in business claim does not explicitly identify legal-company founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373058. |
| ORG-000027 The Hygenic Corp. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000028 Murdock Industrial Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000028 Murdock Industrial Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000029 Akron Rubber Development Laboratory, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000029 Akron Rubber Development Laboratory, Inc. | year_founded | applied | 1962 |
| ORG-000039 Landmark Plastic Corp. | ownership_type | applied | family_owned |
| ORG-000039 Landmark Plastic Corp. | year_founded | held | Manufacturing specified products in Akron since 1984 dates activity at a location, not company formation. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373061. |
| ORG-000044 APV Engineered Coatings | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000044 APV Engineered Coatings | year_founded | applied | 1878 |
| ORG-000047 Smithers | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000047 Smithers | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000050 Synthomer, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000050 Synthomer, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000058 The Steelastic Company, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000058 The Steelastic Company, LLC | year_founded | applied | 1970 |
| ORG-000061 Ferriot, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000061 Ferriot, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000062 Chemionics | ownership_type | applied | private_company |
| ORG-000062 Chemionics | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000067 R.C. Graham Co. LLC (dba Hand-Tite) | ownership_type | applied | family_owned |
| ORG-000067 R.C. Graham Co. LLC (dba Hand-Tite) | year_founded | held | Family owned and operated since 1965 dates family control/operation, not necessarily founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373066. |
| ORG-000071 Miles Rubber & Packing | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000071 Miles Rubber & Packing | year_founded | applied | 1954 |
| ORG-000073 Professional Plastics | ownership_type | applied | family_owned |
| ORG-000073 Professional Plastics | year_founded | applied | 1984 |
| ORG-000074 MRP Solutions | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000074 MRP Solutions | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000081 Novex Operating Company, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000081 Novex Operating Company, LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000083 Michael Day Enterprises, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000083 Michael Day Enterprises, LLC | year_founded | applied | 1981 |
| ORG-000085 Ohio Precision Molding, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000085 Ohio Precision Molding, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000086 Rubber Associates, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000086 Rubber Associates, Inc. | year_founded | held | Manufacturer/in service since 1953 dates service history rather than explicitly stating founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373071. |
| ORG-000110 Team Plastics, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000110 Team Plastics, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000112 Trico Machine Products Corp. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000112 Trico Machine Products Corp. | year_founded | applied | 1953 |
| ORG-000117 North American Plastics-Chem | ownership_type | applied | private_company |
| ORG-000117 North American Plastics-Chem | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000126 CPI Precision Plastics LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000126 CPI Precision Plastics LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000129 Playground Plastics | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000129 Playground Plastics | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000130 Peak Nano | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000130 Peak Nano | year_founded | applied | 2016 |
| ORG-000131 Tarkett North America | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000131 Tarkett North America | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000134 Novagard Solutions | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000134 Novagard Solutions | year_founded | applied | 1977 |
| ORG-000136 Roto Polymers | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000136 Roto Polymers | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000142 Nordson Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000142 Nordson Corporation | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000150 NSL Analytical Services, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000150 NSL Analytical Services, Inc. | year_founded | held | In business since 1945 establishes operating history, not explicitly legal-company formation. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373076. |
| ORG-000153 Moen Incorporated | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000153 Moen Incorporated | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000154 Lincoln Electric | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000156 Swagelok | ownership_type | applied | private_company |
| ORG-000156 Swagelok | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000157 GrafTech International | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000157 GrafTech International | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000172 Graphic Arts Rubber, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000172 Graphic Arts Rubber, LLC | year_founded | held | Providing rubber compounds since 1971 dates the activity, not explicitly company founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373078. |
| ORG-000181 SpringSeal Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000181 SpringSeal Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000182 Orazen Extruded Polymers | ownership_type | applied | family_owned |
| ORG-000182 Orazen Extruded Polymers | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000190 Clark Rubber & Plastics Co. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000190 Clark Rubber & Plastics Co. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000191 Ohio Elastomers | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000191 Ohio Elastomers | year_founded | applied | 1998 |
| ORG-000193 TMI Inc. | ownership_type | applied | family_owned |
| ORG-000193 TMI Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000201 Ashtabula Rubber Co. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000201 Ashtabula Rubber Co. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000204 Hankook Tire America Corp. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000204 Hankook Tire America Corp. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000209 ABC Plastics | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000209 ABC Plastics | year_founded | applied | 1986 |
| ORG-000225 Allpass Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000225 Allpass Corporation | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000229 American Molded Plastic, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000229 American Molded Plastic, Inc. | year_founded | held | Custom injection molding since 1990 dates an activity, not explicitly company founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373083. |
| ORG-000230 American Wire & Cable Co. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000230 American Wire & Cable Co. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000247 Blade-Tech Industries | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000247 Blade-Tech Industries | year_founded | applied | 1995 |
| ORG-000250 Boardman Molded Products, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000250 Boardman Molded Products, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000255 Buckeye Packaging Co., Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000255 Buckeye Packaging Co., Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000257 BVPV Styrenics LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000257 BVPV Styrenics LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000259 CANTEX Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000259 CANTEX Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000274 Chemsultants International, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000274 Chemsultants International, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000278 Silgan Dispensing | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000278 Silgan Dispensing | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000279 Colonial Machine | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000279 Colonial Machine | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000285 Consolidated Plastics Co., Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000285 Consolidated Plastics Co., Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000290 Cosmo Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000290 Cosmo Corporation | year_founded | applied | 1945 |
| ORG-000291 Creative Packaging Concepts | ownership_type | applied | family_owned |
| ORG-000291 Creative Packaging Concepts | year_founded | held | Family-owned since 1983 dates ownership, not necessarily founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373087. |
| ORG-000311 Drummond Corp. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000311 Drummond Corp. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000318 E.L. Mustee & Sons, Inc. | ownership_type | applied | family_owned |
| ORG-000318 E.L. Mustee & Sons, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000321 Eagle Elastomer Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000321 Eagle Elastomer Inc. | year_founded | held | Since 1983, Eagle Elastomer, Inc. dates operating history; the cited witness is not an explicit founding or establishment statement. Settling fact: explicit same-company founding/establishment statement. Retired EVD-373089. |
| ORG-000322 ECP Corp dba Polycase | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000322 ECP Corp dba Polycase | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000327 Enterprise Plastics Inc. | ownership_type | applied | family_owned |
| ORG-000327 Enterprise Plastics Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000348 Freeman Manufacturing & Supply Company | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000348 Freeman Manufacturing & Supply Company | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000349 Full Circle Technologies | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000349 Full Circle Technologies | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000351 Gem City Plastic Machinery, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000351 Gem City Plastic Machinery, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000354 GMR Companies | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000354 GMR Companies | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000355 Godfrey & Wing | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000355 Godfrey & Wing | year_founded | applied | 1948 |
| ORG-000377 Industrial Technologies, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000377 Industrial Technologies, Inc. | year_founded | applied | 1995 |
| ORG-000386 Iten Industries, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000386 Iten Industries, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000389 J.J. White Products, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000389 J.J. White Products, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000390 J & O Plastics Inc. | ownership_type | applied | family_owned |
| ORG-000390 J & O Plastics Inc. | year_founded | applied | 1982 |
| ORG-000392 Jaco Products Co. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000392 Jaco Products Co. | year_founded | held | Manufacturing precision plastic parts since 1948 dates an activity, not explicitly company founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373095. |
| ORG-000418 Lewart Plastics | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000418 Lewart Plastics | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000419 LG Chem America Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000419 LG Chem America Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000425 M&M Industries, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000425 M&M Industries, Inc. | year_founded | applied | 1986 |
| ORG-000426 MacDivitt Rubber Co. LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000426 MacDivitt Rubber Co. LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000448 Mold Surface Textures LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000448 Mold Surface Textures LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000455 MUM Industries, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000455 MUM Industries, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000464 Nippon Paint Automotive Americas, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000464 Nippon Paint Automotive Americas, Inc. | year_founded | applied | 2019 |
| ORG-000473 Oldcastle Infrastructure (IPG | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000473 Oldcastle Infrastructure (IPG | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000485 Perry Fiberglass Products, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000485 Perry Fiberglass Products, Inc. | year_founded | applied | 1984 |
| ORG-000488 Pharmacy-Lite Packaging | ownership_type | applied | family_owned |
| ORG-000488 Pharmacy-Lite Packaging | year_founded | held | Family-owned manufacturer / serving pharmacies since 1991 dates ownership/service, not explicitly founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373100. |
| ORG-000496 Plastics R Unique | ownership_type | applied | family_owned |
| ORG-000496 Plastics R Unique | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000505 Poly Source LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000505 Poly Source LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000508 Polymer 5 | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000508 Polymer 5 | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000510 Polymer Machinery Consultants, Ltd. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000510 Polymer Machinery Consultants, Ltd. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000533 Laird Performance Materials | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000533 Laird Performance Materials | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000547 LANXESS Rhein Chemie | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000547 LANXESS Rhein Chemie | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000549 Robin Industries, Inc. | ownership_type | applied | employee_owned |
| ORG-000549 Robin Industries, Inc. | year_founded | applied | 1947 |
| ORG-000556 SACO AEI Polymers | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000556 SACO AEI Polymers | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000564 Scott Molders, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000564 Scott Molders, Inc. | year_founded | applied | 1954 |
| ORG-000572 Silco, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000572 Silco, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000573 Silicone Solutions | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000573 Silicone Solutions | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000588 Steere Enterprises, Inc. | ownership_type | applied | family_owned |
| ORG-000588 Steere Enterprises, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000589 The Step2 Company | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000589 The Step2 Company | year_founded | applied | 1991 |
| ORG-000592 Sun State Plastics, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000592 Sun State Plastics, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000617 Tymex Plastics | ownership_type | applied | private_company |
| ORG-000617 Tymex Plastics | year_founded | applied | 2001 |
| ORG-000635 The Wooster Brush Company | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000635 The Wooster Brush Company | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000636 Wrap Tite | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000636 Wrap Tite | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000640 Zehrco-Giancola Composites | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000640 Zehrco-Giancola Composites | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000651 Advanced Drainage Systems, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000651 Advanced Drainage Systems, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000665 Amcor Flexibles North America, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000665 Amcor Flexibles North America, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000666 American Colors Inc. | ownership_type | applied | employee_owned |
| ORG-000666 American Colors Inc. | year_founded | applied | 1975 |
| ORG-000799 Dover High Performance Plastics | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000799 Dover High Performance Plastics | year_founded | held | Supplying components since 1990 dates activity, not explicitly company founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373111. |
| ORG-000813 Edge Plastics | ownership_type | applied | family_owned |
| ORG-000813 Edge Plastics | year_founded | applied | 1975 |
| ORG-000823 SIMONA Boltaron Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000823 SIMONA Boltaron Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000841 Flex Technologies | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000841 Flex Technologies | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-000883 Hub Plastics, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000883 Hub Plastics, Inc. | year_founded | held | Building bottles since 1971 dates activity; the copyright range does not establish company founding. Settling fact: explicit exact-company founding/formation statement. Retired EVD-373114. |
| ORG-000927 Prettl PMA | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-000927 Prettl PMA | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001027 Paramont Machine Company | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001027 Paramont Machine Company | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001078 Rhetech Colors | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001078 Rhetech Colors | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001128 Storopack, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001128 Storopack, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001197 Engineered Plastic Components | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001197 Engineered Plastic Components | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001330 Finite Fiber | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001330 Finite Fiber | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001381 Hyload Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001381 Hyload Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001387 Etched Metal | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001387 Etched Metal | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001390 Interpak, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001390 Interpak, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001393 Kaufman Container | ownership_type | applied | family_owned |
| ORG-001393 Kaufman Container | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001394 Kent Displays, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001394 Kent Displays, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001422 Elster Perfection Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001422 Elster Perfection Corporation | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001431 ABC Packaging Direct, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001431 ABC Packaging Direct, LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001432 Cell-O-Core Company | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001432 Cell-O-Core Company | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001436 Modern Builders Supply, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001436 Modern Builders Supply, Inc. | year_founded | applied | 1944 |
| ORG-001460 Spectrum Dispersions, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001460 Spectrum Dispersions, Inc. | year_founded | applied | 1979 |
| ORG-001461 Stuchell Products, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001461 Stuchell Products, LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001504 THEKEN COMPANIES, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001504 THEKEN COMPANIES, LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001505 VisionAir Solutions | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001505 VisionAir Solutions | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001509 Health-Mor, Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001509 Health-Mor, Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001513 Coltene/Whaledent Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001513 Coltene/Whaledent Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001524 Kapp Surgical, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001524 Kapp Surgical, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001526 Viscus Biologics, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001526 Viscus Biologics, LLC | year_founded | applied | 2012 |
| ORG-001528 Mabel Dental Lab | ownership_type | applied | family_owned |
| ORG-001528 Mabel Dental Lab | year_founded | applied | 2010 |
| ORG-001534 Zimmer Surgical, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001534 Zimmer Surgical, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001546 Earthwalk Orthotics Acquisition Company LLC (Earthwalk Orthotics) | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001546 Earthwalk Orthotics Acquisition Company LLC (Earthwalk Orthotics) | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001551 Volk Optical Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001551 Volk Optical Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001556 FARETEC, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001556 FARETEC, Inc. | year_founded | applied | 1991 |
| ORG-001558 Myrava, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001558 Myrava, LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001565 Automation Plastics Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001565 Automation Plastics Corporation | year_founded | applied | 1980 |
| ORG-001579 CartierWilson LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001579 CartierWilson LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001581 ePac Flexible Packaging | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001581 ePac Flexible Packaging | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001597 International Technical Polymer Systems Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001597 International Technical Polymer Systems Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001600 North Shore Strapping Company | ownership_type | applied | private_company |
| ORG-001600 North Shore Strapping Company | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001601 Pison Stream Solutions Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001601 Pison Stream Solutions Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001602 Royal Powder Corp | ownership_type | applied | private_company |
| ORG-001602 Royal Powder Corp | year_founded | applied | 2001 |
| ORG-001619 SOPREMA Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001619 SOPREMA Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001624 ADVANCED CRYOGENIC ENTERPRISES | ownership_type | applied | employee_owned |
| ORG-001624 ADVANCED CRYOGENIC ENTERPRISES | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001634 ASTRA PRODUCTS OF OHIO LTD | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001634 ASTRA PRODUCTS OF OHIO LTD | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001635 EAGLE PLASTICS GROUP | ownership_type | applied | family_owned |
| ORG-001635 EAGLE PLASTICS GROUP | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001637 FTM ENGINEERING GROUP | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001637 FTM ENGINEERING GROUP | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001641 MAINE RUBBER PREFORMS AND EXTRUSIONS LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001641 MAINE RUBBER PREFORMS AND EXTRUSIONS LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001645 RTS COMPANIES INC. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001645 RTS COMPANIES INC. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001646 TUSCO PRODUCTS | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001646 TUSCO PRODUCTS | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001649 YOUNGSTOWN RUBBER PRODUCTS | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001649 YOUNGSTOWN RUBBER PRODUCTS | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001655 C4 Polymers Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001655 C4 Polymers Inc | year_founded | applied | 1996 |
| ORG-001668 Durable Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001668 Durable Corporation | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001671 FastForming.com LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001671 FastForming.com LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001682 Invisible Repair Products Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001682 Invisible Repair Products Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001691 Mike Cindia Sales Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001691 Mike Cindia Sales Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001694 Novatex North America Inc | ownership_type | applied | family_owned |
| ORG-001694 Novatex North America Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001699 Aerocase Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001699 Aerocase Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001700 Certon Technologies, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001700 Certon Technologies, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001701 Cru Performance Coatings LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001701 Cru Performance Coatings LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001704 Venus Product Development Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001704 Venus Product Development Corporation | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001707 Dyna Flex Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001707 Dyna Flex Inc | year_founded | applied | 1995 |
| ORG-001708 ECM Performance Materials Corp | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001708 ECM Performance Materials Corp | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001709 Goodlevel Enterprises LLC dba The Maple City Rubber Company (TUFTEX Balloons) | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001709 Goodlevel Enterprises LLC dba The Maple City Rubber Company (TUFTEX Balloons) | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001714 AML Industries, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001714 AML Industries, Inc. | year_founded | applied | 1989 |
| ORG-001715 Axion Labs, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001715 Axion Labs, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001720 Sun Art Decals, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001720 Sun Art Decals, Inc. | year_founded | applied | 1975 |
| ORG-001723 P&T Products Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001723 P&T Products Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001730 3D Dental Designs and Development LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001730 3D Dental Designs and Development LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001763 Rubber Mold Design LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001763 Rubber Mold Design LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001779 American Sign Products, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001779 American Sign Products, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001780 American Testing Technologies, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001780 American Testing Technologies, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001788 Colonial Patterns Inc | ownership_type | applied | family_owned |
| ORG-001788 Colonial Patterns Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001793 Custom Tarpaulin Products Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001793 Custom Tarpaulin Products Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001794 Dal-Little Fabricating Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001794 Dal-Little Fabricating Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001808 Eurotech | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001808 Eurotech | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001817 G2 Materials Corp | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001817 G2 Materials Corp | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001829 HP Enterprise Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001829 HP Enterprise Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001830 Impact Sleeve | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001830 Impact Sleeve | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001836 Johnsonite Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001836 Johnsonite Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001911 United Feed Screws, Ltd. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001911 United Feed Screws, Ltd. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001941 Thermo Packaging Suppliers, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001941 Thermo Packaging Suppliers, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001956 Eihinger Machine Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001956 Eihinger Machine Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001963 M S B Machine | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001963 M S B Machine | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-001999 Raydar of Ohio, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-001999 Raydar of Ohio, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002010 Sherwood Advanced Composite Technologies Corp | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002010 Sherwood Advanced Composite Technologies Corp | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002022 The Simplay3 Co | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002022 The Simplay3 Co | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002030 Veretec Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002030 Veretec Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002037 Zing-Pac Inc | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002037 Zing-Pac Inc | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002047 Wayne-Dalton Plastics (Wayne Dalton Corp) | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002047 Wayne-Dalton Plastics (Wayne Dalton Corp) | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002068 Chemstress Consultant Company | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002068 Chemstress Consultant Company | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002134 Pu1Tec Oh LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002134 Pu1Tec Oh LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002137 P & P MOLD & DIE INC. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002137 P & P MOLD & DIE INC. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002146 Altor Solutions, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002146 Altor Solutions, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002158 Dimension Industries, Inc. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002158 Dimension Industries, Inc. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002164 Liberty Mold & Machine Co. | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002164 Liberty Mold & Machine Co. | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002174 Parker Rust-Proof of Cleveland | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-002174 Parker Rust-Proof of Cleveland | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-002948 Covia Holdings LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-003196 Eckart America Corporation | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-003196 Eckart America Corporation | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-003576 Micro-Poise Measurement Systems, LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-003576 Micro-Poise Measurement Systems, LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
| ORG-003771 ST BlowMoulding USA LLC | ownership_type | held | Explicit current control statement about this company, distinguishing parent and historical ownership. |
| ORG-003771 ST BlowMoulding USA LLC | year_founded | held | Explicit exact-company formation/founding year, resolving competing dates and predecessor/parent lineage. |
