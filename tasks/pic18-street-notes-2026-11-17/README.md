# PIC-18 streets from site notes — 2026-11-17

Designated integrator: atlas-w17-streetnotes; controller thr_9i2c6byhcz; contract w1116 (rules 13, 14). Branch/PR only; no push to main.

## Counts (unit and filter stated)
- Baseline: 1,046 active Ohio sites in a PIC-18 county; 467 of them have a blank `street_address`.
- **Frame: 392 sites** = active Ohio PIC-18 sites with blank `street_address` whose notes contain at least one street candidate (`NOTES_STREET_RE`, scripts/atlas.py). Independent count with a simple regex (number + words + street-type word): **383 sites**. The two sets differ by 9 sites, all in the frame: 7 are `State/Ohio Route`-style streets the simple regex lacks a suffix for (SITE-000518, 000603, 000983, 001122, 001137, 001606, 001940), 1 is a one-digit house number (SITE-000889, "1 General St") and 1 is a false positive of the frame regex (SITE-000132, "900 figure. Absorbed the legacy Warrensville Heights tech center" — not a street; held NO_NAMED_SOURCE). Opus-1's ~217 was a zero-dedupe-hit subset, a different filter.
- **Applied: 53 site rows** get `street_address` (blank to value, nothing else): 25 own-site pages (stored corpus raw bytes), 28 OSHA filings (ITA 25, inspection spine 3); by existing tier {'C': 20, 'A': 14, 'B': 19}. 53 address evidence rows appended, EVD-395000..395052.
- **Held: 339 sites** (STILL_UNCERTAIN, each with its settling fact in verdicts.csv). No REJECT verdicts. Summit/Cuyahoga/Stark: 7/8/6 applied of 89/97/32 frame sites.

| Hold class | Sites |
|---|---|
| NAMED_SOURCE_NOT_REACHED | 120 |
| NO_NAMED_SOURCE | 114 |
| TWO_STREETS | 47 |
| REGISTRY_CEILING | 14 |
| MAILING_OR_PARENT_LABEL | 13 |
| SUPERSEDED_OR_HISTORICAL | 13 |
| ZIP_CONFLICT | 7 |
| SIBLING_SAME_CITY | 5 |
| ADDRESS_COLLISION | 2 |
| CITY_MISMATCH | 1 |
| NOTES_RETIRED_FLAG | 1 |
| SITEWIDE_FOOTER_SUITE | 1 |
| LEAD_STREET_DIFFERS | 1 |

## How verdicts were made
Every verdict is computed by `scout.py` from fixed rules, **not read site by site**; I read only the 53 applied rows' witnesses (page context and notes) and a sample of held rows. A site is VERIFIED only when: exactly one street candidate in the notes; no mailing/PO/parent/corporate/sales label near it in the notes or in the witness text; no superseded/former/"different" wording or RETIRED flag; a witness reproduces the street with the site's city (and ZIP agrees when both exist) — own-site page from the stored corpus whose domain is on the record (org website or sources), or an OSHA row bound strong to this site (alt_site_ids empty) that the notes cite (ITA 300A, or an OSHA inspection); no other site holds the street in that city; no blank-street sibling of the same organization in the same city; no PPP/SAM lead (street-leads lane) giving a conflicting street. `build.py` re-verifies all of this from the raw bytes (quote words in order, sha256, city, labels, collisions, frozen inputs) before writing; it does not trust verdicts.csv.
- Own-site quotes are words in order from the stored raw HTML (corpus manifest.csv; shas in verdicts.csv). No new fetch was made, so no guessed URL (rule 14).
- Filings witness a historical address, not current occupancy; each such evidence row says so in claim_detail. Federal source_ref strings reuse the street-leads lane's.
- EPA FRS registry rows were NOT used (14 sites, REGISTRY_CEILING): a registry address caps at supports_C, which V-25 refuses on tier A/B sites, and the stored FRS extract has no raw/ record (V-23).
- `notes_mention_any_source` in verdicts.csv only indicates the notes mention some source anywhere; it is not the named-source test.

## Not checked / not adjudicated
- NAMED_SOURCE_NOT_REACHED (120 sites) is **not adjudicated, which means unresolved, not negative**: the notes cite an own-site/filing/TRI/FDA/parcel/Form 5500 source, but no stored witness reproduced the street. No TRI, FDA, parcel, Form 5500 or SEC record was consulted, and no fresh own-site fetch was made.
- NO_NAMED_SOURCE (114): notes cite no source (Grok list, harvest, verification-wave verdicts) or the only witness is a task-folder binding not cited on the record (settling fact names it as a recommendation).
- Hold classes were assigned by pattern (e.g. TWO_STREETS counts "street correction" notes with 2 candidate strings); not every held site was individually read. 47 TWO_STREETS sites often hold the corrected street already; a human pass could settle many.
- Sample ZIP problems: some sites have a street number in the `zip` field (e.g. SITE-001793, SITE-001806, now ZIP_CONFLICT holds); ZIP edits are out of scope.
- Prior street-leads lane holds on SITE-000237, 000241, 000640, 000889, 001606, 001661, 001673, 001538 were re-adjudicated under the above rules: where applied here, the settling fact (own-site/filing physical-address witness, city, ZIP, mailing label, same-operator sibling check) is met by a stored witness; if you disagree, those rows are the first to revert.

## Checks
- `python3 tasks/pic18-street-notes-2026-11-17/scout.py` (frame.csv, verdicts.csv), `build.py --apply` (idempotent), `check.py`.
- check.py recomputes the frame from the merge-base with origin/main and the independent count, recomputes verdict counts, re-runs the witness verification, proves street-only blank-to-value diff and evidence-block parity, byte-identical replay in a temp tree, and fails on 7 injected defects: wrong street, altered quote, mailing-labeled address, city differs, bad sha, non-street column edit, overwrite of a non-blank street.
- validate.py PASS, check_row_loss.py PASS, export_vocab.py --check PASS (2026-11-17).

First user: controller reviewing this draft PR (2026-11-17); non-review by 2026-11-24 is a non-use finding. No multi-family completion approval is claimed.

## Proposed follow-ups
- Settle TWO_STREETS (47) by hand-reading the correction notes.
- Fetch own-site pages for NAMED_SOURCE_NOT_REACHED sites under a dated fetch.
- Raw FRS fetches (raw/ copies) to allow registry rows on tier C/U sites.
- Fix `zip` fields holding street numbers.
