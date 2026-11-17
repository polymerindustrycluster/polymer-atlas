# Ohio federal address re-match, 2026-11-16

Claim: atlas-w16-fed-rematch, controller thr_9i2c6byhcz, slug oh-federal-rematch.
Acceptance: match only existing active Ohio sites whose street was blank at 91cd1a8 and nonblank at pinned main; unique street + city/ZIP + operator-name agreement; fill only blank bands from reliable ITA rows; source-verified registry IDs; no changes to any other site field or tier. First user: Atlas controller reviewing this draft PR on 2026-11-16; no operational tool is introduced.

Frame baseline is pinned in build.py. New site IDs absent at the historical commit are excluded: absence is not a blank historical field. Independent Git diff reconciliation found 571 existing site address gains, of which 570 are active Ohio site rows. All 570 IDs appear in Git's added diff lines. The brief's approximate 440 is superseded by the reproducible 570-site frame; no sampling or hidden truncation is used.

Sources: banked 2026-11-01 OSHA ITA and inspection extracts (B-ITA-ADMISSIBILITY), plus fresh EPA ECHO exporter, streamed from ZIP and filtered to Ohio without building a national index. `echo_receipt.json` records the fresh source download and yield; full Ohio identity cache stays in controller storage. Banked ITA is a filtered extract and its unknown selection filter limits coverage; a no-match is never absence evidence.

Run `python3 tasks/oh-federal-rematch-2026-11-16/fetch_echo.py` (resumable background fetch), then `python3 tasks/oh-federal-rematch-2026-11-16/build.py --apply`, then `python3 tasks/oh-federal-rematch-2026-11-16/check.py`. Rebuild is deterministic against the pinned input. Evidence IDs use EVD-360000–363999. Registry rows and evidence append; sites change only employee_band_site. Pre-pass copies are held in controller persistence; the Git base is also a full recovery copy.

Matching reuses the historical federal-frame name_norm/street_parts/zip5, lead-fusion skey_of/name_compat/band_of, and shard_io.append_sorted. Only exact/nospace/exact-distinct/subset name levels qualify; weak/fuzzy matches and locality-only labels do not. Multiple source records at an address are held even if their names agree. OSHA inspection rows corroborate and screen ITA conflicts but do not provide band fills in this lane. R13 disagreements exceeding one band are held. Existing bands are preserved, including `unknown` (the brief authorizes blanks only).

Every candidate is listed in proposals.csv with an applied/held column and settling fact. Applied means a requested output was produced, not that a tier changed. witnesses.csv preserves matched source records. band_edits.csv, registry_proposals.csv and evidence.csv are the exact output packets. summary.json is the machine-recomputed count record.

Proposed follow-ups: registrant names differing from Atlas site names are listed in alias_followups.csv (B-ALIAS); no trade_names edits. Investigate held ambiguous addresses and name disagreement with a primary operator identity witness. No scope, status, ring, parent, address or verification-tier changes are proposed.

Validation results and final counts are appended below after execution. Independent multi-family approval is reserved to the controller; this lane does not merge or close the task.

Final result: **570 active Ohio site rows** in the historical address-gain frame; **73 FRS + 32 TRI_TRIFID link rows**, covering **91 site rows**; **12 blank site employee-band fills** (existing tiers {'A': 8, 'B': 1, 'C': 2, 'U': 1}); **103 appended evidence rows**. Registry-link and band changes together concern **98 distinct site rows**, tiers A=32, B=10, C=42, U=14. No verification tiers changed. **828 proposal rows: 103 applied, 725 held**; these are proposal units, not distinct-site units. **602 registrant/site-name comparison rows** are listed as follow-ups (including held proposals), not asserted new aliases. Evidence effects: {'supports_C': 78, 'supports_B': 11, 'supports_U': 14}.

Checks: `python3 tasks/oh-federal-rematch-2026-11-16/check.py` passed independent Git reconciliation, source yield, payload verification, deterministic replay and rejection of three injected defects. `python3 scripts/validate.py` passed with zero errors; `python3 scripts/check_row_loss.py --base origin/main` passed; `python3 scripts/export_vocab.py --check` passed; `git diff --check` passed. The direct cell-diff assertion confirmed exactly 12 site cells changed, all employee_band_site.

Not checked: live re-fetch of banked ITA/inspection filings, organizations outside this exact frame, held operator identities, independent cross-family approval (controller review pending). Government filings report historical self-reported employee bands, not current headcounts.
