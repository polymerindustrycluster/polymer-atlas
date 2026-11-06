# L4b round4 capability second-pass packet — 2026-11-06

Preliminary packet for lead independent verification, **not a completed Atlas task or applied data**. Worker: atlas-L4b-r4-capability-packet / thr_cebszachry. Owned directory only; no data, tier, status, parent, EVD allocation, branch, commit, or tracker changes.

## Coverage and result

Frozen frame: **68 unique prior STILL_UNCERTAIN capability-only organizations**, SHA256 `dce673650244c375f8d14ba916a7646031e4de76b7849f95232b38b5bb38c63b`.

- `packet.csv`: **13 proposed field values for 8 frame organizations** (1 process value, 12 material values).
- `verdicts.csv`: **68 unique organization verdicts: 8 VERIFIED, 60 STILL_UNCERTAIN**, each hold names the missing admissible fact and the organization; explanatory exclusions in reason.
- `routes.csv`: **422 frame route attempts**, 6 per organization plus one targeted product follow-up for 14 organizations where navigation consumed attempts. All 68 attempted own-domain sitemap.xml and deeper product/PDF/capability routes before holding. Includes failures, redirects, sparse/empty extraction, Jina availability and final URLs. 25 PDF-named attempts; PDFs actually returned were extracted with `pdftotext -layout`. Empty PDF extraction fails closed (e.g. Container Compliance disclosure).
- Archive: `raw/<org_id>/*.txt` and per-org `routes.json`; paths in CSV are relative to this directory. Fresh `curl -L -A Mozilla/5.0` snapshots, not reused homepage text or summaries. Download bodies discarded after text extraction; email/phone patterns redacted from text archives. Relevant quotes remain intact. Three calibration organizations are outside the 68 and outside frame route totals.

Availability labels are transport/extraction heuristics: 217 available, 205 failed_or_empty. A short valid sitemap may be labeled failed_or_empty; an HTML/JS/index response can be available without being substantive evidence. Neither label establishes organization facts. Semantic acceptance happens only in manually reviewed `selections.json`; JS/CSS and oEmbed navigation artifacts support no values. Jina frequently returned401 and was never treated as evidence of absence.

## Scope discipline and holds

Only explicit own products/operations mapped to SCHEMA §3.1/§3.2. No customer machinery applications, no assumed resin from generic product names. Supplier product material specifications establish the offered material only, not manufacture. Polymer additives are recorded without adopting performance/safety/approval claims in the surrounding quotations. Plas-Mac pattern injection is the own plastic-pattern service, not metal casting. Mustee quote includes TOPAZ product context as requested by lead. Altor historical molding is not proposed as a current process. SPEED Group's explicit extrusion claim is held because North America attribution remains missing; no parent capability transfer. CRT tank supplier materials held rather than treating stocked equipment as own processing. CermeTech ceramic/metal composites are not polymer composites. Soil Moist synthetic acrylic does not establish PMMA; ASA polyimide/resin-bond wheels do not establish phenolic or thermoset chemistry. Organizations have no material_other_note; these stay in hold reasons. PDF catalogs have retained no original download bodies; URLs and extracted text support lead re-fetch.

## Calibration and runnable raw check

`calibration.json` records fresh own-primary known answers: Novex polyurethane belting/sheeting (`novexinc.com`), MIPCO100%-solids epoxy flooring (`mipco.org`), TUFTEX100% natural rubber latex (`tuftexballoons.com`). All three exact quoted word sequences pass the same normalized contiguous word matcher as `tasks/record-fixes-2026-11-03/build_fixes.py::has`. Wrong Novex quote “Novex manufactures epoxy floor patch from natural rubber” is rejected. `raw.Text` is reused for HTML extraction; PDF text comes from pdftotext.

From repo root:

```sh
python3 tasks/pic18-record-health-4-2026-11-06/capability/calibrate.py
python3 tasks/pic18-record-health-4-2026-11-06/capability/build_packet.py --check
```

PASS: three primary positives, one deliberately wrong quote negative; 68 unique frame organizations; 13 vocabulary-valid, unique proposed field values; all witnesses found in their fresh raw text; exactly68 verdicts and422 routes. Build command without `--check` regenerates CSVs from reviewed selections, holds and route logs. Network research can be reproduced with `research.py calibrate`, then `research.py 0 68`, then `deeper.py` (network availability and page content can change). Do not overwrite reviewed artifacts during an independent re-fetch; use a separate directory/copy.

First10 checkpoint was sent to lead and recorded in controller ledger. Lead's Mustee-context instruction and controller's unchanged baseline T1 metric ruling are recorded here; this packet computes no T1 or duplicate-adjusted metric. Lead owns application and whole-PR Codex/Grok refutation; no separate worker council requested. Repo validation/integration and duplicate research were not performed by this helper.


## Lead refutation revision — 2026-11-06

Supersedes the initial 17-value/9-organization packet. Lead thr_3zabsave2n identified the prior PR146 unresolved bridge between frame ORG-001777 American Consolidated Industries Inc and source Anchor Industries Inc. Inspection of all six archived own routes finds Anchor branding and no explicit American Consolidated DBA/ownership bridge. Shared address is insufficient. All four proposed values are withdrawn; the organization is STILL_UNCERTAIN. Missing fact: primary explicit DBA/owned-entity/merger bridge connecting the held legal organization to Anchor before using Anchor capability claims. No extra network fetch made beyond this organization's six-route budget.

Covia witness replaced with neutral own-PDF producer descriptor: “Covia’s nepheline syenite functional fillers and additives are produced”; source and raw_path now point to the already fresh-fetched PDF text. Its own rubber page supplies HIFILL N polymer-application context. No FDA/safe wording remains in the packet quote. Rechecked remaining identities: Mustee TOPAZ catalog, 31 Inc./XtraSeal manufacture context, dedicated Plas-Mac own service page, MultiPlast Systems named product pages, Akron Dispersions named producer statement, 3D Dental named Joy product, Altor named shippers, and Covia named additive producer. Material-only offerings carry no manufacturing inference; SPEED remains held for subsidiary attribution. Remaining operation proposal is Plas-Mac own plastic pattern injection; not metal casting or machines sold.

Revised result: 13 values (12 material, 1 process), 8 VERIFIED organizations, 60 STILL_UNCERTAIN organizations, 68 unique verdicts, 422 unchanged routes. Calibration and build_packet.py --check PASS. Per lead's newer “Do not write outside capability/” instruction, this revision writes no controller ledger; the report preserves the cross-thread refutation and superseding counts for lead/controller ledger recording.
