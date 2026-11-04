# STRONG wave: MN (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on MN's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
3 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 48)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 8 |
| VERIFIED, new organization plus its site | 33 |
| DUPLICATE_OF a held site | 2 |
| REJECT (scope or closure, with the deciding fact) | 3 |
| STILL_UNCERTAIN (with the settling fact) | 2 |

**Yield:** 41 of 48 (85%) verified.

## Applied (`build.py`)
orgs 33 {'MN': 23, 'US': 9, 'GA': 1}; sites 40 Counter({'C': 25, 'B': 15}); evidence 513 (EVD-114001..EVD-114513); holds 1

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 36, 'no_own_url': 1, 'no': 4}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from a per-state block set in `build.py` (`ORG0, SITE0, EVD0`), above main and every open PR at build
  time. States in one batch are built in sequence on one branch.

## Held
- `holds.csv`: 1.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`, `lanes/L3/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
