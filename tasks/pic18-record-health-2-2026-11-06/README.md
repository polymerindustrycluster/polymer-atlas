# L4b PIC18 capability-only continuation — 2026-11-06

First user: campaign controller / PIC analyst now; non-use finding date 2026-12-15.
Acceptance before application: work the frozen 85 capability-only organizations from first-pass baseline; own-site explicit corporate claims only; controlled §3.1/§3.2 values; one raw-checked evidence row per value; no tier, site, status, website or peer-lane edits. Availability failures never establish absence. No off-vocabulary organization note column exists; ambiguous chemistry is held rather than assigned a vocabulary value.

## Result

Baseline for this PR is first-pass commit 04592d0 (PR #133): **430/632 PIC18 Ring1–2 organizations = 68.04%** free of T1 blocking gaps. After: **446/632 = 70.57%**, +16 organizations. Original campaign baseline remains **428/632 = 67.72%**.

Frozen frame.csv: 85 unique organizations whose only original blocking gap was capabilities. Verdict census: 16 VERIFIED; 69 STILL_UNCERTAIN. Added 22 controlled values in 18 cells across 17 organization rows; 22 append-only own_site scope evidence rows EVD-170012–170034, each supports_A for that claim only. No verification tiers changed. No entities, sites or relationships created. No inclusion decisions or merges. Evidence shards follow each organization's existing shard. No L9/L10 columns touched.

Own-site sources: Novex, Dalton, Flexsys, Grafix, J.J. White, Jet Dock, MIPCO, MMI, Nova, Autoneum, Kar-Del, Chardon Custom Polymers, ValenSil, ITPS, Homestead Finishing, Speedline, TUFTEX. evidence_packet.csv carries exact URLs and short quotes per value. Corporate offerings are not assigned to individual plants. Common-name/material words in customer descriptions or machinery listings are not process witnesses. Anchor/ACI domain-to-parent identity is held. Polycarbosilane and general water-storing polymers are not forced into a family tag.

## Research and holds

All 85 homepage routes attempted with browser-UA curl: 61 fetches succeeded at transport level, 24 failed. Empty/JS-only/suspended/blocked content still does not establish capability. For available pages, up to four own-domain links selected from capabilities/materials/process/about/product paths; initial and prioritized selections can revisit a URL. At most six primary attempts per organization including Jina fallback for missing/short pages. Jina yielded no usable witnesses. `fetch_manifest.csv` records extracted text inventory, not a claim of evidentiary quality. `verdicts.csv` gives all 85 dispositions. The 68 holds require an explicit corporate process/material witness in schema vocabulary and identity continuity where unclear. No closure or no-establishment rejection made.

## Reproduction and checks

```
python3 tasks/pic18-record-health-2-2026-11-06/refetch.py
python3 tasks/pic18-record-health-2-2026-11-06/build.py --raw-check
python3 tasks/pic18-record-health-2-2026-11-06/check.py
python3 tasks/pic18-record-health-2026-11-06/health.py --self-check --output tasks/pic18-record-health-2-2026-11-06/health.csv
python3 scripts/validate.py
```

Known answers: existing first-pass HTML extractor and token matcher reused; Novex polyurethane, MIPCO epoxy and TUFTEX natural rubber quotes matched; injected wrong nylon phrase rejected. No automated semantic matcher introduced: controlled values selected manually from exact quotes. `check.py` checks all CSVs against 04592d0, exact cell delta, evidence append-only, one evidence row per value, all 85 verdicts. Validator: PASS zero errors. Build replay: byte-identical. No scripts/ edits, so scripts pytest requirement not triggered.

Reviews: pending assigned Codex and Grok clerks under controller BOARD 05:55 authorization (supersedes council-only route). Draft until both families approve. PR is stacked on #133; controller must merge #133 first, then refresh main data and rerun this builder if needed. Only the controller merges or changes task status.

Negative control: removed one packet evidence row temporarily, ran check.py, observed nonzero failure, restored packet. Replay hashes of all data CSVs unchanged.

Refresh: merged first PR25c81b2 (which merges main9489b60), took its data wholesale, replayed this builder. Exact-delta checker baseline now25c81b2. First-pass check.py intentionally applies to first-pass tree; continuation checker covers this tree. Refreshed health446/632 and validate0 pass. Controller authorized main's LF federal-frame normalization; net diff versus main zero. Original inherited bytes remain backed up. No evidence values changed during refresh.

First-PR Grok Faull refutation propagated: Faull material/tier held on parent; continuation values unchanged. Exact-delta baseline nowc980a66caf3ab0ae97902c3025d6b700bb23a390; firstPR430/632→continuation446/632. Earlier448/632 snapshot superseded.

Grok2 REFUTE fixed:JJWhitecustomer-nylonfabric doesnotsettleownnylonresinclaim. ProposedmaterialseditandunintegratedEVD170017withdrawn;IDretired. VERDICTchangedtoSTILL_UNCERTAIN. Final18cells/16orgs,22EVD,85census16VERIFIED69holds;T1446/632=70.57%. EarlierCodexapprovalsupersededforfinalrevision,rereviewrequested. R4frozen68framepredatesthisnewholdandisnotretroactivelyexpanded.
