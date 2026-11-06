# L3 merged-site quality, batch2

All15 newly merged L3 tier-C establishments from #202(MN10) and #204(NJ5) are frozen on main be76f04. The earlier #216 frame of three sites is excluded; #164 was open at this freeze. Frame and integration SHAs are separate in baseline.json, so later main merges do not silently change the census.

Six establishments are promoted C→B: five in Minnesota and one in New Jersey. Nine remain STILL_UNCERTAIN with settling facts. No records are created. Exactly18 site cells change(tier,sources,notes); last_verified is assigned its existing2026-11-06 date. Status stays unknown. Address, city, ZIP, NAICS, process, ring, county, qualifier, registry and relationship fields remain unchanged.

Thirty appended supports_B evidence rows cover all five mandatory claims for each promotion:24 government_filing observations(existence,address,code,parent) and6 own_site scope observations. Existing evidence rows remain untouched. Allocation is EVD304100+6*frozen input index, through304189, inside the controller's unused304000+ block. Each sixth slot and all held-site slots remain permanent unused gaps. Prior #216 IDs304012–016 are disjoint.

## Full promotion census

| Site | Establishment | Primary witness |
|---|---|---|
| SITE012620 | Carpenter, Albert Lea MN | Own location page names the city and fabrication of polyether foams, bedding, laminated mattresses and polyester fiber; exact street matches the filing. |
| SITE012668 | Plastic Products, Princeton MN | Own facility page explicitly identifies this Princeton site as a custom plastic/metal/ceramic injection molder and gives its street. |
| SITE012669 | Oatey/Cherne, Shakopee MN | Own2021-07-15 announcement binds relocated Shakopee manufacture to robotic joining of natural-rubber plug cores. Later banked federal filing corroborates the same site. |
| SITE012682 | Revolution, Oakdale MN | Own locations page's Oakdale section describes film blowing and commercial sheeting/bags. Firecrawl rawHTML200 was used after curl/Jina failures. |
| SITE012700 | T.O. Plastics, Otsego MN | Own quality page explicitly describes its Otsego thermoforming facility; no certification tags are added. |
| SITE012809 | Benjamin Moore, Newark NJ | Own FAQ identifies its paint/coatings manufacture and Newark among its manufacturing facilities in the same answer. |

Full exact source/city/issuer/binding quotes, dates, routes and cache hashes are in selected.json and full-promotion-census.csv; source URL receipts are in rawcheck.json. The six scope claim_detail values contain only exact own-page words, under the controller's07:20 rule. Government names, identifiers, codes and operator atoms remain on government_filing rows, never attributed to own pages.

Four federal claims per site use the same controller-authorized banked OSHA ITA CY2025 records: packet observed2026-11-01, reviewed2026-11-06, filing submission date in notes. Exact street/state/ZIP/code/reliability and filed company_name bind to the existing site and held operator. Joint primary-source identity/location/activity review supportsB under the campaign/L11 quality convention. No fresh federal download or current-operation claim is asserted; activity/liveness rows remainC and are not mandatory for unknown status.

## Issuer and date discipline

These are operator-issued pages. Direct source domains match held website domains for PPC, Oatey, T.O. Plastics and Benjamin Moore. Carpenter's held website is blank; its page names the same Carpenter Co. operator. Revolution's website field is also blank; raw og:site_name explicitly names Revolution Sustainable Solutions, matching its held legal/trade identity. These observations do not populate organization websites or invent parent relationships. The raw metadata issuer is checked separately from page text. The selected pages do not require a new B-PARENT exception; source/operator identity is bound before application.

Oatey's source is explicitly dated2021-07-15; its source date is preserved and checked against the visible heading. Other selected pages have no explicit article date and are observed on retrieval2026-11-06. Revolution metadata reports an older modification timestamp; this is not represented as a new operating event. All operating_status values stay unknown.

Firecrawl is a live rawHTML fallback, not AI extraction. One Revolution request and one Ring request returned200 after four curl/Jina routes each. Revolution's raw page contains both the local film-production section and issuer metadata. Ring's page corroborates Springfield's street only, so Ring stays held. Full raw captures/text stay outside the public repository, in/tmp; an ignored build cache is also available. No personal contacts, private content or licensed data are committed.

## Nine holds

holds.csv names each settling fact; holds-sources.json supplies its primary URLs and raw cache:
- Amcon Fridley: own contact uses Minneapolis for the same street/ZIP; a raw Fridley-specific process/locality bridge is still needed.
- Morris Plymouth: own contact describes print/lamination; reconcile with filed plastics-film manufacturing code before promotion.
- Amcor Mankato: the located own job names2111 Third Avenue, while this site is1301 Third Avenue. Same city does not bind the other street.
- Tank/Solar Delano: Solar's own job binds Delano rotomolding, but its distinct Solar Plastics issuer is not yet bridged to the held Tank Holding operator under B-PARENT. No repoint/parent invention.
- ADS Fairmont: own maintenance job identifies Fairmont and plant maintenance; corporate plastic-recycling boilerplate does not independently establish this site's polymer process.
- Graham Seabrook: fetched own about/careers pages do not settle this specific plant's city/activity.
- Homeland: own extrusion job names Millville while the filing has Milville; an exact street/locality bridge is still needed. No silent spelling/address correction.
- Pretium Hillsborough: own locations page gives08854, filing/site08844. The ZIP conflict is held.
- Ring Springfield: raw own locations page binds50 Fadem Rd, but a local polymer-production witness is still needed.

These are unsettled facts, not absence or closure verdicts. Failed routes were availability signals only. No scope, ring or vocabulary ruling is self-made. No six-route minimum is implied; we stop when a conflict needs reconciliation rather than spending routes on generic company pages.

## Checks

Reuses #216's builder/check pattern, the calibrated STRONG/evidence-repair matcher and house append_sorted. Before relying on matches, three independently read known sources(Carpenter,PPC,T.O.) and fabricated-suffix negatives pass; all6 selected scope/city/binding quotes and six negatives pass. No new network fetcher was introduced. The standard metadata string check binds Revolution's issuer.

Run build.py --apply, check.py --negative-controls, and python3 scripts/validate.py. Results: independently reconstructed15-site merged-only census;6V9holds;30B rows; exact4 data files/18 cells; all old canonical rows/evidence preserved. The actual mandatory-claim gate rejects all30 single-missing-claim cases. Nine hold source receipts also pass raw hash/quote and fake-suffix tests; an injected fabricated hold quote is rejected. Seven injected defects(EVD cross-shard collision, fabricated scope, absent city, issuer, hash, misattributed URL, and another real city from the same page) fail before any canonical write. Temp CSV hashes stay unchanged. Both build replay and all canonical CSV hashes are byte-identical. Validator:0 errors. Full6-promotion census replaces a20-row sample because there are only6 promotions. No shared scripts changed, so full scripts pytest was not run.

Strict NAICS326 counts are unchanged: MN58/368 and NJ33/368 QCEW2023 private establishments. C already entered the strict numerator; Benjamin Moore is325510 and remains outside it. Ratios are counts, not matched coverage.

First user is the controller/research integrator, review date2026-11-06. Acceptance and reserved IDs preceded fetching/application. This is the next batch of the existing merged-site quality assignment, not a new tracked commitment. Two-family deep completion refutes remain pending; controller alone merges and changes tracker status. Prior PR findings stay higher priority.

Grok/xAI deep completion refute: APPROVE, zero findings at e9e1254 (clerk-grok-3, thr_4g4uwqjxjv). Independently read all six own pages and the complete six-promotion/five-claim census. Exact operator issuers, local activity sections, company-page/plant bindings, Oatey2021 date, federal street/city/ZIP/code/operator claims, 30 append-only B rows and nine retained holds pass. Check --negative-controls, validator0, row-loss, exact four canonical files/18 site cells and strict326 MN58/NJ33 unchanged all pass. Report: reviews/232-clerk-grok-3.md in controller storage. This receipt changes README only; canonical payload/code/source selection unchanged. Codex approval remains pending; no Ready/Done/merge claim. Conservation: current PR/review fixes only, no new frame/batch. Owner rule supersedes inherited tier: every future bb thread tell/spawn explicitly --service-tier default, Codex reviews only R-codex-8/9.
