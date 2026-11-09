# ORCID iDs for people records (2026-11-09)

**+804 rows** in `data/people_identifiers.csv` (0 → 804): one ORCID iD for each of 804 of the 1,454 people records. No
people record, evidence row or other table changes. Schema v1.10 created the table empty (SCHEMA §4.21, owner ruling
2026-11-04); this pass is its first fill.

| `match_basis` | People records | What linked them |
|-|-|-|
| `orcid_on_institution_page` | 109 | The person's own profile page (the record's `public_profile_url`) links exactly one ORCID iD. The ORCID record's family name is the record's surname, and one of the record's given names is among the ORCID given or other names. |
| `orcid_record_employment_match_ror` | 285 | The ORCID public record's name matches, and it lists a current employment whose ROR id is the institution's `ror_id`. |
| `orcid_record_employment_match_name` | 410 | The same, but matched on the institution's name (`atlas.name_key` of its legal or trade name) because the employment carries no matching ROR id. |

A current employment has no end date **and** names a role or a department. `as_of` is 2026-11-09, the date the ORCID
records and pages were read.

## Method (`build.py`)

`python3 tasks/people-orcid-2026-11-09/build.py --cache <dir> [--census <census.sqlite>] [--fetch] [--apply]`

Finding a candidate is kept separate from linking it, as §4.21 requires. A name resemblance can find a candidate; only
the iD itself links one.

**Finders**
- The person's own profile page, read raw, for the ORCID iDs it links.
- ORCID public search: family name AND first given name AND (the institution's ROR id OR its legal name).
- The private polymer-faculty-census: a candidate with the same first and last name at the same IPEDS unitid that
  carries an ORCID iD. The census is only a finder and is not cited.

**Linking**
- A page iD links when it is the only iD on the page and the names agree as in the table above.
- Otherwise the ORCID record must match on both name and employment:
  - **Name:** the first given name equals the people record's first name, and the family name is the record's last
    word or words. When both sides carry a middle name or initial, the first letters must agree ("Wei A. Gao" is not
    "Wei B. Gao").
  - **Employment:** a current employment at the institution.

**Held, never linked**
- A person with two passing iDs.
- An iD that passes for two people.
- A page iD that differs from a record match.

`build.py` checks its name and employment rules against 11 cases on every run. The ORCID API was called anonymously,
with a User-Agent that names this repository and no personal address. Responses are cached outside the repository.

## Checks

- **Page versus record:** 112 profile pages link exactly one ORCID iD. On 66 of them, the record rule (without the page)
  also links that person. It picks the same iD all 66 times and a different iD none of the time.
  - This is measured only on people who publish their iD, who probably keep ORCID more current than most. Treat it as
    an upper bound for the name-matched rows.
- **Two-family refute** of a stratified random sample of 40 links (20 name-matched, 12 ROR-matched, 8 page), run on the
  first draft of the rule, which then linked 910:
  - **codex:** 40 of 40 sound; verdict SOUND.
  - **grok:** 38 sound and 2 doubtful (Bin Liu, Sonal Deshpande). Codex had confirmed both with independent facts, a
    shared public email and a shared paper. Grok's verdict was UNSOUND because of two gaps in the rule:
    - An open employment with no role and no department cannot tell a professor from a same-name student at a large
      university.
    - A page link checked only the family name.
  - **Both gaps are now closed in the rule above.** Together they removed 106 links, among them the two doubtful rows.
    The removals cost some correct links, which is the price of not accepting the gaps.
- **Stale employments:** both reviewers noted that a missing end date does not prove someone is still there. One sampled
  record leaves a postdoc open beside the faculty job that followed it. The stale line does not link anyone wrongly by
  itself. Because the people record was already verified at its institution, linking it still needs a namesake as well.
  This limit of ORCID data is accepted here, not fixed.

## Held (7) and not linked (643)

| Outcome | People records |
|-|-|
| No candidate passed the name + employment test | 454 |
| No candidate found | 189 |
| Two or more iDs pass (common names, e.g. Satish Kumar, Shu Yang, Yi Liu, Wei Zhang, Rui Wang) | 7 |

**A dedupe lead for the integrator:** PERSON-000597 (Argonne National Laboratory, research scientist) and PERSON-000812
(University of Chicago, assistant professor) are both "Jie Xu". The first draft of the rule matched both to one ORCID
iD. Under the final rule neither links, because that record's employment lines name no role. AGENTS §6 records a joint
appointment once, at the primary home institution. If these records are one person, they merge under that rule. This
pass merges nothing.

Per-person outcomes are in `journal.csv`. For an unlinked person it lists no candidate iD, because that candidate may be
someone else.

## Not done

- **Unlinked people:** §4.21 never records a missing link as a negative fact. The 643 unlinked people can be retried as
  ORCID records change.
- **Unreadable pages:** 187 pages were empty or blocked, or need JavaScript. They were not read through another route.
