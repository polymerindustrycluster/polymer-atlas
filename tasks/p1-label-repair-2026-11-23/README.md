# ATLAS-38 public-field label repair (G4)

Built by: Codex GPT-6.2 Sol (atlas-p1-integrator-1), 2026-11-23.

This applies the controller-approved partial repair under owner round 24
item 1. The packet pin is 1eb16577d3bafad6f4b2ca1a8ecaf3deca5578fc. The
integration resolves record IDs against the current canonical shards
and matches every exact old cell before writing.

| Corrected field | Cells |
|---|---:|
| Organization NAICS source name | 1,743 |
| Organization and ecosystem descriptions | 142 |
| Program facilities note | 1 |
| People sources | 1 |
| Total | 1,887 |

The NAICS subset has 1,338 explicit public source names and 405 existing
researcher assignments. Of the 405 assignments, 350 retain a date stated
in the old label and 55 retain undated attribution. The published NAICS
codes, source types and confidence values were checked against the pin.
The 143 prose repairs remove the approved internal wording.

The one people edit removes one contact-bearing citation and preserves
three citations. The packet uses the exact old-cell SHA-256 for this
edit and the checker compares it before writing. The people contact scan
goes from one affected cell to zero across all 1,614 people rows.

## Scope and remaining work

The strict descriptive scan currently reports 830 held cells, listed in
`OPEN_QUEUE.csv` with current path and line locators. Of those, 603 NAICS
source names require a public-source lookup (410 company-disclosed,
149 government filing, 43 directory-assigned and one own-site) and 227
other descriptive cells require review. The packet's old pinned scan
also reports provenance and structural matches as report-only. Audit
withholding remains the owner-approved treatment for unresolved phrases.

Counts by verified record tier, using changed cells as the unit, are
583 A, 1,072 B, 212 C and 20 U. The 1,887 entries in
`CLAIMS_CHECKED.csv` are corrected cells. The edits use the existing sealed
witnesses and recorded source labels. The prior #513 census audit covers
its eight admitted permit observations and six process fills.

## Check

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-label-repair-2026-11-23/check.py --at HEAD
```

The check verifies the controller's eight sealed packet files, runs the
lane replay and its planted faults, reapplies every approved cell repair
against the integration base, and compares the exact canonical diff and
both ledgers. The lane's strict report exits 1 with 830 in-scope holds.
Integration requires that exact held population and zero post-edit people
contact matches. The lane's Sonnet verifier approved the seeded 60-cell
sample from the original edits and the 20-cell researcher-assignment
sample. Source re-fetching and adjudicating held wording were outside
this batch.
