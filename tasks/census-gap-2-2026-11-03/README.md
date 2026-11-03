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

## Applied

- `data/people.csv` +49 (PERSON-001334 to PERSON-001382), all tier A.
- `data/inclusion_log.csv` +3, the borderline admissions:
  - Mary Boyce: an emerita *administrative* title held alongside a current professor rank;
  - Ellis Meng: an interests-list phrase;
  - Jeffrey S. Moore: `research_professor`.

| Source | People records added |
|-|-:|
| Census-gap follow-ups: lane T (JHU, Columbia), lanes R1 and R2 | 17 |
| Band-A census leads: 4 lanes, run locally | 32 |

**Owner rulings applied (2026-11-03, `tasks/OWNER_BATTERY_2026-11-03.md`):**
- **B-CG-2:** a biopolymer passes Gate B when the stated research engineers it as a material.
  - Schroeder is released from hold ("Mineralization of biopolymers for sustainable material development").
  - Ribbeck stays held, because her quote describes mucins rather than engineering them.
  - Mai was re-verdicted VERIFIED (`lanes/OWNER/`), but she is already held as PERSON-000914, so no second record.
  - Molinari fails.
- **B-CG-1:** Muller's "Professor of the Graduate School" is outside Gate A.
- **B-CG-3:** `senior_lecturer` is added to the builder's roles. No admitted row changes.

**Admission rule** (`build_people.py`). A person record is admitted only when all of these hold:
- the lane verdict is VERIFIED;
- the **raw-page check** passes (`raw_check.csv`). The integrator re-fetched every gate URL and found both quotes
  word for word in order. Gate A also needs the person's surname within 40 words of the quote, so a bare "Professor"
  on a roster page cannot pass for someone else.
  - Pages came from the NAS Firecrawl.
  - jhu.edu and columbia.edu pages came from the Tavily extract cache (owner-approved route, 72 URLs used). For those
    two hosts the check is a verbatim-copy check against the same saved text, not an independent fetch;
- the role is in the university professor vocabulary;
- all URLs are on the institution's own domain;
- the institution is already held, matched by IPEDS UNITID, including universities held as organization records
  through `registry_links.csv`;
- the name is not already in `people.csv`;
- the integrator's review of every Gate B quote did not hold it.

No institutions were created.

## Census-gap follow-ups (unit: people examined)

The first wave left 79 people STILL_UNCERTAIN (`uncertain.csv`):
- 12 are already held at the same university.
- 1 (Herrera-Alonso) is held at another institution. Her current home was **not** re-checked, because jhu.edu was
  blocked. That stays a follow-up.
- 3 are owner questions: B-CG-1 and B-CG-2.
- 63 were re-run.

| Lane | Input people | Sweep people | VERIFIED | Raw check passed |
|-|-:|-:|-:|-:|
| T (JHU, Columbia; via Tavily) | 8 | 23 | 9 | 8 |
| R1 (+ Northeastern roster sweep) | 28 | 5 | 14 | 11 |
| R2 | 27 | 0 | 5 | 4 |

## Band-A census leads (unit: people; 133 input rows, 132 people)

The census lists 1,176 rostered people, meaning people it found on the school's own roster page. 765 of them are not
in the Atlas at the same school: 133 in band A and 632 in band B. The census's band-A spot-check measured whether
someone is *current polymer faculty at that school*. These gates also require a non-emeritus professor rank and a
polymer sentence on the person's own pages, so the two rates measure different things.

| Outcome | People |
|-|-:|
| VERIFIED by a lane | 37 |
| (of which admitted after the raw check and review) | 32 |
| Already held at the same school | 11 |
| Emeritus styling (fails Gate A) | 30 |
| Other non-professor styling (research associate, senior lecturer, research assistant, former faculty) | 4 |
| At a different school than the census lists | 1 |
| No polymer sentence on the person's own pages (REJECT or STILL_UNCERTAIN) | 41 |
| Not reachable (jhu.edu or columbia.edu not fetched in these lanes, Iowa State or Princeton ECE blocked) | 8 |
| **Total** | **132** |

Band B (632 people) was not run in full. The owner ruled B-CG-4 (a): a 60-person sample runs first.

## Held (`holds.csv`, 18)

- **Integrator review (11):**
  - 5 rest on news items instead of the person's own pages: Wiley, Erb, Gupta, Nguyen and Monroe.
  - 2 rest on department research-area pages: Yang Yang and Jenn-Ming Yang.
  - 1 rests on a consortium page: Vorst.
  - 1 is held under B-CG-2: Ribbeck, whose quote describes rather than engineers.
  - 1 has a title that is a sentence fragment: Kokkoli.
  - 1 is a duplicate row: Jeff Moore, the same person as Jeffrey S. Moore.
- **Raw check (5):**
  - Czabaj, Green and Sletten: the Gate A quote was not found next to their name.
  - Asadi: the Gate B quote was not found on the page.
  - Kirshenbaum: the Gate A page could not be fetched.
- **Already held (2):**
  - Sokolov is held at ORNL (PERSON-000478). Joint appointments are recorded at the primary home.
  - Mai is held at Stanford as PERSON-000914.

## Known gap

SCHEMA §4.9 [v1.8.2] lists `senior_lecturer` in the people vocabulary, but this wave's brief, following the first
wave's, fails lecturers at Gate A, and `build_integration.py`'s `ROLES` omits the value. One lead (a senior lecturer)
was rejected on it, and no admitted row is affected. B-CG-3 was ruled (a): `senior_lecturer` is now in this
builder's roles, and the other stylings stay outside Gate A. The styling classes the lanes met were:
- teaching professor;
- professor of the practice;
- post-tenure;
- senior lecturer.

## Rebuild

```bash
python3 tasks/census-gap-2-2026-11-03/build_people.py --data-dir <pre-pass data> --raw tasks/census-gap-2-2026-11-03/raw_check.csv \
  --school-map <local school map> tasks/census-gap-2-2026-11-03/lanes/{T,R1,R2}/people.csv <local band-A lane people.csv files>
```

The band-A lane packets and the school map stay local, because they are drawn from the private census. Their
admitted rows are in `people_rows.csv`.
