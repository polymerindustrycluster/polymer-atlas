# D10 federal-program anchors — 2026-11-06

Controller assigns agent/codex/federal-programs, ORG013300–013399 / EVD296000–296999, delegated application under AGENTS §2.7. Reservation recorded on BOARD before work; new branch off main. SPEC.md records acceptance. Branch history is the pre-pass backup; this folder is the packet/pass journal. Only ecosystem.csv and evidence_ecosystem.csv change.

First user: PIC staff locating manufacturing/federal support anchors. Non-use review2026-12-06; no use or current funding commitment claimed.

## Census and additions

Unit/filter:12 selected institution/program/network candidates from the controller's named targets plus NEPIRC, not companies or an inventory of every regional MEP affiliate. 1VERIFIED,5DUPLICATE_OF,6STILL_UNCERTAIN; zeroREJECT. inputs.csv/verdicts.csv reconcile exactly by candidate_id.

| Candidate family | Candidate units | New ecosystem rows | Held duplicates | Holds |
|---|---:|---:|---:|---:|
| MEP institutions/networks/units |6|0|1|5|
| Manufacturing USA institutes |5|1|3|1|
| Sustainable Polymers Tech Hub |1|0|1|0|
| Total |12|1|5|6|

Canonical additions:1 tier-C ecosystem institution, LIFT ORG-013300 (Detroit, Michigan, Wayne), and5 append-only ecosystem evidence rows EVD-296000–296004. New A/B/U rows0; existing canonical row edits0. No tier/status change, organization-shard/site/program/registry/derived-column change or inclusion_log entry. New ecosystem subtype count: nonprofit_rd_consortium1 ecosystem row.

Duplicates terminate at held MAGNET ORG000159; IACMI ORG002099; America Makes ORG001217; REMADE ORG002100; Sustainable Polymers Tech Hub ORG002825. No source/tier/location/status/funding fact is applied to those rows. Both EDA/Ohio hub designations already ride one held Tech Hub record; its existing Chamber parent is preserved.

## LIFT scope and provenance

The own homepage states LIFT's ALMMII operator and nonprofit public-private identity. Its own resources page offers members access to named high-bay resources and collaboration with LIFT experts. It explicitly names Plasmatreat Cell and Hot Isostatic Processing, treatment of plastics, and processing of polymer powders. These concrete named member services support §1/§4.6's named-service test; a generic advanced-manufacturing mission alone would not suffice. polymer_program_name records both published service names, with the own resources URL. No polymer-exclusive mission or unobserved degree/project is asserted.

Typed scope observations cover nonprofit_rd_consortium, polymer_program=true, generalist=false (research institute with named material services, not a geographic generalist EDO), facilities access/technical assistance, national geography and the description. The homepage's national-institute statement supports geography. The own facilities page labels Detroit headquarters and publishes1400 Rosa Parks Boulevard, Detroit MI48216. County Wayne comes from a Census address-geography match: exact matched address/one county/GEOID26163. Only street/city/state/county text is used; no coordinates are inspected, copied or used for verification tier. Source_class government_filing uses §4.13's “government record of fact” branch, not a corporate-filing assertion.

All5 observations use supports_C, consistent with AGENTS §3 new-create C/U. Statusunknown: no liveness, current federal grant amount or funding commitment is asserted. Evidence existence/address/scope cover every populated substantive field; observation dates, author and tier are researcher metadata.

Dedupe: house atlas.py across all organization shards/ecosystem by domain/name/street/trade names, including LIFT, ALMMII, full American Lightweight Materials Manufacturing Innovation Institute, and former Lightweight Innovations for Tomorrow. No hits before creation. Builder reuses atlas.load_tables/dedupe on the actual data tree and preflights global ORG/EVD namespaces before writing. shard-of --hq-state MI was run (shard-reference.json); §4.6 Ring5 institutions remain in unsharded ecosystem.csv, with evidence_ecosystem.csv, rather than organization state shards.

## Owner battery and holds

Controller explicitly agreed the first two hold families and will carry them into the battery. No scope/grain/vocabulary ruling is self-applied.

| Item | Governing rule and recommendation | Settling decision |
|---|---|---|
| B-D10-GEN: out-of-state generalist MEPs | §1 Ring5 item2 admits in-scope generalist EDO/workforce entities; §4.6 says polymer_program=false only for NE Ohio generalists. Hold PA/MI/IN generalist-only creates. | Owner explicitly settles geographic exception, or own named polymer service is verified. Legacy false/state rows are not authority for a new exception. |
| B-D10-GRAIN: Ohio/institution-hosted MEP units | §4.6 ecosystem grain excludes program; §4.11 governs program rows. Ohio MEP is a program-grain candidate; Purdue MEP is a named unit of held Purdue ORG004662. Ohio own route failed, so its reading remains a lead. Recommend host annotation or lawful program after grain/type/host evidence is settled. | Owner names permitted representation. No separate institution, invented office grain or unallocated PROG ID here. |
| B-D10-GEO: NEPIRC | Own online training explicitly names Plastics Processing; own contact places office at Hanover Township PA. Its multi-county PA service lacks an unambiguous §4.6 geography_served token (site_local/county/ne_ohio/ohio/national/international). | Recommend dated US-state values with narrower service region stated, or explicitly define county for multi-county service. Do not copy legacy pennsylvania or invent national reach. |

Six STILL_UNCERTAIN candidates:
- Ohio MEP: lawful program/host representation and reachable own source.
- Pennsylvania MEP: generalist geographic ruling or own named polymer offer.
- Michigan Manufacturing Technology Center: same ruling or material-specific pathway; generic additive manufacturing is not assumed polymer training.
- Purdue MEP: host/program grain and generalist eligibility; no clone of Purdue institution.
- NIIMBL: six www/non-www/about/contact/project/fallback routes returned curl56/no body. Need accessible own identity/address and its named single-use-plastics project. The indexed project is a discovery lead only, with no excerpt integrated.
- NEPIRC: named Plastics Processing pathway verified on own page; B-D10-GEO remains.

## Availability and limits

source-fetches.csv logs all selected URLs/roles. Admitted yield4/4 URLs (3own LIFT pages + Census), producing5/5 observations. Primary discovery stayed within~6 distinct routes per organization; validation re-fetches repeat admitted URLs. A LIFT2025 equipment poster was fetched as a lead only; current HTML is the admitted service witness.

Failed routes: NIIMBL6, Ohio development MEP route, Tech Hub homepage, America Makes homepage and REMADE homepage, all curl56/no body here. Route availability is never absence/closure; held identities still resolve and no status changes follow. MAGNET/IACMI, PA MEP, Michigan Center, Purdue MEP, NEPIRC and all admitted LIFT pages were reachable. Estate lookup was partial on this Mac (missing Windows Documents catalogues), not an absence finding.

No regional completeness claim: other Ohio operators and Pennsylvania affiliates were not individually inventoried. Raw pages/PDF/JSON stay uncommitted under build/. No personal contacts, CRM, private or licensed data are copied into records or packet quotes.

## Named checks and review

- Three hand-known held identities: MAGNET→ORG000159, IACMI→ORG002099, REMADE→ORG002100. Reused house dedupe finds3/3 before application. No new fuzzy matcher.
- House word-sequence matcher reused from equipment wave1/rawcheck conventions. Operator, Plasmatreat and HIP source words manually confirmed first. build.py --raw-check:5/5 observations/4of4 URLs, no admitted-source skips; fabricated-program negative rejected. Census parser checks exact matched address and Wayne/GEOID26163.
- check.py:12/12 census; exact1Cecosystem/5EVD main delta; all main rows unchanged; all-CSV replay byte-identical. Cross-shard ORG/EVD ID collisions each refuse before writes. Removing both address witnesses leaves3 valid rows and fails typed evidence preflight; fabricated quote fails raw check with all CSVs unchanged.
- validate.py: zero errors; full validate.txt. No scripts/ changes, so full scripts pytest was not repeated for this data packet.

Codex/Grok completion refutes pending; not ready for merge. Review should challenge the named-service scope, ALMMII dedupe/grain, county and evidence-backed fields/holds. No current funding/liveness check, individual inventory of every regional MEP, hosted deployment or physical facility inspection was performed.

Integration journal: merged main80bb5140e0f1598d85fe30b28777def59c9b83c6; restored exact main copies of both owned canonical files and replayed the builder. integration.json proves all prior rows unchanged and exactly1ecosystem/5EVD added. The scope check was rerun after the merge commit so HEAD includes the new main base; post-merge raw5/5, all failure/replay checks and validator0 pass. No hand CSV conflict merge.
