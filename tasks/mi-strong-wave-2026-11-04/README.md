# STRONG wave: MI (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on MI's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
5 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 106)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 17 |
| VERIFIED, new organization plus its site | 70 |
| DUPLICATE_OF a held site | 0 |
| REJECT (scope or closure, with the deciding fact) | 7 |
| STILL_UNCERTAIN (with the settling fact) | 12 |

**Yield:** 87 of 106 (82%) verified.

## Applied (`build.py`)
orgs 66 {'MI': 36, 'US': 30}; sites 85 Counter({'C': 73, 'B': 12}); evidence 1071 (EVD-100001..EVD-101071); holds 2

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 82, 'no': 3, 'no_own_url': 2}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from a per-state block above main's maximum on 2026-11-04 (ORG-006267, SITE-008340, EVD-078027) and
  every open PR, set in `build.py` (`ORG0, SITE0, EVD0`). The seven states were built in sequence on one branch.

## Held
- `holds.csv`: 2.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`, `lanes/L3/NOTES.md`, `lanes/L4/NOTES.md`, `lanes/L5/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
