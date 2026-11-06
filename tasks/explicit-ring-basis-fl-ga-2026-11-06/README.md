# Explicit ring basis — merged FL/GA L7 audit

Controller requested audit and smallcorrectionPR for everymerged site classified via blanket325→Ring2. Acceptance fixed beforeapplication: enumerateall37mergedFL/GAcreates;exact11fallback-derivedsites(FL4,GA7);identifyexplicitSCHEMA2.2basis;append-only evidence;no existingevidence/site edits;fix originalbuildersfallback;knownmap/unresolvedresin regressions;source/ID/census/priorrow/replay checks;validate0;two-familyrefute. Firstuser campaignintegrator2026-11-06;non-use finding2026-11-13.

Pinnedmainbase c2674712c0c9f8aeefac9179597b8a4c6e5eda5f;unused L7 EVD-206000–206010 reserved;noORG/SITEIDs.37creates=17FL+20GA;11fallbackrows=4FL+7GA,all325510/325520 andallalreadyRing2. Thus0incorrectmergedringvalues,11missingexplicitbasisobservations. No325211 mergedcreate inthiscohort. audit.csv lists everyaffectedsite. Existing Ring2 classification fromexactSCHEMA2.2 code is applied,not an owner/schema change. No evidence deletion or edits allowed.

Sources: banked OSHA ITA CY2025 establishment-specific employer filings, official https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv ; controller inherited-packet authorization at observed2026-11-01 remains applicable. Each added row keeps establishment_ID,date_submitted and review2026-11-06. Source is the dated government filing,not our schema or task notes. SCHEMA2.2 supplies the classification rule:325510 paint/coating manufacturing and325520 adhesive manufacture explicitly Ring2; retail/dealer325510 exclusion remains binding. Named plants/manufacturing labels and filedcodes match these11existingCsites. No current-operation,tier,status or exact employment claims added. No own_site rows or newscope/vocabulary ruling.

Correction: append11scope observations (4FL,7GA) that name the exactcode and explicitRing2 activity basis. All earlier evidence retained field-for-field; no existing sitefield changes needed because0ringvalues werewrong. Original FL/GA builders now map the exact supported325212/325510/325520/325991 codes and326 family explicitly;325211/unknowncodes raiseHOLD requiring explicit site/scope interpretation. This fixes the causalblanketfallback without changing any currentlyapproved FL/GA site/evidence output. No newactive-site claims,source upgrades,registry orqualifier changes.

Named checks: python3 tasks/explicit-ring-basis-fl-ga-2026-11-06/check.py PASS37merged-create census/11fallback census,exactsourcecode/evidenceIDbinding,unchangedallprior site/evidence rows,5known mappings and325211/325998/325999 HOLDcontrols inbothbuilders,byte-idempotent evidence replay,and cross-tableIDcollision rejected beforeanywrite. python3 scripts/validate.py PASS0errors. No scripts/ edited; scripts pytest not applicable. Bothfamily refutes pending,draft only. Refresh frommain by taking main evidence shards and rerunning builder; no hand CSVmerge or evidence rewrites.

Affected merged sites (unit: establishments;all existingring2,all correctedbasisRing2):
|Site|State|Name|Filed NAICS|ITA establishment|
|---|---|---|---|---|
|SITE-016001|FL|The Sherwin-Williams Company - Orlando|325510|204465|
|SITE-016004|FL|MAPEI Corporation - Wildwood|325520|1558286|
|SITE-016010|FL|Cork Industries Inc. - Jacksonville|325510|1248403|
|SITE-016011|FL|LATICRETE International, Inc. - West Palm Beach|325520|1454532|
|SITE-016104|GA|The Sherwin-Williams Company - Lawrenceville|325510|208892|
|SITE-016106|GA|Penn Color Inc. - Ringgold|325510|1427307|
|SITE-016108|GA|MAPEI Corporation - Dalton|325520|519695|
|SITE-016109|GA|MAPEI Corporation - Calhoun|325520|1417323|
|SITE-016111|GA|The Sherwin-Williams Company - Covington|325510|345917|
|SITE-016115|GA|The Sherwin-Williams Company - Morrow|325510|208942|
|SITE-016119|GA|Crown USA, Inc. - Thomaston|325510|1336218|
