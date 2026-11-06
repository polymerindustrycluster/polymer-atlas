# L3 merged-site quality

The frozen census contains three merged L3 tier-C establishments: Watson Coatings (SITE-012001, merged #141), Poly Processing Monroe (SITE-012503), and Plastipak Pineville (SITE-012511), the latter two from merged #198. The pinned main is d1e618b. PRs #164, #202 and #204 were open and are excluded.

One establishment is promoted C→B: Plastipak Pineville. Two remain STILL_UNCERTAIN. No organizations or sites are created. Only three site cells change: verification_tier, sources, and notes. last_verified is assigned2026-11-06, its existing value. Address, code, process, ring, status, county, qualifiers, registry links and relationships remain unchanged.

Five appended evidence rows, EVD-304012–304016, cover the promoted site's five mandatory claims at B. Allocation is304000+6*frozen input index, inside the controller's unused304000+ block. Slots304000–304011 remain unused permanent gaps. All existing evidence is preserved.

## Plastipak Pineville: joint primary-source support

The company's careers page links its Workday tenant. The tenant's public company-issued job JSON for REQ24583 names Plastipak-Pineville, LA; the hiring organization1000 Plastipak Packaging Inc. (US); and plastic-container manufacture using extrusion and blow-molding equipment. The source date is2026-09-23; retrieval/review was2026-11-06. The direct JSON request returned200. The HTML job URL returned a JavaScript shell and the Jina route failed; these availability signals did not supply evidence. The own careers page also returned200.

selected.json records the exact source URL, public job URL, issuer/location/activity strings, dates, raw paths and SHA256 digests. The complete raw responses remain in/tmp, outside the public repository. The job is an own-issued document, rather than a platform-assigned category; the company's own careers link establishes the issuer. The named employer is the held operator, so no parent/group relationship is inferred. B-PARENT does not require a new relationship for this issuer.

The own_site scope claim_detail contains only the exact job sentence. It includes no government identifiers, registrant aliases, NAICS or federal claims, under the controller's07:20 rule.

Four government_filing observations at B cover existence, address, code and operator linkage from ITA192504: Plastipak-Pineville;4101 Pardue Rd, Pineville LA71360; NAICS326160; and filed company_name Plastipak Packaging Inc. These values match the held site and operator. The source remains the controller-authorized banked CY2025 filing, packet observed2026-11-01, submitted2026-01-16. No fresh federal download is asserted.

This follows the campaign and L11 mi-il-site-quality convention: the independent company-issued city/activity witness corroborates the federal plant identity and location, with all five mandatory claims explicitly supported at B. Government facts remain government claims. The fifth claim, scope, is the own-issued quote. Operating_status remains unknown; no current-operation/status claim is made. Existing C activity/liveness observations remain append-only and are not mandatory for unknown status. There is no A promotion.

## Holds

Watson: its own homepage/about page supports coatings manufacture at325 Paul Avenue, Ferguson MO63135. The held city is ST LOUIS and the site's NAICS is blank. Promotion needs site-code provenance at B and postal-locality reconciliation. Banked FRS325510 is an old registry context; the employer Form5500 padded group325500 does not settle the current site code. No locality, code, status or tier correction is applied. See watson-source-gaps.md.

Poly Processing: its own contact page names2201 Old Sterlington Rd, Monroe LA71203; the held filing/site ZIP is71210. Its own blog confirms manufacturing in Monroe, but does not reconcile the ZIP. Hold pending physical ZIP reconciliation; no ZIP, status or tier change. Both pages returned200 and their quotes are raw-verified in rawcheck.json.

## Checks

Before use, the existing STRONG/evidence-repair parser and matcher passed three known Watson quotes and three fabricated-suffix negatives. Two Poly quotes and negatives also pass. Plastipak's source quote, issuer, city, date and careers delegation are checked against its raw JSON/HTML. This uses standard JSON parsing and the existing matcher, with no new network fetcher.

Primary routes: Watson2, Poly2, Plastipak4 (job HTML, Jina fallback, direct company-issued JSON, careers bridge), within the approximate six-route cap. Search-index job text was discovery only until direct JSON verification. A bridge hash initially used newline-normalized text rather than raw bytes; the preflight rejected it before any canonical write. It was corrected to hash the same raw bytes used by the builder.

Run:
- python3 tasks/l3-merged-site-quality-2026-11-06/build.py --apply
- python3 tasks/l3-merged-site-quality-2026-11-06/check.py --negative-controls
- python3 scripts/validate.py

Results: PASS3/3 independently reconstructed merged-C inputs, one promotion/two holds, all five B claims, every old canonical row/evidence preserved, exact two data files/three site cells/five evidence rows. The actual require_five gate rejects each missing mandatory claim. Four mutations (fabricated scope, wrong city, raw hash, cross-shard EVD collision) reject before any write; temporary canonical CSV hashes remain unchanged. Raw receipts pass five quote/five fake-suffix checks, plus the selected job quote and its negative. All canonical CSVs are byte-identical after builder replay. Validator:0 errors.

Full promotion census is full-promotion-census.csv (one establishment, so inspect all rather than sample20). No shared scripts changed; full scripts pytest was not run. Raw cache paths in selected.json/rawcheck.json are available on this shared host; re-fetch public URLs with curl/browser UA if needed. Full page bodies are not committed because they may contain personal contacts. The missing Mac entity catalogue was reported INCOMPLETE, never absence.

Strict NAICS326 counts are unchanged: MO43/368 and LA9/117 QCEW2023 private establishments. Tier C already entered the strict numerator; this quality promotion changes no establishment count or NAICS value. These are count ratios, not matched coverage; see qcew.json.

The first user is the controller/research integrator, review date2026-11-06. Acceptance preceded application; merged #198 frame expansion was recorded before promotion. Earlier research checkpoints in research-journal.md are superseded. The priority MN wrong-parent correction b420831 was completed before this application. Two-family deep completion refutes remain pending; the controller alone merges and changes tracker status.

Grok/xAI deep completion refute: APPROVE,0findings on344d5bd(clerk-grok-3/thr_4g4uwqjxjv). Independent livecareers200stilllinksWorkdaytenant; livepublicjobJSON200exactSHA9f65ba63 matchesrawcache,city/joblocation/countryUS/noadditionalcity/no-remote/issuer/date/scope/extrusionblowmolding bindsPineville only. Hiringissuer isnotclaim_detail orparentatom;parentclaimcomesfromITA192504/heldoperator. Full3frame/1C→B2holds/5Bclaims/exact3cells+5EVD/0statusaddresscodeedits/check5missingclaimfaults+4no-writefaults/replay/validator0/rowloss PASS. Watson/Polyrawholdquotesverified;nofindings. Dynamiclivecareershashdriftedbuttenantlinkremains,thecachedreceiptischeckedasitsownsnapshot. Codex completion refute pending. This receipt update changesREADME only,data/code unchanged.

Codex/OpenAI deep completion refute: APPROVE, zero blocking findings on d8c93e4 (clerk-codex-3, thr_jukpm97t9c). Fresh own careers tenant link and exact public Workday JSON SHA, date, Pineville-only location, scope/extrusion/blow-molding, and full six changed rows independently checked. Mandatory claims, old-row preservation, ID gaps, five missing-claim faults, four no-write faults, validator, row-loss and all-CSV replay PASS. Report: reviews/216-clerk-codex-3.md on controller storage. Together with Grok3, both families approve the same canonical payload; no active-operation or fresh federal-fetch approval.

Integration onto pinned main 4f30a8ebf5dde4a2d84618ba02163bb2bad4c375 restores all canonical files from that SHA and replays the unchanged builder. Frame remains frozen at d1e618b; frame_commit is separated from integration commit so later merged continuation sites cannot silently expand this packet. Only the check's Git snapshot selection changes; builder/source selection unchanged. Approved site and five evidence rows must remain field-identical. Conservation: no new research or frame.

Integration verification PASS: all six approved SITE/EVD rows field-identical to d8c93e4; exact two canonical files/three site cells/five append-only observations; all old main rows preserved. Named check including five missing-claim/four no-write controls, all-canonical byte-identical replay and validator0 pass on final tree. Current strict326 MO47/368 and LA9/117 before=after; historical MO43 preceded merged PR164's four Missouri326 establishments. qcew.json refreshed for the integration baseline, not a quality count increase.
