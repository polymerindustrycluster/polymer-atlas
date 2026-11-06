# STRONG-wave site quality, 2026-11-06

Controller-assigned continuation: merged tier-C sites created by the MN, NY, NJ, NC, TN, KY, VA and MA STRONG waves of 2026-11-04 (#116/#120). Application is delegated to L11. First user: the controller and Atlas research lanes, on 2026-11-06.

Acceptance criteria, fixed before research/application:
- Reconcile each original task's actual site creates to its published applied counts; assert unique site/cluster IDs and freeze the current tier-C subset. Every framed site receives exactly one verdict.
- Consult T2's read-only bulk ECHO index and T1's existing site corpus before live retrieval. Preserve their download/retrieval dates and hashes; no index rebuild or REST requests.
- Promote C to B only with all seven must-have site claims at B, including activity/liveness because these records retain active status. A raw own-site witness must name plant city and activity, with physical/operator binding. B-PARENT requires a previously documented parent relationship. Own-site details contain only actual page words (07:20 rule).
- Hold ambiguous identity, scope, ring, street and source availability; failed routes are never absence. List non-plant/closure/address findings separately for the correction method. No correction or status motion rides this promotion PR.
- Preserve every prior evidence row and all non-authorized record cells. No creates, org edits, registry/derived edits, or vocabulary/ring changes. Reserve EVD-279000–279999; allocate immutable selected-site slots only after research.
- Ship an idempotent builder, public witness acquisition instructions, full promotion source census, known-answer checks, fabricated negatives, before-write collision/preimage/hash checks, replay, validator zero errors and row-loss check. Require Codex and Grok refutation approvals before completion.

Controller conservation instruction supersedes the original all-161 worked scope: work ONLY the first 40 rows of the already frozen eligible frame, then one PR. `eligible_frame.csv` preserves the initial 161-C-site order; `input.csv` is its exact first40 (25MN,15NY). The remaining121 are UNWORKED, not holds/verdicts, and no continuation batch is started. Discovery outside these40 occurred before the cap and is retained as unused research; it mints nothing. Disputed promotion candidates are withdrawn and held rather than triggering another review round.

## Final capped packet

40 worked sites = 7 VERIFIED promotions + 33 STILL_UNCERTAIN holds; 121 other eligible sites remain UNWORKED. Promotions: 4 Minnesota sites and 3 New York sites, all C→B, all retaining active status. 49 new evidence observations = 28 government_filing supports_B + 21 own_site supports_B, seven claim types per promoted site. No organization, status, type, street, county, ring, code, capability, registry or derived changes. Only tier, source, notes and verification date change on the seven site rows; original evidence is unchanged.

| State | Promoted sites | New evidence rows | NAICS326 strict sites before→after / QCEW2023 private establishments |
|---|---:|---:|---|
| MN | 4 | 28 | 58→58 / 368 (15.7609%) |
| NY | 3 | 21 | 50→50 / 410 (12.1951%) |

Strict filter: US sites, tier A/B/C, active or unknown status, primary NAICS starts326; this count ratio is not matched coverage. Promotion changes evidence quality, not establishment counts.

Each of the seven promotions has a full source census in selected.csv and allocations.csv. Own-site scope/activity/liveness details are literal page words only. Every admitted domain is already the held operator's website domain; there are no cross-domain parent exceptions. Currier's already-recorded Alentra website/rebrand note is corroborated by the page's explicit “Currier ... are now Alentra” announcement; the federal Currier legal operator remains unchanged. Organization tiers are unchanged.

Address must-haves include county. The banked ITA/inspection establishes operator/street/code; an official Census geographies response independently confirms the matched physical address and county. Census coordinates are never tier inputs and no coordinate cells change. These observations cite the exact Census URL; raw JSON hashes are in county_receipts.json. Midstate's own page expressly separates physical6SpruceStreet from POBox230. The filed concatenated postal/physical string remains in government provenance; no address cell is rewritten.

### Holds, withdrawals and incidental findings

The 33 holds name a settling fact in verdicts.csv. Literal federal operator/street/ZIP/code comparisons are in federal_review.csv. Newer competing codes are held rather than silently selecting an older matching inspection. Contact/footer addresses and corporate/global capabilities do not automatically establish local plant activity.

Four proposed promotions were withdrawn before publication, with 28 evidence IDs permanently retired: Plastic Products/Lindstrom (competing ITA3M/327910 identity at the same street), Oneida (fresh acquisition ROBOTS_BLOCKED after a readable original), Stern and T.O.Plastics (address-exact Census county corroboration absent/ambiguous). Availability failures say nothing about closure or non-existence. id_slots.csv keeps all original11 slots; retired_ids.csv prevents reuse; only7 slots integrate.

No confirmed non-plant correction is applied within the worked40. findings.csv records the two worked source/code conflicts. Pre-cap incidental observations outside40 are explicitly UNWORKED: Rimco's exact street is labeled “Corporate Headquarters and Warehouse”; UFP Newburyport is “Massachusetts HQ”; Jones Plantside is HQ plus7press molding/toolshop; MGC describes resin polymerization while its held ring is2. These are correction-method leads only, with no new frame, verdict, evidence, status or type motion. HQ/warehouse wording alone does not prove absence of manufacturing. Scope/ring/dominance questions remain owner-held.

### Sources, reuse and acquisition

Before live research, consulted T2's read-only ECHO index: 132 linked bulk rows across the original eligible frame; snapshot3,233,462 rows, official ZIP URL/date/SHA in echo_manifest.json. Three known banked records reproduce exact registry/name/street/city/county fields in bulk_known_answers.json. No FRS REST or index writes. T1's existing corpus yielded73 current-version, hash-verified same-domain receipts; these were discovery, never automatic semantic support.

Pre-cap initial discovery155 requested URLs =130ok+18ROBOTS_BLOCKED+7FETCH_FAILED; first extra32 =20ok+1blocked+11failed; second extra10 =9ok+1failed. These are attempts/pages, not verified claims, and include unused research outside40. Repeated public verification and robots requests are disclosed separately, not hidden in a successful-page count. No organization had more than6 distinct primary content URLs requested by this pass; federal bulk lookups are local reads. Whole-source text stays in ignored/external caches, never in git.

Independent public reacquisition attempted11 own pages:10passed reviewed normalized hash/ordered quotes/binding,1Oneida was blocked and held; one successful page (Plastic Products) was separately withdrawn for the federal conflict. All7 surviving own pages are among those successful receipts (public_acquire_receipt.json). Nine official Census addresses were attempted after three known county/address cases;7passed and2were held. Initial county calibration caught an implementation error: Census `fromAddress` is the street-range endpoint, not the matched house number. Matching now uses `matchedAddress`; three known county/address pairs then passed before remaining candidates were admitted. No coordinate-based verification or inference is used.

Clean-checkout reproduction (no cache copy):

```bash
python3 tasks/strong-wave-site-quality-2026-11-06/acquire.py
python3 tasks/strong-wave-site-quality-2026-11-06/county_check.py
python3 tasks/strong-wave-site-quality-2026-11-06/build.py --apply
python3 tasks/strong-wave-site-quality-2026-11-06/check.py
python3 scripts/validate.py
python3 scripts/check_row_loss.py --base origin/main
```

Acquisition uses the shipped shared Corpus transport, whitespace-only normalization and reviewed full text hashes. Wrong page, missing witness, changed hash or quote fails closed. Government records use the controller-authorized banked packet vintage (observed2026-11-01), with source-specific submission/inspection dates separately retained. Re-run builder on fresh main canonical files; never hand-merge CSV conflicts.

### Named checks and review

`python3 tasks/strong-wave-site-quality-2026-11-06/check.py` PASS: exact40-prefix frame,220original-create reconciliation,161eligible/121unworked,3known own-source answers with fabricated negatives,3known bulk records,3known county/address cases, full7promotion census/all7claims,29 positive quote/binding checks, old rows/cells unchanged, all-other-canonical bytes unchanged, globalID/retirement checks, byte-identical replay and7fail-before-write faults. Validator passes0errors. Full script suite/hosted CI and independent current operating outcomes are not claimed.

Codex and Grok deep refutations requested at publication; no approval or Done claimed until both report. Under conservation instruction, disputed candidates are withdrawn/held as strict subsets, not sent through another research/review round.
