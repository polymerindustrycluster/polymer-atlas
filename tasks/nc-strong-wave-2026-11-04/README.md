# STRONG wave: NC (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on NC's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
2 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 35)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 12 |
| VERIFIED, new organization plus its site | 13 |
| DUPLICATE_OF a held site | 1 |
| REJECT (scope or closure, with the deciding fact) | 3 |
| STILL_UNCERTAIN (with the settling fact) | 6 |

**Yield:** 25 of 35 (71%) verified.

## Applied (`build.py`)
orgs 13 {'NC': 11, 'US': 1, 'IL': 1}; sites 25 Counter({'C': 19, 'B': 6}); evidence 275 (EVD-120001..EVD-120275); holds 0

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 22, 'no_own_url': 1, 'no_quote': 1, 'no': 1}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from a per-state block set in `build.py` (`ORG0, SITE0, EVD0`), above main and every open PR at build
  time. States in one batch are built in sequence on one branch.

## Held
- `holds.csv`: 0.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
