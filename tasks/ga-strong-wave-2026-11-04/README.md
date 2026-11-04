# STRONG wave: GA (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on GA's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
2 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 34)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 6 |
| VERIFIED, new organization plus its site | 16 |
| DUPLICATE_OF a held site | 1 |
| REJECT (scope or closure, with the deciding fact) | 7 |
| STILL_UNCERTAIN (with the settling fact) | 4 |

**Yield:** 22 of 34 (65%) verified.

## Applied (`build.py`)
orgs 16 {'INTL': 1, 'GA': 13, 'IN': 1, 'US': 1}; sites 22 Counter({'C': 16, 'B': 6}); evidence 268 (EVD-110001..EVD-110268); holds 0

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 18, 'no': 2, 'unfetchable': 2}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from a per-state block above main's maximum on 2026-11-04 (ORG-006267, SITE-008340, EVD-078027) and
  every open PR, set in `build.py` (`ORG0, SITE0, EVD0`). The seven states were built in sequence on one branch.

## Held
- `holds.csv`: 0.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
