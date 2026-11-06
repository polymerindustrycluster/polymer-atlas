# L3 CORROBORATED MO/SC — corrected final packet

All143 CORROBORATED establishment clusters(MO63,SC80) appear exactly once:9 VERIFIED(MO4,SC5),134 STILL_UNCERTAIN(MO59,SC75),0 DUPLICATE_OF/REJECT. Creates9 provisionalC/operating_status unknown sites under held operators,0 organizations. Adds67 evidence observations(63siteC+4primary-government registrant identityA);four held organization trade_names fields gain actual filed company names. No other old field/tier/status/registry/qualifier/graph change. Full9-create source census is blind-full-census.csv; every create was independently reviewed. LA42,MN119,NJ91 are separate PRs198/202/204.

## Source and creation gates

Source: controller-admitted banked public OSHA ITA CY2025 establishment extract; packet observed2026-11-01/reviewed2026-11-06. Official source URL keyedestablishment_ID on every observation. No fresh federal download,own-site witness or present-day operation asserted. Every new site remainsC/unknown; primary registrant identity supports_A is claim-local and changes no held tier. County remains unset.0newown_site rows meets controller07:20 pagefacts-only rule.

Filed company_name must independently match exactly one active surviving held legal/trade identity, not merely a plant/parent label. Reliable consistent street/state/code and explicit polymer manufacture required. House domain/name/trade/street/successor dedupe across all shards before every create. Nonempty normalized street keys required; parent/locality blank-street overlap blocks create. Known3 held operators(Plastipak,NikeIHM,Hydrite) and ambiguous-alias negative pass before matcher use. No new network fetcher/matcher.

Acceptance/firstuser/ID allocations in LANE_BRIEF.md. Stable SITE012100+inputindex, EVD300000+20*index under controller300000–309999 grant; fixedunusedgaps permanent. Main merge/restore/baseline all use the same pinned SHA in baseline.json, never a moving origin/main ref. Canonical files restored from that main and builder replayed, no hand CSV merge. Historical checkpoints in pass-journal.md are superseded by this README.

## Refute findings and holds

| Finding / cluster | Final verdict and settling fact |
|---|---|
| Grok3 REFUTE,LF-MO-00380 Aurora | STILL_UNCERTAIN. Need held-operator identity at #6CapperDrive PacificMO. House normalizer strips leading hash to empty; empty-v-empty cannot link to Avient SITE002896. No target/create. Lane nonempty-key guard and exact false-link injection added. |
| Codex3 REFUTE,LF-SC-00287 Cooper River | STILL_UNCERTAIN. Need primary reconciliation of surviving/restarted polymer manufacturing after reported PET halt/production transfer and subsequent decommissioning/dismantling/remediation. Later OSHA filing alone does not settle activity. |
| LF-MO-00442 Crown Festus | Legal/operator continuity between lamp-shade filing and held Ohio UHMW maker. |
| LF-SC-00014 Duncan Innovation | Resolve production plant versus innovation/R&D function. |
| Remaining130 holds | Named activity/address/identity settling facts in verdicts.csv; no closure/absence inference or self-ruled scope/ring. |

Cooper River evidence: freshly curl/browser-UA fetched two own-issued Alpek PDFs, bothHTTP200. 4Q2023 results physicalp4 report PET halt and completed transfer of production.2025annualreport physicalp80/note2(f) reports decommissioning/dismantling,environmentalcleanup/remediation and closure costs. Raw quotes match using calibrated STRONG/evidence-repair token matcher; fabricated suffixes rejected. URLs/PDFsizes/SHA256/page/quotes in cooper-river-rawcheck.json. These facts establish a contradiction to reconcile, not authority to close/reject the address or infer all activity ceased. AGENTS2.8–9/3/4 govern. No status changes applied; Form5500 closure-reject gate not invoked because this is a hold, not a closure REJECT.

Unmerged proposed SITE012208 and EVD302160–302166 are withdrawn by fresh-main builder regeneration and remain permanent unused IDs. No evidence row present on the pinned main is edited/deleted. Cooper River is325211, so withdrawing it changes no strict326 numerator. Full initial10-create audit becomes final9-create census plus1held conflict. All other nine create facts remain unchanged. This correction supersedes10V133U/10sites74EVD in prior checkpoints.

## Counts and checks

| State | Clusters | VERIFIED / holds | New C/unknown sites | New evidence | Strict326 before→after / QCEW2023 |
|---|---:|---:|---:|---:|---:|
| MO |63|4 /59|4|31(28siteC+3identityA)|43→47 /368|
| SC |80|5 /75|5|36(35siteC+1identityA)|52→57 /406|

Count ratios MO11.68→12.77%,SC12.81→14.04%; numerator active/unknown US A/B/C primaryNAICS326 establishments, denominator QCEW2023private326. Ratios are counts, not matched establishment coverage. Delta+4/+5 reconciles exactly to the9creates, all now326.

Named runnable checks:
- `python3 tasks/corroborated-mo-sc-2026-11-06/prep.py` reproduces143input/verdict/dedupe/knownanswers, excluding this lane's own creates on replay.
- `python3 tasks/corroborated-mo-sc-2026-11-06/build.py --state MO --apply`, thenSC, idempotent sorted appends with globalID/uniqueoperator preflight.
- `python3 tasks/corroborated-mo-sc-2026-11-06/check.py --negative-controls`: exact143census/3censusdefects,Aurora false-link regression,9Cunknownsites/67source-boundEVD,retiredCooperIDs absent,globalreservedIDs/T3; SITE/EVD cross-shard duplicates and ambiguous company fail beforewrites. Exact refuted Cooper create re-enabled in isolated packet must fail manualhold before ANY write; tempCSVhashes unchanged.
- `python3 scripts/validate.py`:0errors required; alloldcanonicalrows preserved exceptsame4aliasfields; allCSVreplay byte-identical.

Codex3/OpenAI REFUTE on c9adf8a accepted/cured; both targeted families now approve, as recorded below. Earlier Grok3 Aurora finding also accepted/cured. No final two-family approval/Done claim. No shared scripts changed; fullscripts pytest and fresh bulk federal/current-operation checks not performed. The banked-vintage/provisional-tier limits remain.

Executed corrected-tree checks PASS: pinnedmain43326cd alloldcanonicalrows preserved except4aliasfields,exact10datafiles/9newsites/67EVD,allCSVreplaybyte-identical;exactrefutedCooperproposal andother3no-writefaults rejected;validator0errors. Freshprimary2PDFquotes+2fabricatedsuffixnegativesPASS.

Grok/xAI targeted re-review: APPROVE,0findings ona6f98e9 (clerk-grok-3,thr_4g4uwqjxjv);report controller reviews/164-clerk-grok-3-rereview.md. Independently confirmed Aurorahold/street_hits empty/exactbadlinkinjection rejects,CooperRiverhold/retiredIDsabsent+neveronmain/all9survivorsfield-identicaltopriorhead/no closureREJECT. Raw2AlpekPDFs200/SHA/quotes+fake-suffixnegative andexactCooperrecreatebeforewritefault PASS. checknegativecontrols9V134U0D67EVD/T3MO43→47SC52→57/replaypending0/validator0/rowloss PASS. Codex3 targeted approval subsequently received below. This receipt update changesREADMEonly,data/code unchanged.

Codex/OpenAI targeted re-review: APPROVE,0 blocking findings on720322f(payload a6f98e9),clerk-codex-3/thr_jukpm97t9c. Report controller reviews/164-clerk-codex-3.md supersedes sole Cooper River REFUTE. Independently re-enabled exact VERIFIED Cooper proposal; actualSCbuilder manualhold rejects beforeANYCSVwrite. BothAlpekPDFs200/exactSHA/wordsinorder/p4p80+fake-suffixnegativesPASS. Recomputed143=9V134U0D,9Cunknownsites67EVD63siteC4identityA0org,all9sites67EVDfield-identicalc9adf8a,oldrowspreservedexcept4aliases,replayallCSV/exact10files/strictMO43→47SC52→57/checkfourfaults/validator0/rowlossPASS. Targeted limits: unchangednine currentoperations/sourcecensus not freshly researched. Grok3APPROVEa6f98e90findings alreadyrecorded; samepayload. NoclosureREJECT/statuschange.

Final integration after both approvals: pinnedmain29ee5d8,ALLcanonicalfilesrestoredfromthatSHA then unchangedbothstatebuilders replayed. ALL76approvedSITE/EVDrowsfield-identical,exact10datafiles/9sites67EVD4aliascells;everyothermainrow/EVDpreserved,includingNC/OH/SCadditions/corrections. CooperRiverSITE012208/EVD302160–166absentglobally,permanentunused;Aurorastaysholdnorepoint. Check143/source/globalIDs/fourno-writefaults/T3/allCSVbyte-identicalreplay/validator0PASS. No newfacts beyond approvedpacket;controllermerges/statuses.
