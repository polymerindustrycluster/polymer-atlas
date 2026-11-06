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

Every hold names its settling fact in verdicts.csv. Source failures are availability only. No arbitrary inactive/closure change is made to any held record. The4 inherited registry-link candidate rows remain STILL_UNCERTAIN/held: PR129 was verified OPEN, mergedAt null, on2026-11-06. Their identifiers are not newly asserted as verified registry facts. They have not been applied or independently reverified pending the controller's restoration gate. registry_links.csv remains untouched.

## Canonical additions

1 organization row at tierC (ORG-009600 Peak Performance Polymers, organizations_US.csv),1 Ohio site row at tierC (SITE-013100 Strasburg, Tuscarawas),8 append-only evidence rows EVD-295000–295007 (4 organization/4 site). Existing canonical rows changed:0. No tierA/B additions. Equipment rows in this PR:0.

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
