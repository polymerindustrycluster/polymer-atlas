# Ohio people settlement, second pass — 2026-11-06

Controller-authorized continuation of L12, branch `agent/codex/people-settle-2`, separate from PR149.
Acceptance criteria were fixed before application: exactly 342 prior uncertain candidate people, deepest missing gates
first, current own-institution professor rank and polymer-material research, prospective own_site existence/scope/parent,
dedupe, immutable IDs, idempotent builder, named checks and two-family refutes. The controller owns merge/status.

Applied **12 new tier-C people** and **37 append-only evidence observations**; no existing people/evidence cells change.
IDs PERSON002100–002116 exclude permanently retired002101/002102/002106/002107/002114; retired evidence IDs are listed in withdrawn_proposals.csv. EVD282051 is withdrawn (retired, no replacement row).
Three core claims per person produce36 observations; Pascall's characterization
specialty receives one additional observation. All added values trace to public professional institutional sources.

## Candidate accounting

Unit: candidate people in the exactly 342 identities marked STILL_UNCERTAIN in the original fresh-Ohio archive.
The original archive SHA256 is `5a7f6bb37c1e838b31bba5f457b6d927d2ee28449b4e91f6d5aa993afc71fb85`.
First-PR later holds for Julie/John/Zhang/Pavel are outside this immutable input; no band-B census 572 leads enter.

| Disjoint source list | Candidate people | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---:|---:|---:|---:|---:|
| Non-OSU/non-UC helper |171|5|11|152|3|
| Cincinnati |58|2|4|52|0|
| OhioState60 |60|2|8|50|0|
| OhioState follow-up15 |15|0|2|13|0|
| OhioState follow-up8 |8|1|0|7|0|
| OhioState root30 |30|2|0|28|0|
| Total exact prior-uncertain frame |342|12|25|302|3|

All input IDs have exactly one disposition; no unread input is hidden as passing a gate. Rejections use positive
excluded-rank or dated death evidence. Duplicate chains terminate at held people; none are deleted or merged.
Uncertain means the required settling fact remains missing, including owner scope/vocabulary, rank/home conflicts,
current material identity, or inspectability. A bounded research review does not imply both gates were inspected
successfully for every person. Detailed review stages and availability counts remain in each lane README.

## Sources and interpretations

New department directories, named lab research statements, dated faculty catalogs/CVs and current institutional
project descriptions resolve missing facts. Known blocked engineering routes sometimes yielded usable full-page NAS
or web-engine institutional bodies. Hashes explicitly distinguish sanitized extracted text from original HTTP bytes;
no source body is published. Browser-UA curl and house Jina were tried; failures remain availability observations.

Gate A checks correct person-entry rank and surname within 40 words, with exact printed titles. Gate B requires current
polymer research objects; publication titles, menus, neighboring PI projects, historical degrees, external-lab-only
scope and natural biological molecules alone do not carry it. Own laboratory PI attribution is explicitly checked.
Jiang's current Assoc Professor department-directory and research-directory headers conflict with a 2018-start Assistant biography on the same research-directory page; the rank rests on those two current headers (EVD282033 and EVD282035). The lane's dated 2023 UC news corroboration (`lanes/uc58/rank_resolution.csv`) is no longer published as an evidence row. Current UC 2024–2027 PVC project carries scope;
external linked CV/lab are corroboration only. Fisch's dated 2026–27 catalog and linked 2025 CV agree on Associate rank;
the undated profile says generic Professor. Xu's current Tennessee profile explicitly bridges prior Akron home;
the held Tennessee institution is used without moving/merging any existing person.

SCHEMA4.9/§3 controls specialties. The earlier literal-specialty interpretation was wrong and is superseded.
Existing controlled tags only: literal PVC, elastomer and carbon-composite statements map directly to `pvc`,
`elastomers_rubber`, `composites_carbon`; unstated composite type stays `composites_unspecified`. Expert polymer
property measurements/drug-delivery programs use supported §3.5 terms. No vocabulary/scope decision is self-ruled.

| Hold | Evidence and recommendation | Settling action |
|---|---|---|
| Zheng-Rong Lu | Prior own biodegradable macromolecular MRI statement; owner-style engineered-material boundary. | Owner Gate-B ruling; unchanged hold. |
| Carlos Crespo | Prior own biopolymer photochemistry; material engineering remains unsettled. | Owner Gate-B ruling; unchanged hold. |
| Pelagia-Iren Gouma | Current own lab explicitly explains polymer-solution electrospinning and continued method development. `electrospinning` is absent from governed vocabulary. Recommend owner consider a dated process term or supported mapping. | HOLD admission; assigned002114/EVD282042–44 permanently unused; no proxy invented. |
| Jon Parquette | Functional macromolecular/supramolecular synthesis does not clearly state the narrow polymer_synthesis specialty. Codex accepted; Grok refuted. | Owner mapping;002101 and threeEVD retired, no replacement tag. |
| Bern Kohler | Excited-state dynamics/ultrafast spectroscopy of listed coordination-polymer materials does not clearly state polymer structure/property characterization_methods. | Owner mapping;002102 and threeEVD retired, no replacement tag. |
| Giuseppe Strangi | Nanoparticle optics in polymer/liquid-crystal dispersions does not clearly state polymer-system structure/property, thermodynamics or statistical-mechanics specialty. | Owner mapping;002106 and threeEVD retired, no replacement tag. |
| Geyou Ao | Engineered glycopolymer probes do not clearly state the biomedical_polymers medical-device/drug-delivery/tissue-engineering specialty. | Owner mapping;002107 and threeEVD retired, no replacement tag. |
| Rank/home/material conflicts | Specific missing facts in private dispositions; failed fetches never establish absence. | Current attributable own-page evidence or owner ruling. |

## Checks and provenance

`build.py` uses the existing shard writer. `reviewed.csv`, `rawcheck.csv`, `evidence_append.csv`, `withdrawn_proposals.csv`
and `base_commit.txt` freeze application and pre-pass backup. On fresh main, take main's owned data and rerun the builder;
do not hand-merge CSV conflicts. Dedupe compares normalized names, global first/surname variants and discovery aliases
against current main plus the frozen12-person first-PR snapshot from73cd5ee. PR149 later merged11 after Lee withdrawal; the extra retired Lee candidate makes this historical snapshot conservative, not a claim of12 currently pending creates. The Cyrillic-name control is preserved without ASCII erasure.

- `python3 tasks/people-settle-2-2026-11-06/check.py` — PASS: 342 exact identities;12 new tier-C people /37 evidence rows;41 distinct raw quote keys;
  controlled-vocabulary and missing-parent mutations rejected; every pre-pass row preserved; byte-identical replay.
- `python3 scripts/validate.py` — PASS0errors, including V22/V51. No `scripts/` changes; pytest not required.
- `python3 scripts/check_row_loss.py --base origin/main` — PASS; no keyed row removed since base 620c2ec.
- Private `people-settle-2-private/account.py` — PASS: 342=12V25R302U3D; duplicate/missing-input mutations fail.
- Four actual-page known answers (Yavitt/Fisch/Park/Binienda) passed before the builder; five boundary/wrong-entry
  negatives passed. Lane checks additionally inject false quotes, wrong identity/rank and source-ownership defects.

Initial independent parent inspection covered all16 then-proposed admissions, plus all 25 rejection witnesses and three duplicate
endpoints. Zhao's independent full institutional web body had a two-day crawl age after fresh curl/NAS failed;
other source observations retain their explicit route/freshness limitations. PDFs use real pdftotext with physical
page yields and inspected-page bounds; no PDF bytes counted as prose. No live broad API replay was needed for this
fixed continuation frame. Uncertain backlog was bounded-researched, not proved absent.

A parent audit found unrelated rendered observations attached to six OhioState60 records by substring matching. The helper
removed 47 observations and required explicit source ownership; the original defect now fails its check. Counts and
admissions did not change from that provenance repair. Parent also required the subsequent prospective vocabulary
audit, which moved Gouma from proposed admission to owner hold.

Full candidate identities/dispositions, exact source URLs/hashes and rebuild/accounting remain in durable private
`people-settle-2-private/`; `runtime_manifest.json` pins those artifacts. Only institution-supported verified facts and
aggregate counts publish. No CRM, directory biographies, personal contacts, salary values or licensed content retained.

## Independent refutes

Codex APPROVE a68c873: full16 mappings, current ranks/person-scope, three claims, raw witnesses and conservation checks.
Grok REFUTE a68c873: four specialty mappings above plus Jiang evidence detail combining multiple sources. All other12
mappings and Jiang rank/PVC scope accepted. Under controller conservation instruction, disputed admissions are withdrawn
and held rather than retagged or sent through another full review round. Retained12 people and37 evidence rows are exact
subsets of the reviewed artifact. Unmerged EVD282051 (claim_detail stated facts from other UC pages) is withdrawn and retired with no replacement row;
PERSON-002111 is retained, and the UC news URL leaves its `sources` cell because only that withdrawn row cited it.

Current-data replay starts from capturedmain4f30a8e (including merged PR149). Every captured-main person/evidence row is
preserved; no CSV conflict is hand-merged. Original a68 review snapshots/hashes are retained privately;342identityframe
is immutable and current disposition manifests are revised. The original5a7f6 archive hash is a provenance pointer;
this342checker recomputes its own frame/disposition hashes, not the separate first-pass archive. Controller owns final
strict-subset/claim-narrowing acceptance and merge; no exact-new-head technical vote is invented.
