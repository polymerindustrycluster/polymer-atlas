# CA CORROBORATED batch1, revised after Codex refute

Controller-designated L6 application; first user: campaign integrator2026-11-06; non-use finding2026-11-13.40contiguous ranked core clusters selected from262CA CORROBORATED: core prefixes3252/3261/3262/325991, score descending, cluster_id ascending. Revised verdicts:19VERIFIED establishment proposals/21STILL_UNCERTAIN. This supersedes the initial20/20 counts.

Application:10new parent organizations atC,19CA sites(16C/3B),151evidence rows. No pre-existing main evidence row is edited/deleted. Unmerged proposals are rebuilt through build.py; reserved-ids.json fixes issued record/evidence allocations across revisions. Mission ORG-010006/SITE-014012 and its evidence slots are permanently retired from this packet, never reassigned. EVD-181000 adds SSI's primary address witness. Main's LF federal-frame files were taken under controller06:12 authority; net diff to main is zero.

## Evidence and scope

Sources: inherited OSHA ITA CY2025 and inspection packets at2026-11-01 vintage, reviewed2026-11-06 (controller grant, relayed by L7/BOARD). ITA citations include the actual CY2025 largefiles URL, establishmentID and submission date. Federal classifications support provisionalC scope only, neverB or inferred capabilities. B requires raw, site-applicable own scope evidence. County/HQ/current-status unknown are deliberate nonclaims; no permit or historic inspection is treated as proof of current operation. ParentC at birth follows STRONG convention.12 reliable ITA site bands remain directly sourced; CalSpas conflicting size code is held unknown; no plan-participant counts used. ECHO/FRS and exact same-address extra federal-frame IDs are notes only; no FRS REST or registry_links writes.

Domain/name/street/trade-name dedupe is in dedupe.json. Known domains ADS→ORG-000651,Graham→ORG-001403,CA Mercury→ORG-007413(not unrelated OH Mercury). Generic Madera/Modesto aliases use ITA company_name. North Maple OSHA witness in Dart cluster is explicitly excluded; only South Maple supports the site. Cytec latest325998 is held. Remaining holds include conflicting/uncertain operators, employer-only witnesses, code/scope conflict and Oroville WARN outcome. Settling facts are in verdicts.csv; no owner scope/ring/vocabulary exception is applied.

## Codex refutation and corrections

Original independent Codex deep review REFUTE is preserved in review-codex-1.md;20/20 blind federal rows inspected,0missing, all provisionalC on their face. Findings:

1. Mission Ontario: live homepage https://www.missionplastics.com/ re-fetched raw2026-11-06 explicitly places manufacturing in Mexicali and technical support in Rancho Cucamonga. Historic Ontario inspection does not resolve current site applicability. Held, not declared closed. Its unmerged org/site/evidence proposals removed; IDs permanently reserved.
2. SSI: ITA says1310ThurmanRd; current operator contact page explicitly prints1310ThurmanStreet,LodiCA95240. Corrected proposed physical street to primary wording under lane brief's own-address correction rule; EVD-181000 cites contact page. address-rawcheck.csv records successful raw word check/hash. No street-equivalence assumption or external-geocoder inference.
3. Federal scope strength: classification-only scope rows now supports_C regardless of selected site tier; separate own scope witnesses alone supplyB. Mutation removes all3own scope witnesses; validator now fails all3Bsites. This fixes the shared builder defect, not only four rows.

Quotes were re-fetched via curl browser UA; W matcher from evidence-repair-2/prep.py is reused. Four original own quotes/hashes matched in independent Codex review, but Mission quote failed semantic site applicability. The main update now supplies the originally missing ownership-status-2 rawcheck tool; the earlier fallback reflected the prior checkout, not a permanent platform gap.

## Checks and pending gate

`python3 scripts/validate.py`:0errors/OK. `python3 tasks/corroborated-ca-tx-2026-11-06/check.py`:40unique verdicts,19/19source census, byte-identical replay, scope-removal mutation rejected. `python3 scripts/shard_io.py`:PASS. Initial duplicate-verdict mutation41rows/40IDs rejected. All original main rows compared by ID unchanged; append_sorted can reorder historical unsorted evidence without value edits.

Strict NAICS326 US sites(A/B/C,statusactive/unknown)75→93/1306QCEW2023private establishments:5.7427%→7.1210%,+18strict326 and1site325212. Count ratio, not matched census coverage. New parent/site/evidence IDs stay inside controller block. Known source errors (CalSpas awnings classification, VM Church spelling) are not upgraded into capabilities; CalSpas size-band fill is held unknown.

Draft PR135 remains unapproved. Corrected19-create census and two-family rereview pending. Controller05:55/06:25 clerk routing supersedes council-only/pre-draft gates. No merge or tracker state change.

Final technical reviews at cf2e185: Codex(OpenAI) APPROVE,0blocking findings, full19-source census and3scope-removal mutation validated; report controller storage reviews/135-clerk-codex-4.md. Grok APPROVE,0findings, full19/19blind census and primary pages refetched; report reviews/135-clerk-grok-2.md. Controller requested merge-current-main integration without new review if lane delta stays identical. Main data files taken and builder replayed; all10org/19site/151EVD lane rows compared byte-for-field against approved cf2e185 unchanged. Local check.py/validate pass after integration. No merge to main performed by lane.
