# STRONG wave: TX (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on TX's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
2 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 42)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 14 |
| VERIFIED, new organization plus its site | 18 |
| DUPLICATE_OF a held site | 0 |
| REJECT (scope or closure, with the deciding fact) | 1 |
| STILL_UNCERTAIN (with the settling fact) | 9 |

**Yield:** 32 of 42 (76%) verified.

## Applied (`build.py`)
orgs 18 {'TX': 14, 'US': 2, 'IL': 1, 'INTL': 1}; sites 32 Counter({'C': 25, 'B': 7}); evidence 357 (EVD-104001..EVD-104357); holds 0

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 25, 'no': 5, 'no_own_url': 2}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from this state's reserved block in `tasks/CAMPAIGN.md`, above every id used by open PRs at build time.

## Held
- `holds.csv`: 0.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
