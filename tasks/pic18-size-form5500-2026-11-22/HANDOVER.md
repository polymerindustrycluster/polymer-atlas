# Handover: Form 5500 follow-up for the 28 fills withdrawn from PR #468 (2026-11-22)

State: the packet is built and checked; nothing is applied. Branch `agent/claude-code/pic18-size-form5500-2026-11-22`, cut from #468 head cc65f3a4; no `data/` change against it.

Where things are (all in this folder unless noted)
- Builder: `build.py` (the two EIN-wide tests plus the partial-plan tests); it imports `tasks/pic18-size-sprint-2026-11-22/build.py` for the street, name and band functions.
- Extract: `extract_ein.py` streams the six national Form 5500/5500-SF zips for a list of EINs. Its input (`f5500_28_eins.csv`, site to EIN) and output (`f5500_ein28.csv`, with mailing and location lines) are NOT in the repo: controller storage, `persist/size-sprint-2026-11-22/` (the EIN list and the street lines must not be published).
- Checker: `check.py --raw <store>/raw --selftest --base-data <base>/data` (about 6 minutes over the share; last run 0 failures, 3 planted faults caught).
- Inputs: `inputs_28.csv` (the 28 withdrawn fills, no street), `INPUTS.sha256`. Outputs: `packet.csv` (22), `holds.csv` (6), `sponsor_plan_inventory.csv` (87 filings), `counts.json`, `README.md`.

Done: 22 of 28 survive both Codex tests (one plan number with positive participants; the selected return is the latest return of that plan). 21 if any other plan number counts. 0 fail the partial-plan tests (the 5500-SF field is `COLLECTIVELY_BARGAINED`). No street, EIN, sponsor or plan name is published.

Not done / open
- The owner's ruling on whole-company plans (may one plan's active participants set a site band?). Do not apply before it.
- Applying needs a NEW evidence-id range (the 28 first-head ids stay gaps in #468), one `size_band` row per fill in #468's format, a PR, and the two-family review. #468 must merge first; then rebuild against the new base.
- Not checked: that any survivor's plan covers every employee; filing years outside the six files.

The 28 sites (SITE-xxxxxx)
- Survive (22): 000068, 000076, 000152, 000275, 000304, 000310, 000339, 000405, 000488, 000544, 001565, 001568, 001593, 001606, 001664, 001667, 001719, 001834, 001856, 001900, 001909, 003327.
- Held (6): 000145 f5500_multiple_plans; 000285 newer_return_of_same_plan; 000293 f5500_multiple_plans; 001897 f5500_multiple_plans; 001972 newer_return_of_same_plan; 002113 newer_return_of_same_plan.
