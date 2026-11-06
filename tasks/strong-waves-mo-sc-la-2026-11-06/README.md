# L3 STRONG wave — Missouri, South Carolina, Louisiana

Scope: 36 lead-fusion STRONG establishment clusters, MO 15 / SC 14 / LA 7. `verdicts.csv` is exhaustive, not a sampling frame.
The original recipe is `../mi-strong-wave-2026-11-04/`; the binding lane acceptance criteria are in `LANE_BRIEF.md`.

Sources: public operator pages selected in `research.py`, re-fetched in `rawcheck.csv`; OSHA ITA CY2025 establishments,
OSHA inspection records and DOL EFAST2 sponsor packets already held under tasks/. ECHO/FRS identifiers are notes only;
no FRS REST requests were made (shared-IP restriction from controller 2026-11-06, recorded on BOARD).

`dedupe.json` records atlas.py's four steps, including domain, normalized legal/trade names, street and successor chains.
Street matching additionally ignores mailing-city and ZIP variations. JM Eagle ORG-002260 is tombstoned: Columbia attaches
to survivor ORG-002261. Insulfab uses held ORG-006173; Nike uses ORG-003555; Yokohama TWS uses ORG-001336.
The Aurora substring in Polyply notes is a lead, not proof of common legal identity; the Aurora cases remain held.
No organizations were merged, no ownership/status changes were applied, and no inclusion-log borderline create was made.

## Build and checks

Before applying: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py`, then `adjudicate.py` in that directory.
The three known published witnesses (TG Missouri, Manchester Packaging, Insulfab) passed 3/3; appending a nonexistent token
to each quote failed 3/3. Script/style content is excluded. Failed routes are not evidence of absence.

Apply each state: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/build.py --state MO --apply` (then SC, LA).
IDs are deterministic input-index offsets in the reserved block. `append_sorted` is used for every append. Reapplication
asserts exact equality for held IDs instead of overwriting evidence. On fresh main, re-run adjudication and inspect new
dedupe hits before re-running the builder; do not merge CSV conflicts by hand.

Named checks: `python3 scripts/validate.py`; `python3 tasks/strong-waves-mo-sc-la-2026-11-06/check.py`.
`check.py` injects three missing/duplicate census defects and requires all three to fail. It also checks exact creates,
unique IDs and the per-state NAICS 326 strict-site/QCEW rise using `scripts/build_qcew_denominators.py::atlas_numerators`.
Denominator = QCEW 2023 private establishments, NAICS 326: MO 368, SC 406, LA 117; held official-source denominator file.
A ratio is not matched establishment coverage. No QCEW downloads or denominator changes are needed.

## Holds

`holds.csv` is the holds table: one cluster and named settling fact per row. Fetch availability holds remain explicit.
Agfa is held pending dated closure outcome + address-matched EFAST2, never rejected solely on a closure headline.
PIDC is excluded under owner B-SCOPE (2026-11-04), inorganic alumina output; deciding regulator source is in its verdict.
County/HQ are not inferred from postal city or plant location. Blank fields remain honest unknowns.

## Pass journal and reviews

Application counts, before/after ratios and independent review verdicts are appended below before PR publication.

- Missouri application: 7 new organizations (tier C), 9 new establishments {'C': 1, 'B': 8}; 98 evidence observations. `validate.py`: zero errors. Builder replay: passed.
- South Carolina application: 4 new organizations (tier C), 6 new establishments (tier B); 64 evidence observations; 2 held-parent alias updates. `validate.py`: zero errors. Builder replay: passed.
- Louisiana application: 4 new organizations (tier C), 4 new establishments (tier B); 48 evidence observations. `validate.py`: zero errors. Builder replay: passed.

Final census: {'STILL_UNCERTAIN': 16, 'VERIFIED': 19, 'REJECT': 1} across the 36 STRONG establishment clusters. Creates: 15 organizations (C), 19 establishments (18 B / 1 C), 280 evidence rows (210 original + 70 supplemental); 4 held-parent alias additions.

| State | QCEW 2023 NAICS 326 private establishments | Atlas strict before | Atlas strict after | Strict/QCEW before → after |
|---|---:|---:|---:|---:|
| MO | 368 | 37 | 43 | 10.05% → 11.68% |
| SC | 406 | 49 | 52 | 12.07% → 12.81% |
| LA | 117 | 6 | 7 | 5.13% → 5.98% |

`check.py`: PASS, exact 36/36 verdict census, 3/3 injected census defects caught, 19 applied sites, unique IDs, T3 rises in all states. Prior-row comparison against pre-pass commit: every old evidence row preserved; only four old organization trade_names fields gained aliases. All three builder replays are byte-identical across 16 changed data files.

### Held clusters and settling facts

| Cluster | Settling fact |
|---|---|
| LF-MO-00006 | Need a polymer formulation or captive shaping witness; contract filling alone does not settle scope. |
| LF-MO-00018 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00053 | Need polymer-binder formulation at Clifton Avenue; broad chemical blending and distribution does not settle site scope. |
| LF-MO-00120 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00165 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00289 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00047 | Need polymer-specific production or qualifying polymer value-chain focus at Rock Hill; metal finishing alone is insufficient. |
| LF-SC-00129 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00198 | Closure reporting found; need dated primary outcome and address-matched EFAST2 check before any closure REJECT. No active create. |
| LF-SC-00206 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00302 | Need Laurens foam-control product binder/composition; silicone/polymer formulation versus nonpolymer defoamer not settled. |
| LF-SC-00326 | Need primary operator identity linking Curd Enterprises to Multiplastics and current manufacturing at 476 Long Point Road. |
| LF-SC-00358 | Need captive polymer processing or site-grain Ring 4 two-of-three test; chlorination equipment alone is insufficient. |
| LF-LA-00029 | Need dedicated polymer line or polymer-specific value-chain witness; sulfuric acid regeneration alone is insufficient. |
| LF-LA-00183 | Need current operator/site identity after Berry/Amcor transaction, and plant-specific polymer scope at 4611 Central Avenue. |
| LF-LA-00234 | Precursor-only Ring 3 precedent applies, but dated current operating outcome and operator after restructuring must be settled before active create. |

Controller 2026-11-06 authorized merge of origin/main instead of rebase to preserve the two pre-existing CRLF-dirty federal-frame files; this supersedes the lane rebase-only route for this integration. Controller also authorized publishing draft for queued refute-clerk review while saturated council calls remain pending; two-family approval is still required. Reviews pending at this checkpoint.

### Grok initial REFUTE and correction

The initial Grok 4.7 deep review REFUTED four weak scope/plant witnesses, own-site attribution of new-org federal aliases,
and missing address/count-composition checks. All original evidence rows remain untouched. Five raw-checked supplemental
quotes in `supplements.csv` now provide Davis coating activity, CMP's Louisiana address, Hahl's Lexington address, Sun's
Belle Chasse manufacturing location, and its own Lubra-Glide copolymer manufacturing technical sheet. The PDF was freshly
fetched with curl and extracted with pdftotext 26.10.0; its manufacturer sentence is verbatim. Government filing activity
descriptions complement plant-only own-site witnesses. Every federal alias group now has a source-specific government
observation (including the actual EFAST2 sponsor filing); these answer the earlier weak own-site attribution. Supplemental
IDs occupy 165000+ within the lane block. Total evidence observations are now 280 (70 appended); creates unchanged.

The builder now asserts every used federal street matches the input physical street using atlas.street_key and the same
state, and refuses changed verdict order. `check.py` ties raw quote/URL to verdicts, supplements to evidence, checks exact
15/19/280 counts, and reconciles each state's strict 326 increment against the actual created-site codes: MO +6, SC +3,
LA +1. Ring 1 counts differ because federal NAICS codes outside 326 remain as filed; no count is hidden or relabelled.
The reviewer had only a text packet and explicitly did not inspect federal data. Follow-up review includes the resolved
federal witness metadata and created-site code composition.

Corrected validation: `validate.py` zero errors; `check.py` PASS; `prepare.py --supplements-only` 5/5 raw quotes, PDF mutation rejected. Every prior evidence row byte-for-field identical across 8 supplemental shards; all-state builder replay byte-identical. Corrected re-review pending.

### Codex initial REFUTE and parent correction

Codex independently confirmed the census, source quotes, dedupe, prior-row preservation and T3, but REFUTED alias source
attribution (answered above) and CMP's group-domain classification without a recorded parent. The source explicitly identifies
Chugoku Marine Paints and lists CMP Coatings with its Louisiana address. The builder now records `ultimate_parent_name`
Chugoku Marine Paints, Ltd. on the new CMP organization, adds the B-PARENT-WEB group-domain notes flag, and appends parent
observation EVD-169900. No pre-existing organization parent or ownership field changes. This satisfies B-PARENT's documented
relationship condition; CMP's federal marine-paint manufacturing witness and raw group-page plant address supply activity/city.
Evidence final total: 280 = 210 original + 70 append-only supplements. Corrected validation and replay pass; re-review pending.

### Final independent completion approval

- **Codex/OpenAI APPROVE**, clerk-codex-3 thr_jukpm97t9c, reviewed bcb3344. Fresh raw quote checks, 27 alias/source observations,
  injected federal street/state mismatches rejected before writes, all-data replay byte-identical, validator0errors, row-loss
  guard PASS, exact36/15/19/280 counts and T3 deltas independently reproduced. Original210 observations unchanged,70 appended.
- **Grok APPROVE**, clerk-grok-3 thr_4g4uwqjxjv, reviewed f903cb0 (same data/code, before authorized normalized-main merge).
  Findings0. Fresh 5 supplemental quotations/PDF,28 federal street/state matches, full-create dedupe and alias citations,
  row-loss guard, validator0errors and check.py PASS. Original initial REFUTEs are preserved in the task review files;
  their substantive findings were fixed, not waived. The Grok stale-count documentation note is corrected here.

Review limits: Codex targeted re-review did not repeat the full initial random-row/dedupe audit or bulk government downloads.
Federal-vintage and provisional C limits remain explicit; neither family claimed a new federal download or closure outcome.
Controller's required two-family completion gate is satisfied for this STRONG PR. Controller alone merges/statuses tasks.

### Subsequent Grok REFUTE — alias source attribution removed at root

R-grok-1 REFUTED bcb3344 after earlier approvals: the original own-site existence rows still asserted federal alias lists.
The controller agreed, held the PR, and explicitly authorized regenerating these **unmerged lane-only** observations with
unchanged IDs, superseding the earlier preserve-every-local-observation interpretation for this correction. This does not
edit any evidence row on main. The builder now writes only legal_name and website on own-site existence observations;
registrant names remain solely in government observations and trade_names. All280 lane evidence rows were checked:
**zero own_site rows contain “federal registrant aliases”**; EVD-161300 no longer contains KOLLER ENTERPRISES. Earlier
statements that all210 original lane observations were unchanged describe the prior reviewed checkpoint and are superseded
by this authorized regeneration. All pre-existing main evidence is preserved unchanged.

Main bdb8b98 merged by taking main's conflicting evidence_OH and replaying all three state builders on main data. Named
validator/check/replay gates pass, counts/tiers/T3 unchanged. PR returned to draft. Targeted R-grok-1 re-review pending;
previous approvals do not override this valid subsequent finding.
