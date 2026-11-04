# STRONG wave: NJ (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on NJ's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
2 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 32)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 5 |
| VERIFIED, new organization plus its site | 18 |
| DUPLICATE_OF a held site | 0 |
| REJECT (scope or closure, with the deciding fact) | 6 |
| STILL_UNCERTAIN (with the settling fact) | 3 |

**Yield:** 23 of 32 (72%) verified.

## Applied (`build.py`)
orgs 18 {'NJ': 14, 'US': 3, 'INTL': 1}; sites 23 Counter({'C': 23}); evidence 288 (EVD-118001..EVD-118288); holds 0

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 19, 'no': 2, 'no_own_url': 2}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from a per-state block set in `build.py` (`ORG0, SITE0, EVD0`), above main and every open PR at build
  time. States in one batch are built in sequence on one branch.

## Held
- `holds.csv`: 0.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
