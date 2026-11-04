# STRONG wave: WI (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on WI's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
3 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 47)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 7 |
| VERIFIED, new organization plus its site | 28 |
| DUPLICATE_OF a held site | 2 |
| REJECT (scope or closure, with the deciding fact) | 3 |
| STILL_UNCERTAIN (with the settling fact) | 7 |

**Yield:** 35 of 47 (74%) verified.

## Applied (`build.py`)
orgs 27 {'WI': 17, 'US': 10}; sites 34 Counter({'C': 29, 'B': 5}); evidence 427 (EVD-102001..EVD-102427); holds 1

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 28, 'no': 3, 'unfetchable': 2, 'no_own_url': 2}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from a per-state block above main's maximum on 2026-11-04 (ORG-006267, SITE-008340, EVD-078027) and
  every open PR, set in `build.py` (`ORG0, SITE0, EVD0`). The seven states were built in sequence on one branch.

## Held
- `holds.csv`: 1.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`, `lanes/L3/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
