# STRONG-wave site quality, continuation (rows 41-80), 2026-11-06

Controller-assigned continuation of PR #237 (`tasks/strong-wave-site-quality-2026-11-06/`, merged: 7 C→B, 33 held). It works rows 41-80 of that task's frozen `eligible_frame.csv` (161 tier-C sites, order preserved) and nothing else. Claude worker L15 (Sonnet), branch `agent/claude-code/strong-wave-site-quality-2`, evidence block EVD-330000–330999. First user: the controller and Atlas research lanes, 2026-11-06.

Acceptance criteria, fixed before research:
- Every framed site gets exactly one verdict; rows 1-40 (round 1) and 81-161 are untouched. `input.csv` must equal `eligible_frame.csv[40:80]` and every framed site row must still equal the frame on the pinned main.
- Consult T2's read-only bulk ECHO index and T1's site corpus before any live request; no index rebuild, no FRS REST.
- Promote C→B only with all seven must-have site claims at B, activity/liveness included (these records stay active). One raw own-site page must name the plant city and a present-tense activity, bound to the held operator by its own domain and by the filed street (B-PARENT: no parent-page exceptions are used). Own-site rows contain only actual page words (07:20 rule).
- Hold ambiguous identity, scope, ring, street, county and source availability, each with a settling fact. A failed or robots-blocked fetch is availability, never absence.
- No creates, org edits, registry or derived edits, vocabulary or ring changes, correction or status motion. Allocate EVD ids only in the block, after research.

## Final packet

Unit: sites in the frozen frame, rows 41-80 (8 NY, 23 NJ, 9 NC; all tier C, active at the frame).

**40 worked sites = 9 VERIFIED promotions (C→B, active retained) + 31 STILL_UNCERTAIN holds.** 63 new evidence rows = 36 government_filing + 27 own_site, all `supports_B`, seven claim types per promoted site (existence, address, code, parent, scope, activity, liveness), EVD-330000–330062. Only `verification_tier`, `sources`, `notes` and `last_verified` change on the nine site rows; every prior evidence row and every other cell is byte-identical.

| State | Frame sites | Promoted | New evidence rows | NAICS 326 strict sites before→after / QCEW 2023 private establishments |
|---|---:|---:|---:|---|
| NY | 8 | 4 | 28 | 50→50 / 410 (12.1951%) |
| NJ | 23 | 4 | 28 | 33→33 / 368 (8.9674%) |
| NC | 9 | 1 | 7 | 103→103 / 453 (22.7373%) |

Strict filter: US sites, tier A/B/C, active or unknown status, primary NAICS starts 326; the ratio is a count ratio, not matched coverage. Promotion changes evidence quality, not establishment counts.

Promoted: SITE-011167 CJK (Rochester), 011169 ECK Plastic (Binghamton), 011171 Nortek Powder Coating (Rome), 011172 Aladdin Packaging (Hauppauge), 011302 Master Bond (Hackensack), 011306 Microseal (Paterson), 011313 Innovative Resin Systems (Newark), 011317 Minor Rubber (Bloomfield), 011456 Urethane Innovators (New Bern). Each has a one-page census in `selected.csv` and `allocations.csv`. Every admitted page is on the held operator's recorded website domain. Address must-haves include county: the banked filing gives operator, street and code, and an official Census geographies response independently confirms the matched physical address and the held county (raw JSON hashes in `county_receipts.json`; coordinates are never tier inputs and no coordinate or county cell changes). ECK's page brand is Eck Plastic Arts, the trading name already recorded in the held organization note; the same-street federal ITA row is also named ECK PLASTIC ARTS. Flexcraft's page states "Holocraft (d/b/a Flexcraft)" but is held for an unrelated county gap.

### Holds (31, each with a settling fact in `verdicts.csv`)

| Count | Class | Sites |
|---:|---|---|
| 17 | Federal set not literal-admitted (held-name alias, street or primary code does not match the filed registrant): 10 code conflicts, 7 registrant-name linkages | 011173, 011301, 011303, 011304, 011305, 011307, 011309, 011310, 011314, 011318, 011319, 011320, 011322, 011323, 011452, 011454, 011457 |
| 7 | Own pages do not tie the plant or its activity to the held street | 011166 Mercury, 011168 Apple Rubber, 011170 Rimco, 011316 Keystone, 011321 Datwyler, 011451 Bonset, 011458 Arjobex |
| 4 | Scope/ring question flagged by the creating lane (owner-held) | 011312 Pan Technology, 011315 Merlin, 011455 Premiere Fibers, 011459 Colony Tire |
| 1 | Own-site must-haves now look settled (follow-up read after Grok finding on #238), but no hash-locked witness is acquirable through the house transport; promotion deferred to a later packet | 011453 Modern Polymers |
| 2 | Raw plant witness passed but the site county cell is blank, so the address must-have cannot reach B | 011308 Holocraft (Census also returned no match), 011311 Engineering Laboratories (Census: Bergen) |

Scope, ring and county questions are not self-ruled; no vocabulary, ring or type motion rides this PR.

**SITE-011453 correction (Grok finding on #238).** The hold first read "modernpolymers.com ROBOTS_BLOCKED / FETCH_FAILED", which was wrong as a reason. robots.txt disallows only `/wp-admin/`. The shared transport's agent string gets HTTP 520 from the origin on every content page (and on the http robots route, which the transport scored as ROBOTS_BLOCKED), while robots.txt and sitemap.xml return 200. A follow-up raw read with the default curl agent (HTTP 200, `modern_polymers_followup.json`, read 2026-11-06) shows `/contact/` printing "Modern Polymers, Inc. 901 W Academy St. Cherryville, NC 28021" beside "custom molded EPS or EPP foam solutions", and `/facilities/` stating "Located in Cherryville NC EPS Division: 68,000 Sq. Ft."; the quotes were checked in order. The federal row already literal-admitted (OSHA 326140), and an address-exact Census check returned PASS (Gaston County, GEOID 37071; run for this follow-up, not shipped). So the seven-claim bar now looks met, but the site stays STILL_UNCERTAIN here: the page cannot be acquired and hash-locked through the house transport, and a promotion adds data rows that need their own review. No data, evidence, id or count changed; the hold count stays 31. Effort note: this organization has now had 8 distinct URLs requested (3 home-page route variants plus contact, facilities, capabilities, service-areas and about), above the ~6 cap, at the controller's instruction; nothing is minted from them.

### Non-plant, address and code findings (`findings.csv`, correction-method leads only)

Apple Rubber's own Locations page labels 310 Erie Street "Headquarters" and 204 Cemetery Road "Manufacturing" while the held site is typed a manufacturing plant at 310 Erie. Rimco's contact page labels 316 Colonial Drive "Corporate Headquarters and Warehouse" (HQ/warehouse wording alone does not prove absence of manufacturing). Mercury's about page says it operates two distribution facilities and never places paint manufacture at 4808 Farragut Road. Infra Pipes (Rockaway) is filed as Endot Industries. PM Plastics and Thunderbird carry newer ITA primary code 333248 (machinery) against held 326199; Darnel carries a newer 326112 against held 326140. No correction, status, type or code is applied here.

## Sources, reuse and acquisition

- T2 bulk ECHO index (read-only): 27 of the 40 sites carry an ECHO registry id and all 27 resolve to a bulk row (`echo_lookup.csv`; snapshot, official ZIP URL, date and SHA-256 in `echo_manifest.json`). It was consulted for orientation and the known-answer test; no ECHO row is cited as evidence. No FRS REST requests.
- T1 site corpus (read-only): 20 current-version hash-verified receipts for 3 of the 40 domains (datwyler.com, amcor.com, saint-gobain.com), all for held sites; none supports a promotion (`corpus_lookup.csv`).
- Federal evidence is the banked OSHA ITA / OSHA inspection packet (observed 2026-11-01, with each row's own submission or inspection date retained) under round 1's literal rule: held operator alias, street, state, ZIP and primary code must match, and a newer competing code at the same street is held rather than skipped (`federal_prep.py` → `federal_review.csv`: 23 of 40 admitted, 17 held).
- Live own-site requests through the shared Corpus transport (`research.py`, `extra_research.py`; cache outside git): 59 requested URLs = 51 ok + 5 ROBOTS_BLOCKED + 3 FETCH_FAILED, over 23 federally admitted sites; counts are attempts, not verified claims. No organization had more than 6 distinct primary content URLs requested (maximum 5, Master Bond). Whole-page text lives outside git in `/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/strong-wave-site-quality-2/` (frozen pages and Census JSON), regenerated by the scripts below; `selected.csv` holds the paths and SHA-256 hashes.
- Independent public re-acquisition: all 9 selected pages were re-fetched into a fresh cache and matched their reviewed normalized-text hash and ordered quotes (9/9 PASS), which also shows the pages are stable rather than carrying per-fetch timestamps.

### Known-answer tests (run before the fetcher or matcher was trusted)

- Own-site fetcher: round 1's three known-B pages (SITE-011013, 011015, 011017) reproduce their quote; a fabricated suffix is rejected (`known_answers.json`).
- Bulk ECHO index: Mercury Paint, Nortek and Master Bond registry ids reproduce the independently banked OSHA/ITA operator name, street, city and state (`bulk_known_answers.json`).
- Census county/address: round 1's three known cases (SITE-011028, 011011, 011151) reproduce county, GEOID and matched address before any candidate was admitted (`county_calibration.json`).

## Reproduction (clean checkout)

```bash
python3 tasks/strong-wave-site-quality-2-2026-11-06/acquire.py          # re-fetch the 9 own pages, verify hashes, rewrite the persisted witnesses
python3 tasks/strong-wave-site-quality-2-2026-11-06/county_check.py     # known cases first, then the 9 candidates
python3 tasks/strong-wave-site-quality-2-2026-11-06/build.py --apply
python3 tasks/strong-wave-site-quality-2-2026-11-06/check.py
python3 scripts/validate.py
python3 scripts/check_row_loss.py --base origin/main
```

Research order, for audit: `prep.py` (freeze rows 41-80, bulk and corpus lookups) → `federal_prep.py` → `research.py` / `extra_research.py` → `select_sites.py` (quotes verified against cached pages) → `decide.py` (verdicts, id slots, findings) → `county_check.py` → `build.py`. When main moves, check out main's `data/` files, rerun the builder and `check.py`, and move the `base` pin in `baseline.json`; never hand-merge a CSV.

## Named check and review

`python3 tasks/strong-wave-site-quality-2-2026-11-06/check.py` PASS: frame equals `eligible_frame.csv[40:80]` with no overlap with round 1; 40 verdicts; 9 promotions × 7 claims = 63 rows inside the id block with immutable slots and no reuse; 3+3+3 known answers; 41 positive quote/binding checks and fabricated negatives against the persisted pages; 27 own_site rows carry only page words and no registrant, alias, registry or record ids; old rows and non-authorized cells unchanged; all other canonical bytes equal the pin; global id uniqueness; byte-identical replay; and 7 injected defects (fabricated quote, wrong binding, wrong hash, unrelated domain, dropped verdict, stale street preimage, cross-shard evidence-id collision) each fail before any write. The check itself was also confirmed to fail when a registrant word is injected into an own_site row and when an unrelated shard changes.

Review: this lane runs no `council-ask` (Claude-worker override). The controller routes the independent refutations; no approval or Done is claimed. Not checked: full script suite and hosted CI, current operating status beyond the undated present-tense page words, and the 121-site remainder of the frame (rows 81-161), which stays unworked.

## Integration pin

Main moved to `170b6a18bb6fd280565643f9dd3ec85cca0636c1` while this lane ran; it changed only `archive_links.csv`, `evidence_people.csv` and `people.csv`, none of the six shards this lane touches. `git merge origin/main` was clean. As a check, the six shards were then restored from the pin, the unchanged builder was rerun (`build.py --apply`), and the result was byte-identical to the merged tree. `baseline.json` `base` now holds the pin (`frame_commit` keeps the commit the frame was frozen against, 1cd71d0). `check.py`, `scripts/validate.py` (0 errors) and `scripts/check_row_loss.py --base origin/main` (OK) pass on this tree. Strict counts remain NY 50/410, NJ 33/368, NC 103/453.
