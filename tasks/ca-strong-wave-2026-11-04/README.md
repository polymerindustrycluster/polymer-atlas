# STRONG wave: CA (2026-11-04)

The repo owner requested this pass in session on 2026-11-04 ("do it all"). The state is claimed in
`tasks/CAMPAIGN.md` (#81). The pass repeats the Indiana pilot (#75) on CA's lead-fusion STRONG clusters: those that
three or more independent federal families record. The clusters were re-deduped against today's Atlas, and
4 packet lanes ran under `LANE_BRIEF.md`.

## Verdicts (unit: candidate establishments; 78)

| Verdict | Count |
|-|-:|
| VERIFIED, new site under a held organization | 10 |
| VERIFIED, new organization plus its site | 48 |
| DUPLICATE_OF a held site | 0 |
| REJECT (scope or closure, with the deciding fact) | 5 |
| STILL_UNCERTAIN (with the settling fact) | 15 |

**Yield:** 58 of 78 (74%) verified.

## Applied (`build.py`)
orgs 42 {'CA': 25, 'US': 16, 'SC': 1}; sites 54 Counter({'C': 49, 'B': 5}); evidence 678 (EVD-108001..EVD-108678); holds 4

- **Tiers:** a site is tier B only with a federal source plus an own-site quote that the integrator re-fetched raw and
  found verbatim. Federal-only sites are tier C, and new organizations are tier C.
- **Raw check** (`rawcheck.csv`): {'yes': 52, 'no': 2, 'unfetchable': 2, 'no_own_url': 2}.
- **Sources:** federal facts are cited from the OSHA ITA and OSHA inspection extracts. ECHO/FRS ids sit in `notes` only.
- **Ids** come from this state's reserved block in `tasks/CAMPAIGN.md`, above every id used by open PRs at build time.

## Held
- `holds.csv`: 4.
- Lane flags for the integrator are in `lanes/L1/NOTES.md`, `lanes/L2/NOTES.md`, `lanes/L3/NOTES.md`, `lanes/L4/NOTES.md`. They cover scope questions for the owner, HQ disagreements
  on held records, operator changes, and sites that look closed but have no dated closure statement.
