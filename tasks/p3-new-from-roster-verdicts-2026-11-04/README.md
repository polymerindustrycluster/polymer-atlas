# P3: NEW_FROM_ROSTER verdicts (packet-only)

Source: `tasks/new-from-roster-2026-11-04/NEW_FROM_ROSTER.md` on main (PR 95). The file has 100 bullet entries, numbered NFR-001..100 in file order.

- Gate A: the institution's own page shows a current faculty rank line.
- Gate B: a person-level polymer-research witness on the institution's own pages.

No IDs are minted. No contact data is included. All checks were run on 2026-11-04.

## Counts (pass 2: all 100 rows checked)
| Verdict | Rows |
|---|---|
| VERIFIED | 78 (77 people; NFR-100 duplicates NFR-069 Grubbs) |
| REJECT | 7 |
| STILL_UNCERTAIN | 15 (2 are duplicates: NFR-087 of 080 and NFR-088 of 079) |

All rows have now been witness-checked. Every uncertain row carries a settling fact.

### Rejects
- NFR-042 Lund: "Research Scientist" is a staff title.
- These people are no longer at the institution the lane filed them under. Each is a lead for re-filing at the new institution:
  - NFR-020 Sangoro, now at Ohio State.
  - NFR-027 Ratcliff, now at Georgia Tech.
  - NFR-073 Biqiong Chen, now at Liverpool.
  - NFR-081 Adam Smith, now at Mississippi State.
  - NFR-086 Venerus, now at NJIT.
- NFR-084 Maldarelli died in July 2026 (CCNY ChE department announcement).

### Uncertain, by settling fact
- **Emeritus ruling needed:** NFR-080/087 Alamo, NFR-015 Mark Green, NFR-046 Currie (retired 2024).
- **Gate A missing or adjunct:**
  - NFR-014 Dong Meng: no NYU rank page found.
  - NFR-023 Hsu: adjunct at Duke; primary appointment at UChicago.
  - NFR-050 Sims: no faculty page found.
  - NFR-097 Jia: UNMC former-lab-member listing; current status unclear.
- **Gate B weak (rank is fine):** NFR-008 Fong, NFR-039 Nikkhah, NFR-054 Viijayan, NFR-056 Gerlach, NFR-083 Reinemann, NFR-090 Jie Lian.
- **Duplicate:** NFR-088 (of 079 Hallinan, now VERIFIED).

## Judgment calls
- Emeritus/emerita titles are held as uncertain pending a ruling (Alamo, Green, Currie).
- Pomeroy (NFR-007) is "Senior Lecturer with Security of Employment", which is UC's teaching-professor faculty rank. I treated it as a faculty rank, by analogy with the Principal Lecturer ruling.
- Istrate (NFR-074) is a UK "Senior Lecturer", which I treated as a faculty rank.
- Research Assistant Professor counts as a faculty rank: Lima (NFR-034) and Romanova (NFR-095).
- Some rows use one institution page for both gates because the profile states both rank and polymer research: 030, 040, 053, 057, 066, 071, 075, 082, 091, 092, 095, 096.
- Gate B sources that are institution-hosted but non-standard:
  - NFR-076 uses scholarworks.utrgv.edu.
  - NFR-085 uses sites.google.com/iit.edu.
- NFR-076 Gate A rests on a UTRGV centre faculty page.
- NFR-084's death notice is the department's own LinkedIn post, not a ccny.cuny.edu page.
- Several lanes recorded the wrong rank. Where the institution page differs, the institution page wins; for example, Ricarte (NFR-077) is now Associate Professor.
- Duplicates are flagged and not double-counted: NFR-069/100, NFR-080/087, NFR-079/088.
- Several lanes filed entries under the wrong institution heading. Verdicts use the person's actual institution, and `lane_note` keeps the original note.
- Witness URLs were located via search and are on institution domains. Personal lab sites on non-institution domains were not used.
