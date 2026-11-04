# P3: NEW_FROM_ROSTER verdicts (packet-only)

Source: `tasks/new-from-roster-2026-11-04/NEW_FROM_ROSTER.md` on main (PR 95). The file has 100 bullet entries, numbered NFR-001..100 in file order.

- Gate A: the institution's own page shows a current faculty rank line.
- Gate B: a person-level polymer-research witness on the institution's own pages.

No IDs are minted. No contact data is included. All checks were run on 2026-11-04.

## Counts
| Verdict | Rows |
|---|---|
| VERIFIED | 15 (14 people; NFR-100 duplicates NFR-069 Grubbs) |
| REJECT | 1 (NFR-042 Lund: "Research Scientist" is a staff title) |
| STILL_UNCERTAIN | 84 |

Of the 84 uncertain rows, 8 have specific open questions and 76 are not yet checked. Every row carries a settling fact.

## Judgment calls
- Alamo (NFR-080/087) is styled "Professor Emerita". I left it uncertain pending a ruling on whether emeritus status counts as current faculty.
- Po-Chun Hsu (NFR-023) is an adjunct; left uncertain.
- Duplicates are flagged and not double-counted: NFR-069/100, NFR-080/087, NFR-079/088.
- Several lanes filed entries under the wrong institution heading. The `lane_note` column keeps the institution the note names.
- Witness URLs were located via search and are all on institution domains. Personal lab sites on non-institution domains (e.g. natolab.com) were not used.
