# Ohio people settlement, second pass — 2026-11-06

Controller-authorized continuation of L12, branch `agent/codex/people-settle-2`, separate from PR149.
Acceptance criteria were fixed before application: exactly 342 prior uncertain candidate people, deepest missing gates
first, current own-institution professor rank and polymer-material research, prospective own_site existence/scope/parent,
dedupe, immutable IDs, idempotent builder, named checks and two-family refutes. The controller owns merge/status.

Applied **16 new tier-C people** and **50 append-only evidence observations**; no existing people/evidence cells change.
IDs PERSON002100–002116 exclude permanently retired002114 (Gouma); EVD282000–282052 exclude282042–282044.
Three core claims per person produce 48 observations; Jiang's dated rank resolution and Pascall's characterization
specialty each receive one additional observation. All added values trace to public professional institutional sources.

## Candidate accounting

Unit: candidate people in the exactly 342 identities marked STILL_UNCERTAIN in the original fresh-Ohio archive.
The original archive SHA256 is `5a7f6bb37c1e838b31bba5f457b6d927d2ee28449b4e91f6d5aa993afc71fb85`.
First-PR later holds for Julie/John/Zhang/Pavel are outside this immutable input; no band-B census 572 leads enter.

| Disjoint source list | Candidate people | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---:|---:|---:|---:|---:|
| Non-OSU/non-UC helper |171|7|11|150|3|
| Cincinnati |58|2|4|52|0|
| OhioState60 |60|2|8|50|0|
| OhioState follow-up15 |15|0|2|13|0|
| OhioState follow-up8 |8|1|0|7|0|
| OhioState root30 |30|4|0|26|0|
| Total exact prior-uncertain frame |342|16|25|298|3|

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
Jiang's current Assoc Professor header conflicts with a 2018-start Assistant biography; own dated 2023 Associate
observation plus own Jianbing/Jimmy identity bridge resolves the rank. Current UC 2024–2027 PVC project carries scope;
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
| Rank/home/material conflicts | Specific missing facts in private dispositions; failed fetches never establish absence. | Current attributable own-page evidence or owner ruling. |

## Checks and provenance

`build.py` uses the existing shard writer. `reviewed.csv`, `rawcheck.csv`, `evidence_append.csv`, `withdrawn_proposals.csv`
and `base_commit.txt` freeze application and pre-pass backup. On fresh main, take main's owned data and rerun the builder;
do not hand-merge CSV conflicts. Dedupe compares normalized names, global first/surname variants and discovery aliases
against main plus the current 12 pending first-PR people. The Cyrillic-name control is preserved without ASCII erasure.

- `python3 tasks/people-settle-2-2026-11-06/check.py` — PASS: 342 exact identities;16 new tier-C people / 50 evidence rows;41 distinct raw quote keys;
  controlled-vocabulary and missing-parent mutations rejected; every pre-pass row preserved; byte-identical replay.
- `python3 scripts/validate.py` — PASS0errors, including V22/V51. No `scripts/` changes; pytest not required.
- `python3 scripts/check_row_loss.py --base origin/main` — PASS; no keyed row removed since base 620c2ec.
- Private `people-settle-2-private/account.py` — PASS: 342=16V25R298U3D; duplicate/missing-input mutations fail.
- Four actual-page known answers (Yavitt/Fisch/Park/Binienda) passed before the builder; five boundary/wrong-entry
  negatives passed. Lane checks additionally inject false quotes, wrong identity/rank and source-ownership defects.

Independent parent inspection covered all 16 proposed admissions, plus all 25 rejection witnesses and three duplicate
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

Codex and Grok deep adversarial completion reviews will be requested for the exact committed artifact. No completion
approval is claimed before both verdicts; no push to main or merge is authorized.
