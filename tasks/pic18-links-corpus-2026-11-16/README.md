# PIC-18 corpus navigation links — 2026-11-16

Claim: atlas-w16-links, controller thr_9i2c6byhcz, designated integrator for the three navigation columns only. First user: John, company profile lookups after merge; non-use review 2026-12-15. Acceptance: deterministic stored-HTML witnesses, blank cells only, schema v1.11, no unrelated column changes, replay without changes.

## Result and units

Frozen frame: 958 organization rows with a website and an Ohio establishment in PIC-18, independently reconstructed from base.txt. Input manifest: 3,604 page attempts across both corpus passes. Of 2,668 originally blank navigation cells, 234 cells filled on 176 organization rows: 25 LinkedIn company links, 162 newsroom indexes, 47 declared RSS/Atom URLs. The affected organization rows retain their tiers: A 83, B 85, C 7, U 1. No record creates, tier changes, evidence rows or inclusion-log changes.

2,434 cells held: LinkedIn 806, newsroom 737, feed 891. Each blank-cell proposal has an applied/held column and a named settling fact in [proposals.csv](proposals.csv); this includes cases with no eligible stored witness. Existing nonblank cells are retained. Sources are the public organization pages identified by source_url, raw_file and sha256 in that packet. The corpus itself remains in controller persistence; only metadata and link witnesses travel.

## Method and precedent

Imports canonical company-URL parsing, header/footer ancestry detection and own-domain checks from linkedin-navigation-2026-11-06; reuses its normalized legal/trade-name identity and shared-domain classification. All HTML company anchors participate in the multiple-slug hold, including body links; only header/footer anchors can fill. Personal and share links cannot fill. No requests to LinkedIn or any other network service are made.

Imports newsroom label, feed declaration and registrable-domain parsing from newsroom-urls-pic18-2026-11-06. Eligible news-kind pages require a recognized index path; home-page header/footer/nav links require an index label and recognized path. Ambiguous indexes are held. RSS/Atom links must be explicitly declared on the chosen or existing newsroom page, be own-domain, and not be comment feeds. Feed contents are not fetched or asserted. Reader-only text captures lack HTML anchors and cannot fill. HTML hashes are verified before parsing; unavailable pages assert no absence.

Schema v1.11 and both predecessor builders treat navigation as navigation, minting zero evidence rows. Reserved EVD-386000–386999 remains unused. Only linkedin_url, newsroom_url and newsroom_feed_url change. Pre-pass shard backups reside in controller persistence at pic18-links-corpus-backups/.

## Reproduce and check

Run `python3 tasks/pic18-links-corpus-2026-11-16/build.py --apply` to replay the frozen packet. `--freeze` is for original packet creation only, not replay. Run `python3 tasks/pic18-links-corpus-2026-11-16/check.py`: recomputes every proposal from pinned HTML, independently reconstructs the input organization census, checks the entire base-to-current organization cell delta, proves byte-identical reruns, and rejects changed-value, missing-row and duplicate-row defects. summary.json carries all published counts.

Passed: lane check (3 injected defects rejected); `python3 scripts/validate.py` (0 errors); `python3 scripts/check_row_loss.py --base origin/main` (no rows removed); `python3 scripts/export_vocab.py --check` (current). scripts/ is untouched. Full repository test suite and live page/feed fetches were not run. Cross-family completion review is controller-owned; this PR stays draft.

## Proposed follow-ups

- Resolve each held cell only when its named settling fact is available; expand the conservative index-path allowlist through a separately reviewed pass if needed.
- Confirm navigation use by the first user on the stated review date.
