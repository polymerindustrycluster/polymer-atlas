# Pennsylvania entity-grain review — 2026-10-30

Draft PR lane: `agent/codex/pa-entity-adjudication`. Baseline: `3036121b0245bee1e6b1c8f46ed63c0a39821226`.

## What changes when this PR merges

This PR adds ten auditable case packets and a read-only drift check. It makes **zero canonical data changes**, allocates no IDs, changes no verification tiers, and executes no corporate merges or site closures. The cases are recommended review dispositions, not approved mutations. This deliberate boundary avoids destructive false merges while Muse/Grok continue integration.

`cases.json` supplies exact current IDs, full-row fingerprints, fresh source URLs, findings, and the unresolved fact for each case. Source facts are paraphrased rather than copied. Pages were read on October 30, 2026; historical documents retain their own dates in the finding. Inaccessible pages are explicitly access failures and contribute no evidence claim. The Luicana permit search result is a lead, not an observed witness. None of this packet is silently backfilled into `data/evidence.csv`.

## Results

- PA-01 Westlake: regulatory wastewater asset versus organization; resolve permit identity.
- PA-02 Pannier: likely parent duplication with an unresolved old street number and ring/code conflict.
- PA-03 MI Windows: distinct plants; resolve legal operator before consolidating parents.
- PA-04 M&Q: likely old/current-name duplication; malformed postal text must not become an invented street number.
- PA-05 Bostik/Arkema: **keep separate**, despite shared domain. Current primary source also identifies different HQs from the held records.
- PA-06 SIMONA: historical own-company evidence calls Hazleton a former plant; priority liveness adjudication, not an invented closure date.
- PA-07 Ultra-Poly: likely plant-as-parent split; retain separate physical sites.
- PA-08 Luicana: applicant mailing address versus manufacturing situs requires permit adjudication.
- PA-09 JM Eagle: certificate names two addresses; do not collapse both sites based on similar company names.
- PA-10 Rehrig: access-limited, unresolved campus/building boundary; no unsupported merge.

The standing PA same-street queue (Tredegar, CPG/Scranton, Taylor, Eastman/Synthomer) is **not claimed by this lane**. Its SITE IDs must not be confused with numerically similar ORG IDs. This packet does not alter those existing motions.

## Safe handoff

1. Fetch current main and read open PRs. A branch-local claim does not lock main.
2. Run `python3 scripts/check_review_packet.py docs/reviews/2026-10-30-pa-entity-adjudication/cases.json`. A changed or missing row blocks reuse of the packet; re-adjudicate against the new facts. Fingerprints include all columns, not just names.
3. Confirm each source's stated settling fact. Owner review remains required for ambiguous grain and historical-status decisions.
4. A later canonical change must preserve tombstones, external IDs and dependent references (sites, capabilities, memberships, evidence and relationships), carry fresh must-have evidence under schema §4.13, and allocate any new IDs at integration. This PR has no apply mode.
5. Re-run the full validator and SQLite build on the actual integration tree. Do not infer passing data validation means the entity decision is correct.

## Verification

- Full baseline and final `scripts/validate.py`: passed with existing warnings.
- `scripts/build_sqlite.py`: passed; build outputs remain uncommitted.
- `python3 -m unittest discover -s tests -p 'test_review_packet.py'`: six regression tests cover unchanged records, changed values, missing IDs, duplicate IDs, shard moves and rejection of automatic actions.
- Packet preflight: all references match the baseline.
- Remote CI is not claimed; this repository currently has no workflow file.
