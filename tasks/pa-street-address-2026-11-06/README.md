# Pennsylvania street addresses — L2 continuation, 2026-11-06

Second branch/PR: agent/codex/pa-street-address. Controller allocated EVD-155000–159999 on 2026-11-06; Ohio retains EVD-150000–154999. Preparation only until the Ohio PR is open.

Baseline main bd57a08: 774 active Pennsylvania site rows, 750 streets (96.90%), 24 blanks. No blank active PA site has a site-keyed registry link. All held ITA matches for these 24 sites are moderate/weak, and all held ECHO matches are weak; none is admissible under the lane's exact/strong federal requirement. One existing address evidence row is city-grain only. Operator pages are the remaining admissible route.

Acceptance: existing active PA site rows only; street + sources and append-only address evidence; no county/county_source/ZIP/status/tier changes. Conflicting city, existing ZIP or notes street → HOLD. Raw website quotes only. All accepted fills will be re-fetched as a census (maximum 24 rows, so a 30-row sample is impossible). Validator zero errors; builder idempotence and mutation-boundary check; two-family deep refute before second PR. First user Atlas integrator, review date 2026-11-06; non-use finding date 2026-11-13.


Final pass (base c71c041, PR128 merged while Ohio stayed on its own branch): **7 active Pennsylvania site street fills**, seven own_site address evidence rows (supports_A), sparse IDs EVD-155004–155021. Record tiers unchanged: A5/B2. Active PA street coverage **750/774 (96.90%) → 757/774 (97.80%)**. No site/org creates, registry links, inclusion-log calls or other column edits beyond street_address/sources.

The parser initially admitted preceding phone fragments as part of two address candidates (e.g. `2166 1 Lark Ave`). Before any application it was tightened to reject bare numeric tokens inside a street body, and two injected phone-fragment cases were added to the known-answer check. The resulting candidates are exact raw-page substrings. Quotes remain address blocks only; no personal contacts or whole pages are retained.

Checks:
- `python3 tasks/pa-street-address-2026-11-06/build.py --known`: 3 known address blocks passed (Erie, Fallsington, Lebanon); injected wrong city/PO-box and two phone-fragment cases rejected/correctly parsed. These are parser known-answer fixtures drawn from held addresses, not claims those sites have been freshly verified.
- `python3 tasks/pa-street-address-2026-11-06/check.py`: PASS 7 fills; only street/sources change, second build byte-identical; injected pre-existing conflicting street refused.
- `python3 tasks/pa-street-address-2026-11-06/build.py --audit`: **7/7 accepted fill rows freshly re-fetched, zero missing quotes/errors**. This is the complete accepted-fill census, exceeding a proportional sample because only 7 fills exist.
- `python3 scripts/validate.py`: OK — validation passed, **0 errors**. No scripts/ files changed; the Ohio pass ran the full 221-test unittest suite (one existing skip), and this pass uses its own builder check.

Holds (unit: active PA blank site rows; verdicts in holds.csv):

| Site | Operator site | Settling fact |
|---|---|---|
| SITE-002807 | Adept Corp. - York | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002817 | Covington Plastic Molding Inc. - York | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002822 | Executool Precision Tooling Inc. - Erie | existing ZIP conflicts with own-page ZIP; geography correction is outside this pass |
| SITE-002824 | Gemini Plastics Inc. - Fallsington | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002829 | M&Q Packaging LLC - Schuylkill Haven | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002831 | Millet Plastics Inc. - Lebanon | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002838 | Oil Creek Plastics Inc. - Titusville | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002845 | Retal PA LLC - Donora | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002848 | Viking Plastics Inc - Corry | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002852 | Graham Packaging Company - Lancaster | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002854 | Quality Plastics LLC - Erie | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-003584 | Valex Group Headquarters | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-003723 | Zurn PEX Erie plant | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004115 | Acmos, Inc. — Wexford office | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004272 | Technical Process & Engineering - Lehighton HQ plant | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004558 | Norac Additives - Ambler (HQ and development lab) | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004560 | Sudarshan — Fairless Hills | need own-operator physical street page for this city; none raw-checked within cap |

SITE-002822 Executool is held because recorded ZIP13485 conflicts with own-page ZIP16505; 13485 also appears in the notes as an ISO certificate number, but correcting ZIP is outside this address-only lane. SITE-002838 Oil Creek carries ZIP45619 while its notes state16354 (and house45619); its current website fetch failed, so the notes are a correction lead only, never a street witness. No ZIP is changed. Other holds need an own-page physical address at the recorded city; unavailable or unparsable pages never prove absence.

Controller's 05:55 clerk route explicitly supersedes the brief's council-only publication order: draft PR first, then designated Codex/Grok clerks. Both technical verdicts pending. Pre-pass backups remain local and ignored.

Final independent completion refutes — both cover substantive commit e77dd5e6dd9c43299300d70809721d84b57cc731:

- Codex/OpenAI (R-codex-4, thr_x5xruuutxp): **APPROVE, zero blocking findings**. Independently fetched7/7 operator URLs with browser-UA curl, exact address quotes/operator/site context; check.py, known answers, audit and validate0errors pass; row-loss guard passes;7 street/sources-only edits,7 append-only evidence, tiersA5B2/counts750→757 of774, IDs unique/in-block, no duplicate site streets. Receipt: controller reviews/147-clerk-codex-4.md.
- Grok/xAI (R-grok-4, thr_95ffgh3rxy): **APPROVE, zero findings**. Independently fetched7/7 URLs; address quotes remain verbatim in correct city/operator contexts. Munot/Audia full-page hashes changed while quoted addresses remained present, as expected for live pages. Recomputed counts,24=7+17 verdict partition, exact7 evidence, unique IDs, row-loss guard/check/known/validator all pass. No county/ZIP/status/tier/registry changes.

Integration after reviews follows controller06:12 explicit LF exception: took main's two federal-frame LF files, then merged main9489b60. Net diff for those files vs main is zero; all seven PA site/evidence changes and source artifacts are substantively unchanged from reviewed e77dd5e. Documentation-only verdict record added. Both approvals satisfy the two-family gate; no issue closure or merge performed by this worker.
