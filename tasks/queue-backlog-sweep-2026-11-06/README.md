# L13 discrete QUEUE backlog sweep

Controller09:15 BOARD assignment, new branch agent/codex/queue-backlog-sweep off main85b8560.
This new assignment supersedes the prior stop-after-final169 instruction. Programme
research scope stays closed; PR144/160/168/174 independent, review replies still handled.
Integrator delegation/controller task-status ownership unchanged. QUEUE.md is read-only.
First user: Atlas maintainer/researcher; non-use finding2026-12-06.

## Acceptance before research/application

Exactly12 discrete backlog items: Chromaflo tombstone; JVIS Ohio/TNJ Ohio as ONE alias/
legal-entity verification item (not two speculative parents); K20NorthPoint company;
Equistar grain; two parcel settlements; four PA same-street pairs; EtchedMetal R6;
Robin SITE001836. One legal verdict per item, explicit settling facts for holds.

- Read existing rows/notes/owner decisions and dedupe across all shards before creates.
  Legacy alias/merged records are not new companies. IDs only ORG013200–013299,
  SITE013200–013299,EVD310000–314999; verify global uniqueness before writes.
- Chromaflo acquired→Vibrantz treatment follows existing SCHEMA5.2 precedent, not new
  lane grain policy. Dated primary transaction outcome/legal name needed; acquisition
  news alone never proves facility closure. Derived relationships generated, not authored.
- JVIS/TNJ andNorthPoint need public primary legal identity, activity/scope, parent/HQ
  evidence; separate plants never transferred from parent assumptions. New companies C/U
  under AGENTS creation rule; no invented county or NAICS fact.
- **County ONLY from situs parcel fabric**, per this assignment. Never mailing city,
  ZIP, or coordinates. Unread/unmatched parcel route stays held; coordinates reference only.
- PA pairs link+flag, no destructive fold without dated exactsame-entity/operator proof.
  Existing tombstones remain; no record deletion, no new site-group invention.
- Equistar and R6 ring/grain questions produce owner HOLD +recommendation, never self-rule.
  EtchedMetal two-of-three evidence may be packetized/inclusion-logged without ring change.
- Raw own-source quotes, source receipts and effort cap~6/org. Failed fetch never absence.
  Before closure/no-establishment REJECT run Form5500 gate; no automatic status changes.
- Idempotent frozen builder, old evidence preserved, named row/source/key checks and
  no-write collision/preimage mutations; validate.py0errors. No scripts edits planned.
  Deep Codex3/Grok3 clerk refutes before completion approval; draft route05:55/06:25.

## Source availability

Mac entity/data-estate catalogue unavailable at Windows-only Documents paths. whois
initial basePython lackedPyYAML; rerun via ephemeral uv--withpyyaml succeeded and reported
missing entity index. This is a platform/catalogue gap, not a negative fact. Committed
canonical records/QUEUE/schema and fresh public primary sources supply this bounded task.

## Outcome and units

Frozen **12 discrete QUEUE items**: **3 VERIFIED /1 DUPLICATE_OF /8 STILL_UNCERTAIN**.
Verdicts are in verdicts.csv, with all8 settling facts/recommendations/governing readings
in holds.csv. A positive partial identity is not a completed company verification.

Canonical delta: **1 new U-tier historical acquired organization**, ORG-013200; **0 new
active organizations/sites**. **8 existing site rows** receive **22 cell edits**:
2 Ohio county/situs settlements (5cells each), and6 Pennsylvania site cross-reference
annotations (2cells each). Existing site tiers unchanged: Ohio2A, PA2A+4B.
**16 appended evidence rows**: organizations_OH6, sites_OH4, sites_PA6.
**1 generated successor_of edge**, REL-000460, from canonical successor/status/date.
Controller10:35 allocated REL460–469; this supersedes the original block list's omission
of relationship IDs. REL461–469 unused; no SITE ID allocated. EVD310000–310015 used.

- Chromaflo: SCHEMA5.2's explicit historical predecessor ruling governs; acquired
  2022-04-21 into Vibrantz ORG000007. GLEIF549300O4T63Z3HULPN02 confirms former legal
  name and current VIBRANTZ COLOR SOLUTIONS INC. entity ACTIVE. This is **not legal
  dissolution**, a site closure, a new active subsidiary, or a plant transfer. Current
  renamed-entity HQ2600MichiganAve matches Ashtabula parcel05-318-00-006-00; no historical
  HQ date inferred. NAICS325130 is explicitly researcher_inferred/low from the own
  polymer-colorants history under SCHEMA2.2, not copied from successor; conservative U
  retains code uncertainty. No founding-year convention chosen. Existing Vibrantz and
  site rows untouched (including unrelated inherited Vibrantz county inconsistency).
- ACSIC SITE001850: Franklin parcel273-001702, official situs565SMetroPl, matches own
  565MetroPlaceSSTE300. WRS SITE001907: Union parcel15-0027019.0230, official situs8485
  ESTATECOURT, matches own8485EstatesCourt. Singular/plural road spelling explicitly
  reconciled by exact house/road/ZIP. An unrelated8485AVALONLN and third-party.0270 lead
  were excluded. No mailing-city county inference; county_source=parcel. Initial Union
  quoted numeric SQL returned HTTP200/error400; corrected against integer layer metadata.
- Tredegar SITE002612 is already closed/retired as duplicate of activeSITE002486 by
  pass16. No duplicate new tombstone. Three other pairs get reciprocal counterpart notes
  and primary evidence, no folds/reparenting/registry-link edits. Taylor2025permit makes
  a strong duplicate candidate, but held org/registry reconciliation remains explicit.
  Synthomer own location names the subsidiary; subsidiary/group grain remains held.
  Scranton2025buyer outcome supports business separation, not exact current CPG premises.
- JVIS/TNJ: JobsOhio names TNJOhioLLC d/b/aJVISOhio; HQ/legal parent and transferred-plant
  schedules remain unsettled. Existing JVISManufacturingMI and TMD are not conflated.
  NorthPoint own Atlanta+Akron platform presence does not choose unique legal HQ or own
  operating establishment. K20 standard-company instruction respected; no ecosystem row.
- Owner holds: Equistar subsidiary threshold (retain ultimate-parent linkage pending
  decision); EtchedMetal R6 (recommend owner assess B+C from acrylic performance/Solon
  production+design, but locality alone does not settle decision locality and A unproved).
  Robin's current NorthCanton corporate page does not establish closure of its old
  Independence office. No status changes from omission/404/403; no REJECT for closure,
  hence no Form5500 closure gate triggered.

## Provenance, calibration and runnable checks

Primary/source URLs and short quotations: sources.csv; rawcheck.csv receipts include
fresh curl/browser-UA hash/byte count/date. Existing house W normalizer reused from
`tasks/evidence-repair-2-2026-11-04/prep.py`; existing visible HTML text extractor reused
from `tasks/pic18-record-health-2026-11-06/refetch.py` (scripts/styles excluded).
PDF via pdftotext. JSON parsed, not a summary. Official parcel query responses persist
only selected business-situs attributes; no owner/contact personal data copied. GLEIF
selected identity fields in gleif-identity.json; no registry_links edits.

Before trusting the matcher: `python3 tasks/queue-backlog-sweep-2026-11-06/rawcheck.py --known`
passed **3/3 fresh known-answer own-site addresses** (ACSIC,WRS,Synthomer); fabricated
quote rejected on all3. Then `python3 tasks/queue-backlog-sweep-2026-11-06/rawcheck.py`
passed **16/16 quote observations over15fresh URLs**, all16canonical evidence quotations
also rechecked against the same fresh documents. Fabrication rejected on every source.
Sources for held items do not masquerade as complete program/company scope evidence.
No new broad fetcher/search abstraction introduced. ~6primary routes per organization
cap retained; parcel metadata/query and selected sources recorded. Fetch failures in
fetches/followup_fetches/pair_fetches are availability only, not negative facts.

`python3 tasks/queue-backlog-sweep-2026-11-06/build.py` applies frozen rows via house
append_sorted; preflights all IDs across all shards/ecosystem and all edit preimages
before writes. Relationship fields derive mechanically from organization columns,
using house dedupe-hq-2 edge pattern, never an independently authored edge packet.

`python3 tasks/queue-backlog-sweep-2026-11-06/check.py` PASS:12-item conservation;
3/1/8verdict counts;8specific holds;fresh-base rebuild against pinned18a8f8a exactly matches
all7canonical files; all prior rows/evidence preserved; byte-identical replay. Injected
cross-shard occupied ID and wrong-county preimage fail before any write. Injected parcel
JSONerror/truncation/multiple matches/wrong road all rejected (4of4). Official narrow
parcel queries require exactly1feature and no error/exceededTransferLimit; a200alone
never passes. Derived REL has exact canonical from/type/to/date parity.

`python3 scripts/validate.py` PASS0errors after live GLEIF fetched2026-11-06 marker
correction. No scripts/ edits, fullscripts pytest not run. Prior evidence never edited
or deleted; initial uncommitted packet correction reconstructed the affected shard from
pinned main then replayed. No QUEUE, registry_links, tier1 qualifiers, federal-frame,
status or ring changes outside the one explicitly governed historical predecessor.

## Refute status

Draft PR185: https://github.com/polymerindustrycluster/polymer-atlas/pull/185
Deep adversarial Codex3 (thr_jukpm97t9c) /Grok3 (thr_4g4uwqjxjv) requests queued once each on83d8c9a with brief.md. Controller05:55 explicitly supersedes never-mode-queue only for clerk requests;06:25 assigns this pair. This receipt is docs-only; data/code unchanged.
No two-family approval or Done claim until both verdicts are received and findings fixed/held.

Dedupe command before creation: `python3 scripts/atlas.py dedupe-check --domain vibrantz.com
--name 'Chromaflo Technologies Corporation' --street '2600 Michigan Avenue' --city Ashtabula
--state OH --zip 44004 --json` (dedupe-chromaflo.json). Domain/name presumptively hit
successorORG000007; the **explicit SCHEMA5.2 former-parent tombstone exception** governs
this single historical creation, not another active company under the same domain.
ORG001475ChromaScape mentions the former company in acquisition notes; it is a distinct
held buyer, not the Chromaflo legal predecessor. No organization lives in two tables;
ecosystem shared namespace checked before create. atlas shard-of confirms OH placement.

## Grok approval receipt

Grok/xAI clerk3 (thr_4g4uwqjxjv) APPROVE 188deead996ba3fbc9e790e1c27670ac7c4551db, zero findings. Reviewed data commit83d8c9a unchanged by the prior README receipt. All12 verdicts and all16 quotations independently rechecked against fresh sources. Confirmed official Franklin273-001702, Union15-0027019.0230 and Ashtabula05-318-00-006-00 parcel matches; no Avalon or third-party.0270 substitution. Chromaflo remains the SCHEMA5.2 historical acquired U record; GLEIF renamed legal entity remains ACTIVE, not closed. NAICS325130 remains explicitly inferred/low/U.

Fresh-base replay, old-row preservation, global collision/preimage zero-write tests, four parcel defects, validator0 and row-loss pass. Canonical delta unchanged:1 U historical organization,1 generated successor edge,16 appended evidence rows,8 existing site rows edited; no new active organization/site, registry or script edit. Eight holds and all owner questions remain unresolved; no PA folds. Taylor permit quotation is a mailing address, not proof warranting consolidation. Report: controller reviews/185-clerk-grok-3.md.

Codex approval remains pending; PR stays draft without a two-family completion claim. This receipt changes documentation only. No fresh source fetches or full scripts pytest repeated for the receipt.

## Codex correction — controller ruling on unmerged evidence

Controller ruling: unmerged branch-only evidence rows are not yet canonical. Regenerate EVD310000–310015 in place with the same IDs; append-only binds rows on main. Precedent L3 PR141 EVD161300. This explicit ruling supersedes the earlier proposed retirement/replacement interpretation; no IDs retired or added. All pre-existing main evidence remains untouched. Original branch commits remain the pre-pass backup.

All new own-site claim_details now contain literal source quotations only. Internal SITE/ORG IDs, counterpart/duplicate decisions, ring/NAICS inferences and reconciliation instructions stay in record notes/verdicts/evidence notes, never attributed as the page’s own statement. Audited every new own-site row, not only the four flagged rows. Taylor government permit detail similarly states its mailing-address fact only; no fold inferred. Regenerated via exact base shards plus builder, not hand-edited canonical lines.

Builder now preflights aggregate pending-EVD uniqueness across all shards, and refuses own-site detail prefixes that exceed literal quotations before writes. Exact new/new EVD collision plus an injected internal Atlas duplicate claim both fail on pristine data with every CSV unchanged. Existing global-held-ID and county-preimage mutations remain. Edited-site tiers recomputed and asserted: PA2A/4B plus Ohio2A = total4A/4B; no tier changes. Named check/replay/old-row preservation, all16quotes fresh,4parcel defects and validator0 rerun for corrected packet. Prior family approvals do not approve the corrected guard/provenance; both same refuting/review clerks receive corrected-head requests.

## Grok corrected guard/provenance approval

Grok/xAI clerk3 (thr_4g4uwqjxjv) APPROVE 22995200f23b22670f13704e0df8191c6fddfd19, zero findings. This is the corrected-head gate; the earlier188deea approval remains historical. Verified aggregate pending-EVD collision rejection on pristine data before any write; all nine own-site claim_details are literal raw quotations only, with internal-prefix injection refused without writes. Taylor permit rows state mailing-address facts and leave duplicate decisions in notes. Edited tiers independently counted PA2A/4B plus Ohio2A = total4A/4B, no tier edits. Organization, both site shards and relationship payload remain byte-identical to83d8c9a.

Fresh rawcheck16quotations/15URLs, named replay/old-row preservation/four no-write classes/four parcel defects, validator0 and row-loss pass. Same-ID regeneration of the16unmerged evidence rows follows controller ruling; IDs remain absent from main at review. Acquired/U Chromaflo and inferred-low NAICS unchanged. Report: controller reviews/185-clerk-grok-3-rereview (review message receipt). Codex corrected-head rereview remains pending; PR stays draft without a two-family completion claim. This documentation-only receipt changes no data, code or packet. Full scripts pytest and fresh research were not repeated for this receipt.

## Final approvals and main replay

Codex/OpenAI clerk8thr_c3tss59qsx APPROVEa96bd3b,0remaining; Grok/xAI clerk3 APPROVE2299520,
0findings. Those heads differ only by README receipt; corrected guard and source-only
payload are identical. Codex independently reproduces pending310010→310000/own-site
prefix zero-write controls, all9literal own-site details,4A/4Btiercounts, all16fresh
quotes/15URLs, replay/oldrows/4parceldefects/validator0/rowloss. Targeted re-review only;
full scripts suite/eight unresolved owner/research holds not settled.

Controller-requested replay on main4f30a8ebf5dde4a2d84618ba02163bb2bad4c375: merged main,
took all seven owned canonical files exactly from main and ran unchanged builder. No
CSV hand merge. All approved packet CSVs and builder hash-identical; all main rows and
old evidence preserved except the exact22declared cells on8sites. Same1Uhistorical org,
1generatedREL,16EVD; no new site or active company. integration-final.json records counts
and data hashes. Named check/replay/4zero-write classes/4parceldefects/validator0 PASS.
base.txt now pins replay main for deterministic fresh-base check; research unchanged.
