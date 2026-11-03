# Census-gap researcher wave (2026-11-03)

**Integrator for this pass:** claude-code. The repo owner requested this pass in session on 2026-11-03.
**Lanes:** six packet lanes (`lanes/L1`–`L6`) under `LANE_BRIEF.md`. Lanes wrote only to their own folders.
**Discovery lead:** the PIC faculty census's private list of target schools. 17 major research universities on it had
no Atlas record, or a record with no people, as of main `ae47b63`. The list chose where to look and is never cited. No name, count or fact
comes from it.

**Rebuilt on main after passes 41–46.** Overnight, the R2 tranche-2 pass (pass 45) created records for all 14 of these
universities and many of the same faculty. This packet was therefore re-integrated against current main:
- every person was re-checked against `people.csv`;
- people are attached to main's institution records, matched by IPEDS UNITID;
- IDs are allocated above main's maxima.

## Applied

| Table | Rows added | Unit and filter |
|---|---:|---|
| `people.csv` | 73 | Professor-rank faculty (`PERSON-001247`–`001319`) not already in the Atlas. Each passes Gate A (faculty rank) and Gate B (polymer work stated). Both gates are met on the university's own pages. |
| `ecosystem.csv` | 0 | All 14 universities already exist on main (pass 45). |

People added, by school:

| School | People |
|---|---:|
| Berkeley | 9 |
| Utah | 7 |
| Rice | 7 |
| Stanford | 6 |
| UW | 6 |
| NYU | 6 |
| Northeastern | 6 |
| UConn | 6 |
| Maryland | 5 |
| Duke | 5 |
| UCLA | 4 |
| UT Knoxville | 3 |
| Yale | 2 |
| Columbia | 1 |
| UCSD | 0 (all already held) |
| USC | 0 (all already held) |

## Lane verdicts (unit: people examined, all lanes)

| Verdict | People |
|---|---:|
| VERIFIED | 124 |
| STILL_UNCERTAIN | 79 |
| REJECT | 49 |
| **Total** | **252** |

STILL_UNCERTAIN rows name the fact that would settle each one. Many come from fetch failures, which are availability signals,
not evidence:
- Johns Hopkins: every jhu.edu host returned a Cloudflare 403, so no JHU page was read.
- Columbia: most hosts returned 403.
- UCSD and Northeastern engineering sites returned 503s.

## Held by the integrator (`holds.csv`, 51)

**Already in the Atlas (47).**
- 44 are held at the same university, most from pass 45.
- 3 are held at another primary home:
  - Sokolov and Advincula under ORNL (SCHEMA §4.9: a joint appointment is recorded at the primary home institution);
  - Karen Lozano at UT Rio Grande Valley.
- **LaShanda Korley** is held at the University of Delaware (PERSON-000719), but NYU's pages now style her as an NYU professor.
  The Delaware record looks stale and needs re-verification, not a second record.

**Gate B review (4).** I reviewed every VERIFIED Gate B quote and held four where the polymer statement was not
person-level or named no polymer:
- Nutt (USC): the quote is the composites center's page.
- M. Chen (Utah): department area list.
- Magda (Utah): department strengths page.
- Hartgerink (Rice): "peptide nanofibers, and hydrogels".

## Follow-ups (queued)

- Re-run JHU and Columbia from a route that is not bot-walled. Re-run the UCSD and Northeastern engineering rosters.
- Settle the 79 STILL_UNCERTAIN on their named facts.
- Re-verify Korley (PERSON-000719).

## Rebuild

```bash
python3 tasks/census-gap-people-2026-11-03/build_integration.py --data-dir <pre-pass data> --hd HD2024.csv --ipeds-ror <polymer-programs-db>/incoming/ipeds_ror.tsv --ror-cache <dir>
```
