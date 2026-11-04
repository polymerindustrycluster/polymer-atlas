# STRONG wave: MA (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on MA's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
3 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 56)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 14 |
| VERIFIED, new organization plus its site | 30 |
| DUPLICATE_OF a held site | 0 |
| REJECT (scope or closure, with the deciding fact) | 2 |
| STILL_UNCERTAIN (with the settling fact) | 10 |

**Yield:** 44 of 56 (79%) verified.

## Applied (`build.py`)
orgs 30 {'MA': 24, 'US': 6}; sites 43 Counter({'C': 31, 'B': 12}); evidence 514 (EVD-106001..EVD-106514); holds 1

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 34, 'no_own_url': 6, 'no_quote': 2, 'no': 2}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from a per-state block above main's maximum on 2026-11-04 (ORG-006267, SITE-008340, EVD-078027) and
  every open PR, set in `build.py` (`ORG0, SITE0, EVD0`). The seven states were built in sequence on one branch.

## Held
- `holds.csv`: 1.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`, `lanes/L3/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
