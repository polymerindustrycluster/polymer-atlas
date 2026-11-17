# PIC-18 capability corpus pass — 2026-11-16

Designated integrator: atlas-w16-capabilities. Controller contract overrides the queue-edit rule; no QUEUE write. First user: PIC cluster reporting analyst; review use by 2026-12-16. Draft for controller review, not a completion claim for all missing capabilities.

Acceptance: only processes/materials cells on eligible sites; append reserved CAP/EVD rows; preserve all other cells and all existing rows; exact witnessed terms; menu strength C and capability-only on A/B; no organization changes. One draft PR, no merge.

## Frame and yield

224 active tier A–C PIC-18 Ohio sites have a blank process or material field, an organization with exactly one active Atlas site across all shards, and at least one stored corpus text page. Excludes every site in either frame or verdict file of b01/b02. `base.txt` pins the input tree; `frame()` recomputes it independently of committed `frame.csv`.

14 term decisions cover 4 sites; new data is applied to 3 sites (1.34% of 224 frame sites). The other 220 sites are held without admitted terms, and Apollo's three menu terms are held from section-3 tags. Three site rows gain tags (two tier B, one tier A), with 11 supports_A evidence rows. Eight company_disclosed capability rows cover two tier B sites. Apollo is tier A: injection molding and PVC already have live capability rows, and tooling has no §3.6 term, so it receives no new data. Evidence range EVD-377000–377010; capability range CAP-001100–001107. No tiers changed, inclusion decisions or organization/site creates.

`verdicts.csv` has an applied/held disposition for every proposal and one hold row for every remaining frame site, with its settling fact. These holds mean no plant allocation was admitted in this pass; they are not claims that the capability is absent. The 220 holds have not all received individual human-like adjudication; corpus screening is not exhaustive verification. No additional fetches were used.

## Sources and decisions

Stored own-site pages supplied by the controller, fetched 2026-11-16: esterle.com, apolloplastics.net, inter-ion.com, cosarmold.com. Decisions retain exact quotes, page/raw paths, hashes and locality witnesses, never whole contact-bearing pages. `check.py` verifies raw SHA256, ordered raw words, normalized text substring, locality witness, vocabulary, full-row preservation, append-only delta, output counts and byte-idempotence. It fails on injected false quote, invalid term, and false locality witness.

Reuse: b01/b02's narrative/menu distinction, fill-blank scope, §3.6 exact mapping, and the 2026-11-14 ruling. No broad umbrella inference was needed. CAP rows carry their own quote and provenance; as in b02, A/B menu-only holds mint no C-strength section-3 evidence row. Existing matching capabilities are not duplicated.

## Replay and checks

Run `python3 tasks/pic18-capabilities-corpus-2026-11-16/build.py`, then `python3 tasks/pic18-capabilities-corpus-2026-11-16/check.py`. Larger raw pages remain in controller storage, required for replay. Replay is additive in the two allowed site columns and refuses mismatching preexisting reserved IDs. `check.py` is deliberately pinned to the initial tree for this draft; after a merge of main, rebaseline and review overlap before claiming exact replay.

Pass journal: canonical files backed up from pinned base into controller persist/pic18-capabilities-corpus/backups; application limited to the three authorized CSVs. No shared scripts changed. Checks recorded in CHECKS.txt.

## Proposed follow-ups

- Allocate Boardman's disclosed capabilities among its multiple plants.
- Bind C4 materials to warehouse versus headquarters.
- Review the remaining 220 holds individually for explicit plant allocation; apply no org-wide claim to an unproven plant.
- Controller to obtain the required two-family refute review before merge; worker contract prohibits council calls or other-thread review requests.
