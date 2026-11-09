# ORCID iDs for people records (2026-11-09)

**+910 rows** in `data/people_identifiers.csv` (0 → 910): one ORCID iD for 910 of the 1,454 people records. No people
record, evidence row or other table changes. The table was created empty by schema v1.10 (SCHEMA §4.21, owner ruling
2026-11-04); this is its first fill.

| `match_basis` | People records | What linked them |
|-|-|-|
| `orcid_on_institution_page` | 109 | The person's own profile page (the record's `public_profile_url`) links exactly one ORCID iD, and that ORCID record's family name is the record's surname |
| `orcid_record_employment_match_ror` | 354 | The ORCID public record's name matches, and it lists a current employment (no end date) whose ROR id is the institution's `ror_id` |
| `orcid_record_employment_match_name` | 447 | The same, matched on the institution's name (`atlas.name_key` of its legal or trade name) where the employment carries no matching ROR id |

`as_of` is 2026-11-09, the date the ORCID records and pages were read.

## Method (`build.py`)

`python3 tasks/people-orcid-2026-11-09/build.py --cache <dir> [--census <census.sqlite>] [--fetch] [--apply]`

Finding candidates is separate from linking them, as §4.21 requires. A name resemblance finds a candidate, and only the
iD itself links one.

- **Finders:**
  - iDs linked on the person's own profile page, read raw;
  - ORCID public search for family name AND first given name AND (the institution's ROR id OR its legal name);
  - the private polymer-faculty-census, where a candidate with the same first and last name at the same IPEDS unitid
    carries an ORCID iD. The census only suggests a candidate and is not cited.
- **Linking:**
  - A page iD links when it is the only iD on the page and the record's family name matches.
  - Otherwise the ORCID record must match both ways:
    - **Name:** the first given name equals the people record's first name, and the family name is its last word or
      words. When both sides carry a middle name or initial, the first letters must agree ("Wei A. Gao" is not
      "Wei B. Gao").
    - **Employment:** a current employment at the institution.
- **Held, never linked:**
  - a person with two passing iDs;
  - an iD passing for two people;
  - a page iD that differs from a record match.

`build.py` checks the name rule against eight cases on every run. The ORCID API was called anonymously, with a
User-Agent naming this repository and no personal address. Responses are cached outside the repository.

## Precision check

112 profile pages link exactly one ORCID iD.

- **Name matches:** on 106 of them, the ORCID record's full name matches.
- **Record rule:** for 77 of those 106, the record rule (no page) also links a person. It links the same iD in all 77
  cases and a different iD in none.

The other 29 have no current employment at the institution on their ORCID record, so the page is what links them. The
77-of-77 agreement is measured only on people who publish their iD, and they probably keep their ORCID records more
current than average. That makes it an upper bound for the name-matched rows, not a measured precision for them.

## Held (10) and not linked (534)

| Outcome | People records |
|-|-|
| No candidate passed the name + employment test | 345 |
| No candidate found | 189 |
| Two or more iDs pass (common names: Satish Kumar, Shu Yang, Yi Liu, Wei Zhang, Rui Wang and others) | 8 |
| Dedupe alarm: one iD on two records | 2 |

**Dedupe alarm, a lead for the integrator:** PERSON-000597 (Argonne National Laboratory, research scientist) and
PERSON-000812 (University of Chicago, assistant professor) are both "Jie Xu", and both match one ORCID iD. AGENTS §6
records a joint appointment once, at the primary home institution. If this is one person, the records merge under
that rule. This pass links neither.

The per-person outcomes are in `journal.csv`. It lists no candidate iD for an unlinked person, because an unlinked
candidate may belong to someone else.

## Not done

- A missing link is never recorded as a negative fact (§4.21). The 534 unlinked people can be retried as ORCID records
  change.
- Pages that need JavaScript, or that blocked the fetch (187 empty or blocked), were not read through another route.
