# ORCID completion pass 2 + dedupe sweep (2026-11-11)

**Task:** QUEUE item claimed by spaghetti 2026-11-11 at the owner's instruction. **Scope:** the 649 people
records the first fill (`tasks/people-orcid-2026-11-09/`, PR #259) left unlinked — 453 "no candidate
passed", 189 "no candidate found", 7 "held: two or more iDs pass" (journal outcomes joined to current
`data/people.csv`; the 650th pass-1 unlinked record, PERSON-000812, was removed by the #260 dedupe).

## Rule — unchanged
SCHEMA §4.21 as implemented by pass 1 and tightened by its two-family refute: a candidate is *found* by
name resemblance; a row is *minted* only on the iD itself — published on the person's own profile page
(only iD on the page, family name + a given name agreeing), or carried by an ORCID public record whose
name matches (first given name equal, family name equal, middle initials agreeing when both sides carry
one) **and** whose current employments include the record's institution (ROR id, else name key), where a
current employment has no end date and names a role or a department. Held, never linked: two passing iDs
for one person; a page iD that differs from a record match; an iD passing for two records (dedupe alarm).
No row is minted for an iD already in the table (§4.21 one row per identifier value).

## What changed — finders and target set only
- **Targets:** records with no row in `data/people_identifiers.csv` (649). Already-linked records are
  never re-judged; if an iD recorded for one person passes for another, that is a §4.21 dedupe alarm:
  journaled, listed in `alarm_pairs.csv`, never minted.
- **Page finder:** raw fetch first, as pass 1; an empty or near-empty raw read (blocked / JS shell —
  187 pages were unreadable in pass 1) falls back to the Jina Reader rendering of the same URL.
- **Search finder:** pass 1's affiliation query (family + given + institution ROR/name), plus a
  name-only query (family + given, rows=50). The wider net only finds candidates.
- **Census finder:** not used — no `census.sqlite` exists in this environment (pass 1 ran on the owner's
  desktop). Recorded so the omission is a fact, not an oversight.
- **Two repairs after QA on the first completed run** (finders/institution keys only; the linking rule
  itself is byte-identical — see `build.py`'s docstring): the page finder also harvests an iD printed as
  bare text in a labelled ORCID field ("orcid" in the 160 characters before the iD), which the URL-only
  harvest missed entirely; and institution name keys also include the legal/trade name with
  parenthetical qualifiers stripped, only when that stripped key is produced by exactly one institution
  in the dataset (collision-guarded). One case was deliberately **not** repaired (Rodriguez, under QA):
  loosening `name_matches` is a rule change, not a finder repair.

## Method (`build.py`, adapted from pass 1 with its 11-case self-check intact)
`python3 tasks/people-orcid-2-2026-11-11/build.py --cache <dir> [--fetch] [--apply]`
The ORCID API was called anonymously, with a User-Agent that names this repository and no personal
address. Responses are cached outside the repository; the run is resumable per call. `as_of` is
2026-11-11.

## Results
- **Minted: 11 rows** appended to `data/people_identifiers.csv` (as_of 2026-11-11) — 6 on
  `orcid_record_employment_match_name`, 5 on `orcid_on_institution_page`. The table goes from 804 to
  **815 rows**; linked people are 815 of 1,453 people records; **638 people records remain unlinked**.
- Journal over the 649 targeted records (sums to 649): 582 no candidate passed; 49 no candidate found;
  7 held — two or more iDs pass (PERSON-000194, PERSON-000401, PERSON-000593, PERSON-000971,
  PERSON-001011, PERSON-001026, PERSON-001280); 11 linked.
- **5,514 candidate iDs judged; 0 candidate records unfetched.** Page fallback (Jina) used for 0 pages.
  **Dedupe alarms: 0** (`alarm_pairs.csv` is header-only).
- Run history, for the record: the first fetch run was killed silently mid-run (~08:26 EST) after
  caching ~5,185 responses; the per-call cache made the resume lossless. The first completed tally
  minted 4; QA (below) found the two finder/key defects, and the tally above is the repaired run's.
  Exactly 7 outcomes changed between the two runs, all "no candidate passed" → linked, each listed
  under QA.

## QA
- Journal outcomes sum to the 649-record target set; `--apply` asserted 0 unfetched candidate records
  before appending.
- **All 11 minted rows were hand-re-read by the integrator from the cached ORCID records:** name
  agreement confirmed for each, and for the 6 record-basis rows a current (no end date) employment at
  the Atlas institution carrying a role or department. For the 5 page-basis rows the iD was confirmed
  present in the cached text of the person's own profile page — all five are Penn State MatSE directory
  pages (Vogt, Kim, Hasegawa, van der Vlies, Qiming Zhang).
- The built-in page-vs-record agreement check (a page iD differing from a record match is held) fired
  0 times.
- Borderline calls, disclosed rather than buried:
  - **PERSON-000835 (André J. van der Vlies)** is the weakest mint: page basis only, and his ORCID
    record carries no employment entries at all. §4.21's page clause is the whole basis — the iD sits
    in the ORCID field of his own MatSE directory page and the record's name agrees.
  - The two repairs account for 7 of the 11 mints: Elacqua and Gomez via the stripped institution key
    (their records say "The Pennsylvania State University"; the Atlas legal name is "Pennsylvania State
    University (University Park)"), and the 5 page-basis mints via the labelled bare-iD harvest (Kim's
    record had never even been fetched under the URL-only harvest).
  - **Not minted, named for the owner:** PERSON-000541 (Brittany A. Rodriguez, ORNL). Her iD is on her
    ORNL staff page and her current ORNL employment matches by name key, but her ORCID record puts the
    full name in given-names with family-name empty (the exact name, with middle initial, appears in
    the record's other-names), so the name check fails under the rule as written. Whether that record
    shape should count as a name match is an owner rule question; she stays unlinked in this pass.
- Page-text audit of the residue: of 635 cached profile pages for still-unlinked records, only 9
  contain any ORCID-shaped string at all. The residue is dominated by institutions that publish no iD
  and by ORCID records too sparse or stale to satisfy the strict rule — a precision-bound result, not
  a fetch failure.
- Post-apply `dedupe_scan.py`: **identifier collisions 0**; the table asserts one row per identifier
  value and per person (815 rows / 815 distinct iDs / 815 distinct people).

## Dedupe sweep (`dedupe_scan.py`, `dedupe_leads.csv`, `alarm_pairs.csv`)
Static screen over all 1,453 records: the identifier table asserts clean (804 iDs before this pass,
815 after; no value on two records, no record with two iDs; re-asserted post-apply, collisions 0).
This pass produced no ORCID-keyed alarm for either lead below — neither Modestino record and neither
Advincula record was linked. Name/institution screen: 5 leads, adjudicated here by the integrator:
- **PERSON-001187 / PERSON-001260 — Miguel (Antonio) Modestino, both NYU (ORG-004705), both professor.**
  One record cites an NYU news article, the other his faculty page (Director, Sustainable Engineering
  Initiative). **Verdict: DUPLICATE_OF lead — same person, same institution.** Merge packet recommended
  as its own PR on the #260 pattern (merge into the older record, REMOVALS.csv, inclusion_log entry);
  not merged in this PR (AGENTS §2 rule 4, single-purpose).
- **PERSON-000477 / PERSON-001402 — Rigoberto Advincula, ORNL (ORG-002814) / UT Knoxville
  (ORG-004681).** Governor's Chair is a joint ORNL–UTK appointment by design; both records style him
  Governor's Chair. **Verdict: DUPLICATE_OF lead — one person, joint appointment** (AGENTS §6: record
  once, at the primary home institution). Which record is primary is flagged for the merge packet; if
  this pass links one iD to both records it lands in `alarm_pairs.csv` as corroboration.
- PERSON-000651 / PERSON-000813 — Andrew Ferguson: **not duplicates**; two people, each already
  carrying a distinct ORCID iD (NREL research scientist; UChicago professor).
- PERSON-000354 / PERSON-000767 — Wei Zhang: **not duplicates** (Pitt pharmaceutical sciences;
  Colorado chemistry, who carries his own iD). Common name.
- PERSON-000167 / PERSON-001431 — Young-Teck Kim (Virginia Tech, own iD) / Young Jo Kim (UNH):
  **not duplicates**; different people grouped by the first/last name key.

## Not done
- Unlinked people remaining after this pass stay unlinked: §4.21 never records a missing link as a
  negative fact, and ORCID records change over time.
- The two DUPLICATE_OF leads are merge *packets*, not merges: each merge is its own PR with a
  REMOVALS.csv manifest and an inclusion_log entry (the #260/#261 pattern), and the Advincula
  primary-home call is the owner's if the packet's recommendation is contested.
