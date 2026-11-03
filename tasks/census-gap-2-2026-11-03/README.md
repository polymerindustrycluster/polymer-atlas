# People wave 2: census-gap follow-ups and band-A census leads (2026-11-03)

**Integrator for this pass:** claude-code. The repo owner requested it in session on 2026-11-03 (handoff items 2 and 4).

**Gates:** these are unchanged from `tasks/census-gap-people-2026-11-03/LANE_BRIEF.md`, with this wave's deltas in
`LANE_BRIEF.md`:
- Gate A: a professor rank.
- Gate B: a sentence about current polymer research.
- Both must be on the university's own pages.

**Discovery leads:** two sources, neither ever cited.
- The first wave's STILL_UNCERTAIN rows.
- The PIC faculty census, a private list. Its band-A rostered people not yet in the Atlas were exported to a
  **local-only** lead list, which is not in this repo.

## Applied: `data/people.csv` +51 (PERSON-001334 to PERSON-001384), all tier A

| Source | People records added |
|-|-:|
| Census-gap follow-ups: lane T (JHU, Columbia), lanes R1 and R2 | 19 |
| Band-A census leads: 4 lanes, run locally | 32 |

**Admission rule** (`build_people.py`). A person record is admitted only when all of these hold:
- the lane verdict is VERIFIED;
- the **raw-page check** passes (`raw_check.csv`). The integrator re-fetched every gate URL raw and found both quotes
  word for word. Pages came from the NAS Firecrawl, and jhu.edu and columbia.edu pages from the Tavily extract cache
  (owner-approved route, 72 URLs used);
- the role is in the university professor vocabulary;
- all URLs are on the institution's own domain;
- the institution is already held, matched by IPEDS UNITID;
- the name is not already in `people.csv`;
- the integrator's review of every Gate B quote did not hold it.

No institutions were created.

## Census-gap follow-ups (unit: people examined)

The first wave left 79 people STILL_UNCERTAIN (`uncertain.csv`):
- 13 are already in the Atlas: 12 at the same university, and 1 (Herrera-Alonso) at another institution.
- 3 are owner questions: B-CG-1 and B-CG-2, in the 2026-11-03 owner battery.
- 63 were re-run.

| Lane | Input people | Sweep people | VERIFIED | Raw check passed |
|-|-:|-:|-:|-:|
| T (JHU, Columbia; via Tavily) | 8 | 23 | 9 | 9 |
| R1 (+ Northeastern roster sweep) | 28 | 5 | 14 | 12 |
| R2 | 27 | 0 | 5 | 4 |

The rest are REJECT or remain STILL_UNCERTAIN in each lane's `people.csv`, each with its settling fact.

## Band-A census leads (unit: people examined)

The census lists 1,176 rostered people (people it found on the school's own roster page). 765 are not in the Atlas
at the same school: 133 in band A and 632 in band B.

The 133 band-A people went through four lanes:

| Outcome | People |
|-|-:|
| VERIFIED | 38 rows, 37 people (one person appeared twice) |
| Raw check passed | 38 of 38 rows |
| Already held | 11 |
| Rejected or still uncertain | the remainder; emeritus styling was the commonest Gate A failure |

Band-A precision through the full gates is therefore about **28%** (37 of 133 people), well below the census's own
band-A spot-check. Band B (632 people) has not been run.

## Held (`holds.csv`, 15)

- **Integrator review (12):**
  - 5 rest on news items instead of the person's own pages: Wiley, Erb, Gupta, Nguyen and Monroe.
  - 2 rest on department research-area pages: Yang Yang and Jenn-Ming Yang.
  - 1 rests on a consortium page: Vorst.
  - 2 have a biological polymer as the Gate B object, held for owner battery B-CG-2: Ribbeck and Schroeder.
  - 1 has a title that is a sentence fragment: Kokkoli.
  - 1 is a duplicate row: Jeff Moore, the same person as Jeffrey S. Moore.
- **Raw check (2):**
  - Czabaj: the Gate A quote is not on the page.
  - Kirshenbaum: the Gate A page could not be fetched.
- **Already held elsewhere (1):** Sokolov is held at ORNL (PERSON-000478). Joint appointments are recorded at the
  primary home.

## Rebuild

```bash
python3 tasks/census-gap-2-2026-11-03/build_people.py --data-dir <pre-pass data> --raw tasks/census-gap-2-2026-11-03/raw_check.csv \
  --school-map <local school map> tasks/census-gap-2-2026-11-03/lanes/{T,R1,R2}/people.csv <local band-A lane people.csv files>
```

The band-A lane packets and the school map stay local, because they are drawn from the private census. Their
admitted rows are in `people_rows.csv`.
