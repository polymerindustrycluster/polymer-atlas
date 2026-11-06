# L3 CORROBORATED continuation — Louisiana

All42 Louisiana lead-fusion CORROBORATED establishment clusters are screened:2 VERIFIED,40 STILL_UNCERTAIN with settling
facts in verdicts.csv. This completes the185-cluster continuation census together with MO63+SC80 in separate PR164.
STRONG is separate mergedPR141. This PR stands on fresh main, not on the MO/SC draft.

Creates2 establishments under held Poly Processing Company and Plastipak Packaging. Both provisional tier C,
operating_status unknown;0 organizations. Adds15 evidence observations:14 site claims at C,1 primary government
registrant identity observation(A) supporting an actual company_name variant in trade_names. No held tier/status changes.
CountryUS comes from filed state/address; county remains unset. Generic city/unit labels stay in site notes, not aliases.
No registry links, derived qualifiers, coordinates, personal/private/licensed-source data or inclusion-log borderline creates.

Source: inherited OSHA ITA CY2025 public establishment extract banked2026-11-01, reviewed2026-11-06. Official source URL
keyed by establishment_ID cited on every site observation. This is filing-vintage evidence; no current operating check,
own-site witness, new bulk download or fresh registry observation is asserted. identity source ceiling government_filing
allows A for the primary registrant name; it does not promote the new plant beyond C or turn unknown status active.

Strict identity gate: filed company_name must independently normalize to exactly one active surviving held legal/trade
name. A parent/division/plant label alone is held. All linked ITA records must have reliable consistent code/street/state
and an explicit polymer production description. Existing street/state and parent/locality blank-street records block creates.
The40 holds need reliable plant-grain activity/identity/address evidence as named per cluster; no closure REJECT is inferred.
No scope or ownership rule is self-made. Dedupe includes all shards, legal/trade names, street and survivor chains, and the
create-time domain query. Every raw source field published is taken from the actual ITA row, not a fused display label.

Implementation reuses L3 MO/SC's audited mechanism (itself adapted from L11 MI/IL CORROBORATED): prep.py, build.py,
check.py, house atlas.py/shard_io.py. No dependency or import from an unmerged task folder. Acceptance in LANE_BRIEF.md;
baseline commit in baseline.json. Stable allocationSITE012500+frozen input index,EVD306000+20*index. No gap filling.

Checks:

- `python3 tasks/corroborated-la-2026-11-06/prep.py`: known3 identities(Plastipak,NikeIHM,Hydrite) PASS, injected ambiguity
  rejected; exact42 census and dedupe/verdict packet generated.
- `python3 tasks/corroborated-la-2026-11-06/build.py --state LA --apply`: idempotent global preflight and sorted appends.
- `python3 tasks/corroborated-la-2026-11-06/check.py --negative-controls`: exact42 census,3 census defects rejected,
  2C/unknown sites and15 evidence source-bound, global/reservedIDs, T3 delta; wrong-shard SITE collision must fail before writes.
- `python3 scripts/validate.py`: required0errors. All old canonical rows/evidence preserved except the one alias addition;
  builder replay byte-identical. Source-only blind review packet contains the full2-create census (fewer than20 creates).

T3 denominator QCEW2023 privateNAICS326 establishments117; numerator active/unknown A/B/C US sites with primaryNAICS326.
The held official denominator is unchanged. Ratios are counts, not matched establishment coverage. Results/reviews below.

Final checks: validator0errors; exact42 census and source/ID gatesPASS;3census defects caught; SITE and EVD wrong-shard collisions both rejected before any data write; replaybyte-identical. Actual2Cunknownsites/15evidence,0org. Only prior-record edit is registrant alias on ['ORG-001033'].

T3 strict326 establishments: 7→9 /117 QCEW2023 establishments; 5.98%→7.69%. Delta+2 reconciles to the two actual created-site codes.

Negative control initially exposed a real global-ID dictionary-collapse bug dependent on shard iteration order. Fixed by asserting SITE and EVD uniqueness before building lookup dictionaries; both injected duplicates now fail before writes. Same fix propagates to pending MO/SC PR164. No canonical data duplication occurred.

Fresh-main identity preflight also asserts the filed company_name resolves to exactly one active surviving organization at application time, preventing stale packet identity from bypassing newly added aliases. A temp-copy mutation adds that company name to another active organization; it is rejected before any data write. SITE/EVD duplicates and ambiguous operator are three independent no-write negative controls. All42 verdicts and2 creates unchanged after fresh-main screening.

Fresh-main integration at5a90bb1: all four affected canonical files restored from main before builder replay; baseline refreshed. Exact four-file boundary/all old canonical rows preserved except ORG001033 trade_names,2site+15EVD additions, all-CSV byte-identical replay, validator0errors. Address matcher now refuses empty normalized keys (the separate MO/SC Grok finding); blank/blank and leading-hash/blank negatives plus Road/Rd positive pass. No Louisiana verdict changed. Preparer excludes its own created sites during replay. Shared scripts remain unchanged.

Codex completion refute pending; draft until both independent families approve.

Grok/xAI deep completion refute: APPROVE,0findings on99c9f38 (clerk-grok-5,thr_r5auppm5ps). Report: controller reviews/198-clerk-grok-5.md. Independent live OSHA ITA bulk row check matched both establishment IDs288347/192504,company/street/state/ZIP/NAICS/submission dates; no other held site street hit. Exact2site/15EVD/1alias delta versus5a90bb1,tiersC/statusunknown/countiesblank,check42/T3 7→9/117,validator0,row-loss andID allocation PASS. Reviewer identified apparent main-versus-head tier/website differences as stale-behind, not this PR's delta. This approval-record update changes no data/code. Current operation remains unchecked; Codex approval still pending.
