# LinkedIn navigation — 2026-11-06

Controller-assigned branch agent/codex/linkedin-navigation; acceptance in SPEC before fetching. SCHEMA4.4/B-LINKEDIN/V58: navigation only, never evidence/monitoring. Only blank organizations.linkedin_url cells change. Zero IDs/creates/EVD, no tier/status/website/membership or other-field changes. No LinkedIn page was requested; own sources only.

## Current corrected result

325navigation cells on39organization shards:233Tier1first,92additionalPIC18footprint rows. Frozen tiers129A/172B/24C/0U, unchanged by this pass. Frozen frame2,061organization rows=1,299with nonblank tier1_qualifier then762others with an active Ohio site in housePIC18(allrings). Ten non-active organization rows held. These are organization/navigation-cell counts, not companies contacted, operations or impact.

1,736STILL_UNCERTAIN frame rows remain. Disjoint hold counts:423unavailable/blocked/non200 discovery routes;776no single structurally valid header/footer company link;180exact name/alias bridge needed;98shared held domains;10non-active frozen orgs;245no held own website;4fresh raw failures. All2,061IDs have exactly one verdict and settling fact. Failed fetches/missing recognized anchors never imply absence or closure. No private/CRM/licensed/outreach source used.

Discovery covers1,708eligible own-site URLs in Tier1-first phases:1,285HTTP200/423other outcomes. Final discovery log has2,214HTTPrequests including same-domain redirects; this excludes calibration, the interrupted first attempt and later validation passes. No whole-run cost/time claim. All request chains are logged and own-domain-only. External redirects stop before the next request; direct/redirected/encoded/nonASCII LinkedIn-like hosts are blocked before curl. No site scripts/assets are downloaded or executed.

The corrected parser reprocessed all1,285HTTP200snapshots from digest-verified caches.512pages have recognized header/footer company anchors. Classification yielded329candidates; fresh re-fetch of all329gave325PASS/4HOLD with no skipped candidate. Raw failures:Covestro403,Indelco500,OwensCorning/Novation200but no exact qualifying current anchor under the corrected parser. Availability/markup observations do not establish absence.

## Binding and source proof

proposals.csv records held own source/final URL, exact published href, qualifying location, observed date and canonical company URL. rawcheck.csv has325successful current witnesses/digests; raw-outcomes.csv hasall329attempted candidates; raw-requests.json logs every re-fetch request. Discovery outcomes and source hashes remain reviewable. Downloaded HTML stays uncommitted underbuild/linkedin-navigation/raw because it can contain personal contacts.

Exactly one distinct company URL, unique held organization/ecosystem domain and exact normalized legal/trade-name slug are required. Houseatlas.name_key supplies conservative equality, not fuzzy matching. Parent/brand ambiguity is held. Query/fragment tracking and local LinkedIn hostnames normalize towww/company/slug/, with slug preserved. Personal/share/malformed/encoded-dot URLs fail. No LinkedIn destination is visited.

Frozen input frame IDs/cohorts/tiers/website/identity began at e008ab9. On integration at be76f042, two public main trade-name fields had additive aliases only:ORG000651AdvancedDrainageSystems andORG000133Oatey. preimage-refresh.csv records exactbefore/after/maincommit. Legal name/website/status/parent/successor and binding to the published slug were unchanged. Only the packet's inputpreimages were refreshed; these alias additions were already on main and are not authored by this pass. No frame rows/cohorts/verification tiers changed.

## Codex7 refute accepted and corrected

Codex7/OpenAI REFUTE23e4a2e found that div.article-header within main/article and a page-wide div.site-header-footer wrapper could launder body links into header/footer evidence. Exact slug binding did not cure the location error. Accepted.

The parser now defers qualification until the entire page is parsed. Anchors within main/article ancestry are rejected; a candidate header/footer marker container that contains main/article cannot qualify. Independent proper header/footer children can still qualify. Article/entry/post-header class markers are excluded. Six permanent body/wrapper/ordering negatives fail both Links and actual rawcheck.verify; four independent real-header/footer structural positives survive. ancestry_check.py is run by the named check.

Re-parsing changed26cached pages and reduced pages with recognized anchors536→512. Sixteen initial unmerged proposals lost a qualifying location;4more failed the new fresh raw pass. withdrawn-navigation.csv records all20withdrawals from the original345-cell packet. Canonical files were restored from current main and only325survivors replayed; withdrawn cells remain main's blank value. No held record/ID/EVD was deleted. ancestry-reconciliation.json records the full reparse outcome.

Codex6's prior23e4a2eAPPROVE is transport-guard-only and is not counted as full source-semantic approval. Actual refuting Codex7 and full Grok6 reviews are required on this correction.

## Calibration, reproduction and limits

Three hand-read own anchors before bulk:AvientCorporation,RTPCompany,AveryDennison. known-answers.json/self-check.txt record3/3expected company links/source digests. self_check.py also tests valuelesshref,personal/share/body/globalbodyclass/unsafeURL/direct+redirectLinkedIn/encodedhost/fabricatedsourceanchor cases. The first parser stopped at an emptyhref after94persisted outcomes; valueless attributes and a literal checkpoint newline were repaired without losing rows. All successful snapshots were reparsed before application. Validation re-fetches repeat admitted own routes; distinct primary discovery remained bounded.

Run build.py --apply to preflight every proposal before writing. Held IDs/frozenidentity/currentwebsite,uniquehelddomain/exactslug,ownsource/finalURL,raw witness/location/date/reporting metadata and blank-or-exact cell all must match. Replay yields0changes.

Named check:python3 tasks/linkedin-navigation-2026-11-06/check.py. Exact325-cell projection on39shards against immutable integration mainbe76f042; all other canonical bytes/keys/fields unchanged;all2,061outcomes/all1,708URLcensus/all329rawattempts reconcile;all logged requesthosts safe;ancestryfixtures/4zero-writecontrols/byte-identicalreplay pass. CLI conflictingnavigation/entitypreimage and poisonedslug/frozen-tiermetadata refuse. Validator0/native row-loss PASS. No scripts/ changes, so full scripts pytest not repeated.

First user:PICstaffnavigatingpublicdatasetprofiles;non-usereview2026-12-06,no usage/deployment claim. Pending corrected full Codex+Grok approval;draft. No LinkedIn destination, JS-only footer, hosted deployment or nationwide completeness check. Dynamic source snapshots and failed routes are availability limits.

Corrected BOTH-family approval:Codex7/OpenAI andGrok6/xAI APPROVE67820c8,zero findings. Each independently reproduced325currentrawcachewitnesses/href/companyURL/location andcorrectedancestry;Groksecondwalkeragreed,28tradealias-onlymatchesheld,0parentlegalnamecollisions/duplicateslugs/percentslugs. OriginalbroaderCodexreviewretained;Codex6transport-onlyapprovalnotusedasfullgate. Reviewreports219-rereview-clerk-codex-7.md/219-clerk-grok-6.md. Limit:116historicaldiscoverybodieswereoverwrittenbylaterownrefetches;1169stillreproduce. All1285producerreparsewitnesseswereverifiedatcorrectiontime,butfullhistoricalreplayisnotnowclaimed. All325currentwitnessdigestsreproduce.

Landing integration main2845288 viaca93d38 restoresALLcanonicalfilesfrommain thenreplaysunchanged325cellpayload. No CSV conflict hand merge; no retained URL/ID changes. Check325cells/39shards/allothercanonicalbytes/keys/fields/replay/4faults,validator0/nativeguardPASS afterreplay. Earlierbe76f042figuresdescribeapprovedpayloadbase;currentbase.txtpins2845288. Controllerownsmerge/status;nochildmerge.
