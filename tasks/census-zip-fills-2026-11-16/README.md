# Census ZIP fills — atlas-w16-geo

Task claim: controller instruction 2026-11-16, separate from coordinate PR #336. Owner ruled YES on GEO-ZIP in session on 2026-11-16: a unique Census Match, Exact result may fill a blank ZIP as reference address normalization, retaining the response as provenance; never overwrite an existing ZIP. SCHEMA v1.13.2 records this ruling.

Acceptance criteria before application: every ZIP fill equals the five-digit postal ZIP in a unique Exact Census result for the unchanged input address; no nonblank ZIP or any other data cell changes; three existing recorded ZIPs agree with Census; three injected defects fail. First user: Atlas address/map maintainer at PR review; non-use finding date 2026-11-23.

Sources: six responses copied byte-for-byte from tasks/census-geocode-2026-11-16/ (Census geographies/addressbatch, Public_AR_Current / Current_Current, fetched 2026-11-16). No new fetch is needed. Reference normalization under the dated ruling requires no evidence rows or tier change. No creates, ID allocation, dedupe or inclusion-log decisions.

Run build.py then check.py in this folder. base.txt pins the main commit used for the complete data diff. proposals.csv records applied ZIP cells; holds.csv records each blank-ZIP candidate without an Exact result and its settling fact. Existing ZIPs are preserved even when different. No county or coordinate corrections are included.

Results: 5,631 US street-address site responses; 473 baseline blank ZIPs; 348 applied ZIP fills (A 54, B 223, C 63, U 8; tiers unchanged); 125 blank-ZIP holds. Three known answers are the first baseline Exact rows whose existing ZIP agrees with Census, recorded in known_answers.csv. No records created or removed.

Checks passed: `python3 tasks/census-zip-fills-2026-11-16/check.py` verifies complete response yield against the pinned site frame, all data cells, Exact ZIP equality, unchanged nonblank ZIPs, every published result count, three known answers, raw response copies and idempotence. Wrong filled ZIP, changed existing ZIP and unrelated city edit each fail the check. `python3 scripts/validate.py` passes with zero errors; `python3 scripts/check_row_loss.py --base origin/main` passes; `python3 scripts/export_vocab.py --check` passes. No shared scripts changed.

Proposed follow-ups: resolve 125 holds through unique Exact Census results or separately sourced address evidence. No fresh address verification or independent postal deliverability checks were performed; Census ZIP normalization does not establish that an operator remains at the address.
