# L14 — PIC-18 discovery residue, 2026-11-06

Continuation claim: controller06:30 BOARD entry, new branch agent/codex/pic18-discovery-residue from main9489b60. This task is independent of equipment PR140. Branch history is the pre-pass backup; this README is the pass journal. Acceptance/first user/non-use date are in SPEC.md.

## Exact population and outcome

26 lead rows, pinned from all prior STILL_UNCERTAIN rows in tasks/discovery-pic18-2026-11-03/L1–L4; 26 unique lead IDs, no omitted input. These are heterogeneous discovery units:25 organization/site leads plus1 unavailable directory route (WEB-Huron-3). The source-route unit is not counted as a company.

| Verdict | Lead rows |
|---|---:|
| VERIFIED |1|
| DUPLICATE_OF |1|
| REJECT |2|
| STILL_UNCERTAIN |22|
| Total |26|

Every hold names its settling fact in verdicts.csv. Source failures are availability only. No arbitrary inactive/closure change is made to any held record. The4 inherited registry-link candidates are now VERIFIED and applied (3FRS,1EIN), after PR129 merged and fresh source-system verification. The prior restoration hold is superseded by the controller's release and the registry addendum below. No existing link row changed.

## Canonical additions

1 organization row at tierC (ORG-009600 Peak Performance Polymers, organizations_US.csv),1 Ohio site row at tierC (SITE-013100 Strasburg, Tuscarawas),13 append-only evidence rows EVD-295000–295012 (5 organization/8 site), plus4 registry-link rows (3FRS/1EIN). Existing canonical rows changed:0. No tierA/B record additions or tier changes. Equipment rows in this PR:0.

Peak's own homepage explicitly states custom polyurethane manufacturing. Ohio EPA's fresh no-exposure list, permit0GRN00360*BG, names both applicant and facility and the physical address9109 State Route250 NW, Strasburg, Tuscarawas. PDF page277 was rendered and visually read, so column-wrap extraction did not decide the address/county. The government list's address is the new fact that settles the prior address hold. Company-level polymer scope is linked to that same-named facility at tierC; no facility-specific molding method is invented. Current operating status remains unknown; an unexpired permit is not a liveness witness.

HQ city/state/county remain blank: an applicant address is not necessarily headquarters. Organization is therefore placed in the US residual shard by AppendixC, not forced into OH. No NAICS, ZIP, incorporation type, employee band, certification or ownership is invented. Material polyurethane_pu and ring1 are based on the explicit custom polyurethane manufacturing claim. Specific molding process is left blank.

Unit/filter: all Ohio site rows with physical county in scripts.regions.PIC18, all tiers/statuses, rise1135→1136. This is a stored-site-row count, not an active-establishment census or coverage ratio.

Dedupe: atlas.py dedupe-check domain/name/street/city/state for Peak returned no hits at all four ordered steps (dedupe.json). All organization/site shards searched; trade_names/notes checked. No new source registrant alias arises. Tree-wide ID namespaces are checked before writes, including ecosystem sharing ORG ids. IDs are in controller's disjoint reservation; no gap reused. Site and org shard-of commands return OH for physical/site state; org deliberately US residual because HQ state is not established.

## Resolved existing/historical leads

- WEB-richland-2 terminates at held SITE-001473 under ORG-001426. Held name already says Techniplas US LLC dba NEXXTA, notes150 E Longview. Fresh NEXXTA own locations page confirms this exact address and26 injection molding presses. No duplicate organization/site and no rebrand/status edit.
- LF-OH-00398: City of Huron2024-06-25 council minutes p6 state IAC closed its doors. Scanned page rendered and OCR read, dated municipal outcome rather than WARN prediction. Bulk Form5500 spine snapshot2026-11-01 searched by IAC sponsor name + exact Ohio establishment address:3 name hits,0 matching1608 Sawmill. The filing screen is snapshot-limited, not a current DOL no-filing certification.
- LF-OH-00339: Sandusky memo dated2018-01-09 in2018-01-22 agenda describes1702 Campbell as vacant former Ultimate Industries factory under State ownership, requesting demolition/asbestos bid. Vacancy is an observed outcome, not an announcement of planned closure. Same Form5500 spine:0 Ultimate Industries sponsor-name hits. No held record status is changed.

## Source availability and effort

Primary own routes reached: Peak, Greenbridge, Mansfield Plumbing, MD Plastics, EPC's corrected epcmfg.com domain, Veolia, IAC, Mondi, Kraton, NEXXTA, American Quality Stripping, Wheeling Rubber. Government sources reached: Ohio EPA no-exposure/CRO PDFs and the Huron/Sandusky municipal PDFs. Newman/Jaco/ProVia own pages returned403 and Jina401; Huron membership list403. Guessed Craft/old EPC/Wise Machine routes failed; NCCM brochure404. All are retained as availability observations only. No source retry storm; at most~6 primary fetches per organization. Search snippets remain discovery leads, not create evidence. Raw HTML/PDF files stay uncommitted under build/; pages may include personal contact details, which are not copied into this packet.

## Named checks and replay

- `python3 tasks/pic18-discovery-residue-2026-11-06/build.py --raw-check --apply`: PASS8/8 evidence quotes,3/3 admitted/calibration sources, zero source skips. House word normalizer imported from existing evidence-repair-2 prep; curl browser UA and pdftotext used. Re-fetch failure or absent quote aborts before apply.
- Three hand-known answers: own Peak custom polyurethane manufacturing; visually checked EPA Peak permit address; NEXXTA150 E Longview and26 injection presses matches held SITE001473. All3/3 checked. Fabricated plant-name negative control rejected on every source.
- `python3 tasks/pic18-discovery-residue-2026-11-06/check.py`: PASS26→26 exact census, all-CSV replay byte-identical, injected reserved-ID collision in a different shard fails before any write. See checks.txt. Every prior canonical/evidence row is preserved.
- `python3 scripts/validate.py`: PASS zero errors; existing warnings remain. Captured validation-summary.txt. scripts/ is unchanged by this PR; global scripts pytest gate not applicable.

On main advance: merge origin/main; for any canonical CSV conflict take main's file and rerun this builder, never hand-merge CSVs. Preflight completes across all files before any append; an interruption can be recovered by rerun. Historical observed dates do not silently advance on replay.

## Reviews

Pending independent Codex/Grok refute clerk pair4 under controller06:25 routing. No completion approval claimed.

## Registry application after restoration (supersedes the initial four-link hold)

Controller released the gate after PR129 merged as9d69978. Merged current main before application (mergefea3ce4). `registry_additions.csv` has4 unique new triples, none present in the5373 restored/current links; data/registry_links.csv is exactly4 appended lines, old rows byte-preserved. Registry has composite keys and no immutable single-ID column; the existing append_sorted helper is used for all ID tables, and registry append uses the same CSV header with preflight composite uniqueness and original order preserved (V36 applies to org/site IDs, not registry triples).

Source-system proof, retrieved2026-11-06:

| Candidate | Primary verification | Application |
|---|---|---|
| Dover FRS110000741822 | Fresh FRS REST returns Dover Chemical Corporation,3676 Davis RD NW,Dover OH44622 | ORG000798 / SITE000863 |
| Convertapax FRS110007706900 | Fresh FRS REST returns Convertapax Inc,Gundy DR BLDG NO3,Midvale OH44653 | ORG000751 / SITE000813; FRS omits street number, so no full-address assertion; held site already cites this exact source ID and same street/locality |
| Catalyst FRS110000390390 | Fresh FRS REST returns Quest Automotive Products,2290 Zimmerman RD SE,Gnadenhutten OH44629; fresh Ohio EPA CRO2557 jointly labels Quest Automotive Products / Catalyst Systems at exact street | ORG001919 / SITE001910; historical facility identity only, no operator/status/parent change |
| Dover EIN391205755 | Fresh DOL EFAST2 PY2024 bulk CSV, ACK20251015110824NAL0008891586001: exact sponsor Dover Chemical Corporation AND3676 Davis Road NW,Dover OH | ORG000798, no site_id per R11;3 exact-name/street filings found. A separate ICC-named filing with the same EIN is excluded; no parent inference |

The OSHA ITA direct download returned403; that is availability only. R11 is satisfied by a fresh source-system Form5500 filing instead. Raw federal downloads remain uncommitted in build/pic18-registry; registry_sources.csv preserves only corporate identity/address/identifier fields, citation, record key and observed-byte SHA256. XML coordinates are not a matching input and are not copied to the packet.

Added5 identity evidence observations:3 FRS site observations,1 DOL organization EIN observation,1 Ohio EPA joint-label corroboration (EVD295008–295012). None asserts current operation or changes any existing record field. `verify_registry.py` independently re-fetches3 FRS records, the DOL bulk and the Ohio EPA corroboration; all4 identities and the joint label pass, with exact field/filing-yield checks and negative ID controls. These checks run within build.py --raw-check before application; no source may silently skip. Original8 evidence quotes retain their separate8/8 raw check.

`check.py` now additionally injects a conflicting existing registry triple and proves refusal before any write. Final validation/replay results are in registry-checks.txt. Prior review packet is historical; review-packet-v2.json covers the expanded registry scope, requiring updated independent family review.

### Integration after equipment merge

Merged current main85b8560, which already contains equipment PR140 and both final approval receipts (a025fad/30fb413). No extra equipment data/code or receipt delta rides this PR. Resolved canonical CSV conflicts by taking main versions of all six owned canonical files and replaying the unchanged builder; no hand CSV merge. All main rows in those files preserved field-for-field;1organization+1site+13evidence+4registry rows added. All six packet/value CSVs are byte-identical to cf6c9cd. check.py census/replay/collision gates and validate.py zero errors pass. integration-replay.json records exact counts and baseline. PR159 remains draft pending its own independent reviews.

### Independent review receipt — Grok4

Grok4 (xAI, thr_95ffgh3rxy) APPROVE at 9a0622c, zero blockers; grok-review.md records the received verdict. Independently confirmed preservation, census/replay/negative controls, validator, Peak scope/address, duplicate terminus, closure filing screens, and all four source-system identifiers. A later FRS429 in its verifier followed the clerk's successful independent HTTP200 record fetch; no quote/identity failure. Six payload CSVs remain byte-identical cf6c9cd. This receipt-only addendum changes no canonical or implementation file. Codex4 review remains pending; PR159 stays draft.
