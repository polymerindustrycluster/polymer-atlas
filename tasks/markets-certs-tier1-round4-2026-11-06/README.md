# L10 Tier-1 markets/certifications round 4

Controller-assigned next100, new branch agent/codex/markets-certs-tier1-round4 from pinned main f437e0b; IDs EVD240400+. Acceptance before research/application: active + stored Tier1 + blankmarkets, any held PIC18 Ohio county-site first then org_id, no website filter, exclude all prior30+100 frames plus unresolved ORG62/101. Frame100 unique IDs frozen in frame.csv/frame.json. First user PIC supplier-matching staff; non-use review2026-12-15.

Only markets_served/certifications and matching append-only evidence. Exact schema vocabulary; corporate entity-served markets, no parent/global union or generic-material-use inference. Certifications follow R3c/R12: current certificate or current own page naming non-superseded edition; expiry stated when known; expired/superseded/editionless held. ISO transition owner battery remains unresolved, no lane ruling. Failed fetch is availability only. Effort cap ~6 distinct primary pages/org; keep all100 verdicts incl unavailable and blank websites.

Gates: calibrated4known/4fabrication+challenge controls, everyquote fresh rawcheck, seeded fresh30value audit0errors, frame/verdict unique coverage, builder no-write guards, data boundary/oldrow/evidence preservation and idempotence, validator0, both deep Codex/Grok refutes before ready. Prior157/179 remain separate; handle findings first. Research not yet applied or approved.

Pre-application certificate basis clarification: own quality pages can publish original PDFs on their Webflow CDN. Abrasive Technology's quality page directly links two named-entity, dated PDFs; keep that own linking-page URL alongside the original PDF URL, verify the exact href live, and retain both in the evidence note. This is company-published evidence, not a third-party directory. Current-edition-page alternative also permits ISO/IEC17025:2017 under existing R3c; date fields stay empty unless an exact dated certificate is read. No currency exception introduced.

## Results and provenance

Frozen frame100: **30 VERIFIED organization-enrichment outcomes /70 STILL_UNCERTAIN**, no rejects/duplicates/creates. VERIFIED means at least one supported value, no tier upgrade or all-field verification. 47 organizations have no recorded website;53 have53 distinct URLs. Initial home fetch37 succeeded; one later failed fresh raw retrieval, leaving **36 FETCHED/17 UNFETCHABLE/47 NO_WEBSITE** in final attempts.csv. Discovery availability is not verification. Local name resolver ran100names; estate search reported missing Mac catalogue layers, so no private-corpus completeness claim or fact from them is used.

**99 candidate values:93 accepted =88 markets+5 certifications;6 explicit unapplied market holds**. UnitedSecuritySeals initially matched but repeated fresh GET/Jina routes returned403 before application; all6 remain STILL_UNCERTAIN. IDs **EVD240400–405 are permanent unused slots**; accepted IDs **240406–240498** retain original indexes. check.py reports those6 excluded holds explicitly; it requires every VERIFIED quote to fetch/match, never silently skips an accepted row. Holds table has **86 claim/org cases =70 no-fill organizations+16 partial cases**. No claim of market/certificate absence or closure.

Applied **33 cells on30 active stored-Tier1 organizations**:30 market cells+3 certification cells, unchanged tiers **A14/B14/C2**. **93 append-only evidence rows:OH20/PA73**. Only those two columns; no website/status/parent/tier/sources/notes/newsroom/registry edits. Exact URLs, quotes, currency and scope in inputs.csv; public company market/product pages and original company-published PDFs only. No licensed/private content.

Initial main f437e0b: unit active canonical organizations4899, populated markets **404→434**, certs **52→55**. Active nonempty stored-Tier1 subset1261:markets **162→192**,certs **15→18**. These count populated organizations, not tag count. counts.json records application; counts.sql independently reconciles canonical shards and frame/verdict/value yield, excluding generated exports.

Accepted certifications:

| Organization | Basis | Current dates/scope |
|---|---|---|
| Abrasive Technology LLC ORG1542 | Original company-linked Amtivo251559 PDF, AS9100D |2025-07-30..2028-07-29; named LewisCenter LLC aerospace-engine superabrasive coating; UKLTD E-Bonding appendix only. PDF identity governs over imprecise quality-page heading. ISO9001 portion held.|
| Same | Original company-linked Intertek0077840-03 MDSAP PDF, ISO13485:2016 |2024-07-03..2027-07-03; named LewisCenter main site FIN F000716, dental/podiatry/dermatology instruments. No group-wide scope inference.|
| Corry Rubber ORG2266 | Own original URS204567/A/0001/SM/En/IATF0494399 PDF, IATF16949:2016 |2023-12-30..2026-12-29; Corry601WestMain design/manufacture molded rubber,405WestMain Banbury manufacturing support appendix.|
| Same | Current own registration/lab page explicitly ISO17025:2017 |R3c page basis; states Corry testing lab validDec2025–Nov2027. PDF is image-only to pdftotext; exact expiry day not asserted, date fields empty.|
| Custom Processing Services ORG2630 | Current own Quality&Compliance list explicitly ISO/IEC17025:2017 |R3c page basis; analytical lab services offered; exact facility scope/expiry unknown and date fields empty. No edition-less GMP/FDA or supersededISO9001 added.|

Edition context only, never organization evidence: [ISO17025 official current edition](https://committee.iso.org/standard/66912.html?browse=tc) confirms2017 (reviewed2023); [ISO13485 official page](https://www.iso.org/iso-13485-medical-devices.html) identifies2016. IATF2016/AS9100D context remains the official IATF/IAQG sources checked in prior approved packets; no ISO9001/14001 transition ruling introduced.

Scope-sensitive choices: YUSA OEM uses its actual automaker customers, never Lord joint-venture history markets. Vanguard generic OEM does not imply automotive; its rail/forklift/garden/drum offerings support only corresponding markets. Abrasive medical_device uses explicit medical-device manufacturing tooling. PennFoam named packaging customers remain general medical, not devices. Corry explicitly identifies endoscope/device parts; its AS9100 is in progress and held. Polytek uses its own Industries page/named Polytek and CPD product offerings, not generic material properties; medical models remain general healthcare. CustomLaminating explicit protective clothing supports apparel, distinct from generic textiles held in round3. CK transport mode stays unknown. Regupol rail-adjacent building vibration protection is not rail-industry evidence. Parent-wide Yanfeng/Flint/Quanex/Jennmar pages remain held; no website or parent changes.

## Named checks and replay

```sh
python3 tasks/markets-certs-tier1-round4-2026-11-06/check.py
python3 tasks/markets-certs-tier1-round4-2026-11-06/guardcheck.py
python3 tasks/markets-certs-tier1-round4-2026-11-06/build.py
python3 tasks/markets-certs-tier1-round4-2026-11-06/boundary.py <pinned-main-sha>
duckdb :memory: < tasks/markets-certs-tier1-round4-2026-11-06/counts.sql
python3 scripts/validate.py
```

Known-answer calibration before trusting copied fetch/matcher: CIMAmarkets positive,ESTERLEISO2015 positive,HudsonISO2015 positive,CIMAqualityISO2015 negative:4/4;4fabricated quotes refused. JSredirect challenge refused on both routes. Company-asset link matcher:2known original PDF links positive,1fabricated certificate URL refused. Raw matcher reuses house W from evidence-repair-2/prep.py (requested ownership-status rawcheck tool absent);curl browserUA/Jina fallback,pdftotext,ordered normalized tokens. CSS visibility is not evaluated. No new dependency.

Fresh check **93/93 accepted quotes**, all dated certificate identity/expiry quotes and both exact own-page CDN links pass, zero accepted unavailable pages. **Random fresh30 VERIFIED value rows,0 raw errors**, seed20361108; routes and parsed-text hashes in audit30.csv. Not30 distinct organizations or a substitute for semantic refutes. Six availability-held candidate values are explicitly uninspected/unapplied in the final check.

guardcheck.py temporary-root injections:duplicate existing global EVD;ISO17025 page2017→2015;expired dated PDF;external PDF without its own publishing page;99/100verdict yield. **All five reject; builder failures leave every canonical CSV hash unchanged**. boundary.py on f437e0b:30organizations/30+3cells/93newEVD,zero old-key loss/unrelated fields/old-evidence edits; replay byte-identical. Validator **zero errors**,36509totalEVD on this initial baseline. Shared scripts unchanged, no scripts pytest gate triggered.

On main movement, preserve branch history; merge pinned main, replace **all four owned OH/PA org+evidence files** from that exact main, replay builder and named checks. Never hand-merge CSVs. boundary.json records latest integration base; refresh denominator counts, preserve original frame and input-index IDs. Prior157/179 are independent packets; neither is bundled as this lane's delta.

## Refutes and unchecked work

Codex4/Grok4 deep reviews pending; no Done/merge claim. Holds are explicit in holds.csv. Unselected organizations,47unrecorded websites,17failed routes, scanned PDF exact dates, current-page-only cert expiry/facility details, private-corpus completeness and owner ISO-transition exception are unchecked. Hosted CI pending after PR creation; controller owns merge and task status.

Integration receipt: pinned current main **c2674712c0c9f8aeefac9179597b8a4c6e5eda5f** includes controller-merged PR157. Resolved OH evidence conflict by exact main copies of **all four OH/PA org+evidence files**, then unchanged input packet/builder. Same30org/33cells/93EVD; boundary old-key/field/evidence preservation and byte-identical replay PASS. Latest active4899:markets **416→446**,certs **54→57**; stored-Tier1active1261:markets **174→204**,certs **17→20**. Validator0,**36699total evidence rows**. Earlierf437 counts remain historical; counts.json/boundary.json now describe this integration. Prior179 is not in this base and remains independently reviewed. Shared scripts changed only through merged main, with no lane-authored script delta.

Codex6 (OpenAI) **APPROVE** @18d56a0,0findings. Independent10org sample expanded31claims/18pages plus all5certs; raw93/fresh30zero,counts/IDs/scope/oldrows/replay/5originalguards/validator0 pass. Explicitly accepted named Polytek/CPD applications and Corry/CPS R3c ISO17025:2017 page bases. Report controller storage reviews/190-clerk-codex-6.md. Unsampled surrounding-page semantic census, suspension registries, scanOCR and hostedCI were not inspected.

Subsequent guard-only hardening from Codex179finding: retain existing evidence file+payload and require expected mirror shard before replay, including identical payloads. Added identical-planned-row move toDE negative control; **six** guard controls nowPASS, all failure cases leave canonical hashes unchanged. packet-equivalence.json confirms every data byte and inputs/frame/rawchecker/fetcher unchanged from approved18d56a0; boundary/replay/validator0 PASS (36699EVD). No source/data change or fullsource rerun for this preflight-only fix. Codex guard-only rereview/final Grok pending; draft retained.

Controller explicitly limits this repair to active builders. Merged136/157 historical builders lack the stronger shard guard; leave them unchanged and **do not re-run them**, superseding their old replay recipes. Their main data was validated; no historical-data finding. Current packets use hardened active builders.
