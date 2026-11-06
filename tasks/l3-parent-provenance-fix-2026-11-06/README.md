# L3 correction — PR141 group-domain provenance

Corrects the R-codex-1 finding on merged STRONG PR141. Full audit covers all19 site-create issuer contexts:15 new
organizations and4 held parents. Every issuer brand was freshly re-fetched with curl/browser UA (Jina fallback),19/19
matched on raw HTML text with scripts/styles excluded. audit.csv records every disposition, source URL and receipt route.
Six contexts use group sources;13 are direct operator brands. CMP already has the required parent+flag.

## Exact changes

| Organization | Correction |
|---|---|
| ORG-009026 Hahl Inc | ultimate_parent_name `Serafin Group (via Perlon Group)` + group-domain website flag |
| ORG-009017 EMS-CHEMIE North America | ultimate_parent_name `EMS-CHEMIE HOLDING AG` + group-domain website flag |
| ORG-009022 Re:Build CR, LLC | ultimate_parent_name `Re:Build Manufacturing, LLC` + group-domain website flag |
| ORG-003555 Nike IHM | Group-domain website flag only; existing `NIKE, Inc.` parent retained |
| ORG-001336 Yokohama TWS North America | Group-domain source flag only; existing Yokohama Rubber parent retained, website field remains empty |

Three parent fields and five notes flags (8 cells),5 existing organizations;0 new organizations/sites, no tier/status/website,
HQ, qualifier, registry or relationship-edge changes. Notes preserve all previous text. Seven new evidence observations:
5 parent-chain observations for the3 fills,2 publisher-identity observations for the existing-parent source flags. These last
two observations attest the issuer of the corporate source, not a newly asserted ownership transaction. All pre-existing
canonical evidence is unchanged; this is append-only after PR141 merged. EVD307000–307006 within controller grant300000–309999,
disjoint from MO/SC300000+ and Louisiana306000+.

## Why these parent values

Hahl's current Perlon vacancy portal names Hahl Inc at its Lexington address; Perlon's current portrait identifies the
PerlonNextrusion/Hahl-Pedex group. Its own issued February1,2024 release explicitly says Perlon is part of Serafin Group.
The chain is preserved rather than calling the operating group the highest parent: `Serafin Group (via Perlon Group)`.
This follows the existing `Sekisui Chemical Co. (via Sekisui America Corporation)` field pattern, not a vocabulary change.
The upper-link observation carries the source date2024-02-01; its current group profile and portal were checked2026-11-06.
Two linked old job PDFs returned404 and were discarded as unavailable routes, never closure or disaffiliation evidence.

EMS Group's Finance Report2025 explicitly lists EMS-CHEMIE (North America) Inc, Sumter, as a100%-owned subsidiary, and names
EMS-CHEMIE HOLDING AG. The subsidiary list is explicitly dated31.12.2025, used as observed_date; retrieval/check2026-11-06.
The report is primary own-issued evidence. Source quote rechecked from the downloaded PDF using pdftotext -layout.

Re:Build Composite Resources' current about page states its2021 strategic acquisition by Re:Build Manufacturing, LLC,
plus Rock Hill and composite manufacturing. This third missing parent was found by auditing all the other creates.

Nike and Yokohama already meet B-PARENT's recorded-parent condition; the correction merely flags the group source usage.
JM Eagle (documented operator trade brand) and Insulfab have operator-branded witnesses. The other11 direct-brand issuers
likewise do not depend on a group-host exception; belonging to a corporation does not make an operator-issued page a
parent-issued source. No private/licensed content, personal contacts or new commitment/tracker write.

The native entity index is absent on this Mac (ENTITIES.sqlite platform gap); the lookup reported INCOMPLETE, not absence.
Name resolution uses held Atlas legal/trade identities and the cited public group disclosures. No claim is made that a
missing catalogue means we lack a source.

## Checks and review

`python3 tasks/l3-parent-provenance-fix-2026-11-06/build.py --apply`

`python3 tasks/l3-parent-provenance-fix-2026-11-06/check.py`

`python3 scripts/validate.py`

Results: validator0errors; checker PASS19/19 issuer coverage, exact3 parent+5 flag cells,7 source-bound appended evidence,
10 injected missing-parent/missing-flag mutations all rejected, exact6 data-file boundary, every other organization/evidence
row preserved. Six-file builder replay byte-identical. Five parent quote witnesses and both publisher identity quotes were
verified raw; matcher reused from the previously calibrated evidence-repair/STRONG raw-check code. Four parent-quote mutated
suffix tests also failed as expected. No new network parser was introduced.

Two-family targeted completion refutes approved,0findings each. Controller alone merges and changes tracker status.

Main integration: restored all six affected canonical files from main5a90bb1 before builder replay; refreshed baseline org snapshots/commit. Exact field/evidence boundaries and ten fault controls still pass, validator0errors, six-file replay byte-identical. No hand-merged canonical CSV.

Codex/OpenAI targeted completion refute: APPROVE,0findings on67788eb (R-codex-1/thr_86bb34wxm8), report controller reviews/196-clerk-codex-1.md. Independent fresh7/7quotes+19/19issuers,26fake-suffix negatives; full source-chain review, exact8cells/5org/7EVD, validator0,row-loss,all6filesfresh-base builder replay,10conditionfaults and conflicting-EVD-before-write mutation PASS. Full scripts pytest/old federal checks not repeated. Grok-family approval subsequently received below. This review-record commit changes no data or code.

Grok/xAI targeted completion refute: APPROVE,0findings on3c2c59f/data67788eb (clerk-grok-6,thr_3b6qu2kt8w). Report controller reviews/196-clerk-grok-6.md. Fresh7quotes/19issuers,sourceparentchains,3parentfields5notes/7EVD,10missingconditionmutations,exact6files/oldrowpreservation/replay/validator0/row-loss PASS. Two empty-replycurl brand routes were independently checked throughFirecrawl200 byreviewer; no absence inference. Codex1 alsoAPPROVE67788eb0findings. Both approvals cover the samedata/code;3c2c59f wasREADME-only.

Finalintegration pinnedmaind1e618b: fullcanonicalrestore+unchangedbuilderreplay; baselineorgsnapshots refreshed. All7approvedEVD rows field-identical,3parents5notes/8cells5org exact;allpriorcanonicalrows unchangedexceptthosecells. Main-derivedYokohama national_footprint qualifier andallnewOH EVD preserved. check19/19+10faults/exact6files/allCSVreplay/validator0PASS. No status/tier/website/registry/graph/qualifier edits bythispacket. Controllerownsmerge/status.
